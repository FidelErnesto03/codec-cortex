---
view: display-only
reversible: false
profile: HCORTEX-EXPLANATION
source: skill/cortex/SKILL.md §11, §12, §2, §8, §9
mode: READABLE
---

# E3 Documentation Protocol — Deep Explanation

> **source:** skill/cortex/SKILL.md §11:DESC:hcortex_def · §12:DESC:out_def · §8:!:survive_priority · §9:KNW:profile_*

This document explains the why behind the CODEC-CORTEX documentation architecture: why CORTEX and HCORTEX exist as separate formats, why the codec is deterministic (no LLM in the loop), how the truth chain works, and what makes this protocol different from conventional documentation.

---

## 1. Why two formats: CORTEX and HCORTEX

| Aspect | CORTEX | HCORTEX | source |
|--------|--------|---------|--------|
| Audience | Agents & CLI | Humans | `$11:DESC:hcortex_def` |
| Format | Dense structured | Markdown tables, lists, PUML | `$11:DESC:hcortex_def` |
| Source of truth | ✅ Yes | No (derived) | `!hcortex_expand` |
| Roundtrip capable | ✅ Yes | ✅ Yes (via VIEW) | `$13:VIEW:*` |
| Self-contained | ✅ Yes ($0 glossary) | No (references CORTEX) | `$11:DESC:hcortex_def` |
| Token cost | Minimal | Human-readable | `$2:AXM:canon` |

**The principle:** CORTEX is the canonical source. HCORTEX is a reversible human view of the same information. One source, two representations. This avoids the documentation duplication trap where Markdown docs and code comments drift apart.

**Why not just Markdown?**

| Limitation | Why it matters | source |
|------------|----------------|--------|
| No contract system | No required fields, no type validation | `$7:CNST:contract_*` |
| Non-deterministic parsing | Agents cannot parse reliably | `!type_strict` |
| No roundtrip | Cannot verify fidelity | `$13:VIEW:*` |
| No glossary/sigil system | No structured vocabulary | `$0:canonical_sigils` |

HCORTEX looks like Markdown but is governed by VIEW directives that make it structurally reversible back to CORTEX.

---

## 2. The truth chain

| Layer | Format | Verifiable | source |
|:-----:|:------:|:----------:|--------|
| Protocol spec (`skill/cortex/SKILL.md`) | CORTEX | ✅ | `$1:REF:*` |
| Command API (`docs/cortex/api/*.cortex`) | CORTEX | ✅ | `$1:REF:*` |
| HCORTEX reference | HCORTEX | ✅ (via VIEW) | `$11:KNW:hc_modes` |
| Tutorials / How-to / Explanations | HCORTEX (display) | ❌ (narrative) | `$11:KNW:hc_modes` |

**Rules of the chain:**

| Rule | Description | source |
|:----:|-------------|--------|
| 1 | Write once in CORTEX | `!:docs_source_of_truth` |
| 2 | Derive, never duplicate | `!hcortex_expand` |
| 3 | Validate the source, not the view | `!:type_strict` |
| 4 | Roundtrip proves fidelity | `$13:VIEW:*` |

---

## 3. Why no LLM in the codec loop

CODEC-CORTEX is a **deterministic structural compression protocol**. The codec operates without any LLM inference.

| Operation | Uses LLM? | Why | source |
|-----------|:---------:|-----|--------|
| Parse `.cortex` → AST | ❌ No | Deterministic lexer + parser | `!type_strict` |
| Encode AST → `.cortex` | ❌ No | Deterministic serializer | `!type_strict` |
| Verify structure | ❌ No | Rule-based validator | `!:precommit_verify` |
| Render HCORTEX | ❌ No | VIEW-driven template engine | `!hcortex_expand` |
| `cortex docstring` | ❌ No | Extracts structured fields | `docs/cortex/api/docstring.cortex` |
| CORTEX-OUT response | ✅ Yes | LLM produces the output | `$12:DESC:out_def` |

**Why this matters:**

