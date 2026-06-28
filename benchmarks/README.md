# Benchmarks — CODEC-CORTEX

Benchmarks científicos reproducibles que validan las propiedades del protocolo CODEC-CORTEX. Cada versión incluye corpus, métodos, métricas, scripts y resultados versionados. Los artefactos binarios (PNG, SVG, PDF) se regeneran desde las fuentes y se distribuyen como GitHub Release assets.

## Catálogo

| Versión | Fecha | CODEC-CORTEX | CLI | Runs | Métodos | Escenarios | Métricas | Estado |
|---------|-------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| [v1.0.0](./v1.0.0/) | 2026-06-28 | v0.3.0 | v1.1.9 | 4,840 | 11 | 11 | 15 | **current** |
| 0.2 | — | — | — | — | — | — | — | referencia |
| 0.1b | — | — | — | — | — | — | — | referencia |
| 0.1 | — | — | — | — | — | — | — | referencia |

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
