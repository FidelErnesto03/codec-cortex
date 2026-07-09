# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Document kind inference and level-policy validation.

Implements the cognitive governance rules that close the audit gaps:

- B-001 / H-01: `brain.cortex` MUST have `FCS` and `OBJ` active.
- B-002 / H-02: `SKILL.cortex` (Nivel 1) MUST NOT contain live working
  state (`FCS`/`OBJ`/`WRK`/`STP`/`NXT` as actual state, not contract).
- B-009: `survive` attribute MUST be in `{min, recovery, work, full}`.
- Blocking `CNST` MUST have `survive:min` (P0).
- Nivel 3 packages MUST NOT contain live `WRK` state outside recovery mode.

The kind is inferred from:
  1. Explicit `kind` attribute in `IDN:agent`/`IDN:skill`/`IDN:package`
  2. Filename (`brain.cortex`, `SKILL.cortex`, `package.cortex`)
  3. Sigil signature (presence of `FCS`+`OBJ`+`WRK` ⇒ brain;
     presence of `AXM`+`HDL` without `WRK` ⇒ skill;
     presence of `LIM`+`CLAIM` without `WRK` ⇒ package)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .ast import CortexDocument, Entry
from .errors import (
    ALLOWED_SURVIVE,
    E023_LEVEL1_LIVE_STATE,
    E024_LEVEL2_MISSING_FOCUS,
    E025_INVALID_SURVIVE,
    E026_BLOCKING_NOT_P0,
    E027_ATTRS_POS_ARITY,
    E029_LEVEL3_LIVE_STATE,
    E031_SECRET_NOT_BYPASSABLE,
    E032_CRITICAL_SIGIL_INCOMPLETE,
    E033_ZERO_SECTION_MEMORY_ENTRY,
    E034_CRITICAL_REQUIRED_FIELD_EMPTY,
)


# Sigils that constitute "live working state" — forbidden in Nivel 1
# Per SKILL.md Section 7.2 matrix: FCS/OBJ/WRK/STP/NXT are live working
# state; SES/LNG are also forbidden as LIVE state in Nivel 1 (only
# allowed as historical examples with status=specification or
# nature=example).  Re-audit gap H-RA-02: SES/LNG were missing.
LIVE_WORKING_SIGILS = frozenset({"FCS", "OBJ", "WRK", "STP", "NXT"})
LIVE_SESSION_SIGILS = frozenset({"SES", "LNG"})
LIVE_STATE_SIGILS = LIVE_WORKING_SIGILS | LIVE_SESSION_SIGILS

# Sigils forbidden as live state specifically in Nivel 1 (SKILL.cortex).
# Per SKILL.md §7.2: FCS/OBJ/STP only as contract/example; WRK/NXT not
# allowed; SES/LNG only as historical (must be marked).
SKILL_FORBIDDEN_LIVE_SIGILS = LIVE_STATE_SIGILS


@dataclass
class DocumentKind:
    """Inferred kind of a :class:`CortexDocument`."""

    kind: str  # "skill" | "brain" | "package" | "generic"
    source: str  # how it was inferred: "idn_attr" | "filename" | "sigils" | "default"

    def __str__(self) -> str:
        return f"{self.kind} (inferred via {self.source})"


