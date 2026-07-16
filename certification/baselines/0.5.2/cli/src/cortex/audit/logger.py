# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""E2.4 (v0.3.4) — On-demand audit logging.

This module implements the audit log described in the E2.4 plan:

  - Logging is OFF by default. No automatic logging of any operation.
  - ``cortex audit on``  → enable logging for the current session.
  - ``cortex audit off`` → disable logging for the current session.
  - ``cortex audit status`` → show whether logging is on or off.
  - ``cortex audit snapshot`` → export a single snapshot of a .cortex
    file to ``~/.codec-cortex/audit/snapshots/`` (one-shot, not a stream).

The session state (on/off) is stored in
``~/.codec-cortex/audit/session.state`` so it persists across CLI
invocations within the same shell/session. The state file is removed
by ``cortex audit off``.

When logging is ON, mutation commands (add/update/delete/move/format)
append a JSONL line to ``~/.codec-cortex/audit/YYYY-MM-DD.jsonl``::

    {"t":"2026-07-01T12:00:00Z","op":"add","file":"brain.cortex",
     "mode":"editor","result":"ok"}

Design principles:
  - **No silent logging.** Nothing is written unless the user opts in.
  - **Append-only.** Existing entries are never modified.
  - **Out-of-repo.** Logs live in the user's home, not in the project
    repo, so they don't pollute git history.
  - **Per-day rotation.** A new JSONL file is created each day.
"""

from __future__ import annotations

import datetime
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def audit_dir() -> Path:
    """Return the audit directory under the user's home.

    Defaults to ``~/.codec-cortex/audit/``. Can be overridden by the
    ``CORTEX_AUDIT_DIR`` environment variable (useful for tests).
    """
    override = os.environ.get("CORTEX_AUDIT_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".codec-cortex" / "audit"


def session_state_path() -> Path:
    """Path to the session state file (created by `audit on`)."""
    return audit_dir() / "session.state"


def daily_log_path(date: Optional[datetime.date] = None) -> Path:
    """Path to the daily JSONL log file (``YYYY-MM-DD.jsonl``)."""
    if date is None:
        date = datetime.date.today()
    return audit_dir() / f"{date.isoformat()}.jsonl"


def snapshots_dir() -> Path:
    """Directory where `audit snapshot` exports one-shot snapshots."""
    return audit_dir() / "snapshots"


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

@dataclass
class SessionState:
    """In-memory representation of the audit session state."""

    enabled: bool
    started_at: Optional[str] = None  # ISO 8601 timestamp
    pid: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "started_at": self.started_at,
            "pid": self.pid,
        }


def read_session_state() -> SessionState:
    """Read the current session state from disk.

    Returns a disabled SessionState if no state file exists.
    """
    path = session_state_path()
    if not path.is_file():
        return SessionState(enabled=False)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return SessionState(
            enabled=bool(data.get("enabled", False)),
            started_at=data.get("started_at"),
            pid=data.get("pid"),
        )
    except (json.JSONDecodeError, OSError):
        return SessionState(enabled=False)


def write_session_state(state: SessionState) -> None:
    """Persist the session state to disk. Creates the audit dir if needed."""
    path = session_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(state.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def enable_logging() -> SessionState:
    """Enable audit logging for the current session."""
    state = SessionState(
        enabled=True,
        started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        pid=os.getpid(),
    )
    write_session_state(state)
    # Also create the daily log file if it doesn't exist (touch).
    log_path = daily_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.touch()
    return state


def disable_logging() -> SessionState:
    """Disable audit logging. The state file is removed; existing log
    entries are preserved."""
    path = session_state_path()
    if path.is_file():
        path.unlink()
    return SessionState(enabled=False)


# ---------------------------------------------------------------------------
# Log entry
# ---------------------------------------------------------------------------

@dataclass
class AuditEntry:
    """A single audit log entry."""

    op: str          # "add" | "update" | "delete" | "move" | "format" | ...
    file: str        # path to the .cortex file
    mode: str        # "read-only" | "editor" | "admin"
    result: str      # "ok" | "error" | "dry-run"
    selector: Optional[str] = None  # entry selector (e.g. "FCS:primary")
    error_code: Optional[str] = None
    timestamp: Optional[str] = None  # ISO 8601; defaults to now()

    def to_dict(self) -> dict:
        ts = self.timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat()
        d: dict[str, Any] = {
            "t": ts,
            "op": self.op,
            "file": self.file,
            "mode": self.mode,
            "result": self.result,
        }
        if self.selector:
            d["selector"] = self.selector
        if self.error_code:
            d["error_code"] = self.error_code
        return d

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, separators=(",", ":"))


def append_entry(entry: AuditEntry) -> Optional[Path]:
    """Append ``entry`` to today's JSONL log if logging is enabled.

    Returns the path to the log file if written, or None if logging is
    disabled.
    """
    state = read_session_state()
    if not state.enabled:
        return None

    log_path = daily_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # Append-only: open in append mode, write one line, close.
    with log_path.open("a", encoding="utf-8") as f:
        f.write(entry.to_jsonl() + "\n")
    return log_path


# ---------------------------------------------------------------------------
# Snapshot
# ---------------------------------------------------------------------------

def snapshot_file(cortex_path: Path, *, label: Optional[str] = None) -> Path:
    """Export a one-shot snapshot of ``cortex_path`` to the snapshots dir.

    The snapshot is a verbatim copy of the .cortex file, named with a
    timestamp so multiple snapshots don't collide. An optional ``label``
    can be appended to the filename for human readability.

    Returns the path to the written snapshot.
    """
    if not cortex_path.is_file():
        raise FileNotFoundError(f"cannot snapshot non-existent file: {cortex_path}")

    snapshots_dir().mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    stem = cortex_path.stem
    suffix = cortex_path.suffix
    label_part = f"_{label}" if label else ""
    snap_name = f"{stem}_{ts}{label_part}{suffix}"
    snap_path = snapshots_dir() / snap_name
    snap_path.write_bytes(cortex_path.read_bytes())
    return snap_path


# ---------------------------------------------------------------------------
# Rotation (E2 risk mitigation)
# ---------------------------------------------------------------------------

MAX_LOG_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def rotate_if_needed(log_path: Path) -> Optional[Path]:
    """Rotate ``log_path`` if it exceeds :data:`MAX_LOG_SIZE_BYTES`.

    Renames ``YYYY-MM-DD.jsonl`` to ``YYYY-MM-DD.jsonl.1`` (overwriting
    any previous rotation). Returns the rotated path if rotation
    happened, None otherwise.
    """
    if not log_path.is_file():
        return None
    if log_path.stat().st_size < MAX_LOG_SIZE_BYTES:
        return None
    rotated = log_path.with_suffix(log_path.suffix + ".1")
    log_path.rename(rotated)
    log_path.touch()
    return rotated


def prune_old_logs(*, keep_days: int = 30) -> int:
    """Delete daily log files older than ``keep_days`` days.

    Returns the number of files deleted.
    """
    cutoff = datetime.date.today() - datetime.timedelta(days=keep_days)
    deleted = 0
    for p in audit_dir().glob("*.jsonl"):
        # Skip rotated files (.jsonl.1) — they're handled separately.
        if p.name.endswith(".1"):
            continue
        try:
            date_str = p.stem  # "YYYY-MM-DD"
            file_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            continue
        if file_date < cutoff:
            p.unlink()
            deleted += 1
    return deleted
