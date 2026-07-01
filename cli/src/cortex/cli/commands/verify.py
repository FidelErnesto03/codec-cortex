"""``cortex verify`` — validate a .cortex file and optionally roundtrip."""

from __future__ import annotations

import json
import os
import tempfile

from ...core.compare import compare_ast
from ...core.document_kind import infer_document_kind
from ...core.parser import parse_cortex
from ...core.writer import write_cortex
from ...core.validator import validate
from ...hcortex import parse_hcortex_edit, render_hcortex_edit
from ..commands import load_doc


def run(args) -> int:
    doc = load_doc(args.input)

    # Apply explicit kind if provided (audit gap H-01/H-02)
    kind = None
    if getattr(args, "kind", None):
        from ...core.document_kind import DocumentKind
        kind = DocumentKind(kind=args.kind, source="cli")

    strict = getattr(args, "strict", False)
    diagnostics = validate(doc, strict=strict, kind=kind)
    errors = [d for d in diagnostics if d.get("severity") == "error"]
    warnings = [d for d in diagnostics if d.get("severity") == "warning"]

    # Infer kind for display if not explicit
    if kind is None:
        kind = infer_document_kind(doc, args.input)

    text_lines = []
    text_lines.append(f"verifying: {args.input}")
    text_lines.append(f"  kind:          {kind.kind} (inferred via {kind.source})")
    text_lines.append(f"  sections:      {len(doc.sections)}")
    text_lines.append(f"  sigils:        {len(doc.glossary.sigils)}")
    total_entries = sum(len(s.entries) for s in doc.sections if s.id != "$0")
    text_lines.append(f"  entries:       {total_entries}")
    text_lines.append(f"  errors:        {len(errors)}")
    text_lines.append(f"  warnings:      {len(warnings)}")
    text_lines.append(f"  strict mode:   {strict}")
    if errors:
        text_lines.append("")
        text_lines.append("errors:")
        for e in errors:
            text_lines.append(f"  [{e.get('code')}] {e.get('message')}")

    roundtrip_ok = None
    roundtrip_diffs = []
    if args.roundtrip == "hcortex-edit":
        md = render_hcortex_edit(doc, source=args.input)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".hcortex.edit.md", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(md)
            tmp_path = tmp.name
        try:
            with open(tmp_path, "r", encoding="utf-8") as f:
                md_text = f.read()
            doc2 = parse_hcortex_edit(md_text, source=tmp_path)
            cortex2 = write_cortex(doc2)
            doc3 = parse_cortex(cortex2, path="<roundtrip>")
            diff = compare_ast(doc, doc3)
            roundtrip_ok = diff.equal
            roundtrip_diffs = [d.to_dict() for d in diff.diffs]
            if not roundtrip_ok:
                text_lines.append(f"  roundtrip:     FAILED ({len(diff.diffs)} diff(s))")
            else:
                text_lines.append("  roundtrip:     OK (structural identity preserved)")
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    elif args.roundtrip == "cortex":
        # Plain .cortex → .cortex roundtrip (no HCORTEX step)
        text2 = write_cortex(doc)
        doc3 = parse_cortex(text2, path="<roundtrip>")
        diff = compare_ast(doc, doc3)
        roundtrip_ok = diff.equal
        roundtrip_diffs = [d.to_dict() for d in diff.diffs]
        text_lines.append(
            f"  roundtrip:     {'OK' if roundtrip_ok else 'FAILED'} "
            f"({len(diff.diffs)} diff(s))"
        )

    payload = {
        "text": "\n".join(text_lines),
        "input": args.input,
        "kind": kind.kind,
        "sections": len(doc.sections),
        "entries": total_entries,
        "errors": errors,
        "warnings": warnings,
        "strict": strict,
        "roundtrip": {
            "mode": args.roundtrip,
            "ok": roundtrip_ok,
            "diffs": roundtrip_diffs,
        } if args.roundtrip else None,
    }

    json_mode = getattr(args, "_json_mode", False)
    if json_mode:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        print(payload["text"])

    if errors:
        return 1
    if strict and warnings:
        return 1
    if args.roundtrip and not roundtrip_ok:
        return 2
    return 0
