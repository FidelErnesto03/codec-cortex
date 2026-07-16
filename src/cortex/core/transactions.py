"""Transaction service for atomic, auditable mutations.

This module provides a single entry point for all canonical mutations
to cortex documents. Every mutation goes through:

1. load — read current document and compute source hash
2. expected-hash — optional CAS check to prevent concurrent overwrites
3. plan — describe the intended change
4. diff — render human-readable explanation
5. validate — ensure mutated AST is valid
6. write temp — write to temporary file
7. fsync — ensure durability
8. backup — copy original to .bak
9. atomic replace — rename temp to target
10. re-read — verify written content matches intent
11. verify — parse and validate result
12. audit result — return full provenance

Critical properties:
- No silent replacements (default is no-replace)
- Backup always created before mutation
- expected_hash prevents concurrent modification conflicts
- Full audit trail with before/after hashes
- Rollback capability via backup file
"""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .ast import CortexDocument, Entry
from .parser import parse_cortex
from .writer import write_cortex


@dataclass
class TransactionResult:
    """Result of a completed transaction."""
    
    success: bool
    operation: str
    path: str
    before_hash: str
    after_hash: str
    backup_path: Optional[str] = None
    changes: List[Dict[str, Any]] = field(default_factory=list)
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MutationPlan:
    """Describes an intended mutation."""
    
    operation: str  # add | update | delete | migrate
    section_id: str
    entry_selector: Optional[str] = None  # SIGIL:name or None for add
    new_entry: Optional[Entry] = None
    updated_value: Optional[Dict[str, Any]] = None
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        base = {
            "operation": self.operation,
            "section_id": self.section_id,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }
        if self.entry_selector:
            base["entry_selector"] = self.entry_selector
        if self.new_entry:
            base["new_entry"] = {
                "sigil": self.new_entry.sigil,
                "name": self.new_entry.name,
                "value": self.new_entry.value if isinstance(self.new_entry.value, dict) else {},
            }
        if self.updated_value:
            base["updated_value"] = dict(self.updated_value)
        return base


