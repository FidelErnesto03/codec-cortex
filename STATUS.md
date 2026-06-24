<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

# CODEC-CORTEX Status

This file is the maturity registry for public claims in the repository. README, Skill docs and specifications must not imply a stronger status than this file.

## Implemented Now

- Repository documentation structure.
- README public entry point.
- `skill/SKILL.md` and `skill/SKILL.en.md` Skill specification drafts.
- `skill/SKILL.cortex` dense Skill draft (26 sigils, 13 rules).
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
- Documentation: `docs/specs/context-survival.md`, `docs/specs/benchmark-methodology.md`.
- Benchmarks registry: `benchmarks/README.md` (0.1, 0.1b, 0.2).

## Specification Exists

- `.cortex` sections and sigils (19 canonical + 6 new).
- HCORTEX concept: render target with minimum P0/P1 traceability.
- Direct Skill adoption model with progressive compatibility.
- Parser and verifier design.
- MCP handler map as future design.
- HCORTEX equivalence chart (P0/P1 minimum).

## Designed But Not Implemented

- Deterministic parser.
- AST representation.
- Encoder and decoder.
- Structural verifier.
- HCORTEX renderer (manual/procedural exists, automated planned).
- Minimal CLI.
- Runtime lifecycle operations.
- MCP server.
- Automated survival benchmarks.

## Planned Next

- Implement a deterministic parser.
- Define a stable AST representation.
- Add encode/decode and structural verify tests.
- Add a basic HCORTEX renderer.
- Add minimal CLI commands only after the codec exists.
- Automate survival benchmark methodology.

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
