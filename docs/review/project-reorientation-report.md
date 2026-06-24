<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

# Project Reorientation Report

## Diagnosis

The repository narrative was codec-first and used implementation-strength claims before the codec, CLI, runtime and MCP existed. The adjustment pass reorients CODEC-CORTEX as a universal Skill and contextual memory protocol first, with `.cortex` as the model-facing memory format and HCORTEX as the human audit view.

## Risk Register

| Risk | Correction |
|------|------------|
| Unsupported token metrics | Marked as targets or illustrative examples pending benchmarks |
| Generic 100% reversibility | Scoped to structural codec roundtrip targets; HCORTEX is contextual reversibility |
| Phantom CLI commands | Marked planned where retained as design examples |
| MCP as current capability | Marked future enterprise phase |
| Example files as real state | Added template/status language and placeholders |
| Layer collapse | Added README stack, ROADMAP and STATUS registry |

## File-by-File Recommendations Applied

| File | Applied change |
|------|----------------|
| `README.md` | Rewritten as Skill-first public entry point with status, stack, quick start and claim policy |
| `STATUS.md` | Added maturity registry |
| `ROADMAP.md` | Added six-phase plan |
| `skill/SKILL.md` | Added progressive adoption and operation status table |
| `skill/SKILL.en.md` | Added progressive adoption and operation status table |
| `skill/SKILL.cortex` | Rewritten as dense status-aware Skill expression |
| `skill/AGENT.cortex` | Marked as example/template and softened absolute format rule |
| `skill/brain.cortex` | Added template notice and placeholder markers |
| `docs/*/specs/*.md` | Added status notes and softened unsupported metrics/absolute claims |
| `pyproject.toml` | Updated description to specification/Skill-first language |
| `src/codec_cortex/__init__.py` | Clarified package placeholder status |

## Remaining Risks

The long reference documents still contain planned algorithm details. They are acceptable as design material only while the status banners and STATUS.md remain authoritative. Before a release, add executable tests and benchmark fixtures or remove numeric targets from public-facing sections.
