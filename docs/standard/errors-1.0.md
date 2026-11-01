# CORTEX 1.0 — Catálogo de Errores Cerrado

**Estado:** draft-1.0 (compañero de CORTEX-SPEC-1.0 §9)
**Invariante:** catálogo == emitidos ∪ reservados-declarados. Generado mecánicamente del código fuente de las 5 superficies (2026-11-01).

## Mapa código ↔ emisor ↔ superficie

| Código | python | go | node | rust | bash |
|---|---|---|---|---|---|
| G002_GLOSSARY_REOPENED | x | x | x | x | x |
| G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS | x | x | x | x | x |
| G005_FORMAT_REQUIRED | — | — | — | — | x |
| G006_DUPLICATE_FORMAT | x | x | x | x | x |
| G007_UNSUPPORTED_VERSION | x | x | x | x | x |
| G008_INVALID_CONTRACT | x | x | x | x | x |
| G010_FORMAT_REQUIRED | x | — | — | — | — |
| G011_ENCODING_REQUIRED | x | x | x | x | x |
| G012_INVALID_MICRO | x | x | x | x | x |
| G014_INVALID_ENUM | x | x | x | x | x |
| G015_DUPLICATE_SYMBOL | x | — | — | — | — |
| G016_SYMBOL_TYPE_REQUIRED | x | x | x | x | x |
| G017_UNKNOWN_SHAPE | x | x | x | x | x |
| G018_SYMBOL_WEIGHT_REQUIRED | x | x | x | x | x |
| G019_INVALID_WEIGHT | x | x | x | x | x |
| G020_SYMBOL_DESCRIPTION_REQUIRED | x | x | x | x | x |
| G021_ATTRS_CONTRACT_REQUIRED | x | x | x | x | x |
| G022_POSITIONAL_CONTRACT_REQUIRED | x | x | x | x | x |
| G023_RELATION_CONTRACT_TOO_SHORT | x | x | x | x | x |
| G024_FOCUS_REQUIRED | x | x | x | x | x |
| G025_UNKNOWN_FOCUS_FIELD | x | x | x | x | x |
| G030_SIGIL_MAP_REQUIRED | x | — | — | — | — |
| G031_DUPLICATE_SIGIL_MAP | x | — | — | — | — |
| G032_INVALID_SIGIL_MAP | x | — | — | — | — |
| G033_SLOT_CONTRACT_REQUIRED | x | — | — | — | — |
| G034_SLOT_CONTRACT_GAP | x | — | — | — | — |
| G035_DUPLICATE_SLOT_POSITION | x | — | — | — | — |
| G036_DUPLICATE_SLOT_NAME | x | — | — | — | — |
| G037_SLOT_FOCUS_UNRESOLVED | x | — | — | — | — |
| G038_SLOTS_OPEN_FORBIDDEN | x | — | — | — | — |
| G039_ENCODING_SHAPE_MISMATCH | x | — | — | — | — |
| G040_CONTRACT_SURFACE_CONFLICT | x | — | — | — | — |
| G041_SIGIL_MAP_ORDER | x | — | — | — | — |
| H401_MISSING_ENVELOPE | x | — | — | — | — |
| H401_UNSUPPORTED_HCORTEX_VERSION | x | — | — | — | — |
| H403_MISSING_GLOSSARY_BLOCK | x | — | — | — | — |
| H481_HIDDEN_COPY | x | — | — | — | — |
| I001_UNDECLARED_SYMBOL | x | x | x | x | x |
| I004_SHAPE_DELIMITER_MISMATCH | x | x | x | x | x |
| I005_UNKNOWN_FIELD | x | — | — | — | — |
| I006_DUPLICATE_FIELD | x | — | — | — | — |
| I006_DUPLICATE_IDEA_ADDRESS | x | — | — | — | — |
| I008_REQUIRED_FIELD_MISSING | x | — | — | — | — |
| I012_POSITIONAL_ARITY | x | x | x | x | x |
| I023_UNKNOWN_FIELD_TYPE | x | — | — | — | — |
| I050_SLOT_NOT_ALLOWED_IN_GLOSSARY | x | — | — | — | — |
| I051_DUPLICATE_SLOT | x | — | — | — | — |
| I052_UNKNOWN_SLOT | x | — | — | — | — |
| I053_MISSING_REQUIRED_SLOT | x | — | — | — | — |
| I054_SLOT_OUT_OF_ORDER | x | — | — | — | — |
| I055_NAMED_ATTR_IN_SLOT_IDEA | x | — | — | — | — |
| I056_PIPE_PAYLOAD_IN_SLOT_IDEA | x | — | — | — | — |
| I057_SLOT_INDEX_LIMIT | x | — | — | — | — |
| I057_SLOT_INDEX_OUT_OF_RANGE | — | x | x | — | x |
| I058_MIXED_SURFACE_VERSION | x | x | x | — | x |
| L001_INVALID_SYMBOL | x | x | x | x | x |
| L003_INVALID_KEY | x | x | x | x | x |
| L005_INVALID_STRING | x | x | x | x | x |
| L007_INVALID_LIST | x | x | x | x | x |
| L008_UNCLOSED_BRACE | — | — | x | — | — |
| L010_INVALID_ATOM | x | x | x | x | x |
| L020_HOMOGLYPH_MARKER | — | x | x | — | x |
| L020_INVALID_SLOT_MARKER | x | — | — | — | — |
| L021_INVALID_SLOT_INDEX | x | x | x | — | x |
| L022_SLOT_INDEX_ZERO | — | x | x | — | x |
| L022_SLOT_ZERO_FORBIDDEN | x | — | — | — | — |
| L023_SLOT_INDEX_LEADING_ZERO | — | x | x | — | x |
| L023_SLOT_LEADING_ZERO | x | — | — | — | — |
| L024_SLOT_INDEX_SEPARATOR | — | x | x | — | x |
| L024_SLOT_SEPARATOR_REQUIRED | x | — | — | — | — |
| S001_OPEN_EXTRA_FIELD | — | x | — | — | — |
| S002_DUPLICATE_SECTION | x | — | — | — | — |
| S002_EMPTY_SECTION | — | x | — | — | — |
| S003_INVALID_IDEA_HEAD | x | x | x | x | x |
| S003_NAMESPACE_SIGIL_COLLISION | — | x | — | — | — |
| S004_UNTITLED_SECTION | — | x | — | — | — |
| S005_CONTENT_OUTSIDE_SECTION | x | x | x | x | x |
| S005_PIPE_IN_TABLE_VALUE | — | x | — | — | — |
| S006_BLOCK_BOUNDARY_WHITESPACE | — | x | — | — | — |
| S006_INVALID_ATTRS | x | x | x | x | x |
| S007_BODY_BOUNDARY_WHITESPACE | — | x | — | — | — |
| S007_UNCLOSED_BODY | x | — | — | — | — |
| S999_INTERNAL_PARSE_FAILURE | x | x | x | x | x |
| U001_BOM_FORBIDDEN | x | x | x | x | x |

