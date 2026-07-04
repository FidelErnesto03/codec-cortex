<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MPL-2.0 -->

# Changelog

All notable changes to CODEC-CORTEX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] — 2026-07-04

### Fixed

- **Bug E003_UNKNOWN_SIGIL**: `cortex add` rechazaba sigilos declarados en $0 cuando el brain tenía header `<!-- CODEC-CORTEX -->`. Causa: el parser v2 no reconoce glosario en formato de comentarios (`# IDN | identity | ...`). Fix en `load_doc()`: inyección de comment-based glossary en conversión v2→v1.

## [0.3.2] — 2026-06-30

### Added

- **E1 Distribution & CI/CD**: GitHub Actions CI (ruff lint + test 3.9-3.12 + verify-view + roundtrip-bidir + build). `pip install codec-cortex` published to PyPI (v0.3.2).
- **Ruff lint**: 0 errors across all 59 Python files (231 legacy errors fixed).
- **Pre-commit hooks**: ruff, trailing-whitespace, end-of-file-fixer, cortex verify --strict.
- **Makefile targets**: `install`, `test`, `lint`, `build`, `publish`, `verify`, `roundtrip`, `release`.
- **Flag `--preserve`** en `canonicalize`: preserva estructura original incluso con VIEW directives.
- **Corpus benchmark migrado a VIEW**: 10 artefactos .cortex con 12+ VIEW directives c/u, coverage 100%, reversibility True.
- **Workflow del agente**: `docs/specs/agent-workflow.md` con 5 diagramas PUML, 4 reglas `!`, 5 perfiles CORTEX-OUT.
- **Reglas `!` en skill**: `!:canonical_names`, `!:startup_verify`, `!:precommit_verify`.

### Changed

- `cortex canonicalize` ahora es VIEW-aware: sin VIEW directives preserva estructura (fix B-01/B-05).
- Métodos de benchmark renombrados: `cortex_v2_priority_pack` → `cortex_priority_pack`, `cortex_v2_canonical` → `cortex_canonical`.
- Regex de parser extendido para aceptar formato `$N: DESCRIPTION` (compatibilidad v1).

### Fixed

- B-01: `cortex_v2_canonical` BCFNR=1.0 → corregido con VIEW-aware canonicalize.
- B-05: `v2-canonicalize` rompía compatibilidad con v1 render — ahora preserva estructura cuando no hay VIEW.
- Versión del proyecto actualizada a v0.3.2 en todas las superficies.

## [0.3.1] — 2026-06-29

### Changed

- **CLI actualizado** de v1.1.9 → v2.4.0 (núcleo bidireccional CORTEX ⇄ HCORTEX).
- 25 nuevos comandos v2: `v2-roundtrip`, `v2-convert`, `v2-roundtrip-bidir`, `v2-compare`, `v2-verify-view`, `v2-explain-loss`, `v2-canonicalize`, `v2-inspect`.
- Roundtrip bidireccional: CORTEX → HCORTEX → CORTEX AST-equivalent, 0 diffs sobre artefactos canónicos.
- HCORTEX → CORTEX → HCORTEX content-equivalent, 0 diffs.
- VIEW directives: 44/44 en skill/cortex/SKILL.md, coverage 100%.
- Gates de reversibilidad: `reversible:true` solo con coverage 100% y cero errores.
- Post-write validation: no escribe output si hay pérdida salvo --force.
- Test suite: 341 passed, 3 skipped (vs 222 tests anteriores).
- Versión del proyecto actualizada a v0.3.1.

### Fixed

- BENCHMARK.md, STATUS.md, README.md alineados al canon v2.4.0.
- `INFORME_DE_ENTREGA_v2.3.1.md` agregado para trazabilidad de versiones.

## [0.3.0] — 2026-06-27

### Added

- CLI v1.1.9 integrated at `cli/` — 17 commands (`new`, `render`, `compile`, `verify`, `get`, `list`, `add`, `update`, `delete`, `move`, `glossary`, `micro`, `doctor`, `diff`, `format`, `recover`, `diagram`), 222 tests passing in 4.92s.
- `cortex verify --strict` validates structure, glossary, contracts, governance and level policy on all `.cortex` files.
- `cortex render` produces HCORTEX markdown views (readable and audit modes).
- `cortex doctor` deep diagnostics with governance checks and secret scanning.
- `cortex recover` repairs legacy or non-conforming `.cortex` files.
- SKILL.md upgraded to v1.2.0-enterprise-candidate: `$0` self-containment emphasis, new risk row, reordered checklist.
- 5 new check items for `brain.cortex` conformance: `$0` first, no external glossary dependency, all sigils/micros registered, no positional contract without declaration.

### Changed

- `brain.cortex`, `SKILL.cortex`, `alfred-memory.cortex` migrated to canonical `.cortex` format with `$N:` section headers, 6-column glossary with Cognitive Layer, and proper field contracts.
- All three `.cortex` files pass `cortex verify --strict` with 0 errors, 0 warnings.
- `README.md`: version 0.2.3 → 0.3.0, stage alpha → beta, CLI and codec moved from planned to current.
- `STATUS.md`: CLI and deterministic codec moved from "Designed but Not Implemented" to "Implemented Now".
- `ROADMAP.md`: Phase 4 status updated to current/specification with CLI deliverables.
- `brain.md` and `alfred-memory.md` regenerated from canonical `.cortex` via `cortex render --mode audit`.

