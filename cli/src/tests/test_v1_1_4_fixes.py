# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""v1.1.4 fixes — tests for the 4 issues raised in the fifth review.

P0:
  1. E024_LEVEL2_MISSING_FOCUS is non-bypassable → --force cannot delete FCS
  2. --force cannot delete operational P0 (FCS/OBJ/CNST:blocking/STP)
  3. --unsafe-allow-secret-forensics marks artefact as non_conformant

P1:
  4. pytest is declared as dev dependency
  5. Demo v1.1.4 exists and is reproducible
  6. recover adds general RSK when $0 is reconstructed (even for canonical sigils)
"""

import json
import os
import subprocess
import sys

import pytest

from cortex.templates import build_brain
from cortex.crud.transactions import atomic_write_cortex
from cortex.hcortex import recover_cortex


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
# P0-1: --force cannot persist brain without FCS (E024 is non-bypassable)
# ---------------------------------------------------------------------------

def test_force_delete_fcs_blocked(tmp_path):
    """cortex delete FCS:primary --force must NOT persist the invalid brain.

    v1.1.4 P0-1: E024_LEVEL2_MISSING_FOCUS is now bypassable=False, so
    --force cannot override it.  The file on disk must NOT be modified.
    """

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    # Record original content
    with open(path) as f:
        original = f.read()

    # Try to delete FCS:primary with --force
    r = _run_cli(["delete", path, "FCS:primary", "--force"])
    assert r.returncode != 0, (
        f"--force should NOT allow deleting FCS:primary; rc={r.returncode}\n{r.stdout}"
    )

    # File on disk must NOT have been modified
    with open(path) as f:
        after = f.read()
    assert after == original, "file was modified despite non-bypassable governance error"


def test_force_delete_obj_blocked(tmp_path):
    """cortex delete OBJ:main --force must NOT persist the invalid brain."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    r = _run_cli(["delete", path, "OBJ:main", "--force"])
    assert r.returncode != 0, (
        f"--force should NOT allow deleting OBJ:main; rc={r.returncode}\n{r.stdout}"
    )


def test_force_update_fcs_to_done_blocked(tmp_path):
    """cortex update FCS:primary --set status=done --force must NOT persist.

    v1.1.4: setting FCS to 'done' removes the active focus, which is
    E024_LEVEL2_MISSING_FOCUS (non-bypassable).
    """

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    r = _run_cli(["update", path, "FCS:primary", "--set", "status=done", "--force"])
    assert r.returncode != 0, (
        f"--force should NOT allow FCS→done; rc={r.returncode}\n{r.stdout}"
    )


def test_non_governance_force_still_works(tmp_path):
    """--force can still bypass non-governance errors (e.g. benign update).

    v1.1.4: --force still works for bypassable errors; only governance
    invariants (E023/E024/E026/E029/E031/E032) are non-bypassable.
    """

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    # A benign update with --no-validate-write + --force should work
    r = _run_cli([
        "update", path, "FCS:primary", "--set", "what=updated focus",
        "--no-validate-write", "--force",
    ])
    assert r.returncode == 0, f"benign update should pass; rc={r.returncode}\n{r.stderr}"


# ---------------------------------------------------------------------------
# P0-3: --unsafe-allow-secret-forensics marks artefact as non_conformant
# ---------------------------------------------------------------------------

