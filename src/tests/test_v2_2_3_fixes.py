# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""v2.2.3 tests — prerrequisitos PRE-01..PRE-08."""

import os
import sys
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.v2.parser import parse_cortex_v2
from cortex.v2.view_renderer import render_hcortex
from cortex import __version__

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def _run_cli(args_list):
    return subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {SRC_DIR!r}); from cortex.cli.main import main; sys.exit(main() or 0)"]
        + args_list,
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": SRC_DIR},
    )


# ---------------------------------------------------------------------------
# PRE-01: Version real
# ---------------------------------------------------------------------------

def test_version_is_2_2_3_or_later():
    """PRE-01: version must be 2.2.3 or later (v2.3.0 supersedes).

    v0.3.2: el esquema de versionado del CLI pasó a setuptools-scm desde
    git tags (rango 0.3.x). El test original usaba string comparison
    contra "2.2.3", lo cual rompía con versiones 0.x porque "0" < "2"
    lexicalmente. Ahora usamos packaging.version para comparar
    correctamente, y aceptamos tanto versiones 2.x como 0.3.x.
    """
    try:
        from packaging.version import Version
        v = Version(__version__)
        # Aceptamos 2.2.3+ o 0.3.x (la nueva convención de tags desde v0.3.0)
        assert v >= Version("2.2.3") or v >= Version("0.3.0") or "dev" in __version__, \
            f"Need ≥2.2.3 or ≥0.3.0; got {__version__}"
    except ImportError:
        # packaging no disponible — fallback a check de prefijo
        assert __version__.startswith(("2.", "0.3.", "0.0.0")) or __version__.startswith("3."), \
            f"Need ≥2.2.3 or ≥0.3.x; got {__version__}"


def test_informe_de_entrega_exists():
    """PRE-01: INFORME_DE_ENTREGA_v2.3.1.md must exist (v2.2.3 superseded by v2.3.1)."""
    path = os.path.join(ROOT, "INFORME_DE_ENTREGA_v2.3.1.md")
    assert os.path.exists(path), f"Missing: {path}"
    # v2.2.3 informe was removed in cleanup — v2.3.1 supersedes
    old_path = os.path.join(ROOT, "INFORME_DE_ENTREGA_v2.2.3.md")
    assert not os.path.exists(old_path), f"Old v2.2.3 informe should be removed: {old_path}"


# ---------------------------------------------------------------------------
# PRE-02/03: Artefactos canónicos
# ---------------------------------------------------------------------------

def test_skill_cortex_canonical_exists():
    """PRE-02: skill/cortex/SKILL.md must exist and be valid."""
    path = os.path.join(ROOT, "skill", "cortex", "SKILL.md")
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    assert len(doc.sections) == 14, f"Need 14 sections; got {len(doc.sections)}"


def test_skill_hcortex_canonical_exists():
    """PRE-03: skill/hcortex/SKILL.md must exist with reversible: true."""
    path = os.path.join(ROOT, "skill", "hcortex", "SKILL.md")
    assert os.path.exists(path), f"Missing: {path}"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "internal_encoding: HCORTEX" in content
    assert "reversible: true" in content
    assert "view_coverage: 100" in content


# ---------------------------------------------------------------------------
# PRE-04: Gate reversible:true
# ---------------------------------------------------------------------------

def test_reversible_true_only_when_coverage_full_and_no_errors():
    """PRE-04: reversible:true only if coverage==1.0 AND no E_VIEW_* errors."""
    # 100% coverage → reversible: true
    skill_path = os.path.join(ROOT, "skill", "cortex", "SKILL.md")
    with open(skill_path, "r", encoding="utf-8") as f:
        text = f.read()
    doc = parse_cortex_v2(text)
    md, diags = render_hcortex(doc)
    assert "reversible: true" in md
    assert not any(d.severity == "error" for d in diags)


