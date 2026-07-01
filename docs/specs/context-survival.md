<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

<p align="center">
  <strong>CODEC-CORTEX</strong> — Context Survival Specification
  <br>
  <sub>SPECIFICATION · Survival Core · v0.3.5 · MIT · <a href="../../AUTHORS.md">Fidel Ernesto Lozada A.</a></sub>
</p>

---

> **NOTA DE ESTADO:** Este documento es especificación. A v0.3.5 los conceptos aquí definidos (atributo `survive`, priority pack P0-P5, perfiles MIN/RECOVERY/WORK/FULL, política de degradación, HCORTEX como render target) están implementados en el CLI (`cortex verify`, `cortex render`, `cortex canonicalize`, `cortex inspect`) y en el parser determinista. La métrica de eficiencia contextual sigue siendo conceptual: la automatización de benchmarks de supervivencia está planificada pero no es bloqueante para el uso actual del protocolo.

**Abstract:** Documento único que consolida los fundamentos del Survival Core de CODEC-CORTEX: atributo `survive`, priority pack P0-P5, perfiles conceptuales de carga, política de degradación, HCORTEX como render target, y métrica de eficiencia contextual.

| | |
|---|---|
| **Author** | Fidel Ernesto Lozada A. — Systems Engineer / MSc. Management Sciences |
| **Repository** | github.com/FidelErnesto03/codec-cortex |
| **License** | MIT |
| **Version** | v0.3.5 (conceptos implementados en CLI; benchmark automatizado planeado) |
| **Language** | Español |

---

## 1. Atributo `survive`

El atributo `survive` gobierna qué entradas `.cortex` se preservan cuando el contexto se reduce.

| Nivel | Significado | Presupuesto típico | Entradas típicas |
|-------|-------------|:---:|------------------|
| `min` | Supervivencia mínima | ~300 tokens | CNST con `severity:blocking`, IDN |
| `recovery` | Recuperación de estado | ~1000 tokens | OBJ activos, RSK |
| `work` | Continuidad de trabajo | ~3000 tokens | FCS, STP, WRK, NXT |
| `full` | Contexto completo | Sin límite | SES, REF, histórico |

**Reglas de asignación:**

| Condición | Nivel sugerido |
|-----------|:---:|
| CNST con `severity:blocking` | `min` |
| OBJ activo (`status:in_progress`) | `recovery` |
| FCS, WRK, STP — estado de trabajo actual | `work` |
| Documental, histórico, referencia | `full` |
| Entrada sin `survive` explícito | Válida — compatibilidad progresiva |

---

## 2. Priority Pack P0-P5

Cuando la ventana de contexto se reduce, el agente preserva entradas por prioridad cognitiva, nunca por posición. **Carga: P0→P5. Degradación: P5→P1. P0 nunca se elimina.**

| Nivel | Nombre | Presupuesto | Preserva |
|:---:|--------|:---:|----------|
| **P0** | Supervivencia mínima | ~300t | `FCS`, `OBJ`, `CNST`, `STP` |
| **P1** | Estado operativo | ~600t | `WRK`, `AUD`, `RSK`, `NXT` (cuando existan) |
| **P2** | Honestidad y límites | ~1Kt | `CLAIM`, `LIM`, `KNW:active`, `LNG:critical` (cuando existan) |
| **P3** | Evidencia reciente | ~2Kt | `SES:last`, `STAT`, `VAL`, `RES`, `FIND` (cuando existan) |
| **P4** | Referencias críticas | ~3Kt | `REF:critical`, `DOC`, `ART` (cuando existan) |
| **P5** | Contexto ampliado | Sin límite | `DIAG`, `TBL`, referencias largas, histórico |

**Reglas de aplicación:**

| Regla | Descripción |
|-------|-------------|
| Anti-truncado posicional | Nunca reducir por cola/cabecera si existe política de prioridad |
| P0 inmutable | FCS, OBJ, CNST, STP nunca se eliminan |
| CNST:blocking | Sobrevive incluso en CORTEX-MIN |
| CLAIM/LIM | Sobreviven al menos hasta RECOVERY |
| "Cuando existan" | Sigilos no presentes = nivel con menos entradas (no es error) |

---

## 3. Perfiles conceptuales de carga

Cuatro perfiles definidos por prioridad mínima, no por lista cerrada de sigilos.

| Perfil | Propósito | Prioridad | Presupuesto |
|--------|-----------|:---:|:---:|
| **CORTEX-MIN** | Emergencia. Solo identidad y reglas de seguridad | P0 | ~300t |
| **CORTEX-RECOVERY** | Recuperación tras interrupción o nueva sesión | P0+P1 | ~1000t |
| **CORTEX-WORK** | Continuidad de trabajo sin re-leer historia | P0+P1+P2 | ~3000t |
| **CORTEX-FULL** | Memoria completa sin restricción de ventana | P0–P5 | Sin límite |

**Selección directa por presupuesto:** sin cadena secuencial. Saltar directamente al perfil requerido.

| Presupuesto | Perfil |
|:---:|--------|
| ≤512 tokens | CORTEX-MIN |
| ≤1000 tokens | CORTEX-RECOVERY |
| ≤3000 tokens | CORTEX-WORK |
| >3000 tokens | CORTEX-FULL |

---

## 4. HCORTEX como render target

HCORTEX no es un perfil `.cortex`. Es un render target efímero generado desde el perfil activo.

| Regla | Descripción |
|-------|-------------|
| No es persistencia | Se genera desde el perfil activo; no se almacena como `.cortex` |
| Render bajo demanda | Cualquier perfil puede renderizar a HCORTEX |
| Trazabilidad mínima | P0/P1 incluidos deben tener representación en HCORTEX |
| Origen explícito | Cada sección HCORTEX indica su sigilo `.cortex` de origen |

**Equivalencias recomendadas (P0/P1):**

| `.cortex` | HCORTEX |
|-----------|---------|
| `FCS` | Foco actual |
| `OBJ` | Objetivo |
| `CNST` | Restricciones |
| `WRK` | Estado operativo |
| `STP` / `NXT` | Próximo paso |
| `AUD` / `RSK` | Evidencia / Riesgos |
| `CLAIM` / `LIM` | Límites de afirmación |

---

## 5. Política de degradación

Cadena conceptual: `CORTEX-FULL → CORTEX-WORK → CORTEX-RECOVERY → CORTEX-MIN`. Selección operativa directa.

| Al degradar | Se reduce o elimina |
|-------------|---------------------|
| FULL → WORK | DIAG, TBL largos, REF largos, SES históricos |
| WORK → RECOVERY | KNW→KNW:active, LNG→LNG:critical, REF→REF:critical |
| RECOVERY → MIN | SES:last, AUD, RSK, NXT, STAT. Solo P0 |

**Nunca desaparece:**

| Condición | Protegidos |
|-----------|------------|
| Cualquier perfil | CNST con `severity:blocking` y `survive:min` |
| Cualquier perfil | FCS, OBJ, STP (P0 inmutable) |
| Al menos RECOVERY | CLAIM, LIM que bloqueen afirmaciones públicas |

---

## 6. Métrica de eficiencia contextual

```
E = Critical_Context_Recovered / Tokens_Used
```

La eficiencia se mide por cuántas decisiones, restricciones, foco, objetivo, estado y próximo paso sobreviven por token usado. El conjunto exacto de campos críticos se estabilizará con benchmarks posteriores. A v0.3.5 el parser determinista y el CLI ya existen — la métrica sigue siendo conceptual en tanto no se publiquen suites automatizadas de supervivencia que la calculen de forma reproducible.
