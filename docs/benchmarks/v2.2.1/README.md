# Benchmark Comparativo CODEC-CORTEX v2.2.1 — PyPI

> **Benchmark comparativo contra paquetes PyPI** · 2026-07-02 · MIT License
> 220 paquetes "cortex" analizados, 7 comparables, 3 testeados empíricamente

## 🆕 Novedades v2.2.1 vs v2.2.0

| Aspecto | v2.2.0 | v2.2.1 |
|---------|--------|--------|
| Tipo | Benchmark individual | **Comparativo contra PyPI** |
| Paquetes analizados | 1 (codec-cortex) | **7 comparables + 220 landscape** |
| Paquetes testeados empíricamente | 1 | **3** (codec-cortex + cortex-ai-memory + llm-cortex-memory) |
| Feature matrix | 24 métricas internas | **12 features comparativas × 7 paquetes** |
| Hallazgo clave | Learning Engine funciona | **CODEC-CORTEX es único en 9/9 features** |

## 📊 Hallazgos principales

| # | Hallazgo | Estado |
|:---:|----------|:---:|
| H-01 | CODEC-CORTEX es el **único paquete PyPI** con 9/9 features críticas | **Demostrado** |
| H-02 | CODEC-CORTEX logra **100% preservación** vs 0-40% de competidores | **Demostrado** |
| H-03 | cortex-ai-memory es 50× más rápido pero pierde 80-100% de evidencia | **Demostrado** |
| H-04 | cortext-memory es el más similar (5/9) pero con namespace conflict | **Demostrado** |
| H-05 | CODEC-CORTEX ocupa nicho único: determinismo + estructura + audit + learning + bidirectional | **Demostrado** |

## 📈 Preservación de evidencia

| Paquete | FCS | OBJ | CNST | Promedio |
|---------|:---:|:---:|:---:|:---:|
| **codec-cortex** v0.3.6 | **100%** | **100%** | **100%** | **100%** |
| cortex-ai-memory v2.2.0 | 10% | 0% | 20% | 10% |
| llm-cortex-memory v1.2.0 | 10% | 0% | 40% | 17% |

## 📦 Contenido

```
benchmark-cortex-v221/
├── Benchmark_CODEC_CORTEX_v2.2.1.pdf   ← Informe (15 págs, 866 KB)
├── README.md
├── runs/comparative_pypi_results.json  ← Resultados empíricos + feature matrix
├── reports/scientific_report_v221.md   ← Informe científico HCORTEX
├── diagrams/                           ← 7 diagramas (5 PNG + 2 PUML)
└── scripts/
    ├── comparative_pypi_benchmark.py   ← Harness comparativo
    └── generate_diagrams_v221.py       ← Generador de diagramas
```

## 🚀 Reproducción

```bash
# 1. Instalar codec-cortex + paquetes comparables
pip install codec-cortex cortex-ai-memory llm-cortex-memory cortex-mem

# 2. Ejecutar benchmark comparativo
python scripts/comparative_pypi_benchmark.py

# 3. Generar diagramas
python scripts/generate_diagrams_v221.py

# 4. Compilar PDF
python scripts/build_pdf_v221.py
```

## 📄 Licencia

MIT — Fidel Ernesto Lozada A. (CODEC-CORTEX) · Benchmark harness: Z.ai (2026)
