# CORTEX 0.2 — Modelo ideático con slots explícitos

**Document ID:** `CORTEX-SPEC-0.2-001`
**Versión del lenguaje:** `0.2`
**Status:** `normative-draft`
**Idioma normativo:** español
**Codificación:** UTF-8
**Autoridad superior:** `CORTEX-CONSTITUTION-001`
**Sustituye:** nada — coexiste con `CORTEX-SPEC-0.1` vía `$0:format{cortex:X}`.
**Compatibilidad:** Un documento CORTEX 0.1 permanece válido bajo el parser 0.1. Un documento CORTEX 0.2 requiere `$0:format{cortex:0.2,...}`.

---

## 1. Naturaleza

CORTEX 0.2 extiende CORTEX 0.1 con un eje de codificación **explícito por slots**. Un slot es una posición nombrada y enumerada dentro de la superficie de una Idea. La codificación por slots es **ortogonal** a los 5 shapes fundamentales (attrs, attrs-pos, cuerpo, bloque, relacion) y se activa mediante el atributo `encoding:slots` en la declaración del sigilo.

El marker de slot es el carácter Unicode `※` (U+203B, REGISTERED SIGN con circulación). Es el **único** marker normativo. Cuatro caracteres visualmente confundibles están PROHIBIDOS como marker (ver §16 — `L020_HOMOGLYPH_MARKER`).

CORTEX 0.2 no introduce un sexto shape, no reemplaza `$0` nominal, no reemplaza el AST nominal, no altera los 5 shapes fundamentales. Toda la semántica de 0.1 se preserva; 0.2 añade un eje.

## 2. Lenguaje normativo

Las palabras **DEBE**, **NO DEBE**, **REQUERIDO**, **DEBERÍA**, **NO DEBERÍA** y **PUEDE** son normativas. Su incumplimiento genera un diagnostic con código estable.

## 3. Dispatch por versión

El dispatch entre el parser 0.1 y el parser 0.2 lo decide **exclusivamente** el valor `cortex` de `$0:format`. El parser bootstrap:

1. Lee la primera línea no vacía que comience con `$0`.
2. Si encuentra `$0:format{...}` y `cortex:0.1` → `parse_cortex_01`.
3. Si encuentra `$0:format{...}` y `cortex:0.2` → `parse_cortex_02`.
4. Si la versión es ausente, desconocida o mayor que 0.2 → `G007_UNSUPPORTED_VERSION`.

**NO DEBE** usarse la presencia de `※` para decidir la versión. La presencia de `※` en un documento declarado `0.1` se valida en el parser 0.2 (ver §17 — `I058_MIXED_SURFACE_VERSION`).

## 4. Marker de slot

```text
slot-marker = "※"  ; U+203B, tres octetos UTF-8: E2 80 BB
```

El marker **DEBE** estar seguido inmediatamente por un índice entero positivo ASCII sin ceros a la izquierda (excepto el índice `0`, que está prohibido). Tras el índice sigue un `:` ASCII, seguido por el valor del slot.

```text
※1:valor
※42:"texto quoted"
```

Caracteres PROHIBIDOS como marker (homoglyphs):

| Código | Carácter | Nombre Unicode |
|---|---|---|
| `L020` | `•` | U+2022 BULLET |
| `L020` | `·` | U+00B7 MIDDLE DOT |
| `L020` | `∙` | U+2219 BULLET OPERATOR |
| `L020` | `●` | U+25CF BLACK CIRCLE |

La prohibición es léxica y absoluta: un documento con cualquiera de estos caracteres en posición estructural de marker es rechazado por `L020_HOMOGLYPH_MARKER`. Aparecer como contenido ordinario en strings/cuerpo/bloque es permitido.

## 5. Índice de slot

```text
slot-index = nonzero-digit *DIGIT
```

