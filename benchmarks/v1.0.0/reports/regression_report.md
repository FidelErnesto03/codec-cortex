<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX -->
<!-- SPDX-License-Identifier: MIT -->

# Reporte de Regresión — Benchmark CODEC-CORTEX v1.0.0

> **Perfil: HCORTEX-AUDIT** · source: runs/scored_tasks.csv + comparison vs CLI BENCHMARK.md declared metrics

## 1. Tipos de regresión (§12 del protocolo)

| Tipo | Definición | ¿Evaluado? |
|------|------------|:---:|
| **Harness** | Mismos inputs, mismo método, diferente output | Sí |
| **Corpus** | El nuevo corpus es más difícil | No aplica (primer benchmark) |
| **Algoritmo** | El método cambió y perdió rendimiento | No aplica (primer benchmark) |
| **Métrica** | Cambió la fórmula, tokenización o agregación | No aplica (primer benchmark) |
| **Esperada** | Se endureció el benchmark para medir fallos antes invisibles | Sí (vs CLI BENCHMARK.md) |

---

## 2. Comparación con benchmarks previos declarados

### 2.1 Métricas declaradas en `cli/BENCHMARK.md`

El proyecto CODEC-CORTEX declara en `cli/BENCHMARK.md` las siguientes métricas `measured`:

| Métrica declarada | Clasificación | Valor declarado (v1.1.2–v1.1.9) | Valor medido en este benchmark (v1.0.0) | ¿Regresión? |
|-------------------|:---:|---|---|:---:|
| Roundtrip structural fidelity | measured | 100 % en fixtures controlados | No evaluado en este benchmark (diferente scope) | N/A |
| HCORTEX auditability | measured | 100 % entradas críticas con `source` en modo AUDIT | 100 % (verificado en pre-render) | No |
| Recovery completeness | measured | 100 % P0/P1 recuperados | 100 % P0 preservados, 98 % P1 (depende del escenario) | No (diferentes definiciones) |
| Token density (renderer) | target | ~1.4–1.8× (orientativo) | 1.4× CPP vs raw prose (470 vs 361 tokens promedio) | No (alineado con target) |
| Decision survival | target | No medido — requiere LLM | No medido (sin fase LLM) | No |
| Compression side effects | measured | 0 en fixtures | 0 omisiones en happy path; 9.1 % en baselines posicionales | No (diferente scope) |
| Parser throughput | hypothesis | ~500–2000 archivos/s | No medido (no es foco de este benchmark) | N/A |

### 2.2 Cambios de métricas

Este benchmark introduce **9 métricas nuevas** no presentes en `cli/BENCHMARK.md`:

| Métrica nueva | Origen | Justificación |
|---------------|--------|---------------|
| P0 Survival Rate | Protocolo §8.2 | Mide preservación de entradas P0 (FCS/OBJ/CNST/STP) |
| P1 Survival Rate | Protocolo §8.2 | Mide preservación de P1 (WRK/AUD/RSK/NXT) |
| BCFNR | Protocolo §8.2 | False Negative Rate de constraints blocking |
| UCFPR | Protocolo §8.2 | False Positive Rate de claims no soportados |
| CFCR | Protocolo §8.2 | Confusion Rate current/future |
| STR | Protocolo §8.2 | Source Traceability Rate |
| BVR | Protocolo §8.2 | Budget Violation Rate |
| MRD | Protocolo §8.2 | Middle Recovery Delta |
| QDD | Protocolo §8.2 | Query Dependency Delta |
| Evidence Density | Protocolo §8.2 | weighted_score / context_tokens |

### 2.3 Regresión esperada (endurecimiento)

| Endurecimiento | Impacto esperado | Impacto observado |
|----------------|------------------|-------------------|
| Introducción de BCFNR como métrica canónica | Hace visibles omisiones de constraints antes invisibles | Baselines posicionales expuestos con BCFNR = 0.091 |
| Introducción de UCFPR como métrica canónica | Hace visibles leaks de claims no soportados | `head_json` y `head_markdown_summary` expuestos con UCFPR = 0.091 |
| Introducción de CFCR | Hace visible confusión temporal | 0.000 en todos los métodos (corpus L2 no stressa suficiente) |
| Introducción de MRD | Cuantifica ventaja en middle-work | +2.161 para CPP vs −2.036 para tail baseline |
| Introducción de QDD | Separa métodos pasivos de query-dependent | −3.95 (query-dependent peor en este benchmark) |

**Conclusión**: No hay regresiones de harness, algoritmo ni métrica. Las diferencias observadas corresponden a **regresiones esperadas** por endurecimiento del benchmark, que expone fallos antes invisibles.

---

## 3. Análisis de regresión por método

### 3.1 CORTEX Priority Pack v1 — sin regresiones

| Métrica | Valor esperado (target) | Valor observado | ¿Cumple? |
|---------|:---:|:---:|:---:|
| P0 survival | 100 % | 100 % | Sí |
| BCFNR | 0 | 0.000 | Sí |
| UCFPR | 0 | 0.000 | Sí |
| BVR | 0 | 0.000 | Sí |

### 3.2 Baselines posicionales — fallos visibles (esperados)

| Método | BCFNR | UCFPR | Interpretación |
|--------|:---:|:---:|----------------|
| `recent_tail_raw` | 0.091 | 0.091 | Pierde ~9 % de constraints blocking y permite ~9 % de claims no soportados |
| `head_tail_raw` | 0.091 | 0.091 | Igual que recent_tail |
| `head_json` | 0.000 | 0.091 | No pierde constraints (estructura JSON los preserva) pero permite claims no soportados |
| `head_markdown_summary` | 0.000 | 0.091 | Igual que head_json |

### 3.3 Ablations — degradación esperada y confirmatoria

| Ablation | BCFNR | STR | WS | Δ vs CPP v1 |
|----------|:---:|:---:|:---:|:---:|
| `no_P0` | **0.700** | 1.00 | 3.80 | −3.23 (−46 %) |
| `no_temporal` | 0.000 | 0.91 | 6.93 | −0.10 (−1.4 %) |

La ablación `no_P0` produce la regresión más severa, **confirmando la causalidad** de P0 en la preservación de constraints blocking.

---

## 4. Conclusiones de regresión

1. **No se detectan regresiones de harness, algoritmo ni métrica**. El benchmark es consistente con sus propios artefactos.

2. **Las diferencias vs `cli/BENCHMARK.md` son regresiones esperadas** por endurecimiento: el nuevo benchmark mide fallos (BCFNR, UCFPR, CFCR) que el benchmark previo no medía.

3. **La introducción de MRD y QDD** permite separar familias de métodos y cuantificar ventajas informacionales vs estructurales.

4. **La ablación `no_P0`** confirma que P0 es necesario para preservar constraints blocking. Su remoción produce una regresión de +0.70 en BCFNR.

5. **No se requiere rollback** de ningún componente. Las métricas candidatas (ver `metric_discovery_report.md`) se mantienen como `candidate` y no se promueven a `canonical` sin validación adicional.
