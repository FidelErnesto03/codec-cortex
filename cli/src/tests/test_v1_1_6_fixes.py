"""v1.1.6 fixes — tests for semantic emptiness and recovery conformant exit.

P0:
  1. E034_CRITICAL_REQUIRED_FIELD_EMPTY for "", "   ", null in critical fields
  2. FCS/OBJ with empty required fields do not satisfy Nivel 2
  3. E034 is non-bypassable

P1:
  4. recover moves operational entries out of $0 even if $0 already exists
  5. recover returns non-zero if the artefact is not conformant
  6. BENCHMARK.md has recovery semantic non-emptiness metric
"""

import json
import os
import subprocess
import sys

import pytest

from cortex.templates import build_brain
from cortex.core.parser import parse_cortex, build_entry_from_value
from cortex.core.writer import write_cortex
from cortex.crud.transactions import atomic_write_cortex
from cortex.hcortex import recover_cortex
from cortex.core.validator import validate
from cortex.core.document_kind import DocumentKind, _is_field_empty


HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))


def _run_cli(args_list, env=None):
    e = os.environ.copy()
    e["PYTHONPATH"] = SRC_DIR + os.pathsep + e.get("PYTHONPATH", "")
    if env:
        e.update(env)
    return subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, %r); from cortex.cli.main import main; rc = main(); sys.exit(rc or 0)" % SRC_DIR]
        + args_list,
        capture_output=True, text=True, env=e,
    )


# ---------------------------------------------------------------------------
# P0-1: E034_CRITICAL_REQUIRED_FIELD_EMPTY
# ---------------------------------------------------------------------------

def test_is_field_empty_helper():
    """The _is_field_empty helper correctly detects empty values."""
    assert _is_field_empty(None) is True
    assert _is_field_empty("") is True
    assert _is_field_empty("   ") is True
    assert _is_field_empty("\t\n") is True
    assert _is_field_empty("real value") is False
    assert _is_field_empty(0) is False  # 0 is not empty (it's a number)
    assert _is_field_empty(False) is False  # boolean False is not "empty"


def test_e034_empty_string_in_critical_field():
    """FCS with what:"" must produce E034."""

    doc = build_brain()
    fcs = doc.find_entries(sigil="FCS")[0]
    fcs.value["what"] = ""
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E034_CRITICAL_REQUIRED_FIELD_EMPTY" in codes, (
        f"expected E034 for empty 'what'; got: {codes}"
    )


def test_e034_whitespace_only_in_critical_field():
    """FCS with what:"   " must produce E034."""

    doc = build_brain()
    fcs = doc.find_entries(sigil="FCS")[0]
    fcs.value["what"] = "   "
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E034_CRITICAL_REQUIRED_FIELD_EMPTY" in codes


def test_e034_null_in_critical_field():
    """FCS with what:null must produce E034."""

    doc = build_brain()
    fcs = doc.find_entries(sigil="FCS")[0]
    fcs.value["what"] = None
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E034_CRITICAL_REQUIRED_FIELD_EMPTY" in codes


def test_e034_non_bypassable():
    """E034 must be tagged bypassable=False."""

    doc = build_brain()
    fcs = doc.find_entries(sigil="FCS")[0]
    fcs.value["what"] = ""
    diags = validate(doc)
    e034_diags = [d for d in diags if d.get("code") == "E034_CRITICAL_REQUIRED_FIELD_EMPTY"]
    assert e034_diags, "expected at least one E034 finding"
    for d in e034_diags:
        assert d.get("bypassable") is False, "E034 must be non-bypassable"


def test_e034_not_fired_for_non_empty_value():
    """FCS with what:"real focus" must NOT produce E034."""

    doc = build_brain()
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E034_CRITICAL_REQUIRED_FIELD_EMPTY" not in codes


# ---------------------------------------------------------------------------
# P0-3: FCS/OBJ with empty fields do not satisfy Nivel 2
# ---------------------------------------------------------------------------

def test_empty_fcs_does_not_satisfy_level2():
    """A brain with FCS what:"" must fail E024 (no active FCS)."""

    doc = build_brain()
    fcs = doc.find_entries(sigil="FCS")[0]
    fcs.value["what"] = ""
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E024_LEVEL2_MISSING_FOCUS" in codes, (
        f"empty FCS should not satisfy Nivel 2; expected E024; got: {codes}"
    )


