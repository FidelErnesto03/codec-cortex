# API Reference en CORTEX

La fuente canónica de referencia de comandos vive en archivos `.cortex`, uno por comando.

| Comando | Fuente |
|---|---|
| canonicalize | `canonicalize.cortex` |
| convert | `convert.cortex` |
| verify | `verify.cortex` |
| doctor | `doctor.cortex` |
| audit | `audit.cortex` |
| modes | `modes.cortex` |
| docstring | `docstring.cortex` |
| benchmark | `benchmark.cortex` |

Validación esperada:

```bash
cortex verify docs/cortex/api/canonicalize.cortex --strict
cortex docstring canonicalize
```
