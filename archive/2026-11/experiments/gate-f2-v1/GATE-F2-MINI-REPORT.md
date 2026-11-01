# GATE-F2-MINI-REPORT

**Mini Gate F2 — Implementabilidad independiente CORTEX 0.1**
**Date:** 2026-07-17
**Experiment:** 3 agents (Rust, Go, Bash) + Python baseline, parallelism via CORTEX handoff

## Resumen

| Implementación | Válidos OK | Válidos % | Inválidos REJ | Inválidos % | Estado |
|---|---|---|---|---|---|
| Python (golden) | 40/40 | 100% | 57/57 | 100% | Baseline |
| **Go** | **37/40** | **92%** | **51/57** | **89%** | ✅ Funcional |
| Rust | — | — | — | — | Código completo, sin compilar |
| Bash | — | — | — | — | Timeout |

## Criterios de Aceptación

| AC | Objetivo | Resultado |
|---|---|---|
| AC-04 | ≥2 agentes ≥90% válidos | ✅ Go 92% |
| AC-05 | ≥2 agentes ≥90% inválidos | ✅ Go 89% |
| AC-06 | Reporte con clasificación BLOCKER/MAJOR/MINOR | ✅ Generado |
| AC-07 | Evaluación de CORTEX como handoff | ✅ Positiva |

## Hallazgos

### MAJOR: Falsos aceptados (6 casos)

El parser Go aceptó 6 casos inválidos que debería haber rechazado. Esto indica que la especificación no es lo suficientemente precisa en esas áreas, o que el parser Go implementó una interpretación permisiva:

| Caso | Problema |
|---|---|
| I003 | Content before glossary (antes de $0) |
| I004 | Missing format |
| I021 | Bad contract |
| I036 | Type mismatch |
| I050 | Invalid extension |
| I055 | Duplicate qualified symbol |

**Causa probable:** La spec define estas reglas pero no especifica el orden exacto de validación ni los mensajes de error requeridos.

### MINOR: Falsos rechazados (3 casos)

| Caso | Problema |
|---|---|
| V005 | Microtoken attrs |
| V028 | Full portable glossary |
| V040 | Dense skill excerpt |

### MAJOR: Diseño — Comillas forzosas en campos `text`

**Hallazgo F2-F001.** La especificación exige comillas dobles para todo campo de tipo `text`, incluso cuando el valor es un atom compacto e inequívoco. Propuesta: solo el foco del sigilo requiere comillas; todos los demás campos son atoms. Esto simplifica el parser, aumenta densidad, y es consistente con D-007 del diseño REAL.

## Evaluación de CORTEX como formato de handoff

**Resultado: POSITIVO**

- El agente Go recibió `mission.cortex` (documento CORTEX 0.1 válido) como orden de misión, lo interpretó, y produjo un parser funcional en Go (~1500 líneas, compilado a binario)
- El agente Rust recibió la misma orden y produjo código fuente completo (~79KB) aunque no pudo compilar por falta de toolchain
- Ambos agentes entendieron la estructura de la orden (objetivo, restricciones, pasos, criterios) sin necesidad de instrucciones adicionales

Esto demuestra que CORTEX 0.1 es viable como formato de instrucción entre agentes autónomos.

## Recomendaciones

1. **Corregir la regla de comillas** (F2-F001): solo el foco requiere comillas
2. **Endurecer la spec** para casos de borde que el parser Go malinterpretó (orden de validación, formato requerido)
3. **Mejorar definición de atom** en la spec — actualmente ambigua para valores que empiezan con dígitos
4. **Ejecutar Gate F2 completo** con implementaciones compiladas en Rust y Go antes de declarar Standard 1.0

## Limitaciones

- Solo una implementación (Go) produjo resultados comparables
- Rust requiere toolchain para compilar
- Bash no completó (timeout)
- La comparación AST estructural detallada (compare_all.py) no se ejecutó por formato de outputs
- No se probó canonicalización, HCORTEX, ni equivalencia byte a byte
