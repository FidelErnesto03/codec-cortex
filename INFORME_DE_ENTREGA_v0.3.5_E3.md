# Informe de entrega — CODEC-CORTEX v0.3.5 E3

## Alcance

v0.3.5 implementa el protocolo documental E3 sobre `main`, preservando v0.3.4 como release previa.

## Entregables

| Área | Entrega |
|---|---|
| Documentación central | `docs/README.md` |
| Documentación humana | `docs/hcortex/` |
| Fuente API para agentes | `docs/cortex/api/*.cortex` |
| Especificación documental | `docs/cortex/specs/documentation-protocol.cortex` |
| Docstrings | `cortex docstring` |
| Benchmarks | `cortex benchmark` |
| CI | coverage gate, verify docs API, docstring smoke, benchmark inventory |

## Verificación mínima

| Check | Estado |
|---|---|
| Sintaxis Python de módulos E3 | verificada localmente |
| Tests E3 nuevos | incluidos |
| Package metadata | actualizado |
| CI gates | actualizados |

## Comandos esperados

```bash
cd cli
pip install -e .[dev]
ruff check src/
python -m pytest src/tests/ -q --cov-config ../.coveragerc
for f in ../docs/cortex/api/*.cortex; do cortex verify "$f" --strict; done
cortex docstring canonicalize
cortex benchmark --list
SETUPTOOLS_SCM_PRETEND_VERSION=0.3.5 python -m build
```