- **NO** se permite `0` como índice (`L022_SLOT_INDEX_ZERO`).
- **NO** se permiten ceros a la izquierda (`L023_SLOT_INDEX_LEADING_ZERO`).
- **DEBE** consistir de dígitos ASCII `0`-`9` únicamente. Dígitos Unicode no-ASCII (p.ej. arábigo-indio ٠١٢, devanágari ०१२) están PROHIBIDOS (`L021_INVALID_SLOT_INDEX`).
- Un espacio entre el marker y el índice está PROHIBIDO (`L021_INVALID_SLOT_INDEX`).
- Un espacio entre el índice y `:` está PROHIBIDO (`L024_SLOT_INDEX_SEPARATOR`).
- El índice **DEBE** ser acotado por la implementación antes de materializar memoria. El límite normativo es `2^31 - 1`. Un índice mayor (p.ej. `※999999999999999`) dispara `I057_SLOT_INDEX_OUT_OF_RANGE` antes de cualquier asignación.

## 6. Eje de codificación: `encoding:slots`

El atributo `encoding` se introduce en 0.2 como clave de declaración de sigilo. Valores:

| `encoding` | Significado |
|---|---|
| ausente | superficie 0.1 por defecto (attrs/posicional según shape) |
| `slots` | superficie con slots explícitos `※N:valor` |

`encoding:slots` **NO DEBE** declararse sobre un sigilo `type:cuerpo` o `type:bloque` (`G039_SLOTS_ENCODING_ON_BODY_SHAPE`). Cuerpo y bloque no tienen contrato posicional que slotificar.

`encoding:slots` **NO DEBE** combinarse con `fields` en attrs (`G040_CONTRACT_SURFACE_CONFLICT`). El contrato se declara una sola vez vía `$0:sigil-map`.

Para `attrs-pos` y `relacion`, `encoding:slots` reemplaza la superficie `|...|` por la superficie `{※1:...,※2:...}`. Una Idea slot-encoded NO usa pipes (`I056_PIPE_IN_SLOT_IDEA`).

## 7. `$0:sigil-map` — meta-declaración de contratos de slot

```cortex
$0:sigil-map{KNW:"1=topic:text|2=content:text?"}
```

Sintaxis del valor: un string quoted conteniendo `slot-contract`:

```text
slot-contract      = slot-entry *("|" slot-entry)
slot-entry          = position "=" name [":" type] ["?"]
position            = nonzero-digit *DIGIT
name                = (ALPHA / "_") *(ALPHA / DIGIT / "_" / "." / "-" )
type                = fundamental-type / "%" enum-name
```

Reglas:

- `position` **DEBE** ser positiva, ASCII, sin ceros a la izquierda.
- Las posiciones **DEBEN** ser únicas dentro de un contrato (`G035_DUPLICATE_SLOT_POSITION`).
- Los nombres **DEBEN** ser únicos dentro de un contrato (`G036_DUPLICATE_SLOT_NAME`).
- Las posiciones **DEBEN** ser contiguas a partir de 1 — sin huecos (`G034_SLOT_POSITION_GAP`).
- `?` marca el slot como opcional; sin `?` el slot es requerido.

`$0:sigil-map` **DEBE** declararse una sola vez (`G031_DUPLICATE_SIGIL_MAP`). **DEBE** declararse **ANTES** de cualquier sigilo con `encoding:slots` (`G041_SIGIL_MAP_ORDER`). **DEBE** contener un contrato para CADA sigilo con `encoding:slots` (`G030_SIGIL_MAP_MISSING`).

`$0:sigil-map` NO DEBE contener entradas para sigilos que no usen `encoding:slots` (advertencia no-normativa; no bloquea conformidad).

El focus de un sigilo con `encoding:slots` **DEBE** referenciar una posición existente en el contrato del sigil-map (`G037_UNKNOWN_FOCUS_SLOT`) y **DEBE** ser un slot requerido (`G037_UNKNOWN_FOCUS_SLOT` si referencia slot opcional).

## 8. Superficie de Idea slot-encoded

Para un sigilo `type:attrs, encoding:slots` o `type:attrs-pos, encoding:slots` o `type:relacion, encoding:slots`:

```cortex
SIGIL:nombre{※1:valor,※2:valor}
```

Reglas:

- **DEBE** usar braces `{...}`. Una Idea slot-encoded con pipes es `I056_PIPE_IN_SLOT_IDEA`.
- **DEBE** contener solo slots `※N:valor`. Un attr nombrado `campo:valor` dentro de una Idea slot-encoded es `I055_NAMED_ATTR_IN_SLOT_IDEA`.
- Los slots **DEBEN** aparecer en orden ascendente por índice (`I054_SLOT_OUT_OF_ORDER`).
- **NO DEBE** haber duplicados de índice (`I051_DUPLICATE_SLOT`).
- **NO DEBE** haber slots desconocidos al contrato (`I052_UNKNOWN_SLOT`).
- Los slots requeridos **DEBEN** estar presentes (`I053_REQUIRED_SLOT_MISSING`).
- Opcionales ausentes se omiten.
- Un slot opcional intermedio puede omitirse; un slot opcional final puede omitirse.
- **NO DEBE** haber `※` en `$0` (glosario). `$0` es nominal y no se slotifica (`I050_SLOT_IN_GLOSSARY`).

Ejemplo:

```cortex
$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
$0:sigil-map{KNW:"1=topic:text|2=content:text?"}
KNW:knowledge{type:attrs,encoding:slots,weight:B,focus:1,desc:"Conocimiento verificable"}
$1:KNOW
KNW:codec{※1:"CORTEX",※2:"Codec ideático lineal"}
```

Equivalente estructural en 0.1:

```cortex
KNW:codec{topic:"CORTEX",content:"Codec ideático lineal"}
```

## 9. AST nominal con posición

El AST 0.2 añade a `Idea.payload` el kind `"slots"` cuando `encoding:slots`:

```json
{
  "shape": "attrs",
  "encoding": "slots",
  "slots": [
    {"position": 1, "name": "topic", "value": {...scalar...}},
    {"position": 2, "name": "content", "value": {...scalar...}}
  ]
}
```

- `SymbolDef.encoding` se añade: `"slots"` o `null`.
- `SymbolDef.slot_contract` se añade: lista de `{position, name, type, required}` cuando `encoding=slots`, vacío en caso contrario.
- `ContractField.position` se añade a `ContractField` para slots.
- `FieldValue` (en attrs) preserva `kind`/`value`/`lexeme`.

El AST 0.2 es **nominal**: dos documentos con campos/posiciones equivalentes pero distinto `encoding` NO son structural-equivalent. Un attrs-0.1 y un attrs-slots-0.2 con el mismo contrato lógico producen ASTs distintos y hashes distintos.

## 10. Version dispatch (detalle)

El dispatcher expone `parse_cortex(source)`:

```python
def parse_cortex(source: str) -> Document:
    version = _bootstrap_version(source)  # lee $0:format{cortex:X}
    if version == "0.1":
        return parse_cortex_01(source)
    if version == "0.2":
        return parse_cortex_02(source)
    raise ParseError("G007_UNSUPPORTED_VERSION", ...)
```

`_bootstrap_version` escanea las primeras líneas hasta hallar `$0:format{...}`. No interpreta `※`.

## 11. Mixed-version detection — `I058_MIXED_SURFACE_VERSION`

Un documento declarado `cortex:0.1` NO DEBE contener `※` en posición estructural. Posición estructural significa:

- como primer carácter de una Idea payload dentro de `{...}`;
- como primer carácter de un attr-pair en un attrs payload;
- inmediatamente después de `{` o `,` en un braced-idea payload.

Aparecer `※` dentro de strings, cuerpo o bloque es **contenido ordinario** y NO dispara I058. Esta distinción la hace el parser 0.2 cuando inspecciona un documento declarado 0.1 (ver §17).

Un documento declarado `cortex:0.2` puede contener `※` libremente (estructural o no). Un documento declarado `cortex:0.2` puede usar superficies 0.1 (attrs nombrados, pipes) en sigilos sin `encoding:slots`. Esto NO es mixed-version: 0.2 admite ambas superficies simultáneamente, dispatchadas por `SymbolDef.encoding`.

`I058_MIXED_SURFACE_VERSION` **solo** dispara cuando:
1. El documento está declarado `cortex:0.1`.
2. `※` aparece en posición estructural en una Idea payload.

## 12. Hash domain — `CORTEX-C14N-0.2`

```text
hash = SHA-256( b"CORTEX-C14N-0.2" + b"\x00" + canonical_bytes )
```

