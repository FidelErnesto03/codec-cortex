# VIEW_SCHEMA — Contrato de directivas VIEW

**Versión:** 1  
**Última actualización:** v2.4.0

VIEW es el contrato declarativo de correspondencia entre entradas CORTEX y bloques HCORTEX. Sin VIEW/trazabilidad equivalente, HCORTEX es solo Markdown legible (`display-only`). Con VIEW válido, cobertura 100% y roundtrip exitoso, HCORTEX es reversible por contrato.

## Sintaxis CORTEX

```text
VIEW:name{kind:KIND,target:"SELECTOR",reverse:REVERSE[,fields:"F1,F2,..."][,order:ORDER][,title:"..."][,status:STATUS][,scope:"..."][,section:"$N"][,source_section:"$N"][,preserve:verbatim][,hash:"sha256:..."][,fallback:"..."]}
```

## Marker HCORTEX

```html
<!-- VIEW:name kind=table target="$N:SIGIL:*" reverse=rows_to_entries fields="..." order=source title="..." status=cur -->
```

Los marcadores HCORTEX pueden incluir `hash="sha256:..."`. En v2.4.0 la verificación de hash es real cuando el hash está declarado; los artefactos canónicos actuales usan source markers y VIEW metadata, pero no incorporan hash en los 44 markers.

## Campos

| Campo | Req | Descripción |
|---|---|---|
| `kind` | Sí | Tipo de render: table, kv_table, list, numbered_list, checklist, prose, quote, puml, code, callout, section, raw, matrix |
| `target` | Sí | Selector de entries |
| `reverse` | Sí | Estrategia inversa |
| `fields` | No | Columnas esperadas; ayuda a reversión y evita ambigüedad |
| `order` | No | `source` o `declared` |
| `title` | No | Título humano del bloque |
| `status` | No | `cur`, `planned`, `deprecated`, `human_only`, `generated`, `edited` |
| `scope` | No | Ámbito semántico |
| `section` | No | Sección destino al revertir |
| `source_section` | No | Sección fuente original |
| `preserve` | No | `verbatim` para DIAG/PUML/CODE |
| `hash` | No | Hash de integridad del bloque, validado si existe |
| `fallback` | No | Estrategia fallback |

## Compatibilidad kind × reverse

| kind | reverses válidos |
|---|---|
| `table` | rows_to_entries, columns_to_attrs |
| `kv_table` | row_to_attrs |
| `matrix` | columns_to_attrs, rows_to_entries |
| `list` | items_to_entries, body_to_cuerpo |
| `numbered_list` | items_to_ordered_entries |
| `checklist` | items_to_status_entries |
| `prose` | body_to_cuerpo, preserve_human_block |
| `quote` | body_to_cuerpo |
| `puml` | verbatim_to_bloque |
| `code` | verbatim_to_bloque |
| `callout` | callout_to_risk, callout_to_limit, preserve_human_block |
| `section` | preserve_human_block |
| `raw` | verbatim_to_bloque, preserve_human_block |

## Cobertura

- Coverage global canónico del SKILL v2.4.0: 100%.
- Entries elegibles: todas las entries semánticas excepto VIEW y meta estructural de `$0`.
- `0 entries + 0 VIEW` no es 100%; debe reportar 0% y `reversible:false`.

## Diagnósticos principales

| Código | Severidad | Causa |
|---|---|---|
| `E_VIEW_UNKNOWN_KIND` | error | kind desconocido |
| `E_VIEW_UNKNOWN_REVERSE` | error | reverse desconocido |
| `E_VIEW_INCOMPATIBLE_REVERSE` | error | kind/reverse incompatibles |
| `E_VIEW_DUPLICATE_NAME` | error | VIEW duplicado |
| `E_VIEW_MISSING` | error | bloque semántico sin VIEW en modo estricto |
| `E_VIEW_TARGET_UNRESOLVED` | error | target no resuelve |
| `E_VIEW_REVERSE_UNSUPPORTED` | error | reverse no soportado |
| `E_VIEW_HASH_MISMATCH` | error | hash declarado no coincide |
| `W_VIEW_EMPTY_TARGET` | warning | target resuelve a 0 entries |
| `W_VIEW_HETEROGENEOUS_TARGET` | warning | schemas mixtos sin fields |
| `W_HCORTEX_DISPLAY_ONLY` | warning | Markdown legible no canónico |
