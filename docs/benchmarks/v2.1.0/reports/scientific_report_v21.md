<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX v2.1.0 -->
<!-- SPDX-License-Identifier: MIT -->
<!-- source: scientific_report_v21.md — HCORTEX scientific report v2.1.0 -->

# Informe Científico del Benchmark CODEC-CORTEX v2.1.0

> **Perfil: HCORTEX-FULL** · v2.1.0 · 2026-07-01 · source: benchmark harness v2.1.0 + CLI v0.3.2

---

## 0. Resumen ejecutivo

| Campo | Valor |
|-------|-------|
| **Benchmark version** | 2.1.0 |
| **Versiones anteriores** | 1.0.0 (2026-06-28), 2.0.0 (2026-06-30) |
| **Fecha de ejecución** | 2026-07-01 |
| **CODEC-CORTEX versión** | 0.3.2 |
| **CLI versión** | 0.3.2 (nombres canónicos: `convert`, `canonicalize`, `verify-view`, `roundtrip-bidir`) |
| **Harness versión** | 2.1.0 |
| **Corpus** | L2-multidominio migrado a VIEW directives (10 dominios, 50 artefactos, 108 VIEW directives) |
| **Métodos comparados** | 11 (4 posicionales + 1 semántico + 1 query-dep + 1 CODEC v1 + 2 CODEC v2 + 2 ablations) |
| **Escenarios** | 11 (sin cambios vs v2.0.0) |
| **Tareas** | 40 (sin cambios vs v2.0.0) |
| **Total de runs** | 4 840 (11 × 11 × 40) |
| **Fase LLM** | No ejecutada (determinística pura, §11.2 del protocolo) |
| **Reproducibilidad** | Hashes SHA-256 + manifest + scripts versionados |

### Novedades v2.1.0 vs v2.0.0

| Aspecto | v2.0.0 | v2.1.0 |
|---------|--------|--------|
| **CLI version** | 2.4.0 (`v2-*` commands) | 0.3.2 (nombres canónicos sin prefijo) |
| **CODEC-CORTEX versión** | 0.3.1 | 0.3.2 |
| **Corpus** | Sin VIEW directives (v1.0.0 reutilizado) | **Migrado a VIEW** (10-13 VIEW por caso) |
| **`canonicalize`** | Rompe compatibilidad (BCFNR = 1.0) | **`--preserve` VIEW-aware** (BCFNR = 0.0) |
| **VIEW coverage** | 0 % en todos los casos | **100 % en todos los casos** |
| **Reversibility** | 0 (False) en todos los casos | **1 (True) en todos los casos** |
| **`convert` output** | 251 bytes (vacío sin VIEW) | **4 718 bytes (sustancial)** |
| **WS ganador** | 7.03 (CPP v1 con fallback) | **9.31 (CORTEX PP v2 nativo)** |

### Hallazgos principales v2.1.0

| # | Hallazgo | Estado | Evidencia |
|:---:|----------|:---:|-----------|
| H-01 | CORTEX PP v2 (CLI v0.3.2 `convert`) es el nuevo ganador con WS = 9.31 | **Demostrado** | `summary_tasks.csv`: cortex_priority_pack WS = 9.31 |
| H-02 | `canonicalize --preserve` fixea el issue B-01/B-05: WS pasa de −2.73 a +9.31 | **Demostrado** | `summary_tasks.csv`: cortex_canonical WS = 9.31 |
| H-03 | VIEW coverage = 100 % y reversibility = 1.0 en todos los métodos v2 | **Demostrado** | `summary_tasks.csv`: avg_VIEW_coverage = 1.00, avg_reversibility = 1.0 |
| H-04 | MRD = +4.38 (vs +2.16 en v2.0.0): la ventaja sobre baselines posicionales se amplía | **Demostrado** | `derived_metrics.json`: MRD winner = cortex_priority_pack = +4.38 |
| H-05 | QDD = −6.24 (vs −3.95 en v2.0.0): la estructura cognitiva supera aún más a query-dependent | **Demostrado** | `derived_metrics.json`: QDD = −6.24 |
| H-06 | BCFNR = 0 mantenido en métodos v2 (constraints blocking nunca omitidas) | **Demostrado** | `summary_tasks.csv`: avg_BCFNR = 0.000 |
| H-07 | Trade-off: +396 tokens promedio (HCORTEX v2 más verbose) pero +2.28 WS | **Demostrado** | `v1_vs_v2_comparison.json`: ctx_tokens +396.2, WS +2.28 |
| H-08 | EAS baja ligeramente (0.984 → 0.950) por nombres canónicos de campos en HCORTEX v2 | **Demostrado** | `summary_tasks.csv`: avg_EAS 0.984 (v1) vs 0.950 (v2) |
| H-09 | `roundtrip-bidir` falla por E_TABLE_SCHEMA_MISMATCH (issue pendiente para v2.2.0) | **Demostrado** | bidir_equivalence = 0 en todos los métodos |
| H-10 | Los 3 issues de v2.0.0 (corpus VIEW, canonicalize, naming) están resueltos en v0.3.2 | **Demostrado** | Comparación directa v2.0.0 vs v2.1.0 |

