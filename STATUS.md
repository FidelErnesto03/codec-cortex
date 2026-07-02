<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MPL-2.0 -->

# CODEC-CORTEX Status

This file is the maturity registry for public claims in the repository. README, Skill docs and specifications must not imply a stronger status than this file.

## Implemented Now

- Repository documentation structure.
- README public entry point.
- `skill/SKILL.md` and `skill/SKILL.en.md` Skill specification drafts.
- `skill/SKILL.cortex` dense Skill draft (19 canonical sigils — 25 total documented in SKILL.md).
- `skill/AGENT.cortex` example identity file.
- `skill/brain.cortex` local brain template.
- Spanish and English reference documents.
- Python package placeholder exposing `__version__`.
- **Survival Core:** `survive` attribute with 4 levels (min/recovery/work/full).
- **Survival Core:** 5 minimum field contracts (FCS, OBJ, CNST, STP, WRK).
- **Survival Core:** Priority pack P0-P5 with anti-positional truncation.
- **Survival Core:** 4 conceptual context profiles (MIN/RECOVERY/WORK/FULL).
- **Survival Core:** Degradation policy with direct selection by budget.
- **HCORTEX render protocol:** 5 rules, 8 steps (profile, source, instance, type, order).
- **Context Survival Rules** in `SKILL.md` and `SKILL.en.md`.
- Documentation: `docs/en/specs/context-survival.md` (EN) · `docs/es/specs/supervivencia-contexto.md` (ES) · `docs/en/specs/benchmark-methodology.md` (EN) · `docs/es/specs/metodologia-benchmark.md` (ES).
- Benchmarks registry: `benchmarks/README.md` (0.1, 0.1b, 0.2).
- **CLI v1.1.9 at `cli/`:** 17 commands (`new`, `render`, `compile`, `verify`, `get`, `list`, `add`, `update`, `delete`, `move`, `glossary`, `micro`, `doctor`, `diff`, `format`, `recover`, `diagram`), 222 tests passing.
- **Deterministic parser, verifier and HCORTEX renderer** integrated in CLI: `cortex verify --strict`, `cortex render`, `cortex doctor`.
- **CRUD operations:** `cortex add`, `cortex update`, `cortex delete`, `cortex list`, `cortex get`.
- **Structural diff:** `cortex diff` with governance-aware mode.
- **Recovery:** `cortex recover` repairs legacy/non-conforming `.cortex` files.
- **Diagram operations:** `cortex diagram extract` and `cortex diagram validate`.
- **All `.cortex` files validated:** `brain.cortex`, `SKILL.cortex`, `alfred-memory.cortex` pass `cortex verify --strict` (0 errors, 0 warnings).
- **SKILL.md v1.3.0:** HCORTEX canonical with 35 VIEW directives, 0 errors verify.

## Specification Exists

- `.cortex` sections and sigils (19 canonical + 6 new).
- HCORTEX concept: render target with minimum P0/P1 traceability.
- Direct Skill adoption model with progressive compatibility.
- Parser and verifier design.
- MCP handler map as future design.
- HCORTEX equivalence chart (P0/P1 minimum).

## Designed But Not Implemented

- Runtime lifecycle operations.
- MCP server.
- Automated survival benchmarks.

## Planned Next

- Automate survival benchmark methodology.
- Expand CLI command coverage.
- Stabilize AST representation for codec roundtrip.

## Future Phase

- Memory runtime for WRK, SES, LNG and KNW lifecycle.
- Automatic consolidation with explicit user-confirmed promotion policy.
- Enterprise MCP server.
- Governance, audit and deployment layer.

## Not Promised

- Literal reconstruction of every original message.
- Measured high token reduction without reproducible benchmarks.
- Guaranteed recall improvement.
- Production-ready enterprise MCP today.
- Universal performance improvement across all models.
