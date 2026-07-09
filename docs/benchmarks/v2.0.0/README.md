# Benchmark Científico CODEC-CORTEX v2.0.0

> **Informe científico completo y reproducible** · 2026-06-30 · MIT License
> Evaluación de preservación de evidencia con CLI v2.4.0 (bidireccional CORTEX ⇄ HCORTEX)

## 🆕 Novedades v2.0.0 vs v1.0.0

| Aspecto | v1.0.0 | v2.0.0 |
|---------|--------|--------|
| CLI version | 1.1.9 (legacy `render`) | **2.4.0** (bidireccional, `v2-*` commands) |
| CODEC-CORTEX versión | 0.3.0 | **0.3.1** |
| Métodos CODEC | 3 variantes CPP v1 (idénticas) | **1 v1 + 2 v2 nuevos diferenciados** |
| Métricas | 15 canónicas | **19** (+4 v2 nuevas: VIEW, rev, bidir, loss) |
| Capacidad bidireccional | No evaluada | **Evaluada** (requiere VIEW directives) |

## 📦 Contenido del paquete

```
benchmark-cortex-v2/
├── Benchmark_CODEC_CORTEX_v2.0.pdf      ← Informe maestro (23 págs, 847 KB)
├── manifest.json                         ← Versión 2.0.0, CLI 2.4.0
├── README.md                             ← Este archivo
│
├── corpus/                               ← Corpus L2 (reutilizado de v1.0.0)
│   ├── source/                           ← 10 .cortex + 40 alternativas
│   ├── source_v1_backup/                 ← Backups originales
│   └── normalized/hashes.json            ← SHA-256
│
├── methods/method_registry.json          ← 11 métodos (1 v1 + 2 v2 + 8 legacy)
├── metrics/metric_registry.json          ← 19 métricas (15 + 4 nuevas)
│
├── runs/                                 ← Resultados (4 840 runs)
│   ├── scored_tasks.csv                  ← 4 840 filas con métricas v2
│   ├── summary_tasks.csv                 ← Agregado por método
│   ├── v1_vs_v2_comparison.json          ← Deltas v1 vs v2 (clave)
│   ├── derived_metrics.json              ← MRD, QDD
│   ├── scenario_results.json
│   ├── method_results.json
│   └── provenance.csv
│
├── diagrams/                             ← 8 diagramas v2.0.0
│   ├── 01_v1_vs_v2_weighted.png          ← Comparativa directa v1 vs v2
│   ├── 02_all_methods_v2.png             ← Todos los métodos
│   ├── 03_v1_vs_v2_radar.png             ← Radar comparativo
│   ├── 04_view_coverage.png              ← VIEW coverage y reversibility
│   ├── 05_cli_timeline.png               ← Timeline v1 → v2
│   ├── 06_v2_failure_modes.png           ← Modos de fallo
│   ├── 07_v2_architecture.{puml,png}     ← Arquitectura v2
│   └── 08_v2_findings.{puml,png}         ← Hallazgos clave
│
├── reports/                              ← Informes HCORTEX v2.0.0
│   ├── scientific_report_v2.md           ← Informe principal
│   ├── claim_matrix_v2.md                ← 13 claims (10 demostrados)
│   └── regression_report_v2.md           ← v1 vs v2 (sin regresiones legacy)
│
└── scripts/                              ← Scripts reproducibles
    ├── run_benchmark_v2.py               ← Harness v2.0.0 (~3 min)
    ├── generate_diagrams_v2.py           ← 8 diagramas
    ├── build_pdf_v2.py                   ← PDF maestro
    └── update_corpus_v2.py               ← (experimental) añade VIEW directives
```

## 🚀 Reproducción rápida

```bash
# 1. Clonar CODEC-CORTEX v0.3.1
git clone https://github.com/FidelErnesto03/codec-cortex.git
cd codec-cortex && git checkout v0.3.1
cd cli && pip install -e .

# 2. Ejecutar benchmark v2.0.0 (~3 min)
python scripts/run_benchmark_v2.py

# 3. Generar diagramas
python scripts/generate_diagrams_v2.py

# 4. Compilar PDF
python scripts/build_pdf_v2.py
```

