#!/usr/bin/env python3
"""Verify a CODEC-CORTEX audit signature by recompute.

The signature scheme is declared inside the artifact itself
(`signature_scheme`): sha256 over the UTF-8 bytes of the audit object
serialized with sorted keys, 2-space indent and no trailing newline, with the
`signature` key removed. This script makes that claim executable instead of
rhetorical (Constitution Art. XVII).

Usage: python bench/verify_audit.py [path/to/audit.sig]
Exit 0 when the signature and the referenced artifacts verify, 1 otherwise.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def payload_digest(doc: dict) -> str:
    body = {key: value for key, value in doc.items() if key != "signature"}
    blob = json.dumps(body, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else ROOT / "bench" / "results" / "audit.sig"
    doc = json.loads(path.read_text(encoding="utf-8"))

    signature = doc.get("signature", "")
    algorithm, _, digest = signature.partition(":")
    failures: list[str] = []

    if algorithm != "heimdall":
        failures.append(f"unexpected auditor signature {algorithm!r}")
    if digest != payload_digest(doc):
        failures.append("signature does not match the recomputed payload digest")

    artifacts = doc.get("artifacts", {})
    cert = artifacts.get("certificate.json", {}).get("sha256")
    if cert:
        cert_path = ROOT / "bench" / "results" / "certificate.json"
        actual = hashlib.sha256(cert_path.read_bytes()).hexdigest()
        if actual != cert:
            failures.append(f"certificate.json sha256 {actual} != audited {cert}")

    print(f"audit_sig: {doc.get('audit_sig')}  verdict: {doc.get('verdict')}  auditor: {doc.get('auditor')}")
    print(f"commit: {doc.get('commit')}")
    print(f"signature: {signature}")
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("OK signature and artifacts verify by recompute")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
