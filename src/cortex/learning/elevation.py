"""Elevation planner: propose, dry-run and apply patches to ``brain.cortex``.

Elevations are the only path through which the learning engine mutates
``brain.cortex``.  Every elevation MUST go through:

1.  :func:`plan_patch` — produce a :class:`Patch` describing the change
2.  :func:`render_diff` — turn the patch into a human-readable diff
3.  :func:`apply_patch` — write the new brain to disk (only when the
    caller explicitly passes ``mode="apply"``; ``"dry-run"`` is the
    default and produces NO filesystem change)
4.  :func:`verify_post_apply` — re-parse the brain and rebuild the
    index to confirm the mutation is sound

Critical-sigil protection is enforced inside :func:`plan_patch` so a
common policy cannot elevate ``CNST:blocking`` / ``IDN`` / ``AXM`` /
``CLAIM`` / ``LIM``.  Admin policies (``requires == "admin_policy"``)
can — but only with explicit user confirmation at the CLI layer.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.ast import CortexDocument, Entry, normalize_section_id
from ..core.parser import build_entry_from_value, parse_cortex
from ..core.transactions import MutationPlan, execute_transaction
from ..core.writer import write_cortex
from .candidates import Candidate
from .errors import (
    LE008_ELEVATION_BLOCKED,
    LE010_POLICY_NOT_FOUND,
    LE013_DRY_RUN_REQUIRED,
    LearningError,
)
from .index import rebuild_for_workspace
from .policy import LearningPolicy, LearningPolicySet, find_policy, is_protected_by_policy
from .workspace import Workspace


# ---------------------------------------------------------------------------
# Patch
# ---------------------------------------------------------------------------


@dataclass
class Patch:
    """A planned mutation to ``brain.cortex``."""

    source_entries: List[str]
    target_layer: str
    target_section: str
    new_entry_sigil: str
    new_entry_name: str
    new_entry_value: Dict[str, Any]
    reason: str = ""
    policy_id: Optional[str] = None
    promotion_score: int = 0
    affected_files: List[str] = field(default_factory=list)
    mode: str = "propose"  # propose | apply | apply_confirmed | block

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_entries": list(self.source_entries),
            "target_layer": self.target_layer,
            "target_section": self.target_section,
            "new_entry": {
                "sigil": self.new_entry_sigil,
                "name": self.new_entry_name,
                "value": dict(self.new_entry_value),
            },
            "reason": self.reason,
            "policy_id": self.policy_id,
            "promotion_score": self.promotion_score,
            "affected_files": list(self.affected_files),
            "mode": self.mode,
        }


# ---------------------------------------------------------------------------
# Section resolution
# ---------------------------------------------------------------------------

# Where each elevated sigil should land by default.
_DEFAULT_SECTION_FOR_SIGIL = {
    "SES": "$4",
    "LNG": "$5",
    "KNW": "$6",
    "CNST": "$3",
    "STP": "$2",
}


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------


def plan_patch(
    brain_doc: CortexDocument,
    ps: LearningPolicySet,
    candidate: Candidate,
    *,
    policy_id: Optional[str] = None,
    admin_confirmed: bool = False,
    user_confirmed: bool = False,
) -> Patch:
    """Plan a patch for ``candidate``.

    Behaviour:

    - If ``policy_id`` is given, the matching policy MUST exist and
      MUST authorise the elevation (action ``apply`` or ``propose``).
    - If the candidate's source sigil is protected, the patch is
      returned with ``mode="block"`` (no exception — the caller may
      still want to render a diff explaining the block).
    - Otherwise the patch mode is ``propose`` (dry-run only). To
      actually apply, the caller must invoke :func:`apply_patch` with
      ``mode="apply"``.
    """

    # Resolve policy (if any)
    policy: Optional[LearningPolicy] = None
    if policy_id:
        policy = find_policy(ps, policy_id)
        if policy is None:
            raise LearningError(
                LE010_POLICY_NOT_FOUND,
                f"no policy with id {policy_id!r}",
            )
    # Protection check — common policies cannot elevate protected sigils.
    # Look up the source entry so we can pass its attrs to the matcher
    # (this catches the "CNST:blocking" pattern in the protected list).
    src_selector = candidate.source_entries[0] if candidate.source_entries else ""
    src_sigil = src_selector.split(":", 1)[0] if src_selector else ""
    src_attrs: Optional[Dict[str, Any]] = None
    for sec, e in brain_doc.iter_entries():
        if f"{e.sigil}:{e.name}" == src_selector:
            src_attrs = e.value if isinstance(e.value, dict) else None
            break
    if is_protected_by_policy(ps, src_sigil, src_selector.split(":", 1)[1] if ":" in src_selector else "", attrs=src_attrs):
        return Patch(
            source_entries=list(candidate.source_entries),
            target_layer=candidate.target,
            target_section=_DEFAULT_SECTION_FOR_SIGIL.get(candidate.target, "$4"),
            new_entry_sigil=candidate.target,
            new_entry_name=_derive_name(brain_doc, candidate),
            new_entry_value={},
            reason=f"protected sigil {src_sigil} cannot be elevated by common policy",
            policy_id=policy_id,
            promotion_score=candidate.promotion_score,
            affected_files=[".cortex/brain.cortex"],
            mode="block",
        )

    # Determine the new entry's value by aggregating source entries
    new_value = _aggregate_source_entries(brain_doc, candidate)

    # Policy gate
    mode = "propose"
    if policy is not None:
        if policy.action == "block":
            mode = "block"
        elif policy.action == "apply":
            # Admin policies require explicit confirmation
            if policy.is_admin and not admin_confirmed:
                mode = "propose"  # cannot auto-apply admin policy
            else:
                # ``apply`` policy authorises the engine to apply —
                # but the CLI still requires --apply + --confirm at
                # the user layer.
                mode = "apply" if user_confirmed else "propose"
        elif policy.action == "propose":
            mode = "propose"

    target_section = _DEFAULT_SECTION_FOR_SIGIL.get(candidate.target, "$4")
    return Patch(
        source_entries=list(candidate.source_entries),
        target_layer=candidate.target,
        target_section=target_section,
        new_entry_sigil=candidate.target,
        new_entry_name=_derive_name(brain_doc, candidate),
        new_entry_value=new_value,
        reason=candidate.reason or f"elevate {src_sigil}→{candidate.target}",
        policy_id=policy_id,
        promotion_score=candidate.promotion_score,
        affected_files=[".cortex/brain.cortex"],
        mode=mode,
    )


def _derive_name(brain_doc: CortexDocument, candidate: Candidate) -> str:
    """Derive a name for the elevated entry from its source cluster."""

    if not candidate.source_entries:
        return f"elevated_{candidate.target.lower()}"
    first = candidate.source_entries[0]
    # Strip sigil prefix (e.g. "SES:policy_externalization_1" → "policy_externalization")
    if ":" in first:
        name = first.split(":", 1)[1]
    else:
        name = first
    # Strip trailing _N suffix used for cluster enumeration
    parts = name.rsplit("_", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0]
    return name


def _aggregate_source_entries(
    brain_doc: CortexDocument,
    candidate: Candidate,
) -> Dict[str, Any]:
    """Aggregate the source entries' attributes into a single value dict.

    Strategy:

    - ``topic`` / ``outcome`` / ``lesson`` / ``risk`` are merged by
      taking the first non-empty value.
    - ``user_validated`` is set to ``True`` if ANY source has it true.
    - ``promotion_score`` is set from the candidate.
    - Required fields for the target sigil are filled with sensible
      defaults so the new entry passes validation.
    """

    sources: List[Entry] = []
    for sel in candidate.source_entries:
        for sec, e in brain_doc.iter_entries():
            if f"{e.sigil}:{e.name}" == sel:
                sources.append(e)
                break
    merged: Dict[str, Any] = {}
    user_validated_any = False
    for e in sources:
        attrs = e.value if isinstance(e.value, dict) else {}
        for k in ("topic", "outcome", "lesson", "risk", "statement", "content"):
            v = attrs.get(k)
            if isinstance(v, str) and v and k not in merged:
                merged[k] = v
        if attrs.get("user_validated") is True:
            user_validated_any = True
    if user_validated_any:
        merged["user_validated"] = True
    # Fill required fields per target sigil (so validation passes)
    target = candidate.target
    if target == "LNG":
        merged.setdefault("type", "operational")
        merged.setdefault("cause", "repeated_observation")
        merged.setdefault("lesson", merged.get("outcome", merged.get("topic", "elevated_lesson")))
        merged.setdefault("prevention", "follow_policy")
    elif target == "KNW":
        merged.setdefault("topic", merged.get("topic", "elevated_knowledge"))
        merged.setdefault("content", merged.get("lesson", merged.get("outcome", "")))
        merged.setdefault("status", "active")
    elif target == "SES":
        merged.setdefault("input", "")
        merged.setdefault("output", "")
        merged.setdefault("outcome", merged.get("outcome", "elevated_outcome"))
        merged.setdefault("date", "")
    elif target == "CNST":
        merged.setdefault("rule", merged.get("risk", merged.get("statement", "elevated_constraint")))
        merged.setdefault("severity", "blocking")
        merged.setdefault("survive", "min")
    elif target == "STP":
        merged.setdefault("action", merged.get("action", "next_action"))
        merged.setdefault("reason", "elevated_from_recurrent_nxt")
        merged.setdefault("owner", "agent")
        merged.setdefault("status", "current")
        merged.setdefault("survive", "min")
    return merged


# ---------------------------------------------------------------------------
# Diff rendering
# ---------------------------------------------------------------------------


def render_diff(brain_doc: CortexDocument, patch: Patch) -> str:
    """Render a human-readable unified diff for ``patch``.

    The diff shows the new entry that would be appended to the target
    section. No actual mutation is performed.
    """

    target_sec_id = normalize_section_id(patch.target_section)
    target_sec = brain_doc.get_section(target_sec_id)
    section_header = f"{target_sec_id}"
    if target_sec and target_sec.title:
        section_header = f"{target_sec_id}: {target_sec.title}"
    # Build the new entry text
    new_entry = build_entry_from_value(
        target_sec_id,
        patch.new_entry_sigil,
        patch.new_entry_name,
        "attrs",
        patch.new_entry_value,
    )
    from ..core.writer import serialize_entry
    new_entry_line = serialize_entry(new_entry, brain_doc.glossary)
    lines: List[str] = []
    lines.append(f"# Patch mode: {patch.mode}")
    lines.append(f"# Reason: {patch.reason}")
    if patch.policy_id:
        lines.append(f"# Policy: {patch.policy_id}")
    lines.append(f"# Promotion score: {patch.promotion_score}")
    lines.append(f"# Affected files: {', '.join(patch.affected_files)}")
    lines.append("")
    lines.append(f"--- {patch.affected_files[0]} (current)")
    lines.append(f"+++ {patch.affected_files[0]} (proposed)")
    lines.append(f"@@ {section_header} @@")
    lines.append(f"+{new_entry_line}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------


def apply_patch(
    workspace: Workspace,
    brain_doc: CortexDocument,
    patch: Patch,
    *,
    mode: str = "dry-run",
    confirm: bool = False,
) -> Dict[str, Any]:
    """Apply ``patch`` to ``brain.cortex``.

    Modes:

    - ``dry-run`` (default): no filesystem change; returns the diff.
    - ``apply``: writes the new brain to disk and rebuilds the index.
      Requires ``confirm=True`` to actually write.
    - ``apply_confirmed``: same as ``apply`` with implicit confirmation
      (used when the user has already confirmed at the CLI layer).

    Returns a dict with keys: ``mode``, ``applied``, ``diff``,
    ``new_entry_selector``, and transaction provenance.
    """

    if patch.mode == "block":
        raise LearningError(
            LE008_ELEVATION_BLOCKED,
            f"patch is blocked: {patch.reason}",
        )

    if mode == "dry-run":
        return {
            "mode": "dry-run",
            "applied": False,
            "diff": render_diff(brain_doc, patch),
            "new_entry_selector": f"{patch.new_entry_sigil}:{patch.new_entry_name}",
        }

    if mode in ("apply", "apply_confirmed"):
        if not confirm and mode != "apply_confirmed":
            raise LearningError(
                LE013_DRY_RUN_REQUIRED,
                "apply mode requires --confirm (or apply_confirmed)",
            )
        
        # Build the new entry
        target_sec_id = normalize_section_id(patch.target_section)
        new_entry = build_entry_from_value(
            target_sec_id,
            patch.new_entry_sigil,
            patch.new_entry_name,
            "attrs",
            patch.new_entry_value,
        )
        
        # Create mutation plan for TransactionService
        plan = MutationPlan(
            operation="add",
            section_id=target_sec_id,
            new_entry=new_entry,
            reason=patch.reason,
            metadata={
                "policy_id": patch.policy_id,
                "promotion_score": patch.promotion_score,
                "source_entries": list(patch.source_entries),
                "target_layer": patch.target_layer,
            },
        )
        
        # Execute transaction with CAS, backup, and validation
        result = execute_transaction(
            workspace.brain_path,
            plan,
            create_backup=True,
            validate_fn=lambda doc: [],  # No additional validation beyond parse
            dry_run=False,
        )
        
        if not result.success:
            raise LearningError(
                LE008_ELEVATION_BLOCKED,
                result.error or "Transaction failed",
            )
        
        # Rebuild index after successful transaction
        idx = rebuild_for_workspace(workspace)
        
        return {
            "mode": mode,
            "applied": True,
            "diff": render_diff(brain_doc, patch),
            "new_entry_selector": f"{patch.new_entry_sigil}:{patch.new_entry_name}",
            "new_index_entries": len(idx.entries),
            "transaction": result.to_dict(),
        }
    
    raise LearningError(
        LE008_ELEVATION_BLOCKED,
        f"unknown apply mode {mode!r}",
    )


def _section_title_for(section_id: str) -> str:
    titles = {
        "$2": "ACTIVE WORK",
        "$3": "GOVERNANCE",
        "$4": "SESSIONS",
        "$5": "LESSONS",
        "$6": "KNOWLEDGE",
    }
    return titles.get(section_id, "")


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


def verify_post_apply(workspace: Workspace) -> Dict[str, Any]:
    """Re-parse brain and rebuild index after a mutation."""

    brain_doc = workspace.parse_brain()
    idx = rebuild_for_workspace(workspace)
    return {
        "brain_hash": workspace.brain_hash(),
        "policy_hash": workspace.policy_hash(),
        "index_entries": len(idx.entries),
        "brain_entries": sum(1 for _ in brain_doc.iter_entries()),
    }


__all__ = [
    "Patch",
    "plan_patch",
    "render_diff",
    "apply_patch",
    "verify_post_apply",
]
