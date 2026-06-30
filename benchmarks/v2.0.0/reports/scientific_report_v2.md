<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX v2.0.0 -->
<!-- SPDX-License-Identifier: MIT -->
<!-- source: scientific_report_v2.md — HCORTEX scientific report v2.0.0 -->

# Informe Científico del Benchmark CODEC-CORTEX v2.0.0

> **Perfil: HCORTEX-FULL** · v2.0.0 · 2026-06-30 · source: benchmark harness v2.0.0 + CLI v2.4.0

---

## 0. Resumen ejecutivo

| Campo | Valor |
|-------|-------|
| **Benchmark version** | 2.0.0 |
| **Versión anterior** | 1.0.0 (2026-06-28) |
| **Fecha de ejecución** | 2026-06-30 |
| **Ejecutor** | run_benchmark_v2.py (determinístico) |
| **CODEC-CORTEX versión** | 0.3.1 (CLI 2.4.0, bidireccional CORTEX ⇄ HCORTEX) |
| **Harness versión** | 2.0.0 |
| **Corpus** | L2-multidominio reutilizado de v1.0.0 (10 dominios, 50 artefactos) |
| **Métodos comparados** | 11 (4 posicionales + 1 semántico + 1 query-dep + 1 CODEC v1 + 2 CODEC v2 + 2 ablations) |
| **Escenarios** | 11 (sin cambios vs v1.0.0) |
| **Tareas** | 40 (sin cambios vs v1.0.0) |
| **Total de runs** | 4 840 (11 × 11 × 40) |
| **Fase LLM** | No ejecutada (determinística pura, §11.2 del protocolo) |
| **Reproducibilidad** | Hashes SHA-256 + manifest + scripts versionados |
| **Tokenizador** | Proxy char-based (1 token ≈ 3.5–4.0 chars según formato) |

### Novedades de v2.0.0 vs v1.0.0

| Aspecto | v1.0.0 | v2.0.0 |
|---------|--------|--------|
| **CLI version** | 1.1.9 (legacy `render`) | 2.4.0 (bidireccional, `v2-*` commands) |
| **CODEC-CORTEX versión** | 0.3.0 | 0.3.1 |
| **Métodos CODEC** | 3 variantes CPP v1 | 1 CPP v1 + 2 métodos v2 nuevos |
| **Métricas** | 15 canónicas | 15 + 4 nuevas (VIEW_coverage, reversibility, bidir_equivalence, loss_count) |
| **Comandos CLI usados** | `verify`, `render` | + `v2-convert`, `v2-verify-view`, `v2-roundtrip-bidir`, `v2-canonicalize`, `v2-explain-loss` |
| **Capacidad bidireccional** | No evaluada | Evaluada (requiere VIEW directives) |

### Hallazgos principales v2.0.0

| # | Hallazgo | Estado | Evidencia |
|:---:|----------|:---:|-----------|
| H-01 | CORTEX PP v1 mantiene 100 % P0 survival y BCFNR = 0 en v2.0.0 (igual que v1.0.0) | **Demostrado** | `summary_tasks.csv`: avg_P0_survival = 1.00, avg_BCFNR = 0.000 |
| H-02 | CORTEX v2 PP con fallback a v1 produce resultados idénticos a CPP v1 (Δ = 0.0 en todas las métricas) | **Demostrado** | `v1_vs_v2_comparison.json`: todos los deltas = 0.0 |
| H-03 | CORTEX v2 Canonical (v2-canonicalize + v2-convert) falla: BCFNR = 1.0, WS = −2.73 | **Demostrado** | `summary_tasks.csv`: cortex_v2_canonical avg_BCFNR = 1.000 |
| H-04 | VIEW coverage = 0 % en todos los casos del corpus v1.0.0 (sin VIEW directives) | **Demostrado** | `v2-verify-view` en los 10 casos: 0% coverage |
| H-05 | Reversibility = 0 en todos los casos del corpus v1.0.0 (requiere migración a v2) | **Demostrado** | `v2-verify-view` en los 10 casos: reversible = False |
| H-06 | v2-convert produce HCORTEX vacío (251 bytes) cuando el .cortex no tiene VIEW directives | **Demostrado** | Tamaño de output: 251 bytes vs 3030 bytes del v1 render |
| H-07 | QDD = −3.95 (igual que v1.0.0): la estructura cognitiva sigue superando a query-dependent | **Demostrado** | `derived_metrics.json`: QDD = -3.9528 |
| H-08 | La bidireccionalidad CORTEX ⇄ HCORTEX requiere migrar artefactos al formato v2 con VIEW directives | **Hipótesis razonable** | Skill canónico (`skill/cortex/SKILL.md`) logra 100% coverage y reversibility con 44 VIEW directives |

