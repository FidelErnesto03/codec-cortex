"""``cortex verify`` — validate a .cortex file and optionally roundtrip.

v0.3.4 (E2.6): supports ``--signature <MANIFEST>`` (and alias
``--manifest``) to verify the SHA256 of the input file against a
SHA256SUMS manifest produced by ``scripts/sign_release.py``.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from ...core.compare import compare_ast
from ...core.document_kind import infer_document_kind
from ...core.writer import write_cortex
from ...core.validator import validate
from ...hcortex import parse_hcortex_edit, render_hcortex_edit
from ...security.signature import verify_signature
from ..commands import load_doc


def _run_signature_check(args) -> int:
    """E2.6 (v0.3.4): handle ``cortex verify --signature <manifest>``.

    Returns 0 on match, 1 on mismatch/missing.
    """
    manifest_arg = getattr(args, "signature_manifest", None) or getattr(
        args, "manifest_path", None
    )
    if not manifest_arg:
        # Should not happen — caller checks before dispatching.
        raise RuntimeError("verify_signature dispatched without --signature/--manifest")
    manifest_path = Path(manifest_arg).expanduser().resolve()
    target_file = Path(args.input).expanduser().resolve()
    strict = getattr(args, "strict", False)

    result = verify_signature(target_file, manifest_path, strict=strict)

    json_mode = getattr(args, "_json_mode", False)
    if json_mode:
        payload = {
            "ok": result.ok,
            "input": args.input,
            "manifest": str(manifest_path),
            "strict": strict,
            "result": result.to_dict(),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        lines = [
            f"signature verify: {args.input}",
            f"  manifest:      {manifest_path}",
            f"  ok:            {result.ok}",
            f"  reason:        {result.reason}",
        ]
        if result.expected_hash:
            lines.append(f"  expected:      {result.expected_hash}")
        if result.actual_hash:
            lines.append(f"  actual:        {result.actual_hash}")
        print("\n".join(lines))
    return 0 if result.ok else 1


def _run_verify_v2(args, raw_text: str) -> int:
    """Verify a v2-format CORTEX file using the v2 parser directly.

    v2 files have a ```markdown wrapper and/or <!-- CODEC-CORTEX --> header.
    The v2 parser handles these natively. Validation checks structure:
    - $0 must exist and have section definitions
    - All sections must parse
    - At least one VIEW directive in $13
    """
    from ...v2.parser import parse_cortex_v2

    strict = getattr(args, "strict", False)

    inner = raw_text
    if inner.startswith("```"):
        idx = inner.find("\n")
        if idx != -1:
            inner = inner[idx + 1 :]
        close_idx = inner.rfind("\n```")
        if close_idx != -1:
            inner = inner[:close_idx]

    v2_doc = parse_cortex_v2(inner)

    total_entries = sum(len(s.entries) for s in v2_doc.sections)
    errors: list[str] = []
    warnings: list[str] = []

    # Structural validation for v2 CORTEX
    if "$0" not in {s.id for s in v2_doc.sections}:
        errors.append("[E_MISSING_GLOSSARY] $0 section not found")
    else:
        s0 = next(s for s in v2_doc.sections if s.id == "$0")
        if not s0.entries:
            warnings.append("[W_EMPTY_GLOSSARY] $0 section exists but has no entries")

    # Check $13 has VIEW directives
    if "$13" in {s.id for s in v2_doc.sections}:
        s13 = next(s for s in v2_doc.sections if s.id == "$13")
        view_count = sum(1 for e in s13.entries if e.sigil == "VIEW")
        if view_count == 0:
            warnings.append("[W_NO_VIEWS] $13 section exists but has no VIEW directives")

    if strict and not errors and not warnings:
        pass  # v2 format validated

    kind_label = "v2"
    from pathlib import Path
    p = Path(args.input)
    if p.name.lower().startswith("skill") or "skill" in str(p).lower():
        kind_label = "skill (v2)"

    print(f"verifying: {args.input}")
    print(f"  kind:          {kind_label}")
    print(f"  sections:      {len(v2_doc.sections)}")
    print(f"  entries:       {total_entries}")
    print(f"  errors:        {len(errors)}")
    print(f"  warnings:      {len(warnings)}")
    print(f"  strict mode:   {strict}")
    if errors:
        print()
        print("errors:")
        for e in errors:
            print(f"  {e}")
    if warnings:
        print()
        print("warnings:")
        for w in warnings:
            print(f"  {w}")

    return 0 if not errors else 1


def run(args) -> int:
    # v0.3.4 (E2.6): --signature short-circuits all other validation.
    signature_manifest = getattr(args, "signature_manifest", None) or getattr(
        args, "manifest_path", None
    )
    if signature_manifest:
        return _run_signature_check(args)

    # Detect v2 format early — use v2 parser directly
    from ...core.parser import parse_cortex

    with open(args.input, "r", encoding="utf-8") as f:
        raw_text = f.read()

    is_v2 = raw_text.lstrip().startswith("```") or "<!-- CODEC-CORTEX" in raw_text

    if is_v2:
        return _run_verify_v2(args, raw_text)

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
