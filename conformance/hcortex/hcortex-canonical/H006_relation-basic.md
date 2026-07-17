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
| `—` | `KNW` | `knowledge` | `attrs` | `B` | `topic:text\|content:text\|status:%state?\|evidence:text?` | `content` | `false` | Conocimiento verificable |
| `—` | `REL` | `relation` | `relacion` | `M` | `source:atom\|predicate:atom\|target:atom\|qualifier:text?` | `predicate` | `false` | Relación dirigida |

---

## $1

<!-- cortex-entry {"name":"parser","namespace":null,"section":"1","shape":"attrs","symbol":"KNW"} -->
### KNW:parser · knowledge

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `topic` | `Parser` |
| 2 | `content` | `"Analiza CORTEX."` |

<!-- cortex-entry {"name":"ast","namespace":null,"section":"1","shape":"attrs","symbol":"KNW"} -->
### KNW:ast · knowledge

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `topic` | `AST` |
| 2 | `content` | `"Preserva Ideas."` |

<!-- cortex-entry {"name":"parser_ast","namespace":null,"section":"1","shape":"relacion","symbol":"REL"} -->
### REL:parser_ast · relation

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `source` | `$1:KNW:parser` |
| 2 | `predicate` | `produces` |
| 3 | `target` | `$1:KNW:ast` |
| 4 | `qualifier` | `deterministic` |
