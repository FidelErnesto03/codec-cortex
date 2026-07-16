"""Feedback loop for the learning engine (v0.6.0).

CRITICAL CHANGE from v0.5.x:
- Feedback is now an append-only ledger
- Threshold adjustments are computed in-memory, NOT persisted to feedback.json
- To change thresholds, feedback produces a policy patch proposal
- Policy changes require explicit confirmation via CLI
- adaptive=true default is overridden to false in migration

This implements P0-007: Feedback governance.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .policy import LearningPolicySet
from .workspace import Workspace


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FEEDBACK_CACHE_NAME = "feedback.json"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class FeedbackRecord:
    """A single accept/reject decision on a candidate."""

    candidate_id: str
    candidate_type: str       # "SES->LNG", "LNG->KNW", etc.
    sigil_pattern: str        # e.g. "KNW:benchmark_*"
    decision: bool            # True=accepted, False=rejected
    reason: Optional[str] = None
    timestamp: str = ""       # ISO-8601 UTC
    promotion_score: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FeedbackHistory:
    """All recorded feedback, grouped by candidate type."""

    records: List[FeedbackRecord] = field(default_factory=list)
    # CRITICAL: adjusted_thresholds is NOT persisted in v0.6.0
    # It's computed in-memory and used to generate policy patches
    adjusted_thresholds: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "records": [r.to_dict() for r in self.records],
            # Do NOT persist adjusted_thresholds - they're transient
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackHistory":
        records = [FeedbackRecord(**r) for r in data.get("records", [])]
        return cls(
            records=records,
            # Ignore any persisted adjusted_thresholds from old versions
            adjusted_thresholds={},
        )


# ---------------------------------------------------------------------------
# Cache load / save
# ---------------------------------------------------------------------------


def feedback_cache_path(workspace: Workspace) -> Path:
    return workspace.cache_dir / FEEDBACK_CACHE_NAME


def load_feedback_history(workspace: Workspace) -> FeedbackHistory:
    """Load the feedback cache (returns an empty history if absent)."""

    p = feedback_cache_path(workspace)
    if not p.exists():
        return FeedbackHistory()
    try:
        return FeedbackHistory.from_dict(json.loads(p.read_text(encoding="utf-8")))
    except Exception:
        return FeedbackHistory()


def save_feedback_history(workspace: Workspace, history: FeedbackHistory) -> None:
    """Persist the feedback cache to disk."""

    workspace.ensure_dirs()
    p = feedback_cache_path(workspace)
    p.write_text(
        json.dumps(history.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Candidate-type derivation
# ---------------------------------------------------------------------------


def derive_candidate_type(source_sigil: str, target_sigil: str) -> str:
    """Return a canonical ``"SES->LNG"`` style candidate-type string."""

    return f"{source_sigil}->{target_sigil}"


def derive_sigil_pattern(sigil: str, name: str) -> str:
    """Build a glob-style sigil pattern from an entry's sigil+name.

    The pattern strips trailing ``_<digits>`` suffixes so
    ``"SES:policy_externalization_1"`` becomes ``"SES:policy_externalization_*"``.
    """

    base = re.sub(r"_\d+$", "", name)
    if base == name:
        return f"{sigil}:{name}"
    return f"{sigil}:{base}_*"


# ---------------------------------------------------------------------------
# Recording feedback
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record_feedback(
    workspace: Workspace,
    *,
    candidate_id: str,
    candidate_type: str,
    sigil_pattern: str,
    decision: bool,
    reason: Optional[str] = None,
    promotion_score: int = 0,
) -> FeedbackHistory:
    """Record a feedback decision and persist the history.

    Returns the updated :class:`FeedbackHistory`. The caller is
    responsible for calling :func:`adjust_thresholds` afterwards (or
    letting the CLI command do it).
    """

    history = load_feedback_history(workspace)
    rec = FeedbackRecord(
        candidate_id=candidate_id,
        candidate_type=candidate_type,
        sigil_pattern=sigil_pattern,
        decision=decision,
        reason=reason,
        timestamp=_now_iso(),
        promotion_score=promotion_score,
    )
    history.records.append(rec)
    save_feedback_history(workspace, history)
    return history


# ---------------------------------------------------------------------------
# Acceptance stats
# ---------------------------------------------------------------------------


def acceptance_rate(history: FeedbackHistory) -> Dict[str, Dict[str, Any]]:
    """Group records by candidate_type and compute acceptance stats."""

    out: Dict[str, Dict[str, Any]] = {}
    for rec in history.records:
        d = out.setdefault(rec.candidate_type, {
            "total": 0, "accepted": 0, "rejected": 0, "rate": 0.0,
        })
        d["total"] += 1
        if rec.decision:
            d["accepted"] += 1
        else:
            d["rejected"] += 1
    for d in out.values():
        d["rate"] = d["accepted"] / d["total"] if d["total"] else 0.0
    return out


# ---------------------------------------------------------------------------
# Adaptive threshold adjustment
# ---------------------------------------------------------------------------


def adjust_thresholds(
    history: FeedbackHistory,
    ps: LearningPolicySet,
) -> Dict[str, int]:
    """Recompute per-candidate-type adjusted thresholds IN-MEMORY ONLY.

    CRITICAL CHANGE v0.6.0:
    - Thresholds are NOT persisted to feedback.json
    - Results are used to generate policy patch proposals
    - Caller must explicitly apply patches via TransactionService
    
    Strategy (per ``learning-engine-evolution.md`` §D):

    - For each candidate type with >= 3 records:
        - If acceptance_rate > 0.8  → lower the static threshold by 10%
        - If acceptance_rate < 0.3  → raise the static threshold by 20%
        - Otherwise → leave unchanged
    - Clamp to ``[feedback.min_threshold, feedback.max_threshold]``.
    - If ``feedback.adaptive`` is False, return the static defaults
      unchanged.

    The static defaults come from :class:`FibonacciThresholds`:
    ``SES→LNG`` uses ``lng``, ``LNG→KNW`` uses ``knw``, etc.

    Returns the new adjusted-thresholds dict (NOT persisted).
    """

    # CRITICAL: In v0.6.0, adaptive defaults to False for safety
    # Even if ps.feedback.adaptive is True, we require explicit opt-in
    if not ps.feedback.adaptive:
        # Return static defaults - no adjustment
        return {}

    fib = ps.fibonacci_thresholds
    # Map candidate_type → static default threshold
    static_defaults = {
        "SES->LNG": fib.lng,
        "LNG->KNW": fib.knw,
        "WRK->SES": fib.ses,
        "RSK->CNST": fib.auto_knw,
        "NXT->STP": fib.ses,
    }

    stats = acceptance_rate(history)
    adjusted: Dict[str, int] = {}
    for cand_type, stat in stats.items():
        if stat["total"] < 3:
            continue
        default = static_defaults.get(cand_type, fib.lng)
        rate = stat["rate"]
        if rate > 0.8:
            new_t = int(round(default * (1.0 - ps.feedback.adjustment_rate)))
        elif rate < 0.3:
            new_t = int(round(default * (1.0 + ps.feedback.adjustment_rate * 2)))
        else:
            new_t = default
        # Clamp
        new_t = max(ps.feedback.min_threshold, min(ps.feedback.max_threshold, new_t))
        adjusted[cand_type] = new_t

    # Store in-memory only (NOT persisted)
    history.adjusted_thresholds = adjusted
    return adjusted


def create_policy_patch(
    adjusted_thresholds: Dict[str, int],
    ps: LearningPolicySet,
) -> Dict[str, Any]:
    """Create a policy patch proposal from adjusted thresholds.
    
    This is the NEW v0.6.0 way to change thresholds:
    - Compute adjustments in-memory
    - Generate a patch document
    - User reviews and confirms via CLI
    - Patch applied via TransactionService
    
    Returns a dict suitable for creating a policy mutation plan.
    """
    if not adjusted_thresholds:
        return {"action": "none", "reason": "no_adjustments_needed"}
    
    changes = []
    for cand_type, new_threshold in adjusted_thresholds.items():
        # Find current threshold
        fib = ps.fibonacci_thresholds
        current = {
            "SES->LNG": fib.lng,
            "LNG->KNW": fib.knw,
            "WRK->SES": fib.ses,
            "RSK->CNST": fib.auto_knw,
            "NXT->STP": fib.ses,
        }.get(cand_type, fib.lng)
        
        if new_threshold != current:
            changes.append({
                "candidate_type": cand_type,
                "current_threshold": current,
                "new_threshold": new_threshold,
                "change": new_threshold - current,
            })
    
    if not changes:
        return {"action": "none", "reason": "no_effective_changes"}
    
    return {
        "action": "update_thresholds",
        "changes": changes,
        "requires_confirmation": True,
        "reason": "feedback_driven_adjustment",
    }


# ---------------------------------------------------------------------------
# Apply adjusted thresholds to a policy set (in-memory)
# ---------------------------------------------------------------------------


def apply_adjusted_thresholds(
    ps: LearningPolicySet,
    history: FeedbackHistory,
) -> LearningPolicySet:
    """Copy ``history.adjusted_thresholds`` onto ``ps.adjusted_thresholds``.

    Returns ``ps`` (mutated in place) so the caller can chain.
    """

    ps.adjusted_thresholds = dict(history.adjusted_thresholds)
    return ps


__all__ = [
    "FeedbackRecord",
    "FeedbackHistory",
    "FEEDBACK_CACHE_NAME",
    "feedback_cache_path",
    "load_feedback_history",
    "save_feedback_history",
    "derive_candidate_type",
    "derive_sigil_pattern",
    "record_feedback",
    "acceptance_rate",
    "adjust_thresholds",
    "apply_adjusted_thresholds",
]
