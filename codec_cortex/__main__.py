#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI entry point for CODEC-CORTEX (dual-surface: 0.1 + slots).

Naming convention:
    hcortex.py       — HCORTEX 0.1 render/compile (legacy surface)
    slothcortex.py   — HCORTEX 0.2 render/compile (slots surface)

Commands:
    parse <file>            parse and print AST JSON (dispatcher)
    validate <file>         validate; exit 0 if valid, 1 if error
    canonicalize <file>     print canonical bytes (dispatcher)
    hash <file>             print canonical hash (dispatcher)
    harness [C14N_DIR] [HCORTEX_DIR]
                            legacy F3/F4 reviewer harness (run_all_tests)
    conformance [MANIFEST_DIR]
                            slots conformance harness (manifest-driven)
    to-hcortex [--embed-ast] <file>
                            render CORTEX 0.2 to HCORTEX 0.2
    from-hcortex <file>     compile HCORTEX 0.2 back to CORTEX 0.2
    migrate <cmd> <file>    migrate 0.1→0.2 (inspect|plan|apply|verify|rollback)

With no arguments, prints this help. The historical behavior of running
the F3/F4 harness by default is preserved via the `harness` subcommand.

Exit codes:
    0 = success
    1 = parse/validation failure
    2 = CLI usage error

