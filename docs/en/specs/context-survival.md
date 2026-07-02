<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

<p align="center">
  <strong>CODEC-CORTEX</strong> — Context Survival Specification
  <br>
  <sub>SPECIFICATION · Survival Core · v0.3.7 · MIT · <a href="../../AUTHORS.md">Fidel Ernesto Lozada A.</a></sub>
</p>

---

> **STATUS NOTE:** This document is specification. As of v0.3.7 the concepts defined here (`survive` attribute, priority pack P0-P5, MIN/RECOVERY/WORK/FULL profiles, degradation policy, HCORTEX as render target) are implemented in the CLI (`cortex verify`, `cortex render`, `cortex canonicalize`, `cortex inspect`) and in the deterministic parser. The contextual efficiency metric remains conceptual: survival benchmark automation is planned but not blocking for current protocol usage.

**Abstract:** Single document consolidating the foundations of the CODEC-CORTEX Survival Core: `survive` attribute, priority pack P0-P5, conceptual load profiles, degradation policy, HCORTEX as render target, and contextual efficiency metric.

| | |
|---|---|
| **Author** | Fidel Ernesto Lozada A. — Systems Engineer / MSc. Management Sciences |
| **Repository** | github.com/FidelErnesto03/codec-cortex |
| **License** | MIT |

---

## 1. `survive` attribute

The `survive` attribute declares how much context an entry requires to remain operative. It is the fundamental unit of the survival core.

| Level | Label | Budget | Behavior |
|:-----:|-------|:------:|----------|
| 4 | `full` | _max_ | Preserved under all profiles |
| 3 | `work` | ~3Kt | Preserved under WORK and FULL |
| 2 | `recovery` | ~1.5Kt | Preserved under RECOVERY, WORK and FULL |
| 1 | `min` | ~500t | Only loaded under CORTEX-MIN |

---

## 2. Priority Pack P0-P5

When the context window shrinks, the agent preserves entries by cognitive priority, never by position. **Load order: P0→P5. Degradation order: P5→P1. P0 is never removed.**

| Level | Name | Budget | Preserves |
|:-----:|------|:-----:|-----------|
| **P0** | Minimum survival | ~300t | `FCS`, `OBJ`, `CNST`, `STP` |
| **P1** | Operational state | ~600t | `WRK`, `AUD`, `RSK`, `NXT` (when present) |
| **P2** | Honesty and limits | ~1Kt | `CLAIM`, `LIM`, `KNW:active`, `LNG:critical` (when present) |
| **P3** | Recent evidence | ~2Kt | `SES:last`, `STAT`, `VAL`, `RES`, `FIND` (when present) |
| **P4** | Critical references | ~3Kt | `REF:critical`, `DOC`, `ART` (when present) |
| **P5** | Extended context | Unlimited | `DIAG`, `TBL`, long references, history |

**Application rules:**

| Rule | Description |
|------|-------------|
| Anti-positional truncation | Never reduce by head/tail if priority policy exists |
| P0 immutable | FCS, OBJ, CNST, STP are never removed |
| CNST:blocking | Survives even in CORTEX-MIN |
| CLAIM/LIM | Survive at least until RECOVERY |
| "When present" | Sigils not present = level has fewer entries (not an error) |

---

## 3. Conceptual load profiles

| Profile | Budget | P-levels loaded | Suitable for |
|---------|:-----:|:---------------:|--------------|
| CORTEX-MIN | ~500t | P0 + CNST:blocking + survive:min | Extreme budget, single directive |
| CORTEX-RECOVERY | ~2Kt | P0–P2 + survive:recovery | Resuming from compressed SES |
| CORTEX-WORK | ~4Kt | P0–P3 + survive:work | Daily operation |
| CORTEX-FULL | ~8Kt | P0–P5 + survive:full | Audit, review, full session |

---

## 4. HCORTEX as render target

HCORTEX is the human-readable output of the survival core. When an agent responds, it should render the surviving entries as HCORTEX — not raw `.cortex` and not arbitrary prose.

| Profile | HCORTEX mode | Includes |
|---------|:-----------:|----------|
| CORTEX-MIN | Readable | P0 entries as a single table |
| CORTEX-RECOVERY | Readable + source | P0–P2 with source column |
| CORTEX-WORK | Readable + source | P0–P3 with source, full names |
| CORTEX-FULL | Audit | All levels, PUML verbatim, traceable |

---

## 5. Degradation policy

When context budget is exceeded, entries are degraded **P5→P1**. P0 is never degraded.

1. Remove all P5 entries (DIAG, TBL, long history).
2. Remove all P4 entries (REF:critical, DOC, ART).
3. Remove all P3 entries (SES:last, STAT, etc.).
4. Remove P2 non-critical entries.
5. If still over budget, remove P1 non-essential entries.
6. P0 + CNST:blocking always survive.

---

## 6. Contextual efficiency metric

> ⚠️ Conceptual. Automated survival benchmarks are planned but not blocking for current usage.

```text
E_context = (P0_retained + P1_retained + P2_retained) / (P0_total + P1_total + P2_total)
```

Where:
- `P{N}_retained` = entries of that level that survived compression
- `P{N}_total` = entries of that level before compression

> **See:** [`docs/es/specs/supervivencia-contexto.md`](../es/specs/supervivencia-contexto.md) for the Spanish version with additional notes on implementation constraints.
