# C14N-0.2 — Canonicalización con slots

**Document ID:** `CORTEX-C14N-0.2-001`
**Status:** `normative-draft`
**Authority:** `CORTEX-SPEC-0.2-001`

---

## 1. Propósito

`C14N-0.2: CORTEX 0.2 structure-valid → bytes UTF-8 canónicos`. Extiende C14N-0.1 con:

- emisión de slots en orden ascendente por posición;
- microtoken expansion aplicada a slot atoms;
- bloque verbatim preservado (sin NFC);
- hash domain `CORTEX-C14N-0.2`.

Toda regla de C14N-0.1 (quoting, orden normalizable, NFC, microtokens) se preserva salvo las extensiones de slots.

## 2. Invariante de idempotencia

Para todo documento 0.2 válido `x`:

```text
canonicalize_02(canonicalize_02(x)) == canonicalize_02(x)
parse_02(canonicalize_02(x)) ≡structural parse_02(x)
```

Para `x`, `y` bajo CORTEX 0.2:

```text
x ≡structural y ⇔ canonicalize_02(x) == canonicalize_02(y)
```

## 3. Orden de slots

Los slots de una Idea slot-encoded se emiten en orden **ascendente por posición**:

```text
※1:valor,※2:valor,※3:valor
```

Si el source tiene slots desordenados, C14N los ordena. Si hay duplicados o gaps, el documento no es structure-valid y la canonicalización se rechaza antes de emitir bytes.

## 4. Emisión canónica de slots

Cada slot se emite como `※` + posición ASCII + `:` + valor-scalar-canónico:

```text
※1:valor
※42:"texto quoted"
※7:[a,b,c]
```

El valor escalar sigue las mismas reglas de quoting de C14N-0.1 según el tipo declarado en el contrato. `focus:text` siempre quoted; `text` no-focus bare cuando es inequívoco; los demás tipos siguen su literal canónico.

## 5. Hash

```text
hash = SHA-256( b"CORTEX-C14N-0.2" + b"\x00" + canonical_bytes )
```

- `b"\x00"` separa el domain tag de los bytes.
- `canonical_bytes` es UTF-8 sin BOM de la salida C14N-0.2.
- Hex lowercase, 64 caracteres.

## 6. Bloque verbatim

`bloque` se preserva byte-semánticamente. C14N-0.2 NO aplica NFC al contenido de `bloque`. Solo homologa line endings a LF. Espacios, TAB, blank lines y composición Unicode participan en equivalencia.

`※` dentro de `bloque` se preserva literalmente como contenido (no se interpreta como marker).

## 7. Cuerpo

`cuerpo` se normaliza a Unicode NFC. `※` dentro de cuerpo se preserva literalmente como contenido.

## 8. Microtokens

Si un slot atom coincide con un microtoken declarado, se expande a su `expand` lógico. La declaración `$0:micro_*` se preserva. La expansión no aplica dentro de strings, nombres, keys o sigilos.

## 9. Orden del glosario 0.2

El orden normalizable del glosario se extiende con sigil-map justo después de `$0:format`:

```text
1. $0 (capa) 
2. $0:format
3. $0:sigil-map         ← nuevo en 0.2
4. enum_*, micro_*, namespace_*, extension_*, otras (por nombre UTF-8 NFC)
5. sigilos (por identidad cualificada UTF-8 NFC)
```

`$0:sigil-map` debe aparecer exactamente una vez y antes de cualquier sigilo `encoding:slots`. Su ausencia es válida si ningún sigilo usa `encoding:slots`.

## 10. Emisión del sigil-map

```cortex
$0:sigil-map{KNW:"1=topic:text|2=content:text?"}
```

- Claves (nombres de sigilo) ordenadas por UTF-8 NFC.
- Valores: string quoted con el slot-contract intacto (sin normalizar espacios — el slot-contract es canónico).
- Si un sigilo con `encoding:slots` no aparece en sigil-map, el documento es inválido (G030); la canonicalización no se invoca.

## 11. Emisión del sigilo con `encoding:slots`

```cortex
KNW:knowledge{type:attrs,encoding:slots,weight:B,focus:1,desc:"..."}
```

Orden de claves del sigilo (extiende 0.1):

```text
type, encoding, weight, fields, pos, slots, focus, desc, open, namespace, version, <extras>
```

`encoding` aparece solo si es `slots`. `slots` no aparece como attr de sigilo (se declara vía sigil-map). `fields` y `pos` son mutuamente excluyentes con `encoding:slots`.

## 12. Invariantes preservadas de 0.1

- Una Idea regular por línea física.
- Un LF final exactamente.
- Sin BOM, sin CR, sin TAB estructural fuera de bloque.
- Sin comentarios, sin líneas vacías.
- Sin trailing spaces.
- Sin terminadores `;`.

## 13. Domain tag y prevención de colisión

El domain tag `CORTEX-C14N-0.2` difiere de `CORTEX-C14N-0.1`. Por ello, un documento 0.1 y un documento 0.2 con bytes canónicos idénticos producen hashes distintos. Esto previene confundir un hash 0.1 con un hash 0.2.

## 14. Pérdida

C14N-0.2 es estructuralmente no destructiva. El `loss report` normativo para una operación exitosa es:

```json
{"structuralLoss": false, "losses": []}
```

## 15. Decisions cerradas

```text
slot emission       = ascending by position
hash domain         = "CORTEX-C14N-0.2" || 0x00 || canonical
bloque              = verbatim, no NFC
cuerpo              = NFC, ※ preserved as content
microtokens         = expand in slot atoms
sigil-map emission  = after format, before other meta
sigil key order     = type, encoding, weight, fields, pos, slots, focus, desc, open, namespace, version, <extras>
```
