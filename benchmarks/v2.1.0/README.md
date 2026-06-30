# Benchmark Científico CODEC-CORTEX v2.1.0

> **Informe científico completo y reproducible** · 2026-07-01 · MIT License
> Evaluación de preservación de evidencia con CLI v0.3.2 (corpus migrado a VIEW directives)

## 🆕 Novedades v2.1.0 vs v2.0.0

| Aspecto | v2.0.0 | v2.1.0 |
|---------|--------|--------|
| CLI version | 2.4.0 (`v2-*` commands) | **0.3.2** (nombres canónicos) |
| CODEC-CORTEX versión | 0.3.1 | **0.3.2** |
| Corpus | Sin VIEW directives | **Migrado a VIEW** (108 directives, 100% coverage) |
| `canonicalize` | Rompe compatibilidad (WS = −2.73) | **`--preserve` VIEW-aware (WS = +9.31)** |
| VIEW coverage | 0% en todos los casos | **100% en todos los casos** |
| Reversibility | 0 (False) | **1 (True)** |
| WS ganador | 7.03 (con fallback) | **9.31 (nativo, sin fallback)** |

## 📦 Contenido del paquete

```
benchmark-cortex-v21/
├── Benchmark_CODEC_CORTEX_v2.1.pdf       ← Informe maestro (24 págs, 933 KB)
├── manifest.json                          ← Versión 2.1.0, CLI 0.3.2
├── README.md                              ← Este archivo
│
├── corpus/                                ← Corpus L2 migrado a VIEW
│   ├── source/                            ← 10 .cortex con VIEW + 40 alternativas
│   ├── source_pre_header_backup/          ← Backups pre-migración
│   └── normalized/
│       ├── hashes.json                    ← SHA-256
│       └── corpus_manifest.json           ← Metadatos con view_count por caso
│
├── methods/method_registry.json           ← 11 métodos (1 v1 + 2 v2 + 8 legacy)
├── metrics/metric_registry.json           ← 19 métricas (15 + 4 v2)
│
├── runs/                                  ← Resultados (4 840 runs)
│   ├── scored_tasks.csv                   ← 4 840 filas
│   ├── summary_tasks.csv                  ← Agregado por método
│   ├── v1_vs_v2_comparison.json           ← Deltas v1 vs v2.1 (clave)
│   ├── derived_metrics.json               ← MRD, QDD
│   ├── scenario_results.json
│   ├── method_results.json
│   └── provenance.csv
│
├── diagrams/                              ← 8 diagramas v2.1.0
│   ├── 01_v21_weighted.png                ← Comparativa global
│   ├── 02_progression_v1_v2_v21.png       ← Progresión 3 versiones
│   ├── 03_v2_metrics_activated.png        ← Métricas v2 activadas
│   ├── 04_canonical_fix.png               ← Fix canonicalize (B-01/B-05)
│   ├── 05_token_vs_score_v21.png          ← Trade-off tokens vs score
│   ├── 06_radar_top4_v21.png              ← Radar top-4
│   ├── 07_v21_architecture.{puml,png}     ← Arquitectura
│   └── 08_v21_findings.{puml,png}         ← Hallazgos clave
│
├── reports/                               ← Informes HCORTEX v2.1.0
│   ├── scientific_report_v21.md           ← Informe principal
│   ├── claim_matrix_v21.md                ← 13 claims (12 demostrados, 92%)
│   └── regression_report_v21.md           ← v2.0.0 vs v2.1.0 (progresión)
│
└── scripts/                               ← Scripts reproducibles
    ├── prepare_corpus_v21.py              ← Migración corpus a VIEW + header
    ├── run_benchmark_v21.py               ← Harness v2.1.0 (~3 min)
    ├── generate_diagrams_v21.py           ← 8 diagramas
    └── build_pdf_v21.py                   ← PDF maestro
```

## 🚀 Reproducción rápida

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

## 📊 Hallazgos principales v2.1.0

| # | Hallazgo | Estado |
|:---:|----------|:---:|
| H-01 | CORTEX PP v2 (`convert`) es el nuevo ganador con WS = 9.31 (+2.28 vs v1) | **Demostrado** |
| H-02 | `canonicalize --preserve` fixea B-01/B-05: WS −2.73 → +9.31 | **Demostrado** |
| H-03 | VIEW coverage = 100% y reversibility = 1.0 en métodos v2 | **Demostrado** |
| H-04 | MRD = +4.38 (vs +2.16 en v2.0.0): ventaja se duplica | **Demostrado** |
| H-05 | QDD = −6.24 (vs −3.95): estructura cognitiva amplía ventaja | **Demostrado** |
| H-06 | BCFNR = 0 mantenido (constraints blocking preservadas) | **Demostrado** |
| H-07 | Trade-off: +396 tokens por +2.28 WS (ratio aceptable) | **Demostrado** |
| H-08 | EAS baja 0.034 por nombres canónicos de campos | **Demostrado** |
| H-09 | `roundtrip-bidir` direction 1 falla por E_TABLE_SCHEMA_MISMATCH | **Demostrado** (pendiente v2.2.0) |
| H-10 | Los 3 issues de v2.0.0 están resueltos en v0.3.2 | **Demostrado** |

## 📈 Progresión v1.0.0 → v2.0.0 → v2.1.0

| Dimensión | v1.0.0 | v2.0.0 | v2.1.0 |
|-----------|--------|--------|--------|
| CLI version | 1.1.9 | 2.4.0 | **0.3.2** |
| WS ganador | 7.03 | 7.03 | **9.31** |
| VIEW coverage | N/A | 0% | **100%** |
| Reversibility | N/A | 0 | **1.0** |
| `canonicalize` funciona | N/A | No (WS=−2.73) | **Sí (WS=+9.31)** |
| MRD | +2.16 | +2.16 | **+4.38** |
| QDD | −3.95 | −3.95 | **−6.24** |
| BCFNR ganador | 0.000 | 0.000 | 0.000 |
| Claims demostrados | 44% | 77% | **92%** |

## ⚠️ Limitaciones declaradas v2.1.0

1. **EAS baja ligeramente** (0.984 → 0.950) por nombres canónicos de campos en HCORTEX v2.
2. **`roundtrip-bidir` direction 1 falla** por E_TABLE_SCHEMA_MISMATCH (issue pendiente v2.2.0).
3. **`verify --strict` legacy** no acepta `status:cur` (micro-token), pero no afecta al benchmark.
4. **Sin fase LLM**: igual que versiones anteriores.

## 🔮 Trabajo futuro v2.2.0

1. Fix `roundtrip-bidir` direction 1 (E_TABLE_SCHEMA_MISMATCH)
2. Alinear `fields` declarados en VIEW con schema real de tabla
3. Migrar corpus a 2-3 casos por dominio (L2 completo)
4. Re-evaluar EAS con tareas adaptadas a nombres canónicos v2
5. Ejecutar fase LLM separada (protocolo §11)

## 📄 Licencia

MIT — Fidel Ernesto Lozada A. (CODEC-CORTEX) · Benchmark harness: Z.ai (2026)
