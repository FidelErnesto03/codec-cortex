"""CODEC-CORTEX CLI entry point.

Usage (canonical commands):
    cortex new brain --out brain.cortex
    cortex render brain.cortex --format hcortex --mode edit --out brain.hcortex.edit.md
    cortex compile brain.hcortex.edit.md --out brain.cortex
    cortex verify brain.cortex --roundtrip hcortex-edit
    cortex list brain.cortex
    cortex get brain.cortex FCS:primary --format json
    cortex add brain.cortex --section $2 --sigil FCS --name primary --value 'what:"x"'
    cortex update brain.cortex FCS:primary --set what="new"
    cortex delete brain.cortex FCS:secondary
    cortex move brain.cortex FCS:primary --to-section $3
    cortex glossary list brain.cortex
    cortex micro list brain.cortex
    cortex doctor brain.cortex
    cortex diff a.cortex b.cortex
    cortex format brain.cortex
    cortex recover legacy.cortex --out legacy.fixed.cortex
    cortex diagram list brain.cortex
    cortex diagram extract brain.cortex --name flow

Aliases (Section 22.2 of SKILL.md):
    cortex decode   = cortex render   (decode .cortex to a view)
    cortex encode   = cortex compile  (encode a view back to .cortex)
    cortex patch_add     = cortex add
    cortex patch_update  = cortex update
    cortex patch_remove  = cortex delete
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .. import __version__
from .commands import (
    new as cmd_new,
    render as cmd_render,
    compile as cmd_compile,
    verify as cmd_verify,
    get as cmd_get,
    list as cmd_list,
    add as cmd_add,
    update as cmd_update,
    delete as cmd_delete,
    move as cmd_move,
    glossary as cmd_glossary,
    micro as cmd_micro,
    doctor as cmd_doctor,
    diff as cmd_diff,
    format as cmd_format,
    recover as cmd_recover,
    diagram as cmd_diagram,
    v2_roundtrip as cmd_v2_roundtrip,
    v2_convert as cmd_v2_convert,
    v2_roundtrip_bidir as cmd_v2_roundtrip_bidir,
    v2_compare as cmd_v2_compare,
    v2_verify_view as cmd_v2_verify_view,
    v2_explain_loss as cmd_v2_explain_loss,
    v2_canonicalize as cmd_v2_canonicalize,
    v2_inspect as cmd_v2_inspect,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cortex",
        description=(
            "CODEC-CORTEX CLI — modular deterministic processor for .cortex files. "
            f"v{__version__}"
        ),
    )
    p.add_argument("--version", action="version", version=f"cortex {__version__}")
    p.add_argument(
        "--json", action="store_true",
        help="emit machine-readable JSON where supported",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # ------------------------------------------------------------------
    # new
    # ------------------------------------------------------------------
    sp = sub.add_parser("new", help="create a new .cortex file from a template")
    sp.add_argument("kind", choices=["brain", "skill", "package", "generic"])
    sp.add_argument("--out", required=True, help="output file path")
    sp.add_argument("--name", default=None)
    sp.add_argument("--version", dest="doc_version", default=None)
    sp.add_argument("--domain", default=None)
    sp.add_argument("--owner", default=None)
    sp.add_argument("--language", default="en")
    sp.add_argument("--template", choices=["minimal", "standard", "enterprise"], default="standard")
    sp.add_argument("--with-diagrams", action="store_true")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_new.run)

    # ------------------------------------------------------------------
    # render  (alias: decode)
    # ------------------------------------------------------------------
    # v1.1.3 P2-8: `decode <file>` (alias) defaults to --mode readable
    # so the planned `cortex decode <file>` UX works without flags.
    sp = sub.add_parser("render", help="render .cortex to HCORTEX markdown", aliases=["decode"])
    sp.add_argument("input")
    sp.add_argument("--format", choices=["hcortex"], default="hcortex")
    sp.add_argument(
        "--mode", choices=["read", "edit", "readable", "audit", "recovery", "full"],
        default=None,
        help="read=readable, edit=editable; recovery/full are profile aliases; "
             "default=readable (v1.1.3 P2-8)",
    )
    sp.add_argument("--profile", choices=["min", "recovery", "work", "full"], default=None,
                    help="HCORTEX profile (MIN/RECOVERY/WORK/FULL)")
    sp.add_argument(
        "--layout", choices=["priority", "section"], default=None,
        help="priority=global P0→P5 order; section=preserve section grouping; "
             "auto-selects based on profile/mode",
    )
    sp.add_argument("--out", default=None)
    sp.add_argument("--with-source", action="store_true",
                    help="include source column in READ mode (audit mode)")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_render.run)

    # ------------------------------------------------------------------
    # compile  (alias: encode)
    # ------------------------------------------------------------------
    sp = sub.add_parser("compile", help="compile HCORTEX-EDIT markdown back to .cortex",
                        aliases=["encode"])
    sp.add_argument("input")
    sp.add_argument("--out", required=True)
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_compile.run)

    # ------------------------------------------------------------------
    # verify  (with --strict and --kind)
    # ------------------------------------------------------------------
    sp = sub.add_parser("verify", help="validate a .cortex file (optionally with roundtrip)")
    sp.add_argument("input")
    sp.add_argument("--roundtrip", choices=["hcortex-edit", "cortex"], default=None)
    sp.add_argument("--strict", action="store_true",
                    help="promote warnings to errors (cognitive governance)")
    sp.add_argument("--kind", choices=["brain", "skill", "package", "generic"], default=None,
                    help="explicit document kind for level-policy checks")
    sp.set_defaults(func=cmd_verify.run)

    # ------------------------------------------------------------------
    # get
    # ------------------------------------------------------------------
    sp = sub.add_parser("get", help="get a single entry by selector")
    sp.add_argument("input")
    sp.add_argument("selector")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_get.run)

    # ------------------------------------------------------------------
    # list
    # ------------------------------------------------------------------
    sp = sub.add_parser("list", help="list entries in a .cortex file")
    sp.add_argument("input")
    sp.add_argument("--section", default=None)
    sp.add_argument("--sigil", default=None)
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_list.run)

    # ------------------------------------------------------------------
    # add  (alias: patch_add)
    # ------------------------------------------------------------------
    sp = sub.add_parser("add", help="add a new entry to a .cortex file",
                        aliases=["patch_add"])
    sp.add_argument("input")
    sp.add_argument("--section", required=True)
    sp.add_argument("--sigil", required=True)
    sp.add_argument("--name", required=True)
    sp.add_argument("--value", required=True, help='attrs body e.g. \'what:"x", priority:"high"\'')
    sp.add_argument("--create-section", action="store_true")
    sp.add_argument("--allow-duplicate", action="store_true")
    sp.add_argument(
        "--allow-unknown-sigil", action="store_true",
        help="permit adding entries with sigils not declared in $0 (recovery/debug)",
    )
    sp.add_argument(
        "--no-validate-write", action="store_true",
        help="skip post-mutation validation before persisting (default: validate)",
    )
    sp.add_argument(
        "--strict-write", action="store_true",
        help="require strict validation (warnings also block write)",
    )
    sp.add_argument(
        "--unsafe-allow-secret-forensics", action="store_true",
        help="FORENSIC ONLY: bypass E031_SECRET_NOT_BYPASSABLE for secret "
             "scanning.  Use with extreme caution; --force alone cannot "
             "override the no-clear-text-secrets rule (SKILL.md §16.1).",
    )
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_add.run)

    # ------------------------------------------------------------------
    # update  (alias: patch_update)
    # ------------------------------------------------------------------
    sp = sub.add_parser("update", help="update an existing entry",
                        aliases=["patch_update"])
    sp.add_argument("input")
    sp.add_argument("selector")
    sp.add_argument("--set", dest="set_pairs", action="append", default=[],
                    help='key="value" (can repeat)')
    sp.add_argument("--body", default=None, help="replace cuerpo/bloque body")
    sp.add_argument("--append", action="store_true")
    sp.add_argument(
        "--no-validate-write", action="store_true",
        help="skip post-mutation validation before persisting (default: validate)",
    )
    sp.add_argument(
        "--strict-write", action="store_true",
        help="require strict validation (warnings also block write)",
    )
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_update.run)

    # ------------------------------------------------------------------
    # delete  (alias: patch_remove)
    # ------------------------------------------------------------------
    sp = sub.add_parser("delete", help="delete an entry",
                        aliases=["patch_remove"])
    sp.add_argument("input")
    sp.add_argument("selector")
    sp.add_argument(
        "--no-validate-write", action="store_true",
        help="skip post-mutation validation before persisting (default: validate)",
    )
    sp.add_argument(
        "--strict-write", action="store_true",
        help="require strict validation (warnings also block write)",
    )
    sp.add_argument("--force", action="store_true")
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=cmd_delete.run)

    # ------------------------------------------------------------------
    # move
    # ------------------------------------------------------------------
    sp = sub.add_parser("move", help="move an entry to another section")
    sp.add_argument("input")
    sp.add_argument("selector")
    sp.add_argument("--to-section", required=True)
    sp.add_argument(
        "--no-validate-write", action="store_true",
        help="skip post-mutation validation before persisting (default: validate)",
    )
    sp.add_argument(
        "--strict-write", action="store_true",
        help="require strict validation (warnings also block write)",
    )
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_move.run)

    # ------------------------------------------------------------------
    # glossary
    # ------------------------------------------------------------------
    sp = sub.add_parser("glossary", help="glossary CRUD")
    g_sub = sp.add_subparsers(dest="glossary_command", required=True)

    gsp = g_sub.add_parser("list", help="list sigils in $0")
    gsp.add_argument("input")
    gsp.add_argument("--format", choices=["text", "json"], default="text")
    gsp.set_defaults(func=cmd_glossary.run_list)

    gsp = g_sub.add_parser("add", help="add a sigil to $0")
    gsp.add_argument("input")
    gsp.add_argument("--sigil", required=True)
    gsp.add_argument("--name", required=True)
    gsp.add_argument("--type", required=True)
    gsp.add_argument("--risk", default="M")
    gsp.add_argument("--layer", default="Semantic")
    gsp.add_argument("--description", required=True)
    gsp.add_argument("--force-governance", action="store_true")
    gsp.add_argument("--dry-run", action="store_true")
    gsp.set_defaults(func=cmd_glossary.run_add)

    gsp = g_sub.add_parser("update", help="update a sigil's metadata")
    gsp.add_argument("input")
    gsp.add_argument("--sigil", required=True)
    gsp.add_argument("--description", default=None)
    gsp.add_argument("--risk", default=None)
    gsp.add_argument("--layer", default=None)
    gsp.add_argument("--force-governance", action="store_true")
    gsp.add_argument("--dry-run", action="store_true")
    gsp.set_defaults(func=cmd_glossary.run_update)

    gsp = g_sub.add_parser("delete", help="remove a sigil from $0")
    gsp.add_argument("input")
    gsp.add_argument("--sigil", required=True)
    gsp.add_argument("--force", action="store_true")
    gsp.add_argument("--dry-run", action="store_true")
    gsp.set_defaults(func=cmd_glossary.run_delete)

    # ------------------------------------------------------------------
    # micro
    # ------------------------------------------------------------------
    sp = sub.add_parser("micro", help="micro-token CRUD")
    m_sub = sp.add_subparsers(dest="micro_command", required=True)

    msp = m_sub.add_parser("list", help="list micro-tokens")
    msp.add_argument("input")
    msp.add_argument("--format", choices=["text", "json"], default="text")
    msp.set_defaults(func=cmd_micro.run_list)

    msp = m_sub.add_parser("add", help="add a micro-token")
    msp.add_argument("input")
    msp.add_argument("--token", required=True)
    msp.add_argument("--value", required=True)
    msp.add_argument("--dry-run", action="store_true")
    msp.set_defaults(func=cmd_micro.run_add)

    msp = m_sub.add_parser("update", help="update a micro-token")
    msp.add_argument("input")
    msp.add_argument("--token", required=True)
    msp.add_argument("--value", required=True)
    msp.add_argument("--dry-run", action="store_true")
    msp.set_defaults(func=cmd_micro.run_update)

    msp = m_sub.add_parser("delete", help="remove a micro-token")
    msp.add_argument("input")
    msp.add_argument("--token", required=True)
    msp.add_argument("--force", action="store_true")
    msp.add_argument("--dry-run", action="store_true")
    msp.set_defaults(func=cmd_micro.run_delete)

    # ------------------------------------------------------------------
    # doctor  (with --strict and --kind)
    # ------------------------------------------------------------------
    sp = sub.add_parser("doctor", help="deep diagnostic of a .cortex file")
    sp.add_argument("input")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.add_argument("--strict", action="store_true",
                    help="promote warnings to errors (cognitive governance)")
    sp.add_argument("--kind", choices=["brain", "skill", "package", "generic"], default=None,
                    help="explicit document kind for level-policy checks")
    sp.set_defaults(func=cmd_doctor.run)

    # ------------------------------------------------------------------
    # diff  (with --profile)
    # ------------------------------------------------------------------
    sp = sub.add_parser("diff", help="structural diff between two .cortex files")
    sp.add_argument("left")
    sp.add_argument("right")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.add_argument(
        "--profile", choices=["structural", "semantic", "governance"], default="structural",
        help="structural=AST diff, semantic=values+glossary, governance=+level policy",
    )
    sp.set_defaults(func=cmd_diff.run)

    # ------------------------------------------------------------------
    # format
    # ------------------------------------------------------------------
    sp = sub.add_parser("format", help="re-serialize a .cortex file canonically")
    sp.add_argument("input")
    sp.add_argument("--out", default=None)
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_format.run)

    # ------------------------------------------------------------------
    # recover  (new — audit gap H-06)
    # ------------------------------------------------------------------
    sp = sub.add_parser("recover", help="recover a legacy or non-conforming .cortex file")
    sp.add_argument("input")
    sp.add_argument("--out", default=None,
                    help="write the recovered .cortex to this path (default: stdout)")
    sp.add_argument("--strict", action="store_true")
    sp.add_argument(
        "--embed-aud-rsk", action="store_true",
        help="embed AUD and RSK entries in the recovered .cortex so the "
             "artefact itself carries the recovery trace (re-audit M-RA-03)",
    )
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_recover.run)

    # ------------------------------------------------------------------
    # diagram  (new — audit gap B-010)
    # ------------------------------------------------------------------
    sp = sub.add_parser("diagram", help="diagram operations (DIAG sigil)")
    d_sub = sp.add_subparsers(dest="diagram_command", required=True)

    dsp = d_sub.add_parser("list", help="list DIAG entries")
    dsp.add_argument("input")
    dsp.add_argument("--format", choices=["text", "json"], default="text")
    dsp.set_defaults(func=cmd_diagram.run_list)

    dsp = d_sub.add_parser("extract", help="extract a DIAG bloque verbatim")
    dsp.add_argument("input")
    dsp.add_argument("--name", required=True, help="DIAG entry name")
    dsp.add_argument("--out", default=None, help="output file (default: stdout)")
    dsp.add_argument(
        "--print-newline", action="store_true",
        help="add a trailing newline on stdout output (terminal-friendly; "
             "default: write exactly the bytes)",
    )
    dsp.set_defaults(func=cmd_diagram.run_extract)

    dsp = d_sub.add_parser("validate", help="validate DIAG bloque integrity")
    dsp.add_argument("input")
    dsp.add_argument("--name", default=None, help="specific DIAG name (default: all)")
    dsp.add_argument("--format", choices=["text", "json"], default="text")
    dsp.set_defaults(func=cmd_diagram.run_validate)

    # ------------------------------------------------------------------
    # v2-roundtrip (v2.0.0 — CORTEX v2 byte-identical roundtrip)
    # ------------------------------------------------------------------
    sp = sub.add_parser("v2-roundtrip", help="verify CORTEX v2 roundtrip fidelity (byte-identical)")
    sp.add_argument("input", help="CORTEX v2 file to test")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_v2_roundtrip.run)

    # ------------------------------------------------------------------
    # v2-convert (v2.1.0 — CORTEX ⇄ HCORTEX conversion)
    # ------------------------------------------------------------------
    sp = sub.add_parser("v2-convert", help="convert between CORTEX v2 and HCORTEX v2")
    sp.add_argument("input", help="input file")
    sp.add_argument("--from", dest="from_format", choices=["cortex", "hcortex", "hcortex-r"], required=True,
                    help="source format")
    sp.add_argument("--to", dest="to_format", choices=["cortex", "hcortex", "hcortex-r"], required=True,
                    help="target format")
    sp.add_argument("--out", default=None, help="output file (default: stdout)")
    sp.add_argument(
        "--force-write-on-error", action="store_true",
        help="v2.2.2: write --out even when E_VIEW_* errors occur. "
             "Default: skip writing --out if any E_VIEW_* error is present "
             "(prevents invalid artefacts on disk).",
    )
    sp.add_argument(
        "--strict", action="store_true",
        help="v2.2.2: promote W_VIEW_* warnings to errors (rc=1).",
    )
    sp.add_argument(
        "--mode", choices=["normal", "strict", "audit", "recovery", "display"], default="normal",
        help="v2.2.3 PRE-05: operating mode. 'display' produces Markdown without "
             "reversible contract (not canonical HCORTEX).",
    )
    sp.set_defaults(func=cmd_v2_convert.run)

    # ------------------------------------------------------------------
    # v2-roundtrip-bidir (v2.3.0 — CORTEX ⇄ HCORTEX bidirectional roundtrip)
    # ------------------------------------------------------------------
    sp = sub.add_parser("v2-roundtrip-bidir",
                        help="v2.3.0: validate CORTEX ⇄ HCORTEX bidirectional roundtrip")
    sp.add_argument("input", help="CORTEX or HCORTEX file")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_v2_roundtrip_bidir.run)

    # ------------------------------------------------------------------
    # v2-compare (v2.3.0 — compare two artefacts)
    # ------------------------------------------------------------------
    sp = sub.add_parser("v2-compare",
                        help="v2.3.0: compare two CORTEX/HCORTEX artefacts (byte/AST/semantic/content)")
    sp.add_argument("left", help="left file")
    sp.add_argument("right", help="right file")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.add_argument("--verbose", action="store_true", help="show first 20 diffs in detail")
    sp.set_defaults(func=cmd_v2_compare.run)

    # ------------------------------------------------------------------
    # v2-verify-view (v2.3.0 — validate VIEW coverage and reversibility)
    # ------------------------------------------------------------------
    sp = sub.add_parser("v2-verify-view",
                        help="v2.3.0: validate VIEW coverage, reversibility, consistency")
    sp.add_argument("input", help="CORTEX file")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.add_argument("--strict", action="store_true", help="warnings also cause non-zero rc")
    sp.set_defaults(func=cmd_v2_verify_view.run)

    # ------------------------------------------------------------------
    # v2-explain-loss (v2.3.0 — explain loss, omission, non-reversible)
    # ------------------------------------------------------------------
    sp = sub.add_parser("v2-explain-loss",
                        help="v2.3.0: explain loss, omission, or non-reversible content")
    sp.add_argument("input", help="CORTEX or HCORTEX file")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_v2_explain_loss.run)

    # ------------------------------------------------------------------
    # v2-canonicalize (v2.3.0 — normalize without changing semantics)
    # ------------------------------------------------------------------
    sp = sub.add_parser("v2-canonicalize",
                        help="v2.3.0: normalize artefact without changing semantics")
    sp.add_argument("input", help="CORTEX or HCORTEX file")
    sp.add_argument("--out", default=None, help="output file (default: stdout)")
    sp.set_defaults(func=cmd_v2_canonicalize.run)

    # ------------------------------------------------------------------
    # v2-inspect (v2.3.0 — show AST, sections, sigils, VIEW, errors)
    # ------------------------------------------------------------------
    sp = sub.add_parser("v2-inspect",
                        help="v2.3.0: inspect AST, sections, sigils, VIEW coverage, errors")
    sp.add_argument("input", help="CORTEX or HCORTEX file")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_v2_inspect.run)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 2

    # Normalise --json: stash it on args so subcommands can read it (audit L-03)
    json_mode = getattr(args, "json", False) or ("--json" in (argv or sys.argv))
    args._json_mode = json_mode  # type: ignore[attr-defined]

    try:
        rc = args.func(args)
        return int(rc or 0)
    except Exception as e:
        if json_mode:
            print(json.dumps({
                "ok": False,
                "error": {
                    "code": getattr(e, "code", "E000_UNKNOWN"),
                    "message": str(e),
                },
            }, indent=2, ensure_ascii=False))
        else:
            print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
