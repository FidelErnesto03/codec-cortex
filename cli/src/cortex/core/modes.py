# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""E2.3 (v0.3.4) — Mutation gates: read-only / editor / admin modes.

Three operating modes govern which CLI operations are permitted:

  ============= ===================================================== ===========
  Mode          Operations allowed                                   ``--force``
  ============= ===================================================== ===========
  ``read-only`` ``get``, ``list``, ``verify``, ``verify-view``,      Blocked
                ``inspect``, ``diff``, ``glossary list``, ``diagram``
  ``editor``    All of the above + ``add``, ``update``, ``delete``,  Requires
                ``move``, ``format``                                  confirm
  ``admin``     All of the above + unrestricted ``--force``           Allowed
  ============= ===================================================== ===========

The mode is resolved from (in priority order):

  1. The ``--mode`` CLI flag.
  2. The ``CORTEX_MODE`` environment variable.
  3. The default: ``editor``.

Mutations in ``read-only`` mode raise :class:`ModeReadOnlyError`.
Destructive mutations with ``--force`` in ``editor`` mode raise
:class:`ModeEditorConfirmRequiredError` unless confirmation was given.

The mode is propagated to command handlers via ``args.mode`` (a
:class:`Mode` enum) and ``args.mode_confirmed`` (bool).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .errors import CortexError


# ---------------------------------------------------------------------------
# Mode enum
# ---------------------------------------------------------------------------

class Mode(str, Enum):
    """Operating mode of the CLI."""

    READ_ONLY = "read-only"
    EDITOR = "editor"
    ADMIN = "admin"

    @classmethod
    def from_string(cls, value: Optional[str]) -> "Mode":
        if value is None or value == "":
            return cls.EDITOR  # default
        value = value.strip().lower()
        # Accept a few common aliases
        if value in ("read-only", "readonly", "ro"):
            return cls.READ_ONLY
        if value in ("editor", "edit", "standard"):
            return cls.EDITOR
        if value in ("admin", "administrator", "privileged"):
            return cls.ADMIN
        raise ModeUnknownError(value)

    @property
    def allows_writes(self) -> bool:
        return self in (Mode.EDITOR, Mode.ADMIN)

    @property
    def allows_force(self) -> bool:
        return self == Mode.ADMIN


# ---------------------------------------------------------------------------
# Error codes
# ---------------------------------------------------------------------------

E035_MODE_READ_ONLY = "E035_MODE_READ_ONLY"
E036_MODE_EDITOR_CONFIRM = "E036_MODE_EDITOR_CONFIRM"
E037_MODE_UNKNOWN = "E037_MODE_UNKNOWN"


@dataclass
class ModeReadOnlyError(CortexError):
    def __init__(self, op: str, **kw):
        super().__init__(
            E035_MODE_READ_ONLY,
            f"cannot run `{op}` in read-only mode (use --mode editor or --mode admin)",
            **kw,
        )


@dataclass
class ModeEditorConfirmRequiredError(CortexError):
    def __init__(self, op: str, **kw):
        super().__init__(
            E036_MODE_EDITOR_CONFIRM,
            f"`{op}` with --force requires confirmation in editor mode "
            "(use --mode admin to skip, or set CORTEX_MODE=admin)",
            **kw,
        )


@dataclass
class ModeUnknownError(CortexError):
    def __init__(self, value: str, **kw):
        super().__init__(
            E037_MODE_UNKNOWN,
            f"unknown mode '{value}'; must be one of: read-only, editor, admin",
            **kw,
        )


# ---------------------------------------------------------------------------
# Command classification
# ---------------------------------------------------------------------------

#: Commands that only read state — always allowed, even in read-only mode.
READ_ONLY_COMMANDS = frozenset({
    "get", "list", "verify", "verify-view", "inspect", "diff", "explain-loss",
    "roundtrip", "roundtrip-bidir", "compare", "doctor",
    "glossary list", "micro list",
    "diagram list", "diagram extract", "diagram validate",
    "render", "decode",  # render produces output but doesn't mutate the input
    "audit status", "audit snapshot",  # audit reads/snapshots, doesn't mutate .cortex
})

#: Commands that mutate a .cortex file — blocked in read-only mode.
WRITE_COMMANDS = frozenset({
    "add", "patch_add",
    "update", "patch_update",
    "delete", "patch_remove",
    "move",
    "format",
    "compile", "encode",   # compile writes a .cortex file
    "recover",
    "canonicalize",        # writes output (but typically to a different file)
    "glossary add", "glossary update", "glossary delete",
    "micro add", "micro update", "micro delete",
})

