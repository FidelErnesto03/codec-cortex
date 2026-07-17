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
| `—` | `OBJ` | `objective` | `attrs` | `H` | `goal:text\|status:%state\|metric:text?` | `goal` | `false` | Objetivo explícito |

---

## $1

<!-- cortex-entry {"name":"simple","namespace":null,"section":"1","shape":"attrs","symbol":"OBJ"} -->
### OBJ:simple · objective

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `goal` | `"No repetir opcionales."` |
| 2 | `status` | `planned` |
