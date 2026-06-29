"""v2.2.2 tests — surgical hardening post-auditoría v2.2.1.

5 brechas cerradas:
1. SKILL.md migrado con VIEW directives reales (100% coverage)
2. E_VIEW_EMPTY_TARGET renombrado a W_VIEW_EMPTY_TARGET (consistencia)
3. --out no se escribe si hay E_VIEW_* (salvo --force-write-on-error)
4. --strict promueve W_VIEW_* a errors
5. Detección de targets heterogéneos (W_VIEW_HETEROGENEOUS_TARGET)

6. Documentación alineada al modelo CORTEX/HCORTEX/VIEW
"""

import os
import sys
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.v2.parser import parse_cortex_v2
from cortex.v2.writer import write_cortex_v2
from cortex.v2.view import (
    parse_view_entries_from_doc,
    calculate_view_coverage,
    resolve_target,
)
from cortex.v2.view_renderer import render_hcortex, has_view_errors, has_view_warnings

FIXTURES_DIR = os.path.join(HERE, "fixtures")
SKILL_CORTEX_PATH = os.path.join(FIXTURES_DIR, "SKILL_v2.cortex.md")


def _run_cli(args_list):
    """Run the cortex CLI with the given args, return CompletedProcess."""
    return subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {SRC_DIR!r}); from cortex.cli.main import main; sys.exit(main() or 0)"]
        + args_list,
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": SRC_DIR},
    )


# ---------------------------------------------------------------------------
# P0-1: SKILL.md migrado con VIEW directives (100% coverage)
# ---------------------------------------------------------------------------

