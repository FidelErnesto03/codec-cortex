#!/usr/bin/env python3
"""
Actualiza el corpus v1.0.0 a v2.0.0 añadiendo VIEW directives a cada .cortex.

Las VIEW directives son el mecanismo v2 para mapear entradas CORTEX a HCORTEX.
Sin VIEW, v2-convert produce HCORTEX vacío.

Estrategia: para cada .cortex del corpus, añadir un bloque VIEW al final que
mapee cada sigilo a su representación HCORTEX canónica.
"""

from pathlib import Path
import re
import shutil

SRC = Path("/home/z/my-project/download/benchmark-cortex-v2/corpus/source")
BACKUP = Path("/home/z/my-project/download/benchmark-cortex-v2/corpus/source_v1_backup")
BACKUP.mkdir(exist_ok=True)

# VIEW template: maps each sigil to its HCORTEX rendering
# Format: VIEW:name{kind:"kv_table|table|prose", target:"$N/SIGIL:name", reverse:"...", status:cur, title:"..."}
VIEW_TEMPLATE = """
$99: HCORTEX_VIEWS

VIEW:idn_view{kind:"kv_table", target:"$1/IDN", reverse:"row_to_attrs", title:"Identity"}
VIEW:dom_view{kind:"kv_table", target:"$1/DOM", reverse:"row_to_attrs", title:"Domain"}
VIEW:cnst_view{kind:"kv_table", target:"$2/CNST", reverse:"row_to_attrs", title:"Constraints"}
VIEW:fcs_view{kind:"kv_table", target:"$2/FCS", reverse:"row_to_attrs", title:"Focus"}
VIEW:obj_view{kind:"kv_table", target:"$2/OBJ", reverse:"row_to_attrs", title:"Objective"}
VIEW:wrk_view{kind:"kv_table", target:"$2/WRK", reverse:"row_to_attrs", title:"Work State"}
VIEW:stp_view{kind:"kv_table", target:"$2/STP", reverse:"row_to_attrs", title:"Next Step"}
VIEW:nxt_view{kind:"kv_table", target:"$4/NXT", reverse:"row_to_attrs", title:"Queued Actions"}
VIEW:audit_view{kind:"kv_table", target:"$3/AUD", reverse:"row_to_attrs", title:"Audit"}
VIEW:rsk_view{kind:"kv_table", target:"$3/RSK", reverse:"row_to_attrs", title:"Risks"}
VIEW:claim_view{kind:"kv_table", target:"$5/CLAIM", reverse:"row_to_attrs", title:"Claims"}
VIEW:lim_view{kind:"kv_table", target:"$5/LIM", reverse:"row_to_attrs", title:"Limits"}
VIEW:ref_view{kind:"kv_table", target:"$4/REF", reverse:"row_to_attrs", title:"References"}
VIEW:ses_view{kind:"kv_table", target:"$3/SES", reverse:"row_to_attrs", title:"Sessions"}
VIEW:lng_view{kind:"kv_table", target:"$4/LNG", reverse:"row_to_attrs", title:"Lessons"}
VIEW:knw_view{kind:"kv_table", target:"$5/KNW", reverse:"row_to_attrs", title:"Knowledge"}
"""


def update_cortex_file(path: Path) -> bool:
    """Add VIEW directives to a .cortex file. Returns True if updated."""
    content = path.read_text(encoding="utf-8")
    # Skip if already has VIEW block
    if "$VIEW:" in content:
        return False
    # Add VIEW sigil to $0 glossary if not present
    if "# VIEW " not in content and "# VIEW|" not in content:
        # Add VIEW declaration after the last glossary line (before $1: section)
        # Format: # Sigil | Name | Type | Risk | Cognitive Layer | Description
        content = re.sub(
            r'(\n)(\$1: )',
            r'\n# VIEW | view       | attrs | M | Prefrontal  | HCORTEX view mapping directive\n\1\2',
            content,
            count=1,
        )
    # Append VIEW block at the end
    new_content = content.rstrip() + "\n" + VIEW_TEMPLATE
    # Backup original (only if not already backed up)
    backup_path = BACKUP / path.name
    if not backup_path.exists():
        shutil.copy2(path, backup_path)
    # Write updated
    path.write_text(new_content, encoding="utf-8")
    return True


def main():
    print("Updating corpus .cortex files to v2.0.0 (adding VIEW directives)...")
    updated = 0
    skipped = 0
    for cortex_file in sorted(SRC.glob("*.cortex")):
        if update_cortex_file(cortex_file):
            updated += 1
            print(f"  UPDATED: {cortex_file.name}")
        else:
            skipped += 1
            print(f"  SKIPPED (already has VIEW): {cortex_file.name}")

    print(f"\nTotal: {updated} updated, {skipped} skipped")
    print(f"Backup of v1 originals: {BACKUP}")

    # Validate updated files
    print("\nValidating updated files with cortex verify --strict...")
    import subprocess
    all_ok = True
    for cortex_file in sorted(SRC.glob("*.cortex")):
        r = subprocess.run(
            ["/home/z/.venv/bin/python", "-m", "cortex", "verify",
             str(cortex_file), "--strict"],
            capture_output=True, text=True, timeout=15,
        )
        # Extract last line
        last = r.stdout.strip().split("\n")[-1] if r.stdout else r.stderr.strip().split("\n")[-1]
        status = "OK" if r.returncode == 0 else "FAIL"
        print(f"  {status} {cortex_file.name}: {last}")
        if r.returncode != 0:
            all_ok = False

    if all_ok:
        print("\n✓ All .cortex files pass verify --strict")
    else:
        print("\n⚠ Some files failed validation")

    # Test v2-convert on updated file
    print("\nTesting v2-convert on updated devops-k8s-rollout.cortex...")
    r = subprocess.run(
        ["/home/z/.venv/bin/python", "-m", "cortex", "v2-convert",
         "--from", "cortex", "--to", "hcortex",
         str(SRC / "devops-k8s-rollout.cortex"), "--out", "/tmp/test_v2_updated.md"],
        capture_output=True, text=True, timeout=15,
    )
    import os
    if os.path.exists("/tmp/test_v2_updated.md"):
        size = os.path.getsize("/tmp/test_v2_updated.md")
        print(f"  Output size: {size} bytes (was 251 before VIEW)")
        if size > 1000:
            print("  ✓ v2-convert now produces substantial HCORTEX output")
        else:
            print("  ⚠ Output still small")
    if r.stderr:
        print(f"  stderr: {r.stderr[:200]}")


if __name__ == "__main__":
    main()
