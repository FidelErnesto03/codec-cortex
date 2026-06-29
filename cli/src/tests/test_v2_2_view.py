"""v2.2.0 tests — VIEW directives: parsing, rendering, coverage."""

import os
import sys
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.v2.parser import parse_cortex_v2
from cortex.v2.writer import write_cortex_v2
from cortex.v2.view import (
    ViewDirective, ViewKind, ReverseStrategy, ViewDiagnostic,
    parse_view_entry, parse_view_entries_from_doc,
    resolve_target, calculate_view_coverage,
    VALID_KINDS, VALID_REVERSES, KIND_REVERSE_COMPAT,
)
from cortex.v2.view_renderer import render_hcortex, render_hcortex_r


FIXTURES_DIR = os.path.join(HERE, "fixtures")
SKILL_CORTEX_PATH = os.path.join(FIXTURES_DIR, "SKILL_v2.cortex.md")


# ---------------------------------------------------------------------------
# ViewDirective parsing
# ---------------------------------------------------------------------------

def test_parse_view_directive_minimal():
    """Minimal VIEW with required fields must parse."""

    attrs = {
        "kind": "table",
        "target": "$0:canonical_sigils",
        "reverse": "rows_to_entries",
        "status": "cur",
    }
    directive, diags = parse_view_entry("test", attrs)
    assert directive is not None
    assert directive.kind == ViewKind.TABLE
    assert directive.reverse == ReverseStrategy.ROWS_TO_ENTRIES
    assert len(diags) == 0


def test_parse_view_directive_full():
    """Full VIEW with all fields must parse."""

    attrs = {
        "kind": "table",
        "target": "$0:canonical_sigils",
        "fields": "sigil,name,type,risk,cortex,desc",
        "order": "source",
        "reverse": "rows_to_entries",
        "title": "Sigilos canónicos",
        "scope": "glossary",
        "status": "cur",
        "preserve": "verbatim",
    }
    directive, diags = parse_view_entry("glossary_table", attrs)
    assert directive is not None
    assert directive.title == "Sigilos canónicos"
    assert directive.fields == "sigil,name,type,risk,cortex,desc"


def test_view_unknown_kind_fails():
    """Unknown kind must produce error."""

    attrs = {"kind": "invalid_kind", "target": "IDN:*", "reverse": "rows_to_entries", "status": "cur"}
    directive, diags = parse_view_entry("test", attrs)
    assert directive is None
    assert any(d.code == "E_VIEW_UNKNOWN_KIND" and d.severity == "error" for d in diags)


def test_view_unknown_reverse_fails():
    """Unknown reverse must produce error."""

    attrs = {"kind": "table", "target": "IDN:*", "reverse": "invalid_reverse", "status": "cur"}
    directive, diags = parse_view_entry("test", attrs)
    assert directive is None
    assert any(d.code == "E_VIEW_UNKNOWN_REVERSE" and d.severity == "error" for d in diags)


def test_view_incompatible_reverse_fails():
    """Incompatible kind+reverse must produce error."""

    # table + body_to_cuerpo is incompatible
    attrs = {"kind": "table", "target": "IDN:*", "reverse": "body_to_cuerpo", "status": "cur"}
    directive, diags = parse_view_entry("test", attrs)
    assert directive is None
    assert any(d.code == "E_VIEW_INCOMPATIBLE_REVERSE" and d.severity == "error" for d in diags)


def test_view_missing_kind_fails():
    """Missing kind must produce error."""

    attrs = {"target": "IDN:*", "reverse": "rows_to_entries", "status": "cur"}
    directive, diags = parse_view_entry("test", attrs)
    assert directive is None
    assert any(d.code == "E_VIEW_UNKNOWN_KIND" for d in diags)


def test_view_missing_target_fails():
    """Missing target must produce error."""

    attrs = {"kind": "table", "reverse": "rows_to_entries", "status": "cur"}
    directive, diags = parse_view_entry("test", attrs)
    assert directive is None
    assert any(d.code == "E_VIEW_EMPTY_TARGET" for d in diags)


def test_view_missing_reverse_fails():
    """Missing reverse must produce error."""

    attrs = {"kind": "table", "target": "IDN:*", "status": "cur"}
    directive, diags = parse_view_entry("test", attrs)
    assert directive is None
    assert any(d.code == "E_VIEW_UNKNOWN_REVERSE" for d in diags)


