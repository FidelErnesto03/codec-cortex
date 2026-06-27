"""v1.1.3 fixes — tests for the 10 issues raised in the fourth review.

P0 (critical):
  - recover reconstructs $0 for files that start directly with entries
  - E031_SECRET_NOT_BYPASSABLE cannot be bypassed with --force
  - CRUD blocks critical sigils with missing required fields
  - FCS/OBJ status:done does NOT count as active

P1 (audit/output):
  - Perfil: CORTEX-<LEVEL> is the first real line of HCORTEX-READ
  - render --mode audit declares Mode: AUDIT (not READABLE)
  - source is visible for cuerpo/bloque entries in audit mode

P2 (CLI/canon):
  - cortex decode <file> works without --mode (defaults to readable)
  - recovery legacy claim is "current with known limits"
  - SKILL_canon.md is present and matches the declared version
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
from cortex.hcortex import recover_cortex, render_hcortex_read
from cortex.core.validator import validate
from cortex.core.document_kind import DocumentKind, validate_level_policy


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
# P0-1: recover reconstructs $0 for files starting directly with entries
# ---------------------------------------------------------------------------

def test_recover_entry_first_file_without_glossary():
    """recover must reconstruct $0 even when the file starts with entries."""

    legacy = (
        'IDN:package{name:"legacy", kind:"package", status:"current"}\n'
        'KNW:topic{topic:"x", content:"y", status:"current"}\n'
    )
    result = recover_cortex(legacy, path="legacy.cortex", embed_aud_rsk=True)
    # Glossary must be reconstructed with IDN and KNW
    assert "IDN" in result.doc.glossary.sigils, "IDN not in reconstructed glossary"
    assert "KNW" in result.doc.glossary.sigils, "KNW not in reconstructed glossary"
    # Should have the E030_RECOVERY_INCOMPLETE diagnostic
    codes = [d["code"] for d in result.diagnostics]
    assert "E030_RECOVERY_INCOMPLETE" in codes, f"expected E030, got {codes}"
    # verify --strict must pass (no E003_UNKNOWN_SIGIL)
    diags = validate(result.doc, strict=True)
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E003_UNKNOWN_SIGIL" not in codes, (
        f"recovered file should not have unknown sigils; got E003: {codes}"
    )


def test_recover_entry_first_file_cli_verify_strict(tmp_path):
    """End-to-end CLI: recover + verify --strict on entry-first legacy file."""

    legacy_path = str(tmp_path / "legacy.cortex")
    with open(legacy_path, "w") as f:
        f.write(
            'IDN:package{name:"legacy", kind:"package", status:"current"}\n'
            'KNW:topic{topic:"x", content:"y", status:"current"}\n'
        )
    out_path = str(tmp_path / "legacy.fixed.cortex")

    r = _run_cli(["recover", legacy_path, "--out", out_path, "--embed-aud-rsk"])
    assert r.returncode == 0, f"recover failed: {r.stderr}"

    r = _run_cli(["verify", out_path, "--strict"])
    assert r.returncode == 0, (
        f"verify --strict should pass on recovered entry-first file; "
        f"rc={r.returncode}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )


# ---------------------------------------------------------------------------
# P0-2: E031_SECRET_NOT_BYPASSABLE cannot be bypassed with --force
# ---------------------------------------------------------------------------

def test_secret_not_bypassable_with_force(tmp_path):
    """--force must NOT override E031_SECRET_NOT_BYPASSABLE."""

    # Create a clean brain
    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    # Try to add a secret with --force
    r = _run_cli([
        "add", path, "--section", "$3", "--sigil", "REF", "--name", "secret",
        "--value", 'provider:"x", password:"abc123456"',
        "--create-section", "--force",
    ])
    assert r.returncode != 0, (
        f"--force should NOT bypass secret detection; rc={r.returncode}\n{r.stdout}"
    )
    payload = json.loads(r.stdout)
    assert payload["ok"] is False
    assert "E031_SECRET_NOT_BYPASSABLE" in str(payload.get("diagnostics", []))


def test_secret_bypassable_with_unsafe_forensics_flag(tmp_path):
    """--unsafe-allow-secret-forensics CAN bypass secret detection (forensic only)."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    r = _run_cli([
        "add", path, "--section", "$3", "--sigil", "REF", "--name", "secret",
        "--value", 'provider:"x", password:"abc123456"',
        "--create-section", "--force", "--unsafe-allow-secret-forensics",
    ])
    # With the forensic flag, the secret bypass should work
    assert r.returncode == 0, (
        f"--unsafe-allow-secret-forensics should allow forensic bypass; "
        f"rc={r.returncode}\n{r.stdout}"
    )


