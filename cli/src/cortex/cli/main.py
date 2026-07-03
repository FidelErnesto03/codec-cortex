# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

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

v2 commands (canonical names since v0.3.2; v2-* aliases are deprecated):
    cortex roundtrip        <file>           # was v2-roundtrip
    cortex convert          <file> ...       # was v2-convert
    cortex roundtrip-bidir  <file>           # was v2-roundtrip-bidir
    cortex compare          <a> <b>          # was v2-compare
    cortex verify-view      <file>           # was v2-verify-view
    cortex explain-loss     <file>           # was v2-explain-loss
    cortex canonicalize     <file>           # was v2-canonicalize (now VIEW-aware)
    cortex inspect          <file>           # was v2-inspect

Aliases (Section 22.2 of SKILL.md):
    cortex decode   = cortex render   (decode .cortex to a view)
    cortex encode   = cortex compile  (encode a view back to .cortex)
    cortex patch_add     = cortex add
    cortex patch_update  = cortex update
    cortex patch_remove  = cortex delete

Deprecated aliases (still accepted, will be removed in v1.0.0):
    v2-roundtrip, v2-convert, v2-roundtrip-bidir, v2-compare,
    v2-verify-view, v2-explain-loss, v2-canonicalize, v2-inspect
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .. import __version__
from ..core.modes import (
    annotate_args,
    check_permission,
    is_write_command,
    resolve_mode,
)
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
    audit as cmd_audit,
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
    # v0.3.4 (E2.3): mutation gate — global --mode flag.
    # NOTE: ``dest="op_mode"`` to avoid collision with v2-convert's own
    # ``--mode`` flag (which has different choices: normal/strict/audit/...).
    # The env var is ``CORTEX_MODE`` (per the E2.3 plan).
    p.add_argument(
        "--mode", dest="op_mode", default=None,
        choices=["read-only", "editor", "admin"],
        help="v0.3.4 (E2.3): operating mode. read-only blocks writes; "
             "editor (default) requires confirmation for --force; admin "
             "skips all checks. Can also be set via $CORTEX_MODE.",
    )
    p.add_argument(
        "--yes", dest="yes", action="store_true",
        help="v0.3.4 (E2.3): pre-confirm destructive operations in editor "
             "mode (equivalent to answering 'y' to all prompts).",
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
    # verify  (with --strict, --kind, --signature)
    # v0.3.4 (E2.6): --signature <manifest> verifies SHA256 of the input
    # file against the manifest entry.
    # ------------------------------------------------------------------
    sp = sub.add_parser("verify", help="validate a .cortex file (optionally with roundtrip)")
    sp.add_argument("input")
    sp.add_argument("--roundtrip", choices=["hcortex-edit", "cortex"], default=None)
    sp.add_argument("--strict", action="store_true",
                    help="promote warnings to errors (cognitive governance)")
    sp.add_argument("--kind", choices=["brain", "skill", "package", "generic"], default=None,
                    help="explicit document kind for level-policy checks")
    sp.add_argument(
        "--signature", dest="signature_manifest", default=None,
        metavar="MANIFEST",
        help="v0.3.4 (E2.6): verify the SHA256 of <input> against a "
             "SHA256SUMS manifest. When set, no other validation runs; "
             "exit code 0 = match, 1 = mismatch/missing. Combine with "
             "--strict to also fail when the file is not listed in the "
             "manifest.",
    )
    sp.add_argument(
        "--manifest", dest="manifest_path", default=None,
        metavar="MANIFEST",
        help="alias for --signature (mutually exclusive: if both are "
             "set, --signature wins).",
    )
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
    # doctor  (with --strict, --kind, and E2.2 secret scan flags)
    # ------------------------------------------------------------------
    sp = sub.add_parser("doctor", help="deep diagnostic of a .cortex file")
    sp.add_argument("input")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.add_argument("--strict", action="store_true",
                    help="promote warnings to errors (cognitive governance)")
    sp.add_argument("--kind", choices=["brain", "skill", "package", "generic"], default=None,
                    help="explicit document kind for level-policy checks")
    sp.add_argument(
        "--scan-secrets", action="store_true",
        help="v0.3.4 (E2.2): exit 2 if any high-severity secret finding "
             "is detected. The scan always runs and is reported in the "
             "summary; this flag only changes the exit code.",
    )
    sp.add_argument(
        "--scan-secrets-paths", dest="scan_secrets_paths", nargs="+", default=[],
        metavar="PATH",
        help="v0.3.4 (E2.2): additional paths to scan for secrets "
             "(in addition to <input>). Use to scan a whole repo.",
    )
    sp.add_argument(
        "--secrets-baseline", dest="secrets_baseline", default=None,
        metavar="BASELINE",
        help="v0.3.4 (E2.2): path to a .secrets.baseline JSON file. "
             "Findings matching (path, rule, line) in the baseline are "
             "silenced. Use `cortex doctor --scan-secrets-paths ... --format json` "
             "to produce a baseline draft.",
    )
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
    # audit  (E2.4, v0.3.4 — on-demand audit logging)
    # ------------------------------------------------------------------
    sp = sub.add_parser("audit", help="on-demand audit logging control (E2.4)")
    a_sub = sp.add_subparsers(dest="audit_command", required=True)

    asp = a_sub.add_parser("on", help="enable audit logging for this session")
    asp.set_defaults(func=cmd_audit.run_on)

    asp = a_sub.add_parser("off", help="disable audit logging")
    asp.set_defaults(func=cmd_audit.run_off)

    asp = a_sub.add_parser("status", help="show audit logging status")
    asp.set_defaults(func=cmd_audit.run_status)

    asp = a_sub.add_parser("snapshot", help="export a one-shot snapshot of a .cortex file")
    asp.add_argument("file", help="path to the .cortex file to snapshot")
    asp.add_argument("--label", default=None, help="optional label appended to the snapshot filename")
    asp.set_defaults(func=cmd_audit.run_snapshot)

    asp = a_sub.add_parser("prune", help="delete old daily log files")
    asp.add_argument("--keep-days", type=int, default=30, help="delete logs older than N days (default: 30)")
    asp.set_defaults(func=cmd_audit.run_prune)

    # ------------------------------------------------------------------
    # roundtrip  (canonical; alias: v2-roundtrip — deprecated)
    # v2.0.0: CORTEX v2 byte-identical roundtrip.
    # v0.3.2: rename v2-roundtrip → roundtrip (canonical).
    # ------------------------------------------------------------------
    sp = sub.add_parser(
        "roundtrip",
        help="verify CORTEX v2 roundtrip fidelity (byte-identical)",
        aliases=["v2-roundtrip"],
    )
    sp.add_argument("input", help="CORTEX v2 file to test")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_v2_roundtrip.run)

    # ------------------------------------------------------------------
    # convert  (canonical; alias: v2-convert — deprecated)
    # v2.1.0: CORTEX ⇄ HCORTEX conversion.
    # v0.3.2: rename v2-convert → convert (canonical).
    # ------------------------------------------------------------------
    sp = sub.add_parser(
        "convert",
        help="convert between CORTEX v2 and HCORTEX v2",
        aliases=["v2-convert"],
    )
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
    # roundtrip-bidir  (canonical; alias: v2-roundtrip-bidir — deprecated)
    # v2.3.0: CORTEX ⇄ HCORTEX bidirectional roundtrip.
    # v0.3.2: rename v2-roundtrip-bidir → roundtrip-bidir (canonical).
    # ------------------------------------------------------------------
    sp = sub.add_parser(
        "roundtrip-bidir",
        help="validate CORTEX ⇄ HCORTEX bidirectional roundtrip",
        aliases=["v2-roundtrip-bidir"],
    )
    sp.add_argument("input", help="CORTEX or HCORTEX file")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_v2_roundtrip_bidir.run)

    # ------------------------------------------------------------------
    # compare  (canonical; alias: v2-compare — deprecated)
    # v2.3.0: compare two CORTEX/HCORTEX artefacts.
    # v0.3.2: rename v2-compare → compare (canonical).
    # ------------------------------------------------------------------
    sp = sub.add_parser(
        "compare",
        help="compare two CORTEX/HCORTEX artefacts (byte/AST/semantic/content)",
        aliases=["v2-compare"],
    )
    sp.add_argument("left", help="left file")
    sp.add_argument("right", help="right file")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.add_argument("--verbose", action="store_true", help="show first 20 diffs in detail")
    sp.set_defaults(func=cmd_v2_compare.run)

    # ------------------------------------------------------------------
    # verify-view  (canonical; alias: v2-verify-view — deprecated)
    # v2.3.0: validate VIEW coverage, reversibility, consistency.
    # v0.3.2: rename v2-verify-view → verify-view (canonical).
    # ------------------------------------------------------------------
    sp = sub.add_parser(
        "verify-view",
        help="validate VIEW coverage, reversibility, consistency",
        aliases=["v2-verify-view"],
    )
    sp.add_argument("input", help="CORTEX file")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.add_argument("--strict", action="store_true", help="warnings also cause non-zero rc")
    sp.set_defaults(func=cmd_v2_verify_view.run)

    # ------------------------------------------------------------------
    # explain-loss  (canonical; alias: v2-explain-loss — deprecated)
    # v2.3.0: explain loss, omission, or non-reversible content.
    # v0.3.2: rename v2-explain-loss → explain-loss (canonical).
    # ------------------------------------------------------------------
    sp = sub.add_parser(
        "explain-loss",
        help="explain loss, omission, or non-reversible content",
        aliases=["v2-explain-loss"],
    )
    sp.add_argument("input", help="CORTEX or HCORTEX file")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_v2_explain_loss.run)

    # ------------------------------------------------------------------
    # canonicalize  (canonical; alias: v2-canonicalize — deprecated)
    # v2.3.0: normalize artefact without changing semantics.
    # v0.3.2: rename v2-canonicalize → canonicalize (canonical).
    #          Adds --preserve flag and VIEW-aware behavior (B-01/B-05 fix):
    #          - If the artefact has no VIEW directives, emit a warning and
    #            only normalize whitespace/section ordering (no structural
    #            rewrite). This preserves v1-render compatibility.
    #          - --preserve forces this behavior even when VIEW directives
    #            are present.
    # ------------------------------------------------------------------
    sp = sub.add_parser(
        "canonicalize",
        help="normalize artefact without changing semantics (VIEW-aware)",
        aliases=["v2-canonicalize"],
    )
    sp.add_argument("input", help="CORTEX or HCORTEX file")
    sp.add_argument("--out", default=None, help="output file (default: stdout)")
    sp.add_argument(
        "--preserve", action="store_true",
        help="v0.3.2: preserve original structure even if VIEW directives "
             "are present. Only normalize whitespace and section ordering. "
             "Forces v1-render compatibility.",
    )
    sp.set_defaults(func=cmd_v2_canonicalize.run)

    # ------------------------------------------------------------------
    # inspect  (canonical; alias: v2-inspect — deprecated)
    # v2.3.0: inspect AST, sections, sigils, VIEW coverage, errors.
    # v0.3.2: rename v2-inspect → inspect (canonical).
    # ------------------------------------------------------------------
    sp = sub.add_parser(
        "inspect",
        help="inspect AST, sections, sigils, VIEW coverage, errors",
        aliases=["v2-inspect"],
    )
    sp.add_argument("input", help="CORTEX or HCORTEX file")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(func=cmd_v2_inspect.run)

    # ------------------------------------------------------------------
    # learn  (CODEC-CORTEX Learning Engine / CLE)
    # Deterministic, local-first learning engine for .cortex workspaces.
    # See SPEC §8 for the full command surface.
    # ------------------------------------------------------------------
    from ..learning.cli import add_learn_subparser
    add_learn_subparser(sub)

    # ------------------------------------------------------------------
    # session  (v0.2.0 — CODEC-CORTEX session lifecycle)
    # Wraps the learning engine's session module: start / status /
    # consolidate / close. See learning-engine-evolution.md §A.
    # ------------------------------------------------------------------
    from ..learning.session_cli import add_session_subparser
    add_session_subparser(sub)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 2

    # v0.3.4: prefer the parsed subcommand name from argparse, which is
    # always correct regardless of preceding global flags like --mode.
    invoked_command = getattr(args, "command", None)
    if not invoked_command:
        # Fallback: scan argv for the first non-flag token (used when the
        # command is invoked via an alias like `v2-roundtrip` — argparse
        # resolves the alias to the canonical name in `args.command`, so
        # this fallback is only for very edge cases).
        for token in (argv or sys.argv[1:]):
            if token.startswith("-"):
                continue
            invoked_command = token
            break

    # v0.3.2 — Deprecation warning for v2-* aliases.
    # The original alias name (e.g. "v2-roundtrip") must be detected from
    # the raw argv because argparse resolves it to the canonical name
    # (e.g. "roundtrip") before we see `args.command`.
    _DEPRECATED_ALIASES = {
        "v2-roundtrip", "v2-convert", "v2-roundtrip-bidir", "v2-compare",
        "v2-verify-view", "v2-explain-loss", "v2-canonicalize", "v2-inspect",
    }
    raw_alias_used = None
    for token in (argv or sys.argv[1:]):
        if token in _DEPRECATED_ALIASES:
            raw_alias_used = token
            break
        if token and not token.startswith("-") and token not in (
            "read-only", "editor", "admin"
        ):
            # First non-flag, non-mode-value token is the command name;
            # if it's not in DEPRECATED_ALIASES, we can stop scanning.
            break
    if raw_alias_used:
        canonical = raw_alias_used.removeprefix("v2-")
        print(
            f"WARNING: `cortex {raw_alias_used}` is deprecated since v0.3.2; "
            f"use `cortex {canonical}` instead. The `v2-` prefix will be "
            f"removed in v1.0.0.",
            file=sys.stderr,
        )

    # Normalise --json: stash it on args so subcommands can read it (audit L-03)
    json_mode = getattr(args, "json", False) or ("--json" in (argv or sys.argv))
    args._json_mode = json_mode  # type: ignore[attr-defined]

    # v0.3.4 (E2.3) — Mutation gate.
    mode = resolve_mode(getattr(args, "op_mode", None))
    annotate_args(args, mode)
    if getattr(args, "yes", False):
        args.mode_confirmed = True  # type: ignore[attr-defined]

    # Build the canonical command name for the gate. For subcommand groups
    # (glossary, micro, diagram, audit), the canonical name is "<group> <sub>".
    cmd_name = invoked_command or ""
    sub_action = getattr(args, "glossary_command", None) or \
                 getattr(args, "micro_command", None) or \
                 getattr(args, "diagram_command", None) or \
                 getattr(args, "audit_command", None)
    if sub_action and cmd_name:
        canonical_cmd = f"{cmd_name} {sub_action}"
    else:
        canonical_cmd = cmd_name

    uses_force = bool(getattr(args, "force", False))
    non_interactive = not sys.stdin.isatty()

    gate_error = check_permission(
        mode=mode,
        command=canonical_cmd,
        uses_force=uses_force,
        confirmed=bool(getattr(args, "mode_confirmed", False)),
        non_interactive=non_interactive,
    )
    if gate_error is not None:
        if json_mode:
            print(json.dumps({
                "ok": False,
                "error": {
                    "code": gate_error.code,
                    "message": str(gate_error),
                },
                "mode": mode.value,
                "command": canonical_cmd,
            }, indent=2, ensure_ascii=False))
        else:
            print(f"error: {gate_error}", file=sys.stderr)
        # Exit code 13 = mode violation (distinguishes from generic rc=1).
        # Still log the blocked attempt if audit is on.
        _maybe_audit_log(canonical_cmd, args, mode, result="blocked",
                         error_code=gate_error.code)
        return 13

    try:
        rc = args.func(args)
        rc_int = int(rc or 0)
        # E2.4: log successful or failed mutation (only if audit is on).
        result = "ok" if rc_int == 0 else "error"
        _maybe_audit_log(canonical_cmd, args, mode, result=result)
        return rc_int
    except Exception as e:
        # E2.4: log the exception.
        _maybe_audit_log(
            canonical_cmd, args, mode, result="error",
            error_code=getattr(e, "code", "E000_UNKNOWN"),
        )
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


def _maybe_audit_log(
    command: str,
    args,
    mode,
    *,
    result: str,
    error_code: Optional[str] = None,
) -> None:
    """E2.4 (v0.3.4): append an audit entry IF logging is enabled.

    Only mutation commands (add/update/delete/move/format/compile/recover)
    are logged. Read commands (list/get/verify/...) are NOT logged — the
    plan says "Cada mutación CRUD solo se loguea si `cortex audit on`
    está activo".
    """
    from ..audit.logger import AuditEntry, append_entry

    if not is_write_command(command):
        return

    # The .cortex file path is in args.input for most commands.
    file_path = getattr(args, "input", None) or ""

    entry = AuditEntry(
        op=command,
        file=str(file_path),
        mode=mode.value,
        result=result,
        selector=getattr(args, "selector", None),
        error_code=error_code,
    )
    try:
        append_entry(entry)
    except Exception:
        # Audit logging must NEVER break the actual command.
        # Silently swallow errors.
        pass


if __name__ == "__main__":
    sys.exit(main())
