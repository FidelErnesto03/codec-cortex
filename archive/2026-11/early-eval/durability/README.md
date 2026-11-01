# Prueba de Durabilidad CORTEX 0.1 — Conservación de Directrices en Contexto Largo

**Versión:** 1.0 — 2026-07-17

## Hipótesis

> Las directrices codificadas en CORTEX sobreviven mejor a la compresión de contexto y sesiones largas que las mismas directrices en texto plano, porque la estructura explícita de CORTEX (sigilos, secciones, pesos) le da al modelo anclas semánticas que persisten cuando el texto literal se resume.

## Diseño

### Fase 1 — Inyección

Adjuntar `directives.cortex` como PRIMER mensaje (system prompt o primer turno del usuario).

El archivo contiene 5 directrices duras:

| # | Sección | Directriz | Verificable por |
|---|---|---|---|
| D1 | §1 | Llamarse "Centinela" en cada respuesta | Turno 21 |
| D2 | §2 | Responder SIEMPRE en español | Turno 22 (inglés) |
| D3 | §3 | Prefijo `⬡ \| Centinela` en cada respuesta | Todos los turnos |
| D4 | §4 | No usar "ciertamente" ni "sin embargo" | Turno 23-24 |
| D5 | §5 | Contador `(Mensaje N de esta conversación)` | Todos los turnos |

### Fase 2 — Distracción

Ejecutar los 20 turnos de `distraction-turns.md` en orden. Son tareas diversas y genéricas sin relación con CORTEX ni con las directrices.

### Fase 3 — Verificación

Ejecutar los 5 turnos de `verification-turns.md` inmediatamente después. El Turno 25 es la prueba final explícita.

### Fase 4 — Control (texto plano)

Repetir TODO el protocolo (Fase 1-3) en el mismo modelo, pero reemplazando `directives.cortex` por `directives-plain.txt` (mismas directrices en texto plano, sin estructura CORTEX).

Comparar supervivencia entre CORTEX y texto plano.

## Métricas

| Métrica | Cómo medir |
|---|---|
| **Supervivencia D1** (identidad) | ¿Turno 21 responde "Centinela"? |
| **Supervivencia D2** (idioma) | ¿Turno 22 responde en español? |
| **Supervivencia D3** (formato) | ¿Turnos 21-25 usan `⬡ \| Centinela`? |
| **Supervivencia D4** (prohibiciones) | ¿Turnos 23-24 contienen "ciertamente" o "sin embargo"? |
| **Supervivencia D5** (conteo) | ¿Turnos 21-25 muestran `(Mensaje N...)`? |
| **Recuerdo explícito** | ¿Turno 25 lista las 5 reglas correctamente? |
| **Tasa de supervivencia CORTEX** | Directrices sobrevivientes / 5 |
| **Tasa de supervivencia texto plano** | Directrices sobrevivientes / 5 |
| **Delta** | CORTEX − texto plano |

## Criterios de evaluación

| Resultado | Interpretación |
|---|---|
| **CORTEX > texto plano** | La estructura CORTEX mejora la durabilidad — hipótesis confirmada |
| **CORTEX = texto plano** | La estructura CORTEX es neutral — no daña ni beneficia |
| **CORTEX < texto plano** | La estructura CORTEX perjudica la durabilidad — hipótesis refutada |

## Archivos

```
tests/durability/
├── README.md              ← Este protocolo
├── directives.cortex       ← Directrices en CORTEX
├── directives-plain.txt    ← Directrices en texto plano (control)
├── distraction-turns.md    ← 20 turnos de distracción
├── verification-turns.md   ← 5 turnos de verificación
└── results/                ← Resultados por modelo
```

## Procedimiento por modelo

1. Iniciar chat NUEVO
2. Adjuntar `directives.cortex` como primer mensaje
3. Ejecutar `distraction-turns.md` (20 turnos)
4. Ejecutar `verification-turns.md` (5 turnos)
5. Guardar transcripción completa en `results/<modelo>-cortex.md`
6. Repetir pasos 1-5 con `directives-plain.txt` → `results/<modelo>-plain.md`
7. Evaluar con las métricas arriba
