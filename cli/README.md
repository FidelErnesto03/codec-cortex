# codec-cortex

> Implementación funcional **parcial** del codec CODEC-CORTEX definido por
> `SKILL.md` v1.2.0-enterprise-candidate. No es una implementación
> canónica completa del protocolo; ver `STATUS.md` para la matriz exacta
> de capacidades por nivel de madurez.

`codec-cortex` es un CLI determinista (sin dependencia de LLM) que
procesa archivos `.cortex` como artefactos estructurados: parsea a AST,
serializa canónicamente, renderiza vistas humanas (HCORTEX), ejecuta
CRUD gobernado y verifica roundtrip estructural.

## Estado de madurez

| Capacidad | Estado |
|---|---|
| Parser / AST / Writer | `current` |
| HCORTEX-EDIT reversible | `current` |
| HCORTEX-READ canónico (perfiles + P0→P5 + AUDIT) | `current` (1.1.0) |
| Validación sintáctica | `current` |
| Validación cognitiva (separación de niveles, FCS/OBJ, survive) | `current` (1.1.0) |
| CRUD gobernado + escritura atómica | `current` |
| Recuperación de artefactos legacy | `current` (1.1.0) |
| Operaciones de diagrama | `current` (1.1.0) |
| Benchmark reproducible | `planned` |
| MCP server | `future` |
| Runtime de maduración (promote/decay) | `future` |

Ver `STATUS.md` para el detalle completo y `BENCHMARK.md` para la
evidencia empírica.

## Instalación

```bash
cd codec-cortex
pip install -e .
```

O sin instalación:

```bash
export PYTHONPATH=$(pwd)/src
python -m cortex --help
```

## Quick start

```bash
# Crear brain.cortex
cortex new brain --name my-brain --out brain.cortex

# Validar (estricto)
cortex verify brain.cortex --strict --kind brain

# Render HCORTEX-EDIT (reversible)
cortex render brain.cortex --mode edit --out brain.hcortex.edit.md

# Compilar de vuelta a .cortex
cortex compile brain.hcortex.edit.md --out brain.compiled.cortex

# Roundtrip completo
cortex verify brain.cortex --roundtrip hcortex-edit

# Render HCORTEX-AUDIT con perfil WORK
cortex render brain.cortex --mode audit --profile work --out brain.audit.md

# CRUD
cortex list brain.cortex
cortex get brain.cortex FCS:primary
cortex add brain.cortex --section $2 --sigil FCS --name secondary \
    --value 'what:"side task", priority:"medium", status:"planned", survive:"work"'
cortex update brain.cortex FCS:primary --set what="new focus"
cortex delete brain.cortex FCS:secondary
cortex move brain.cortex FCS:primary --to-section $3

# Glosario + micro-tokens
cortex glossary list brain.cortex
cortex glossary add brain.cortex --sigil PFL --name pitfall --type attrs \
    --risk M --layer Prefrontal --description "Known antipattern"
cortex micro list brain.cortex
cortex micro add brain.cortex --token xyz --value "custom value"

# Diagnóstico y diff
cortex doctor brain.cortex --strict --kind brain
cortex diff brain.cortex brain.compiled.cortex --profile structural

# Recuperación de artefactos legacy
cortex recover legacy.cortex --out legacy.fixed.cortex

# Diagramas
cortex diagram list brain.cortex
cortex diagram extract brain.cortex --name flow
cortex diagram validate brain.cortex

# Formato canónico
cortex format brain.cortex --out brain.formatted.cortex

# JSON output (el flag --json va ANTES del subcomando)
cortex --json new brain --out brain.cortex --force
cortex --json list brain.cortex
cortex --json render brain.cortex --mode edit
```

## JSON output

El flag global `--json` (que va **antes** del subcomando: `cortex --json new ...`)
produce salida JSON parseable en todos los comandos que soportan
automatización: `new`, `render`, `compile`, `verify`, `get`, `list`,
`add`, `update`, `delete`, `move`, `glossary`, `micro`, `doctor`, `diff`,
`format`, `recover`, `diagram`.

Los comandos `get`, `list`, `glossary list`, `micro list`, `doctor`, `diff`,
`recover` y `diagram` también aceptan `--format json` como flag local.

## Aliases CLI

Para alinear con el contrato planificado del SKILL §22.2:

| Alias | Equivalente |
|---|---|
| `cortex decode` | `cortex render` |
| `cortex encode` | `cortex compile` |
| `cortex patch_add` | `cortex add` |
| `cortex patch_update` | `cortex update` |
| `cortex patch_remove` | `cortex delete` |

## Arquitectura

```
src/cortex/
  cli/             argparse entry point + 17 comandos (15 + recover + diagram)
  core/            lexer, parser, ast, writer, validator, compare, errors,
                   document_kind  (NUEVO 1.1.0)
  glossary/        $0 model, minimal sigil sets, resolver, contracts
  hcortex/         READ renderer, EDIT renderer, EDIT parser,
                   profiles  (NUEVO 1.1.0)
                   recovery  (NUEVO 1.1.0)
  crud/            selectors, mutations, atomic transactions
  templates/       brain / skill / package / generic factories
src/tests/         61+ tests + fixtures + invalid examples
```

## Códigos de error

30 códigos `E0xx_*` implementados. Ver `src/cortex/core/errors.py` para
el catálogo completo y `CHANGELOG.md` para los añadidos en 1.1.0.

## Tests

```bash
# Instalar con dependencias dev (incluye pytest)
pip install -e ".[dev]"

# O alternativamente:
pip install -e . pytest

# Ejecutar la suite completa
python -m pytest src/tests/ -v

# Demo portátil end-to-end
bash scripts/cortex_demo_v1_1_8.sh
```

## Licencia

MIT. Ver `LICENSE`.

## Autoría

Fidel Ernesto Lozada A. — `SKILL.md` v1.2.0-enterprise-candidate.
