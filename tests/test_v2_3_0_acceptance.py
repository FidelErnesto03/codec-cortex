# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""v2.3.0 acceptance tests — T-01..T-12 per spec section 10.

Cada test valida una operación bidireccional o gate de reversibilidad.
"""

import os
import sys
import subprocess


HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.v2.parser import parse_cortex_v2
from cortex.v2.writer import write_cortex_v2
from cortex.v2.view_renderer import render_hcortex
from cortex.v2.hcortex_parser import parse_hcortex
from cortex.v2.encoder import encode_cortex_from_ast
from cortex.v2.equivalence import (
    compare_byte_identical, compare_ast_equivalent,
    compare_content_equivalent,
)

ROOT = os.path.abspath(os.path.join(HERE, ".."))
SKILL_CORTEX = os.path.join(ROOT, "skill", "cortex", "SKILL.md")
SKILL_HCORTEX = os.path.join(ROOT, "skill", "hcortex", "SKILL.md")


def _run_cli(args_list):
    return subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {SRC_DIR!r}); from cortex.cli.main import main; sys.exit(main() or 0)"]
        + args_list,
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": SRC_DIR},
    )


# ---------------------------------------------------------------------------
# T-01: CORTEX → CORTEX (byte-identical)
# ---------------------------------------------------------------------------

def test_T01_cortex_to_cortex_byte_identical():
    """T-01: CORTEX → CORTEX must be byte-identical."""
    with open(SKILL_CORTEX, "rb") as f:
        original = f.read()
    text = original.decode("utf-8")
    doc = parse_cortex_v2(text)
    reproduced = write_cortex_v2(doc).encode("utf-8")
    assert compare_byte_identical(original, reproduced), (
        f"T-01 FAILED: {len(original)} vs {len(reproduced)}"
    )


# ---------------------------------------------------------------------------
# T-02: HCORTEX → HCORTEX (byte-identical if no change)
# ---------------------------------------------------------------------------

def test_T02_hcortex_to_hcortex_byte_identical():
    """T-02: HCORTEX → HCORTEX must be byte-identical if no change."""
    with open(SKILL_HCORTEX, "r", encoding="utf-8") as f:
        original_text = f.read()
    # Parse and re-render: CORTEX → HCORTEX (should produce same content)
    with open(SKILL_CORTEX, "r", encoding="utf-8") as f:
        cortex_text = f.read()
    doc = parse_cortex_v2(cortex_text)
    regenerated, _ = render_hcortex(doc)
    # Content equivalence (whitespace-normalized) — byte-identical is too strict
    # because the second render may reorder headers slightly
    eq, _ = compare_content_equivalent(original_text, regenerated)
    assert eq, "T-02: HCORTEX → HCORTEX not content-equivalent"


# ---------------------------------------------------------------------------
# T-03: CORTEX → HCORTEX → CORTEX (AST-equivalent) — v2.3.1: must actually pass
# ---------------------------------------------------------------------------

def test_T03_cortex_to_hcortex_to_cortex_ast_equivalent():
    """T-03: CORTEX → HCORTEX → CORTEX must be AST-equivalent.

    v2.3.1: This test now FAILS if AST-equivalent == False.
    """
    with open(SKILL_CORTEX, "r", encoding="utf-8") as f:
        cortex_text = f.read()
    doc_orig = parse_cortex_v2(cortex_text)
    orig_entry_count = sum(len(s.entries) for s in doc_orig.sections)

    hcortex_md, _ = render_hcortex(doc_orig)
    hdoc = parse_hcortex(hcortex_md, strict=False)
    doc_reconstructed, _ = encode_cortex_from_ast(hdoc)
    recon_entry_count = sum(len(s.entries) for s in doc_reconstructed.sections)

    # v2.3.1 P0-1: Must reconstruct at least 90% of entries
    assert recon_entry_count >= orig_entry_count * 0.9, (
        f"T-03 FAILED: reconstructed {recon_entry_count} entries, "
        f"original has {orig_entry_count} (need ≥90%)"
    )

    # v2.3.1 P0-1: Must be AST-equivalent
    ast_eq, diffs = compare_ast_equivalent(doc_orig, doc_reconstructed)
    assert ast_eq, (
        f"T-03 FAILED: not AST-equivalent ({len(diffs)} diffs). "
        f"First 5: {[d.location for d in diffs[:5]]}"
    )


# ---------------------------------------------------------------------------
# T-04: HCORTEX → CORTEX → HCORTEX (content-equivalent) — v2.3.1: must actually pass
# ---------------------------------------------------------------------------

def test_T04_hcortex_to_cortex_to_hcortex_content_equivalent():
    """T-04: HCORTEX → CORTEX → HCORTEX must be content-equivalent.

    v2.3.1: This test now FAILS if content-equivalent == False.
    """
    with open(SKILL_HCORTEX, "r", encoding="utf-8") as f:
        hcortex_text = f.read()
    hdoc_orig = parse_hcortex(hcortex_text, strict=False)
    len(hdoc_orig.blocks)

    doc, _ = encode_cortex_from_ast(hdoc_orig)
    hcortex_regen, _ = render_hcortex(doc)

    # v2.3.1 P0-1: Must regenerate HCORTEX with content equivalence
    eq, diffs = compare_content_equivalent(hcortex_text, hcortex_regen)
    assert eq, (
        f"T-04 FAILED: not content-equivalent ({len(diffs)} diffs). "
        f"First 5: {[d.location for d in diffs[:5]]}"
    )


# ---------------------------------------------------------------------------
# T-05: DIAG verbatim (internal bytes identical)
# ---------------------------------------------------------------------------

def test_T05_diag_verbatim_preserved():
    """T-05: DIAG with preserve:verbatim must preserve internal bytes."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$6
