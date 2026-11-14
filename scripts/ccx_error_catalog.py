#!/usr/bin/env python3
"""Verify the closed error catalog (spec §9, AC-05).

Invariant: catalog == emitted ∪ declared-reserved.

- Every code listed in docs/standard/errors-1.0.md must have an emitter in at
  least one of the five surfaces, or be declared reserved/collision-documented.
- Every code emitted by a surface must appear in the catalog.

Exit code 0 when the invariant holds, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "standard" / "errors-1.0.md"

CODE_RE = re.compile(r"^[A-Z][0-9]{3}(?:_[A-Z0-9_]+)?$")
QUOTED_RE = re.compile(r"[\"'`]([A-Z][0-9]{3}(?:_[A-Z0-9_]+)?)[\"'`]")
BASH_EMIT_RE = re.compile(r"\bccx_error\s+\"?([A-Z][0-9]{3}(?:_[A-Z0-9_]+)?)")

SURFACES = {
    "python": ["codec_cortex/**/*.py"],
    "go": ["codec-cortex-go/cortex/*.go", "codec-cortex-go/cmd/**/*.go"],
    "node": ["codec-cortex-node/src/*.js", "codec-cortex-node/bin/*.js"],
    "rust": ["codec-cortex-rs/src/**/*.rs"],
    "bash": ["codec-cortex-bash/lib/*.sh", "codec-cortex-bash/bin/*"],
}

SKIP_PARTS = {"target", "bin", "vendor", "__pycache__", "node_modules"}


def catalog_codes() -> set[str]:
    codes: set[str] = set()
    for line in CATALOG.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cell = line.split("|")[1].strip().strip("`")
        if CODE_RE.match(cell):
            codes.add(cell)
    return codes


def declared_extras() -> set[str]:
    """Codes documented outside the emitter table (reserved, collisions, legacy)."""
    text = CATALOG.read_text(encoding="utf-8")
    start = text.find("## Códigos reservados y colisiones conocidas")
    if start < 0:
        return set()
    end = text.find("\n## ", start + 3)
    block = text[start:] if end < 0 else text[start:end]
    pattern = r"(?<![A-Z0-9_])[A-Z][0-9]{3}(?:_[A-Z0-9_]+)?"
    return {match for match in re.findall(r"`(" + pattern + r")`", block)}


def emitted_codes(patterns: list[str]) -> set[str]:
    found: set[str] = set()
    for pattern in patterns:
        for path in ROOT.glob(pattern):
            if SKIP_PARTS & set(path.parts):
                continue
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            found.update(QUOTED_RE.findall(text))
            found.update(BASH_EMIT_RE.findall(text))
    return found


TABLE_HEADER = "| Código | python | go | node | rust | bash |"
SURFACE_ORDER = ["python", "go", "node", "rust", "bash"]


def rewrite_table(emitted: dict[str, set[str]]) -> None:
    lines = CATALOG.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(TABLE_HEADER)
    except ValueError:
        raise SystemExit("table header not found in errors-1.0.md")
    end = start + 2
    while end < len(lines) and lines[end].startswith("|"):
        end += 1
    codes = sorted(set().union(*emitted.values()))
    table = [TABLE_HEADER, "|---|---|---|---|---|---|"]
    for code in codes:
        marks = ["x" if code in emitted[surface] else "—" for surface in SURFACE_ORDER]
        table.append("| " + code + " | " + " | ".join(marks) + " |")
    CATALOG.write_text("\n".join(lines[:start] + table + lines[end:]) + "\n", encoding="utf-8")
    print(f"catalog table rewritten with {len(codes)} codes")


def main() -> int:
    if "--write" in sys.argv[1:]:
        rewrite_table({surface: emitted_codes(patterns) for surface, patterns in SURFACES.items()})
        return 0

    catalog = catalog_codes()
    extras = declared_extras()
    emitted = {surface: emitted_codes(patterns) for surface, patterns in SURFACES.items()}
    union = set().union(*emitted.values())

    undocumented = sorted(union - catalog - extras)
    orphaned = sorted(code for code in catalog if code not in union)

    print(f"catalog codes: {len(catalog)}")
    for surface, codes in emitted.items():
        print(f"  {surface}: {len(codes)}")
    print(f"emitted union: {len(union)}")

    if orphaned:
        print("\ncatalog codes with no emitter and no reservation:")
        for code in orphaned:
            print(f"  {code}")
    if undocumented:
        print("\nemitted codes missing from the catalog:")
        for code in undocumented:
            print(f"  {code}")

    if orphaned or undocumented:
        print("\nFAIL error catalog is not closed")
        return 1
    print(f"OK catalog closed (declared extras: {', '.join(sorted(extras)) or 'none'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
