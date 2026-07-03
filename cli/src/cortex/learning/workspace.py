"""Workspace discovery and initialization for the learning engine.

A *workspace* is a project directory that contains a canonical
``.cortex/`` folder::

    .cortex/
      MANIFEST.cortex
      brain.cortex
      learn-policies.cortex
      index/
        learn-index.json
      cache/
        fingerprints.json
        candidates.json

The manifest declares the artefacts; the brain is the operational
memory; the policies are external; the index is rebuildable.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.ast import CortexDocument
from ..core.parser import parse_cortex
from .errors import (
    LE001_WORKSPACE_NOT_FOUND,
    LE002_MANIFEST_MISSING,
    LE003_BRAIN_MISSING,
    LearningError,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORKSPACE_DIR = ".cortex"
MANIFEST_NAME = "MANIFEST.cortex"
BRAIN_NAME = "brain.cortex"
POLICY_NAME = "learn-policies.cortex"
INDEX_DIR = "index"
INDEX_NAME = "learn-index.json"
CACHE_DIR = "cache"

DEFAULT_ENGINE_VERSION = "0.1.0"


# ---------------------------------------------------------------------------
# Workspace dataclass
# ---------------------------------------------------------------------------


@dataclass
class Workspace:
    """A resolved learning-engine workspace.

    ``policy_path`` and ``index_path`` may not exist on disk (the
    policies file is optional, the index is derived and rebuildable).
    The brain and manifest paths MUST exist for a workspace to be
    considered valid.
    """

    root: Path
    cortex_dir: Path
    manifest_path: Path
    brain_path: Path
    policy_path: Optional[Path]
    index_path: Path
    cache_dir: Path
    fingerprints_path: Path
    candidates_cache_path: Path
    manifest_doc: Optional[CortexDocument] = field(default=None, repr=False)

    # ----- discovery -------------------------------------------------------

    @classmethod
    def discover(cls, start: Optional[Path] = None) -> "Workspace":
        """Walk up from ``start`` (default: cwd) looking for ``.cortex/``.

        Raises :class:`LearningError` (LE001) if no workspace is found.
        """

        here = Path(start or os.getcwd()).resolve()
        for cand in [here, *here.parents]:
            cortex_dir = cand / WORKSPACE_DIR
            if cortex_dir.is_dir():
                return cls._from_cortex_dir(cortex_dir)
        raise LearningError(
            LE001_WORKSPACE_NOT_FOUND,
            f"no {WORKSPACE_DIR}/ workspace found starting from {here}",
        )

    @classmethod
    def _from_cortex_dir(cls, cortex_dir: Path) -> "Workspace":
        manifest = cortex_dir / MANIFEST_NAME
        if not manifest.exists():
            raise LearningError(
                LE002_MANIFEST_MISSING,
                f"missing {MANIFEST_NAME} in {cortex_dir}",
            )
        # Parse manifest to discover brain/policy paths (best-effort).
        # We don't fail hard if the manifest points elsewhere — the
        # canonical layout is the source of truth.
        try:
            manifest_text = manifest.read_text(encoding="utf-8")
            manifest_doc = parse_cortex(manifest_text, path=str(manifest))
        except Exception:
            manifest_doc = None
        brain_path = cortex_dir / BRAIN_NAME
        if not brain_path.exists():
            raise LearningError(
                LE003_BRAIN_MISSING,
                f"missing {BRAIN_NAME} in {cortex_dir}",
            )
        policy_path = cortex_dir / POLICY_NAME
        return cls(
            root=cortex_dir.parent,
            cortex_dir=cortex_dir,
            manifest_path=manifest,
            brain_path=brain_path,
            policy_path=policy_path if policy_path.exists() else None,
            index_path=cortex_dir / INDEX_DIR / INDEX_NAME,
            cache_dir=cortex_dir / CACHE_DIR,
            fingerprints_path=cortex_dir / CACHE_DIR / "fingerprints.json",
            candidates_cache_path=cortex_dir / CACHE_DIR / "candidates.json",
            manifest_doc=manifest_doc,
        )

    # ----- IO helpers ------------------------------------------------------

    def read_brain(self) -> str:
        return self.brain_path.read_text(encoding="utf-8")

    def read_policy(self) -> str:
        if self.policy_path is None or not self.policy_path.exists():
            return ""
        return self.policy_path.read_text(encoding="utf-8")

    def parse_brain(self) -> CortexDocument:
        return parse_cortex(self.read_brain(), path=str(self.brain_path))

    def parse_policy(self) -> CortexDocument:
        text = self.read_policy()
        if not text.strip():
            from .policy_defaults import default_policy_text
            text = default_policy_text()
        return parse_cortex(text, path=str(self.policy_path or self.cortex_dir / POLICY_NAME))

    def brain_hash(self) -> str:
        return _sha256_file(self.brain_path)

    def policy_hash(self) -> str:
        if self.policy_path is None or not self.policy_path.exists():
            return _sha256_text("")
        return _sha256_file(self.policy_path)

    def ensure_dirs(self) -> None:
        """Create ``index/`` and ``cache/`` directories if missing."""

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------


def _sha256_text(text: str) -> str:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"sha256:{h}"


def _sha256_file(path: Path) -> str:
    return _sha256_text(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


def init_workspace(root: Path, *, force: bool = False) -> Workspace:
    """Create a fresh ``.cortex/`` workspace under ``root``.

    Existing files are preserved unless ``force=True``. The function is
    idempotent: running it twice on the same workspace is a no-op
    (apart from re-creating missing directories).
    """

    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    cortex_dir = root / WORKSPACE_DIR
    cortex_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = cortex_dir / MANIFEST_NAME
    brain_path = cortex_dir / BRAIN_NAME
    policy_path = cortex_dir / POLICY_NAME
    index_dir = cortex_dir / INDEX_DIR
    cache_dir = cortex_dir / CACHE_DIR
    index_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Manifest
    if not manifest_path.exists() or force:
        manifest_path.write_text(_default_manifest_text(), encoding="utf-8")

    # Brain — only create if absent; never overwrite an existing brain
    # unless explicitly forced.
    if not brain_path.exists() or force:
        brain_path.write_text(_default_brain_text(), encoding="utf-8")

    # Policies
    if not policy_path.exists() or force:
        from .policy_defaults import default_policy_text
        policy_path.write_text(default_policy_text(), encoding="utf-8")

    return Workspace._from_cortex_dir(cortex_dir)


# ---------------------------------------------------------------------------
# Default artefact texts
# ---------------------------------------------------------------------------


def _default_manifest_text() -> str:
    return """# -- $0: GLOSSARY --
