"""Pre/post-action handlers for the learning engine (v0.2.0, Fase B).

The engine exposes two entry points that the agent (or any external
runtime) can call around each user interaction:

- :func:`pre_action`  — called BEFORE the agent acts on user input.
  Detects recurrent themes and patterns; if accumulated signals cross
  the configured threshold, the entry is marked for post-action
  evaluation.

- :func:`post_action` — called AFTER the agent has acted. If signals
  accumulated during pre_action cross the candidate threshold, the
  engine emits a candidate notification (the agent should surface this
  to the user).

These functions DO NOT mutate ``brain.cortex``. They only:

- Read the brain + index + policy set.
- Update the in-session signal accumulator (stored in
  ``.cortex/cache/signals.json``).
- Optionally log a ``modify`` event to the session cache (via
  :mod:`cortex.learning.session`).

The actual elevation (mutation) is still gated behind an explicit
``cortex learn elevate`` command.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .errors import LearningError
from .index import LearnIndex, load_or_rebuild
from .policy import LearningPolicySet, parse_policy_document
from .workspace import Workspace


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SIGNALS_CACHE_NAME = "signals.json"


# ---------------------------------------------------------------------------
# Signal accumulator
# ---------------------------------------------------------------------------


@dataclass
class SignalAccumulator:
    """In-session accumulator for theme recurrence signals.

    Keyed by a normalized theme string (lowercased, alnum-only).
    Each value is a list of occurrences (ISO-8601 timestamps).
    """

    themes: Dict[str, List[str]] = field(default_factory=dict)
    pending_candidates: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "themes": {k: list(v) for k, v in self.themes.items()},
            "pending_candidates": list(self.pending_candidates),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SignalAccumulator":
        return cls(
            themes={k: list(v) for k, v in (data.get("themes") or {}).items()},
            pending_candidates=list(data.get("pending_candidates") or []),
        )


# ---------------------------------------------------------------------------
# Cache load / save
# ---------------------------------------------------------------------------


def signals_cache_path(workspace: Workspace) -> Path:
    return workspace.cache_dir / SIGNALS_CACHE_NAME


def load_signals(workspace: Workspace) -> SignalAccumulator:
    p = signals_cache_path(workspace)
    if not p.exists():
        return SignalAccumulator()
    try:
        return SignalAccumulator.from_dict(json.loads(p.read_text(encoding="utf-8")))
    except Exception:
        return SignalAccumulator()


def save_signals(workspace: Workspace, acc: SignalAccumulator) -> None:
    workspace.ensure_dirs()
    p = signals_cache_path(workspace)
    p.write_text(
        json.dumps(acc.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Theme extraction
# ---------------------------------------------------------------------------


def _normalize_theme(text: str) -> str:
    """Lowercase, strip non-alphanumeric, collapse whitespace."""

    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def _extract_themes(text: str, *, max_themes: int = 5) -> List[str]:
    """Extract up to ``max_themes`` candidate theme tokens from ``text``.

    The heuristic is intentionally simple: split on whitespace, drop
    stopwords, drop tokens shorter than 4 chars, return the first
    ``max_themes``. This is good enough for signal accumulation; the
    scoring layer does the heavy lifting.
    """

    STOPWORDS = {
        "the", "and", "for", "with", "that", "this", "from", "have",
        "you", "are", "was", "but", "not", "all", "can", "had", "her",
        "was", "one", "our", "out", "day", "get", "has", "him", "his",
        "how", "its", "may", "more", "new", "now", "old", "see", "way",
        "who", "did", "got", "let", "say", "she", "too", "use",
        "alfred", "fidel",  # proper nouns from the spec example
        "necesito", "que", "los", "las", "del", "por", "para", "con",
        "una", "uno", "como", "pero", "mas", "esto", "esta", "esse",
    }
    tokens = _normalize_theme(text).split()
    out: List[str] = []
    seen = set()
    for t in tokens:
        if len(t) < 4:
            continue
        if t in STOPWORDS:
            continue
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
        if len(out) >= max_themes:
            break
    return out


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# pre_action
# ---------------------------------------------------------------------------


@dataclass
class PreActionReport:
    """Result of :func:`pre_action`."""

    themes_detected: List[str] = field(default_factory=list)
    new_signals: Dict[str, int] = field(default_factory=dict)
    blocked: bool = False
    block_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "themes_detected": list(self.themes_detected),
            "new_signals": dict(self.new_signals),
            "blocked": self.blocked,
            "block_reason": self.block_reason,
        }


def pre_action(
    workspace: Workspace,
    user_input: str,
    *,
    ps: Optional[LearningPolicySet] = None,
) -> PreActionReport:
    """Detect recurrent themes in ``user_input`` and accumulate signals.

    Returns a :class:`PreActionReport`. The accumulator is persisted to
    ``.cortex/cache/signals.json`` so subsequent calls build on it.

    The function NEVER blocks the agent — ``blocked`` is reserved for
    future policy-driven blocking (e.g. "this action requires
    confirmation"). Today it always returns ``blocked=False``.
    """

    if ps is None:
        ps = parse_policy_document(workspace.parse_policy())
    acc = load_signals(workspace)
    themes = _extract_themes(user_input)
    now = _now_iso()
    new_signals: Dict[str, int] = {}
    for theme in themes:
        occurrences = acc.themes.setdefault(theme, [])
        occurrences.append(now)
        new_signals[theme] = len(occurrences)
    save_signals(workspace, acc)
    return PreActionReport(
        themes_detected=themes,
        new_signals=new_signals,
        blocked=False,
        block_reason="",
    )


# ---------------------------------------------------------------------------
# post_action
# ---------------------------------------------------------------------------


@dataclass
class PostActionReport:
    """Result of :func:`post_action`."""

    candidates_above_threshold: List[Dict[str, Any]] = field(default_factory=list)
    brain_modified: bool = False
    notifications: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidates_above_threshold": list(self.candidates_above_threshold),
            "brain_modified": self.brain_modified,
            "notifications": list(self.notifications),
        }


def post_action(
    workspace: Workspace,
    *,
    brain_modified: bool = False,
    ps: Optional[LearningPolicySet] = None,
    idx: Optional[LearnIndex] = None,
) -> PostActionReport:
    """Evaluate accumulated signals against the candidate threshold.

    The function:

    1. Reads the in-session signal accumulator.
    2. Reads (or rebuilds) the learn-index.
    3. For every entry whose ``promotion_score`` >= the configured
       candidate threshold, emits a notification entry.
    4. If ``brain_modified=True``, logs a ``modify`` event to the
       running session (via :mod:`cortex.learning.session`).

    Returns a :class:`PostActionReport`. Does NOT mutate ``brain.cortex``.
    """

    if ps is None:
        ps = parse_policy_document(workspace.parse_policy())
    if idx is None:
        idx = load_or_rebuild(workspace)
    acc = load_signals(workspace)

    threshold = ps.threshold("candidate")  # default 5
    # v0.2.0: use feedback-adjusted threshold when available
    candidate_type_default = "SES->LNG"
    threshold = ps.effective_threshold(candidate_type_default, threshold)

    above: List[Dict[str, Any]] = []
    for selector, rec in idx.entries.items():
        if rec.promotion_score >= threshold and rec.candidate:
            above.append({
                "selector": selector,
                "promotion_score": rec.promotion_score,
                "hotness_score": rec.hotness_score,
                "suggested_action": rec.suggested_action,
            })

    notifications: List[str] = []
    if above:
        first = above[0]
        notifications.append(
            f"Candidate detected: {first['selector']} "
            f"(promotion_score={first['promotion_score']}). "
            f"Consider `cortex learn elevate --candidate {first['selector']}`."
        )

    # If brain was modified, log a session event (best-effort).
    if brain_modified:
        try:
            from .session import session_event
            session_event(workspace, kind="modify", detail="post_action")
        except LearningError:
            # No active session — skip silently.
            pass

    # Clear pending candidates that have been notified
    acc.pending_candidates = [c["selector"] for c in above]
    save_signals(workspace, acc)

    return PostActionReport(
        candidates_above_threshold=above,
        brain_modified=brain_modified,
        notifications=notifications,
    )


__all__ = [
    "SignalAccumulator",
    "PreActionReport",
    "PostActionReport",
    "SIGNALS_CACHE_NAME",
    "signals_cache_path",
    "load_signals",
    "save_signals",
    "pre_action",
    "post_action",
]
