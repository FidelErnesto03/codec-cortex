# CODEC-CORTEX v0.6.0 — Certification Plan

## Executive Summary

**Base Version:** v0.5.2 (commit `97c5f23ec9f297ddfbfff77c7fe684fc04e5b398`)  
**Target Version:** v0.6.0 — Compatibility & Codec Hardening  
**License:** MPL-2.0 (prospectively; MIT rights preserved for v0.3.7 artifacts)  
**Status:** Development → Release Candidate  

---

## 1. Completed Actions (R0-R1)

### R0 — Source Freezing & Baseline

✅ **PyPI 0.3.7 baseline captured**
- Location: `certification/baselines/0.3.7/`
- Artifact: `codec_cortex-0.3.7-py3-none-any.whl`
- SHA-256: `b336464ad3b3279b69ce5fce0cc85dc0d0263a11d5cb5f452eea0d4b76cfd764`
- Manifest: 100 files (93 `.py` + resources)
- Learning modules confirmed: 11 files in `cortex/learning/`

### R1 — Unified Distribution

✅ **Single `pyproject.toml` consolidated**
- Build system: `setuptools` + `setuptools-scm`
- Package root: `cli/src/cortex`
- All subpackages included explicitly:
  - `cortex`, `cortex.audit`, `cortex.cli`, `cortex.cli.commands`
  - `cortex.core`, `cortex.crud`, `cortex.glossary`, `cortex.hcortex`
  - `cortex.learning`, `cortex.security`, `cortex.templates`, `cortex.v2`
- Python support: `>=3.9` (added 3.13 classifier)
- Entry point: `cortex = "cortex.cli.main_e3:main"`
- CLI `pyproject.toml` removed (integrated into root)

✅ **Installation verified**
- `cortex --version` returns tag-based version
- All imports functional including `cortex.learning`
- 539 tests passing (4 skipped)

---

## 2. Critical Findings Status

### BLOCKER Issues (10 total)

| ID | Issue | Status | Resolution Plan |
|----|-------|--------|-----------------|
| P0-001 | Release identity | ⚠️ Partial | setuptools-scm provides version; STATUS.md needs sync |
| P0-002 | Packaging | ✅ Fixed | Single pyproject.toml with explicit packages |
| P0-003 | Writer compatibility | 🔴 Open | Multiline collapse in `cuerpo`, `relación`, non-DIAG `bloque` |
| P0-004 | Core/v2 downcast | 🔴 Open | Commands convert v2→v1 text then reparse |
| P0-005 | Learning elevation | 🔴 Open | `apply_patch` lacks CAS, backup, strict validation |
| P0-006 | Session runtime | 🔴 Open | Writes `SES:current` to brain; no CAS on close |
| P0-007 | Feedback governance | 🔴 Open | `feedback.json` changes thresholds outside policy |
| P0-008 | Certification CI | 🔴 Open | Non-blocking gates; wheel-only build |
| P0-009 | Legal provenance | ⚠️ Partial | MPL-2.0 set; historical audit pending |
| P0-010 | Backward compatibility | 🔴 Open | No differential test suite vs 0.3.7 |

### HIGH Issues (11 total)

All require resolution before RC:
- P1-011: Auto-repair fabricates values
- P1-012: Schema allows local override of canonical required fields
- P1-013: Parser auto-registers unknown sigils (vs 0.3.7 E003)
- P1-014: Workspace adoption not explicit
- P1-015: Detection policies not implemented
- P1-016: Decay inconsistent (read_priority not recalculated)
- P1-017: Candidate ID unstable (sequential vs hash-based)
- P1-018: CLI/API inconsistency
- P1-019: Skill/docs contradictions
- P1-020: Duplicate entries allowed across sections
- P1-021: Direct writes bypass TransactionService

---

## 3. Test Execution Results

### Current Suite (v0.5.2)

```
============================= test session starts ==============================
collected 543 items

cli/src/tests/test_acceptance.py ...............                         [  2%]
cli/src/tests/test_audit_gates.py ...........................            [  7%]
cli/src/tests/test_crud.py ............................                  [ 14%]
cli/src/tests/test_learning_engine.py .................................. [ 40%]
cli/src/tests/test_learning_engine_v02.py .............................. [ 48%]
cli/src/tests/test_v2_roundtrip.py ...........                           [100%]

================== 539 passed, 4 skipped in 66.75s ===================
```

### Proposed Additional Tests

#### 3.1 Compatibility Tests (`tests/compatibility/`)

```python
# test_037_compatibility.py
class TestPyPI037Compatibility:
    """Verify v0.6.0 maintains compatibility with 0.3.7 oracle."""
    
    def test_read_valid_037_files(self):
        """All files valid under 0.3.7 must be readable."""
        pass
    
    def test_verify_strict_unknown_sigil(self):
        """Unknown sigil must fail with E003 in strict mode."""
        pass
    
    def test_multiline_preservation(self):
        """Multiline cuerpo/bloque/relación preserved by default."""
        pass
    
    def test_cli_exit_codes_golden(self):
        """Exit codes match 0.3.7 for equivalent operations."""
        pass
    
    def test_json_legacy_format(self):
        """--json flag preserves 0.3.7 output structure."""
        pass
```

#### 3.2 Property Tests (`tests/property/`)