def test_secret_finding_tagged_non_bypassable():
    """Secret findings must have bypassable=False in the diagnostic."""

    doc = build_brain()
    sec = doc.get_or_create_section("$3")
    sec.entries.append(build_entry_from_value(
        "$3", "REF", "creds", "attrs",
        {"provider": "x", "password": "abc123456"},
    ))
    diags = validate(doc)
    secret_diags = [
        d for d in diags
        if d.get("code") in ("E031_SECRET_NOT_BYPASSABLE", "E028_SECRET_IN_CLEAR")
    ]
    assert secret_diags, "expected at least one secret finding"
    for d in secret_diags:
        assert d.get("bypassable") is False, (
            f"secret finding must be bypassable=False, got: {d}"
        )


# ---------------------------------------------------------------------------
# P0-3: CRUD blocks critical sigils with missing required fields
# ---------------------------------------------------------------------------

def test_critical_sigil_incomplete_blocked_by_default(tmp_path):
    """add with incomplete OBJ must be blocked by default (non-bypassable)."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    r = _run_cli([
        "add", path, "--section", "$2", "--sigil", "OBJ", "--name", "partial",
        "--value", 'goal:"partial"',
    ])
    assert r.returncode != 0, (
        f"incomplete OBJ should be blocked; rc={r.returncode}\n{r.stdout}"
    )
    payload = json.loads(r.stdout)
    assert payload["ok"] is False
    diag_codes = [d.get("code") for d in payload.get("diagnostics", [])]
    assert "E032_CRITICAL_SIGIL_INCOMPLETE" in diag_codes, (
        f"expected E032, got: {diag_codes}"
    )


def test_critical_sigil_incomplete_not_bypassable_with_force(tmp_path):
    """--force must NOT override E032_CRITICAL_SIGIL_INCOMPLETE."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    r = _run_cli([
        "add", path, "--section", "$2", "--sigil", "OBJ", "--name", "partial",
        "--value", 'goal:"partial"', "--force",
    ])
    assert r.returncode != 0, (
        f"--force should NOT bypass critical sigil completeness; rc={r.returncode}\n{r.stdout}"
    )