def infer_document_kind(doc: CortexDocument, path: Optional[str] = None) -> DocumentKind:
    """Infer the document kind (skill / brain / package / generic).

    The inference checks, in order of authority:
      1. The ``kind`` attribute of ``IDN:agent``/``IDN:skill``/``IDN:package``
      2. The filename (``brain.cortex``, ``SKILL.cortex``, ``package.cortex``)
      3. The sigil signature
      4. Default: ``generic``
    """

    # 1. IDN attribute
    for sec, entry in doc.iter_entries():
        if entry.sigil != "IDN":
            continue
        if isinstance(entry.value, dict):
            kind_val = entry.value.get("kind")
            if isinstance(kind_val, str) and kind_val in ("skill", "brain", "package"):
                return DocumentKind(kind=kind_val, source="idn_attr")
            # Heuristic: IDN:skill → skill, IDN:agent → brain, IDN:package → package
            if entry.name == "skill":
                return DocumentKind(kind="skill", source="idn_attr")
            if entry.name == "package":
                return DocumentKind(kind="package", source="idn_attr")
            if entry.name == "agent":
                return DocumentKind(kind="brain", source="idn_attr")

    # 2. Filename
    if path:
        import os
        basename = os.path.basename(path).lower()
        if basename == "brain.cortex" or basename.startswith("brain."):
            return DocumentKind(kind="brain", source="filename")
        if basename == "skill.cortex" or basename.startswith("skill."):
            return DocumentKind(kind="skill", source="filename")
        if basename == "package.cortex" or basename.startswith("package."):
            return DocumentKind(kind="package", source="filename")

    # 3. Sigil signature
    sigils_present = {e.sigil for _, e in doc.iter_entries()}
    if "WRK" in sigils_present and "FCS" in sigils_present:
        return DocumentKind(kind="brain", source="sigils")
    if "AXM" in sigils_present and "WRK" not in sigils_present:
        return DocumentKind(kind="skill", source="sigils")
    if "CLAIM" in sigils_present and "LIM" in sigils_present and "WRK" not in sigils_present:
        return DocumentKind(kind="package", source="sigils")

    return DocumentKind(kind="generic", source="default")


# ---------------------------------------------------------------------------
# Level-policy validation
# ---------------------------------------------------------------------------

def _is_field_empty(value) -> bool:
    """Return True if ``value`` is semantically empty.

    v1.1.6: "", "   " (whitespace-only), None are treated as empty.
    v1.1.7: the literal string "null" (case-insensitive) is also treated
    as empty.
    v1.1.8: expanded to cover all common null-like sentinels that a user
    or LLM might write instead of a real value: none, nil, undefined,
    n/a, n.a., na, tbd, todo, tbc, ???, ?, -, --.  These are all
    semantically empty for critical required fields per SKILL.md §6.
    """
    if value is None:
        return True
    if isinstance(value, str):
        stripped = value.strip().lower()
        if stripped == "":
            return True
        # v1.1.8: comprehensive null-like sentinels
        NULL_LIKE = frozenset({
            "null", "none", "nil", "undefined",
            "n/a", "n.a.", "na",
            "tbd", "todo", "tbc",
            "???", "?",
            "-", "--",
        })
        if stripped in NULL_LIKE:
            return True
    return False


def _is_live_entry(entry: Entry) -> bool:
    """Return True if ``entry`` represents live working state (not contract).

    An entry is "live" unless it is explicitly marked as
    ``example``/``template``/``non_operational``/``contract`` via the
    ``nature`` attribute or the entry name.
    """

    if entry.sigil not in LIVE_STATE_SIGILS:
        return False
    if not isinstance(entry.value, dict):
        return True
    nature = entry.value.get("nature", "")
    if isinstance(nature, str) and nature in (
        "example", "template", "non_operational", "contract", "specification",
    ):
        return False
    status = entry.value.get("status", "")
    if status in ("specification", "planned", "future", "deprecated"):
        # Specification entries are not "live" — they're contracts/examples
        return False
    return True


