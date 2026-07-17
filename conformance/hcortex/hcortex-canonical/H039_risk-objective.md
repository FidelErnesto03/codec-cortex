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
| `—` | `RSK` | `risk` | `attrs` | `H` | `risk:text\|impact:text\|status:%state` | `risk` | `false` | Riesgo explícito |

---

## $1

<!-- cortex-entry {"name":"gate","namespace":null,"section":"1","shape":"attrs","symbol":"OBJ"} -->
### OBJ:gate · objective

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `goal` | `"100% roundtrip estructural."` |
| 2 | `status` | `current` |
| 3 | `metric` | `"40/40"` |

<!-- cortex-entry {"name":"view","namespace":null,"section":"1","shape":"attrs","symbol":"RSK"} -->
### RSK:view · risk

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `risk` | `"VIEW contamina el canon."` |
| 2 | `impact` | `"Pérdida de reversibilidad."` |
| 3 | `status` | `blocked` |
