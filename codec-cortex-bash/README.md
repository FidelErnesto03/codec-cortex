# codec-cortex-bash

Implementación funcional en **Bash** de la referencia Python suministrada para:

- CORTEX 0.1: lexer de escalares, parser y AST.
- C14N-0.1: canonicalización determinista e idempotente.
- HCORTEX-0.1: render canónico y compilación inversa.
- Harness F3/F4: golden bytes, idempotencia, roundtrip y diagnósticos.
- SHA-256 y hash con dominio `CORTEX-C14N-0.1`.

No invoca Python ni contiene una envoltura sobre el paquete original. La implementación es Bash orientada a archivos y usa `jq` como motor de AST JSON y `uconv` para Unicode NFC.

## Requisitos

- Bash 4.3 o posterior.
- jq 1.6 o posterior.
- ICU `uconv`.
- `sed`, `awk`, `sort`, `mktemp`, `seq`, `xargs`.
- `sha256sum` o `shasum`.

En Debian/Ubuntu:

```bash
sudo apt install bash jq icu-devtools coreutils
```

## Uso directo

```bash
bin/codec-cortex validate document.cortex
bin/codec-cortex parse document.cortex
bin/codec-cortex canonicalize document.cortex
bin/codec-cortex to-hcortex document.cortex
bin/codec-cortex from-hcortex document.hcortex.md
bin/codec-cortex inspect document.cortex
bin/codec-cortex c14n-hash canonical.cortex
```

También se incluye el alias `bin/cortex`.

La entrada `-` usa stdin:

```bash
cat document.cortex | bin/codec-cortex canonicalize -
```

## Pruebas

```bash
make test              # prueba rápida contra goldens Python
make phase4            # gate HCORTEX completo incluido
make phase3            # corpus C14N de 40 casos; intensivo
make conformance       # F3 + F4
```

El paralelismo del gate F3 se controla con:

```bash
CCX_JOBS=2 make phase3
```

En máquinas con poca memoria conviene usar `CCX_JOBS=1` o `2`; `jq` multiplica el consumo al elevar el paralelismo.

## API sourceable

```bash
source lib/codec-cortex.sh
canonicalize input.cortex output.cortex
render_hcortex input.cortex output.md
compile_hcortex input.md ast.json diagnostics.json
```

La API Bash es deliberadamente orientada a archivos. `parse_cortex` devuelve el AST JSON por stdout; las funciones internas usan el prefijo `ccx_`.

## Contrato de paridad

La correspondencia exacta de módulos, reglas y comportamientos heredados está documentada en [`docs/PYTHON_PARITY.md`](docs/PYTHON_PARITY.md). La prueba rápida compara bytes contra salidas generadas por la implementación Python original.

## Alcance

Este repositorio es exclusivamente un codec. No contiene runtime, sesiones, learning, gobierno, ArqUX ni vocabularios obligatorios de agentes.
