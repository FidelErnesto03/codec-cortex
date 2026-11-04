# C4 — costo por sesión multi-turno (hipótesis C4-H)

Escenario: 20 turnos (verify/locate/update/cite) sobre el corpus
NexusCorp en markdown vs cortex migrado. Modelo de costo determinista en
`sim/cost-model.json`.

## Resultado del modelo (sin LLM — solo contabilidad de tokens)

| Sesión | markdown | cortex | ratio |
|---|---|---|---|
| K=5  | 7104 | 2077 | **3.42×** a favor CORTEX |
| K=20 | 23532 | 2613 | **9.01×** a favor CORTEX |

El cruce ocurre antes de lo predicho en C4: ya en K=5 CORTEX ahorra ~70%.

## Lo que el LLM-run debe validar (supuestos del modelo)

1. md realmente requiere re-ingesta para verify/locate (sin hash ni
   direcciones, el agente no tiene otra vía fiable)
2. cortex realmente permite re-ingesta quirúrgica por `SIGILO:nombre`
   (¿el agente la usa, o re-ingiere todo por hábito?)
3. errores de referencia: ¿MD produce más alucinación de citas?

## Falsación (de C4 §4)

Si a K=20 el total real de markdown ≤ cortex con ≤ errores → C4-H muere.

## Celdas

`cells/c4-cells.json` — 40 celdas (2 modelos × 2 formatos ×
K{5,20} × R=5). Contrato: cada celda materializa `raw/<cell_id>.txt` con
el transcript multi-turno y metadatos de tokens por turno.
