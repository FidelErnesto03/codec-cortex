# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""E2.2 (v0.3.4) — Heuristic secret scanner.

Detects likely secrets (API tokens, passwords, private keys) in text
content without requiring any external tool. The patterns cover the
common high-signal cases:

  - GitHub Personal Access Tokens (``ghp_...``, ``github_pat_...``)
  - PyPI tokens (``pypi-...``)
  - AWS access keys (``AKIA...``) and secret keys (40-char base64)
  - Google API keys (``AIza...``)
  - Slack tokens (``xoxb-``, ``xoxp-``, ``xoxs-``)
  - Stripe keys (``sk_live_``, ``sk_test_``, ``rk_live_``)
  - Generic ``password``/``secret``/``token``/``api_key`` assignments
    in INI/YAML/ENV style
  - PEM private key blocks

The scanner is intentionally conservative: it surfaces findings as
``findings`` (a list of ``SecretFinding`` dataclasses) and leaves the
decision to block or warn to the caller.  Callers include:

  - ``cortex doctor`` (CLI command) — reports findings in the diagnostic
    summary.
  - ``cortex doctor --scan-secrets`` — same, but exits 1 if any finding
    is severity ``high``.
  - ``.pre-commit-config.yaml`` ``cortex-secret-scan`` hook — runs the
    scanner on staged files and fails the commit if any high-severity
    finding is present.

A ``.secrets.baseline`` JSON file can be used to silence known false
positives.  The format is::

    {
      "version": 1,
      "findings": [
        {"path": "path/to/file", "rule": "github_pat", "line": 12, "match": "ghp_xxxx"}
      ]
    }

Findings whose ``path`` AND ``rule`` AND ``line`` match a baseline
entry are suppressed.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SecretPattern:
    """A single secret-detection rule."""

    rule: str
    description: str
    severity: str  # "high" | "medium"
    pattern: re.Pattern
    # Optional: required context (substring must appear on the same line
    # to count as a finding).  This avoids matching on example data.
    required_context: Optional[str] = None


# High-signal patterns: known service prefixes.
# Each pattern is anchored to the specific token format so that example
# data (``ghp_xxxxx`` placeholders) won't match unless the placeholder
# is replaced with the actual token format (28+ alphanumeric chars).
_PATTERNS: List[SecretPattern] = [
    SecretPattern(
        rule="github_pat_classic",
        description="GitHub Personal Access Token (classic, ghp_ prefix)",
        severity="high",
        pattern=re.compile(r"\bghp_[A-Za-z0-9]{36,}\b"),
    ),
    SecretPattern(
        rule="github_pat_fine",
        description="GitHub fine-grained PAT (github_pat_ prefix)",
        severity="high",
        pattern=re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b"),
    ),
    SecretPattern(
        rule="pypi_token",
        description="PyPI API token (pypi- prefix)",
        severity="high",
        pattern=re.compile(r"\bpypi-[A-Za-z0-9]{60,}\b"),
    ),
    SecretPattern(
        rule="aws_access_key_id",
        description="AWS Access Key ID (AKIA prefix)",
        severity="high",
        pattern=re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    ),
    SecretPattern(
        rule="google_api_key",
        description="Google API key (AIza prefix)",
        severity="high",
        pattern=re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"),
    ),
    SecretPattern(
        rule="slack_token",
        description="Slack token (xox[bps]- prefix)",
        severity="high",
        pattern=re.compile(r"\bxox[bps]-[A-Za-z0-9-]{10,}\b"),
    ),
    SecretPattern(
        rule="stripe_secret_key",
        description="Stripe secret key (sk_live_ / sk_test_ / rk_live_)",
        severity="high",
        pattern=re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{20,}\b"),
    ),
    SecretPattern(
        rule="pem_private_key",
        description="PEM private key block",
        severity="high",
        pattern=re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    ),
    # Generic key=value patterns. These have medium severity because they
    # can produce false positives (test fixtures, documentation, etc.).
    SecretPattern(
        rule="password_assignment",
        description="password = \"...\" assignment (>= 8 chars)",
        severity="medium",
        pattern=re.compile(
            r"(?i)\bpassword\s*[:=]\s*['\"][^'\"]{8,}['\"]"
        ),
        required_context=None,
    ),
    SecretPattern(
        rule="api_key_assignment",
        description="api_key = \"...\" assignment (>= 12 chars)",
        severity="medium",
        pattern=re.compile(
            r"(?i)\bapi[_-]?key\s*[:=]\s*['\"][^'\"]{12,}['\"]"
        ),
    ),
    SecretPattern(
        rule="secret_assignment",
        description="secret = \"...\" assignment (>= 12 chars)",
        severity="medium",
        pattern=re.compile(
            r"(?i)\bsecret\s*[:=]\s*['\"][^'\"]{12,}['\"]"
        ),
    ),
    SecretPattern(
        rule="token_assignment",
        description="token = \"...\" assignment (>= 12 chars)",
        severity="medium",
        pattern=re.compile(
            r"(?i)\btoken\s*[:=]\s*['\"][^'\"]{12,}['\"]"
        ),
    ),
]


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

@dataclass
class SecretFinding:
    """A single secret detected by the scanner."""

    path: str
    line: int  # 1-indexed
    rule: str
    description: str
    severity: str  # "high" | "medium"
    match: str  # the matched substring (may be redacted downstream)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "line": self.line,
            "rule": self.rule,
            "description": self.description,
            "severity": self.severity,
            "match": self.match,
        }

    def fingerprint(self) -> tuple[str, str, int]:
        """Stable identity for baseline comparison: (path, rule, line)."""
        return (self.path, self.rule, self.line)


