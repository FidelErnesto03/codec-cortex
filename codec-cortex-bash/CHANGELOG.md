# Changelog

## 1.0.0-rc.1 — 2026-10-10

- Versión alineada a la canónica del proyecto (`CCX_VERSION=1.0.0-rc.1`).
- Licencia Apache-2.0 homologada (`LICENSE`, `NOTICE`).
- Paridad D3 verificada: `bin/codec-cortex c14n-hash` produce el digest
  canónico `4ad4aec9…` sobre el vector semilla (certificado Nivel A, 5/5 runtimes).

## 0.1.0 — 2026-07-17

- Port funcional de los siete módulos Python suministrados.
- Parser CORTEX y AST JSON.
- Canonicalizador C14N-0.1.
- Renderer y compilador HCORTEX-0.1.
- Harness F3/F4 y hashes.
- CLI ampliado y API Bash sourceable.
- Corpus autocontenido y goldens diferenciales.
