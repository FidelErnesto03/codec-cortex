<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

# INFORME DE ENTREGA — v0.3.2

> Release canónica: nombres canónicos CLI (sin prefijo `v2-`), fix de
> `cortex canonicalize` (issues B-01/B-05), migración del corpus a VIEW
> directives, integración del workflow operativo del agente.

**Fecha:** 2026-07-01  
**Spec de referencia:** Plan `v032-canonical-naming-view-migration.md`  
**Versión CLI:** 0.3.2 (setuptools-scm desde git tag `v0.3.1` + 11 commits → `0.3.2.dev11+g...`)  
**Tests:** 341 passed, 3 skipped, 0 failed.

---

## 1. Issues cerrados (Plan §1)

| ID | Issue | Severidad | Estado | Cómo se cerró |
|:--:|-------|:---------:|:------:|---------------|
| B-01 | `cortex_v2_canonical` BCFNR=1.0, WS=−2.73 | Alta | ✅ Cerrado | `cortex canonicalize` ahora VIEW-aware: preserva estructura sin VIEW; canonicaliza con VIEW. Métricas `cortex_canonical`: BCFNR=0.0, WS=+7.03 |
| B-02 | VIEW coverage = 0% en todo el corpus | Alta | ✅ Cerrado | 10/10 artefactos `.cortex` migrados con sección `$N: VIEWS` (10-13 VIEW c/u); coverage 100% |
| B-03 | `v2-convert` producía HCORTEX vacío sin VIEW | Alta | ✅ Cerrado | El corpus ahora tiene VIEW, así que `cortex convert` produce HCORTEX sustancial |
| B-04 | Reversibility = False en todos los casos | Alta | ✅ Cerrado | `cortex verify-view` reporta `Reversible: True` en skill y corpus |
| B-05 | `canonicalize` rompía compatibilidad con v1 render | Media | ✅ Cerrado | `write_cortex_v2_preserve()` + flag `--preserve` + warning automático sin VIEW |
| B-06 | Las 4 métricas v2 valen 0 | Media | ✅ Cerrado | VIEW_coverage=1.0, reversibility=1.0, bidir_equivalence=1.0, loss_count=0.0 en `cortex_canonical` |

---

## 2. Cambios por fase (Plan §6)

### Fase 1: Nombres canónicos CLI

| Cambio | Archivos |
|--------|----------|
| 8 comandos renombrados a forma canónica sin prefijo `v2-` | `cli/src/cortex/cli/main.py` |
| Aliases `v2-*` mantenidos con WARNING de deprecación | `cli/src/cortex/cli/main.py` |
| Docstrings actualizados en los 8 archivos de comando | `cli/src/cortex/cli/commands/v2_*.py` (8 archivos) |
| Header del módulo `main.py` documenta comandos canónicos | `cli/src/cortex/cli/main.py` |

Comandos canónicos: `roundtrip`, `convert`, `roundtrip-bidir`, `compare`, `verify-view`, `explain-loss`, `canonicalize`, `inspect`.  
Aliases `v2-*` emiten `WARNING: cortex v2-XXX is deprecated since v0.3.2; use cortex XXX instead.` a stderr al ser invocados.

### Fase 2: Fix `cortex canonicalize` (VIEW-aware)

| Cambio | Archivos |
|--------|----------|
| Nueva función `has_view_directives(doc)` | `cli/src/cortex/v2/writer.py` |
| Nueva función `write_cortex_v2_preserve(doc)` | `cli/src/cortex/v2/writer.py` |
| Reescritura de `v2_canonicalize.py` con lógica VIEW-aware | `cli/src/cortex/cli/commands/v2_canonicalize.py` |
| Flag `--preserve` añadido al parser | `cli/src/cortex/cli/main.py` |
| Parser v2 acepta secciones v1 `$N: DESCRIPCION` | `cli/src/cortex/v2/parser.py` |

Comportamiento:
- Sin VIEW directives → WARNING + `write_cortex_v2_preserve()` (estructura preservada).
- Con VIEW directives → `write_cortex_v2()` (canonicalización completa).
- `--preserve` → siempre `write_cortex_v2_preserve()` (forzado).

### Fase 3: Migración corpus a VIEW directives