def validate_level_policy(
    doc: CortexDocument,
    kind: Optional[DocumentKind] = None,
) -> List[dict]:
    """Run level-policy rules and return diagnostic dicts.

    The rules implemented (per audit H-01, H-02, B-009, B-002):

      - Nivel 1 (skill): no live ``FCS/OBJ/WRK/STP/NXT`` entries.
      - Nivel 2 (brain): at least one ``FCS`` and one ``OBJ`` entry,
        each with ``status`` in {current, blocked} (v1.1.3: ``done`` is
        a closed state, not active).
      - Nivel 3 (package): no live ``WRK``/``FCS``/``OBJ``/``STP``/``NXT``
        (only historical ``SES``/``LNG`` allowed).
      - ``survive`` attribute must be in {min, recovery, work, full}.
      - ``CNST`` with ``severity:blocking`` MUST have ``survive:min``.
      - ``attrs-pos`` with arity mismatch MUST error.
      - No secrets in clear (API keys, passwords, tokens, etc.).
    """

    if kind is None:
        kind = infer_document_kind(doc, doc.meta.get("path"))

    findings: List[dict] = []
    {e.sigil for _, e in doc.iter_entries()}

    # --- $0 section integrity (v1.1.5 P0-1) ------------------------------
    # $0 is structural metadata, NOT working memory.  Only glossary
    # declaration sigils (GSIG/GTYP/GMIC/GCON) are allowed as entries
    # inside $0.  Any other sigil is operational memory hidden from
    # HCORTEX (which omits $0 by design) — a critical governance breach.
    GLOSSARY_ENTRY_SIGILS = frozenset({"GSIG", "GTYP", "GMIC", "GCON"})
    for sec in doc.sections:
        if sec.id != "$0":
            continue
        for entry in sec.entries:
            if entry.sigil in GLOSSARY_ENTRY_SIGILS:
                continue
            findings.append({
                "code": E033_ZERO_SECTION_MEMORY_ENTRY,
                "message": (
                    f"$0 MUST NOT contain operational entries; found "
                    f"{entry.sigil}:{entry.name} in $0.  $0 is structural "
                    "metadata only (SKILL.md §4.1).  Move operational "
                    "entries to $1 or later sections."
                ),
                "section": "$0",
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "error",
                "bypassable": False,  # v1.1.5 P0-1: non-bypassable
            })

    # --- Nivel 1: skill MUST NOT contain live state ----------------------
    if kind.kind == "skill":
        for sec, entry in doc.iter_entries():
            if sec.id == "$0":
                continue  # v1.1.5 P0-2: $0 is structural; E033 handles $0 entries
            if not _is_live_entry(entry):
                continue
            if entry.sigil in LIVE_STATE_SIGILS:
                findings.append({
                    "code": E023_LEVEL1_LIVE_STATE,
                    "message": (
                        f"Nivel 1 (skill) MUST NOT contain live state "
                        f"sigil {entry.sigil}:{entry.name}; only contracts/examples allowed"
                    ),
                    "line": entry.line_start,
                    "section": sec.id,
                    "sigil": entry.sigil,
                    "entry": entry.name,
                    "severity": "error",
                    "bypassable": False,  # v1.1.4 P0-1: governance invariant
                })

    # --- Nivel 2: brain MUST have FCS and OBJ active ---------------------
    if kind.kind == "brain":
        # v1.1.3 P0-4: `done` is a closed state, NOT an active one.
        # v1.1.5 P0-2: entries under $0 do NOT count — $0 is structural
        # metadata, not working memory.  FCS/OBJ in $0 are invisible to
        # HCORTEX and must not satisfy the operational brain invariant.
        # v1.1.6 P0-3: FCS/OBJ with empty required fields (what:"", goal:"")
        # do NOT count as active — a semantically empty focus/objective
        # is not a real focus/objective.
        active_status = {"current", "blocked"}
        has_fcs = False
        has_obj = False
        for sec, entry in doc.iter_entries():
            if sec.id == "$0":
                continue  # v1.1.5 P0-2: $0 entries don't count as operational
            if entry.sigil == "FCS":
                if not isinstance(entry.value, dict):
                    continue
                status = entry.value.get("status")
                if status not in active_status:
                    continue
                # v1.1.6 P0-3: check that required fields are non-empty
                what = entry.value.get("what")
                if _is_field_empty(what):
                    continue  # empty FCS doesn't count
                has_fcs = True
            elif entry.sigil == "OBJ":
                if not isinstance(entry.value, dict):
                    continue
                status = entry.value.get("status")
                if status not in active_status:
                    continue
                # v1.1.6 P0-3: check that required fields are non-empty
                goal = entry.value.get("goal")
                if _is_field_empty(goal):
                    continue  # empty OBJ doesn't count
                has_obj = True
        if not has_fcs:
            findings.append({
                "code": E024_LEVEL2_MISSING_FOCUS,
                "message": (
                    "Nivel 2 (brain) MUST have at least one active FCS entry "
                    "(status=current|blocked; 'done' is a closed state, not active)"
                ),
                "section": "$2",
                "sigil": "FCS",
                "severity": "error",
                "bypassable": False,  # v1.1.4 P0-1: --force cannot remove operational focus
            })
        if not has_obj:
            findings.append({
                "code": E024_LEVEL2_MISSING_FOCUS,
                "message": (
                    "Nivel 2 (brain) MUST have at least one active OBJ entry "
                    "(status=current|blocked; 'done' is a closed state, not active)"
                ),
                "section": "$2",
                "sigil": "OBJ",
                "severity": "error",
                "bypassable": False,  # v1.1.4 P0-1: --force cannot remove operational objective
            })

    # --- Nivel 3: package MUST NOT contain live state --------------------
    if kind.kind == "package":
        for sec, entry in doc.iter_entries():
            if sec.id == "$0":
                continue  # v1.1.5 P0-2: $0 is structural; E033 handles $0 entries
            if not _is_live_entry(entry):
                continue
            if entry.sigil in LIVE_STATE_SIGILS:
                findings.append({
                    "code": E029_LEVEL3_LIVE_STATE,
                    "message": (
                        f"Nivel 3 (package) MUST NOT contain live state "
                        f"sigil {entry.sigil}:{entry.name}"
                    ),
                    "line": entry.line_start,
                    "section": sec.id,
                    "sigil": entry.sigil,
                    "entry": entry.name,
                    "severity": "error",
                    "bypassable": False,  # v1.1.4 P0-1: governance invariant
                })

    # --- survive attribute validation (all kinds) ------------------------
    for sec, entry in doc.iter_entries():
        if not isinstance(entry.value, dict):
            continue
        survive = entry.value.get("survive")
        if survive is None:
            continue
        if not isinstance(survive, str) or survive not in ALLOWED_SURVIVE:
            findings.append({
                "code": E025_INVALID_SURVIVE,
                "message": (
                    f"{entry.sigil}:{entry.name} survive={survive!r} "
                    f"not in {sorted(ALLOWED_SURVIVE)}"
                ),
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "error",
            })

    # --- blocking protection is independent from retention ---------------
    # ``severity:blocking`` is a non-bypassable security predicate.  It must
    # remain protected even when the document explicitly selects a different
    # retention level; retention is validated above and is not security.
    for sec, entry in doc.iter_entries():
        if entry.sigil != "CNST":
            continue
        if not isinstance(entry.value, dict):
            continue
        severity = entry.value.get("severity")
        survive = entry.value.get("survive")
        if severity == "blocking":
            # Deliberately no E026: ``blocking`` is enforced by the
            # independent protection predicate in validator/profiles.
            continue

    # --- attrs-pos arity check -------------------------------------------
    for sec, entry in doc.iter_entries():
        if entry.type != "attrs-pos":
            continue
        contract = doc.glossary.contract_for(entry.sigil)
        if contract is None:
            continue  # already flagged by E007
        # The body was parsed to a dict using the contract; check raw body
        # for actual positional count by re-parsing raw
        from .parser import _extract_body  # type: ignore
        body = _extract_body(entry.raw)
        parts = [p for p in body.split("|")]
        # Don't count empty trailing
        expected = len(contract.fields)
        if len(parts) > expected:
            findings.append({
                "code": E027_ATTRS_POS_ARITY,
                "message": (
                    f"{entry.sigil}:{entry.name} attrs-pos has {len(parts)} positional "
                    f"values but contract declares {expected} fields "
                    f"({', '.join(contract.fields)}); excess values silently dropped"
                ),
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "error",
            })

    # --- critical sigil completeness (v1.1.3 P0-3) -----------------------
    # Per SKILL.md §6, sigilos críticos tienen campos requeridos obligatorios.
    # v1.1.2 los trataba como warning (W001_MISSING_FIELDS), lo que permitía
    # persistir memoria semánticamente inválida por defecto.  Ahora son
    # errores no-bypassables para los sigilos críticos enumerados abajo.
    from .validator import REQUIRED_FIELDS  # local import to avoid cycle
    from .schema import SchemaResolver
    CRITICAL_SIGILS_WITH_REQUIRED_FIELDS = frozenset(REQUIRED_FIELDS.keys())
    resolver = SchemaResolver(doc.glossary)
    for sec, entry in doc.iter_entries():
        if entry.sigil not in CRITICAL_SIGILS_WITH_REQUIRED_FIELDS:
            continue
        if not isinstance(entry.value, dict):
            continue
        required = (
            resolver.required_fields(entry.sigil)[0]
            if resolver.has_fields(entry.sigil)
            else REQUIRED_FIELDS[entry.sigil]
        )
        missing = [f for f in required if f not in entry.value]
        if missing:
            findings.append({
                "code": E032_CRITICAL_SIGIL_INCOMPLETE,
                "message": (
                    f"{entry.sigil}:{entry.name} missing required fields {missing}; "
                    "critical sigils MUST be complete to persist (SKILL.md §6)"
                ),
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "error",
                "bypassable": False,  # v1.1.3 P0-3: not bypassable with --force
            })
        # v1.1.6 P0-1/P0-2: check for semantically empty fields (E034).
        # A field that exists but is "", "   ", or null is just as bad
        # as a missing field — it produces a formally valid but
        # semantically empty brain.
        empty_fields = [
            f for f in required
            if f in entry.value and _is_field_empty(entry.value[f])
        ]
        if empty_fields:
            findings.append({
                "code": E034_CRITICAL_REQUIRED_FIELD_EMPTY,
                "message": (
                    f"{entry.sigil}:{entry.name} has empty required fields {empty_fields}; "
                    "critical fields MUST have non-empty values (SKILL.md §6). "
                    "A brain with FCS:primary{what:\"\"} is formally valid but "
                    "semantically empty."
                ),
                "line": entry.line_start,
                "section": sec.id,
                "sigil": entry.sigil,
                "entry": entry.name,
                "severity": "error",
                "bypassable": False,  # v1.1.6 P0-1: non-bypassable
            })

    # --- secret scanning --------------------------------------------------
    findings.extend(_scan_for_secrets(doc))

    return findings


