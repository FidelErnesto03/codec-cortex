#!/usr/bin/env python3
"""
Actualiza los .cortex del corpus v2.1.0 añadiendo el header CODEC-CORTEX
que el parser v2 (CLI v0.3.2) requiere para detectar el formato y habilitar
roundtrip-bidir, convert, y otros comandos v2.

También normaliza los status:cur -> status:"current" en VIEW directives
para que verify --strict del CLI v1.x legacy los acepte.

Estrategia:
1. Añadir header <!-- CODEC-CORTEX ... --> al inicio de cada .cortex
2. Reemplazar status:cur por status:"current" en VIEW directives
3. Validar con cortex verify (sin --strict para permitir warnings)
4. Validar con cortex verify-view (debe reportar 100% coverage, reversible=True)
"""

from pathlib import Path
import re
import shutil
import subprocess

SRC = Path("/home/z/my-project/download/benchmark-cortex-v21/corpus/source")
BACKUP = Path("/home/z/my-project/download/benchmark-cortex-v21/corpus/source_pre_header_backup")
BACKUP.mkdir(exist_ok=True)

PYTHON = "/home/z/.venv/bin/python"
CORTEX_CLI = [PYTHON, "-m", "cortex"]


def update_cortex_file(path: Path) -> bool:
    """Add CODEC-CORTEX header and fix status:cur in VIEW directives."""
    content = path.read_text(encoding="utf-8")

    # Backup
    backup_path = BACKUP / path.name
    if not backup_path.exists():
        shutil.copy2(path, backup_path)

    # Fix status:cur -> status:"current" in VIEW directives (and others)
    # Pattern: status:cur followed by , or }
    content = re.sub(r'status:cur([,}])', r'status:"current"\1', content)
    content = re.sub(r'status:pln([,}])', r'status:"planned"\1', content)
    content = re.sub(r'status:fut([,}])', r'status:"future"\1', content)
    content = re.sub(r'status:blk([,}])', r'status:"blocked"\1', content)

    # Add CODEC-CORTEX header if not present
    if "<!-- CODEC-CORTEX" not in content:
        header = f"""<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: benchmark corpus v2.1.0
status: specification
-->

"""
        content = header + content

    path.write_text(content, encoding="utf-8")
    return True


def main():
    print("Updating .cortex files for v2.1.0 (adding CODEC-CORTEX header, fixing status)...")

    updated = 0
    for cortex_file in sorted(SRC.glob("*.cortex")):
        update_cortex_file(cortex_file)
        updated += 1
        print(f"  UPDATED: {cortex_file.name}")

    print(f"\nTotal: {updated} files updated")
    print(f"Backup: {BACKUP}")

    # Validate with cortex verify (not strict, to allow warnings)
    print("\n=== Validation with cortex verify (non-strict) ===")
    all_ok = True
    for cortex_file in sorted(SRC.glob("*.cortex")):
        r = subprocess.run(
            CORTEX_CLI + ["verify", str(cortex_file)],
            capture_output=True, text=True, timeout=15,
        )
        # Count errors (not warnings)
        errors = [l for l in r.stdout.split("\n") if "error" in l.lower() and "[" in l]
        status = "OK" if r.returncode == 0 or not errors else "FAIL"
        print(f"  [{status}] {cortex_file.name}: rc={r.returncode}, errors={len(errors)}")
        if errors:
            all_ok = False
            for e in errors[:3]:
                print(f"    {e.strip()}")

    # Validate with cortex verify-view
    print("\n=== Validation with cortex verify-view ===")
    for cortex_file in sorted(SRC.glob("*.cortex")):
        r = subprocess.run(
            CORTEX_CLI + ["verify-view", str(cortex_file), "--format", "json"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0 and r.stdout.strip():
            import json
            data = json.loads(r.stdout)
            cov = data.get("view_coverage_percent", 0)
            rev = data.get("reversible", False)
            uncov = data.get("uncovered_count", 0)
            status = "OK" if cov == 100.0 and rev else "WARN"
            print(f"  [{status}] {cortex_file.name}: coverage={cov}%, reversible={rev}, uncovered={uncov}")
        else:
            print(f"  [FAIL] {cortex_file.name}: rc={r.returncode}")

    # Test roundtrip-bidir on first file
    print("\n=== Test roundtrip-bidir on devops-k8s-rollout.cortex ===")
    test_file = SRC / "devops-k8s-rollout.cortex"
    r = subprocess.run(
        CORTEX_CLI + ["roundtrip-bidir", str(test_file)],
        capture_output=True, text=True, timeout=30,
    )
    print(f"  rc={r.returncode}")
    if r.stdout:
        # Show last 10 lines
        for line in r.stdout.strip().split("\n")[-10:]:
            print(f"  {line}")
    if r.stderr:
        print(f"  stderr: {r.stderr[:200]}")

    # Test convert
    print("\n=== Test convert on devops-k8s-rollout.cortex ===")
    r = subprocess.run(
        CORTEX_CLI + ["convert", "--from", "cortex", "--to", "hcortex",
                       str(test_file), "--out", "/tmp/v21_convert_test.md"],
        capture_output=True, text=True, timeout=15,
    )
    import os
    if os.path.exists("/tmp/v21_convert_test.md"):
        size = os.path.getsize("/tmp/v21_convert_test.md")
        print(f"  Output size: {size} bytes")
        if size > 1000:
            print("  ✓ v2-convert produces substantial HCORTEX output")
        else:
            print("  ⚠ Output still small")

    # Test canonicalize
    print("\n=== Test canonicalize --preserve ===")
    r = subprocess.run(
        CORTEX_CLI + ["canonicalize", "--preserve", str(test_file),
                       "--out", "/tmp/v21_canon_test.cortex"],
        capture_output=True, text=True, timeout=15,
    )
    print(f"  rc={r.returncode}")
    if r.stdout:
        print(f"  stdout: {r.stdout.strip()[:200]}")


if __name__ == "__main__":
    main()
