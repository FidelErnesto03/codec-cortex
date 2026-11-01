#!/usr/bin/env python3
"""Run the cortex parser against all valid and invalid test cases."""
import json
import os
import subprocess
import sys

WORKSPACE = "/home/vatrox/workspace/CODEC-CORTEX"
PARSER = "/home/vatrox/rust-v2/target/release/cortex_parser"
OUTPUT_DIR = "/home/vatrox/rust-v2"

def run_test(source_path, out_path, diag_path):
    with open(out_path, 'w') as outf, open(diag_path, 'w') as diagf:
        result = subprocess.run(
            [PARSER, source_path],
            stdout=outf,
            stderr=diagf,
            timeout=30
        )
    return result.returncode

def main():
    os.makedirs(f"{OUTPUT_DIR}/valid", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/invalid", exist_ok=True)

    manifest_path = f"{WORKSPACE}/examples/manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    results = {"valid": {"passed": 0, "failed": 0, "details": []},
               "invalid": {"passed": 0, "failed": 0, "details": []}}

    # Run valid cases
    for case in manifest["valid"]:
        case_id = case["id"]
        source = f"{WORKSPACE}/examples/{case['source']}"
        out_path = f"{OUTPUT_DIR}/valid/{case_id}.json"
        diag_path = f"{OUTPUT_DIR}/invalid/{case_id}_diag.json"  # unused for valid

        # We'll capture to named files
        ast_out = f"{OUTPUT_DIR}/valid/{case_id}_ast.json"
        ast_err = f"{OUTPUT_DIR}/valid/{case_id}_stderr.json"

        try:
            rc = run_test(source, ast_out, ast_err)
            # Check if output is valid JSON
            if rc == 0:
                with open(ast_out) as f:
                    data = json.load(f)
                results["valid"]["passed"] += 1
                results["valid"]["details"].append({"id": case_id, "status": "pass", "rc": rc})
            else:
                # Check for diagnostics on stderr
                with open(ast_err) as f:
                    errs = f.read().strip()
                results["valid"]["failed"] += 1
                results["valid"]["details"].append({"id": case_id, "status": "fail", "rc": rc, "diags": errs[:200]})
        except Exception as e:
            results["valid"]["failed"] += 1
            results["valid"]["details"].append({"id": case_id, "status": "error", "error": str(e)})

    # Run invalid cases
    for case in manifest["invalid"]:
        case_id = case["id"]
        source = f"{WORKSPACE}/examples/{case['source']}"
        required_codes = set(case.get("requiredCodes", []))
        ast_out = f"{OUTPUT_DIR}/invalid/{case_id}_ast.json"
        diag_out = f"{OUTPUT_DIR}/invalid/{case_id}_diag.json"

        try:
            rc = run_test(source, ast_out, diag_out)
            # Read diagnostics
            diags = []
            with open(diag_out) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            d = json.loads(line)
                            diags.append(d.get("code", ""))
                        except:
                            pass

            found_codes = set(diags)
            missing = required_codes - found_codes
            if not missing and rc != 0:
                results["invalid"]["passed"] += 1
                results["invalid"]["details"].append({"id": case_id, "status": "pass", "rc": rc, "codes": list(found_codes)})
            else:
                results["invalid"]["failed"] += 1
                results["invalid"]["details"].append({
                    "id": case_id, "status": "fail", "rc": rc,
                    "required": list(required_codes),
                    "found": list(found_codes),
                    "missing": list(missing),
                    "rc_expected_nonzero": rc == 0
                })
        except Exception as e:
            results["invalid"]["failed"] += 1
            results["invalid"]["details"].append({"id": case_id, "status": "error", "error": str(e)})

    # Print summary
    print(f"\n{'='*60}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*60}")
    vp = results["valid"]["passed"]
    vt = vp + results["valid"]["failed"]
    ip = results["invalid"]["passed"]
    it = ip + results["invalid"]["failed"]
    print(f"Valid:   {vp}/{vt} passed ({vp/vt*100:.0f}%)" if vt > 0 else "Valid:   0/0")
    print(f"Invalid: {ip}/{it} passed ({ip/it*100:.0f}%)" if it > 0 else "Invalid: 0/0")
    print()

    # Print details for failed cases
    for cat in ["valid", "invalid"]:
        fails = [d for d in results[cat]["details"] if d["status"] != "pass"]
        if fails:
            print(f"\n{cat.upper()} FAILURES:")
            for f in fails:
                print(f"  {f['id']}: {f.get('status')} (rc={f.get('rc')})")
                if 'missing' in f:
                    print(f"    Required codes: {f.get('required')}")
                    print(f"    Found codes: {f.get('found')}")
                    print(f"    Missing: {f.get('missing')}")
                if 'diags' in f:
                    print(f"    Diags: {f.get('diags')}")

    # Save results
    with open(f"{OUTPUT_DIR}/results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {OUTPUT_DIR}/results.json")

    # Exit code reflects if all required criteria met
    vpct = vp / vt * 100 if vt > 0 else 0
    ipct = ip / it * 100 if it > 0 else 0
    if vpct >= 90 and ipct >= 90:
        print("CRITERIA MET: >=90% on both valid and invalid")
        sys.exit(0)
    else:
        print(f"CRITERIA NOT MET: valid={vpct:.0f}%, invalid={ipct:.0f}% (need >=90%)")
        sys.exit(1)

if __name__ == "__main__":
    main()
