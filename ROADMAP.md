<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

# CODEC-CORTEX Roadmap

## Phase 1: Universal Skill

**Status:** current.

**Goal:** make CODEC-CORTEX adoptable by any LLM/SLM through instructions and `.cortex` files.

**Deliverables:** `skill/hcortex/SKILL_HCORTEX.md`, `skill/cortex/SKILL.md`, `skill/cortex/AGENT.md`, `skill/cortex/brain.cortex`.

**Non-goals:** no Python package, server or MCP bridge required for initial adoption.

**Acceptance criteria:** a reader understands that initial adoption is Skill-first and can separate FCS, OBJ and WRK from linear history.

## Phase 2: Cortex Format

**Status:** current/specification.

**Goal:** stabilize `.cortex` structure, sigils, sections, glossary and examples.

**Deliverables:** formal grammar, valid examples, pitfall catalog and template files.

**Non-goals:** no unsupported promise of literal source reconstruction.

**Acceptance criteria:** examples are coherent, placeholders are explicit and sigil rules are consistent.

### Phase 2.1: Survival Core

**Status:** current.

**Goal:** define minimum survival context: `survive` attribute, priority pack P0-P5, conceptual profiles, and degradation policy.

**Deliverables:** `survive` specification, P0-P5 priority pack, context profiles (MIN/RECOVERY/WORK/FULL), HCORTEX as render target, degradation policy with direct selection. Documents: `docs/specs/context-survival.md`, `docs/specs/benchmark-methodology.md`.

**Non-goals:** no parser, no runtime, no automated benchmarks.

**Acceptance criteria:** SKILL.cortex instructs agents to survive context reduction by cognitive priority.

## Phase 3: HCORTEX

**Status:** current/specification.

**Goal:** define a human-readable contextual output for inspection, audit, correction and continuity.

**Deliverables:** rendering rules, sample HCORTEX output and audit checklist.

**Non-goals:** HCORTEX is not a literal decode of every original raw message.

**Acceptance criteria:** a human can inspect focus, objective, rules, state, sessions and lessons.

## Phase 4: Deterministic Codec

**Status:** current.

**Goal:** maintain parser, encoder, decoder, verifier, renderer and CLI.

**Deliverables:** `cortex` CLI at `cli/` — v0.3.2, 25 comandos (17 clásicos + 8 canónicos v2 con alias `v2-*` deprecados), 341 tests, núcleo bidireccional CORTEX ⇄ HCORTEX verificado sobre artefactos canónicos (266 entries, 44 VIEW, coverage 100%, roundtrip 0 diffs), corpus benchmark migrado a VIEW directives (10/10 artefactos), `cortex canonicalize` VIEW-aware (B-01/B-05 fix), workflow operativo del agente integrado al skill.

| Capacidad | Estado |
|-----------|:------:|
| CORTEX → HCORTEX | `current` — byte-identical contra canónico |
| HCORTEX → CORTEX | `current` — reconstruye 266/266 entries |
| Roundtrip bidireccional | `current` — AST-equivalent y content-equivalent, 0 diffs |
| VIEW directives | `current` — 44/44 en skill; 10/10 artefactos del corpus migrados en v0.3.2 |
| Gate reversible:true | `current` — coverage 100%, cero errores, no display-only |
| CLI commands | `current` — 25 comandos (8 canónicos v2 + 8 alias `v2-*` deprecados + 9 legacy) |
| `cortex canonicalize` VIEW-aware | `current` — v0.3.2: preserva estructura sin VIEW; canonicaliza con VIEW; flag `--preserve` |
| Nombres canónicos CLI | `current` — v0.3.2: `roundtrip`, `convert`, `inspect`, etc. sin prefijo `v2-` |
| Workflow operativo del agente | `current` — v0.3.2: 5 PUML + 4 reglas `!` + 5 perfiles CORTEX-OUT |
| `doctor` v2 | `planned` — no implementado como comando separado |
| JSON uniforme para todos los v2 | `planned` — no declarar como actual |
| MCP server | `future` — no implementado |
| Runtime promote/decay | `future` — no implementado |

**Acceptance criteria:** all `.cortex` files pass `cortex verify --strict` with 0 errors. HCORTEX renders correctly in readable and audit modes. Roundtrip CORTEX → HCORTEX → CORTEX is AST-equivalent. Roundtrip HCORTEX → CORTEX → HCORTEX is content-equivalent. Corpus benchmark completa con VIEW directives y coverage 100% (v0.3.2). `cortex canonicalize` no rompe compatibilidad con artefactos sin VIEW (v0.3.2).

## Phase 5: Memory Runtime

**Status:** future.

**Goal:** manage context lifecycle and maturation.

