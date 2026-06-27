"""Mutations — add / update / delete / move entries in a :class:`CortexDocument`.

All mutations operate on the AST in memory; persistence (atomic write)
is handled by :mod:`cortex.crud.transactions`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ..core.ast import CortexDocument, Entry, Section, normalize_section_id
from ..core.errors import (
    DuplicateEntryError,
    InvalidValueError,
    NotFoundError,
    ProtectedEntryError,
)
from ..core.parser import build_entry_from_value, parse_attrs_body
from ..core.validator import is_protected_entry
from .selectors import select, select_one, parse_selector


# ---------------------------------------------------------------------------
# Add
# ---------------------------------------------------------------------------

def add_entry(
    doc: CortexDocument,
    section: str,
    sigil: str,
    name: str,
    value: Union[str, Dict[str, Any]],
    *,
    create_section: bool = False,
    allow_duplicate: bool = False,
    allow_unknown_sigil: bool = False,
) -> Entry:
    """Add a new entry to ``doc``.

    ``value`` may be:
      - a dict (used as-is for attrs)
      - a string (parsed as attrs body for attrs, or stored verbatim for
        cuerpo / bloque)

    Re-audit H-RA-06: by default the sigil MUST exist in ``$0``.  If it
    doesn't, :class:`~cortex.core.errors.UnknownSigilError` is raised.
    Pass ``allow_unknown_sigil=True`` (or CLI ``--allow-unknown-sigil``)
    to permit undeclared sigils (recovery/debug scenarios).

    v1.1.5 P0-4: adding operational entries to ``$0`` is rejected.
    ``$0`` is structural metadata only (SKILL.md §4.1); only glossary
    declaration sigils (GSIG/GTYP/GMIC/GCON) are allowed there.
    """

    # Resolve section
    sec_id = normalize_section_id(section)

    # v1.1.5 P0-4: $0 is reserved for glossary declarations, not memory.
    GLOSSARY_ENTRY_SIGILS = frozenset({"GSIG", "GTYP", "GMIC", "GCON"})
    if sec_id == "$0" and sigil not in GLOSSARY_ENTRY_SIGILS:
        from ..core.errors import CortexError
        raise CortexError(
            "E033_ZERO_SECTION_MEMORY_ENTRY",
            f"$0 MUST NOT contain operational entries; refusing to add "
            f"{sigil}:{name} to $0.  $0 is structural metadata only "
            "(SKILL.md §4.1).  Use $1 or later sections for operational memory.",
        )

    target = doc.get_section(sec_id)
    if target is None:
        if not create_section:
            raise NotFoundError(f"section {sec_id}")
        target = doc.get_or_create_section(sec_id)

    # Check for duplicates
    existing = doc.find_entries(sigil=sigil, name=name, section=sec_id)
    if existing and not allow_duplicate:
        raise DuplicateEntryError(sigil, name, section=sec_id)

    # Determine type from glossary
    sigil_def = doc.glossary.sigils.get(sigil)
    if sigil_def is None and not allow_unknown_sigil:
        from ..core.errors import UnknownSigilError
        raise UnknownSigilError(sigil)
    type_ = sigil_def.type if sigil_def else "attrs"

    # Build value
    if isinstance(value, dict):
        v = value
    elif isinstance(value, str):
        if type_ == "attrs":
            try:
                v = parse_attrs_body(value)
            except Exception as e:
                raise InvalidValueError(f"cannot parse attrs body: {e}")
        elif type_ in ("cuerpo", "bloque", "relación"):
            v = value
        else:
            v = value
    else:
        raise InvalidValueError(f"unsupported value type: {type(value).__name__}")

    entry = build_entry_from_value(sec_id, sigil, name, type_, v)
    target.entries.append(entry)
    return entry


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_entry(
    doc: CortexDocument,
    selector: str,
    *,
    set_: Optional[Dict[str, Any]] = None,
    replace_body: Optional[str] = None,
    append: bool = False,
) -> Entry:
    """Update an entry selected by ``selector``.

    For ``attrs`` / ``attrs-pos`` entries, ``set_`` merges key/value
    pairs into the existing dict.  For ``cuerpo`` / ``bloque`` entries,
    ``replace_body`` replaces the body (or appends if ``append=True``).
    """

    entry = select_one(doc, selector)
    if entry.type in ("attrs", "attrs-pos"):
        if set_ is None:
            return entry
        if not isinstance(entry.value, dict):
            entry.value = {}
        for k, v in set_.items():
            entry.value[k] = v
        # Recompute raw + hash
        from ..core.writer import serialize_entry, serialize_entry_value
        body = serialize_entry_value(entry.value, entry.type)
        entry.raw = f"{entry.sigil}:{entry.name}{{{body}}}"
        from ..core.ast import compute_entry_hash
        entry.hash = compute_entry_hash(entry)
        entry.entry_id = entry.hash
        return entry
    elif entry.type in ("cuerpo", "bloque", "relación"):
        if replace_body is None:
            return entry
        if append:
            entry.value = str(entry.value or "") + "\n" + str(replace_body)
        else:
            entry.value = str(replace_body)
        from ..core.writer import serialize_entry_value
        body = serialize_entry_value(entry.value, entry.type)
        entry.raw = f"{entry.sigil}:{entry.name}{{{body}}}"
        from ..core.ast import compute_entry_hash
        entry.hash = compute_entry_hash(entry)
        entry.entry_id = entry.hash
        return entry
    else:
        raise InvalidValueError(f"cannot update entry of type {entry.type!r}")


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_entry(
    doc: CortexDocument,
    selector: str,
    *,
    force: bool = False,
) -> Entry:
    """Delete the entry matching ``selector`` from ``doc``.

    Protected entries (P0 / ``severity:blocking`` / ``survive:min`` on
    FCS, OBJ, CNST) require ``force=True``.
    """

    entry = select_one(doc, selector)
    if is_protected_entry(entry) and not force:
        raise ProtectedEntryError(entry.sigil, entry.name)

    sec = doc.get_section(entry.section)
    if sec is None:
        raise NotFoundError(f"section {entry.section}")
    sec.entries = [e for e in sec.entries if not (
        e.sigil == entry.sigil and e.name == entry.name and e.section == entry.section
    )]
    return entry


# ---------------------------------------------------------------------------
# Move
# ---------------------------------------------------------------------------

def move_entry(
    doc: CortexDocument,
    selector: str,
    to_section: str,
) -> Entry:
    """Move an entry from its current section to ``to_section``."""

    entry = select_one(doc, selector)
    old_sec = doc.get_section(entry.section)
    if old_sec is None:
        raise NotFoundError(f"section {entry.section}")
    new_sec_id = normalize_section_id(to_section)
    new_sec = doc.get_section(new_sec_id)
    if new_sec is None:
        new_sec = doc.get_or_create_section(new_sec_id)
    # Remove from old
    old_sec.entries = [e for e in old_sec.entries if not (
        e.sigil == entry.sigil and e.name == entry.name and e.section == entry.section
    )]
    # Add to new
    entry.section = new_sec_id
    new_sec.entries.append(entry)
    return entry


# ---------------------------------------------------------------------------
# Glossary mutations
# ---------------------------------------------------------------------------

def add_sigil_to_glossary(
    doc: CortexDocument,
    sigil: str,
    name: str,
    type_: str,
    risk: str = "M",
    layer: str = "Semantic",
    description: str = "",
    *,
    force_governance: bool = False,
) -> None:
    """Add a new sigil to ``$0``.

    Refuses to silently REDEFINE a sigil that's already declared in $0.
    Canonical sigils that are not yet declared MAY be added (the user is
    extending a minimal glossary to include canonical sigils they need).
    ``force_governance`` is required only to redefine an existing sigil
    with a different type/contract.
    """

    from ..core.errors import CANONICAL_SIGILS, ProtectedSigilError
    existing = doc.glossary.sigils.get(sigil)
    if existing is not None:
        # Refuse to redefine without explicit governance override
        if not force_governance:
            raise ProtectedSigilError(sigil)
        # With --force-governance, allow replacement if type is unchanged
        if existing.type != type_:
            raise ProtectedSigilError(sigil)
    from ..core.ast import SigilDef
    doc.glossary.add_sigil(SigilDef(
        sigil=sigil, name=name, type=type_, risk=risk,
        layer=layer, description=description,
    ))


def update_sigil_in_glossary(
    doc: CortexDocument,
    sigil: str,
    *,
    description: Optional[str] = None,
    risk: Optional[str] = None,
    layer: Optional[str] = None,
    force_governance: bool = False,
) -> None:
    """Update a sigil's metadata (NOT its type if used)."""

    from ..core.errors import SigilInUseError
    sd = doc.glossary.sigils.get(sigil)
    if sd is None:
        raise NotFoundError(f"sigil {sigil}")
    if description is not None:
        sd.description = description
    if risk is not None:
        sd.risk = risk
    if layer is not None:
        sd.layer = layer


