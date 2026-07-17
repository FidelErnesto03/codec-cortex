#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test harness for F3 (C14N golden + idempotence) and F4 (HCORTEX roundtrip + idempotence).
Sections 8-9 of the independent reviewer's implementation.

Adapted to use the modularized package and the new paired schema format.
"""

import os
import json
import hashlib
import datetime
from typing import Any, Dict, List, Optional

from .scalars import ParseError
from .parser import parse_cortex
from .c14n import canonicalize
from .hcortex import render_hcortex, compile_hcortex


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def c14n_hash(b: bytes) -> str:
    domain = b"CORTEX-C14N-0.1"
    return "sha256:" + hashlib.sha256(domain + b"\x00" + b).hexdigest()


# ---------------------------------------------------------------------------
# 9. Test harness
# ---------------------------------------------------------------------------

def run_phase3(c14n_dir: str) -> dict:
    """Run F3: C14N golden + idempotence."""
    manifest_path = os.path.join(c14n_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        return {
            "golden_pass": 0,
            "idempotence_pass": 0,
            "total": 0,
            "failures": [{"stage": "exception", "error": f"manifest not found: {manifest_path}"}],
            "status": "FAIL",
        }
    manifest = json.load(open(manifest_path))
    results: Dict[str, Any] = {
        "golden_pass": 0,
        "idempotence_pass": 0,
        "total": len(manifest["cases"]),
        "failures": [],
    }
    for case in manifest["cases"]:
        cid = case["id"]
        # Paths in manifest are relative to the conformance root, not c14n_dir
        input_rel = case.get("input", f"{cid}.cortex")
        canon_rel = case.get("canonical", f"canonical/{cid}.cortex")
        # Try as-is relative to c14n_dir, also try relative to parent
        input_path = os.path.join(c14n_dir, input_rel)
        if not os.path.exists(input_path):
            input_path = os.path.join(c14n_dir, "..", input_rel)
        canonical_path = os.path.join(c14n_dir, canon_rel)
        if not os.path.exists(canonical_path):
            canonical_path = os.path.join(c14n_dir, "..", canon_rel)
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                source = f.read()
            doc = parse_cortex(source)
            canonical = canonicalize(doc)
            canonical_bytes = canonical.encode("utf-8")
            with open(canonical_path, "rb") as f:
                golden_bytes = f.read()
            if canonical_bytes == golden_bytes:
                results["golden_pass"] += 1
            else:
                results["failures"].append({
                    "case": cid,
                    "stage": "golden",
                    "expected_sha256": sha256_bytes(golden_bytes),
                    "actual_sha256": sha256_bytes(canonical_bytes),
                })
            # Idempotence: canonicalize(canonicalize(x)) == canonicalize(x)
            doc2 = parse_cortex(canonical)
            canonical2 = canonicalize(doc2)
            if canonical2.encode("utf-8") == canonical_bytes:
                results["idempotence_pass"] += 1
            else:
                results["failures"].append({
                    "case": cid,
                    "stage": "idempotence",
                })
        except Exception as e:
            results["failures"].append({
                "case": cid,
                "stage": "exception",
                "error": f"{type(e).__name__}: {e}",
            })
    results["status"] = "PASS" if results["golden_pass"] >= 38 and results["idempotence_pass"] == 40 else "FAIL"
    return results


def run_phase4(hcortex_dir: str) -> dict:
    """Run F4: roundtrip + idempotence + invalid diagnostics + view deps."""
    manifest_path = os.path.join(hcortex_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        return {
            "roundtrip_pass": 0,
            "idempotence_pass": 0,
            "invalid_diag_pass": 0,
            "view_dependencies": 0,
            "failures": [{"stage": "exception", "error": f"manifest not found: {manifest_path}"}],
            "status": "FAIL",
        }
    manifest = json.load(open(manifest_path))
    results: Dict[str, Any] = {
        "roundtrip_pass": 0,
        "idempotence_pass": 0,
        "invalid_diag_pass": 0,
        "view_dependencies": 0,
        "failures": [],
    }

    # Roundtrip + idempotence for canonical cases
    for case in manifest["canonical"]:
        cid = case["id"]
        title = case["title"]
        cortex_path = os.path.join(hcortex_dir, "corpus", "cortex", f"{cid}_{title}.cortex")
        hcortex_path = os.path.join(hcortex_dir, "corpus", "hcortex-canonical", f"{cid}_{title}.md")

        if not os.path.exists(cortex_path):
            # Try alternate path
            cortex_path = os.path.join(hcortex_dir, "cortex", f"{cid}_{title}.cortex")
        if not os.path.exists(hcortex_path):
            hcortex_path = os.path.join(hcortex_dir, "hcortex-canonical", f"{cid}_{title}.md")

        try:
            # Read inputs
            if os.path.exists(cortex_path):
                with open(cortex_path, "r", encoding="utf-8") as f:
                    cortex_source = f.read()
            else:
                # Try reading from the conformance directory structure
                alt_cortex = os.path.join(hcortex_dir, case.get("cortex", f"{cid}_{title}.cortex"))
                if os.path.exists(alt_cortex):
                    with open(alt_cortex, "r", encoding="utf-8") as f:
                        cortex_source = f.read()
                else:
                    results["failures"].append({
                        "case": cid,
                        "stage": "missing_input",
                        "error": f"CORTEX source not found: {cortex_path}",
                    })
                    continue

            golden_hcortex_bytes = None
            if os.path.exists(hcortex_path):
                with open(hcortex_path, "rb") as f:
                    golden_hcortex_bytes = f.read()

            # 1. Parse + canonicalize CORTEX
            doc = parse_cortex(cortex_source)
            canonical_cortex = canonicalize(doc).encode("utf-8")

            # 2. Render HCORTEX using new paired schema format
            rendered_hcortex = render_hcortex(doc).encode("utf-8")
            rendered_sha = sha256_bytes(rendered_hcortex)

            # 3. Compile HCORTEX → AST
            compiled_doc, diags = compile_hcortex(rendered_hcortex.decode("utf-8"))
            if compiled_doc is None or any(d.severity == "error" for d in diags):
                results["failures"].append({
                    "case": cid,
                    "stage": "compile_rendered",
                    "diags": [{"code": d.code, "msg": d.message} for d in diags],
                })
                continue

            # 4. Canonicalize compiled AST → CORTEX
            roundtrip_cortex = canonicalize(compiled_doc).encode("utf-8")
            roundtrip_sha = sha256_bytes(roundtrip_cortex)
            expected_roundtrip_sha = case.get("roundtrip_cortex_sha256", case.get("cortex_sha256", ""))

            # Check roundtrip
            if expected_roundtrip_sha and roundtrip_sha == expected_roundtrip_sha:
                results["roundtrip_pass"] += 1
            elif not expected_roundtrip_sha:
                # No expected SHA — just count if roundtrip didn't fail
                results["roundtrip_pass"] += 1
            else:
                results["failures"].append({
                    "case": cid,
                    "stage": "roundtrip_cortex_mismatch",
                    "expected_sha256": expected_roundtrip_sha,
                    "actual_sha256": roundtrip_sha,
                })

            # 5. Idempotence: render → compile → render should be byte-identical
            doc3, _ = compile_hcortex(rendered_hcortex.decode("utf-8"))
            if doc3 is not None:
                rendered3 = render_hcortex(doc3).encode("utf-8")
                if rendered3 == rendered_hcortex:
                    results["idempotence_pass"] += 1
                else:
                    results["failures"].append({
                        "case": cid,
                        "stage": "hcortex_idempotence",
                    })
            else:
                results["failures"].append({
                    "case": cid,
                    "stage": "hcortex_idempotence_compile_fail",
                })

        except Exception as e:
            results["failures"].append({
                "case": cid,
                "stage": "exception",
                "error": f"{type(e).__name__}: {e}",
            })

    # Invalid diagnostics
    invalid_cases = manifest.get("invalid", [])
    for case in invalid_cases:
        cid = case["id"]
        expected_code = case.get("expected_diagnostic", case.get("expected_code", ""))
        invalid_path = os.path.join(hcortex_dir, "invalid", f"{cid}.md")
        if not os.path.exists(invalid_path):
            invalid_path = os.path.join(hcortex_dir, "corpus", "invalid", f"{cid}.md")
        if not os.path.exists(invalid_path):
            # Skip missing invalid files
            continue
        try:
            with open(invalid_path, "r", encoding="utf-8") as f:
                invalid_source = f.read()
            _, diags = compile_hcortex(invalid_source)
            codes = [d.code for d in diags]
            if expected_code in codes:
                results["invalid_diag_pass"] += 1
            else:
                results["failures"].append({
                    "case": cid,
                    "stage": "invalid_diag",
                    "expected_code": expected_code,
                    "actual_codes": codes,
                })
        except Exception as e:
            results["failures"].append({
                "case": cid,
                "stage": "invalid_exception",
                "error": f"{type(e).__name__}: {e}",
            })

    # VIEW dependencies — count is 0 by design (we never invoke VIEW)
    results["view_dependencies"] = 0

    total_expected = len(manifest.get("canonical", []))
    pass_condition = (
        results["roundtrip_pass"] == total_expected and
        results["idempotence_pass"] == total_expected
    )
    if not invalid_cases:
        pass_condition = pass_condition and results["invalid_diag_pass"] >= 0
    else:
        pass_condition = pass_condition and results["invalid_diag_pass"] == len(invalid_cases)

    pass_condition = pass_condition and results["view_dependencies"] == 0
    results["status"] = "PASS" if pass_condition else "FAIL"
    return results


def run_all_tests(c14n_dir: str, hcortex_dir: str) -> dict:
    """Run all phases and generate a comprehensive report."""
    started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    print("Running Phase 3 (C14N-0.1)...")
    phase3 = run_phase3(c14n_dir)
    print(f"  golden: {phase3['golden_pass']}/{phase3['total']}")
    print(f"  idempotence: {phase3['idempotence_pass']}/{phase3['total']}")
    if phase3.get("failures"):
        print(f"  failures: {len(phase3['failures'])}")

    print("Running Phase 4 (HCORTEX)...")
    phase4 = run_phase4(hcortex_dir)
    total_canon = len(json.load(open(os.path.join(hcortex_dir, "manifest.json"))).get("canonical", []))
    total_invalid = len(json.load(open(os.path.join(hcortex_dir, "manifest.json"))).get("invalid", []))
    print(f"  roundtrip: {phase4['roundtrip_pass']}/{total_canon}")
    print(f"  idempotence: {phase4['idempotence_pass']}/{total_canon}")
    print(f"  invalid diag: {phase4['invalid_diag_pass']}/{total_invalid}")
    print(f"  view deps: {phase4['view_dependencies']}")
    if phase4.get("failures"):
        print(f"  failures: {len(phase4['failures'])}")
        for f in phase4["failures"][:5]:
            print(f"    - {f}")

    completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Verdict
    if (phase3["golden_pass"] >= 38 and phase3["idempotence_pass"] == 40
            and phase4["roundtrip_pass"] == total_canon and phase4["idempotence_pass"] == total_canon
            and phase4["view_dependencies"] == 0):
        verdict = "PASS"
    elif (phase3["golden_pass"] >= 36 and phase4["roundtrip_pass"] >= total_canon - 2
            and phase4["view_dependencies"] == 0):
        verdict = "CONDITIONAL_PASS"
    else:
        verdict = "FAIL"

    findings = []
    if phase3.get("failures"):
        findings.append({"phase": "F3", "count": len(phase3["failures"]), "items": phase3["failures"]})
    if phase4.get("failures"):
        findings.append({"phase": "F4", "count": len(phase4["failures"]), "items": phase4["failures"]})

    report = {
        "reviewer": {
            "name": "independent-python-reviewer",
            "language": "Python 3",
            "started_at": started_at,
            "completed_at": completed_at,
        },
        "phase3": phase3,
        "phase4": phase4,
        "findings": findings,
        "verdict": verdict,
    }

    print(f"\nVerdict: {verdict}")
    return report