- `b"\x00"` es el byte nulo de separación de dominio (igual que en C14N-0.1).
- `canonical_bytes` es la salida UTF-8 de C14N-0.2.
- Representación textual: `sha256:<64 hex lowercase>`.
- Dos documentos con idéntico AST pero distinto `cortex` declarado (0.1 vs 0.2) producen hashes distintos porque el domain tag difiere.

## 13. HCORTEX 0.2

Sobre (render AST → markdown) y (compile markdown → AST). Invariante: **no-hidden-copy**.

- Envelope: `<!-- HCORTEX v=0.2 t=canonical k=corpus -->`.
- Hidden glossary block: `<!-- glossary -->` ... `<!-- /glossary -->` conteniendo: format, sigil-map, todos los sigilos con `type`/`encoding`/`weight`/`focus`/`schema`/`open`/`desc`/`label`, slot/fields/pos contracts.
- Schema per section: `<!-- schema:N -->` ... `<!-- /schema:N -->` con tabla para attrs/slots, prose para cuerpo, fence para bloque.
- Compile path: parsea envelope + hidden glossary + schemas, reconstruye Document AST 0.2.
- **RECHAZO** de hidden copy: si HCORTEX contiene `cortex-ast:`, `base64:` o cualquier shadow payload, el compilador dispara `H481_HIDDEN_COPY` y rehusa compilar.

Roundtrip HCORTEX 0.2 ↔ CORTEX 0.2 es byte-exacto en los 5 shapes (attrs, attrs-pos, cuerpo, bloque, relacion) con y sin encoding:slots.

## 14. Projection fragments

Una sección CORTEX 0.2 puede declararse `$N:project:VIEW` para indicar que es una **proyección** generada desde otra sección. Las proyecciones son vistas derivadas; el AST 0.2 preserva el marcador pero no interpreta la derivación. Una proyección no se slotifica (sigilos con `encoding:slots` no pueden aparecer en secciones de proyección).

## 15. Migration contract — `0.1 → 0.2`

```text
inspect  → leer $0:format, validar que cortex=0.1, capturar source_sha256
plan     → producir plan {source_path, source_sha256, output_path, to_version=0.2}
apply    → verificar source_sha256 (P28), construir Document 0.2 preservando TODO
           el metadata de format (P25: language, type extras), escribir temp+fsync+rename,
           computar output hash, escribir migration-safety.json con equivalencia AST
           completa (P26: NO solo addresses)
verify   → parse source 0.1 + parse target 0.2, comparar AST completo + glosario
rollback → borrar output si existe (P27), verificar source_sha256 inalterado
```

**Política de pérdida**: la migración 0.1→0.2 NO es lossy. Todo attrs 0.1 con `fields` se preserva; el migrador NO convierte attrs a slots automáticamente (es opcional para el autor). Si el autor no añade `encoding:slots` y `$0:sigil-map`, el documento 0.2 es estructuralmente idéntico al 0.1.

**Atomic write**: temp file + `fsync` + atomic `rename`. Si el proceso se cae antes del rename, el output está ausente. Si se cae después del rename, el output está completo. **NO** hay estado parcial.

**Source hash precondition**: si `source_sha256` medido en `apply` difiere del medido en `plan`, `MigrationError("SOURCE_CHANGED_AFTER_PLAN")` (P28).

**AST equivalence**: `verify` compara el AST 0.1 (parseado con `parse_cortex_01`) contra el AST 0.2 (parseado con `parse_cortex_02`). La comparación es profunda: sections, ideas, payloads, scalars. Si solo las addresses coinciden pero el AST difiere, `verdict=fail` (P26).

**Rollback**: `rollback` borra el output_path si existe (P27). Verifica que source_sha256 no haya cambiado. **NO** toca el source original.

## 16. Catálogo de códigos diagnósticos 0.2

### 16.1 Lexical — `L020`-`L024`

| Código | Condición |
|---|---|
| `L020_HOMOGLYPH_MARKER` | marker estructural es `•`/`·`/`∙`/`●` en vez de `※` |
| `L021_INVALID_SLOT_INDEX` | dígito Unicode no-ASCII, o espacio entre marker e índice |
| `L022_SLOT_INDEX_ZERO` | `※0` |
| `L023_SLOT_INDEX_LEADING_ZERO` | `※01` |
| `L024_SLOT_INDEX_SEPARATOR` | espacio entre índice y `:` (p.ej. `※1 :x`) |

