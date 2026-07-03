"""Argparse integration for the ``cortex session`` subcommand (v0.2.0, Fase A).

Provides:

- ``cortex session start [--input "..."]``
- ``cortex session status``
- ``cortex session consolidate --input "..." --output "..." --outcome "..."``
- ``cortex session close [--no-consolidate] [--no-decay] [--input "..."] [--output "..."] [--outcome "..."]``
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .errors import LearningError
from .session import (
    session_close,
    session_consolidate,
    session_start,
    session_status,
)
from .workspace import Workspace


def add_session_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``session`` subcommand on an existing argparse parser."""

    sp: argparse.ArgumentParser = subparsers.add_parser(
        "session",
        help="CODEC-CORTEX session lifecycle (start/status/consolidate/close)",
    )
    sp.add_argument(
        "--workspace", default=None,
        help="workspace root (default: discover .cortex/ from cwd)",
    )
    sub = sp.add_subparsers(dest="session_command", required=True)

    def _mk(name: str, help: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help)
        p.add_argument("--workspace", default=None)
        p.add_argument("--json", action="store_true")
        return p

    p_start = _mk("start", "start a new session")
    p_start.add_argument("--input", default="", help="optional input description")
    p_start.set_defaults(func=_cmd_start)

    p_status = _mk("status", "show active session info")
    p_status.set_defaults(func=_cmd_status)

    p_cons = _mk("consolidate", "consolidate the running session into SES:last")
    p_cons.add_argument("--input", default="", help="session input summary")
    p_cons.add_argument("--output", default="", help="session output summary")
    p_cons.add_argument("--outcome", default="", help="session outcome summary")
    p_cons.set_defaults(func=_cmd_consolidate)

    p_close = _mk("close", "close the running session (consolidate + decay)")
    p_close.add_argument("--no-consolidate", action="store_true",
                          help="skip consolidation step")
    p_close.add_argument("--no-decay", action="store_true",
                          help="skip decay step")
    p_close.add_argument("--input", default="", help="session input summary")
    p_close.add_argument("--output", default="", help="session output summary")
    p_close.add_argument("--outcome", default="", help="session outcome summary")
    p_close.set_defaults(func=_cmd_close)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_workspace(args) -> Workspace:
    root = getattr(args, "workspace", None)
    if root:
        return Workspace.discover(__import__("pathlib").Path(root))
    return Workspace.discover()


def _json_active(args) -> bool:
    if getattr(args, "_json_mode", False):
        return True
    return bool(getattr(args, "json", False))


def _emit(payload: Any, json_mode: bool) -> None:
    if json_mode:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        if isinstance(payload, dict) and "text" in payload:
            print(payload["text"])
        else:
            print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


# ---------------------------------------------------------------------------
# Command implementations
# ---------------------------------------------------------------------------


def _cmd_start(args) -> int:
    try:
        ws = _resolve_workspace(args)
        state = session_start(ws, input_text=args.input)
    except LearningError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    payload = {
        "started": True,
        "session_id": state.session_id,
        "start": state.start,
        "brain_hash_at_start": state.brain_hash_at_start,
    }
    _emit(payload, _json_active(args))
    return 0


def _cmd_status(args) -> int:
    try:
        ws = _resolve_workspace(args)
        status = session_status(ws)
    except LearningError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    _emit(status, _json_active(args))
    return 0


def _cmd_consolidate(args) -> int:
    try:
        ws = _resolve_workspace(args)
        result = session_consolidate(
            ws,
            input_text=args.input,
            output_text=args.output,
            outcome_text=args.outcome,
        )
    except LearningError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    _emit(result, _json_active(args))
    return 0


def _cmd_close(args) -> int:
    try:
        ws = _resolve_workspace(args)
        result = session_close(
            ws,
            consolidate=not args.no_consolidate,
            input_text=args.input,
            output_text=args.output,
            outcome_text=args.outcome,
            run_decay=not args.no_decay,
        )
    except LearningError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    _emit(result, _json_active(args))
    return 0


__all__ = ["add_session_subparser"]
