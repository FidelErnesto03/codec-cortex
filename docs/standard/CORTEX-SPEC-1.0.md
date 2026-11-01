# CORTEX 1.0 — Especificación Normativa

**Estado:** draft-1.0 (pendiente de ratificación del Arquitecto)
**Reemplaza:** CORTEX-SPEC-0.1 (draft-for-independent-implementation) y CORTEX-SPEC-SLOTS (0.2) como referencia normativa única. 0.1 y 0.2 permanecen legibles como alias de lectura (§11).
**Canon:** este documento es el contrato del lenguaje. Si spec e implementación difieren, la discrepancia es un bug en uno de los dos — nunca una ambigüedad aceptable.

---

## §1 Naturaleza y axiomas

CORTEX es un codec ideático lineal: un documento es una secuencia de **Ideas**, cada una expresando una unidad atómica de significado. Axiomas:

1. **Una línea física por idea regular.** Excepción única: ideas `cuerpo`/`bloque` con payload delimitado `{...}` (§4.3), que siguen siendo UNA idea aunque ocupen varias líneas.
2. **Declaración explícita.** Ningún sigilo se usa sin declararse en el glosario (`I001`).
3. **Determinismo.** Todo artefacto derivado (AST, forma canónica, hash, render HCORTEX) es función pura del documento fuente. Prohibidos: hora, locale, orden de hash de implementación, azar.
4. **Sin inferencia de versión.** El dialecto se declara en `$0:format{cortex:X}` — nunca se adivina por contenido.
5. **Permanencia.** Lo válido en 1.0 es válido siempre (§11.2).

## §2 Documento

```
$0:KERNEL                      ← encabezado, primera línea no vacía
$0:format{cortex:1.0,encoding:UTF-8[,language:<tag>]}
[$0:sigil-map{...}]            ← obligatorio si hay sigilos con encoding:slots
[$0:enum_<n>{values:"a|b|c"}]
[$0:micro_<t>{expand:<atom|"…">}]
[$0:namespace_<a>{prefix:<iri>}]
[$0:extension_<n>{...}]
[SIGIL:nombre{contract attrs}]  ← una declaración por sigilo usado fuera de $0
$1: TÍTULO[:CAPA]
<Ideas>
$2: TÍTULO[:CAPA]
<Ideas>
```

- `$0` aparece exactamente una vez, al inicio (`G002` si reaparece).
- `cortex:1.0` es la única declaración canónica nueva. `0.1`/`0.2` se aceptan en lectura (§11.1). Valor bare (no quoted) es la forma canónica.
- `encoding:UTF-8` requerido (`G011`). BOM prohibido (`U001`).
- Secciones `$N: TÍTULO[:CAPA]`, N entero positivo, sin repetir (`S002`). Subsecciones `$N.M` válidas. CAPA opcional: `KERNEL|CORE|KNOW|DATA|FLOW|CACHE` — metadata sin semántica de runtime. Default DATA para N≥2.
- Ideas antes de `$0` o entre meta y `$0:format`: error (`I003`, `G002`).

## §3 Glosario

Cada sigilo usado fuera de `$0` se declara como idea dentro de `$0`:

```
SIGIL:nombre{type:<shape>,weight:<L|M|H>,focus:<campo|"$body">,
             desc:"...",open:<true|false>,
             fields:"a:text|b:int|c:atom|d:atom?"      ← si type:attrs
             pos:"a:text|b:text|c:int"                ← si type:attrs-pos|relacion
             [slots:"1=a:text|2=b:text",encoding:slots] ← eje slots (§5)
             [schema:table]}
```

- `type` ∈ los 5 shapes (§4). `weight`: L|M|H.
- `focus`: para `attrs`/`attrs-pos`/`relacion` debe nombrar un campo del contrato (`G025`); para `cuerpo`/`bloque` es `$body`.
- Contrato `attrs`: `fields` requerido (`G021`). `attrs-pos`/`relacion`: `pos` requerido (`G022`); `relacion` exige ≥3 campos (`G023`).
- `open:true` = sigilo extensible (attrs fuera de contrato permitidos).
- Declaraciones auxiliares: `enum_<n>` (atom cerrado), `micro_<t>` (token expandible), `namespace_<a>` (alias→IRI para `ns::SIGIL:`), `extension_<n>` (requiere `open` correspondiente — `I049` si se usa extensión no declarada).

