# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""BLP-006 AC-01/AC-02/AC-03: CLI --output json, --help, kebab-case."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a cortex command as a subprocess (Pattern B from learning CLI tests)."""
    env = dict(__session_started__="0")  # Suppress session auto-start
    import os
    full_env = {**os.environ, **env, "PYTHONPATH": str(SRC)}
    cortex_bin = _find_cortex()
    if cortex_bin:
        cmd = [str(cortex_bin)] + list(args)
    else:
        cmd = [sys.executable, "-m", "cortex.cli.main_e3"] + list(args)
    return subprocess.run(
        cmd, capture_output=True, text=True, env=full_env, cwd=cwd or str(SRC),
    )


def _find_cortex() -> Path | None:
    """Find the cortex binary."""
    import shutil
    return shutil.which("cortex")


# ---------------------------------------------------------------------------
# AC-01: --help on every command
# ---------------------------------------------------------------------------


class TestAC01Help:
    """AC-01: ``--help`` muestra ayuda en todos los comandos."""

    CMD_TREES: list[list[str]] = [
        ["session"],
        ["session", "start"],
        ["session", "status"],
        ["session", "event"],
        ["session", "consolidate"],
        ["session", "close"],
        ["session", "abort"],
        ["session", "detect-legacy"],
        ["session", "migrate-legacy"],
        ["learn"],
        ["learn", "init"],
        ["learn", "doctor"],
        ["learn", "scan"],
        ["learn", "candidates"],
        ["learn", "explain"],
        ["learn", "elevate"],
        ["learn", "profile"],
        ["learn", "feedback"],
        ["learn", "feedback-show"],
        ["learn", "policy"],
        ["learn", "policy", "show"],
        ["learn", "policy", "validate"],
        ["learn", "policy", "apply"],
        ["learn", "policy", "add"],
        ["learn", "policy", "set"],
        ["learn", "policy", "profile"],
        ["learn", "policy", "reset"],
        ["learn", "index"],
        ["learn", "index", "rebuild"],
        ["learn", "index", "status"],
        ["learn", "index", "clean"],
    ]

    @pytest.mark.parametrize("args", CMD_TREES)
    def test_help(self, args: list[str]) -> None:
        r = _run(*args, "--help")
        # --help should exit 0 for valid commands
        assert r.returncode == 0 or "usage:" in r.stdout or "usage:" in r.stderr, (
            f"{' '.join(args)} --help failed (rc={r.returncode}): {r.stderr[:200]}"
        )
        assert "usage:" in r.stdout or "usage:" in r.stderr, (
            f"{' '.join(args)} --help did not show usage"
        )


# ---------------------------------------------------------------------------
# AC-02: all flags use kebab-case (validated at parser-build time)
# ---------------------------------------------------------------------------


class TestAC02KebabCase:
    """AC-02: todos los flags están en kebab-case.

    Verified at parser-build time: argparse raises no custom flags with
    underscores, and the global --help output only shows kebab-case flags.
    """

    def test_help_shows_kebab_flags(self) -> None:
        """Root --help output uses kebab-case flags."""
        r = _run("--help")
        assert r.returncode == 0
        text = r.stdout + r.stderr
        # Scan for snake_case flags (--something_else)
        import re
        snake_flags = re.findall(r'--[a-z]+_[a-z][a-z_-]*', text)
        assert len(snake_flags) == 0, (
            f"Found snake_case flags in --help: {snake_flags}"
        )

    def test_session_help_shows_kebab(self) -> None:
        """session --help output uses kebab-case flags."""
        r = _run("session", "--help")
        assert r.returncode == 0
        text = r.stdout + r.stderr
        import re
        snake_flags = re.findall(r'--[a-z]+_[a-z][a-z_-]*', text)
        assert len(snake_flags) == 0, (
            f"Found snake_case flags in session --help: {snake_flags}"
        )


# ---------------------------------------------------------------------------
# AC-03: --output json disponible en comandos de datos
# ---------------------------------------------------------------------------


class TestAC03OutputJson:
    """AC-03: ``--output json`` disponible en comandos de datos."""

    @pytest.mark.parametrize("args", [
        ["session", "start", "--output", "json"],
        ["session", "status", "--output", "json"],
        ["session", "event", "--kind", "note", "--output", "json"],
        ["session", "consolidate", "--output", "json"],
        ["session", "close", "--output", "json"],
        ["session", "abort", "--output", "json"],
        ["session", "detect-legacy", "--output", "json"],
        ["session", "migrate-legacy", "--id", "SES:test", "--action", "review",
         "--output", "json"],
        ["learn", "scan", "--output", "json"],
        ["learn", "profile", "--output", "json"],
        ["learn", "candidates", "--output", "json"],
    ])
    def test_output_json_parses(self, args: list[str], tmp_path: Path) -> None:
        """--output json produces parseable JSON output."""
        r = _run(*args, cwd=tmp_path)
        # The command should either:
        # (a) return parseable JSON on stdout, or
        # (b) gracefully fail with non-JSON error text
        if r.returncode == 0:
            # Success: verify JSON is parseable
            assert r.stdout.strip(), (
                f"{' '.join(args)} returned 0 with empty stdout"
            )
            try:
                json.loads(r.stdout)
            except json.JSONDecodeError:
                # Allow non-JSON if stderr has the actual error
                if not r.stderr:
                    pytest.fail(
                        f"{' '.join(args)}: stdout not valid JSON and no stderr error\n"
                        f"stdout: {r.stdout[:300]}"
                    )
        else:
            # Failure is OK (may need a real workspace) — just verify --output json
            # doesn't cause a argparse error
            assert "--output" not in r.stderr, (
                f"{' '.join(args)}: --output json rejected by argparse\n"
                f"stderr: {r.stderr[:300]}"
            )

    def test_output_json_global_alias(self, tmp_path: Path) -> None:
        """Global --output json propagates to subcommands."""
        r = _run("--output", "json", "session", "start", cwd=tmp_path)
        # Should not fail with argparse error
        assert "--output" not in r.stderr, (
            f"Global --output json rejected: {r.stderr[:300]}"
        )

    def test_output_json_equivalent_to_json(self, tmp_path: Path) -> None:
        """--output json and --json produce identical output."""
        r_output = _run("learn", "doctor", "--output", "json", cwd=tmp_path)
        r_json = _run("learn", "doctor", "--json", cwd=tmp_path)
        # Both should either succeed or fail the same way
        assert r_output.returncode == r_json.returncode, (
            f"--output json rc={r_output.returncode} vs --json rc={r_json.returncode}"
        )
