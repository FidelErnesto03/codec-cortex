#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ideatic line emission (additive 1.x tooling — U4).

`emit` produces a valid, escaped CORTEX idea line from plain Python values,
so consumers stop hand-rolling esc() for quotes/newlines/tabs.
`emit_value` emits a single scalar literal with canonical escapes.
"""

import math
import re
from typing import Any, Dict, List, Optional, Union

from .scalars import Scalar, emit_string_literal, is_ascii_identifier

_IDEA_HEAD_RE = re.compile(r"^(!|[A-Z][A-Z0-9_]*)$")
_NAMESPACE_RE = re.compile(r"^[a-z][a-z0-9_.-]*$")
_DEC_RE = re.compile(r"^-?(0|[1-9][0-9]*)\.[0-9]+$")
# Mirrors the parser's idea-name grammar ([^{|}\s]+) and attr-key stops.
_IDEA_NAME_FORBIDDEN_RE = re.compile(r"[\s{}|]")
_ATTR_KEY_FORBIDDEN_RE = re.compile(r"[\s:,{}]")

_SHAPES = ("attrs", "attrs-pos", "relacion", "cuerpo", "bloque")


def _valid_idea_name(name: str) -> bool:
    return (is_ascii_identifier(name)
            and not _IDEA_NAME_FORBIDDEN_RE.search(name))


def _valid_attr_key(key: str) -> bool:
    return (is_ascii_identifier(key)
            and not _ATTR_KEY_FORBIDDEN_RE.search(key))


def emit_value(value: Any) -> str:
    """Emit the CORTEX literal for a Python value (canonical escapes).

    - str      -> quoted string literal (always escaped via emit_string_literal)
    - bool     -> true / false
    - int      -> integer lexeme
    - float    -> decimal lexeme (finite only)
    - None     -> null
    - list/tuple -> [v1,v2,...]
    - Scalar   -> its lexeme verbatim (full control: atoms, enums, ...)
    """
    if isinstance(value, Scalar):
        return value.lexeme
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"emit_value: non-finite float {value!r} has no CORTEX literal")
        lex = format(value, "f")
        if "." in lex:
            stripped = lex.rstrip("0").rstrip(".")
            lex = stripped if "." in stripped else stripped + ".0"
        if not _DEC_RE.match(lex):
            raise ValueError(f"emit_value: float {value!r} has no valid decimal lexeme")
        return lex
    if isinstance(value, str):
        return emit_string_literal(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(emit_value(v) for v in value) + "]"
    raise ValueError(f"emit_value: unsupported type {type(value).__name__}")


def emit(sigil: str, name: str, payload: Any = None, *,
         namespace: Optional[str] = None,
         shape: Optional[str] = None) -> str:
    """Emit a valid CORTEX idea line (escaped; no trailing newline).

    Shape is inferred from the payload when omitted:
      dict            -> attrs        SIG:name{key:value,...}
      list/tuple      -> attrs-pos    SIG:name|cell|cell|...
      str / None      -> cuerpo       SIG:name{text}  (multiline braces if '\\n' in text)
    Explicit `shape` accepts: attrs, attrs-pos, relacion, cuerpo, bloque.
    `shape="bloque"` always emits the multiline braced form.
    `namespace` emits the qualified head `ns::SIG:name`.
    """
    if not _IDEA_HEAD_RE.match(sigil or ""):
        raise ValueError(f"emit: invalid sigil {sigil!r} (expected ! or [A-Z][A-Z0-9_]*)")
    if not _valid_idea_name(name or ""):
        raise ValueError(f"emit: invalid idea name {name!r} (printable ASCII, no whitespace/{{}}|)")
    if namespace is not None and not _NAMESPACE_RE.match(namespace):
        raise ValueError(f"emit: invalid namespace {namespace!r}")

    if shape is None:
        if isinstance(payload, dict):
            shape = "attrs"
        elif isinstance(payload, (list, tuple)):
            shape = "attrs-pos"
        elif payload is None or isinstance(payload, str):
            shape = "cuerpo"
        else:
            raise ValueError(
                f"emit: cannot infer shape from payload type {type(payload).__name__}; "
                "pass shape= explicitly")
    if shape not in _SHAPES:
        raise ValueError(f"emit: unknown shape {shape!r} (expected one of {_SHAPES})")

    head = f"{namespace}::{sigil}:{name}" if namespace else f"{sigil}:{name}"

    if shape == "attrs":
        if not isinstance(payload, dict):
            raise ValueError("emit: attrs payload must be a dict {key: value}")
        parts = []
        for k, v in payload.items():
            if not _valid_attr_key(k):
                raise ValueError(f"emit: invalid attr key {k!r}")
            parts.append(f"{k}:{emit_value(v)}")
        return head + "{" + ",".join(parts) + "}"

    if shape in ("attrs-pos", "relacion"):
        if not isinstance(payload, (list, tuple)):
            raise ValueError(f"emit: {shape} payload must be a list of cells")
        return head + "|" + "|".join(emit_value(c) for c in payload)

    # cuerpo / bloque
    if payload is None:
        payload = ""
    if not isinstance(payload, str):
        raise ValueError(f"emit: {shape} payload must be a string body")
    if shape == "bloque" or "\n" in payload:
        return head + "{\n" + payload + "\n}"
    return head + "{" + payload + "}"


__all__ = ["emit", "emit_value"]
