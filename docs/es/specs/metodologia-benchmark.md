<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

<p align="center">
  <strong>CODEC-CORTEX</strong> — Benchmark Methodology
  <br>
  <sub>SPECIFICATION · Survival Core · v0.3.6 · MIT · <a href="../../AUTHORS.md">Fidel Ernesto Lozada A.</a></sub>
</p>

---

> **NOTA DE ESTADO:** Este documento es especificación. A v0.3.6 el parser determinista, el CLI y `cortex benchmark` (inventario + validación de suites) están implementados. Las suites científicas v1.0.0, v2.0.0 y v2.1.0 existen en `benchmarks/` con 4,840 runs cada una. Las suites 0.1, 0.1b y 0.2 siguen listadas como referencia histórica offline/proxy. La metodología descrita aquí es aplicable tanto a las suites existentes como a futuras automatizaciones de supervivencia contextual.

**Abstract:** Metodología de benchmark centrada en supervivencia de decisiones — no en ocurrencia de términos. Define 5 preguntas de evaluación, 2 escenarios, y métricas de tasa de supervivencia contextual. Las suites 0.1, 0.1b y 0.2 existen como evidencia offline/proxy; las suites v1.0.0, v2.0.0 y v2.1.0 son benchmarks científicos reproducibles publicados en `benchmarks/`.

| | |
|---|---|
| **Author** | Fidel Ernesto Lozada A. — Systems Engineer / MSc. Management Sciences |
| **Repository** | github.com/FidelErnesto03/codec-cortex |
| **License** | MIT |
| **Version** | v0.3.6 (methodology; suites v1.0.0 / v2.0.0 / v2.1.0 publicadas) |
| **Language** | Español |

---

## 1. Filosofía

El benchmark tradicional pregunta: **"¿aparece el término esperado?"**

El benchmark de supervivencia contextual pregunta: **"¿sobrevive la decisión correcta?"**

CODEC-CORTEX no mide eficiencia por compresión de bytes. La mide por cuántas decisiones, restricciones y pasos sobreviven bajo reducción de contexto.

---

## 2. Cinco preguntas de evaluación

| # | Pregunta | Qué evalúa | Sigilos implicados |
|:---:|----------|------------|--------------------|
| 1 | **decision_survival** | ¿Sobrevive la decisión correcta? | FCS, OBJ |
| 2 | **constraint_survival** | ¿Sobrevive la restricción bloqueante? | CNST (severity:blocking) |
| 3 | **next_step_survival** | ¿Sobrevive el próximo paso? | STP |
| 4 | **claim_avoidance** | ¿Se evita el claim prohibido? | CLAIM, LIM |
| 5 | **current_future_distinction** | ¿Se distingue actual vs futuro? | STAT:current vs STAT:planned/future |

---

## 3. Escenarios

### Escenario A: reduced_window

| Parámetro | Valor |
|-----------|-------|
| Ventana | 512 tokens |
| Perfil | CORTEX-MIN |
| Expectativa | P0 sobrevive completo (FCS, OBJ, CNST, STP). CNST:blocking con survive:min intacto |

### Escenario B: middle_work

| Parámetro | Valor |
|-----------|-------|
| Ventana | 1000 tokens |
| Perfil | CORTEX-RECOVERY |
| Expectativa | P0+P1 sobreviven. CLAIM/LIM preservados. SES:last como evidencia. |

---

## 4. Métricas

| Métrica | Definición | Umbral objetivo |
|---------|------------|:---:|
| **Tasa de supervivencia P0** | Entradas P0 preservadas / entradas P0 totales | 100% |
| **Tasa de supervivencia P1** | Entradas P1 preservadas / entradas P1 totales (cuando existan) | ≥80% |
| **E contextual** | (FCS+OBJ+CNST+STP+WRK preservados) / tokens usados | Conceptual |
| **Falsos positivos** | Claims no verificables que sobrevivieron | 0 |
| **Falsos negativos** | CNST:blocking que no sobrevivió | 0 |
| **DIAG caption check** | Diagramas PUML en HCORTEX incluyen `' source: DIAG:<nombre>` | 100% |

---

## 5. Benchmarks de referencia

| Benchmark | Fecha | Tipo | Descripción |
|-----------|-------|------|-------------|
| **v2.1.0** | 2026-06-30 | científico reproducible | 4,840 runs · 11 métodos · 11 escenarios · 19 métricas · VIEW coverage 100% · reversibility True · `current` |
| **v2.0.0** | 2026-06-30 | científico reproducible | 4,840 runs · primeros 4 métodos v2 informativos · CLI v2.4.0 |
| **v1.0.0** | 2026-06-28 | científico reproducible | 4,840 runs · 11 métodos · 11 escenarios · 15 métricas · CLI v1.1.9 |
| **0.2** | — | offline/proxy | Primer benchmark de supervivencia contextual (referencia histórica) |
| **0.1b** | — | offline/proxy | `cortex_priority_pack` como experimento (referencia histórica) |
| **0.1** | — | offline/proxy | Evaluación inicial de densidad y compresión (referencia histórica) |

Las suites v1.0.0, v2.0.0 y v2.1.0 se publican en `benchmarks/` con corpus, scripts y resultados reproducibles. Las suites 0.1, 0.1b y 0.2 son artefactos generados por agentes externos como evidencia temprana. A v0.3.6 `cortex benchmark --list` y `cortex benchmark --suite <name>` permiten inventariar y validar las suites locales; la automatización de la metodología de supervivencia descrita en §2-§4 sobre nuevos escenarios es trabajo en curso.
