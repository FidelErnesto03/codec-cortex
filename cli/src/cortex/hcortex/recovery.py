"""Recovery / migration mode for legacy ``.cortex`` artefacts.

Closes audit gap H-06 / B-006:

  - Tolerates preambles (SPDX headers, Markdown front-matter) before ``$0``.
  - Accepts legacy glossary column ``Expansion`` as an alias for ``Type``.
  - Accepts legacy type name ``contenido`` as an alias for ``cuerpo``.
  - Accepts glossaries that omit the ``Layer`` column.
  - When ``$0`` is missing entirely, reconstructs a minimal ``$0`` from
    the sigils observed in the file and marks every reconstructed sigil
    with an ``RSK`` diagnostic so the user can review before trusting.

The recovery flow is:

    raw text
       │
       ▼
    strip_preamble()        → text without leading SPDX/markdown
       │
       ▼
    parse_cortex()          → AST (with reconstructed $0 if missing)
       │
       ▼
    diagnose_ambiguities()  → list of RSK/AUD diagnostics
       │
       ▼
    write_cortex()          → canonical, conformant .cortex output

Usage from the CLI:

    cortex recover legacy.cortex --out legacy.fixed.cortex
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from ..core.ast import (
    AttrsPosContract,
    CortexDocument,
    Glossary,
    MicroDef,
    Section,
    SigilDef,
    TypeDef,
)
from ..core.errors import (
    CANONICAL_MICRO,
    CANONICAL_TYPES,
    CortexError,
    E030_RECOVERY_INCOMPLETE,
)
from ..core.parser import parse_cortex
from ..core.writer import write_cortex


# ---------------------------------------------------------------------------
# Preamble stripping
# ---------------------------------------------------------------------------

# SPDX header lines: <!-- SPDX-FileCopyrightText: ... -->
_SPDX_RE = re.compile(r"^\s*<!--\s*SPDX-", re.IGNORECASE)
# Markdown front-matter: ---\n...\n---
_FRONTMATTER_DELIM = re.compile(r"^---\s*$")
# HTML comment opening: <!-- ...
_HTML_COMMENT_OPEN = re.compile(r"^\s*<!--")
_HTML_COMMENT_CLOSE = re.compile(r"-->\s*$")
# Markdown headings or horizontal rule before $0
_MD_HEADING_RE = re.compile(r"^#+\s")
_MD_HR_RE = re.compile(r"^(-{3,}|\*{3,}|_{3,})\s*$")


def strip_preamble(text: str) -> Tuple[str, List[str]]:
    """Strip leading non-``.cortex`` content from ``text``.

    Returns ``(clean_text, preamble_lines)`` where ``preamble_lines`` is
    the list of lines that were removed (for traceability — the caller
    may keep them as a comment in the rebuilt file).

    Recognised preamble forms:
      - SPDX comments (``<!-- SPDX-... -->``)
      - Markdown front-matter (``---`` ... ``---``)
      - HTML comments before the first section
      - Markdown headings / horizontal rules
      - Plain prose paragraphs before ``$0``
    """

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    preamble: List[str] = []
    i = 0
    n = len(lines)
    # State for HTML comment / front-matter
    in_html_comment = False
    in_frontmatter = False

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Front-matter handling
        if i == 0 and _FRONTMATTER_DELIM.match(stripped):
            in_frontmatter = True
            preamble.append(line)
            i += 1
            continue
        if in_frontmatter:
            preamble.append(line)
            if _FRONTMATTER_DELIM.match(stripped):
                in_frontmatter = False
            i += 1
            continue

        # HTML comment block
        if _HTML_COMMENT_OPEN.match(line) and not _HTML_COMMENT_CLOSE.search(line):
            in_html_comment = True
            preamble.append(line)
            i += 1
            continue
        if in_html_comment:
            preamble.append(line)
            if _HTML_COMMENT_CLOSE.search(line):
                in_html_comment = False
            i += 1
            continue

        # SPDX single-line comment
        if _SPDX_RE.match(line):
            preamble.append(line)
            i += 1
            continue

        # Empty line inside preamble
        if not stripped:
            preamble.append(line)
            i += 1
            continue

        # Markdown heading or horizontal rule
        if _MD_HEADING_RE.match(line) or _MD_HR_RE.match(line):
            preamble.append(line)
            i += 1
            continue

        # If we hit a section header ($N or $0), stop
        if _is_section_header(stripped):
            break

        # If we hit an entry start (SIGIL:name{), stop
        if _looks_like_entry_start(stripped):
            break

        # Otherwise: treat as prose preamble
        preamble.append(line)
        i += 1

    clean = "\n".join(lines[i:])
    return clean, preamble


def _is_section_header(stripped: str) -> bool:
    if stripped.startswith("$"):
        head = stripped[1:].split(":", 1)[0].split("·", 1)[0].strip()
        return head.isdigit()
    if stripped.startswith("#"):
        inner = stripped.lstrip("#").strip().lstrip("-").strip()
        if inner.startswith("$"):
            head = inner[1:].split(":", 1)[0].split("·", 1)[0].strip()
            return head.isdigit()
    return False


def _looks_like_entry_start(stripped: str) -> bool:
    return bool(re.match(r"^([A-Z][A-Z0-9_]*|!):[A-Za-z_][A-Za-z0-9_]*\s*\{", stripped))


# ---------------------------------------------------------------------------
# Legacy glossary compatibility
# ---------------------------------------------------------------------------

# Legacy column-name aliases (audit gap B-006)
LEGACY_COLUMN_ALIASES = {
    "expansion": "type",       # legacy "Expansion" column → "Type"
    "kind": "type",
    "value": "type",
    "cognitive_layer": "layer",
    "cortex_layer": "layer",
    "description": "description",
    "desc": "description",
    "comment": "description",
}

# Legacy type name aliases (audit gap B-006)
LEGACY_TYPE_ALIASES = {
    "contenido": "cuerpo",
    "body": "cuerpo",
    "text": "cuerpo",
    "code": "bloque",
    "raw": "bloque",
    "block": "bloque",
    "positional": "attrs-pos",
    "pos": "attrs-pos",
    "relation": "relación",
    "rel": "relación",
    "relacion": "relación",
}


def normalise_legacy_type_name(name: str) -> str:
    """Normalise a legacy type name to the canonical form."""

    return LEGACY_TYPE_ALIASES.get(name.lower(), name)


# Legacy declaration regex that accepts EITHER the new 6-column form
# (Sigil | Name | Type | Risk | Layer | Description) or the legacy
# 5-column form (Sigil | Name | Expansion | Risk | Description).
_LEGACY_GLOSSARY_RE = re.compile(
    r"""^\s*\#?\s*
    (?P<sigil>[A-Z][A-Z0-9_]*|!)
    \s*\|\s*
    (?P<name>[A-Za-z_][A-Za-z0-9_]*)
    \s*\|\s*
    (?P<type>[A-Za-z\-]+)
    \s*\|\s*
    (?P<risk>[A-Z])
    (?:\s*\|\s*(?P<layer>[A-Za-z/]+))?
    (?:\s*\|\s*(?P<desc>.+?))?
    \s*$
    """,
    re.VERBOSE,
)


# ---------------------------------------------------------------------------
# Recovery result
# ---------------------------------------------------------------------------

@dataclass
class RecoveryResult:
    """Outcome of :func:`recover_cortex`."""

    doc: CortexDocument
    preamble: List[str] = field(default_factory=list)
    diagnostics: List[dict] = field(default_factory=list)
    reconstructed_glossary: bool = False
    source_text: str = ""

    def to_dict(self) -> dict:
        return {
            "preamble_lines": len(self.preamble),
            "preamble_preview": "\n".join(self.preamble[:10]),
            "diagnostics": self.diagnostics,
            "reconstructed_glossary": self.reconstructed_glossary,
            "sections": [s.id for s in self.doc.sections],
            "sigils": list(self.doc.glossary.sigils.keys()),
        }


# ---------------------------------------------------------------------------
# Main recovery entry point
# ---------------------------------------------------------------------------

def recover_cortex(
    text: str,
    path: str = "<recovery>",
    strict: bool = False,
    embed_aud_rsk: bool = False,
) -> RecoveryResult:
    """Recover a (possibly legacy) ``.cortex`` text into a conforming AST.

    Steps:
      1. Strip preamble (SPDX, front-matter, HTML comments, prose).
      2. Try to parse the remaining text.
      3. If parsing fails because ``$0`` is missing, reconstruct a
         minimal ``$0`` from the observed sigils.
      4. Normalise legacy column names and type aliases.
      5. Emit ``RSK`` diagnostics for every reconstructed sigil.
      6. If ``embed_aud_rsk=True``, insert ``AUD`` and ``RSK`` entries
         into the recovered ``.cortex`` so the artefact itself carries
         the recovery trace (re-audit M-RA-03).
      7. Return a :class:`RecoveryResult` with the rebuilt doc.
    """

    diagnostics: List[dict] = []
    clean_text, preamble = strip_preamble(text)
    if preamble:
        diagnostics.append({
            "code": "I001_PREAMBLE_STRIPPED",
            "message": (
                f"stripped {len(preamble)} preamble line(s) before $0; "
                "preamble is preserved in the result but not interpreted"
            ),
            "severity": "info",
        })

    # Try normal parse first
    doc: Optional[CortexDocument] = None
    try:
        doc = parse_cortex(clean_text, path=path)
        # v1.1.3 P0-1: detect "empty glossary with observable entries" as
        # equivalent to missing-glossary.  The parser accepts files that
        # start directly with entries by creating an implicit empty $0,
        # so we must check post-parse whether $0 is actually populated.
        observed_sigils = {e.sigil for _, e in doc.iter_entries()}
        if not doc.glossary.sigils and observed_sigils:
            diagnostics.append({
                "code": E030_RECOVERY_INCOMPLETE,
                "message": (
                    "file has $0 section but glossary is empty while "
                    f"{len(observed_sigils)} sigil(s) are used in entries; "
                    "attempting reconstruction — review before trusting as memory"
                ),
                "severity": "warning",
            })
            doc = _reconstruct_glossary(clean_text, path)
    except CortexError as e:
        # If it's a missing-glossary error, try to reconstruct $0
        if e.code in ("E001_MISSING_GLOSSARY", "E002_GLOSSARY_NOT_FIRST"):
            diagnostics.append({
                "code": E030_RECOVERY_INCOMPLETE,
                "message": (
                    "file is missing $0 glossary; attempting reconstruction "
                    "from observed sigils — review before trusting as memory"
                ),
                "severity": "warning",
            })
            doc = _reconstruct_glossary(clean_text, path)
        else:
            raise

    # Normalise legacy type names in glossary
    for sigil, sd in list(doc.glossary.sigils.items()):
        new_type = normalise_legacy_type_name(sd.type)
        if new_type != sd.type:
            diagnostics.append({
                "code": "I002_LEGACY_TYPE_ALIAS",
                "message": (
                    f"sigil {sigil}: legacy type {sd.type!r} normalised to "
                    f"canonical {new_type!r}"
                ),
                "sigil": sigil,
                "severity": "info",
            })
            sd.type = new_type

    # Emit RSK for every reconstructed sigil
    if doc.meta.get("reconstructed_glossary"):
        for sigil in doc.meta.get("reconstructed_sigils", []):
            diagnostics.append({
                "code": "W010_RECONSTRUCTED_SIGIL",
                "message": (
                    f"sigil {sigil!r} was reconstructed from usage; "
                    "verify its name/type/risk/layer before trusting"
                ),
                "sigil": sigil,
                "severity": "warning",
            })

    # v1.1.6 P1-4: move operational entries out of $0 even if $0 already
    # existed.  The SKILL says $0 is structural metadata only; if a legacy
    # file has operational entries mixed into $0, recovery must separate
    # them into a proper operational section.
    # v1.1.8 Fix 1: find a truly FREE section by scanning $1, $2, ... $99,
    # $100, ... until we find one that doesn't exist.  Never contaminate
    # an existing section.
    GLOSSARY_ENTRY_SIGILS = frozenset({"GSIG", "GTYP", "GMIC", "GCON"})
    sec0 = doc.get_section("$0")
    moved_live_entries: list = []  # v1.1.8 Fix 2: track for RSK embedding
    if sec0 is not None:
        ops_in_zero = [
            e for e in sec0.entries
            if e.sigil not in GLOSSARY_ENTRY_SIGILS
        ]
        if ops_in_zero:
            # Move operational entries out of $0
            sec0.entries = [
                e for e in sec0.entries
                if e.sigil in GLOSSARY_ENTRY_SIGILS
            ]
            # v1.1.8 Fix 1: find the first truly free section.
            # Scan $1, $2, ..., $99, $100, ... until we find one that doesn't exist.
            recovery_section_id = None
            n = 1
            while True:
                candidate = f"${n}"
                if doc.get_section(candidate) is None:
                    recovery_section_id = candidate
                    break
                n += 1
            recovery_sec = doc.get_or_create_section(
                recovery_section_id, title="RECOVERED CONTENT"
            )
            for e in ops_in_zero:
                e.section = recovery_section_id
                recovery_sec.entries.append(e)
            diagnostics.append({
                "code": "I004_OPS_MOVED_FROM_ZERO",
                "message": (
                    f"moved {len(ops_in_zero)} operational entr(y/ies) from $0 "
                    f"to {recovery_section_id}: RECOVERED CONTENT "
                    "($0 is structural metadata only)"
                ),
                "severity": "info",
            })
            # v1.1.7 P1-5: add RSK when FCS/OBJ/WRK/STP/NXT are moved from $0
            moved_live = [
                e for e in ops_in_zero
                if e.sigil in ("FCS", "OBJ", "WRK", "STP", "NXT")
            ]
            if moved_live:
                moved_live_entries = moved_live  # save for embed
                diagnostics.append({
                    "code": "W011_RECOVERED_LIVE_STATE",
                    "message": (
                        f"{len(moved_live)} live working-state entr(y/ies) "
                        f"({', '.join(e.sigil + ':' + e.name for e in moved_live)}) "
                        "recovered from $0 — verify operational validity before "
                        "trusting as active memory"
                    ),
                    "severity": "warning",
                })

    # v1.1.9: repair an existing but incomplete $0 by auto-declaring
    # observed sigils and canonical types before validation/rendering.
    auto_declared_sigils = _repair_incomplete_glossary(doc, diagnostics)

    # Re-audit M-RA-03: optionally embed AUD/RSK entries in the artefact
    # v1.1.8 Fix 2/3: pass recovery context so AUD describes the real event
    # and RSK is embedded for W011_RECOVERED_LIVE_STATE.
    if embed_aud_rsk and diagnostics:
        recovery_context = {
            "reconstructed_glossary": doc.meta.get("reconstructed_glossary", False),
            "repaired_incomplete_glossary": doc.meta.get("repaired_incomplete_glossary", False),
            "auto_declared_sigils": list(doc.meta.get("auto_declared_sigils", [])),
            "auto_declared_types": list(doc.meta.get("auto_declared_types", [])),
            "moved_live_entries": moved_live_entries,
        }
        _embed_recovery_trace(doc, diagnostics, preamble, recovery_context)

    result = RecoveryResult(
        doc=doc,
        preamble=preamble,
        diagnostics=diagnostics,
        reconstructed_glossary=bool(doc.meta.get("reconstructed_glossary")),
        source_text=text,
    )
    return result


def _canonical_sigil_lookup() -> dict:
    """Build canonical sigil lookup with brain > skill > package priority."""
    from ..glossary.minimal import brain_sigils, skill_sigils, package_sigils
    canonical_lookup = {}
    for source in (package_sigils(), skill_sigils(), brain_sigils()):
        for sd in source:
            canonical_lookup[sd.sigil] = sd
    return canonical_lookup


def _ensure_canonical_types_and_micro(doc: CortexDocument, diagnostics: List[dict]) -> list:
    """Ensure canonical types and micro-tokens exist in the glossary."""
    from ..core.errors import CANONICAL_TYPES, CANONICAL_MICRO
    from ..core.ast import TypeDef, MicroDef
    added_types = []
    for t in CANONICAL_TYPES:
        if t not in doc.glossary.types:
            doc.glossary.add_type(TypeDef(name=t, description="canonical type"))
            added_types.append(t)
    for tok, val in CANONICAL_MICRO.items():
        if tok not in doc.glossary.micro:
            doc.glossary.add_micro(MicroDef(token=tok, value=val))
    return added_types


def _repair_incomplete_glossary(doc: CortexDocument, diagnostics: List[dict]) -> list:
    """Auto-declare observed sigils missing from an existing $0.

    v1.1.9: Missing local declarations are a recoverable $0 incompleteness
    case, not a runtime permission to keep E003_UNKNOWN_SIGIL.
    """

    added_types = _ensure_canonical_types_and_micro(doc, diagnostics)
    canonical_lookup = _canonical_sigil_lookup()

    observed_sigils: list = []
    seen: set = set()
    for _sec, entry in doc.iter_entries():
        if entry.sigil in {"GSIG", "GTYP", "GMIC", "GCON"}:
            continue
        if entry.sigil not in seen:
            seen.add(entry.sigil)
            observed_sigils.append(entry.sigil)

    repaired: list = []
    noncanonical: list = list(doc.meta.get("reconstructed_sigils", []))
    for sig in observed_sigils:
        if sig in doc.glossary.sigils:
            continue
        if sig in canonical_lookup:
            doc.glossary.add_sigil(canonical_lookup[sig])
        else:
            from ..core.ast import SigilDef
            doc.glossary.add_sigil(SigilDef(
                sigil=sig,
                name=sig.lower(),
                type="attrs",
                risk="M",
                layer="Semantic",
                description="auto-declared while repairing incomplete $0 (was: unknown)",
            ))
            if sig not in noncanonical:
                noncanonical.append(sig)
        repaired.append(sig)
        diagnostics.append({
            "code": "W012_INCOMPLETE_GLOSSARY_REPAIRED",
            "message": (
                f"sigil {sig!r} was used by entries but missing from $0; "
                "auto-declared during recovery — verify local contract before trusting"
            ),
            "sigil": sig,
            "severity": "warning",
        })

    if repaired or added_types:
        doc.meta["repaired_incomplete_glossary"] = True
        doc.meta["auto_declared_sigils"] = repaired
        doc.meta["auto_declared_types"] = added_types
        doc.meta["reconstructed_sigils"] = noncanonical

    return repaired


def _first_free_recovery_section_id(doc: CortexDocument) -> str:
    """Return a section id guaranteed not to exist in ``doc``.

    v1.1.8 Fix 1 / v1.1.9 Fix 3: Scan until the first free positive integer
    id; no artificial ceiling.
    """

    n = 1
    while True:
        candidate = f"${n}"
        if doc.get_section(candidate) is None:
            return candidate
        n += 1


def _embed_recovery_trace(
    doc: CortexDocument,
    diagnostics: List[dict],
    preamble: List[str],
    recovery_context: Optional[dict] = None,
) -> None:
    """Insert AUD and RSK entries into ``doc`` carrying the recovery trace.

    v1.1.8 Fix 2: embed RSK for W011_RECOVERED_LIVE_STATE (moved live state).
    v1.1.8 Fix 3: AUD describes the real event, not always glossary_reconstruction.
    v1.1.9: embed RSK/RSK for incomplete_glossary_repair.
    """

    from ..core.parser import build_entry_from_value
    from ..core.ast import SigilDef

    if recovery_context is None:
        recovery_context = {}

    # v1.1.2/v1.1.9: ensure AUD and RSK are declared in $0 before adding entries
    canonical_lookup = _canonical_sigil_lookup()
    for required in ("AUD", "RSK"):
        if required not in doc.glossary.sigils:
            sd = canonical_lookup.get(required) or SigilDef(
                sigil=required,
                name=required.lower(),
                type="attrs",
                risk="M",
                layer="Prefrontal",
                description=f"{required} entry (auto-declared by recovery)",
            )
            doc.glossary.add_sigil(sd)
            diagnostics.append({
                "code": "I003_SIGIL_AUTO_DECLARED",
                "message": (
                    f"sigil {required!r} auto-declared in $0 to support "
                    f"embedded recovery trace"
                ),
                "sigil": required,
                "severity": "info",
            })

    # v1.1.8 Fix 3: AUD describes the real event(s)
    reconstructed = recovery_context.get("reconstructed_glossary", False)
    repaired_incomplete = recovery_context.get("repaired_incomplete_glossary", False)
    auto_declared = list(recovery_context.get("auto_declared_sigils", []))
    auto_declared_types = list(recovery_context.get("auto_declared_types", []))
    moved_live = recovery_context.get("moved_live_entries", [])

    events = []
    if reconstructed:
        events.append("glossary_reconstruction")
    if repaired_incomplete:
        events.append("incomplete_glossary_repair")
    if moved_live:
        events.append("live_state_recovered_from_zero")
    if not events:
        events.append("recovery_processing")
    event_str = "+".join(events)

    result_parts = []
    if reconstructed:
        result_parts.append("reconstructed $0 from observed sigils")
    if repaired_incomplete:
        sigs = ", ".join(auto_declared) if auto_declared else "no missing sigils"
        types = ", ".join(auto_declared_types) if auto_declared_types else "no missing types"
        result_parts.append(f"repaired incomplete $0 by auto-declaring sigils: {sigs}; types: {types}")
    if moved_live:
        sigs = ", ".join(f"{e.sigil}:{e.name}" for e in moved_live)
        result_parts.append(f"moved {len(moved_live)} live-state entr(y/ies) from $0 ({sigs})")
    if not result_parts:
        result_parts.append("recovery trace embedded")
    result_str = "; ".join(result_parts)

    # AUD entry
    aud_sec = doc.get_or_create_section("$8", title="RECOVERY AUDIT")
    aud_sec.entries.append(build_entry_from_value(
        "$8", "AUD", "recovery", "attrs",
        {
            "event": event_str,
            "evidence": f"{len(diagnostics)} diagnostic(s) emitted",
            "result": result_str,
            "date": "1970-01-01",
        },
    ))

    # v1.1.4 P1-6: general RSK when $0 was reconstructed
    if reconstructed:
        rsk_sec = doc.get_or_create_section("$5", title="RECOVERY RISKS")
        rsk_sec.entries.append(build_entry_from_value(
            "$5", "RSK", "reconstructed_glossary", "attrs",
            {
                "risk": "$0 glossary was missing and reconstructed from observed sigils; canonical metadata may not match original intent",
                "impact": "medium",
                "mitigation": "review $0 declarations and verify each sigil's name/type/risk/layer before trusting as memory",
                "status": "current",
                "survive": "work",
            },
        ))
        for sig in doc.meta.get("reconstructed_sigils", []):
            rsk_sec.entries.append(build_entry_from_value(
                "$5", "RSK", f"reconstructed_{sig.lower()}", "attrs",
                {
                    "risk": f"sigil {sig!r} was reconstructed from usage without canonical metadata",
                    "impact": "medium",
                    "mitigation": "verify name/type/risk/layer before trusting as memory",
                    "status": "current",
                    "survive": "work",
                },
            ))

    # v1.1.9: embed RSK when an existing but incomplete $0 was repaired
    if repaired_incomplete:
        rsk_sec = doc.get_or_create_section("$5", title="RECOVERY RISKS")
        rsk_sec.entries.append(build_entry_from_value(
            "$5", "RSK", "incomplete_glossary_repaired", "attrs",
            {
                "risk": "existing $0 glossary was incomplete and was auto-repaired from observed entry sigils",
                "impact": "medium",
                "mitigation": "review auto-declared sigils and confirm their name/type/risk/layer before trusting as memory",
                "status": "current",
                "survive": "work",
            },
        ))
        for sig in auto_declared:
            rsk_sec.entries.append(build_entry_from_value(
                "$5", "RSK", f"auto_declared_{sig.lower()}", "attrs",
                {
                    "risk": f"sigil {sig!r} was used by entries but missing from $0; recovery auto-declared it",
                    "impact": "medium",
                    "mitigation": f"verify {sig!r} local contract before trusting recovered content",
                    "status": "current",
                    "survive": "work",
                },
            ))

    # v1.1.8 Fix 2: embed RSK for W011_RECOVERED_LIVE_STATE
    if moved_live:
        rsk_sec = doc.get_or_create_section("$5", title="RECOVERY RISKS")
        for e in moved_live:
            rsk_sec.entries.append(build_entry_from_value(
                "$5", "RSK", f"recovered_live_{e.sigil.lower()}_{e.name.lower()}", "attrs",
                {
                    "risk": f"{e.sigil}:{e.name} was recovered from $0 (structural metadata section) — operational validity unverified",
                    "impact": "high",
                    "mitigation": f"verify {e.sigil}:{e.name} represents valid operational state before trusting as active memory",
                    "status": "current",
                    "survive": "work",
                },
            ))


def _reconstruct_glossary(text: str, path: str) -> CortexDocument:
    """Build a minimal ``$0`` from the sigils used in ``text``.

    The reconstruction:
      - Scans for entry starts (``SIGIL:name{...``) in the text.
      - For each unique sigil, registers a SigilDef with reasonable
        defaults: type=attrs, risk=M, layer=Semantic.
      - If the sigil is canonical, uses the canonical metadata.
        Re-audit M-RA-04: prefer ``brain_sigils()`` definitions over
        ``package_sigils()`` for shared sigils (e.g. IDN) so that
        ``IDN:agent`` doesn't inherit "Package identity" description.
      - Builds a synthetic ``$0`` section with comment-form declarations.
      - Re-parses the resulting text with the parser.
    """

    # Find all entry starts
    sigils_seen: List[str] = []
    seen_set = set()
    for m in re.finditer(r"(?:^|\n)\s*([A-Z][A-Z0-9_]*|!):[A-Za-z_][A-Za-z0-9_]*\s*\{", text):
        sig = m.group(1)
        if sig not in seen_set:
            seen_set.add(sig)
            sigils_seen.append(sig)

    # Build minimal glossary
    from ..core.errors import CANONICAL_SIGILS  # local import to avoid cycle
    # Re-audit M-RA-04: build canonical lookup with explicit priority
    # (brain > skill > package) so shared sigils like IDN get the most
    # generic (brain-flavoured) description rather than the package one.
    from ..glossary.minimal import brain_sigils, skill_sigils, package_sigils
    canonical_lookup = {}
    # Insert in reverse priority so higher-priority overrides lower
    for source in (package_sigils(), skill_sigils(), brain_sigils()):
        for sd in source:
            canonical_lookup[sd.sigil] = sd

    g = Glossary()
    for t in CANONICAL_TYPES:
        g.add_type(TypeDef(name=t, description="canonical type"))
    for tok, val in CANONICAL_MICRO.items():
        g.add_micro(MicroDef(token=tok, value=val))
    reconstructed_sigils: List[str] = []
    for sig in sigils_seen:
        if sig in canonical_lookup:
            g.add_sigil(canonical_lookup[sig])
        else:
            g.add_sigil(SigilDef(
                sigil=sig,
                name=sig.lower(),
                type="attrs",
                risk="M",
                layer="Semantic",
                description=f"reconstructed from usage (was: unknown)",
            ))
            reconstructed_sigils.append(sig)

    # Build a synthetic document: $0 (synthetic) + $1: RECOVERED CONTENT
    # + the original text body.
    # v1.1.5 P0-3: the original text must NOT stay inside $0.  We insert
    # a "$1: RECOVERED CONTENT" section header before the original
    # entries so they land in $1 (operational) instead of $0 (structural).
    # This ensures:
    #   - verify --strict passes (no E033_ZERO_SECTION_MEMORY_ENTRY)
    #   - HCORTEX audit shows the recovered entries (it omits $0 by design)
    #   - The recovery procedure is faithful to SKILL.md §4.1.3
    from ..core.writer import serialize_glossary
    glossary_text = serialize_glossary(g)
    # Check if the original text already starts with a section header.
    # If it does, we don't need to add $1 (the entries are already in a
    # proper section).  If it doesn't (entry-first), we add $1.
    stripped_text = text.lstrip()
    if stripped_text.startswith("$") or stripped_text.startswith("#"):
        # Already has a section header; use as-is
        synthetic = f"$0: RECOVERED GLOSSARY\n\n{glossary_text}\n\n{stripped_text}"
    else:
        # Entry-first: wrap original entries in $1: RECOVERED CONTENT
        synthetic = (
            f"$0: RECOVERED GLOSSARY\n\n{glossary_text}\n\n"
            f"$1: RECOVERED CONTENT\n\n{stripped_text}"
        )

    doc = parse_cortex(synthetic, path=path)
    doc.meta["reconstructed_glossary"] = True
    doc.meta["reconstructed_sigils"] = reconstructed_sigils
    return doc
