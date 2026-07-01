<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

<p align="center">
  <strong>CODEC-CORTEX</strong> — Universal Memory Skill for LLM/SLM Agents
  <br>
  <sub>v0.3.6 · MIT · <a href="AUTHORS.md">Fidel Ernesto Lozada A.</a> · <a href="skill/hcortex/SKILL_HCORTEX.md">Specification</a></sub>
</p>

---

CODEC-CORTEX is a universal memory Skill and contextual memory protocol for LLM/SLM agents. It helps agents organize persistent memory as structured operational context: identity, focus, objective, working state, rules, sessions, lessons, knowledge and references.

Its native `.cortex` format is designed for dense model consumption. HCORTEX provides a human-readable view for inspection, audit, correction and continuity. A CLI with 17 commands (verify, render, CRUD, doctor, diff, format, diagram) is now available at `cli/`. Memory runtime and enterprise MCP bridge remain planned phases.

| | |
|---|---|
| **Author** | Fidel Ernesto Lozada A. — Systems Engineer / MSc. Management Sciences |
| **Repository** | [github.com/FidelErnesto03/codec-cortex](https://github.com/FidelErnesto03/codec-cortex) |
| **License** | [MIT](LICENSE) |
| **Version** | 0.3.6 |
| **Stage** | Specification / beta |

---

## Problem

Agent memory usually grows as linear text. As conversations, files and decisions accumulate, important intent gets diluted, working state is mixed with history, and the next agent or session must recover context from noisy prose.

CODEC-CORTEX separates operational memory into explicit structures so an agent can recover what matters now without rereading the entire history.

## Current Stage

This repository is in specification/beta stage.

Current:

- Universal Skill documents and `.cortex` examples.
- `.cortex` contextual memory format specification.
- HCORTEX human-readable context view specification.
- Spanish and English reference documents.
- **CLI v1.1.9** at `cli/` — 17 commands, 222 tests, `cortex verify --strict` passes on all `.cortex` files.
- **Deterministic Python codec** — parser, encoder, decoder, verifier and HCORTEX renderer integrated in CLI.

Planned or future:

- Memory runtime for WRK, SES, LNG and KNW lifecycle management.
- Enterprise MCP bridge with governance and auditability.

See [STATUS.md](STATUS.md) for the maturity registry.

## Canonical Stack

```puml
@startuml
title CODEC-CORTEX Canonical Stack

rectangle "Universal Skill
current adoption layer" as skill
rectangle ".cortex
structured contextual memory" as cortex
rectangle "HCORTEX
human-readable context view" as hcortex
rectangle "Deterministic Codec
parse encode decode verify" as codec
rectangle "Memory Runtime
WRK SES LNG lifecycle" as runtime
rectangle "Enterprise MCP
agent tools governance audit" as mcp

skill --> cortex : defines memory discipline
cortex --> hcortex : renders for humans
cortex --> codec : automated maintenance
codec --> runtime : managed lifecycle
runtime --> mcp : enterprise exposure

note right of skill
  Current center of gravity.
  No server or Python package is required
  for initial adoption.
end note

note right of codec
  CLI v1.1.9 implements this.
  See cli/ for details.
end note

note right of mcp
  Future enterprise phase.
  Not a current feature.
end note
@enduml
```

## Installation

### From source (current)

```bash
git clone https://github.com/FidelErnesto03/codec-cortex.git
cd codec-cortex/cli
pip install -e .          # minimal install
pip install -e ".[dev]"   # with test dependencies
cortex --version
```

### From PyPI

```bash
pip install codec-cortex
cortex --version
```

Requires Python ≥ 3.9. The package installs the `cortex` CLI with all v2 commands (`convert`, `inspect`, `roundtrip-bidir`, `canonicalize`, etc.).

See `cli/README.md` for full CLI documentation and `skill/cortex/README.md` for installation as a universal agent skill.

## Quick Start

1. Read `skill/hcortex/SKILL_HCORTEX.md` for the HCORTEX Skill specification.
2. Load `skill/cortex/SKILL.md` as the dense CORTEX native Skill expression.
3. Use `skill/cortex/AGENT.md` as the identity entry point.
4. Copy or adapt `skill/cortex/brain.cortex` as a local memory template.
5. Render or summarize active context as HCORTEX for human review.
6. Try `cortex` commands from `cli/`: `cortex --help`, `cortex verify brain.cortex`.

A `cortex` CLI binary is available at `cli/`. Initial adoption does not require a server, MCP bridge or Python package. An agent can use CODEC-CORTEX by reading the Skill and following the `.cortex` memory discipline.

### Personal files

`brain.cortex`, `brain.md`, `alfred-memory.cortex` and `alfred-memory.md` are **per-agent** and excluded from version control via `.gitignore`. A template is available at `skill/cortex/brain.cortex`. Copy it to initialize your agent memory:

```bash
cp skill/cortex/brain.cortex brain.cortex
```

## Current Context

Agents and reviewers that need the project state behind this release can read `brain.cortex` at the repository root. It is the local operational memory snapshot for CODEC-CORTEX: active focus, release state, recent sessions, lessons, validation evidence and audit references.

The **Survival Core** (v0.2.1) adds: `survive` attribute with 4 levels, priority pack P0-P5, conceptual context profiles (MIN/RECOVERY/WORK/FULL), degradation policy, HCORTEX render protocol (5 rules, 8 steps), and source traceability. See `docs/en/specs/context-survival.md` for the consolidated specification (EN) or `docs/es/specs/supervivencia-contexto.md` (ES).

For a human-readable HCORTEX view of that same context, read `brain.md`. Use `skill/cortex/brain.cortex` as the reusable template for a new local memory file. Use root `brain.cortex` and `brain.md` only as this repository's current context snapshot.

## Structure

| Path | Content | Status |
|------|---------|--------|
| `brain.cortex` | Current CODEC-CORTEX operational context snapshot for agents/reviewers | Current/local memory |
| `brain.md` | HCORTEX human-readable view of root `brain.cortex` | Current/local memory view |
| `skill/` | Skill specification, dense Skill file, AGENT example and local brain template | Current/specification |
| `docs/en/specs/` | English fundamentals, algorithm, adoption and MCP design docs | Specification |
| `docs/es/specs/` | Spanish fundamentals, algorithm, adoption and MCP design docs | Specification |
| `cli/` | CLI v1.1.9: cortex verify, render, CRUD, doctor, diff, format, diagram | Current/implementation |
| `src/` | Python package placeholder | Legacy placeholder |
| `ROADMAP.md` | Phase plan from Skill adoption to enterprise MCP | Current |
| `STATUS.md` | Truth registry for implemented, specified, planned and future capabilities | Current |

## Documentation

| Document | Content | Language |
|----------|---------|----------|
| `skill/hcortex/SKILL_HCORTEX.md` | Main HCORTEX Skill specification (canon) | ES |
| `skill/cortex/SKILL.md` | Dense CORTEX Skill expression | CORTEX |
| `docs/es/specs/fundamentos.md` | Ontology, axioms, principles, maturation and HCORTEX | ES |
| `docs/en/specs/fundamentals.md` | Ontology, axioms, principles, maturation and HCORTEX | EN |
| `docs/es/specs/algoritmo.md` | Parser, verification and planned codec algorithms | ES |
| `docs/en/specs/algorithm.md` | Parser, verification and planned codec algorithms | EN |
| `docs/es/specs/adopcion.md` | Layered agent adoption guide | ES |
| `docs/en/specs/adoption.md` | Layered agent adoption guide | EN |
| `docs/es/specs/mcp-bridge.md` | Future MCP bridge architecture | ES |
| `docs/en/specs/mcp-bridge.md` | Future MCP bridge architecture | EN |
|| `docs/es/specs/supervivencia-contexto.md` | Survival Core: survive, P0-P5, profiles, HCORTEX | ES |
|| `docs/en/specs/context-survival.md` | Survival Core: survive, P0-P5, profiles, HCORTEX | EN |
|| `docs/es/specs/metodologia-benchmark.md` | Survival benchmark methodology (5 questions) | ES |
|| `docs/en/specs/benchmark-methodology.md` | Survival benchmark methodology (5 questions) | EN |
|| `docs/es/specs/distribucion-skill.md` | Universal Skill distribution for all agent platforms | ES |
|| `docs/en/specs/skill-distribution.md` | Universal Skill distribution for all agent platforms | EN |
| `ROADMAP.md` | Phase plan from Skill to enterprise (E1-E5) | EN |

## Claim Policy

- Token reduction targets are design goals or illustrative examples until reproducible benchmarks exist.
- The planned codec is deterministic and does not require LLM calls for parse, encode, decode or verify.
- Reversibility means structural roundtrip for codec operations and contextual reversibility through HCORTEX for humans.
- Literal reconstruction of every original message or raw source text is not promised.
- Enterprise MCP is a future phase.

## Roadmap

1. Universal Skill.
2. `.cortex` format.
2.1. **Survival Core** — survive, P0-P5, profiles, degradation, HCORTEX render target.
3. HCORTEX human view.
4. Deterministic codec and CLI.
5. Memory runtime.
6. Enterprise MCP.

See [ROADMAP.md](ROADMAP.md) for phase details.

## License

MIT — See [LICENSE](LICENSE) for details.
