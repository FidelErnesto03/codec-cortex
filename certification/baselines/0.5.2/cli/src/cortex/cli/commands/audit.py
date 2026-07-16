# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex audit`` — on-demand audit logging control (E2.4, v0.3.4).

Subcommands::

    cortex audit on          # enable logging for this session
    cortex audit off         # disable logging
    cortex audit status      # show whether logging is on/off
    cortex audit snapshot <file>  # export a one-shot snapshot
    cortex audit prune [--keep-days N]  # delete old logs
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ...audit.logger import (
    audit_dir,
    daily_log_path,
    disable_logging,
    enable_logging,
    prune_old_logs,
    read_session_state,
    snapshot_file,
)


def _emit_status() -> int:
    state = read_session_state()
    payload = {
        "enabled": state.enabled,
        "started_at": state.started_at,
        "pid": state.pid,
        "audit_dir": str(audit_dir()),
        "daily_log": str(daily_log_path()),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def run_on(args) -> int:
    state = enable_logging()
    print("audit logging: ON")
    print(f"  started_at: {state.started_at}")
    print(f"  pid:        {state.pid}")
    print(f"  log file:   {daily_log_path()}")
    return 0


def run_off(args) -> int:
    disable_logging()
    print("audit logging: OFF")
    print(f"  (existing entries in {audit_dir()} are preserved)")
    return 0


def run_status(args) -> int:
    return _emit_status()


def run_snapshot(args) -> int:
    target = Path(args.file).expanduser().resolve()
    if not target.is_file():
        print(f"error: file not found: {target}", file=sys.stderr)
        return 1
    label = getattr(args, "label", None)
    snap = snapshot_file(target, label=label)
    print(f"snapshot written: {snap}")
    print(f"  size: {snap.stat().st_size} bytes")
    return 0


def run_prune(args) -> int:
    keep_days = getattr(args, "keep_days", 30)
    deleted = prune_old_logs(keep_days=keep_days)
    print(f"pruned {deleted} log file(s) older than {keep_days} days")
    return 0


def run(args) -> int:
    # Dispatch by subcommand.
    sub = getattr(args, "audit_command", None)
    if sub == "on":
        return run_on(args)
    if sub == "off":
        return run_off(args)
    if sub == "status":
        return run_status(args)
    if sub == "snapshot":
        return run_snapshot(args)
    if sub == "prune":
        return run_prune(args)
    print(f"error: unknown audit subcommand: {sub}", file=sys.stderr)
    return 2
