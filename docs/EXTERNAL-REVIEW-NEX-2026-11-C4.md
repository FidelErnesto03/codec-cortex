# EXTERNAL-REVIEW-NEX-2026-11 · C4 — la métrica que BLP-003 no mide (aún)

> Capítulo 4 de la revisión externa. Autor: Lokky (voz NEX, agente
> externo a ArqUX). Mismo método que C1–C3: cada afirmación con su
> experimento, y un criterio de falsación explícito.

## 1 · El hallazgo de la conversación de medición

El conteo neutral de tokens (`tiktoken/o200k_base`) sobre el corpus
sellado de BLP-003 dio:

| Formato | tokens | vs cortex |
|---|---|---|
| markdown | 1332 | −30% |
| plaintext | 1601 | −16% |
| yaml | 1793 | −6% |
| cortex | 1902 | — |
| json | 2385 | +25% |
| xml | 3239 | +70% |

Lectura naive: *"CORTEX no es compacto; markdown gana"*. Esa lectura es
correcta **y** parcial: mide `tokens/documento`, cuando el costo real en
interacción con la ventana de contexto es:

```
costo_real = tokens_por_lectura × N_reingestas
```

donde `N_reingestas` = cuántas veces el documento (o parte) debe volver a
entrar al contexto para sostener ideas, verificar cambios y referenciar
contenido a lo largo del trabajo.

## 2 · La hipótesis C4 (falsable)

> **C4-H:** En flujos que iteran sobre un documento (verificar, localizar,
> actualizar, citar entre turnos o sesiones), CORTEX consume menos tokens
> totales que los formatos narrativos, aunque cada lectura individual sea
> más cara — porque su estructura reduce N_reingestas.

El mecanismo propuesto, con su precio en tokens:

| Necesidad | Con markdown | Con CORTEX |
|---|---|---|
| "¿cambió algo?" | re-ingesta completa + comparación | hash semántico → **~0 tokens** |
| "¿QUÉ cambió?" | diff difuso, re-ingesta | hash por idea → re-ingesta **solo de `SIGILO:nombre`** (~50 tokens) |
| referenciar | "el riesgo de la fuga…" ambiguo | `RSK:R01` — dirección estable, cita exacta sin re-contexto |
| sostener estado | re-lectura para re-anclar | contrato de campos ancla cada idea |

## 3 · El punto de equilibrio (ya calculable)

Con los datos actuales del corpus:

    CORTEX paga 1902/1332 ≈ 1.43× por lectura vs markdown.
    Empieza a ahorrar cuando evita ~1.4 re-lecturas por documento.
    En un loop gobernado (verify por operación, digest por sesión,
    refresh de canon) ese umbral se cruza a la segunda verificación.

**La condición honesta:** si el uso es *"lee una vez, pregunta, olvida"*,
markdown gana siempre — C4-H requiere iteración. No es un claim universal;
es un claim sobre flujos gobernados/iterativos, que es donde CODEC-CORTEX
se posiciona.

## 4 · Experimento propuesto (para BLP-003 iteración 2, o BLP-004)

Celda nueva: **sesión multi-turno sobre documento mutable**, no lectura
única.

    escenario   un documento (corpus NexusCorp o similar) evoluciona
                durante K turnos: el agente debe verificar integridad,
                responder preguntas, aplicar modificaciones y citar ideas
    formatos    markdown vs cortex (mínimo; los demás son variantes)
    medición    tokens TOTales consumidos por sesión (ingesta + re-ingesta)
                y errores cometidos (referencia incorrecta, cambio no
                detectado, contenido alucinado)
    celdas      K ∈ {5, 20} turnos × formato × modelo × R=5

**Predicción C4-H (prerregistrable):** a K=5 los totales empatan o difieren
<20%; a K=20 CORTEX reduce ≥30% el total y produce menos errores de
referencia.

**Criterio de falsación:** si a K=20 markdown consume igual o menos
tokens totales con igual o menos errores, C4-H muere — y el
posicionamiento de CORTEX queda *"no más eficiente en contexto, solo
verificable"*, que sigue siendo un claim útil pero distinto.

## 5 · Lo que ya está medido y lo que falta

| Pieza | Estado |
|---|---|
| tokens/documento (6 formatos, o200k) | **medido** — `bench/lokky/tokens/` |
| pipeline cell→raw→score | **probado** — run-001 (MiMo×cortex, media 0.952) |
| costo por sesión multi-turno | **no medido** — este capítulo lo propone |
| comprensión comparada | pendiente celdas LLM de BLP-003 |

## 6 · Nota de método

Esta hipótesis nació de una objeción del Arquitecto durante la revisión de
los números de tokens — no de una intuición mía. La registramos así porque
BLP-003 fija un principio que aquí también aplica: *ningún claim sin
evidencia reproducible*. C4-H es, hoy, solo un claim bien formado con un
experimento definido y una condición de muerte explícita.
