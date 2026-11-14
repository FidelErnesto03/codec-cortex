# API Python y referencia de CLI

Guía para desarrolladores: modelo de datos, módulos públicos y comandos de las
cinco superficies. El paquete se instala desde PyPI.

---

## Instalación

```bash
pip install codec-cortex        # Python 3.10+, sin dependencias externas
```

## Modelo de datos

```python
Document(
    cortex_version: str,        # "0.1" | "0.2" | "1.0"
    encoding: str,
    glossary: Glossary,
    sections: list[Section],
)

Glossary(
    capa: str | None,           # KERNEL|CORE|KNOW|DATA|FLOW|CACHE o None
    format: FormatDecl | None,  # $0:format
    meta, enums, micros, namespaces, extensions,
    symbols: list[SymbolDef],
)

Section(id: int, title: str | None, ideas: list[Idea], capa: str | None)

Idea(
    section: int,
    namespace: str | None,
    symbol: str,                # sigilo
    name: str,
    shape: str,                 # attrs|attrs-pos|relacion|cuerpo|bloque|slots
    payload: tuple,             # ("attrs", [(k, Scalar)]) | (shape, [Scalar])
                                # | (shape, str) | ("slots", [FieldValue])
    source_line: int,
)

Scalar(kind, value, lexeme)     # kind: string|atom|integer|decimal|boolean|null|list
SymbolDef(sigil, label, shape, weight, focus, desc, open, contract, attrs, encoding)
ContractField(name, type, required, position)
```

## Módulos públicos

### `codec_cortex.api` — fachada de dominio (recomendado)

```python
import codec_cortex as cc

doc = cc.parse(source)          # cualquier dialecto declarado (0.1, 0.2, 1.0)
cc.validate(source)             # idem; ParseError si es inválido
canon = cc.canonicalize(doc)    # bytes canónicos (str)
digest = cc.hash(doc)           # "sha256:<64hex>"
digest = cc.hash_source(source) # parse + hash en un paso
md = cc.to_hcortex(doc)         # render HCORTEX (despacha por dialecto)
doc2 = cc.from_hcortex(md)      # compile HCORTEX; CompileError con .diagnostics
```

`CompileError.diagnostics` es una lista de `{code, severity, message, line}`.
Los módulos internos (`parser`, `slotparser`, `dispatcher`, …) siguen
importables para compatibilidad; el facade es la superficie estable.

### `codec_cortex.emit` — emisión de líneas de ideas

```python
import codec_cortex as cc

cc.emit("KNW", "alpha", {"topic": "T", "content": 'com "comillas" y\nnewline'})
# → KNW:alpha{topic:"T",content:"com \"comillas\" y\nnewline"}

cc.emit("POS", "p1", ["a", 1], shape="attrs-pos")   # → POS:p1|"a"|1
cc.emit("BOD", "t1", "línea 1\nlínea 2")            # cuerpo multilínea
cc.emit("KNW", "ns1", {"k": "v"}, namespace="tenant.x")  # tenant.x::KNW:ns1{...}
```

Escapes canónicos automáticos (comillas, saltos, tabs). Valida sigilos,
namespaces, nombres y shapes; `shape` se infiere del payload si se omite
(`dict`→attrs, `list`→attrs-pos, `str`/`None`→cuerpo).

### `codec_cortex.dispatcher` — punto de entrada único

```python
from codec_cortex import parse_cortex, canonicalize, hash_cortex

doc = parse_cortex(source)      # enruta por $0:format{cortex:X}
canon = canonicalize(doc)       # bytes canónicos del dialecto detectado
digest = hash_cortex(doc)       # hash canónico con dominio por versión (hex)…
                                # …la CLI lo imprime como sha256:<64hex>
```

- `parse_cortex` lanza `ParseError` con `.code` (p. ej. `G042_GLOSSARY_HEADER_INVALID`).
- La versión **se declara**, nunca se infiere por contenido.
- `canonicalize` puede mutar el AST en memoria (expansión de microtokens,
  normalización de atributos). Si vas a renderizar y canonicalizar el mismo
  documento, **renderizá primero**.

### `codec_cortex.parser` / `slotparser` — sintaxis

```python
from codec_cortex.parser import parse_cortex as parse_01     # superficie fundamental
from codec_cortex.slotparser import parse_slots              # 0.2 y 1.0

doc01 = parse_01(source)
doc10 = parse_slots(source, version="1.0")
```

### `codec_cortex.hcortex` / `slothcortex` — HCORTEX

