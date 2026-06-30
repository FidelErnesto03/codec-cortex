<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX v2.0.0 -->
<!-- SPDX-License-Identifier: MIT -->

# Reporte de Regresión v2.0.0 — v1.0.0 vs v2.0.0

> **Perfil: HCORTEX-AUDIT** · source: comparación runs v1.0.0 vs v2.0.0

## 1. Resumen de regresión

| Tipo de regresión | ¿Detectada? | Severidad |
|-------------------|:---:|:---:|
| **Harness** | No | — |
| **Corpus** | No (mismo corpus) | — |
| **Algoritmo (v1)** | No | — |
| **Algoritmo (v2)** | **Sí** — `cortex_v2_canonical` falla | Alta |
| **Métrica** | No (misma fórmula) | — |
| **Esperada** | Sí — 4 métricas nuevas todas = 0 | Baja |

## 2. Análisis por método

### 2.1 Métodos legacy (sin regresión)

| Método | WS v1.0.0 | WS v2.0.0 | Δ | ¿Regresión? |
|--------|:---:|:---:|:---:|:---:|
| `recent_tail_raw` | 4.62 | 4.62 | 0.00 | No |
| `head_tail_raw` | 4.62 | 4.62 | 0.00 | No |
| `head_json` | 4.88 | 4.88 | 0.00 | No |
| `head_markdown_summary` | 4.88 | 4.88 | 0.00 | No |
| `semantic_field_pack` | 4.70 | 4.70 | 0.00 | No |
| `keyword_retrieval_raw` | 3.08 | 3.08 | 0.00 | No |
| `cortex_priority_pack_v1` | 7.03 | 7.03 | 0.00 | No |
| `cortex_ablation_no_P0` | 3.80 | 3.80 | 0.00 | No |
| `cortex_ablation_no_temporal` | 6.93 | 6.93 | 0.00 | No |

**Conclusión**: 9 de 9 métodos legacy sin regresión. CLI v2.4.0 mantiene compatibilidad total con CLI v1.1.9 para métodos legacy.

### 2.2 Métodos v2 nuevos (no comparables con v1.0.0)

| Método | WS v2.0.0 | Comportamiento |
|--------|:---:|----------------|
| `cortex_v2_priority_pack` | 7.03 | Fallback a v1 exitoso; idéntico a CPP v1 |
| `cortex_v2_canonical` | **−2.73** | **Falla**: v2-canonicalize rompe compatibilidad |

### 2.3 Regresión de `cortex_v2_canonical`

| Métrica | Valor | Causa raíz |
|---------|:---:|------------|
| EAS | 0.175 | HCORTEX vacío (71 tokens) no contiene términos esperados |
| P0 survival | 0.00 | Sin entries P0 en output |
| BCFNR | **1.000** | Todas las constraints blocking omitidas |
| WS | **−2.73** | Penalización por BCFNR + métricas en 0 |

**Causa raíz identificada**: `v2-canonicalize` reescribe el `.cortex` a un formato canónico v2 que:
1. Pierde compatibilidad con `v1 render --profile` (legacy)
2. No añade VIEW directives (necesarias para v2-convert)
3. Produce un .cortex intermedio que ni v1 ni v2 pueden renderizar correctamente

**Severidad**: Alta — el método produce output peor que cualquier baseline.

**Recomendación**: No usar `v2-canonicalize` sobre corpus v1.0.0 sin migración previa a formato v2 con VIEW directives.

## 3. Regresión esperada (endurecimiento)

| Endurecimiento v2.0.0 | Impacto |
|------------------------|---------|
| 4 métricas nuevas (VIEW, rev, bidir, loss) | Todas = 0 en corpus v1.0.0 (esperado) |
| Comparación v1 vs v2 explícita | Permite aislar cambios atribuibles al CLI |
| Diferenciación de 3 variantes CPP | v2.0.0 distingue v1, v2_PP, v2_canonical (v1.0.0 las tenía idénticas) |

## 4. Conclusión de regresión

1. **No hay regresiones de harness ni de algoritmo v1**. CLI v2.4.0 es backward-compatible con CLI v1.1.9.

2. **`cortex_v2_canonical` es una regresión de algoritmo v2** atribuible a incompatibilidad entre `v2-canonicalize` y el corpus v1.0.0 sin VIEW directives. No es un bug del CLI v2.4.0 per se, sino una incompatibilidad de formato.

3. **Las 4 métricas v2 nuevas son todas 0** en el corpus actual, lo cual es **regresión esperada** (no se puede medir VIEW coverage sin VIEW directives).

4. **No se requiere rollback** del CLI v2.4.0. Las regresiones se resuelven migrando el corpus a formato v2 (trabajo futuro v2.1.0).

5. **Recomendación para el proyecto CODEC-CORTEX**: documentar que `v2-canonicalize` requiere VIEW directives en el .cortex de entrada, o implementar fallback automático a v1 render.
