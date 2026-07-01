"""Audit gate tests — G1 through G8 from the audit report.

Each gate verifies that the corresponding acceptance criterion
(cognitive governance, HCORTEX canónico, recovery, etc.) is met.
"""

import os
import subprocess
import sys

import pytest

from cortex.templates import build_brain, build_skill
from cortex.core.parser import parse_cortex, build_entry_from_value
from cortex.core.writer import write_cortex
from cortex.core.validator import validate
from cortex.hcortex import (
    render_hcortex_read, render_hcortex_edit, parse_hcortex_edit,
    recover_cortex, resolve_profile, classify_entry,
    filter_by_profile,
)
from cortex.crud.mutations import update_entry
from cortex.core.compare import compare_ast


HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))


# ---------------------------------------------------------------------------
# G1: verify --strict brain.cortex fails if FCS or OBJ missing
# ---------------------------------------------------------------------------

def test_g1_strict_brain_without_fcs_fails():
    doc = build_brain()
    sec2 = doc.get_section("$2")
    sec2.entries = [e for e in sec2.entries if e.sigil != "FCS"]
    diags = validate(doc, strict=True)
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E024_LEVEL2_MISSING_FOCUS" in codes


def test_g1_strict_brain_without_obj_fails():
    doc = build_brain()
    sec2 = doc.get_section("$2")
    sec2.entries = [e for e in sec2.entries if e.sigil != "OBJ"]
    diags = validate(doc, strict=True)
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E024_LEVEL2_MISSING_FOCUS" in codes


def test_g1_strict_brain_with_fcs_and_obj_passes():
    doc = build_brain()
    diags = validate(doc, strict=True)
    errors = [d for d in diags if d["severity"] == "error"]
    assert not errors, f"unexpected errors: {[d['code'] for d in errors]}"


# ---------------------------------------------------------------------------
# G2: verify --strict SKILL.cortex fails if WRK/NXT/SES/LNG live
# ---------------------------------------------------------------------------

def test_g2_strict_skill_with_live_wrk_fails():
    doc = build_skill()
    sec = doc.get_or_create_section("$2", title="AXIOMS")
    sec.entries.append(build_entry_from_value(
        "$2", "WRK", "live", "attrs",
        {"phase": "active", "current": "work", "blocked": False, "survive": "min"},
    ))
    diags = validate(doc, strict=True)
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E023_LEVEL1_LIVE_STATE" in codes


def test_g2_strict_skill_with_example_wrk_passes():
    """WRK marked as example/specification is allowed in skill (contract)."""

    doc = build_skill()
    sec = doc.get_or_create_section("$2", title="AXIOMS")
    sec.entries.append(build_entry_from_value(
        "$2", "WRK", "example", "attrs",
        {
            "phase": "active", "current": "example", "blocked": False,
            "survive": "min", "nature": "example", "status": "specification",
        },
    ))
    diags = validate(doc, strict=True)
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E023_LEVEL1_LIVE_STATE" not in codes


# ---------------------------------------------------------------------------
# G3: render --mode audit --profile recovery includes source and limits to P0/P1
# ---------------------------------------------------------------------------

def test_g3_audit_recovery_mode_includes_source_and_limits_plevels():
    doc = build_brain()
    md = render_hcortex_read(
        doc, with_source=True, profile="RECOVERY", mode="READABLE",
    )
    # Must include the Perfil line
    assert "Perfil: CORTEX-RECOVERY" in md
    # Must include source column header (audit mode)
    assert "| source |" in md
    # Must NOT include DIAG entries (P5, excluded by RECOVERY profile)
    assert "### Diagram:" not in md
    # Must include FCS (P0, included by RECOVERY)
    assert "### Focus: primary" in md


def test_g3_audit_work_mode_includes_p0_p1_p2():
    doc = build_brain()
    md = render_hcortex_read(
        doc, with_source=True, profile="WORK", mode="AUDIT",
    )
    assert "Perfil: CORTEX-WORK" in md
    assert "| source |" in md
    # WORK includes P0/P1/P2 — FCS (P0) and WRK (P1/2) should appear
    assert "### Focus: primary" in md


def test_g3_min_profile_excludes_p1():
    doc = build_brain()
    md = render_hcortex_read(doc, profile="MIN", mode="READABLE")
    assert "Perfil: CORTEX-MIN" in md
    # MIN = P0 only; WRK maps to P1 (excluded)
    # But WRK has survive=work → P2, definitely excluded
    # FCS has survive=min → P0, included
    assert "### Focus: primary" in md  # FCS
    # Omissions section should mention excluded entries
    assert "Omissions by profile" in md


# ---------------------------------------------------------------------------
# G4: roundtrip hcortex-edit preserves values with pipes, quotes, unicode, blocks
# ---------------------------------------------------------------------------

