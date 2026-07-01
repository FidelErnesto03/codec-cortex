"""``cortex diff`` — structural/semantic/governance diff between two .cortex files.

v1.1.2: ``--profile governance`` redefinido.  Antes comparaba sólo los
``findings`` de ``validate_level_policy`` (ambos archivos válidos → rc=0
aun si cambiaron restricciones críticas).  Ahora compara los **cambios
reales** en entradas de gobernanza (FCS, OBJ, CNST, RSK, AUD, CLAIM,
LIM) entre los dos archivos, además de los findings.  Retorna non-zero
si hay cualquier cambio en gobernanza.
"""

from __future__ import annotations

import json

from ...core.compare import compare_ast
from ...core.document_kind import infer_document_kind, validate_level_policy
from ..commands import load_doc


# Sigilos que constituyen "gobernanza" — cualquier cambio en estas
# entradas afecta las invariantes cognitivas del protocolo.
GOVERNANCE_SIGILS = frozenset({
    "FCS", "OBJ", "WRK", "STP", "NXT",      # working state
    "CNST", "AXM", "!",                       # hard constraints
    "RSK", "AUD", "CLAIM", "LIM",            # risk / audit / limits
    "KNW",                                     # promoted knowledge
})


def _extract_governance_changes(left, right) -> list:
    """Return a list of governance-relevant diffs between two ASTs.

    Filters :func:`~cortex.core.compare.compare_ast` results to only
    those affecting governance sigils.  This is the real "governance
    diff": did any constraint, risk, audit or working-state entry
    change between the two files?
    """

    result = compare_ast(left, right)
    gov_diffs = []
    for d in result.diffs:
        path = d.path or ""
        # path is like "$2/FCS:primary" or "sigils.FCS"
        # We consider it governance-relevant if any GOVERNANCE_SIGILS
        # appears in the path.
        path_upper = path.upper()
        if any(sig in path_upper for sig in GOVERNANCE_SIGILS):
            gov_diffs.append(d.to_dict())
        # Glossary changes to governance sigils also count
        if path.startswith("sigils."):
            sig = path.split(".", 1)[1]
            if sig in GOVERNANCE_SIGILS:
                gov_diffs.append(d.to_dict())
    return gov_diffs


def run(args) -> int:
    left = load_doc(args.left)
    right = load_doc(args.right)
    profile = getattr(args, "profile", "structural")

    json_mode = getattr(args, "_json_mode", False)
    if args.format == "json" or json_mode:
        if profile == "governance":
            # v1.1.2: governance diff = real changes in governance entries
            # + level-policy findings on both sides
            left_kind = infer_document_kind(left, args.left)
            right_kind = infer_document_kind(right, args.right)
            left_findings = validate_level_policy(left, left_kind)
            right_findings = validate_level_policy(right, right_kind)
            gov_changes = _extract_governance_changes(left, right)
            ok = (not gov_changes) and (not left_findings) and (not right_findings)
            print(json.dumps({
                "ok": ok,
                "profile": profile,
                "left": {
                    "kind": left_kind.kind,
                    "findings": left_findings,
                },
                "right": {
                    "kind": right_kind.kind,
                    "findings": right_findings,
                },
                "governance_changes": gov_changes,
                "summary": {
                    "governance_changes_count": len(gov_changes),
                    "left_findings_count": len(left_findings),
                    "right_findings_count": len(right_findings),
                },
            }, indent=2, default=str))
            return 0 if ok else 1
        else:
            result = compare_ast(left, right)
            print(json.dumps({
                "ok": result.equal,
                "profile": profile,
                "left": args.left,
                "right": args.right,
                "diffs": [d.to_dict() for d in result.diffs],
            }, indent=2, default=str))
            return 0 if result.equal else 1

    # Text mode
    if profile == "governance":
        left_kind = infer_document_kind(left, args.left)
        right_kind = infer_document_kind(right, args.right)
        left_findings = validate_level_policy(left, left_kind)
        right_findings = validate_level_policy(right, right_kind)
        gov_changes = _extract_governance_changes(left, right)
        ok = (not gov_changes) and (not left_findings) and (not right_findings)
        if ok:
            print(f"✓ {args.left} and {args.right} are governance-equal "
                  f"(no changes in governance entries, no findings)")
        else:
            print(f"✗ governance diff between {args.left} and {args.right}:")
            print(f"  left kind:  {left_kind.kind} ({len(left_findings)} finding(s))")
            print(f"  right kind: {right_kind.kind} ({len(right_findings)} finding(s))")
            print(f"  governance entry changes: {len(gov_changes)}")
            for c in gov_changes[:10]:
                print(f"  [{c.get('kind')}] {c.get('path')}: {c.get('message')}")
            for f in left_findings:
                print(f"  [L] [{f.get('code')}] {f.get('message')}")
            for f in right_findings:
                print(f"  [R] [{f.get('code')}] {f.get('message')}")
        return 0 if ok else 1

    # structural / semantic
    result = compare_ast(left, right)
    if result.equal:
        print(f"✓ {args.left} and {args.right} are structurally equal (profile={profile})")
    else:
        print(f"✗ {args.left} and {args.right} differ ({len(result.diffs)} diff(s), profile={profile}):")
        for d in result.diffs:
            print(f"  [{d.kind}] {d.path}: {d.message}")
    return 0 if result.equal else 1
