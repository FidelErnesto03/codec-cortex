# ERRORS — Taxonomía v2 relevante

| Código | Severidad | Significado |
|---|---|---|
| `E_HCORTEX_HEADER_INVALID` | error | Header HCORTEX ausente o inválido |
| `E_HCORTEX_NOT_REVERSIBLE` | error | Declara/requiere reversibilidad sin cumplir gates |
| `E_VIEW_MISSING` | error | Bloque semántico no cubierto por VIEW/trazabilidad |
| `E_VIEW_TARGET_UNRESOLVED` | error | Target VIEW no resoluble |
| `E_VIEW_REVERSE_UNSUPPORTED` | error | Estrategia inversa no soportada |
| `E_VIEW_HASH_MISMATCH` | error | Hash declarado no coincide con el bloque |
| `E_HUMAN_BLOCK_UNDECLARED` | error | Prosa humana no declarada en modo estricto |
| `E_TABLE_SCHEMA_MISMATCH` | error | Tabla no coincide con fields/schema esperado |
| `E_BLOCK_NOT_PRESERVED` | error | Bloque verbatim mutó durante roundtrip |
| `E_AST_EQUIVALENCE_FAIL` | error | Reparse/roundtrip no conserva AST |
| `W_HCORTEX_DISPLAY_ONLY` | warning | Markdown legible no canónico |
| `W_VIEW_EMPTY_TARGET` | warning | Target VIEW sin entries |
| `W_VIEW_HETEROGENEOUS_TARGET` | warning | Target con schemas mixtos sin fields |

Regla: errores de reversibilidad no deben escribir `--out`, salvo `--force-write-on-error`, y en ese caso el artefacto debe quedar marcado como no reversible/experimental.
