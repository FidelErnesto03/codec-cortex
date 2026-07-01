"""v1.1.7 fixes — tests for null/None handling and recovery section isolation.

P0:
  1. String "null" treated as empty in critical fields
  2. OBJ.success:null, CNST.rule:null blocked by E034
  3. update --set field=null serializes None (not "null")

P1:
  4. recover creates dedicated RECOVERED CONTENT section if $1 exists
  5. recover adds RSK when FCS/OBJ/WRK/STP/NXT moved from $0
"""

import os
import subprocess
import sys


from cortex.templates import build_brain
from cortex.core.parser import build_entry_from_value
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
# P0-1: String "null" treated as empty
# ---------------------------------------------------------------------------

def test_is_field_empty_treats_null_string_as_empty():
    """_is_field_empty must treat the string "null" as empty."""
    assert _is_field_empty("null") is True
    assert _is_field_empty("NULL") is True
    assert _is_field_empty("Null") is True
    assert _is_field_empty("null ") is True  # with trailing space
    assert _is_field_empty("real value") is False


def test_e034_for_string_null_in_critical_field():
    """CNST with rule:"null" must produce E034."""

    doc = build_brain()
    cnst = doc.find_entries(sigil="CNST")[0]
    cnst.value["rule"] = "null"
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E034_CRITICAL_REQUIRED_FIELD_EMPTY" in codes, (
        f"expected E034 for rule='null'; got: {codes}"
    )


# ---------------------------------------------------------------------------
# P0-2: OBJ.success:null, CNST.rule:null blocked
# ---------------------------------------------------------------------------

def test_obj_success_null_blocked():
    """OBJ with success:null must produce E034."""

    doc = build_brain()
    obj = doc.find_entries(sigil="OBJ")[0]
    obj.value["success"] = None
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E034_CRITICAL_REQUIRED_FIELD_EMPTY" in codes


def test_cnst_rule_null_blocked():
    """CNST with rule:null must produce E034."""

    doc = build_brain()
    cnst = doc.find_entries(sigil="CNST")[0]
    cnst.value["rule"] = None
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E034_CRITICAL_REQUIRED_FIELD_EMPTY" in codes


def test_rsk_mitigation_null_blocked():
    """RSK with mitigation:null must produce E034."""

    doc = build_brain()
    sec = doc.get_or_create_section("$5", title="RISKS")
    sec.entries.append(build_entry_from_value(
        "$5", "RSK", "test", "attrs",
        {
            "risk": "test risk",
            "impact": "medium",
            "mitigation": None,
            "status": "current",
            "survive": "work",
        },
    ))
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E034_CRITICAL_REQUIRED_FIELD_EMPTY" in codes


def test_aud_evidence_null_blocked():
    """AUD with evidence:null must produce E034."""

    doc = build_brain()
    sec = doc.get_or_create_section("$8", title="AUDIT")
    sec.entries.append(build_entry_from_value(
        "$8", "AUD", "test", "attrs",
        {
            "event": "test",
            "evidence": None,
            "result": "ok",
            "date": "2026-06-27",
        },
    ))
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E034_CRITICAL_REQUIRED_FIELD_EMPTY" in codes


# ---------------------------------------------------------------------------
# P0-3: update --set field=null serializes None, not "null"
# ---------------------------------------------------------------------------

def test_update_set_null_converts_to_none():
    """update --set field=null must convert to Python None, not string 'null'."""

    from cortex.cli.commands.update import _parse_set_pairs
    result = _parse_set_pairs(["rule=null"])
    assert result == {"rule": None}, f"expected None, got {result!r}"