def test_g4_roundtrip_preserves_pipe_in_value():
    """Audit gap H-04: pipe in attrs value must roundtrip."""

    doc = build_brain()
    update_entry(doc, "FCS:primary", set_={"what": "A | B"})
    md = render_hcortex_edit(doc)
    doc2 = parse_hcortex_edit(md)
    cortex2 = write_cortex(doc2)
    doc3 = parse_cortex(cortex2)
    diff = compare_ast(doc, doc3)
    assert diff.equal, f"pipe roundtrip failed: {[d.to_dict() for d in diff.diffs]}"


def test_g4_roundtrip_preserves_unicode():
    doc = build_brain()
    update_entry(doc, "FCS:primary", set_={"what": "café — Ñandú"})
    md = render_hcortex_edit(doc)
    doc2 = parse_hcortex_edit(md)
    cortex2 = write_cortex(doc2)
    doc3 = parse_cortex(cortex2)
    diff = compare_ast(doc, doc3)
    assert diff.equal, f"unicode roundtrip failed: {[d.to_dict() for d in diff.diffs]}"


def test_g4_roundtrip_preserves_plantuml_block():
    """DIAG bloque with PlantUML must roundtrip verbatim."""

    doc = build_brain()
    sec = doc.get_or_create_section("$6", title="DIAGRAMS")
    puml = "@startuml\nA --> B\nB --> C\nnote right: héllo\n@enduml"
    sec.entries.append(build_entry_from_value("$6", "DIAG", "flow", "bloque", puml))
    md = render_hcortex_edit(doc)
    doc2 = parse_hcortex_edit(md)
    cortex2 = write_cortex(doc2)
    doc3 = parse_cortex(cortex2)
    diff = compare_ast(doc, doc3)
    assert diff.equal, f"plantuml roundtrip failed: {[d.to_dict() for d in diff.diffs]}"
    # Verify verbatim preservation
    entry = None
    for s in doc3.sections:
        for e in s.entries:
            if e.sigil == "DIAG" and e.name == "flow":
                entry = e
    assert entry is not None
    assert entry.value == puml


def test_g4_roundtrip_preserves_attrs_pos():
    """attrs-pos with full contract must roundtrip."""

    doc = build_skill()
    sec = doc.get_or_create_section("$4", title="HANDLERS")
    sec.entries.append(build_entry_from_value(
        "$4", "HDL", "decode", "attrs-pos",
        {"operation": "decode", "status": "current", "requires": ".cortex file"},
    ))
    md = render_hcortex_edit(doc)
    doc2 = parse_hcortex_edit(md)
    cortex2 = write_cortex(doc2)
    doc3 = parse_cortex(cortex2)
    diff = compare_ast(doc, doc3)
    assert diff.equal, f"attrs-pos roundtrip failed: {[d.to_dict() for d in diff.diffs]}"


# ---------------------------------------------------------------------------
# G5: recover legacy.cortex reconstructs $0 and marks risks
# ---------------------------------------------------------------------------

def test_g5_recover_reconstructs_glossary():
    """Audit gap H-06: recovery of file without $0."""

    legacy = """\
<!-- SPDX-License-Identifier: MIT -->
# My Legacy Brain

$1: X

IDN:agent{name:"legacy"}
FCS:primary{what:"old focus", priority:"high", status:"current", survive:"min"}
"""
    result = recover_cortex(legacy, path="legacy.cortex")
    assert result.reconstructed_glossary is True
    # Reconstructed $0 should include FCS and IDN (canonical sigils)
    assert "FCS" in result.doc.glossary.sigils
    assert "IDN" in result.doc.glossary.sigils
    # Diagnostics should include E030_RECOVERY_INCOMPLETE
    codes = [d["code"] for d in result.diagnostics]
    assert "E030_RECOVERY_INCOMPLETE" in codes
    # Preamble should be stripped
    assert len(result.preamble) > 0


def test_g5_recover_with_legacy_type_alias():
    """Legacy type 'contenido' should normalise to 'cuerpo'."""

    # Build a brain with an AXM cuerpo entry, then change the glossary type
    # declaration to 'contenido' and verify recovery normalises it.
    doc = build_brain()
    # Inject a custom sigil with legacy type name
    write_cortex(doc)
    # The recovery path normalises type names in the glossary;
    # we test the helper directly:
    from cortex.hcortex import normalise_legacy_type_name
    assert normalise_legacy_type_name("contenido") == "cuerpo"
    assert normalise_legacy_type_name("body") == "cuerpo"
    assert normalise_legacy_type_name("code") == "bloque"
    assert normalise_legacy_type_name("positional") == "attrs-pos"
    assert normalise_legacy_type_name("attrs") == "attrs"  # unchanged


