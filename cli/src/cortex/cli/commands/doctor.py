"""``cortex doctor`` — deep diagnostic of a .cortex file."""

from __future__ import annotations

import json

from ...core.document_kind import infer_document_kind
from ...core.validator import validate
from ..commands import load_doc


def run(args) -> int:
    doc = load_doc(args.input)
    strict = getattr(args, "strict", False)

    # Apply explicit kind if provided (audit gap H-01/H-02)
    kind = None
    if getattr(args, "kind", None):
        from ...core.document_kind import DocumentKind
        kind = DocumentKind(kind=args.kind, source="cli")
    if kind is None:
        kind = infer_document_kind(doc, args.input)

    diagnostics = validate(doc, strict=strict, kind=kind)
    errors = [d for d in diagnostics if d.get("severity") == "error"]
    warnings = [d for d in diagnostics if d.get("severity") == "warning"]
    sections = doc.sections
    sigils = list(doc.glossary.sigils.values())
    types = list(doc.glossary.types.values())
    micro = list(doc.glossary.micro.values())
    entries = [(s.id, e) for s in sections if s.id != "$0" for e in s.entries]

    json_mode = getattr(args, "_json_mode", False)
    if args.format == "json" or json_mode:
        print(json.dumps({
            "ok": len(errors) == 0,
            "input": args.input,
            "kind": kind.kind,
            "kind_source": kind.source,
            "sections": len(sections),
            "entries": len(entries),
            "sigils": len(sigils),
            "types": len(types),
            "micro": len(micro),
            "strict": strict,
            "errors": errors,
            "warnings": warnings,
            "section_ids": [s.id for s in sections],
            "sigil_names": [s.sigil for s in sigils],
        }, indent=2, default=str))
    else:
        lines = []
        lines.append(f"doctor: {args.input}")
        lines.append(f"  kind:         {kind.kind} (inferred via {kind.source})")
        lines.append(f"  strict:       {strict}")
        lines.append(f"  sections:     {len(sections)}  ({', '.join(s.id for s in sections)})")
        lines.append(f"  entries:      {len(entries)}")
        lines.append(f"  sigils:       {len(sigils)}")
        lines.append(f"  types:        {len(types)}")
        lines.append(f"  micro:        {len(micro)}")
        lines.append(f"  errors:       {len(errors)}")
        lines.append(f"  warnings:     {len(warnings)}")
        if errors:
            lines.append("")
            lines.append("errors:")
            for e in errors:
                lines.append(f"  [{e.get('code')}] {e.get('message')}")
        if warnings:
            lines.append("")
            lines.append("warnings:")
            for w in warnings:
                lines.append(f"  [{w.get('code')}] {w.get('message')}")
        print("\n".join(lines))
    return 1 if errors else 0
