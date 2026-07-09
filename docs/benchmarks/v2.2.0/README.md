# Benchmark Científico CODEC-CORTEX v2.2.0

> **Informe científico completo y reproducible** · 2026-07-02 · MIT License
> Evaluación con CLI v0.3.6 + Learning Engine v0.1.0 + E2 Security + SKILL v1.3.0

## 🆕 Novedades v2.2.0 vs v2.1.0

| Aspecto | v2.1.0 | v2.2.0 |
|---------|--------|--------|
| CLI version | 0.3.2 | **0.3.6** (verify v2 nativo, audit, --mode, doctor --scan-secrets) |
| Learning Engine | No existía | **CLE v0.1.0** (cortex learn scan/candidates/elevate) |
| E2 Security | No evaluada | **Evaluada** (0 secrets en corpus limpio) |
| SKILL version | v1.2.0 | **v1.3.0** (HCORTEX con 35 VIEW directives) |
| AGENT.md | Básico | **Con KNW entries** para 18 comandos CLI |
| Métricas | 19 | **24** (+5 learning/security) |
| WS ganador | 9.31 | **9.47** (+0.16) |

## 📦 Contenido del paquete

```
benchmark-cortex-v22/
├── Benchmark_CODEC_CORTEX_v2.2.pdf       ← Informe maestro (25 págs, 1.45 MB)
├── manifest.json                          ← Versión 2.2.0, CLI 0.3.6
├── README.md                              ← Este archivo
│
├── corpus/                                ← Corpus L2 migrado a VIEW (de v2.1.0)
│   ├── source/                            ← 10 .cortex con VIEW + 40 alternativas
│   └── normalized/hashes.json             ← SHA-256
│
├── learning_workspaces/                   ← NUEVO v2.2.0: workspaces para Learning Engine
│   └── <case_id>/.cortex/                 ← 10 workspaces (brain, policies, index, cache)
│
├── methods/method_registry.json           ← 11 métodos
├── metrics/metric_registry.json           ← 24 métricas (15 v1 + 4 v2.0 + 5 v2.2 NEW)
│
├── runs/                                  ← Resultados (4 840 runs)
│   ├── scored_tasks.csv                   ← 4 840 filas con métricas learning
│   ├── summary_tasks.csv                  ← Agregado por método
│   ├── v1_vs_v2_comparison.json           ← Deltas v1 vs v2.2
│   ├── derived_metrics.json               ← MRD, QDD
│   └── ...
│
├── diagrams/                              ← 10 diagramas v2.2.0
│   ├── 01_v22_weighted.png                ← Comparativa global
│   ├── 02_progression_4_versions.png      ← Progresión 4 versiones
│   ├── 03_learning_engine.png             ← Learning Engine por método
│   ├── 04_learning_per_case.png           ← Learning por caso del corpus
│   ├── 05_security_e2.png                 ← E2 Security
│   ├── 06_token_vs_score_v22.png          ← Trade-off tokens vs score
│   ├── 07_radar_top4_v22.png              ← Radar top-4 con learning
│   ├── 08_v22_architecture.{puml,png}     ← Arquitectura
│   ├── 09_v22_findings.{puml,png}         ← Hallazgos clave
│   └── 10_learning_flow.{puml,png}        ← Flujo del Learning Engine
│
├── reports/                               ← Informes HCORTEX v2.2.0
│   ├── scientific_report_v22.md           ← Informe principal
│   ├── claim_matrix_v22.md                ← 16 claims (15 demostrados, 94%)
│   └── regression_report_v22.md           ← v2.1.0 vs v2.2.0 (progresión)
│
└── scripts/                               ← Scripts reproducibles
    ├── run_benchmark_v22.py               ← Harness v2.2.0 (~3.5 min)
    ├── generate_diagrams_v22.py           ← 10 diagramas
    └── build_pdf_v22.py                   ← PDF maestro
```

## 🚀 Reproducción rápida

```bash
# 1. Clonar CODEC-CORTEX v0.3.6
git clone https://github.com/FidelErnesto03/codec-cortex.git
cd codec-cortex && git checkout v0.3.6
cd cli && pip install -e .

# 2. Preparar corpus migrado a VIEW (reutilizar v2.1.0)
# (copiar corpus/source/ de benchmarks/v2.1.0/)

# 3. Ejecutar benchmark v2.2.0 (~3.5 min)
python scripts/run_benchmark_v22.py

# 4. Generar diagramas
python scripts/generate_diagrams_v22.py

# 5. Compilar PDF
python scripts/build_pdf_v22.py
```

## 📊 Hallazgos principales v2.2.0

