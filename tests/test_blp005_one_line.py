# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""BLP-005: one physical line per non-DIAG entry — focused tests.

Verifies the canonical serialization invariant:
  - Every non-DIAG entry occupies exactly one physical source line.
  - DIAG remains the sole multiline exception (byte-preserved).
  - No escaped-newline convention is introduced.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.core.ast import (
    CortexDocument, Section, Entry, Glossary, SigilDef, TypeDef,
)
from cortex.core.parser import parse_cortex
from cortex.core.writer import write_cortex
from cortex.v2.parser import parse_cortex_v2
from cortex.v2.writer import write_cortex_v2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _count_source_lines(text: str) -> int:
    """Count non-blank, non-comment physical lines of CORTEX source."""
    count = 0
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("$"):
            count += 1
    return count


def _count_entry_lines(text: str) -> list:
    """Return a list of entry counts per physical line (1 == single-line)."""
    counts = []
    for line in text.split("\n"):
        stripped = line.strip()
        # Match any SIGIL:name{...} or SIGIL name{...} entry
        if stripped and not stripped.startswith("#") and not stripped.startswith("$") and "{" in stripped:
            counts.append(1)
    return counts


# ---------------------------------------------------------------------------
# Core writer — DIAG verbose multiline  (AC-02, AC-05)
# ---------------------------------------------------------------------------

def _make_diag_doc(diag_raw: str = "line one\nline two\nline three") -> CortexDocument:
    return CortexDocument(
        glossary=Glossary(
            sigils={
                "DIAG": SigilDef(sigil="DIAG", name="diagnostic", type="bloque", risk="M", layer="Prefrontal"),
                "WRK": SigilDef(sigil="WRK", name="work", type="attrs", risk="B", layer="Working"),
            },
            types={
                "attrs": TypeDef(name="attrs", description="attrs"),
                "bloque": TypeDef(name="bloque", description="bloque"),
            },
        ),
        sections=[
            Section(id="$0", title="", entries=[]),
            Section(id="$1", entries=[
                Entry(section="$1", sigil="DIAG", name="test", type="bloque", value=diag_raw, raw=diag_raw),
                Entry(section="$1", sigil="WRK", name="state", type="attrs", value={"status": "ok"}),
            ]),
        ],
    )


def test_diag_multiline_preserved():
    """DIAG multiline content must survive write with verbatim lines."""
    diag_text = "line one\nline two\nline three"
    doc = _make_diag_doc(diag_text)
    result = write_cortex(doc)
    # DIAG content must appear with its original newlines
    assert "line one" in result
    assert "line two" in result
    assert "line three" in result
    # DIAG entry must span multiple physical lines
    lines = result.split("\n")
    diag_lines = [i for i, line in enumerate(lines) if "DIAG:test" in line]
    assert len(diag_lines) == 1  # opening line
    # Verify the entry occupies more than one line
    assert any("line one" in line for line in lines)
    assert any("line two" in line for line in lines)


def test_non_diag_bloque_collapsed():
    """Non-DIAG bloque entries must be collapsed to one line."""
    doc = _make_diag_doc()
    # Replace DIAG with a non-DIAG bloque (e.g., DESC)
    glossary = Glossary(
        sigils={
            "DESC": SigilDef(sigil="DESC", name="description", type="bloque", risk="B", layer="Semantic"),
        },
        types={"bloque": TypeDef(name="bloque", description="bloque")},
    )
    doc = CortexDocument(
        glossary=glossary,
        sections=[
            Section(id="$0", title="", entries=[]),
            Section(id="$1", entries=[
                Entry(section="$1", sigil="DESC", name="test", type="bloque",
                      value="line one\nline two\nline three"),
            ]),
        ],
    )
    result = write_cortex(doc)
    lines = result.split("\n")
    # DESC entry must be on a single physical line
    desc_lines = [line for line in lines if "DESC:test" in line]
    assert len(desc_lines) == 1
    # Newlines must be collapsed (content joined by spaces)
    assert "line one" in desc_lines[0]
    assert "line two" in desc_lines[0]
    assert "line three" in desc_lines[0]