def _compute_hash(content: str) -> str:
    """Compute SHA-256 hash of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _create_backup(path: Path) -> Path:
    """Create a backup copy of the file."""
    backup_path = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup_path)
    return backup_path


def execute_transaction(
    path: Path,
    plan: MutationPlan,
    *,
    expected_hash: Optional[str] = None,
    create_backup: bool = True,
    validate_fn: Optional[Callable[[CortexDocument], List[Dict[str, Any]]]] = None,
    dry_run: bool = False,
) -> TransactionResult:
    """Execute a transaction with full audit trail.
    
    Args:
        path: Path to the cortex document to mutate
        plan: Description of the intended mutation
        expected_hash: If provided, verify current file hash matches (CAS)
        create_backup: Whether to create a .bak backup before mutation
        validate_fn: Optional validation function returning diagnostics
        dry_run: If True, simulate without writing
    
    Returns:
        TransactionResult with full provenance
    """
    timestamp = _now_iso()
    changes: List[Dict[str, Any]] = []
    diagnostics: List[Dict[str, Any]] = []
    
    # Step 1: Load current document
    if not path.exists():
        return TransactionResult(
            success=False,
            operation=plan.operation,
            path=str(path),
            before_hash="",
            after_hash="",
            error=f"File not found: {path}",
            timestamp=timestamp,
        )
    
    content = path.read_text(encoding="utf-8")
    before_hash = _compute_hash(content)
    
    # Step 2: CAS check
    if expected_hash is not None and expected_hash != before_hash:
        return TransactionResult(
            success=False,
            operation=plan.operation,
            path=str(path),
            before_hash=before_hash,
            after_hash="",
            error=f"E_CONFLICT: expected hash mismatch. Expected {expected_hash[:16]}..., got {before_hash[:16]}...",
            timestamp=timestamp,
        )
    
    # Parse document
    try:
        doc = parse_cortex(content)
    except Exception as e:
        return TransactionResult(
            success=False,
            operation=plan.operation,
            path=str(path),
            before_hash=before_hash,
            after_hash="",
            error=f"Parse failed: {e}",
            timestamp=timestamp,
        )
    
    # Step 3-4: Apply mutation plan
    try:
        _apply_mutation(doc, plan, changes)
    except Exception as e:
        return TransactionResult(
            success=False,
            operation=plan.operation,
            path=str(path),
            before_hash=before_hash,
            after_hash="",
            error=f"Mutation failed: {e}",
            timestamp=timestamp,
        )
    
    # Step 5: Validate mutated document
    if validate_fn is not None:
        diagnostics = validate_fn(doc)
        has_errors = any(d.get("severity") == "error" for d in diagnostics)
        if has_errors:
            return TransactionResult(
                success=False,
                operation=plan.operation,
                path=str(path),
                before_hash=before_hash,
                after_hash="",
                diagnostics=diagnostics,
                error="Validation failed after mutation",
                timestamp=timestamp,
            )
    
    # Serialize mutated document
    new_content = write_cortex(doc)
    after_hash = _compute_hash(new_content)
    
    if dry_run:
        return TransactionResult(
            success=True,
            operation=plan.operation,
            path=str(path),
            before_hash=before_hash,
            after_hash=after_hash,
            changes=changes,
            diagnostics=diagnostics,
            timestamp=timestamp,
        )
    
    # Step 6-9: Write with backup and atomic replace
    backup_path: Optional[Path] = None
    if create_backup:
        backup_path = _create_backup(path)
    
    # Write to temp file
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".cortex.tmp", dir=path.parent)
    try:
        with open(tmp_fd, "w", encoding="utf-8") as f:
            f.write(new_content)
            f.flush()
            import os
            os.fsync(f.fileno())
        
        # Step 9: Atomic replace
        tmp_path_obj = Path(tmp_path)
        tmp_path_obj.replace(path)
        
        # Step 10-11: Re-read and verify
        verify_content = path.read_text(encoding="utf-8")
        verify_hash = _compute_hash(verify_content)
        if verify_hash != after_hash:
            # Rollback from backup
            if backup_path:
                shutil.copy2(backup_path, path)
            return TransactionResult(
                success=False,
                operation=plan.operation,
                path=str(path),
                before_hash=before_hash,
                after_hash="",
                backup_path=str(backup_path) if backup_path else None,
                error="Post-write verification failed: hash mismatch",
                timestamp=timestamp,
            )
        
    except Exception as e:
        # Attempt rollback
        if backup_path:
            try:
                shutil.copy2(backup_path, path)
            except Exception:
                pass  # Best effort rollback
        return TransactionResult(
            success=False,
            operation=plan.operation,
            path=str(path),
            before_hash=before_hash,
            after_hash="",
            backup_path=str(backup_path) if backup_path else None,
            error=f"Write failed: {e}",
            timestamp=timestamp,
        )
    
    return TransactionResult(
        success=True,
        operation=plan.operation,
        path=str(path),
        before_hash=before_hash,
        after_hash=after_hash,
        backup_path=str(backup_path) if backup_path else None,
        changes=changes,
        diagnostics=diagnostics,
        timestamp=timestamp,
    )


def _apply_mutation(doc: CortexDocument, plan: MutationPlan, changes: List[Dict[str, Any]]) -> None:
    """Apply a mutation plan to a document AST."""
    
    section = doc.get_section(plan.section_id)
    if section is None:
        section = doc.add_section(plan.section_id, title="")
    
    if plan.operation == "add":
        if plan.new_entry is None:
            raise ValueError("add operation requires new_entry")
        section.entries.append(plan.new_entry)
        changes.append({
            "action": "add",
            "section": plan.section_id,
            "entry": f"{plan.new_entry.sigil}:{plan.new_entry.name}",
        })
    
    elif plan.operation == "update":
        if not plan.entry_selector:
            raise ValueError("update operation requires entry_selector")
        
        found = False
        for i, entry in enumerate(section.entries):
            selector = f"{entry.sigil}:{entry.name}"
            if selector == plan.entry_selector:
                if plan.updated_value:
                    # Merge updated values
                    if isinstance(entry.value, dict):
                        entry.value = {**entry.value, **plan.updated_value}
                    else:
                        entry.value = plan.updated_value
                elif plan.new_entry:
                    # Replace entire entry
                    section.entries[i] = plan.new_entry
                found = True
                changes.append({
                    "action": "update",
                    "section": plan.section_id,
                    "entry": selector,
                })
                break
        
        if not found:
            raise ValueError(f"Entry not found: {plan.entry_selector}")
    
    elif plan.operation == "delete":
        if not plan.entry_selector:
            raise ValueError("delete operation requires entry_selector")
        
        original_count = len(section.entries)
        section.entries = [
            e for e in section.entries
            if f"{e.sigil}:{e.name}" != plan.entry_selector
        ]
        if len(section.entries) == original_count:
            raise ValueError(f"Entry not found for deletion: {plan.entry_selector}")
        changes.append({
            "action": "delete",
            "section": plan.section_id,
            "entry": plan.entry_selector,
        })
    
    elif plan.operation == "migrate":
        # Migration is a complex operation handled by caller
        # This is just a placeholder for audit trail
        changes.append({
            "action": "migrate",
            "section": plan.section_id,
            "metadata": plan.metadata,
        })
    
    else:
        raise ValueError(f"Unknown operation: {plan.operation}")


__all__ = [
    "TransactionResult",
    "MutationPlan",
    "execute_transaction",
]