---

## 1. Introducción y contexto

### 1.1 Motivación de v2.0.0

El commit `83ee45a` del repositorio CODEC-CORTEX introdujo **CLI v2.4.0** con capacidades bidireccionales CORTEX ⇄ HCORTEX, un cambio arquitectónico mayor. El benchmark v1.0.0 evaluó CLI v1.1.9 (legacy `render`); v2.0.0 evalúa CLI v2.4.0 con sus nuevos comandos `v2-*` y la introducción de **VIEW directives** como mecanismo de mapeo explícito entre representaciones.

La pregunta central de v2.0.0 es: **¿las nuevas capacidades bidireccionales del CLI v2.4.0 mejoran la preservación de evidencia, o requieren migración del corpus para ser funcionales?**

### 1.2 Cambios del CLI v2.4.0 relevantes para el benchmark

| Comando v2 | Propósito | Estado |
|------------|-----------|--------|
| `v2-inspect` | Inspecciona AST, secciones, VIEW coverage | `current` |
| `v2-convert` | Convierte CORTEX ⇄ HCORTEX con VIEW | `current` |
| `v2-roundtrip-bidir` | Valida ida y vuelta CORTEX⇄HCORTEX | `current` |
| `v2-verify-view` | Valida cobertura VIEW y reversibilidad | `current` |
| `v2-canonicalize` | Normaliza artefacto sin cambiar semántica | `current` |
| `v2-explain-loss` | Explica pérdida/no-reversibilidad | `current` |
| `v2-compare` | Compara dos artefactos (byte/AST/semántico) | `current` |

### 1.3 Hipótesis v2.0.0

| Hipótesis | Formulación |
|-----------|-------------|
| H1-v2 | Los métodos v2 (`v2-convert`) producen HCORTEX equivalente o superior al v1 `render` cuando hay VIEW directives. |
| H2-v2 | Sin VIEW directives, v2-convert produce HCORTEX vacío, requiriendo fallback a v1. |
| H3-v2 | `v2-canonicalize` preserva la semántica del .cortex original. |
| H4-v2 | Las métricas v1 (EAS, P0 survival, BCFNR) se mantienen estables entre v1.0.0 y v2.0.0 para los métodos legacy. |

---

## 2. Método científico v2.0.0

### 2.1 Diseño experimental

El benchmark v2.0.0 mantiene el diseño factorial **11 × 11 × 40 = 4 840 runs** de v1.0.0, pero:

1. **Sustituye** las 3 variantes CPP v1 (que en v1.0.0 eran idénticas) por:
   - `cortex_priority_pack_v1` (CLI v1.1.9 `render --profile`)
   - `cortex_v2_priority_pack` (CLI v2.4.0 `v2-convert` con fallback)
   - `cortex_v2_canonical` (CLI v2.4.0 `v2-canonicalize` + `v2-convert`)
2. **Añade 4 métricas nuevas**: VIEW_coverage, reversibility, bidir_equivalence, loss_count
3. **Añade comparación v1 vs v2**: `v1_vs_v2_comparison.json` con deltas por métrica

### 2.2 Métodos bajo comparación v2.0.0