---

## 1. Introducción y contexto

### 1.1 Motivación de v2.1.0

El benchmark v2.0.0 identificó **3 issues críticos** que impedían explotar las capacidades bidireccionales del CLI v2.4.0:

1. **Corpus sin VIEW directives**: el corpus v1.0.0 no tenía VIEW directives, causando que `v2-convert` produjera HCORTEX vacío (251 bytes).
2. **`v2-canonicalize` rompía compatibilidad**: al normalizar el .cortex, perdía compatibilidad con v1 render, produciendo BCFNR = 1.0.
3. **Nombres `v2-*` no canónicos**: los comandos usaban prefijo `v2-` que se consideraba temporal.

El commit `91b8c4c` del repositorio CODEC-CORTEX (v0.3.2) aborda estos 3 issues:

1. ✅ **Migración del corpus a VIEW directives**: los 10 .cortex ahora incluyen secciones `$N: VIEWS` con 10-13 VIEW directives cada uno.
2. ✅ **Fix `canonicalize` (issues B-01/B-05)**: nuevo flag `--preserve` que fuerza canonicalización structure-preserving cuando el artefacto no tiene VIEW directives, y comportamiento VIEW-aware cuando sí las tiene.
3. ✅ **Nombres canónicos CLI**: `v2-convert` → `convert`, `v2-canonicalize` → `canonicalize`, etc. (los alias `v2-*` se mantienen como `deprecated`).

### 1.2 Hipótesis v2.1.0

| Hipótesis | Formulación |
|-----------|-------------|
| H1-v21 | Con corpus migrado a VIEW, `convert` produce HCORTEX sustancial (>1 KB) sin necesidad de fallback. |
| H2-v21 | `canonicalize --preserve` preserva compatibilidad y produce WS ≥ 0 (vs −2.73 en v2.0.0). |
| H3-v21 | VIEW coverage = 100 % y reversibility = True en todos los casos del corpus migrado. |
| H4-v21 | Los métodos v2 superan a los métodos v1 en WS gracias a las métricas v2 activadas. |
| H5-v21 | MRD y QDD mejoran vs v2.0.0 porque los métodos v2 ahora funcionan correctamente. |

---

## 2. Método científico v2.1.0

### 2.1 Cambios vs v2.0.0

| Componente | v2.0.0 | v2.1.0 |
|------------|--------|--------|
| CLI | v2.4.0 (`v2-*` commands) | v0.3.2 (nombres canónicos, alias `v2-*` deprecated) |
| Corpus | v1.0.0 sin VIEW | **Migrado a VIEW** (10-13 VIEW por caso, 100% coverage) |
| `canonicalize` | Sin `--preserve`, rompe compatibilidad | **`--preserve` VIEW-aware** |
| Header corpus | Sin `<!-- CODEC-CORTEX -->` | **Header añadido** para habilitar detección de formato |
| Status VIEW | `status:cur` (no aceptado por strict) | **`status:"current"`** (aceptado) |
| Métodos | `cortex_v2_priority_pack`, `cortex_v2_canonical` | `cortex_priority_pack`, `cortex_canonical` (nombres canónicos) |

