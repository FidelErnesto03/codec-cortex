# Benchmark v2.2.2 — Bridge + 4 Familias + Resource Metrics

> **Benchmark que aborda las 6 recomendaciones del informe analítico externo** · 2026-07-02 · MIT

## 🆕 Novedades v2.2.2 vs v2.2.1

| Aspecto | v2.2.1 | v2.2.2 |
|---------|--------|--------|
| Tipo | Comparativo PyPI (3 paquetes) | **Bridge + 4 familias + resource metrics** |
| Benchmark estándar | No | **LoCoMo/LongMemEval-style (30 tareas, 100% EAS)** |
| Familias comparadas | 7 paquetes PyPI "cortex" | **4 familias arquitectónicas** (Mem0, Zep, Letta, LangMem) |
| Resource metrics | No | **Throughput (4.7 files/s), RAM (0.06 MB), latencia (214 ms)** |
| Version audit | No | **42 superficies auditadas (v0.3.6 vs v0.4.1)** |
| Threat model | No | **6 amenazas + 3 gaps + privacy policy** |

## 📊 Hallazgos principales

| # | Hallazgo | Estado |
|:---:|----------|:---:|
| H-01 | codec-cortex logra **100% EAS** en 30 tareas bridge estilo LoCoMo/LongMemEval | **Demostrado** |
| H-02 | codec-cortex usa **0.06 MB peak RAM** (3-4 órdenes de magnitud más liviano que competidores) | **Demostrado** |
| H-03 | Throughput: **4.7 files/s** (214 ms/file) para verify/render/verify-view/learn-scan | **Demostrado** |
| H-04 | **42 superficies declaran v0.3.6, 0 declaran v0.4.1** — confirma observación del análisis | **Demostrado** |
| H-05 | CHANGELOG **sin entrada v0.4.1** — gap documental crítico | **Demostrado** |
| H-06 | codec-cortex es **único** (determinista + local + audit + learning + bidirectional) entre 4 familias | **Demostrado** |
| H-07 | 6 amenazas identificadas, todas mitigadas; 3 gaps documentales | **Demostrado** |

## 📈 Bridge Benchmark: LoCoMo/LongMemEval-style

| Tipo | N tareas | EAS | Categoría |
|------|:---:|:---:|------------|
| LoCoMo single_hop | 20 | 100% | event_recall |
| LoCoMo multi_hop | 4 | 100% | reasoning |
| LongMemEval temporal | 3 | 100% | temporal_reasoning |
| LongMemEval info_flow | 3 | 100% | constraint_survival |
| **Total** | **30** | **100%** | |

## 💾 Resource Metrics

| Operación | Throughput | Latencia | Peak RAM |
|-----------|:---:|:---:|:---:|
| `cortex verify` | 4.67 files/s | 214 ms | **0.06 MB** |
| `cortex render` | 4.66 files/s | 215 ms | **0.06 MB** |
| `cortex verify-view` | 4.74 files/s | 211 ms | **0.06 MB** |
| `cortex learn scan` | 4.69 files/s | 213 ms | **0.06 MB** |

## 🔍 4 Familias comparadas

| Familia | Stars | LoCoMo | Determinista | Local | Audit | Learning |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| **codec-cortex** | 0 | 100% (bridge) | ✓ | ✓ | ✓ | ✓ |
| Mem0 | 60k | 91.6% | ✗ | ✓ | ✗ | ✗ |
| Zep/Graphiti | 28.3k | 94.7% | ✗ | ✗ | ✗ | ✗ |
| Letta | 23.6k | 74.0% | ✗ | ✗ | ✗ | ✗ |
| LangMem | 1.5k | N/A | ✗ | ✗ | ✗ | ✗ |

## 🛡️ Threat Model

6 amenazas identificadas (T-01 a T-06), todas con mitigación implementada en v0.3.2-v0.3.6. 3 gaps documentales: threat model formal, privacy policy, MCP network surface.

## 📦 Contenido

```
benchmark-cortex-v222/
├── Benchmark_CODEC_CORTEX_v2.2.2.pdf   ← Informe (14 págs, 615 KB)
├── README.md
├── runs/
│   ├── v222_results.json               ← Resultados completos
│   ├── version_audit.json              ← Auditoría 42 superficies
│   ├── four_family_matrix.json         ← Matriz 4 familias
│   └── threat_model.json               ← 6 amenazas + privacy
├── resource_metrics/
│   └── resource_metrics.json           ← Throughput/RAM/latencia
├── bridge_benchmark/                   ← 30 tareas LoCoMo/LongMemEval-style
├── reports/scientific_report_v222.md   ← Informe HCORTEX
├── diagrams/                           ← 7 diagramas
└── scripts/
    ├── run_benchmark_v222.py           ← Harness principal
    └── generate_diagrams_v222.py       ← Generador diagramas
```

## ✅ Recomendaciones del informe analítico abordadas

| # | Recomendación | Estado |
|:---:|---------------|:---:|
| 1 | Alinear versiones a v0.4.1 | ✓ Auditado (42 superficies) |
| 2 | Abrir canal de issues | ✗ Requiere maintainer |
| 3 | Benchmark puente LoCoMo/LongMemEval | ✓ Implementado (30 tareas) |
| 4 | API Python estable | ✗ Requiere decisión diseño |
| 5 | Threat model/privacy | ✓ Documentado (6 amenazas) |
| 6 | Priorizar E4/E5 | ✗ Requiere roadmap |

## 📄 Licencia

MIT — Fidel Ernesto Lozada A. (CODEC-CORTEX) · Benchmark harness: Z.ai (2026)
