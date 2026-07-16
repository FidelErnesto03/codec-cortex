# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cortex.cli.commands import benchmark as cmd_benchmark
from cortex.cli.main_e3 import main


def _make_suite(root: Path, name: str = "v-test") -> Path:
    suite = root / name
    (suite / "corpus" / "source").mkdir(parents=True)
    (suite / "runs").mkdir(parents=True)
    (suite / "manifest.json").write_text(json.dumps({"name": name}), encoding="utf-8")
    (suite / "corpus" / "source" / "sample.cortex").write_text("$0\n", encoding="utf-8")
    (suite / "runs" / "summary_tasks.csv").write_text("task,score\na,1\n", encoding="utf-8")
    (suite / "runs" / "scored_tasks.csv").write_text("task,score\na,1\n", encoding="utf-8")
    (suite / "runs" / "method_results.json").write_text("{}", encoding="utf-8")
    (suite / "runs" / "scenario_results.json").write_text("{}", encoding="utf-8")
    return suite


def test_benchmark_inspects_complete_suite(tmp_path: Path):
    suite = _make_suite(tmp_path / "benchmarks")
    result = cmd_benchmark.inspect_suite(suite)
    assert result["ok"] is True
    assert result["corpus_count"] == 1
    assert result["summary_rows"] == 1


def test_benchmark_command_lists_suites(tmp_path: Path, capsys):
    root = tmp_path / "benchmarks"
    _make_suite(root)
    args = argparse.Namespace(root=str(root), suite=None, list=True, format="text")
    assert cmd_benchmark.run(args) == 0
    assert "v-test" in capsys.readouterr().out


def test_main_e3_routes_benchmark(tmp_path: Path, capsys):
    root = tmp_path / "benchmarks"
    _make_suite(root)
    rc = main(["benchmark", "--root", str(root), "--suite", "v-test"])
    assert rc == 0
    assert "suite: v-test" in capsys.readouterr().out
