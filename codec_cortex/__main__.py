#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI entry point for the CORTEX reviewer tool.
Run F3 (C14N golden + idempotence) and F4 (HCORTEX roundtrip + idempotence).

Usage:
    python3 -m tools.cortex_rev [C14N_DIR] [HCORTEX_DIR]
"""

import sys
import os
import json

from .harness import run_all_tests


def main():
    """Run the full test suite and output a report."""
    # Default paths — override via command line or environment
    base = os.environ.get(
        "REV_PACKAGE",
        os.path.join(os.path.dirname(__file__), "..", "..", "experiments")
    )

    c14n_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        base, "gate-f3", "c14n-corpus"
    )
    hcortex_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        base, "gate-f4"
    )

    # Try alternate paths if defaults don't exist
    if not os.path.exists(c14n_dir):
        alt_c14n = os.path.join(base, "c14n", "corpus")
        if os.path.exists(alt_c14n):
            c14n_dir = alt_c14n

    if not os.path.exists(hcortex_dir):
        alt_hc = os.path.join(base, "hcortex")
        if os.path.exists(alt_hc):
            hcortex_dir = alt_hc

    print(f"C14N directory: {c14n_dir}")
    print(f"HCORTEX directory: {hcortex_dir}")
    print()

    if not os.path.exists(c14n_dir) and not os.path.exists(hcortex_dir):
        print("ERROR: Neither corpus directory found.")
        print("Provide paths as arguments: python3 -m tools.cortex_rev C14N_DIR HCORTEX_DIR")
        sys.exit(1)

    report = run_all_tests(c14n_dir, hcortex_dir)

    # Write report
    out_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "rev-report.json"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport written to: {out_path}")

    verdict = report["verdict"]
    if verdict == "PASS":
        sys.exit(0)
    elif verdict == "CONDITIONAL_PASS":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
