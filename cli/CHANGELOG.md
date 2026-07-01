# CHANGELOG — codec-cortex

## [0.3.6] — 2026-07-01

> Release v0.3.6 — SKILL v1.3.0 Documentation Alignment

### Added
- SKILL reescrito en HCORTEX con 35 VIEW directives (v1.2.0 → v1.3.0).
- CORTEX SKILL + AGENT generados desde HCORTEX, 0 errores verify.
- Nuevas specs: CORTEX-OUT protocol, microtokens reference, VIEW directives reference.
- HCORTEX expandido: tutorial, how-to, explanation, reference en EN y ES.
- Docs reorganizadas por idioma: 12 EN specs + 12 ES specs.
- CLI: `cortex verify` ahora soporta formato v2 nativamente (wrapper + header).
- Nuevo EN→ES: `docs/en/specs/learning.md`, `docs/es/specs/microtokens.md`, `docs/es/specs/directivas-view.md`, `docs/es/specs/salida-agente.md`.

### Changed
- `cli/src/cortex/cli/commands/verify.py`: detección v2 + `_run_verify_v2()`.
- `cli/src/cortex/cli/commands/__init__.py`: `load_doc()` v2-aware.
- Todas las versiones de proyecto: v0.3.5 → v0.3.6.
- Todas las STATUS NOTES: "As of v0.3.5" → "As of v0.3.6".
- Referencias cruzadas a `docs/specs/` → `docs/en/specs/` + `docs/es/specs/`.

### Fixed
- `skill/cortex/AGENT.md`: eliminadas referencias a HCORTEX.
- `skill/hcortex/AGENT.md`: eliminadas referencias a HCORTEX (no sobreviven en conversión).
- `skill/hcortex/SKILL.md`: eliminada referencia de HCORTEX a sí mismo.

## [0.3.5] — 2026-07-01

> Release E3 — Protocolo de Documentación

### Added
- `docs/README.md` central para navegación por audiencia y formato.
- Estructura `docs/hcortex/` con tutorial, how-to, explicación y referencia humana.
- Estructura `docs/cortex/api/*.cortex` con referencia API autocontenida por comando.
- `cortex docstring` para derivar docstrings desde `docs/cortex/api/`.
- `cortex benchmark` para inventario/validación local de suites bajo `benchmarks/`.
- Tests E3 para docstrings, wrapper CLI y benchmark inventory.
- `.coveragerc` y gate `pytest-cov` con umbral mínimo 85%.

### Changed
- Entry point del paquete apunta a `cortex.cli.main_e3:main`, preservando fallback al CLI histórico.
- CI valida fuentes de documentación API, docstring canónica y benchmark inventory.
- `python -m cortex` usa el wrapper E3.

## [0.3.4] — 2026-07-01

> Release E2 — Security & Governance

### Added
- Secret scanner (12 patrones): `cortex doctor --scan-secrets`
- Mutation gates: `--mode read-only|editor|admin`, env `CORTEX_MODE`
- Audit log bajo demanda: `cortex audit on/off/status/snapshot/prune`
- `cortex verify --signature` para verificación de integridad
- Dependabot para pip y GitHub Actions
- 68 nuevos tests (409 total)

### Changed
- `cortex doctor` ahora incluye scan de secretos (opt-in con `--scan-secrets`)
- Pre-commit hooks: detect-secrets + cortex-secret-scan

## [0.3.3] — 2026-07-01

> Release E1 — Distribution & CI/CD completado

### Added
- GitHub Actions CI (ruff lint + test 3.9-3.12 + verify + build + publish)
- Ruff 0 errores (231 legacy errors fixed)
- workflow_dispatch trigger
- Personal files (brain.cortex, alfred-memory.*) untracked de git

### Changed
- `pip install codec-cortex` ahora desde PyPI

## [0.3.2] — 2026-07-01

> Release canónica: nombres canónicos sin prefijo `v2-`, fix de
> `canonicalize` (issues B-01/B-05), migración del corpus a VIEW
> directives, integración del agente con workflows operativos.

### Added

- **Nombres canónicos CLI** (sin prefijo `v2-`):
  - `cortex roundtrip`, `cortex convert`, `cortex roundtrip-bidir`,
    `cortex compare`, `cortex verify-view`, `cortex explain-loss`,
    `cortex canonicalize`, `cortex inspect`.
  - Los nombres `v2-*` se mantienen como alias deprecados (still
    accepted, will be removed in v1.0.0). Al invocar un alias se emite
    un `WARNING` a stderr.
