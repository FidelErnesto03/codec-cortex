<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX v2.1.0 -->
<!-- SPDX-License-Identifier: MIT -->

# Matriz de Claims — Benchmark v2.1.0

> **Perfil: HCORTEX-AUDIT** · source: scientific_report_v21.md

## 1. Claims v2.1.0

| # | Claim | Status | Evidence | Allowed wording | Forbidden wording |
|:---:|-------|:---:|----------|-----------------|-------------------|
| C-v21-01 | v0.3.2 resuelve los 3 issues principales de v2.0.0 | **Demostrado** | Comparación v2.0.0 vs v2.1.0 | "v0.3.2 aborda issues de v2.0.0" | "v0.3.2 resuelve todos los issues" |
| C-v21-02 | CORTEX PP v2 (`convert`) es el nuevo ganador (WS = 9.31) | **Demostrado** | `summary_tasks.csv` | "CPP v2 supera a CPP v1 en WS" | "CPP v2 es siempre superior" |
| C-v21-03 | `canonicalize --preserve` fixea B-01/B-05 (WS: −2.73 → +9.31) | **Demostrado** | Comparación v2.0.0 vs v2.1.0 | "`canonicalize --preserve` es VIEW-aware" | "`canonicalize` siempre preserva compatibilidad" |
| C-v21-04 | VIEW coverage = 100 % en todos los casos del corpus migrado | **Demostrado** | `verify-view` en 10 casos | "Corpus migrado alcanza 100% VIEW coverage" | "VIEW coverage es 100% en cualquier corpus" |
| C-v21-05 | Reversibility = True en todos los casos del corpus migrado | **Demostrado** | `verify-view` en 10 casos | "Corpus migrado es reversible" | "Cualquier .cortex es reversible" |
| C-v21-06 | MRD se duplica (+2.16 → +4.38) por activación de métricas v2 | **Demostrado** | `derived_metrics.json` | "MRD mejora con corpus migrado" | "MRD siempre mejora con VIEW" |
| C-v21-07 | QDD se amplía (−3.95 → −6.24) | **Demostrado** | `derived_metrics.json` | "Estructura cognitiva amplía ventaja" | "Query-dependent nunca supera a estructura" |
| C-v21-08 | BCFNR = 0 mantenido en métodos v2 | **Demostrado** | `summary_tasks.csv` | "Constraints blocking preservadas" | "BCFNR siempre es 0" |
| C-v21-09 | Trade-off: +396 tokens por +2.28 WS | **Demostrado** | `v1_vs_v2_comparison.json` | "El overhead de tokens se justifica" | "v2 es más eficiente en tokens" |
| C-v21-10 | EAS baja ligeramente (0.984 → 0.950) por nombres canónicos | **Demostrado** | `summary_tasks.csv` | "EAS baja por nombres canónicos de campos" | "v2 pierde evidencia" |
| C-v21-11 | `roundtrip-bidir` direction 1 falla por E_TABLE_SCHEMA_MISMATCH | **Demostrado** | bidir_equivalence = 0 | "roundtrip-bidir tiene issue pendiente" | "roundtrip-bidir no funciona" |
| C-v21-12 | v2.1.0 es mejor que v1.0.0 (WS +2.28, MRD +2.22) | **Demostrado** | Comparación v1.0.0 vs v2.1.0 | "v2.1.0 supera a v1.0.0 en métricas agregadas" | "v2.1.0 es siempre superior" |
| C-v21-13 | v2.1.0 mejora el razonamiento LLM | **No soportado** | No evaluado (fase LLM no ejecutada) | (no claim permitido) | "v2.1.0 mejora agentes LLM" |

## 2. Resumen por estado

| Estado | Cantidad | % |
|--------|:---:|:---:|
| Demostrado | 12 | 92 % |
| No soportado | 1 | 8 % |
| **Total** | **13** | **100 %** |

## 3. Evolución de claims entre versiones

| Versión | Demostrados | % | No soportados |
|---------|:---:|:---:|:---:|
| v1.0.0 | 7/16 | 44 % | 3 |
| v2.0.0 | 10/13 | 77 % | 1 |
| **v2.1.0** | **12/13** | **92 %** | **1** |

La tasa de claims demostrados mejora con cada versión, reflejando la madurez creciente del CLI y del corpus.
