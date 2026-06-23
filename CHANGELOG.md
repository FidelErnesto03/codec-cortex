<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

# Changelog

All notable changes to CODEC-CORTEX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-06-23

### Added
- Initial public release of the CODEC-CORTEX protocol
- Universal skill specification (`skill/SKILL.md`) with 25 sigils, 17 principles, 14 pitfalls
- Skill in native `.cortex` format (`skill/SKILL.cortex`) — dogfooding with 80% compression
- Local brain with golden ratio distribution (`skill/brain.cortex`)
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
