# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Security & governance modules (E2, v0.3.4+).

Public surface:

- :mod:`cortex.security.signature` — SHA256SUMS manifest verification
  (used by ``cortex verify --signature``).
- :mod:`cortex.security.secret_scanner` — heuristic secret detection
  (used by ``cortex doctor`` and pre-commit hook).
"""

from __future__ import annotations

from .secret_scanner import (
    ScanResult,
    SecretFinding,
    SecretPattern,
    load_baseline,
    redact,
    save_baseline,
    scan_file,
    scan_paths,
    scan_text,
)
from .signature import (
    SignatureResult,
    parse_manifest,
    sha256_file,
    verify_signature,
)

__all__ = [
    # signature
    "SignatureResult",
    "parse_manifest",
    "sha256_file",
    "verify_signature",
    # secret_scanner
    "ScanResult",
    "SecretFinding",
    "SecretPattern",
    "load_baseline",
    "redact",
    "save_baseline",
    "scan_file",
    "scan_paths",
    "scan_text",
]
