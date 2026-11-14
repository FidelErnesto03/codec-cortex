# codec-cortex-rs

Implementación funcional en **Rust** del canon **CORTEX 1.0** (`0.1` y `0.2`
legibles como alias):

- parsear CORTEX 0.1/0.2/1.0, incluido el eje de slots;
- construir un AST tipado;
- canonicalizar mediante C14N con dominio por versión;
- renderizar y compilar HCORTEX 1.0;
- emitir el reporte de pérdidas declaradas (`loss-report`);
- ejecutar el harness de conformidad F3/F4;
- operar mediante una biblioteca Rust y el binario `cortex`.

> Esta entrega es un **port funcional derivado del código Python**, no una implementación independiente escrita únicamente desde la especificación. Por ello no debe contabilizarse, por sí sola, como la segunda implementación independiente exigida por Gate F7.

## Estado

Versión: `1.0.0` (canónica del proyecto; `Cargo.toml`).

Paridad verificada por el certificado del proyecto: D3 (hash) y D3b (render
HCORTEX byte-exacto) con las otras cuatro superficies, y D6 (`loss-report`
byte-idéntico).

El alcance reproduce los contratos observables del paquete Python de referencia. No incorpora runtime, sesiones, learning, perfiles de agente, ArqUX, MCP ni gobierno de proyectos.

Licencia: **Apache-2.0** (ratificada 2026-10; ver `LICENSE` y `NOTICE` en la raíz). `publish = false` permanece activo por decisión de distribución — la superficie Rust se distribuye hoy solo como binario compilado (`cargo build --release`), no vía crates.io.

## Arquitectura

```text
src/
├── model.rs      AST y valores escalares tipados
├── scalars.rs    Unicode, strings, átomos, listas y atributos
├── parser.rs     CORTEX 0.1 → AST
├── c14n.rs       AST → CORTEX canónico (0.1)
├── hcortex.rs    AST ↔ HCORTEX canónico (0.1)
├── slotparser.rs detección y hash del eje slots
├── v10.rs        parser, C14N, render y compile de 0.2/1.0
├── lossreport.rs pérdidas declaradas (loss-report 1.0)
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
cortex loss-report input.cortex
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

Superficie 1.0 y pérdidas declaradas:

```rust
use codec_cortex::v10::{canonicalize_any, compile_any, parse_any, render_any};
use codec_cortex::lossreport::{build_loss_report, dumps_canonical, loss_case_name};

let report = build_loss_report(&source, &loss_case_name("doc.cortex"))?;
print!("{}", dumps_canonical(&report));
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

## Limitaciones heredadas (dialecto 0.1)

En **HCORTEX 0.1**, una sección `table` con un símbolo `attrs` `open:true` pierde
al renderizar los atributos extra no declarados en `fields`; el fixture
`examples/full.cortex` lo fija. En **HCORTEX 1.0** esa pérdida no existe: el
renderer degrada la sección a `prose` para preservar el payload completo, y
`loss-report` declara cualquier orden editorial no preservado (`L405`).

El detalle histórico está en
[`docs/KNOWN-PARITY-LIMITATIONS.md`](docs/KNOWN-PARITY-LIMITATIONS.md).

## Documentación

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/EQUIVALENCE.md`](docs/EQUIVALENCE.md)
- [`docs/KNOWN-PARITY-LIMITATIONS.md`](docs/KNOWN-PARITY-LIMITATIONS.md)
- [`docs/VERIFICATION.md`](docs/VERIFICATION.md)
- [`VERIFICATION_REPORT.json`](VERIFICATION_REPORT.json)
- [`SOURCE_MANIFEST.json`](SOURCE_MANIFEST.json)
- [`MIGRATION.md`](MIGRATION.md)
- [`SECURITY.md`](SECURITY.md)