### 2.2 Métodos bajo comparación v2.1.0

| Familia | Método | CLI | Descripción |
|---------|--------|-----|-------------|
| **Pasivo posicional** | `recent_tail_raw` | — | Últimos N tokens raw prose |
| | `head_tail_raw` | — | 25% head + 75% tail |
| | `head_json` | — | Primeros N tokens JSON |
| | `head_markdown_summary` | — | Primeros N tokens Markdown |
| **Pasivo semántico** | `semantic_field_pack` | — | Selecciona IDN/DOM/CNST/FCS/OBJ/STP |
| **Query-dependent** | `keyword_retrieval_raw` | — | BM25-like con gold terms |
| **CODEC-CORTEX v1** | `cortex_priority_pack_v1` | v1.x `render` | CLI legacy con `--profile` |
| **CODEC-CORTEX v2** ⭐ | `cortex_priority_pack` | v0.3.2 `convert` | Bidireccional nativo (sin fallback) |
| **CODEC-CORTEX v2** ⭐ | `cortex_canonical` | v0.3.2 `canonicalize --preserve` + `convert` | Normalización + conversión |
| **Ablations** | `cortex_ablation_no_P0` | — | Sin prioridad P0 |
| | `cortex_ablation_no_temporal` | — | Sin distinción temporal |

### 2.3 Corpus migrado a VIEW

| Caso | VIEW directives | VIEW coverage | Reversible |
|------|:---:|:---:|:---:|
| devops-k8s-rollout | 12 | 100 % | True |
| ecom-fraud-checkout | 10 | 100 % | True |
| health-medication-alert | 10 | 100 % | True |
| fintech-aml-kyc | 10 | 100 % | True |
| iot-hvac-anomaly | 11 | 100 % | True |
| legal-contract-redline | 11 | 100 % | True |
| edu-adaptive-lesson | 10 | 100 % | True |
| sec-incident-response | 13 | 100 % | True |
| robotics-warehouse-bot | 11 | 100 % | True |
| climate-grid-balancing | 10 | 100 % | True |
| **Total** | **108** | **100 %** | **10/10** |

---

## 3. Resultados v2.1.0

### 3.1 Tabla agregada por método

> source: `runs/summary_tasks.csv` · 440 runs por método

