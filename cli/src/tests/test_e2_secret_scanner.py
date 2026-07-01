"""E2.2 (v0.3.4) — Tests for the secret scanner.

NOTE: The test values below are SYNTHETIC and do not represent real
credentials. They are constructed at runtime by concatenating prefix
and body to avoid being matched by any background secret scanner that
might modify this file.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.security.secret_scanner import (
    ScanResult,
    SecretFinding,
    load_baseline,
    redact,
    save_baseline,
    scan_file,
    scan_paths,
    scan_text,
)

# Construct synthetic tokens at runtime to avoid background redaction.
_GHP_PREFIX = "ghp" + "_"
_GHP_BODY = "abcdefghijklmnopqrstuvwxyz0123456789ABCD"
_GHP_TOKEN = _GHP_PREFIX + _GHP_BODY

_PYPI_PREFIX = "pypi" + "-"
_PYPI_BODY = "A" * 60
_PYPI_TOKEN = _PYPI_PREFIX + _PYPI_BODY

_AKIA_TOKEN = "AKIA" + "IOSFODNN7EXAMPLE"

_PEM_HEADER = "-----BEGIN RSA PRIVATE KEY-----"

_SLACK_TOKEN = "xoxb" + "-1234567890-abcdefghij"


# ---------------------------------------------------------------------------
# Pattern detection
# ---------------------------------------------------------------------------

def test_detects_github_pat_classic():
    """Scanner must detect ghp_ tokens (36+ alphanumeric)."""
    text = f'GH_TOKEN = "{_GHP_TOKEN}"'
    findings = scan_text(text, path="test.py")
    rules = [f.rule for f in findings]
    assert "github_pat_classic" in rules


def test_detects_pypi_token():
    """Scanner must detect pypi- tokens (60+ chars)."""
    text = f'PYPI_TOKEN = "{_PYPI_TOKEN}"'
    findings = scan_text(text, path="test.py")
    rules = [f.rule for f in findings]
    assert "pypi_token" in rules


def test_detects_aws_access_key():
    """Scanner must detect AKIA-prefixed AWS access key IDs."""
    text = f'AWS_KEY = "{_AKIA_TOKEN}"'
    findings = scan_text(text, path="test.py")
    rules = [f.rule for f in findings]
    assert "aws_access_key_id" in rules


def test_detects_pem_private_key():
    """Scanner must detect PEM private key headers."""
    text = f"{_PEM_HEADER}\nMIIEpAIBAAKCAQEA..."
    findings = scan_text(text, path="key.pem")
    rules = [f.rule for f in findings]
    assert "pem_private_key" in rules


def test_detects_password_assignment():
    """Scanner must detect password = '...' assignments (8+ chars)."""
    text = 'password = "supersecret123"'
    findings = scan_text(text, path="config.py")
    rules = [f.rule for f in findings]
    assert "password_assignment" in rules


def test_does_not_detect_short_password():
    """Scanner must NOT flag short passwords (< 8 chars)."""
    text = 'password = "short"'
    findings = scan_text(text, path="config.py")
    rules = [f.rule for f in findings]
    assert "password_assignment" not in rules


def test_detects_slack_token():
    """Scanner must detect xox[bps]- tokens."""
    text = f'SLACK_TOKEN = "{_SLACK_TOKEN}"'
    findings = scan_text(text, path="config.py")
    rules = [f.rule for f in findings]
    assert "slack_token" in rules


# ---------------------------------------------------------------------------
# Severity classification
# ---------------------------------------------------------------------------

def test_high_severity_for_known_prefixes():
    """ghp_, pypi-, AKIA, etc. must be classified as 'high'."""
    text = f'TOKEN = "{_GHP_TOKEN}"'
    findings = scan_text(text, path="test.py")
    high_findings = [f for f in findings if f.severity == "high"]
    assert len(high_findings) > 0


def test_medium_severity_for_generic_assignments():
    """password = '...' assignments are 'medium' (may be false positives)."""
    text = 'password = "supersecret123"'
    findings = scan_text(text, path="config.py")
    medium_findings = [f for f in findings if f.severity == "medium"]
    assert len(medium_findings) > 0


# ---------------------------------------------------------------------------
# File scanning
# ---------------------------------------------------------------------------

def test_scan_file_skips_binary():
    """Binary files (containing NUL bytes) must be skipped."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
        f.write(b"\x00\x01\x02\x03ghp_test")
        path = Path(f.name)
    try:
        findings, was_scanned, n = scan_file(path)
        assert not was_scanned
        assert findings == []
    finally:
        path.unlink()


def test_scan_file_reads_utf8():
    """UTF-8 files must be scanned and findings returned.

    Note: some environments have a background secret scanner that may
    redact token-like strings in temp files before our scanner sees them.
    We assert >= 1 finding (not exactly 1) to handle both cases.
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py",
                                      encoding="utf-8") as f:
        f.write(f'TOKEN = "{_GHP_TOKEN}"\n')
        path = Path(f.name)
    try:
        findings, was_scanned, n = scan_file(path)
        assert was_scanned
        assert len(findings) >= 1
    finally:
        path.unlink()


# ---------------------------------------------------------------------------
# scan_paths (directory walking)
# ---------------------------------------------------------------------------

def test_scan_paths_walks_directory():
    """scan_paths must walk directories recursively."""
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "a.py").write_text(f'T = "{_GHP_TOKEN}"\n')
        sub = Path(tmp) / "sub"
        sub.mkdir()
        (sub / "b.py").write_text(f'T = "{_GHP_TOKEN}E"\n')
        result = scan_paths([Path(tmp)])
        assert result.files_scanned == 2
        assert len(result.findings) == 2


def test_scan_paths_skips_hidden_dirs():
    """.git, .venv, __pycache__ etc. must be skipped."""
    with tempfile.TemporaryDirectory() as tmp:
        git_dir = Path(tmp) / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text(f'T = "{_GHP_TOKEN}"\n')
        result = scan_paths([Path(tmp)])
        assert result.files_scanned == 0
        assert len(result.findings) == 0


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------

def test_baseline_suppresses_findings():
    """Findings matching (path, rule, line) in the baseline must be silenced."""
    text = f'T = "{_GHP_TOKEN}"\n'
    findings = scan_text(text, path="leak.py")
    assert len(findings) == 1

    baseline_path = Path(tempfile.mktemp(suffix=".baseline"))
    save_baseline(baseline_path, findings)
    try:
        baseline = load_baseline(baseline_path)
        assert len(baseline) == 1
        findings2 = scan_text(text, path="leak.py", baseline=baseline)
        assert len(findings2) == 0
    finally:
        baseline_path.unlink()


# ---------------------------------------------------------------------------
# Redaction
# ---------------------------------------------------------------------------

def test_redact_keeps_prefix_and_suffix():
    """redact() must keep the first 8 and last 4 chars, replace middle."""
    redacted = redact(_GHP_TOKEN)
    assert redacted.startswith("ghp_abcd")
    assert redacted.endswith("ABCD")
    assert "..." in redacted


def test_redact_short_match():
    """redact() on a short match keeps only the prefix."""
    match = "short"
    redacted = redact(match)
    assert redacted.startswith("short") or redacted.startswith("shor")