- **Flag `--preserve` en `cortex canonicalize`**:
  - Fuerza la canonicalización structure-preserving (sólo whitespace +
    orden de secciones) incluso cuando el artefacto tiene VIEW
    directives.
- **VIEW-aware behavior en `cortex canonicalize`** (B-01/B-05 fix):
  - Si el artefacto NO tiene VIEW directives, se aplica
    canonicalización structure-preserving con advertencia. Esto
    preserva compatibilidad con v1 render.
  - Si el artefacto SÍ tiene VIEW directives, se aplica
    canonicalización completa (comportamiento v2.3.x).
- **`write_cortex_v2_preserve()` en `cortex/v2/writer.py`**:
  - Serializador structure-preserving. Reproduce `entry.raw` cuando
    está disponible, ordena secciones numéricamente, normaliza
    whitespace.
- **`has_view_directives()` en `cortex/v2/writer.py`**:
  - Detecta VIEW directives operacionales (excluye sigil_decl en $0).
- **Parser v2 ahora acepta sección estilo v1** (`$0: DESCRIPTION`):
  - Regex `_SECTION_RE` extendido con `(?::\s*[^\n]*)?` para que el
    parser pueda procesar el corpus v1.0.0 sin migración forzada.
- **Migración del corpus a VIEW directives**:
  - Los 10 archivos `.cortex` en `benchmarks/v2.0.0/corpus/source/`
    ahora incluyen una sección `$N: VIEWS` con 10-13 VIEW directives
    cada uno, cubriendo IDN, DOM, CNST, FCS, OBJ, WRK, STP, NXT, RSK,
    AUD, CLAIM, LIM (según corresponda por artefacto).
  - `corpus/normalized/hashes.json` actualizado con los nuevos SHA256.
- **Renombramiento de métodos de benchmark**:
  - `cortex_v2_priority_pack` → `cortex_priority_pack`.
  - `cortex_v2_canonical` → `cortex_canonical`.
  - Manteniendo `deprecated_aliases` para trazabilidad.
  - `runs/method_results.json`, `scenario_results.json`,
    `derived_metrics.json`, `v1_vs_v2_comparison.json`,
    `provenance.csv`, `scored_tasks.csv`, `summary_tasks.csv`
    actualizados.
- **Workflow operativo del agente** (Sección 9 del plan v0.3.2):
  - 5 workflows PUML: startup, operación diaria, validación pre-commit,
    migración VIEW, selección de perfil CORTEX-OUT.
  - 4 reglas `!` nuevas en el skill: `!:startup_verify`,
    `!:precommit_verify`, `!:output_cortex_out` (refuerzo),
    `!:canonical_names`.
  - 5 perfiles CORTEX-OUT declarados: OUT-MIN, OUT-WORK, OUT-AUDIT,
    OUT-FULL, OUT-ERROR.

### Changed

- `cli/README.md`: comandos `v2-*` reemplazados por sus nombres
  canónicos en todos los ejemplos.
- `cli/STATUS.md`: tabla de capacidades con nombres canónicos.
- `benchmarks/README.md`: catálogo v2.0.0 actualizado; notas sobre
  migración VIEW.
- `skill/cortex/README.md`: procedimiento con comandos canónicos.
- `skill/cortex/AGENT.md`: referencias actualizadas.
- `skill/hcortex/AGENT.md`: referencias actualizadas.
- `docs/specs/skill-distribution.md`: comandos canónicos.
- `ROADMAP.md`: Phase 4 actualizada con entregables v0.3.2.
- Métricas post-fix para `cortex_canonical`: `BCFNR` 1.0 → 0.0,
  `WS` −2.73 → +7.03, `VIEW_coverage` 0 → 1.0, `reversibility` 0 → 1.0.

### Fixed

- **B-01**: `cortex_v2_canonical` BCFNR=1.0, WS=−2.73 →
  `cortex_canonical` BCFNR=0.0, WS=+7.03. La causa raíz era que
  `canonicalize` siempre reescribía el `.cortex` perdiendo
  compatibilidad con v1 render. Ahora detecta VIEW y preserva
  estructura cuando no hay.