## §4 Shapes (5)

| Shape | Sintaxis | Payload |
|---|---|---|
| `attrs` | `SIG:name{k:v,k:v}` | pares clave-valor acotados al contrato `fields` |
| `attrs-pos` | `SIG:name\|c1\|c2\|c3` | celdas posicionales acotadas al contrato `pos` |
| `cuerpo` | `SIG:name{texto}` o multilínea `{...}` | texto semántico libre (NFC) |
| `bloque` | `SIG:name{...}` | texto verbatim (sin NFC) |
| `relacion` | `SIG:name\|from\|to\|w` | ≥3 celdas posicionales (contrato `pos`) |

### §4.1 Aridad posicional estricta (norma 1.0)

Para `attrs-pos` y `relacion`: `requeridos ≤ celdas ≤ len(contrato)` — `I012_POSITIONAL_ARITY` en ambos extremos. **Cambio respecto a 0.1:** el parser 0.1 toleraba overflow; en 1.0 es error. Un doc 0.1 con overflow es reparable con `migrate to-1.0` + edición (la migración no rescribe celdas).

### §4.2 Escalares en celdas/payload

`atom` (sin comillas, `[a-zA-Z0-9_.-]+`), `string` (quoted, escapes `\"` `\\` `\n` `\t`), `int`, `float`, `boolean` (`true|false`), `null`. Microtoken `<t>` expande via `micro_<t>`. Enum valida contra `enum_<n>`. `|` dentro de una celda exige string quoted.

### §4.3 Multilínea

`SIG:name{` sola abre payload multilínea; cierra la primera línea que es exactamente `}`. Contenido interior verbatim para `bloque`, NFC para `cuerpo`. Delimitador mal formado: `I004`.

## §5 Eje de codificación slots

Integrado de 0.2 como **sección normativa**, no dialecto aparte:

- `$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}` — obligatorio antes del primer sigilo con `encoding:slots` (`G041`).
- Sigilo con `encoding:slots` declara `slots:"N=campo:tipo"`; usos codifican celdas como `※N:valor`.
- Orden de slots por `order` del sigil-map (ascending|declared). Slot no declarado: `I05x`. Referencia `※` estructural en doc sin sigil-map: error de superficie mezclada (`I058`).
- `cuerpo`/`bloque` nunca usan slots — sus payloads son opacos.

## §6 Namespaces y extensiones

- `ns::SIGIL:name` calificado — `ns` debe estar declarado via `namespace_<a>` (`I001`/G0xx si no).
- `!:` es namespace reservado interno (sistema); no redeclarable.
- Extensiones nombradas via `extension_<n>`; sigilos extensión requieren `open:true` o contrato que las admita.

## §7 C14N-1.0 — canonicalización y hash

Función pura `canonicalize(doc) → bytes`:

1. Orden de secciones: `$0` primero; luego `$N` ascendente (subsecciones `$N.M` ordenadas `N` luego `M` numérico).
2. Dentro de sección: ideas en orden documental — **el orden canónico se fija aquí como orden documental** (cierra el "pendiente de Fase 3" de 0.1).
3. Glosario serializado en orden de declaración: format, sigil-map, enums, micros, namespaces, extensions, meta, sigilos.
4. Escalares normalizados: NFC para `cuerpo`/strings; `bloque` verbatim; atoms lowercase-preservado; números en forma canónica.
5. Hash: `SHA-256("CORTEX\x00" + canonical_bytes)` — dominio separado de cualquier hash de contenido raw.
6. Idempotencia obligatoria: `canonicalize(parse(canonicalize(parse(src)))) == canonicalize(parse(src))` — vector D1.

