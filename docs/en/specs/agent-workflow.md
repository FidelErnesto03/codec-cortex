<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MPL-2.0 -->

# CODEC-CORTEX — Agent Workflow (v0.3.7)

> Operational workflow specification for agents loading the `codec-cortex` skill. Complements the canonical `SKILL.md` with concrete procedural instructions: how to start, how to operate per interaction, how to validate before commit, how to migrate artifacts to VIEW directives, and how to select the CORTEX-OUT profile.

---

## 1. Startup workflow (on skill load)

```
On loading codec-cortex:
  1. Verify canon:   cortex verify --strict skill/cortex/SKILL.md
  2. Validate VIEW:  cortex verify-view skill/cortex/SKILL.md
  3. Validate roundtrip: cortex roundtrip-bidir skill/cortex/SKILL.md
  4. Load brain:     read brain.cortex → extract FCS + OBJ + STP
  5. Activate CORTEX-OUT: profile OUT-AUDIT for agent responses
```

If any of steps 1–3 fails, the agent EMITS a `WARNING` describing the problem but continues operating. Verification failures do NOT block skill loading — they are only reported.

---

## 2. Daily operation workflow

```
Per user interaction:
  1. Verify active FCS/OBJ (from brain.cortex or native memory)
  2. Apply CNST:blocking before executing
  3. Respond in CORTEX-OUT (profile per criticality)
  4. On significant task closure:
     a. Update WRK if recoverable progress exists
     b. Register SES with input→output→outcome
     c. Extract LNG if error or pattern occurred
     d. Update AUD if something was verified
     e. cortex verify --strict brain.cortex before commit
```

---

## 3. Validation workflow (pre-commit / pre-push)

```
Before any commit that touches .cortex:
  1. cortex verify --strict <file>
  2. cortex verify-view <file>        (if it has VIEW)
  3. cortex roundtrip-bidir <file>    (if it has VIEW)
  4. cortex doctor --scan-secrets     (E2: secret scan)
  5. git diff --check

Before any tag:
  1. make all  (lint + test + verify + roundtrip)
  2. cortex roundtrip-bidir skill/cortex/SKILL.md
  3. cortex roundtrip-bidir skill/hcortex/SKILL.md
  4. cortex verify --signature skill/cortex/SKILL.md  (E2)
  5. cortex docstring --all                             (E3)
  6. cortex benchmark --list                            (E3)
  7. grep -r "0\\.3\\.[0-4]" docs/ or exit 1            (no stale versions)
```

---

## 4. VIEW migration workflow (for corpus)

When adding VIEW directives to existing `.cortex` files (corpus migration):

```
For each file:
  1. cortex inspect <file>        → identify eligible entries
  2. Add $N: VIEWS section        → one VIEW directive per table/sigil
  3. cortex verify-view <file>    → coverage must be 100%
  4. cortex roundtrip-bidir <file>→ must be byte-identical
```

---

## 5. `!` rules

| Rule | Scope | Description |
|------|:-----:|-------------|
| `!:type_strict` | `always` | attrs MUST use key/value pairs; attrs-pos MUST follow exact positional order from $0 contract; DIAG MUST be preserved bit-by-bit; parser MUST NOT infer types by heuristic if $0 defines them. |
| `!:section_normalize` | `startup` | Parser SHOULD accept `2`, `$2`, `$2:CONTEXT`, `#--$2:CONTEXT--` and normalize internally to `$2`. |
| `!:id_format` | `always` | Instances in snake_case (FCS:primary, RSK:premature_claim); sigils in UPPERCASE except `!` and registered operators in $0. |
| `!:micro_delimit` | `always` | Micro-tokens expand only if delimited by space, `|`, `,`, `{}`, newline, value start/end. MUST NOT expand inside words. |
| `!:extend_glossary` | `always` | New sigil → register in $0 before first use; new micro-token → register in $0 before first use; existing sigils → DO NOT redefine silently; unknown sigil → treat as untrustworthy until registered/confirmed. |
| `!:hcortex_expand` | `always` | attrs → table; cuerpo → indented block; bloque → verbatim. Type resolved from $0, not by heuristic. |
| `!:hcortex_source` | `always` | P0/P1 attrs → source column with SIGIL:name; PUML → 'source:DIAG:name' as first comment; cuerpo → source:SIGIL:name line under block; missing source in P0/P1 → WARNING:missing source. |
| `!:hcortex_multi` | `always` | Multiple instances of the same sigil → sub-sections `### SIGIL:name`, preserve source order. |
| `!:hcortex_order` | `always` | Order sections P0→P5; no P-level → after P5; same P-level → source order. Never truncate by position → eliminate by cognitive value. |
| `!:canonical_names` | `always` | Use canonical names for CLI commands and resources. Do not use version prefixes (v2-, v3-) in public names. Deprecated aliases exist for compatibility but are not documented as primary names. |
| `!:startup_verify` | `startup` | On skill load, run `cortex verify --strict skill/cortex/SKILL.md`. If it fails, warn but continue. |
| `!:precommit_verify` | `precommit` | Before committing changes to a `.cortex` file, run `cortex verify --strict <file>`. |
| `!:output_cortex_out` | `always` | Agent responses must use CORTEX-OUT profile appropriate to criticality. See [`cortex-out.md`](cortex-out.md). |
| `!:mutation_mode` | `always` | Respect `--mode read-only|editor|admin` and `$CORTEX_MODE` env (E2). |
| `!:docs_source_of_truth` | `always` | CLI help and docstrings derive from `docs/cortex/api/*.cortex`. Do not edit generated views directly (E3). |
| `!:secret_scan` | `precommit` | Run `cortex doctor --scan-secrets` before committing (E2). |
| `!:out_independence` | `always` | CORTEX-OUT MUST remain outside the .cortex→AST→HCORTEX pipeline. |
| `!:out_density` | `always` | SHOULD eliminate filler, unnecessary recap, and decorative closing. |
| `!:out_action` | `always` | SHOULD prioritize result, criterion, risk and action. |
| `!:out_honesty` | `always` | MUST NOT save tokens by hiding uncertainty or relevant limits. |
| `!:out_adaptive` | `always` | SHOULD adjust length per intent, criticality and evidence need. |
| `!:out_no_parse` | `always` | MUST NOT be treated as .cortex; MUST NOT create sigils, alter $0, or require parse contracts. |