def test_skill_v2_2_2_has_section_13_with_view_directives():
    """SKILL_v2.cortex.md must have a $13 section with VIEW directives."""
    with open(SKILL_CORTEX_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    sec13 = doc.get_section("$13")
    assert sec13 is not None, "SKILL.md must have $13 section"
    view_entries = [e for e in sec13.entries if e.sigil == "VIEW"]
    assert len(view_entries) >= 40, f"Need ≥40 VIEW directives; got {len(view_entries)}"


def test_skill_v2_2_2_view_coverage_100_percent():
    """SKILL_v2.cortex.md must achieve 100% VIEW coverage after migration."""
    with open(SKILL_CORTEX_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    directives, diags = parse_view_entries_from_doc(doc)
    assert len(directives) >= 40, f"Need ≥40 directives; got {len(directives)}"

    coverage, uncovered = calculate_view_coverage(doc, directives)
    assert coverage == 1.0, f"Coverage must be 100%; got {coverage:.1%}, uncovered={uncovered[:5]}"
    assert len(uncovered) == 0, f"Uncovered entries: {uncovered[:5]}"


def test_skill_v2_2_2_roundtrip_byte_identical():
    """SKILL_v2.cortex.md with $13 VIEW section must roundtrip byte-identical."""
    with open(SKILL_CORTEX_PATH, "rb") as f:
        original_bytes = f.read()
    text = original_bytes.decode("utf-8")
    doc = parse_cortex_v2(text)
    reproduced = write_cortex_v2(doc)
    repro_bytes = reproduced.encode("utf-8")
    assert repro_bytes == original_bytes, (
        f"Roundtrip FAILED: {len(original_bytes)} vs {len(repro_bytes)}"
    )


def test_skill_v2_2_2_v2_convert_no_warnings():
    """CLI v2-convert on SKILL_v2.cortex.md must produce 0 warnings, 0 errors."""
    r = _run_cli(["v2-convert", SKILL_CORTEX_PATH,
                  "--from", "cortex", "--to", "hcortex", "--out", "/tmp/_v222_skill.md"])
    assert r.returncode == 0, f"rc={r.returncode}, stderr={r.stderr}"
    assert "errors:   0" in r.stdout, f"Expected 0 errors in stdout: {r.stdout}"
    assert "warnings: 0" in r.stdout, f"Expected 0 warnings in stdout: {r.stdout}"


# ---------------------------------------------------------------------------
# P0-2: E_VIEW_EMPTY_TARGET → W_VIEW_EMPTY_TARGET
# ---------------------------------------------------------------------------

def test_view_empty_target_uses_W_prefix():
    """Empty target must report W_VIEW_EMPTY_TARGET (not E_VIEW_EMPTY_TARGET)."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test"}
$2
VIEW:empty_target{kind:table,target:"$99",reverse:rows_to_entries,status:cur}
```'''
    doc = parse_cortex_v2(text)
    md, diags = render_hcortex(doc)
    codes = [d.code for d in diags]
    assert "W_VIEW_EMPTY_TARGET" in codes, f"Expected W_VIEW_EMPTY_TARGET in {codes}"
    assert "E_VIEW_EMPTY_TARGET" not in codes, f"Old E_VIEW_EMPTY_TARGET still present in {codes}"


def test_view_empty_target_severity_is_warning():
    """W_VIEW_EMPTY_TARGET must have severity='warning', not 'error'."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test"}
$2
VIEW:empty_target{kind:table,target:"$99",reverse:rows_to_entries,status:cur}
```'''
    doc = parse_cortex_v2(text)
    md, diags = render_hcortex(doc)
    empty_target_diags = [d for d in diags if d.code == "W_VIEW_EMPTY_TARGET"]
    assert len(empty_target_diags) >= 1
    assert all(d.severity == "warning" for d in empty_target_diags)


def test_view_empty_target_does_not_cause_nonzero_rc():
    """Empty target alone (no E_VIEW_*) must NOT cause rc=1."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test"}
$2
VIEW:empty_target{kind:table,target:"$99",reverse:rows_to_entries,status:cur}
```'''
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".cortex", delete=False) as f:
        f.write(text)
        tmp_path = f.name
    try:
        r = _run_cli(["v2-convert", tmp_path, "--from", "cortex", "--to", "hcortex",
                      "--out", "/tmp/_v222_empty.md"])
        assert r.returncode == 0, f"Empty target alone must NOT cause rc=1; got rc={r.returncode}, stderr={r.stderr}"
    finally:
        os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# P0-3: --out no se escribe si hay E_VIEW_* (salvo --force-write-on-error)
# ---------------------------------------------------------------------------

def _make_bad_view_cortex(tmp_path):
    """Create a CORTEX file with an E_VIEW_UNKNOWN_KIND error."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test"}
$2
VIEW:bad{kind:bogus,target:"IDN:*",reverse:rows_to_entries,status:cur}
```'''
    p = str(tmp_path / "bad.cortex")
    with open(p, "w") as f:
        f.write(text)
    return p


def test_out_not_written_on_view_errors(tmp_path):
    """--out must NOT be written when E_VIEW_* errors are present."""
    bad_path = _make_bad_view_cortex(tmp_path)
    out_path = str(tmp_path / "out.md")
    r = _run_cli(["v2-convert", bad_path, "--from", "cortex", "--to", "hcortex",
                  "--out", out_path])
    assert r.returncode == 1, f"Expected rc=1 on E_VIEW_*; got rc={r.returncode}"
    assert not os.path.exists(out_path), (
        f"--out must NOT be written on E_VIEW_* errors; file exists at {out_path}"
    )
    assert "NOT written" in r.stderr, f"Expected 'NOT written' in stderr: {r.stderr}"


def test_out_written_with_force_write_on_error(tmp_path):
    """--out IS written when --force-write-on-error is given, but rc is still 1."""
    bad_path = _make_bad_view_cortex(tmp_path)
    out_path = str(tmp_path / "out_forced.md")
    r = _run_cli(["v2-convert", bad_path, "--from", "cortex", "--to", "hcortex",
                  "--out", out_path, "--force-write-on-error"])
    assert r.returncode == 1, f"rc must still be 1 even with --force-write-on-error; got {r.returncode}"
    assert os.path.exists(out_path), (
        f"--out MUST be written with --force-write-on-error; missing {out_path}"
    )
    with open(out_path) as f:
        content = f.read()
    assert "internal_encoding: HCORTEX" in content


def test_out_written_when_no_errors(tmp_path):
    """--out IS written when there are no E_VIEW_* errors (normal case)."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test"}
$2
VIEW:ok{kind:table,target:"$1:IDN:*",reverse:rows_to_entries,fields:"name",status:cur}
```'''
    p = str(tmp_path / "ok.cortex")
    with open(p, "w") as f:
        f.write(text)
    out_path = str(tmp_path / "out_ok.md")
    r = _run_cli(["v2-convert", p, "--from", "cortex", "--to", "hcortex",
                  "--out", out_path])
    assert r.returncode == 0, f"rc=0 expected; got {r.returncode}, stderr={r.stderr}"
    assert os.path.exists(out_path), f"--out should exist when no errors: {out_path}"


# ---------------------------------------------------------------------------
# P0-4: --strict promueve W_VIEW_* a errors
# ---------------------------------------------------------------------------

def test_strict_promotes_w_view_to_errors(tmp_path):
    """--strict flag promotes W_VIEW_* warnings to errors (rc=1)."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test"}
