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
| `—` | `DIAG` | `diagram` | `bloque` | `B` | `—` | `$body` | `false` | Bloque verbatim |
| `—` | `HDL` | `procedure` | `attrs-pos` | `M` | `action:text\|status:%state\|target:text\|constraint:text?` | `action` | `false` | Procedimiento compacto |
| `—` | `KNW` | `knowledge` | `attrs` | `B` | `topic:text\|content:text\|status:%state?\|evidence:text?` | `content` | `false` | Conocimiento verificable |
| `—` | `REL` | `relation` | `relacion` | `M` | `source:atom\|predicate:atom\|target:atom\|qualifier:text?` | `predicate` | `false` | Relación dirigida |
| `—` | `TXT` | `text` | `cuerpo` | `B` | `—` | `$body` | `false` | Texto semántico |

---

## $1

<!-- cortex-entry {"name":"k","namespace":null,"section":"1","shape":"attrs","symbol":"KNW"} -->
### KNW:k · knowledge

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `topic` | `Todos` |
| 2 | `content` | `"Cobertura de shapes."` |

<!-- cortex-entry {"name":"p","namespace":null,"section":"1","shape":"attrs-pos","symbol":"HDL"} -->
### HDL:p · procedure

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `action` | `renderizar` |
| 2 | `status` | `current` |
| 3 | `target` | `AST` |

<!-- cortex-entry {"name":"t","namespace":null,"section":"1","shape":"cuerpo","symbol":"TXT"} -->
### TXT:t · text

```hcortex-text
Texto humano.
```

<!-- cortex-entry {"media_type":"text/plain","name":"b","namespace":null,"section":"1","shape":"bloque","symbol":"DIAG"} -->
### DIAG:b · diagram

```cortex-block
verbatim
```

<!-- cortex-entry {"name":"r","namespace":null,"section":"1","shape":"relacion","symbol":"REL"} -->
### REL:r · relation

| # | Campo | Valor |
| --- | --- | --- |
| 1 | `source` | `$1:KNW:k` |
| 2 | `predicate` | `supports` |
| 3 | `target` | `$1:TXT:t` |
