"""``cortex render`` (alias: ``cortex decode``) — render .cortex to HCORTEX markdown.

v1.1.2: ``--json`` now produces real JSON output (was text-only before).
"""

from __future__ import annotations

import json
import os
import sys

from ...core.errors import CortexError
from ...crud.transactions import atomic_write_text
from ...hcortex import render_hcortex_edit, render_hcortex_read
from ..commands import load_doc


def run(args) -> int:
    doc = load_doc(args.input)
    # v1.1.3 P2-8: default mode is 'readable' so `decode <file>` works
    # without --mode (matches the SKILL §22.2 planned UX).
    mode = (args.mode or "readable").lower()

    # Mode normalisation: legacy 'read'/'edit' → canonical
    if mode == "read":
        mode = "readable"
    # Map profile arg to uppercase
    profile = args.profile.upper() if args.profile else None

    if mode == "edit":
        md = render_hcortex_edit(doc, source=args.input)
    elif mode in ("readable", "audit", "recovery", "full"):
        # Map mode aliases to profile + with_source
        if mode == "recovery":
            profile = profile or "RECOVERY"
        elif mode == "full":
            profile = profile or "FULL"
            args.with_source = True
        elif mode == "audit":
            args.with_source = True
        md = render_hcortex_read(
            doc,
            with_source=getattr(args, "with_source", False),
            profile=profile,
            mode=mode.upper() if mode in ("recovery", "full") else "READABLE",
            layout=getattr(args, "layout", None),
        )
    else:
        raise CortexError(
            "E021_INVALID_VALUE",
            f"unknown render mode {args.mode!r}",
        )

    out = args.out
    json_mode = getattr(args, "_json_mode", False)
    if out:
        # If --out exists and no --force, error (audit gap L-03).
        if os.path.exists(out) and not getattr(args, "force", False):
            raise CortexError(
                "E015_ATOMIC_WRITE_FAILED",
                f"output file exists: {out} (use --force to overwrite)",
            )
        result = atomic_write_text(md, out, keep_backup=False)
        payload = {
            "ok": True,
            "text": (
                f"rendered {args.input} → {out} "
                f"({result.bytes_written} bytes, mode={mode}"
                f"{f', profile={profile}' if profile else ''})"
            ),
            "input": args.input,
            "out": out,
            "mode": mode,
            "profile": profile,
            "bytes": result.bytes_written,
        }
        if json_mode:
            print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
        else:
            print(payload["text"])
    else:
        # No --out: write markdown to stdout.  --json wraps it in a payload.
        if json_mode:
            print(json.dumps({
                "ok": True,
                "input": args.input,
                "mode": mode,
                "profile": profile,
                "markdown": md,
            }, indent=2, ensure_ascii=False, default=str))
        else:
            sys.stdout.write(md)
    return 0
