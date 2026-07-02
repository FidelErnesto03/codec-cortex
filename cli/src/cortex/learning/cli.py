# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Argparse subcommand integration for the learning engine.

Adds a ``learn`` subcommand to the existing ``cortex`` CLI with the
following sub-actions (SPEC §8):

- ``cortex learn init [--workspace .] [--force]``
- ``cortex learn doctor``
- ``cortex learn policy show|validate|apply [--file ...] [--dry-run|--confirm]``
- ``cortex learn policy add --name ... --source ... --target ... --when ... --action ... --requires ...``
- ``cortex learn index rebuild|status|clean``
- ``cortex learn scan [--json]``
- ``cortex learn candidates [--limit N] [--json]``
- ``cortex learn explain --candidate <id>``
- ``cortex learn elevate --candidate <id> --dry-run|--apply --confirm``
- ``cortex learn elevate --policy <id> --dry-run|--apply``
- ``cortex learn profile --budget N --json``
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .candidates import detect_candidates, explain_candidate
from .elevation import apply_patch, plan_patch
from .errors import LearningError
from .index import (
    is_stale,
    load_index,
    rebuild_for_workspace,
)
from .policy import parse_policy_document
from .workspace import Workspace, doctor, init_workspace


# ---------------------------------------------------------------------------
# Parser construction
# ---------------------------------------------------------------------------