def test_unsafe_forensics_marks_non_conformant(tmp_path):
    """--unsafe-allow-secret-forensics must add STAT:forensic_quarantine."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    r = _run_cli([
        "add", path, "--section", "$3", "--sigil", "REF", "--name", "secret",
        "--value", 'provider:"x", password:"abc123456"',
        "--create-section", "--force", "--unsafe-allow-secret-forensics",
    ])
    assert r.returncode == 0, (
        f"--unsafe-allow-secret-forensics should allow write with marker; "
        f"rc={r.returncode}\n{r.stdout}"
    )
    payload = json.loads(r.stdout)
    assert payload["ok"] is True
    assert "warning" in payload, "expected warning about non_conformant_forensic_artifact"
    assert "non_conformant_forensic_artifact" in payload["warning"]

    # The file must contain the STAT:forensic_quarantine marker
    with open(path) as f:
        text = f.read()
    assert "forensic_quarantine" in text, "STAT:forensic_quarantine marker not in file"
    assert "non_conformant_forensic_artifact" in text


def test_unsafe_forensics_verify_still_fails(tmp_path):
    """Even with forensic marker, verify --strict must still fail (secret present)."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)

    _run_cli([
        "add", path, "--section", "$3", "--sigil", "REF", "--name", "secret",
        "--value", 'provider:"x", password:"abc123456"',
        "--create-section", "--force", "--unsafe-allow-secret-forensics",
    ])

    r = _run_cli(["verify", path, "--strict"])
    assert r.returncode != 0, "verify --strict must still fail on forensic artefact"


# ---------------------------------------------------------------------------
# P1-4: pytest is declared as dev dependency
# ---------------------------------------------------------------------------

def test_pytest_dev_dependency_declared():
    """pyproject.toml must declare pytest as a dev dependency."""

    pyproject_path = os.path.join(SRC_DIR, "..", "pyproject.toml")
    if not os.path.exists(pyproject_path):
        pytest.skip("pyproject.toml not present")
    with open(pyproject_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "[project.optional-dependencies]" in text, (
        "pyproject.toml must have [project.optional-dependencies] section"
    )
    assert "dev" in text and "pytest" in text, (
        "pyproject.toml must declare pytest in dev optional dependencies"
    )


# ---------------------------------------------------------------------------
# P1-6: recover adds general RSK when $0 is reconstructed (even canonical)
# ---------------------------------------------------------------------------

def test_recover_adds_general_rsk_for_canonical_sigils():
    """recover --embed-aud-rsk must add a general RSK even when all
    reconstructed sigils are canonical (v1.1.4 P1-6)."""

    # A file with only canonical sigils (IDN, FCS, OBJ) but no $0
    legacy = (
        'IDN:agent{name:"legacy"}\n'
        'FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}\n'
        'OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}\n'
    )
    result = recover_cortex(legacy, path="legacy.cortex", embed_aud_rsk=True)
    # Must have a general RSK:reconstructed_glossary entry
    rsk_entries = [e for _, e in result.doc.iter_entries() if e.sigil == "RSK"]
    rsk_names = [e.name for e in rsk_entries]
    assert "reconstructed_glossary" in rsk_names, (
        f"expected RSK:reconstructed_glossary for general reconstruction risk; "
        f"got RSK names: {rsk_names}"
    )


def test_recover_general_rsk_has_correct_fields():
    """The general RSK:reconstructed_glossary must have proper fields."""

    legacy = (
        'IDN:agent{name:"legacy"}\n'
        'FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}\n'
        'OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}\n'
    )
    result = recover_cortex(legacy, path="legacy.cortex", embed_aud_rsk=True)
    rsk = None
    for _, e in result.doc.iter_entries():
        if e.sigil == "RSK" and e.name == "reconstructed_glossary":
            rsk = e
            break
    assert rsk is not None, "RSK:reconstructed_glossary not found"
    assert isinstance(rsk.value, dict)
    assert "risk" in rsk.value
    assert "impact" in rsk.value
    assert "mitigation" in rsk.value
    assert rsk.value.get("status") == "current"


# ---------------------------------------------------------------------------
# P1-5: Demo v1.1.4 exists
# ---------------------------------------------------------------------------
# v2.3.1 cleanup: demo scripts from v1.1.x were removed as obsolete artifacts.
# These tests are skipped — the demo functionality is covered by the v2.x CLI tests.
# ---------------------------------------------------------------------------

def test_demo_v1_1_4_removed():
    """v2.3.1 cleanup: old v1.1.x demo scripts were removed as obsolete."""
    demo_path = os.path.join(SRC_DIR, "..", "scripts", "cortex_demo_v1_1_4.sh")
    assert not os.path.exists(demo_path), (
        f"v1.1.x demo should have been removed in v2.3.1 cleanup: {demo_path}"
    )