## 📊 Hallazgos principales v2.0.0

| # | Hallazgo | Estado |
|:---:|----------|:---:|
| H-01 | CLI v2.4.0 no degrada métodos v1 (Δ = 0.0 en todas las métricas) | **Demostrado** |
| H-02 | `cortex_v2_priority_pack` con fallback = idéntico a CPP v1 (Δ = 0.0) | **Demostrado** |
| H-03 | `cortex_v2_canonical` falla: BCFNR = 1.0, WS = −2.73 | **Demostrado** |
| H-04 | VIEW coverage = 0% en corpus v1.0.0 (sin VIEW directives) | **Demostrado** |
| H-05 | Reversibility = 0 en corpus v1.0.0 (requiere migración a v2) | **Demostrado** |
| H-06 | v2-convert produce HCORTEX vacío (251 bytes) sin VIEW directives | **Demostrado** |
| H-07 | QDD = −3.95 (igual que v1.0.0): estructura > query-dependent | **Demostrado** |
| H-08 | Bidireccionalidad requiere migrar artefactos a formato v2 con VIEW | **Hipótesis razonable** |

## 🎯 Métricas v2.0.0 (19)

**v1 heredadas (15)**: EAS · ETC · F1 · DA · Avg CT · P0 Survival · P1 Survival · BCFNR · UCFPR · CFCR · STR · BVR · MRD · QDD · Evidence Density

**v2 nuevas (4)**: VIEW_coverage · reversibility · bidir_equivalence · loss_count

## 🔬 Métodos comparados (11)

- **Pasivos posicionales (4)**: recent_tail_raw, head_tail_raw, head_json, head_markdown_summary
- **Pasivo semántico (1)**: semantic_field_pack
- **Query-dependent (1)**: keyword_retrieval_raw
- **CODEC-CORTEX v1 (1)**: cortex_priority_pack_v1 (CLI v1.1.9 `render`)
- **CODEC-CORTEX v2 (2)** ⭐: cortex_v2_priority_pack, cortex_v2_canonical (CLI v2.4.0)
- **Ablations (2)**: cortex_ablation_no_P0, cortex_ablation_no_temporal

## ⚠️ Limitaciones declaradas v2.0.0

1. **Corpus no migrado a v2**: el corpus v1.0.0 no tiene VIEW directives, impidiendo evaluar el potencial completo del CLI v2.4.0.
2. **`v2-canonicalize` rompe compatibilidad** con v1 render cuando no hay VIEW directives.
3. **Skill canónico no pasa `verify --strict`** con CLI v2.4.0 (E032 critical sigil incomplete).
4. **Sin fase LLM**: igual que v1.0.0.
5. **4 métricas v2 nuevas todas = 0** en corpus actual.

## 📈 Comparación v1.0.0 vs v2.0.0

| Dimensión | v1.0.0 | v2.0.0 | Δ |
|-----------|--------|--------|:---:|
| CPP v1 WS | 7.03 | 7.03 | 0.00 |
| CPP v1 P0 survival | 100% | 100% | 0 |
| CPP v1 BCFNR | 0.000 | 0.000 | 0.000 |
| MRD | +2.16 | +2.16 | 0.00 |
| QDD | −3.95 | −3.95 | 0.00 |
| Métricas totales | 15 | 19 | +4 |
| Métodos CODEC | 3 (idénticos) | 3 (diferenciados) | +0 |

## 🔮 Trabajo futuro v2.1.0

1. Migrar corpus a formato v2 con VIEW directives
2. Fix `v2-canonicalize` para preservar compatibilidad
3. Re-evaluar métodos v2 con corpus migrado
4. Comparar con skill canónico (266 entries, 44 VIEW, 100% coverage)
5. Ejecutar fase LLM separada

## 📄 Licencia

MIT — Fidel Ernesto Lozada A. (CODEC-CORTEX) · Benchmark harness: Z.ai (2026)