| Property | Benefit | source |
|----------|---------|--------|
| Reproducibility | Same input → same result on any agent | `!type_strict` |
| Auditability | Prove validity without LLM | `!:precommit_verify` |
| Performance | 2,000-line file verifies in milliseconds | `$3:HDL:verify` |
| Security | Codec cannot hallucinate errors | `!type_strict` |

---

## 4. The maturation model (4 stages)

```
Novice → Advanced Beginner → Competent → Proficient
```

| Stage | Can produce | Can verify | Requires human | source |
|-------|-------------|:----------:|:--------------:|--------|
| **Novice** | Basic `.cortex` with FCS/OBJ | `verify --strict` | Sigil guidance | `$8:!:survive_priority` |
| **Advanced Beginner** | SES, LNG, WRK, STP | roundtrip-bidir | VIEW coverage | `$3:HDL:session_close` |
| **Competent** | Full brain with AUD, RSK, CLAIM | Full suite | KNW promotion | `$5:CNST:sep_l2` |
| **Proficient** | Autonomous memory mgmt | All gates | Semantic promotion | `$5:CNST:sep_l2` |

**Fibonacci thresholds:**

| Score | State | Action | source |
|:----:|-------|--------|--------|
| 1 | Observed | Keep transient or SES | `docs/en/specs/learning.md` |
| 3 | Pattern | Create LNG | `docs/en/specs/learning.md` |
| 5 | Candidate | Mark LNG as candidate | `docs/en/specs/learning.md` |
| 8 | Validatable | Request human confirmation | `docs/en/specs/learning.md` |
| 13 | Promotable | Promote to KNW | `docs/en/specs/learning.md` |
| 21 | Critical | Raise priority and register AUD | `docs/en/specs/learning.md` |

---

## 5. Survival Core: why P0-P5 exists

| Level | Budget | Preserves | Degrades when | source |
|:-----:|:------:|-----------|:-------------:|--------|
| P0 | ~300t | FCS, OBJ, CNST, STP | Never | `$8:!:survive_priority` |
| P1 | ~600t | WRK, AUD, RSK, NXT | Budget exhausted | `$8:!:survive_priority` |
| P2 | ~1Kt | CLAIM, LIM, KNW:active | Budget exhausted | `$8:!:survive_priority` |
| P3-P5 | 2Kt+ | SES, REF, DIAG, history | Budget exhausted | `$8:!:survive_priority` |

**Key insight:** Degradation is not deletion. When the context expands again, entries are reloaded in reverse order (P0 → P5).

---

## 6. CORTEX-OUT: why it is separate from HCORTEX

| | HCORTEX | CORTEX-OUT | source |
|---|---|---|---|
| Source | `.cortex` AST | Agent reasoning | `$11:DESC:hcortex_def` · `$12:DESC:out_def` |
| Pipeline | decode → render | LLM inference → format | `$12:DESC:out_def` |
| Roundtrip | ✅ Yes | ❌ Not applicable | `$12:!:out_independence` |
| VERIFY scope | ✅ Full validation | ❌ Not applicable | `$12:!:out_no_parse` |
| Output | Markdown tables + PUML | Natural language + blocks | `$12:KNW:out_blocks` |

**Why they must be separate:**

If you confuse them, you either force every agent response to be a roundtrippable `.cortex` (impractical) or lose the audit trail because responses are not verifiable.

The convention: **HCORTEX for memory audit, CORTEX-OUT for conversation.**

---

## 7. Controlled risks

| Risk | Control | source |
|------|---------|--------|
| API reference duplicated | Single source in `docs/cortex/api/` | `!:docs_source_of_truth` |
| Human adoption barrier | `docs/README.md` in standard Markdown | `docs/cortex/specs/documentation-protocol.cortex` |
| CLI help misaligned | `cortex docstring` derives from CORTEX | `docs/cortex/api/docstring.cortex` |
| Docs drift from implementation | `cortex verify --strict` on every `.cortex` | `!:precommit_verify` |
| LLM hallucination in verification | Deterministic codec | `!type_strict` |
