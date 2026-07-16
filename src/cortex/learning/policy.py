"""Learning-policy parser, validator and evaluator.

A *learning policy* is a structured rule stored in
``.cortex/learn-policies.cortex``. The grammar reuses the existing
``.cortex`` parser (so the file is itself a valid CortexDocument) but
the semantic layer is owned by this module.

Policy entry shapes recognised here:

- ``IDN:learn_policies{...}``         — policy file identity
- ``THR:golden_fibonacci{...}``       — numeric thresholds for signals
- ``PRT:critical_sigils{...}``        — protected-target list
- ``POL:<id>{source,target,when,action,requires}`` — a learning policy
- ``GTE:<id>{action, default}``       — a mutation gate

The :class:`LearningPolicySet` aggregates everything in a single
in-memory representation that the scoring and elevation modules use.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core.ast import CortexDocument, Entry
from .conditions import Condition, parse_condition
from .errors import LE004_POLICY_INVALID, LearningError


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class Thresholds:
    """Numeric thresholds (Fibonacci-style by default)."""

    observed: int = 1
    repeated: int = 2
    pattern: int = 3
    candidate: int = 5
    ask_user: int = 8
    strong_candidate: int = 13
    critical: int = 21

    def as_signal_weights(self) -> Dict[str, int]:
        return {
            "observed": self.observed,
            "repeated": self.repeated,
            "pattern": self.pattern,
            "candidate": self.candidate,
            "ask_user": self.ask_user,
            "strong_candidate": self.strong_candidate,
            "critical": self.critical,
        }


@dataclass
class LearningPolicy:
    """A single ``POL:<id>{...}`` rule."""

    id: str
    source: str
    target: Optional[str]
    when: str
    action: str  # score | propose | apply | block
    requires: str
    # Cached parsed condition (lazy, but parsed at load time so failures
    # surface during ``policy validate`` rather than during evaluation).
    condition: Optional[Condition] = None
    # Optional admin flag (treated as ``requires=="admin_policy"``)
    is_admin: bool = False

    def __post_init__(self) -> None:
        if self.condition is None and self.when:
            self.condition = parse_condition(self.when)
        self.is_admin = (self.requires == "admin_policy")

    def evaluate(self, context: Dict[str, Any]) -> bool:
        if self.condition is None:
            return True
        return self.condition.evaluate(context)


@dataclass
class ProtectedTargets:
    """Critical sigils that common policies cannot mutate.

    Each item in ``items`` is either:

    - a bare sigil (e.g. ``"IDN"``) — protects every entry with that sigil;
    - a ``SIGIL:value`` form (e.g. ``"CNST:blocking"``) — protects
      entries whose sigil matches AND whose ``severity`` attribute
      equals ``value``. This is the canonical form for the SPEC §4.3
      ``PRT:critical_sigils`` list.
    """

    items: List[str] = field(default_factory=list)
    mutation_mode: str = "explicit_user_confirmation"

    def matches(self, sigil: str, name: str = "", *, attrs: Optional[dict] = None) -> bool:
        """Return True if (sigil, name, attrs) is protected."""

        for it in self.items:
            if it == sigil:
                return True
            if ":" in it and it.startswith(f"{sigil}:"):
                # Form: SIGIL:value — match severity (or name) against value.
                value = it.split(":", 1)[1]
                if attrs is not None:
                    if attrs.get("severity") == value:
                        return True
                    if attrs.get("status") == value:
                        return True
                # Fall back: match name exactly (less common, but supported)
                if name == value:
                    return True
        return False


@dataclass
class Gate:
    """A ``GTE:<id>{...}`` mutation gate."""

    id: str
    action: str
    default: str  # dry_run_first | block_unless_admin_policy | ...


# ---------------------------------------------------------------------------
# v0.2.0 — Configurable threshold profiles
# ---------------------------------------------------------------------------


@dataclass
class FibonacciThresholds:
    """Per-sigil promotion thresholds (``POL:fibonacci_thresholds{...}``).

    These are *minimum* ``promotion_score`` values required for an entry
    of the given sigil to be considered for elevation to the next layer.
    """

    ses: int = 1
    lng: int = 3
    knw: int = 8
    auto_knw: int = 13

    def to_dict(self) -> Dict[str, Any]:
        return {"ses": self.ses, "lng": self.lng, "knw": self.knw, "auto_knw": self.auto_knw}


@dataclass
class CoolingPolicy:
    """Decay / cooling parameters (``POL:cooling{...}``).

    The cooling factor is ``0.5 ** (days / half_life_days)`` — an
    exponential decay with the given half-life. Entries whose cooled
    ``promotion_score`` falls below ``min_score_to_survive`` are
    dropped from the index.
    """

    half_life_days: int = 7
    min_score_to_survive: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "half_life_days": self.half_life_days,
            "min_score_to_survive": self.min_score_to_survive,
        }


@dataclass
class DetectionPolicy:
    """Candidate-detection tuning (``POL:detection{...}``).

    ``same_sigil_in_window`` is the minimum number of occurrences of the
    same sigil (within ``window_hours``) required to fire the
    ``pattern`` signal. ``cross_session`` controls whether occurrences
    from previous sessions count.
    """

    same_sigil_in_window: int = 3
    window_hours: int = 72
    cross_session: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "same_sigil_in_window": self.same_sigil_in_window,
            "window_hours": self.window_hours,
            "cross_session": self.cross_session,
        }


@dataclass
class FeedbackPolicy:
    """Feedback-loop tuning (``POL:feedback{...}``).

    When ``adaptive`` is true, the engine adjusts per-sigil-type
    thresholds based on acceptance rate. ``adjustment_rate`` is the
    fraction (0..1) by which thresholds move per feedback event.
    Adjusted thresholds are clamped to ``[min_threshold, max_threshold]``.
    """

    adaptive: bool = True
    adjustment_rate: float = 0.1
    min_threshold: int = 1
    max_threshold: int = 20

    def to_dict(self) -> Dict[str, Any]:
        return {
            "adaptive": self.adaptive,
            "adjustment_rate": self.adjustment_rate,
            "min_threshold": self.min_threshold,
            "max_threshold": self.max_threshold,
        }


@dataclass
class ProtectedPatterns:
    """Glob-style protected sigil patterns (``POL:protected_patterns{...}``).

    Each pattern is a sigil-name glob like ``"CNST:*"``, ``"!:*"``,
    ``"FCS:*"``. The engine treats matching entries as protected from
    both elevation and decay.
    """

    patterns: List[str] = field(default_factory=list)

    def matches(self, sigil: str, name: str = "") -> bool:
        import fnmatch
        for pat in self.patterns:
            if ":" in pat:
                psig, pname = pat.split(":", 1)
                if psig != sigil:
                    continue
                if fnmatch.fnmatchcase(name, pname):
                    return True
            else:
                if pat == sigil:
                    return True
        return False


@dataclass
class LearningPolicySet:
    """Aggregated, validated policy view of a ``learn-policies.cortex`` file."""

    identity: Dict[str, Any] = field(default_factory=dict)
    thresholds: Thresholds = field(default_factory=Thresholds)
    protected: ProtectedTargets = field(default_factory=ProtectedTargets)
    policies: List[LearningPolicy] = field(default_factory=list)
    gates: List[Gate] = field(default_factory=list)
    candidate_scan_sigils: List[str] = field(default_factory=list)
    candidate_algorithm: str = "golden_fibonacci_v1"
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)
    # v0.2.0 — configurable threshold profile fields
    fibonacci_thresholds: FibonacciThresholds = field(default_factory=FibonacciThresholds)
    cooling: CoolingPolicy = field(default_factory=CoolingPolicy)
    detection: DetectionPolicy = field(default_factory=DetectionPolicy)
    feedback: FeedbackPolicy = field(default_factory=FeedbackPolicy)
    protected_patterns: ProtectedPatterns = field(default_factory=ProtectedPatterns)
    # v0.2.0 — per-sigil-type adjusted thresholds (feedback-loop product).
    # Maps a candidate-type string like "SES->LNG" to an int threshold.
    adjusted_thresholds: Dict[str, int] = field(default_factory=dict)

    def policies_for(self, source: str, target: Optional[str] = None) -> List[LearningPolicy]:
        out: List[LearningPolicy] = []
        for p in self.policies:
            if source and source not in p.source.split("|"):
                continue
            if target and p.target and target not in p.target.split("|"):
                continue
            out.append(p)
        return out

    def threshold(self, name: str) -> int:
        return getattr(self.thresholds, name, 0)

    # v0.2.0 — convenience accessors

    def effective_threshold(self, candidate_type: str, default: int) -> int:
        """Return the feedback-adjusted threshold for a candidate type,
        falling back to the static ``default`` when no adjustment is
        registered."""

        return self.adjusted_thresholds.get(candidate_type, default)

    def record_adjusted_threshold(self, candidate_type: str, value: int) -> None:
        """Record / overwrite the adjusted threshold for a candidate type."""

        self.adjusted_thresholds[candidate_type] = int(value)

    def is_protected_pattern(self, sigil: str, name: str = "") -> bool:
        """Return True if (sigil, name) matches a protected pattern."""

        return self.protected_patterns.matches(sigil, name)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

_VALID_ACTIONS = {"score", "propose", "apply", "block"}


def parse_policy_document(doc: CortexDocument) -> LearningPolicySet:
    """Build a :class:`LearningPolicySet` from a parsed policy document.

    Raises :class:`LearningError` (LE004) on any structural violation.
    """

    ps = LearningPolicySet()

    # Walk all entries; classify by sigil.
    for sec, entry in doc.iter_entries():
        try:
            if entry.sigil == "IDN":
                _handle_identity(ps, entry)
            elif entry.sigil == "THR":
                _handle_threshold(ps, entry)
            elif entry.sigil == "PRT":
                _handle_protected(ps, entry)
            elif entry.sigil == "POL":
                _handle_policy(ps, entry)
            elif entry.sigil == "GTE":
                _handle_gate(ps, entry)
            else:
                # Ignore unknown sigils silently — the file is also a
                # valid Cortex document so glossary entries etc. will
                # show up here.
                continue
        except LearningError:
            raise
        except Exception as e:
            raise LearningError(
                LE004_POLICY_INVALID,
                f"failed to parse {entry.sigil}:{entry.name}: {e}",
            )
    _validate_policy_set(ps)
    return ps


def _handle_identity(ps: LearningPolicySet, entry: Entry) -> None:
    attrs = entry.value if isinstance(entry.value, dict) else {}
    ps.identity = {
        "name": attrs.get("name", entry.name),
        "version": attrs.get("version", "0.0.0"),
        "target": attrs.get("target", ""),
    }


def _handle_threshold(ps: LearningPolicySet, entry: Entry) -> None:
    attrs = entry.value if isinstance(entry.value, dict) else {}
    # Expect: golden_fibonacci{observed:1, repeated:2, ...}
    # The threshold *name* is the entry.name (e.g. "golden_fibonacci")
    # but we honour the canonical names from SPEC §4.3.
    if entry.name not in ("golden_fibonacci", "fibonacci", "default"):
        # Unknown threshold profile — record but do not override.
        return
    for key in ("observed", "repeated", "pattern", "candidate", "ask_user",
                "strong_candidate", "critical"):
        if key in attrs and isinstance(attrs[key], int):
            setattr(ps.thresholds, key, attrs[key])


def _handle_protected(ps: LearningPolicySet, entry: Entry) -> None:
    attrs = entry.value if isinstance(entry.value, dict) else {}
    items = attrs.get("items", "")
    if isinstance(items, str):
        ps.protected.items = [s.strip() for s in items.split("|") if s.strip()]
    elif isinstance(items, list):
        ps.protected.items = [str(s).strip() for s in items if str(s).strip()]
    if "mutation" in attrs:
        ps.protected.mutation_mode = str(attrs["mutation"])


def _handle_policy(ps: LearningPolicySet, entry: Entry) -> None:
    attrs = entry.value if isinstance(entry.value, dict) else {}

    # v0.2.0 — handle configuration-style policy entries that do NOT
    # follow the elevation-policy schema (no source/target/when). These
    # are configuration blocks, not elevation rules.
    if entry.name == "fibonacci_thresholds":
        ps.fibonacci_thresholds = FibonacciThresholds(
            ses=int(attrs.get("ses", 1)),
            lng=int(attrs.get("lng", 3)),
            knw=int(attrs.get("knw", 8)),
            auto_knw=int(attrs.get("auto_knw", 13)),
        )
        return
    if entry.name == "cooling":
        ps.cooling = CoolingPolicy(
            half_life_days=int(attrs.get("half_life_days", 7)),
            min_score_to_survive=int(attrs.get("min_score_to_survive", 1)),
        )
        return
    if entry.name == "detection":
        ps.detection = DetectionPolicy(
            same_sigil_in_window=int(attrs.get("same_sigil_in_window", 3)),
            window_hours=int(attrs.get("window_hours", 72)),
            cross_session=bool(attrs.get("cross_session", True)),
        )
        return
    if entry.name == "feedback":
        ps.feedback = FeedbackPolicy(
            adaptive=bool(attrs.get("adaptive", True)),
            adjustment_rate=float(attrs.get("adjustment_rate", 0.1)),
            min_threshold=int(attrs.get("min_threshold", 1)),
            max_threshold=int(attrs.get("max_threshold", 20)),
        )
        return
    if entry.name == "protected_patterns":
        patterns = attrs.get("patterns", "")
        if isinstance(patterns, str):
            pat_list = [s.strip() for s in patterns.split("|") if s.strip()]
        elif isinstance(patterns, list):
            pat_list = [str(s).strip() for s in patterns if str(s).strip()]
        else:
            pat_list = []
        ps.protected_patterns = ProtectedPatterns(patterns=pat_list)
        return

    # Standard elevation-policy schema
    action = str(attrs.get("action", "score"))
    if action not in _VALID_ACTIONS:
        raise LearningError(
            LE004_POLICY_INVALID,
            f"policy {entry.name!r}: invalid action {action!r} "
            f"(expected one of {sorted(_VALID_ACTIONS)})",
        )
    p = LearningPolicy(
        id=entry.name,
        source=str(attrs.get("source", "")),
        target=str(attrs.get("target")) if attrs.get("target") else None,
        when=str(attrs.get("when", "")),
        action=action,
        requires=str(attrs.get("requires", "")),
    )
    ps.policies.append(p)
    # Remember the candidate-detection scan list when present.
    if entry.name == "candidate_detection":
        scan = attrs.get("scan_sigils", "")
        if isinstance(scan, str):
            ps.candidate_scan_sigils = [s.strip() for s in scan.split("|") if s.strip()]
        algo = attrs.get("algorithm", "")
        if isinstance(algo, str) and algo:
            ps.candidate_algorithm = algo


def _handle_gate(ps: LearningPolicySet, entry: Entry) -> None:
    attrs = entry.value if isinstance(entry.value, dict) else {}
    ps.gates.append(Gate(
        id=entry.name,
        action=str(attrs.get("action", "")),
        default=str(attrs.get("default", "")),
    ))


def _validate_policy_set(ps: LearningPolicySet) -> None:
    """Sanity-check the parsed policy set (cross-references, etc.)."""

    seen_ids = set()
    for p in ps.policies:
        if p.id in seen_ids:
            raise LearningError(
                LE004_POLICY_INVALID,
                f"duplicate policy id {p.id!r}",
            )
        seen_ids.add(p.id)
        if not p.source:
            raise LearningError(
                LE004_POLICY_INVALID,
                f"policy {p.id!r}: missing 'source'",
            )
    if not ps.protected.items:
        # Default protection list (matches SPEC §4.3 PRT:critical_sigils)
        ps.protected.items = ["IDN", "AXM", "CNST:blocking", "CLAIM", "LIM"]


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def is_protected_by_policy(
    ps: LearningPolicySet,
    sigil: str,
    name: str = "",
    *,
    attrs: Optional[dict] = None,
) -> bool:
    """Return True if (sigil, name, attrs) is protected by the policy set."""

    return ps.protected.matches(sigil, name, attrs=attrs)


def find_policy(ps: LearningPolicySet, policy_id: str) -> Optional[LearningPolicy]:
    for p in ps.policies:
        if p.id == policy_id:
            return p
    return None


__all__ = [
    "Thresholds",
    "LearningPolicy",
    "ProtectedTargets",
    "Gate",
    "LearningPolicySet",
    "parse_policy_document",
    "is_protected_by_policy",
    "find_policy",
    # v0.2.0
    "FibonacciThresholds",
    "CoolingPolicy",
    "DetectionPolicy",
    "FeedbackPolicy",
    "ProtectedPatterns",
]
