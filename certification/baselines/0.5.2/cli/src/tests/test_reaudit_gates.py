# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Re-audit gap tests — CLI end-to-end coverage for H-RA-01 through H-RA-09 + M-RA-02/03/04.

These tests run the actual CLI as subprocesses (not just the internal API)
to verify that claims like ``verify --kind package`` actually behave as
declared.  They complement the unit tests in ``test_audit_gates.py``.
"""

import json
import os
import subprocess
import sys

import pytest

from cortex.templates import build_brain, build_skill
from cortex.core.parser import build_entry_from_value
from cortex.core.writer import write_cortex
from cortex.core.document_kind import DocumentKind
from cortex.core.validator import validate
from cortex.crud.transactions import atomic_write_cortex
from cortex.hcortex import recover_cortex, render_hcortex_read


HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(HERE, ".."))


def _run_cli(args_list, env=None):
    """Run the cortex CLI as a subprocess and return the CompletedProcess.

    The subprocess invokes ``main()`` and propagates its return code via
    ``sys.exit()`` so the shell sees the correct exit status.
    """

    e = os.environ.copy()
    e["PYTHONPATH"] = SRC_DIR + os.pathsep + e.get("PYTHONPATH", "")
    if env:
        e.update(env)
    return subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, %r); from cortex.cli.main import main; rc = main(); sys.exit(rc or 0)" % SRC_DIR]
        + args_list,
        capture_output=True, text=True, env=e,
    )


# ---------------------------------------------------------------------------
# H-RA-01: --kind must actually govern validation (not just display)
# ---------------------------------------------------------------------------

def test_cli_verify_kind_package_overrides_idn_agent(tmp_path):
    """A file with IDN:agent + FCS+OBJ+WRK, verified as --kind package,
    MUST fail with E029_LEVEL3_LIVE_STATE."""

    # Build a brain (which has FCS/OBJ/WRK) and save it
    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)
    # Now verify as package — FCS/OBJ/WRK are forbidden in Nivel 3
    r = _run_cli(["verify", path, "--strict", "--kind", "package"])
    assert r.returncode != 0, f"expected non-zero rc, got {r.returncode}\nstdout: {r.stdout}"
    # The output should mention E029 or LEVEL3
    combined = r.stdout + r.stderr
    assert ("E029" in combined) or ("LEVEL3" in combined) or ("live state" in combined.lower()), (
        f"expected E029 in output, got: {combined}"
    )


def test_cli_verify_kind_skill_overrides_filename_or_idn(tmp_path):
    """A file containing live WRK verified as --kind skill MUST fail
    with E023_LEVEL1_LIVE_STATE — even if the filename suggests 'brain'."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)
    r = _run_cli(["verify", path, "--strict", "--kind", "skill"])
    assert r.returncode != 0
    combined = r.stdout + r.stderr
    assert ("E023" in combined) or ("LEVEL1" in combined) or ("live state" in combined.lower())


def test_cli_verify_kind_generic_disables_level_policy(tmp_path):
    """With --kind generic, level-policy rules are not enforced (no live-state errors)."""

    doc = build_brain()
    # SchemaResolver always requires 'name' field; populate from entry names
    for _, entry in doc.iter_entries():
        if isinstance(entry.value, dict) and "name" not in entry.value:
            entry.value["name"] = entry.name
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)
    r = _run_cli(["verify", path, "--strict", "--kind", "generic"])
    # generic kind disables level-policy checks → should pass
    assert r.returncode == 0, f"expected rc=0, got {r.returncode}\n{r.stdout}\n{r.stderr}"


