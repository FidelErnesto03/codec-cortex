# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""UpgradeService — structural migration for .cortex files between versions.

Provides inspect/plan/apply/rollback lifecycle for upgrading .cortex
artefacts from a baseline (e.g. v0.5.2) to a candidate (e.g. v0.6.0).

Each .cortex file is parsed through the canonical parser and compared
structurally via ``compare_ast``. The service classifies every file as
one of four categories:

- **compatible** — same parsed structure in both versions (no action)
- **deprecated** — exists in baseline but removed from candidate
- **migrable**  — exists in both but has structural differences
- **incompatible** — candidate file cannot be parsed

Usage::

    from cortex.upgrade import UpgradeService

    svc = UpgradeService()
    report = svc.inspect("/path/to/baseline", "/path/to/candidate")
    plan = svc.plan(report)
    svc.apply(plan)       # creates backups under certification/backups/
    svc.rollback(plan)    # restores from backups
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from cortex.core.parser import parse_cortex
from cortex.core.compare import compare_ast
from cortex.core.errors import CortexError


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class FileStatus:
    """Analysis result for a single .cortex file."""
    rel_path: str                    # relative path within baseline
    status: str                      # compatible | deprecated | migrable | incompatible
    detail: str = ""                 # human-readable explanation
    diff_count: int = 0              # number of structural diffs (0 for compatible/deprecated)
    hash_baseline: str = ""          # document hash of baseline version
    hash_candidate: str = ""         # document hash of candidate version (empty if deprecated)


@dataclass
class InspectResult:
    """Full inspection report."""
    baseline_path: str
    candidate_path: str
    files: List[FileStatus] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=lambda: {
        "total": 0,
        "compatible": 0,
        "deprecated": 0,
        "migrable": 0,
        "incompatible": 0,
    })

    @property
    def total(self) -> int:
        return len(self.files)

    def to_dict(self) -> dict:
        return {
            "baseline_path": self.baseline_path,
            "candidate_path": self.candidate_path,
            "summary": self.summary,
            "files": [asdict(f) for f in self.files],
        }


@dataclass
class PlanStep:
    """Single migration step."""
    file: str                        # relative path
    action: str                      # keep | migrate | deprecate | remove
    risk: str                        # low | medium | high
    detail: str = ""                 # human-readable explanation


@dataclass
class MigrationPlan:
    """Migration plan generated from an InspectResult."""
    steps: List[PlanStep] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=lambda: {
        "total": 0,
        "keep": 0,
        "migrate": 0,
        "deprecate": 0,
        "remove": 0,
    })

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "steps": [asdict(s) for s in self.steps],
        }


# ---------------------------------------------------------------------------
# UpgradeService
# ---------------------------------------------------------------------------

