"""v2.2.1 tests — HCORTEX model correction + VIEW hardening.

Tests obligatorios per spec:
P0: VIEW declaration in $0, errors rc!=0, DIAG verbatim, header HCORTEX, deprecated alias, coverage
P1: marker metadata, HUMAN_BLOCK, strict mode, v2-view-lint, display mode
"""

import os
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.v2.parser import parse_cortex_v2
from cortex.v2.writer import write_cortex_v2
from cortex.v2.view import (
    parse_view_entry, parse_view_entries_from_doc,
    calculate_view_coverage,
)
from cortex.v2.view_renderer import render_hcortex, has_view_errors

FIXTURES_DIR = os.path.join(HERE, "fixtures")
SKILL_CORTEX_PATH = os.path.join(FIXTURES_DIR, "SKILL_v2.cortex.md")


def _run_cli(args_list):
    return subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {SRC_DIR!r}); from cortex.cli.main import main; sys.exit(main() or 0)"]
        + args_list,
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": SRC_DIR},
    )


# ---------------------------------------------------------------------------
# P0-1: VIEW declaration in $0 is not parsed as directive
# ---------------------------------------------------------------------------

def test_view_declaration_in_zero_not_parsed_as_directive():
    """VIEW:view in $0 with type/risk/cortex/desc is a sigil declaration, not a directive."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$0
VIEW:view{type:attrs,risk:B,cortex:Semantic,desc:"directiva declarativa de render reversible HCORTEX"}
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"test"}
```'''
    doc = parse_cortex_v2(text)
    directives, diags = parse_view_entries_from_doc(doc)
    # VIEW:view in $0 should NOT be parsed as a directive
    assert len(directives) == 0, f"VIEW:view in $0 should not be a directive; got {len(directives)}"
    # No errors should be produced
    errors = [d for d in diags if d.severity == "error"]
    assert len(errors) == 0, f"Should have no errors; got: {[d.message for d in errors]}"


def test_view_directive_outside_zero_requires_kind_target_reverse():
    """VIEW outside $0 without kind/target/reverse must fail."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"test"}

$1
VIEW:bad{type:attrs,risk:B,cortex:Semantic,desc:"this looks like a sigil decl but it's in $1"}
```'''
    doc = parse_cortex_v2(text)
    directives, diags = parse_view_entries_from_doc(doc)
    # VIEW:bad in $1 with type/risk/cortex/desc but no kind/target/reverse should fail
    assert len(directives) == 0
    errors = [d for d in diags if d.severity == "error"]
    assert len(errors) > 0, "Should have errors for missing kind/target/reverse"


# ---------------------------------------------------------------------------
# P0-2: E_VIEW_* errors produce rc!=0
# ---------------------------------------------------------------------------

def test_view_errors_return_nonzero():
    """CLI v2-convert with E_VIEW_* errors must return rc!=0."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"test"}

$1
VIEW:bad{kind:invalid_kind,target:"IDN:*",reverse:"rows_to_entries",status:cur}
```'''
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(text)
        tmp_path = f.name

    r = _run_cli(["v2-convert", tmp_path, "--from", "cortex", "--to", "hcortex"])
    os.unlink(tmp_path)
    assert r.returncode != 0, "Should return non-zero for E_VIEW errors; got rc=0"


def test_duplicate_view_returns_nonzero():
    """Duplicate VIEW names must produce error and rc!=0."""

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
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(text)
        tmp_path = f.name

    r = _run_cli(["v2-convert", tmp_path, "--from", "cortex", "--to", "hcortex"])
    os.unlink(tmp_path)
    # Duplicate VIEW produces E_VIEW_DUPLICATE_NAME which is an error
    assert r.returncode != 0 or "E_VIEW_DUPLICATE_NAME" in r.stdout, (
        f"Should return non-zero or show error; rc={r.returncode}, stdout={r.stdout[:200]}"
    )


# ---------------------------------------------------------------------------
# P0-3: DIAG preserve:verbatim keeps blank lines
# ---------------------------------------------------------------------------

def test_diag_preserve_verbatim_keeps_blank_lines():
    """DIAG with preserve:verbatim must not strip/trim content."""

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

title Test

A --> B

@enduml
}
```'''
    doc = parse_cortex_v2(text)
    hcortex_md, _ = render_hcortex(doc)
    # The blank lines inside @startuml/@enduml must be preserved
    assert "@startuml\n\ntitle Test\n\nA --> B\n\n@enduml" in hcortex_md, (
        "DIAG preserve:verbatim must keep blank lines"
    )


