"""Tests for the CODEC-CORTEX Learning Engine v0.2.0 (Fases A–E).

Covers the new functionality defined in ``learning-engine-evolution.md``:

- A. Ciclo de sesión (``cortex session start/status/consolidate/close``)
- B. Auto-detección en handlers (``cortex learn pre-action/post-action``)
- C. Decay y enfriamiento (``cooling_factor``, ``apply_decay_to_index``)
- D. Feedback loop (``cortex learn feedback``, adaptive thresholds)
- E. Thresholds configurables (profiles, ``policy set/profile/reset``)

Run::

    pytest cli/src/tests/test_learning_engine_v02.py -q
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cortex.core.parser import parse_cortex  # noqa: E402
from cortex.learning import ENGINE_VERSION  # noqa: E402
from cortex.learning.candidates import detect_candidates  # noqa: E402
from cortex.learning.decay import (  # noqa: E402
    apply_decay_to_index,
    cooling_factor,
)
from cortex.learning.errors import LearningError  # noqa: E402
from cortex.learning.feedback import (  # noqa: E402
    adjust_thresholds,
    derive_candidate_type,
    derive_sigil_pattern,
    load_feedback_history,
    record_feedback,
)
from cortex.learning.handlers import (  # noqa: E402
    load_signals,
    post_action,
    pre_action,
    save_signals,
)
from cortex.learning.index import rebuild_for_workspace  # noqa: E402
from cortex.learning.policy import (  # noqa: E402
    parse_policy_document,
)
from cortex.learning.policy_defaults import (  # noqa: E402
    PROFILES,
    aggressive_policy_text,
    conservative_policy_text,
    default_policy_text,
)
from cortex.learning.session import (  # noqa: E402
    SES_CURRENT_NAME,
    SES_LAST_NAME,
    session_close,
    session_consolidate,
    session_start,
    session_status,
)
from cortex.learning.workspace import Workspace, init_workspace  # noqa: E402


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
    return init_workspace(tmp_path)


@pytest.fixture
def spec_workspace(tmp_path: Path) -> Workspace:
    ws = init_workspace(tmp_path)
    ws.brain_path.write_text(SPEC_BRAIN, encoding="utf-8")
    return ws


# ---------------------------------------------------------------------------
# Fase E — Configurable thresholds
# ---------------------------------------------------------------------------


class TestConfigurableThresholds:
    """SPEC §E — fibonacci_thresholds / cooling / detection / feedback / protected_patterns."""

    def test_default_policy_has_v02_blocks(self) -> None:
        text = default_policy_text()
        assert "POL:fibonacci_thresholds{ses:1, lng:3, knw:8, auto_knw:13}" in text
        assert "POL:cooling{half_life_days:7, min_score_to_survive:1}" in text
        assert "POL:detection{same_sigil_in_window:3, window_hours:72, cross_session:true}" in text
        assert "POL:feedback{adaptive:true, adjustment_rate:0.1, min_threshold:1, max_threshold:20}" in text
        assert 'POL:protected_patterns{patterns:"CNST:*|!:*|FCS:*|OBJ:*"}' in text

    def test_default_parses_to_config_objects(self) -> None:
        ps = parse_policy_document(parse_cortex(default_policy_text()))
        assert ps.fibonacci_thresholds.ses == 1
        assert ps.fibonacci_thresholds.lng == 3
        assert ps.fibonacci_thresholds.knw == 8
        assert ps.fibonacci_thresholds.auto_knw == 13
        assert ps.cooling.half_life_days == 7
        assert ps.cooling.min_score_to_survive == 1
        assert ps.detection.same_sigil_in_window == 3
        assert ps.detection.window_hours == 72
        assert ps.detection.cross_session is True
        assert ps.feedback.adaptive is True
        assert ps.feedback.adjustment_rate == 0.1
        assert "CNST:*" in ps.protected_patterns.patterns

    def test_aggressive_profile_changes_thresholds(self) -> None:
        text = aggressive_policy_text()
        assert "lng:2" in text
        assert "knw:5" in text
        assert "half_life_days:3" in text

    def test_conservative_profile_changes_thresholds(self) -> None:
        text = conservative_policy_text()
        assert "lng:5" in text
        assert "knw:13" in text
        assert "half_life_days:30" in text

    def test_profiles_dict_has_three_entries(self) -> None:
        assert set(PROFILES.keys()) == {"default", "aggressive", "conservative"}

    def test_protected_patterns_match(self) -> None:
        ps = parse_policy_document(parse_cortex(default_policy_text()))
        # CNST:* matches any CNST entry
        assert ps.is_protected_pattern("CNST", "anything")
        assert ps.is_protected_pattern("CNST", "blocking_rule")
        # FCS:* matches FCS
        assert ps.is_protected_pattern("FCS", "primary")
        # LNG is NOT in protected_patterns
        assert not ps.is_protected_pattern("LNG", "score_performance")


# ---------------------------------------------------------------------------
# Fase A — Session lifecycle
# ---------------------------------------------------------------------------


class TestSessionLifecycle:
    """SPEC §A — cortex session start/status/consolidate/close."""

    def test_start_creates_ses_current(self, tmp_workspace: Workspace) -> None:
        state = session_start(tmp_workspace, input_text="test session")
        assert state.status == "running"
        assert state.session_id  # non-empty
        # Brain should now contain SES:current
        brain = tmp_workspace.parse_brain()
        ses_entries = [e for _, e in brain.iter_entries() if e.sigil == "SES" and e.name == SES_CURRENT_NAME]
        assert len(ses_entries) == 1
        assert ses_entries[0].value["status"] == "running"

    def test_start_twice_blocks(self, tmp_workspace: Workspace) -> None:
        session_start(tmp_workspace)
        with pytest.raises(LearningError):
            session_start(tmp_workspace)

    def test_status_no_active_session(self, tmp_workspace: Workspace) -> None:
        status = session_status(tmp_workspace)
        assert status["active"] is False

    def test_status_active_session(self, tmp_workspace: Workspace) -> None:
        session_start(tmp_workspace, input_text="active test")
        status = session_status(tmp_workspace)
        assert status["active"] is True
        assert "session_id" in status
        assert "duration" in status

    def test_consolidate_writes_ses_last(self, tmp_workspace: Workspace) -> None:
        session_start(tmp_workspace, input_text="consolidation test")
        result = session_consolidate(
            tmp_workspace,
            input_text="input summary",
            output_text="output summary",
            outcome_text="outcome summary",
        )
        assert result["consolidated"] is True
        brain = tmp_workspace.parse_brain()
        ses_last = [e for _, e in brain.iter_entries() if e.sigil == "SES" and e.name == SES_LAST_NAME]
        assert len(ses_last) == 1
        assert ses_last[0].value["input"] == "input summary"
        assert ses_last[0].value["output"] == "output summary"

    def test_close_removes_ses_current(self, tmp_workspace: Workspace) -> None:
        session_start(tmp_workspace, input_text="close test")
        session_close(
            tmp_workspace,
            input_text="in", output_text="out", outcome_text="ok",
            run_decay=False,
        )
        brain = tmp_workspace.parse_brain()
        ses_current = [e for _, e in brain.iter_entries() if e.sigil == "SES" and e.name == SES_CURRENT_NAME]
        assert len(ses_current) == 0
        # SES:last should still be there
        ses_last = [e for _, e in brain.iter_entries() if e.sigil == "SES" and e.name == SES_LAST_NAME]
        assert len(ses_last) == 1

    def test_close_without_session_errors(self, tmp_workspace: Workspace) -> None:
        with pytest.raises(LearningError):
            session_close(tmp_workspace, run_decay=False)

    def test_close_with_decay_runs_decay(self, spec_workspace: Workspace) -> None:
        # Build an index with old timestamps
        rebuild_for_workspace(spec_workspace)
        session_start(spec_workspace, input_text="decay test")
        result = session_close(
            spec_workspace,
            input_text="in", output_text="out", outcome_text="ok",
            run_decay=True,
        )
        assert result["closed"] is True
        assert result["decay"] is not None
        assert result["decay"]["applied"] is True


# ---------------------------------------------------------------------------
# Fase B — Pre/post-action handlers
# ---------------------------------------------------------------------------


class TestHandlers:
    """SPEC §B — pre_action / post_action."""

    def test_pre_action_detects_themes(self, spec_workspace: Workspace) -> None:
        report = pre_action(spec_workspace, "Revisemos los benchmarks v2.2.2 otra vez")
        # Should have detected at least one theme
        assert len(report.themes_detected) > 0
        assert "benchmarks" in report.themes_detected
        assert not report.blocked

    def test_pre_action_accumulates_signals(self, spec_workspace: Workspace) -> None:
        # Call pre_action multiple times with the same theme
        for _ in range(3):
            pre_action(spec_workspace, "benchmarks benchmarks benchmarks")
        acc = load_signals(spec_workspace)
        assert "benchmarks" in acc.themes
        assert len(acc.themes["benchmarks"]) == 3

    def test_post_action_emits_notifications(self, spec_workspace: Workspace) -> None:
        rebuild_for_workspace(spec_workspace)
        report = post_action(spec_workspace, brain_modified=False)
        # The SPEC brain has at least one candidate with promotion_score >= 5
        assert len(report.candidates_above_threshold) >= 1
        assert len(report.notifications) >= 1

    def test_post_action_with_modification_logs_session_event(
        self, spec_workspace: Workspace,
    ) -> None:
        rebuild_for_workspace(spec_workspace)
        session_start(spec_workspace, input_text="handler test")
        report = post_action(spec_workspace, brain_modified=True)
        assert report.brain_modified is True

    def test_signals_cache_roundtrip(self, tmp_workspace: Workspace) -> None:
        from cortex.learning.handlers import SignalAccumulator
        acc = SignalAccumulator(themes={"foo": ["t1", "t2"]}, pending_candidates=["x"])
        save_signals(tmp_workspace, acc)
        loaded = load_signals(tmp_workspace)
        assert loaded.themes == {"foo": ["t1", "t2"]}
        assert loaded.pending_candidates == ["x"]


# ---------------------------------------------------------------------------
# Fase C — Decay / cooling
# ---------------------------------------------------------------------------


class TestDecay:
    """SPEC §C — cooling_factor, apply_decay_to_index."""

    def test_cooling_factor_zero_days(self) -> None:
        assert cooling_factor(0) == 1.0

    def test_cooling_factor_half_life(self) -> None:
        # At 7 days with default half-life of 7, factor should be 0.5
        assert abs(cooling_factor(7, half_life_days=7) - 0.5) < 1e-9

    def test_cooling_factor_two_half_lives(self) -> None:
        # At 14 days with default half-life of 7, factor should be 0.25
        assert abs(cooling_factor(14, half_life_days=7) - 0.25) < 1e-9

    def test_cooling_factor_30_days(self) -> None:
        # 30 days ≈ 0.05
        f = cooling_factor(30, half_life_days=7)
        assert 0.04 < f < 0.06

    def test_apply_decay_drops_old_entries(self, spec_workspace: Workspace) -> None:
        idx = rebuild_for_workspace(spec_workspace)
        ps = parse_policy_document(spec_workspace.parse_policy())
        # Force old timestamps on SES entries
        old_ts = "2026-06-01T00:00:00Z"
        for k, rec in idx.entries.items():
            if k.startswith("SES:"):
                rec.last_accessed = old_ts
        # Apply decay
        brain_doc = spec_workspace.parse_brain()
        now = datetime(2026, 7, 2, 0, 0, 0, tzinfo=timezone.utc)
        new_idx, report = apply_decay_to_index(idx, ps, now, brain_doc=brain_doc)
        # All SES entries should be dropped (30 days × 0.05 factor → 0)
        ses_dropped = [s for s in report.dropped if s.startswith("SES:")]
        assert len(ses_dropped) >= 3

    def test_apply_decay_preserves_structural_sigils(self, spec_workspace: Workspace) -> None:
        idx = rebuild_for_workspace(spec_workspace)
        ps = parse_policy_document(spec_workspace.parse_policy())
        # Force ALL entries old
        old_ts = "2026-06-01T00:00:00Z"
        for k, rec in idx.entries.items():
            rec.last_accessed = old_ts
        brain_doc = spec_workspace.parse_brain()
        now = datetime(2026, 7, 2, 0, 0, 0, tzinfo=timezone.utc)
        new_idx, report = apply_decay_to_index(idx, ps, now, brain_doc=brain_doc)
        # Structural sigils (IDN, DOM, CNST) should be in untouched, not dropped
        dropped_set = set(report.dropped)
        assert "IDN:agent" not in dropped_set
        assert "DOM:workspace" not in dropped_set
        assert "CNST:blocking_rule" not in dropped_set

    def test_apply_decay_cools_but_keeps_partial(self, spec_workspace: Workspace) -> None:
        idx = rebuild_for_workspace(spec_workspace)
        ps = parse_policy_document(spec_workspace.parse_policy())
        # Force 14-day-old timestamps on SES entries (factor ≈ 0.25)
        old_ts = "2026-06-18T00:00:00Z"
        for k, rec in idx.entries.items():
            if k.startswith("SES:"):
                rec.last_accessed = old_ts
        brain_doc = spec_workspace.parse_brain()
        now = datetime(2026, 7, 2, 0, 0, 0, tzinfo=timezone.utc)
        new_idx, report = apply_decay_to_index(idx, ps, now, brain_doc=brain_doc)
        # At least one SES entry should be cooled (not dropped)
        ses_cooled = [c for c in report.cooled if c["selector"].startswith("SES:")]
        assert len(ses_cooled) >= 1
        # Original 13 → cooled to ~3
        for c in ses_cooled:
            assert "13→" in c["promotion"]

    def test_survive_min_never_decays(self, spec_workspace: Workspace) -> None:
        """Entries with survive:"min" must not be cooled."""
        idx = rebuild_for_workspace(spec_workspace)
        ps = parse_policy_document(spec_workspace.parse_policy())
        old_ts = "2025-01-01T00:00:00Z"
        for k, rec in idx.entries.items():
            rec.last_accessed = old_ts
        brain_doc = spec_workspace.parse_brain()
        now = datetime(2026, 7, 2, 0, 0, 0, tzinfo=timezone.utc)
        new_idx, report = apply_decay_to_index(idx, ps, now, brain_doc=brain_doc)
        # CNST:blocking_rule has survive:"min" → must be untouched
        dropped_set = set(report.dropped)
        assert "CNST:blocking_rule" not in dropped_set


# ---------------------------------------------------------------------------
# Fase D — Feedback loop
# ---------------------------------------------------------------------------


class TestFeedback:
    """SPEC §D — feedback recording and adaptive thresholds."""

    def test_derive_candidate_type(self) -> None:
        assert derive_candidate_type("SES", "LNG") == "SES->LNG"
        assert derive_candidate_type("LNG", "KNW") == "LNG->KNW"

    def test_derive_sigil_pattern_strips_numeric_suffix(self) -> None:
        # policy_externalization_1 → policy_externalization_*
        pat = derive_sigil_pattern("SES", "policy_externalization_1")
        assert pat == "SES:policy_externalization_*"
        # No numeric suffix → unchanged
        pat = derive_sigil_pattern("LNG", "score_performance")
        assert pat == "LNG:score_performance"

    def test_record_feedback_persists(self, tmp_workspace: Workspace) -> None:
        history = record_feedback(
            tmp_workspace,
            candidate_id="cand_001",
            candidate_type="SES->LNG",
            sigil_pattern="SES:foo_*",
            decision=True,
            reason="accepted",
            promotion_score=13,
        )
        assert len(history.records) == 1
        # Reload from disk
        loaded = load_feedback_history(tmp_workspace)
        assert len(loaded.records) == 1
        assert loaded.records[0].decision is True

    def test_adjust_thresholds_lowers_when_acceptance_high(
        self, tmp_workspace: Workspace,
    ) -> None:
        # Record 4 accepts (rate 1.0 > 0.8)
        for i in range(4):
            record_feedback(
                tmp_workspace,
                candidate_id=f"cand_{i}",
                candidate_type="SES->LNG",
                sigil_pattern="SES:foo_*",
                decision=True,
                promotion_score=13,
            )
        ps = parse_policy_document(parse_cortex(default_policy_text()))
        history = load_feedback_history(tmp_workspace)
        adjusted = adjust_thresholds(history, ps)
        # Default lng threshold is 3; with 100% acceptance, should drop to 3 * 0.9 ≈ 3
        # (rounded). Verify it's <= default.
        assert "SES->LNG" in adjusted
        assert adjusted["SES->LNG"] <= ps.fibonacci_thresholds.lng

    def test_adjust_thresholds_raises_when_acceptance_low(
        self, tmp_workspace: Workspace,
    ) -> None:
        # Record 4 rejects (rate 0.0 < 0.3)
        for i in range(4):
            record_feedback(
                tmp_workspace,
                candidate_id=f"cand_{i}",
                candidate_type="SES->LNG",
                sigil_pattern="SES:foo_*",
                decision=False,
                reason="one-time event",
                promotion_score=5,
            )
        ps = parse_policy_document(parse_cortex(default_policy_text()))
        history = load_feedback_history(tmp_workspace)
        adjusted = adjust_thresholds(history, ps)
        # Default lng=3; with 0% acceptance, should rise to 3 * 1.2 = 3.6 → 4
        assert "SES->LNG" in adjusted
        assert adjusted["SES->LNG"] >= ps.fibonacci_thresholds.lng

    def test_adjust_thresholds_skipped_when_adaptive_false(
        self, tmp_workspace: Workspace,
    ) -> None:
        for i in range(4):
            record_feedback(
                tmp_workspace,
                candidate_id=f"cand_{i}",
                candidate_type="SES->LNG",
                sigil_pattern="SES:foo_*",
                decision=True,
                promotion_score=13,
            )
        # Disable adaptive
        text = default_policy_text().replace(
            "POL:feedback{adaptive:true", "POL:feedback{adaptive:false",
        )
        ps = parse_policy_document(parse_cortex(text))
        history = load_feedback_history(tmp_workspace)
        adjusted = adjust_thresholds(history, ps)
        assert adjusted == {}

    def test_adjust_thresholds_needs_min_three_records(
        self, tmp_workspace: Workspace,
    ) -> None:
        # Only 2 records → no adjustment
        for i in range(2):
            record_feedback(
                tmp_workspace,
                candidate_id=f"cand_{i}",
                candidate_type="SES->LNG",
                sigil_pattern="SES:foo_*",
                decision=True,
                promotion_score=13,
            )
        ps = parse_policy_document(parse_cortex(default_policy_text()))
        history = load_feedback_history(tmp_workspace)
        adjusted = adjust_thresholds(history, ps)
        # With <3 records, no adjustment
        assert adjusted == {}


# ---------------------------------------------------------------------------
# Integration — full v0.2.0 session lifecycle
# ---------------------------------------------------------------------------


class TestFullSessionLifecycle:
    """End-to-end: start → pre-action → post-action → feedback → close."""

    def test_full_session_with_feedback(self, spec_workspace: Workspace) -> None:
        # Build index
        rebuild_for_workspace(spec_workspace)
        # Start session
        state = session_start(spec_workspace, input_text="full lifecycle test")
        assert state.status == "running"
        # Pre-action
        pre = pre_action(spec_workspace, "Revisemos los benchmarks otra vez")
        assert len(pre.themes_detected) > 0
        # Post-action
        post = post_action(spec_workspace, brain_modified=False)
        assert len(post.candidates_above_threshold) >= 1
        # Feedback on the first candidate
        first_sel = post.candidates_above_threshold[0]["selector"]
        record_feedback(
            spec_workspace,
            candidate_id=first_sel,
            candidate_type="SES->LNG",
            sigil_pattern=derive_sigil_pattern("SES", first_sel.split(":", 1)[1]),
            decision=True,
            promotion_score=post.candidates_above_threshold[0]["promotion_score"],
        )
        # Close session
        result = session_close(
            spec_workspace,
            input_text="test input",
            output_text="test output",
            outcome_text="test outcome",
            run_decay=False,  # skip decay to keep entries intact for assertion
        )
        assert result["closed"] is True
        # Feedback history should have 1 record
        history = load_feedback_history(spec_workspace)
        assert len(history.records) == 1


# ---------------------------------------------------------------------------
# Integration — CLI commands
# ---------------------------------------------------------------------------


class TestV02CLI:
    """Run the v0.2.0 CLI commands through subprocess."""

    def _run(self, *args, cwd=None):
        import subprocess
        import shutil
        env = dict(os.environ)
        env["PYTHONPATH"] = str(SRC)
        cortex_bin = shutil.which("cortex")
        if cortex_bin:
            cmd = [cortex_bin] + list(args)
        else:
            cmd = [sys.executable, "-m", "cortex.cli.main_e3"] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd)

    def test_session_start_status_close(self, tmp_path: Path) -> None:
        self._run("learn", "init", "--workspace", str(tmp_path))
        r = self._run("session", "start", "--workspace", str(tmp_path), "--json")
        assert r.returncode == 0, r.stderr
        d = json.loads(r.stdout)
        assert d["started"] is True
        r = self._run("session", "status", "--workspace", str(tmp_path), "--json")
        d = json.loads(r.stdout)
        assert d["active"] is True
        r = self._run(
            "session", "close", "--workspace", str(tmp_path), "--json",
        )
        assert r.returncode == 0, r.stderr
        d = json.loads(r.stdout)
        assert d["closed"] is True

    def test_policy_profile_aggressive(self, tmp_path: Path) -> None:
        self._run("learn", "init", "--workspace", str(tmp_path))
        r = self._run(
            "learn", "policy", "profile", "aggressive",
            "--workspace", str(tmp_path), "--confirm", "--json",
        )
        assert r.returncode == 0, r.stderr
        # Verify the policy file was updated
        text = (tmp_path / ".cortex" / "learn-policies.cortex").read_text()
        assert "lng:2" in text
        assert "half_life_days:3" in text

    def test_policy_set_cooling(self, tmp_path: Path) -> None:
        self._run("learn", "init", "--workspace", str(tmp_path))
        r = self._run(
            "learn", "policy", "set", "cooling",
            "--half-life", "14",
            "--workspace", str(tmp_path), "--confirm", "--json",
        )
        assert r.returncode == 0, r.stderr
        text = (tmp_path / ".cortex" / "learn-policies.cortex").read_text()
        assert "half_life_days:14" in text

    def test_policy_reset(self, tmp_path: Path) -> None:
        self._run("learn", "init", "--workspace", str(tmp_path))
        # First apply aggressive
        self._run("learn", "policy", "profile", "aggressive",
                  "--workspace", str(tmp_path), "--confirm")
        # Then reset
        r = self._run(
            "learn", "policy", "reset",
            "--workspace", str(tmp_path), "--confirm", "--json",
        )
        assert r.returncode == 0, r.stderr
        text = (tmp_path / ".cortex" / "learn-policies.cortex").read_text()
        assert "lng:3" in text  # default
        assert "half_life_days:7" in text  # default

    def test_pre_post_action_cli(self, spec_workspace: Workspace) -> None:
        ws = spec_workspace
        self._run("learn", "index", "rebuild", "--workspace", str(ws.root))
        r = self._run(
            "learn", "pre-action", "--input", "benchmarks benchmarks benchmarks",
            "--workspace", str(ws.root), "--json",
        )
        assert r.returncode == 0, r.stderr
        d = json.loads(r.stdout)
        assert "benchmarks" in d["themes_detected"]
        r = self._run(
            "learn", "post-action", "--workspace", str(ws.root), "--json",
        )
        d = json.loads(r.stdout)
        assert len(d["candidates_above_threshold"]) >= 1

    def test_feedback_cli_accept(self, spec_workspace: Workspace) -> None:
        ws = spec_workspace
        self._run("learn", "index", "rebuild", "--workspace", str(ws.root))
        r = self._run(
            "learn", "feedback", "--accept", "--candidate", "cand_001",
            "--workspace", str(ws.root), "--json",
        )
        assert r.returncode == 0, r.stderr
        d = json.loads(r.stdout)
        assert d["recorded"] is True
        assert d["decision"] == "accept"
        assert d["candidate_type"] == "SES->LNG"

    def test_feedback_show_cli(self, spec_workspace: Workspace) -> None:
        ws = spec_workspace
        self._run("learn", "index", "rebuild", "--workspace", str(ws.root))
        self._run("learn", "feedback", "--accept", "--candidate", "cand_001",
                  "--workspace", str(ws.root), "--json")
        r = self._run(
            "learn", "feedback-show", "--workspace", str(ws.root), "--json",
        )
        d = json.loads(r.stdout)
        assert d["total_records"] >= 1
        assert "SES->LNG" in d["acceptance_stats"]


# ---------------------------------------------------------------------------
# Forbidden-pattern scans (still hold for v0.2.0)
# ---------------------------------------------------------------------------


class TestV02ForbiddenPatterns:
    """v0.2.0 modules must still pass the forbidden-pattern checks."""

    def test_no_llm_or_network_imports(self) -> None:
        import cortex.learning
        learn_dir = Path(cortex.learning.__file__).parent
        bad = ["openai", "anthropic", "requests", "httpx", "urllib"]
        for py in learn_dir.rglob("*.py"):
            text = py.read_text(encoding="utf-8")
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if stripped.startswith("import ") or stripped.startswith("from "):
                    for token in bad:
                        assert token not in stripped, \
                            f"forbidden import in {py.name}: {stripped}"

    def test_no_eval_or_exec_calls(self) -> None:
        import cortex.learning
        learn_dir = Path(cortex.learning.__file__).parent
        for py in learn_dir.rglob("*.py"):
            text = py.read_text(encoding="utf-8")
            for i, line in enumerate(text.splitlines(), 1):
                code = line.split("#", 1)[0]
                assert "eval(" not in code, f"{py.name}:{i}: eval( in {line!r}"
                assert "exec(" not in code, f"{py.name}:{i}: exec( in {line!r}"

    def test_engine_version_is_v02(self) -> None:
        assert ENGINE_VERSION == "0.2.0"


# ---------------------------------------------------------------------------
# Backwards compatibility — v0.1.0 features still work
# ---------------------------------------------------------------------------


class TestBackwardsCompat:
    """v0.1.0 features must still work after the v0.2.0 upgrade."""

    def test_v01_spec_brain_still_produces_cand_001_score_13(
        self, spec_workspace: Workspace,
    ) -> None:
        """SPEC §17 expected output: cand_001 promotion_score=13."""
        idx = rebuild_for_workspace(spec_workspace)
        brain_doc = spec_workspace.parse_brain()
        ps = parse_policy_document(spec_workspace.parse_policy())
        cands = detect_candidates(brain_doc, idx, ps)
        ses_cands = [c for c in cands if c.target == "LNG"]
        assert len(ses_cands) >= 1
        assert ses_cands[0].promotion_score == 13

    def test_index_preserves_last_accessed_across_rebuild(
        self, spec_workspace: Workspace,
    ) -> None:
        """v0.2.0: rebuild should preserve last_accessed timestamps."""
        idx1 = rebuild_for_workspace(spec_workspace)
        # Stash a custom timestamp
        custom_ts = "2026-06-15T00:00:00Z"
        for k, rec in idx1.entries.items():
            if k.startswith("SES:"):
                rec.last_accessed = custom_ts
        from cortex.learning.index import save_index
        save_index(idx1, spec_workspace.index_path)
        # Rebuild — should preserve the timestamps
        idx2 = rebuild_for_workspace(spec_workspace)
        for k, rec in idx2.entries.items():
            if k.startswith("SES:"):
                assert rec.last_accessed == custom_ts, \
                    f"last_accessed not preserved for {k}"
