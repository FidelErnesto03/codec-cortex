# Matriz de equivalencia Python → Rust

| Python | Rust | Estado |
|---|---|---|
| `scalars.Scalar` | `model::Scalar` + `ScalarValue` | completo y tipado |
| `scalars.ParseError` | `error::ParseError` | códigos y posición preservados |
| `to_nfc` | `scalars::to_nfc` | equivalente |
| `parse_string_literal` | `scalars::parse_string_literal` | equivalente |
| `emit_string_literal` | `scalars::emit_string_literal` | equivalente |
| `parse_attrs_payload` | `scalars::parse_attrs_payload` | equivalente; Rust rechaza trailing content |
| dataclasses de AST | structs/enums `model` | completo |
| `parse_contract_fields` | `parser::parse_contract_fields` | equivalente |
| `parse_cortex` | `parser::parse_cortex` | completo; EOF multiline es más estricto |
| `canonicalize` | `c14n::canonicalize` | bytes compatibles en vectores dorados |
| `_expand_microtokens` | `c14n::expand_microtokens` | equivalente |
| `render_hcortex` | `hcortex::render_hcortex` | bytes compatibles en vectores dorados |
| `compile_hcortex` | `hcortex::compile_hcortex` | equivalente en schemas soportados |
| `HDiagnostic` | `hcortex::HDiagnostic` | equivalente |
| `sha256_bytes` | `harness::sha256_bytes` | equivalente |
| `c14n_hash` | `harness::c14n_hash` | equivalente y domain-separated |
| `run_phase3` | `harness::run_phase3` | equivalente |
| `run_phase4` | `harness::run_phase4` | equivalente |
| `run_all_tests` | `harness::run_all_tests` | equivalente |
| `python -m codec_cortex` | `cortex conformance` | equivalente funcional ampliado |

## Diferencias deliberadas

### 1. AST Rust fuertemente tipado

Python representa payloads mediante tuplas etiquetadas. Rust usa `IdeaPayload`, evitando estados inválidos y casts dinámicos.

### 2. Canonicalización no mutante por defecto

Python modifica el AST recibido. Rust clona en `canonicalize`; la mutación solo ocurre mediante `canonicalize_in_place`.

### 3. Fin de archivo dentro de cuerpo multilinea

Python puede terminar sin cerrar el cuerpo y devolver silenciosamente un documento incompleto. Rust devuelve `I004_SHAPE_DELIMITER_MISMATCH`.

### 4. Contenido posterior a `}`

El parser Python de atributos deja contenido posterior sin validar. Rust lo rechaza con `S006_INVALID_ATTRS`.

Estas diferencias endurecen errores destructivos sin cambiar los bytes de entradas válidas cubiertas por los vectores.

## Lo que esta entrega no prueba

La equivalencia sobre fixtures no demuestra todavía conformidad universal. Para ello se necesita ejecutar el corpus F3/F4 completo, fuzzing diferencial y una revisión externa. Tampoco satisface independencia de implementación, porque el código Python fue fuente de comportamiento.
