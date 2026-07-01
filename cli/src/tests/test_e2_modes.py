"""E2.3 (v0.3.4) — Tests for mutation gates (read-only/editor/admin)."""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.core.modes import (
    Mode,
    ModeReadOnlyError,
    ModeUnknownError,
    check_permission,
    is_read_command,
    is_write_command,
    resolve_mode,
)


# ---------------------------------------------------------------------------
# Mode enum
# ---------------------------------------------------------------------------

def test_mode_from_string_defaults_to_editor():
    assert Mode.from_string(None) == Mode.EDITOR
    assert Mode.from_string("") == Mode.EDITOR


def test_mode_from_string_accepts_aliases():
    assert Mode.from_string("read-only") == Mode.READ_ONLY
    assert Mode.from_string("readonly") == Mode.READ_ONLY
    assert Mode.from_string("ro") == Mode.READ_ONLY
    assert Mode.from_string("editor") == Mode.EDITOR
    assert Mode.from_string("edit") == Mode.EDITOR
    assert Mode.from_string("admin") == Mode.ADMIN
    assert Mode.from_string("privileged") == Mode.ADMIN


def test_mode_from_string_unknown_raises():
    with pytest.raises(ModeUnknownError):
        Mode.from_string("superuser")


def test_mode_properties():
    assert Mode.READ_ONLY.allows_writes is False
    assert Mode.READ_ONLY.allows_force is False
    assert Mode.EDITOR.allows_writes is True
    assert Mode.EDITOR.allows_force is False
    assert Mode.ADMIN.allows_writes is True
    assert Mode.ADMIN.allows_force is True


# ---------------------------------------------------------------------------
# Command classification
# ---------------------------------------------------------------------------

def test_is_read_command():
    assert is_read_command("get")
    assert is_read_command("list")
    assert is_read_command("verify")
    assert is_read_command("verify-view")
    assert is_read_command("inspect")
    assert is_read_command("diff")
    assert not is_read_command("delete")
    assert not is_read_command("add")


def test_is_write_command():
    assert is_write_command("add")
    assert is_write_command("update")
    assert is_write_command("delete")
    assert is_write_command("move")
    assert is_write_command("format")
    assert not is_write_command("list")
    assert not is_write_command("verify")


# ---------------------------------------------------------------------------
# resolve_mode (env var priority)
# ---------------------------------------------------------------------------

def test_resolve_mode_uses_cli_flag_first():
    """--mode flag takes priority over $CORTEX_MODE."""
    old = os.environ.pop("CORTEX_MODE", None)
    try:
        assert resolve_mode("admin") == Mode.ADMIN
        os.environ["CORTEX_MODE"] = "read-only"
        assert resolve_mode("admin") == Mode.ADMIN  # CLI flag wins
    finally:
        if old is None:
            os.environ.pop("CORTEX_MODE", None)
        else:
            os.environ["CORTEX_MODE"] = old


def test_resolve_mode_uses_env_when_no_flag():
    old = os.environ.pop("CORTEX_MODE", None)
    try:
        os.environ["CORTEX_MODE"] = "read-only"
        assert resolve_mode(None) == Mode.READ_ONLY
    finally:
        if old is None:
            os.environ.pop("CORTEX_MODE", None)
        else:
            os.environ["CORTEX_MODE"] = old


def test_resolve_mode_defaults_to_editor():
    old = os.environ.pop("CORTEX_MODE", None)
    try:
        assert resolve_mode(None) == Mode.EDITOR
    finally:
        if old is None:
            os.environ.pop("CORTEX_MODE", None)
        else:
            os.environ["CORTEX_MODE"] = old


# ---------------------------------------------------------------------------
# check_permission
# ---------------------------------------------------------------------------

def test_read_only_blocks_writes():
    err = check_permission(Mode.READ_ONLY, "delete", uses_force=False)
    assert isinstance(err, ModeReadOnlyError)


def test_read_only_blocks_add():
    err = check_permission(Mode.READ_ONLY, "add", uses_force=False)
    assert isinstance(err, ModeReadOnlyError)


def test_read_only_allows_reads():
    assert check_permission(Mode.READ_ONLY, "list") is None
    assert check_permission(Mode.READ_ONLY, "verify") is None
    assert check_permission(Mode.READ_ONLY, "get") is None