$2
VIEW:empty{kind:table,target:"$99",reverse:rows_to_entries,status:cur}
```'''
    p = str(tmp_path / "warn.cortex")
    with open(p, "w") as f:
        f.write(text)
    out_path = str(tmp_path / "out_strict.md")
    r = _run_cli(["v2-convert", p, "--from", "cortex", "--to", "hcortex",
                  "--out", out_path, "--strict"])
    assert r.returncode == 1, f"Strict must promote W_VIEW_* to rc=1; got rc={r.returncode}"
    assert not os.path.exists(out_path), (
        f"--out should NOT be written in strict mode with W_VIEW_* promoted to errors"
    )


def test_strict_no_warnings_no_errors_normal(tmp_path):
    """--strict with no warnings/errors should still rc=0."""
    # Use the clean SKILL.md (100% coverage, 0 warnings, 0 errors)
    out_path = str(tmp_path / "out_skill_strict.md")
    r = _run_cli(["v2-convert", SKILL_CORTEX_PATH,
                  "--from", "cortex", "--to", "hcortex",
                  "--out", out_path, "--strict"])
    assert r.returncode == 0, f"rc=0 expected for clean SKILL.md; got {r.returncode}, stderr={r.stderr}"


# ---------------------------------------------------------------------------
# P0-5: Detección de targets heterogéneos (W_VIEW_HETEROGENEOUS_TARGET)
# ---------------------------------------------------------------------------

def test_heterogeneous_target_warns_without_fields():
    """Target matching entries with different entry_types AND no fields → warn."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test",version:"1.0"}
IDN:other{topic:"different",content:"mismatch"}
$2
VIEW:hetero{kind:table,target:"IDN:*",reverse:rows_to_entries,status:cur}
```'''
    doc = parse_cortex_v2(text)
    md, diags = render_hcortex(doc)
    codes = [d.code for d in diags]
    assert "W_VIEW_HETEROGENEOUS_TARGET" in codes, (
        f"Expected W_VIEW_HETEROGENEOUS_TARGET in {codes}"
    )


def test_heterogeneous_target_silent_with_fields():
    """Same heterogeneous target but WITH fields → no warning."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test",version:"1.0"}
IDN:other{topic:"different",content:"mismatch"}
$2
VIEW:hetero{kind:table,target:"IDN:*",reverse:rows_to_entries,fields:"name,version,topic,content",status:cur}
```'''
    doc = parse_cortex_v2(text)
    md, diags = render_hcortex(doc)
    codes = [d.code for d in diags]
    assert "W_VIEW_HETEROGENEOUS_TARGET" not in codes, (
        f"With explicit fields, no W_VIEW_HETEROGENEOUS_TARGET expected; got {codes}"
    )


def test_homogeneous_target_no_warn():
    """Target matching entries with same schema → no heterogeneous warning."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
REF:a{path:"a.md",role:"x"}
REF:b{path:"b.md",role:"y"}
REF:c{path:"c.md",role:"z"}
$2
VIEW:refs{kind:table,target:"$1:REF:*",reverse:rows_to_entries,status:cur}
```'''
    doc = parse_cortex_v2(text)
    md, diags = render_hcortex(doc)
    codes = [d.code for d in diags]
    assert "W_VIEW_HETEROGENEOUS_TARGET" not in codes, (
        f"Homogeneous target should not warn; got {codes}"
    )


def test_heterogeneous_target_strict_causes_nonzero_rc(tmp_path):
    """In strict mode, W_VIEW_HETEROGENEOUS_TARGET promotes to error → rc=1."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test",version:"1.0"}
