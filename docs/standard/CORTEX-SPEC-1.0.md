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
SIGIL:nombre{type:<shape>,weight:<B|M|H>,focus:<campo|"$body">,
             desc:"...",open:<true|false>,
             fields:"a:text|b:int|c:atom|d:atom?"      ← si type:attrs
             pos:"a:text|b:text|c:int"                ← si type:attrs-pos|relacion
             [slots:"1=a:text|2=b:text",encoding:slots] ← eje slots (§5)
             [schema:table]}
```

- `type` ∈ los 5 shapes (§4). `weight`: B|M|H.
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

### §4.4 Charset de identificadores (norma 1.0)

Identificadores estructurales — nombre de idea, clave de attr, label de sigilo en `$0`, nombre de declaración `$0:x` (incl. `enum_<n>`, `micro_<t>`, `namespace_<a>`, `extension_<n>`) y nombre de campo de contrato — se restringen al **subconjunto ASCII imprimible**. Fuera de charset: `U003_NON_ASCII_IDENTIFIER`. El contenido textual (`string` quoted, `cuerpo`, `bloque`, títulos de sección) permanece Unicode libre. Motivo normativo: homoglifos en identificadores producen direcciones visualmente idénticas con identidad semántica distinta — incompatible con manifiestos verificables por humanos.

## §5 Eje de codificación slots

Integrado de 0.2 como **sección normativa**, no dialecto aparte:

- `$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}` — obligatorio antes del primer sigilo con `encoding:slots` (`G041`).
- Sigilo con `encoding:slots` declara `slots:"N=campo:tipo"`; usos codifican celdas como `※N:valor`.
- Orden de slots por `order` del sigil-map (ascending|declared). Slot no declarado: `I05x`. Referencia `※` estructural en doc sin sigil-map: error de superficie mezclada (`I058`).
- `cuerpo`/`bloque` nunca usan slots — sus payloads son opacos.

## §6 Namespaces y extensiones

- `ns::SIGIL:name` calificado — `ns` debe estar declarado via `namespace_<a>` (`I001`/G0xx si no).
- `!` es sigilo reservado interno: declaŕable en `$0` como cualquier sigilo (el corpus normativo `V024` lo ejercita); su semantica es definida por el documento, no por el runtime.
- Extensiones nombradas via `extension_<n>`; sigilos extensión requieren `open:true` o contrato que las admita.

## §7 C14N-1.0 — canonicalización y hash

Función pura `canonicalize(doc) → bytes`:

1. Orden de secciones: `$0` primero; luego `$N` ascendente (subsecciones `$N.M` ordenadas `N` luego `M` numérico).
2. Dentro de sección: ideas en orden documental — **el orden canónico se fija aquí como orden documental** (cierra el "pendiente de Fase 3" de 0.1).
3. Glosario serializado en orden de declaración: format, sigil-map, enums, micros, namespaces, extensions, meta, sigilos.
4. En ideas `attrs`, los campos se emiten en el orden declarado en `fields`; los campos adicionales de sigilos `open:true` se emiten después del contrato, ordenados por clave UTF-8 NFC — la permutación editorial de campos no altera el canónico ni el hash.
5. Escalares normalizados: NFC para `cuerpo`/strings; `bloque` verbatim; atoms lowercase-preservado; números en forma canónica.
6. Hash: `SHA-256(dominio + 0x00 + canonical_bytes)` con dominio por versión declarada: `CORTEX-C14N-0.1` para `cortex:0.1`, `CORTEX-C14N-0.2` para `cortex:0.2` y `cortex:1.0`. Dominio separado de cualquier hash de contenido raw — mismo documento con distinta versión declarada produce hashes distintos.
7. Idempotencia obligatoria: `canonicalize(parse(canonicalize(parse(src)))) == canonicalize(parse(src))` — vector D1.

### §7.1 Contrato de firma

Lo que se firma con un hash `sha256:` es el **documento canónico**, no el archivo de texto. El contrato exacto:

**Altera el hash** (forma parte del canónico): versión declarada en `$0:format` (vía dominio), glosario completo en orden de declaración, secciones y su título, cada idea (sigilo, nombre, payload normalizado: campos en orden de contrato, extras `open:true` ordenados por clave UTF-8 NFC, valores escalares en forma canónica, cuerpo NFC, bloque verbatim).

**No altera el hash** (variación editorial tolerada): permutación de campos `attrs` respecto al orden de contrato (se normaliza), microtokens usados en fuente (se expanden en C14N), comentarios `#`, líneas en blanco, whitespace intra-línea no significativo, comillas alternativas equivalentes (`focus` siempre quoted en el canónico).

**Consecuencia operativa**: verificar una firma = canonicalizar y re-hashear; comparar dos documentos = comparar hashes canónicos; un diff de firma exige diff de canónico, nunca diff de texto.

## §8 HCORTEX-1.0 — proyección humana determinista

`render(doc) : Document → bytes` es **función pura del AST**:

