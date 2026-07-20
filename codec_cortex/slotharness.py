#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slots conformance harness — manifest-driven runner for slots corpus.

Public API:
    run_slots_conformance(manifest_dir) -> dict

The harness loads conformance/slots/manifest.json and verifies:
  - valid cases: canonical output and hash match expected goldens
  - invalid cases: parse raises diagnostics matching requiredCodes
  - empty corpus: explicit FAIL (P24)
  - fault injection: corrupted source ⇒ diagnostic/FAIL

CLI: python3 -m codec_cortex slotharness [manifest_dir]
"""

import json
import os
import sys
import hashlib
import tempfile
from pathlib import Path


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _load_manifest(manifest_dir: str) -> dict:
    path = os.path.join(manifest_dir, "manifest.json")
    if not os.path.exists(path):
        return {"valid": [], "invalid": [], "_error": f"manifest not found: {path}"}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _read_source(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _resolve_path(manifest_dir: str, rel_path: str) -> str:
    candidate = os.path.join(manifest_dir, rel_path)
    if os.path.exists(candidate):
        return candidate
    parent = os.path.dirname(manifest_dir)
    candidate2 = os.path.join(parent, rel_path)
    if os.path.exists(candidate2):
        return candidate2
    return candidate


def _run_valid_case(manifest_dir: str, case: dict) -> dict:
    cid = case["id"]
    source_rel = case.get("source", f"{cid}.cortex")
    expected_canon_rel = case.get("expectedCanonical")
    expected_hash = case.get("expectedHash")

    source_path = _resolve_path(manifest_dir, source_rel)
    if not os.path.exists(source_path):
        return {"id": cid, "stage": "missing_source", "status": "error",
                "detail": f"source not found: {source_path}"}

    from codec_cortex.dispatcher import parse_cortex, canonicalize, hash_cortex

    try:
        source = _read_source(source_path)
        doc = parse_cortex(source)
        actual_canon = canonicalize(doc)
        actual_hash = hash_cortex(doc)
    except Exception as e:
        cb = getattr(e, "code", None)
        return {"id": cid, "stage": "parse", "status": "fail",
                "detail": f"{cb or type(e).__name__}: {e}"}

    checks = []
    if expected_canon_rel:
        canon_path = _resolve_path(manifest_dir, expected_canon_rel)
        if os.path.exists(canon_path):
            expected_bytes = _read_source(canon_path).encode("utf-8")
            actual_bytes = actual_canon.encode("utf-8")
            if actual_bytes == expected_bytes:
                checks.append({"check": "canonical", "status": "pass"})
            else:
                checks.append({"check": "canonical", "status": "fail",
                               "expected_sha256": sha256_bytes(expected_bytes),
                               "actual_sha256": sha256_bytes(actual_bytes)})
        else:
            checks.append({"check": "canonical", "status": "skip",
                           "detail": f"golden not found: {canon_path}"})

    if expected_hash:
        if actual_hash == expected_hash:
            checks.append({"check": "hash", "status": "pass"})
        else:
            checks.append({"check": "hash", "status": "fail",
                           "expected": expected_hash, "actual": actual_hash})

    # Idempotence: canonicalize(canonicalize(x)) == canonicalize(x)
    try:
        doc2 = parse_cortex(actual_canon)
        canon2 = canonicalize(doc2)
        if canon2.encode("utf-8") == actual_canon.encode("utf-8"):
            checks.append({"check": "idempotence", "status": "pass"})
        else:
            checks.append({"check": "idempotence", "status": "fail"})
    except Exception as e:
        cb = getattr(e, "code", None)
        checks.append({"check": "idempotence", "status": "fail",
                       "detail": f"{cb or type(e).__name__}: {e}"})

    all_pass = all(c.get("status") == "pass" for c in checks)
    return {"id": cid, "stage": "valid", "status": "pass" if all_pass else "fail",
            "checks": checks}


def _run_invalid_case(manifest_dir: str, case: dict) -> dict:
    cid = case["id"]
    source_rel = case.get("source", f"{cid}.cortex")
    required_codes = case.get("requiredCodes", [])

    source_path = _resolve_path(manifest_dir, source_rel)
    if not os.path.exists(source_path):
        return {"id": cid, "stage": "missing_source", "status": "error",
                "detail": f"source not found: {source_path}"}

    from codec_cortex.dispatcher import parse_cortex

    try:
        source = _read_source(source_path)
        parse_cortex(source)
        return {"id": cid, "stage": "invalid", "status": "fail",
                "detail": "expected parse error, got success"}
    except Exception as e:
        code = getattr(e, "code", type(e).__name__)
        if not required_codes:
            return {"id": cid, "stage": "invalid", "status": "pass",
                    "detail": f"error raised: {code}"}
        if code in required_codes:
            return {"id": cid, "stage": "invalid", "status": "pass",
                    "detail": f"got expected code: {code}"}
        return {"id": cid, "stage": "invalid", "status": "fail",
                "detail": f"got code {code}, expected one of {required_codes}"}


def _test_empty_corpus_fails() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = os.path.join(tmp, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump({"valid": [], "invalid": []}, f)
        report = run_slots_conformance(tmp)
    verdict = report.get("verdict", "")
    total = report.get("total", 0)
    if verdict == "empty" or total == 0:
        return {"probe": "P24", "status": "pass",
                "detail": f"empty corpus → verdict={verdict}, total={total}"}
    return {"probe": "P24", "status": "fail",
            "detail": f"empty corpus did not FAIL: verdict={verdict}, total={total}"}


def _test_fault_injection(manifest_dir: str) -> dict:
    manifest = _load_manifest(manifest_dir)
    valid = manifest.get("valid", [])
    if not valid:
        return {"probe": "fault_injection", "status": "skip",
                "detail": "no valid cases to corrupt"}
    from codec_cortex.dispatcher import parse_cortex
    case = valid[0]
    cid = case["id"]
    source_rel = case.get("source", f"{cid}.cortex")
    source_path = _resolve_path(manifest_dir, source_rel)
    if not os.path.exists(source_path):
        return {"probe": "fault_injection", "status": "skip",
                "detail": f"source not found: {source_path}"}
    source = _read_source(source_path)
    corrupted = source + "\nBROKEN{{{"
    try:
        parse_cortex(corrupted)
        return {"probe": "fault_injection", "status": "fail",
                "detail": "corrupted source parsed without error"}
    except Exception:
        return {"probe": "fault_injection", "status": "pass",
                "detail": "corrupted source correctly rejected"}


def run_slots_conformance(manifest_dir: str) -> dict:
    manifest = _load_manifest(manifest_dir)
    error = manifest.pop("_error", None)
    if error:
        return {"verdict": "error", "error": error, "total": 0, "passed": 0,
                "failed": 0, "results": []}

    valid_cases = manifest.get("valid", [])
    invalid_cases = manifest.get("invalid", [])

    if not valid_cases and not invalid_cases:
        return {"verdict": "empty", "total": 0, "passed": 0, "failed": 0,
                "skipped": 0, "errors": 0,
                "results": [], "note": "empty corpus — explicit FAIL (P24)"}

    results = []

    for case in valid_cases:
        r = _run_valid_case(manifest_dir, case)
        results.append(r)

    for case in invalid_cases:
        r = _run_invalid_case(manifest_dir, case)
        results.append(r)

    p24 = _test_empty_corpus_fails()
    results.append(p24)
    fi = _test_fault_injection(manifest_dir)
    results.append(fi)

    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "pass")
    failed = sum(1 for r in results if r.get("status") == "fail")
    skipped = sum(1 for r in results if r.get("status") == "skip")
    errors = sum(1 for r in results if r.get("status") == "error")

    all_pass = failed == 0 and errors == 0
    verdict = "PASS" if (all_pass and total > 0) else "FAIL"

    return {
        "verdict": verdict,
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "errors": errors,
        "results": results,
    }


def main_cli(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        manifest_dir = os.path.join(
            os.path.dirname(__file__), "..", "conformance", "slots"
        )
    else:
        manifest_dir = argv[0]

    manifest_dir = os.path.abspath(manifest_dir)
    print(f"Manifest directory: {manifest_dir}")
    report = run_slots_conformance(manifest_dir)
    print(f"Verdict: {report['verdict']}")
    print(f"  total:  {report['total']}")
    print(f"  passed: {report['passed']}")
    print(f"  failed: {report['failed']}")
    print(f"  skipped:{report.get('skipped', 0)}")
    print(f"  errors: {report.get('errors', 0)}")
    if report.get("note"):
        print(f"  note: {report['note']}")
    if report.get("failed", 0) > 0:
        for r in report.get("results", []):
            if r.get("status") == "fail":
                print(f"  FAIL: {r.get('id', '?')} ({r.get('detail', 'no detail')})")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main_cli())