def add_learn_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``learn`` subcommand on an existing argparse parser."""

    sp: argparse.ArgumentParser = subparsers.add_parser(
        "learn",
        help="CODEC-CORTEX Learning Engine — deterministic, local learning",
    )
    sp.add_argument(
        "--workspace", default=None,
        help="workspace root (default: discover .cortex/ from cwd)",
    )
    sub = sp.add_subparsers(dest="learn_command", required=True)

    def _mk(name: str, help: str) -> argparse.ArgumentParser:
        """Create a sub-action parser pre-loaded with --workspace and --json."""
        p = sub.add_parser(name, help=help)
        p.add_argument("--workspace", default=None,
                        help="workspace root (overrides learn --workspace)")
        p.add_argument("--json", action="store_true")
        return p

    # init
    p_init = _mk("init", "initialize a .cortex/ workspace")
    p_init.add_argument("--force", action="store_true",
                        help="overwrite existing artefacts")
    p_init.set_defaults(func=_cmd_init)

    # doctor
    p_doc = _mk("doctor", "validate workspace integrity")
    p_doc.set_defaults(func=_cmd_doctor)

    # policy
    p_pol = sub.add_parser("policy", help="inspect / validate / apply policies")
    pol_sub = p_pol.add_subparsers(dest="policy_command", required=True)
    p_pol_show = pol_sub.add_parser("show", help="print the active policy file")
    p_pol_show.add_argument("--workspace", default=None)
    p_pol_show.add_argument("--json", action="store_true")
    p_pol_show.set_defaults(func=_cmd_policy_show)
    p_pol_val = pol_sub.add_parser("validate", help="validate the active policy file")
    p_pol_val.add_argument("--workspace", default=None)
    p_pol_val.add_argument("--json", action="store_true")
    p_pol_val.set_defaults(func=_cmd_policy_validate)
    p_pol_apply = pol_sub.add_parser("apply", help="apply a proposed policy file")
    p_pol_apply.add_argument("--workspace", default=None)
    p_pol_apply.add_argument("--file", required=True, help="policy file to apply")
    p_pol_apply.add_argument("--dry-run", action="store_true")
    p_pol_apply.add_argument("--confirm", action="store_true")
    p_pol_apply.add_argument("--json", action="store_true")
    p_pol_apply.set_defaults(func=_cmd_policy_apply)
    p_pol_add = pol_sub.add_parser("add", help="add a single policy rule")
    p_pol_add.add_argument("--workspace", default=None)
    p_pol_add.add_argument("--name", required=True)
    p_pol_add.add_argument("--source", required=True)
    p_pol_add.add_argument("--target", required=True)
    p_pol_add.add_argument("--when", required=True)
    p_pol_add.add_argument("--action", required=True,
                            choices=["score", "propose", "apply", "block"])
    p_pol_add.add_argument("--requires", default="")
    p_pol_add.add_argument("--dry-run", action="store_true")
    p_pol_add.add_argument("--confirm", action="store_true")
    p_pol_add.add_argument("--json", action="store_true")
    p_pol_add.set_defaults(func=_cmd_policy_add)

    # index
    p_idx = sub.add_parser("index", help="learn-index operations")
    idx_sub = p_idx.add_subparsers(dest="index_command", required=True)
    p_idx_rb = idx_sub.add_parser("rebuild", help="rebuild the learn-index")
    p_idx_rb.add_argument("--workspace", default=None)
    p_idx_rb.add_argument("--json", action="store_true")
    p_idx_rb.set_defaults(func=_cmd_index_rebuild)
    p_idx_st = idx_sub.add_parser("status", help="show index freshness")
    p_idx_st.add_argument("--workspace", default=None)
    p_idx_st.add_argument("--json", action="store_true")
    p_idx_st.set_defaults(func=_cmd_index_status)
    p_idx_cl = idx_sub.add_parser("clean", help="delete the learn-index")
    p_idx_cl.add_argument("--workspace", default=None)
    p_idx_cl.add_argument("--json", action="store_true")
    p_idx_cl.set_defaults(func=_cmd_index_clean)

    # scan
    p_scan = _mk("scan", "scan brain and produce index entries")
    p_scan.set_defaults(func=_cmd_scan)

    # candidates
    p_cand = _mk("candidates", "list elevation candidates")
    p_cand.add_argument("--limit", type=int, default=10)
    p_cand.set_defaults(func=_cmd_candidates)

    # explain
    p_exp = _mk("explain", "explain a candidate in detail")
    p_exp.add_argument("--candidate", required=True)
    p_exp.set_defaults(func=_cmd_explain)

    # elevate
    p_el = _mk("elevate", "elevate a candidate or policy")
    p_el.add_argument("--candidate", default=None)
    p_el.add_argument("--policy", default=None)
    p_el.add_argument("--dry-run", action="store_true")
    p_el.add_argument("--apply", action="store_true")
    p_el.add_argument("--confirm", action="store_true")
    p_el.set_defaults(func=_cmd_elevate)

    # profile
    p_prof = _mk("profile", "produce a load profile by read_priority")
    p_prof.add_argument("--budget", type=int, default=1000,
                         help="approximate token budget")
    p_prof.set_defaults(func=_cmd_profile)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_workspace(args) -> Workspace:
    # The ``learn`` parent parser has --workspace; some subcommands
    # (init) also accept their own --workspace which shadows it.
    root = getattr(args, "workspace", None)
    if root:
        return Workspace.discover(Path(root))
    return Workspace.discover()


def _json_active(args) -> bool:
    """Return True if either the subcommand-level ``--json`` or the
    global ``--json`` flag is active."""

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


def _cmd_init(args) -> int:
    root = getattr(args, "workspace", None) or "."
    force = bool(getattr(args, "force", False))
    ws = init_workspace(Path(root), force=force)
    print(f"initialized workspace at {ws.cortex_dir}")
    print(f"  manifest : {ws.manifest_path}")
    print(f"  brain    : {ws.brain_path}")
    print(f"  policy   : {ws.policy_path}")
    print(f"  index dir: {ws.index_path.parent}")
    print(f"  cache dir: {ws.cache_dir}")
    return 0


def _cmd_doctor(args) -> int:
    try:
        ws = _resolve_workspace(args)
    except LearningError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    report = doctor(ws)
    _emit(report.to_dict(), _json_active(args))
    return 0 if report.ok else 1


def _cmd_policy_show(args) -> int:
    ws = _resolve_workspace(args)
    text = ws.read_policy()
    if not text.strip():
        from .policy_defaults import default_policy_text
        text = default_policy_text()
    _emit({"text": text, "path": str(ws.policy_path)}, _json_active(args))
    return 0


def _cmd_policy_validate(args) -> int:
    ws = _resolve_workspace(args)
    try:
        doc = ws.parse_policy()
        ps = parse_policy_document(doc)
        payload = {
            "ok": True,
            "identity": ps.identity,
            "policy_count": len(ps.policies),
            "policy_ids": [p.id for p in ps.policies],
            "protected": ps.protected.items,
            "thresholds": ps.thresholds.as_signal_weights(),
        }
    except LearningError as e:
        payload = {"ok": False, "error": {"code": e.code, "message": str(e)}}
        _emit(payload, _json_active(args))
        return 1
    _emit(payload, _json_active(args))
    return 0


def _cmd_policy_apply(args) -> int:
    ws = _resolve_workspace(args)
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"error: file not found: {file_path}", file=sys.stderr)
        return 1
    text = file_path.read_text(encoding="utf-8")
    from ..core.parser import parse_cortex
    try:
        doc = parse_cortex(text, path=str(file_path))
        ps = parse_policy_document(doc)
    except LearningError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if args.dry_run:
        print(f"# dry-run: would write {len(ps.policies)} policies to {ws.policy_path}")
        for p in ps.policies:
            print(f"  - {p.id}: {p.source}→{p.target} when={p.when!r} action={p.action}")
        return 0
    if not args.confirm:
        print("error: --confirm required to apply", file=sys.stderr)
        return 1
    target = ws.policy_path or ws.cortex_dir / "learn-policies.cortex"
    target.write_text(text, encoding="utf-8")
    print(f"applied policy file to {target}")
    return 0


def _cmd_policy_add(args) -> int:
    ws = _resolve_workspace(args)
    new_entry_line = (
        f'POL:{args.name}{{source:"{args.source}", target:"{args.target}", '
        f'when:"{args.when}", action:"{args.action}", requires:"{args.requires}"}}'
    )
    if args.dry_run:
        print(f"# dry-run: would append to {ws.policy_path}")
        print(new_entry_line)
        return 0
    if not args.confirm:
        print("error: --confirm required to apply", file=sys.stderr)
        return 1
    target = ws.policy_path or ws.cortex_dir / "learn-policies.cortex"
    text = target.read_text(encoding="utf-8") if target.exists() else ""
    if not text.endswith("\n"):
        text = text + "\n"
    text = text + new_entry_line + "\n"
    target.write_text(text, encoding="utf-8")
    print(f"added policy {args.name} to {target}")
    return 0


def _cmd_index_rebuild(args) -> int:
    ws = _resolve_workspace(args)
    idx = rebuild_for_workspace(ws)
    print(f"rebuilt index at {ws.index_path}")
    print(f"  engine_version: {idx.engine_version}")
    print(f"  algorithm     : {idx.algorithm}")
    print(f"  brain_hash    : {idx.brain_hash}")
    print(f"  policy_hash   : {idx.policy_hash}")
    print(f"  entries       : {len(idx.entries)}")
    return 0


def _cmd_index_status(args) -> int:
    ws = _resolve_workspace(args)
    if not ws.index_path.exists():
        _emit({"present": False, "stale": True, "path": str(ws.index_path)},
              _json_active(args))
        return 0
    try:
        idx = load_index(ws.index_path)
    except Exception as e:
        _emit({"present": True, "stale": True, "error": str(e)},
              _json_active(args))
        return 0
    stale = is_stale(idx, ws.brain_hash(), ws.policy_hash())
    _emit({
        "present": True,
        "stale": stale,
        "path": str(ws.index_path),
        "engine_version": idx.engine_version,
        "algorithm": idx.algorithm,
        "brain_hash": idx.brain_hash,
        "policy_hash": idx.policy_hash,
        "current_brain_hash": ws.brain_hash(),
        "current_policy_hash": ws.policy_hash(),
        "entries": len(idx.entries),
    }, _json_active(args))
    return 0 if not stale else 0  # status is informational, always rc=0


def _cmd_index_clean(args) -> int:
    ws = _resolve_workspace(args)
    if ws.index_path.exists():
        ws.index_path.unlink()
        print(f"removed {ws.index_path}")
    else:
        print(f"no index at {ws.index_path}")
    return 0


def _cmd_scan(args) -> int:
    ws = _resolve_workspace(args)
    from .index import load_or_rebuild
    idx = load_or_rebuild(ws)
    payload = {
        "brain_hash": idx.brain_hash,
        "policy_hash": idx.policy_hash,
        "stale_index": False,
        "entries": [r.to_dict() for r in idx.entries.values()],
    }
    _emit(payload, _json_active(args))
    return 0


def _cmd_candidates(args) -> int:
    ws = _resolve_workspace(args)
    from .index import load_or_rebuild
    idx = load_or_rebuild(ws)
    brain_doc = ws.parse_brain()
    ps = parse_policy_document(ws.parse_policy())
    cands = detect_candidates(brain_doc, idx, ps, limit=args.limit)
    payload = {
        "brain_hash": idx.brain_hash,
        "policy_hash": idx.policy_hash,
        "stale_index": False,
        "candidates": [c.to_dict() for c in cands],
    }
    _emit(payload, _json_active(args))
    return 0


def _cmd_explain(args) -> int:
    ws = _resolve_workspace(args)
    from .index import load_or_rebuild
    idx = load_or_rebuild(ws)
    brain_doc = ws.parse_brain()
    ps = parse_policy_document(ws.parse_policy())
    cands = detect_candidates(brain_doc, idx, ps)
    try:
        expl = explain_candidate(brain_doc, idx, ps, cands, args.candidate)
    except LearningError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    _emit(expl, _json_active(args))
    return 0


def _cmd_elevate(args) -> int:
    ws = _resolve_workspace(args)
    from .index import load_or_rebuild
    idx = load_or_rebuild(ws)
    brain_doc = ws.parse_brain()
    ps = parse_policy_document(ws.parse_policy())
    cands = detect_candidates(brain_doc, idx, ps)

    candidate = None
    policy_id = None
    if args.candidate:
        for c in cands:
            if c.candidate_id == args.candidate:
                candidate = c
                break
        if candidate is None:
            print(f"error: candidate {args.candidate!r} not found", file=sys.stderr)
            return 1
    elif args.policy:
        policy_id = args.policy
        # Look up the policy directly; find any candidate whose source
        # sigil matches the policy's declared source. This lets the
        # user explicitly pick an "apply" policy even when the
        # candidate's auto-detected policy_match is a "propose" policy.
        from .policy import find_policy
        pol = find_policy(ps, policy_id)
        if pol is None:
            print(f"error: policy {args.policy!r} not found", file=sys.stderr)
            return 1
        pol_sources = pol.source.split("|") if pol.source else []
        for c in cands:
            for src_sel in c.source_entries:
                src_sig = src_sel.split(":", 1)[0]
                if src_sig in pol_sources:
                    candidate = c
                    break
            if candidate is not None:
                break
        if candidate is None:
            print(f"error: no candidate matched policy {args.policy!r}", file=sys.stderr)
            return 1
    else:
        print("error: --candidate or --policy required", file=sys.stderr)
        return 1

    patch = plan_patch(
        brain_doc, ps, candidate,
        policy_id=policy_id,
        admin_confirmed=False,
        user_confirmed=bool(args.confirm),
    )
    mode = "apply" if args.apply and args.confirm else "dry-run"
    if args.apply and not args.confirm:
        print("error: --apply requires --confirm", file=sys.stderr)
        return 1
    result = apply_patch(ws, brain_doc, patch, mode=mode, confirm=bool(args.confirm))
    _emit(result, _json_active(args))
    return 0


def _cmd_profile(args) -> int:
    ws = _resolve_workspace(args)
    from .index import load_or_rebuild
    idx = load_or_rebuild(ws)
    # Order entries by read_priority, then by promotion_score
    order = ["P0", "P1", "P2", "P3", "P4", "P5"]
    entries = sorted(
        idx.entries.values(),
        key=lambda r: (order.index(r.read_priority), -r.promotion_score),
    )
    budget = int(args.budget)
    # Rough token estimate: ~12 tokens per entry selector + ~3 per signal
    used = 0
    selected = []
    for r in entries:
        cost = 12 + 3 * len(r.signals)
        if used + cost > budget:
            break
        selected.append(r.to_dict())
        used += cost
    payload = {
        "budget": budget,
        "used": used,
        "selected_count": len(selected),
        "total_entries": len(entries),
        "entries": selected,
    }
    _emit(payload, _json_active(args))
    return 0


__all__ = ["add_learn_subparser"]