| Familia | Método | CLI | Descripción |
|---------|--------|-----|-------------|
| **Pasivo posicional** | `recent_tail_raw` | — | Últimos N tokens raw prose |
| | `head_tail_raw` | — | 25% head + 75% tail |
| | `head_json` | — | Primeros N tokens JSON |
| | `head_markdown_summary` | — | Primeros N tokens Markdown |
| **Pasivo semántico** | `semantic_field_pack` | — | Selecciona IDN/DOM/CNST/FCS/OBJ/STP |
| **Query-dependent** | `keyword_retrieval_raw` | — | BM25-like con gold terms |
| **CODEC-CORTEX v1** | `cortex_priority_pack_v1` | v1.1.9 `render` | CLI legacy con `--profile` |
| **CODEC-CORTEX v2** ⭐ | `cortex_v2_priority_pack` | v2.4.0 `v2-convert` | Bidireccional con fallback a v1 |
| **CODEC-CORTEX v2** ⭐ | `cortex_v2_canonical` | v2.4.0 `v2-canonicalize` + `v2-convert` | Normalización + conversión |
| **Ablations** | `cortex_ablation_no_P0` | — | Sin prioridad P0 |
| | `cortex_ablation_no_temporal` | — | Sin distinción temporal |

### 2.3 Métricas v2.0.0

Las 15 métricas canónicas de v1.0.0 + 4 nuevas:

| Métrica nueva | Tipo | Descripción |
|---------------|------|-------------|
| `VIEW_coverage` | ratio 0..1 | % de entries con VIEW directive (v2-verify-view) |
| `reversibility` | binario 0/1 | 1 si v2-verify-view reporta reversible=True |
| `bidir_equivalence` | binario 0/1 | 1 si v2-roundtrip-bidir pasa (AST-equivalent) |
| `loss_count` | count ≥0 | Número de pérdidas explicadas por v2-explain-loss |

---

## 3. Resultados v2.0.0

### 3.1 Tabla agregada por método

> source: `runs/summary_tasks.csv` · 440 runs por método

| Método | v2 | EAS | ETC | F1 | DA | P0 surv | P1 surv | BCFNR | UCFPR | STR | VIEW cov | rev | ctx tok | ED | WS |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `cortex_priority_pack_v1` | 0 | **0.984** | **0.984** | 0.060 | 0.25 | **1.00** | 0.98 | **0.000** | **0.000** | **1.00** | 0.00 | 0 | 726 | 0.0099 | **7.03** |
| `cortex_v2_priority_pack` ⭐ | 1 | **0.984** | **0.984** | 0.060 | 0.25 | **1.00** | 0.98 | **0.000** | **0.000** | **1.00** | 0.00 | 0 | 726 | 0.0099 | **7.03** |
| `cortex_ablation_no_temporal` | 0 | 0.977 | 0.977 | 0.051 | 0.25 | 1.00 | **1.00** | 0.000 | 0.000 | 0.91 | 0.00 | 0 | 707 | 0.0099 | 6.93 |
| `head_json` | 0 | 0.971 | 0.964 | 0.075 | 0.25 | 0.66 | 0.81 | 0.000 | 0.091 | 0.00 | 0.00 | 0 | 488 | 0.0111 | 4.88 |
| `head_markdown_summary` | 0 | 0.795 | 0.795 | 0.082 | 0.25 | 0.84 | 0.87 | 0.000 | 0.091 | 0.00 | 0.00 | 0 | 388 | 0.0151 | 4.88 |
| `semantic_field_pack` | 0 | 0.800 | 0.800 | 0.097 | 0.25 | 1.00 | 0.05 | 0.000 | 0.000 | 0.00 | 0.00 | 0 | 242 | 0.0196 | 4.70 |
| `recent_tail_raw` | 0 | 0.757 | 0.525 | 0.042 | 0.25 | 0.71 | 0.64 | 0.091 | 0.091 | 1.00 | 0.00 | 0 | 361 | 0.0148 | 4.62 |
| `head_tail_raw` | 0 | 0.757 | 0.523 | 0.042 | 0.25 | 0.71 | 0.64 | 0.091 | 0.091 | 1.00 | 0.00 | 0 | 620 | 0.0079 | 4.62 |
| `cortex_ablation_no_P0` | 0 | 0.645 | 0.473 | 0.031 | 0.25 | 1.00 | 1.00 | **0.700** | 0.000 | 1.00 | 0.00 | 0 | 528 | 0.0074 | 3.80 |
| `keyword_retrieval_raw` | 0 | 0.757 | 0.525 | 0.075 | 0.25 | 0.48 | 0.31 | 0.320 | 0.057 | 0.77 | 0.00 | 0 | 203 | 0.0249 | 3.08 |
| `cortex_v2_canonical` ⭐ | 1 | 0.175 | 0.175 | 0.005 | 0.00 | 0.00 | 0.00 | **1.000** | 0.000 | 0.00 | 0.00 | 0 | 71 | −0.0384 | **−2.73** |