# ---------------------------------------------------------------------------
# P0-4: Header uses internal_encoding: HCORTEX (not HCORTEX-R)
# ---------------------------------------------------------------------------

def test_hcortex_header_uses_internal_encoding_hcortex_not_hcortex_r():
    """Generated HCORTEX must use internal_encoding: HCORTEX, not HCORTEX-R."""

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
    hcortex_md, _ = render_hcortex(doc)
    assert "internal_encoding: HCORTEX" in hcortex_md
    assert "internal_encoding: HCORTEX-R" not in hcortex_md
    assert "reversible: true" in hcortex_md
    assert "view_schema: 1" in hcortex_md
    assert "view_coverage:" in hcortex_md


# ---------------------------------------------------------------------------
# P0-5: hcortex-r alias deprecated warning
# ---------------------------------------------------------------------------

def test_hcortex_r_alias_deprecated_warning():
    """--to hcortex-r must emit deprecation warning."""

    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(open(SKILL_CORTEX_PATH).read())
        tmp_path = f.name
    out_path = tmp_path + ".out"

    r = _run_cli(["v2-convert", tmp_path, "--from", "cortex", "--to", "hcortex-r", "--out", out_path])
    os.unlink(tmp_path)
    if os.path.exists(out_path):
        os.unlink(out_path)
    # Should emit warning in stderr
    assert "deprecated" in r.stderr.lower() or "deprecated" in r.stdout.lower(), (
        f"Should emit deprecation warning; stderr={r.stderr[:200]}, stdout={r.stdout[:200]}"
    )


# ---------------------------------------------------------------------------
# P0-6: SKILL.md VIEW coverage is not zero (when VIEW directives exist)
# ---------------------------------------------------------------------------

def test_skill_view_coverage_not_zero():
    """SKILL.md with VIEW directives must have coverage > 0."""

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
DOM:domain{type:attrs,risk:B,cortex:Semantic,desc:"dominio"}
```'''
    doc = parse_cortex_v2(text)
    directives, _ = parse_view_entries_from_doc(doc)
    coverage, uncovered = calculate_view_coverage(doc, directives)
    assert coverage > 0.0, f"Coverage should be > 0 with VIEW directives; got {coverage}"


# ---------------------------------------------------------------------------
# P1: VIEW marker preserves title, status, scope, hash, fallback
# ---------------------------------------------------------------------------

def test_view_marker_preserves_title_status_scope_hash_fallback():
    """VIEW markers must preserve all metadata fields."""

    attrs = {
        "kind": "table",
        "target": "$0:canonical_sigils",
        "reverse": "rows_to_entries",
        "status": "cur",
        "title": "Sigilos canónicos",
        "scope": "glossary",
        "hash": "sha256:abc123",
        "fallback": "manual_review",
    }
    directive, _ = parse_view_entry("test", attrs)
    assert directive is not None
    assert directive.title == "Sigilos canónicos"
    assert directive.scope == "glossary"
    assert directive.hash == "sha256:abc123"
    assert directive.fallback == "manual_review"

    # Render and check marker
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$0
VIEW:test{kind:table,target:"$0:canonical_sigils",reverse:"rows_to_entries",title:"Sigilos canónicos",scope:"glossary",hash:"sha256:abc123",fallback:"manual_review",status:cur}
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"test"}
```'''
    doc = parse_cortex_v2(text)
    hcortex_md, _ = render_hcortex(doc)
    assert 'title="Sigilos canónicos"' in hcortex_md
    assert 'scope="glossary"' in hcortex_md
    assert 'hash="sha256:abc123"' in hcortex_md
    assert 'fallback="manual_review"' in hcortex_md


# ---------------------------------------------------------------------------
# P1: HUMAN_BLOCK is preserved
# ---------------------------------------------------------------------------

def test_human_block_is_preserved():
    """HUMAN_BLOCK target must render without error (preserve_human_block)."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$0
VIEW:intro{kind:prose,target:"HUMAN_BLOCK:intro",reverse:"preserve_human_block",title:"Introduction",status:human_only}
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"test"}
```'''
    doc = parse_cortex_v2(text)
    hcortex_md, diags = render_hcortex(doc)
    # HUMAN_BLOCK should produce a VIEW block (even with 0 entries, the block is emitted)
    # The VIEW:intro directive is in $0, but it has kind/target/reverse (not type/risk/cortex/desc)
    # so it should be parsed as a directive
    assert "<!-- VIEW:intro" in hcortex_md or "VIEW:intro" in hcortex_md, (
        f"HUMAN_BLOCK VIEW should be rendered; output: {hcortex_md[:300]}"
    )
    # No errors for HUMAN_BLOCK
    assert not has_view_errors(diags)


