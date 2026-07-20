# Glosario fundamental CORTEX 0.2

**Document ID:** `CORTEX-FUNDAMENTAL-GLOSSARY-0.2-001`
**Status:** `normative-draft`
**Authority:** `CORTEX-SPEC-0.2-001`

---

## 1. Propósito

Extiende el glosario fundamental 0.1 con declaraciones necesarias para slots explícitos. NO redefine las declaraciones 0.1; las referencia desde `fundamental-glossary-0.1.md`.

## 2. Meta-sección 0.2

| Elemento | Significado |
|---|---|
| `$0` | glosario local (heredado 0.1) |
| `$0:format{cortex:0.2,...}` | declaración de versión 0.2 |
| `$0:sigil-map{SIGIL:"<slot-contract>"}` | mapa de contratos de slots por sigilo |
| `$0:enum_*`, `$0:micro_*`, `$0:namespace_*`, `$0:extension_*`, `$0:<name>` | heredados 0.1 |

## 3. Meta-declaraciones 0.2

### 3.1 `$0:format`

```cortex
$0:format{cortex:0.2,encoding:UTF-8,language:es}
```

Claves obligatorias: `cortex` (DEBE ser `0.2`), `encoding` (DEBE ser `UTF-8`). Clave opcional: `language` y extras.

### 3.2 `$0:sigil-map`

```cortex
$0:sigil-map{KNW:"1=topic:text|2=content:text?"}
```

- Claves: nombres de sigilo (atom form, sin namespace).
- Valores: string quoted con slot-contract.
- DEBE aparecer antes de cualquier sigilo con `encoding:slots`.
- DEBE aparecer a lo sumo una vez.
- DEBE contener una entrada para cada sigilo con `encoding:slots`.

### 3.3 Sigilo con `encoding:slots`

```cortex
KNW:knowledge{type:attrs,encoding:slots,weight:B,focus:1,desc:"..."}
```

Clave nueva: `encoding` con valor `slots`. Sin `fields`. Sin `pos`. `focus` referencia la posición numérica del slot.

## 4. Slot-contract

```text
slot-contract = slot-entry *("|" slot-entry)
slot-entry    = position "=" name [":" type] ["?"]
position      = nonzero-digit *DIGIT
name          = (ALPHA / "_") *(ALPHA / DIGIT / "_" / "." / "-")
type          = "any" | "text" | "atom" | "int" | "dec" | "bool" | "null" | "list" | "%" enum-name
```

- `position` DEBE ser ASCII, positiva, sin ceros a la izquierda.
- Posiciones DEBEN ser contiguas desde 1.
- Posiciones únicas (G035). Nombres únicos (G036).
- `?` = opcional.

## 5. Combinaciones válidas por shape/encoding

| Shape | `encoding:slots` | Surface | Contrato |
|---|---|---|---|
| attrs | ausente | `{k:v,...}` (0.1) | `fields` |
| attrs | `slots` | `{※N:v,...}` | sigil-map entry |
| attrs-pos | ausente | `|c|c|c` (0.1) | `pos` |
| attrs-pos | `slots` | `{※N:v,...}` | sigil-map entry |
| relacion | ausente | `|c|c|c` (0.1) | `pos` (≥3) |
| relacion | `slots` | `{※N:v,...}` | sigil-map entry (≥3) |
| cuerpo | ausente | `{...}` o multiline (0.1) | ninguno |
| cuerpo | `slots` | **PROHIBIDO** (G039) | — |
| bloque | ausente | `{...}` multiline (0.1) | ninguno |
| bloque | `slots` | **PROHIBIDO** (G039) | — |

## 6. Combinaciones prohibidas

| Combinación | Código |
|---|---|
| `type:attrs, encoding:slots, fields:...` | `G040_CONTRACT_SURFACE_CONFLICT` |
| `type:cuerpo, encoding:slots` | `G039_SLOTS_ENCODING_ON_BODY_SHAPE` |
| `type:bloque, encoding:slots` | `G039_SLOTS_ENCODING_ON_BODY_SHAPE` |
| `encoding:slots, open:true` | `G038_OPEN_SLOTS_CONTRACT` |
| `encoding:slots` sin entrada en sigil-map | `G030_SIGIL_MAP_MISSING` |
| sigil-map después de sigilo con `encoding:slots` | `G041_SIGIL_MAP_ORDER` |

## 7. Claves de declaración de sigilo 0.2

Orden normativo extendido:

```text
type, encoding, weight, fields, pos, slots, focus, desc, open, namespace, version, <extras>
```

`encoding` y `slots` son nuevos. `slots` NO se usa como attr de sigilo (el contrato vive en sigil-map).

## 8. Herencias 0.1

Todo lo definido en `fundamental-glossary-0.1.md` (claves fundamentales, shapes, tipos de fields, peso, scalars, delimitadores, prohibiciones) se preserva sin cambios en 0.2.

## 9. Prohibiciones adicionales 0.2

- `※` en `$0` (glosario) → `I050_SLOT_IN_GLOSSARY`.
- `※` estructural en documento declarado 0.1 → `I058_MIXED_SURFACE_VERSION`.
- Homoglyphs (`•`, `·`, `∙`, `●`) como marker → `L020_HOMOGLYPH_MARKER`.
- Dígitos Unicode no-ASCII en slot index → `L021_INVALID_SLOT_INDEX`.