def test_editor_allows_writes_without_force():
    assert check_permission(Mode.EDITOR, "delete", uses_force=False) is None
    assert check_permission(Mode.EDITOR, "add", uses_force=False) is None


def test_editor_force_non_interactive_proceeds():
    """In non-interactive mode (CI), editor + --force proceeds without prompt."""
    assert check_permission(
        Mode.EDITOR, "delete", uses_force=True, non_interactive=True
    ) is None


def test_editor_force_confirmed_proceeds():
    assert check_permission(
        Mode.EDITOR, "delete", uses_force=True, confirmed=True
    ) is None


def test_admin_allows_everything():
    assert check_permission(Mode.ADMIN, "delete", uses_force=True) is None
    assert check_permission(Mode.ADMIN, "add", uses_force=False) is None
    assert check_permission(Mode.ADMIN, "list") is None


# ---------------------------------------------------------------------------
# CLI integration: --mode read-only blocks mutations
# ---------------------------------------------------------------------------

def _run_cli(args_list, env=None):
    import subprocess
    e = {**os.environ, "PYTHONPATH": SRC_DIR}
    if env:
        e.update(env)
    return subprocess.run(
        [sys.executable, "-c",
         f"import sys; sys.path.insert(0, {SRC_DIR!r}); from cortex.cli.main import main; rc = main(); sys.exit(rc or 0)"]
        + args_list,
        capture_output=True, text=True, env=e,
    )


def test_cli_read_only_blocks_delete(tmp_path):
    """`cortex --mode read-only delete ...` must exit 13 with E035_MODE_READ_ONLY."""
    # Create a minimal .cortex file
    cortex_path = tmp_path / "brain.cortex"
    cortex_path.write_text(
        "$0: GLOSSARY\n"
        "IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:\"x\"}\n\n"
        "$1: IDENTITY\n"
        "IDN:human{name:\"test\"}\n"
    )
    r = _run_cli(["--mode", "read-only", "delete", str(cortex_path), "IDN:human"])
    assert r.returncode == 13, f"expected rc=13, got {r.returncode}\n{r.stderr}"
    assert "E035_MODE_READ_ONLY" in r.stderr


def test_cli_read_only_blocks_add(tmp_path):
    cortex_path = tmp_path / "brain.cortex"
    cortex_path.write_text(
        "$0: GLOSSARY\n"
        "IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:\"x\"}\n\n"
        "$1: IDENTITY\n"
        "IDN:human{name:\"test\"}\n"
    )
    r = _run_cli([
        "--mode", "read-only", "add", str(cortex_path),
        "--section", "$1", "--sigil", "IDN", "--name", "x",
        "--value", 'name:"x"',
    ])
    assert r.returncode == 13
    assert "E035_MODE_READ_ONLY" in r.stderr


def test_cli_read_only_allows_list(tmp_path):
    cortex_path = tmp_path / "brain.cortex"
    cortex_path.write_text(
        "$0: GLOSSARY\n"
        "IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:\"x\"}\n\n"
        "$1: IDENTITY\n"
        "IDN:human{name:\"test\"}\n"
    )
    r = _run_cli(["--mode", "read-only", "list", str(cortex_path)])
    assert r.returncode == 0


def test_cli_env_var_sets_mode(tmp_path):
    """CORTEX_MODE=read-only must behave like --mode read-only."""
    cortex_path = tmp_path / "brain.cortex"
    cortex_path.write_text(
        "$0: GLOSSARY\n"
        "IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:\"x\"}\n\n"
        "$1: IDENTITY\n"
        "IDN:human{name:\"test\"}\n"
    )
    r = _run_cli(["delete", str(cortex_path), "IDN:human"],
                  env={"CORTEX_MODE": "read-only"})
    assert r.returncode == 13
    assert "E035_MODE_READ_ONLY" in r.stderr


def test_cli_admin_allows_force(tmp_path):
    """`cortex --mode admin delete ... --force` must NOT exit 13."""
    cortex_path = tmp_path / "brain.cortex"
    cortex_path.write_text(
        "$0: GLOSSARY\n"
        "IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:\"x\"}\n\n"
        "$1: IDENTITY\n"
        "IDN:human{name:\"test\"}\n"
    )
    r = _run_cli([
        "--mode", "admin", "delete", str(cortex_path), "IDN:human", "--force",
    ])
    # rc != 13 means the gate passed (may be 0 or 1 depending on validation).
    assert r.returncode != 13, f"gate blocked: {r.stderr}"