#: Commands that are always safe (not subject to mode checks).
META_COMMANDS = frozenset({
    "new",  # creates a new file from template; not a mutation of existing data
    "audit on", "audit off",  # toggles session-level audit logging
})


def is_write_command(command: str) -> bool:
    """Return True if ``command`` mutates a .cortex file."""
    return command in WRITE_COMMANDS


def is_read_command(command: str) -> bool:
    """Return True if ``command`` only reads state."""
    return command in READ_ONLY_COMMANDS


def is_meta_command(command: str) -> bool:
    """Return True if ``command`` is a meta operation (new, audit toggle)."""
    return command in META_COMMANDS


# ---------------------------------------------------------------------------
# Mode resolution + permission check
# ---------------------------------------------------------------------------

def resolve_mode(cli_flag: Optional[str] = None) -> Mode:
    """Resolve the effective mode.

    Priority: ``cli_flag`` > ``$CORTEX_MODE`` > default (``editor``).
    """
    if cli_flag:
        return Mode.from_string(cli_flag)
    env = os.environ.get("CORTEX_MODE")
    if env:
        return Mode.from_string(env)
    return Mode.EDITOR  # default


def check_permission(
    mode: Mode,
    command: str,
    *,
    uses_force: bool = False,
    confirmed: bool = False,
    non_interactive: bool = False,
) -> Optional[CortexError]:
    """Check whether ``mode`` permits running ``command``.

    Returns None if permitted, or a :class:`CortexError` describing why
    the operation is blocked.

    Behaviour matrix:

    ============ ======== =========== ===============================
    Mode         Writes   --force     Notes
    ============ ======== =========== ===============================
    read-only    Blocked  Blocked     E035_MODE_READ_ONLY
    editor       Allowed  Prompt(*)   (*) In interactive mode only.
                                        In non-interactive mode (CI,
                                        scripts, tests), --force
                                        proceeds without prompt
                                        (the user already opted in).
    admin        Allowed  Allowed     No checks
    ============ ======== =========== ===============================

    Parameters
    ----------
    mode
        The resolved :class:`Mode`.
    command
        The canonical command name (e.g. ``"delete"``, ``"audit on"``,
        ``"glossary list"``).
    uses_force
        True if the user passed ``--force`` for this command.
    confirmed
        True if the user pre-confirmed (e.g. via ``--yes``).
    non_interactive
        If True, never prompt; in editor mode + --force, proceed without
        confirmation (the explicit --force is the opt-in). If False
        (interactive terminal), prompt the user with y/N.
    """
    # Read commands are always allowed.
    if is_read_command(command):
        return None
    # Meta commands (new, audit on/off) are always allowed.
    if is_meta_command(command):
        return None

    # Write commands
    if is_write_command(command):
        if mode == Mode.READ_ONLY:
            return ModeReadOnlyError(command)
        if mode == Mode.EDITOR and uses_force:
            if confirmed:
                return None
            if non_interactive:
                # Non-interactive (CI, scripts, tests): the explicit
                # --force is the opt-in. Proceed without prompt.
                # This preserves backward compatibility with existing
                # scripts that use --force in non-interactive contexts.
                return None
            # Interactive: prompt the user.
            if not _prompt_confirm(command):
                return ModeEditorConfirmRequiredError(command)
            return None
        # editor without --force, or admin → allowed
        return None

    # Unknown command classification: allow by default (the command will
    # fail later if it doesn't exist).
    return None


def _prompt_confirm(command: str) -> bool:
    """Interactive y/N prompt for destructive operations in editor mode."""
    try:
        print(
            f"WARNING: `{command}` with --force in editor mode. Confirm? [y/N] ",
            end="",
            flush=True,
            file=sys.stderr,
        )
        answer = sys.stdin.readline().strip().lower()
        return answer in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


# ---------------------------------------------------------------------------
# Convenience: annotate args with mode info
# ---------------------------------------------------------------------------

def annotate_args(args, mode: Mode) -> None:
    """Stash mode info on the parsed args for command handlers to read.

    v0.3.4: uses ``args.op_mode`` (a :class:`Mode` enum) and
    ``args.op_mode_value`` (its string value) to avoid colliding with
    subcommand-specific ``args.mode`` attributes (e.g. ``render --mode
    read`` sets ``args.mode = "read"``, which we must not overwrite).
    """
    args.op_mode = mode                        # type: ignore[attr-defined]
    args.op_mode_value = mode.value            # type: ignore[attr-defined]
    # mode_confirmed is set by --yes or by the prompt logic; default False.
    if not hasattr(args, "mode_confirmed"):
        args.mode_confirmed = False            # type: ignore[attr-defined]
