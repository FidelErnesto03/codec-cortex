#!/usr/bin/env python3
"""
Benchmark comparativo v2.2.1: CODEC-CORTEX vs paquetes PyPI comparables.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE = Path("/home/z/my-project/download/benchmark-cortex-v22")
SRC = BASE / "corpus" / "source"
V221 = Path("/home/z/my-project/download/benchmark-cortex-v221")
RUNS = V221 / "runs"
RUNS.mkdir(parents=True, exist_ok=True)

PYTHON = "/home/z/.venv/bin/python"


def load_corpus_cases() -> List[Dict]:
    manifest = json.loads((BASE / "corpus" / "normalized" / "corpus_manifest.json").read_text())
    cases = []
    for cmeta in manifest["cases"]:
        cid = cmeta["case_id"]
        case = {
            "case_id": cid,
            "domain": cmeta["domain"],
            "cortex": (SRC / f"{cid}.cortex").read_text(),
            "raw": (SRC / f"{cid}.raw.md").read_text(),
        }
        cortex_text = case["cortex"]
        fcs_match = re.search(r'FCS:primary\{what:"([^"]+)"', cortex_text)
        obj_match = re.search(r'OBJ:\w+\{goal:"([^"]+)"', cortex_text)
        cnst_match = re.search(r'CNST:(\w+)\{[^}]*severity:"blocking"', cortex_text)
        case["fcs"] = fcs_match.group(1) if fcs_match else ""
        case["obj"] = obj_match.group(1) if obj_match else ""
        case["cnst_name"] = cnst_match.group(1) if cnst_match else ""
        case["cnst_blocking"] = "blocking" in cortex_text
        cases.append(case)
    return cases


def test_cortex_ai_memory(cases: List[Dict]) -> Dict:
    results = {"package": "cortex-ai-memory", "version": "2.2.0", "cases": []}
    try:
        from cortex_ai_memory import Cortex
        import tempfile
        for case in cases:
            case_result = {"case_id": case["case_id"], "errors": []}
            db_path = tempfile.mktemp(suffix='.db')
            try:
                t0 = time.time()
                c = Cortex(db_path=db_path)
                init_time = time.time() - t0
                t0 = time.time()
                c.ingest(text=case["raw"], channel="benchmark")
                ingest_time = time.time() - t0
                t0 = time.time()
                ctx = c.get_context(max_tokens=512, channel="benchmark")
                ctx_time = time.time() - t0
                t0 = time.time()
                results_q = c.retrieve(query="focus objective", limit=5, channel="benchmark")
                query_time = time.time() - t0
                ctx_lower = (ctx or "").lower()
                case_result.update({
                    "init_time": round(init_time, 4),
                    "ingest_time": round(ingest_time, 4),
                    "context_time": round(ctx_time, 4),
                    "query_time": round(query_time, 4),
                    "context_chars": len(ctx or ""),
                    "fcs_preserved": case["fcs"][:20].lower() in ctx_lower if case["fcs"] else False,
                    "obj_preserved": case["obj"][:20].lower() in ctx_lower if case["obj"] else False,
                    "cnst_preserved": case["cnst_name"].lower() in ctx_lower if case["cnst_name"] else False,
                    "context_preview": (ctx or "")[:200],
                })
            except Exception as e:
                case_result["errors"].append(f"{type(e).__name__}: {str(e)[:200]}")
            finally:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            results["cases"].append(case_result)
    except ImportError as e:
        results["error"] = f"Import failed: {e}"
    return results


def test_llm_cortex_memory(cases: List[Dict]) -> Dict:
    results = {"package": "llm-cortex-memory", "version": "1.2.0", "cases": []}
    try:
        from cortex_memory import Cortex
        for case in cases:
            case_result = {"case_id": case["case_id"], "errors": []}
            try:
                t0 = time.time()
                c = Cortex()
                init_time = time.time() - t0
                t0 = time.time()
                mem_id = c.store(text=case["raw"])
                store_time = time.time() - t0
                t0 = time.time()
                results_q = c.query(text="focus objective constraint", top_k=5)
                query_time = time.time() - t0
                stats = c.stats()
                results_text = " ".join(str(r) for r in (results_q or []))
                results_lower = results_text.lower()
                case_result.update({
                    "init_time": round(init_time, 4),
                    "store_time": round(store_time, 4),
                    "query_time": round(query_time, 4),
                    "results_count": len(results_q) if results_q else 0,
                    "fcs_preserved": case["fcs"][:20].lower() in results_lower if case["fcs"] else False,
                    "obj_preserved": case["obj"][:20].lower() in results_lower if case["obj"] else False,
                    "cnst_preserved": case["cnst_name"].lower() in results_lower if case["cnst_name"] else False,
                })
            except Exception as e:
                case_result["errors"].append(f"{type(e).__name__}: {str(e)[:200]}")
            results["cases"].append(case_result)
    except ImportError as e:
        results["error"] = f"Import failed: {e}"
    return results


def test_cortex_mem(cases: List[Dict]) -> Dict:
    results = {"package": "cortex-mem", "version": "1.0.0", "cases": [], "type": "cli_service"}
    try:
        case_result = {"case_id": "all", "errors": []}
        t0 = time.time()
        r = subprocess.run(
            [PYTHON, "-m", "cortex_mem", "status"],
            capture_output=True, text=True, timeout=10,
        )
        status_time = time.time() - t0
        case_result["status_rc"] = r.returncode
        case_result["status_time"] = round(status_time, 4)
        case_result["status_output"] = (r.stdout + r.stderr)[:300]
        case_result["note"] = "CLI service; requires running service for full per-case test"
        results["cases"].append(case_result)
    except Exception as e:
        results["error"] = str(e)
    return results


def test_cortext_memory(cases: List[Dict]) -> Dict:
    results = {"package": "cortext-memory", "version": "0.3.1", "cases": []}
    try:
        import cortex as cortext_pkg
        pkg_dir = os.path.dirname(cortext_pkg.__file__)
        case_result = {
            "case_id": "all",
            "note": "Package conflict with codec-cortex (both use 'cortex' namespace)",
            "package_files": os.listdir(pkg_dir),
        }
        schema_path = os.path.join(pkg_dir, "schema.sql")
        if os.path.exists(schema_path):
            case_result["schema"] = open(schema_path).read()[:500]
        results["cases"].append(case_result)
    except Exception as e:
        results["error"] = f"Import/analysis failed: {e}"
    return results


def test_codec_cortex(cases: List[Dict]) -> Dict:
    results = {"package": "codec-cortex", "version": "0.3.6", "cases": []}
    for case in cases:
        case_result = {"case_id": case["case_id"], "errors": []}
        cortex_path = SRC / f"{case['case_id']}.cortex"
        try:
            t0 = time.time()
            r = subprocess.run(
                [PYTHON, "-m", "cortex", "verify", str(cortex_path), "--strict"],
                capture_output=True, text=True, timeout=15,
            )
            verify_time = time.time() - t0
            t0 = time.time()
            tmp_out = f"/tmp/v221_codec_render_{case['case_id']}.md"
            subprocess.run(
                [PYTHON, "-m", "cortex", "render", str(cortex_path),
                 "--mode", "read", "--profile", "full", "--out", tmp_out],
                capture_output=True, text=True, timeout=15,
            )
            render_time = time.time() - t0
            rendered = Path(tmp_out).read_text() if os.path.exists(tmp_out) else ""
            t0 = time.time()
            r2 = subprocess.run(
                [PYTHON, "-m", "cortex", "verify-view", str(cortex_path), "--format", "json"],
                capture_output=True, text=True, timeout=15,
            )
            view_time = time.time() - t0
            view_info = json.loads(r2.stdout) if r2.returncode == 0 and r2.stdout.strip() else {}
            t0 = time.time()
            ws_path = BASE / "learning_workspaces" / case["case_id"]
            r3 = subprocess.run(
                [PYTHON, "-m", "cortex", "learn", "scan", "--workspace", str(ws_path), "--json"],
                capture_output=True, text=True, timeout=30,
            )
            learn_time = time.time() - t0
            learn_data = json.loads(r3.stdout) if r3.returncode == 0 and r3.stdout.strip() else {}
            learn_entries = learn_data.get("entries", [])
            rendered_lower = rendered.lower()
            case_result.update({
                "verify_time": round(verify_time, 4),
                "render_time": round(render_time, 4),
                "view_time": round(view_time, 4),
                "learn_time": round(learn_time, 4),
                "verify_rc": r.returncode,
                "rendered_chars": len(rendered),
                "view_coverage": view_info.get("view_coverage_percent", 0),
                "reversible": view_info.get("reversible", False),
                "learn_candidates": len(learn_entries) if isinstance(learn_entries, list) else 0,
                "fcs_preserved": case["fcs"][:20].lower() in rendered_lower if case["fcs"] else False,
                "obj_preserved": case["obj"][:20].lower() in rendered_lower if case["obj"] else False,
                "cnst_preserved": case["cnst_name"].lower() in rendered_lower if case["cnst_name"] else False,
            })
        except Exception as e:
            case_result["errors"].append(f"{type(e).__name__}: {str(e)[:200]}")
        results["cases"].append(case_result)
    return results


FEATURE_MATRIX = {
    "codec-cortex": {
        "version": "0.3.6", "summary": "Deterministic codec for .cortex structured memory with VIEW directives",
        "deterministic": True, "local_first": True, "structured_memory": True, "audit_trail": True,
        "learning_engine": True, "secret_scanner": True, "mutation_gates": True, "mcp_server": False,
        "vector_search": False, "embeddings": False, "knowledge_graph": False,
        "contradiction_aware": True, "temporal_aware": True, "token_efficient": True,
        "bidirectional": True, "cli_commands": 25, "dependencies": 0, "license": "MIT",
        "python_requires": ">=3.9", "corpus_format": ".cortex (structured attrs)",
        "profiles": "MIN/RECOVERY/WORK/FULL (P0-P5)", "scoring_algorithm": "golden_fibonacci_v1",
    },
    "cortex-ai-memory": {
        "version": "2.2.0", "summary": "Rust-based memory engine with knowledge graph, local-first",
        "deterministic": False, "local_first": True, "structured_memory": True, "audit_trail": False,
        "learning_engine": False, "secret_scanner": False, "mutation_gates": False, "mcp_server": False,
        "vector_search": True, "embeddings": True, "knowledge_graph": True,
        "contradiction_aware": False, "temporal_aware": False, "token_efficient": False,
        "bidirectional": False, "cli_commands": 0, "dependencies": 0, "license": "Proprietary",
        "python_requires": ">=3.9", "corpus_format": "Natural language (ingest)",
        "profiles": "N/A", "scoring_algorithm": "salience-based",
    },
    "cortex-mem": {
        "version": "1.0.0", "summary": "Always-On Memory Service with Progressive Disclosure L0/L1/L2",
        "deterministic": False, "local_first": True, "structured_memory": True, "audit_trail": False,
        "learning_engine": False, "secret_scanner": False, "mutation_gates": False, "mcp_server": False,
        "vector_search": True, "embeddings": True, "knowledge_graph": False,
        "contradiction_aware": False, "temporal_aware": False, "token_efficient": True,
        "bidirectional": False, "cli_commands": 5, "dependencies": 11, "license": "MIT",
        "python_requires": ">=3.10", "corpus_format": "Service-based (start/stop)",
        "profiles": "L0/L1/L2 (Progressive Disclosure)", "scoring_algorithm": "weighted retrieval",
    },
    "cortext-memory": {
        "version": "0.3.1", "summary": "Cognitive memory W5H-structured, contradiction-aware, token-efficient",
        "deterministic": True, "local_first": True, "structured_memory": True, "audit_trail": False,
        "learning_engine": False, "secret_scanner": False, "mutation_gates": False, "mcp_server": False,
        "vector_search": True, "embeddings": False, "knowledge_graph": False,
        "contradiction_aware": True, "temporal_aware": False, "token_efficient": True,
        "bidirectional": False, "cli_commands": 0, "dependencies": 5, "license": "MIT",
        "python_requires": ">=3.10", "corpus_format": "W5H (Who/What/When/Where/Why/How)",
        "profiles": "tiered_retrieval", "scoring_algorithm": "tier_generator",
    },
    "llm-cortex-memory": {
        "version": "1.2.0", "summary": "Portable model-agnostic memory layer with clustering",
        "deterministic": False, "local_first": True, "structured_memory": False, "audit_trail": False,
        "learning_engine": True, "secret_scanner": False, "mutation_gates": False, "mcp_server": False,
        "vector_search": True, "embeddings": True, "knowledge_graph": False,
        "contradiction_aware": False, "temporal_aware": False, "token_efficient": False,
        "bidirectional": False, "cli_commands": 0, "dependencies": 6, "license": "MIT",
        "python_requires": ">=3.9", "corpus_format": "Natural language (store/query)",
        "profiles": "N/A", "scoring_algorithm": "cluster-based",
    },
    "cortex-recall": {
        "version": "0.6.1", "summary": "Four-layer cognitive memory with knowledge graph and learned evolution",
        "deterministic": True, "local_first": True, "structured_memory": True, "audit_trail": False,
        "learning_engine": True, "secret_scanner": False, "mutation_gates": False, "mcp_server": False,
        "vector_search": True, "embeddings": True, "knowledge_graph": True,
        "contradiction_aware": False, "temporal_aware": False, "token_efficient": False,
        "bidirectional": False, "cli_commands": 0, "dependencies": 9, "license": "MIT",
        "python_requires": ">=3.9", "corpus_format": "Four-layer cognitive",
        "profiles": "four-layer", "scoring_algorithm": "learned evolution",
    },
    "cortex-persist": {
        "version": "1.0.0", "summary": "Cryptographic memory integrity, audit trails, verifiable lineage",
        "deterministic": False, "local_first": True, "structured_memory": True, "audit_trail": True,
        "learning_engine": False, "secret_scanner": False, "mutation_gates": False, "mcp_server": False,
        "vector_search": False, "embeddings": False, "knowledge_graph": True,
        "contradiction_aware": False, "temporal_aware": False, "token_efficient": False,
        "bidirectional": False, "cli_commands": 0, "dependencies": 48, "license": "Proprietary",
        "python_requires": ">=3.10", "corpus_format": "cryptographic lineage",
        "profiles": "N/A", "scoring_algorithm": "verifiable lineage",
    },
}


def main():
    print("Benchmark comparativo v2.2.1: CODEC-CORTEX vs PyPI comparables")
    print("=" * 70)
    cases = load_corpus_cases()
    print(f"Loaded {len(cases)} corpus cases")

    all_results = {}
    print("\n[1] Testing codec-cortex (reference)...")
    all_results["codec-cortex"] = test_codec_cortex(cases)
    n_ok = sum(1 for c in all_results["codec-cortex"]["cases"] if not c.get("errors"))
    print(f"  {n_ok}/{len(cases)} cases OK")

    print("\n[2] Testing cortex-ai-memory...")
    all_results["cortex-ai-memory"] = test_cortex_ai_memory(cases)
    n_ok = sum(1 for c in all_results["cortex-ai-memory"]["cases"] if not c.get("errors"))
    print(f"  {n_ok}/{len(cases)} cases OK")

    print("\n[3] Testing llm-cortex-memory...")
    all_results["llm-cortex-memory"] = test_llm_cortex_memory(cases)
    n_ok = sum(1 for c in all_results["llm-cortex-memory"]["cases"] if not c.get("errors"))
    print(f"  {n_ok}/{len(cases)} cases OK")

    print("\n[4] Testing cortex-mem (CLI service)...")
    all_results["cortex-mem"] = test_cortex_mem(cases)
    print(f"  Service-based; analyzed CLI")

    print("\n[5] Testing cortext-memory (namespace conflict)...")
    all_results["cortext-memory"] = test_cortext_memory(cases)
    print(f"  Analyzed package structure")

    output = {
        "benchmark_version": "2.2.1",
        "generated_at": "2026-07-02",
        "corpus_cases": len(cases),
        "packages_tested": list(all_results.keys()),
        "empirical_results": all_results,
        "feature_matrix": FEATURE_MATRIX,
    }
    out_path = RUNS / "comparative_pypi_results.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nResults written to: {out_path}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for pkg, data in all_results.items():
        if data.get("error"):
            print(f"  {pkg}: ERROR - {data['error'][:80]}")
        else:
            cases_data = data.get("cases", [])
            n_ok = sum(1 for c in cases_data if not c.get("errors"))
            n_total = len(cases_data)
            print(f"  {pkg}: {n_ok}/{n_total} cases OK")

    print("\n" + "=" * 70)
    print("FEATURE MATRIX")
    print("=" * 70)
    features = ["deterministic", "local_first", "structured_memory", "audit_trail",
                "learning_engine", "contradiction_aware", "temporal_aware",
                "token_efficient", "bidirectional"]
    print(f"{'Package':<22}", end="")
    for f in features:
        print(f"{f[:9]:<10}", end="")
    print()
    for pkg, fm in FEATURE_MATRIX.items():
        print(f"{pkg:<22}", end="")
        for f in features:
            val = fm.get(f, False)
            print(f"{'Y' if val else '-':<10}", end="")
        print()


if __name__ == "__main__":
    main()