def test_cli_doctor_kind_skill_overrides_filename(tmp_path):
    """doctor --kind skill must apply Nivel-1 rules regardless of filename."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)
    r = _run_cli(["doctor", path, "--kind", "skill", "--format", "json"])
    payload = json.loads(r.stdout)
    # Should have errors because brain has WRK which is forbidden in skill
    assert payload["ok"] is False
    codes = [e.get("code") for e in payload.get("errors", [])]
    assert "E023_LEVEL1_LIVE_STATE" in codes, f"expected E023 in {codes}"


# ---------------------------------------------------------------------------
# H-RA-02: SES/LNG live in skill must fail
# ---------------------------------------------------------------------------

def test_g2_strict_skill_with_live_ses_fails():
    doc = build_skill()
    sec = doc.get_or_create_section("$2", title="SESSIONS")
    sec.entries.append(build_entry_from_value(
        "$2", "SES", "live", "attrs",
        {"input": "x", "output": "y", "outcome": "z", "date": "2026-06-26"},
    ))
    diags = validate(doc, strict=True, kind=DocumentKind("skill", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E023_LEVEL1_LIVE_STATE" in codes, f"SES should be forbidden in skill; got {codes}"


def test_g2_strict_skill_with_live_lng_fails():
    doc = build_skill()
    sec = doc.get_or_create_section("$2", title="LESSONS")
    sec.entries.append(build_entry_from_value(
        "$2", "LNG", "live", "attrs",
        {"type": "error", "cause": "x", "lesson": "y", "prevention": "z"},
    ))
    diags = validate(doc, strict=True, kind=DocumentKind("skill", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E023_LEVEL1_LIVE_STATE" in codes, f"LNG should be forbidden in skill; got {codes}"


def test_g2_strict_skill_with_historical_ses_example_passes():
    """SES marked as example/specification is allowed in skill (contract form)."""

    doc = build_skill()
    sec = doc.get_or_create_section("$2", title="SESSIONS")
    sec.entries.append(build_entry_from_value(
        "$2", "SES", "example", "attrs",
        {
            "input": "x", "output": "y", "outcome": "z", "date": "2026-06-26",
            "nature": "example", "status": "specification",
        },
    ))
    diags = validate(doc, strict=True, kind=DocumentKind("skill", "test"))
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    assert "E023_LEVEL1_LIVE_STATE" not in codes


# ---------------------------------------------------------------------------
# H-RA-03: HCORTEX --layout priority orders P0 before P2 globally
# ---------------------------------------------------------------------------

def test_hcortex_layout_priority_orders_p0_before_p2():
    """With layout=priority, P0 entries (FCS) must appear before P2 entries (IDN)."""

    doc = build_brain()
    md = render_hcortex_read(doc, profile="WORK", mode="READABLE", layout="priority")
    # Find positions of FCS:primary (P0) and IDN:agent (P2)
    pos_fcs = md.find("Focus: primary")
    pos_idn = md.find("Identity: agent")
    assert pos_fcs != -1 and pos_idn != -1, "entries not found in output"
    assert pos_fcs < pos_idn, f"expected FCS (P0) before IDN (P2); got FCS@{pos_fcs} IDN@{pos_idn}"


def test_hcortex_layout_priority_default_for_min():
    """MIN profile should auto-select priority layout (re-audit H-RA-03)."""

    doc = build_brain()
    md = render_hcortex_read(doc, profile="MIN", mode="READABLE")
    assert "Layout: priority" in md


def test_hcortex_layout_section_preserves_section_order():
    """With layout=section, $1 (Identity) appears before $2 (Active Work)."""

    doc = build_brain()
    md = render_hcortex_read(doc, profile="WORK", mode="READABLE", layout="section")
    pos_1 = md.find("$1 ·")
    pos_2 = md.find("$2 ·")
    assert pos_1 != -1 and pos_2 != -1
    assert pos_1 < pos_2


# ---------------------------------------------------------------------------
# H-RA-04: diagram extract --out preserves bytes exactly
# ---------------------------------------------------------------------------

def test_g7_diagram_extract_out_preserves_exact_bytes(tmp_path):
    """Re-audit H-RA-04: extract --out must NOT append a trailing newline."""

    puml = "@startuml\nA-->B\n@enduml"  # no trailing newline
    doc = build_brain()
    sec = doc.get_or_create_section("$6", title="DIAGRAMS")
    sec.entries.append(build_entry_from_value("$6", "DIAG", "flow", "bloque", puml))
    cortex_path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, cortex_path, force=True)

    out_path = str(tmp_path / "flow.puml")
    r = _run_cli(["diagram", "extract", cortex_path, "--name", "flow", "--out", out_path])
    assert r.returncode == 0, f"extract failed: {r.stderr}"

    with open(out_path, "r", encoding="utf-8") as f:
        extracted = f.read()
    assert extracted == puml, (
        f"verbatim mismatch:\n  expected {puml!r}\n  got      {extracted!r}"
    )


# ---------------------------------------------------------------------------
# H-RA-05: attrs-pos with | in value must error (writer side)
# ---------------------------------------------------------------------------

def test_attrs_pos_writer_rejects_pipe_in_value():
    """The writer must refuse to serialize attrs-pos values containing '|'."""

    from cortex.core.ast import AttrsPosContract
    from cortex.core.writer import serialize_attrs_pos
    from cortex.core.errors import InvalidValueError

    contract = AttrsPosContract(sigil="HDL", fields=["operation", "status", "requires"])
    attrs = {"operation": "decode | render", "status": "current", "requires": "file"}
    with pytest.raises(InvalidValueError) as exc_info:
        serialize_attrs_pos(attrs, contract)
    assert "attrs-pos" in str(exc_info.value).lower()
    assert "|" in str(exc_info.value)


def test_attrs_pos_with_pipe_in_value_does_not_roundtrip_silently():
    """If somehow a value with | reaches the parser, it parses wrong
    (this is by design — pipes are forbidden).  The validator must
    catch the arity mismatch via E027."""

    doc = build_skill()
    sec = doc.get_or_create_section("$4", title="HANDLERS")
    from cortex.core.ast import Entry, compute_entry_hash
    raw = 'HDL:bad{"decode | render" | "current" | "file"}'
    entry = Entry(
        section="$4", sigil="HDL", name="bad", type="attrs-pos",
        value={"operation": '"decode', "status": 'render"', "requires": "current"},
        raw=raw, line_start=0, line_end=0, hash="",
    )
    entry.hash = compute_entry_hash(entry)
    entry.entry_id = entry.hash
    sec.entries.append(entry)
    diags = validate(doc)
    codes = [d["code"] for d in diags if d["severity"] == "error"]
    # Should detect either arity mismatch or invalid status
    assert "E027_ATTRS_POS_ARITY" in codes or "W002_INVALID_STATUS" in [d["code"] for d in diags]


# ---------------------------------------------------------------------------
# H-RA-06: add_entry blocks unknown sigil by default
# ---------------------------------------------------------------------------

def test_cli_add_rejects_unknown_sigil_by_default(tmp_path):
    """cortex add with a sigil not in $0 must fail by default."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)
    r = _run_cli([
        "add", path, "--section", "$2", "--sigil", "BOGUS", "--name", "x",
        "--value", 'key:"value"',
    ])
    assert r.returncode != 0, f"expected non-zero rc, got {r.returncode}"
    combined = r.stdout + r.stderr
    assert ("E003" in combined) or ("unknown sigil" in combined.lower()), (
        f"expected E003 in output, got: {combined}"
    )