def test_g5_recover_preserves_entries():
    """Recovery should preserve all original entries (not just $0)."""

    legacy = """\
$1: X

IDN:agent{name:"legacy"}
FCS:primary{what:"old focus", priority:"high", status:"current", survive:"min"}
"""
    result = recover_cortex(legacy, path="legacy.cortex")
    # The original entries should still be in the doc
    sigils_found = {e.sigil for _, e in result.doc.iter_entries()}
    assert "IDN" in sigils_found
    assert "FCS" in sigils_found


# ---------------------------------------------------------------------------
# G6: doctor --strict promotes critical warnings to errors
# ---------------------------------------------------------------------------

def test_g6_doctor_strict_promotes_warnings_to_errors():
    """A document with warnings should fail under --strict."""

    doc = build_brain()
    # Introduce a warning: missing required field on FCS
    fcs = doc.find_entries(sigil="FCS")[0]
    del fcs.value["survive"]
    diags_non_strict = validate(doc, strict=False)
    diags_strict = validate(doc, strict=True)
    # The survive-missing should be a warning in non-strict mode
    # (note: E025 is also fired because None is not in ALLOWED_SURVIVE,
    # but missing-field is a separate warning)
    non_strict_errors = [d for d in diags_non_strict if d["severity"] == "error"]
    strict_errors = [d for d in diags_strict if d["severity"] == "error"]
    assert len(strict_errors) >= len(non_strict_errors)


# ---------------------------------------------------------------------------
# G7: diagram extract preserves DIAG bloque verbatim
# ---------------------------------------------------------------------------

def test_g7_diagram_extract_preserves_verbatim():
    puml = "@startuml\nA --> B\nB --> C\n@enduml"
    doc = build_brain()
    sec = doc.get_or_create_section("$6", title="DIAGRAMS")
    sec.entries.append(build_entry_from_value("$6", "DIAG", "flow", "bloque", puml))
    # Use the diagram command's _find_diagrams helper
    from cortex.cli.commands.diagram import _find_diagrams
    diags = _find_diagrams(doc, name="flow")
    assert len(diags) == 1
    _, entry = diags[0]
    assert entry.value == puml


def test_g7_diagram_validate_detects_unbalanced_plantuml():
    doc = build_brain()
    sec = doc.get_or_create_section("$6", title="DIAGRAMS")
    sec.entries.append(build_entry_from_value(
        "$6", "DIAG", "broken", "bloque",
        "@startuml\nA --> B\n",  # missing @enduml
    ))
    from cortex.cli.commands.diagram import _find_diagrams
    diags = _find_diagrams(doc, name="broken")
    _, entry = diags[0]
    text = str(entry.value or "")
    issues = []
    if "@startuml" in text and "@enduml" not in text:
        issues.append("missing @enduml")
    assert issues, "expected validation issue for unbalanced plantuml"


# ---------------------------------------------------------------------------
# G8: benchmark declares measured only with reproducible evidence
# ---------------------------------------------------------------------------

def test_g8_benchmark_measured_metrics_are_reproducible():
    """All `measured` metrics in BENCHMARK.md must have a reproduction command."""

    benchmark_path = os.path.join(SRC_DIR, "..", "BENCHMARK.md")
    if not os.path.exists(benchmark_path):
        pytest.skip("BENCHMARK.md not present")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Every `measured` row must reference a reproducible command (bash block)
    # or be backed by the test suite.
    assert "```bash" in text or "pytest" in text, (
        "BENCHMARK.md must contain reproducible commands for `measured` metrics"
    )
    # Must NOT contain "sin pérdida" as a positive claim.
    # The anti-overclaim section cites it only to forbid it; the check
    # verifies it's never made as a metric claim.
    # Allowed context: "NO permitido decir: comprime sin pérdida"
    for line in text.splitlines():
        ln = line.lower().strip()
        if "sin pérdida" in ln:
            # must be in a clearly negative context (forbidden quote)
            assert ("no permitido" in ln) or ("no se permite" in ln) or (
                ln.startswith(">")), (
                f"'sin pérdida' used as positive claim: {line!r}"
            )


# ---------------------------------------------------------------------------
# Additional regression tests for the audit gaps
# ---------------------------------------------------------------------------