GSIG:IDN{sigil:"IDN", name:"identity", type:"attrs", risk:"B", description:"workspace identity"}
GSIG:REF{sigil:"REF", name:"reference", type:"attrs", risk:"B", description:"workspace file reference"}
GSIG:CNST{sigil:"CNST", name:"constraint", type:"attrs", risk:"H", description:"workspace hard rule"}

# -- $1: IDENTITY --
IDN:workspace{name:"codec_cortex_workspace", version:"0.1.0"}

# -- $2: FILES --
REF:brain{path:".cortex/brain.cortex", role:"operational_memory", required:true, canonical:true}
REF:learn_policy{path:".cortex/learn-policies.cortex", role:"learning_policy", required:false, canonical:true}
REF:learn_index{path:".cortex/index/learn-index.json", role:"learning_performance_index", required:false, canonical:false, rebuildable:true}

# -- $3: CONSTRAINTS --
CNST:no_direct_llm_mutation{rule:"LLM/SLM must request mutations through the learning engine", severity:"blocking"}
CNST:index_rebuildable{rule:"learning index is derived and rebuildable; it is not canonical memory", severity:"blocking"}
"""


def _default_brain_text() -> str:
    return """# -- $0: GLOSSARY --
GSIG:IDN{sigil:"IDN", name:"identity", type:"attrs", risk:"B", description:"identity descriptor"}
GSIG:DOM{sigil:"DOM", name:"domain", type:"attrs", risk:"B", description:"workspace domain"}
GSIG:FCS{sigil:"FCS", name:"focus", type:"attrs", risk:"H", description:"current focus"}
GSIG:OBJ{sigil:"OBJ", name:"objective", type:"attrs", risk:"H", description:"current objective"}
GSIG:WRK{sigil:"WRK", name:"work", type:"attrs", risk:"M", description:"work state"}
GSIG:STP{sigil:"STP", name:"step", type:"attrs", risk:"M", description:"next step"}
GSIG:CNST{sigil:"CNST", name:"constraint", type:"attrs", risk:"H", description:"hard rule"}
GSIG:SES{sigil:"SES", name:"session", type:"attrs", risk:"B", description:"session memory"}
GSIG:LNG{sigil:"LNG", name:"lesson", type:"attrs", risk:"M", description:"learned lesson"}
GSIG:KNW{sigil:"KNW", name:"knowledge", type:"attrs", risk:"M", description:"operational knowledge"}
GSIG:RSK{sigil:"RSK", name:"risk", type:"attrs", risk:"H", description:"risk"}
GSIG:NXT{sigil:"NXT", name:"next", type:"attrs", risk:"M", description:"next planned action"}
GSIG:REF{sigil:"REF", name:"reference", type:"attrs", risk:"B", description:"external reference"}