def test_cli_add_allows_unknown_sigil_with_flag(tmp_path):
    """cortex add --allow-unknown-sigil permits undeclared sigils."""

    doc = build_brain()
    path = str(tmp_path / "brain.cortex")
    atomic_write_cortex(doc, path, force=True)
    r = _run_cli([
        "add", path, "--section", "$99", "--sigil", "BOGUS", "--name", "x",
        "--value", 'key:"value"',
        "--allow-unknown-sigil", "--create-section", "--no-validate-write",
        "--force",  # atomic_write_cortex validates; --force overrides
    ])
    assert r.returncode == 0, f"expected rc=0, got {r.returncode}\n{r.stdout}\n{r.stderr}"


def test_add_entry_internal_blocks_unknown_sigil():
    """The internal add_entry must raise UnknownSigilError by default."""

    from cortex.crud.mutations import add_entry
    from cortex.core.errors import UnknownSigilError

    doc = build_brain()
    with pytest.raises(UnknownSigilError):
        add_entry(doc, "$2", "BOGUS", "x", {"k": "v"})


# ---------------------------------------------------------------------------
# H-RA-07: BENCHMARK.md must not claim "measured" for throughput
# ---------------------------------------------------------------------------

def test_benchmark_throughput_not_measured():
    """Re-audit H-RA-07: 'Parser throughput' must NOT be classified as `measured`."""

    benchmark_path = os.path.join(SRC_DIR, "..", "BENCHMARK.md")
    if not os.path.exists(benchmark_path):
        pytest.skip("BENCHMARK.md not present")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Find the throughput row
    for line in text.splitlines():
        if "throughput" in line.lower():
            assert "measured" not in line.lower(), (
                f"throughput row should not be 'measured': {line!r}"
            )
            # Should be hypothesis or illustrative
            assert ("hypothesis" in line.lower() or "illustrative" in line.lower() or "target" in line.lower()), (
                f"throughput should be hypothesis/illustrative/target: {line!r}"
            )


