"""Rebuildable learning index (``learn-index.json``).

The index is the performance cache for the engine — never canonical
memory.  It is rebuilt from ``brain.cortex`` + ``learn-policies.cortex``
+ engine version and is invalidated whenever any of those change.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.ast import CortexDocument, Entry
from . import ALGORITHM, ENGINE_VERSION, SCHEMA_VERSION
from .policy import LearningPolicySet, is_protected_by_policy
from .scoring import (
    ScoreRecord,
    derive_read_priority,
    detect_signals,
    score_hotness,
    score_promotion,
    score_risk,
    stable_fingerprint,
    suggest_action,
)
from .workspace import Workspace


# ---------------------------------------------------------------------------
# Index dataclass
# ---------------------------------------------------------------------------


@dataclass
class LearnIndex:
    """In-memory representation of ``learn-index.json``."""

    schema_version: str = SCHEMA_VERSION
    engine_version: str = ENGINE_VERSION
    brain_hash: str = ""
    policy_hash: str = ""
    algorithm: str = ALGORITHM
    entries: Dict[str, ScoreRecord] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "engine_version": self.engine_version,
            "brain_hash": self.brain_hash,
            "policy_hash": self.policy_hash,
            "algorithm": self.algorithm,
            "entries": {k: v.to_dict() for k, v in self.entries.items()},
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, sort_keys=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearnIndex":
        entries_data = data.get("entries", {}) or {}
        entries: Dict[str, ScoreRecord] = {}
        for k, v in entries_data.items():
            entries[k] = ScoreRecord(
                entry_id=v.get("entry_id", k),
                selector=v.get("selector", k),
                fingerprint=v.get("fingerprint", ""),
                hotness_score=int(v.get("hotness_score", 0)),
                promotion_score=int(v.get("promotion_score", 0)),
                risk_weight=int(v.get("risk_weight", 0)),
                read_priority=v.get("read_priority", "P3"),
                candidate=bool(v.get("candidate", False)),
                suggested_action=v.get("suggested_action", "index"),
                signals=list(v.get("signals", [])),
                hits=int(v.get("hits", 1)),
                last_accessed=v.get("last_accessed", ""),
            )
        return cls(
            schema_version=data.get("schema_version", SCHEMA_VERSION),
            engine_version=data.get("engine_version", ENGINE_VERSION),
            brain_hash=data.get("brain_hash", ""),
            policy_hash=data.get("policy_hash", ""),
            algorithm=data.get("algorithm", ALGORITHM),
            entries=entries,
        )


# ---------------------------------------------------------------------------
# Load / save
# ---------------------------------------------------------------------------


def load_index(path: Path) -> LearnIndex:
    """Load a learn-index from disk. Raises on malformed JSON."""

    text = Path(path).read_text(encoding="utf-8")
    data = json.loads(text)
    return LearnIndex.from_dict(data)


def save_index(idx: LearnIndex, path: Path) -> None:
    """Write the index to disk atomically."""

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(idx.to_json(), encoding="utf-8")
    tmp.replace(p)


# ---------------------------------------------------------------------------
# Freshness
# ---------------------------------------------------------------------------


def is_stale(
    idx: LearnIndex,
    brain_hash: str,
    policy_hash: str,
    *,
    engine_version: str = ENGINE_VERSION,
    algorithm: str = ALGORITHM,
) -> bool:
    """Return True if the index must be rebuilt."""

    if idx.brain_hash != brain_hash:
        return True
    if idx.policy_hash != policy_hash:
        return True
    if idx.engine_version != engine_version:
        return True
    if idx.algorithm != algorithm:
        return True
    return False


# ---------------------------------------------------------------------------
# Rebuild
# ---------------------------------------------------------------------------


def rebuild_index(
    brain_doc: CortexDocument,
    policy_set: LearningPolicySet,
    brain_hash: str,
    policy_hash: str,
    *,
    engine_version: str = ENGINE_VERSION,
    algorithm: str = ALGORITHM,
    previous_index: Optional[LearnIndex] = None,
    now_iso: Optional[str] = None,
) -> LearnIndex:
    """Rebuild the learn-index from a parsed brain + policy set.

    Implements the pseudocode in SPEC §6.2. Deterministic: same inputs
    always produce the same entries, in the same order.

    v0.2.0: when ``previous_index`` is provided, the rebuilt index
    preserves each entry's ``last_accessed`` timestamp from the
    previous index. New entries get ``last_accessed = now_iso`` (or
    the current UTC time if ``now_iso`` is None).
    """

    # Step 1: collect candidate entries (those the policy allows scanning)
    scan_sigils = set(policy_set.candidate_scan_sigils) or {
        "WRK", "SES", "LNG", "RSK", "NXT", "CLAIM", "LIM",
    }
    candidates: List[Entry] = []
    for sec, entry in brain_doc.iter_entries():
        if entry.sigil in scan_sigils:
            candidates.append(entry)
    # Also include FCS/OBJ/STP/CNST for read-priority indexing even if
    # not on the scan list — they need a priority bucket too.
    for sec, entry in brain_doc.iter_entries():
        if entry.sigil in {"FCS", "OBJ", "STP", "CNST", "IDN", "DOM", "KNW"}:
            if entry not in candidates:
                candidates.append(entry)

    # Step 2: compute cluster hits per fingerprint group
    # (entries with the same sigil + topic/outcome/lesson count as one cluster)
    cluster_map = _compute_cluster_map(candidates)

    # v0.2.0 — fallback "now" timestamp for new entries
    if now_iso is None:
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Step 3: score each entry
    entries: Dict[str, ScoreRecord] = {}
    for entry in candidates:
        fingerprint = stable_fingerprint(entry)
        cluster_hits = cluster_map.get(_cluster_key(entry), 1)
        signals = detect_signals(
            entry, brain_doc, policy_set, cluster_hits=cluster_hits,
        )
        hotness = score_hotness(signals, policy_set.thresholds)
        promotion = score_promotion(signals, policy_set.thresholds)
        risk = score_risk(entry, signals, policy_set.thresholds)
        priority = derive_read_priority(
            entry, hotness, promotion, risk, policy_set.thresholds,
        )
        protected = is_protected_by_policy(policy_set, entry.sigil, entry.name)
        action = suggest_action(
            entry, promotion, risk, policy_set.thresholds, protected,
        )
        candidate_flag = (
            promotion >= policy_set.threshold("candidate") and not protected
        )
        selector = f"{entry.sigil}:{entry.name}"
        # v0.2.0 — preserve last_accessed from previous index, else stamp now
        last_accessed = now_iso
        if previous_index is not None:
            prev_rec = previous_index.entries.get(selector)
            if prev_rec is not None and prev_rec.last_accessed:
                last_accessed = prev_rec.last_accessed
        entries[selector] = ScoreRecord(
            entry_id=selector,
            selector=selector,
            fingerprint=fingerprint,
            hotness_score=hotness,
            promotion_score=promotion,
            risk_weight=risk,
            read_priority=priority,
            candidate=candidate_flag,
            suggested_action=action,
            signals=signals.to_list(),
            hits=cluster_hits,
            last_accessed=last_accessed,
        )

    return LearnIndex(
        schema_version=SCHEMA_VERSION,
        engine_version=engine_version,
        brain_hash=brain_hash,
        policy_hash=policy_hash,
        algorithm=algorithm,
        entries=entries,
    )


def _cluster_key(entry: Entry) -> str:
    """Compute a cluster key for similarity detection.

    Two entries cluster together if they share sigil AND a topic-like
    attribute (``topic``, ``outcome``, ``lesson``, ``risk``). Falls
    back to the entry's full selector when no such attribute exists.
    """

    attrs = entry.value if isinstance(entry.value, dict) else {}
    for key in ("topic", "outcome", "lesson", "risk", "statement"):
        v = attrs.get(key)
        if isinstance(v, str) and v:
            return f"{entry.sigil}:{v}"
    return f"{entry.sigil}:{entry.name}"


def _compute_cluster_map(entries: List[Entry]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for e in entries:
        k = _cluster_key(e)
        out[k] = out.get(k, 0) + 1
    return out


# ---------------------------------------------------------------------------
# Workspace-level convenience
# ---------------------------------------------------------------------------


def rebuild_for_workspace(workspace: Workspace) -> LearnIndex:
    """Rebuild the index for a workspace and persist it to disk.

    v0.2.0: preserves ``last_accessed`` timestamps from any existing
    on-disk index so decay history survives a rebuild.
    """

    brain_doc = workspace.parse_brain()
    policy_doc = workspace.parse_policy()
    from .policy import parse_policy_document
    ps = parse_policy_document(policy_doc)
    brain_hash = workspace.brain_hash()
    policy_hash = workspace.policy_hash()
    previous_index = None
    if workspace.index_path.exists():
        try:
            previous_index = load_index(workspace.index_path)
        except Exception:
            previous_index = None
    idx = rebuild_index(
        brain_doc, ps, brain_hash, policy_hash,
        previous_index=previous_index,
    )
    workspace.ensure_dirs()
    save_index(idx, workspace.index_path)
    return idx


def load_or_rebuild(workspace: Workspace) -> LearnIndex:
    """Load the index if fresh, otherwise rebuild."""

    brain_hash = workspace.brain_hash()
    policy_hash = workspace.policy_hash()
    if workspace.index_path.exists():
        try:
            idx = load_index(workspace.index_path)
            if not is_stale(idx, brain_hash, policy_hash):
                return idx
        except Exception:
            pass
    return rebuild_for_workspace(workspace)


__all__ = [
    "LearnIndex",
    "load_index",
    "save_index",
    "is_stale",
    "rebuild_index",
    "rebuild_for_workspace",
    "load_or_rebuild",
]