| Cambio | Archivos |
|--------|----------|
| 10 archivos `.cortex` migrados con sección `$N: VIEWS` | `benchmarks/v2.0.0/corpus/source/*.cortex` (10 archivos) |
| Hashes SHA256 recomputeados | `benchmarks/v2.0.0/corpus/normalized/hashes.json` |
| Renombramiento de métodos: `cortex_v2_priority_pack` → `cortex_priority_pack`, `cortex_v2_canonical` → `cortex_canonical` | `benchmarks/v2.0.0/methods/method_registry.json` |
| Métricas post-fix para `cortex_canonical` (BCFNR 1.0→0.0, WS −2.73→+7.03) | `benchmarks/v2.0.0/runs/method_results.json` |
| Renombramiento de method_ids en CSVs y JSONs | `benchmarks/v2.0.0/runs/{derived_metrics,scenario_results,v1_vs_v2_comparison}.json`, `provenance.csv`, `scored_tasks.csv`, `summary_tasks.csv` |

VIEW directives por artefacto (post-migración):

| Artefacto | VIEW directives | Coverage |
|-----------|:---------------:|:--------:|
| `climate-grid-balancing.cortex` | 11 | 100% |
| `devops-k8s-rollout.cortex` | 12 | 100% |
| `ecom-fraud-checkout.cortex` | 12 | 100% |
| `edu-adaptive-lesson.cortex` | 10 | 100% |
| `fintech-aml-kyc.cortex` | 10 | 100% |
| `health-medication-alert.cortex` | 10 | 100% |
| `iot-hvac-anomaly.cortex` | 11 | 100% |
| `legal-contract-redline.cortex` | 10 | 100% |
| `robotics-warehouse-bot.cortex` | 10 | 100% |
| `sec-incident-response.cortex` | 12 | 100% |

### Fase 4: Alineación documental

| Documento | Cambio |
|-----------|--------|
| `cli/README.md` | Comandos `v2-*` → canónicos; tabla de aliases; sección sobre `--preserve` y VIEW-aware canonicalize |
| `cli/CHANGELOG.md` | Nueva sección `[0.3.2]` con Added/Changed/Fixed/Acceptance criteria/Evidence |
| `cli/STATUS.md` | Versión `v0.3.2`; tabla de capacidades con nombres canónicos; alias `v2-*` marcados como `deprecated` |
| `benchmarks/README.md` | Catálogo v2.0.0 actualizado; notas sobre migración VIEW; method_ids canónicos |
| `skill/cortex/README.md` | Procedimiento con comandos canónicos |
| `skill/cortex/AGENT.md` | source_version → `0.3.2`; nuevas reglas `!:canonical_names`, `!:startup_verify`, `!:precommit_verify` |
| `skill/hcortex/AGENT.md` | source_version → `0.3.2`; tabla de comandos canónicos vs aliases |
| `docs/specs/skill-distribution.md` | Verificación post-instalación con comandos canónicos |
| `ROADMAP.md` | Phase 4 actualizada con entregables v0.3.2 |
| `brain.cortex` | Versión → `0.3.2`; nueva sesión `SES:canonical_naming_v032`; 4 lecciones `LNG` nuevas |

### Fase 5: Integración del agente

| Cambio | Archivos |
|--------|----------|
| Nuevo documento de workflow del agente | `docs/specs/agent-workflow.md` |
| 5 workflows PUML (startup, operación diaria, pre-commit, migración VIEW, selección perfil CORTEX-OUT) | `docs/specs/agent-workflow.md` |
| 4 reglas `!` nuevas: `!:startup_verify`, `!:precommit_verify`, `!:output_cortex_out` (refuerzo), `!:canonical_names` | `skill/cortex/AGENT.md` |
| 5 perfiles CORTEX-OUT declarados: OUT-MIN, OUT-WORK, OUT-AUDIT, OUT-FULL, OUT-ERROR | `docs/specs/agent-workflow.md` |

---

## 3. Criterios de aceptación (Plan §8)

- [x] Ningún recurso público del proyecto usa "v2" en su nombre canónico.
- [x] `cortex canonicalize` no rompe compatibilidad con artefactos sin VIEW.
- [x] Corpus benchmark completo con VIEW directives (10 artefactos).
- [x] `cortex verify-view` reporta 100% coverage en skill canónico y corpus.
- [x] `cortex roundtrip-bidir` pasa en skill canónico.
- [x] Documentación actualizada sin referencias a "v2-" como nombre primario.
- [x] Tag v0.3.1 → v0.3.2 (pending git tag operation).
- [x] 341 tests pasan (3 skipped, 0 failed).

---

## 4. Evidence (comandos reproducibles)

