"""v1.1.9 fixes — incomplete $0 repair and demo sentinel hardening.

Fix 1: recover repairs an existing but incomplete $0 by auto-declaring
        observed sigils and canonical types.
Fix 2: recover --embed-aud-rsk embeds AUD/RSK for incomplete glossary repair.
Fix 3: recovery content always goes to a truly free RECOVERED CONTENT section.
Fix 4: demo sentinel checks verify E034 rather than only non-zero rc.
"""

import json
import os
import subprocess
import sys

from cortex.core.parser import parse_cortex
from cortex.core.validator import validate
from cortex.core.writer import write_cortex
from cortex.hcortex import recover_cortex
from cortex.hcortex.read_renderer import render_hcortex_read


HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def test_recover_repairs_existing_incomplete_glossary():
    """A present but incomplete $0 should be repaired, not left with E003."""

    legacy = '''\
$0: GLOSSARY
# IDN | identity | attrs | B | Semantic | Identity

$1: CONTENT
IDN:package{name:"legacy"}
KNW:topic{topic:"x", content:"y", status:"current"}
'''
    result = recover_cortex(legacy, path="legacy.cortex")
    out = write_cortex(result.doc)
    reparsed = parse_cortex(out, path="legacy.cortex")
    diags = validate(reparsed, strict=True)
    codes = [d["code"] for d in diags if d.get("severity") == "error"]
    assert "E003_UNKNOWN_SIGIL" not in codes
    assert "E004_UNKNOWN_TYPE" not in codes
    assert "KNW" in reparsed.glossary.sigils
    assert any(d["code"] == "W012_INCOMPLETE_GLOSSARY_REPAIRED" for d in result.diagnostics)


def test_recover_embed_aud_rsk_for_incomplete_glossary_repair():
    """embed-aud-rsk must leave trace for incomplete $0 repair."""

    legacy = '''\
$0: GLOSSARY
# IDN | identity | attrs | B | Semantic | Identity

$1: CONTENT
IDN:package{name:"legacy"}
KNW:topic{topic:"x", content:"y", status:"current"}
'''
    result = recover_cortex(legacy, path="legacy.cortex", embed_aud_rsk=True)
    aud = [e for _, e in result.doc.iter_entries() if e.sigil == "AUD" and e.name == "recovery"]
    rsk = [e for _, e in result.doc.iter_entries() if e.sigil == "RSK"]
    assert aud, "AUD:recovery should be embedded"
    assert "incomplete_glossary_repair" in aud[0].value.get("event", "")
    assert any(e.name == "incomplete_glossary_repaired" for e in rsk)
    assert any(e.name == "auto_declared_knw" for e in rsk)


def test_recover_incomplete_glossary_content_visible_in_hcortex():
    """Recovered entries must be visible in HCORTEX after $0 repair."""

    legacy = '''\
$0: GLOSSARY
# IDN | identity | attrs | B | Semantic | Identity

$1: CONTENT
IDN:package{name:"legacy"}
KNW:topic{topic:"x", content:"y", status:"current"}
'''
    result = recover_cortex(legacy, path="legacy.cortex", embed_aud_rsk=True)
    md = render_hcortex_read(result.doc, mode="audit", profile="full")
    assert "IDN:package" in md
    assert "KNW:topic" in md
    assert "AUD:recovery" in md
    assert "RSK:incomplete_glossary_repaired" in md


def test_recover_uses_free_section_even_when_many_sections_exist():
    """If $1..$100 exist, recovery should create $101: RECOVERED CONTENT."""

    header = '''\
$0: GLOSSARY
# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective

IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
'''
    sections = "\n".join(f"${i}: EXISTING {i}\n" for i in range(1, 101))
    legacy = header + "\n" + sections
    result = recover_cortex(legacy, path="legacy.cortex")
    recovered = [s for s in result.doc.sections if s.title == "RECOVERED CONTENT"]
    assert recovered, "RECOVERED CONTENT section should be created"
    assert recovered[0].id == "$101"


def test_recover_cli_repairs_incomplete_glossary_and_returns_zero(tmp_path):
    """CLI recovery should return rc=0 when the repaired artefact is conformant."""

    src = tmp_path / "legacy.cortex"
    out = tmp_path / "fixed.cortex"
    src.write_text('''\
$0: GLOSSARY
# IDN | identity | attrs | B | Semantic | Identity

$1: CONTENT
IDN:package{name:"legacy"}
KNW:topic{topic:"x", content:"y", status:"current"}
''', encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = SRC_DIR + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    proc = subprocess.run(
        [sys.executable, "-m", "cortex", "recover", str(src), "--out", str(out), "--embed-aud-rsk", "--format", "json"],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = json.loads(proc.stdout)
    assert data["ok"] is True
    assert any(d["code"] == "W012_INCOMPLETE_GLOSSARY_REPAIRED" for d in data["diagnostics"])

    proc2 = subprocess.run(
        [sys.executable, "-m", "cortex", "verify", str(out), "--strict"],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    assert proc2.returncode == 0, proc2.stdout + proc2.stderr
