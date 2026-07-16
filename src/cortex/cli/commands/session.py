# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex session`` — session lifecycle commands (BLP-004).

Commands:
    cortex session start                 — start a new session
    cortex session status                — show current session state
    cortex session event --kind X [--payload {"k":"v"}]  — record an event
    cortex session consolidate           — generate a patch for brain.cortex
    cortex session close                 — apply patch and close session
    cortex session abort                 — abort session (discard changes)
    cortex session detect-legacy         — scan brain.cortex for legacy SES entries
    cortex session migrate-legacy --id X --action close|abort|review
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Optional


def add_session_subparser(subparsers) -> None:
    """Register the ``session`` subcommand on an existing argparse parser."""

    sp = subparsers.add_parser(
        "session",
        help="session lifecycle: start/status/event/consolidate/close/abort/detect-legacy/migrate-legacy",
    )
    sp.add_argument(
        "--workspace", default=None,
        help="workspace root (default: cwd)",
    )
    sp.add_argument("--json", action="store_true", help="JSON output")
    sub = sp.add_subparsers(dest="session_command", required=True)

    # --- start ---
    p = sub.add_parser("start", help="start a new session")
    p.add_argument("--workspace", default=None)
    p.add_argument("--json", action="store_true", help="shortcut for --output json")
    p.add_argument("--output", choices=["text", "json"], default=None,
                   help="output format (default: text)")
    p.set_defaults(func=_cmd_start)

    # --- status ---
    p = sub.add_parser("status", help="show current session state")
    p.add_argument("--workspace", default=None)
    p.add_argument("--json", action="store_true", help="shortcut for --output json")
    p.add_argument("--output", choices=["text", "json"], default=None,
                   help="output format (default: text)")
    p.set_defaults(func=_cmd_status)

    # --- event ---
    p = sub.add_parser("event", help="record an event in the session")
    p.add_argument("--kind", required=True, help="event kind: modify|candidate|feedback|decay|note")
    p.add_argument("--payload", default=None, help='JSON payload, e.g. \'{"selector":"$1/FCS:prim"}\'')
    p.add_argument("--workspace", default=None)
    p.add_argument("--json", action="store_true", help="shortcut for --output json")
    p.add_argument("--output", choices=["text", "json"], default=None,
                   help="output format (default: text)")
    p.set_defaults(func=_cmd_event)

    # --- consolidate ---
    p = sub.add_parser("consolidate", help="consolidate session changes into a patch")
    p.add_argument("--workspace", default=None)
    p.add_argument("--json", action="store_true", help="shortcut for --output json")
    p.add_argument("--output", choices=["text", "json"], default=None,
                   help="output format (default: text)")
    p.set_defaults(func=_cmd_consolidate)

    # --- close ---
    p = sub.add_parser("close", help="close session (apply patch via TransactionService)")
    p.add_argument("--workspace", default=None)
    p.add_argument("--json", action="store_true", help="shortcut for --output json")
    p.add_argument("--output", choices=["text", "json"], default=None,
                   help="output format (default: text)")
    p.set_defaults(func=_cmd_close)

    # --- abort ---
    p = sub.add_parser("abort", help="abort session (discard all changes)")
    p.add_argument("--workspace", default=None)
    p.add_argument("--json", action="store_true", help="shortcut for --output json")
    p.add_argument("--output", choices=["text", "json"], default=None,
                   help="output format (default: text)")
    p.set_defaults(func=_cmd_abort)

    # --- detect-legacy ---
    p = sub.add_parser("detect-legacy", help="scan brain.cortex for legacy SES entries")
    p.add_argument("--workspace", default=None)
    p.add_argument("--json", action="store_true", help="shortcut for --output json")
    p.add_argument("--output", choices=["text", "json"], default=None,
                   help="output format (default: text)")
    p.set_defaults(func=_cmd_detect_legacy)

    # --- migrate-legacy ---
    p = sub.add_parser("migrate-legacy", help="migrate a legacy SES entry")
    p.add_argument("--id", dest="legacy_id", required=True,
                   help="legacy session selector, e.g. SES:current")
    p.add_argument(
        "--action", required=True,
        choices=["close", "migrate", "abort", "review"],
        help="migration action",
    )
    p.add_argument("--workspace", default=None)
    p.add_argument("--json", action="store_true", help="shortcut for --output json")
    p.add_argument("--output", choices=["text", "json"], default=None,
                   help="output format (default: text)")
    p.set_defaults(func=_cmd_migrate_legacy)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_workspace(root: Optional[str]) -> Path:
    if root:
        return Path(root)
    return Path.cwd()


def _make_service(root: Optional[str]):
    from ...runtime.session import SessionService
    from ...learning.workspace import Workspace
    start = Path(root) if root else None
    ws = Workspace.discover(start)
    return SessionService(ws)


def _make_detector():
    from ...runtime.session import LegacyDetector  # type: ignore[attr-defined]
    return LegacyDetector()  # type: ignore[attr-defined]


def _json_mode(args) -> bool:
    if getattr(args, "_json_mode", False):
        return True
    if getattr(args, "_output_mode", None) == "json":
        return True
    if bool(getattr(args, "json", False)):
        return True
    if getattr(args, "output", None) == "json":
        return True
    return False


