# CHANGELOG — codec-cortex

## [0.3.5] — 2026-07-01

> Release E3 — Protocolo de Documentación

### Added
- `docs/README.md` central para navegación por audiencia y formato.
- Estructura `docs/hcortex/` con tutorial, how-to, explicación y referencia humana.
- Estructura `docs/cortex/api/*.cortex` con referencia API autocontenida por comando.
- `cortex docstring` para derivar docstrings desde `docs/cortex/api/`.
- `cortex benchmark` para inventario/validación local de suites bajo `benchmarks/`.
- Tests E3 para docstrings, wrapper CLI y benchmark inventory.
- `.coveragerc` y gate `pytest-cov` con umbral mínimo 85%.

### Changed
- Entry point del paquete apunta a `cortex.cli.main_e3:main`, preservando fallback al CLI histórico.
- CI valida fuentes de documentación API, docstring canónica y benchmark inventory.
- `python -m cortex` usa el wrapper E3.

## [0.3.4] — 2026-07-01

> Release E2 — Security & Governance

### Added
- Secret scanner: `cortex doctor --scan-secrets`.
- Mutation gates: `--mode read-only|editor|admin`, env `CORTEX_MODE`.
- Audit log bajo demanda: `cortex audit on/off/status/snapshot/prune`.
- `cortex verify --signature` para verificación de integridad.
- Dependabot para pip y GitHub Actions.
- 68 nuevos tests, 409 total.

### Changed
- `cortex doctor` incluye scan de secretos bajo demanda.
- Pre-commit hooks: detect-secrets + cortex-secret-scan.

## [0.3.3] — 2026-07-01

> Release E1 — Distribution & CI/CD completado

### Added
- GitHub Actions CI: ruff lint, test 3.9-3.12, verify, build y publish.
- Ruff 0 errores.
- workflow_dispatch trigger.
- Personal files fuera de git.

### Changed
- `pip install codec-cortex` desde PyPI.

## [0.3.2] — 2026-07-01

> Release canónica: nombres canónicos sin prefijo `v2-`, fix de `canonicalize`, migración del corpus a VIEW directives e integración del agente con workflows operativos.

### Added
- Nombres canónicos CLI sin prefijo `v2-`.
- Flag `--preserve` en `cortex canonicalize`.
- VIEW-aware behavior en `cortex canonicalize`.

### Fixed
- B-01/B-05: `canonicalize` preserva estructura cuando no hay VIEW.
