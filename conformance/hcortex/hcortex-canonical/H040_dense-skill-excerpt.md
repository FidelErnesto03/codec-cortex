<!-- hcortex {"cortex":"0.1","encoding":"UTF-8","hcortex":"0.1","mode":"canonical"} -->
# HCORTEX · CORTEX 0.1

## Glosario

### Formato
| Clave | Valor |
| --- | --- |
| `cortex` | `0.1` |
| `encoding` | `UTF-8` |
| `language` | `es` |

### Enums
| Nombre | Valores |
| --- | --- |
| `state` | `["current","planned","blocked","done"]` |

### Microtokens
| Token | Expansión |
| --- | --- |
| `—` | `—` |

### Namespaces
| Nombre | URI | Versión |
| --- | --- | --- |
| `—` | `—` | `—` |

### Extensiones
| Namespace | ID | Versión | Requerida | Config |
| --- | --- | --- | --- | --- |
| `—` | `—` | `—` | `—` | `—` |

### Sigilos
| Namespace | Sigilo | Nombre | Shape | Peso | Contrato | Foco | Open | Descripción |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `—` | `HDL` | `procedure` | `attrs-pos` | `M` | `action:text\|status:%state\|target:text\|constraint:text?` | `action` | `false` | Procedimiento compacto |
| `—` | `KNW` | `knowledge` | `attrs` | `B` | `topic:text\|content:text\|status:%state?\|evidence:text?` | `content` | `false` | Conocimiento verificable |
| `—` | `OBJ` | `objective` | `attrs` | `H` | `goal:text\|status:%state\|metric:text?` | `goal` | `false` | Objetivo explícito |
| `—` | `REL` | `relation` | `relacion` | `M` | `source:atom\|predicate:atom\|target:atom\|qualifier:text?` | `predicate` | `false` | Relación dirigida |

---

## $1

<!-- cortex-entry {"name":"intent","namespace":null,"section":"1","shape":"attrs","symbol":"OBJ"} -->
### OBJ:intent · objective

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `goal` | `"Transformar contexto sin pérdida."` |
| 2 | `status` | `current` |

<!-- cortex-entry {"name":"step1","namespace":null,"section":"1","shape":"attrs-pos","symbol":"HDL"} -->
### HDL:step1 · procedure

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `action` | `parsear CORTEX` |
| 2 | `status` | `done` |
| 3 | `target` | `AST` |

<!-- cortex-entry {"name":"step2","namespace":null,"section":"1","shape":"attrs-pos","symbol":"HDL"} -->
### HDL:step2 · procedure

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `action` | `renderizar HCORTEX` |
| 2 | `status` | `done` |
| 3 | `target` | `Markdown canónico` |

<!-- cortex-entry {"name":"invariant","namespace":null,"section":"1","shape":"attrs","symbol":"KNW"} -->
### KNW:invariant · knowledge

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `topic` | `Reversibilidad` |
| 2 | `content` | `"compile(render(AST)) produce el mismo AST."` |

<!-- cortex-entry {"name":"proof","namespace":null,"section":"1","shape":"relacion","symbol":"REL"} -->
### REL:proof · relation

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `source` | `$1:HDL:step1` |
| 2 | `predicate` | `precedes` |
| 3 | `target` | `$1:HDL:step2` |