def _emit(payload: Any, json_mode: bool) -> None:
    if json_mode:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        if isinstance(payload, dict):
            text = payload.get("text", json.dumps(payload, indent=2, default=str))
            print(text)
        else:
            print(payload)


# ---------------------------------------------------------------------------
# Command implementations
# ---------------------------------------------------------------------------


def _cmd_start(args) -> int:
    try:
        svc = _make_service(args.workspace)
        session = svc.start()
        _emit({
            "status": "started",
            "started": True,
            "session_id": session.id,
            "created_at": session.created_at,
            "workspace": session.workspace,
        }, _json_mode(args))
        return 0
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def _cmd_status(args) -> int:
    try:
        svc = _make_service(args.workspace)
        session = svc.status()
        _emit({
            "status": "ok",
            "active": session.status == "active",
            "session_id": session.id,
            "session_status": session.status,
            "created_at": session.created_at,
            "events_count": len(session.events),
            "has_patch": session.patch is not None,
        }, _json_mode(args))
        return 0
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def _cmd_event(args) -> int:
    try:
        svc = _make_service(args.workspace)
        payload_raw = getattr(args, "payload", None)
        payload = None
        if payload_raw:
            payload = json.loads(payload_raw)
        evt = svc.event(kind=args.kind, payload=payload)
        _emit({
            "status": "recorded",
            "event_id": evt.id,
            "kind": evt.kind,
            "timestamp": evt.timestamp,
        }, _json_mode(args))
        return 0
    except (RuntimeError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def _cmd_consolidate(args) -> int:
    try:
        svc = _make_service(args.workspace)
        patch = svc.consolidate()
        _emit({
            "status": "consolidated",
            "brain_hash": patch.brain_hash,
            "mutations_count": len(patch.mutations),
            "created_at": patch.created_at,
        }, _json_mode(args))
        return 0
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def _cmd_close(args) -> int:
    try:
        svc = _make_service(args.workspace)
        result = svc.close()
        if result.get("status") == "conflict":
            _emit({
                "status": "conflict",
                "error": "E_CONFLICT: brain.cortex changed during session",
                "detail": result,
            }, _json_mode(args))
            return 0  # Inform user, not a crash
        _emit({
            "status": "closed",
            "closed": True,
            "session_id": result.get("session_id"),
        }, _json_mode(args))
        return 0
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def _cmd_abort(args) -> int:
    try:
        svc = _make_service(args.workspace)
        result = svc.abort()
        _emit(result, _json_mode(args))
        return 0
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def _cmd_detect_legacy(args) -> int:
    try:
        ws = _resolve_workspace(args.workspace)
        brain_path = ws / ".cortex" / "brain.cortex"
        if not brain_path.exists():
            brain_path = ws / "brain.cortex"
        if not brain_path.exists():
            print("No brain.cortex found", file=sys.stderr)
            return 1

        detector = _make_detector()
        legacy = detector.detect(str(brain_path))
        proposals = detector.propose_migration(legacy)

        if not legacy:
            _emit({"status": "clean", "legacy_sessions": []}, _json_mode(args))
            return 0

        _emit({
            "status": "found",
            "legacy_sessions": [
                {
                    "selector": ls.selector,
                    "section_id": ls.section_id,
                    "body": ls.body,
                }
                for ls in legacy
            ],
            "proposals": proposals,
        }, _json_mode(args))
        return 0
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def _cmd_migrate_legacy(args) -> int:
    try:
        ws = _resolve_workspace(args.workspace)
        brain_path = ws / ".cortex" / "brain.cortex"
        if not brain_path.exists():
            brain_path = ws / "brain.cortex"
        if not brain_path.exists():
            print("No brain.cortex found", file=sys.stderr)
            return 1

        detector = _make_detector()
        legacy_list = detector.detect(str(brain_path))

        # Find the requested legacy session
        target = None
        for ls in legacy_list:
            if ls.selector == args.legacy_id:
                target = ls
                break

        if target is None:
            print(
                f"Legacy session {args.legacy_id} not found in brain.cortex",
                file=sys.stderr,
            )
            return 1

        action = args.action

        if action == "review":
            _emit({
                "status": "pending_review",
                "session": target.selector,
                "body": target.body,
                "message": "Manual review required. Check the legacy entry and"
                           " decide close/abort manually.",
            }, _json_mode(args))
            return 0

        if action in ("close", "abort"):
            from ...crud.mutations import build_mutation_plan  # type: ignore[attr-defined]
            from ...crud.transactions import apply_mutations  # type: ignore[attr-defined]

            plan = build_mutation_plan(
                path=str(brain_path),
                operation="delete",
                selector=args.legacy_id,
            )
            result = apply_mutations(
                path=str(brain_path),
                plan=plan,
                reason=f"BLP-004 legacy migration: {action} {args.legacy_id}",
            )

            _emit({
                "status": action,
                "session": args.legacy_id,
                "transaction_result": result.to_dict() if hasattr(result, "to_dict") else str(result),
            }, _json_mode(args))
            return 0

        # Fallback: unknown action
        print(f"Unknown migration action: {action}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


__all__ = ["add_session_subparser"]