```python
# test_parse_write_idempotence.py
class TestParseWriteIdempotence:
    """Parser and writer must be idempotent."""
    
    def test_canonical_form_stable(self):
        """write(parse(write(parse(file)))) == write(parse(file))."""
        pass
    
    def test_multiline_roundtrip(self):
        """DIAG blocks preserve exact bytes through roundtrip."""
        pass
    
    def test_glossary_deterministic(self):
        """Same glossary produces identical $0 section."""
        pass
```

#### 3.3 Transaction Tests (`tests/integration/`)

```python
# test_transaction_service.py
class TestTransactionService:
    """All mutations must use transaction service."""
    
    def test_cas_conflict_detection(self):
        """Expected hash mismatch raises E_CONFLICT."""
        pass
    
    def test_backup_created(self):
        """Backup file created before atomic replace."""
        pass
    
    def test_rollback_on_failure(self):
        """Failed write restores from backup."""
        pass
    
    def test_no_direct_writes(self):
        """No module writes brain.cortex without transaction."""
        pass
```

#### 3.4 Session Tests (`tests/integration/`)

```python
# test_session_runtime.py
class TestSessionRuntime:
    """Session management must be safe and transitory."""
    
    def test_no_brain_write_during_session(self):
        """Session events do not write to brain.cortex."""
        pass
    
    def test_consolidate_produces_patch(self):
        """Consolidate generates explicit patch file."""
        pass
    
    def test_close_requires_cas(self):
        """Close fails if brain changed since start."""
        pass
    
    def test_crash_recovery(self):
        """Interrupted session can be recovered or aborted."""
        pass
```

#### 3.5 Learning Engine Tests (`tests/property/`)

```python
# test_learning_determinism.py
class TestLearningDeterminism:
    """Learning engine must be deterministic."""
    
    def test_same_input_same_scores(self):
        """Identical input/policy/version => same scores."""
        pass
    
    def test_candidate_id_stable(self):
        """Candidate ID based on hash, not sequence."""
        pass
    
    def test_decay_recalculates_priority(self):
        """Decay updates read_priority and suggested_action."""
        pass
    
    def test_feedback_no_policy_side_effect(self):
        """Feedback cache deletion doesn't change policies."""
        pass
```

#### 3.6 Fuzz Tests (`tests/fuzz/`)

```python
# test_fuzz_parser.py
class TestFuzzParser:
    """Parser must handle malformed input gracefully."""
    
    def test_random_bytes_no_crash(self):
        """Random byte sequences don't cause unhandled exceptions."""
        pass
    
    def test_unicode_edge_cases(self):
        """Unicode edge cases handled correctly."""
        pass
    
    def test_extreme_lengths(self):
        """Very long lines/sections handled without crash."""
        pass
```

---

## 4. Roadmap to v0.6.0

### Phase 1: Codec Hardening (R2-R4)
- [ ] Implement verbatim multiline preservation (P0-003)
- [ ] Native Core/V2 document adapters (P0-004)
- [ ] Parser strictness with opt-in recovery (P1-013)
- [ ] Schema canonical field protection (P1-012)
- [ ] Property tests for parse/write idempotence

### Phase 2: Transaction & Safety (R5)
- [ ] TransactionService for all mutations (P0-005, P1-021)
- [ ] CAS, backup, rollback implementation
- [ ] Repair command with plan/apply separation (P1-011)
- [ ] Migration command with explain-loss

### Phase 3: Runtime & Learning (R6-R7)
- [ ] Session transitory state (P0-006)
- [ ] Feedback governance (P0-007)
- [ ] Detection policy implementation (P1-015)
- [ ] Stable candidate IDs (P1-017)
- [ ] Decay consistency (P1-016)

### Phase 4: CLI & Documentation (R8-R9)
- [ ] Unified CLI entry point (P1-018)
- [ ] JSON schema v2 envelope
- [ ] Skill.cortex canonical source (P1-019)
- [ ] Duplicate entry handling (P1-020)
- [ ] Bilingual documentation (ES/EN)

### Phase 5: Certification (R10-R11)
- [ ] Compatibility test suite vs 0.3.7 (P0-010)
- [ ] CI matrix: Linux/Windows/macOS × Python 3.9-3.13
- [ ] Wheel + sdist parity checks
- [ ] SBOM, attestations, reproducibility
- [ ] Release candidates and external audit

---

## 5. Definition of Done

v0.6.0 is certified when:

1. **All BLOCKER issues resolved** or formally accepted with mitigation
2. **All HIGH issues resolved**
3. **539 existing tests pass** plus new compatibility/property/integration tests
4. **Coverage ≥90%** overall, ≥95% for core/transactions/runtime/learning
5. **Compatibility gate passed**: 100% of 0.3.7 valid files readable with zero semantic loss
6. **Artifacts verified**: wheel + sdist installable, module parity confirmed
7. **Documentation complete**: bilingual README, STATUS, API reference
8. **Legal clear**: license provenance documented, NOTICE and SPDX present

---

## 6. Next Steps

1. **Address P0-003 (Writer compatibility)**: Modify `writer.py` to preserve multiline content by default
2. **Create compatibility test harness**: Dual-venv runner comparing 0.3.7 vs 0.6.0 behavior
3. **Implement TransactionService**: Unify all mutation paths
4. **Fix session runtime**: Move to `.cortex/runtime/session.cortex`
5. **Stabilize learning engine**: Deterministic IDs, proper decay, feedback governance

---

**Generated:** 2026-07-16  
**Auditor:** AI Code Assistant  
**Based on:** Comprehensive audit report from v0.5.2 tag
