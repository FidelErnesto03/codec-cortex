# STATUS — codec-cortex v0.3.5

> Matriz de madurez de capacidades. Ningún claim debe presentarse como `current` sin evidencia reproducible.

## Capacidades v0.3.5 E3

| Capacidad | Estado | Evidencia |
|---|---|---|
| Documentación central | `current` | `docs/README.md` |
| HCORTEX humano | `current` | `docs/hcortex/tutorials/getting-started.md` |
| API reference CORTEX | `current` | `docs/cortex/api/*.cortex` |
| Docstring derivada | `current` | `cortex docstring canonicalize` |
| Benchmark inventory | `current` | `cortex benchmark --list` |
| Coverage gate | `current` | `.coveragerc` + CI |

## Límites

| Área | Límite |
|---|---|
| `cortex docstring` | Lee `docs/cortex/api` desde el checkout del repositorio |
| `cortex benchmark` | Inventaria suites versionadas; no ejecuta modelos externos |
| Publicación v0.3.5 | Requiere tag `v0.3.5` |
