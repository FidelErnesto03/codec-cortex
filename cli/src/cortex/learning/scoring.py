"""Golden-ratio / Fibonacci scoring for the learning engine.

Implements four derived scores per SPEC §6.1:

- ``hotness_score``    — recurrence, freshness and contextual usage
- ``promotion_score``  — aptness for elevation
- ``risk_weight``      — cost of omitting / degrading the entry
- ``read_priority``    — P0..P5 priority bucket for loading

The algorithm is deterministic and side-effect free. The same
``brain.cortex`` + ``learn-policies.cortex`` + engine version always
yields the same scores.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..core.ast import CortexDocument, Entry
from .policy import LearningPolicySet, Thresholds


# ---------------------------------------------------------------------------
# Fingerprint
# ---------------------------------------------------------------------------


def stable_fingerprint(entry: Entry) -> str:
    """Return a stable content hash for ``entry``.

    The fingerprint is computed over the entry's *canonical* payload
    (sigil + name + parsed value) — not over its raw text — so cosmetic
    formatting changes do not invalidate the fingerprint.  This makes
    the index stable across formatting roundtrips.
    """

    payload = {
        "sigil": entry.sigil,
        "name": entry.name,
        "value": _normalise_value(entry.value),
    }
    blob = repr(payload).encode("utf-8")
    return "sha256:" + hashlib.sha256(blob).hexdigest()


def _normalise_value(v: Any) -> Any:
    """Sort dict keys so equivalent dicts hash identically."""

    if isinstance(v, dict):
        return {k: _normalise_value(v[k]) for k in sorted(v.keys())}
    if isinstance(v, list):
        return [_normalise_value(x) for x in v]
    return v


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------

# Canonical signal names — these are the strings stored in the
# ``signals`` list of each index entry.
SIGNAL_OBSERVED = "observed"
SIGNAL_REPEATED = "repeated"
SIGNAL_PATTERN = "pattern"
SIGNAL_DECISION_RELEVANT = "decision_relevant"
SIGNAL_USER_VALIDATED = "user_validated"
SIGNAL_RISK_PREVENTING = "risk_preventing"
SIGNAL_CRITICAL = "critical"


@dataclass
class SignalSet:
    """Detected signals for a single entry (or a candidate cluster)."""

    signals: List[str] = field(default_factory=list)

    def add(self, name: str) -> None:
        if name not in self.signals:
            self.signals.append(name)

    def has(self, name: str) -> bool:
        return name in self.signals

    def to_list(self) -> List[str]:
        return list(self.signals)


# ---------------------------------------------------------------------------
# Score record
# ---------------------------------------------------------------------------


@dataclass
class ScoreRecord:
    """One entry's scores in the index."""

    entry_id: str
    selector: str
    fingerprint: str
    hotness_score: int = 0
    promotion_score: int = 0
    risk_weight: int = 0
    read_priority: str = "P3"
    candidate: bool = False
    suggested_action: str = "index"
    signals: List[str] = field(default_factory=list)
    hits: int = 1
    # v0.2.0 — last_accessed (ISO-8601 UTC) for decay computation.
    # Stored in the index, NOT in brain.cortex. Updated on every scan.
    last_accessed: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "entry_id": self.entry_id,
            "selector": self.selector,
            "fingerprint": self.fingerprint,
            "hotness_score": self.hotness_score,
            "promotion_score": self.promotion_score,
            "risk_weight": self.risk_weight,
            "read_priority": self.read_priority,
            "candidate": self.candidate,
            "suggested_action": self.suggested_action,
            "signals": list(self.signals),
            "hits": self.hits,
        }
        if self.last_accessed:
            d["last_accessed"] = self.last_accessed
        return d


# ---------------------------------------------------------------------------
# Signal detection
# ---------------------------------------------------------------------------


def detect_signals(
    entry: Entry,
    doc: CortexDocument,
    ps: LearningPolicySet,
    *,
    cluster_hits: int = 1,
) -> SignalSet:
    """Detect signals for ``entry``.

    The detection is fully deterministic and depends only on:

    - the entry's own attributes (e.g. ``user_validated=true``);
    - the entry's sigil (e.g. ``CNST:blocking`` is always critical);
    - how many similar entries (by fingerprint) exist in the brain
      (drives ``repeated`` / ``pattern``);
    - whether the entry's sigil is on the protected list.

    No external services, no clock, no LLM.
    """

    ss = SignalSet()
    ss.add(SIGNAL_OBSERVED)

    attrs = entry.value if isinstance(entry.value, dict) else {}

    # Repeated: more than one entry with the same fingerprint cluster
    if cluster_hits >= 2:
        ss.add(SIGNAL_REPEATED)
    # Pattern: 3+ occurrences of a similar entry (heuristic: same sigil
    # AND same ``topic`` attribute OR same fingerprint).
    if cluster_hits >= 3:
        ss.add(SIGNAL_PATTERN)

    # user_validated attribute
    if attrs.get("user_validated") is True:
        ss.add(SIGNAL_USER_VALIDATED)

    # decision_relevant: known decision-shaping sigils
    if entry.sigil in {"FCS", "OBJ", "STP", "WRK", "NXT"}:
        ss.add(SIGNAL_DECISION_RELEVANT)

    # risk_preventing: sigils that, when present, actively prevent
    # regressions (RSK, LIM, CNST, CLAIM).
    if entry.sigil in {"RSK", "LIM", "CLAIM"}:
        ss.add(SIGNAL_RISK_PREVENTING)

    # critical: protected sigils OR CNST:blocking OR IDN/AXM
    if ps.protected.matches(entry.sigil, entry.name):
        ss.add(SIGNAL_CRITICAL)
    if entry.sigil == "CNST" and attrs.get("severity") == "blocking":
        ss.add(SIGNAL_CRITICAL)

    return ss


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------


