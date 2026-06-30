# Benchmarks — CODEC-CORTEX

Benchmarks científicos reproducibles que validan las propiedades del protocolo CODEC-CORTEX. Cada versión incluye corpus, métodos, métricas, scripts y resultados versionados. Los artefactos binarios (PNG, SVG, PDF) se regeneran desde las fuentes y se distribuyen como GitHub Release assets.

## Catálogo

|| Versión | Fecha | CODEC-CORTEX | CLI | Runs | Métodos | Escenarios | Métricas | Estado |
||---------|-------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|| [v2.0.0](./v2.0.0/) | 2026-06-30 | v0.3.1 | v2.4.0 | 4,840 | 11 | 11 | 19 | **current** |
|| [v1.0.0](./v1.0.0/) | 2026-06-28 | v0.3.0 | v1.1.9 | 4,840 | 11 | 11 | 15 | current |
|| 0.2 | — | — | — | — | — | — | — | referencia |
|| 0.1b | — | — | — | — | — | — | — | referencia |
|| 0.1 | — | — | — | — | — | — | — | referencia |

## v2.0.0 — Benchmark científico v2 (núcleo bidireccional)

**Hallazgos principales:** CORTEX v2 Priority Pack y v2 Canonical mantienen 100% P0 survival (BCFNR=0, UCFPR=0). VIEW coverage 100% en todo el corpus. Reversibilidad y bidir_equivalence perfectas. 4 nuevas métricas v2: VIEW_coverage, reversibility, bidir_equivalence, loss_count.

| Artefacto | Descripción |
|-----------|-------------|
| [scientific_report_v2.md](./v2.0.0/reports/scientific_report_v2.md) | Informe científico v2 (HCORTEX) |
| [regression_report_v2.md](./v2.0.0/reports/regression_report_v2.md) | Regresión contra v1.0.0 |
| [claim_matrix_v2.md](./v2.0.0/reports/claim_matrix_v2.md) | Matriz de claims v2 |
| [corpus/](./v2.0.0/corpus/) | Corpus L2 extendido — 10 dominios × 5 formatos, incluye source_v1_backup |
| [scripts/](./v2.0.0/scripts/) | Scripts reproducibles v2 (run_benchmark_v2, build_pdf_v2, generate_diagrams_v2, update_corpus_v2) |
| [runs/](./v2.0.0/runs/) | Resultados — 4,840 runs + v1_vs_v2_comparison.json |
| [diagrams/](./v2.0.0/diagrams/) | Fuentes PUML (2 diagramas). PNG se regeneran con `generate_diagrams_v2.py` |
| [comparatives/](./v2.0.0/comparatives/) | Tablas comparativas v1 vs v2 |

**Nuevos métodos v2:** `cortex_v2_priority_pack`, `cortex_v2_canonical`.
**Nuevas métricas v2:** `VIEW_coverage`, `reversibility`, `bidir_equivalence`, `loss_count`.
**Comandos CLI usados:** `v2-convert`, `v2-verify-view`, `v2-roundtrip-bidir`, `v2-canonicalize`, `v2-explain-loss`.

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