class UpgradeService:
    """Structural upgrade inspector and executor for .cortex files."""

    def __init__(self) -> None:
        self._last_inspect: Optional[InspectResult] = None
        self._last_plan: Optional[MigrationPlan] = None
        self._backup_root: Optional[str] = None

    # -- public API --------------------------------------------------------

    def inspect(
        self,
        baseline_path: str,
        candidate_path: str,
        path_mapping: Optional[Dict[str, str]] = None,
    ) -> InspectResult:
        """Compare .cortex files between *baseline_path* and *candidate_path*.

        *path_mapping* maps baseline path prefixes to candidate path prefixes
        for structural relocations (e.g. ``{"cli/src/tests": "tests"}``).

        Returns an :class:`InspectResult` with per-file status and summary.
        """
        baseline_root = Path(baseline_path).resolve()
        candidate_root = Path(candidate_path).resolve()

        if not baseline_root.is_dir():
            raise NotADirectoryError(f"baseline_path is not a directory: {baseline_root}")
        if not candidate_root.is_dir():
            raise NotADirectoryError(f"candidate_path is not a directory: {candidate_root}")

        result = InspectResult(
            baseline_path=str(baseline_root),
            candidate_path=str(candidate_root),
        )

        # Collect all .cortex files in baseline (exclude .cortex.md)
        baseline_files: List[Path] = []
        for dirpath, _dirs, files in os.walk(str(baseline_root)):
            for fname in files:
                if fname.endswith(".cortex") and not fname.endswith(".cortex.md"):
                    baseline_files.append(Path(dirpath) / fname)

        for bl_file in baseline_files:
            rel_path = str(bl_file.relative_to(baseline_root))

            # Resolve candidate path using mapping
            cand_rel = self._resolve_candidate_path(rel_path, path_mapping)
            cand_file = candidate_root / cand_rel if cand_rel else None

            if cand_file is None or not cand_file.is_file():
                # Exists in baseline but not in candidate
                result.files.append(FileStatus(
                    rel_path=rel_path,
                    status="deprecated",
                    detail=f"baseline file {rel_path} not found in candidate",
                ))
                result.summary["deprecated"] += 1
                result.summary["total"] += 1
                continue

            # Parse and compare
            try:
                bl_text = bl_file.read_text(encoding="utf-8")
                cand_text = cand_file.read_text(encoding="utf-8")
            except Exception as exc:
                result.files.append(FileStatus(
                    rel_path=rel_path,
                    status="incompatible",
                    detail=f"cannot read file: {exc}",
                ))
                result.summary["incompatible"] += 1
                result.summary["total"] += 1
                continue

            try:
                bl_doc = parse_cortex(bl_text, path=str(bl_file))
            except CortexError as exc:
                result.files.append(FileStatus(
                    rel_path=rel_path,
                    status="incompatible",
                    detail=f"baseline parse error: {exc}",
                ))
                result.summary["incompatible"] += 1
                result.summary["total"] += 1
                continue

            try:
                cand_doc = parse_cortex(cand_text, path=str(cand_file))
            except CortexError as exc:
                result.files.append(FileStatus(
                    rel_path=rel_path,
                    status="incompatible",
                    detail=f"candidate parse error: {exc}",
                ))
                result.summary["incompatible"] += 1
                result.summary["total"] += 1
                continue

            from cortex.core.ast import compute_document_hash
            bl_hash = compute_document_hash(bl_text)
            cand_hash = compute_document_hash(cand_text)

            diff_result = compare_ast(bl_doc, cand_doc)
            if diff_result.equal:
                result.files.append(FileStatus(
                    rel_path=rel_path,
                    status="compatible",
                    detail="structurally identical",
                    hash_baseline=bl_hash,
                    hash_candidate=cand_hash,
                ))
                result.summary["compatible"] += 1
            else:
                result.files.append(FileStatus(
                    rel_path=rel_path,
                    status="migrable",
                    detail=f"{len(diff_result.diffs)} structural difference(s)",
                    diff_count=len(diff_result.diffs),
                    hash_baseline=bl_hash,
                    hash_candidate=cand_hash,
                ))
                result.summary["migrable"] += 1

            result.summary["total"] += 1

        self._last_inspect = result
        return result

    def plan(self, inspect_result: Optional[InspectResult] = None) -> MigrationPlan:
        """Generate a migration plan from an inspection result.

        If *inspect_result* is omitted, uses the last result from
        :meth:`inspect`.
        """
        result = inspect_result or self._last_inspect
        if result is None:
            raise RuntimeError("no inspection result available — call inspect() first")

        plan = MigrationPlan()

        for fs in result.files:
            if fs.status == "compatible":
                plan.steps.append(PlanStep(
                    file=fs.rel_path,
                    action="keep",
                    risk="low",
                    detail="structurally identical — no action required",
                ))
                plan.summary["keep"] += 1
            elif fs.status == "deprecated":
                plan.steps.append(PlanStep(
                    file=fs.rel_path,
                    action="deprecate",
                    risk="low",
                    detail="removed from candidate — flag for deprecation notice",
                ))
                plan.summary["deprecate"] += 1
            elif fs.status == "migrable":
                risk = "high" if fs.diff_count > 5 else "medium"
                plan.steps.append(PlanStep(
                    file=fs.rel_path,
                    action="migrate",
                    risk=risk,
                    detail=f"{fs.diff_count} diff(s) — candidate version should replace baseline",
                ))
                plan.summary["migrate"] += 1
            elif fs.status == "incompatible":
                plan.steps.append(PlanStep(
                    file=fs.rel_path,
                    action="remove",
                    risk="high",
                    detail="parse error — manual review required",
                ))
                plan.summary["remove"] += 1

        plan.summary["total"] = len(plan.steps)
        self._last_plan = plan
        return plan

    def apply(
        self,
        plan: Optional[MigrationPlan] = None,
        candidate_path: Optional[str] = None,
        target_dir: Optional[str] = None,
    ) -> str:
        """Execute a migration plan.

        Copies candidate files to *target_dir* (defaults to baseline parent
        for cross-version upgrades). Creates a timestamped backup under
        ``certification/backups/upgrade-{ts}/`` beforehand.

        Returns the backup directory path.
        """
        migration_plan = plan or self._last_plan
        if migration_plan is None:
            raise RuntimeError("no plan available — call plan() first")

        if candidate_path is None:
            raise ValueError("candidate_path is required for apply()")

        candidate_root = Path(candidate_path).resolve()
        if target_dir is None:
            target_dir = str(candidate_root.parent / f"{candidate_root.name}-upgraded")

        # Create backup
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_dir = str(
            Path("certification") / "backups" / f"upgrade-{timestamp}"
        )
        backup_root = Path(backup_dir)
        backup_root.mkdir(parents=True, exist_ok=True)

        self._backup_root = str(backup_root)

        migrated: List[str] = []
        for step in migration_plan.steps:
            if step.action == "keep":
                continue

            src = candidate_root / step.file
            if not src.exists():
                continue

            # Backup existing target file if present
            dst = Path(target_dir) / step.file
            if dst.exists():
                backup_file = backup_root / step.file
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(dst), str(backup_file))

            # Execute migration
            if step.action == "migrate":
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(dst))
                migrated.append(step.file)
            elif step.action == "deprecate":
                # For deprecation, remove from target (backup already made)
                if dst.exists():
                    dst.unlink()
            elif step.action == "remove":
                # For incompatible, remove from target (manual review needed)
                if dst.exists():
                    dst.unlink()

        # Write backup manifest
        manifest = {
            "timestamp": timestamp,
            "candidate_path": str(candidate_root),
            "target_dir": target_dir,
            "backup_root": str(backup_root),
            "plan": migration_plan.to_dict(),
            "migrated_files": migrated,
        }
        (backup_root / "MANIFEST.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return backup_dir

    def rollback(
        self,
        plan: Optional[MigrationPlan] = None,
        backup_dir: Optional[str] = None,
        target_dir: Optional[str] = None,
    ) -> int:
        """Restore files from a backup directory.

        Returns the number of files restored.
        """
        if backup_dir is None:
            backup_dir = self._backup_root
        if backup_dir is None:
            raise ValueError("no backup_dir known — provide one or run apply() first")

        backup_root = Path(backup_dir)
        if not backup_root.is_dir():
            raise NotADirectoryError(f"backup directory not found: {backup_root}")

        if target_dir is None and plan is None:
            # Try reading from manifest
            manifest_path = backup_root / "MANIFEST.json"
            if manifest_path.is_file():
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                target_dir = manifest.get("target_dir")
            if target_dir is None:
                raise ValueError("target_dir required when manifest has no target_dir")

        target_root = Path(target_dir) if target_dir else None

        restored = 0
        for backup_file in backup_root.rglob("*"):
            if not backup_file.is_file() or backup_file.name == "MANIFEST.json":
                continue
            rel = backup_file.relative_to(backup_root)
            if target_root is not None:
                dst = target_root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(backup_file), str(dst))
                restored += 1

        return restored

    # -- reporting helpers -------------------------------------------------

    def write_report(self, inspect_result: InspectResult, path: str) -> str:
        """Write an inspection report as JSON to *path*.

        Returns the absolute path written.
        """
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(inspect_result.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return str(out.resolve())

    # -- internal ----------------------------------------------------------

    @staticmethod
    def _resolve_candidate_path(
        rel_path: str,
        mapping: Optional[Dict[str, str]],
    ) -> Optional[str]:
        """Map a baseline relative path to candidate relative path.

        Tries each mapping prefix; if none matches, returns *rel_path*
        unchanged (same-relative-path lookup).
        """
        if mapping:
            for prefix, replacement in mapping.items():
                if rel_path.startswith(prefix):
                    tail = rel_path[len(prefix):]
                    if tail.startswith("/"):
                        tail = tail[1:]
                    if replacement is None:
                        return None  # explicitly deprecated
                    if replacement:
                        return f"{replacement}/{tail}" if tail else replacement
        return rel_path
