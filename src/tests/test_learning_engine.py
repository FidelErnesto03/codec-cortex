"""Unit + integration tests for the CODEC-CORTEX Learning Engine (CLE).

These tests cover SPEC §10 (Unit tests), §10.2 (Integration tests),
§10.3 (Regression anchor) and §11.1 (checks automáticos mínimos).

Run::

    pytest cli/src/tests/test_learning_engine.py -q
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

# Ensure src/ is importable when tests run from the project root.
HERE = Path(__file__).resolve().parent
SRC = HERE.parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cortex.core.parser import parse_cortex  # noqa: E402
from cortex.learning import ALGORITHM, ENGINE_VERSION, SCHEMA_VERSION  # noqa: E402
from cortex.learning.candidates import detect_candidates  # noqa: E402
from cortex.learning.conditions import parse_condition  # noqa: E402
from cortex.learning.elevation import (  # noqa: E402
    apply_patch,
    plan_patch,
    render_diff,
)
from cortex.learning.errors import LearningError  # noqa: E402
from cortex.learning.index import (  # noqa: E402
    is_stale,
    load_index,
    rebuild_for_workspace,
)
from cortex.learning.policy import parse_policy_document  # noqa: E402
from cortex.learning.policy_defaults import default_policy_text  # noqa: E402
from cortex.learning.scoring import (  # noqa: E402
    derive_read_priority,
    detect_signals,
    score_hotness,
    score_promotion,
    score_risk,
    stable_fingerprint,
    Thresholds,
)
from cortex.learning.workspace import (  # noqa: E402
    Workspace,
    init_workspace,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


SPEC_BRAIN = """# -- $0: GLOSSARY --
GSIG:SES{sigil:"SES", name:"session", type:"attrs", risk:"B", description:"session memory"}
GSIG:LNG{sigil:"LNG", name:"lesson", type:"attrs", risk:"M", description:"learned lesson"}
GSIG:KNW{sigil:"KNW", name:"knowledge", type:"attrs", risk:"M", description:"operational knowledge"}
GSIG:CNST{sigil:"CNST", name:"constraint", type:"attrs", risk:"H", description:"hard rule"}
GSIG:IDN{sigil:"IDN", name:"identity", type:"attrs", risk:"B", description:"identity"}
GSIG:DOM{sigil:"DOM", name:"domain", type:"attrs", risk:"B", description:"domain"}
GSIG:REF{sigil:"REF", name:"reference", type:"attrs", risk:"B", description:"reference"}

# -- $1: IDENTITY --
IDN:agent{name:"test_agent", role:"operator"}
DOM:workspace{area:"testing", protocol:"CODEC-CORTEX", artifact:"brain.cortex"}

# -- $2: SESSIONS --
SES:policy_externalization_1{topic:"learning policies", outcome:"policy should be external to brain", user_validated:true}
SES:policy_externalization_2{topic:"learning policies", outcome:"policy should be external to brain", user_validated:true}
SES:policy_externalization_3{topic:"learning policies", outcome:"policy should be external to brain", user_validated:true}
LNG:score_performance{type:"operational", cause:"spec_review", lesson:"learning score exists to improve runtime performance, not auditability", prevention:"keep scores in derived index", user_validated:true}

