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
| `—` | `[]` |

### Microtokens
| Token | Expansión |
| --- | --- |
| `—` | `—` |

### Namespaces
| Nombre | URI | Versión |
| --- | --- | --- |
| `agent` | `urn:cortex:agent` | `0.1` |

### Extensiones
| Namespace | ID | Versión | Requerida | Config |
| --- | --- | --- | --- | --- |
| `—` | `—` | `—` | `—` | `—` |

### Sigilos
| Namespace | Sigilo | Nombre | Shape | Peso | Contrato | Foco | Open | Descripción |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `agent` | `KNW` | `knowledge` | `attrs` | `B` | `topic:text\|content:text` | `content` | `false` | Conocimiento namespaced |

---

## $1

<!-- cortex-entry {"name":"codec","namespace":"agent","section":"1","shape":"attrs","symbol":"KNW"} -->
### agent::KNW:codec · knowledge

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `topic` | `Namespace` |
| 2 | `content` | `"El símbolo conserva su namespace."` |
