#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Domain facade — the stable public API (U2/U3).

Thin, documented wrappers over the dispatcher internals. The underlying
modules (parser, slotparser, slothcortex, hcortex, scalars, ...) remain
importable for compatibility; new code should use this facade.
"""

import re
from typing import List, Optional

from .dispatcher import parse_cortex, canonicalize as _canonicalize_doc, hash_cortex
from .parser import Document
from .scalars import ParseError
from . import hcortex as _hcortex_legacy
from . import slothcortex as _hcortex_slots

_ENVELOPE_VERSION_RE = re.compile(r"HCORTEX\s+v=(\S+)")


class CompileError(Exception):
    """HCORTEX compilation failed.

    Carries `.diagnostics`: a list of {code, message, ...} dicts, one per
    problem found (same shape the CLI prints).
    """

    def __init__(self, diagnostics: List[dict]):
        self.diagnostics = list(diagnostics)
        first = self.diagnostics[0] if self.diagnostics else {}
        super().__init__(
            f"{first.get('code', 'COMPILE_ERROR')}: "
            f"{first.get('message', 'compile failed')}"
        )


def parse(source: str) -> Document:
    """Parse CORTEX source (any declared dialect: 0.1, 0.2 or 1.0) into a Document AST."""
    return parse_cortex(source)


def validate(source: str) -> Document:
    """Validate CORTEX source; returns the Document or raises ParseError."""
    return parse_cortex(source)


def canonicalize(doc: Document) -> str:
    """Return the canonical CORTEX bytes (str) for a parsed Document."""
    return _canonicalize_doc(doc)


def hash(doc: Document) -> str:
    """Return the canonical hash of a Document as 'sha256:<hex>'."""
    digest = hash_cortex(doc)
    return digest if digest.startswith("sha256:") else f"sha256:{digest}"


def hash_source(source: str) -> str:
    """Parse CORTEX source and return its canonical 'sha256:<hex>' hash."""
    return hash(parse_cortex(source))


def to_hcortex(doc: Document, *, embed_ast: bool = False) -> str:
    """Render a Document to HCORTEX markdown (dispatches on the document dialect)."""
    if getattr(doc, "cortex_version", None) == "0.1":
        return _hcortex_legacy.render_hcortex(doc)
    return _hcortex_slots.render_hcortex_slots(doc, embed_ast=embed_ast)


def from_hcortex(source: str) -> Document:
    """Compile HCORTEX markdown back to a Document.

    Dispatches on the envelope version (v=0.1 legacy / v=0.2|1.0 slots).
    Raises CompileError carrying all diagnostics when compilation fails.
    """
    m = _ENVELOPE_VERSION_RE.search(source)
    version = m.group(1) if m else None
    if version == "0.1":
        doc, diags = _hcortex_legacy.compile_hcortex(source)
        normalized = [
            {"code": d.code, "severity": d.severity, "message": d.message, "line": d.line}
            for d in diags
        ]
    else:
        doc, normalized = _hcortex_slots.compile_hcortex_slots(source)
    if normalized:
        raise CompileError(normalized)
    return doc


__all__ = [
    "CompileError",
    "parse", "validate", "canonicalize", "hash", "hash_source",
    "to_hcortex", "from_hcortex",
]
