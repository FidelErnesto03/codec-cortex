# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Document handle — unified transport wrapper for any CORTEX dialect.

Provides a :class:`DocumentHandle` that wraps an AST with dialect metadata
and diagnostics, plus adapters that let consumers load, render, and
roundtrip documents without knowing which parser/writer to call.

M4: eliminate the implicit v2-to-v1 downcast in ``load_doc()``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .ast import CortexDocument, compute_document_hash
from .errors import CortexError


# ---------------------------------------------------------------------------
# Enums and data types
# ---------------------------------------------------------------------------


class Dialect(str, Enum):
    """Known CORTEX dialects that the handle system can transport."""

    CORE = "core"
    V2 = "v2"
    HCORTEX = "hcortex"


@dataclass
class Diagnostic:
    """A single diagnostic attached to a document."""

    code: str
    message: str
    severity: str  # "error" | "warning" | "info"
    line: Optional[int] = None


@dataclass
class DocumentHandle:
    """Unified transport wrapper around any CORTEX dialect AST.

    ``dialect`` identifies which parser produced the AST.
    ``source`` is the file path or ``<string>`` for in-memory content.
    ``source_hash`` is the SHA256 of the source text.
    ``ast`` holds the dialect-specific AST object.
    ``diagnostics`` collects non-fatal findings discovered during loading.

    Consumers should inspect ``dialect`` before accessing ``ast`` to
    determine which concrete type it holds.

    Roundtrip guarantee::

        handle = adapter.load(path)
        text   = adapter.render(handle)
        assert text == open(path).read()
    """

    dialect: Dialect
    source: str
    source_hash: str
    ast: Any  # CortexDocument (Core / HCORTEX) or CortexV2Document (V2)
    diagnostics: List[Diagnostic] = field(default_factory=list)

    @property
    def is_core(self) -> bool:
        return self.dialect == Dialect.CORE

    @property
    def is_v2(self) -> bool:
        return self.dialect == Dialect.V2

    @property
    def is_hcortex(self) -> bool:
        return self.dialect == Dialect.HCORTEX

    def core_ast(self) -> CortexDocument:
        """Return the AST as a v1 :class:`CortexDocument`.

        Raises ``TypeError`` if the dialect is not Core or HCORTEX.
        """
        if self.dialect in (Dialect.CORE, Dialect.HCORTEX):
            return self.ast
        raise TypeError(
            f"cannot return CortexDocument for dialect {self.dialect!r}; "
            f"use adapter or convert first"
        )


# ---------------------------------------------------------------------------
# Abstract adapter
# ---------------------------------------------------------------------------


class DocumentAdapter(ABC):
    """Interface for loading and rendering documents in a specific dialect."""

    @abstractmethod
    def load(self, source: str) -> DocumentHandle:
        """Read a file and produce a :class:`DocumentHandle`."""
        ...

    @abstractmethod
    def loads(self, text: str, source: str = "<string>") -> DocumentHandle:
        """Parse text and produce a :class:`DocumentHandle`."""
        ...

    @abstractmethod
    def render(self, handle: DocumentHandle) -> str:
        """Render a :class:`DocumentHandle` back to source text."""
        ...


# ---------------------------------------------------------------------------
# Core adapter (v1)
# ---------------------------------------------------------------------------


class CoreDocumentAdapter(DocumentAdapter):
    """Adapter for v1 (Core) CORTEX documents.

    Uses ``parse_cortex()`` from :mod:`cortex.core.parser` and
    ``write_cortex()`` from :mod:`cortex.core.writer`.
    """

    def load(self, source: str) -> DocumentHandle:
        import os

        if not os.path.exists(source):
            raise CortexError("E013_NOT_FOUND", f"file not found: {source}")
        with open(source, "r", encoding="utf-8") as f:
            text = f.read()
        return self.loads(text, source=source)

    def loads(self, text: str, source: str = "<string>") -> DocumentHandle:
        from .parser import parse_cortex

        source_hash = compute_document_hash(text)
        doc = parse_cortex(text, path=source)
        handle = DocumentHandle(
            dialect=Dialect.CORE,
            source=source,
            source_hash=source_hash,
            ast=doc,
        )
        # Promote parser diagnostics
        for d in doc.diagnostics:
            handle.diagnostics.append(
                Diagnostic(
                    code=d.get("code", "UNKNOWN"),
                    message=d.get("message", ""),
                    severity=d.get("severity", "warning"),
                    line=d.get("line"),
                )
            )
        return handle

    def render(self, handle: DocumentHandle) -> str:
        from .writer import write_cortex

        doc = handle.core_ast()
        return write_cortex(doc)


# ---------------------------------------------------------------------------
# V2 adapter
# ---------------------------------------------------------------------------


