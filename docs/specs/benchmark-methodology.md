<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

<p align="center">
  <strong>CODEC-CORTEX</strong> — Benchmark Methodology
  <br>
  <sub>SPECIFICATION · Survival Core · MIT · <a href="../../AUTHORS.md">Fidel Ernesto Lozada A.</a></sub>
</p>

---

**Abstract:** Metodología de benchmark centrada en supervivencia de decisiones — no en ocurrencia de términos. Define 5 preguntas de evaluación, 2 escenarios, y métricas de tasa de supervivencia contextual. Los benchmarks 0.1, 0.1b y 0.2 existen como evidencia offline/proxy.

| | |
|---|---|
| **Author** | Fidel Ernesto Lozada A. — Systems Engineer / MSc. Management Sciences |
| **Repository** | github.com/FidelErnesto03/codec-cortex |
| **License** | MIT |
| **Version** | specification draft |
| **Language** | Español |
| **Cycle** | CORTEX-CONSOLIDATION-001 |

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

---

## 5. Benchmarks de referencia

| Benchmark | Fecha | Tipo | Descripción |
|-----------|-------|------|-------------|
| **0.1** | — | offline/proxy | Evaluación inicial de densidad y compresión |
| **0.1b** | — | offline/proxy | cortex_priority_pack como experimento |
| **0.2** | — | offline/proxy | Primer benchmark de supervivencia contextual |

Estos benchmarks existen como artefactos generados por agentes externos. La automatización requiere parser. La metodología aquí definida será aplicable cuando exista codec.