**Deliverables:** WRK update, SES consolidation, LNG extraction, promote/decay policy and audit rules.

**Non-goals:** the runtime must not silently promote knowledge without a user-confirmed policy.

**Acceptance criteria:** lifecycle transitions are explicit, auditable and reversible as operational context.

## Phase 6: Enterprise MCP

**Status:** future.

**Goal:** expose implemented codec/runtime operations as enterprise-grade agent tools.

**Deliverables:** MCP server, handler schemas, auth model, audit events and deployment guide.

**Non-goals:** MCP is not the first adoption mechanism.

**Acceptance criteria:** every MCP handler maps to implemented codec/runtime functions and emits auditable operations.

---

## Enterprise Track

Phases E1–E5 represent the enterprise-hardening track. They are independent of the canonical stack phases (1–6) and can be executed in parallel.

### Phase E1: Distribution and CI/CD

**Status:** planned.

**Goal:** automate distribution, testing and publishing of the `cortex` CLI and SKILL artifacts across platforms.

**Deliverables:**
- PyPI package (`cortex-cli` or `codec-cortex`) — `pip install codec-cortex` installs CLI and SKILL.
- GitHub Actions CI: lint, test (Python 3.9–3.12), verify-fixtures, coverage gate (≥85%).
- `Makefile` or `Taskfile`: `install`, `test`, `lint`, `build`, `publish` targets.
- `setuptools-scm` or `bump-my-version` for automated versioning.
- Pre-commit hooks (`.pre-commit-config.yaml`): ruff, secret-scan, `cortex verify --strict`.

**Non-goals:** no MCP server, no runtime.

**Acceptance criteria:** `pip install codec-cortex` works. CI passes on every PR. Release published automatically on tag.

### Phase E2: Security and Governance

**Status:** planned.

**Goal:** harden the CLI and protocol against misuse, secret leakage and unauthorized mutations.

**Deliverables:**
- Pre-commit secret scanner (hardens existing `cortex doctor` scan).
- RBAC-like mutation gates: read-only mode, editor mode, admin mode (governs `--force`).
- Persistent audit log: CRUD operations logged outside the `.cortex` file.
- Release signing: SHA256 hashes for all published artifacts.
- `cortex verify --signature` for artifact integrity checks.
- Dependabot/Renovate configuration for dev dependencies.

**Non-goals:** no federated identity, no enterprise SSO.

**Acceptance criteria:** pre-commit hooks block secrets. Audit log captures every mutation with timestamp and agent identity.

### Phase E3: Documentation and Test Coverage

**Status:** planned.

**Goal:** achieve production-grade documentation coverage and test quality.

**Deliverables:**
- Sphinx or MkDocs site with API reference, tutorials, how-to guides and explanations.
- Docstrings complete for all public API in `cortex.core`, `cortex.crud`, `cortex.hcortex`, `cortex.glossary`.
- Test coverage ≥85% measured by `pytest-cov`.
- Automated benchmark suite: compression ratio, roundtrip fidelity, render latency.
- `cortex benchmark` command (runs reproducible benchmarks from `benchmarks/`).

**Non-goals:** no user-analytics, no telemetry.

**Acceptance criteria:** coverage gate blocks PRs below 85%. MkDocs site auto-deploys on release.

### Phase E4: Enterprise MCP Server

**Status:** future.

**Goal:** expose CLI and protocol capabilities as MCP tools for multi-agent orchestration.

**Deliverables:**
- `cortex-mcp` entry point (stdio transport, local).
- `cortex-mcp --http` for HTTP/SSE transport (cloud deployments).
- Auth middleware: API key, bearer token.
- Audit events: every tool call emits `AUD`-compatible structured log.
- Tool catalog: `cortex_list`, `cortex_verify`, `cortex_render`, `cortex_get`, `cortex_diff`.

**Non-goals:** no runtime lifecycle management.

**Acceptance criteria:** `cortex-mcp` connects to any MCP client (Claude Desktop, VS Code, custom). Every tool call is auditable.

### Phase E5: Memory Runtime

**Status:** future.

**Goal:** automate the WRK → SES → LNG → KNW lifecycle with user-confirmed policies.

**Deliverables:**
- `cortex session start/close/status` — WRK lifecycle.
- `cortex session consolidate` — compress SES from WRK history.
- `cortex lesson extract` — detect patterns across SES (threshold configurable).
- `cortex profile --budget 1000` — apply P0-P5 triage automatically.
- Auto-promotion: `detect_recurrence(threshold=N) → ask_user → promote/decay`.

**Non-goals:** no silent autonomous promotion.

**Acceptance criteria:** lifecycle transitions are explicit, auditable and require human confirmation for promote/decay.