def test_view_duplicate_name_detected():
    """Duplicate VIEW names must produce error."""

    # Build a minimal CORTEX doc with two VIEW entries with same name
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$0
VIEW:test{kind:table,target:"$0:canonical_sigils",reverse:"rows_to_entries",status:cur}
VIEW:test{kind:table,target:"$0:contracts",reverse:"rows_to_entries",status:cur}
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"test"}
```'''
    doc = parse_cortex_v2(text)
    directives, diags = parse_view_entries_from_doc(doc)
    assert any(d.code == "E_VIEW_DUPLICATE_NAME" and d.severity == "error" for d in diags)


# ---------------------------------------------------------------------------
# Target resolution
# ---------------------------------------------------------------------------

def test_view_target_resolution_canonical_sigils():
    """$0:canonical_sigils must resolve to sigil declarations."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    entries = resolve_target("$0:canonical_sigils", doc)
    assert len(entries) > 0
    assert all(e.entry_type == "sigil_decl" for e in entries)


def test_view_target_resolution_contracts():
    """$0:contracts must resolve to contract entries."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    entries = resolve_target("$0:contracts", doc)
    assert len(entries) > 0
    assert all(e.name.startswith("contract_") for e in entries)


def test_view_target_resolution_wildcard():
    """SIGIL:* must resolve to all entries of that sigil."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    entries = resolve_target("REF:*", doc)
    assert len(entries) > 0
    assert all(e.sigil == "REF" for e in entries)


def test_view_target_resolution_exact():
    """SIGIL:name must resolve to exact entry."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    entries = resolve_target("IDN:project", doc)
    assert len(entries) == 1
    assert entries[0].name == "project"


def test_view_target_resolution_section():
    """$N must resolve to entire section."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    entries = resolve_target("$3", doc)
    assert len(entries) > 0


def test_view_target_empty_returns_empty():
    """Non-existent target must return empty list."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    entries = resolve_target("NONEXISTENT:*", doc)
    assert len(entries) == 0


# ---------------------------------------------------------------------------
# Coverage
# ---------------------------------------------------------------------------

def test_view_coverage_no_directives():
    """Without VIEW directives, coverage should be 0."""

    with open(SKILL_CORTEX_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    coverage, uncovered = calculate_view_coverage(doc, [])
    assert coverage == 0.0
    assert len(uncovered) > 0


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def test_render_hcortex_r_with_views():
    """CORTEX with VIEW directives must produce HCORTEX-R with markers."""

    # Build a minimal CORTEX doc with VIEW
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$0
VIEW:glossary_table{kind:table,target:"$0:canonical_sigils",fields:"sigil,name,type,risk,cortex,desc",order:"source",reverse:"rows_to_entries",title:"Sigilos canónicos",status:cur}
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identidad"}
DOM:domain{type:attrs,risk:B,cortex:Semantic,desc:"dominio"}

$1
IDN:project{name:"test",version:"1.0"}
```'''
    doc = parse_cortex_v2(text)
    hcortex_r, diags = render_hcortex(doc)

    # Must have VIEW markers
    assert "<!-- VIEW:glossary_table" in hcortex_r
    assert "<!-- /VIEW:glossary_table -->" in hcortex_r
    # Must have table headers
    assert "| Sigilo |" in hcortex_r
    # v2.2.3 PRE-04: reversible reflects actual state — 66.7% coverage → false
    assert "reversible: false" in hcortex_r
    assert "view_schema: 1" in hcortex_r


def test_render_table_view():
    """Table VIEW must produce a proper Markdown table."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$0
VIEW:glossary_table{kind:table,target:"$0:canonical_sigils",fields:"sigil,name,type,risk,cortex,desc",reverse:"rows_to_entries",title:"Glossary",status:cur}
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identidad"}
DOM:domain{type:attrs,risk:B,cortex:Semantic,desc:"dominio"}
```'''
    doc = parse_cortex_v2(text)
    hcortex_r, _ = render_hcortex(doc)
    assert "| `IDN` | identity | `attrs` | B | Semantic | identidad |" in hcortex_r
    assert "| `DOM` | domain | `attrs` | B | Semantic | dominio |" in hcortex_r


def test_render_prose_view():
    """Prose VIEW must produce prose text."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$2
VIEW:purpose{kind:prose,target:"DESC:purpose",reverse:"body_to_cuerpo",title:"Purpose",status:cur}
DESC:purpose{This is the purpose text.}
```'''
    doc = parse_cortex_v2(text)
    hcortex_r, _ = render_hcortex(doc)
    assert "This is the purpose text." in hcortex_r
    assert "<!-- VIEW:purpose" in hcortex_r


def test_render_quote_view():
    """Quote VIEW must produce a blockquote."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$2