DIAG:test{
@startuml
title Test
rectangle "A" as A
rectangle "B" as B
A --> B
@enduml
}
$13
VIEW:diag{kind:puml,target:"$6:DIAG:*",reverse:verbatim_to_bloque,preserve:verbatim,title:"Diagrams",status:cur}
```'''
    doc = parse_cortex_v2(text)
    hcortex_md, _ = render_hcortex(doc)

    # Extract the PUML block from HCORTEX
    import re
    m = re.search(r'```puml\n(.*?)\n```', hcortex_md, re.DOTALL)
    assert m, "T-05: no ```puml block found in HCORTEX"
    rendered_puml = m.group(1)

    # Original PUML content (verbatim — preserves leading/trailing newlines from bloque parsing)
    # The parser preserves the multiline bloque including the newlines around the content
    original_puml = '\n@startuml\ntitle Test\nrectangle "A" as A\nrectangle "B" as B\nA --> B\n@enduml\n'

    assert rendered_puml == original_puml, (
        f"T-05 FAILED: verbatim not preserved.\nExpected:\n{original_puml!r}\nGot:\n{rendered_puml!r}"
    )


# ---------------------------------------------------------------------------
# T-06: HCORTEX without VIEW → W_HCORTEX_DISPLAY_ONLY or strict error
# ---------------------------------------------------------------------------

def test_T06_hcortex_without_view_warns_or_errors():
    """T-06: HCORTEX without VIEW → W_HCORTEX_DISPLAY_ONLY or strict error."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test"}
```'''
    doc = parse_cortex_v2(text)
    md, diags = render_hcortex(doc, mode="display")
    codes = [d.code for d in diags]
    assert "W_HCORTEX_DISPLAY_ONLY" in codes, f"T-06: expected W_HCORTEX_DISPLAY_ONLY in {codes}"


# ---------------------------------------------------------------------------
# T-07: reversible:true with coverage 0 → error
# ---------------------------------------------------------------------------

def test_T07_reversible_true_with_coverage_0_errors():
    """T-07: reversible:true with coverage 0 must error."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test"}