## [0.2.3] — 2026-06-24

### Added
- HCORTEX views: `brain.md`, `alfred-memory.md`, `summary.md` — human-readable `.md` equivalents for every operational `.cortex` file.
- Lesson learned `cortex_md_sync`: all `.cortex` files must have a corresponding `.md` HCORTEX view.

### Changed
- `README.md`: v0.2.2 header, Survival Core context, roadmap 2.1, new docs in documentation table.
- `STATUS.md`: sigil count clarified (19 dense + 25 documented), Survival Core entries added.
- `pyproject.toml` and `__init__.py`: version aligned to v0.2.2.
- `CHANGELOG.md`: [0.2.2] section for HCORTEX corrections.

### Fixed
- Version inconsistency: all surfaces now declare v0.2.2 (README, pyproject, __init__, summary).
- Sigil count: STATUS.md explains 19 active / 25 documented distinction.

## [0.2.2] — 2026-06-24

### Added
- HCORTEX render protocol: 5 rules (`!hcortex_profile_selection`, `!hcortex_source_traceability`, `!hcortex_multi_instance`, `!hcortex_expansion_render`, `!hcortex_render_order`) in `SKILL.cortex $4`.
- HCORTEX render procedure: 8 steps in `SKILL.cortex $10` (profile, source, instance, expansion type, P0-P5 order).
- Source traceability column (`<SIGIL>:<name>`) in HCORTEX tables for P0/P1 entries.
- Multi-instance sub-sections for sigils with multiple named instances (FCS:primary, FCS:secondary).
- 5 render strategies by expansion type (attrs, cuerpo, contenido, bloque, attrs-pos).
- P0-P5 priority ordering for HCORTEX sections.
- `!gov_isolation` rule: no DIALECT governance references in public project files.
- Audit segmentation support: explicit `CORTEX-FULL (segmentado)` for insufficient budget.
- `DIAG caption check` metric in `benchmark-methodology.md`.
- README and STATUS.md updated to reflect v0.2.1 Survival Core.

### Fixed
- D-01: HCORTEX render now selects profile by context budget before rendering (MIN/RECOVERY/WORK/FULL).
- D-02: Source column added to all P0/P1 tables. `WARNING: missing source` on missing traceability.
- D-03: Multi-instance entries render as distinct sub-sections or with instance column.
- D-04: Expansion type-specific render strategies (no more uniform K/V tables for all types).
- D-05: PUML diagrams include `' source: DIAG:<name>` caption.
- D-06: HCORTEX sections ordered by P-level priority (P0 first, P5 last).

## [0.2.1] — 2026-06-24

### Added
- Survival Core: `survive` attribute with 4 levels (min, recovery, work, full).
- Survival Core: priority pack P0-P5 for cognitive context reduction.
- Survival Core: conceptual context profiles (CORTEX-MIN, RECOVERY, WORK, FULL).
- Survival Core: HCORTEX as render target with minimum P0/P1 traceability.
- Survival Core: degradation policy with direct profile selection by budget.
- New sigils in `$0` glossary: STP, AUD, RSK, NXT, CLAIM, LIM (19 total).
- Minimum field contracts for FCS, OBJ, CNST, STP, WRK.
- Context Survival Rules section in SKILL.md and SKILL.en.md.
- Documentation: `docs/specs/context-survival.md`, `docs/specs/benchmark-methodology.md`.
- Benchmarks registry: `benchmarks/README.md`.

## [0.2.0] — 2026-06-24

### Changed
- Reoriented the public narrative from codec-first to universal memory Skill-first.
- Added explicit maturity separation for current Skill adoption, `.cortex`, HCORTEX, planned codec/CLI, future runtime, and future MCP.
- Rewrote Skill and dense `.cortex` guidance to distinguish direct adoption from planned automation.
- Softened unsupported benchmark and reversibility claims into targets or scoped structural/contextual language.

### Added
- Added `STATUS.md` as the repository maturity registry.
- Added `ROADMAP.md` with the six-phase CODEC-CORTEX plan.
- Added `docs/review/project-reorientation-report.md` with the reorientation diagnosis and risk register.

## [0.1.0] — 2026-06-23

### Added
- Initial public release of the CODEC-CORTEX protocol
- Universal skill specification (`skill/SKILL.md`) with 25 sigils, 17 principles, 14 pitfalls
- Skill in native `.cortex` format (`skill/SKILL.cortex`) — dogfooding with 80% compression
- Local brain with golden ratio distribution (`brain.cortex`)
- Agent entry point (`skill/AGENT.cortex`) + HCORTEX human-readable version (`skill/AGENT.md`)
- Technical documentation: fundamentos, algoritmo, adopción, MCP bridge
- HCORTEX output protocol for human-readable decompression
- Context management cycle (Operate → Consolidate → ... → GATE Exit)
- Maturation engine (detect → ask_user → promote → decay)
- PUML diagrams as native compression (62 diagrams, zero ASCII art)
- Collapse of redundant attributes (attrs-pos) — 15-20% token reduction
- Micro-glossary with semantic naming patterns — 30-40% additional reduction
- GATE exit for clean de-adoption
- Golden ratio (φ=1.618) memory distribution across cognitive layers
- Industry-standard publication patterns (AUTHORS, CITATION.cff, CODEOWNERS, CONTRIBUTING, GOVERNANCE)
