# Benchmark Científico CODEC-CORTEX v1.0.0

> **Informe científico completo y reproducible** · 2026-06-28 · MIT License
> Evaluación de preservación de evidencia bajo compresión contextual

## 📦 Contenido del paquete

```
benchmark-cortex/
├── Benchmark_CODEC_CORTEX_v1.0.pdf     ← Informe maestro (49 páginas, 1.8 MB)
├── manifest.json                        ← Versión, entorno, totales
├── README.md                            ← Este archivo
│
├── corpus/                              ← Corpus L2-multidominio (50 artefactos)
│   ├── source/                          ← 10 .cortex + 10 raw.md + 10 md + 10 json + 10 yaml
│   └── normalized/
│       ├── hashes.json                  ← SHA-256 de los 50 artefactos
│       └── corpus_manifest.json         ← Metadatos por caso
│
├── methods/
│   └── method_registry.json             ← 11 métodos bajo comparación
│
├── metrics/
│   └── metric_registry.json             ← 15 métricas canónicas
│
├── runs/                                ← Resultados del benchmark (4 840 runs)
│   ├── scored_tasks.csv                 ← 4 840 filas, una por run
│   ├── summary_tasks.csv                ← Agregado por método
│   ├── scenario_results.json            ← Agregado por método × escenario
│   ├── method_results.json              ← Métricas por método
│   ├── derived_metrics.json             ← MRD y QDD
│   ├── errors.csv                       ← Errores (vacío)
│   └── provenance.csv                   ← Trazabilidad por run
│
├── diagrams/                            ← 17 diagramas (PNG + PUML + SVG)
│   ├── 01_weighted_score.png            ← Comparativa global
│   ├── 02_p0_p1_survival.png            ← Supervivencia P0/P1
│   ├── 03_eas_by_budget.png             ← EAS por presupuesto
│   ├── 04_failure_modes.png             ← Modos de fallo (BCFNR+UCFPR+CFCR)
│   ├── 05_evidence_density.png          ← Densidad de evidencia
│   ├── 06_scenario_heatmap.png          ← Mapa de calor método × escenario
│   ├── 07_ablation_impact.png           ← Impacto de ablations
│   ├── 08_mrd.png                       ← Middle Recovery Delta
│   ├── 09_radar_top4.png                ← Radar comparativo top-4
│   ├── 10_token_vs_score.png            ← Trade-off tokens vs score
│   ├── 11_architecture.{puml,png,svg}   ← Arquitectura del benchmark
│   ├── 12_codec_stack.{puml,png,svg}    ← Pila canónica CODEC-CORTEX
│   ├── 13_experiment_flow.{puml,png,svg}← Flujo experimental
│   ├── 14_comparative_landscape.*       ← Panorama comparativo
│   ├── 15_degradation_flow.*            ← Perfil de degradación
│   ├── 16_ontology.*                    ← Ontología cognitiva (4 cortezas)
│   └── 17_claim_matrix.*                ← Matriz de claims visual
│
├── reports/                             ← Informes en formato HCORTEX
│   ├── scientific_report.md             ← Informe científico principal
│   ├── claim_matrix.md                  ← Matriz de claims (16 claims)
│   ├── regression_report.md             ← Reporte de regresión
│   ├── metric_discovery_report.md       ← 6 métricas candidatas propuestas
│   └── comparative_analysis.md          ← Análisis CODEC vs MemGPT/RAG/MCP/A-MEM
│
└── scripts/                             ← Scripts reproducibles
    ├── build_corpus.py                  ← Genera corpus L2 (50 artefactos)
    ├── prerender_hcortex.py             ← Pre-renderiza HCORTEX en paralelo
    ├── run_benchmark.py                 ← Harness principal (4 840 runs en 6.4s)
    ├── generate_diagrams.py             ← Genera 17 diagramas
    ├── build_pdf.py                     ← Compila PDF maestro
    └── validate_reproducibility.py      ← Valida determinismo
```

## 🚀 Reproducción rápida

```bash
# 1. Instalar CODEC-CORTEX CLI v1.1.9
git clone https://github.com/FidelErnesto03/codec-cortex.git
cd codec-cortex/cli && pip install -e .

# 2. Reconstruir corpus
python scripts/build_corpus.py

# 3. Pre-renderizar HCORTEX (paralelo, ~30s)
python scripts/prerender_hcortex.py

# 4. Ejecutar benchmark (~6.4s)
python scripts/run_benchmark.py

# 5. Generar diagramas
python scripts/generate_diagrams.py

# 6. Compilar PDF
python scripts/build_pdf.py

# 7. Validar reproducibilidad
python scripts/validate_reproducibility.py
```

## 📊 Hallazgos principales

| # | Hallazgo | Estado |
|:---:|----------|:---:|
| H-01 | CORTEX Priority Pack preserva 100 % de entradas P0 en todos los escenarios | Demostrado |
| H-02 | CPP mantiene BCFNR = 0 y UCFPR = 0 | Demostrado |
| H-03 | CPP supera a baselines posicionales en MRD = +2.161 | Demostrado |
| H-04 | Ablation `no_P0` degrada BCFNR a 0.70 (causalidad confirmada) | Demostrado |
| H-05 | `keyword_retrieval_raw` (query-dependent) tiene BCFNR = 0.32 | Demostrado |
| H-06 | CPP consume ~1.4× más tokens pero produce ~1.9× más score | Demostrado |

## 🎯 Métricas canónicas (15)

EAS · ETC · F1 · DA · Avg CT · P0 Survival · P1 Survival · BCFNR · UCFPR · CFCR · STR · BVR · MRD · QDD · Evidence Density

## 🔬 Métodos comparados (11)

- **Pasivos posicionales (4)**: recent_tail_raw, head_tail_raw, head_json, head_markdown_summary
- **Pasivo semántico (1)**: semantic_field_pack
- **Query-dependent (1)**: keyword_retrieval_raw (BM25-like)
- **CODEC-CORTEX (3)**: cortex_priority_pack_v1, _adaptive, _semantic_hybrid
- **Ablations (2)**: cortex_ablation_no_P0, cortex_ablation_no_temporal

## 🧪 Escenarios (11)

`full` · `reduced_window_{512,1024,2048,4096}` · `middle_work_adversarial` · `stale_state_conflict` · `blocking_constraint_survival` · `unsupported_claim_suppression` · `corrupted_memory_tolerance` · `multi_instance_sigil`

## ⚠️ Limitaciones declaradas

1. **Sin fase LLM**: cualquier claim sobre "mejora del razonamiento LLM" está prohibido (protocolo §1.4).
2. **Tokenizador proxy**: char-based (1 token ≈ 3.5–4.0 chars). No es BPE real.
3. **Corpus L2 con 1 caso por dominio**: validez externa limitada.
4. **3 variantes CPP idénticas**: limitación del CLI v1.1.9 (no expone diferenciación).
5. **Determinístico puro**: sin aleatoriedad ni semillas.

## 📚 Referencias

- Proyecto CODEC-CORTEX: https://github.com/FidelErnesto03/codec-cortex
- Protocolo canónico de benchmark: `PROTOCOLO_BENCHMARK.md` (proporcionado)
- SKILL.md v1.2.0-enterprise-candidate
- CLI STATUS: 222 tests passing, v1.1.9

## 📄 Licencia

MIT — Fidel Ernesto Lozada A. (CODEC-CORTEX) · Benchmark harness: Z.ai (2026)
