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
| `agent` | `urn:agent` | `0.1` |
| `project` | `urn:project` | `0.1` |

### Extensiones
| Namespace | ID | Versión | Requerida | Config |
| --- | --- | --- | --- | --- |
| `—` | `—` | `—` | `—` | `—` |

### Sigilos
| Namespace | Sigilo | Nombre | Shape | Peso | Contrato | Foco | Open | Descripción |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `agent` | `KNW` | `knowledge` | `attrs` | `B` | `content:text` | `content` | `false` | Agent knowledge |
| `project` | `KNW` | `knowledge` | `attrs` | `B` | `content:text` | `content` | `false` | Project knowledge |

---

## $1

<!-- cortex-entry {"name":"a","namespace":"agent","section":"1","shape":"attrs","symbol":"KNW"} -->
### agent::KNW:a · knowledge

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `content` | `"Agente"` |

<!-- cortex-entry {"name":"p","namespace":"project","section":"1","shape":"attrs","symbol":"KNW"} -->
### project::KNW:p · knowledge

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `content` | `"Proyecto"` |
