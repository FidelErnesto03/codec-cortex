"""Candidate detection and explanation.

A *candidate* is a group of one or more index entries that the engine
believes are ready for elevation (e.g. ``SES → LNG`` or ``LNG → KNW``).
Candidates are derived from the index — they are NOT stored
persistently (that would make the index canonical memory, which the
SPEC forbids).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..core.ast import CortexDocument, Entry
from .errors import LE009_CANDIDATE_NOT_FOUND, LearningError
from .index import LearnIndex
from .policy import LearningPolicySet, find_policy, is_protected_by_policy
from .scoring import ScoreRecord


@dataclass
class Candidate:
    """A proposed elevation candidate."""

    candidate_id: str
    source_entries: List[str]
    target: str
    promotion_score: int
    hotness_score: int
    risk_weight: int
    read_priority: str
    suggested_action: str
    policy_match: Optional[str] = None
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "source_entries": list(self.source_entries),
            "target": self.target,
            "promotion_score": self.promotion_score,
            "hotness_score": self.hotness_score,
            "risk_weight": self.risk_weight,
            "read_priority": self.read_priority,
            "suggested_action": self.suggested_action,
            "policy_match": self.policy_match,
            "reason": self.reason,
        }


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

# Elevation target per source sigil (SPEC §7.1)
_DEFAULT_TARGET = {
    "WRK": "SES",
    "SES": "LNG",
    "LNG": "KNW",
    "RSK": "CNST",
    "NXT": "STP",
}


def detect_candidates(
    brain_doc: CortexDocument,
    idx: LearnIndex,
    ps: LearningPolicySet,
    *,
    limit: Optional[int] = None,
) -> List[Candidate]:
    """Return a list of :class:`Candidate` objects, ordered by score.

    The detection groups entries by their cluster key (sigil + topic)
    and emits one candidate per cluster whose ``promotion_score`` ≥
    ``thresholds.candidate`` (5) and whose sigil has a known elevation
    target.
    """

    # Group index records by source sigil + topic-like attribute
    clusters: Dict[str, List[ScoreRecord]] = {}
    cluster_meta: Dict[str, Dict[str, Any]] = {}
    for sec, entry in brain_doc.iter_entries():
        selector = f"{entry.sigil}:{entry.name}"
        rec = idx.entries.get(selector)
        if rec is None:
            continue
        if not rec.candidate:
            continue
        if entry.sigil not in _DEFAULT_TARGET:
            continue
        attrs = entry.value if isinstance(entry.value, dict) else None
        if is_protected_by_policy(ps, entry.sigil, entry.name, attrs=attrs):
            continue
        key = _cluster_key_for(entry)
        clusters.setdefault(key, []).append(rec)
        cluster_meta[key] = {
            "sigil": entry.sigil,
            "target": _DEFAULT_TARGET[entry.sigil],
            "selectors": clusters[key],
        }

    out: List[Candidate] = []
    cand_counter = 0
    for key, recs in clusters.items():
        if not recs:
            continue
        # Aggregate scores: take the max across cluster members
        promotion = max(r.promotion_score for r in recs)
        hotness = max(r.hotness_score for r in recs)
        risk = max(r.risk_weight for r in recs)
        priority = _max_priority([r.read_priority for r in recs])
        action = recs[0].suggested_action
        sigil = cluster_meta[key]["sigil"]
        target = cluster_meta[key]["target"]
        # Try to find a matching policy
        policy_match = None
        for p in ps.policies_for(sigil, target):
            # ``apply`` policies match first, then ``propose``
            if p.action in ("apply", "propose"):
                policy_match = p.id
                break
        cand_counter += 1
        out.append(Candidate(
            candidate_id=f"cand_{cand_counter:03d}",
            source_entries=[r.selector for r in recs],
            target=target,
            promotion_score=promotion,
            hotness_score=hotness,
            risk_weight=risk,
            read_priority=priority,
            suggested_action=action,
            policy_match=policy_match,
            reason=_explain_reason(recs, sigil, target),
        ))
    # Sort: highest promotion_score first, then by hotness
    out.sort(key=lambda c: (-c.promotion_score, -c.hotness_score))
    if limit is not None:
        out = out[:limit]
    return out


def _cluster_key_for(entry: Entry) -> str:
    attrs = entry.value if isinstance(entry.value, dict) else {}
    for key in ("topic", "outcome", "lesson", "risk", "statement"):
        v = attrs.get(key)
        if isinstance(v, str) and v:
            return f"{entry.sigil}:{v}"
    return f"{entry.sigil}:{entry.name}"


def _max_priority(priorities: List[str]) -> str:
    order = ["P0", "P1", "P2", "P3", "P4", "P5"]
    best = "P5"
    for p in priorities:
        if order.index(p) < order.index(best):
            best = p
    return best


def _explain_reason(recs: List[ScoreRecord], sigil: str, target: str) -> str:
    if not recs:
        return ""
    r = recs[0]
    parts = [f"{sigil}→{target}"]
    if "repeated" in r.signals:
        parts.append("repeated")
    if "pattern" in r.signals:
        parts.append("pattern")
    if "user_validated" in r.signals:
        parts.append("user_validated")
    parts.append(f"promotion={r.promotion_score}")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Explanation (single candidate)
# ---------------------------------------------------------------------------


def explain_candidate(
    brain_doc: CortexDocument,
    idx: LearnIndex,
    ps: LearningPolicySet,
    candidates: List[Candidate],
    candidate_id: str,
) -> Dict[str, Any]:
    """Return a detailed explanation dict for a single candidate."""

    for c in candidates:
        if c.candidate_id == candidate_id:
            recs = [idx.entries.get(s) for s in c.source_entries]
            recs = [r for r in recs if r is not None]
            return {
                "candidate": c.to_dict(),
                "entries": [r.to_dict() for r in recs],
                "policy": (
                    find_policy(ps, c.policy_match).__dict__
                    if c.policy_match and find_policy(ps, c.policy_match) else None
                ),
                "thresholds": ps.thresholds.as_signal_weights(),
            }
    raise LearningError(
        LE009_CANDIDATE_NOT_FOUND,
        f"no candidate with id {candidate_id!r}",
    )


__all__ = [
    "Candidate",
    "detect_candidates",
    "explain_candidate",
]
