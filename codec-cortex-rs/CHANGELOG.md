# Changelog

## 1.0.0-rc.1 — 2026-10-10

- Versión alineada a la canónica del proyecto (`Cargo.toml: 1.0.0-rc.1`).
- Licencia Apache-2.0 homologada (`LICENSE`, `NOTICE`).
- Paridad D3 verificada: el binario `cortex hash` produce el digest canónico
  `4ad4aec9…` sobre el vector semilla (certificado Nivel A, 5/5 runtimes).
- `publish = false` se mantiene: distribución solo-binario por ahora.

## 0.1.0 — 2026-07-17

- port funcional completo del paquete Python recibido;
- AST Rust tipado;
- parser CORTEX 0.1;
- canonicalizador C14N-0.1;
- renderer/compiler HCORTEX 0.1;
- harness F3/F4;
- CLI multipropósito;
- fixtures y pruebas de paridad Python;
- documentación de pérdidas heredadas;
- workflow CI.
