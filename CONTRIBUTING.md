<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MPL-2.0 -->

# Contributing to CODEC-CORTEX

Thanks for your interest in contributing to the CODEC-CORTEX protocol.

## How to Contribute

1. **Read the spec** — `skill/hcortex/SKILL_HCORTEX.md` is the canonical specification
2. **Fork & branch** — `git checkout -b feature/your-feature`
3. **Follow HCORTEX** — Write documentation in HCORTEX format: tables, lists, diagrams. No prose.
4. **Test your changes** — `cortex verify` on any .cortex files you modify
5. **Open a PR** — Describe what you changed and why

## What We Need

- **Implementations** — Parser/compiler in Python, Rust, Go, TypeScript
- **Integrations** — MCP server, LangChain, AutoGen, CrewAI adapters
- **Translations** — SKILL.md in other languages
- **Benchmarks** — Compression ratio tests on real agent workloads
- **Documentation** — Fixes, clarifications, examples

## Style Guide

- English for structural tags, Spanish for semantic content
- PUML diagrams over ASCII art (always)
- Tables over lists over prose
- Every flow of 3+ steps requires a diagram
- Follow HCORTEX formatting conventions (see skill/hcortex/SKILL_HCORTEX.md §9)

## License

By contributing to CODEC-CORTEX, you agree that your contributions are licensed under the Mozilla Public License 2.0 (MPL-2.0), unless explicitly stated otherwise in writing.

You represent that you have the right to submit the contribution and to license it under MPL-2.0.

Contributions that include third-party code, generated code, model outputs, datasets or external artifacts must clearly identify their origin and license.
