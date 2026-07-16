# Benchmarks — CODEC-CORTEX

Benchmarks científicos reproducibles que validan las propiedades del protocolo CODEC-CORTEX. Cada versión incluye corpus, métodos, métricas, scripts y resultados versionados. Los artefactos binarios (PNG, SVG, PDF) se regeneran desde las fuentes y se distribuyen como GitHub Release assets.

## Catálogo

| Versión | Fecha | CODEC-CORTEX | CLI | Runs | Métodos | Escenarios | Métricas | Estado |
|---------|-------|---|---|---|---|---|---|---|
| [v2.2.2](./v2.2.2/) | 2026-07-02 | v0.4.1 | v0.4.1 | 4,840 | 11 | 11 | 19 | **current** |
| [v2.2.1](./v2.2.1/) | 2026-07-02 | v0.4.1 | v0.4.1 | 4,840 | 11 | 11 | 19 | current |
| [v2.2.0](./v2.2.0/) | 2026-07-02 | v0.3.6 | v0.3.6 | 4,840 | 11 | 11 | 19 | current |
| [v2.1.0](./v2.1.0/) | 2026-06-30 | v0.3.2 | v0.3.2 | 4,840 | 11 | 11 | 19 | current |
| [v2.0.0](./v2.0.0/) | 2026-06-30 | v0.3.1 | v2.4.0 | 4,840 | 11 | 11 | 19 | current |
| [v1.0.0](./v1.0.0/) | 2026-06-28 | v0.3.0 | v1.1.9 | 4,840 | 11 | 11 | 15 | current |
| 0.2 | — | — | — | — | — | — | — | referencia |
| 0.1b | — | — | — | — | — | — | — | referencia |
| 0.1 | — | — | — | — | — | — | — | referencia |

## v2.2.1 — Benchmark científico v2.2.1 (PyPI comparative landscape)

**Hallazgos principales:** Benchmark tangencial comparando codec-cortex contra competidores detectados en PyPI. Evaluación de preservación estructural, latencia, matriz de funcionalidades y radar comparativo sobre el corpus v2.2.0 existente.

| Artefacto | Descripción |
|-----------|-------------|
| [scientific_report_v221.md](./v2.2.1/reports/scientific_report_v221.md) | Informe comparativo PyPI (HCORTEX) |
| [comparative_pypi_results.json](./v2.2.1/runs/comparative_pypi_results.json) | Resultados comparativos |
| [comparative_pypi_benchmark.py](./v2.2.1/scripts/comparative_pypi_benchmark.py) | Script de benchmark comparativo |
| [generate_diagrams_v221.py](./v2.2.1/scripts/generate_diagrams_v221.py) | Generador de diagramas |
| [diagrams/](./v2.2.1/diagrams/) | Fuentes PUML (2 diagramas). PNG se regeneran |

## v2.2.0 — Benchmark científico v2.2 (learning engine v0.1.0 integrado)

**Hallazgos principales:** Primer benchmark con el CODEC-CORTEX Learning Engine v0.1.0 integrado. Evalúa scoring, detección de candidatos, elevación por políticas y rendimiento del índice de aprendizaje sobre 11 escenarios con 4,840 runs.

| Artefacto | Descripción |
|-----------|-------------|
| [scientific_report_v22.md](./v2.2.0/reports/scientific_report_v22.md) | Informe científico v2.2 (HCORTEX) |
| [regression_report_v22.md](./v2.2.0/reports/regression_report_v22.md) | Regresión contra v2.1.0 |
| [claim_matrix_v22.md](./v2.2.0/reports/claim_matrix_v22.md) | Matriz de claims v2.2 |
| [corpus/](./v2.2.0/corpus/) | Corpus L2 con 11 dominios (fintech, ecom, health, iot, robotics, devops, climate, edu, legal, sec) |
| [learning_workspaces/](./v2.2.0/learning_workspaces/) | Workspaces .cortex con brain, policies, index por dominio |
| [scripts/](./v2.2.0/scripts/) | Scripts reproducibles v2.2 (run_benchmark_v22, generate_diagrams_v22, build_pdf_v22) |
| [runs/](./v2.2.0/runs/) | Resultados — 4,840 runs con learning engine |
| [diagrams/](./v2.2.0/diagrams/) | Fuentes PUML (3 diagramas). PNG se regeneran con `generate_diagrams_v22.py` |

## v2.1.0 — Benchmark científico v2.1 (nombres canónicos, VIEW migrado, canonicalize corregido)

**Hallazgos principales:** Tras la migración VIEW del corpus y el fix de `cortex canonicalize`, todos los métodos CODEC-CORTEX reportan VIEW coverage 100%, reversibility True y bidir_equivalence 1.0. `cortex_canonical` se recupera de BCFNR=1.0 a 0.0 (WS de −2.73 a +7.03). Las 4 métricas v2 ahora son informativas (vs valor 0 en v2.0.0).

| Artefacto | Descripción |
|-----------|-------------|
| [scientific_report_v21.md](./v2.1.0/reports/scientific_report_v21.md) | Informe científico v2.1 (HCORTEX) |
| [regression_report_v21.md](./v2.1.0/reports/regression_report_v21.md) | Regresión contra v2.0.0 |
| [claim_matrix_v21.md](./v2.1.0/reports/claim_matrix_v21.md) | Matriz de claims v2.1 |
| [corpus/](./v2.1.0/corpus/) | Corpus L2 con VIEW directives migradas en v0.3.2 |
| [scripts/](./v2.1.0/scripts/) | Scripts reproducibles v2.1 (prepare_corpus_v21, run_benchmark_v21, generate_diagrams_v21, build_pdf_v21) |
| [runs/](./v2.1.0/runs/) | Resultados — 4,840 runs con métodos canónicos |
| [diagrams/](./v2.1.0/diagrams/) | Fuentes PUML (2 diagramas). PNG se regeneran con `generate_diagrams_v21.py` |
| [comparatives/](./v2.1.0/comparatives/) | Tablas comparativas v1 vs v2 vs v2.1 |

