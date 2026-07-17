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

---

## $1

<!-- cortex-entry {"name":"same","namespace":null,"section":"1","shape":"attrs","symbol":"KNW"} -->
### KNW:same · knowledge

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `topic` | `Uno` |
| 2 | `content` | `"Primera sección."` |

---

## $2

<!-- cortex-entry {"name":"same","namespace":null,"section":"2","shape":"attrs","symbol":"KNW"} -->
### KNW:same · knowledge

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `topic` | `Dos` |
| 2 | `content` | `"Segunda sección."` |