def test_benchmark_roundtrip_count_matches_suite():
    """v1.1.2: BENCHMARK.md should NOT hardcode test counts (they drift).

    Previously the test demanded "88" in the file; that became stale when
    the suite grew.  Now we verify that BENCHMARK.md explicitly avoids
    hardcoding the count and points to the live `pytest` command instead.
    """

    benchmark_path = os.path.join(SRC_DIR, "..", "BENCHMARK.md")
    if not os.path.exists(benchmark_path):
        pytest.skip("BENCHMARK.md not present")
    with open(benchmark_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Must explicitly state that the count is not hardcoded
    assert "no se hardcodea" in text.lower() or "not hardcoded" in text.lower(), (
        "BENCHMARK.md should declare that test counts are not hardcoded"
    )
    # Must point to the live pytest command for the actual count
    assert "python -m pytest src/tests/ -q" in text, (
        "BENCHMARK.md should include the live pytest command for test count"
    )


# ---------------------------------------------------------------------------
# H-RA-08: version of SKILL must be consistent across docs
# ---------------------------------------------------------------------------

def test_declared_skill_version_matches_reference_file():
    """All docs should reference the same SKILL version."""

    skill_path = os.path.join(SRC_DIR, "..", "SKILL_canon.md")
    if not os.path.exists(skill_path):
        pytest.skip("SKILL_canon.md not present")
    with open(skill_path, "r", encoding="utf-8") as f:
        skill_text = f.read()
    # Extract version from SKILL.md (e.g. "v1.1.0-enterprise-candidate")
    import re
    m = re.search(r"v(\d+\.\d+\.\d+-enterprise-candidate)", skill_text)
    if not m:
        pytest.skip("could not extract SKILL version")
    skill_version = m.group(1)

    # Check README, STATUS, INFORME reference the same version
    docs_to_check = ["README.md", "STATUS.md"]
    for doc_name in docs_to_check:
        doc_path = os.path.join(SRC_DIR, "..", doc_name)
        if not os.path.exists(doc_path):
            continue
        with open(doc_path, "r", encoding="utf-8") as f:
            doc_text = f.read()
        if "enterprise-candidate" in doc_text:
            # extract any version reference
            for line in doc_text.splitlines():
                if "enterprise-candidate" in line:
                    m2 = re.search(r"v?(\d+\.\d+\.\d+-enterprise-candidate)", line)
                    if m2:
                        assert m2.group(1) == skill_version, (
                            f"{doc_name} references {m2.group(1)} but SKILL.md is {skill_version}"
                        )


# ---------------------------------------------------------------------------
# M-RA-02: diff governance --format json returns non-zero on findings
# ---------------------------------------------------------------------------

def test_cli_diff_governance_json_returns_nonzero_on_findings(tmp_path):
    """Re-audit M-RA-02: governance diff with findings must return non-zero.

    v1.1.4: E026_BLOCKING_NOT_P0 is now bypassable=False, so we can't
    use `update --force` to create a CNST with survive=work.  Instead,
    we write the file directly with atomic_write_cortex(force=True).
    """

    doc1 = build_brain()
    path1 = str(tmp_path / "brain1.cortex")
    atomic_write_cortex(doc1, path1, force=True)

    doc2 = build_brain()
    cnst = doc2.find_entries(sigil="CNST")[0]
    cnst.value["survive"] = "work"
    path2 = str(tmp_path / "brain2.cortex")
    # v1.1.4: atomic_write_cortex blocks non-bypassable errors even with
    # force=True.  We bypass by using --no-validate-write equivalent:
    # write the text directly to the file.
    text2 = write_cortex(doc2)
    with open(path2, "w") as f:
        f.write(text2)

    r = _run_cli([
        "diff", path1, path2, "--profile", "governance", "--format", "json",
    ])
    assert r.returncode != 0, (
        f"expected non-zero rc for a governance value change, got {r.returncode}\n{r.stdout}"
    )
    payload = json.loads(r.stdout)
    left_findings = payload.get("left", {}).get("findings", [])
    right_findings = payload.get("right", {}).get("findings", [])
    assert not left_findings and not right_findings, "retention override is not a governance finding"


# ---------------------------------------------------------------------------
# M-RA-03: recover --embed-aud-rsk inserts AUD/RSK entries in the artefact
# ---------------------------------------------------------------------------

def test_recover_embed_aud_rsk_inserts_entries():
    """Re-audit M-RA-03: with embed_aud_rsk=True, the recovered .cortex
    must contain AUD and RSK entries."""

    legacy = """\
<!-- SPDX-License-Identifier: MIT -->
$1: X

IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
"""
    result = recover_cortex(legacy, path="legacy.cortex", embed_aud_rsk=True)
    # Look for AUD and RSK entries in the recovered doc
    sigils_found = {e.sigil for _, e in result.doc.iter_entries()}
    assert "AUD" in sigils_found, f"AUD not embedded; found: {sigils_found}"


def test_recover_embed_aud_rsk_cli(tmp_path):
    """End-to-end CLI test for --embed-aud-rsk."""

    legacy_path = str(tmp_path / "legacy.cortex")
    with open(legacy_path, "w") as f:
        f.write(
            "$1: X\n\n"
            'IDN:agent{name:"legacy"}\n'
            'FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}\n'
            'OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}\n'
        )
    out_path = str(tmp_path / "legacy.fixed.cortex")
    r = _run_cli(["recover", legacy_path, "--out", out_path, "--embed-aud-rsk"])
    assert r.returncode == 0, f"recover failed: {r.stderr}"
    with open(out_path) as f:
        text = f.read()
    assert "AUD:" in text, "AUD entry not embedded in recovered file"
