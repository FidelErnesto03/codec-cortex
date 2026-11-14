# Authoring HCORTEX 1.0

Guía para humanos que leen —y ocasionalmente editan— HCORTEX sin romper el
roundtrip.

---

## Qué es y qué no es

HCORTEX es la **proyección humana determinista** de CORTEX: mismo AST, mismos
bytes en las cinco superficies. Se genera con `to-hcortex` y se compila de vuelta
con `from-hcortex`. No es la fuente de verdad: la fuente es el `.cortex`.

Editar HCORTEX a mano es posible, pero el compilador es estricto. Si el render
cambia de forma editorial, `loss-report` lo dirá con un código del catálogo.

## Estructura de un HCORTEX 1.0

```markdown
<!-- HCORTEX v=1.0 t=canonical k=TIPO -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8}
<!-- /glossary -->

## §1: TITULO

<!-- schema:1 capa:CORE -->
### SIGIL:nombre
| campo1 | campo2 |
|---|---|
| "valor" | atom |
<!-- /schema:1 -->
```

| Pieza | Regla |
|---|---|
| Envelope | `<!-- HCORTEX v=1.0 t=canonical k=<tipo> -->`; sin envelope = `H400`/`H401` |
| Glosario | `<!-- glossary -->` … `<!-- /glossary -->` con el glosario textual completo; ausente = `H403` |
| Sección | `## §N: Título`; la capa va en el marcador de schema, no en el título |
| Schema | `<!-- schema:N -->` o `<!-- schema:N capa:CAPA -->`, cerrado con `<!-- /schema:N -->` |
| Idea | `### SIGIL:nombre` seguido del payload en la forma del schema |
| Copia oculta | prohibida: `cortex-ast:`, `base64:`, `shadow:`, `ast:` = `H481` |

## Los tres schemas de 1.0

El schema lo decide el shape de la sección, no el autor:

| Shape | Schema | Payload |
|---|---|---|
| `attrs`, `attrs-pos`, `relacion` | `table` | tabla con cabecera y una fila |
| `cuerpo` | `prose` | texto en líneas |
| `bloque` | `diagram` | fence ` ``` ` con el contenido verbatim |

`list` y `check` existen en HCORTEX 0.1 y **no los produce el renderer 1.0**:
son sintaxis histórica, conservada solo como alias de lectura.

## Ejemplo completo (salida real)

Documento fuente:

```cortex
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8}
$0:enum_state{values:"current|done"}
RUL:rule{type:attrs,weight:H,focus:rule,desc:"Regla",fields:"rule:text|status:%state"}
NOTA:note{type:cuerpo,weight:M,desc:"Nota"}
DIAG:diagram{type:bloque,weight:M,desc:"Diagrama"}
$1: REGLAS:CORE
RUL:strict{rule:"El canon manda sobre la implementacion.",status:current}
$2: NOTAS:DATA
NOTA:recordatorio{
Revisar la documentacion antes de entregar.
}
$3: ARQUITECTURA:DATA
DIAG:flujo{
@startuml
A -> B
@enduml
}
```

HCORTEX generado:

```markdown
<!-- HCORTEX v=1.0 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8}
$0:enum_state{values:"current|done"}
RUL:rule{type:attrs,weight:H,focus:rule,desc:"Regla",fields:"rule:text|status:%state"}
NOTA:note{type:cuerpo,weight:M,desc:"Nota"}
DIAG:diagram{type:bloque,weight:M,desc:"Diagrama"}

<!-- /glossary -->

## §1: REGLAS

<!-- schema:1 capa:CORE -->
### RUL:strict
| rule | status |
|---|---|
| "El canon manda sobre la implementacion." | current |

<!-- /schema:1 -->

## §2: NOTAS

<!-- schema:2 capa:DATA -->
### NOTA:recordatorio
Revisar la documentacion antes de entregar.

<!-- /schema:2 -->

## §3: ARQUITECTURA

<!-- schema:3 capa:DATA -->
### DIAG:flujo
```
@startuml
A -> B
@enduml
```

<!-- /schema:3 -->
```

## Reglas para que compile de vuelta

1. **El glosario es obligatorio** para recompilar: es el `$0` textual, no una
   copia oculta.
2. **Schema y sección deben coincidir**: `schema:N` dentro de `## §N`.
3. **Una sección, un schema.** Para variar de forma, abrí otra sección.
4. **Los valores de texto van entrecomillados** en las tablas; los `atom` no.
5. **No reordenes atributos de sigilos `open:true`**: C14N los normaliza y el
   orden editorial se declara como pérdida (`L405`).
6. **Comentarios y espacios de más** no sobreviven: son `L402` y `L403`.
7. **No inyectes hashes ni AST**: `H481_HIDDEN_COPY`.

## Verificar antes de entregar

```bash
python -m codec_cortex from-hcortex doc.md > doc.back.cortex
python -m codec_cortex canonicalize doc.back.cortex > back.canon
python -m codec_cortex canonicalize doc.cortex      > src.canon
cmp back.canon src.canon            # sin salida = roundtrip exacto
python -m codec_cortex loss-report doc.cortex
```

## Histórico

Las plantillas 0.1 (esquemas `list`/`check`, envelope `v=0.1`, glosario sin
`<!-- /glossary -->`) están archivadas en
[`archive/2026-11/standard-0x/hcortex-0.1.md`](../../archive/2026-11/standard-0x/hcortex-0.1.md).
