<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX v2.2.0 -->
<!-- SPDX-License-Identifier: MIT -->

# Reporte de Regresión v2.2.0 — v2.1.0 vs v2.2.0

> **Perfil: HCORTEX-AUDIT**

## 1. Resumen de regresión

| Tipo | ¿Detectada? | Severidad |
|------|:---:|:---:|
| **Harness** | No | — |
| **Corpus** | No (mismo corpus v2.1.0) | — |
| **Algoritmo (v1)** | No | — |
| **Algoritmo (v2)** | **Progresión** (+0.16 WS por learning metrics) | Mejora |
| **Métrica** | Sí (+5 nuevas métricas learning/security) | Mejora |
| **Esperada** | Sí — Learning Engine y E2 Security activados | Mejora |

## 2. Análisis por método (v2.1.0 → v2.2.0)

### 2.1 Métodos legacy (sin regresión)

| Método | WS v2.1.0 | WS v2.2.0 | Δ | ¿Regresión? |
|--------|:---:|:---:|:---:|:---:|
| `recent_tail_raw` | 4.62 | 4.62 | 0.00 | No |
| `head_tail_raw` | 4.62 | 4.62 | 0.00 | No |
| `head_json` | 4.88 | 4.88 | 0.00 | No |
| `head_markdown_summary` | 4.88 | 4.88 | 0.00 | No |
| `semantic_field_pack` | 4.70 | 4.70 | 0.00 | No |
| `keyword_retrieval_raw` | 3.08 | 3.08 | 0.00 | No |

### 2.2 Métodos CODEC (progresión)

| Método | WS v2.1.0 | WS v2.2.0 | Δ | Causa |
|--------|:---:|:---:|:---:|-------|
| `cortex_priority_pack_v1` | 7.03 | **7.18** | **+0.15** | Learning metrics contribution |
| `cortex_priority_pack` | 9.31 | **9.47** | **+0.16** | Learning metrics contribution |
| `cortex_canonical` | 9.31 | **9.47** | **+0.16** | Learning metrics contribution |
| `cortex_ablation_no_P0` | 3.79 | 3.94 | +0.15 | Learning metrics contribution |
| `cortex_ablation_no_temporal` | 6.92 | 7.08 | +0.16 | Learning metrics contribution |

**Conclusión**: Todos los métodos CODEC progresan +0.15-0.16 puntos por la contribución de learning metrics al weighted score. Los métodos legacy (sin .cortex) no cambian porque no tienen learning metrics.

### 2.3 Progresión de métricas nuevas

| Métrica | v2.1.0 | v2.2.0 | Estado |
|---------|:---:|:---:|:---:|
| learn_candidates | N/A | 1.05 | ✅ ACTIVADA |
| learn_promotion_score | N/A | 0.65 | ✅ ACTIVADA |
| learn_elevations | N/A | 0.58 | ✅ ACTIVADA |
| learn_hotness_avg | N/A | 0.65 | ✅ ACTIVADA |
| secret_count | N/A | 0.00 | ✅ ACTIVADA (0 secrets) |

## 3. Conclusión de regresión

1. **No hay regresiones** de harness, corpus, algoritmo v1 ni métrica.

2. **Todos los métodos CODEC progresan +0.15-0.16** por la contribución de learning metrics.

3. **Learning Engine v0.1.0 es funcional** y produce métricas informativas (1.05 candidates/run, 0.65 promotion_score).

4. **E2 Security no produce falsos positivos** (0 secrets en corpus limpio).

5. **No se requiere rollback**. La progresión se atribuye a:
   - Integración de Learning Engine v0.1.0
   - E2 Security evaluada
   - SKILL v1.3.0 y AGENT.md actualizados
   - CLI v0.3.6 con verify v2 nativo

6. **Recomendación**: el issue de `roundtrip-bidir` direction 1 persiste pero es recognized as known limitation en CI (non-blocking).
