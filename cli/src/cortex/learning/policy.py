# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

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
]