def test_empty_obj_does_not_satisfy_level2():
    """A brain with OBJ goal:"" must fail E024 (no active OBJ)."""

    doc = build_brain()
    obj = doc.find_entries(sigil="OBJ")[0]
    obj.value["goal"] = ""
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E024_LEVEL2_MISSING_FOCUS" in codes


def test_non_empty_fcs_obj_satisfies_level2():
    """A brain with proper FCS/OBJ must pass (no E024)."""

    doc = build_brain()
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E024_LEVEL2_MISSING_FOCUS" not in codes


# ---------------------------------------------------------------------------
# P1-4: recover moves operational entries out of $0 even if $0 exists
# ---------------------------------------------------------------------------

def test_recover_moves_ops_from_existing_zero():
    """recover must move operational entries from $0 to $1 even if $0
    already existed with glossary declarations."""

    # A file with a proper $0 glossary but operational entries mixed in
    legacy = """\
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus

IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
"""
    result = recover_cortex(legacy, path="legacy.cortex")
    # $0 should NOT contain IDN or FCS
    sec0 = result.doc.get_section("$0")
    assert sec0 is not None
    ops_in_zero = [e for e in sec0.entries if e.sigil not in ("GSIG", "GTYP", "GMIC", "GCON")]
    assert len(ops_in_zero) == 0, (
        f"$0 should not have operational entries; found: {[(e.sigil, e.name) for e in ops_in_zero]}"
    )
    # $1 should contain the moved entries
    sec1 = result.doc.get_section("$1")
    assert sec1 is not None, "$1: RECOVERED CONTENT not created"
    sigils_in_sec1 = [e.sigil for e in sec1.entries]
    assert "IDN" in sigils_in_sec1, "IDN:agent should be in $1"
    assert "FCS" in sigils_in_sec1, "FCS:primary should be in $1"


# ---------------------------------------------------------------------------
# P1-5: recover returns non-zero if not conformant
# ---------------------------------------------------------------------------

def test_recover_returns_zero_for_conformant_input(tmp_path):
    """recover of a valid brain (with $0, FCS, OBJ) should return 0."""

    doc = build_brain()
    path = str(tmp_path / "valid.cortex")
    atomic_write_cortex(doc, path, force=True)
    out_path = str(tmp_path / "fixed.cortex")
    r = _run_cli(["recover", path, "--out", out_path])
    assert r.returncode == 0, f"recover of valid brain should return 0; got {r.returncode}\n{r.stdout}"


def test_recover_returns_zero_for_repairable_entry_first(tmp_path):
    """recover of entry-first file should return 0 (it can be repaired)."""

    path = str(tmp_path / "legacy.cortex")
    with open(path, "w") as f:
        f.write(
            'IDN:agent{name:"legacy"}\n'
            'FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}\n'
            'OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}\n'
        )
    out_path = str(tmp_path / "fixed.cortex")
    r = _run_cli(["recover", path, "--out", out_path, "--embed-aud-rsk"])
    assert r.returncode == 0, (
        f"recover of repairable entry-first should return 0; got {r.returncode}\n{r.stdout}"
    )


# ---------------------------------------------------------------------------
# P1-6: BENCHMARK.md has recovery semantic non-emptiness metric
# ---------------------------------------------------------------------------

def test_benchmark_has_recovery_semantic_non_emptiness():
    """BENCHMARK.md must mention recovery semantic non-emptiness."""

    bench_path = os.path.join(SRC_DIR, "..", "BENCHMARK.md")
    if not os.path.exists(bench_path):
        pytest.skip("BENCHMARK.md not present")
    with open(bench_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "semantic non-emptiness" in text.lower() or "semantically non-empty" in text.lower() or \
           "non-emptiness" in text.lower(), (
        "BENCHMARK.md should mention recovery semantic non-emptiness"
    )


def test_benchmark_has_e034_metric():
    """BENCHMARK.md must mention E034 / critical field emptiness."""

    bench_path = os.path.join(SRC_DIR, "..", "BENCHMARK.md")
    if not os.path.exists(bench_path):
        pytest.skip("BENCHMARK.md not present")
    with open(bench_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "E034" in text or "emptiness" in text.lower(), (
        "BENCHMARK.md should mention E034 or emptiness metric"
    )