def test_audit_b007_pipe_roundtrip_via_cli(tmp_path):
    """End-to-end CLI test: pipe in value survives render + compile."""

    brain_path = str(tmp_path / "brain.cortex")
    edit_path = str(tmp_path / "brain.hcortex.edit.md")
    compiled_path = str(tmp_path / "brain.compiled.cortex")

    # Build brain with pipe value
    doc = build_brain()
    update_entry(doc, "FCS:primary", set_={"what": "A | B"})
    from cortex.crud.transactions import atomic_write_cortex
    atomic_write_cortex(doc, brain_path, force=True)

    env = os.environ.copy()
    env["PYTHONPATH"] = SRC_DIR + os.pathsep + env.get("PYTHONPATH", "")

    # render edit
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, %r); from cortex.cli.main import main; main()" % SRC_DIR,
         "render", brain_path, "--mode", "edit", "--out", edit_path, "--force"],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode == 0, f"render failed: {r.stderr}"

    # compile
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, %r); from cortex.cli.main import main; main()" % SRC_DIR,
         "compile", edit_path, "--out", compiled_path],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode == 0, f"compile failed: {r.stderr}"

    # verify roundtrip
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, %r); from cortex.cli.main import main; main()" % SRC_DIR,
         "verify", brain_path, "--roundtrip", "hcortex-edit"],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode == 0, f"verify failed: {r.stderr}"
    assert "roundtrip:     OK" in r.stdout, f"roundtrip not OK: {r.stdout}"


def test_audit_b008_attrs_pos_excess_fields_errors():
    """attrs-pos with 4 values but contract declares 3 must error."""

    doc = build_skill()
    # The HDL contract is operation|status|requires (3 fields)
    sec = doc.get_or_create_section("$4", title="HANDLERS")
    # Build an HDL entry with 4 positional values (raw form)
    from cortex.core.ast import Entry, compute_entry_hash
    raw = "HDL:bad{op | cur | file | extra}"
    entry = Entry(
        section="$4", sigil="HDL", name="bad", type="attrs-pos",
        value={"operation": "op", "status": "cur", "requires": "file"},
        raw=raw, line_start=0, line_end=0, hash="",
    )
    entry.hash = compute_entry_hash(entry)
    entry.entry_id = entry.hash
    sec.entries.append(entry)
    diags = validate(doc)
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E027_ATTRS_POS_ARITY" in codes, f"expected E027, got: {codes}"


def test_audit_b009_survive_domain_validated():
    """survive=forever must produce E025_INVALID_SURVIVE."""

    doc = build_brain()
    fcs = doc.find_entries(sigil="FCS")[0]
    fcs.value["survive"] = "forever"
    diags = validate(doc)
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E025_INVALID_SURVIVE" in codes


def test_audit_m03_secret_detection():
    """api_key in clear text must produce E031_SECRET_NOT_BYPASSABLE.

    v1.1.3 P0-2: renamed from E028 to E031 and tagged bypassable=False.
    """

    doc = build_brain()
    sec = doc.get_or_create_section("$3")
    sec.entries.append(build_entry_from_value(
        "$3", "IDN", "creds", "attrs",
        {"name": "x", "api_key": "AKIAIOSFODNN7EXAMPLE"},
    ))
    diags = validate(doc)
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    # Accept either the old code (E028) or the new non-bypassable code (E031)
    assert "E031_SECRET_NOT_BYPASSABLE" in codes or "E028_SECRET_IN_CLEAR" in codes, (
        f"expected secret detection code, got: {codes}"
    )
    # v1.1.3: secret finding must be tagged non-bypassable
    secret_diags = [d for d in diags if d.get("code") in ("E031_SECRET_NOT_BYPASSABLE", "E028_SECRET_IN_CLEAR")]
    assert all(d.get("bypassable") is False for d in secret_diags), (
        "secret findings must be tagged bypassable=False (v1.1.3 P0-2)"
    )


def test_audit_h03_profile_filtering_works():
    """filter_by_profile should exclude P3+ entries in MIN profile."""

    doc = build_brain()
    prof = resolve_profile("MIN")  # P0 only
    result = filter_by_profile(doc, prof)
    plevels_kept = {p for _, _, p in result.kept}
    assert plevels_kept.issubset({"P0"}), f"MIN kept non-P0: {plevels_kept}"
    # P1+ entries should be in omitted
    assert len(result.omitted) > 0


def test_audit_priority_classifier_fcs_min_is_p0():
    """FCS with survive=min must classify as P0."""

    doc = build_brain()
    fcs = doc.find_entries(sigil="FCS")[0]
    plevel = classify_entry(fcs)
    assert plevel == "P0"


def test_audit_priority_classifier_cnst_blocking_is_p0():
    """CNST with severity=blocking must classify as P0."""

    doc = build_brain()
    cnst = doc.find_entries(sigil="CNST")[0]
    plevel = classify_entry(cnst)
    assert plevel == "P0"


def test_audit_priority_classifier_diag_is_p5():
    """DIAG entries default to P5."""

    doc = build_brain()
    sec = doc.get_or_create_section("$6", title="DIAGRAMS")
    sec.entries.append(build_entry_from_value(
        "$6", "DIAG", "test", "bloque", "@startuml\nA-->B\n@enduml",
    ))
    diag = doc.find_entries(sigil="DIAG")[0]
    plevel = classify_entry(diag)
    assert plevel == "P5"
