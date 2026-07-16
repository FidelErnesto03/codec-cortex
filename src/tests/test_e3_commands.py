# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Coverage tests for the E3 documentation and benchmark commands."""

from argparse import Namespace
import json

import pytest

from cortex.cli import main_e3
from cortex.cli.commands import benchmark, docstring


def _api_doc(path, *, include_summary=True, include_command=True):
    lines = []
    if include_command:
        lines.append('IDN:command{name:"verify", cli:"cortex verify", status:"current"}')
    if include_summary:
        lines.append('DESC:summary{text:"Validate a document."}')
    lines.append('ARG:input{name:"input", required:"yes", description:"File"}')
    lines.append('LIM:scope{limit:"local", scope:"file"}')
    path.write_text("\n".join(lines), encoding="utf-8")


def test_docstring_parsing_rendering_and_json_output(tmp_path, capsys):
    _api_doc(tmp_path / "verify.cortex")
    data = docstring.parse_api_doc(tmp_path / "verify.cortex")
    rendered = docstring.render_docstring(data)
    assert "cortex verify" in rendered and "Validate a document." in rendered
    assert docstring.run(Namespace(docs_root=str(tmp_path), all=False, command="verify", format="json")) == 0
    assert json.loads(capsys.readouterr().out)["command"] == "verify"


def test_docstring_all_and_error_cases(tmp_path, capsys):
    _api_doc(tmp_path / "verify.cortex")
    _api_doc(tmp_path / "audit.cortex")
    assert docstring.run(Namespace(docs_root=str(tmp_path), all=True, command=None, format="text")) == 0
    assert "---" in capsys.readouterr().out
    with pytest.raises(docstring.DocstringError, match="provide a command"):
        docstring.run(Namespace(docs_root=str(tmp_path), all=False, command=None, format="text"))
    with pytest.raises(docstring.DocstringError, match="API doc not found"):
        docstring.run(Namespace(docs_root=str(tmp_path), all=False, command="missing", format="text"))
    _api_doc(tmp_path / "bad.cortex", include_summary=False)
    with pytest.raises(docstring.DocstringError, match="missing DESC"):
        docstring.parse_api_doc(tmp_path / "bad.cortex")


def test_docstring_root_resolution_errors(tmp_path):
    assert docstring.resolve_docs_root(str(tmp_path)) == tmp_path
    with pytest.raises(docstring.DocstringError, match="docs root not found"):
        docstring.resolve_docs_root(str(tmp_path / "missing"))


def _suite(root, name="suite", complete=True):
    suite = root / name
    (suite / "runs").mkdir(parents=True)
    (suite / "corpus" / "source").mkdir(parents=True)
    (suite / "manifest.json").write_text('{"name":"suite"}', encoding="utf-8")
    if complete:
        (suite / "corpus" / "source" / "one.cortex").write_text("$0\n", encoding="utf-8")
        (suite / "runs" / "summary_tasks.csv").write_text("id\n1\n", encoding="utf-8")
        (suite / "runs" / "scored_tasks.csv").write_text("id\n1\n2\n", encoding="utf-8")
        (suite / "runs" / "method_results.json").write_text("{}", encoding="utf-8")
        (suite / "runs" / "scenario_results.json").write_text("{}", encoding="utf-8")
    return suite


def test_benchmark_discovery_inspection_and_json(tmp_path, capsys):
    _suite(tmp_path)
    assert benchmark.discover_suites(tmp_path)[0].name == "suite"
    info = benchmark.inspect_suite(tmp_path / "suite")
    assert info["ok"] and info["summary_rows"] == 1 and info["scored_rows"] == 2
    assert benchmark.run(Namespace(root=str(tmp_path), suite=None, list=False, format="json")) == 0
    assert json.loads(capsys.readouterr().out)[0]["ok"] is True


def test_benchmark_list_incomplete_and_errors(tmp_path, capsys):
    _suite(tmp_path, complete=False)
    assert benchmark.run(Namespace(root=str(tmp_path), suite=None, list=True, format="text")) == 0
    assert "suite" in capsys.readouterr().out
    assert benchmark.run(Namespace(root=str(tmp_path), suite=None, list=False, format="text")) == 1
    with pytest.raises(benchmark.BenchmarkError, match="suite not found"):
        benchmark.run(Namespace(root=str(tmp_path), suite="missing", list=False, format="text"))
    with pytest.raises(benchmark.BenchmarkError, match="not found"):
        benchmark.resolve_root(str(tmp_path / "missing"))


def test_benchmark_invalid_json_and_missing_csv(tmp_path):
    bad = _suite(tmp_path, complete=False)
    (bad / "manifest.json").write_text("{", encoding="utf-8")
    with pytest.raises(benchmark.BenchmarkError, match="invalid JSON"):
        benchmark.inspect_suite(bad)
    assert benchmark._count_csv_rows(tmp_path / "missing.csv") == 0


def test_e3_wrapper_routes_and_reports_errors(monkeypatch, capsys):
    monkeypatch.setattr(main_e3.cmd_docstring, "run", lambda args: 7)
    assert main_e3.main(["docstring", "verify"]) == 7
    monkeypatch.setattr(main_e3.cmd_benchmark, "run", lambda args: 8)
    assert main_e3.main(["benchmark", "--list"]) == 8
    monkeypatch.setattr(main_e3, "legacy_main", lambda args: 9)
    assert main_e3.main(["verify", "file.cortex"]) == 9
    monkeypatch.setattr(main_e3, "legacy_main", lambda args: (_ for _ in ()).throw(ValueError("bad")))
    assert main_e3.main(["verify"]) == 1
    assert "error: bad" in capsys.readouterr().err
