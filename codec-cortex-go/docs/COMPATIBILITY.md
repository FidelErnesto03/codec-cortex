# Python compatibility contract

`codec-cortex-go` is a behavior-preserving Go port of the supplied Python package.
The Go runtime does not invoke Python; the Python source is retained only under
`reference/python/` for audit and differential verification.

## Module mapping

| Python | Go |
|---|---|
| `scalars.py` | `cortex/scalars.go` |
| `parser.py` | `cortex/parser.go` |
| `c14n.py` | `cortex/canonical.go` |
| `hcortex.py` | `cortex/hcortex.go` |
| `harness.py` | `cortex/harness.go` |
| `__main__.py` | `cmd/codec-cortex/main.go` |
| `__init__.py` exports | package `cortex` public API |

## Preserved behavior

- CORTEX 0.1 scalar kinds and lexemes.
- Parse error codes and source positions where the Python code reports them.
- Source-order AST with ordered attributes.
- C14N-0.1 key ordering, NFC normalization, microtoken expansion and final LF.
- Domain-separated C14N hash.
- HCORTEX paired-schema rendering and compilation.
- F3/F4 manifest harness, thresholds and verdict semantics.
- Namespace-qualified symbols such as `agent::FCS`.

## Inherited HCORTEX limitations

These are observable behaviors of the supplied Python implementation and are
therefore preserved rather than silently corrected:

1. In table schema, `attrs` fields outside the declared contract are not rendered,
   even when the symbol is `open:true`.
2. Empty sections are rendered without a paired schema block and are not reconstructed.
3. Untitled sections receive a synthesized title when rendered.
4. The HCORTEX compiler indexes symbol shape by unqualified lowercase sigil, so
   identical sigils in different namespaces can collide.
5. Pipe characters inside table values are not escaped by the renderer.
6. HCORTEX compilation trims boundary whitespace in prose and diagram bodies.
7. Invalid symbol declarations inside the hidden glossary are ignored by the Python
   compiler and the Go compatibility compiler.

Use `codec-cortex explain-loss FILE` or `cortex.ExplainHCORTEXLoss` to identify
these risks before conversion. This diagnostic is additive and does not alter
compatibility output.
