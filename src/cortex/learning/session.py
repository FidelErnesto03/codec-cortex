"""Session lifecycle for the learning engine (v0.2.0, Fase A).

Implements the ``cortex session`` family of commands described in
``learning-engine-evolution.md`` §A:

- ``cortex session start``       — opens a session, writes ``SES:current``
- ``cortex session status``      — shows active-session info
- ``cortex session consolidate`` — compresses activity into ``SES:last``,
                                   extracts LNG proposals when patterns
                                   are detected
- ``cortex session close``       — closes the session, runs decay,
                                   updates the index

The session state is stored *in* ``brain.cortex`` itself, as
``SES:current`` (while running) and ``SES:last`` (after close). This
keeps the engine stateless across runs — the brain IS the session
ledger.

A sidecar cache file ``.cortex/cache/session.json`` records the
session id, start timestamp, brain hash at start, counters and a
rolling list of "session events" (modifications, candidate detections).
The cache is rebuildable: if it is lost, the engine falls back to
the ``SES:current`` entry in ``brain.cortex``.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.ast import CortexDocument, Entry, normalize_section_id
from ..core.parser import build_entry_from_value, parse_cortex
from ..core.writer import write_cortex
from .errors import LearningError
from .workspace import Workspace


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SESSION_CACHE_NAME = "session.json"
SES_CURRENT_NAME = "current"
SES_LAST_NAME = "last"
DEFAULT_SESSION_SECTION = "$4"  # SESSIONS section


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
    """In-memory representation of the session cache."""

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
            entries_modified=int(data.get("entries_modified", 0)),
            candidates_detected=int(data.get("candidates_detected", 0)),
            status=data.get("status", "running"),
            survive=data.get("survive", "min"),
            events=events,
        )


# ---------------------------------------------------------------------------
# Time helpers (UTC, ISO-8601)
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    """Current UTC time as ISO-8601 string. Deterministic per call."""

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_date() -> str:
    """Current UTC date as ``YYYY-MM-DD``."""

    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _new_session_id() -> str:
    """Generate a unique session id of the form ``YYYY-MM-DD-NNN``.

    The ``NNN`` suffix is a random 3-digit number to avoid collisions
    across same-day sessions. The id is NOT used for scoring, so the
    non-determinism here does not violate the engine's overall
    determinism guarantee (scores depend on brain + policy + engine
    version, never on the session id).
    """

    return f"{_now_date()}-{uuid.uuid4().hex[:6]}"


def _parse_duration_seconds(start: str, end: str) -> int:
    """Return the duration between two ISO-8601 UTC timestamps, in seconds."""

    fmt = "%Y-%m-%dT%H:%M:%SZ"
    try:
        t0 = datetime.strptime(start, fmt).replace(tzinfo=timezone.utc)
        t1 = datetime.strptime(end, fmt).replace(tzinfo=timezone.utc)
        return max(0, int((t1 - t0).total_seconds()))
    except Exception:
        return 0


def _format_duration(seconds: int) -> str:
    """Format a duration as ``"3h"`` / ``"45m"`` / ``"30s"``."""

    if seconds >= 3600:
        return f"{seconds // 3600}h"
    if seconds >= 60:
        return f"{seconds // 60}m"
    return f"{seconds}s"


# ---------------------------------------------------------------------------
# Cache load / save
# ---------------------------------------------------------------------------


def session_cache_path(workspace: Workspace) -> Path:
    return workspace.cache_dir / SESSION_CACHE_NAME


def load_session_state(workspace: Workspace) -> Optional[SessionState]:
    """Load the session cache. Returns ``None`` if absent or unreadable."""

    p = session_cache_path(workspace)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return SessionState.from_dict(data)
    except Exception:
        return None


def save_session_state(workspace: Workspace, state: SessionState) -> None:
    """Persist the session cache to disk."""

    workspace.ensure_dirs()
    p = session_cache_path(workspace)
    p.write_text(json.dumps(state.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Brain-side SES:current / SES:last management
# ---------------------------------------------------------------------------


def _find_ses_entry(brain_doc: CortexDocument, name: str) -> Optional[Entry]:
    for sec, e in brain_doc.iter_entries():
        if e.sigil == "SES" and e.name == name:
            return e
    return None


def _replace_or_add_entry(
    brain_doc: CortexDocument,
    section_id: str,
    sigil: str,
    name: str,
    value: Dict[str, Any],
    *,
    section_title: str = "",
) -> None:
    """Replace an entry (by sigil+name) or append it to the section."""

    sec_id = normalize_section_id(section_id)
    sec = brain_doc.get_section(sec_id)
    if sec is None:
        sec = brain_doc.get_or_create_section(sec_id, title=section_title)
    new_entry = build_entry_from_value(sec_id, sigil, name, "attrs", value)
    for i, e in enumerate(sec.entries):
        if e.sigil == sigil and e.name == name:
            sec.entries[i] = new_entry
            return
    sec.entries.append(new_entry)


def _write_brain(workspace: Workspace, brain_doc: CortexDocument) -> None:
    """Serialize + atomic write the brain back to disk."""

    new_text = write_cortex(brain_doc)
    # Re-parse to validate
    parse_cortex(new_text)
    tmp = workspace.brain_path.with_suffix(workspace.brain_path.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(workspace.brain_path)


# ---------------------------------------------------------------------------
# Public session commands
# ---------------------------------------------------------------------------


def session_start(workspace: Workspace, *, input_text: str = "") -> SessionState:
    """Start a new session.

    - Creates a fresh :class:`SessionState` (or reuses the running one
      if the caller explicitly asks).
    - Writes ``SES:current{...}`` into ``brain.cortex``.
    - Records ``brain_hash_at_start`` for later delta computation.

    Raises :class:`LearningError` if a session is already running.
    """

    existing = load_session_state(workspace)
    if existing is not None and existing.status == "running":
        raise LearningError(
            "LE014_SESSION_ALREADY_RUNNING",
            f"session {existing.session_id!r} is still running; "
            "run `cortex session close` first",
        )

    brain_doc = workspace.parse_brain()
    brain_hash = workspace.brain_hash()
    state = SessionState(
        session_id=_new_session_id(),
        start=_now_iso(),
        brain_hash_at_start=brain_hash,
        status="running",
        survive="min",
    )
    # Write SES:current into the brain.
    ses_value = {
        "id": state.session_id,
        "start": state.start,
        "brain_hash": brain_hash,
        "entries_modified": 0,
        "candidates_detected": 0,
        "status": "running",
        "survive": "min",
    }
    if input_text:
        ses_value["input"] = input_text
    _replace_or_add_entry(brain_doc, DEFAULT_SESSION_SECTION, "SES", SES_CURRENT_NAME, ses_value,
                          section_title="SESSIONS")
    _write_brain(workspace, brain_doc)
    save_session_state(workspace, state)
    return state


def session_status(workspace: Workspace) -> Dict[str, Any]:
    """Return a status dict for the current session.

    If no session is running, returns ``{"active": False, ...}``.
    """

    state = load_session_state(workspace)
    if state is None or state.status != "running":
        return {
            "active": False,
            "message": "no active session (run `cortex session start`)",
        }
    # Re-read brain to compute live counters from SES:current
    brain_doc = workspace.parse_brain()
    ses_current = _find_ses_entry(brain_doc, SES_CURRENT_NAME)
    duration_seconds = _parse_duration_seconds(state.start, _now_iso())
    return {
        "active": True,
        "session_id": state.session_id,
        "start": state.start,
        "duration": _format_duration(duration_seconds),
        "duration_seconds": duration_seconds,
        "brain_hash_at_start": state.brain_hash_at_start,
        "current_brain_hash": workspace.brain_hash(),
        "entries_modified": state.entries_modified,
        "candidates_detected": state.candidates_detected,
        "events": len(state.events),
        "ses_current_in_brain": ses_current is not None,
    }


def session_event(
    workspace: Workspace,
    *,
    kind: str,
    selector: str = "",
    detail: str = "",
) -> SessionState:
    """Record a session event and update counters.

    Used by ``handlers.post_action`` to log modifications and by
    ``candidates.detect_candidates`` (via the CLI) to log detections.
    """

    state = load_session_state(workspace)
    if state is None or state.status != "running":
        raise LearningError(
            "LE015_SESSION_NOT_RUNNING",
            "no active session; run `cortex session start` first",
        )
    event = SessionEvent(
        kind=kind, selector=selector, detail=detail, timestamp=_now_iso(),
    )
    state.events.append(event)
    if kind == "modify":
        state.entries_modified += 1
    elif kind == "candidate":
        state.candidates_detected += 1
    save_session_state(workspace, state)

    # Update SES:current counters in the brain too (best-effort).
    try:
        brain_doc = workspace.parse_brain()
        ses = _find_ses_entry(brain_doc, SES_CURRENT_NAME)
        if ses is not None and isinstance(ses.value, dict):
            ses.value["entries_modified"] = state.entries_modified
            ses.value["candidates_detected"] = state.candidates_detected
            _write_brain(workspace, brain_doc)
    except Exception:
        pass
    return state


def session_consolidate(
    workspace: Workspace,
    *,
    input_text: str = "",
    output_text: str = "",
    outcome_text: str = "",
) -> Dict[str, Any]:
    """Consolidate the running session into ``SES:last``.

    Returns a dict describing the consolidation. Does NOT close the
    session — call :func:`session_close` for that.
    """

    state = load_session_state(workspace)
    if state is None or state.status != "running":
        raise LearningError(
            "LE015_SESSION_NOT_RUNNING",
            "no active session to consolidate",
        )
    end = _now_iso()
    duration_seconds = _parse_duration_seconds(state.start, end)
    ses_last_value = {
        "id": state.session_id,
        "input": input_text or "(not specified)",
        "output": output_text or "(not specified)",
        "outcome": outcome_text or "(not specified)",
        "date": _now_date(),
        "duration": _format_duration(duration_seconds),
        "score": state.candidates_detected,
        "survive": "recovery",
        "entries_modified": state.entries_modified,
        "candidates_detected": state.candidates_detected,
    }
    brain_doc = workspace.parse_brain()
    _replace_or_add_entry(brain_doc, DEFAULT_SESSION_SECTION, "SES", SES_LAST_NAME, ses_last_value,
                          section_title="SESSIONS")
    _write_brain(workspace, brain_doc)
    state.status = "consolidated"
    state.end = end
    save_session_state(workspace, state)
    return {
        "consolidated": True,
        "session_id": state.session_id,
        "duration": _format_duration(duration_seconds),
        "entries_modified": state.entries_modified,
        "candidates_detected": state.candidates_detected,
        "ses_last_selector": "SES:last",
    }


def session_close(
    workspace: Workspace,
    *,
    consolidate: bool = True,
    input_text: str = "",
    output_text: str = "",
    outcome_text: str = "",
    run_decay: bool = True,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Close the running session.

    Sequence:

    1. If ``consolidate=True`` AND the session is still ``running``,
       run :func:`session_consolidate` first. (If the session is
       already ``consolidated``, skip — the consolidation already
       happened.)
    2. If ``run_decay=True``, apply decay over the learn-index entries.
    3. Remove ``SES:current`` from ``brain.cortex`` (keep ``SES:last``).
    4. Mark the session state as ``closed`` and persist.
    """

    state = load_session_state(workspace)
    if state is None or state.status not in ("running", "consolidated"):
        raise LearningError(
            "LE015_SESSION_NOT_RUNNING",
            "no active session to close",
        )

    consolidation = None
    if consolidate and state.status == "running":
        consolidation = session_consolidate(
            workspace,
            input_text=input_text,
            output_text=output_text,
            outcome_text=outcome_text,
        )
        # Reload state after consolidation
        state = load_session_state(workspace)

    decay_report = None
    if run_decay:
        from .decay import apply_decay_to_index
        from .index import load_or_rebuild, save_index
        idx = load_or_rebuild(workspace)
        if now is None:
            now_dt = datetime.now(timezone.utc)
        else:
            now_dt = now
        # Load policy set for cooling config
        from .policy import parse_policy_document
        ps = parse_policy_document(workspace.parse_policy())
        brain_doc = workspace.parse_brain()
        idx, decay_report = apply_decay_to_index(idx, ps, now_dt, brain_doc=brain_doc)
        save_index(idx, workspace.index_path)

    # Remove SES:current from brain (keep SES:last)
    brain_doc = workspace.parse_brain()
    for sec in brain_doc.sections:
        if sec.id != normalize_section_id(DEFAULT_SESSION_SECTION):
            continue
        sec.entries = [e for e in sec.entries if not (e.sigil == "SES" and e.name == SES_CURRENT_NAME)]
    _write_brain(workspace, brain_doc)

    state.status = "closed"
    state.end = _now_iso()
    save_session_state(workspace, state)

    return {
        "closed": True,
        "session_id": state.session_id,
        "consolidation": consolidation,
        "decay": decay_report.to_dict() if decay_report else None,
    }


__all__ = [
    "SessionEvent",
    "SessionState",
    "session_start",
    "session_status",
    "session_event",
    "session_consolidate",
    "session_close",
    "load_session_state",
    "save_session_state",
    "session_cache_path",
    "DEFAULT_SESSION_SECTION",
    "SES_CURRENT_NAME",
    "SES_LAST_NAME",
]
