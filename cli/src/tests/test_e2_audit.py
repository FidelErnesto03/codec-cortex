"""E2.4 (v0.3.4) — Tests for on-demand audit logging."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from cortex.audit.logger import (
    AuditEntry,
    append_entry,
    disable_logging,
    enable_logging,
    read_session_state,
    snapshot_file,
)


@pytest.fixture
def isolated_audit_dir(tmp_path, monkeypatch):
    """Redirect the audit dir to a temp directory for each test."""
    audit = tmp_path / "audit"
    monkeypatch.setenv("CORTEX_AUDIT_DIR", str(audit))
    return audit


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def test_audit_disabled_by_default(isolated_audit_dir):
    """No state file → logging is off."""
    state = read_session_state()
    assert state.enabled is False


def test_enable_logging_creates_state_file(isolated_audit_dir):
    state = enable_logging()
    assert state.enabled is True
    assert state.started_at is not None
    assert state.pid == os.getpid()
    # State file must exist on disk.
    assert (isolated_audit_dir / "session.state").is_file()


def test_disable_logging_removes_state_file(isolated_audit_dir):
    enable_logging()
    assert (isolated_audit_dir / "session.state").is_file()
    disable_logging()
    assert not (isolated_audit_dir / "session.state").is_file()


# ---------------------------------------------------------------------------
# append_entry
# ---------------------------------------------------------------------------

def test_append_entry_nothing_written_when_disabled(isolated_audit_dir):
    """When logging is off, append_entry returns None and writes nothing."""
    entry = AuditEntry(op="add", file="brain.cortex", mode="editor", result="ok")
    result = append_entry(entry)
    assert result is None
    # No JSONL files should exist.
    assert list(isolated_audit_dir.glob("*.jsonl")) == []


def test_append_entry_writes_line_when_enabled(isolated_audit_dir):
    """When logging is on, append_entry writes a JSONL line."""
    enable_logging()
    entry = AuditEntry(
        op="add", file="brain.cortex", mode="editor", result="ok",
        selector="FCS:primary",
    )
    log_path = append_entry(entry)
    assert log_path is not None
    assert log_path.is_file()
    content = log_path.read_text(encoding="utf-8").strip()
    data = json.loads(content)
    assert data["op"] == "add"
    assert data["file"] == "brain.cortex"
    assert data["mode"] == "editor"
    assert data["result"] == "ok"
    assert data["selector"] == "FCS:primary"
    assert "t" in data  # timestamp


def test_append_entry_appends_multiple_lines(isolated_audit_dir):
    """Multiple entries are appended to the same daily log."""
    enable_logging()
    for i in range(3):
        append_entry(AuditEntry(op="add", file=f"f{i}.cortex",
                                 mode="editor", result="ok"))
    log_path = isolated_audit_dir / f"{__import__('datetime').date.today().isoformat()}.jsonl"
    lines = log_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 3


# ---------------------------------------------------------------------------
# AuditEntry
# ---------------------------------------------------------------------------

def test_audit_entry_to_jsonl_is_single_line():
    entry = AuditEntry(op="delete", file="brain.cortex", mode="admin", result="ok")
    jsonl = entry.to_jsonl()
    assert "\n" not in jsonl
    data = json.loads(jsonl)
    assert data["op"] == "delete"


def test_audit_entry_includes_error_code_when_set():
    entry = AuditEntry(
        op="update", file="brain.cortex", mode="editor", result="error",
        error_code="E008_DUPLICATE_ENTRY",
    )
    data = json.loads(entry.to_jsonl())
    assert data["error_code"] == "E008_DUPLICATE_ENTRY"


# ---------------------------------------------------------------------------
# snapshot_file
# ---------------------------------------------------------------------------

def test_snapshot_file_copies_content(isolated_audit_dir, tmp_path):
    """snapshot_file must produce a verbatim copy of the source."""
    source = tmp_path / "brain.cortex"
    source.write_text("$0: GLOSSARY\nIDN:identity{type:attrs,risk:B,cortex:Semantic,desc:\"x\"}\n")
    snap = snapshot_file(source)
    assert snap.is_file()
    assert snap.read_bytes() == source.read_bytes()


def test_snapshot_file_with_label(isolated_audit_dir, tmp_path):
    source = tmp_path / "brain.cortex"
    source.write_text("content")
    snap = snapshot_file(source, label="pre-migration")
    assert "pre-migration" in snap.name


def test_snapshot_file_missing_source_raises(isolated_audit_dir):
    with pytest.raises(FileNotFoundError):
        snapshot_file(Path("/nonexistent/brain.cortex"))


# ---------------------------------------------------------------------------
# CLI integration
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


def test_cli_audit_status_off(isolated_audit_dir):
    r = _run_cli(["audit", "status"])
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["enabled"] is False


def test_cli_audit_on_then_status(isolated_audit_dir):
    r = _run_cli(["audit", "on"])
    assert r.returncode == 0
    r = _run_cli(["audit", "status"])
    data = json.loads(r.stdout)
    assert data["enabled"] is True


def test_cli_audit_off(isolated_audit_dir):
    _run_cli(["audit", "on"])
    r = _run_cli(["audit", "off"])
    assert r.returncode == 0
    state = read_session_state()
    assert state.enabled is False


def test_cli_mutation_logged_when_audit_on(isolated_audit_dir, tmp_path):
    """A mutation command with audit ON must append a log entry."""
    cortex_path = tmp_path / "brain.cortex"
    cortex_path.write_text(
        "$0: GLOSSARY\n"
        "IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:\"x\"}\n\n"
        "$1: IDENTITY\n"
        "IDN:human{name:\"test\"}\n"
    )
    _run_cli(["audit", "on"])
    # Perform a mutation (non-interactive, so editor+force works without prompt)
    _run_cli([
        "add", str(cortex_path),
        "--section", "$1", "--sigil", "IDN", "--name", "agent",
        "--value", 'name:"agent"', "--allow-duplicate",
    ], env={"CORTEX_AUDIT_DIR": str(isolated_audit_dir)})
    # Check the log file has an entry.
    log_files = list(isolated_audit_dir.glob("*.jsonl"))
    assert len(log_files) >= 1, f"no log file in {isolated_audit_dir}"
    log_content = log_files[0].read_text(encoding="utf-8").strip()
    assert log_content, "log file is empty"
    lines = log_content.split("\n")
    last = json.loads(lines[-1])
    assert last["op"] == "add"
    assert last["result"] in ("ok", "error")


def test_cli_mutation_not_logged_when_audit_off(isolated_audit_dir, tmp_path):
    """A mutation command with audit OFF must NOT append any log entry."""
    cortex_path = tmp_path / "brain.cortex"
    cortex_path.write_text(
        "$0: GLOSSARY\n"
        "IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:\"x\"}\n\n"
        "$1: IDENTITY\n"
        "IDN:human{name:\"test\"}\n"
    )
    # Audit is off by default (no `audit on` call).
    _run_cli([
        "add", str(cortex_path),
        "--section", "$1", "--sigil", "IDN", "--name", "agent",
        "--value", 'name:"agent"', "--allow-duplicate",
    ])
    log_files = list(isolated_audit_dir.glob("*.jsonl"))
    # No log files (or empty ones) should exist.
    for f in log_files:
        assert f.read_text(encoding="utf-8").strip() == "", \
            f"unexpected log content in {f}"


def test_cli_audit_snapshot(isolated_audit_dir, tmp_path):
    cortex_path = tmp_path / "brain.cortex"
    cortex_path.write_text("$0: GLOSSARY\nIDN:identity{type:attrs}\n")
    r = _run_cli(["audit", "snapshot", str(cortex_path), "--label", "test"])
    assert r.returncode == 0
    assert "snapshot written:" in r.stdout
    # The snapshot must exist.
    snaps = list((isolated_audit_dir / "snapshots").glob("*"))
    assert len(snaps) == 1
    assert "test" in snaps[0].name
