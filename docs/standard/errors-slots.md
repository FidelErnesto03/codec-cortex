# Catálogo de diagnósticos CORTEX 0.2

**Document ID:** `CORTEX-ERRORS-0.2-001`
**Status:** `normative-draft`
**Authority:** `CORTEX-SPEC-0.2-001`

---

## 1. Contrato

Todo diagnostic normativo 0.2 contiene:

```json
{
  "code": "I053_REQUIRED_SLOT_MISSING",
  "severity": "error",
  "span": {"line": 8, "column": 1},
  "message": "Slot requerido 1 ausente en Idea KNW:codec."
}
```

Códigos y severidades son estables. Mensajes pueden traducirse.

## 2. Severidades

| Severidad | Efecto |
|---|---|
| `error` | impide conformidad |
| `warning` | utilizable con riesgo declarado |
| `info` | informativo |

## 3. Familias 0.2 (nuevas)

| Prefijo | Área |
|---|---|
| `L020`-`L025` | lexical de slots (nuevo en 0.2) |
| `G030`-`G041` | glossary de slots (nuevo en 0.2) |
| `I050`-`I058` | Idea slot-encoded (nuevo en 0.2) |
| `H401`-`H406`, `H481` | HCORTEX 0.2 (nuevo en 0.2) |

## 4. Catálogo 0.2

### 4.1 Lexical — slots

| Código | Condición | Severidad |
|---|---|---|
| `L020_HOMOGLYPH_MARKER` | marker estructural es `•`/`·`/`∙`/`●` en vez de `※` | error |
| `L021_INVALID_SLOT_INDEX` | dígito Unicode no-ASCII o espacio entre marker e índice | error |
| `L022_SLOT_INDEX_ZERO` | `※0` | error |
| `L023_SLOT_INDEX_LEADING_ZERO` | `※01` | error |
| `L024_SLOT_INDEX_SEPARATOR` | espacio entre índice y `:` (p.ej. `※1 :x`) | error |
| `L025_TRAILING_COMMA` | trailing comma antes de `}` en attrs/slots payload | error |

### 4.2 Glossary — slots

| Código | Condición | Severidad |
|---|---|---|
| `G030_SIGIL_MAP_MISSING` | sigilo con `encoding:slots` sin entrada en `$0:sigil-map` | error |
| `G031_DUPLICATE_SIGIL_MAP` | `$0:sigil-map` declarado más de una vez | error |
| `G032_SIGIL_MAP_INVALID_VALUES` | valor de sigil-map no es slot-contract válido | error |
| `G033_SLOTS_CONTRACT_MISSING` | entrada de sigil-map vacía o ausente para sigilo con `encoding:slots` | error |
| `G034_SLOT_POSITION_GAP` | posiciones no contiguas | error |
| `G035_DUPLICATE_SLOT_POSITION` | posición repetida en contrato | error |
| `G036_DUPLICATE_SLOT_NAME` | nombre repetido en contrato | error |
| `G037_UNKNOWN_FOCUS_SLOT` | focus no es posición existente o es opcional | error |
| `G038_OPEN_SLOTS_CONTRACT` | `open:true` con `encoding:slots` | error |
| `G039_SLOTS_ENCODING_ON_BODY_SHAPE` | `encoding:slots` sobre `type:cuerpo` o `type:bloque` | error |
| `G040_CONTRACT_SURFACE_CONFLICT` | `fields` y `encoding:slots` simultáneamente | error |
| `G041_SIGIL_MAP_ORDER` | sigil-map después de sigilo con `encoding:slots` | error |

### 4.3 Ideas — slots

| Código | Condición | Severidad |
|---|---|---|
| `I050_SLOT_IN_GLOSSARY` | `※` aparece en `$0` (glosario) | error |
| `I051_DUPLICATE_SLOT` | índice de slot repetido en una Idea | error |
| `I052_UNKNOWN_SLOT` | slot no declarado en contrato | error |
| `I053_REQUIRED_SLOT_MISSING` | slot requerido ausente | error |
| `I054_SLOT_OUT_OF_ORDER` | slots no en orden ascendente | error |
| `I055_NAMED_ATTR_IN_SLOT_IDEA` | attr nombrado dentro de Idea slot-encoded | error |
| `I056_PIPE_IN_SLOT_IDEA` | pipe `|` dentro de Idea slot-encoded | error |
| `I057_SLOT_INDEX_OUT_OF_RANGE` | índice > 2^31-1 o memoria requerida > límite | error |
| `I058_MIXED_SURFACE_VERSION` | `※` estructural en documento declarado 0.1 | error |

### 4.4 Ideas — type/enum (alias 0.2)

| Código | Condición | Severidad |
|---|---|---|
| `I012_TYPE_MISMATCH` | scalar no cumple tipo declarado en slot-contract | error |
| `G013_UNKNOWN_ENUM_REFERENCE` | enum `%X` referenciado en slot-contract no declarado | error |
| `I013_ENUM_VIOLATION` | atom fuera de enum en slot value | error |

### 4.5 HCORTEX 0.2

| Código | Condición | Severidad |
|---|---|---|
| `H401_MISSING_ENVELOPE` | falta `<!-- HCORTEX v=0.2 ... -->` | error |
| `H402_MALFORMED_ENVELOPE` | envelope con sintaxis inválida | error |
| `H403_MISSING_GLOSSARY_BLOCK` | falta `<!-- glossary -->` block | error |
| `H404_GLOSSARY_BLOCK_INCOMPLETE` | glossary block no contiene todas las declaraciones | error |
| `H405_SCHEMA_BLOCK_MALFORMED` | schema block con sintaxis inválida | error |
| `H406_SCHEMA_BLOCK_MISMATCH` | schema block no coincide con la sección | error |
| `H481_HIDDEN_COPY` | HCORTEX contiene `cortex-ast:`, `base64:` o shadow payload | error |

## 5. Inherited 0.1 codes

Los códigos 0.1 permanecen vigentes en 0.2. NO se redefinen aquí. Referencia: `errors.md`.

En particular, se reutilizan sin modificación:

- `L001`-`L010` (lexical 0.1)
- `S001`-`S007` (sintaxis 0.1; `S007_UNCLOSED_BODY` es alias 0.2 de `I014_UNCLOSED_BODY`)
- `G001`-`G028` (glossary 0.1; `G015_DUPLICATE_SYMBOL` para sigilos duplicados)
- `I001`-`I016` (Ideas 0.1; en particular `I005_UNKNOWN_FIELD`, `I006_DUPLICATE_FIELD`, `I006_DUPLICATE_IDEA_ADDRESS`, `I007_FIELD_ORDER`, `I008_REQUIRED_FIELD_MISSING`, `I009_FIELD_TYPE_MISMATCH`)
- `X001`-`X002`, `U001`-`U002`

## 6. Orden de prioridad

Cuando varias no conformidades se solapan, una implementación debería reportar primero:

1. decodificación y controles (U);
2. estructura de secciones (S);
3. glosario y sigil-map (G);
4. contrato de slots (G033-G037);
5. Idea y payload (I);
6. mixed-version (I058);
7. HCORTEX (H).

## 7. Extensión del catálogo

Una implementación puede agregar códigos propios con prefijo de proveedor, pero:

- no puede reutilizar un código normativo con otra condición;
- no puede degradar `error` a warning;
- debe preservar los códigos requeridos por el corpus 0.2.