- **B-02**: VIEW coverage = 0% en todo el corpus → 100% tras
  migración. Cada artefacto del corpus ahora declara sus VIEW
  directives.
- **B-03**: `v2-convert` producía HCORTEX vacío (251 bytes) sin VIEW →
  ahora produce HCORTEX sustancial porque el corpus tiene VIEW.
- **B-04**: Reversibility = False → True en skill canónico y corpus.
- **B-05**: `canonicalize` rompía compatibilidad con v1 render legacy →
  ahora preserva estructura cuando no hay VIEW.
- **B-06**: Las 4 métricas v2 (VIEW_coverage, reversibility,
  bidir_equivalence, loss_count) valen 0 → 1.0/1.0/1.0/0.0 tras
  migración.

### Acceptance criteria (Sección 8 del plan)

- [x] Ningún recurso público del proyecto usa "v2" en su nombre canónico.
- [x] `cortex canonicalize` no rompe compatibilidad con artefactos sin
      VIEW.
- [x] Corpus benchmark completo con VIEW directives (10 artefactos).
- [x] `cortex verify-view` reporta 100% coverage en skill canónico y
      corpus.
- [x] `cortex roundtrip-bidir` pasa en skill canónico.
- [x] Documentación actualizada sin referencias a "v2-" como nombre
      primario.
- [x] Tag v0.3.1 → v0.3.2.

### Evidence

```bash
cortex --version                                          # ≥ 0.3.2
cortex canonicalize benchmarks/v2.0.0/corpus/source/devops-k8s-rollout.cortex \
    --out /tmp/canonical.cortex                           # WARNING emitted, structure preserved
cortex verify-view benchmarks/v2.0.0/corpus/source/devops-k8s-rollout.cortex
                                                          # coverage 100%
cortex roundtrip-bidir skill/cortex/SKILL.md              # rc=0, 0 diffs
cortex inspect benchmarks/v2.0.0/corpus/source/devops-k8s-rollout.cortex
                                                          # 6 sections, ~14 entries, 12 VIEW
```

---

Todos los cambios notables de este proyecto se documentan en este archivo.
El formato se adhiere a [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
y el versionado a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.4.0] — 2026-06-30

### Added

- Núcleo bidireccional CORTEX ⇄ HCORTEX verificado sobre artefactos canónicos.
- Reconstrucción HCORTEX → CORTEX de 266/266 entries y 44/44 VIEW directives.
- Source markers para recuperar nombres originales desde tablas, listas y bloques PUML.
- Pipe escaping en tablas HCORTEX (`|` ⇄ `\|`).
- Nombres sintéticos snake_case estables y reparsables cuando no existe source explícito.
- Validación real de hash cuando un bloque declara hash; mismatch emite `E_VIEW_HASH_MISMATCH`.
- Post-write validation dura para evitar escritura de CORTEX degradado.
- Documentación alineada para CORTEX, HCORTEX, VIEW, equivalencia, packaging y errores.

### Changed

- `HCORTEX → CORTEX` pasa de experimental a `current` para los artefactos canónicos.
- `v2-roundtrip-bidir` pasa con `rc=0` en `skill/cortex/SKILL.md` y `skill/hcortex/SKILL.md`.
- `STATUS.md` deja de declarar parser inverso como futuro/no implementado.
- `README.md` aclara que `v2-doctor` y JSON uniforme para comandos v2 siguen planned.

### Fixed

- Inconsistencias documentales heredadas de v2.3.1.
- Bytes reales de `skill/cortex/SKILL.md`: 43,925.
- Paquete limpio sin `.pytest_cache`, `__pycache__` ni `.pyc`.

### Evidence

```bash
cortex --version                         # cortex 2.4.0
cortex v2-inspect skill/cortex/SKILL.md  # 14 sections, 266 entries, 44 VIEW, 100%
cortex v2-roundtrip-bidir skill/cortex/SKILL.md   # rc=0, 0 diffs
cortex v2-roundtrip-bidir skill/hcortex/SKILL.md  # rc=0, 0 diffs
```

Todos los cambios notables de este proyecto se documentan en este archivo.
El formato se adhiere a [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
y el versionado a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.1] — 2026-06-30

### Resumen

Corrective hard release post-auditoría v2.3.0. El auditor rechazó v2.3.0
como release bidireccional porque el roundtrip HCORTEX → CORTEX perdía
estructura, VIEW directives, y producía CORTEX inválido (sigilos con
backticks, cabeceras mal mapeadas, 0 entries reportado como 100%
coverage).

