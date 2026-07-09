# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex benchmark`` — inspect and validate suites under ``benchmarks/``."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class BenchmarkError(RuntimeError):
    pass


def _candidate_roots(explicit: Optional[str] = None) -> Iterable[Path]:
    if explicit:
        yield Path(explicit).expanduser().resolve()
        return
    cwd = Path.cwd().resolve()
    yield cwd / "benchmarks"
    for parent in cwd.parents:
        yield parent / "benchmarks"
        yield parent / "docs" / "benchmarks"
    module_root = Path(__file__).resolve()
    for parent in module_root.parents:
        yield parent / "benchmarks"
        yield parent / "docs" / "benchmarks"


def resolve_root(explicit: Optional[str] = None) -> Path:
    for candidate in _candidate_roots(explicit):
        if candidate.is_dir():
            return candidate
    raise BenchmarkError("benchmarks directory not found; pass --root")


def discover_suites(root: Path) -> List[Path]:
    return sorted(p for p in root.iterdir() if p.is_dir() and (p / "manifest.json").is_file())


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BenchmarkError(f"invalid JSON: {path}: {exc}") from exc


def _count_csv_rows(path: Path) -> int:
    if not path.is_file():
        return 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        return max(sum(1 for _ in csv.DictReader(handle)), 0)


def inspect_suite(path: Path) -> Dict[str, Any]:
    manifest_path = path / "manifest.json"
    manifest = _read_json(manifest_path)
    runs = path / "runs"
    corpus_files = sorted((path / "corpus" / "source").glob("*.cortex"))
    present = {
        "manifest": manifest_path.is_file(),
        "corpus_source": bool(corpus_files),
        "summary_tasks": (runs / "summary_tasks.csv").is_file(),
        "scored_tasks": (runs / "scored_tasks.csv").is_file(),
        "method_results": (runs / "method_results.json").is_file(),
        "scenario_results": (runs / "scenario_results.json").is_file(),
    }
    return {
        "suite": path.name,
        "path": str(path),
        "manifest": manifest,
        "present": present,
        "ok": all(present.values()),
        "corpus_count": len(corpus_files),
        "summary_rows": _count_csv_rows(runs / "summary_tasks.csv"),
        "scored_rows": _count_csv_rows(runs / "scored_tasks.csv"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cortex benchmark")
    parser.add_argument("--root", default=None, help="benchmarks directory")
    parser.add_argument("--suite", default=None, help="suite name, e.g. v2.1.0")
    parser.add_argument("--list", action="store_true", help="list available benchmark suites")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser


def run(args) -> int:
    root = resolve_root(getattr(args, "root", None))
    suites = discover_suites(root)
    if getattr(args, "suite", None):
        selected = root / args.suite
        if not selected.is_dir():
            raise BenchmarkError(f"suite not found: {args.suite}")
        suites = [selected]
    if not suites:
        raise BenchmarkError(f"no benchmark suites with manifest.json under {root}")
    payload = [{"suite": p.name, "path": str(p), "manifest": str(p / "manifest.json")} for p in suites] if getattr(args, "list", False) else [inspect_suite(p) for p in suites]
    if getattr(args, "format", "text") == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        for item in payload:
            if "ok" not in item:
                print(f"{item['suite']}\t{item['manifest']}")
                continue
            status = "OK" if item["ok"] else "INCOMPLETE"
            print(f"suite: {item['suite']} [{status}]")
            print(f"  corpus:       {item['corpus_count']}")
            print(f"  summary rows: {item['summary_rows']}")
            print(f"  scored rows:  {item['scored_rows']}")
    return 0 if all(item.get("ok", True) for item in payload) else 1
