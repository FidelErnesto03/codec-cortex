---
view: reference
reversible: true
profile: HCORTEX-REF
source: skill/cortex/SKILL.md §0, docs/cortex/api/*
mode: AUDIT
---

# HCORTEX Reference

> **source:** skill/cortex/SKILL.md §0:canonical_sigils · docs/cortex/api/*

Quick lookup for sigils, CLI commands, profiles, error codes, and conventions.

---

## Sigils

| Sigil | Type | Risk | Cortex | Description | source |
|:-----:|:----:|:----:|:------:|-------------|--------|
| IDN | attrs | B | Semantic | Project/artifact identity | `$0:IDN:identity` |
| DOM | attrs | B | Semantic | Domain, scope, adoption context | `$0:DOM:domain` |
| KNW | attrs | B | Semantic | Base or promoted knowledge | `$0:KNW:knowledge` |
| REF | attrs | B | Semantic | File/repo/document reference | `$0:REF:reference` |
| TAG | attrs | B | Semantic | Classification metadata | `$0:TAG:tag` |
| ! | attrs | H | Prefrontal | Compact operational rule | `$0:!:rule` |
| AXM | cuerpo | H | Prefrontal | Non-negotiable principle | `$0:AXM:axiom` |
| CNST | attrs | H | Prefrontal | Hard constraint or limit | `$0:CNST:constraint` |
| CLAIM | attrs | M | Prefrontal | Verifiable claim with evidence | `$0:CLAIM:claim` |
| LIM | attrs | M | Prefrontal | Explicit usage or maturity limit | `$0:LIM:limit` |
| AUD | attrs | M | Prefrontal | Verification/audit record | `$0:AUD:audit` |
| RSK | attrs | M | Prefrontal | Identified risk with mitigation | `$0:RSK:risk` |
| FCS | attrs | H | Working | Active attention anchor | `$0:FCS:focus` |
| OBJ | attrs | H | Working | Active goal with success criterion | `$0:OBJ:objective` |
| WRK | attrs | B | Working | Current execution state | `$0:WRK:work` |
| STP | attrs | M | Working | Next immediate action | `$0:STP:step` |
| NXT | attrs | M | Working | Queued action with trigger | `$0:NXT:next` |
| SES | attrs | M | Episodic | Compressed I/O/R episode | `$0:SES:session` |
| LNG | attrs | M | Episodic | Learned lesson or pattern | `$0:LNG:lesson` |
| DIAG | bloque | M | Episodic/Visual | PlantUML or verbatim visual block | `$0:DIAG:diagram` |
| HDL | attrs-pos | M | Semantic | Operation descriptor or interface contract | `$0:HDL:handler` |
| PFL | attrs | M | Prefrontal | Known antipattern and prevention | `$0:PFL:pitfall` |
| DEP | attrs | M | Semantic | Artifact/module dependency | `$0:DEP:dependency` |
| DESC | cuerpo | B | Semantic | Structured textual description | `$0:DESC:description` |
| ERR | attrs | M | Prefrontal | Known error with cause and solution | `$0:ERR:error` |

---

## CLI commands

| Command | Since | Description | source |
|---------|:-----:|-------------|--------|
| `cortex --version` | 0.3.0 | Show version | `docs/cortex/api/canonicalize.cortex` |
| `cortex new` | 0.3.0 | Create new `.cortex` from template | `docs/cortex/api/canonicalize.cortex` |
| `cortex inspect` | 0.3.2 | Show sections, entries, VIEW, coverage | `docs/cortex/api/canonicalize.cortex` |
| `cortex verify` | 0.3.0 | Validate structure and optional roundtrip | `docs/cortex/api/verify.cortex` |
| `cortex verify-view` | 0.3.2 | VIEW coverage and reversibility | `docs/cortex/api/verify.cortex` |
| `cortex verify --signature` | 0.3.4 | Integrity verification | `docs/cortex/api/verify.cortex` |
| `cortex roundtrip` | 0.3.2 | Byte-identical roundtrip | `docs/cortex/api/convert.cortex` |
| `cortex roundtrip-bidir` | 0.3.2 | Bidirectional CORTEX⇄HCORTEX | `docs/cortex/api/convert.cortex` |
| `cortex convert` | 0.3.2 | Convert between CORTEX and HCORTEX | `docs/cortex/api/convert.cortex` |
| `cortex compare` | 0.3.2 | Structural comparison | `docs/cortex/api/convert.cortex` |
| `cortex canonicalize` | 0.3.2 | Normalize `.cortex` structure | `docs/cortex/api/canonicalize.cortex` |
| `cortex explain-loss` | 0.3.2 | Report loss/non-reversibility | `docs/cortex/api/convert.cortex` |
| `cortex add` | 0.3.0 | Add entry to `.cortex` | `docs/cortex/api/canonicalize.cortex` |
| `cortex update` | 0.3.0 | Update existing entry | `docs/cortex/api/canonicalize.cortex` |
| `cortex delete` | 0.3.0 | Remove entry | `docs/cortex/api/canonicalize.cortex` |
| `cortex move` | 0.3.0 | Move entry between sections | `docs/cortex/api/canonicalize.cortex` |
| `cortex doctor` | 0.3.0 | Deep diagnostics | `docs/cortex/api/doctor.cortex` |
| `cortex doctor --scan-secrets` | 0.3.4 | Secret pattern scan | `docs/cortex/api/doctor.cortex` |
| `cortex audit` | 0.3.4 | Audit log management | `docs/cortex/api/audit.cortex` |
| `cortex recover` | 0.3.0 | Recover legacy files | `docs/cortex/api/canonicalize.cortex` |
| `cortex docstring` | 0.3.5 | Generate docstrings from CORTEX API | `docs/cortex/api/docstring.cortex` |
| `cortex benchmark` | 0.3.5 | List and inspect benchmark suites | `docs/cortex/api/benchmark.cortex` |

---

## HCORTEX profiles

| Profile | Budget | P-levels | When | source |
|---------|:------:|:--------:|------|--------|
| CORTEX-MIN | ~300t | P0 | Emergency, single directive | `$9:KNW:profile_min` |
| CORTEX-RECOVERY | ~1Kt | P0-P2 | Resuming from compressed SES | `$9:KNW:profile_recovery` |
| CORTEX-WORK | ~4Kt | P0-P3 | Daily operation | `$9:KNW:profile_work` |
| CORTEX-FULL | ~8Kt | P0-P5 | Audit, review, full session | `$9:KNW:profile_full` |

---

## HCORTEX render modes

| Mode | Source visible | For | source |
|------|:--------------:|-----|--------|
| READABLE | No | Clean executive reading | `$11:KNW:hc_modes` |
| AUDIT | Yes | Traceability and debugging | `$11:KNW:hc_modes` |
| RECOVERY | No (only P0-P2) | Reconnection after context loss | `$11:KNW:hc_modes` |
| FULL | Yes | Full export and exit gate | `$11:KNW:hc_modes` |

---

## CORTEX-OUT profiles

| Profile | Blocks | When | source |
|---------|--------|------|--------|
| OUT-MIN | Result + Action | Budget <500t | `$12:KNW:out_blocks` |
| OUT-WORK | Result + Criterion + Action + Limit | Operational response | `$12:KNW:out_blocks` |
| OUT-AUDIT | All blocks with traceability | Verification or audit | `$12:KNW:out_blocks` |
| OUT-FULL | All blocks expanded | Full session report | `$12:KNW:out_blocks` |
| OUT-ERROR | Error code + cause + recovery | Error or warning | `$12:KNW:out_blocks` |

---

## Error codes

| Code | Severity | Description | source |
|:----:|:--------:|-------------|--------|
| E003 | Error | Unknown sigil (not declared in $0) | `!:extend_glossary` |
| E023 | Error | Level 1 live state violation | `$5:CNST:sep_l1` |
| E024 | Error | Level 2 missing focus | `$5:CNST:sep_l2` |
| E031 | Error | Secret in clear (non-bypassable) | `!:secret_scan` |
| E032 | Error | Critical sigil incomplete | `$7:CNST:contract_*` |
| E034 | Error | Critical field empty | `$7:CNST:contract_*` |
| E_VIEW_* | Error | VIEW directive violation | `$13:VIEW:*` |
| W_VIEW_* | Warning | VIEW coverage or target issue | `$13:VIEW:*` |
| W_HCORTEX_DISPLAY_ONLY | Warning | HCORTEX not reversible | `$11:KNW:hc_modes` |

---

## Microtokens

| Token | Expansion | source | Token | Expansion | source |
|:-----:|:---------|--------|:-----:|:---------|--------|
| cur | current | `$0:micro_cur` | min | minimum | `$0:micro_min` |
| pln | planned | `$0:micro_pln` | rec | recovery | `$0:micro_rec` |
| fut | future | `$0:micro_fut` | wrk | work | `$0:micro_wrk` |
| blk | blocked | `$0:micro_blk` | full | full | `$0:micro_full` |
| ok | success | `$0:micro_ok` | fail | failure | `$0:micro_fail` |
| d1 | decode | `$0:micro_d1` | d2 | detect | `$0:micro_d2` |
| d3 | decay | `$0:micro_d3` | c1 | .cortex | `$0:micro_c1` |
| c2 | HCORTEX | `$0:micro_c2` | v1 | validate | `$0:micro_v1` |
| v2 | verify | `$0:micro_v2` | p1 | promote | `$0:micro_p1` |

> **Full reference:** See `docs/en/specs/microtokens.md` for all 30+ microtokens.

---

## Conventions

| Convention | Rule | source |
|------------|------|--------|
| Sigil names | UPPERCASE (FCS, OBJ, KNW), except `!` | `!:id_format` |
| Instance names | snake_case (FCS:primary, RSK:premature_claim) | `!:id_format` |
| File extension | `.cortex` for CORTEX, `.md` for HCORTEX | `$11:DESC:hcortex_def` |
| Glossary first | `$0` must be the first section | `!section_normalize` |
| Source of truth | CORTEX files in `docs/cortex/api/` | `!:docs_source_of_truth` |
| Canonical names | No version prefixes | `!:canonical_names` |

---

## Source hierarchy

| Source | Location | Format | Verifiable | source |
|--------|----------|:------:|:----------:|--------|
| Protocol spec | `skill/cortex/SKILL.md` | CORTEX | ✅ | `$1:REF:art_skill_cortex` |
| Human view | `skill/hcortex/SKILL.md` | HCORTEX | ✅ | `$1:REF:art_skill_hcortex` |
| CLI API | `docs/cortex/api/*.cortex` | CORTEX | ✅ | `docs/cortex/api/README.md` |
| Tutorials | `docs/en/hcortex/tutorials/` | HCORTEX (disp) | ❌ | This file |
| How-to | `docs/en/hcortex/how-to/` | HCORTEX (disp) | ❌ | This file |
| Explanations | `docs/en/hcortex/explanations/` | HCORTEX (disp) | ❌ | This file |
| Reference | This file | HCORTEX (ref) | ✅ | This file |