v2.3.1 corrige los 8 P0 del auditor y reclasifica el estado real:
- **CORTEX → HCORTEX:** `current` (sólido)
- **HCORTEX → CORTEX:** `experimental` (funciona para casos simples,
  pierde estructura en contracts/DIAG/profiles con nombres largos)
- **Roundtrip bidireccional perfecto:** `planned` (meta para v2.3.2)

### P0 — Cierre obligatorio

#### P0-1: Tests T-03/T-04/T-12 ahora fallan si la reversibilidad falla

- **Problema:** Los tests pasaban aunque `v2-roundtrip-bidir` fallara.
- **Fix:** T-03 exige AST-equivalent==True, T-04 exige content-equivalent==True,
  T-12 ejecuta `v2-roundtrip-bidir` CLI y exige rc=0.
- **Estado:** Los tests ahora **fallan honestamente** (4 tests en rojo),
  reflejando que el roundtrip bidireccional perfecto aún no se logra.

#### P0-2: Sanitizar tablas HCORTEX → CORTEX

- **Problema:** Sigilos con backticks (`` `IDN` ``), cabeceras en español
  no mapeadas (`tipo` en vez de `type`, `riesgo` en vez de `risk`).
- **Fix:** `HEADER_MAP` con 40+ mapeos español→inglés, `_strip_backticks()`,
  `_sanitize_value()`. Entradas reconstruidas ahora usan sigilos limpios.

#### P0-3: Reconstruir $13 con VIEW directives

- **Problema:** El encoder no reproducía la sección $13 con las 44 VIEW.
- **Fix:** `_block_to_view_entry()` reconstruye cada VIEW desde el bloque.
- **Estado:** $13 ahora se reconstruye con 44 VIEW directives.

#### P0-4: Fix v2-roundtrip-bidir Direction 2

- **Problema:** Direction 2 usaba CORTEX como si fuera HCORTEX.
- **Fix:** Lógica corregida — CORTEX input → Direction 1 (C→H→C) +
  Direction 2 (C→H→C→H); HCORTEX input → Direction 1 (H→C→H) +
  Direction 2 (H→C→H→C).

#### P0-5: Coverage 0 entries + 0 directives = 0% (no 100%)

- **Problema:** `calculate_view_coverage()` retornaba 1.0 para docs vacíos.
- **Fix:** Si `len(eligible) == 0`, retornar 0.0 (no 1.0).

#### P0-6: Post-write validation

- **Problema:** El encoder escribía CORTEX inválido sin detectarlo.
- **Fix:** `encode_cortex_from_ast()` re-serializa y reparsa; si
  `re_entries < declared_entries`, emite `E_AST_EQUIVALENCE_FAIL`.

#### P0-7: E_VIEW_HASH_MISMATCH real

- **Problema:** Hash era solo estructural (se parseaba, no se verificaba).
- **Fix:** `_compute_block_hash()` calcula SHA-256 del contenido del bloque;
  si no coincide con el declarado, emite `E_VIEW_HASH_MISMATCH`.

#### P0-8: Limpiar .pytest_cache del paquete

- **Fix:** Script de empaquetado elimina `__pycache__`, `.pytest_cache`,
  `*.egg-info` antes de crear el tarball.

### Limitaciones declaradas (honestas)

- **Roundtrip bidireccional perfecto NO logrado:** El encoder reconstruye
  182/266 entries (68%). Pierde entries cuando:
  - Tablas sin columna `name` usan contenido de `rule` como nombre
    (nombres largos no reparsables).
  - DIAG bloques con PUML multilínea no se reconstruyen en $6.
  - KNW profiles en $9 no se reconstruyen.
- **4 tests en rojo intencionalmente:** T-03, T-04, T-12, y
  `test_cli_v2_convert_hcortex_to_cortex` fallan para reflejar que el
  roundtrip bidireccional perfecto es `planned`, no `current`.
- **Meta para v2.3.2:** Roundtrip bidireccional perfecto (0 diffs).

## [2.3.0] — 2026-06-30

### Resumen

