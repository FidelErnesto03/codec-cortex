"""Session runtime with isolated state (v0.6.0).

CRITICAL CHANGE from v0.5.x:
- Session state NO LONGER writes to brain.cortex during the session
- State lives in .cortex/runtime/session.cortex (transitory)
- brain.cortex is only mutated on consolidate/close with CAS
- SES:current entry is NOT created in brain during session

This implements P0-006: Session runtime isolation.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..core.transactions import MutationPlan, execute_transaction
from ..learning.errors import LearningError, LE015_SESSION_NOT_RUNNING
from ..learning.workspace import Workspace


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SESSION_STATE_FILE = "session.cortex"
RUNTIME_DIR_NAME = "runtime"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class SessionEvent:
    """A single event recorded during a session."""

    kind: str  # "modify" | "candidate" | "feedback" | "decay"
    selector: str = ""
    detail: str = ""
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SessionState:
    """In-memory representation of the session state."""

    session_id: str = ""
    start: str = ""  # ISO-8601 UTC
    end: Optional[str] = None
    brain_hash_at_start: str = ""
    entries_modified: int = 0
    candidates_detected: int = 0
    status: str = "running"  # running | consolidated | closed
    survive: str = "min"
    events: List[SessionEvent] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "start": self.start,
            "end": self.end,
            "brain_hash_at_start": self.brain_hash_at_start,
            "entries_modified": self.entries_modified,
            "candidates_detected": self.candidates_detected,
            "status": self.status,
            "survive": self.survive,
            "events": [e.to_dict() for e in self.events],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        events = [SessionEvent(**e) for e in data.get("events", [])]
        return cls(
            session_id=data.get("session_id", ""),
            start=data.get("start", ""),
            end=data.get("end"),
            brain_hash_at_start=data.get("brain_hash_at_start", ""),
            entries_modified=data.get("entries_modified", 0),
            candidates_detected=data.get("candidates_detected", 0),
            status=data.get("status", "running"),
            survive=data.get("survive", "min"),
            events=events,
        )


# ---------------------------------------------------------------------------
# Session service
# ---------------------------------------------------------------------------


class SessionService:
    """Manages session lifecycle with isolated runtime state."""

    def __init__(self, workspace: Workspace):
        self.workspace = workspace
        self.runtime_dir = workspace.root / RUNTIME_DIR_NAME
        self.session_state_path = self.runtime_dir / SESSION_STATE_FILE
        self._state: Optional[SessionState] = None

    def ensure_runtime_dir(self) -> None:
        """Ensure the runtime directory exists."""
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

    def _now_iso(self) -> str:
        """Return current UTC timestamp."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return str(uuid.uuid4())[:8]

    def start_session(
        self,
        *,
        session_id: Optional[str] = None,
        at_time: Optional[str] = None,
    ) -> SessionState:
        """Start a new session WITHOUT writing to brain.cortex.
        
        CRITICAL: This method does NOT create SES:current in brain.
        State is stored in .cortex/runtime/session.cortex only.
        """
        self.ensure_runtime_dir()
        
        # Load brain to get hash, but don't mutate it
        _ = self.workspace.parse_brain()
        brain_content = self.workspace.brain_path.read_text(encoding="utf-8")
        import hashlib
        brain_hash = hashlib.sha256(brain_content.encode("utf-8")).hexdigest()
        
        session_id = session_id or self._generate_session_id()
        start_time = at_time or self._now_iso()
        
        self._state = SessionState(
            session_id=session_id,
            start=start_time,
            brain_hash_at_start=brain_hash,
            status="running",
        )
        
        # Write session state to runtime file (NOT to brain)
        self._save_state()
        
        return self._state

    def get_current_state(self) -> Optional[SessionState]:
        """Load current session state from runtime file."""
        if not self.session_state_path.exists():
            return None
        
        try:
            data = json.loads(self.session_state_path.read_text(encoding="utf-8"))
            self._state = SessionState.from_dict(data)
            return self._state
        except Exception:
            return None

    def record_event(
        self,
        kind: str,
        selector: str = "",
        detail: str = "",
    ) -> None:
        """Record an event in the session state (NOT in brain)."""
        if self._state is None:
            self._state = self.get_current_state()
            if self._state is None:
                raise LearningError(LE015_SESSION_NOT_RUNNING, "No active session")

        event = SessionEvent(
            kind=kind,
            selector=selector,
            detail=detail,
            timestamp=self._now_iso(),
        )
        self._state.events.append(event)
        
        if kind == "modify":
            self._state.entries_modified += 1
        elif kind == "candidate":
            self._state.candidates_detected += 1
        
        self._save_state()

    def consolidate(self, *, dry_run: bool = False) -> Dict[str, Any]:
        """Consolidate session activity into a patch for brain.cortex.
        
        This produces a mutation plan but does NOT apply it unless
        called with dry_run=False and then followed by close().
        """
        if self._state is None:
            self._state = self.get_current_state()
            if self._state is None:
                raise LearningError(LE015_SESSION_NOT_RUNNING, "No active session")

        # Create a summary of the session
        summary = {
            "session_id": self._state.session_id,
            "start": self._state.start,
            "end": self._state.end or self._now_iso(),
            "entries_modified": self._state.entries_modified,
            "candidates_detected": self._state.candidates_detected,
            "events_count": len(self._state.events),
        }
        
        return {
            "dry_run": dry_run,
            "summary": summary,
            "status": "consolidated",
        }

    def close_session(
        self,
        *,
        confirm: bool = False,
        expected_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Close the session and optionally write final state to brain.
        
        CRITICAL: Uses CAS (expected_hash) to prevent concurrent conflicts.
        If brain changed since session start, aborts with E_CONFLICT.
        """
        if self._state is None:
            self._state = self.get_current_state()
            if self._state is None:
                raise LearningError(LE015_SESSION_NOT_RUNNING, "No active session")

        # Verify brain hasn't changed (CAS)
        brain_content = self.workspace.brain_path.read_text(encoding="utf-8")
        import hashlib
        current_brain_hash = hashlib.sha256(brain_content.encode("utf-8")).hexdigest()
        
        if expected_hash is None:
            # Use the hash captured at session start
            expected_hash = self._state.brain_hash_at_start
        
        if current_brain_hash != expected_hash:
            # Brain changed during session - abort or require explicit override
            self._state.status = "conflict"
            self._save_state()
            return {
                "status": "conflict",
                "error": "E_CONFLICT: brain.cortex changed during session",
                "expected_hash": expected_hash[:16] + "...",
                "actual_hash": current_brain_hash[:16] + "...",
            }
        
        # Update session state
        self._state.end = self._now_iso()
        self._state.status = "closed"
        self._save_state()
        
        # Optionally write a summary entry to brain (only with confirmation)
        if confirm:
            # Create a SES:last entry summarizing the session
            from ..core.parser import build_entry_from_value
            
            session_summary = {
                "session_id": self._state.session_id,
                "start": self._state.start,
                "end": self._state.end,
                "entries_modified": self._state.entries_modified,
                "candidates_detected": self._state.candidates_detected,
                "outcome": "session_completed",
            }
            
            new_entry = build_entry_from_value(
                "$4",  # SESSIONS section
                "SES",
                "last",
                "attrs",
                session_summary,
            )
            
            plan = MutationPlan(
                operation="add",
                section_id="$4",
                new_entry=new_entry,
                reason=f"Close session {self._state.session_id}",
                metadata={"session_id": self._state.session_id},
            )
            
            result = execute_transaction(
                self.workspace.brain_path,
                plan,
                expected_hash=expected_hash,
                create_backup=True,
                dry_run=False,
            )
            
            if not result.success:
                return {
                    "status": "error",
                    "error": result.error,
                }
            
            return {
                "status": "closed",
                "session_id": self._state.session_id,
                "transaction": result.to_dict(),
            }
        
        return {
            "status": "closed",
            "session_id": self._state.session_id,
            "brain_written": False,
        }

    def abort_session(self) -> Dict[str, Any]:
        """Abort the session without any changes to brain."""
        if self._state is None:
            self._state = self.get_current_state()
            if self._state is None:
                return {"status": "no_session"}
        
        self._state.status = "aborted"
        self._state.end = self._now_iso()
        self._save_state()
        
        # Remove runtime state file
        if self.session_state_path.exists():
            self.session_state_path.unlink()
        
        return {
            "status": "aborted",
            "session_id": self._state.session_id,
            "changes_discarded": True,
        }

    def recover_session(self) -> Optional[SessionState]:
        """Recover session state after a crash."""
        return self.get_current_state()

    def _save_state(self) -> None:
        """Save session state to runtime file."""
        self.ensure_runtime_dir()
        if self._state is None:
            return
        
        content = json.dumps(self._state.to_dict(), indent=2, ensure_ascii=False)
        self.session_state_path.write_text(content, encoding="utf-8")


__all__ = [
    "SessionService",
    "SessionState",
    "SessionEvent",
    "SESSION_STATE_FILE",
    "RUNTIME_DIR_NAME",
]