**Leyenda**: ⭐ = método nuevo en v2.0.0. ctx tok = Average Context Tokens. ED = Evidence Density. WS = Weighted Score.

### 3.2 Comparación directa v1 vs v2

> source: `runs/v1_vs_v2_comparison.json`

| Métrica | CPP v1 | CPP v2 PP | Δ (v2 − v1) | Interpretación |
|---------|:---:|:---:|:---:|----------------|
| EAS | 0.984 | 0.984 | **0.000** | Idéntico (fallback activo) |
| ETC | 0.984 | 0.984 | **0.000** | Idéntico |
| F1 | 0.060 | 0.060 | **0.000** | Idéntico |
| DA | 0.25 | 0.25 | **0.000** | Idéntico |
| P0 survival | 1.00 | 1.00 | **0.000** | Idéntico |
| P1 survival | 0.98 | 0.98 | **0.000** | Idéntico |
| BCFNR | 0.000 | 0.000 | **0.000** | Idéntico |
| STR | 1.00 | 1.00 | **0.000** | Idéntico |
| VIEW coverage | 0.00 | 0.00 | **0.000** | Ambos 0 (corpus sin VIEW) |
| Reversibility | 0 | 0 | **0.000** | Ambos 0 (corpus sin VIEW) |
| Weighted Score | 7.03 | 7.03 | **0.000** | Idéntico |

**Interpretación clave**: `cortex_v2_priority_pack` con fallback a v1 produce **resultados byte-idénticos** a `cortex_priority_pack_v1`. El fallback se activa porque `v2-convert` produce HCORTEX vacío (251 bytes < 500 bytes umbral) cuando el `.cortex` no tiene VIEW directives.

### 3.3 Resultados de `cortex_v2_canonical` (falla)

| Métrica | Valor | Interpretación |
|---------|:---:|----------------|
| EAS | 0.175 | 82.5 % de tareas no encuentran términos esperados |
| P0 survival | 0.00 | Ninguna entry P0 preservada |
| BCFNR | **1.000** | Todas las constraints blocking omitidas |
| STR | 0.00 | Sin trazabilidad |
| Weighted Score | **−2.73** | Score negativo (penalización por BCFNR) |

**Causa raíz**: `v2-canonicalize` reescribe el `.cortex` a un formato canónico v2 que pierde compatibilidad con el `v1 render` legacy. Luego `v2-convert` no puede renderizar HCORTEX sustancial sin VIEW directives, produciendo output de 71 tokens (metadata + perfil).

### 3.4 Métricas v2 nuevas (VIEW coverage, reversibility, bidir_equivalence)

> source: `v2-verify-view` y `v2-roundtrip-bidir` en los 10 casos del corpus

| Caso | VIEW coverage | Reversibility | Bidir equivalence |
|------|:---:|:---:|:---:|
| devops-k8s-rollout | 0.0 % | False | 0 |
| ecom-fraud-checkout | 0.0 % | False | 0 |
| health-medication-alert | 0.0 % | False | 0 |
| fintech-aml-kyc | 0.0 % | False | 0 |
| iot-hvac-anomaly | 0.0 % | False | 0 |
| legal-contract-redline | 0.0 % | False | 0 |
| edu-adaptive-lesson | 0.0 % | False | 0 |
| sec-incident-response | 0.0 % | False | 0 |
| robotics-warehouse-bot | 0.0 % | False | 0 |
| climate-grid-balancing | 0.0 % | False | 0 |