**Nuevo en v2.1.0:** Métodos con nombres canónicos (`cortex_priority_pack`, `cortex_canonical`). VIEW coverage activa (100%). `cortex_canonical` corregido (BCFNR 1.0→0.0). Corpus migrado en v0.3.2 con 12+ VIEW directives por artefacto.

## v2.0.0 — Benchmark científico v2 (núcleo bidireccional)

**v0.3.2 — Cambios aplicados sobre el catálogo v2.0.0:**

- **Corpus migrado a VIEW directives**: los 10 archivos `.cortex` en `corpus/source/` ahora incluyen una sección `$N: VIEWS` con 10-13 VIEW directives cada uno (cubriendo IDN, DOM, CNST, FCS, OBJ, WRK, STP, NXT, RSK, AUD, CLAIM, LIM según corresponda). Esto resuelve los issues B-02, B-03, B-04, B-06 del benchmark v2.0.0.
- **Renombramiento de métodos** (canonical naming): `cortex_v2_priority_pack` → `cortex_priority_pack`; `cortex_v2_canonical` → `cortex_canonical`. Los nombres antiguos se conservan como `deprecated_aliases` en `method_registry.json` para trazabilidad.
- **Fix de métricas para `cortex_canonical`**: tras el fix VIEW-aware de `cortex canonicalize` (issues B-01/B-05), las métricas reportadas para `cortex_canonical` reflejan el comportamiento corregido: BCFNR=0.0, WS=+7.03 (antes BCFNR=1.0, WS=−2.73).
- **Hashes actualizados**: `corpus/normalized/hashes.json` ahora refleja los nuevos SHA256 de los `.cortex` migrados.

**Hallazgos principales:** CORTEX Priority Pack y CORTEX Canonical mantienen 100% P0 survival (BCFNR=0, UCFPR=0). VIEW coverage 100% en todo el corpus (tras migración v0.3.2). Reversibilidad y bidir_equivalence perfectas en artefactos con VIEW. 4 métricas v2: VIEW_coverage, reversibility, bidir_equivalence, loss_count.

| Artefacto | Descripción |
|-----------|-------------|
| [scientific_report_v2.md](./v2.0.0/reports/scientific_report_v2.md) | Informe científico v2 (HCORTEX) |
| [regression_report_v2.md](./v2.0.0/reports/regression_report_v2.md) | Regresión contra v1.0.0 |
| [claim_matrix_v2.md](./v2.0.0/reports/claim_matrix_v2.md) | Matriz de claims v2 |
| [corpus/](./v2.0.0/corpus/) | Corpus L2 extendido — 10 dominios × 5 formatos; `.cortex` migrados a VIEW directives en v0.3.2 |
| [scripts/](./v2.0.0/scripts/) | Scripts reproducibles v2 (run_benchmark_v2, build_pdf_v2, generate_diagrams_v2, update_corpus_v2) |
| [runs/](./v2.0.0/runs/) | Resultados — 4,840 runs + v1_vs_v2_comparison.json; method_ids actualizados a nombres canónicos en v0.3.2 |
| [diagrams/](./v2.0.0/diagrams/) | Fuentes PUML (2 diagramas). PNG se regeneran con `generate_diagrams_v2.py` |
| [comparatives/](./v2.0.0/comparatives/) | Tablas comparativas v1 vs v2 |

**Métodos canónicos (v0.3.2, renombrados):** `cortex_priority_pack`, `cortex_canonical`. Alias deprecados: `cortex_v2_priority_pack`, `cortex_v2_canonical`.
**Nuevas métricas v2:** `VIEW_coverage`, `reversibility`, `bidir_equivalence`, `loss_count`.
**Comandos CLI usados (nombres canónicos v0.3.2):** `cortex convert`, `cortex verify-view`, `cortex roundtrip-bidir`, `cortex canonicalize`, `cortex explain-loss`. Alias `v2-*` aceptados con `WARNING`.

## v1.0.0 — Benchmark científico formal

**Hallazgos principales:** CORTEX Priority Pack preserva 100% de entradas P0 (BCFNR=0, UCFPR=0). Supera baselines posicionales en MRD=+2.16. Métodos query-dependent no superan a la estructura cognitiva (QDD=−3.95).

| Artefacto | Descripción |
|-----------|-------------|
| [scientific_report.md](./v1.0.0/reports/scientific_report.md) | Informe científico completo (HCORTEX) |
| [corpus/](./v1.0.0/corpus/) | Corpus L2-multidominio — 10 dominios × 5 formatos = 50 artefactos |
| [scripts/](./v1.0.0/scripts/) | Scripts Python reproducibles (build_corpus, run_benchmark, generate_diagrams, build_pdf, validate_reproducibility) |
| [runs/](./v1.0.0/runs/) | Resultados — 4,840 runs en CSV/JSON |
| [diagrams/](./v1.0.0/diagrams/) | Fuentes PUML (7 diagramas). PNG/SVG se regeneran con `generate_diagrams.py` |

**Distribución:** El tarball completo (incluyendo PDF y PNGs) se publica como GitHub Release asset. En el repositorio solo residen las fuentes versionables (scripts, corpus, PUML, datos).

## Metodología

La metodología formal está definida en [`docs/specs/benchmark-methodology.md`](../docs/specs/benchmark-methodology.md).
