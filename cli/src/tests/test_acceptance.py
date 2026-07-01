"""Acceptance tests — verify all 15 criteria from Section 18 of the spec.

Each criterion is implemented as a separate test so failures pinpoint
exactly which acceptance item is broken.
"""

import json
import os
import subprocess
import sys

import pytest

from cortex.templates import build_brain
from cortex.core.parser import parse_cortex
from cortex.core.writer import write_cortex
from cortex.core.validator import validate, is_valid
from cortex.core.errors import (
    MissingGlossaryError,
    HCortexReadNotCompilableError,
)
from cortex.hcortex import (
    render_hcortex_read, render_hcortex_edit, parse_hcortex_edit,
)
from cortex.crud.selectors import select_one
from cortex.crud.mutations import add_entry, update_entry, delete_entry
from cortex.crud.transactions import atomic_write_cortex
from cortex.core.compare import compare_ast


# ---------------------------------------------------------------------------
# Criterion 1: Creates a valid brain.cortex with $0 minimal local glossary
# ---------------------------------------------------------------------------

def test_criterion_1_brain_has_minimal_glossary(brain_doc):
    assert brain_doc.sections[0].id == "$0"
    g = brain_doc.glossary
    # Must have at least the canonical sigils needed for brain operation
    for s in ("IDN", "DOM", "FCS", "OBJ", "WRK", "STP", "CNST"):
        assert s in g.sigils, f"sigil {s} missing from brain glossary"
    # Must have canonical types
    for t in ("attrs", "cuerpo", "bloque"):
        assert t in g.types, f"type {t} missing"
    # Must have canonical micro-tokens
    for tok in ("cur", "pln", "min"):
        assert tok in g.micro, f"micro-token {tok} missing"


# ---------------------------------------------------------------------------
# Criterion 2: Creates a valid Nivel 3 package with $0 minimal glossary
# ---------------------------------------------------------------------------

def test_criterion_2_package_has_minimal_glossary(package_doc):
    assert package_doc.sections[0].id == "$0"
    g = package_doc.glossary
    for s in ("IDN", "DOM", "KNW", "REF", "LIM", "CLAIM"):
        assert s in g.sigils, f"sigil {s} missing from package glossary"
    # Validate full document
    diagnostics = validate(package_doc)
    errors = [d for d in diagnostics if d.get("severity") == "error"]
    assert not errors, f"package has validation errors: {errors}"


# ---------------------------------------------------------------------------
# Criterion 3: Rejects .cortex without $0 in normal mode
# ---------------------------------------------------------------------------

def test_criterion_3_rejects_missing_glossary():
    """A .cortex without $0 must be rejected in normal mode."""

    from cortex.core.errors import (
        GlossaryNotFirstError, CortexError,
    )
    bad_text = """\
$1: IDENTITY

IDN:agent{name:"test"}
"""
    # Either MissingGlossaryError or GlossaryNotFirstError is acceptable
    # — both signal rejection of a file without $0 as the first section.
    with pytest.raises((MissingGlossaryError, GlossaryNotFirstError)):
        parse_cortex(bad_text)

    # A file with NO sections at all must also be rejected
    with pytest.raises(CortexError):
        parse_cortex("")


# ---------------------------------------------------------------------------
# Criterion 4: Reads .cortex and produces AST
# ---------------------------------------------------------------------------

def test_criterion_4_reads_to_ast(brain_doc):
    text = write_cortex(brain_doc)
    doc = parse_cortex(text)
    assert doc.sections
    assert doc.glossary.sigils
    # AST must have meta with hash
    assert "hash" in doc.meta
    assert doc.meta["hash"].startswith("sha256:")


# ---------------------------------------------------------------------------
# Criterion 5: Renders HCORTEX-READ
# ---------------------------------------------------------------------------

