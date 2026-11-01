# Node differential implementation

Implementación experimental separada del oracle Python.

```bash
node implementations/node/validate.mjs
```

Resultado esperado:

```text
40/40 golden
40/40 idempotence
32/32 equivalence
```

Esta implementación demuestra portabilidad entre codebases, pero no satisface CE-2: el Charter exige Python + Rust independientes y revisión externa.