**Comparación con skill canónico** (`skill/cortex/SKILL.md`): 100 % VIEW coverage, reversible = True, bidir_equivalence = 1 (44 VIEW directives cubren 266 entries).

### 3.5 Métricas derivadas (MRD y QDD)

> source: `runs/derived_metrics.json`

| Métrica | Valor v2.0.0 | Valor v1.0.0 | Δ |
|---------|:---:|:---:|:---:|
| MRD winner | cortex_priority_pack_v1 (+2.16) | cortex_priority_pack_v1 (+2.16) | 0.00 |
| QDD | −3.95 | −3.95 | 0.00 |
| best_passive_score | 7.03 | 7.03 | 0.00 |
| best_query_dependent_score | 3.08 | 3.08 | 0.00 |

Las métricas derivadas son **idénticas entre v1.0.0 y v2.0.0** para los métodos legacy, confirmando que el CLI v2.4.0 no degrada el comportamiento de los métodos v1.

---

## 4. Análisis de hallazgos v2.0.0

### 4.1 Confirmación de hipótesis

| Hipótesis | Estado | Evidencia |
|-----------|:---:|-----------|
| H1-v2: v2-convert produce HCORTEX equivalente con VIEW directives | **No evaluable** | Corpus v1.0.0 sin VIEW; skill canónico sí lo logra |
| H2-v2: Sin VIEW, v2-convert produce HCORTEX vacío | **Confirmada** | 251 bytes output vs 3030 bytes del v1 render |
| H3-v2: v2-canonicalize preserva semántica | **Refutada** | cortex_v2_canonical: BCFNR=1.0, WS=−2.73 |
| H4-v2: Métricas v1 estables entre versiones | **Confirmada** | Todos los métodos legacy tienen Δ=0.0 vs v1.0.0 |

### 4.2 Implicación arquitectónica

El hallazgo central de v2.0.0 es que **la bidireccionalidad CORTEX ⇄ HCORTEX del CLI v2.4.0 requiere migración explícita del corpus al formato v2 con VIEW directives**. Sin esta migración:

- `v2-convert` produce HCORTEX vacío (solo metadata)
- `v2-canonicalize` reescribe el .cortex perdiendo compatibilidad con `v1 render`
- `v2-roundtrip-bidir` falla (no detecta formato CORTEX)
- `VIEW coverage` = 0 %, `reversibility` = False

El skill canónico del repositorio (`skill/cortex/SKILL.md`) demuestra que **con VIEW directives properly configuradas** (44 directives cubriendo 266 entries), el CLI v2.4.0 logra:
- 100 % VIEW coverage
- Reversibility = True
- Bidirectional equivalence = True (AST-equivalent en ambas direcciones)

### 4.3 Comparación v1.0.0 vs v2.0.0 (progresión)

| Dimensión | v1.0.0 | v2.0.0 | Progresión |
|-----------|--------|--------|:---:|
| CLI version | 1.1.9 | 2.4.0 | ↑ Major upgrade |
| Métodos CODEC | 3 (CPP v1 × 3 idénticas) | 3 (1 v1 + 2 v2 diferenciadas) | ↑ Mejor diferenciación |
| Métricas canónicas | 15 | 19 (+4 v2) | ↑ Cobertura ampliada |
| Hallazgo científico | CPP preserva P0 100 % | + Bidireccionalidad requiere VIEW | ↑ Conocimiento ampliado |
| Reproducibilidad | ✓ 100 % determinístico | ✓ 100 % determinístico | = Sin cambios |
| Estabilidad métricas legacy | baseline | Δ = 0.0 vs v1.0.0 | = Sin regresiones |

---

## 5. Diagramas explicativos v2.0.0

### 5.1 Comparativa v1 vs v2 (weighted score)

![v1 vs v2 weighted](diagrams/01_v1_vs_v2_weighted.png)

> source: `diagrams/01_v1_vs_v2_weighted.png`