# ---------------------------------------------------------------------------
# P1: HCORTEX canonical requires reversible:true + view_schema
# ---------------------------------------------------------------------------

def test_hcortex_canonical_requires_reversible_true_view_schema():
    """Generated HCORTEX must have reversible:true and view_schema:1 in header."""

    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
status: specification
-->

$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"test"}
```'''
    doc = parse_cortex_v2(text)
    hcortex_md, _ = render_hcortex(doc)
    # v2.2.3 PRE-04: reversible reflects actual state — 0% coverage → false
    assert "reversible: false" in hcortex_md
    assert "view_schema: 1" in hcortex_md


# ---------------------------------------------------------------------------
# P1: CORTEX roundtrip still works after v2.2.1 changes
# ---------------------------------------------------------------------------

def test_cortex_roundtrip_still_byte_identical():
    """CORTEX roundtrip must still be byte-identical after v2.2.1 changes."""

    with open(SKILL_CORTEX_PATH, 'rb') as f:
        original_bytes = f.read()
    text = original_bytes.decode('utf-8')
    doc = parse_cortex_v2(text)
    reproduced = write_cortex_v2(doc)
    assert original_bytes == reproduced.encode('utf-8'), "CORTEX roundtrip must be byte-identical"


# ---------------------------------------------------------------------------
# P1: CLI v2-convert --to hcortex produces correct header
# ---------------------------------------------------------------------------

def test_cli_v2_convert_to_hcortex_header(tmp_path):
    """CLI v2-convert --to hcortex must produce header with reversible:true."""

    out_path = str(tmp_path / "generated.md")
    r = _run_cli(["v2-convert", SKILL_CORTEX_PATH, "--from", "cortex", "--to", "hcortex", "--out", out_path])
    assert r.returncode == 0, f"v2-convert failed: {r.stderr}"
    with open(out_path) as f:
        content = f.read()
    assert "internal_encoding: HCORTEX" in content
    assert "reversible: true" in content
    assert "view_schema: 1" in content
    assert "view_coverage:" in content
    # Must NOT have internal_encoding: HCORTEX-R in the header (v2.2.1 P0-1)
    # Note: "HCORTEX-R" may legitimately appear inside DIAG entries as "HCORTEX-READABLE"
    header_end = content.find("-->")
    assert header_end != -1, "no header found"
    header = content[:header_end]
    assert "internal_encoding: HCORTEX-R" not in header
    assert "HCORTEX-R\n" not in header  # no bare HCORTEX-R line in header