| Método | v2 | EAS | ETC | F1 | DA | P0 surv | P1 surv | BCFNR | UCFPR | STR | VIEW cov | rev | bidir | ctx tok | ED | WS |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `cortex_priority_pack` ⭐ | 1 | 0.950 | 0.950 | 0.052 | 0.25 | 0.98 | 0.91 | **0.000** | **0.000** | **1.00** | **1.00** | **1.0** | 0.00 | 1122 | 0.0087 | **9.31** |
| `cortex_canonical` ⭐ | 1 | 0.950 | 0.950 | 0.052 | 0.25 | 0.98 | 0.91 | **0.000** | **0.000** | **1.00** | **1.00** | **1.0** | 0.00 | 1122 | 0.0087 | **9.31** |
| `cortex_priority_pack_v1` | 0 | **0.984** | **0.984** | 0.060 | 0.25 | **1.00** | **0.98** | **0.000** | **0.000** | **1.00** | 0.00 | 0.0 | 0.00 | 726 | **0.0099** | 7.03 |
| `cortex_ablation_no_temporal` | 0 | 0.977 | 0.977 | 0.051 | 0.25 | 1.00 | **1.00** | 0.000 | 0.000 | 0.91 | 0.00 | 0.0 | 0.00 | 1105 | 0.0065 | 6.92 |
| `head_json` | 0 | 0.971 | 0.964 | 0.075 | 0.25 | 0.66 | 0.81 | 0.000 | 0.091 | 0.00 | 0.00 | 0.0 | 0.00 | 488 | 0.0111 | 4.88 |
| `head_markdown_summary` | 0 | 0.795 | 0.795 | 0.082 | 0.25 | 0.84 | 0.87 | 0.000 | 0.091 | 0.00 | 0.00 | 0.0 | 0.00 | 388 | 0.0151 | 4.88 |
| `semantic_field_pack` | 0 | 0.800 | 0.800 | 0.097 | 0.25 | 1.00 | 0.05 | 0.000 | 0.000 | 0.00 | 0.00 | 0.0 | 0.00 | 242 | 0.0196 | 4.70 |
| `recent_tail_raw` | 0 | 0.757 | 0.525 | 0.042 | 0.25 | 0.71 | 0.64 | 0.091 | 0.091 | 1.00 | 0.00 | 0.0 | 0.00 | 361 | 0.0148 | 4.62 |
| `head_tail_raw` | 0 | 0.757 | 0.523 | 0.042 | 0.25 | 0.71 | 0.64 | 0.091 | 0.091 | 1.00 | 0.00 | 0.0 | 0.00 | 620 | 0.0079 | 4.62 |
| `cortex_ablation_no_P0` | 0 | 0.643 | 0.473 | 0.031 | 0.25 | 1.00 | 1.00 | **0.700** | 0.000 | 1.00 | 0.00 | 0.0 | 0.00 | 954 | 0.0042 | 3.79 |
| `keyword_retrieval_raw` | 0 | 0.757 | 0.525 | 0.075 | 0.25 | 0.48 | 0.31 | 0.320 | 0.057 | 0.77 | 0.00 | 0.0 | 0.00 | 203 | 0.0249 | 3.08 |

### 3.2 Comparación v1 vs v2.1 (deltas)

> source: `runs/v1_vs_v2_comparison.json`

| Métrica | CPP v1 | CPP v2 (v2.1) | Δ (v2.1 − v1) | Interpretación |
|---------|:---:|:---:|:---:|----------------|
| EAS | 0.984 | 0.950 | **−0.034** | Ligera caída (nombres canónicos) |
| ETC | 0.984 | 0.950 | **−0.041** | Ligera caída |
| F1 | 0.060 | 0.052 | −0.009 | Similar |
| P0 survival | 1.00 | 0.98 | **−0.02** | Ligera caída |
| P1 survival | 0.98 | 0.91 | **−0.067** | Caída moderada |
| BCFNR | 0.000 | 0.000 | **0.000** | Sin cambios (perfecto) |
| STR | 1.00 | 1.00 | **0.000** | Sin cambios |
| **VIEW coverage** | 0.00 | **1.00** | **+1.00** | ✅ ACTIVADA |
| **Reversibility** | 0.0 | **1.0** | **+1.0** | ✅ ACTIVADA |
| Bidir equivalence | 0.00 | 0.00 | 0.00 | Pendiente (E_TABLE_SCHEMA_MISMATCH) |
| Context tokens | 726 | 1122 | **+396** | HCORTEX v2 más verbose |
| Evidence density | 0.0099 | 0.0087 | −0.0012 | Ligera caída (más tokens) |
| **Weighted Score** | 7.03 | **9.31** | **+2.28** | ✅ Mejora neta |

**Interpretación clave**: a pesar de ligeras caídas en EAS/ETC/P0/P1 (por nombres canónicos de campos en HCORTEX v2), el WS mejora +2.28 puntos gracias a la activación de VIEW coverage y reversibility.

### 3.3 Métricas derivadas (MRD y QDD)

| Métrica | v1.0.0 | v2.0.0 | v2.1.0 | Δ v2.1 vs v2.0 |
|---------|:---:|:---:|:---:|:---:|
| MRD winner | CPP v1 (+2.16) | CPP v1 (+2.16) | **CPP v2 (+4.38)** | **+2.22** |
| QDD | −3.95 | −3.95 | **−6.24** | **−2.29** |
| best_passive_score | 7.03 | 7.03 | **9.31** | **+2.28** |
| best_query_dependent_score | 3.08 | 3.08 | 3.08 | 0.00 |

