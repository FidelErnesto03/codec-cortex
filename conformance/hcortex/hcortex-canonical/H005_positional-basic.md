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

---

## $1

<!-- cortex-entry {"name":"verify","namespace":null,"section":"1","shape":"attrs-pos","symbol":"HDL"} -->
### HDL:verify · procedure

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `action` | `validar estructura` |
| 2 | `status` | `current` |
| 3 | `target` | `archivo .cortex` |