## §8 HCORTEX-1.0 — proyección humana determinista

`render(doc) : Document → bytes` es **función pura del AST**:

- Mismo AST → mismos bytes, en cualquier superficie (Python/Go/Node/Rust/Bash) — vector D3.
- Sin hora, locale, RNG, ni orden de hash interno.
- Orden: secciones por `$N` ascendente, ideas en orden documental, glosario por orden de declaración.

### §8.1 Clases de roundtrip

| Clase | Definición |
|---|---|
| `LOSSLESS` | `canonicalize(from_hcortex(render(x))) == canonicalize(x)` |
| `DECLARED-LOSS` | roundtrip diverge solo en pérdidas del catálogo §8.2, cada una reportada |

Ninguna tercera clase. Un render que pierde AST sin declararlo viola **H481** (sin copia oculta — norma 1.0): ningún render válido esconde información semántica no representada.

### §8.2 Catálogo de pérdidas declaradas (L4xx)

| Código | Pérdida | Caso |
|---|---|---|
| `L401` | Marcador de fence bloque | bloque ``` fence cuyo marcador no sobrevive from-hcortex |
| `L402` | Comentarios `#` fuera de glosario | no representados en AST |
| `L403` | Whitespace intra-línea no significativo | colapsado por normalización |
| `L404` | CAPA ausente | sección sin capa declarada no la recupera |
| `L405` | Orden de atributos fuera de contrato | en sigilos `open:true` |

Cada pérdida emite entrada en `loss-report` conforme a `docs/schemas/loss-report.schema.json` con `{code, line, reason}`. Lista cerrada: añadir una pérdida exige nueva versión de spec.

## §9 Catálogo de errores 1.0 (cerrado)

Invariante: `catálogo == emitidos ∪ reservados-declarados`. Cada código lleva `{nombre, emisor, superficie, spec§}`. Mapa completo: `docs/standard/errors-1.0.md`. Un código sin emisor en ninguna superficie se retira o se marca `reserved` con justificación — nunca se deja implícito. Familias: `G*` glosario/formato, `I*` ideas, `L*` léxico/escalares, `S*` estructura, `U*` unicode, `H*` hcortex, `L4xx` pérdidas declaradas.

## §10 Conformidad

Niveles de implementación (booleanos, verificados por `bench/certify.py` + corpus `conformance/`):

| Nivel | Condición |
|---|---|
| Reader | parsea corpus válido + rechaza corpus inválido con código correcto |
| Writer | + canonicaliza idempotente (D1) + hash dominio-separado |
| Renderer | + render HCORTEX byte-exacto vs vectores + loss-report conforme |
| Migrator | + `to-1.0` idempotente con reporte |

Vectores normativos: `conformance/1.0/` (heredados del corpus 0.1+0.2+hcortex validados, promovidos). Sello `tests/SHA256SUMS` cubre el corpus — cualquier mutación lo regenera.

## §11 Versionado y permanencia

### §11.1 Alias de lectura

El dispatcher acepta `cortex:0.1` y `cortex:0.2` en lectura — un doc válido en su dialecto permanece legible. `cortex:1` no es alias: `G007`. Escritura canónica siempre `cortex:1.0`.

### §11.2 Permanencia

Ratificado, 1.0 es inmutable. Evolución: `1.x` aditiva (sigilo/shape/contrato nuevo que nunca invalida docs existentes) o `2.0` (línea de dialecto nueva con migración). Mutación silenciosa del canon = violación del contrato.

## §12 Referencias normativas

- Gramática: `docs/grammar/cortex-1.0.ebnf`, `cortex-1.0.abnf`
- Esquemas: `docs/schemas/ast-schema-1.0.json`, `diagnostic-schema.json`, `loss-report.schema.json`, `hcortex-*.schema.json`
- Errores: `docs/standard/errors-1.0.md`
- Corpus: `conformance/1.0/` + manifiestos
- Certificado: `bench/certify.py` + `.github/workflows/certificate.yml`