# ---------------------------------------------------------------------------
# Secret scanner (M-03)
# ---------------------------------------------------------------------------

# Conservative patterns: catch obvious clear-text secrets without false
# positives on prose.  Each pattern is (regex, label).
import re as _re

_SECRET_PATTERNS: List[tuple] = [
    (_re.compile(r"(?i)\b(api[_-]?key)\b\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}", _re.IGNORECASE), "api_key"),
    (_re.compile(r"(?i)\b(password|passwd|pwd)\b\s*[:=]\s*[\"']?[^\s\"']{4,}", _re.IGNORECASE), "password"),
    (_re.compile(r"(?i)\b(token|secret|bearer)\b\s*[:=]\s*[\"']?[A-Za-z0-9_\-\.]{16,}", _re.IGNORECASE), "token"),
    (_re.compile(r"(?i)\b(aws[_-]?secret[_-]?access[_-]?key)\b\s*[:=]\s*[\"']?[A-Za-z0-9/+=]{40}", _re.IGNORECASE), "aws_secret"),
    (_re.compile(r"(?i)\b(private[_-]?key)\b\s*[:=]\s*[\"']?-----BEGIN"), "private_key"),
    (_re.compile(r"https?://[^/\s]+:[^@/\s]+@"), "url_with_credentials"),
]


