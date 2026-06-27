"""``cortex new`` — create a new .cortex file from a template.

v1.1.2: ``--json`` now produces real JSON output (was text-only before).
"""

from __future__ import annotations

import json
import os

from ...core.errors import CortexError, TemplateUnknownError
from ...crud.transactions import atomic_write_cortex
from ...templates import build_brain, build_package, build_skill


def run(args) -> int:
    kind = args.kind
    if kind == "brain":
        doc = build_brain(
            name=args.name or "project-brain",
            domain=args.domain or "active work",
            owner=args.owner or "agent",
            language=args.language,
            template=args.template,
            with_diagrams=args.with_diagrams,
        )
    elif kind == "skill":
        doc = build_skill(
            name=args.name or "codec-cortex",
            version=args.doc_version or "1.0.0",
            domain=args.domain or "LLM/SLM contextual memory",
            owner=args.owner or "agent",
            language=args.language,
            template=args.template,
            with_diagrams=args.with_diagrams,
        )
    elif kind == "package":
        doc = build_package(
            name=args.name or "context_package",
            version=args.doc_version or "0.1.0",
            domain=args.domain or "specific domain",
            owner=args.owner or "source",
            language=args.language,
            template=args.template,
            with_diagrams=args.with_diagrams,
        )
    elif kind == "generic":
        doc = build_brain(
            name=args.name or "generic-cortex",
            domain=args.domain or "generic",
            owner=args.owner or "agent",
            language=args.language,
            template=args.template,
            with_diagrams=args.with_diagrams,
        )
    else:
        raise TemplateUnknownError(kind)

    out_path = args.out
    if os.path.exists(out_path) and not args.force:
        raise CortexError(
            "E015_ATOMIC_WRITE_FAILED",
            f"output file exists: {out_path} (use --force to overwrite)",
        )

    result = atomic_write_cortex(doc, out_path, force=True, keep_backup=False)
    payload = {
        "ok": True,
        "text": f"created {out_path} ({result.bytes_written} bytes)",
        "path": out_path,
        "bytes": result.bytes_written,
        "kind": kind,
    }
    # v1.1.2: honour --json properly
    json_mode = getattr(args, "_json_mode", False)
    if json_mode:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        print(payload["text"])
    return 0
