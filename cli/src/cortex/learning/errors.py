"""Error model for the learning engine.

These errors are intentionally local to the learning subsystem; they
extend :class:`cortex.core.errors.CortexError` so the existing CLI error
reporting path keeps working, but carry learning-specific codes so the
certification auditor can grep for them.
"""

from __future__ import annotations

from ..core.errors import CortexError


# Learning-engine error codes (LE-xxx)
LE001_WORKSPACE_NOT_FOUND = "LE001_WORKSPACE_NOT_FOUND"
LE002_MANIFEST_MISSING = "LE002_MANIFEST_MISSING"
LE003_BRAIN_MISSING = "LE003_BRAIN_MISSING"
LE004_POLICY_INVALID = "LE004_POLICY_INVALID"
LE005_CONDITION_INVALID = "LE005_CONDITION_INVALID"
LE006_INDEX_STALE = "LE006_INDEX_STALE"
LE007_PROTECTED_SIGIL = "LE007_PROTECTED_SIGIL"
LE008_ELEVATION_BLOCKED = "LE008_ELEVATION_BLOCKED"
LE009_CANDIDATE_NOT_FOUND = "LE009_CANDIDATE_NOT_FOUND"
LE010_POLICY_NOT_FOUND = "LE010_POLICY_NOT_FOUND"
LE011_FORBIDDEN_EVAL = "LE011_FORBIDDEN_EVAL"
LE012_INDEX_HASH_MISMATCH = "LE012_INDEX_HASH_MISMATCH"
LE013_DRY_RUN_REQUIRED = "LE013_DRY_RUN_REQUIRED"


class LearningError(CortexError):
    """Base class for learning-engine errors."""


__all__ = [
    "LearningError",
    "LE001_WORKSPACE_NOT_FOUND",
    "LE002_MANIFEST_MISSING",
    "LE003_BRAIN_MISSING",
    "LE004_POLICY_INVALID",
    "LE005_CONDITION_INVALID",
    "LE006_INDEX_STALE",
    "LE007_PROTECTED_SIGIL",
    "LE008_ELEVATION_BLOCKED",
    "LE009_CANDIDATE_NOT_FOUND",
    "LE010_POLICY_NOT_FOUND",
    "LE011_FORBIDDEN_EVAL",
    "LE012_INDEX_HASH_MISMATCH",
    "LE013_DRY_RUN_REQUIRED",
]