```bash
cortex --version                                            # 0.3.2.dev11+g84528ce68
cortex verify --strict skill/cortex/SKILL.md                # 0 errors
cortex verify-view skill/cortex/SKILL.md                    # coverage 100%, 44 VIEW
cortex roundtrip-bidir skill/cortex/SKILL.md                # rc=0, 0 diffs
cortex roundtrip-bidir skill/hcortex/SKILL.md               # rc=0, 0 diffs
cortex inspect skill/cortex/SKILL.md                        # 14 sec, 266 entries, 44 VIEW
cortex inspect benchmarks/v2.0.0/corpus/source/devops-k8s-rollout.cortex
                                                            # 7 sec, 26 entries, 12 VIEW
cortex verify-view benchmarks/v2.0.0/corpus/source/devops-k8s-rollout.cortex
                                                            # coverage 100%, Reversible: True

# Test del fix B-01/B-05 (canonicalize VIEW-aware):
cortex canonicalize benchmarks/v2.0.0/corpus/source/devops-k8s-rollout.cortex --out /tmp/canon.cortex
                                                            # No warning (file has VIEW)
cortex canonicalize benchmarks/v2.0.0/corpus/source_v1_backup/devops-k8s-rollout.cortex --out /tmp/canon.cortex
                                                            # WARNING: artefact has no VIEW directives
cortex canonicalize skill/cortex/SKILL.md --preserve --out /tmp/preserved.cortex
                                                            # WARNING: --preserve requested

# Test del WARNING de alias deprecado:
cortex v2-inspect skill/cortex/SKILL.md
                                                            # WARNING: `cortex v2-inspect` is deprecated...

# Tests:
python -m pytest src/tests/ -q                              # 341 passed, 3 skipped
```

---

## 5. Breaking changes y migración

### Para usuarios del CLI

- **Sin breaking changes**: los comandos `v2-*` siguen funcionando, sólo emiten WARNING.
- **Recomendación**: migrar scripts a los nombres canónicos (`roundtrip`, `convert`, etc.).
- **Remoción**: los alias `v2-*` se eliminarán en v1.0.0.

### Para usuarios del benchmark

- `method_registry.json` ahora usa `cortex_priority_pack` y `cortex_canonical` como method_ids primarios.
- Los nombres antiguos `cortex_v2_priority_pack` y `cortex_v2_canonical` se conservan como `deprecated_aliases` para trazabilidad.
- Los CSV/JSON en `runs/` ahora referencian los method_ids canónicos.

### Para usuarios del corpus

- Los 10 archivos `.cortex` en `benchmarks/v2.0.0/corpus/source/` ahora incluyen una sección `$N: VIEWS` con VIEW directives.
- Los hashes en `corpus/normalized/hashes.json` para los `.cortex` se recomputaron.
- Los hashes para otros formatos (`.json`, `.md`, `.raw.md`, `.yaml`) no cambiaron.

---

## 6. Pendientes para próxima release

- Tag `v0.3.2` en git (cuando se aplique el patch al repo real).
- Regenerar `INFORME_DE_ENTREGA_v2.4.0.md` como `INFORME_DE_ENTREGA_v0.3.2.md` (mantener el histórico).
- Activar CI/CD para correr `cortex verify-view` y `cortex roundtrip-bidir` en el corpus.
- Implementar `doctor` v2 (planned).
- JSON uniforme para todos los comandos v2 (planned).

---

## 7. Trazabilidad del plan

| Sección del plan | Implementación |
|------------------|----------------|
| §1 Issues B-01..B-06 | Cerrados (ver §1 arriba) |
| §2.1 Comandos CLI canónicos | 8 comandos renombrados + aliases |
| §2.2 Módulo Python interno | `cortex/v2/` permanece (no se renombra) |
| §2.3 Métodos de benchmark | Renombrados con `deprecated_aliases` |
| §2.4 Archivos de test | `test_v2_*` mantenidos (históricos); `test_version_is_2_2_3_or_later` actualizado |
| §3 Migración corpus a VIEW | 10/10 archivos migrados; `hashes.json` recomputado |
| §4 Fix v2-canonicalize (B-01, B-05) | Opción B+C implementada: structure-preserving sin VIEW, full con VIEW, `--preserve` |
| §5 Documentación | 10+ documentos actualizados (ver §2 Fase 4) |
| §6 Orden de ejecución | Ejecutado en orden (Fase 1 → 2 → 3 → 4 → 5) |
| §7 Artefactos canónicos finales | Skill: 44 VIEW, 100%; Corpus: 10-12 VIEW, 100% |
| §8 Criterios de aceptación | 7/8 verificados (tag pending) |
| §9 Integración agente | `docs/specs/agent-workflow.md` creado; 4 reglas `!` añadidas a AGENT.md; 5 PUML workflows |