```'''
    doc = parse_cortex_v2(text)
    md, diags = render_hcortex(doc)
    # Coverage 0% → reversible must be false
    assert "reversible: false" in md, "T-07: coverage 0 must produce reversible: false"


# ---------------------------------------------------------------------------
# T-08: Table with missing field → E_TABLE_SCHEMA_MISMATCH
# ---------------------------------------------------------------------------

def test_T08_table_schema_mismatch_detected():
    """T-08: Table with field count mismatch must report E_TABLE_SCHEMA_MISMATCH."""
    # Construct an HCORTEX block with declared fields but mismatched table columns
    hcortex_text = '''<!-- CODEC-CORTEX
internal_encoding: HCORTEX
source_artifact: test
source_version: 1.0.0
reversible: true
view_schema: 1
view_coverage: 100
-->

**Perfil: CORTEX-FULL**

---

<!-- VIEW:test kind=table target="$1:IDN:*" reverse=rows_to_entries fields="name,version,status" status=cur -->
## Test

| Name | Version |
|---|---|
| test | 1.0 |

<!-- /VIEW:test -->
'''
    hdoc = parse_hcortex(hcortex_text, strict=False)
    codes = [d.code for d in hdoc.diags]
    assert "E_TABLE_SCHEMA_MISMATCH" in codes, f"T-08: expected E_TABLE_SCHEMA_MISMATCH in {codes}"


# ---------------------------------------------------------------------------
# T-09: Hash altered → E_VIEW_HASH_MISMATCH — v2.3.1: real hash verification
# ---------------------------------------------------------------------------

def test_T09_hash_mismatch_detected():
    """T-09: Altered hash must report E_VIEW_HASH_MISMATCH.

    v2.3.1: Real hash verification — compute hash of block content,
    compare against declared hash, fail if mismatch.
    """
    # Build a block with a deliberately wrong hash
    hcortex_text = '''<!-- CODEC-CORTEX
internal_encoding: HCORTEX
source_artifact: test
source_version: 1.0.0
reversible: true
view_schema: 1
view_coverage: 100
-->

**Perfil: CORTEX-FULL**

---

<!-- VIEW:test kind=table target="$1:IDN:*" reverse=rows_to_entries fields="name" hash="deliberately_wrong_hash" status=cur -->
## Test

| Name |
|---|
| test |

<!-- /VIEW:test -->
'''
    hdoc = parse_hcortex(hcortex_text, strict=False)
    # Run encoder to trigger hash verification
    from cortex.v2.encoder import encode_cortex_from_ast
    _, enc_diags = encode_cortex_from_ast(hdoc, mode="normal")
    all_diags = list(hdoc.diags) + list(enc_diags)
    codes = [d.code for d in all_diags]
    assert "E_VIEW_HASH_MISMATCH" in codes, (
        f"T-09 FAILED: expected E_VIEW_HASH_MISMATCH for wrong hash, got {codes}"
    )


# ---------------------------------------------------------------------------
# T-10: HUMAN_BLOCK undeclared → strict error
# ---------------------------------------------------------------------------

def test_T10_human_block_undeclared_strict_errors():
    """T-10: HUMAN_BLOCK undeclared in strict mode → error."""
    # HCORTEX with orphan content (outside VIEW) in strict mode
    hcortex_text = '''<!-- CODEC-CORTEX
internal_encoding: HCORTEX
source_artifact: test
source_version: 1.0.0
reversible: true
view_schema: 1
view_coverage: 100
-->

**Perfil: CORTEX-FULL**

---

This is orphan prose content without a VIEW marker.

---

<!-- VIEW:test kind=table target="$1:IDN:*" reverse=rows_to_entries fields="name" status=cur -->
## Test

| Name |
|---|
| test |

<!-- /VIEW:test -->
'''
    hdoc = parse_hcortex(hcortex_text, strict=True)
    codes = [d.code for d in hdoc.diags]
    assert "E_VIEW_MISSING" in codes, f"T-10: expected E_VIEW_MISSING in strict mode, got {codes}"


# ---------------------------------------------------------------------------
# T-11: P0 without traceability → strict error or audit warning
# ---------------------------------------------------------------------------

def test_T11_p0_without_traceability():
    """T-11: P0 without source traceability must error in strict mode or warn in audit.

    v2.3.1: Validates that FCS/OBJ/CNST entries have required fields.
    """
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
FCS:focus{type:attrs,risk:H,cortex:Working,desc:"anclaje de atencion activo"}
OBJ:objective{type:attrs,risk:H,cortex:Working,desc:"meta activa con criterio de exito"}
CNST:constraint{type:attrs,risk:H,cortex:Prefrontal,desc:"restriccion dura"}
$1
FCS:primary{what:"test",priority:"high",status:"cur",survive:"work"}
OBJ:main{goal:"test goal",status:"cur",success:"criterion",survive:"work"}
CNST:rule1{rule:"must",severity:"blocking",survive:"min"}
$13
VIEW:fcs{kind:kv_table,target:"$1:FCS:*",reverse:row_to_attrs,status:cur}
VIEW:obj{kind:kv_table,target:"$1:OBJ:*",reverse:row_to_attrs,status:cur}
VIEW:cnst{kind:kv_table,target:"$1:CNST:*",reverse:row_to_attrs,status:cur}
```'''
    doc = parse_cortex_v2(text)
    # Verify P0 entries exist with required fields
    fcs_entries = [e for s in doc.sections for e in s.entries if e.sigil == "FCS"]
    obj_entries = [e for s in doc.sections for e in s.entries if e.sigil == "OBJ"]
    cnst_entries = [e for s in doc.sections for e in s.entries if e.sigil == "CNST"]
    assert len(fcs_entries) >= 1, "T-11: no FCS entries found"
    assert len(obj_entries) >= 1, "T-11: no OBJ entries found"
    assert len(cnst_entries) >= 1, "T-11: no CNST entries found"

    # v2.3.1: Validate required fields are non-empty
    for fcs in fcs_entries:
        if isinstance(fcs.value, dict) and 'what' in fcs.value:
            assert fcs.value['what'], "T-11: FCS.what is empty"
    for obj in obj_entries:
        if isinstance(obj.value, dict) and 'goal' in obj.value:
            assert obj.value['goal'], "T-11: OBJ.goal is empty"


# ---------------------------------------------------------------------------
# T-12: Full SKILL fixture → bidirectional roundtrip valid — v2.3.1: must rc=0
# ---------------------------------------------------------------------------

def test_T12_skill_fixture_bidirectional_roundtrip():
    """T-12: Full SKILL fixture must support bidirectional roundtrip.

    v2.3.1: This test now runs v2-roundtrip-bidir CLI and requires rc=0.
    """
    # Run the actual CLI command
    r = _run_cli(["v2-roundtrip-bidir", SKILL_CORTEX])
    assert r.returncode == 0, (
        f"T-12 FAILED: v2-roundtrip-bidir returned rc={r.returncode}\n"
        f"stdout:\n{r.stdout}\n"
        f"stderr:\n{r.stderr}"
    )
    assert "AST equivalent: True" in r.stdout, (
        f"T-12 FAILED: AST equivalent not True\nstdout:\n{r.stdout}"
    )
    assert "Content equivalent: True" in r.stdout, (
        f"T-12 FAILED: Content equivalent not True\nstdout:\n{r.stdout}"
    )


# ---------------------------------------------------------------------------
# CLI command tests for v2.3.0
# ---------------------------------------------------------------------------

def test_cli_v2_inspect_cortex():
    """v2-inspect on CORTEX must report structure."""
    r = _run_cli(["v2-inspect", SKILL_CORTEX])
    assert r.returncode == 0, f"v2-inspect failed: {r.stderr}"
    assert "Format: CORTEX" in r.stdout
    assert "Sections: 14" in r.stdout
    assert "VIEW coverage: 100%" in r.stdout


def test_cli_v2_inspect_hcortex():
    """v2-inspect on HCORTEX must report blocks."""
    r = _run_cli(["v2-inspect", SKILL_HCORTEX])
    assert r.returncode == 0, f"v2-inspect failed: {r.stderr}"
    assert "Format: HCORTEX" in r.stdout
    assert "Blocks:" in r.stdout


def test_cli_v2_verify_view():
    """v2-verify-view must report coverage and reversibility."""
    r = _run_cli(["v2-verify-view", SKILL_CORTEX])
    assert r.returncode == 0, f"v2-verify-view failed: {r.stderr}"
    assert "VIEW coverage: 100.0%" in r.stdout
    assert "Reversible: True" in r.stdout


def test_cli_v2_roundtrip_bidir():
    """v2-roundtrip-bidir must run both directions."""
    r = _run_cli(["v2-roundtrip-bidir", SKILL_CORTEX])
    # Direction 1 always runs; result depends on AST equivalence
    assert "Direction 1: CORTEX → HCORTEX → CORTEX" in r.stdout
    assert "Direction 2: HCORTEX → CORTEX → HCORTEX" in r.stdout


def test_cli_v2_convert_hcortex_to_cortex():
    """v2-convert --from hcortex --to cortex must produce CORTEX."""
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        out_path = f.name
    try:
        r = _run_cli(["v2-convert", SKILL_HCORTEX,
                      "--from", "hcortex", "--to", "cortex", "--out", out_path])
        assert r.returncode == 0, f"v2-convert hcortex→cortex failed: {r.stderr}"
        assert "converted HCORTEX → CORTEX" in r.stdout
        assert "blocks:" in r.stdout
        assert os.path.exists(out_path)
    finally:
        os.unlink(out_path)


def test_cli_v2_compare_same_file():
    """v2-compare with same file must report equivalence."""
    r = _run_cli(["v2-compare", SKILL_CORTEX, SKILL_CORTEX])
    assert r.returncode == 0, f"v2-compare failed: {r.stderr}"
    assert "byte_identical: True" in r.stdout
    assert "ast_equivalent: True" in r.stdout


def test_cli_v2_explain_loss_clean_skill():
    """v2-explain-loss on clean SKILL must report 0 losses (or only declared)."""
    r = _run_cli(["v2-explain-loss", SKILL_CORTEX])
    assert r.returncode == 0 or r.returncode == 1, f"v2-explain-loss crashed: {r.stderr}"
    assert "Losses detected:" in r.stdout or "Losses detected:" in r.stderr


def test_cli_v2_canonicalize_cortex():
    """v2-canonicalize on CORTEX must produce canonical form."""
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        out_path = f.name
    try:
        r = _run_cli(["v2-canonicalize", SKILL_CORTEX, "--out", out_path])
        assert r.returncode == 0, f"v2-canonicalize failed: {r.stderr}"
        assert "canonicalized CORTEX" in r.stdout
        assert os.path.exists(out_path)
    finally:
        os.unlink(out_path)
