"""CORTEX 1.0 declared loss report (spec §8.2 / §8.3).

A declared loss is source information that the parser does not represent in the
AST and that therefore cannot be recovered by
``canonicalize(compile(render(doc)))``. The catalog is closed: any roundtrip
divergence that no catalog entry explains is an L499_UNCLASSIFIED_LOSS and makes
the command fail, so "zero unnamed losses" is verifiable rather than aspirational.

All five surfaces (Python, Go, Node, Rust, Bash) must emit byte-identical output;
this module is the reference implementation.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, List, Optional

from .dispatcher import canonicalize, parse_cortex
from .scalars import to_nfc, utf8_bytes
from .slothcortex import compile_hcortex_slots, render_hcortex_slots

PRESERVED = ["blocks", "identity", "scalars", "structure"]

L402 = "L402_COMMENT_DROPPED"
L403 = "L403_INTRALINE_WHITESPACE"
L405 = "L405_OPEN_ATTR_ORDER"
L499 = "L499_UNCLASSIFIED_LOSS"

_DETAIL = {
    L402: "comment line outside a multiline body is not represented in the AST",
    L403: "intraline whitespace is collapsed by canonicalization",
    L405: "editorial attribute order of an open sigil is not preserved",
    L499: "roundtrip diverges and no declared loss classifies the divergence",
}

_ACTION = {
    L402: "declare-only",
    L403: "declare-only",
    L405: "declare-only",
    L499: "fix-surface",
}


def _finding(code: str, path: str, category: str, recoverability: str) -> Dict[str, str]:
    return {
        "action": _ACTION[code],
        "category": category,
        "code": code,
        "detail": _DETAIL[code],
        "path": path,
        "recoverability": recoverability,
        "severity": "error" if code == L499 else "loss",
    }


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _strip_quoted(line: str) -> str:
    """Return the line with quoted string literals replaced by empty literals."""
    out: List[str] = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch == '"':
            out.append('""')
            i += 1
            while i < n:
                if line[i] == "\\":
                    i += 2
                    continue
                if line[i] == '"':
                    i += 1
                    break
                i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _lexical_losses(source: str) -> List[Dict[str, str]]:
    losses: List[Dict[str, str]] = []
    lines = source.split("\n")
    in_body = False
    for index, raw in enumerate(lines, start=1):
        line = raw[:-1] if raw.endswith("\r") else raw
        stripped = line.strip()
        if in_body:
            if stripped == "}":
                in_body = False
            continue
        if not stripped:
            continue
        if stripped.startswith("#"):
            losses.append(_finding(L402, f"line:{index}", "structure", "from-source-only"))
            continue
        if stripped.endswith("{") and not stripped.startswith("$0:"):
            in_body = True
        probe = _strip_quoted(line)
        if (
            probe != probe.rstrip(" \t")
            or "\t" in probe
            or "  " in probe
        ):
            losses.append(_finding(L403, f"line:{index}", "presentation", "from-source-only"))
    return losses


def _open_attr_order_losses(doc) -> List[Dict[str, str]]:
    losses: List[Dict[str, str]] = []
    symbols = {(s.namespace, s.sigil): s for s in doc.glossary.symbols}
    for section in doc.sections:
        for idea in section.ideas:
            if idea.shape != "attrs" or not idea.payload or idea.payload[0] != "attrs":
                continue
            sym = symbols.get((idea.namespace, idea.symbol)) or symbols.get((None, idea.symbol))
            if sym is None or not getattr(sym, "open", False):
                continue
            keys = [k for k, _ in idea.payload[1]]
            contract = [f.name for f in sym.contract]
            contract_keys = [k for k in contract if k in keys]
            extras = sorted((k for k in keys if k not in contract), key=lambda k: utf8_bytes(to_nfc(k)))
            if keys != contract_keys + extras:
                losses.append(_finding(L405, f"${section.id}", "order", "from-source-only"))
    return losses


def _dedupe(losses: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen = set()
    out: List[Dict[str, str]] = []
    for item in losses:
        key = (item["path"], item["code"])
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    out.sort(key=lambda item: (item["path"], item["code"]))
    return out


def loss_case_name(path: Optional[str]) -> str:
    if path is None or path == "-":
        return "stdin"
    base = os.path.basename(path)
    stem, _ext = os.path.splitext(base)
    return stem or base


def build_loss_report(source: str, case: str) -> Dict:
    doc = parse_cortex(source)
    version = getattr(getattr(doc, "glossary", None), "format", None)
    declared = getattr(version, "cortex", None) if version is not None else None
    if declared not in (None, "1.0"):
        raise ValueError(f"loss-report requires cortex:1.0 (declared: {declared})")

    # Render and detect source-order losses before canonicalizing: C14N mutates
    # the AST in place (microtoken expansion, attribute normalization).
    attr_losses = _open_attr_order_losses(doc)
    rendered = render_hcortex_slots(doc)
    canonical_source = canonicalize(doc)
    roundtrip, _diags = compile_hcortex_slots(rendered)
    if roundtrip is None:
        raise ValueError("HCORTEX roundtrip compilation failed")
    canonical_roundtrip = canonicalize(roundtrip)

    losses = _lexical_losses(source)
    losses.extend(attr_losses)
    equivalent = canonical_source == canonical_roundtrip
    if not equivalent:
        losses.append(_finding(L499, "$", "structure", "irrecoverable"))

    return {
        "case": case,
        "losses": _dedupe(losses),
        "mode": "canonical",
        "operation": "render",
        "preserved": list(PRESERVED),
        "reversible": equivalent,
        "schema_version": "1.0",
        "source_format": "cortex:1.0",
        "source_sha256": _sha256(source),
        "structural_equivalence": equivalent,
        "target_format": "hcortex:1.0",
        "target_sha256": _sha256(rendered),
        "warnings": [],
    }


def dumps_canonical(report: Dict) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