## Pérdidas declaradas HCORTEX (L4xx)

| Código | Pérdida | Emisor |
|---|---|---|
| L401 | Marcador de fence bloque | hcortex.from_hcortex (python) — pendiente en go/node/rs/bash |
| L402 | Comentarios fuera de glosario | hcortex.from_hcortex (python) |
| L403 | Whitespace intra-línea | hcortex renderer |
| L404 | CAPA ausente | hcortex.from_hcortex |
| L405 | Orden de attrs en sigilos open | hcortex.from_hcortex |

Cada pérdida emite entrada loss-report conforme a docs/schemas/loss-report.schema.json.

## Códigos reservados y colisiones conocidas

- `I006` colisiona en el codigo: `I006_DUPLICATE_FIELD` (attrs) e `I006_DUPLICATE_IDEA_ADDRESS` (direccion). Defecto conocido: la implementacion los distingue por contexto; una revision futura debe reasignar uno.
- `X002_REQUIRED_EXTENSION_UNSUPPORTED`, `G026_UNKNOWN_ENUM_REFERENCE`, `I049`, `L025_TRAILING_COMMA`: citados en spec/skill pero SIN emisor — `reserved` (detectables, pendiente implementar o retirar).
- `P17`: emisor real en slots.py (trailing comma) — fuera del esquema de familias; documentado aqui como codigo vigente.

## Códigos reservados

Espacio G0xx reservado para meta-declaraciones futuras; I05x para slots; L4xx para pérdida declarada. Un código reservado sin emisor se lista aquí, nunca implícito.
