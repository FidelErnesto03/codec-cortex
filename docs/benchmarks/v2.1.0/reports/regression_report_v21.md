<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX v2.1.0 -->
<!-- SPDX-License-Identifier: MIT -->

# Reporte de Regresión v2.1.0 — v2.0.0 vs v2.1.0

> **Perfil: HCORTEX-AUDIT** · source: comparación runs v2.0.0 vs v2.1.0

## 1. Resumen de regresión

| Tipo | ¿Detectada? | Severidad |
|------|:---:|:---:|
| **Harness** | No | — |
| **Corpus** | Sí (migración a VIEW) | Mejora |
| **Algoritmo (v1)** | No | — |
| **Algoritmo (v2)** | **Progresión** (canonicalize fixed) | Mejora |
| **Métrica** | No (misma fórmula) | — |
| **Esperada** | Sí — métricas v2 activadas | Mejora |

## 2. Análisis por método (v2.0.0 → v2.1.0)

### 2.1 Métodos legacy (sin regresión, sin cambios)

| Método | WS v2.0.0 | WS v2.1.0 | Δ | ¿Regresión? |
|--------|:---:|:---:|:---:|:---:|
| `recent_tail_raw` | 4.62 | 4.62 | 0.00 | No |
| `head_tail_raw` | 4.62 | 4.62 | 0.00 | No |
| `head_json` | 4.88 | 4.88 | 0.00 | No |
| `head_markdown_summary` | 4.88 | 4.88 | 0.00 | No |
| `semantic_field_pack` | 4.70 | 4.70 | 0.00 | No |
| `keyword_retrieval_raw` | 3.08 | 3.08 | 0.00 | No |
| `cortex_priority_pack_v1` | 7.03 | 7.03 | 0.00 | No |
| `cortex_ablation_no_P0` | 3.80 | 3.79 | −0.01 | No (marginal) |
| `cortex_ablation_no_temporal` | 6.93 | 6.92 | −0.01 | No (marginal) |

**Conclusión**: 9 de 9 métodos legacy sin regresión significativa. Deltas marginales (−0.01) en ablations se atribuyen a cambios menores en el corpus migrado (cabeceras, status values).

### 2.2 Métodos v2 (progresión)

| Método | WS v2.0.0 | WS v2.1.0 | Δ | Estado |
|--------|:---:|:---:|:---:|:---:|
| `cortex_priority_pack` (was `cortex_v2_priority_pack`) | 7.03 (con fallback) | **9.31** (sin fallback) | **+2.28** | ✅ Progresión |
| `cortex_canonical` (was `cortex_v2_canonical`) | **−2.73** (fallaba) | **+9.31** (funciona) | **+12.04** | ✅ Fix mayor |

### 2.3 Progresión de `cortex_canonical` (fix B-01/B-05)

| Métrica | v2.0.0 | v2.1.0 | Δ |
|---------|:---:|:---:|:---:|
| WS | −2.73 | +9.31 | **+12.04** ✅ |
| BCFNR | 1.000 | 0.000 | **−1.00** ✅ |
| P0 survival | 0.00 | 0.98 | +0.98 ✅ |
| STR | 0.00 | 1.00 | +1.00 ✅ |
| VIEW coverage | 0.00 | 1.00 | +1.00 ✅ |
| Reversibility | 0 | 1 | +1 ✅ |

**Causa raíz del fix**: `canonicalize --preserve` (nuevo en v0.3.2) fuerza canonicalización structure-preserving que no rompe compatibilidad con v1 render, incluso cuando el artefacto tiene VIEW directives.

## 3. Regresión esperada (endurecimiento)

| Endurecimiento v2.1.0 | Impacto |
|------------------------|---------|
| Corpus migrado a VIEW (108 VIEW directives) | Métricas v2 activadas (VIEW=100%, rev=1.0) |
| Header CODEC-CORTEX en .cortex | `convert` detecta formato correctamente |
| Status values normalizados (`status:"current"`) | `verify-view` reporta 100% coverage |
| Nombres canónicos CLI | Alias `v2-*` emiten WARNING pero funcionan |

## 4. Issue pendiente (no regresión)

| Issue | Severidad | Causa | Recomendación |
|-------|:---:|-------|---------------|
| `roundtrip-bidir` direction 1 falla | Media | E_TABLE_SCHEMA_MISMATCH: VIEW declara más fields que columnas de tabla | Alinear fields VIEW con schema real, o usar `kind:"section"` |

## 5. Conclusión de regresión

1. **No hay regresiones** de harness, algoritmo v1 ni métrica.

2. **`cortex_canonical` progresa +12.04 puntos** de WS (de peor método a mejor método empatado), confirmando que el fix B-01/B-05 de v0.3.2 es efectivo.

3. **`cortex_priority_pack` progresa +2.28 puntos** al activarse las métricas v2 (VIEW coverage, reversibility) que en v2.0.0 estaban en 0.

4. **Los métodos legacy se mantienen estables** (Δ ≤ 0.01), confirmando que la migración del corpus a VIEW no degrada el comportamiento de métodos v1.

5. **No se requiere rollback**. Las progresiones se atribuyen a:
   - Migración del corpus a VIEW directives
   - Fix de `canonicalize --preserve`
   - Header CODEC-CORTEX en .cortex
   - Nombres canónicos CLI

6. **Recomendación para el proyecto CODEC-CORTEX**: documentar el issue de `roundtrip-bidir` con E_TABLE_SCHEMA_MISMATCH para fix en v0.3.3 o v2.2.0.
