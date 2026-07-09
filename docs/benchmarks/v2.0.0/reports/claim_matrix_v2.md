<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX v2.0.0 -->
<!-- SPDX-License-Identifier: MIT -->

# Matriz de Claims — Benchmark v2.0.0

> **Perfil: HCORTEX-AUDIT** · source: scientific_report_v2.md §6 + runs/

## 1. Claims v2.0.0

| # | Claim | Status | Evidence | Allowed wording | Forbidden wording |
|:---:|-------|:---:|----------|-----------------|-------------------|
| C-v2-01 | CLI v2.4.0 no degrada métodos v1 (Δ = 0.0 en todas las métricas) | **Demostrado** | `v1_vs_v2_comparison.json`: todos los deltas = 0.0 | "v2.4.0 mantiene compatibilidad con v1" | "v2.4.0 mejora métodos v1" |
| C-v2-02 | `cortex_v2_priority_pack` con fallback produce idéntico a CPP v1 | **Demostrado** | WS = 7.03 ambos; Δ = 0.0 | "v2 PP con fallback equivale a v1" | "v2 PP mejora a v1" |
| C-v2-03 | `cortex_v2_canonical` falla (BCFNR = 1.0, WS = −2.73) | **Demostrado** | `summary_tasks.csv` | "v2-canonicalize rompe compatibilidad con v1 render" | "v2-canonicalize preserva semántica" |
| C-v2-04 | VIEW coverage = 0 % en corpus v1.0.0 (sin VIEW directives) | **Demostrado** | `v2-verify-view` en 10 casos: 0% | "Corpus v1.0.0 no tiene VIEW directives" | "v2.4.0 no soporta VIEW" |
| C-v2-05 | Reversibility = False en corpus v1.0.0 | **Demostrado** | `v2-verify-view` en 10 casos: reversible=False | "Reversibilidad requiere migración a v2" | "v2.4.0 no es reversible" |
| C-v2-06 | La bidireccionalidad requiere VIEW directives en el .cortex | **Demostrado** | Skill canónico (100% coverage) vs corpus (0% coverage) | "Bidireccionalidad requiere VIEW" | "Bidireccionalidad falla en v2.4.0" |
| C-v2-07 | v2-convert produce HCORTEX vacío (251 bytes) sin VIEW | **Demostrado** | Tamaño output: 251 vs 3030 bytes | "v2-convert requiere VIEW para output sustancial" | "v2-convert no funciona" |
| C-v2-08 | Las 4 métricas v2 nuevas son informativas pero = 0 en corpus actual | **Demostrado** | `summary_tasks.csv`: VIEW=0, rev=0, bidir=0, loss=0 | "Métricas v2 requieren corpus migrado" | "Métricas v2 no son útiles" |
| C-v2-09 | QDD = −3.95 (igual que v1.0.0): estructura > query-dependent | **Demostrado** | `derived_metrics.json` | "Estructura cognitiva supera a query-dependent" | "v2 mejora QDD" |
| C-v2-10 | MRD = +2.16 (igual que v1.0.0): CPP supera baselines posicionales | **Demostrado** | `derived_metrics.json` | "CPP supera basales en middle-work" | "v2 mejora MRD" |
| C-v2-11 | v2.4.0 es funcionalmente superior en capacidades potenciales | **Parcialmente soportado** | Skill canónico logra 100% coverage; corpus v1.0.0 no puede explotarlo | "v2.4.0 tiene capacidades bidireccionales" | "v2.4.0 es superior en preservación" |
| C-v2-12 | v2.1.0 con corpus migrado mejorará métricas v2 | **Hipótesis razonable** | Skill canónico demuestra que v2.4.0 soporta VIEW | "Se espera que v2.1.0 active métricas v2" | "v2.1.0 mejorará preservación" |
| C-v2-13 | v2.4.0 mejora el razonamiento LLM | **No soportado** | No evaluado (fase LLM no ejecutada) | (no claim permitido) | "v2.4.0 mejora agentes LLM" |

## 2. Resumen por estado

| Estado | Cantidad | % |
|--------|:---:|:---:|
| Demostrado | 10 | 77 % |
| Parcialmente soportado | 1 | 8 % |
| Hipótesis razonable | 1 | 8 % |
| No soportado | 1 | 8 % |
| **Total** | **13** | **100 %** |

## 3. Diferencias vs v1.0.0

| Aspecto | v1.0.0 | v2.0.0 |
|---------|--------|--------|
| Claims demostrados | 7 / 16 (44 %) | 10 / 13 (77 %) |
| Claims no soportados | 3 / 16 (19 %) | 1 / 13 (8 %) |
| Nuevos claims v2 | — | 8 (C-v2-01 a C-v2-08) |
| Claims heredados confirmados | — | 5 (C-v2-09 a C-v2-13) |