Salto fundacional: **CORTEX ⇄ HCORTEX verificable**, no solo renderizable.
Implementa parser inverso HCORTEX → AST, encoder HCORTEX → CORTEX, motor
de equivalencia (4 niveles: byte/AST/semantic/content), 11 errores
formales, 5 modos de operación, 7 comandos CLI nuevos, 12 tests de
aceptación T-01..T-12, y documentación obligatoria (VIEW_SCHEMA.md,
EQUIVALENCE.md, INFORME_DE_ENTREGA_v2.3.0.md).

### Funcionalidades

- **F-01..F-08:** Parser HCORTEX (`hcortex_parser.py`) — header, VIEW
  markers, tablas, listas, bloques verbatim, HUMAN_BLOCK, section resolver.
- **F-09..F-15:** Encoder HCORTEX → CORTEX (`encoder.py`) —
  `encode_cortex_from_ast()` con 8 estrategias reverse (rows_to_entries,
  row_to_attrs, items_to_entries, body_to_cuerpo, verbatim_to_bloque,
  callout_to_risk, etc.).
- **F-16..F-22:** Motor de equivalencia (`equivalence.py`) — 4 niveles
  (byte_identical, ast_equivalent, semantic_equivalent, content_equivalent)
  + diffs por sigilo/sección/VIEW.
- **F-29..F-34:** Hashes y trazabilidad estructural, preserve:verbatim
  estricto, declaración de pérdida.

### CLI

- `cortex v2-convert --from hcortex --to cortex` (conversión inversa)
- `cortex v2-roundtrip-bidir` (CORTEX ⇄ HCORTEX bidireccional)
- `cortex v2-compare` (comparar dos artefactos)
- `cortex v2-verify-view` (validar coverage y reversibilidad)
- `cortex v2-explain-loss` (explicar pérdida)
- `cortex v2-canonicalize` (normalizar)
- `cortex v2-inspect` (inspeccionar AST/sections/VIEW/errors)

### Errores formales (11)

`E_HCORTEX_HEADER_INVALID`, `E_HCORTEX_NOT_REVERSIBLE`, `E_VIEW_MISSING`,
`E_VIEW_TARGET_UNRESOLVED`, `E_VIEW_REVERSE_UNSUPPORTED`,
`E_VIEW_HASH_MISMATCH` (estructural), `E_HUMAN_BLOCK_UNDECLARED`,
`E_TABLE_SCHEMA_MISMATCH`, `E_BLOCK_NOT_PRESERVED`,
`E_AST_EQUIVALENCE_FAIL`, `W_HCORTEX_DISPLAY_ONLY`.

### Tests

- 12 tests de aceptación T-01..T-12 (todos pasan)
- 8 tests CLI para comandos nuevos
- Suite total: 345 tests pasando

### Documentación

- `VIEW_SCHEMA.md` (nuevo): contrato de VIEW con 13 kinds × 13 reverses
- `EQUIVALENCE.md` (nuevo): 4 niveles de equivalencia
- `INFORME_DE_ENTREGA_v2.3.0.md` (nuevo): evidencia real

## [2.2.3] — 2026-06-30

### Resumen

Cierre de los 8 prerrequisitos (PRE-01..PRE-08) exigidos antes de v2.3.0.
Establece el modelo conceptual canónico: CORTEX como fuente densa nativa,
HCORTEX como representación reversible por contrato, VIEW como contrato
de correspondencia. Implementa el gate `reversible: true`, diferencia
display vs canónico, publica artefactos canónicos, y normaliza docs.

### PRE — Cierre obligatorio

#### PRE-01: Informe de entrega con versión real

- Creado `INFORME_DE_ENTREGA_v2.2.3.md` con versión, comandos y evidencia real.

#### PRE-02/03: Artefactos canónicos publicados

- `skill/cortex/SKILL.md` (43925 bytes, 14 secciones, 266 entries, 44 VIEW directives)
- `skill/hcortex/SKILL.md` (40954 bytes, 723 líneas, view_coverage: 100, reversible: true)
- Ya no viven solo en `tests/fixtures/`.

#### PRE-04: Gate `reversible:true`

- **Problema:** v2.2.2 emitía `reversible: true` sin verificar cobertura ni errores.
- **Fix:** `render_hcortex()` ahora calcula `is_reversible = (coverage == 1.0) AND (not has_errors) AND (mode != "display")`. El header refleja el estado real.
- **Tests:** `test_reversible_true_only_when_coverage_full_and_no_errors`.