def test_update_set_null_blocked_by_e034(tmp_path):
    """cortex update --set rule=null must be blocked by E034 (non-bypassable)."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    r = _run_cli([
        "update", path, "CNST:self_contained", "--set", "rule=null", "--force",
    ])
    assert r.returncode != 0, (
        f"update --set rule=null should be blocked; rc={r.returncode}\n{r.stdout}"
    )
    # Verify the file was NOT modified
    with open(path) as f:
        text = f.read()
    assert 'rule:"null"' not in text, "file was modified with rule='null'"


# ---------------------------------------------------------------------------
# P0-2 CLI: verify rejects null in critical fields
# ---------------------------------------------------------------------------

def test_verify_rejects_obj_success_null_cli(tmp_path):
    """CLI: verify --strict must fail on OBJ.success:null."""

    path = str(tmp_path / "bad.cortex")
    with open(path, "w") as f:
        f.write(
            '$0: GLOSSARY\n\n'
            '# IDN | identity | attrs | B | Semantic | Identity\n'
            '# FCS | focus | attrs | H | Working | Focus\n'
            '# OBJ | objective | attrs | H | Working | Objective\n'
            '# CNST | constraint | attrs | H | Prefrontal | Constraint\n'
            '# WRK | work | attrs | M | Working | Work\n'
            '# STP | step | attrs | M | Working | Step\n'
            '# DOM | domain | attrs | B | Semantic | Domain\n\n'
            '$1: IDENTITY\n\n'
            'IDN:agent{name:"test"}\n'
            'DOM:workspace{area:"test"}\n\n'
            '$2: ACTIVE WORK\n\n'
            'FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}\n'
            'OBJ:main{goal:"y", status:"current", success:null, survive:"min"}\n'
            'WRK:state{phase:"active", current:"work", blocked:false, survive:"work"}\n'
            'STP:next{action:"x", reason:"y", owner:"agent", status:"current", survive:"min"}\n\n'
            '$3: GOVERNANCE\n\n'
            'CNST:self_contained{rule:"test", severity:"blocking", survive:"min"}\n'
        )
    r = _run_cli(["verify", path, "--strict", "--kind", "brain"])
    assert r.returncode != 0, f"verify should fail; rc={r.returncode}\n{r.stdout}"
    assert "E034" in r.stdout, f"expected E034 in output: {r.stdout}"


def test_verify_rejects_cnst_rule_null_cli(tmp_path):
    """CLI: verify --strict must fail on CNST.rule:null."""

    path = str(tmp_path / "bad.cortex")
    with open(path, "w") as f:
        f.write(
            '$0: GLOSSARY\n\n'
            '# IDN | identity | attrs | B | Semantic | Identity\n'
            '# FCS | focus | attrs | H | Working | Focus\n'
            '# OBJ | objective | attrs | H | Working | Objective\n'
            '# CNST | constraint | attrs | H | Prefrontal | Constraint\n'
            '# WRK | work | attrs | M | Working | Work\n'
            '# STP | step | attrs | M | Working | Step\n'
            '# DOM | domain | attrs | B | Semantic | Domain\n\n'
            '$1: IDENTITY\n\n'
            'IDN:agent{name:"test"}\n'
            'DOM:workspace{area:"test"}\n\n'
            '$2: ACTIVE WORK\n\n'
            'FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}\n'
            'OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}\n'
            'WRK:state{phase:"active", current:"work", blocked:false, survive:"work"}\n'
            'STP:next{action:"x", reason:"y", owner:"agent", status:"current", survive:"min"}\n\n'
            '$3: GOVERNANCE\n\n'
            'CNST:self_contained{rule:null, severity:"blocking", survive:"min"}\n'
        )
    r = _run_cli(["verify", path, "--strict", "--kind", "brain"])
    assert r.returncode != 0, f"verify should fail; rc={r.returncode}\n{r.stdout}"
    assert "E034" in r.stdout, f"expected E034 in output: {r.stdout}"


# ---------------------------------------------------------------------------
# P1-4: recover creates dedicated RECOVERED CONTENT section if $1 exists
# ---------------------------------------------------------------------------

def test_recover_uses_dedicated_section_when_1_exists():
    """recover must use a free section (not $1) when $1 already exists.

    v1.1.8: the algorithm now scans $1, $2, ... to find the first truly
    free section, rather than hardcoding $99.
    """

    legacy = """\
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus

IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}

$1: EXISTING

DOM:workspace{area:"existing"}
"""
    result = recover_cortex(legacy, path="legacy.cortex")
    sec0 = result.doc.get_section("$0")
    ops_in_zero = [e for e in sec0.entries if e.sigil not in ("GSIG", "GTYP", "GMIC", "GCON")]
    assert len(ops_in_zero) == 0
    sec1 = result.doc.get_section("$1")
    assert sec1 is not None
    # Find RECOVERED CONTENT section (could be $2, $3, etc.)
    recovery_sec = None
    for s in result.doc.sections:
        if s.title == "RECOVERED CONTENT":
            recovery_sec = s
            break
    assert recovery_sec is not None, "RECOVERED CONTENT section not found"
    assert recovery_sec.id != "$1", "RECOVERED CONTENT should NOT be in $1"
    sigils_in_recovery = [e.sigil for e in recovery_sec.entries]
    assert "IDN" in sigils_in_recovery, "IDN:agent should be in recovery section"
    assert "FCS" in sigils_in_recovery, "FCS:primary should be in recovery section"
    sigils_in_1 = [e.sigil for e in sec1.entries]
    assert "DOM" in sigils_in_1, "DOM:workspace should still be in $1"


# ---------------------------------------------------------------------------
# P1-5: recover adds RSK when FCS/OBJ/WRK/STP/NXT moved from $0
# ---------------------------------------------------------------------------

def test_recover_adds_rsk_for_moved_live_state():
    """recover must add W011_RECOVERED_LIVE_STATE when FCS/OBJ moved from $0."""

    legacy = """\
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective

IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
"""
    result = recover_cortex(legacy, path="legacy.cortex")
    codes = [d.get("code") for d in result.diagnostics]
    assert "W011_RECOVERED_LIVE_STATE" in codes, (
        f"expected W011_RECOVERED_LIVE_STATE; got: {codes}"
    )
    # The warning should mention FCS and OBJ
    w011 = [d for d in result.diagnostics if d.get("code") == "W011_RECOVERED_LIVE_STATE"][0]
    assert "FCS" in w011["message"]
    assert "OBJ" in w011["message"]


def test_recover_no_rsk_for_non_live_state():
    """recover must NOT add W011 when only IDN/KNW moved from $0."""

    legacy = """\
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# KNW | knowledge | attrs | B | Semantic | Knowledge

IDN:agent{name:"legacy"}
KNW:topic{topic:"x", content:"y", status:"current"}
"""
    result = recover_cortex(legacy, path="legacy.cortex")
    codes = [d.get("code") for d in result.diagnostics]
    assert "W011_RECOVERED_LIVE_STATE" not in codes, (
        f"should not add W011 for non-live-state sigils; got: {codes}"
    )