# -- $3: GOVERNANCE --
CNST:blocking_rule{rule:"LLM must not mutate brain directly", severity:"blocking", survive:"min"}
"""


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Workspace:
    """Initialize a fresh workspace in tmp_path and return it."""

    return init_workspace(tmp_path)


@pytest.fixture
def spec_workspace(tmp_path: Path) -> Workspace:
    """Workspace with the SPEC §16.1 brain installed."""

    ws = init_workspace(tmp_path)
    ws.brain_path.write_text(SPEC_BRAIN, encoding="utf-8")
    return ws


# ---------------------------------------------------------------------------
# §10.1 — Unit tests
# ---------------------------------------------------------------------------


class TestWorkspaceDiscovery:
    """1, 2 — Workspace discovery + manifest parsing."""

    def test_init_creates_canonical_layout(self, tmp_path: Path) -> None:
        ws = init_workspace(tmp_path)
        assert ws.cortex_dir.is_dir()
        assert ws.manifest_path.exists()
        assert ws.brain_path.exists()
        assert ws.policy_path is not None and ws.policy_path.exists()
        assert ws.index_path.parent.is_dir()
        assert ws.cache_dir.is_dir()

    def test_discover_finds_workspace(self, tmp_workspace: Workspace) -> None:
        ws = Workspace.discover(tmp_workspace.root)
        assert ws.cortex_dir == tmp_workspace.cortex_dir

    def test_discover_walks_up(self, tmp_workspace: Workspace) -> None:
        sub = tmp_workspace.root / "deep" / "nested" / "dir"
        sub.mkdir(parents=True)
        ws = Workspace.discover(sub)
        assert ws.cortex_dir == tmp_workspace.cortex_dir

    def test_manifest_parses(self, tmp_workspace: Workspace) -> None:
        doc = parse_cortex(tmp_workspace.manifest_path.read_text(encoding="utf-8"))
        # Must contain IDN:workspace and REF:brain at minimum
        ids = [e.name for _, e in doc.iter_entries() if e.sigil == "IDN"]
        assert "workspace" in ids
        refs = [e.name for _, e in doc.iter_entries() if e.sigil == "REF"]
        assert "brain" in refs

    def test_init_is_idempotent(self, tmp_path: Path) -> None:
        ws1 = init_workspace(tmp_path)
        brain_hash_1 = ws1.brain_hash()
        # Second call without --force should preserve brain content
        ws2 = init_workspace(tmp_path)
        assert ws2.brain_hash() == brain_hash_1


class TestPolicyParsing:
    """3, 4, 5 — Policy parsing and validation."""

    def test_default_policy_parses(self) -> None:
        doc = parse_cortex(default_policy_text())
        ps = parse_policy_document(doc)
        assert ps.identity["name"] == "default_learning_policies"
        assert ps.thresholds.candidate == 5
        assert ps.thresholds.critical == 21
        assert "IDN" in ps.protected.items
        assert "CNST:blocking" in ps.protected.items
        # 4 policies: candidate_detection, candidate_elevation,
        # auto_ses_to_lng, auto_lng_to_knw
        assert len(ps.policies) == 4
        assert {p.id for p in ps.policies} == {
            "candidate_detection", "candidate_elevation",
            "auto_ses_to_lng", "auto_lng_to_knw",
        }

    def test_invalid_action_rejected(self) -> None:
        text = default_policy_text().replace(
            'action:"apply", requires:"policy_authorized"',
            'action:"commit", requires:"policy_authorized"',
        )
        doc = parse_cortex(text)
        with pytest.raises(LearningError):
            parse_policy_document(doc)

    def test_duplicate_policy_id_rejected(self) -> None:
        text = default_policy_text() + (
            '\nPOL:auto_ses_to_lng{source:"SES", target:"LNG", '
            'when:"promotion_score>=8", action:"score", requires:""}'
        )
        doc = parse_cortex(text)
        with pytest.raises(LearningError):
            parse_policy_document(doc)

    def test_protected_targets_default_when_missing(self) -> None:
        text = """# -- $0: GLOSSARY --
GSIG:IDN{sigil:"IDN", name:"identity", type:"attrs", risk:"B", description:"id"}
GSIG:POL{sigil:"POL", name:"policy", type:"attrs", risk:"M", description:"policy"}

# -- $1: IDENTITY --
IDN:learn_policies{name:"minimal", version:"0.0.1", target:"brain"}

