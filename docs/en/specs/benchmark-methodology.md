<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MPL-2.0 -->

<p align="center">
  <strong>CODEC-CORTEX</strong> — Benchmark Methodology
  <br>
  <sub>SPECIFICATION · Survival Core · v0.3.7 · MIT · <a href="../../AUTHORS.md">Fidel Ernesto Lozada A.</a></sub>
</p>

---

> **STATUS NOTE:** This document is specification. As of v0.3.7 the deterministic parser, the CLI, and `cortex benchmark` (inventory + suite validation) are implemented. The scientific suites v1.0.0, v2.0.0 and v2.1.0 are published under `benchmarks/` with 4,840 runs each. Suites 0.1, 0.1b, and 0.2 remain listed as legacy offline/proxy reference. The methodology described here applies both to existing suites and to future contextual survival automation.

**Abstract:** Decision-survival-centered benchmark methodology — not term occurrence. Defines 5 evaluation questions, 2 scenarios, and contextual survival rate metrics. Suites 0.1, 0.1b, and 0.2 exist as offline/proxy evidence; suites v1.0.0, v2.0.0, and v2.1.0 are reproducible scientific benchmarks published under `benchmarks/`.

| | |
|---|---|
| **Author** | Fidel Ernesto Lozada A. — Systems Engineer / MSc. Management Sciences |
| **Repository** | github.com/FidelErnesto03/codec-cortex |
| **License** | MIT |

---

## 1. Philosophy

The benchmark measures **decision survival** — not term recurrence. A protocol passes when the agent preserves and applies a critical decision under context pressure, not when it repeats keywords.

---

## 2. Five evaluation questions

| # | Question | What it measures |
|:-:|----------|-----------------|
| 1 | Was the decision preserved? | Did the agent retain the core directive under load? |
| 2 | Was the constraint applied? | Did the agent respect boundaries declared in CNST? |
| 3 | Was the context recoverable? | Could the agent resume from compressed SES/LNG? |
| 4 | Was the commitment honored? | Did WRK/NXT survive and trigger follow-through? |
| 5 | Was the output faithful? | Did CORTEX-OUT correctly reflect the protocol state? |

---

## 3. Scenarios

| Scenario | Description | Corpus |
|----------|-------------|--------|
| **Priority pack** | Agent receives a .cortex with 6 live sigils; context is compressed to a budget forcing P5→P1 degradation | 5 randomized variants per suite |
| **Full recovery** | Agent receives only compressed SES/LNG; must reconstruct operational state without FCS/OBJ | 5 randomized variants per suite |

---

## 4. Metrics

| Metric | Formula | Target |
|--------|---------|:-----:|
| Survival rate | decisions_preserved / total_decisions | ≥ 0.85 |
| Recovery rate | state_reconstructed / total_state | ≥ 0.70 |
| Constraint adherence | constraints_applied / total_constraints | 1.0 |
| Output fidelity | correct_outputs / total_outputs | ≥ 0.90 |

---

## 5. Reference benchmarks

| Suite | Version | Type | Runs | Location |
|:-----:|:-------:|:----:|:----:|----------|
| 0.1 | Legacy | Manual offline/proxy | — | Historical reference |
| 0.1b | Legacy | Manual offline/proxy | — | Historical reference |
| 0.2 | Legacy | Manual offline/proxy | — | Historical reference |
| v1.0.0 | Scientific | Reproducible automated | 4,840 | `benchmarks/v1.0.0/` |
| v2.0.0 | Scientific | Reproducible automated | 4,840 | `benchmarks/v2.0.0/` |
| v2.1.0 | Scientific | Reproducible automated | 4,840 | `benchmarks/v2.1.0/` |

> **See:** [`docs/es/specs/metodologia-benchmark.md`](../es/specs/metodologia-benchmark.md) for the Spanish version with detailed scenario descriptions and corpus structure.
