#!/usr/bin/env python3
"""Differential verifier: Python reference versus codec-cortex-rs CLI."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run_rust(binary: Path, command: str, source: Path) -> bytes:
    process = subprocess.run(
        [str(binary), command, str(source)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"Rust command failed ({process.returncode}): "
            f"{process.stderr.decode('utf-8', errors='replace')}"
        )
    return process.stdout


def load_reference(root: Path) -> Any:
    sys.path.insert(0, str(root))
    try:
        return importlib.import_module("codec_cortex")
    except Exception as exc:  # pragma: no cover - operational error path
        raise RuntimeError(f"Cannot import codec_cortex from {root}: {exc}") from exc


def compare_file(reference: Any, binary: Path, source_path: Path) -> dict[str, Any]:
    source = source_path.read_text(encoding="utf-8")

    py_canonical = reference.canonicalize(reference.parse_cortex(source)).encode("utf-8")
    py_hcortex = reference.render_hcortex(reference.parse_cortex(source)).encode("utf-8")

    rs_canonical = run_rust(binary, "canonicalize", source_path)
    rs_hcortex = run_rust(binary, "to-hcortex", source_path)

    canonical_equal = py_canonical == rs_canonical
    hcortex_equal = py_hcortex == rs_hcortex

    return {
        "file": str(source_path),
        "canonical": {
            "equal": canonical_equal,
            "python_sha256": sha256(py_canonical),
            "rust_sha256": sha256(rs_canonical),
        },
        "hcortex": {
            "equal": hcortex_equal,
            "python_sha256": sha256(py_hcortex),
            "rust_sha256": sha256(rs_hcortex),
        },
        "pass": canonical_equal and hcortex_equal,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python-root", type=Path, required=True)
    parser.add_argument("--rust-bin", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("files", type=Path, nargs="+")
    args = parser.parse_args()

    if not args.rust_bin.is_file():
        parser.error(f"Rust binary not found: {args.rust_bin}")

    reference = load_reference(args.python_root)
    cases = [compare_file(reference, args.rust_bin, item) for item in args.files]
    report = {
        "schema": "codec-cortex-differential/1",
        "cases": cases,
        "pass": all(case["pass"] for case in cases),
    }
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
