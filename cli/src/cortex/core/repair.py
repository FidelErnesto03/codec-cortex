"""Auto-repair for brain.cortex files with missing or empty required fields.

Used by ``transactions.atomic_write_cortex`` (auto-repair on write with
``force=True``) and by the CLI ``arqux brain repair`` command.

Goal: allow legacy brains (LNG without ``prevention``, OBJ without
``success``, SES with empty ``output``) to be written when ``force=True``,
without silently discarding structural validation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .errors import E032_CRITICAL_SIGIL_INCOMPLETE, E034_CRITICAL_REQUIRED_FIELD_EMPTY
from .validator import REQUIRED_FIELDS

# Default values for each required field when missing or empty.
# These are semantically neutral — they fill the schema without lying.
FIELD_DEFAULTS: dict[str, str] = {
    "prevention": "not_applicable",
    "success": "pending",
    "output": "pending",
    "cause": "not_specified",
    "survive": "work",
    "status": "active",
    "priority": "medium",
    "goal": "pending",
    "what": "pending",
    "phase": "active",
    "current": "pending",
    "blocked": "no",
    "input": "pending",
    "outcome": "pending",
    "date": "pending",
    "topic": "untitled",
    "content": "pending",
    "type": "note",
    "lesson": "pending",
    "limit": "pending",
    "scope": "project",
    "rule": "pending",
    "risk": "pending",
    "action": "pending",
    "reason": "pending",
    "owner": "auto",
    "statement": "pending",
    "evidence": "pending",
    "event": "pending",
    "result": "pending",
    "mitigation": "pending",
    "severity": "medium",
}


def get_default(field: str) -> str:
    """Return the default for *field*, or ``"pending"`` as fallback."""
    return FIELD_DEFAULTS.get(field, "pending")


def missing_fields(entry: Any) -> List[str]:
    """Return required fields that are absent from *entry.value*."""
    required = REQUIRED_FIELDS.get(entry.sigil)
    if not required or not isinstance(entry.value, dict):
        return []
    return [f for f in required if f not in entry.value]


def empty_fields(entry: Any) -> List[str]:
    """Return required fields that are present but semantically empty."""
    required = REQUIRED_FIELDS.get(entry.sigil)
    if not required or not isinstance(entry.value, dict):
        return []
    return [
        f for f in required
        if f in entry.value and _is_empty(entry.value[f])
    ]


def _is_empty(val: Any) -> bool:
    """True for ``None``, ``""``, or whitespace-only strings."""
    if val is None:
        return True
    if isinstance(val, str) and val.strip() == "":
        return True
    return False


def repair_entry(entry: Any) -> Tuple[bool, Dict[str, str]]:
    """Fill missing / empty required fields in *entry* with defaults.

    Returns ``(changed, changes)`` where *changes* maps field names
    to the default that was applied.
    """
    if not isinstance(entry.value, dict):
        return False, {}

    required = REQUIRED_FIELDS.get(entry.sigil)
    if not required:
        return False, {}

    changes: Dict[str, str] = {}
    for field in required:
        if field not in entry.value:
            default = get_default(field)
            entry.value[field] = default
            changes[field] = default
        elif _is_empty(entry.value[field]):
            default = get_default(field)
            entry.value[field] = default
            changes[field] = default

    return bool(changes), changes


def repair_doc(doc: Any) -> List[Dict[str, Any]]:
    """Scan *doc* and repair all entries with missing/empty required fields.

    Returns a list of repair records (one per modified entry):

    ``{"entry": "LNG:example", "changes": {"prevention": "not_applicable"}}``
    """
    repair_log: List[Dict[str, Any]] = []
    for sec, entry in doc.iter_entries():
        changed, changes = repair_entry(entry)
        if changed:
            repair_log.append({
                "entry": f"{entry.sigil}:{entry.name}",
                "section": sec.id,
                "changes": changes,
            })
    return repair_log


def needs_repair(doc: Any) -> bool:
    """Return True if any entry in *doc* has missing or empty required fields."""
    for sec, entry in doc.iter_entries():
        if missing_fields(entry) or empty_fields(entry):
            return True
    return False


def has_e032_e034(diagnostics: List[Dict[str, Any]]) -> bool:
    """Return True if *diagnostics* contains E032 or E034 errors."""
    for d in diagnostics:
        code = d.get("code", "")
        if code in (E032_CRITICAL_SIGIL_INCOMPLETE, E034_CRITICAL_REQUIRED_FIELD_EMPTY):
            return True
    return False