# -- $1: IDENTITY --
IDN:agent{name:"learning_engine_agent", role:"operator"}
IDN:human{name:"human", role:"architect"}
DOM:workspace{area:"learning", protocol:"CODEC-CORTEX", artifact:"brain.cortex"}

# -- $2: ACTIVE WORK --
FCS:primary{what:"bootstrap learning engine", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"valid workspace with index", status:"current", success:"learn doctor returns ok", survive:"min"}
WRK:state{phase:"bootstrap", current:"init", blocked:false, survive:"work"}
STP:next{action:"run cortex learn doctor", reason:"validate workspace", owner:"human", status:"current", survive:"min"}

# -- $3: GOVERNANCE --
CNST:self_contained{rule:"brain.cortex carries its own minimal $0", severity:"blocking", survive:"min"}
REF:learn_policy{path:".cortex/learn-policies.cortex", role:"external_learning_policy", required:false}
"""


# ---------------------------------------------------------------------------
# Doctor
# ---------------------------------------------------------------------------


@dataclass
class DoctorReport:
    """Result of ``cortex learn doctor``."""

    ok: bool
    workspace_root: str
    checks: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "workspace_root": self.workspace_root,
            "checks": list(self.checks),
        }


def doctor(workspace: Workspace) -> DoctorReport:
    """Validate the structural integrity of a workspace.

    Checks performed (each adds a dict to ``report.checks``):

    - ``cortex_dir`` exists
    - ``manifest`` exists and parses
    - ``brain`` exists and parses
    - ``policy`` (if present) parses
    - ``index`` is fresh or marked stale
    """

    report = DoctorReport(ok=True, workspace_root=str(workspace.root))
    overall_ok = True

    def _check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal overall_ok
        overall_ok = overall_ok and ok
        report.checks.append({"name": name, "ok": ok, "detail": detail})

    _check("cortex_dir", workspace.cortex_dir.is_dir(), str(workspace.cortex_dir))

    # Manifest
    if not workspace.manifest_path.exists():
        _check("manifest_exists", False, f"missing {workspace.manifest_path}")
    else:
        try:
            text = workspace.manifest_path.read_text(encoding="utf-8")
            parse_cortex(text, path=str(workspace.manifest_path))
            _check("manifest_parses", True)
        except Exception as e:
            _check("manifest_parses", False, str(e))

    # Brain
    if not workspace.brain_path.exists():
        _check("brain_exists", False, f"missing {workspace.brain_path}")
    else:
        try:
            workspace.parse_brain()
            _check("brain_parses", True)
        except Exception as e:
            _check("brain_parses", False, str(e))

    # Policy
    if workspace.policy_path is None or not workspace.policy_path.exists():
        _check("policy_present", False, "no learn-policies.cortex (optional)")
    else:
        try:
            workspace.parse_policy()
            _check("policy_parses", True)
        except Exception as e:
            _check("policy_parses", False, str(e))

    # Index freshness — a missing index is NOT a failure (it's rebuildable).
    # Only an existing-but-stale/corrupt index contributes to ``ok=False``.
    if not workspace.index_path.exists():
        _check("index_present", True, "absent (rebuildable; not a failure)")
    else:
        try:
            from .index import load_index, is_stale
            idx = load_index(workspace.index_path)
            brain_hash = workspace.brain_hash()
            policy_hash = workspace.policy_hash()
            stale = is_stale(idx, brain_hash, policy_hash)
            _check("index_fresh", not stale, "stale" if stale else "fresh")
        except Exception as e:
            _check("index_fresh", False, f"failed to load: {e}")

    report.ok = overall_ok
    return report


__all__ = [
    "Workspace",
    "DoctorReport",
    "doctor",
    "init_workspace",
    "WORKSPACE_DIR",
    "MANIFEST_NAME",
    "BRAIN_NAME",
    "POLICY_NAME",
    "INDEX_NAME",
    "DEFAULT_ENGINE_VERSION",
]