IDN:other{topic:"different",content:"mismatch"}
$2
VIEW:hetero{kind:table,target:"IDN:*",reverse:rows_to_entries,status:cur}
```'''
    p = str(tmp_path / "hetero.cortex")
    with open(p, "w") as f:
        f.write(text)
    out_path = str(tmp_path / "out_hetero.md")
    r = _run_cli(["v2-convert", p, "--from", "cortex", "--to", "hcortex",
                  "--out", out_path, "--strict"])
    assert r.returncode == 1, f"Strict + hetero should rc=1; got {r.returncode}"


# ---------------------------------------------------------------------------
# P0-6: Documentación alineada (smoke test)
# ---------------------------------------------------------------------------

def test_readme_contains_conceptual_model():
    """README must contain the CORTEX/HCORTEX/VIEW conceptual model."""
    readme_path = os.path.abspath(os.path.join(HERE, "..", "..", "README.md"))
    with open(readme_path) as f:
        content = f.read()
    assert "Modelo conceptual" in content, "README must have 'Modelo conceptual' section"
    assert "CORTEX" in content
    assert "HCORTEX" in content
    assert "VIEW" in content
    assert "reversible" in content.lower()


def test_status_contains_v2_2_2_capabilities():
    """STATUS.md must list v2.2.2 capabilities."""
    status_path = os.path.abspath(os.path.join(HERE, "..", "..", "STATUS.md"))
    with open(status_path) as f:
        content = f.read()
    assert "2.2.2" in content, "STATUS must reference v2.2.2"
    assert "--force-write-on-error" in content
    assert "W_VIEW_HETEROGENEOUS_TARGET" in content
    assert "SKILL.md migrado con VIEW directives" in content


def test_changelog_contains_v2_2_2_entry():
    """CHANGELOG.md must have a v2.2.2 entry."""
    changelog_path = os.path.abspath(os.path.join(HERE, "..", "..", "CHANGELOG.md"))
    with open(changelog_path) as f:
        content = f.read()
    assert "## [2.2.2]" in content, "CHANGELOG must have [2.2.2] section"
    assert "W_VIEW_EMPTY_TARGET" in content
    assert "force-write-on-error" in content
    assert "W_VIEW_HETEROGENEOUS_TARGET" in content


# ---------------------------------------------------------------------------
# Resolver fixes for 3-part selectors
# ---------------------------------------------------------------------------

def test_resolver_3part_name_selector():
    """resolve_target must handle $N:SIGIL:name (3-part) correctly."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test"}
DOM:scope{domain:"x"}
$2
VIEW:test{kind:kv_table,target:"$1:IDN:project",reverse:row_to_attrs,status:cur}
```'''
    doc = parse_cortex_v2(text)
    results = resolve_target("$1:IDN:project", doc)
    assert len(results) == 1, f"Expected 1 result for $1:IDN:project; got {len(results)}"
    assert results[0].sigil == "IDN"
    assert results[0].name == "project"
    assert results[0].section == "$1"


def test_resolver_single_colon_meta_entry():
    """resolve_target must handle $0:NAME (single colon, meta entry)."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$0:enum_state{values:"cur,pln,fut"}
$1
IDN:project{name:"test"}
$2
VIEW:test{kind:kv_table,target:"$0:enum_state",reverse:row_to_attrs,status:cur}
```'''
    doc = parse_cortex_v2(text)
    results = resolve_target("$0:enum_state", doc)
    assert len(results) == 1, f"Expected 1 result for $0:enum_state; got {len(results)}"
    assert results[0].name == "enum_state"
    assert results[0].section == "$0"


def test_resolver_bang_sigil_with_section():
    """resolve_target must handle $4:!:* (! sigil in section)."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test"}
$4
!:rule1{rule:"first",survive:min}
!:rule2{rule:"second",survive:work}
$5
VIEW:rules{kind:list,target:"$4:!:*",reverse:items_to_entries,fields:"rule,survive",status:cur}
```'''
    doc = parse_cortex_v2(text)
    results = resolve_target("$4:!:*", doc)
    assert len(results) == 2, f"Expected 2 results for $4:!:*; got {len(results)}"
    assert all(r.sigil == "!" for r in results)
