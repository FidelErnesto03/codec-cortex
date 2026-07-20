#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORTEX 0.2 dispatcher: reads $0:format{cortex:X} and dispatches to 0.1 or 0.2.

NEW module. Does NOT touch 0.1 parser.py.
"""

import re
from typing import Optional

from .scalars import ParseError
from .parser import parse_cortex as _parse_cortex_legacy
from .slotparser import parse_slots
from .slots import check_mixed_surface_legacy
from .c14n import canonicalize as _canonicalize_legacy
from .slotc14n import canonicalize_slots, hash_legacy, hash_slots


def _detect_version(source: str) -> str:
    """Read $0:format{cortex:X} via minimal bootstrap (no global ※ scan)."""
    # Normalize line endings
    norm = source.replace("\r\n", "\n").replace("\r", "\n")
    m = re.search(r'^[ \t]*\$0:format\{([^}]*)\}', norm, re.MULTILINE)
    if not m:
        raise ParseError("G010_FORMAT_REQUIRED", "Missing $0:format declaration")
    attrs_str = m.group(1)
    cm = re.search(r'cortex:("([^"]*)"|([^,}\s]+))', attrs_str)
    if not cm:
        raise ParseError("G007_UNSUPPORTED_VERSION", "$0:format missing cortex version")
    version = cm.group(2) if cm.group(2) is not None else cm.group(3)
    if version not in ("0.1", "0.2"):
        raise ParseError("G007_UNSUPPORTED_VERSION", f"Unsupported cortex version: {version}")
    return version


def parse_cortex(source: str):
    """Dispatch by declared version. The ONLY signal is $0:format{cortex:X}.

    NEVER scans for ※ globally. If a 0.1 doc contains a structural ※ slot-ref,
    the 0.2-specific mixed-surface check fires (I058). ※ inside strings/cuerpo/bloque
    in 0.1 docs is ordinary content.
    """
    if source.startswith("\ufeff"):
        raise ParseError("U001_BOM_FORBIDDEN", "BOM forbidden")
    version = _detect_version(source)
    if version == "0.1":
        # I058: detect structural ※ slot-ref in 0.1 doc (conservative — only
        # structural refs with ASCII digits trigger; strings/cuerpo/bloque are
        # preserved as ordinary content per P01-P03).
        check_mixed_surface_legacy(source)
        return _parse_cortex_legacy(source)
    return parse_slots(source)


def canonicalize(doc):
    """Dispatch canonicalization by doc.cortex_version."""
    if doc.cortex_version == "0.1":
        return _canonicalize_legacy(doc)
    return canonicalize_slots(doc)


def hash_cortex(doc) -> str:
    """Dispatch hash by doc.cortex_version."""
    if doc.cortex_version == "0.1":
        return hash_legacy(doc)
    return hash_slots(doc)