def test_critical_sigil_complete_passes(tmp_path):
    """A complete OBJ entry should pass the gate."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    r = _run_cli([
        "add", path, "--section", "$2", "--sigil", "OBJ", "--name", "extra",
        "--value", 'goal:"extra", status:"planned", success:"criterion", survive:"work"',
        "--allow-duplicate",
    ])
    assert r.returncode == 0, f"complete OBJ should pass; rc={r.returncode}\n{r.stdout}"


# ---------------------------------------------------------------------------
# P0-4: FCS/OBJ status:done does NOT count as active
# ---------------------------------------------------------------------------

def test_fcs_obj_done_not_active():
    """A brain with FCS and OBJ in status:done must fail verify --strict."""

    doc = build_brain()
    # Set FCS and OBJ to done
    fcs = doc.find_entries(sigil="FCS")[0]
    fcs.value["status"] = "done"
    obj = doc.find_entries(sigil="OBJ")[0]
    obj.value["status"] = "done"
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E024_LEVEL2_MISSING_FOCUS" in codes, (
        f"brain with FCS/OBJ done should fail; got: {codes}"
    )


def test_fcs_obj_current_passes():
    """A brain with FCS and OBJ in status:current must pass."""

    doc = build_brain()
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E024_LEVEL2_MISSING_FOCUS" not in codes


def test_fcs_obj_blocked_passes():
    """A brain with FCS and OBJ in status:blocked must pass (blocked is active)."""

    doc = build_brain()
    fcs = doc.find_entries(sigil="FCS")[0]
    fcs.value["status"] = "blocked"
    obj = doc.find_entries(sigil="OBJ")[0]
    obj.value["status"] = "blocked"
    diags = validate(doc, strict=True, kind=DocumentKind("brain", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E024_LEVEL2_MISSING_FOCUS" not in codes


# ---------------------------------------------------------------------------
# P1-5: Perfil is the first real line of HCORTEX-READ
# ---------------------------------------------------------------------------

def test_perfil_is_first_line_of_hcortex_read():
    """The first line of HCORTEX-READ must be 'Perfil: CORTEX-<LEVEL>'."""

    doc = build_brain()
    md = render_hcortex_read(doc, profile="WORK", mode="READABLE")
    first_line = md.splitlines()[0]
    assert first_line.startswith("Perfil: CORTEX-"), (
        f"first line should be 'Perfil: CORTEX-<LEVEL>', got: {first_line!r}"
    )


def test_perfil_first_line_all_profiles():
    """Test all profiles produce Perfil as the first line."""

    doc = build_brain()
    for profile in ("MIN", "RECOVERY", "WORK", "FULL"):
        md = render_hcortex_read(doc, profile=profile, mode="READABLE")
        first_line = md.splitlines()[0]
        assert first_line == f"Perfil: CORTEX-{profile}", (
            f"profile {profile}: first line should be 'Perfil: CORTEX-{profile}', "
            f"got: {first_line!r}"
        )


# ---------------------------------------------------------------------------
# P1-6: render --mode audit declares Mode: AUDIT
# ---------------------------------------------------------------------------

def test_audit_mode_declares_audit():
    """render --mode audit must declare 'Mode: AUDIT' in the header."""

    doc = build_brain()
    md = render_hcortex_read(doc, profile="WORK", mode="AUDIT")
    # Find the Mode: line
    mode_lines = [line for line in md.splitlines() if "Mode:" in line]
    assert mode_lines, "expected a 'Mode:' line in HCORTEX-READ header"
    assert any("AUDIT" in line for line in mode_lines), (
        f"expected 'Mode: AUDIT' in header, got: {mode_lines}"
    )


def test_readable_mode_declares_readable():
    """render --mode readable (default) must declare 'Mode: READABLE'."""

    doc = build_brain()
    md = render_hcortex_read(doc, profile="WORK", mode="READABLE")
    mode_lines = [line for line in md.splitlines() if "Mode:" in line]
    assert mode_lines
    assert any("READABLE" in line for line in mode_lines)


# ---------------------------------------------------------------------------
# P1-7: source visible for cuerpo/bloque in audit mode
# ---------------------------------------------------------------------------

def test_source_visible_for_cuerpo_in_audit():
    """AXM (cuerpo) entries must have a visible 'source:' line in audit mode."""

    doc = build_brain()
    # Add an AXM entry
    sec = doc.get_or_create_section("$4", title="RULES")
    sec.entries.append(build_entry_from_value(
        "$4", "AXM", "principle", "cuerpo",
        "This is a principle.",
    ))
    md = render_hcortex_read(doc, profile="FULL", mode="AUDIT")
    # Find the AXM:principle section and check for visible source line
    assert "source: `AXM:principle`" in md, (
        "expected visible 'source: `AXM:principle`' line in audit mode for cuerpo entry"
    )


def test_source_visible_for_bloque_in_audit():
    """DIAG (bloque) entries must have a visible 'source:' line in audit mode."""

    doc = build_brain()
    sec = doc.get_or_create_section("$6", title="DIAGRAMS")
    sec.entries.append(build_entry_from_value(
        "$6", "DIAG", "flow", "bloque",
        "@startuml\nA-->B\n@enduml",
    ))
    md = render_hcortex_read(doc, profile="FULL", mode="AUDIT")
    assert "source: `DIAG:flow`" in md, (
        "expected visible 'source: `DIAG:flow`' line in audit mode for bloque entry"
    )


def test_source_not_visible_in_readable_mode():
    """In READABLE mode, cuerpo/bloque should NOT have visible source lines."""

    doc = build_brain()
    sec = doc.get_or_create_section("$4", title="RULES")
    sec.entries.append(build_entry_from_value(
        "$4", "AXM", "principle", "cuerpo",
        "This is a principle.",
    ))
    md = render_hcortex_read(doc, profile="WORK", mode="READABLE")
    assert "source: `AXM:principle`" not in md


# ---------------------------------------------------------------------------
# P2-8: cortex decode <file> works without --mode
# ---------------------------------------------------------------------------

def test_decode_without_mode_defaults_to_readable(tmp_path):
    """cortex decode <file> (no --mode) must produce readable output."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    r = _run_cli(["decode", path])
    assert r.returncode == 0, f"decode without --mode failed: {r.stderr}"
    # First line should be Perfil (readable mode)
    first_line = r.stdout.splitlines()[0]
    assert first_line.startswith("Perfil: CORTEX-"), (
        f"expected 'Perfil: CORTEX-<LEVEL>' as first line, got: {first_line!r}"
    )