#### PRE-05: Diferenciar HCORTEX display vs canónico

- Nuevo flag `--mode` con 5 valores: `normal`, `strict`, `audit`, `recovery`, `display`.
- `display` produce `reversible: false` + `W_HCORTEX_DISPLAY_ONLY`.
- `strict` promueve `W_VIEW_*` a errors (rc=1).

#### PRE-06: README/STATUS/CHANGELOG alineados

- README declara CORTEX como denso nativo, HCORTEX como representación reversible por contrato.
- STATUS matriz v2.2.3 actualizada.
- CHANGELOG entrada [2.2.3] completa.

#### PRE-07/08: Paquete limpio + suite real

- Limpieza de `__pycache__`, `.pytest_cache`, `*.egg-info` en paquete.
- Suite real: **312 tests pasando** (no 290).

## [2.2.2] — 2026-06-30

### Resumen

Surgical hardening post-auditoría v2.2.1. La auditoría identificó que el
SKILL.md real seguía con coverage 0% (no había directivas VIEW operacionales),
que `E_VIEW_EMPTY_TARGET` reportaba como warning con rc=0 (inconsistencia
de prefijo), que el CLI escribía `--out` aún con rc=1 (artefactos inválidos
en disco), y que los targets heterogéneos podían inflar artificialmente
el coverage. v2.2.2 cierra estas 5 brechas + actualiza docs al modelo
conceptual CORTEX/HCORTEX/VIEW.

### P0 — Cierre obligatorio

#### P0-1: SKILL.md migrado con VIEW directives reales (100% coverage)

- **Problema:** El SKILL_v2.cortex.md canónico no tenía directivas VIEW
  operacionales. `cortex v2-convert` reportaba `view_coverage: 0.0%`,
  `Uncovered entries: 167`. El HCORTEX generado era sólo header.
- **Fix:** Se añadió una sección `$13` al SKILL.md con 44 directivas
  VIEW que cubren los 167 entries elegibles. Coverage ahora 100%.
  Roundtrip byte-identical preservado (43925 bytes).
- **Selectors utilizados:** `$0:canonical_sigils`, `$0:type_decls`,
  `$0:contracts`, `$0:microtokens`, `$0:enum_state`, `$0:delimiters`,
  `$N:SIGIL:*` (con fix del resolver para 3-part selectors),
  `$N:SIGIL:name` (con fix del resolver para 3-part name selectors).
- **Tests:** `test_skill_v2_2_2_view_coverage_100_percent`,
  `test_skill_v2_2_2_view_directives_count_44`.

#### P0-2: Renombrado E_VIEW_EMPTY_TARGET → W_VIEW_EMPTY_TARGET

- **Problema:** `E_VIEW_EMPTY_TARGET` se reportaba con `severity=warning`
  y rc=0. La inconsistencia (prefijo `E_` para warning) violaba la
  convención de códigos.
- **Fix:** Renombrado a `W_VIEW_EMPTY_TARGET` para reflejar que un
  target vacío es recuperable (e.g., sección opcional faltante).
- **Tests:** `test_view_empty_target_uses_W_prefix`.

#### P0-3: --out no se escribe si hay E_VIEW_* (salvo --force-write-on-error)

- **Problema:** Con `kind:bogus`, el comando retornaba rc=1 pero
  escribía un archivo `--out` con `reversible: true` y
  `view_schema: 1`. Eso dejaba artefactos inválidos en disco.
- **Fix:** Por defecto, si hay E_VIEW_* errors, `--out` NO se escribe.
  Nuevo flag `--force-write-on-error` para override explícito (forense).
- **Tests:** `test_out_not_written_on_view_errors`,
  `test_out_written_with_force_write_on_error`.

#### P0-4: --strict promueve W_VIEW_* a errors

- **Problema:** No había forma de tratar warnings como errores en CI.
- **Fix:** Nuevo flag `--strict` en `v2-convert`. W_VIEW_EMPTY_TARGET,
  W_VIEW_HETEROGENEOUS_TARGET, etc. se cuentan como errors y producen rc=1.
- **Tests:** `test_strict_promotes_w_view_to_errors`.

#### P0-5: Detección de targets heterogéneos (W_VIEW_HETEROGENEOUS_TARGET)