def _scan_for_secrets(doc: CortexDocument) -> List[dict]:
    """Scan for secrets in clear text.

    v1.1.3 P0-2: secret findings are tagged ``bypassable=False`` so that
    neither ``--force`` nor ``--no-validate-write`` can override them.
    The SKILL forbids clear-text secrets unconditionally (Section 16.1);
    forensic recovery must use a dedicated explicit flag
    (``--unsafe-allow-secret-forensics``) that lives outside the normal
    mutation path.
    """
    findings: List[dict] = []
    for sec, entry in doc.iter_entries():
        # Check both the value dict and the raw text
        texts_to_check: List[str] = []
        if isinstance(entry.value, dict):
            for k, v in entry.value.items():
                if isinstance(v, str):
                    texts_to_check.append(f"{k}={v}")
        elif isinstance(entry.value, str):
            texts_to_check.append(entry.value)
        texts_to_check.append(entry.raw)
        for text in texts_to_check:
            for pattern, label in _SECRET_PATTERNS:
                if pattern.search(text):
                    findings.append({
                        "code": E031_SECRET_NOT_BYPASSABLE,
                        "message": (
                            f"possible {label} in clear text in {entry.sigil}:{entry.name}; "
                            "use REF:secret{provider:..., key:...} instead — "
                            "this error is NOT bypassable with --force"
                        ),
                        "line": entry.line_start,
                        "section": sec.id,
                        "sigil": entry.sigil,
                        "entry": entry.name,
                        "severity": "error",
                        "bypassable": False,  # v1.1.3 P0-2
                    })
                    break  # one hit per entry is enough
            else:
                continue
            break
    return findings
