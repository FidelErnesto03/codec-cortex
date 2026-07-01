"""Audit logging module (E2.4, v0.3.4+).

Public surface:

- :mod:`cortex.audit.logger` — append-only JSONL audit log with
  on-demand session state, daily rotation, and snapshot export.
"""

from __future__ import annotations

from .logger import (
    AuditEntry,
    SessionState,
    append_entry,
    audit_dir,
    daily_log_path,
    disable_logging,
    enable_logging,
    prune_old_logs,
    read_session_state,
    rotate_if_needed,
    session_state_path,
    snapshot_file,
    snapshots_dir,
    write_session_state,
)

__all__ = [
    "AuditEntry",
    "SessionState",
    "append_entry",
    "audit_dir",
    "daily_log_path",
    "disable_logging",
    "enable_logging",
    "prune_old_logs",
    "read_session_state",
    "rotate_if_needed",
    "session_state_path",
    "snapshot_file",
    "snapshots_dir",
    "write_session_state",
]
