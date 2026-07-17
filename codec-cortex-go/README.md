# codec-cortex-go

Implementación Go autónoma y funcionalmente equivalente al paquete Python
suministrado para **CORTEX 0.1**, **C14N-0.1** y **HCORTEX-0.1**.

No requiere Python en producción ni acceso a internet para compilar: la única
dependencia externa necesaria para NFC está vendorizada.

## Capacidades

- AST tipado y atributos ordenados.
- Parser CORTEX con diagnósticos compatibles.
- Scalars: string, atom, integer, decimal, boolean, null y list.
- Canonicalización C14N idempotente.
- Hash `CORTEX-C14N-0.1` con separación de dominio.
- Render y compilación HCORTEX por esquemas pareados.
- Harness F3/F4 compatible con `manifest.json`.
- CLI y API Go pública.
- Auditoría explícita de pérdidas HCORTEX heredadas.
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
codec-cortex explain-loss archivo.cortex
codec-cortex harness ./c14n-corpus ./gate-f4 --report rev-report.json
```

Todos los comandos de archivo aceptan `-` para stdin.

## API

```go
package main

import (
    "fmt"
    "os"

    cortex "github.com/codec-cortex/codec-cortex-go/cortex"
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
- `ExplainHCORTEXLoss`
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

## Limitaciones heredadas

La implementación base no garantiza roundtrip HCORTEX para todos los constructos.
El port preserva esos resultados para ser equivalente, pero los expone mediante
`explain-loss`. Véase [`docs/COMPATIBILITY.md`](docs/COMPATIBILITY.md).

## Licencia

El archivo Python suministrado no incluía una licencia del proyecto. Antes de
redistribuir públicamente este port debe incorporarse la licencia que corresponda.
Las licencias de dependencias vendorizadas sí se incluyen en `vendor/`.
