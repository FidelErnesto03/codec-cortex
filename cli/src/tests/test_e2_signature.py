"""E2.6 (v0.3.4) — Tests for `cortex verify --signature` and the
underlying :mod:`cortex.security.signature` module.
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

from cortex.security.signature import (
    parse_manifest,
    sha256_file,
    verify_signature,
)


# ---------------------------------------------------------------------------
# sha256_file
# ---------------------------------------------------------------------------

def test_sha256_file_matches_hashlib():
    """sha256_file must match hashlib.sha256 for arbitrary content."""
    import hashlib
    data = b"hello codec-cortex v0.3.4\n"
    expected = hashlib.sha256(data).hexdigest()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(data)
        path = Path(f.name)
    try:
        assert sha256_file(path) == expected
    finally:
        path.unlink()


def test_sha256_file_large_content():
    """sha256_file must handle large files (streaming, 64KB chunks)."""
    import hashlib
    data = b"x" * (65536 * 3 + 17)  # ~200KB
    expected = hashlib.sha256(data).hexdigest()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(data)
        path = Path(f.name)
    try:
        assert sha256_file(path) == expected
    finally:
        path.unlink()


# ---------------------------------------------------------------------------
# parse_manifest
# ---------------------------------------------------------------------------

def test_parse_manifest_standard_format():
    """parse_manifest must accept the standard 'hash  filename' format."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".SHA256SUMS",
                                      delete=False) as f:
        f.write("abc123def4567890abc123def4567890abc123def4567890abc123def4567890  codec_cortex-0.3.4.whl\n")
        f.write("fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210  codec-cortex-0.3.4.tar.gz\n")
        path = Path(f.name)
    try:
        entries = parse_manifest(path)
        assert "codec_cortex-0.3.4.whl" in entries
        assert "codec-cortex-0.3.4.tar.gz" in entries
        assert entries["codec_cortex-0.3.4.whl"] == "abc123def4567890abc123def4567890abc123def4567890abc123def4567890"
    finally:
        path.unlink()


def test_parse_manifest_handles_comments_and_blank_lines():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".SHA256SUMS",
                                      delete=False) as f:
        f.write("# This is a comment\n\n")
        f.write("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  file.whl\n")
        path = Path(f.name)
    try:
        entries = parse_manifest(path)
        assert len(entries) == 1
        assert "file.whl" in entries
    finally:
        path.unlink()


def test_parse_manifest_star_prefix():
    """parse_manifest must accept the '*filename' coreutils binary-mode format."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".SHA256SUMS",
                                      delete=False) as f:
        f.write("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa *binary.whl\n")
        path = Path(f.name)
    try:
        entries = parse_manifest(path)
        assert "binary.whl" in entries
    finally:
        path.unlink()


def test_parse_manifest_missing_file_returns_empty():
    assert parse_manifest(Path("/nonexistent/SHA256SUMS")) == {}


# ---------------------------------------------------------------------------
# verify_signature
# ---------------------------------------------------------------------------

def test_verify_signature_match():
    """verify_signature returns ok=True when the SHA256 matches."""
    import hashlib
    data = b"original content"
    h = hashlib.sha256(data).hexdigest()
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "artifact.whl"
        target.write_bytes(data)
        manifest = Path(tmp) / "SHA256SUMS"
        manifest.write_text(f"{h}  {target.name}\n")
        result = verify_signature(target, manifest)
        assert result.ok
        assert result.reason == "match"
        assert result.actual_hash == h
        assert result.expected_hash == h


def test_verify_signature_mismatch():
    """verify_signature returns ok=False on hash mismatch."""
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "artifact.whl"
        target.write_bytes(b"tampered content")
        manifest = Path(tmp) / "SHA256SUMS"
        manifest.write_text(f"{'0' * 64}  {target.name}\n")
        result = verify_signature(target, manifest)
        assert not result.ok
        assert result.reason == "mismatch"
        assert result.actual_hash != result.expected_hash


def test_verify_signature_missing_in_manifest():
    """verify_signature returns ok=False when the file is not in the manifest."""
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "unlisted.whl"
        target.write_bytes(b"some content")
        manifest = Path(tmp) / "SHA256SUMS"
        manifest.write_text(f"{'0' * 64}  other.whl\n")
        result = verify_signature(target, manifest)
        assert not result.ok
        assert result.reason == "missing_in_manifest"


def test_verify_signature_no_manifest():
    """verify_signature returns ok=False when the manifest doesn't exist."""
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "artifact.whl"
        target.write_bytes(b"some content")
        manifest = Path(tmp) / "nonexistent.SHA256SUMS"
        result = verify_signature(target, manifest)
        assert not result.ok
        assert result.reason == "no_manifest"


def test_verify_signature_missing_file():
    """verify_signature returns ok=False when the target file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "missing.whl"
        manifest = Path(tmp) / "SHA256SUMS"
        manifest.write_text(f"{'0' * 64}  missing.whl\n")
        result = verify_signature(target, manifest)
        assert not result.ok
        assert result.reason == "missing_file"


# ---------------------------------------------------------------------------
# CLI integration: cortex verify --signature
# ---------------------------------------------------------------------------

def _run_cli(args_list):
    import subprocess
    return subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {SRC_DIR!r}); from cortex.cli.main import main; rc = main(); sys.exit(rc or 0)"]
        + args_list,
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": SRC_DIR},
    )


def test_cli_verify_signature_match():
    """`cortex verify <file> --signature <manifest>` returns 0 on match."""
    import hashlib
    data = b"legitimate wheel content"
    h = hashlib.sha256(data).hexdigest()
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "codec_cortex-0.3.4-py3-none-any.whl"
        target.write_bytes(data)
        manifest = Path(tmp) / "SHA256SUMS"
        manifest.write_text(f"{h}  {target.name}\n")
        r = _run_cli(["verify", str(target), "--signature", str(manifest)])
        assert r.returncode == 0, f"expected rc=0, got {r.returncode}\n{r.stderr}"


def test_cli_verify_signature_mismatch():
    """`cortex verify <file> --signature <manifest>` returns 1 on mismatch."""
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "codec_cortex-0.3.4-py3-none-any.whl"
        target.write_bytes(b"tampered content")
        manifest = Path(tmp) / "SHA256SUMS"
        manifest.write_text(f"{'0' * 64}  {target.name}\n")
        r = _run_cli(["verify", str(target), "--signature", str(manifest)])
        assert r.returncode == 1, f"expected rc=1, got {r.returncode}\n{r.stderr}"


def test_cli_verify_signature_missing_in_manifest():
    """`cortex verify <file> --signature <manifest>` returns 1 when file is
    not listed in the manifest."""
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "extra.whl"
        target.write_bytes(b"some content")
        manifest = Path(tmp) / "SHA256SUMS"
        manifest.write_text(f"{'0' * 64}  other.whl\n")
        r = _run_cli(["verify", str(target), "--signature", str(manifest)])
        assert r.returncode == 1, f"expected rc=1, got {r.returncode}\n{r.stderr}"
