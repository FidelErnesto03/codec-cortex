# EXTERNAL-REVIEW-NEX-2026-11 · C5 — supervivencia a compresión

> Capítulo 5. Autor: Lokky. Propuesto por el Arquitecto durante la revisión
> de C4: *"otro escenario real es la supervivencia a la compresión"*.
> Mismo método: lo medible se mide ya; lo que requiere LLM queda como celda.

## 1 · El escenario real

Cuando la ventana de contexto se llena, los harnesses compactan: resumen,
truncan, o evican contenido previo. La pregunta no es "¿cuánto cuesta
leer?" (C4) sino **"¿qué sobrevive?"** — y en qué estado.

## 2 · Lo ya medido: truncamiento mecánico

Corte del corpus NexusCorp al 25/50/75% por bytes. Ideas aún recuperables:

| Formato | 25% | 50% | 75% | Comportamiento |
|---|---|---|---|---|
| **cortex** | **3** | **18** | **29** | atómico: el corte cae entre líneas; lo que queda **parsea** |
| markdown | 2 | 4 | 6 | legible para humano, pero el corte cae a mitad de oración y **no hay señal de integridad**: no sabes qué se perdió |
| json | 0 | 0 | 0 | un corte en cualquier punto rompe el documento entero |
| xml | 0 | 0 | 0 | tags sin cerrar → todo inválido |
| yaml | 0 | 0 | 0 | indentación rota → todo inválido |

La propiedad diferencial de CORTEX no es densidad sino **atomicidad de
línea**: cada idea es una unidad completa que sobrevive o desaparece
entera — nunca a medias, nunca ambigua. Y el parse fallido es una *señal*:
sabes exactamente dónde murió el documento.

## 3 · Hipótesis C5-H (compresión semántica — requiere LLM)

> Tras una compaction (resumen generado por modelo), los valores exactos
> sobreviven mejor en CORTEX que en prosa: las líneas-sigilo ya son densas
> y direccionables, así que el compactador las lleva verbatim o las cita
> por `SIGILO:nombre`; la prosa se parafrasea y pierde precisión (fechas,
> severidades, nombres).

Contrahipótesis honesta: un compactador también puede *mutilar* la sintaxis
sigilo (cortar una línea a mitad) produciendo ideas rotas que el parser
rechaza — en ese caso CORTEX pierde contenido donde MD pierde solo precisión.
El experimento decide.

## 4 · Experimento (40 celdas listas — `bench/lokky/c5/`)

    doc truncado al 50%/75% → el agente compacta → responde chequeos de
    valores exactos (R01.sev, Nebula.due, …) → scoring contra GOLD
    K: 2 modelos × 2 formatos × 2 niveles × R=5

**Falsación:** si MD preserva igual o más valores exactos tras compaction,
C5-H muere y la atomicidad queda como ventaja *mecánica* solamente.

## 5 · Relación con el posicionamiento

C4 (costo multi-turno) y C5 (supervivencia) apuntan al mismo claim real:
CORTEX no compite en "barato de leer una vez" sino en **ciclo de vida del
documento dentro del contexto** — verificar, sobrevivir, re-ingestar
quirúrgicamente. Si ambos experimentos confirman, el posicionamiento honesto
es "formato de contexto durable", no "formato compacto".
