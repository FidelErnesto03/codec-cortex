#!/usr/bin/env python3
"""Test the Rust canonicalize implementation against all 40 corpus cases."""
import json, subprocess, hashlib, sys, os

RUST_BIN = "/home/vatrox/workspace/CODEC-CORTEX/experiments/gate-f3/rust/target/release/cortex_parser"
CORPUS_DIR = "/home/vatrox/workspace/CODEC-CORTEX/conformance/c14n/corpus"
INPUT_DIR = os.path.join(CORPUS_DIR, "input")
CANON_DIR = os.path.join(CORPUS_DIR, "canonical")
MANIFEST_PATH = os.path.join(CORPUS_DIR, "manifest.json")
HASH_VECTORS_PATH = "/home/vatrox/workspace/CODEC-CORTEX/conformance/c14n/vectors/hash-vectors.json"
RESULTS_PATH = "/home/vatrox/workspace/CODEC-CORTEX/experiments/gate-f3/rust/results.json"

with open(MANIFEST_PATH) as f:
    manifest = json.load(f)

results = {"canonicalization": "C14N-0.1", "cases": [], "summary": {}}
passed = 0
failed = 0
total = len(manifest["cases"])

for case in manifest["cases"]:
    cid = case["id"]
    input_path = os.path.join(CORPUS_DIR, case["input"])
    canon_path = os.path.join(CORPUS_DIR, case["canonical"])

    with open(input_path, "rb") as f:
        input_bytes = f.read()
    with open(canon_path, "rb") as f:
        expected_bytes = f.read()

    # Run Rust
    proc = subprocess.run(
        [RUST_BIN, "--canonicalize", input_path],
        capture_output=True, timeout=30
    )
    if proc.returncode != 0:
        results["cases"].append({
            "id": cid, "status": "error",
            "stderr": proc.stderr.decode("utf-8", errors="replace")
        })
        failed += 1
        print(f"  FAIL {cid}: non-zero exit {proc.returncode}")
        continue

    rust_canonical = proc.stdout
    report_text = proc.stderr.decode("utf-8", errors="replace")

    # Parse report
    try:
        report = json.loads(report_text)
    except json.JSONDecodeError:
        results["cases"].append({
            "id": cid, "status": "error",
            "stderr": f"Invalid JSON report: {report_text[:200]}"
        })
        failed += 1
        print(f"  FAIL {cid}: invalid report JSON")
        continue

    # Compare bytes
    canon_match = rust_canonical == expected_bytes

    # Verify hashes
    expected_input_sha = hashlib.sha256(input_bytes).hexdigest()
    expected_canon_sha = hashlib.sha256(expected_bytes).hexdigest()
    expected_chash = hashlib.sha256(b"CORTEX-C14N-0.1\x00" + expected_bytes).hexdigest()

    hash_match = (report["inputSha256"] == expected_input_sha and
                  report["canonicalSha256"] == expected_canon_sha and
                  report["canonicalHash"] == f"sha256:{expected_chash}")

    case_result = {
        "id": cid,
        "status": "pass" if canon_match else "fail",
        "canonicalBytesMatch": canon_match,
        "hashMatch": hash_match,
        "rustSha256": report["inputSha256"],
        "expectedSha256": expected_input_sha,
        "changed": report["changed"],
    }

    if not canon_match:
        case_result["rustCanonicalHex"] = rust_canonical.hex()
        case_result["expectedCanonicalHex"] = expected_bytes.hex()
        print(f"  FAIL {cid}: bytes differ")
        print(f"    Rust ({len(rust_canonical)} bytes):   {rust_canonical[:80]}")
        print(f"    Golden ({len(expected_bytes)} bytes): {expected_bytes[:80]}")
        failed += 1
    elif not hash_match:
        print(f"  FAIL {cid}: hash mismatch")
        failed += 1
    else:
        print(f"  PASS {cid}")
        passed += 1

    results["cases"].append(case_result)

results["summary"] = {
    "total": total,
    "passed": passed,
    "failed": failed,
    "allPassed": failed == 0
}

with open(RESULTS_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*50}")
print(f"Results: {passed}/{total} passed, {failed} failed")
print(f"Written to {RESULTS_PATH}")
sys.exit(0 if failed == 0 else 1)