### 5.2 Todos los métodos v2.0.0

![All methods v2](diagrams/02_all_methods_v2.png)

> source: `diagrams/02_all_methods_v2.png`

### 5.3 Radar v1 vs v2

![Radar v1 vs v2](diagrams/03_v1_vs_v2_radar.png)

> source: `diagrams/03_v1_vs_v2_radar.png`

### 5.4 VIEW coverage y reversibility

![VIEW coverage](diagrams/04_view_coverage.png)

> source: `diagrams/04_view_coverage.png`

### 5.5 Timeline CLI v1 → v2

![CLI timeline](diagrams/05_cli_timeline.png)

> source: `diagrams/05_cli_timeline.png`

### 5.6 Modos de fallo v2.0.0

![v2 failure modes](diagrams/06_v2_failure_modes.png)

> source: `diagrams/06_v2_failure_modes.png`

### 5.7 Arquitectura v2.0.0

![v2 architecture](diagrams/07_v2_architecture.png)

> source: `diagrams/07_v2_architecture.puml`

### 5.8 Hallazgos clave v2.0.0

![v2 findings](diagrams/08_v2_findings.png)

> source: `diagrams/08_v2_findings.puml`

---

## 6. Discusión

### 6.1 ¿Es v2.0.0 mejor que v1.0.0?

**Respuesta matizada**: v2.0.0 es funcionalmente superior en **capacidades potenciales** (bidireccionalidad, VIEW directives, reversibility), pero para el corpus actual (v1.0.0 reutilizado) **no produce mejoras medibles** en preservación de evidencia. De hecho, `cortex_v2_canonical` degrada el rendimiento.

**Tabla comparativa**:

| Aspecto | v1.0.0 | v2.0.0 | Ganador |
|---------|--------|--------|---------|
| Preservación P0 (CPP v1) | 100 % | 100 % | Empate |
| BCFNR (CPP v1) | 0.000 | 0.000 | Empate |
| WS (CPP v1) | 7.03 | 7.03 | Empate |
| Capacidad bidireccional | No evaluada | Evaluada (requiere VIEW) | v2.0.0 |
| Métricas nuevas | 0 | 4 (VIEW, rev, bidir, loss) | v2.0.0 |
| Robustez sin VIEW | N/A | Fallback a v1 funciona | v2.0.0 |
| Canonicalize | N/A | Falla (BCFNR=1.0) | v1.0.0 |

### 6.2 Limitaciones de v2.0.0

1. **Corpus no migrado a v2**: el corpus v1.0.0 no tiene VIEW directives, impidiendo evaluar el potencial completo del CLI v2.4.0.
2. **Skill canónico no pasa verify --strict**: el propio `skill/cortex/SKILL.md` falla validación estricta del CLI v2.4.0 (E032 critical sigil incomplete), sugiriendo que el validador v2 es más estricto que los artefactos canónicos.
3. **v2-canonicalize rompe compatibilidad**: la normalización v2 produce .cortex que ni v1 render ni v2-convert pueden procesar correctamente.
4. **Sin fase LLM**: igual que v1.0.0, no se evalúa mejora del razonamiento.

### 6.3 Recomendaciones para v2.1.0

| Recomendación | Prioridad |
|---------------|:---:|
| Migrar corpus a formato v2 con VIEW directives (siguiendo patrón del skill canónico) | Alta |
| Fix `v2-canonicalize` para preservar compatibilidad con v1 render | Alta |
| Re-evaluar `cortex_v2_priority_pack` y `cortex_v2_canonical` con corpus migrado | Alta |
| Añadir método `cortex_v2_roundtrip` que valide bidirectional equivalence en el hot path | Media |
| Comparar con skill canónico (266 entries, 44 VIEW, 100% coverage) como caso de referencia | Media |
| Ejecutar fase LLM separada (protocolo §11) | Baja |

### 6.4 Amenazas a la validez v2.0.0