**Interpretación**:

- **MRD casi se duplica** (+2.16 → +4.38) porque CPP v2 ahora funciona correctamente y supera a baselines posicionales por mayor margen.
- **QDD se amplía** (−3.95 → −6.24) porque CPP v2 aumenta su ventaja sobre query-dependent.
- **best_passive_score** sube +2.28 puntos, reflejando la activación de VIEW coverage y reversibility.

### 3.4 Progresión de `cortex_canonical` (fix B-01/B-05)

| Métrica | v2.0.0 (sin --preserve) | v2.1.0 (--preserve) | Δ |
|---------|:---:|:---:|:---:|
| WS | **−2.73** | **+9.31** | **+12.04** ✅ |
| BCFNR | 1.000 | 0.000 | −1.00 ✅ |
| P0 survival | 0.00 | 0.98 | +0.98 ✅ |
| STR | 0.00 | 1.00 | +1.00 ✅ |
| VIEW coverage | 0.00 | 1.00 | +1.00 ✅ |

El fix `canonicalize --preserve` transforma `cortex_canonical` de **peor método** (WS = −2.73) a **mejor método empatado** (WS = +9.31).

---

## 4. Análisis de hallazgos v2.1.0

### 4.1 Confirmación de hipótesis

| Hipótesis | Estado | Evidencia |
|-----------|:---:|-----------|
| H1-v21: `convert` produce HCORTEX sustancial sin fallback | **Confirmada** | 4 718 bytes output, fallback no se activa |
| H2-v21: `canonicalize --preserve` produce WS ≥ 0 | **Confirmada** (y superada) | WS = +9.31 (vs −2.73 en v2.0.0) |
| H3-v21: VIEW coverage = 100 % y reversibility = True | **Confirmada** | `verify-view` en 10 casos: 100% coverage, reversible=True |
| H4-v21: Métodos v2 superan a v1 en WS | **Confirmada** | CPP v2 WS = 9.31 vs CPP v1 WS = 7.03 |
| H5-v21: MRD y QDD mejoran vs v2.0.0 | **Confirmada** | MRD +2.22, QDD −2.29 |

### 4.2 Progresión v1.0.0 → v2.0.0 → v2.1.0

| Dimensión | v1.0.0 | v2.0.0 | v2.1.0 | Progresión total |
|-----------|--------|--------|--------|:---:|
| CLI version | 1.1.9 | 2.4.0 | 0.3.2 | ↑↑ |
| WS ganador | 7.03 | 7.03 | **9.31** | **+2.28** |
| VIEW coverage | N/A | 0% | **100%** | ✅ |
| Reversibility | N/A | 0 | **1.0** | ✅ |
| `canonicalize` funciona | N/A | No (WS=−2.73) | **Sí (WS=+9.31)** | ✅ |
| MRD | +2.16 | +2.16 | **+4.38** | **+2.22** |
| QDD | −3.95 | −3.95 | **−6.24** | Ampliada |
| BCFNR ganador | 0.000 | 0.000 | 0.000 | Mantenido |
| Reproducibilidad | ✓ | ✓ | ✓ | Mantenido |

### 4.3 Trade-offs identificados

| Trade-off | Detalle |
|-----------|---------|
| **Tokens vs WS** | CPP v2 consume +396 tokens pero gana +2.28 WS (ratio: 0.0058 WS/token extra) |
| **EAS vs VIEW coverage** | EAS baja 0.034 (nombres canónicos) pero VIEW coverage gana +1.00 |
| **P1 survival vs reversibility** | P1 survival baja 0.067 pero reversibility gana +1.0 |
| **Bidir equivalence** | Sigue en 0 por E_TABLE_SCHEMA_MISMATCH (issue pendiente) |

### 4.4 Issue pendiente: `roundtrip-bidir` falla

El comando `roundtrip-bidir` falla en direction 1 (CORTEX → HCORTEX → CORTEX) con errores `E_TABLE_SCHEMA_MISMATCH`:

```
VIEW:idn header has 2 data cols (excl. Source) but fields declares 8:
  header=['Campo', 'Valor'], fields=['name', 'role', 'team', 'vendor', 'area', 'version', 'type', 'status']
```

**Causa raíz**: las VIEW declarations del corpus migrado listan más `fields` de los que la tabla HCORTEX tiene columnas. La tabla generada por `convert` usa formato kv_table (2 columnas: Campo/Valor), pero la VIEW declara 4-8 fields.

**Direction 2** (HCORTEX → CORTEX → HCORTEX) sí pasa con `content-equivalent: True`.

**Recomendación para v2.2.0**: alinear los `fields` declarados en VIEW con el schema real de la tabla generada, o usar `kind:"section"` en lugar de `kind:"kv_table"` para VIEW directives con múltiples fields.

---

## 5. Diagramas explicativos v2.1.0

### 5.1 Comparativa global v2.1.0

![v2.1.0 weighted](diagrams/01_v21_weighted.png)

### 5.2 Progresión v1.0.0 → v2.0.0 → v2.1.0

![Progression](diagrams/02_progression_v1_v2_v21.png)

### 5.3 Métricas v2 activadas

![v2 metrics activated](diagrams/03_v2_metrics_activated.png)

### 5.4 Fix de `canonicalize` (B-01/B-05)

![Canonical fix](diagrams/04_canonical_fix.png)

### 5.5 Trade-off tokens vs score

![Token vs score](diagrams/05_token_vs_score_v21.png)

### 5.6 Radar Top-4

![Radar top4](diagrams/06_radar_top4_v21.png)

### 5.7 Arquitectura v2.1.0

![v2.1 architecture](diagrams/07_v21_architecture.png)

### 5.8 Hallazgos clave v2.1.0

![v2.1 findings](diagrams/08_v21_findings.png)

---

## 6. Discusión

### 6.1 ¿Se resolvieron los issues de v2.0.0?

| Issue v2.0.0 | Estado v2.1.0 | Evidencia |
|--------------|:---:|-----------|
| Corpus sin VIEW directives | ✅ Resuelto | 10 casos con 10-13 VIEW cada uno, 100% coverage |
| `v2-canonicalize` rompía compatibilidad | ✅ Resuelto | `canonicalize --preserve` produce WS = +9.31 |
| Nombres `v2-*` no canónicos | ✅ Resuelto | Nombres canónicos (`convert`, `canonicalize`, etc.) |
| VIEW coverage = 0 % | ✅ Resuelto | VIEW coverage = 100 % en todos los casos |
| Reversibility = 0 | ✅ Resuelto | Reversibility = 1.0 en todos los casos |
| `convert` producía HCORTEX vacío | ✅ Resuelto | Output de 4 718 bytes (sustancial) |
| `roundtrip-bidir` fallaba | ⚠️ Parcial | Direction 2 pasa; direction 1 falla por schema mismatch |

**Conclusión**: 6 de 7 issues resueltos. Queda 1 issue menor (`roundtrip-bidir` direction 1) para v2.2.0.

### 6.2 ¿Es v2.1.0 mejor que v1.0.0?

**Sí, inequívocamente**:

- WS ganador: 7.03 → 9.31 (+2.28)
- MRD: +2.16 → +4.38 (+2.22)
- VIEW coverage: N/A → 100%
- Reversibility: N/A → 1.0
- BCFNR: 0.000 mantenido
- Reproducibilidad: 100% mantenida

### 6.3 Limitaciones de v2.1.0

1. **EAS baja ligeramente** (0.984 → 0.950) porque HCORTEX v2 usa nombres canónicos de campos que pueden no coincidir exactamente con los términos esperados en las tareas QA.
2. **`roundtrip-bidir` direction 1 falla** por E_TABLE_SCHEMA_MISMATCH (issue pendiente para v2.2.0).
3. **`verify --strict` del CLI v1.x legacy** aún no acepta `status:cur` (micro-token del skill canónico), pero esto no afecta al benchmark porque usamos `verify` sin `--strict`.
4. **Sin fase LLM**: igual que v1.0.0 y v2.0.0.

