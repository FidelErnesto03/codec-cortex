# Decisiones de diseño de Fase 4

**Document ID:** `CORTEX-F4-DESIGN-DECISIONS-001`  
**Status:** `applied`

## D4-001 — Markdown restringido, no Markdown libre

**Decisión:** HCORTEX-CANONICAL define una forma única de headings, tablas, fences y comentarios.

**Alternativa rechazada:** aceptar cualquier Markdown semánticamente parecido.

**Razón:** equivalencia visual no permite compilación determinista ni bytes estables.

## D4-002 — Payload visible, no AST oculto

**Decisión:** tablas y fences visibles son la fuente del payload. Los comentarios conservan únicamente identidad y discriminadores.

**Alternativa rechazada:** insertar JSON completo del AST en comentarios.

**Razón:** esa técnica recupera una copia oculta y no demuestra que la edición humana sea reversible.

## D4-003 — Metadata por Idea

**Decisión:** cada Idea incluye `section`, `namespace`, `symbol`, `name` y `shape`; `bloque` agrega `media_type`.

**Alternativa rechazada:** inferir identidad solo del heading.

**Razón:** headings son editables y Markdown no distingue siempre contenido de identidad. La duplicación mínima permite detectar contradicciones, no resolverlas silenciosamente.

## D4-004 — Sin campo `order`

**Decisión:** el orden físico de secciones e Ideas es normativo.

**Alternativa rechazada:** conservar un índice oculto de orden.

**Razón:** un índice oculto podría ignorar una reordenación humana visible. El orden debe ser lo que el editor ve.

## D4-005 — Glosario visible completo

**Decisión:** `$0` se proyecta como tablas visibles y compilables.

**Alternativa rechazada:** omitirlo y depender del CORTEX fuente o de un perfil externo.

**Razón:** rompería portabilidad y autocontención.

## D4-006 — Scalars como lexemas CORTEX

**Decisión:** las celdas conservan lexemas CORTEX, no valores “bonitos” sin tipo.

**Alternativa rechazada:** renderizar todo como texto humano.

**Razón:** `0.750`, `0.75`, `"3"`, `3` y `current` deben permanecer distinguibles.

## D4-007 — `cuerpo` y `bloque` usan fences distintos

**Decisión:** `hcortex-text` y `cortex-block` son discriminadores visibles.

**Alternativa rechazada:** párrafos Markdown ordinarios para `cuerpo`.

**Razón:** párrafos ordinarios reinterpretan blank lines, listas, headings y HTML; el fence preserva el valor exacto.

## D4-008 — Fence variable para bloque

**Decisión:** el renderer usa una corrida de backticks mayor que cualquier corrida interna.

**Razón:** permite transportar bloques que contienen Markdown fences sin escape destructivo.

## D4-009 — READABLE es derivado con pérdida

**Decisión:** READABLE nunca hereda el claim reversible de CANONICAL.

**Razón:** ocultar glosario y metadata mejora lectura, pero elimina información necesaria para reconstruir.

## D4-010 — VIEW fuera del Gate

**Decisión:** no existe dependencia VIEW en los 40 casos canónicos.

**Razón:** la reversibilidad universal debe funcionar antes de cualquier presentación especializada.

## D4-011 — Contradicción produce error

**Decisión:** metadata, heading, glosario y tabla deben concordar. No existe precedencia implícita.

**Alternativa rechazada:** “metadata gana” o “visible gana”.

**Razón:** cualquiera de las dos políticas puede ocultar una edición accidental o maliciosa.

## D4-012 — Canonicalidad por re-render

**Decisión:** después de compilar, una implementación puede volver a renderizar y comparar bytes para determinar si el input era canónico.

**Razón:** reduce reglas duplicadas y convierte el renderer en normalizador verificable sin hacerlo autoridad superior a la especificación.

## D4-013 — Reporte de pérdida obligatorio

**Decisión:** toda transformación declara `reversible`, `structural_equivalence`, hashes, pérdidas y preservaciones.

**Razón:** “sin pérdida” debe ser una evidencia procesable, no una frase de documentación.

## D4-014 — Corpus neutral

**Decisión:** el corpus incluye dominios no vinculados a agentes y no contiene reglas privilegiadas para KNW/OBJ/etc.

**Razón:** los sigilos son fixtures locales, no vocabulario reservado del Core.
