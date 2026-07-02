# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""``cortex docstring`` — derive compact Python help text from CORTEX API docs."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

_ATTR_RE = re.compile(r'(\w+):("[^"]*"|[^,}]+)')
_ENTRY_RE = re.compile(r'^(?P<sigil>[A-Z][A-Z0-9_]*):(?P<name>[A-Za-z_][A-Za-z0-9_]*)\{(?P<body>.*)\}\s*$', re.MULTILINE)
_BODY_RE = re.compile(r'^DESC:summary\{(?P<body>.*?)\}\s*$', re.MULTILINE | re.DOTALL)


class DocstringError(RuntimeError):
    pass


def _parse_attrs(body: str) -> Dict[str, str]:
    attrs: Dict[str, str] = {}
    for key, raw in _ATTR_RE.findall(body):
        value = raw.strip()
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        attrs[key] = value
    return attrs


def _candidate_roots(start: Optional[Path] = None) -> Iterable[Path]:
    cwd = (start or Path.cwd()).resolve()
    yield cwd
    yield from cwd.parents
    module_root = Path(__file__).resolve()
    yield module_root
    yield from module_root.parents


def resolve_docs_root(explicit: Optional[str] = None) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if path.is_dir():
            return path
        raise DocstringError(f"docs root not found: {path}")
    for base in _candidate_roots():
        candidate = base / "docs" / "cortex" / "api"
        if candidate.is_dir():
            return candidate
    raise DocstringError("docs/cortex/api not found; pass --docs-root")


def _summary_text(body: str) -> str:
    compact = " ".join(body.strip().split())
    attrs = _parse_attrs(compact)
    return attrs.get("text", compact)


def parse_api_doc(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    command: Dict[str, str] = {}
    arguments: List[Dict[str, str]] = []
    limits: List[Dict[str, str]] = []
    summary = ""
    summary_match = _BODY_RE.search(text)
    if summary_match:
        summary = _summary_text(summary_match.group("body"))
    for match in _ENTRY_RE.finditer(text):
        sigil = match.group("sigil")
        name = match.group("name")
        attrs = _parse_attrs(match.group("body"))
        attrs.setdefault("entry", name)
        if sigil == "IDN" and name == "command":
            command = attrs
        elif sigil == "ARG":
            arguments.append(attrs)
        elif sigil == "LIM":
            limits.append(attrs)
    if not command:
        raise DocstringError(f"missing IDN:command in {path}")
    if not summary:
        raise DocstringError(f"missing DESC:summary in {path}")
    return {"source": str(path), "command": command, "summary": summary, "arguments": arguments, "limits": limits}


def render_docstring(data: Dict[str, Any]) -> str:
    command = data["command"]
    cli = command.get("cli") or f"cortex {command.get('name', '')}".strip()
    lines = [
        "**Perfil: HCORTEX-REF**",
        "",
        f"| Comando | `{cli}` |",
        "|---|---|",
        f"| Status | {command.get('status', 'current')} |",
        f"| Requiere | {command.get('requires', 'cortex')} |",
        "",
        data["summary"],
        "",
        "| Argumento | Req | Descripción |",
        "|---|---|---|",
    ]
    for arg in data["arguments"]:
        lines.append(f"| `{arg.get('name', arg.get('entry', ''))}` | {arg.get('required', 'no')} | {arg.get('description', '')} |")
    if data["limits"]:
        lines.extend(["", "| Límite | Alcance |", "|---|---|"])
        for lim in data["limits"]:
            lines.append(f"| {lim.get('limit', '')} | {lim.get('scope', '')} |")
    return "\n".join(lines).strip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cortex docstring")
    parser.add_argument("command", nargs="?", help="command name, e.g. canonicalize")
    parser.add_argument("--all", action="store_true", help="generate docstrings for all API docs")
    parser.add_argument("--docs-root", default=None, help="directory containing docs/cortex/api/*.cortex")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser


def _iter_commands(docs_root: Path) -> List[str]:
    return sorted(p.stem for p in docs_root.glob("*.cortex"))


def run(args) -> int:
    docs_root = resolve_docs_root(getattr(args, "docs_root", None))
    commands = _iter_commands(docs_root) if getattr(args, "all", False) else [args.command]
    if not commands or commands == [None]:
        raise DocstringError("provide a command or --all")
    outputs = []
    for command in commands:
        path = docs_root / f"{command}.cortex"
        if not path.is_file():
            raise DocstringError(f"API doc not found: {path}")
        outputs.append({"command": command, "source": str(path), "docstring": render_docstring(parse_api_doc(path))})
    if getattr(args, "format", "text") == "json":
        print(json.dumps(outputs if len(outputs) > 1 else outputs[0], indent=2, ensure_ascii=False))
    else:
        for index, item in enumerate(outputs):
            if index:
                print("\n---\n")
            print(item["docstring"], end="")
    return 0