def score_hotness(signals: SignalSet, thresholds: Thresholds) -> int:
    """Hotness rewards recurrence and freshness-like signals.

    Additive model: sum of every *non-observed* triggered signal's
    weight, with ``observed`` (1) as the floor. Capped at
    ``thresholds.critical`` (21 by default). This matches the SPEC §17
    example where ``repeated + pattern + user_validated = 13``.
    """

    w = thresholds.as_signal_weights()
    score = 0
    if signals.has(SIGNAL_REPEATED):
        score += w["repeated"]
    if signals.has(SIGNAL_PATTERN):
        score += w["pattern"]
    if signals.has(SIGNAL_USER_VALIDATED):
        score += w["ask_user"]
    if signals.has(SIGNAL_CRITICAL):
        score += w["critical"]
    # Floor: every entry is at least "observed".
    score = max(score, w["observed"])
    return min(score, w["critical"])


def score_promotion(signals: SignalSet, thresholds: Thresholds) -> int:
    """Promotion rewards elevation-readiness (validated, repeated, risky).

    Additive model capped at ``thresholds.critical``. Critical entries
    contribute a small amount (capped at ``candidate``) because they are
    NOT auto-promotion material — they belong in their protected layer.
    """

    w = thresholds.as_signal_weights()
    score = 0
    if signals.has(SIGNAL_REPEATED):
        score += w["repeated"]
    if signals.has(SIGNAL_PATTERN):
        score += w["pattern"]
    if signals.has(SIGNAL_DECISION_RELEVANT):
        score += w["candidate"]
    if signals.has(SIGNAL_USER_VALIDATED):
        score += w["ask_user"]
    if signals.has(SIGNAL_RISK_PREVENTING):
        score += w["strong_candidate"]
    if signals.has(SIGNAL_CRITICAL):
        # Critical entries are NOT auto-promotion material — they
        # belong in their protected layer. Cap their contribution.
        score += w["candidate"]
    score = max(score, w["observed"])
    return min(score, w["critical"])


def score_risk(entry: Entry, signals: SignalSet, thresholds: Thresholds) -> int:
    """Risk weight = cost of omitting / degrading the entry.

    Additive model capped at ``thresholds.critical``.
    """

    w = thresholds.as_signal_weights()
    score = 0
    if signals.has(SIGNAL_DECISION_RELEVANT):
        score += w["candidate"]
    if signals.has(SIGNAL_RISK_PREVENTING):
        score += w["strong_candidate"]
    if signals.has(SIGNAL_CRITICAL):
        score += w["critical"]
    # Sigil-based baseline risk
    if entry.sigil in {"CNST", "CLAIM", "LIM", "IDN", "AXM"}:
        score += w["strong_candidate"]
    score = max(score, w["observed"])
    return min(score, w["critical"])


# ---------------------------------------------------------------------------
# read_priority derivation
# ---------------------------------------------------------------------------


def derive_read_priority(
    entry: Entry,
    hotness: int,
    promotion: int,
    risk: int,
    thresholds: Thresholds,
) -> str:
    """Map (entry, scores) to a P0..P5 priority bucket per SPEC §6.3."""

    attrs = entry.value if isinstance(entry.value, dict) else {}
    # P0 — absolutely critical: blocking constraints, FCS/OBJ primary
    if entry.sigil == "CNST" and attrs.get("severity") == "blocking":
        return "P0"
    if entry.sigil in {"FCS", "OBJ"} and attrs.get("status") == "current":
        return "P0"
    if entry.sigil == "STP" and attrs.get("status") == "current":
        return "P0"
    # P1 — high-priority: critical score, active risk, user-validated
    if risk >= thresholds.critical or hotness >= thresholds.critical:
        return "P1"
    if promotion >= thresholds.strong_candidate:
        return "P1"
    # P2 — strong candidate / active knowledge
    if promotion >= thresholds.ask_user or entry.sigil in {"LNG", "KNW"}:
        return "P2"
    # P3 — useful pattern, not urgent
    if promotion >= thresholds.candidate or hotness >= thresholds.pattern:
        return "P3"
    # P4 — historical / low recurrence
    if hotness >= thresholds.repeated:
        return "P4"
    # P5 — cold archive
    return "P5"


# ---------------------------------------------------------------------------
# Suggested action
# ---------------------------------------------------------------------------


def suggest_action(
    entry: Entry,
    promotion: int,
    risk: int,
    thresholds: Thresholds,
    is_protected: bool,
) -> str:
    """Pick a suggested_action string for the index entry."""

    if is_protected:
        return "protect"
    if entry.sigil == "SES" and promotion >= thresholds.ask_user:
        return "propose_elevation_ses_to_lng"
    if entry.sigil == "LNG" and promotion >= thresholds.strong_candidate:
        return "propose_elevation_lng_to_knw"
    if entry.sigil == "RSK" and risk >= thresholds.strong_candidate:
        return "propose_priority_boost"
    if promotion >= thresholds.candidate:
        return "consider_elevation"
    return "index"


__all__ = [
    "stable_fingerprint",
    "SignalSet",
    "ScoreRecord",
    "detect_signals",
    "score_hotness",
    "score_promotion",
    "score_risk",
    "derive_read_priority",
    "suggest_action",
    "SIGNAL_OBSERVED",
    "SIGNAL_REPEATED",
    "SIGNAL_PATTERN",
    "SIGNAL_DECISION_RELEVANT",
    "SIGNAL_USER_VALIDATED",
    "SIGNAL_RISK_PREVENTING",
    "SIGNAL_CRITICAL",
]