```python
from codec_cortex.slothcortex import render_hcortex_slots, compile_hcortex_slots

hc = render_hcortex_slots(doc)                 # función pura del AST
doc2, diags = compile_hcortex_slots(hc)        # compila y auto-valida su salida
```

`compile_hcortex_slots` devuelve `(None, diags)` si el HCORTEX es inválido.
La superficie `codec_cortex.hcortex` (`render_hcortex`, `compile_hcortex`) es la
de HCORTEX 0.1 y se conserva como alias de lectura.

### `codec_cortex.lossreport` — pérdidas declaradas

```python
from codec_cortex.lossreport import build_loss_report, dumps_canonical, loss_case_name

report = build_loss_report(source, loss_case_name("doc.cortex"))
print(dumps_canonical(report))          # JSON canónico (bytes estables)
```

Estructura del reporte y catálogo: [`LOSS-REPORT.md`](LOSS-REPORT.md).

### `codec_cortex.harness` / `slotharness` — conformidad

```python
from codec_cortex.harness import run_all_tests          # harness F3/F4 histórico
from codec_cortex.slotharness import run_slots_conformance
```

## CLI

| Comando | Python | Go | Node | Rust | Bash |
|---|---|---|---|---|---|
| `parse` | sí | sí | sí | sí | sí |
| `validate` | sí | sí | — | sí | sí |
| `canonicalize` | sí | sí | sí | sí | sí |
| `hash` | sí | sí | sí | sí | `c14n-hash` |
| `to-hcortex` | sí | sí | sí | sí | sí |
| `from-hcortex` | sí | sí | sí | sí | sí |
| `loss-report` | sí | sí | sí | sí | sí |
| `diff` | sí | — | — | — | — |
| `verify` | sí | — | — | — | — |
| `migrate` | sí | — | — | — | — |
| `conformance` | sí | sí | `test` | sí | `test` |
| `compare` / `inspect` | — | — | — | `compare`, `inspect` | `inspect` |

Ejemplos:

```bash
python -m codec_cortex validate doc.cortex
python -m codec_cortex canonicalize doc.cortex > doc.canon.cortex
python -m codec_cortex hash doc.cortex
python -m codec_cortex to-hcortex doc.cortex > doc.md
python -m codec_cortex from-hcortex doc.md > doc.back.cortex
python -m codec_cortex loss-report doc.cortex
python -m codec_cortex diff doc-a.cortex doc-b.cortex   # diff semántico (canónico)
python -m codec_cortex verify doc.cortex sha256:<hex>   # o <hex> u otro .cortex
python -m codec_cortex migrate to-1.0 --apply doc.cortex
```

`diff` compara la **forma canónica** (no el texto): exit `0` si canonizan
igual, `1` con unified diff si difieren, `2` en error de uso/parseo.
`verify` acepta `sha256:<hex>`, hex desnudo de 64 chars, o un archivo
`.cortex` (comparación semántica con diff en caso de mismatch).

Todas las superficies aceptan `-` como entrada estándar.

### Exit codes

| Código | Significado |
|---|---|
| `0` | éxito |
| `1` | documento inválido, compile fallido o `L499_UNCLASSIFIED_LOSS` |
| `2` | uso incorrecto (Python) |

> Nota de ergonomía: el exit code de uso incorrecto no está unificado entre
> superficies (Python `2`, otras `1`). Los scripts deben tratar "no cero" como
> fallo, no como código específico.

## Flujo típico

```python
from codec_cortex import canonicalize, parse_cortex
from codec_cortex.slothcortex import compile_hcortex_slots, render_hcortex_slots

doc = parse_cortex(open("doc.cortex", encoding="utf-8").read())
hc = render_hcortex_slots(doc)                 # 1. mostrar al humano
doc_back, diags = compile_hcortex_slots(hc)    # 2. volver a máquina
assert not diags
assert canonicalize(doc_back) == canonicalize(doc)   # 3. el AST va y vuelve
```

## Referencias

| Documento | Contenido |
|---|---|
| [LOSS-REPORT.md](LOSS-REPORT.md) | pérdidas declaradas |
| [MIGRATION-1.0.md](MIGRATION-1.0.md) | migración desde 0.1/0.2 |
| [standard/CORTEX-SPEC-1.0.md](standard/CORTEX-SPEC-1.0.md) | canon normativo |
| [../skill/codec-cortex.skill.md](../skill/codec-cortex.skill.md) | el estándar en CORTEX |
