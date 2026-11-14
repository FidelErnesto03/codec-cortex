# codec-cortex-bash

Versión canónica del proyecto: `1.0.0` (`CCX_VERSION` en `lib/codec-cortex.sh`).

Implementación funcional en **Bash** de la referencia Python para el canon
**CORTEX 1.0** (`0.1` y `0.2` legibles como alias):

- CORTEX 1.0: lexer de escalares, parser, AST y eje de slots.
- C14N determinista e idempotente, con dominio separado por versión.
- HCORTEX 1.0: render canónico y compilación inversa.
- `loss-report`: pérdidas declaradas en JSON canónico (catálogo §8.2).
- Harness F3/F4: golden bytes, idempotencia, roundtrip y diagnósticos.
- SHA-256 y hash canónico.

Paridad verificada por el certificado del proyecto: D3, D3b, D6 y D7 con las
otras cuatro superficies.

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
bin/codec-cortex loss-report document.cortex
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
bash tests/self-test-slots.sh          # superficie slots
bash tests/self-test-loss-report.sh    # paridad de loss-report + G042 (6/6)
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