# -- $2: POLICIES --
POL:only_one{source:"SES", target:"LNG", when:"promotion_score>=8", action:"propose", requires:"user_confirmation"}
"""
        doc = parse_cortex(text)
        ps = parse_policy_document(doc)
        # Default protection list should be applied
        assert "IDN" in ps.protected.items
        assert "CLAIM" in ps.protected.items


class TestHashing:
    """6, 7, 8 — Hashing and index invalidation."""

    def test_brain_hash_stable(self, tmp_workspace: Workspace) -> None:
        h1 = tmp_workspace.brain_hash()
        h2 = tmp_workspace.brain_hash()
        assert h1 == h2
        assert h1.startswith("sha256:")

    def test_policy_hash_stable(self, tmp_workspace: Workspace) -> None:
        h1 = tmp_workspace.policy_hash()
        h2 = tmp_workspace.policy_hash()
        assert h1 == h2

    def test_index_invalidated_on_brain_change(self, tmp_workspace: Workspace) -> None:
        idx = rebuild_for_workspace(tmp_workspace)
        assert not is_stale(idx, tmp_workspace.brain_hash(), tmp_workspace.policy_hash())
        # Mutate brain
        original = tmp_workspace.brain_path.read_text(encoding="utf-8")
        tmp_workspace.brain_path.write_text(original + "\nSES:new{topic:\"x\", outcome:\"y\", user_validated:true}\n", encoding="utf-8")
        assert is_stale(idx, tmp_workspace.brain_hash(), tmp_workspace.policy_hash())

    def test_index_invalidated_on_policy_change(self, tmp_workspace: Workspace) -> None:
        idx = rebuild_for_workspace(tmp_workspace)
        # Mutate policy
        original = tmp_workspace.policy_path.read_text(encoding="utf-8")
        tmp_workspace.policy_path.write_text(original + "\n# extra\n", encoding="utf-8")
        assert is_stale(idx, tmp_workspace.brain_hash(), tmp_workspace.policy_hash())


class TestFingerprint:
    """9 — Stable fingerprint."""

    def test_equivalent_entries_have_same_fingerprint(self) -> None:
        doc1 = parse_cortex(SPEC_BRAIN)
        doc2 = parse_cortex(SPEC_BRAIN)
        for (s1, e1), (s2, e2) in zip(doc1.iter_entries(), doc2.iter_entries()):
            assert stable_fingerprint(e1) == stable_fingerprint(e2)

    def test_different_entries_have_different_fingerprints(self) -> None:
        text_a = SPEC_BRAIN
        text_b = SPEC_BRAIN.replace("test_agent", "other_agent")
        doc_a = parse_cortex(text_a)
        doc_b = parse_cortex(text_b)
        # The IDN:agent entry should differ
        a_agent = next(e for _, e in doc_a.iter_entries() if e.sigil == "IDN" and e.name == "agent")
        b_agent = next(e for _, e in doc_b.iter_entries() if e.sigil == "IDN" and e.name == "agent")
        assert stable_fingerprint(a_agent) != stable_fingerprint(b_agent)


class TestScoring:
    """10, 11, 12 — Fibonacci scoring, priority derivation, candidate detection."""

    def test_fibonacci_thresholds(self) -> None:
        t = Thresholds()
        assert t.observed == 1
        assert t.repeated == 2
        assert t.pattern == 3
        assert t.candidate == 5
        assert t.ask_user == 8
        assert t.strong_candidate == 13
        assert t.critical == 21

    def test_hotness_rewards_repeated(self, spec_workspace: Workspace) -> None:
        brain = spec_workspace.parse_brain()
        parse_policy_document(spec_workspace.parse_policy())
        ses_entries = [e for _, e in brain.iter_entries() if e.sigil == "SES"]
        assert len(ses_entries) == 3
        # All three share the same cluster key → pattern signal
        from cortex.learning.index import _compute_cluster_map
        cluster = _compute_cluster_map(ses_entries)
        assert any(v >= 3 for v in cluster.values())

    def test_promotion_for_user_validated(self, spec_workspace: Workspace) -> None:
        brain = spec_workspace.parse_brain()
        ps = parse_policy_document(spec_workspace.parse_policy())
        ses = next(e for _, e in brain.iter_entries() if e.sigil == "SES")
        signals = detect_signals(ses, brain, ps, cluster_hits=3)
        assert "user_validated" in signals.signals
        promo = score_promotion(signals, ps.thresholds)
        assert promo >= ps.thresholds.ask_user  # >= 8

    def test_read_priority_for_blocking_cnst(self, spec_workspace: Workspace) -> None:
        brain = spec_workspace.parse_brain()
        ps = parse_policy_document(spec_workspace.parse_policy())
        cnst = next(e for _, e in brain.iter_entries() if e.sigil == "CNST")
        signals = detect_signals(cnst, brain, ps, cluster_hits=1)
        hot = score_hotness(signals, ps.thresholds)
        promo = score_promotion(signals, ps.thresholds)
        risk = score_risk(cnst, signals, ps.thresholds)
        prio = derive_read_priority(cnst, hot, promo, risk, ps.thresholds)
        assert prio == "P0"  # blocking CNST → P0 per SPEC §6.3

    def test_candidate_detection_finds_ses_cluster(self, spec_workspace: Workspace) -> None:
        brain = spec_workspace.parse_brain()
        ps = parse_policy_document(spec_workspace.parse_policy())
        idx = rebuild_for_workspace(spec_workspace)
        cands = detect_candidates(brain, idx, ps)
        # At least one SES→LNG candidate with promotion_score >= 5
        ses_cands = [c for c in cands if c.target == "LNG"]
        assert len(ses_cands) >= 1
        assert ses_cands[0].promotion_score >= 5
        assert "SES:policy_externalization_1" in ses_cands[0].source_entries


class TestConditions:
    """16 — Conditions without eval."""

    def test_basic_and(self) -> None:
        cond = parse_condition("promotion_score>=8|user_validated=true")
        assert cond.evaluate({"promotion_score": 8, "user_validated": True})
        assert not cond.evaluate({"promotion_score": 7, "user_validated": True})
        assert not cond.evaluate({"promotion_score": 8, "user_validated": False})

    def test_string_equality(self) -> None:
        cond = parse_condition('source=="SES"')
        assert cond.evaluate({"source": "SES"})
        assert not cond.evaluate({"source": "LNG"})

    def test_not_equal(self) -> None:
        cond = parse_condition("status!=blocked")
        assert cond.evaluate({"status": "current"})
        assert not cond.evaluate({"status": "blocked"})

    def test_invalid_clause_fails_closed(self) -> None:
        with pytest.raises(LearningError):
            parse_condition("promotion_score>=8||user_validated=true")

    def test_no_operator_fails_closed(self) -> None:
        with pytest.raises(LearningError):
            parse_condition("just_a_word")

    def test_empty_condition_is_true(self) -> None:
        cond = parse_condition("")
        assert cond.evaluate({})

    def test_no_eval_function_used(self) -> None:
        """Verify the conditions module never imports eval/exec."""
        import cortex.learning.conditions as cmod
        src = Path(cmod.__file__).read_text(encoding="utf-8")
        assert "eval(" not in src
        assert "exec(" not in src
        # The word "eval" appears only in docstrings/error messages
        # Ensure there's no `eval(` function call
        assert not any(line.strip().startswith("eval(") for line in src.splitlines())


class TestElevation:
    """13, 14, 15, 17, 18 — Elevation, dry-run, apply, protection."""

    def test_propose_does_not_mutate_brain(self, spec_workspace: Workspace) -> None:
        brain = spec_workspace.parse_brain()
        ps = parse_policy_document(spec_workspace.parse_policy())
        idx = rebuild_for_workspace(spec_workspace)
        cands = detect_candidates(brain, idx, ps)
        ses_cand = next(c for c in cands if c.target == "LNG")
        patch = plan_patch(brain, ps, ses_cand)
        brain_hash_before = spec_workspace.brain_hash()
        result = apply_patch(spec_workspace, brain, patch, mode="dry-run")
        assert result["applied"] is False
        # Brain untouched
        assert spec_workspace.brain_hash() == brain_hash_before

    def test_dry_run_generates_diff(self, spec_workspace: Workspace) -> None:
        brain = spec_workspace.parse_brain()
        ps = parse_policy_document(spec_workspace.parse_policy())
        idx = rebuild_for_workspace(spec_workspace)
        cands = detect_candidates(brain, idx, ps)
        ses_cand = next(c for c in cands if c.target == "LNG")
        patch = plan_patch(brain, ps, ses_cand)
        diff = render_diff(brain, patch)
        assert "Patch mode" in diff
        assert "+LNG:" in diff
        assert "policy_externalization" in diff

    def test_apply_with_policy_writes_brain(self, spec_workspace: Workspace) -> None:
        brain = spec_workspace.parse_brain()
        ps = parse_policy_document(spec_workspace.parse_policy())
        idx = rebuild_for_workspace(spec_workspace)
        cands = detect_candidates(brain, idx, ps)
        ses_cand = next(c for c in cands if c.target == "LNG")
        patch = plan_patch(
            brain, ps, ses_cand,
            policy_id="auto_ses_to_lng",
            user_confirmed=True,
        )
        result = apply_patch(spec_workspace, brain, patch, mode="apply", confirm=True)
        assert result["applied"] is True
        # Brain now contains the elevated entry
        new_brain = spec_workspace.parse_brain()
        lng_entries = [e for _, e in new_brain.iter_entries() if e.sigil == "LNG"]
        names = [e.name for e in lng_entries]
        assert "policy_externalization" in names

    def test_apply_without_confirm_blocked(self, spec_workspace: Workspace) -> None:
        brain = spec_workspace.parse_brain()
        ps = parse_policy_document(spec_workspace.parse_policy())
        idx = rebuild_for_workspace(spec_workspace)
        cands = detect_candidates(brain, idx, ps)
        ses_cand = next(c for c in cands if c.target == "LNG")
        patch = plan_patch(brain, ps, ses_cand)
        with pytest.raises(LearningError):
            apply_patch(spec_workspace, brain, patch, mode="apply", confirm=False)

    def test_apply_then_verify_post_apply(self, spec_workspace: Workspace) -> None:
        brain = spec_workspace.parse_brain()
        ps = parse_policy_document(spec_workspace.parse_policy())
        idx = rebuild_for_workspace(spec_workspace)
        cands = detect_candidates(brain, idx, ps)
        ses_cand = next(c for c in cands if c.target == "LNG")
        patch = plan_patch(brain, ps, ses_cand, policy_id="auto_ses_to_lng", user_confirmed=True)
        apply_patch(spec_workspace, brain, patch, mode="apply", confirm=True)
        from cortex.learning.elevation import verify_post_apply
        report = verify_post_apply(spec_workspace)
        assert report["index_entries"] >= 1
        assert report["brain_entries"] >= 1

    def test_protected_sigil_blocks_elevation(self, tmp_workspace: Workspace) -> None:
        """Try to elevate a CNST:blocking entry — should produce mode='block'."""
        # Install a brain with a CNST:blocking entry that ALSO looks like
        # a candidate (won't normally happen because detect_candidates
        # filters protected sigils, but plan_patch must defend in depth).
        brain_text = """# -- $0: GLOSSARY --