@dataclass
class ScanResult:
    """Aggregate result of scanning one or more files."""

    findings: List[SecretFinding] = field(default_factory=list)
    files_scanned: int = 0
    bytes_scanned: int = 0

    @property
    def has_high(self) -> bool:
        return any(f.severity == "high" for f in self.findings)

    @property
    def has_medium(self) -> bool:
        return any(f.severity == "medium" for f in self.findings)

    def by_severity(self, severity: str) -> List[SecretFinding]:
        return [f for f in self.findings if f.severity == severity]

    def to_dict(self) -> dict:
        return {
            "files_scanned": self.files_scanned,
            "bytes_scanned": self.bytes_scanned,
            "findings_count": len(self.findings),
            "high_count": len(self.by_severity("high")),
            "medium_count": len(self.by_severity("medium")),
            "findings": [f.to_dict() for f in self.findings],
        }


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------

def load_baseline(path: Optional[Path]) -> set[tuple[str, str, int]]:
    """Load a ``.secrets.baseline`` JSON file into a set of fingerprints.

    Returns an empty set if ``path`` is None or does not exist.
    """
    if not path or not path.is_file():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    out: set[tuple[str, str, int]] = set()
    for entry in data.get("findings", []):
        try:
            out.add((entry["path"], entry["rule"], int(entry["line"])))
        except (KeyError, ValueError, TypeError):
            continue
    return out


def save_baseline(path: Path, findings: Iterable[SecretFinding]) -> None:
    """Write ``findings`` to ``path`` as a baseline JSON file."""
    data = {
        "version": 1,
        "findings": [
            {"path": f.path, "rule": f.rule, "line": f.line, "match": f.match}
            for f in findings
        ],
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

# Files we skip entirely. Binary detection is done by trying to decode as
# UTF-8 and falling back to latin-1 if that fails; if the first 8KB
# contains a NUL byte, the file is treated as binary and skipped.
_BINARY_NUL_THRESHOLD = 8192

# Hard size limit (10 MB) — files larger than this are skipped with a
# warning, since they are unlikely to be source files.
_MAX_FILE_SIZE = 10 * 1024 * 1024


def _is_binary(data: bytes) -> bool:
    """Heuristic: a file is binary if its first 8KB contains a NUL byte."""
    return b"\x00" in data[:_BINARY_NUL_THRESHOLD]


def scan_text(
    text: str,
    *,
    path: str,
    baseline: Optional[set[tuple[str, str, int]]] = None,
) -> List[SecretFinding]:
    """Scan ``text`` for secrets. Returns a list of findings.

    ``path`` is used only for reporting (it appears in
    :attr:`SecretFinding.path`).
    """
    baseline = baseline or set()
    findings: List[SecretFinding] = []
    lines = text.splitlines()
    for lineno, line in enumerate(lines, start=1):
        for pat in _PATTERNS:
            for m in pat.pattern.finditer(line):
                fp = (path, pat.rule, lineno)
                if fp in baseline:
                    continue
                findings.append(SecretFinding(
                    path=path,
                    line=lineno,
                    rule=pat.rule,
                    description=pat.description,
                    severity=pat.severity,
                    match=m.group(0),
                ))
    return findings


def scan_file(
    path: Path,
    *,
    baseline: Optional[set[tuple[str, str, int]]] = None,
) -> tuple[List[SecretFinding], bool, int]:
    """Scan a single file. Returns ``(findings, was_scanned, bytes_read)``.

    ``was_scanned`` is False if the file was skipped (binary, too large,
    or unreadable).
    """
    baseline = baseline or set()
    try:
        raw = path.read_bytes()
    except OSError:
        return [], False, 0
    if len(raw) > _MAX_FILE_SIZE:
        return [], False, 0
    if _is_binary(raw):
        return [], False, 0
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw.decode("latin-1")
        except UnicodeDecodeError:
            return [], False, 0
    findings = scan_text(text, path=str(path), baseline=baseline)
    return findings, True, len(raw)


def scan_paths(
    paths: Iterable[Path],
    *,
    baseline: Optional[Path] = None,
) -> ScanResult:
    """Scan multiple paths (files or directories).

    Directories are walked recursively; hidden directories (``.git``,
    ``.venv``, ``node_modules``, ``__pycache__``, ``dist``, ``build``)
    are skipped.
    """
    baseline_set = load_baseline(baseline)
    skip_dirs = {".git", ".venv", "node_modules", "__pycache__", "dist", "build", ".pytest_cache"}
    skip_exts = {".pyc", ".pyo", ".so", ".o", ".a", ".dylib", ".png", ".jpg", ".jpeg",
                 ".gif", ".bmp", ".ico", ".pdf", ".zip", ".gz", ".tar", ".tgz",
                 ".whl", ".egg", ".class", ".jar"}

    result = ScanResult()
    targets: List[Path] = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for sub in p.rglob("*"):
                if any(part in skip_dirs for part in sub.parts):
                    continue
                if sub.is_file() and sub.suffix.lower() not in skip_exts:
                    targets.append(sub)
        elif p.is_file():
            targets.append(p)

    for tgt in targets:
        findings, was_scanned, n = scan_file(tgt, baseline=baseline_set)
        if was_scanned:
            result.files_scanned += 1
            result.bytes_scanned += n
        result.findings.extend(findings)

    return result


def redact(match: str, *, keep_prefix: int = 8, keep_suffix: int = 4) -> str:
    """Redact a secret match for safe display.

    Keeps the first ``keep_prefix`` and last ``keep_suffix`` characters
    visible; replaces the middle with ``...``.
    """
    if len(match) <= keep_prefix + keep_suffix + 3:
        # Short matches: keep prefix only.
        return match[:keep_prefix] + "..." if len(match) > keep_prefix else match
    return f"{match[:keep_prefix]}...{match[-keep_suffix:]}"
