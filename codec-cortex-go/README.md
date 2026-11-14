# codec-cortex-go

Implementación Go autónoma y funcionalmente equivalente al paquete Python de
referencia para el canon **CORTEX 1.0** (superficie fundamental + eje slots),
**C14N-1.0** y **HCORTEX-1.0**. `0.1` y `0.2` siguen siendo legibles como alias
de lectura. Versión canónica del proyecto: `1.0.0` (por tag de git).

Certificado del proyecto: paridad byte-exacta con las otras cuatro superficies
en hash (D3) y render HCORTEX (D3b), y paridad de `loss-report` (D6).

No requiere Python en producción ni acceso a internet para compilar: la única
dependencia externa necesaria para NFC está vendorizada.

## Instalación

```bash
go get github.com/FidelErnesto03/codec-cortex/codec-cortex-go
```

Binarios multiplataforma (Linux/Windows/macOS, amd64/arm64) con `make dist`;
los artefactos quedan en `bin/` junto con `SHA256SUMS` (no versionados en git).

## Capacidades

- AST tipado y atributos ordenados.
- Parser CORTEX 0.1/0.2/1.0 con diagnósticos compatibles y aridad posicional
  estricta (`I012_POSITIONAL_ARITY`).
- `G042_GLOSSARY_HEADER_INVALID`: `$0: <título>` fuera de gramática; `$0`
  desnudo válido y renderizado.
- Scalars: string, atom, integer, decimal, boolean, null y list.
- Canonicalización C14N idempotente y hash con separación de dominio.
- Render y compilación HCORTEX por esquemas pareados, byte-exactos entre
  superficies.
- `loss-report`: pérdidas declaradas en JSON canónico (catálogo 1.0 §8.2).
- Harness F3/F4 compatible con `manifest.json`.
- CLI y API Go pública.
- Fixtures y comparación diferencial Python ↔ Go.

## Compilar y probar

```bash
go test ./...
go build -o bin/codec-cortex ./cmd/codec-cortex
```

También:

```bash
make test
make vet
make build
make differential
make dist
```

`make dist` genera binarios Linux, Windows y macOS para amd64/arm64 junto con
`bin/SHA256SUMS`.

## CLI

```bash
codec-cortex parse archivo.cortex
codec-cortex validate archivo.cortex
codec-cortex canonicalize archivo.cortex
codec-cortex to-hcortex archivo.cortex
codec-cortex from-hcortex archivo.md
codec-cortex hash archivo.cortex
codec-cortex loss-report archivo.cortex    # pérdidas declaradas (JSON canónico)
codec-cortex explain-loss archivo.cortex   # legacy: diagnósticos HLOSS de 0.1
codec-cortex harness ./archive/2026-11/experiments/gate-f4/cortex ./archive/2026-11/experiments/gate-f4/hcortex-canonical --report rev-report.json
```

Todos los comandos de archivo aceptan `-` para stdin.

## API

```go
package main

import (
    "fmt"
    "os"

    cortex "github.com/FidelErnesto03/codec-cortex/codec-cortex-go/cortex"
)

func main() {
    source, err := os.ReadFile("context.cortex")
    if err != nil {
        panic(err)
    }

    doc, err := cortex.Decode(string(source))
    if err != nil {
        panic(err)
    }

    canonical, err := cortex.Encode(doc)
    if err != nil {
        panic(err)
    }

    fmt.Print(canonical)
}
```

API principal:

- `ParseCortex`, `Parse`, `Decode`
- `Canonicalize`, `Encode`
- `CanonicalHash`, `SHA256Bytes`
- `RenderHCORTEX`, `ToHCORTEX`
- `CompileHCORTEX`, `FromHCORTEX`
- `BuildLossReport`, `WriteLossReport`, `LossCaseName`
- `ExplainHCORTEXLoss` (legacy, no normativo)
- `RunPhase3`, `RunPhase4`, `RunAllTests`

## Equivalencia comprobable

```bash
./scripts/differential_check.sh
```

El script usa la copia auditiva de la implementación Python en
`reference/python/` y exige igualdad byte a byte en:

- CORTEX canónico;
- HCORTEX;
- CORTEX posterior al roundtrip.

La copia Python no participa en el build ni en el runtime Go.

## Pérdidas declaradas

`loss-report` implementa el catálogo cerrado §8.2 del canon: `L402`, `L403`,
`L405` y la guardia `L499_UNCLASSIFIED_LOSS`. La salida es byte-idéntica a la de
las otras cuatro superficies (indicador D6 del certificado).

`explain-loss` y su familia `HLOSS*` son **legacy** del dialecto 0.1: se
conservan por compatibilidad y no forman parte del catálogo 1.0. Véase
[`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md) y
[`../docs/LOSS-REPORT.md`](../docs/LOSS-REPORT.md).

## Licencia

**Apache-2.0** — ratificada 2026-10 para el proyecto completo (ver `LICENSE`
y `NOTICE` en la raíz del repositorio). La redistribución debe mantener la
atribución al autor original. Las licencias de dependencias vendorizadas se
incluyen en `vendor/`.
