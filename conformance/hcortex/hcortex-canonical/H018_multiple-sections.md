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

---

## $1 · Objetivos

<!-- cortex-entry {"name":"goal","namespace":null,"section":"1","shape":"attrs","symbol":"OBJ"} -->
### OBJ:goal · objective

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `goal` | `"Cerrar roundtrip."` |
| 2 | `status` | `current` |

---

## $2 · Evidencia

<!-- cortex-entry {"name":"evidence","namespace":null,"section":"2","shape":"attrs","symbol":"KNW"} -->
### KNW:evidence · knowledge

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `topic` | `Evidencia` |
| 2 | `content` | `"Corpus verificable."` |