NOTA: Tras la fusión de slots 0.2, los hashes canónicos 0.1 pueden diferir.
El legacy `harness` puede reportar roundtrip_cortex_mismatch — es esperado.
Usar `conformance` para la nueva superficie slots 0.2.
"""

import sys
import os
import json


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    rest = argv[1:]

    if cmd == "parse":
        return _cmd_parse(rest)
    elif cmd == "validate":
        return _cmd_validate(rest)
    elif cmd == "canonicalize":
        return _cmd_canonicalize(rest)
    elif cmd == "hash":
        return _cmd_hash(rest)
    elif cmd == "harness":
        return _cmd_harness(rest)
    elif cmd == "conformance":
        return _cmd_conformance(rest)
    elif cmd == "to-hcortex":
        return _cmd_to_hcortex(rest)
    elif cmd == "from-hcortex":
        return _cmd_from_hcortex(rest)
    elif cmd == "migrate":
        return _cmd_migrate(rest)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        return 2


def _read_source(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _cmd_parse(args):
    if not args:
        print("Usage: parse <file>", file=sys.stderr)
        return 2
    from codec_cortex.dispatcher import parse_cortex
    try:
        source = _read_source(args[0])
        doc = parse_cortex(source)
        ast_dict = _ast_to_dict(doc)
        print(json.dumps(ast_dict, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        return 1


def _cmd_validate(args):
    if not args:
        print("Usage: validate <file>", file=sys.stderr)
        return 2
    from codec_cortex.dispatcher import parse_cortex
    try:
        source = _read_source(args[0])
        parse_cortex(source)
        print("valid")
        return 0
    except Exception as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        return 1


def _cmd_canonicalize(args):
    if not args:
        print("Usage: canonicalize <file>", file=sys.stderr)
        return 2
    from codec_cortex.dispatcher import parse_cortex, canonicalize
    try:
        source = _read_source(args[0])
        doc = parse_cortex(source)
        sys.stdout.write(canonicalize(doc))
        return 0
    except Exception as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        return 1


def _cmd_hash(args):
    if not args:
        print("Usage: hash <file>", file=sys.stderr)
        return 2
    from codec_cortex.dispatcher import parse_cortex, hash_cortex
    try:
        source = _read_source(args[0])
        doc = parse_cortex(source)
        print(hash_cortex(doc))
        return 0
    except Exception as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        return 1


def _cmd_harness(args):
    """Legacy F3/F4 reviewer harness (pre-merge __main__ behavior).

    NOTA: Tras la fusión de slots 0.2, los hashes canónicos 0.1
    pueden diferir. Si el harness reporta roundtrip_cortex_mismatch,
    es esperado — no es una regresión del ciclo actual.
    Usar 'conformance' para la nueva superficie slots.
    """
    from codec_cortex.harness import run_all_tests

    base = os.environ.get(
        "REV_PACKAGE",
        os.path.join(os.path.dirname(__file__), "..", "experiments")
    )

    c14n_dir = args[0] if len(args) > 0 else os.path.join(base, "gate-f3", "c14n-corpus")
    hcortex_dir = args[1] if len(args) > 1 else os.path.join(base, "gate-f4")

    if not os.path.exists(c14n_dir):
        alt_c14n = os.path.join(base, "c14n", "corpus")
        if os.path.exists(alt_c14n):
            c14n_dir = alt_c14n
    if not os.path.exists(hcortex_dir):
        alt_hc = os.path.join(base, "hcortex")
        if os.path.exists(alt_hc):
            hcortex_dir = alt_hc

    print("╔══════════════════════════════════════════════════════════╗")
    print("║  AVISO: Legacy harness (0.1) — hashes canónicos 0.1   ║")
    print("║  pueden diferir tras la fusión slots 0.2. Si hay      ║")
    print("║  roundtrip_cortex_mismatch, es esperado.              ║")
    print("║  Usar 'conformance' para la superficie slots 0.2.     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"C14N directory: {c14n_dir}")
    print(f"HCORTEX directory: {hcortex_dir}")
    print()

    if not os.path.exists(c14n_dir) and not os.path.exists(hcortex_dir):
        print("ERROR: Neither corpus directory found.")
        print("Provide paths as arguments: python3 -m codec_cortex harness C14N_DIR HCORTEX_DIR")
        return 1

    report = run_all_tests(c14n_dir, hcortex_dir)

    out_path = os.path.join(
        os.path.dirname(__file__), "..", "rev-report.json"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport written to: {out_path}")

    verdict = report["verdict"]
    if verdict in ("PASS", "CONDITIONAL_PASS"):
        return 0
    return 1


def _cmd_conformance(args):
    """Run slots conformance harness (manifest-driven)."""
    from codec_cortex.slotharness import main_cli
    return main_cli(args)


def _cmd_to_hcortex(args):
    """Render CORTEX 0.2 file to HCORTEX 0.2.

    Usage: to-hcortex [--embed-ast] <file>
        --embed-ast  inject <!-- cortex-ast: HASH --> for integrity verification
    """
    embed_ast = False
    files = []
    for a in args:
        if a == "--embed-ast":
            embed_ast = True
        else:
            files.append(a)
    if not files:
        print("Usage: to-hcortex [--embed-ast] <file>", file=sys.stderr)
        return 2
    from codec_cortex.dispatcher import parse_cortex
    from codec_cortex.slothcortex import render_hcortex_slots
    try:
        source = _read_source(files[0])
        doc = parse_cortex(source)
        print(render_hcortex_slots(doc, embed_ast=embed_ast), end="")
        return 0
    except Exception as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        return 1


def _cmd_migrate(args):
    """Migrate CORTEX 0.1 → 0.2. Subcommands: inspect, plan, apply, verify, rollback."""
    from codec_cortex.slotmigrate import main_cli
    return main_cli(args)


def _cmd_from_hcortex(args):
    """Compile HCORTEX 0.2 back to CORTEX 0.2 canonical."""
    if not args:
        print("Usage: from-hcortex <file>", file=sys.stderr)
        return 2
    from codec_cortex.dispatcher import canonicalize
    from codec_cortex.slothcortex import compile_hcortex_slots
    try:
        source = _read_source(args[0])
        doc, diags = compile_hcortex_slots(source)
        if diags:
            for d in diags:
                print(f"{d['code']}: {d['message']}", file=sys.stderr)
            return 1
        print(canonicalize(doc), end="")
        return 0
    except Exception as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        return 1


def _ast_to_dict(doc):
    """Minimal AST to dict for CLI output."""
    from codec_cortex.scalars import Scalar
    def scalar_to_dict(s):
        if s is None:
            return None
        if s.kind == "list":
            return {"kind": s.kind, "value": [scalar_to_dict(x) for x in s.value], "lexeme": s.lexeme}
        return {"kind": s.kind, "value": s.value, "lexeme": s.lexeme}
    sections = []
    for sec in doc.sections:
        ideas = []
        for idea in sec.ideas:
            payload = idea.payload
            pd = None
            if payload and isinstance(payload, tuple):
                kind = payload[0]
                if kind == "attrs":
                    pd = {"kind": "attrs", "pairs": [[k, scalar_to_dict(v)] for k, v in payload[1]]}
                elif kind == "slots":
                    pd = {"kind": "slots", "slots": [{"position": fv.position, "name": fv.name, "value": scalar_to_dict(fv.value)} for fv in payload[1]]}
                elif kind in ("attrs-pos", "relacion"):
                    pd = {"kind": kind, "cells": [scalar_to_dict(c) for c in payload[1]]}
                elif kind in ("cuerpo", "bloque"):
                    pd = {"kind": kind, "text": payload[1]}
            ideas.append({"namespace": idea.namespace, "symbol": idea.symbol,
                          "name": idea.name, "shape": idea.shape, "payload": pd})
        sections.append({"id": sec.id, "title": sec.title, "capa": sec.capa, "ideas": ideas})
    glossary = {
        "capa": doc.glossary.capa,
        "format": None,
        "symbols": [],
        "sigil_map": None,
    }
    if doc.glossary.format:
        glossary["format"] = {
            "cortex": doc.glossary.format.cortex,
            "encoding": doc.glossary.format.encoding,
        }
    for s in doc.glossary.symbols:
        glossary["symbols"].append({
            "namespace": s.namespace, "sigil": s.sigil, "label": s.label,
            "shape": s.shape, "encoding": getattr(s, "encoding", None),
            "weight": s.weight, "focus": s.focus,
        })
    if getattr(doc.glossary, "sigil_map", None):
        sm = doc.glossary.sigil_map
        glossary["sigil_map"] = {
            "marker": sm.marker, "codepoint": sm.codepoint, "base": sm.base,
            "syntax": sm.syntax, "order": sm.order,
        }
    return {"cortex_version": doc.cortex_version, "glossary": glossary, "sections": sections}


if __name__ == "__main__":
    sys.exit(main())
