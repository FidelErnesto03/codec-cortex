# HCORTEX 0.2 — Render y compile con slots

**Document ID:** `CORTEX-HCORTEX-0.2-001`
**Status:** `normative-draft`
**Authority:** `CORTEX-SPEC-0.2-001`, `C14N-0.2-001`

---

## 1. Propósito

HCORTEX 0.2 extiende HCORTEX 0.1 con:
- envelope `v=0.2`;
- hidden glossary block que captura `format`, `sigil-map`, y todos los sigilos con `encoding` y `slots`;
- schema blocks para attrs/slots (tabla), cuerpo (prose), bloque (fence);
- compile path que reconstruye el AST 0.2;
- invariante **no-hidden-copy** (H481).

Roundtrip HCORTEX 0.2 ↔ CORTEX 0.2 es byte-exacto en los 5 shapes, con y sin `encoding:slots`.

## 2. Envelope

```html
<!-- HCORTEX v=0.2 t=canonical k=corpus -->
```

`v=0.2` es obligatorio. `t=canonical` indica tipo. `k=corpus` indica kind. El envelope DEBE ser la primera línea no vacía.

Errores: `H401_MISSING_ENVELOPE`, `H402_MALFORMED_ENVELOPE`.

## 3. Hidden glossary block

```html
<!-- glossary -->
$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
$0:sigil-map{KNW:"1=topic:text|2=content:text?"}
KNW:knowledge{type:attrs,encoding:slots,weight:B,focus:1,desc:"Conocimiento verificable"}
<!-- /glossary -->
```

El block `<!-- glossary -->` ... `<!-- /glossary -->` contiene el glosario CORTEX 0.2 completo en su forma canónica C14N-0.2. Es **hidden** (HTML comment) pero **no es un shadow copy del AST**: es el glosario textual.

Errores: `H403_MISSING_GLOSSARY_BLOCK`, `H404_GLOSSARY_BLOCK_INCOMPLETE`.

## 4. Schemas

Cada sección se renderiza con un schema block:

```html
## §1: KNOW

<!-- schema:1 -->
| topic | content |
|---|---|
| CORTEX | Codec ideático lineal |
<!-- /schema:1 -->
```

Mapping shape → schema:

| Shape | Encoding | Schema |
|---|---|---|
| attrs | default | table (columnas = fields) |
| attrs | slots | table (columnas = slot names) |
| attrs-pos | default | table (columnas = pos names) |
| attrs-pos | slots | table (columnas = slot names) |
| relacion | default | table (columnas = pos names) |
| relacion | slots | table (columnas = slot names) |
| cuerpo | default | prose (§N: Title seguido de párrafo) |
| bloque | default | fence (``` ``` ... ```) |

Errores: `H405_SCHEMA_BLOCK_MALFORMED`, `H406_SCHEMA_BLOCK_MISMATCH`.

## 5. Render nominal

### 5.1 Render attrs/slots → table

Encabezado de tabla: `| name1 | name2 | ... |` con `|---|---|...|`. Cada Idea es una fila con sus valores en orden de contrato. Opcionales ausentes se emiten como celda vacía.

### 5.2 Render cuerpo → prose

```markdown
## §N: TITLE

TXT:idea
contenido del cuerpo en prosa
```

### 5.3 Render bloque → fence

```markdown
## §N: TITLE

BLK:idea
```
contenido verbatim del bloque
```
```

## 6. Compile path

1. Parse envelope. Si ausente o malformado → H401/H402.
2. Parse hidden glossary block con `parse_cortex_02`. Resultado: `Document` con `glossary` y `sections=[]`.
3. Para cada `## §N: TITLE` heading:
   - Parsear el schema block siguiente.
   - Reconstruir Ideas según shape/encoding y mapear a la sección.
4. Combinar glossary + sections en `Document` final.
5. Validar glosario completo (sigil-map, contratos, focus, etc.).
6. Validar invariante no-hidden-copy.

## 7. Invariante no-hidden-copy

El compilador RECHAZA el HCORTEX si contiene:

- `cortex-ast:` — shadow copy del AST como string/base64.
- `base64:` — payload binario embedded.
- Cualquier bloque etiquetado como `shadow`, `ast`, `internal`.

Estos disparan `H481_HIDDEN_COPY`. El compilador no produce un Document; lanza `HDiagnostic(code="H481_HIDDEN_COPY")`.

## 8. Roundtrip byte-exacto

Para todo Document 0.2 válido `D`:

```text
canonicalize_02(compile_hcortex_02(render_hcortex_02(D))) == canonicalize_02(D)
```

El roundtrip se valida para los 5 shapes con y sin `encoding:slots`. La validación incluye:

- AST equivalencia profunda;
- glosario equivalente;
- hash igual.

## 9. Diferencias con HCORTEX 0.1

- Envelope `v=0.2`.
- Hidden glossary block adicional (0.1 no lo tenía explícitamente).
- Slots columnas de tabla provienen del sigil-map.
- No-hidden-copy invariante explícita (H481).

## 10. Decisiones cerradas

```text
envelope              = <!-- HCORTEX v=0.2 t=canonical k=corpus -->
hidden glossary       = <!-- glossary --> block
schemas               = table (attrs/slots/pos), prose (cuerpo), fence (bloque)
no-hidden-copy        = H481 on cortex-ast: / base64: / shadow
roundtrip             = byte-exacto, 5 shapes, con/sin slots
```
