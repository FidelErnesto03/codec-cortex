# Informe de paridad con la implementación Python

## Mapa funcional

| Python | Bash |
|---|---|
| `Scalar`, parser de escalares | objetos JSON `{kind,value,lexeme}` + `ccx_parse_scalar` |
| `parse_string_literal` | `ccx_parse_string_literal` |
| `emit_string_literal` | `ccx_emit_string_literal` |
| `parse_attrs_payload` | `ccx_parse_attrs` |
| `parse_contract_fields` | `ccx_parse_contract` |
| `parse_cortex` | `ccx_parse_cortex_file` / `parse_cortex` |
| dataclasses AST | AST JSON ordenado |
| `canonicalize` | `ccx_canonicalize_ast` / `canonicalize` |
| `render_hcortex` | `ccx_render_hcortex_ast` / `render_hcortex` |
| `compile_hcortex` | `ccx_compile_hcortex_file` / `compile_hcortex` |
| `sha256_bytes` | `ccx_sha256_file` |
| `c14n_hash` | `ccx_c14n_hash_file` |
| `run_phase3` | `ccx_run_phase3` |
| `run_phase4` | `ccx_run_phase4` |
| `run_all_tests` | `ccx_run_all_tests` |

## Reglas reproducidas

- Prohibición de BOM en CORTEX: `U001_BOM_FORBIDDEN`.
- Normalización CRLF/CR a LF.
- Tipos `string`, `atom`, `integer`, `decimal`, `boolean`, `null`, `list`.
- Normalización de `-0` a `0`.
- Contratos requeridos/opcionales y validación de `focus`.
- Shapes `attrs`, `attrs-pos`, `cuerpo`, `bloque`, `relacion`.
- Orden canónico de format, enums, micros, namespaces, extensiones, metadata y símbolos.
- NFC fuera de `bloque`.
- Expansión de microtokens únicamente en átomos de ideas.
- Secciones e ideas preservadas en orden fuente.
- HCORTEX con schemas `table`, `prose`, `list`, `check`, `diagram`.
- Diagnósticos HCORTEX `H400` y `H490`.
- Umbrales originales del gate F3: 38 goldens y 40 idempotencias.

## Comportamientos heredados preservados

La implementación Python posee decisiones que no deben confundirse con reglas ideales del estándar:

1. En HCORTEX, una sección con shapes mixtos cae en `prose`; un `bloque` dentro de esa sección pierde su cuerpo al renderizarse.
2. El compilador HCORTEX separa pipes dentro de ciertos strings citados. Bash reproduce ese resultado para mantener paridad.
3. Una sección sin título se renderiza como `Sección N`; al recompilar, ese texto pasa a ser título explícito.
4. HCORTEX `table` para `attrs` emite solo campos del contrato, no extras de símbolos abiertos.

Estos puntos están cubiertos como compatibilidad, no defendidos como diseño normativo futuro.

## Diferencias inevitables o deliberadas

- El AST público es JSON y no dataclasses, porque Bash no ofrece clases nativas.
- La API trabaja con archivos para no perder saltos finales ni contenido multilinea en sustituciones de comando.
- U+0000 dentro de valores decodificados no es transportable en variables Bash. El formato fuente puede contener la secuencia literal, pero no se garantiza paridad para un scalar cuyo valor lógico incluya NUL.
- El compilador Bash puede ser más estricto ante un glossary HCORTEX malformado. Los documentos válidos y el corpus canónico mantienen paridad.
- Rendimiento: Bash+jq es considerablemente más lento que Python. Se priorizaron auditabilidad, reversibilidad y ausencia de runtime Python.

## Evidencia ejecutada

- `tests/self-test.sh`: PASS contra goldens Python.
- Fixture integral: C14N byte-identical, HCORTEX byte-identical y compilación inversa byte-identical.
- Gate F4 incluido: PASS, 5/5 roundtrip, 5/5 idempotencia y 2/2 diagnósticos.
- Gate F3: runner verificado en subconjunto y corpus completo de 40 casos incluido. La ejecución exhaustiva es intencionalmente intensiva en procesos `jq`.
