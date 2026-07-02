# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Transactions — atomic write with backup, dry-run and diff support.

Per Section 15 of the spec:

    atomic_write(path, content):
        tmp = path + ".tmp"
        bak = path + ".bak"
        write tmp
        parse tmp
        validate tmp
        copy path to bak
        replace path with tmp

The writer NEVER overwrites the target if validation fails.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from typing import Optional

from ..core.ast import CortexDocument
from ..core.errors import AtomicWriteError
from ..core.parser import parse_cortex
from ..core.writer import write_cortex
from ..core.validator import validate


@dataclass
class WriteResult:
    path: str
    backup: Optional[str]
    bytes_written: int
    diagnostics: list
    dry_run: bool

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "backup": self.backup,
            "bytes_written": self.bytes_written,
            "diagnostics": self.diagnostics,
            "dry_run": self.dry_run,
        }


def atomic_write_cortex(
    doc: CortexDocument,
    path: str,
    *,
    force: bool = False,
    dry_run: bool = False,
    keep_backup: bool = True,
    unsafe_allow_secret_forensics: bool = False,
) -> WriteResult:
    """Serialise ``doc`` and atomically write it to ``path``.

    The workflow:
      1. Serialise to canonical text.
      2. Re-parse the text and validate.
      3. If validation produces error-severity diagnostics and ``force``
         is False, abort.
      4. Write to ``path + ".tmp"``.
      5. Copy the original file to ``path + ".bak"`` (if it existed).
      6. Rename ``.tmp`` → ``path``.
      7. If ``dry_run`` is True, do not touch the filesystem; just report.

    v1.1.3 P0-2: ``unsafe_allow_secret_forensics=True`` allows bypassing
    ``E031_SECRET_NOT_BYPASSABLE`` for forensic recovery ONLY.  It does
    NOT bypass ``E032_CRITICAL_SIGIL_INCOMPLETE``.
    """

    text = write_cortex(doc)
    # Re-parse to verify roundtrip-ability
    reparsed = parse_cortex(text, path=path)
    diagnostics = validate(reparsed)
    errors = [d for d in diagnostics if d.get("severity") == "error"]
    # v1.1.3 P0-2/P0-3: non-bypassable errors (secrets, critical sigil
    # incompleteness) CANNOT be overridden by --force.
    non_bypassable = [d for d in errors if d.get("bypassable") is False]
    bypassable = [d for d in errors if d.get("bypassable") is not False]
    # v1.1.3 P0-2: --unsafe-allow-secret-forensics can bypass secret errors ONLY
    if unsafe_allow_secret_forensics:
        non_bypassable = [
            d for d in non_bypassable
            if d.get("code") != "E031_SECRET_NOT_BYPASSABLE"
        ]
    if non_bypassable:
        raise AtomicWriteError(
            f"{len(non_bypassable)} non-bypassable error(s) prevent write; "
            "--force cannot override security/governance rules: "
            + "; ".join(d.get("code", "") + ": " + d.get("message", "")[:80] for d in non_bypassable[:3]),
        )
    if bypassable and not force:
        raise AtomicWriteError(
            f"validation failed with {len(bypassable)} bypassable error(s); "
            "use --force to override",
        )

    if dry_run:
        return WriteResult(
            path=path,
            backup=None,
            bytes_written=len(text.encode("utf-8")),
            diagnostics=diagnostics,
            dry_run=True,
        )

    # Ensure parent directory exists
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)

    tmp_path = path + ".tmp"
    bak_path = path + ".bak"

    # Write tmp
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(text)
    except OSError as e:
        raise AtomicWriteError(f"cannot write tmp file: {e}")

    # Backup original
    backup_created = None
    if keep_backup and os.path.exists(path):
        try:
            shutil.copy2(path, bak_path)
            backup_created = bak_path
        except OSError as e:
            # Clean up tmp
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise AtomicWriteError(f"cannot create backup: {e}")

    # Rename tmp → path
    try:
        os.replace(tmp_path, path)
    except OSError as e:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise AtomicWriteError(f"cannot replace target file: {e}")

    return WriteResult(
        path=path,
        backup=backup_created,
        bytes_written=len(text.encode("utf-8")),
        diagnostics=diagnostics,
        dry_run=False,
    )


def atomic_write_text(
    text: str,
    path: str,
    *,
    dry_run: bool = False,
    keep_backup: bool = True,
) -> WriteResult:
    """Atomic write for arbitrary text (used by render/compile)."""

    if dry_run:
        return WriteResult(
            path=path, backup=None,
            bytes_written=len(text.encode("utf-8")),
            diagnostics=[], dry_run=True,
        )

    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)

    tmp_path = path + ".tmp"
    bak_path = path + ".bak"

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(text)
    except OSError as e:
        raise AtomicWriteError(f"cannot write tmp file: {e}")

    backup_created = None
    if keep_backup and os.path.exists(path):
        try:
            shutil.copy2(path, bak_path)
            backup_created = bak_path
        except OSError as e:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise AtomicWriteError(f"cannot create backup: {e}")

    try:
        os.replace(tmp_path, path)
    except OSError as e:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise AtomicWriteError(f"cannot replace target file: {e}")

    return WriteResult(
        path=path, backup=backup_created,
        bytes_written=len(text.encode("utf-8")),
        diagnostics=[], dry_run=False,
    )