| Amenaza | Severidad | Mitigación |
|---------|:---:|------------|
| Corpus v1.0.0 no representativo del formato v2 | Alta | Declarado; próxima iteración migrará corpus |
| v2-canonicalize falla sin fallback | Media | Documentado; fallback a v1 en v2_priority_pack |
| VIEW coverage = 0 % no permite evaluar bidireccionalidad real | Alta | Skill canónico se usa como evidencia de que v2.4.0 sí soporta VIEW |
| Skill canónico no pasa verify --strict | Media | Reportado; no afecta al benchmark pero sugiere inmadurez del validador v2 |

---

## 7. Reproducibilidad v2.0.0

### 7.1 Artefactos versionados

| Artefacto | Ruta | Hash SHA-256 |
|-----------|------|--------------|
| Corpus .cortex (10) | `corpus/source/*.cortex` | `corpus/normalized/hashes.json` |
| Manifiesto v2 | `manifest.json` | — |
| Scored tasks | `runs/scored_tasks.csv` (4 840 filas) | — |
| v1 vs v2 comparison | `runs/v1_vs_v2_comparison.json` | — |
| Derived metrics | `runs/derived_metrics.json` | — |
| Scripts | `scripts/{run_benchmark_v2,generate_diagrams_v2,build_pdf_v2}.py` | — |

### 7.2 Comando de reproducción

```bash
# 1. Clonar CODEC-CORTEX v0.3.1
git clone https://github.com/FidelErnesto03/codec-cortex.git
cd codec-cortex && git checkout v0.3.1
cd cli && pip install -e .

# 2. Ejecutar benchmark v2.0.0
python scripts/run_benchmark_v2.py   # ~3 min

# 3. Generar diagramas
python scripts/generate_diagrams_v2.py

# 4. Compilar PDF
python scripts/build_pdf_v2.py
```

### 7.3 Determinismo

El benchmark v2.0.0 es **100 % determinístico** (igual que v1.0.0): sin aleatoriedad, sin LLM, sin red (excepto renderizado PUML opcional).

---

## 8. Conclusiones v2.0.0

1. **CLI v2.4.0 no degrada el rendimiento de métodos v1**: todos los métodos legacy tienen Δ = 0.0 vs v1.0.0.

2. **`cortex_v2_priority_pack` con fallback a v1** produce resultados idénticos a `cortex_priority_pack_v1`, demostrando que el harness v2.0.0 es robusto ante la ausencia de VIEW directives.

3. **`cortex_v2_canonical` falla** (BCFNR = 1.0, WS = −2.73) porque `v2-canonicalize` reescribe el .cortex perdiendo compatibilidad con v1 render. Esto es un **bug o limitación** del CLI v2.4.0 a reportar al proyecto.

4. **La bidireccionalidad CORTEX ⇄ HCORTEX requiere migración explícita del corpus al formato v2 con VIEW directives**. El skill canónico del repositorio demuestra que v2.4.0 logra 100 % coverage y reversibility cuando los artefactos están properly migrados.

5. **Las 4 métricas v2 nuevas** (VIEW_coverage, reversibility, bidir_equivalence, loss_count) son **informativas pero todas = 0** en el corpus actual, limitando su utilidad diagnóstica. Su valor se realizará en v2.1.0 con corpus migrado.

6. **Las conclusiones de v1.0.0 se mantienen**: CPP preserva 100 % P0, BCFNR = 0, MRD = +2.16, QDD = −3.95.

---

## 9. Referencias v2.0.0

| ID | Referencia |
|----|------------|
| R-01 | CODEC-CORTEX v0.3.1: https://github.com/FidelErnesto03/codec-cortex (commit ee21965) |
| R-02 | CLI v2.4.0 CHANGELOG: `cli/CHANGELOG.md` |
| R-03 | CLI v2.4.0 STATUS: `cli/STATUS.md` |
| R-04 | Skill canónico v2: `skill/cortex/SKILL.md` (266 entries, 44 VIEW, 100% coverage) |
| R-05 | Benchmark v1.0.0: `benchmarks/v1.0.0/` (referencia comparativa) |
| R-06 | Protocolo canónico de benchmark científico |