`L025_TRAILING_COMMA` — trailing comma antes de `}` en attrs/slots payload (`{a:1,}`). Reuso del código 0.1 `S006_INVALID_ATTRS` no es apropiado para 0.2; se introduce `L025` como código estable 0.2. (Reutilizable también para 0.1 via backport no-normativo.)

### 16.2 Glossary — `G030`-`G041`

| Código | Condición |
|---|---|
| `G030_SIGIL_MAP_MISSING` | sigilo con `encoding:slots` sin entrada en `$0:sigil-map` |
| `G031_DUPLICATE_SIGIL_MAP` | `$0:sigil-map` declarado más de una vez |
| `G032_SIGIL_MAP_INVALID_VALUES` | valor de sigil-map no es un slot-contract válido |
| `G033_SLOTS_CONTRACT_MISSING` | sigilo `encoding:slots` y su entrada de sigil-map está vacía o ausente |
| `G034_SLOT_POSITION_GAP` | posiciones no contiguas (1,3 sin 2) |
| `G035_DUPLICATE_SLOT_POSITION` | posición repetida en contrato |
| `G036_DUPLICATE_SLOT_NAME` | nombre repetido en contrato |
| `G037_UNKNOWN_FOCUS_SLOT` | focus no es una posición existente o es opcional |
| `G038_OPEN_SLOTS_CONTRACT` | `open:true` declarado con `encoding:slots` (slots no admite open) |
| `G039_SLOTS_ENCODING_ON_BODY_SHAPE` | `encoding:slots` sobre `type:cuerpo` o `type:bloque` |
| `G040_CONTRACT_SURFACE_CONFLICT` | sigilo con `fields` y `encoding:slots` simultáneamente |
| `G041_SIGIL_MAP_ORDER` | `$0:sigil-map` declarado después de un sigilo con `encoding:slots` |

### 16.3 Ideas — `I050`-`I058`

| Código | Condición |
|---|---|
| `I050_SLOT_IN_GLOSSARY` | `※` aparece en `$0` (glosario) |
| `I051_DUPLICATE_SLOT` | índice de slot repetido en una Idea |
| `I052_UNKNOWN_SLOT` | slot no declarado en contrato |
| `I053_REQUIRED_SLOT_MISSING` | slot requerido ausente |
| `I054_SLOT_OUT_OF_ORDER` | slots no en orden ascendente |
| `I055_NAMED_ATTR_IN_SLOT_IDEA` | attr nombrado dentro de Idea slot-encoded |
| `I056_PIPE_IN_SLOT_IDEA` | pipe `|` dentro de Idea slot-encoded |
| `I057_SLOT_INDEX_OUT_OF_RANGE` | índice > 2^31-1 o memoria requerida > límite |
| `I058_MIXED_SURFACE_VERSION` | `※` estructural en documento declarado 0.1 |

### 16.4 HCORTEX 0.2 — `H401`-`H406`, `H481`

| Código | Condición |
|---|---|
| `H401_MISSING_ENVELOPE` | falta `<!-- HCORTEX v=0.2 ... -->` |
| `H402_MALFORMED_ENVELOPE` | envelope con sintaxis inválida |
| `H403_MISSING_GLOSSARY_BLOCK` | falta `<!-- glossary -->` block |
| `H404_GLOSSARY_BLOCK_INCOMPLETE` | glossary block no contiene todas las declaraciones necesarias |
| `H405_SCHEMA_BLOCK_MALFORMED` | schema block con sintaxis inválida |
| `H406_SCHEMA_BLOCK_MISMATCH` | schema block no coincide con la sección |
| `H481_HIDDEN_COPY` | HCORTEX contiene `cortex-ast:`, `base64:` o shadow payload |

### 16.5 Inherited 0.1 codes

Los códigos 0.1 (`L001`-`L010`, `S001`-`S007`, `G001`-`G028`, `I001`-`I016`, `X001`-`X002`, `U001`-`U002`) permanecen vigentes en 0.2 con la misma semántica documentada en `errors.md`. NO se redefinen aquí. En particular:

- `I005_UNKNOWN_FIELD` — attr no declarado en contrato cerrado
- `I006_DUPLICATE_FIELD` — field repetido en attrs
- `I006_DUPLICATE_IDEA_ADDRESS` — dirección local repetida (mismo código, distinto sufijo; ver `errors.md`)
- `I007_FIELD_ORDER` — fields fuera del orden contractual
- `I008_REQUIRED_FIELD_MISSING` — falta field requerido
- `I009_FIELD_TYPE_MISMATCH` — scalar no cumple tipo
- `I012_TYPE_MISMATCH` — type mismatch (usado para slot type mismatch; alias de I009 en 0.1)
- `G013_UNKNOWN_ENUM_REFERENCE` (0.2) — enum referenciado en slot-contract no declarado
- `I013_ENUM_VIOLATION` (0.2) — atom fuera de enum en slot
- `S002_DUPLICATE_SECTION` — id de sección repetido
- `S007_UNCLOSED_BODY` — cuerpo/bloque sin cierre (0.2 alias; en 0.1 era `I014_UNCLOSED_BODY` — se respeta el código 0.1)
- `G015_DUPLICATE_SYMBOL` — sigilo declarado dos veces (ver `errors.md` 0.1)

`S007_UNCLOSED_BODY` es la designación 0.2; el parser 0.2 acepta tanto `S007` como `I014` (alias).

## 17. Mixed-version — algoritmo preciso

Cuando el dispatcher detecta `cortex:0.1`, el parser 0.2 ejecuta **además** del parseo 0.1 una verificación de superficie:

```python
def check_i058(source_01: str, doc_01: Document) -> Optional[ParseError]:
    """Para cada Idea en doc_01, inspeccionar el span de su payload en source.
    Si en ese span aparece ※ en posición estructural, devolver ParseError(I058)."""
```

**Posición estructural** se define operacionalmente:

1. Tras `{` o después de `,` dentro de un braced payload.
2. Como primer carácter de un pipe-cell (no aplica — pipes no son slotificados).

El escaneo se hace sobre el source string usando los source_spans del AST 0.1 (línea/col). NO se hace un `source.find("※")` global — eso dispararía falsos positivos en strings/cuerpo/bloque.

Implementación de referencia: el parser 0.2 expone `check_mixed_surface(source, doc01)` que retorna `None` o `ParseError("I058_MIXED_SURFACE_VERSION", line, col)`.

## 18. Conformidad

Una implementación declara conformidad CORTEX 0.2 cuando:

- Implementa el parser 0.2 con todos los códigos diagnósticos de §16.
- Implementa C14N-0.2 con la fórmula de hash de §12.
- Implementa HCORTEX 0.2 con la invariante no-hidden-copy de §13.
- Implementa la migración 0.1↔0.2 con las garantías de §15.
- Preserva el comportamiento 0.1 (parser 0.1, C14N-0.1, HCORTEX-0.1) sin modificaciones.
- Pasa el corpus 0.2 con 100% (no 95%, no conditional).
- Pasa los 29 probes independientes P01-P29.

## 19. Decisiones cerradas

```text
marker              = ※ U+203B (E2 80 BB)
slot-index          = nonzero-digit *DIGIT (ASCII only)
slot-contract       = position "=" name [":" type] ["?"] *( "|" ... )
sigil-map meta      = $0:sigil-map{SIGIL:"<slot-contract>"}
sigil-map order     = before any encoding:slots sigil
encoding attr       = "slots" or absent
shapes              = attrs|attrs-pos|cuerpo|bloque|relacion (unchanged)
slot on cuerpo/bloque = forbidden (G039)
fields + slots      = forbidden (G040)
slot idea surface   = braces {※N:v,...} always
pipe in slot idea   = forbidden (I056)
named attr in slot idea = forbidden (I055)
slot in $0          = forbidden (I050)
mixed surface in 0.1 = I058 (structural ※ only)
hash domain         = "CORTEX-C14N-0.2" || 0x00 || canonical
hidden copy in HCORTEX = H481
migration atomicity = temp + fsync + rename
migration AST equiv = full deep, not addresses-only
```
