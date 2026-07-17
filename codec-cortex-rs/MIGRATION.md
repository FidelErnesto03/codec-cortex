# Migración desde Python

## Correspondencia de uso

### Python

```python
from codec_cortex import parse_cortex, canonicalize, render_hcortex

doc = parse_cortex(source)
canonical = canonicalize(doc)
hcortex = render_hcortex(doc)
```

### Rust

```rust
use codec_cortex::{canonicalize, parse_cortex, render_hcortex};

let doc = parse_cortex(source)?;
let canonical = canonicalize(&doc);
let hcortex = render_hcortex(&doc);
```

## Errores

Python lanza `ParseError`; Rust devuelve `Result<T, ParseError>`. Los códigos se mantienen como strings estables.

## Canonicalización

Python muta el documento. Rust no lo muta por defecto. Para reproducir mutación explícita:

```rust
let mut doc = parse_cortex(source)?;
let canonical = codec_cortex::canonicalize_in_place(&mut doc);
```

## CLI

El ejecutable Rust agrega operaciones directas de parseo, validación, comparación e inspección. El subcomando `conformance` reemplaza el entry point principal Python.