| # | Hallazgo | Estado |
|:---:|----------|:---:|
| H-01 | CORTEX PP v2 es el ganador con WS = 9.47 (+2.29 vs v1, +0.16 vs v2.1) | **Demostrado** |
| H-02 | Learning Engine v0.1.0 funciona: 1.05 candidatos/run, promotion_score 0.65 | **Demostrado** |
| H-03 | Learning Engine detecta 9-14 candidatos por caso (pre-computing) | **Demostrado** |
| H-04 | Promotion scores 5.44-7.73 (escala Fibonacci: 5=candidate, 8=ask_user) | **Demostrado** |
| H-05 | E2 Security: 0 secrets en corpus limpio (corpus seguro) | **Demostrado** |
| H-06 | SKILL v1.3.0 pasa `verify --strict` v2 nativamente (250 entries, 75 VIEW) | **Demostrado** |
| H-07 | AGENT.md incluye KNW entries para 18 comandos CLI v0.3.2+ | **Demostrado** |
| H-08 | WS mejora +0.16 vs v2.1.0 por learning metrics | **Demostrado** |
| H-09 | MRD = +4.38 mantenido, QDD = −6.39 (ligera ampliación) | **Demostrado** |
| H-10 | BCFNR = 0 y secret_count = 0 mantenidos | **Demostrado** |
| H-11 | `roundtrip-bidir` direction 1 sigue como known limitation (CI non-blocking) | **Demostrado** |
| H-12 | Corpus mantiene 100% VIEW coverage y reversibility=True | **Demostrado** |

## 📈 Progresión v1.0.0 → v2.0.0 → v2.1.0 → v2.2.0

| Dimensión | v1.0.0 | v2.0.0 | v2.1.0 | v2.2.0 |
|-----------|--------|--------|--------|--------|
| CLI version | 1.1.9 | 2.4.0 | 0.3.2 | **0.3.6** |
| WS ganador | 7.03 | 7.03 | 9.31 | **9.47** |
| VIEW coverage | N/A | 0% | 100% | **100%** |
| Reversibility | N/A | 0 | 1.0 | **1.0** |
| Learning Engine | N/A | N/A | N/A | **CLE v0.1.0** |
| E2 Security | N/A | N/A | N/A | **Evaluada** |
| SKILL version | v1.2.0 | v1.2.0 | v1.2.0 | **v1.3.0** |
| Métricas totales | 15 | 19 | 19 | **24** |
| MRD | +2.16 | +2.16 | +4.38 | **+4.38** |
| QDD | −3.95 | −3.95 | −6.24 | **−6.39** |
| BCFNR ganador | 0.000 | 0.000 | 0.000 | **0.000** |
| Claims demostrados | 44% | 77% | 92% | **94%** |

## 🧠 Learning Engine v0.1.0 (CLE)

El Learning Engine es **determinista, local-first, sin LLM**:

- **Algoritmo**: `golden_fibonacci_v1` (thresholds: observed=1, repeated=2, pattern=3, candidate=5, ask_user=8, strong=13, critical=21)
- **Flujo**: `cortex learn init` → `cortex learn scan` → `cortex learn candidates` → `cortex learn elevate`
- **Políticas**: declarativas en `learn-policies.cortex` (SES→LNG when score≥8, LNG→KNW when score≥13)
- **Gates**: `dry_run_first` por defecto, `block_unless_admin_policy` para critical sigils
- **Workspace**: `.cortex/` aislado con brain, policies, index, cache

### Resultados por caso del corpus

| Caso | Candidates | Avg Promotion | Elevations | Hotness |
|------|:---:|:---:|:---:|:---:|
| devops-k8s-rollout | 13 | 7.00 | 7 | 7.15 |
| sec-incident-response | 14 | 7.14 | 9 | 9.57 |
| climate-grid-balancing | 12 | 7.50 | 7 | 11.00 |
| **Promedio** | **11.4** | **7.10** | **6.4** | **9.16** |

## 🔒 E2 Security (v0.3.4)

- **Secret scanner**: 12 patrones (API keys, passwords, tokens)
- **Mutation gates**: `--mode read-only|editor|admin`, env `$CORTEX_MODE`
- **Audit log**: `cortex audit on/off/status/snapshot/prune`
- **Signature verification**: `cortex verify --signature MANIFEST`

**Resultado**: 0 secrets detectados en los 10 casos del corpus (corpus limpio y seguro).

## ⚠️ Limitaciones declaradas v2.2.0

1. **`roundtrip-bidir` direction 1** sigue fallando (E_TABLE_SCHEMA_MISMATCH, known limitation en CI)
2. **SKILL canónico 21% VIEW coverage** (synthetic_knw entries no cubiertas) vs corpus 100%
3. **Learning Engine es beta (v0.1.0)**: no implementa `learn-ledger.cortex` aún
4. **Sin fase LLM**: igual que versiones anteriores
5. **Learning metrics son las mismas para todos los métodos CODEC** (CLE opera sobre el .cortex del caso, no sobre el método)

## 🔮 Trabajo futuro v2.3.0

1. Fix `roundtrip-bidir` direction 1 (E_TABLE_SCHEMA_MISMATCH)
2. Implementar `learn-ledger.cortex` (CLE v0.2.0)
3. Migrar corpus a 2-3 casos por dominio (L2 completo)
4. Alinear SKILL synthetic_knw entries con VIEW directives
5. Ejecutar fase LLM separada (protocolo §11)
6. Comparar CLE con MemGPT/Letta learning mechanisms

## 📄 Licencia

MIT — Fidel Ernesto Lozada A. (CODEC-CORTEX) · Benchmark harness: Z.ai (2026)
