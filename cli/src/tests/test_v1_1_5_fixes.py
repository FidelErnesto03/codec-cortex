# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""v1.1.5 fixes — tests for the $0 section integrity breach.

P0:
  1. verify --strict rejects operational entries in $0 (E033)
  2. FCS/OBJ under $0 do not satisfy Nivel 2
  3. recover entry-first moves payload to $1: RECOVERED CONTENT
  4. cortex add --section $0 rejects operational entries

P1:
  5. HCORTEX warns when $0 contains operational entries
  6. BENCHMARK.md measures recovery by HCORTEX visibility
"""

import os
import subprocess
import sys

import pytest

from cortex.templates import build_brain
from cortex.core.parser import parse_cortex
from cortex.crud.transactions import atomic_write_cortex
from cortex.hcortex import recover_cortex, render_hcortex_read
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
# P0-1: verify --strict rejects operational entries in $0
# ---------------------------------------------------------------------------

def test_verify_rejects_memory_entries_in_zero_section():
    """verify --strict must fail with E033 if $0 contains operational entries."""

    text = """\
$0: BAD GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective

IDN:agent{name:"bad-brain"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
"""
    doc = parse_cortex(text)
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E033_ZERO_SECTION_MEMORY_ENTRY" in codes, (
        f"expected E033 for operational entries in $0; got: {codes}"
    )


def test_verify_rejects_memory_entries_in_zero_section_cli(tmp_path):
    """CLI: verify --strict on a file with FCS/OBJ in $0 must fail."""

    path = str(tmp_path / "bad.cortex")
    with open(path, "w") as f:
        f.write(
            '$0: BAD GLOSSARY\n\n'
            '# IDN | identity | attrs | B | Semantic | Identity\n'
            '# FCS | focus | attrs | H | Working | Focus\n'
            '# OBJ | objective | attrs | H | Working | Objective\n\n'
            'IDN:agent{name:"bad-brain"}\n'
            'FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}\n'
            'OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}\n'
        )
    r = _run_cli(["verify", path, "--strict", "--kind", "brain"])
    assert r.returncode != 0, f"verify should fail; rc={r.returncode}\n{r.stdout}"
    assert "E033" in r.stdout, f"expected E033 in output: {r.stdout}"


# ---------------------------------------------------------------------------
# P0-2: FCS/OBJ under $0 do not satisfy Nivel 2
# ---------------------------------------------------------------------------

def test_brain_fcs_obj_under_zero_do_not_satisfy_level2():
    """A brain with FCS/OBJ only in $0 must fail E024."""

    text = """\
$0: BAD GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective

IDN:agent{name:"bad-brain"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
"""
    doc = parse_cortex(text)
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E024_LEVEL2_MISSING_FOCUS" in codes, (
        f"FCS/OBJ in $0 should NOT satisfy Nivel 2; expected E024; got: {codes}"
    )


# ---------------------------------------------------------------------------
# P0-3: recover entry-first moves payload to $1: RECOVERED CONTENT
# ---------------------------------------------------------------------------

def test_recover_entry_first_moves_payload_to_section_1():
    """recover of entry-first file must put original entries in $1, not $0."""

    legacy = (
        'IDN:package{name:"legacy"}\n'
        'KNW:topic{topic:"x", content:"y", status:"current"}\n'
    )
    result = recover_cortex(legacy, path="legacy.cortex", embed_aud_rsk=True)
    # The original entries must be in $1, not $0
    sec0_entries = [e for e in result.doc.sections[0].entries if e.sigil not in ("GSIG", "GTYP", "GMIC", "GCON")]
    assert len(sec0_entries) == 0, (
        f"$0 should not contain operational entries; found: {[(e.sigil, e.name) for e in sec0_entries]}"
    )
    # Find $1 section
    sec1 = None
    for s in result.doc.sections:
        if s.id == "$1":
            sec1 = s
            break
    assert sec1 is not None, "$1: RECOVERED CONTENT section not found"
    sigils_in_sec1 = [e.sigil for e in sec1.entries]
    assert "IDN" in sigils_in_sec1, f"IDN:package should be in $1; got: {sigils_in_sec1}"
    assert "KNW" in sigils_in_sec1, f"KNW:topic should be in $1; got: {sigils_in_sec1}"


def test_recover_entry_first_verify_strict_passes(tmp_path):
    """recover + verify --strict must pass (no E033)."""

    legacy_path = str(tmp_path / "legacy.cortex")
    with open(legacy_path, "w") as f:
        f.write(
            'IDN:package{name:"legacy"}\n'
            'KNW:topic{topic:"x", content:"y", status:"current"}\n'
        )
    out_path = str(tmp_path / "fixed.cortex")
    r = _run_cli(["recover", legacy_path, "--out", out_path, "--embed-aud-rsk"])
    assert r.returncode == 0, f"recover failed: {r.stderr}"
    r = _run_cli(["verify", out_path, "--strict"])
    assert r.returncode == 0, (
        f"verify --strict should pass; rc={r.returncode}\n{r.stdout}"
    )


def test_recover_entry_first_hcortex_shows_payload(tmp_path):
    """HCORTEX audit must show the recovered entries (they're in $1, not $0)."""

    legacy_path = str(tmp_path / "legacy.cortex")
    with open(legacy_path, "w") as f:
        f.write(
            'IDN:package{name:"legacy"}\n'
            'KNW:topic{topic:"x", content:"y", status:"current"}\n'
        )
    out_path = str(tmp_path / "fixed.cortex")
    _run_cli(["recover", legacy_path, "--out", out_path, "--embed-aud-rsk"])

    r = _run_cli(["render", out_path, "--mode", "audit", "--profile", "full"])
    assert r.returncode == 0, f"render failed: {r.stderr}"
    # The recovered entries must be visible
    assert "IDN" in r.stdout and "package" in r.stdout, (
        f"IDN:package not visible in HCORTEX audit: {r.stdout[:500]}"
    )
    assert "KNW" in r.stdout and "topic" in r.stdout, (
        f"KNW:topic not visible in HCORTEX audit: {r.stdout[:500]}"
    )


# ---------------------------------------------------------------------------
# P0-4: cortex add --section $0 rejects operational entries
# ---------------------------------------------------------------------------

def test_add_to_zero_rejects_operational_entry(tmp_path):
    """cortex add --section $0 with an operational sigil must be rejected."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    r = _run_cli([
        "add", path, "--section", "$0", "--sigil", "NXT", "--name", "bad",
        "--value", 'action:"x", trigger:"y", status:"current", survive:"min"',
        "--force",
    ])
    assert r.returncode != 0, (
        f"add to $0 should be rejected; rc={r.returncode}\n{r.stdout}"
    )
    combined = r.stdout + r.stderr
    assert "E033" in combined or "ZERO_SECTION" in combined, (
        f"expected E033 reference; got: {combined}"
    )


def test_add_to_zero_allows_glossary_sigil(tmp_path):
    """cortex add --section $0 with GSIG (glossary declaration) should work."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    # GSIG is a glossary declaration sigil — allowed in $0
    r = _run_cli([
        "add", path, "--section", "$0", "--sigil", "GSIG", "--name", "test",
        "--value", 'sigil:"TEST", name:"test", type:"attrs", risk:"L", layer:"Semantic", description:"test"',
        "--allow-unknown-sigil", "--no-validate-write", "--force",
    ])
    # GSIG may or may not be in the glossary; allow_unknown_sigil handles that
    # The important thing is that E033 is NOT raised
    combined = r.stdout + r.stderr
    assert "E033" not in combined, (
        f"GSIG should be allowed in $0; got E033: {combined}"
    )


# ---------------------------------------------------------------------------
# P1-5: HCORTEX warns when $0 contains operational entries
# ---------------------------------------------------------------------------

def test_hcortex_warns_about_zero_section_entries():
    """HCORTEX-READ must include a warning if $0 has operational entries."""

    text = """\
$0: BAD GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity

IDN:agent{name:"bad-brain"}
"""
    doc = parse_cortex(text)
    md = render_hcortex_read(doc, profile="FULL", mode="AUDIT")
    assert "WARNING" in md or "⚠" in md, (
        "expected warning about $0 operational entries in HCORTEX output"
    )
    assert "IDN:agent" in md or "IDN" in md, (
        "warning should mention the hidden entry"
    )


def test_hcortex_no_warning_for_clean_brain():
    """HCORTEX-READ must NOT include $0 warning for a clean brain."""

    doc = build_brain()
    md = render_hcortex_read(doc, profile="WORK", mode="READABLE")
    assert "WARNING" not in md, (
        f"clean brain should not have $0 warning; got: {md[:300]}"
    )


# ---------------------------------------------------------------------------
# P1-6: BENCHMARK.md measures recovery by HCORTEX visibility
# ---------------------------------------------------------------------------

def test_benchmark_recovery_visibility_claim():
    """BENCHMARK.md must mention HCORTEX visibility as a recovery criterion."""

    bench_path = os.path.join(SRC_DIR, "..", "BENCHMARK.md")
    if not os.path.exists(bench_path):
        pytest.skip("BENCHMARK.md not present")
    with open(bench_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Must mention HCORTEX visibility as a criterion for recovery completeness
    assert "HCORTEX" in text.upper() and "visibility" in text.lower() or \
           "visibilidad" in text.lower(), (
        "BENCHMARK.md should mention HCORTEX visibility for recovery completeness"
    )
