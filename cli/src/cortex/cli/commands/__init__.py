# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Shared helpers for CLI command modules."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from ...core.ast import CortexDocument
from ...core.parser import parse_cortex
from ...core.errors import CortexError
from ...core.validator import validate


def load_doc(path: str) -> CortexDocument:
    """Read a .cortex file and parse it into a :class:`CortexDocument`.

    Handles both v1 (bare CORTEX) and v2 (markdown-wrapped with
    <!-- CODEC-CORTEX --> header) formats. For v2, uses the v2 parser
    and converts to v1 document format for compatibility with v1
    validation, CRUD, and CLI commands.
    """

    if not os.path.exists(path):
        raise CortexError("E013_NOT_FOUND", f"file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # Detect v2 format: markdown wrapper or CODEC-CORTEX header
    is_v2 = text.lstrip().startswith("```") or "<!-- CODEC-CORTEX" in text

    if not is_v2:
        return parse_cortex(text, path=path)

    # v2 format: use v2 parser, convert to v1 text, re-parse with v1 parser
    from ...v2.parser import parse_cortex_v2

    # Strip markdown wrapper for v2 parser
    inner = text
    if inner.startswith("```"):
        idx = inner.find("\n")
        if idx != -1:
            inner = inner[idx + 1 :]
        close_idx = inner.rfind("\n```")
        if close_idx != -1:
            inner = inner[:close_idx]

    v2_doc = parse_cortex_v2(inner)

    # Convert v2 doc to v1-compatible CORTEX text directly
    # (bypass write_cortex_v2 which outputs v2 format with wrapper/header)
    v1_parts: list[str] = []
    for sec in v2_doc.sections:
        v1_parts.append(sec.id)
        for entry in sec.entries:
            if entry.entry_type == "meta":
                v1_parts.append(f"$0:{entry.name}{{{_serialize_attrs_v1(entry.value)}}}")
            elif entry.entry_type == "sigil_decl":
                sig = "!" if entry.sigil == "!" else entry.sigil
                v1_parts.append(f"{sig}:{entry.name}{{{_serialize_attrs_v1(entry.value)}}}")
            elif entry.entry_type == "attrs-pos" and entry.sigil == "HDL":
                v = entry.value
                op = v.get("operation", entry.name)
                st = v.get("status", "")
                req = v.get("requires", "")
                notes = v.get("notes", "")
                v1_parts.append(f"HDL:{entry.name}|{op}|{st}|{req}|{notes}")
            elif entry.entry_type == "attrs":
                v1_parts.append(f"{entry.sigil}:{entry.name}{{{_serialize_attrs_v1(entry.value)}}}")
            elif entry.entry_type == "cuerpo":
                v1_parts.append(f"{entry.sigil}:{entry.name}{{{entry.value}}}")
            elif entry.entry_type == "bloque":
                v1_parts.append(f"{entry.sigil}:{entry.name}{{{entry.value}}}")
        v1_parts.append("")
    v1_text = "\n".join(v1_parts)

    return parse_cortex(v1_text, path=path)


def _serialize_attrs_v1(attrs: dict) -> str:
    """Serialize attrs dict to v1 CORTEX format: key:value,key2:\"value2\""""
    parts = []
    for k, v in attrs.items():
        if isinstance(v, str) and (" " in v or "," in v or "{" in v or "}" in v or '"' in v or "—" in v):
            escaped = v.replace("\\", "\\\\").replace('"', '\\"')
            parts.append(f'{k}:"{escaped}"')
        else:
            parts.append(f"{k}:{v}")
    return ",".join(parts)


def emit(payload: Dict[str, Any], *, json_mode: bool = False) -> None:
    """Print a payload as JSON or as plain text.

    ``payload`` must contain ``text`` (str) for plain mode and any
    JSON-serialisable fields for JSON mode.
    """

    if json_mode:
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        text = payload.get("text", "")
        if text:
            print(text)


def emit_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


def post_mutation_gate(
    doc: CortexDocument,
    args,
) -> Optional[Dict[str, Any]]:
    """Validate ``doc`` after a mutation and return an error payload if blocked.

    v1.1.2: centralised post-mutation validation used by ``add``,
    ``update``, ``delete`` and ``move``.

    v1.1.3 P0-2/P0-3: errors tagged ``bypassable=False`` (secrets in clear
    text, critical sigils incomplete) CANNOT be overridden by ``--force``.
    Only an explicit ``--unsafe-allow-secret-forensics`` flag (for secrets)
    can bypass the secret check, and there is NO bypass for critical-sigil
    incompleteness.

    Behaviour:
      - If ``--no-validate-write`` is set, return None (skip gate) — but
        only if there are no ``bypassable=False`` errors.
      - Run ``validate(doc, strict=args.strict_write)``.
      - If there are error-severity diagnostics:
          * ``bypassable=False`` errors ALWAYS block (unless the dedicated
            ``--unsafe-allow-secret-forensics`` flag is set, and only for
            secret-related codes).
          * Other errors block unless ``--force`` is set.
      - Otherwise return None (mutation can proceed to atomic_write).
    """

    if getattr(args, "no_validate_write", False):
        # Even with --no-validate-write, bypassable=False errors block
        strict_write = getattr(args, "strict_write", False)
        diagnostics = validate(doc, strict=strict_write)
        non_bypassable = [
            d for d in diagnostics
            if d.get("severity") == "error" and d.get("bypassable") is False
        ]
        if non_bypassable:
            # Filter: allow --unsafe-allow-secret-forensics for secret codes
            unsafe = getattr(args, "unsafe_allow_secret_forensics", False)
            if unsafe:
                non_bypassable = [
                    d for d in non_bypassable
                    if d.get("code") != "E031_SECRET_NOT_BYPASSABLE"
                ]
            if non_bypassable:
                return {
                    "ok": False,
                    "error": {
                        "code": "E015_ATOMIC_WRITE_FAILED",
                        "message": (
                            f"mutation would produce {len(non_bypassable)} "
                            "non-bypassable error(s); --no-validate-write cannot "
                            "override security/governance rules"
                        ),
                    },
                    "diagnostics": non_bypassable,
                }
        return None

    strict_write = getattr(args, "strict_write", False)
    diagnostics = validate(doc, strict=strict_write)
    errors = [d for d in diagnostics if d.get("severity") == "error"]
    if not errors:
        return None

    # Split bypassable vs non-bypassable
    non_bypassable = [d for d in errors if d.get("bypassable") is False]
    bypassable = [d for d in errors if d.get("bypassable") is not False]

    # Non-bypassable errors always block (except secrets with --unsafe flag)
    if non_bypassable:
        unsafe = getattr(args, "unsafe_allow_secret_forensics", False)
        if unsafe:
            # Allow bypassing secret errors ONLY with the dedicated flag
            non_bypassable = [
                d for d in non_bypassable
                if d.get("code") != "E031_SECRET_NOT_BYPASSABLE"
            ]
        if non_bypassable:
            return {
                "ok": False,
                "error": {
                    "code": "E015_ATOMIC_WRITE_FAILED",
                    "message": (
                        f"mutation would produce {len(non_bypassable)} "
                        "non-bypassable error(s); --force cannot override "
                        "security/governance rules (use "
                        "--unsafe-allow-secret-forensics for forensic "
                        "recovery of secrets, if absolutely necessary)"
                    ),
                },
                "diagnostics": non_bypassable,
            }

    # Bypassable errors: block unless --force
    if bypassable and not getattr(args, "force", False):
        return {
            "ok": False,
            "error": {
                "code": "E015_ATOMIC_WRITE_FAILED",
                "message": (
                    f"mutation would produce {len(bypassable)} validation error(s); "
                    "use --force to persist anyway, or --no-validate-write to skip"
                ),
            },
            "diagnostics": bypassable,
        }
    return None