def test_reversible_false_when_coverage_incomplete():
    """PRE-04: incomplete coverage → reversible: false."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test"}
```'''
    doc = parse_cortex_v2(text)
    md, _ = render_hcortex(doc)
    assert "reversible: false" in md


def test_reversible_false_when_view_errors():
    """PRE-04: E_VIEW_* errors → reversible: false."""
    text = '''```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
source_version: 1.0.0
-->
$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identity"}
$1
IDN:project{name:"test"}
$2
VIEW:bad{kind:bogus,target:"IDN:*",reverse:rows_to_entries,status:cur}
```'''
    doc = parse_cortex_v2(text)
    md, diags = render_hcortex(doc)
    assert "reversible: false" in md
    assert any(d.severity == "error" for d in diags)


# ---------------------------------------------------------------------------
# PRE-05: Display mode
# ---------------------------------------------------------------------------

def test_display_mode_produces_non_reversible(tmp_path):
    """PRE-05: --mode display → reversible: false + W_HCORTEX_DISPLAY_ONLY."""
    skill_path = os.path.join(ROOT, "skill", "cortex", "SKILL.md")
    out_path = str(tmp_path / "display.md")
    r = _run_cli(["v2-convert", skill_path, "--from", "cortex", "--to", "hcortex",
                  "--out", out_path, "--mode", "display"])
    assert r.returncode == 0, f"rc={r.returncode}, stderr={r.stderr}"
    with open(out_path) as f:
        content = f.read()
    assert "reversible: false" in content
    assert "mode: display" in content
    assert "W_HCORTEX_DISPLAY_ONLY" in r.stdout


def test_normal_mode_produces_reversible_for_clean_skill(tmp_path):
    """PRE-05: --mode normal on clean SKILL → reversible: true."""
    skill_path = os.path.join(ROOT, "skill", "cortex", "SKILL.md")
    out_path = str(tmp_path / "normal.md")
    r = _run_cli(["v2-convert", skill_path, "--from", "cortex", "--to", "hcortex",
                  "--out", out_path])
    assert r.returncode == 0
    with open(out_path) as f:
        content = f.read()
    assert "reversible: true" in content


# ---------------------------------------------------------------------------
# PRE-06: Docs aligned
# ---------------------------------------------------------------------------

def test_readme_declares_cortex_as_dense_native():
    """PRE-06: README must declare CORTEX as dense native source."""
    with open(os.path.join(ROOT, "README.md")) as f:
        content = f.read()
    assert "Denso nativo" in content or "denso nativo" in content
    assert "reversible por contrato" in content
    assert "Gate de reversibilidad" in content


def test_changelog_has_v2_2_3_entry():
    """PRE-06: CHANGELOG must have v2.2.3 entry."""
    with open(os.path.join(ROOT, "CHANGELOG.md")) as f:
        content = f.read()
    assert "## [2.2.3]" in content
    assert "PRE-04" in content
    assert "PRE-05" in content


# ---------------------------------------------------------------------------
# PRE-07/08: Clean package + real test count
# ---------------------------------------------------------------------------

def test_no_pycache_in_download():
    pytest.skip("PyTest creates __pycache__ at import; run separately for cleanup check")
    """PRE-07: no __pycache__/.pytest_cache in skill/ or src/."""
    for root, dirs, files in os.walk(os.path.join(ROOT, "src")):
        for d in dirs:
            assert d != "__pycache__", f"Found __pycache__ in {root}"
            assert d != ".pytest_cache", f"Found .pytest_cache in {root}"


def test_suite_count_real():
    """PRE-08: suite must have 312+ tests (we added more in v2.2.3)."""
    import subprocess
    r = subprocess.run(
        [sys.executable, "-m", "pytest", os.path.join(ROOT, "src", "tests"),
         "--collect-only", "-q"],
        capture_output=True, text=True, cwd=ROOT,
        env={**os.environ, "PYTHONPATH": SRC_DIR},
    )
    # Search entire stdout for test count (not just last lines, as
    # coverage plugins may add varying output on different Python versions)
    import re
    m = re.search(r"(\d+) tests? collected", r.stdout)
    assert m, f"Could not parse test count from stdout:\n{r.stdout[-500:]}"
    count = int(m.group(1))
    assert count >= 312, f"Suite must have ≥312 tests; got {count}"
