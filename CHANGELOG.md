# Changelog

Todos los cambios notables del proyecto se documentan aquí. El proyecto sigue
nombres canónicos sin versión en archivos/esquemas; la versión vive en los
metadatos de cada superficie y en tags de git.

## [Unreleased] — post-`1.0.0-rc.1` en `main`

### Añadido

- `archive/2026-11/` — archivo fechado del material deprecado (916
  archivos movidos con `git mv`): evidencia exploratoria pre-BLP-003,
  artefactos de gates F2–F4, herramientas de fase y revisión documental.
  Congelado bajo `archive/2026-11/SHA256SUMS` (906 archivos) con índice y
  reglas propias; los reportes antiguos llevan cabecera de deprecación.
- Punteros al archivo desde `README.md` y `docs/index.md`.

### Cambiado

- `tests/SHA256SUMS` regenerado sobre el corpus vivo (`conformance/` +
  `examples/`, 829 archivos) tras retirar los reportes archivados del
  sello.
- Documentación pública renovada (commit `fcbfb97`): tabla de
  distribución honesta (solo PyPI publicado), sección Nivel A, evidencia
  exploratoria re-etiquetada.
- Referencias corregidas a rutas archivadas en `codec-cortex-go/README.md`,
  `skill/codec-cortex.skill.md` y specs en `docs/standard/`
  (`REV-PROTOCOL`, `REV-PACKAGE-GUIDE`, `GATE-F2`, `CORTEX-SPEC-0.1`,
  `hcortex-0.1`).

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
