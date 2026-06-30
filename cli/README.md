# codec-cortex

> Implementación determinista del codec CODEC-CORTEX v0.3.2. El núcleo v2 soporta CORTEX ⇄ HCORTEX verificable sobre los artefactos canónicos del paquete. CORTEX es el formato denso nativo; HCORTEX es su representación humana reversible.

`codec-cortex` procesa artefactos `.cortex` y `.hcortex.md` sin depender de LLM: parsea a AST, serializa CORTEX, renderiza HCORTEX, ejecuta validaciones VIEW, compara equivalencia y valida roundtrip bidireccional.

> **v0.3.2 — Naming canónico:** los comandos `v2-*` se han renombrado a sus formas canónicas (`roundtrip`, `convert`, `roundtrip-bidir`, `compare`, `verify-view`, `explain-loss`, `canonicalize`, `inspect`). Los nombres `v2-*` se mantienen como alias deprecados y emiten un `WARNING` a stderr al ser invocados. Serán eliminados en v1.0.0.

## Modelo conceptual v0.3.2

| Concepto | Rol | Estado |
|---|---|---|
| **CORTEX** | Representación densa nativa. Fuente canónica operacional y base de verificación, reversible por contrato VIEW. | `current` |
| **HCORTEX / HUMAN-CORTEX** | Representación humana densa y reversible cuando conserva VIEW/trazabilidad equivalente con cobertura válida. | `current` |
| **VIEW** | Contrato declarativo de correspondencia CORTEX ⇄ HCORTEX. Define render, reversión, campos, preservación y fallback. | `current` |
| **CORTEX-OUT** | Respuesta conversacional eficiente. No participa en decode/encode/verify/roundtrip. | `specification` |

HCORTEX canónico no es "Markdown bonito". Para declararse canónico debe poder participar en `decode/encode/verify/roundtrip` mediante VIEW o trazabilidad equivalente. Un Markdown sin VIEW/trazabilidad se considera `display-only` y debe reportar `reversible:false`.

## Gate de reversibilidad

`reversible:true` solo es válido cuando:

1. `view_coverage == 100%`;
2. no existen errores `E_VIEW_*` ni `E_HCORTEX_*`;
3. el modo no es `display`;
4. el roundtrip canónico aplicable pasa sin pérdida no declarada.

## Estado de madurez

| Capacidad | Estado | Evidencia principal |
|---|---|---|
| CORTEX v2 parser/writer | `current` | `cortex roundtrip` byte-identical |
| CORTEX → HCORTEX | `current` | genera `skill/hcortex/SKILL.md` byte-identical |
| HCORTEX → CORTEX | `current` | reconstruye 266/266 entries en `skill/cortex/SKILL.md` |
| Roundtrip bidireccional | `current` | `cortex roundtrip-bidir` rc=0, 0 diffs en ambos artefactos canónicos |
| VIEW coverage | `current` | 44/44 VIEW en skill; 10/10 artefactos del corpus migrados a VIEW en v0.3.2 |
| `cortex canonicalize` (VIEW-aware) | `current` | preserva estructura sin VIEW; canonicalización completa con VIEW (B-01/B-05 fix) |
| Hash mismatch | `current` para hashes declarados | `E_VIEW_HASH_MISMATCH` si el hash existe y no coincide |
| `doctor` legacy | `current` | diagnóstico clásico del CLI |
| `doctor` v2 | `planned` | no existe como comando separado en v0.3.2 |
| JSON global para comandos legacy soportados | `current` parcial | `--json` donde el comando lo soporta |
| JSON uniforme para todos los comandos v2 | `planned` | no declarar como actual |
| MCP server | `future` | no implementado |
| Runtime de maduración promote/decay | `future` | no implementado |

## Artefactos canónicos

| Ruta | Rol | Métrica verificada |
|---|---|---|
| `skill/cortex/SKILL.md` | CORTEX canónico | 43,925 bytes; 14 secciones; 266 entries; 44 VIEW |
| `skill/hcortex/SKILL.md` | HCORTEX canónico | 47,186 bytes; reversible; roundtrip válido |
| `benchmarks/v2.0.0/corpus/source/*.cortex` (10) | Corpus migrado a VIEW | 10/10 artefactos con VIEW directives; coverage 100% |

