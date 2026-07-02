# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""E2.6 (v0.3.4) — Signature verification for artefacts.

Reads a ``SHA256SUMS`` manifest (the kind produced by
``scripts/sign_release.py``), computes the SHA256 of a target file,
and compares it against the manifest entry.

This module is intentionally free of CLI concerns so it can be unit
tested in isolation and reused by ``cortex verify --signature`` and
by any future tooling that needs to verify artefact integrity.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SignatureResult:
    """Outcome of a signature verification."""

    ok: bool
    file: str
    expected_hash: Optional[str]
    actual_hash: Optional[str]
    reason: str  # "match" | "mismatch" | "missing_in_manifest" |
                 # "missing_file" | "malformed_manifest" | "no_manifest"

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "file": self.file,
            "expected_hash": self.expected_hash,
            "actual_hash": self.actual_hash,
            "reason": self.reason,
        }


def sha256_file(path: Path) -> str:
    """Compute the SHA256 hex digest of ``path`` (streaming, 64KB chunks)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(manifest_path: Path) -> dict[str, str]:
    """Parse a ``SHA256SUMS`` file into ``{filename: expected_hash}``.

    Returns an empty dict if the file does not exist or is empty.
    Lines starting with ``#`` are ignored.  Malformed lines are silently
    skipped.
    """
    if not manifest_path.is_file():
        return {}

    out: dict[str, str] = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([0-9a-fA-F]{64})\s+\*?(.+)$", line)
        if not m:
            continue
        h = m.group(1).lower()
        name = m.group(2).strip()
        out[name] = h
    return out


def verify_signature(
    target_file: Path,
    manifest_path: Path,
    *,
    strict: bool = False,
) -> SignatureResult:
    """Verify ``target_file`` against the SHA256 entry in ``manifest_path``."""
    target_name = target_file.name

    if not manifest_path.is_file():
        return SignatureResult(
            ok=False,
            file=target_name,
            expected_hash=None,
            actual_hash=None,
            reason="no_manifest",
        )

    entries = parse_manifest(manifest_path)
    if not entries:
        return SignatureResult(
            ok=False,
            file=target_name,
            expected_hash=None,
            actual_hash=None,
            reason="malformed_manifest",
        )

    if target_name not in entries:
        return SignatureResult(
            ok=False,
            file=target_name,
            expected_hash=None,
            actual_hash=None,
            reason="missing_in_manifest",
        )

    if not target_file.is_file():
        return SignatureResult(
            ok=False,
            file=target_name,
            expected_hash=entries[target_name],
            actual_hash=None,
            reason="missing_file",
        )

    actual = sha256_file(target_file)
    expected = entries[target_name]
    if actual.lower() == expected.lower():
        return SignatureResult(
            ok=True,
            file=target_name,
            expected_hash=expected,
            actual_hash=actual,
            reason="match",
        )
    return SignatureResult(
        ok=False,
        file=target_name,
        expected_hash=expected,
        actual_hash=actual,
        reason="mismatch",
    )
