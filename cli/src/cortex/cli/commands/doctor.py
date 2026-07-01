"""``cortex doctor`` — deep diagnostic of a .cortex file.

v0.3.4 (E2.2): adds secret scanning via :mod:`cortex.security.secret_scanner`.
By default the scan is reported in the diagnostic summary; pass
``--scan-secrets`` to exit 1 if any high-severity finding is present.
Use ``--scan-secrets-paths <path>...`` to scan additional paths beyond
the .cortex file itself (useful for scanning a whole repo).
"""

from __future__ import annotations

import json
from pathlib import Path

from ...core.document_kind import infer_document_kind
from ...core.validator import validate
from ...security.secret_scanner import redact, scan_paths
from ..commands import load_doc


def run(args) -> int:
    doc = load_doc(args.input)
    strict = getattr(args, "strict", False)

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

    # E2.2 (v0.3.4): secret scan.
    # The .cortex file itself is always scanned. Additional paths can be
    # provided via --scan-secrets-paths (typically used in CI to scan
    # the whole repo, not just the .cortex artefact).
    scan_paths_arg = getattr(args, "scan_secrets_paths", None) or []
    scan_targets = [Path(args.input)] + [Path(p) for p in scan_paths_arg]
    baseline = getattr(args, "secrets_baseline", None)
    baseline_path = Path(baseline) if baseline else None
    scan_result = scan_paths(scan_targets, baseline=baseline_path)

    json_mode = getattr(args, "_json_mode", False)
    if args.format == "json" or json_mode:
        payload = {
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
            "secret_scan": scan_result.to_dict(),
        }
        # Redact matches in the JSON output too, so the doctor output
        # itself doesn't become a secret-leaking artefact.
        for f in payload["secret_scan"]["findings"]:
            f["match"] = redact(f["match"])
        print(json.dumps(payload, indent=2, default=str))
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
        # Secret scan summary
        lines.append("")
        lines.append("secret scan:")
        lines.append(f"  files scanned:  {scan_result.files_scanned}")
        lines.append(f"  bytes scanned:  {scan_result.bytes_scanned}")
        lines.append(f"  findings:       {len(scan_result.findings)} "
                     f"(high={len(scan_result.by_severity('high'))}, "
                     f"medium={len(scan_result.by_severity('medium'))})")
        if scan_result.findings:
            lines.append("")
            lines.append("  findings (match redacted):")
            for f in scan_result.findings:
                lines.append(
                    f"    [{f.severity.upper():6}] {f.path}:{f.line} "
                    f"{f.rule} — {redact(f.match)}"
                )
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

    # Exit codes:
    #   1 if there are validation errors
    #   2 if --scan-secrets was set and any high-severity finding exists
    #   (both can be true; the higher code wins)
    rc = 1 if errors else 0
    if getattr(args, "scan_secrets", False) and scan_result.has_high:
        rc = max(rc, 2)
    return rc