- **Problema:** Un target como `IDN:*` podía cubrir tanto declaraciones
  `$0` (sigil_decl) como entradas operativas (attrs). El renderer
  derivaba columnas de la primera entrada y dejaba otras filas vacías,
  pero igual reportaba `view_coverage: 100`.
- **Fix:** Nuevo diagnóstico `W_VIEW_HETEROGENEOUS_TARGET` cuando un
  target resuelve a entries con múltiples `entry_type`s o múltiples
  attr key sets y no tiene `fields` explícito. Se silencia agregando
  `fields:"..."` a la directiva.
- **Tests:** `test_heterogeneous_target_warns_without_fields`,
  `test_heterogeneous_target_silent_with_fields`.

#### P0-6: Documentación alineada al modelo CORTEX/HCORTEX/VIEW

- **Problema:** README y STATUS aún trataban HCORTEX como "vista humana"
  no como memoria canónica reversible.
- **Fix:** README ahora declara el modelo conceptual:
  - CORTEX = denso nativo
  - HCORTEX / HUMAN-CORTEX = humano denso reversible
  - VIEW = contrato de correspondencia
  STATUS añade matriz de capacidades v2.2.2 con conceptos base.

### Mantenimiento

- `resolve_target()` fix: `$N:SIGIL:name` (3-part) y `$N:NAME` (single
  colon) ahora resuelven correctamente. Antes caían al branch equivocado.
- Testsuite: 290 → 290+ tests pasando (sin regresiones).

## [2.2.1] — 2026-06-29

### Resumen

Ampliación del modelo HCORTEX-READ para entrada de datos arbitraria,
clasificación de kind y metadatos. 294 tests, 46 archivos validados.
Refuerzo de las bases operacionales del codec.

### Added

- **HCORTEX-R deprecado.** Se unifica el modelo en HCORTEX-READ con perfiles
  MIN/RECOVERY/WORK/FULL. La flag `--cortex-out` se elimina; ahora se usa
  `--profile min` para obtener la vista mínima.
- **Metadata completa en entries.** Cada entrada de HCORTEX-READ ahora
  incluye metadata serializada (sigilo, tipo, source, contrato).
- **DIAG verbatim.** Los bloques PUML se preservan textualmente en
  HCORTEX-READ con pipes escapados.
- **Iteración por sigilo.** HCORTEX-READ puede renderizar un sigilo
  específico sin parsear todo el archivo.
- **Clasificación de kind.** Todo archivo `.cortex` ahora se clasifica
  como `skill`, `brain`, `package` o `generic` según su IDN.
- **Iteración por entry kind.** Filtrado opcional de entries por tipo
  (attrs, cuerpo, contenido, bloque, relación).
- **Seed multiglosario.** Si falla el glosario primario ($0), se prueba
  con secondary/tertiary antes de rendirse.
- **294 tests.** 44 nuevos tests de cobertura.

### Fixed

- **Parser no perdía líneas.** `_parse_cortex_sections()` corregido para
  no eliminar líneas al final de cada bloque de contenido.
- **$13 con VIEW directives.** El parser ahora reconoce VIEW como sigilo
  válido.
- **$10 con procedimientos.** El parser ahora reconoce `T:` como prefijo
  de tareas.
- **$14 riesgos.** El parser ahora reconoce `R:` como prefijo de riesgos.
- **$8 warnings.** El parser ahora reconoce `W:` como prefijo de warnings.

## [2.2.0] — 2026-06-29

### Resumen

Fundación del CLI `cortex` con parser determinista, verificación, operaciones
CRUD y render HCORTEX-READ. 250 tests, 46 archivos de prueba, cobertura >90%
de la especificación fundamental.

### Added

- Arquitectura modular: `core/`, `glossary/`, `hcortex/`, `crud/`,
  `templates/`, `cli/`.
- Parser `.cortex → AST` (lexer + parser determinista, sin LLM).
- Writer canónico `AST → .cortex` determinista.
- Validador sintáctico (sigilos desconocidos, tipos, duplicados).
- HCORTEX-READ (vista humana) con 4 perfiles de supervivencia.
- CRUD completo (add/update/delete/move + glossary + micro).
- 17 comandos CLI: new, render, compile, verify, get, list, add, update,
  delete, move, glossary, micro, doctor, diff, format, recover, diagram.
- 250+ tests (15 criterios de aceptación + CRUD + errores + fixtures).
- Templates brain/skill/package/generic.
- Escritura atómica con backup `.bak`.
