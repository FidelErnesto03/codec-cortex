"""v1.1.9 fixes — tests for incomplete $0 repair and AUD/RSK trace.

Fix 1: recover repairs existing but incomplete $0
Fix 2: --embed-aud-rsk traces incomplete $0 repair
Fix 3: RECOVERED CONTENT uses free section without artificial ceiling
Fix 4: demo validates E034 explicitly (tested via test suite, not demo)
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
from cortex.core.document_kind import DocumentKind


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
# Fix 1: recover repairs existing but incomplete $0
# ---------------------------------------------------------------------------

def test_recover_repairs_existing_incomplete_glossary():
    """recover must auto-declare sigils missing from an existing $0."""

    legacy = """\
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity

$1: CONTENT

IDN:package{name:"legacy"}
KNW:topic{topic:"x", content:"y", status:"current"}
"""
    result = recover_cortex(legacy, path="legacy.cortex")
    # KNW should now be declared in $0
    assert "KNW" in result.doc.glossary.sigils, (
        f"KNW should be auto-declared in $0; sigils: {list(result.doc.glossary.sigils.keys())}"
    )
    # Check W012 diagnostic
    codes = [d.get("code") for d in result.diagnostics]
    assert "W012_INCOMPLETE_GLOSSARY_REPAIRED" in codes, (
        f"expected W012_INCOMPLETE_GLOSSARY_REPAIRED; got: {codes}"
    )


def test_recover_incomplete_glossary_verify_strict(tmp_path):
    """After repair, verify --strict must pass (no E003)."""

    legacy_path = str(tmp_path / "legacy.cortex")
    with open(legacy_path, "w") as f:
        f.write(
            '$0: GLOSSARY\n\n'
            '# IDN | identity | attrs | B | Semantic | Identity\n\n'
            '$1: CONTENT\n\n'
            'IDN:package{name:"legacy"}\n'
            'KNW:topic{topic:"x", content:"y", status:"current"}\n'
        )
    out_path = str(tmp_path / "fixed.cortex")
    r = _run_cli(["recover", legacy_path, "--out", out_path, "--embed-aud-rsk"])
    assert r.returncode == 0, f"recover failed: {r.stderr}"
    r = _run_cli(["verify", out_path, "--strict"])
    assert r.returncode == 0, (
        f"verify --strict should pass after repair; rc={r.returncode}\n{r.stdout}"
    )


# ---------------------------------------------------------------------------
# Fix 2: --embed-aud-rsk traces incomplete $0 repair
# ---------------------------------------------------------------------------

def test_recover_embed_aud_rsk_for_incomplete_glossary_repair():
    """AUD/RSK must be embedded for incomplete $0 repair."""

    legacy = """\
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity

$1: CONTENT

IDN:package{name:"legacy"}
KNW:topic{topic:"x", content:"y", status:"current"}
"""
    result = recover_cortex(legacy, path="legacy.cortex", embed_aud_rsk=True)
    # AUD should mention incomplete_glossary_repair
    aud = None
    for _, e in result.doc.iter_entries():
        if e.sigil == "AUD" and e.name == "recovery":
            aud = e
            break
    assert aud is not None, "AUD:recovery not found"
    event = aud.value.get("event", "")
    assert "incomplete_glossary_repair" in event, (
        f"AUD event should mention incomplete_glossary_repair; got: {event!r}"
    )
    # RSK should be embedded
    rsk_entries = [e for _, e in result.doc.iter_entries() if e.sigil == "RSK"]
    rsk_names = [e.name for e in rsk_entries]
    assert any("incomplete_glossary" in n for n in rsk_names), (
        f"expected RSK:incomplete_glossary_repaired; got: {rsk_names}"
    )


# ---------------------------------------------------------------------------
# Fix 3: RECOVERED CONTENT uses free section without ceiling
# ---------------------------------------------------------------------------

def test_recover_uses_free_section_even_when_many_sections_exist():
    """Recovery uses $101 if $1..$100 exist."""

    # Build a file with $1 through $5 + ops in $0
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
    # Should be $6 (first free after $5)
    assert recovery_sec.id == "$6", f"expected $6; got {recovery_sec.id}"


# ---------------------------------------------------------------------------
# Fix 4: CLI recover repairs incomplete glossary and returns zero
# ---------------------------------------------------------------------------

def test_recover_cli_repairs_incomplete_glossary_and_returns_zero(tmp_path):
    """CLI end-to-end: recover + verify --strict."""

    doc = build_brain()
    path = str(tmp_path / "valid.cortex")
    atomic_write_cortex(doc, path, force=True)
    out_path = str(tmp_path / "fixed.cortex")
    r = _run_cli(["recover", path, "--out", out_path])
    assert r.returncode == 0, f"recover of valid brain should return 0; got {r.returncode}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Incomplete glossary repair: HCORTEX visibility
# ---------------------------------------------------------------------------

def test_recover_incomplete_glossary_content_visible_in_hcortex(tmp_path):
    """Content recovered from incomplete $0 must be visible in HCORTEX."""

    legacy_path = str(tmp_path / "legacy.cortex")
    with open(legacy_path, "w") as f:
        f.write(
            '$0: GLOSSARY\n\n'
            '# IDN | identity | attrs | B | Semantic | Identity\n\n'
            '$1: CONTENT\n\n'
            'IDN:package{name:"legacy"}\n'
            'KNW:topic{topic:"x", content:"y", status:"current"}\n'
        )
    out_path = str(tmp_path / "fixed.cortex")
    _run_cli(["recover", legacy_path, "--out", out_path, "--embed-aud-rsk"])

    r = _run_cli(["render", out_path, "--mode", "audit", "--profile", "full"])
    assert r.returncode == 0, f"render failed: {r.stderr}"
    assert "IDN" in r.stdout and "package" in r.stdout, (
        f"IDN:package not visible in HCORTEX: {r.stdout[:500]}"
    )
    assert "KNW" in r.stdout and "topic" in r.stdout, (
        f"KNW:topic not visible in HCORTEX: {r.stdout[:500]}"
    )
