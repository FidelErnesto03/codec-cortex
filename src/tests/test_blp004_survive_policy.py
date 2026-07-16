from cortex.core.parser import parse_cortex
from cortex.core.validator import validate


def test_blocking_protection_is_independent_from_survive():
    doc = parse_cortex(
        '$0: GLOSSARY\n'
        '$1: IDENTITY\n'
        'IDN:agent{name:"a", role:"operator"}\n'
        '$3: GOVERNANCE\n'
        'CNST:critical{rule:"retain protection", severity:"blocking", survive:"work"}\n',
        path="brain.cortex",
    )
    errors = [d for d in validate(doc, strict=True) if d.get("severity") == "error"]
    assert not any(d.get("code") == "E026_BLOCKING_NOT_P0" for d in errors)