VIEW:canon{kind:quote,target:"AXM:canon",reverse:"body_to_cuerpo",title:"Canon",status:cur}
AXM:canon{SKILL gobierna. brain opera.}
```'''
    doc = parse_cortex_v2(text)
    hcortex_r, _ = render_hcortex(doc)
    assert "> SKILL gobierna. brain opera." in hcortex_r


def test_render_puml_view_preserves_verbatim():
    """PUML VIEW must preserve DIAG content verbatim."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$6
VIEW:arch{kind:puml,target:"DIAG:arq",reverse:"verbatim_to_bloque",preserve:"verbatim",title:"Architecture",status:cur}
DIAG:arq{
@startuml
skinparam componentStyle rectangle
title Test
A --> B
@enduml
}
```'''
    doc = parse_cortex_v2(text)
    hcortex_r, _ = render_hcortex(doc)
    assert "```puml" in hcortex_r
    assert "@startuml" in hcortex_r
    assert "A --> B" in hcortex_r
    assert "@enduml" in hcortex_r
    assert "<!-- VIEW:arch" in hcortex_r
    assert "<!-- /VIEW:arch -->" in hcortex_r


def test_render_includes_view_open_close_markers():
    """Every VIEW block must have opening and closing markers."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$0
VIEW:glossary{kind:table,target:"$0:canonical_sigils",reverse:"rows_to_entries",status:cur}
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"test"}
```'''
    doc = parse_cortex_v2(text)
    hcortex_r, _ = render_hcortex(doc)
    # Must have matching open/close
    open_count = hcortex_r.count("<!-- VIEW:")
    close_count = hcortex_r.count("<!-- /VIEW:")
    assert open_count == close_count, f"Open={open_count}, Close={close_count}"


def test_render_unmapped_entries_warning():
    """Entries not covered by VIEW must produce warnings."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$0
VIEW:glossary{kind:table,target:"$0:canonical_sigils",reverse:"rows_to_entries",status:cur}
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"test"}

$1
IDN:project{name:"test"}
DOM:scope{domain:"test"}
```'''
    doc = parse_cortex_v2(text)
    hcortex_r, diags = render_hcortex(doc)
    # $1 entries are not covered by any VIEW
    assert any(d.code == "W_VIEW_UNUSED_ENTRY" for d in diags)


def test_render_kv_table_view():
    """KV table VIEW must produce a key/value table."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$1
VIEW:identity{kind:kv_table,target:"IDN:project",fields:"name,version",reverse:"row_to_attrs",title:"Identity",status:cur}
IDN:project{name:"CODEC-CORTEX",version:"1.0.0"}
```'''
    doc = parse_cortex_v2(text)
    hcortex_r, _ = render_hcortex(doc)
    assert "| Campo | Valor |" in hcortex_r
    assert "| name | CODEC-CORTEX |" in hcortex_r
    assert "| version | 1.0.0 |" in hcortex_r


def test_render_hcortex_r_preserves_cortex_roundtrip():
    """Adding VIEW directives must not break CORTEX roundtrip."""

    with open(SKILL_CORTEX_PATH, 'rb') as f:
        original_bytes = f.read()
    text = original_bytes.decode('utf-8')
    doc = parse_cortex_v2(text)
    reproduced = write_cortex_v2(doc)
    assert original_bytes == reproduced.encode('utf-8'), "CORTEX roundtrip must still be byte-identical"


def test_cli_v2_convert_to_hcortex_r(tmp_path):
    """CLI: cortex v2-convert --from cortex --to hcortex-r must work."""

    import subprocess
    out_path = str(tmp_path / "generated.md")
    r = subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {SRC_DIR!r}); from cortex.cli.main import main; sys.exit(main() or 0)",
         "v2-convert", SKILL_CORTEX_PATH, "--from", "cortex", "--to", "hcortex-r", "--out", out_path],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": SRC_DIR},
    )
    assert r.returncode == 0, f"v2-convert failed: {r.stderr}"
    assert os.path.exists(out_path)
    with open(out_path) as f:
        content = f.read()
    assert "reversible: true" in content
    assert "view_schema: 1" in content


# ---------------------------------------------------------------------------
# Kind/Reverse compatibility
# ---------------------------------------------------------------------------

def test_kind_reverse_compat_table():
    """Table kind must be compatible with rows_to_entries and columns_to_attrs."""

    assert ReverseStrategy.ROWS_TO_ENTRIES in KIND_REVERSE_COMPAT[ViewKind.TABLE]
    assert ReverseStrategy.COLUMNS_TO_ATTRS in KIND_REVERSE_COMPAT[ViewKind.TABLE]
    assert ReverseStrategy.BODY_TO_CUERPO not in KIND_REVERSE_COMPAT[ViewKind.TABLE]


def test_kind_reverse_compat_prose():
    """Prose kind must be compatible with body_to_cuerpo only."""

    assert ReverseStrategy.BODY_TO_CUERPO in KIND_REVERSE_COMPAT[ViewKind.PROSE]
    assert ReverseStrategy.ROWS_TO_ENTRIES not in KIND_REVERSE_COMPAT[ViewKind.PROSE]


def test_kind_reverse_compat_puml():
    """PUML kind must be compatible with verbatim_to_bloque only."""

    assert ReverseStrategy.VERBATIM_TO_BLOQUE in KIND_REVERSE_COMPAT[ViewKind.PUML]
    assert ReverseStrategy.ROWS_TO_ENTRIES not in KIND_REVERSE_COMPAT[ViewKind.PUML]
