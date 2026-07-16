"""Decay / cooling for the learning engine (v0.2.0, Fase C).

Implements the exponential cooling model described in
``learning-engine-evolution.md`` §C:

    cooling_factor(days) = 0.5 ** (days / half_life_days)

Rules:

- Entries with ``survive:"min"`` NEVER decay.
- Entries with ``survive:"recovery"`` decay at HALF speed
  (i.e. ``days`` is divided by 2 before computing the factor).
- Entries matching a protected pattern in ``learn-policies.cortex``
  NEVER decay.
- Entries whose cooled ``promotion_score`` falls below
  ``cooling.min_score_to_survive`` are dropped from the index.

The decay operation runs at ``session close`` time. It mutates the
*index* (a derived cache) — never ``brain.cortex``. The brain retains
all canonical entries; decay only affects which entries the engine
considers "hot" for the next session.

Tracking ``last_accessed`` per entry:

- The index stores ``last_accessed`` as an ISO-8601 UTC string.
- On every ``learn scan``, every entry in the index is touched (i.e.
  ``last_accessed`` is updated to the current UTC time).
- On ``session start``, the entry corresponding to ``SES:current``
  is touched.
- On ``session close``, ``apply_decay_to_index`` runs: for every entry
  whose ``last_accessed`` is older than the configured half-life, the
  cooling factor is applied.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from ..core.ast import Entry
from .index import LearnIndex
from .policy import LearningPolicySet
from .scoring import ScoreRecord


# ---------------------------------------------------------------------------
# Cooling factor
# ---------------------------------------------------------------------------


def cooling_factor(days_since_last_access: float, *, half_life_days: int = 7) -> float:
    """Exponential cooling factor: ``0.5 ** (days / half_life)``.

    - 0 days  → 1.0 (no decay)
    - 7 days  → 0.5 (half-life, default)
    - 14 days → 0.25
    - 21 days → 0.125
    - 30 days → ~0.05
    """

    if days_since_last_access <= 0:
        return 1.0
    if half_life_days <= 0:
        return 1.0
    return 0.5 ** (days_since_last_access / half_life_days)


# ---------------------------------------------------------------------------
# Survive rules
# ---------------------------------------------------------------------------


def _entry_survive_value(entry: Entry) -> str:
    """Return the ``survive`` attribute of ``entry`` (or empty string)."""

    if isinstance(entry.value, dict):
        v = entry.value.get("survive")
        if isinstance(v, str):
            return v
    return ""


def _entry_decays_at_all(
    entry: Entry,
    ps: LearningPolicySet,
) -> bool:
    """Return True if ``entry`` is subject to decay.

    Entries are exempt from decay when ANY of:

    - ``survive == "min"`` or ``survive == "permanent"``
    - The (sigil, name) matches a protected pattern.
    - The sigil is on the protected-targets list.
    - The sigil is structural (IDN, DOM, FCS, OBJ, STP, CNST, REF) —
      these define the workspace's identity and never cool.
    """

    survive = _entry_survive_value(entry)
    if survive in ("min", "permanent"):
        return False
    if entry.sigil in {"IDN", "DOM", "FCS", "OBJ", "STP", "CNST", "REF"}:
        return False
    if ps.is_protected_pattern(entry.sigil, entry.name):
        return False
    from .policy import is_protected_by_policy
    attrs = entry.value if isinstance(entry.value, dict) else None
    if is_protected_by_policy(ps, entry.sigil, entry.name, attrs=attrs):
        return False
    return True


def _decay_speed_multiplier(entry: Entry) -> float:
    """Return 0.5 for ``survive:"recovery"``, 1.0 otherwise."""

    survive = _entry_survive_value(entry)
    if survive == "recovery":
        return 0.5
    return 1.0


# ---------------------------------------------------------------------------
# Decay report
# ---------------------------------------------------------------------------


@dataclass
class DecayReport:
    """Summary of a decay pass."""

    applied: bool = False
    half_life_days: int = 7
    min_score_to_survive: int = 1
    cooled: List[Dict[str, Any]] = field(default_factory=list)
    dropped: List[str] = field(default_factory=list)
    untouched: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "applied": self.applied,
            "half_life_days": self.half_life_days,
            "min_score_to_survive": self.min_score_to_survive,
            "cooled": list(self.cooled),
            "dropped": list(self.dropped),
            "untouched": self.untouched,
        }


# ---------------------------------------------------------------------------
# Apply decay to an index
# ---------------------------------------------------------------------------


def apply_decay_to_index(
    idx: LearnIndex,
    ps: LearningPolicySet,
    now: datetime,
    *,
    brain_doc=None,
) -> Tuple[LearnIndex, DecayReport]:
    """Apply cooling to every entry in ``idx``.

    Returns a tuple ``(new_index, report)``. The original ``idx`` is
    NOT mutated; a new :class:`LearnIndex` is returned with the cooled
    scores and pruned entries.

    ``brain_doc`` is required to look up each entry's ``survive``
    attribute and verify protected-pattern membership. If omitted, the
    function only uses the policy set (and assumes nothing survives
    ``min``).
    """

    report = DecayReport(
        applied=True,
        half_life_days=ps.cooling.half_life_days,
        min_score_to_survive=ps.cooling.min_score_to_survive,
    )

    # Build a selector → Entry map for survive lookup.
    entry_map: Dict[str, Entry] = {}
    if brain_doc is not None:
        for sec, e in brain_doc.iter_entries():
            entry_map[f"{e.sigil}:{e.name}"] = e

    new_entries: Dict[str, ScoreRecord] = {}
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    now.strftime(fmt)
    for selector, rec in idx.entries.items():
        entry = entry_map.get(selector)
        if entry is not None and not _entry_decays_at_all(entry, ps):
            report.untouched += 1
            new_entries[selector] = rec
            continue

        # Parse last_accessed
        last_accessed_str = ""
        # ScoreRecord doesn't carry last_accessed directly; we store it
        # in the index entries via the ``hits`` field hack? No —
        # v0.2.0 extends ScoreRecord with ``last_accessed``. Let's
        # check if it's there.
        last_accessed_str = getattr(rec, "last_accessed", "") or ""
        if not last_accessed_str:
            # Fall back to the index's brain_hash timestamp? No —
            # if we don't know when the entry was last accessed, we
            # treat it as "just touched" (factor=1.0) so we don't
            # destroy fresh data on the first decay pass.
            report.untouched += 1
            new_entries[selector] = rec
            continue

        try:
            last_dt = datetime.strptime(last_accessed_str, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            report.untouched += 1
            new_entries[selector] = rec
            continue

        days = (now - last_dt).total_seconds() / 86400.0
        # Apply survive:"recovery" speed multiplier
        if entry is not None:
            days = days * _decay_speed_multiplier(entry)
        factor = cooling_factor(days, half_life_days=ps.cooling.half_life_days)

        new_hotness = max(0, int(math.floor(rec.hotness_score * factor)))
        new_promotion = max(0, int(math.floor(rec.promotion_score * factor)))
        new_risk = rec.risk_weight  # risk is NOT decayed — it's a structural property

        if new_promotion < ps.cooling.min_score_to_survive and new_hotness < ps.cooling.min_score_to_survive:
            report.dropped.append(selector)
            continue

        cooled_rec = ScoreRecord(
            entry_id=rec.entry_id,
            selector=rec.selector,
            fingerprint=rec.fingerprint,
            hotness_score=new_hotness,
            promotion_score=new_promotion,
            risk_weight=new_risk,
            read_priority=rec.read_priority,
            candidate=(new_promotion >= ps.threshold("candidate")),
            suggested_action=rec.suggested_action,
            signals=list(rec.signals),
            hits=rec.hits,
        )
        # Preserve last_accessed
        try:
            cooled_rec.last_accessed = last_accessed_str  # type: ignore[attr-defined]
        except Exception:
            pass
        if new_hotness != rec.hotness_score or new_promotion != rec.promotion_score:
            report.cooled.append({
                "selector": selector,
                "hotness": f"{rec.hotness_score}→{new_hotness}",
                "promotion": f"{rec.promotion_score}→{new_promotion}",
                "factor": round(factor, 4),
                "days": round(days, 2),
            })
        new_entries[selector] = cooled_rec

    new_idx = LearnIndex(
        schema_version=idx.schema_version,
        engine_version=idx.engine_version,
        brain_hash=idx.brain_hash,
        policy_hash=idx.policy_hash,
        algorithm=idx.algorithm,
        entries=new_entries,
    )
    return new_idx, report


__all__ = [
    "cooling_factor",
    "DecayReport",
    "apply_decay_to_index",
]
