# Changelog

Todos los cambios notables del proyecto se documentan aquí. El proyecto sigue
nombres canónicos sin versión en archivos/esquemas; la versión vive en los
metadatos de cada superficie y en tags de git.

## [1.0.0-rc.1] — 2026-10-10

Publicado en PyPI como `codec-cortex 1.0.0rc1` (pre-release; `latest` en PyPI
permanece en 0.6.2).

### Añadido

- Dialecto **CORTEX 0.2 (SLOTS)**: `slotparser`, `slotc14n`, `slothcortex`,
  `slotmigrate`, `slotharness` + spec `CORTEX-SPEC-SLOTS.md`, `C14N-SLOTS.md`,
  `hcortex-slots.md` + dispatcher por `$0:format{cortex:X}`.
- `bench/` — harness del certificado Nivel A (D1–D6) con preregistro,
  corpus held-out sellado y scorer mecánico (BLP-003).
- `.github/workflows/certificate.yml` — certificado reproducible en CI:
  compila los runtimes Go y Rust antes de medir paridad.
- `tests/SHA256SUMS` — sello del corpus (845 archivos).
- `instrument_sha256` en el certificado — el hash del instrumento queda
  ligado para detectar deriva entre corridas.
- `bench/results/audit.sig` — firma del Nivel A por auditor independiente
  (Heimdall), tras re-ejecución y verificación byte-exacta contra el wheel
  de PyPI (2026-11-01).

### Cambiado

- Licencia ratificada a **Apache-2.0** con atribución obligatoria,
  homologada en las cinco superficies (`LICENSE`, `NOTICE`, `AUTHORS.md`).
- `go.mod` corregido a la ruta real del repositorio
  (`github.com/FidelErnesto03/codec-cortex/codec-cortex-go`).
- URLs de `pyproject.toml` corregidas al repositorio real.
- Paridad D3 ampliada a **5/5 runtimes** (bash, go, node, python, rust).

### Corregido

- Binarios precompilados Go en `bin/` reconstruidos (estaban obsoletos y
  fallaban `S005` sobre el corpus; la fuente era correcta).
- `.pyc` retirados del índice de git.

## [0.6.2] — 2026-07

Última línea estable previa al candidato 1.0. Ver tags `v0.x` para el
historial detallado.