> **Note:** Rules prefixed `!:out_*` belong to the CORTEX-OUT protocol. See [`cortex-out.md`](cortex-out.md) for the full specification.

---

## 6. CORTEX-OUT profiles

| Profile | When | Format |
|---------|:----:|--------|
| OUT-MIN | Minimal context (budget <500t) | Essential FCS/OBJ only, table |
| OUT-WORK | Operational response | Tables + K/V + bullet list |
| OUT-AUDIT | Verification or audit | Traceable, source column included |
| OUT-FULL | Full session report | All sigils, expanded, PUML included |
| OUT-ERROR | Error or warning | Error code + cause + recovery path |

> **Full protocol:** See [`cortex-out.md`](cortex-out.md) for the complete CORTEX-OUT specification including axioms, canonical blocks, constraints, and independence rules.

---

## 7. HDL operational handlers

The canonical SKILL.md defines 6 operational handlers that govern agent behavior at specific lifecycle points:

| Handler | Status | Requires | Description |
|---------|:------:|----------|-------------|
| `agent_init` | specification | SKILL.md, brain.cortex | Read SKILL.md (CORTEX or HCORTEX); identify Level 1 rules; read brain.cortex if exists. If FCS and OBJ explicit → use active state; if not → derive provisional FCS/OBJ from current instructions, keep in transient native memory. Apply CNST, select CORTEX profile, act or respond. |
| `pre_action` | specification | brain.cortex or anchors | Verify active/provisional FCS; verify active/provisional OBJ; verify active CNST:blocking; verify relevant LIM; verify maturity claims; verify active RSK; verify STP if applicable. If user contradicts CNST:blocking → halt or explain incompatibility. |
| `absorb_pkg` | specification | package.cortex, brain.cortex | Receive package.cortex; validate $0 or glossary inheritance; identify purpose, source, scope. If it contains live state → mark warning, do not absorb WRK/FCS/OBJ as live without confirmation. Classify entries by cortex; resolve conflicts with brain.cortex; integrate useful KNW/REF/DIAG/CLAIM/LIM; register AUD of absorption. |
| `session_close` | specification | brain.cortex | Produce/update SES with input, output, outcome, date. Produce LNG if error or relevant pattern. Produce AUD if something was verified. Produce RSK if risk remains active. Produce NXT if pending action remains. Produce HCORTEX closure if human needs audit. |
| `hcortex_render` | specification | .cortex or AST, active profile | 10-step render: 1) resolve profile (explicit > budget > mode > CORTEX-WORK); 2) declare `Perfil: CORTEX-LEVEL` as first line; 3) filter by P-level/survive (no P-level → P5), by entry not by section; 4) resolve type from $0 (attrs→table, cuerpo→indented block, bloque→verbatim); 5) render filtered entries applying type strategy; 6) if audit with insufficient budget → `Perfil: CORTEX-FULL (segmented) Segmento: n/total`, never degrade silently; 7) add source to P0/P1 tables, PUML `source:DIAG:name` as first comment, missing → WARNING:missing source; 8) multiple same-sigil instances → sub-sections `### SIGIL:name`, preserve source order; 9) apply per-type strategy; 10) order P0→P5, no P-level → after P5, same level → source order. |
| `recovery_missing_0` | specification | .cortex without $0 | Do not execute operational decisions based on that file; read only in recovery mode. Identify apparent sigils; reconstruct minimal local $0; mark ambiguities as RSK or AUD; request human confirmation if semantic risk; re-emit repaired file with local $0 before using as reliable memory. |

---

## 8. Workflow diagrams (PUML)

See the Spanish version for the complete PUML diagrams:

> **See:** [`docs/es/specs/flujo-agente.md`](../es/specs/flujo-agente.md) — Spanish version with complete PUML diagrams for startup, daily operation, pre-commit validation, VIEW migration, and CORTEX-OUT selection.