- Mismo AST → mismos bytes, en cualquier superficie (Python/Go/Node/Rust/Bash) — vector D3.
- Sin hora, locale, RNG, ni orden de hash interno.
- Orden: secciones por `$N` ascendente, ideas en orden documental, glosario por orden de declaración.
- **Envelope:** un documento `cortex:1.0` emite `<!-- HCORTEX v=1.0 t=canonical k=corpus -->`. El compilador acepta `v=1.0` (canónico) y `v=0.2` (alias de lectura para documentos 0.2); `v=0.1` pertenece a HCORTEX 0.1. Un render 1.0 nunca emite `v=0.2`.

### §8.1 Clases de roundtrip

| Clase | Definición |
|---|---|
| `LOSSLESS` | `canonicalize(from_hcortex(render(x))) == canonicalize(x)` |
| `DECLARED-LOSS` | roundtrip diverge solo en pérdidas del catálogo §8.2, cada una reportada |

Ninguna tercera clase. Un render que pierde AST sin declararlo viola **H481** (sin copia oculta — norma 1.0): ningún render válido esconde información semántica no representada.

**Auto-validación del compilador (norma 1.0).** `from_hcortex` construye el AST directamente desde markdown, sin pasar por el parser de fuente; por tanto **DEBE** re-parsear la salida canónica que produciría y, si no valida, fallar con el diagnóstico del parser en vez de emitir fuente inválida. Un compilador nunca emite fuente que el propio parser rechaza — implementado en Python (`compile_hcortex_slots`); pendiente en go/node/rs/bash bajo E-0224.

### §8.2 Catálogo de pérdidas declaradas (L4xx)

Una **pérdida declarada** es información presente en la fuente que no se representa en el AST y por tanto no se recupera en `canonicalize(from_hcortex(render(x)))`. El catálogo es cerrado y cada código tiene emisor obligatorio en las cinco superficies.

| Código | Pérdida | Disparador | `path` |
|---|---|---|---|
| `L402_COMMENT_DROPPED` | Comentarios `#` | línea cuyo primer carácter no-espacio es `#`, fuera de cuerpo/bloque (dentro del glosario también se descarta) | `line:<n>` |
| `L403_INTRALINE_WHITESPACE` | Whitespace intra-línea no significativo | tab, espacio final o 2+ espacios consecutivos fuera de literales entrecomillados | `line:<n>` |
| `L405_OPEN_ATTR_ORDER` | Orden editorial de atributos | idea de sigilo `open:true` cuyo orden en fuente ≠ orden de contrato + extras por clave UTF-8 | `$N` |

Invariante de cierre: **toda** divergencia de roundtrip debe pertenecer a una de estas clases. Una divergencia no clasificable emite `L499_UNCLASSIFIED_LOSS` (`severity: error`) y `loss-report` termina con código de salida 1 — "0 pérdidas sin nombre" es verificable, no aspiracional.

Cada pérdida emite una entrada de `loss-report` conforme a `docs/schemas/loss-report-1.0.schema.json` (forma `finding`: `{code, severity, category, path, detail, recoverability, action}`). La lista es cerrada: añadir, retirar o redefinir una pérdida exige nueva versión de spec.

### §8.3 Riesgos retirados del catálogo de pérdidas

Verificación 2026-11-14 (SES004) sobre las cinco superficies: estos dos constructos se declaraban pérdidas y **no lo son**. Permanecen como riesgos documentados, sin emisor y sin entrada en `loss-report`:

| Código histórico | Estado | Evidencia |
|---|---|---|
| `L401` marcador de fence en bloque | **retirado** | `canonicalize(compile(render(x))) == canonicalize(x)` con ` ```python ` y ` ~~~ ` dentro de un bloque, en las cinco superficies; render md5-idéntico. Reservado para el dialecto 0.1 legacy si alguna superficie lo reproduce. |
| `L404` CAPA ausente | **retirado** | `title=None`/`capa=None` roundtriptean intactos; `resolve_capa()` es un valor derivado, no información perdida. El renderer emite `$0` desnudo cuando no hay capa, que la gramática admite. |

**Constructo eliminado, no catalogado:** `$0: <texto>` no pertenece a la gramática 1.0 (`glossary-header = "$0" | "$0:" capa`). Las superficies que lo toleraban lo descartaban en silencio; desde 2026-11-14 se rechaza con `G042_GLOSSARY_HEADER_INVALID` en las cinco superficies. Un constructo fuera de gramática no es una pérdida declarada: es un error.

## §9 Catálogo de errores 1.0 (cerrado)

Invariante: `catálogo == emitidos ∪ reservados-declarados`. Cada código lleva `{nombre, emisor, superficie, spec§}`. Mapa completo: `docs/standard/errors-1.0.md`. Un código sin emisor en ninguna superficie se retira o se marca `reserved` con justificación — nunca se deja implícito. Familias: `G*` glosario/formato, `I*` ideas, `L*` léxico/escalares, `S*` estructura, `U*` unicode, `H*` hcortex, `L4xx` pérdidas declaradas.

## §10 Conformidad

Niveles de implementación (booleanos, verificados por `bench/certify.py` + corpus `conformance/`):

| Nivel | Condición |
|---|---|
| Reader | parsea corpus válido + rechaza corpus inválido con código correcto |
| Writer | + canonicaliza idempotente (D1) + hash dominio-separado |
| Renderer | + render HCORTEX byte-exacto vs vectores + `loss-report` conforme y byte-idéntico en las 5 superficies (D6) |
| Migrator | + `to-1.0` idempotente con reporte |

Vectores normativos: `conformance/1.0/` (heredados del corpus 0.1+0.2+hcortex validados, promovidos). Sello `tests/SHA256SUMS` cubre el corpus — cualquier mutación lo regenera.

## §11 Versionado y permanencia

### §11.1 Alias de lectura

El dispatcher Python (referencia) acepta `cortex:0.1`, `cortex:0.2` y `cortex:1.0`; Go, Node, Rust y Bash aceptan `{0.1, 1.0}` en su subconjunto implementado (sin eje slots — nivel Reader). `cortex:1` no es alias: `G007`. Escritura canónica siempre `cortex:1.0`.

### §11.2 Permanencia

Ratificado, 1.0 es inmutable. Evolución: `1.x` aditiva (sigilo/shape/contrato nuevo que nunca invalida docs existentes) o `2.0` (línea de dialecto nueva con migración). Mutación silenciosa del canon = violación del contrato.

## §12 Normas de autoría (lecciones normativas)

Reglas aprendidas de violaciones reales observadas en el corpus vivo — cada una cita el código de error que la impone:

1. **`|` dentro de una celda va quoted.** `HDL:migrate|a|b|"inspect|plan|apply"` — una celda con `|` interno sin comillas se lee como celdas extra y dispara `I012`. La corrección no es "más celdas", es una celda quoted.
2. **Dirección de idea única por sección.** `SIGIL:nombre` repetido en la misma sección = `I006_DUPLICATE_IDEA_ADDRESS`. Secuencias (pasos, items) nombran cada elemento: `PRC:p1`, `PRC:p2`.
3. **Todo sigilo se declara.** Un documento con sigilos no declarados es inválido bajo su propio parser (`I001`) — incluido el corpus de trabajo. El glosario es obligación, no decoración.
4. **Declarar el dialecto que el documento usa.** La versión describe la gramática del documento, no la del proyecto: sin slots, `cortex:1.0` es la escritura canónica; `cortex:1` no existe (`G007`).
5. **Densidad ideática.** El contenido normativo vive en ideas tipadas (`RUL`, `API`, `PRC`…), no en cuerpos prosa. `cuerpo` es payload semántico; `bloque` es verbatim (ejemplos, referencias). Un documento que "parsea" pero diluye sus reglas en prosa es conforme y aun así mal formado — la forma también es contrato.
6. **Una línea por idea, también al serializar.** Escribir strings con newline literal sin escapar rompe la línea de la idea *y* el artefacto que la contiene — los escritores deben escapar o rechazar (`§4.2`).
7. **`desc` es etiqueta, no frase.** En la declaración de sigilo, `desc` es obligatorio (`G020`) pero debe ser una etiqueta de 1-3 palabras: el glosario es un **sistema de tipos que clasifica**, no un índice que documenta. El significado mínimo basta para que el LLM lo interprete al usuario; la explicación extensa pertenece a la idea o a la spec.
8. **La idea es taquigrafía.** Nombre = etiqueta, enunciado = directo, cero explicación embebida: lo extenso va en `detail` o en la spec. La compactitud es propiedad del formato, no disciplina opcional del autor — cada idea marginal compite contra markdown con sus bytes de señal, no de relleno.
   **Enseñanza por ejemplo** — así se escribe:

   ```
   BIEN:  RUL:pipe_quoted{id:"pipe",rule:"Celda con | va quoted.",detail:"S4.2"}
   MAL:   RUL:porque_las_celdas_con_pipe_deben_ir_entre_comillas{rule:"Es muy importante entender que cuando escribimos una celda que contiene el caracter pipe debemos ponerla entre comillas para evitar que el parser la divida en multiples celdas..."}
   ```

   El nombre es etiqueta (`pipe_quoted`, no una oración). El enunciado es la regla (una línea). La justificación va en `detail`. Un LLM que lee esto aprende la disciplina por contraste, no por definición.
9. **Microtokens por defecto.** Un `atom` que se repite **≥3 veces** y tiene **≥6 caracteres** se declara microtoken (`$0:micro_t{expand:...}`) y se usa en fuente como `t`. La expansión ocurre **solo en C14N** — el hash canónico no cambia, pero el documento fuente pesa menos. Es el único compresor de sintaxis que markdown no puede ofrecer, porque no tiene capa de expansión.

## §13 Referencias normativas

- Gramática: `docs/grammar/cortex-1.0.ebnf`, `cortex-1.0.abnf`
- Esquemas: `docs/schemas/ast-schema-1.0.json`, `diagnostic-schema.json`, `loss-report.schema.json`, `hcortex-*.schema.json`
- Errores: `docs/standard/errors-1.0.md`
- Corpus: `conformance/1.0/` + manifiestos
- Certificado: `bench/certify.py` + `.github/workflows/certificate.yml`