def test_render_without_mode_defaults_to_readable(tmp_path):
    """cortex render <file> (no --mode) must also default to readable."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    r = _run_cli(["render", path])
    assert r.returncode == 0, f"render without --mode failed: {r.stderr}"
    first_line = r.stdout.splitlines()[0]
    assert first_line.startswith("Perfil: CORTEX-")


# ---------------------------------------------------------------------------
# P2-9: recovery legacy claim is "current with known limits"
# ---------------------------------------------------------------------------

def test_status_md_recovery_claim_has_limits():
    """STATUS.md must declare recovery as 'current with known limits'."""

    status_path = os.path.join(SRC_DIR, "..", "STATUS.md")
    if not os.path.exists(status_path):
        pytest.skip("STATUS.md not present")
    with open(status_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Find the recovery legacy line
    recovery_lines = [line for line in text.splitlines() if "Recuperación de artefactos legacy" in line]
    assert recovery_lines, "expected a 'Recuperación de artefactos legacy' line in STATUS.md"
    recovery_line = recovery_lines[0]
    assert "current with known limits" in recovery_line, (
        f"recovery claim should be 'current with known limits', got: {recovery_line!r}"
    )


# ---------------------------------------------------------------------------
# P2-10: SKILL_canon.md is present and matches declared version
# ---------------------------------------------------------------------------

def test_skill_canon_present_and_versioned():
    """SKILL_canon.md must be present in the project root and declare v1.2.0."""

    canon_path = os.path.join(SRC_DIR, "..", "SKILL_canon.md")
    if not os.path.exists(canon_path):
        pytest.skip("SKILL_canon.md not present")
    with open(canon_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Must declare v1.2.0-enterprise-candidate
    assert "v1.2.0-enterprise-candidate" in text, (
        "SKILL_canon.md must declare v1.2.0-enterprise-candidate"
    )


def test_status_md_declares_skill_version():
    """STATUS.md must declare the SKILL version consistently."""

    status_path = os.path.join(SRC_DIR, "..", "STATUS.md")
    if not os.path.exists(status_path):
        pytest.skip("STATUS.md not present")
    with open(status_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "v1.2.0-enterprise-candidate" in text, (
        "STATUS.md must reference v1.2.0-enterprise-candidate"
    )
    # Must mention SKILL_canon.md as the canonical reference
    assert "SKILL_canon.md" in text, (
        "STATUS.md must point to SKILL_canon.md as the canonical reference"
    )
