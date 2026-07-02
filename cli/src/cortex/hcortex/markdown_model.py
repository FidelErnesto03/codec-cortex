# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Markdown model for HCORTEX renderers.

Defines the small set of markers used by the EDIT renderer to embed
structural metadata that the EDIT parser can recover losslessly.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


# Header lines (first line of file)
HCORTEX_READ_HEADER = "<!-- cortex-render: hcortex-read; roundtrip: false -->"
HCORTEX_EDIT_HEADER = "<!-- cortex-render: hcortex-edit; roundtrip: structural; source: {source}; hash: {hash} -->"

# Section marker: <!-- cortex-section: id="$2" title="ACTIVE WORK" -->
SECTION_MARKER_RE = re.compile(
    r'<!--\s*cortex-section:\s*id="(?P<id>[^"]+)"(?:\s+title="(?P<title>[^"]*)")?\s*-->'
)

# Entry marker: <!-- cortex-entry: section="$2" sigil="FCS" name="primary" type="attrs" hash="sha256:..." -->
ENTRY_MARKER_RE = re.compile(
    r'<!--\s*cortex-entry:\s*section="(?P<section>[^"]+)"\s+sigil="(?P<sigil>[^"]+)"\s+'
    r'name="(?P<name>[^"]+)"\s+type="(?P<type>[^"]+)"'
    r'(?:\s+hash="(?P<hash>[^"]+)")?\s*-->'
)

# Glossary block: ```cortex-glossary
GLOSARY_FENCE_RE = re.compile(r"```cortex-glossary\s*\n(?P<body>.*?)\n```", re.DOTALL)

# Verbatim fence: ```puml, ```plantuml, ```code, etc.
VERBATIM_FENCE_RE = re.compile(r"```(?P<lang>[a-zA-Z0-9_\-]+)\s*\n(?P<body>.*?)\n```", re.DOTALL)


@dataclass
class EditHeader:
    """Parsed HCORTEX-EDIT first-line header."""

    source: str
    hash: str

    @classmethod
    def parse(cls, line: str) -> Optional["EditHeader"]:
        if "cortex-render: hcortex-edit" not in line:
            return None
        m = re.search(r'source:\s*([^;]+?)\s*;', line)
        h = re.search(r'hash:\s*(\S+)', line)
        if not m or not h:
            return None
        return cls(source=m.group(1).strip(), hash=h.group(1).strip())


def is_hcortex_read(line: str) -> bool:
    return "cortex-render: hcortex-read" in line


def is_hcortex_edit(line: str) -> bool:
    return "cortex-render: hcortex-edit" in line


def is_hcortex_read_in_text(text: str, max_lines: int = 5) -> bool:
    """Check if any of the first ``max_lines`` lines declares hcortex-read.

    v1.1.3 P1-5: the ``Perfil:`` line is now the first real line, so the
    ``cortex-render`` marker moved to the second line.  Callers that
    need to detect HCORTEX-READ must scan a few lines, not just the first.
    """
    for line in text.splitlines()[:max_lines]:
        if is_hcortex_read(line):
            return True
    return False


def is_hcortex_edit_in_text(text: str, max_lines: int = 5) -> bool:
    """Check if any of the first ``max_lines`` lines declares hcortex-edit."""
    for line in text.splitlines()[:max_lines]:
        if is_hcortex_edit(line):
            return True
    return False