def delete_sigil_from_glossary(
    doc: CortexDocument,
    sigil: str,
    *,
    force: bool = False,
) -> None:
    """Remove a sigil from ``$0``.

    Refuses to remove sigils that are used by entries (unless ``force``).
    """

    from ..core.errors import SigilInUseError
    usage = sum(1 for _, e in doc.iter_entries() if e.sigil == sigil)
    if usage > 0 and not force:
        raise SigilInUseError(sigil, usage)
    doc.glossary.sigils.pop(sigil, None)


# ---------------------------------------------------------------------------
# Micro-token mutations
# ---------------------------------------------------------------------------

def add_micro_to_glossary(
    doc: CortexDocument,
    token: str,
    value: str,
) -> None:
    from ..core.ast import MicroDef
    existing = doc.glossary.micro.get(token)
    if existing is not None and existing.value != value:
        from ..core.errors import CortexError
        raise CortexError(
            "E021_INVALID_VALUE",
            f"micro-token {token!r} already declared with value {existing.value!r}",
        )
    doc.glossary.add_micro(MicroDef(token=token, value=value))


def update_micro_in_glossary(
    doc: CortexDocument,
    token: str,
    value: str,
) -> None:
    existing = doc.glossary.micro.get(token)
    if existing is None:
        from ..core.errors import NotFoundError
        raise NotFoundError(f"micro-token {token}")
    existing.value = value


def delete_micro_from_glossary(
    doc: CortexDocument,
    token: str,
    *,
    force: bool = False,
) -> None:
    from ..glossary.resolver import is_micro_used
    from ..core.errors import MicroInUseError
    all_entries = [e for _, e in doc.iter_entries()]
    if is_micro_used(all_entries, token) and not force:
        raise MicroInUseError(token)
    doc.glossary.micro.pop(token, None)
