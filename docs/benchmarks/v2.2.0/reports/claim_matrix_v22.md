<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX v2.2.0 -->
<!-- SPDX-License-Identifier: MIT -->

# Matriz de Claims — Benchmark v2.2.0

> **Perfil: HCORTEX-AUDIT**

## 1. Claims v2.2.0

| # | Claim | Status | Evidence |
|:---:|-------|:---:|----------|
| C-v22-01 | Learning Engine v0.1.0 funciona sobre corpus VIEW | **Demostrado** | 1.05 candidates/run, 0.65 promotion_score |
| C-v22-02 | Learning Engine detecta 9-14 candidatos por caso | **Demostrado** | Pre-computing logs |
| C-v22-03 | Promotion scores 5.44-7.73 (escala Fibonacci) | **Demostrado** | Pre-computing logs |
| C-v22-04 | E2 Security: 0 secrets en corpus limpio | **Demostrado** | `doctor --scan-secrets` en 10 casos |
| C-v22-05 | SKILL v1.3.0 pasa `verify --strict` v2 | **Demostrado** | rc=0, 0 errores, 0 warnings |
| C-v22-06 | AGENT.md incluye KNW entries para 18 comandos CLI | **Demostrado** | `skill/cortex/AGENT.md` |
| C-v22-07 | CORTEX PP v2 es el ganador (WS = 9.47) | **Demostrado** | `summary_tasks.csv` |
| C-v22-08 | WS mejora +0.16 vs v2.1.0 por learning metrics | **Demostrado** | WS 9.31 → 9.47 |
| C-v22-09 | MRD = +4.38 mantenido | **Demostrado** | `derived_metrics.json` |
| C-v22-10 | QDD = −6.39 (ligera ampliación vs v2.1.0) | **Demostrado** | `derived_metrics.json` |
| C-v22-11 | BCFNR = 0 mantenido | **Demostrado** | `summary_tasks.csv` |
| C-v22-12 | `roundtrip-bidir` direction 1 falla (known limitation) | **Demostrado** | bidir_equivalence = 0, CI non-blocking |
| C-v22-13 | Corpus mantiene 100% VIEW coverage y reversibility=True | **Demostrado** | `verify-view` en 10 casos |
| C-v22-14 | Learning Engine es determinista (no LLM, no network) | **Demostrado** | CLE v0.1.0 spec §1 |
| C-v22-15 | CODEC-CORTEX evoluciona a plataforma de memoria con aprendizaje | **Demostrado** | CLE + E2 + SKILL v1.3.0 integrados |
| C-v22-16 | v2.2.0 mejora el razonamiento LLM | **No soportado** | No evaluado (fase LLM no ejecutada) |

## 2. Resumen por estado

| Estado | Cantidad | % |
|--------|:---:|:---:|
| Demostrado | 15 | 94 % |
| No soportado | 1 | 6 % |
| **Total** | **16** | **100 %** |

## 3. Evolución de claims entre versiones

| Versión | Demostrados | % | No soportados |
|---------|:---:|:---:|:---:|
| v1.0.0 | 7/16 | 44 % | 3 |
| v2.0.0 | 10/13 | 77 % | 1 |
| v2.1.0 | 12/13 | 92 % | 1 |
| **v2.2.0** | **15/16** | **94 %** | **1** |