class V2DocumentAdapter(DocumentAdapter):
    """Adapter for CORTEX v2 documents.

    Uses ``parse_cortex_v2()`` from :mod:`cortex.v2.parser` and
    ``write_cortex_v2()`` from :mod:`cortex.v2.writer` — **no** v1
    downcast.
    """

    def load(self, source: str) -> DocumentHandle:
        import os

        if not os.path.exists(source):
            raise CortexError("E013_NOT_FOUND", f"file not found: {source}")
        with open(source, "r", encoding="utf-8") as f:
            text = f.read()
        return self.loads(text, source=source)

    def loads(self, text: str, source: str = "<string>") -> DocumentHandle:
        from ..v2.parser import parse_cortex_v2

        source_hash = compute_document_hash(text)
        doc = parse_cortex_v2(text)
        return DocumentHandle(
            dialect=Dialect.V2,
            source=source,
            source_hash=source_hash,
            ast=doc,
        )

    def render(self, handle: DocumentHandle) -> str:
        from ..v2.writer import write_cortex_v2

        doc = handle.ast
        return write_cortex_v2(doc)


# ---------------------------------------------------------------------------
# HCORTEX adapter
# ---------------------------------------------------------------------------


class HCortexDocumentAdapter(DocumentAdapter):
    """Adapter for HCORTEX-EDIT documents.

    Uses ``parse_hcortex_edit()`` from :mod:`cortex.hcortex.edit_parser`
    and ``render_hcortex_edit()`` from :mod:`cortex.hcortex.edit_renderer`.
    The AST is a v1 :class:`CortexDocument`.
    """

    def load(self, source: str) -> DocumentHandle:
        import os

        if not os.path.exists(source):
            raise CortexError("E013_NOT_FOUND", f"file not found: {source}")
        with open(source, "r", encoding="utf-8") as f:
            text = f.read()
        return self.loads(text, source=source)

    def loads(self, text: str, source: str = "<string>") -> DocumentHandle:
        from ..hcortex.edit_parser import parse_hcortex_edit

        source_hash = compute_document_hash(text)
        doc = parse_hcortex_edit(text, source=source)
        handle = DocumentHandle(
            dialect=Dialect.HCORTEX,
            source=source,
            source_hash=source_hash,
            ast=doc,
        )
        for d in doc.diagnostics:
            handle.diagnostics.append(
                Diagnostic(
                    code=d.get("code", "UNKNOWN"),
                    message=d.get("message", ""),
                    severity=d.get("severity", "warning"),
                    line=d.get("line"),
                )
            )
        return handle

    def render(self, handle: DocumentHandle) -> str:
        from ..hcortex.edit_renderer import render_hcortex_edit

        doc = handle.core_ast()
        return render_hcortex_edit(doc)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_ADAPTER_REGISTRY: Dict[Dialect, DocumentAdapter] = {}


def adapter_for(dialect: Dialect) -> DocumentAdapter:
    """Return a cached :class:`DocumentAdapter` for the given dialect."""
    if dialect not in _ADAPTER_REGISTRY:
        if dialect == Dialect.CORE:
            _ADAPTER_REGISTRY[dialect] = CoreDocumentAdapter()
        elif dialect == Dialect.V2:
            _ADAPTER_REGISTRY[dialect] = V2DocumentAdapter()
        elif dialect == Dialect.HCORTEX:
            _ADAPTER_REGISTRY[dialect] = HCortexDocumentAdapter()
        else:
            raise ValueError(f"unknown dialect: {dialect!r}")
    return _ADAPTER_REGISTRY[dialect]


# ---------------------------------------------------------------------------
# Dialect detection
# ---------------------------------------------------------------------------


def detect_dialect(text: str) -> Dialect:
    """Detect the CORTEX dialect from source text.

    Heuristics (checked in order):

    1. If the text starts with ````` ``` `` (markdown code fence) or
       contains ``<!-- CODEC-CORTEX`` — it is **V2**.
    2. If the text starts with ``cortex-render: hcortex-edit`` — it is
       **HCORTEX**.
    3. Otherwise — **CORE** (v1 bare CORTEX).
    """
    stripped = text.lstrip()

    # V2 detection: markdown wrapper or CODEC-CORTEX header
    if stripped.startswith("```") or "<!-- CODEC-CORTEX" in text:
        return Dialect.V2

    # HCORTEX detection: the ``cortex-render: hcortex-edit`` marker
    # appears inside an HTML comment: ``<!-- cortex-render: ... -->``
    for line in stripped.split("\n"):
        line = line.strip()
        if "cortex-render: hcortex-edit" in line:
            return Dialect.HCORTEX
        # Skip blank lines and unrelated HTML comments before the declaration
        if line and not line.startswith("#") and not line.startswith("<!--"):
            break

    # Default: v1 Core
    return Dialect.CORE
