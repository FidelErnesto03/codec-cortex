<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MPL-2.0 -->

# CODEC-CORTEX — CORTEX-OUT Protocol

> **STATUS NOTE:** This document is specification. As of v0.3.7 CORTEX-OUT is the canonical output protocol for CODEC-CORTEX agent responses. HCORTEX-OUT may appear as a historical or descriptive design reference but MUST NOT be used as a canonical name — it induces confusion with HCORTEX. CORTEX-OUT does NOT participate in: decode, encode, verify, AST, $0, sigil contracts, roundtrip, or canonical persistence.

---

## 1. Definition

CORTEX-OUT is the conversational output protocol of CODEC-CORTEX.

| Aspect | CORTEX-OUT | HCORTEX |
|--------|-----------|---------|
| **Pipeline** | Agent reasoning → human-efficient response | .cortex/AST → human-auditable Markdown |
| **Canonical role** | Output protocol | Decompression protocol |
| **Participates in** | Agent response only | decode, encode, verify, roundtrip |
| **Sigils/contracts** | MUST NOT create or require | Full sigil contract system |

---

## 2. Guiding axiom

> Agent output must maximize cognitive utility per token without hiding uncertainty, risk, limits, critical evidence, or security constraints.

---

## 3. Rules

| Rule | Scope | Description |
|------|:-----:|-------------|
| `!:out_independence` | `always` | CORTEX-OUT MUST remain outside the .cortex→AST→HCORTEX pipeline. |
| `!:out_density` | `always` | SHOULD eliminate filler, unnecessary recap, and decorative closing. |
| `!:out_action` | `always` | SHOULD prioritize result, criterion, risk and action. |
| `!:out_honesty` | `always` | MUST NOT save tokens by hiding uncertainty or relevant limits. |
| `!:out_adaptive` | `always` | SHOULD adjust length per intent, criticality and evidence need. |
| `!:out_no_parse` | `always` | MUST NOT be treated as .cortex; MUST NOT create sigils, alter $0, or require parse contracts. |

---

## 4. Constraints

| Constraint | Severity | Rule |
|------------|:--------:|------|
| `CNST:out_naming` | warning | Canonical name: CORTEX-OUT. HCORTEX-OUT MUST NOT be used as canonical name. |

---

## 5. Canonical output blocks

CORTEX-OUT is composed of optional blocks. Only blocks that add value should be used; 1–2 blocks is correct if they resolve the task.

| Block | Content | When to use |
|-------|---------|-------------|
| **Resultado** | Direct answer / verdict | Always when there is a conclusion |
| **Criterio** | Technical judgment / reasoned decision | Design, analysis, review |
| **Evidencia** | Verifiable facts / citations / data | Audit, benchmark, critical review |
| **Riesgo** | Problems / inconsistencies / limits / impact | Critical decisions or uncertainty |
| **Acción** | Next step / instruction / recommendation | When operational continuity exists |
| **Límite** | What is not known / not done / not to be assumed | Uncertainty or lack of evidence |
| **Entrega** | Final artifact / code / text / table / document | OUT-FULL or reusable artifacts |
| **Control** | What was modified / what is pending / what to validate | Long-task closures |

---

## 6. CORTEX-OUT profiles

| Profile | When | Includes |
|---------|:----:|----------|
| **OUT-MIN** | Minimal context (budget <500t) | Essential Resultado + Acción |
| **OUT-WORK** | Operational response | Resultado + Criterio + Acción + Límite |
| **OUT-AUDIT** | Verification or audit | All blocks with traceability |
| **OUT-FULL** | Full session report | All blocks, expanded, evidence included |
| **OUT-ERROR** | Error or warning | Error code + cause + recovery path |

---

## 7. Relationship to HCORTEX

| | CORTEX-OUT | HCORTEX |
|---|---|---|
| Source | Agent reasoning | .cortex AST |
| Format | Natural language + structured blocks | Markdown tables + K/V + PUML |
| Goal | Efficient conversational response | Human audit and decompression |
| Roundtrip | Not applicable | Core capability |
| VERIFY scope | Not applicable | Full structural validation |

---

## 8. Knowledge

**Canonical name:** CORTEX-OUT
**Status:** current (v0.3.7)
**First introduced:** v0.3.2 (as output protocol concept)

> **See:** [`agent-workflow.md`](agent-workflow.md) §6 for output profile quick-reference.
> **See:** [`docs/es/specs/salida-agente.md`](../es/specs/salida-agente.md) for the Spanish version.
