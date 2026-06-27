"""Validator — checks an AST against the CODEC-CORTEX contract.

The validator runs a series of structural rules:

1. ``$0`` exists and is the first section (already enforced by parser).
2. Every sigil used by an entry is declared in ``$0``.
3. Every type referenced by a sigil is declared.
4. ``attrs-pos`` sigils have a positional contract.
5. Critical sigils (FCS, OBJ, WRK, STP, CNST, RSK, CLAIM, LIM, AUD,
   SES, LNG, KNW, HDL) have their required fields.
6. Status / severity / priority values are in the allowed sets.
7. No duplicate entries (same sigil+name) unless explicitly allowed.
8. **Cognitive governance** (1.1.0): level separation (Nivel 1 sin estado
   vivo, Nivel 2 con FCS+OBJ, Nivel 3 sin WRK), ``survive`` domain,
   ``CNST:blocking`` → ``survive:min``, secret scanning.

Two modes are supported:
  - ``validate(doc, strict=False)`` (default): warnings stay warnings,
    errors stay errors.
  - ``validate(doc, strict=True)``: all warnings are promoted to errors
    so ``verify --strict`` fails on any contract violation.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .ast import CortexDocument, Entry, Section
from .errors import (
    ALLOWED_PRIORITY,
    ALLOWED_SEVERITY,
    ALLOWED_STATUS,
    CANONICAL_SIGILS,
    Diagnostic,
    E003_UNKNOWN_SIGIL,
    E004_UNKNOWN_TYPE,
    E007_ATTRS_POS_CONTRACT_MISSING,
    E008_DUPLICATE_ENTRY,
)
from .document_kind import (
    DocumentKind,
    infer_document_kind,
    validate_level_policy,
)


# Required fields per critical sigil (Section 6 of SKILL.md)
REQUIRED_FIELDS: Dict[str, List[str]] = {
    "FCS":   ["what", "priority", "status", "survive"],
    "OBJ":   ["goal", "status", "success", "survive"],
    "WRK":   ["phase", "current", "blocked", "survive"],
    "STP":   ["action", "reason", "owner", "status", "survive"],
    "CNST":  ["rule", "severity", "survive"],
    "CLAIM": ["statement", "evidence", "status"],
    "LIM":   ["limit", "scope", "status"],
    "RSK":   ["risk", "impact", "mitigation", "status", "survive"],
    "AUD":   ["event", "evidence", "result", "date"],
    "SES":   ["input", "output", "outcome", "date"],
    "LNG":   ["type", "cause", "lesson", "prevention"],
    "KNW":   ["topic", "content", "status"],
}


# Sigils protected from deletion without --force (P0 / blocking severity)
def _is_protected(entry: Entry) -> bool:
    if entry.sigil in ("FCS", "OBJ", "CNST"):
        attrs = entry.value if isinstance(entry.value, dict) else {}
        sev = attrs.get("severity", "")
        if sev == "blocking":
            return True
        if attrs.get("survive") == "min":
            return True
    return False


def is_protected_entry(entry: Entry) -> bool:
    """Public wrapper used by the CRUD layer."""

    return _is_protected(entry)


def validate(
    doc: CortexDocument,
    strict: bool = False,
    kind: Optional[DocumentKind] = None,
) -> List[Dict]:
    """Run all validators and return a list of diagnostic dicts.

    Existing ``doc.diagnostics`` are preserved; new findings are appended.

    Parameters
    ----------
    doc : CortexDocument
        The document to validate.
    strict : bool, default False
        When True, all ``warning`` findings are promoted to ``error``
        severity so that ``verify --strict`` fails on any contract
        violation (audit gap M-02).
    kind : DocumentKind, optional
        Explicit document kind for level-policy checks.  When None, the
        kind is inferred from the document (filename, IDN, sigil
        signature).  Passing an explicit kind overrides inference so
        ``verify --kind package`` actually applies Nivel-3 rules —
        closing re-audit gap H-RA-01.
    """

    findings: List[Dict] = list(doc.diagnostics)

    # 1. Unknown sigils (parser may already have flagged some)
    for sec, entry in doc.iter_entries():
        if entry.sigil in {"GSIG", "GTYP", "GMIC", "GCON"}:
            continue
        if entry.sigil not in doc.glossary.sigils:
            findings.append({
                "code": E003_UNKNOWN_SIGIL,
                "message": f"sigil {entry.sigil!r} (entry {entry.name!r}) not declared in $0",
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "error",
            })
            continue
        sd = doc.glossary.sigils[entry.sigil]
        if sd.type not in doc.glossary.types:
            findings.append({
                "code": E004_UNKNOWN_TYPE,
                "message": f"type {sd.type!r} (sigil {entry.sigil!r}) not declared in $0",
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "error",
            })
        if sd.type == "attrs-pos" and doc.glossary.contract_for(entry.sigil) is None:
            findings.append({
                "code": E007_ATTRS_POS_CONTRACT_MISSING,
                "message": f"attrs-pos sigil {entry.sigil!r} has no positional contract",
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "error",
            })

    # 2. Required fields for critical sigils
    for sec, entry in doc.iter_entries():
        required = REQUIRED_FIELDS.get(entry.sigil)
        if not required:
            continue
        if not isinstance(entry.value, dict):
            findings.append({
                "code": "W001_MISSING_FIELDS",
                "message": f"{entry.sigil}:{entry.name} value is not a dict; cannot check fields",
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "warning",
            })
            continue
        missing = [f for f in required if f not in entry.value]
        if missing:
            findings.append({
                "code": "W001_MISSING_FIELDS",
                "message": f"{entry.sigil}:{entry.name} missing required fields: {missing}",
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "warning",
            })

    # 3. Status / severity / priority allowed values
    for sec, entry in doc.iter_entries():
        if not isinstance(entry.value, dict):
            continue
        status = entry.value.get("status")
        if isinstance(status, str) and status not in ALLOWED_STATUS:
            findings.append({
                "code": "W002_INVALID_STATUS",
                "message": f"{entry.sigil}:{entry.name} status={status!r} not in {sorted(ALLOWED_STATUS)}",
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "warning",
            })
        severity = entry.value.get("severity")
        if isinstance(severity, str) and severity not in ALLOWED_SEVERITY:
            findings.append({
                "code": "W003_INVALID_SEVERITY",
                "message": f"{entry.sigil}:{entry.name} severity={severity!r} not in {sorted(ALLOWED_SEVERITY)}",
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "warning",
            })
        priority = entry.value.get("priority")
        if isinstance(priority, str) and priority not in ALLOWED_PRIORITY:
            findings.append({
                "code": "W004_INVALID_PRIORITY",
                "message": f"{entry.sigil}:{entry.name} priority={priority!r} not in {sorted(ALLOWED_PRIORITY)}",
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "warning",
            })

    # 4. Duplicate entries (same sigil+name) within the same section
    seen: Dict[str, List[str]] = {}
    for sec, entry in doc.iter_entries():
        if entry.sigil in {"GSIG", "GTYP", "GMIC", "GCON"}:
            continue
        key = f"{sec.id}::{entry.sigil}::{entry.name}"
        if key in seen:
            findings.append({
                "code": E008_DUPLICATE_ENTRY,
                "message": f"duplicate entry {entry.sigil}:{entry.name} in {sec.id}",
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "error",
            })
        seen.setdefault(key, []).append(entry.name)

    # 5. Cognitive governance (audit hardening, 1.1.0):
    #    level separation, FCS/OBJ in brain, survive domain, blocking→min,
    #    attrs-pos arity, secret scanning.
    # Re-audit H-RA-01: pass explicit `kind` through so `verify --kind X`
    # actually applies the right level-policy rules.
    findings.extend(validate_level_policy(doc, kind=kind))

    # 6. Strict mode: promote all warnings to errors
    if strict:
        for f in findings:
            if f.get("severity") == "warning":
                f["severity"] = "error"
                f["message"] = f"[strict] {f.get('message', '')}"

    # Deduplicate findings by (code, line, sigil, entry, message)
    seen_keys = set()
    deduped: List[Dict] = []
    for f in findings:
        k = (f.get("code"), f.get("line"), f.get("sigil"),
             f.get("entry"), f.get("message"))
        if k in seen_keys:
            continue
        seen_keys.add(k)
        deduped.append(f)

    return deduped


def is_valid(
    doc: CortexDocument,
    strict: bool = False,
    kind: Optional[DocumentKind] = None,
) -> bool:
    """Return True if the document has no error-severity diagnostics.

    When ``strict=True``, warnings also count as failures.
    """

    for f in validate(doc, strict=strict, kind=kind):
        if f.get("severity") == "error":
            return False
    return True
