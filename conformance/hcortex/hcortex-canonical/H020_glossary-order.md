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
| `—` | `OBJ` | `objective` | `attrs` | `H` | `goal:text\|status:%state\|metric:text?` | `goal` | `false` | Objetivo explícito |
| `—` | `RSK` | `risk` | `attrs` | `H` | `risk:text\|impact:text\|status:%state` | `risk` | `false` | Riesgo explícito |

---

## $1

<!-- cortex-entry {"name":"goal","namespace":null,"section":"1","shape":"attrs","symbol":"OBJ"} -->
### OBJ:goal · objective

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `goal` | `"Orden canónico."` |
| 2 | `status` | `current` |

<!-- cortex-entry {"name":"ambiguity","namespace":null,"section":"1","shape":"attrs","symbol":"RSK"} -->
### RSK:ambiguity · risk

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `risk` | `"Orden variable."` |
| 2 | `impact` | `"Hash distinto."` |
| 3 | `status` | `blocked` |
