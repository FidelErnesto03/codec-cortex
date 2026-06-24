<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

# Changelog

All notable changes to CODEC-CORTEX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