GSIG:IDN{sigil:"IDN", name:"identity", type:"attrs", risk:"B", description:"id"}
GSIG:DOM{sigil:"DOM", name:"domain", type:"attrs", risk:"B", description:"domain"}
GSIG:CNST{sigil:"CNST", name:"constraint", type:"attrs", risk:"H", description:"hard rule"}
GSIG:SES{sigil:"SES", name:"session", type:"attrs", risk:"B", description:"session"}
GSIG:LNG{sigil:"LNG", name:"lesson", type:"attrs", risk:"M", description:"lesson"}

# -- $1: IDENTITY --
IDN:agent{name:"a", role:"operator"}
DOM:workspace{area:"x", protocol:"CODEC-CORTEX", artifact:"brain.cortex"}

# -- $2: SESSIONS --
SES:x_1{topic:"x", outcome:"y", user_validated:true}
SES:x_2{topic:"x", outcome:"y", user_validated:true}

# -- $3: GOVERNANCE --
CNST:blocking_rule{rule:"don't touch", severity:"blocking", survive:"min"}
"""
        tmp_workspace.brain_path.write_text(brain_text, encoding="utf-8")
        brain = tmp_workspace.parse_brain()
        ps = parse_policy_document(tmp_workspace.parse_policy())
        # Manually craft a candidate that targets a protected sigil
        from cortex.learning.candidates import Candidate
        fake = Candidate(
            candidate_id="cand_xxx",
            source_entries=["CNST:blocking_rule"],
            target="KNW",  # not in _DEFAULT_TARGET but plan_patch checks protection first
            promotion_score=21,
            hotness_score=21,
            risk_weight=21,
            read_priority="P0",
            suggested_action="block",
            policy_match=None,
            reason="attempt to elevate protected CNST",
        )
        patch = plan_patch(brain, ps, fake)
        assert patch.mode == "block"


class TestIndexRebuild:
    """Rebuild determinism + JSON validity."""

    def test_rebuild_is_deterministic(self, spec_workspace: Workspace) -> None:
        idx1 = rebuild_for_workspace(spec_workspace)
        # Wipe and rebuild
        spec_workspace.index_path.unlink()
        idx2 = rebuild_for_workspace(spec_workspace)
        assert idx1.to_json() == idx2.to_json()

    def test_index_json_roundtrip(self, spec_workspace: Workspace) -> None:
        idx = rebuild_for_workspace(spec_workspace)
        # Reload from disk
        idx2 = load_index(spec_workspace.index_path)
        assert idx2.brain_hash == idx.brain_hash
        assert idx2.policy_hash == idx.policy_hash
        assert idx2.engine_version == ENGINE_VERSION
        assert idx2.algorithm == ALGORITHM
        assert set(idx2.entries.keys()) == set(idx.entries.keys())

    def test_index_schema_fields(self, spec_workspace: Workspace) -> None:
        idx = rebuild_for_workspace(spec_workspace)
        d = idx.to_dict()
        assert d["schema_version"] == SCHEMA_VERSION
        assert d["engine_version"] == ENGINE_VERSION
        assert d["algorithm"] == ALGORITHM
        for k, v in d["entries"].items():
            assert "entry_id" in v
            assert "selector" in v
            assert "fingerprint" in v
            assert "hotness_score" in v
            assert "promotion_score" in v
            assert "risk_weight" in v
            assert "read_priority" in v
            assert "candidate" in v
            assert "signals" in v


# ---------------------------------------------------------------------------
# §10.2 — Integration tests
# ---------------------------------------------------------------------------


class TestIntegrationCLI:
    """Run the actual CLI through subprocess to mirror SPEC §10.2."""

    def _run(self, *args, cwd=None):
        import subprocess
        env = dict(os.environ)
        env["PYTHONPATH"] = str(SRC)
        # Use the installed `cortex` entry point (which routes through
        # main_e3 then main). Falls back to `python -m cortex.cli.main_e3`
        # if cortex is not on $PATH.
        import shutil
        cortex_bin = shutil.which("cortex")
        if cortex_bin:
            cmd = [cortex_bin, "learn", *args]
        else:
            cmd = [sys.executable, "-m", "cortex.cli.main_e3", "learn", *args]
        r = subprocess.run(
            cmd, capture_output=True, text=True, env=env, cwd=cwd,
        )
        return r

    def test_case_a_init_and_doctor(self, tmp_path: Path) -> None:
        r = self._run("init", "--workspace", str(tmp_path))
        assert r.returncode == 0, r.stderr
        r = self._run("doctor", "--workspace", str(tmp_path), "--json")
        assert r.returncode == 0
        d = json.loads(r.stdout)
        assert d["ok"] is True

    def test_case_b_index_rebuild_and_status(self, tmp_path: Path) -> None:
        self._run("init", "--workspace", str(tmp_path))
        r = self._run("index", "rebuild", "--workspace", str(tmp_path))
        assert r.returncode == 0
        r = self._run("index", "status", "--workspace", str(tmp_path), "--json")
        d = json.loads(r.stdout)
        assert d["present"] is True
        assert d["stale"] is False

    def test_case_c_scan_and_candidates(self, spec_workspace: Workspace) -> None:
        ws = spec_workspace
        r = self._run("scan", "--workspace", str(ws.root), "--json")
        assert r.returncode == 0
        d = json.loads(r.stdout)
        assert len(d["entries"]) >= 1
        r = self._run("candidates", "--limit", "5", "--workspace", str(ws.root), "--json")
        d = json.loads(r.stdout)
        assert "candidates" in d
        # The SPEC §16.1 brain should yield at least one SES→LNG candidate
        ses_cands = [c for c in d["candidates"] if c["target"] == "LNG"]
        assert len(ses_cands) >= 1
        assert ses_cands[0]["promotion_score"] >= 5

    def test_case_d_dry_run_no_mutation(self, spec_workspace: Workspace) -> None:
        ws = spec_workspace
        before = ws.brain_hash()
        # Find a candidate
        r = self._run("candidates", "--workspace", str(ws.root), "--json")
        cands = json.loads(r.stdout)["candidates"]
        cand_id = cands[0]["candidate_id"]
        r = self._run("elevate", "--candidate", cand_id, "--dry-run", "--workspace", str(ws.root), "--json")
        assert r.returncode == 0, r.stderr
        d = json.loads(r.stdout)
        assert d["applied"] is False
        assert ws.brain_hash() == before  # brain untouched

    def test_case_e_policy_driven_apply(self, spec_workspace: Workspace) -> None:
        ws = spec_workspace
        before = ws.brain_hash()
        r = self._run("elevate", "--policy", "auto_ses_to_lng", "--apply", "--confirm",
                      "--workspace", str(ws.root), "--json")
        assert r.returncode == 0, r.stderr
        d = json.loads(r.stdout)
        assert d["applied"] is True
        assert ws.brain_hash() != before  # brain was mutated

    def test_case_f_critical_protection(self, spec_workspace: Workspace) -> None:
        """Common policy cannot mutate CNST:blocking."""
        ws = spec_workspace
        brain = ws.parse_brain()
        ps = parse_policy_document(ws.parse_policy())
        from cortex.learning.candidates import Candidate
        fake = Candidate(
            candidate_id="cand_cnst",
            source_entries=["CNST:blocking_rule"],
            target="KNW",
            promotion_score=21,
            hotness_score=21,
            risk_weight=21,
            read_priority="P0",
            suggested_action="block",
            policy_match=None,
            reason="attempt elevate CNST",
        )
        patch = plan_patch(brain, ps, fake, policy_id=None)
        assert patch.mode == "block"


# ---------------------------------------------------------------------------
# §11.1 — Forbidden patterns
# ---------------------------------------------------------------------------


class TestForbiddenPatterns:
    """SPEC §11.1 — automatic checks."""

    def test_no_llm_or_network_imports(self) -> None:
        import cortex.learning
        learn_dir = Path(cortex.learning.__file__).parent
        bad = ["openai", "anthropic", "requests", "httpx", "urllib"]
        for py in learn_dir.rglob("*.py"):
            text = py.read_text(encoding="utf-8")
            for token in bad:
                # Allow the token to appear only in comments or strings,
                # never as an import statement.
                for line in text.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    if stripped.startswith("import ") or stripped.startswith("from "):
                        assert token not in stripped, \
                            f"forbidden import in {py.name}: {stripped}"

    def test_no_eval_or_exec_calls(self) -> None:
        import cortex.learning
        learn_dir = Path(cortex.learning.__file__).parent
        for py in learn_dir.rglob("*.py"):
            text = py.read_text(encoding="utf-8")
            # Reject any "eval(" or "exec(" that isn't in a comment.
            for i, line in enumerate(text.splitlines(), 1):
                code = line.split("#", 1)[0]
                assert "eval(" not in code, f"{py.name}:{i}: eval( in {line!r}"
                assert "exec(" not in code, f"{py.name}:{i}: exec( in {line!r}"

    def test_no_time_based_results(self) -> None:
        """Score determinism: no time-module usage that influences results."""
        import cortex.learning
        learn_dir = Path(cortex.learning.__file__).parent
        for py in learn_dir.rglob("*.py"):
            text = py.read_text(encoding="utf-8")
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                # time module is allowed only in comments/strings; the
                # engine must be deterministic.
                if "import time" in stripped or "from time" in stripped:
                    pytest.fail(f"time import in {py.name}: {stripped}")

    def test_index_rebuildable_after_deletion(self, spec_workspace: Workspace) -> None:
        """SPEC §1.3 — index must be regenerable from brain + policy."""
        ws = spec_workspace
        idx1 = rebuild_for_workspace(ws)
        # Delete the index
        ws.index_path.unlink()
        assert not ws.index_path.exists()
        # Rebuild
        idx2 = rebuild_for_workspace(ws)
        assert idx2.to_json() == idx1.to_json()

    def test_brain_has_no_runtime_scores(self, spec_workspace: Workspace) -> None:
        """SPEC §11 cert check #11 — brain must not carry scores."""
        brain_text = spec_workspace.read_brain()
        # The words 'hotness_score' or 'promotion_score' should not
        # appear in brain.cortex (they belong only to learn-index.json).
        assert "hotness_score" not in brain_text
        assert "promotion_score" not in brain_text
        assert "read_priority" not in brain_text

    def test_no_learn_ledger_dependency(self, tmp_workspace: Workspace) -> None:
        """SPEC §1.6 — learn-ledger.cortex must NOT be a dependency."""
        assert not (tmp_workspace.cortex_dir / "learn-ledger.cortex").exists()
        # The learning engine should work fine without it — verified
        # implicitly by every other test in this file.


# ---------------------------------------------------------------------------
# §17 — Expected JSON shape of `learn candidates --json`
# ---------------------------------------------------------------------------


class TestCandidatesJsonShape:
    """SPEC §17 — verify the candidates JSON payload structure."""

    def test_payload_has_required_keys(self, spec_workspace: Workspace) -> None:
        ws = spec_workspace
        r = TestIntegrationCLI()._run(
            "candidates", "--limit", "10", "--workspace", str(ws.root), "--json",
        )
        d = json.loads(r.stdout)
        assert "brain_hash" in d
        assert "policy_hash" in d
        assert "stale_index" in d
        assert "candidates" in d
        assert d["brain_hash"].startswith("sha256:")
        for c in d["candidates"]:
            assert "candidate_id" in c
            assert "source_entries" in c
            assert "target" in c
            assert "promotion_score" in c
            assert "hotness_score" in c
            assert "risk_weight" in c
            assert "read_priority" in c
            assert "suggested_action" in c