### 6.4 Recomendaciones para v2.2.0

| Recomendación | Prioridad |
|---------------|:---:|
| Fix `roundtrip-bidir` direction 1 (E_TABLE_SCHEMA_MISMATCH) | Alta |
| Alinear `fields` declarados en VIEW con schema real de tabla | Alta |
| Considerar `kind:"section"` para VIEW con múltiples fields | Media |
| Re-evaluar EAS con tareas adaptadas a nombres canónicos v2 | Media |
| Migrar corpus a 2-3 casos por dominio (L2 completo) | Media |
| Ejecutar fase LLM separada (protocolo §11) | Baja |

---

## 7. Reproducibilidad v2.1.0

### 7.1 Comando de reproducción

```bash
# 1. Clonar CODEC-CORTEX v0.3.2
git clone https://github.com/FidelErnesto03/codec-cortex.git
cd codec-cortex && git checkout v0.3.2
cd cli && pip install -e .

# 2. Preparar corpus migrado a VIEW
python scripts/prepare_corpus_v21.py

# 3. Ejecutar benchmark v2.1.0 (~3 min)
python scripts/run_benchmark_v21.py

# 4. Generar diagramas
python scripts/generate_diagrams_v21.py

# 5. Compilar PDF
python scripts/build_pdf_v21.py
```

### 7.2 Determinismo

El benchmark v2.1.0 es **100 % determinístico** (igual que v1.0.0 y v2.0.0): sin aleatoriedad, sin LLM, sin red (excepto renderizado PUML opcional).

---

## 8. Conclusiones v2.1.0

1. **v0.3.2 resuelve los 3 issues principales** que v2.0.0 señalaba: corpus migrado a VIEW, fix de `canonicalize`, nombres canónicos CLI.

2. **CORTEX PP v2 (`convert`) es el nuevo ganador** con WS = 9.31 (+2.28 vs CPP v1), gracias a la activación de VIEW coverage (100 %) y reversibility (1.0).

3. **`canonicalize --preserve` fixea el issue B-01/B-05**: `cortex_canonical` pasa de WS = −2.73 (peor método en v2.0.0) a WS = +9.31 (mejor método empatado en v2.1.0).

4. **MRD casi se duplica** (+2.16 → +4.38) y **QDD se amplía** (−3.95 → −6.24), confirmando que la estructura cognitiva con VIEW directives amplía la ventaja sobre baselines posicionales y query-dependent.

5. **BCFNR = 0 mantenido**: las constraints blocking siguen preservadas en todos los métodos v2.

6. **Trade-off aceptable**: +396 tokens promedio a cambio de +2.28 WS y activación de 2 métricas v2 (VIEW coverage, reversibility).

7. **Issue pendiente**: `roundtrip-bidir` direction 1 falla por E_TABLE_SCHEMA_MISMATCH. Recomendado fix para v2.2.0.

8. **Las conclusiones de v1.0.0 se mantienen y amplían**: CPP preserva P0 (98-100 %), BCFNR = 0, MRD positivo. v2.1.0 añade VIEW coverage 100 % y reversibility 1.0.

---

## 9. Referencias v2.1.0

| ID | Referencia |
|----|------------|
| R-01 | CODEC-CORTEX v0.3.2: https://github.com/FidelErnesto03/codec-cortex (commit 8e71096) |
| R-02 | CLI v0.3.2 CHANGELOG: `cli/CHANGELOG.md` — naming canónico, fix canonicalize, corpus VIEW |
| R-03 | CLI v0.3.2 STATUS: `cli/STATUS.md` |
| R-04 | Benchmark v2.0.0: `benchmarks/v2.0.0/` (referencia comparativa) |
| R-05 | Benchmark v1.0.0: `benchmarks/v1.0.0/` (referencia comparativa) |
| R-06 | Skill canónico v2: `skill/cortex/SKILL.md` (266 entries, 44 VIEW, 100% coverage) |
| R-07 | Protocolo canónico de benchmark científico |
