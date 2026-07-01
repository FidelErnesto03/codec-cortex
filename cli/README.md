# codec-cortex

> Implementación determinista del codec CODEC-CORTEX v0.3.6. Procesador modular de artefactos `.cortex` y `.hcortex.md` sin dependencia de LLM: parsea a AST, serializa CORTEX, renderiza HCORTEX, ejecuta validaciones VIEW, compara equivalencia, valida roundtrip bidireccional, deriva documentación e inventaria benchmarks.

`codec-cortex` es un procesador determinista de memoria cognitiva para agentes LLM/SLM. Opera sobre archivos `.cortex` (formato denso nativo) y `.hcortex.md` (representación humana reversible), sin depender de modelos de lenguaje.

## Gate de reversibilidad

`reversible:true` solo es válido cuando:

1. `view_coverage == 100%`;
2. no existen errores `E_VIEW_*` ni `E_HCORTEX_*`;
3. el modo no es `display`;
4. el roundtrip canónico aplicable pasa sin pérdida no declarada.

## Modelo conceptual

| Concepto | Rol | Estado |
|---|---|---|
| **CORTEX** | Representación densa nativa. Fuente canónica operacional y base de verificación, reversible por contrato VIEW. | `current` |
| **HCORTEX / HUMAN-CORTEX** | Representación humana densa y reversible cuando conserva VIEW/trazabilidad equivalente con cobertura válida. | `current` |
| **VIEW** | Contrato declarativo de correspondencia CORTEX ⇄ HCORTEX. Define render, reversión, campos, preservación y fallback. | `current` |
| **CORTEX-OUT** | Respuesta conversacional eficiente. No participa en decode/encode/verify/roundtrip. | `specification` |

## Instalación

```bash
pip install codec-cortex
# o para desarrollo
pip install -e ".[dev]"
```

## Comandos principales

```bash
# Identidad
cortex --version

# Documentación y benchmark (E3)
cortex docstring canonicalize
cortex docstring --all
cortex benchmark --list

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

# Canonicalización
cortex canonicalize skill/cortex/SKILL.md --out /tmp/canonical.cortex.md

# Seguridad y auditoría (E2)
cortex doctor --scan-secrets
cortex audit status
cortex verify --signature skill/cortex/SKILL.md
```

## Estado de madurez

| Capacidad | Estado | Evidencia |
|---|---|---|
| CORTEX v2 parser/writer | `current` | `cortex roundtrip` byte-identical |
| CORTEX → HCORTEX | `current` | genera `skill/hcortex/SKILL.md` byte-identical |
| HCORTEX → CORTEX | `current` | reconstruye 266/266 entries |
| Roundtrip bidireccional | `current` | `cortex roundtrip-bidir` rc=0, 0 diffs |
| VIEW coverage | `current` | 44/44 VIEW en skill; 10/10 artefactos del corpus |
| Docstring derivada | `current` | `cortex docstring` (E3) |
| Benchmark inventory | `current` | `cortex benchmark --list` (E3) |
| Coverage gate | `current` | `pytest-cov` ≥85% (E3) |
| Secret scanner | `current` | `cortex doctor --scan-secrets` (E2) |
| Mutation gates | `current` | `--mode read-only\|editor\|admin` (E2) |
| Audit log | `current` | `cortex audit on/off/snapshot` (E2) |
| MCP server | `future` | no implementado |

## Versiones

- **v0.3.6** (actual) — SKILL v1.3.0 Documentation Alignment. CLI soporta formato v2, docs reorganizadas por idioma, HCORTEX expandido.
- **v0.3.4** — E2: Security & Governance. Secret scanner, mutation gates, audit log, verify --signature.
- **v0.3.3** — E1: CI/CD + PyPI. GitHub Actions, ruff 0 errores, publish automático.
- **v0.3.2** — Nombres canónicos CLI. VIEW-aware canonicalize, corpus VIEW migration.
- **v2.4.0** — Núcleo bidireccional CORTEX ⇄ HCORTEX verificado.

## Licencia

MIT — Fidel Ernesto Lozada A.
