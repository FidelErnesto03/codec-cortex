# codec-cortex-rs

Implementación funcional en **Rust** del paquete Python suministrado para:

- parsear CORTEX 0.1;
- construir un AST tipado;
- canonicalizar mediante C14N-0.1;
- renderizar y compilar HCORTEX 0.1;
- ejecutar el harness de conformidad F3/F4;
- operar mediante una biblioteca Rust y el binario `cortex`.

> Esta entrega es un **port funcional derivado del código Python**, no una implementación independiente escrita únicamente desde la especificación. Por ello no debe contabilizarse, por sí sola, como la segunda implementación independiente exigida por Gate F7.

## Estado

Versión inicial: `0.1.0`.

El alcance reproduce los contratos observables del paquete Python recibido. No incorpora runtime, sesiones, learning, perfiles de agente, ArqUX, MCP ni gobierno de proyectos.

La licencia no se ha inventado ni reasignado: `publish = false` permanece activo hasta que el propietario defina la licencia del código fuente y del port.

## Arquitectura

```text
src/
├── model.rs      AST y valores escalares tipados
├── scalars.rs    Unicode, strings, átomos, listas y atributos
├── parser.rs     CORTEX 0.1 → AST
├── c14n.rs       AST → CORTEX canónico
├── hcortex.rs    AST ↔ HCORTEX canónico
├── harness.rs    Gates F3/F4, hashes y reporte
├── error.rs      diagnósticos estructurados
├── lib.rs        API pública
└── main.rs       CLI `cortex`
```

## Construcción

Requisitos:

- toolchain estable de Rust;
- Cargo;
- acceso a las dependencias declaradas en `Cargo.toml`.

```bash
cargo build --release
cargo test --all-targets
```

El binario resultante será:

```bash
target/release/cortex
```

## CLI

```bash
cortex parse input.cortex
cortex validate input.cortex
cortex canonicalize input.cortex -o canonical.cortex
cortex to-hcortex input.cortex -o input.hcortex.md
cortex from-hcortex input.hcortex.md -o reconstructed.cortex
cortex from-hcortex input.hcortex.md --format ast
cortex hash input.cortex
cortex compare left.cortex right.cortex
cortex inspect input.cortex --json
cortex conformance PATH_C14N PATH_HCORTEX -r report.json
```

`-` puede utilizarse como entrada estándar.

## API

```rust
use codec_cortex::{
    canonicalize, compile_hcortex, parse_cortex, render_hcortex,
};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let source = std::fs::read_to_string("context.cortex")?;
    let document = parse_cortex(&source)?;

    let canonical = canonicalize(&document);
    let hcortex = render_hcortex(&document);

    let (reconstructed, diagnostics) = compile_hcortex(&hcortex);
    assert!(diagnostics.is_empty());
    assert_eq!(canonicalize(&reconstructed.unwrap()), canonical);
    Ok(())
}
```

## Pruebas de paridad

`tests/reference_parity.rs` fija como vectores dorados salidas generadas por la implementación Python:

- bytes C14N;
- bytes HCORTEX;
- roundtrip estructural;
- idempotencia;
- códigos de diagnóstico;
- hashes SHA-256.

Para una comparación diferencial directa:

```bash
python tools/differential.py \
  --python-root /ruta/al/paquete-python \
  --rust-bin target/release/cortex \
  tests/fixtures/roundtrip.cortex
```

## Limitaciones heredadas

La equivalencia incluye conductas defectuosas del original cuando forman parte de su salida observable. La más relevante es esta:

- En secciones HCORTEX de tipo `table`, un símbolo `attrs` con `open:true` pierde al renderizar los atributos extra no declarados en `fields`. El fixture `examples/full.cortex` fija y demuestra esa pérdida.

No debe afirmarse reversibilidad total para ese subconjunto hasta corregir conjuntamente especificación, Python, Rust y corpus. Véase [`docs/KNOWN-PARITY-LIMITATIONS.md`](docs/KNOWN-PARITY-LIMITATIONS.md).

## Documentación

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/EQUIVALENCE.md`](docs/EQUIVALENCE.md)
- [`docs/KNOWN-PARITY-LIMITATIONS.md`](docs/KNOWN-PARITY-LIMITATIONS.md)
- [`docs/VERIFICATION.md`](docs/VERIFICATION.md)
- [`VERIFICATION_REPORT.json`](VERIFICATION_REPORT.json)
- [`SOURCE_MANIFEST.json`](SOURCE_MANIFEST.json)
- [`MIGRATION.md`](MIGRATION.md)
- [`SECURITY.md`](SECURITY.md)
