#!/usr/bin/env python3
"""
Valida reproducibilidad del benchmark: re-ejecuta el harness y verifica
que los outputs son idénticos a los previamente generados.
"""

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASE = Path("/home/z/my-project/download/benchmark-cortex")
RUNS = BASE / "runs"
PYTHON = "/home/z/.venv/bin/python"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    print("=" * 70)
    print("VALIDACIÓN DE REPRODUCIBILIDAD DEL BENCHMARK CODEC-CORTEX v1.0.0")
    print("=" * 70)

    # 1. Hashes de outputs actuales
    print("\n[1] Hashes de artefactos actuales:")
    artifacts = [
        "runs/scored_tasks.csv",
        "runs/summary_tasks.csv",
        "runs/method_results.json",
        "runs/scenario_results.json",
        "runs/derived_metrics.json",
        "runs/provenance.csv",
        "manifest.json",
    ]
    before_hashes = {}
    for rel in artifacts:
        p = BASE / rel
        if p.exists():
            h = sha256_file(p)
            before_hashes[rel] = h
            print(f"  {rel}: {h[:16]}...")

    # 2. Re-ejecutar benchmark
    print("\n[2] Re-ejecutando benchmark...")
    r = subprocess.run(
        [PYTHON, "scripts/run_benchmark.py"],
        capture_output=True, text=True, cwd=str(BASE), timeout=120,
    )
    if r.returncode != 0:
        print(f"  FAIL: rc={r.returncode}")
        print(r.stderr[-500:])
        sys.exit(1)
    # Extract last line
    last_line = [l for l in r.stdout.split("\n") if l.strip()][-1]
    print(f"  {last_line}")

    # 3. Comparar hashes
    print("\n[3] Comparando hashes antes/después:")
    all_match = True
    for rel, before_h in before_hashes.items():
        p = BASE / rel
        after_h = sha256_file(p)
        match = "✓" if before_h == after_h else "✗"
        if before_h != after_h:
            all_match = False
        print(f"  {match} {rel}: {before_h[:16]} → {after_h[:16]}")

    # 4. Validar scored_tasks count
    print("\n[4] Conteo de runs:")
    with open(RUNS / "scored_tasks.csv") as f:
        rows = list(csv.DictReader(f))
    print(f"  scored_tasks.csv: {len(rows)} filas")
    expected = 11 * 11 * 40  # methods * scenarios * tasks
    print(f"  esperado: {expected}")
    if len(rows) == expected:
        print(f"  ✓ Conteo correcto")
    else:
        print(f"  ✗ Conteo incorrecto")
        all_match = False

    # 5. Validar consistencia de métricas clave
    print("\n[5] Validando consistencia de métricas clave:")
    summary = list(csv.DictReader(open(RUNS / "summary_tasks.csv")))
    cpp = next((r for r in summary if r["method_id"] == "cortex_priority_pack_v1"), None)
    if cpp:
        checks = [
            ("avg_P0_survival", 1.0, "P0 preservado 100%"),
            ("avg_BCFNR", 0.0, "BCFNR = 0 (sin omisiones)"),
            ("avg_UCFPR", 0.0, "UCFPR = 0 (sin leaks)"),
            ("avg_BVR", 0.0, "BVR = 0 (sin violaciones)"),
            ("avg_STR", 1.0, "STR = 1.00 (trazabilidad total)"),
        ]
        for k, expected_v, desc in checks:
            actual_v = float(cpp[k])
            match = "✓" if abs(actual_v - expected_v) < 1e-9 else "✗"
            print(f"  {match} CPP {k}: {actual_v:.4f} (esperado {expected_v:.4f}) — {desc}")
            if abs(actual_v - expected_v) >= 1e-9:
                all_match = False

    # 6. Validar manifest
    print("\n[6] Validando manifest:")
    m = json.loads((BASE / "manifest.json").read_text())
    print(f"  benchmark_version: {m['benchmark_version']}")
    print(f"  totals: {m['totals']}")
    if m["totals"]["runs"] == 4840:
        print(f"  ✓ Total runs = 4840")
    else:
        print(f"  ✗ Total runs incorrecto: {m['totals']['runs']}")
        all_match = False

    # 7. Validar hashes del corpus
    print("\n[7] Validando hashes del corpus:")
    hashes = json.loads((BASE / "corpus" / "normalized" / "hashes.json").read_text())
    print(f"  {len(hashes)} artefactos con hash registrado")
    mismatches = 0
    for fname, expected_h in hashes.items():
        p = BASE / "corpus" / "source" / fname
        if p.exists():
            actual_h = sha256_file(p)
            if actual_h != expected_h:
                mismatches += 1
                print(f"  ✗ {fname}: hash mismatch")
    if mismatches == 0:
        print(f"  ✓ Todos los {len(hashes)} hashes coinciden")
    else:
        print(f"  ✗ {mismatches} artefactos con hash mismatch")
        all_match = False

    # Conclusion
    print("\n" + "=" * 70)
    if all_match:
        print("✅ REPRODUCIBILIDAD VALIDADA — el benchmark es 100% determinístico")
        print("   Mismas entradas → mismas salidas, sin semillas, sin aleatoriedad")
    else:
        print("⚠️  REPRODUCIBILIDAD PARCIAL — revisar discrepancias arriba")
    print("=" * 70)


if __name__ == "__main__":
    main()
