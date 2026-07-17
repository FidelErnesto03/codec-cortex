# Verificación de la entrega

## Base recibida

- Archivo: `codec_cortex.tar.gz`
- SHA-256: `47640ad335bc8f422d346c3f962b12e5e7b317b06080560d1b25070eb54259b2`
- Módulos auditados: `scalars.py`, `parser.py`, `c14n.py`, `hcortex.py`, `harness.py`, `__init__.py`, `__main__.py`.

## Evidencia generada

### Fixture reversible

`tests/fixtures/roundtrip.cortex` fue procesado por Python para generar:

- `roundtrip.canonical.cortex`;
- `roundtrip.hcortex.md`;
- `roundtrip.reference.json`.

Resultados de referencia:

```text
canonical SHA-256 fbee0b99e464dfee332c2e6ed21f60b28c7f46764e66dc05b6efa243bf649c58
HCORTEX  SHA-256 35ed3d5381050ca31a775ecd62b0e16406a02b61b8d91e1e851102ca80556242
roundtrip_equal    true
```

### Fixture integral con pérdida conocida

`examples/full.reference.json` demuestra la omisión de `extra:z` en HCORTEX. Esa diferencia no está ocultada.

## Validaciones realizadas en este entorno

- extracción y lectura completa del paquete Python;
- ejecución de la referencia Python sobre fixtures;
- generación de bytes dorados y hashes;
- análisis sintáctico de todos los archivos `.rs` mediante parser Tree-sitter Rust;
- revisión de API y mapping módulo por módulo;
- incorporación de tests unitarios e integración diferencial.

## Validación no ejecutada aquí

Este entorno solo disponía de los lanzadores de `rustup`, sin un toolchain Rust instalado; la descarga del toolchain no pudo completarse por indisponibilidad de DNS saliente. Por tanto, no se afirma falsamente que `cargo test` haya sido ejecutado localmente.

La CI incluida ejecutará:

```bash
cargo check --all-targets
cargo clippy --all-targets --all-features
cargo test --all-targets
cargo build --release
```

Antes de etiquetar una release deben añadirse `Cargo.lock`, el reporte real de CI y el corpus F3/F4 completo.

## Reporte legible por máquina

Los resultados y las limitaciones de esta revisión están fijados en `VERIFICATION_REPORT.json`.
