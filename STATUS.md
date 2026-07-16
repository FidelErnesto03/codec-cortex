<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MPL-2.0 -->

# CODEC-CORTEX Status

This file is the maturity registry for public claims in the repository. README, Skill docs and specifications must not imply a stronger status than this file.

## Implemented Now

- **v0.6.0** — Compatibility & Codec Hardening release with native v1/v2 document support, multiline preservation (CP-03), TransactionService CAS protection, session runtime isolation, feedback governance, and MPL-2.0 license clarity.
- **v0.5.0** — Rebranded as "Universal Communication Protocol for LLM/SLM Agents".
- **Repository documentation fully reorganized**: structured under `docs/` with reference, releases, verification, benchmarks, proposals, and archive categories.
- **README updated** with enterprise positioning: 3-layer protocol (Syntax → Transport → Knowledge) with compression metrics.
- **Roadmap documented**: Phase 1 (File CODEC ✅), Phase 2 (Stream CODEC / MCP 🚧), Phase 3 (Database CODEC 🔮).
- **CORTEX ≠ ArqUX distinction documented**: format vs governance framework.
- `skill/SKILL.md` and `skill/SKILL.cortex` Skill specifications.
- `skill/AGENT.cortex` example identity file.
- `skill/brain.cortex` local brain template.
- Spanish and English reference documents under `docs/reference/`.
- **CLI at `src/cortex/cli`:** v1.1.9+ with 17 commands (`new`, `render`, `compile`, `verify`, `get`, `list`, `add`, `update`, `delete`, `move`, `glossary`, `micro`, `doctor`, `diff`, `format`, `recover`, `diagram`), 222+ tests.
- **Deterministic parser, verifier and HCORTEX renderer** integrated in CLI.
- **CRUD operations:** `cortex add`, `cortex update`, `cortex delete`, `cortex list`, `cortex get`.
- **Structural diff:** `cortex diff` with governance-aware mode.
- **Recovery:** `cortex recover` repairs legacy `.cortex` files.
- **Diagram operations:** `cortex diagram extract` and `cortex diagram validate`.
- **Learning engine (v2):** `cortex.learn` with SES→LNG→KNW elevation pipeline.
- **Survival Core:** `survive` attribute with 4 levels, priority pack P0-P5, degradation policy.
- **HCORTEX render protocol:** 5 rules, 8 steps.
- **Auto-numbering:** BLP-003 in progress — sequential section counters for .cortex entries.
- **All `.cortex` files validated:** pass `cortex verify --strict`.
- **Native v1/v2 document handle:** No implicit downcasting; dialect-preserving operations.
- **Multiline preservation:** CP-03 compliant with verbatim newline retention by default.
- **TransactionService:** Atomic writes with expected_hash CAS, backup, validation and audit trail.

## Specification Exists

- `.cortex` sections and sigils (19 canonical + extensions via local $0 glossary).
- HCORTEX concept: render target with P-level filtering.
- Direct Skill adoption model with progressive compatibility.
- MCP server protocol design for Phase 2 (Stream CODEC).
- Learning engine specification (SES → LNG → KNW).
- 3-layer protocol architecture (Syntax → Transport → Knowledge).

## Designed But Not Implemented

- MCP server (`cortex.encode` / `cortex.decode` as MCP tools).
- ACP transport layer (cross-agent task delegation).
- LSP language server for .cortex editing.
- Database CODEC (sigil queries, semantic indexes, streaming).

## Planned Next

- Complete BLP-003 (auto-numbering sequential section counters).
- Implement MCP server for real-time agent encoding/decoding.
- Integrate learning engine as MCP tool.

## Future Phase

- Database CODEC: persistent sigil queries, streaming between agents.
- ACP integration for multi-agent orchestration.
- LSP for developer editor support.
- Governance, audit and deployment layer.

## Not Promised

- Literal reconstruction of every original message.
- Guaranteed recall improvement without reproducible benchmarks.
- Production-ready enterprise MCP today.
- Universal performance improvement across all models.
