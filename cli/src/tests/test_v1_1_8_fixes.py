"""v1.1.8 fixes — tests for free section selection, RSK embedding, AUD description, null-like sentinels.

Fix 1: Recovery chooses a truly free section ($1, $2, ..., $99, $100, ...)
Fix 2: --embed-aud-rsk embeds RSK for W011_RECOVERED_LIVE_STATE
Fix 3: AUD:recovery describes the real event (not always glossary_reconstruction)
Fix 4: E034 covers none, nil, undefined, n/a, tbd in critical fields
"""

import os

import pytest

from cortex.templates import build_brain
from cortex.hcortex import recover_cortex
from cortex.core.validator import validate
from cortex.core.document_kind import DocumentKind, _is_field_empty


HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))


# ---------------------------------------------------------------------------
# Fix 1: Recovery chooses a truly free section
# ---------------------------------------------------------------------------

def test_recover_finds_free_section_when_1_and_99_exist():
    """recover must not contaminate $1 or $99 if both already exist."""

    legacy = """\
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus

IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}

$1: EXISTING

DOM:workspace{area:"existing"}

$99: EXISTING SPECIAL

DOM:special{area:"special"}
"""
    result = recover_cortex(legacy, path="legacy.cortex")
    sec0 = result.doc.get_section("$0")
    ops_in_zero = [e for e in sec0.entries if e.sigil not in ("GSIG", "GTYP", "GMIC", "GCON")]
    assert len(ops_in_zero) == 0
    sec1 = result.doc.get_section("$1")
    sec99 = result.doc.get_section("$99")
    assert sec1 is not None and sec1.title == "EXISTING"
    assert sec99 is not None and sec99.title == "EXISTING SPECIAL"
    recovery_sec = None
    for s in result.doc.sections:
        if s.title == "RECOVERED CONTENT":
            recovery_sec = s
            break
    assert recovery_sec is not None, "RECOVERED CONTENT section not found"
    assert recovery_sec.id not in ("$1", "$99"), (
        f"RECOVERED CONTENT should not be in $1 or $99; got {recovery_sec.id}"
    )
    sigils = [e.sigil for e in recovery_sec.entries]
    assert "IDN" in sigils and "FCS" in sigils


def test_recover_never_contaminates_existing_section():
    """Even if all sections $1..$5 exist, recover finds $6."""

    legacy = """\
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus

IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}

$1: A
$2: B
$3: C
$4: D
$5: E

DOM:workspace{area:"test"}
"""
    result = recover_cortex(legacy, path="legacy.cortex")
    recovery_sec = None
    for s in result.doc.sections:
        if s.title == "RECOVERED CONTENT":
            recovery_sec = s
            break
    assert recovery_sec is not None
    assert recovery_sec.id == "$6", (
        f"expected $6 as first free section; got {recovery_sec.id}"
    )


# ---------------------------------------------------------------------------
# Fix 2: --embed-aud-rsk embeds RSK for W011_RECOVERED_LIVE_STATE
# ---------------------------------------------------------------------------

def test_embed_aud_rsk_inserts_rsk_for_moved_live_state():
    """recover --embed-aud-rsk must insert RSK entries for moved FCS/OBJ."""

    legacy = """\
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective

IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
"""
    result = recover_cortex(legacy, path="legacy.cortex", embed_aud_rsk=True)
    rsk_entries = [e for _, e in result.doc.iter_entries() if e.sigil == "RSK"]
    rsk_names = [e.name for e in rsk_entries]
    assert any("recovered_live_fcs" in n for n in rsk_names), (
        f"expected RSK for recovered FCS; got RSK names: {rsk_names}"
    )
    assert any("recovered_live_obj" in n for n in rsk_names), (
        f"expected RSK for recovered OBJ; got RSK names: {rsk_names}"
    )


# ---------------------------------------------------------------------------
# Fix 3: AUD describes the real event
# ---------------------------------------------------------------------------

def test_aud_describes_real_event_not_always_glossary_reconstruction():
    """When $0 was NOT reconstructed but live state was moved, AUD should
    describe 'live_state_recovered_from_zero', not 'glossary_reconstruction'."""

    legacy = """\
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective

IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
"""
    result = recover_cortex(legacy, path="legacy.cortex", embed_aud_rsk=True)
    aud = None
    for _, e in result.doc.iter_entries():
        if e.sigil == "AUD" and e.name == "recovery":
            aud = e
            break
    assert aud is not None, "AUD:recovery not found"
    event = aud.value.get("event", "")
    assert "glossary_reconstruction" not in event or "live_state" in event, (
        f"AUD event should describe live_state recovery; got: {event!r}"
    )
    assert "live_state_recovered_from_zero" in event, (
        f"AUD event should mention live_state_recovered_from_zero; got: {event!r}"
    )


def test_aud_describes_glossary_reconstruction_when_it_happened():
    """When $0 WAS reconstructed, AUD should mention glossary_reconstruction."""

    legacy = (
        'IDN:agent{name:"legacy"}\n'
        'FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}\n'
        'OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}\n'
    )
    result = recover_cortex(legacy, path="legacy.cortex", embed_aud_rsk=True)
    aud = None
    for _, e in result.doc.iter_entries():
        if e.sigil == "AUD" and e.name == "recovery":
            aud = e
            break
    assert aud is not None
    event = aud.value.get("event", "")
    assert "glossary_reconstruction" in event, (
        f"AUD event should mention glossary_reconstruction; got: {event!r}"
    )


# ---------------------------------------------------------------------------
# Fix 4: E034 covers none, nil, undefined, n/a, tbd
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("null_like", ["none", "nil", "undefined", "n/a", "N/A", "tbd", "TBD", "???", "-", "--"])
def test_null_like_sentinels_blocked_in_critical_fields(null_like):
    """Each null-like sentinel must be treated as empty by _is_field_empty."""

    assert _is_field_empty(null_like) is True, (
        f"_is_field_empty({null_like!r}) should be True"
    )


@pytest.mark.parametrize("null_like", ["none", "nil", "undefined", "n/a", "tbd"])
def test_e034_for_null_like_in_cnst_rule(null_like):
    """CNST with rule:<null_like> must produce E034."""

    doc = build_brain()
    cnst = doc.find_entries(sigil="CNST")[0]
    cnst.value["rule"] = null_like
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E034_CRITICAL_REQUIRED_FIELD_EMPTY" in codes, (
        f"expected E034 for rule={null_like!r}; got: {codes}"
    )


def test_real_values_not_blocked():
    """Real non-empty values must NOT trigger E034."""

    assert _is_field_empty("real value") is False
    assert _is_field_empty("blocking constraint") is False
    assert _is_field_empty(0) is False
    assert _is_field_empty(False) is False
    assert _is_field_empty("min") is False