## Instalación

```bash
pip install -e .
# o para desarrollo
pip install -e ".[dev]"
```

## Comandos principales (nombres canónicos v0.3.2)

```bash
# Identidad
cortex --version

# Inspección y cobertura
cortex inspect skill/cortex/SKILL.md
cortex verify-view skill/cortex/SKILL.md

# Roundtrip CORTEX byte-identical
cortex roundtrip skill/cortex/SKILL.md

# CORTEX → HCORTEX
cortex convert skill/cortex/SKILL.md --from cortex --to hcortex --out /tmp/skill.hcortex.md

# HCORTEX → CORTEX
cortex convert skill/hcortex/SKILL.md --from hcortex --to cortex --out /tmp/skill.cortex.md

# Roundtrip bidireccional
cortex roundtrip-bidir skill/cortex/SKILL.md
cortex roundtrip-bidir skill/hcortex/SKILL.md

# Comparación de equivalencia
cortex compare skill/cortex/SKILL.md /tmp/skill.cortex.md

# Pérdida / canonicalización (VIEW-aware desde v0.3.2)
cortex explain-loss skill/hcortex/SKILL.md
cortex canonicalize skill/cortex/SKILL.md --out /tmp/canonical.cortex.md
cortex canonicalize benchmarks/v2.0.0/corpus/source/devops-k8s-rollout.cortex \
    --out /tmp/canonical.cortex            # WARNING: no VIEW → structure-preserving
cortex canonicalize skill/cortex/SKILL.md --preserve --out /tmp/preserved.cortex
```

### Alias deprecados (aún aceptados, removidos en v1.0.0)

| Canonical | Alias deprecado |
|-----------|------------------|
| `cortex roundtrip` | `cortex v2-roundtrip` |
| `cortex convert` | `cortex v2-convert` |
| `cortex roundtrip-bidir` | `cortex v2-roundtrip-bidir` |
| `cortex compare` | `cortex v2-compare` |
| `cortex verify-view` | `cortex v2-verify-view` |
| `cortex explain-loss` | `cortex v2-explain-loss` |
| `cortex canonicalize` | `cortex v2-canonicalize` |
| `cortex inspect` | `cortex v2-inspect` |

## Comandos legacy principales

```bash
cortex new brain --name my-brain --out brain.cortex
cortex verify brain.cortex --strict --kind brain
cortex render brain.cortex --mode edit --out brain.hcortex.edit.md
cortex compile brain.hcortex.edit.md --out brain.compiled.cortex
cortex doctor brain.cortex --strict --kind brain
cortex diff brain.cortex brain.compiled.cortex --profile structural
```

## JSON

El flag global `--json` existe, pero no todos los comandos v2 emiten JSON uniforme en v0.3.2. No declarar JSON v2 completo como capacidad actual. Los comandos legacy que lo soportan siguen disponibles; algunos comandos aceptan `--format json` local.

## Tests

```bash
python -m pytest src/tests/ -q
python -m pytest src/tests/test_v2_3_0_acceptance.py -q
```

## Documentación

| Documento | Contenido |
|---|---|
| `STATUS.md` | Matriz honesta de capacidades actuales, planned y future |
| `CHANGELOG.md` | Cambios por versión |
| `VIEW_SCHEMA.md` | Contrato VIEW |
| `EQUIVALENCE.md` | Niveles byte/AST/semantic/content |
| `BENCHMARK.md` | Evidencia y comandos reproducibles |
| `PACKAGING.md` | Reglas de paquete limpio |
| `ERRORS.md` | Taxonomía de errores v2 |
| `INFORME_DE_ENTREGA_v2.4.0.md` | Informe de entrega alineado |

## Licencia

MIT. Ver `LICENSE`.

## Autoría

Fidel Ernesto Lozada A. — `SKILL.md` v1.2.0-enterprise-candidate.
