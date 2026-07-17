# Porting report

## Scope

The supplied archive contained seven Python source modules implementing:

- scalar parsing and string escaping;
- the CORTEX 0.1 AST and parser;
- C14N-0.1 canonicalization and hashing;
- HCORTEX 0.1 rendering and compilation;
- F3/F4 conformance harness execution;
- a Python module CLI.

The Go port implements all of those responsibilities as a standalone module and
adds an idiomatic multi-command CLI without changing the compatibility APIs.

## Structural choices

- Ordered slices are used for attributes; Go maps are not used where ordering affects bytes.
- Scalars retain both semantic value and canonical/source lexeme.
- Idea payloads are typed as attrs, positional cells or body text rather than `any`.
- Unicode NFC is provided by vendored `x/text` code, allowing offline builds.
- The CLI supports stdin with `-` and emits machine-readable JSON for AST,
  diagnostics, loss reports and harness reports.

## Verification

The included fixture exercises:

- attrs, attrs-pos, cuerpo, bloque and relacion shapes;
- namespaces, extensions, enums, micros and generic metadata;
- booleans, null, integers, decimals, strings and lists;
- Unicode decomposition/composition;
- canonical ordering and HCORTEX roundtrip.

`./scripts/differential_check.sh` executes both implementations and requires
byte-identical canonical CORTEX, HCORTEX and roundtrip output.