def test_criterion_5_renders_hcortex_read(brain_doc):
    md = render_hcortex_read(brain_doc)
    lines = md.splitlines()
    # v1.1.3 P1-5: Perfil is now the first real line
    assert lines[0].startswith("Perfil: CORTEX-")
    # The cortex-render marker is on line 2 (within first 3 lines)
    first_3 = "\n".join(lines[:3])
    assert "cortex-render: hcortex-read" in first_3
    assert "roundtrip: false" in first_3
    # Should not contain cortex-entry markers (those are for EDIT mode)
    assert "cortex-entry:" not in md


# ---------------------------------------------------------------------------
# Criterion 6: Renders HCORTEX-EDIT
# ---------------------------------------------------------------------------

def test_criterion_6_renders_hcortex_edit(brain_doc):
    md = render_hcortex_edit(brain_doc)
    first = md.splitlines()[0]
    assert "cortex-render: hcortex-edit" in first
    assert "roundtrip: structural" in first
    # Must contain cortex-section markers
    assert "cortex-section:" in md
    # Must contain cortex-entry markers for every entry
    n_entries = sum(len(s.entries) for s in brain_doc.sections if s.id != "$0")
    assert md.count("cortex-entry:") == n_entries
    # Must contain the glossary block
    assert "```cortex-glossary" in md


# ---------------------------------------------------------------------------
# Criterion 7: Compiles HCORTEX-EDIT back to .cortex
# ---------------------------------------------------------------------------

def test_criterion_7_compiles_hcortex_edit(brain_doc):
    md = render_hcortex_edit(brain_doc)
    doc2 = parse_hcortex_edit(md)
    cortex_text = write_cortex(doc2)
    # Resulting .cortex must be re-parseable
    doc3 = parse_cortex(cortex_text)
    assert doc3.sections
    assert doc3.glossary.sigils


# ---------------------------------------------------------------------------
# Criterion 8: Rejects compiling HCORTEX-READ
# ---------------------------------------------------------------------------

def test_criterion_8_rejects_hcortex_read_compile(brain_doc):
    md = render_hcortex_read(brain_doc)
    with pytest.raises(HCortexReadNotCompilableError):
        parse_hcortex_edit(md)


# ---------------------------------------------------------------------------
# Criterion 9: Executes CRUD on attrs entries
# ---------------------------------------------------------------------------

def test_criterion_9_crud_on_attrs(brain_doc):
    # Add
    add_entry(
        brain_doc, section="$2", sigil="FCS", name="secondary",
        value='what:"side task", priority:"medium", status:"planned", survive:"work"',
    )
    entry = select_one(brain_doc, "FCS:secondary")
    assert entry.value["what"] == "side task"
    # Update
    update_entry(brain_doc, "FCS:secondary", set_={"what": "updated task"})
    entry = select_one(brain_doc, "FCS:secondary")
    assert entry.value["what"] == "updated task"
    # Delete
    delete_entry(brain_doc, "FCS:secondary")
    from cortex.crud.selectors import select
    assert not select(brain_doc, "FCS:secondary")


# ---------------------------------------------------------------------------
# Criterion 10: Preserves bloque entries verbatim
# ---------------------------------------------------------------------------

def test_criterion_10_preserves_bloque_verbatim():
    bloque_content = "@startuml\nA --> B\nB --> C\n@enduml"
    from cortex.core.parser import build_entry_from_value
    doc = build_brain()
    sec = doc.get_or_create_section("$6", title="DIAGRAMS")
    sec.entries.append(build_entry_from_value(
        "$6", "DIAG", "test_diagram", "bloque", bloque_content,
    ))
    # Render to HCORTEX-EDIT
    md = render_hcortex_edit(doc)
    # Compile back
    doc2 = parse_hcortex_edit(md)
    cortex2 = write_cortex(doc2)
    doc3 = parse_cortex(cortex2)
    # Find the bloque entry
    entry = None
    for s in doc3.sections:
        for e in s.entries:
            if e.sigil == "DIAG" and e.name == "test_diagram":
                entry = e
                break
    assert entry is not None, "bloque entry not found after roundtrip"
    assert entry.value == bloque_content, (
        f"bloque content changed:\n  expected: {bloque_content!r}\n  got: {entry.value!r}"
    )


