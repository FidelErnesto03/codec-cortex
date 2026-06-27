"""``cortex recover`` — recover a legacy or non-conforming .cortex file.

Closes audit gap H-06: tolerates preambles, legacy column names, missing
``$0``, and reconstructs a conforming document with RSK diagnostics for
every reconstructed sigil.

v1.1.6 P1-5: recover now validates the result and returns non-zero if
the recovered artefact is not conformant (e.g. still has E033/E034 errors
that recovery cannot fix).
"""

from __future__ import annotations

import json
import os
import sys

from ...core.errors import CortexError
from ...core.parser import parse_cortex
from ...core.writer import write_cortex
from ...core.validator import validate
from ...crud.transactions import atomic_write_text
from ...hcortex import recover_cortex
from ..commands import load_doc  # noqa: F401  (re-exported helper)


def run(args) -> int:
    if not os.path.exists(args.input):
        raise CortexError("E013_NOT_FOUND", f"file not found: {args.input}")
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    result = recover_cortex(
        text, path=args.input, strict=args.strict,
        embed_aud_rsk=getattr(args, "embed_aud_rsk", False),
    )
    cortex_text = write_cortex(result.doc)

    # v1.1.6 P1-5: validate the recovered artefact.  If it still has
    # non-bypassable errors, return non-zero so CI and automation can
    # detect that recovery did not produce a conformant file.
    reparsed = parse_cortex(cortex_text, path=args.input)
    post_diags = validate(reparsed, strict=False)
    post_errors = [d for d in post_diags if d.get("severity") == "error"]
    conformant = len(post_errors) == 0

    if args.out:
        # Write even if non-conformant — the user may need to inspect
        # the partial recovery.  But return non-zero to signal the issue.
        atomic_write_text(cortex_text, args.out, keep_backup=False)
        if args.format == "json":
            print(json.dumps({
                "ok": conformant,
                "input": args.input,
                "out": args.out,
                "reconstructed_glossary": result.reconstructed_glossary,
                "preamble_lines": len(result.preamble),
                "diagnostics": result.diagnostics,
                "post_validation_errors": post_errors if not conformant else [],
                "conformant": conformant,
            }, indent=2, default=str))
        else:
            print(f"recovered {args.input} → {args.out}")
            print(f"  preamble stripped: {len(result.preamble)} line(s)")
            print(f"  reconstructed $0: {result.reconstructed_glossary}")
            print(f"  diagnostics: {len(result.diagnostics)}")
            for d in result.diagnostics:
                sev = d.get("severity", "info")
                print(f"  [{sev}] {d.get('code')}: {d.get('message')}")
            if not conformant:
                print(f"  ⚠ WARNING: recovered artefact has {len(post_errors)} "
                      "validation error(s) — NOT conformant")
                for e in post_errors[:5]:
                    print(f"    [{e.get('code')}] {e.get('message', '')[:100]}")
    else:
        if args.format == "json":
            print(json.dumps({
                "ok": conformant,
                "input": args.input,
                "reconstructed_glossary": result.reconstructed_glossary,
                "preamble_lines": len(result.preamble),
                "diagnostics": result.diagnostics,
                "conformant": conformant,
                "cortex": cortex_text,
            }, indent=2, default=str))
        else:
            sys.stdout.write(cortex_text)

    # v1.1.6 P1-5: non-zero if not conformant
    return 0 if conformant else 1
