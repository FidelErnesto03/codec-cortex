# Migración al canon 1.0

Qué cambió respecto de 0.1/0.2, quién se ve afectado y cómo se corrige sin
adivinar. Todo lo de aquí está cubierto por vectores ejecutables.

---

## Resumen

| Cambio | Impacto | Acción |
|---|---|---|
| `$0: <título>` deja de ser válido | breaking | reemplazar por `$0` o `$0:<CAPA>` |
| Glosario sin capa emite `$0` desnudo | corrección | regenerar renders; el compilador ya acepta su salida |
| Aridad posicional estricta también en 0.1 | breaking solo en documentos laxos | ajustar celdas al contrato |
| `0.1` / `0.2` pasan a alias de lectura | informativo | escribir siempre `cortex:1.0` |
| `cortex:1` no es alias | informativo | usar `cortex:1.0` (`G007` si no) |

## 1. `$0: <título>` → `G042_GLOSSARY_HEADER_INVALID`

La gramática 1.0 define `glossary-header = "$0" | "$0:" capa`. Un título detrás
de `$0:` se descartaba en silencio; ahora se rechaza.

```diff
- $0: NEXUSCORP KB:KERNEL
+ $0:KERNEL
```

Si el título era informativo, no hay forma canónica de conservarlo: el glosario
clasifica, no documenta (`desc` de los sigilos cumple esa función).

**Afecta a documentos reales del repo** que se conservan intactos por ser corpus
de benchmark congelado: `bench/formats/cortex.cortex` y
`bench/lokky/corpus-migration/cortex.cortex`.

## 2. Glosario sin capa: `$0` desnudo

Antes, un documento sin `$0:<CAPA>` renderizaba un glosario **sin** la línea
`$0`, produciendo un HCORTEX que el propio compilador rechazaba. Ahora el render
emite `$0` desnudo —gramática válida— y el roundtrip cierra.

```cortex
$0
$0:format{cortex:1.0,encoding=UTF-8}
```

No requiere acción: los renders viejos de estos documentos deben regenerarse.

## 3. Aridad posicional estricta en 0.1

`0.1` toleraba más celdas que las declaradas en el contrato; `0.2` ya lo
rechazaba. En 1.0 es estricto en ambas superficies:

```cortex
REL:map{type:relacion,weight:M,pos:"from:text|to:text",focus:from,desc:"Relacion"}
$1: DATA
REL:x|A|B|C        →  I012_POSITIONAL_ARITY (3 celdas vs 2 campos)
```

Arreglo: reducir celdas o ampliar el contrato. Si la celda lleva un `|` interno,
va entrecomillada (sigue siendo **una** celda).

## 4. Alias de lectura

`0.1` y `0.2` siguen parseando; la escritura canónica es `cortex:1.0`. Los textos
normativos 0.x están archivados en
[`archive/2026-11/standard-0x/`](../archive/2026-11/standard-0x/).

## 5. Orden de atributos y hash

El orden editorial de atributos **no altera el hash**: C14N normaliza (campos de
contrato en orden declarado, extras de sigilos `open:true` por clave UTF-8). Es
la única pérdida "editorial" del catálogo: `L405_OPEN_ATTR_ORDER`. Si te importa
el orden visual, no lo pongas en la fuente: el canónico manda.

## Receta de migración

```bash
# 1. Copia de trabajo y detección de cabeceras inválidas
grep -rn --include='*.cortex' -E '^\$0:[[:space:]]' .

# 2. Reescribir la cabecera (revisar a mano si el título tenía información)
perl -0pi -e 's/^\$0:\s+[^:\n]*:([A-Z]+)\s*$/\$0:$1/mg; s/^\$0:\s+[^\n]*$/\$0/mg' doc.cortex

# 3. Normalizar al canon 1.0 (idempotente)
python -m codec_cortex migrate to-1.0 --apply doc.cortex

# 4. Verificar
python -m codec_cortex validate doc.cortex
python -m codec_cortex canonicalize doc.cortex > doc.canon.cortex
python -m codec_cortex loss-report doc.cortex
```

Criterio de éxito: `validate` exit 0, `canonicalize` idempotente y `loss-report`
sin `L499`.

## Qué NO cambia

- El significado de un documento 0.1/0.2 válido: sigue parseando y rinde el
  mismo AST.
- Los hashes de documentos ya canónicos 1.0.
- La sintaxis de ideas, secciones, escalares, slots y HCORTEX.