# ---------------------------------------------------------------------------
# Criterion 11: Validates local glossary
# ---------------------------------------------------------------------------

def test_criterion_11_validates_local_glossary(brain_doc):
    diagnostics = validate(brain_doc)
    errors = [d for d in diagnostics if d.get("severity") == "error"]
    assert not errors, f"brain.cortex has validation errors: {errors}"
    assert is_valid(brain_doc)


# ---------------------------------------------------------------------------
# Criterion 12: Detects unknown sigils
# ---------------------------------------------------------------------------

def test_criterion_12_detects_unknown_sigil(brain_doc):
    from cortex.core.parser import build_entry_from_value
    # Add an entry with an unknown sigil
    sec = brain_doc.get_or_create_section("$2")
    sec.entries.append(build_entry_from_value(
        "$2", "UNKNOWN", "phantom", "attrs", {"key": "value"},
    ))
    diagnostics = validate(brain_doc)
    codes = [d.get("code") for d in diagnostics]
    assert "E003_UNKNOWN_SIGIL" in codes, f"unknown sigil not detected: {codes}"


# ---------------------------------------------------------------------------
# Criterion 13: Executes verify --roundtrip hcortex-edit
# ---------------------------------------------------------------------------

def test_criterion_13_roundtrip_verify(brain_doc):
    # .cortex → HCORTEX-EDIT → .cortex → AST → compare
    md = render_hcortex_edit(brain_doc)
    doc2 = parse_hcortex_edit(md)
    cortex2 = write_cortex(doc2)
    doc3 = parse_cortex(cortex2)
    diff = compare_ast(brain_doc, doc3)
    assert diff.equal, f"roundtrip failed: {[d.to_dict() for d in diff.diffs[:5]]}"


# ---------------------------------------------------------------------------
# Criterion 14: Writes atomically with backup
# ---------------------------------------------------------------------------

def test_criterion_14_atomic_write_with_backup(brain_doc, tmp_path):
    path = str(tmp_path / "brain.cortex")
    # First write
    result = atomic_write_cortex(brain_doc, path, keep_backup=True)
    assert os.path.exists(path)
    assert result.bytes_written > 0
    assert result.backup is None  # no backup on first write
    # Modify and write again
    add_entry(
        brain_doc, section="$2", sigil="FCS", name="secondary",
        value='what:"new", priority:"medium", status:"planned", survive:"work"',
    )
    result = atomic_write_cortex(brain_doc, path, keep_backup=True)
    assert os.path.exists(path)
    assert result.backup is not None, "backup file not created"
    assert os.path.exists(result.backup), f"backup file missing: {result.backup}"


# ---------------------------------------------------------------------------
# Criterion 15: Produces JSON output for automation
# ---------------------------------------------------------------------------

def test_criterion_15_json_output(brain_doc, tmp_path):
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(brain_doc, path, keep_backup=False)

    # Run `python -m cortex list brain.cortex --format json`
    # Set PYTHONPATH so subprocess can find the cortex package
    import os
    env = os.environ.copy()
    # src/ contains the cortex/ package
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env["PYTHONPATH"] = src_dir + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, %r); from cortex.cli.main import main; rc = main(); sys.exit(rc or 0)" % src_dir,
         "list", path, "--format", "json"],
        capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    payload = json.loads(result.stdout)
    assert "entries" in payload
    assert isinstance(payload["entries"], list)
    assert len(payload["entries"]) > 0
    # Each entry must have the expected JSON fields
    e = payload["entries"][0]
    for field in ("section", "sigil", "name", "type", "value", "hash"):
        assert field in e, f"entry missing field {field!r}"