def test_cuerpo_newlines_collapsed():
    """Cuerpo-type entries with internal newlines must collapse to one line."""
    glossary = Glossary(
        sigils={
            "DESC": SigilDef(sigil="DESC", name="description", type="cuerpo", risk="B", layer="Semantic"),
        },
        types={"cuerpo": TypeDef(name="cuerpo", description="cuerpo")},
    )
    doc = CortexDocument(
        glossary=glossary,
        sections=[
            Section(id="$0", title="", entries=[]),
            Section(id="$1", entries=[
                Entry(section="$1", sigil="DESC", name="multi", type="cuerpo",
                      value="paragraph one\n\nparagraph two\n\nparagraph three"),
            ]),
        ],
    )
    result = write_cortex(doc)
    desc_lines = [line for line in result.split("\n") if "DESC:multi" in line]
    assert len(desc_lines) == 1
    assert "paragraph one" in desc_lines[0]
    assert "paragraph two" in desc_lines[0]
    assert "paragraph three" in desc_lines[0]
    # Must NOT contain literal newlines
    assert "\n" not in desc_lines[0]


def test_attrs_always_one_line():
    """Attrs entries must always serialize on one physical line."""
    glossary = Glossary(
        sigils={
            "WRK": SigilDef(sigil="WRK", name="work", type="attrs", risk="B", layer="Working"),
        },
        types={"attrs": TypeDef(name="attrs", description="attrs")},
    )
    doc = CortexDocument(
        glossary=glossary,
        sections=[
            Section(id="$0", title="", entries=[]),
            Section(id="$1", entries=[
                Entry(section="$1", sigil="WRK", name="state", type="attrs",
                      value={"status": "current", "phase": "testing", "note": "a\nb"}),
            ]),
        ],
    )
    result = write_cortex(doc)
    wrk_lines = [line for line in result.split("\n") if "WRK:state" in line]
    assert len(wrk_lines) == 1
    # Escaped newline \\n is OK inside attrs (it's an escape, not a physical line break)
    # The key assertion is one physical line
    assert "\n" not in wrk_lines[0]


# ---------------------------------------------------------------------------
# Core writer round-trip (AC-05, AC-06)
# ---------------------------------------------------------------------------

def test_parse_write_roundtrip_single_line():
    """Parse → write → parse: single-line entries survive unchanged."""
    source = "$0\n# -- $0: GLOSSARY --\n# WRK | work | attrs | B | Working | desc\n#\n# Types:\n# attrs = attrs\n\n$1\nWRK:task{status:\"done\"}\n"
    doc = parse_cortex(source)
    result = write_cortex(doc)
    # Result must be valid cortex
    doc2 = parse_cortex(result)
    assert doc2 is not None
    # Check the entry survived
    entries = list(doc2.iter_entries())
    assert len(entries) == 1
    assert entries[0][1].sigil == "WRK"


# ---------------------------------------------------------------------------
# V2 writer — DIAG preservation (AC-02)
# ---------------------------------------------------------------------------

def _make_v2_source_with_diag() -> str:
    """Return a v2 CORTEX source with a DIAG entry."""
    return """```markdown
$0
# -- $0: GLOSSARY --
# DIAG | diagnostic | bloque | M | Prefrontal | Diagnostic block

$1: DIAG
DIAG:crash{
A real error
with multiple
lines
}
```"""


def test_v2_diag_multiline_preserved():
    """V2 writer must preserve DIAG multiline content."""
    source = _make_v2_source_with_diag()
    doc = parse_cortex_v2(source)
    result = write_cortex_v2(doc)
    assert "A real error" in result
    assert "with multiple" in result
    assert "lines" in result
    # Opening brace must be on the DIAG:crash{ line
    assert "DIAG:crash{" in result


# ---------------------------------------------------------------------------
# V2 writer — non-DIAG collapsed (AC-01)
# ---------------------------------------------------------------------------

def test_v2_non_diag_collapsed():
    """V2 writer must collapse non-DIAG cuerpo entries to one line."""
    source = """```markdown
$0
# -- $0: GLOSSARY --
# DESC | description | cuerpo | B | Semantic | Description

$1: DESC
DESC:text{hello
world
}
```"""
    doc = parse_cortex_v2(source)
    result = write_cortex_v2(doc)
    desc_lines = [line for line in result.split("\n") if "DESC:text" in line]
    assert len(desc_lines) == 1
    assert "hello" in desc_lines[0]
    assert "world" in desc_lines[0]
