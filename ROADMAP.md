<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

# CODEC-CORTEX Roadmap

## Phase 1: Universal Skill

**Status:** current.

**Goal:** make CODEC-CORTEX adoptable by any LLM/SLM through instructions and `.cortex` files.

**Deliverables:** `skill/SKILL.md`, `skill/SKILL.en.md`, `skill/SKILL.cortex`, `skill/AGENT.cortex`, `skill/brain.cortex`.

**Non-goals:** no Python package, server or MCP bridge required for initial adoption.

**Acceptance criteria:** a reader understands that initial adoption is Skill-first and can separate FCS, OBJ and WRK from linear history.

## Phase 2: Cortex Format

**Status:** current/specification.

**Goal:** stabilize `.cortex` structure, sigils, sections, glossary and examples.

**Deliverables:** formal grammar, valid examples, pitfall catalog and template files.

**Non-goals:** no unsupported promise of literal source reconstruction.

**Acceptance criteria:** examples are coherent, placeholders are explicit and sigil rules are consistent.

### Phase 2.1: Survival Core

**Status:** specification draft.

**Goal:** define minimum survival context: `survive` attribute, priority pack P0-P5, conceptual profiles, and degradation policy.

**Deliverables:** `survive` specification, P0-P5 priority pack, context profiles (MIN/RECOVERY/WORK/FULL), HCORTEX as render target, degradation policy with direct selection. Documents: `docs/specs/context-survival.md`, `docs/specs/benchmark-methodology.md`.

**Non-goals:** no parser, no runtime, no automated benchmarks, no v0.3.0 release.

**Acceptance criteria:** SKILL.cortex instructs agents to survive context reduction by cognitive priority.

## Phase 3: HCORTEX

**Status:** current/specification.

**Goal:** define a human-readable contextual output for inspection, audit, correction and continuity.

**Deliverables:** rendering rules, sample HCORTEX output and audit checklist.

**Non-goals:** HCORTEX is not a literal decode of every original raw message.

**Acceptance criteria:** a human can inspect focus, objective, rules, state, sessions and lessons.

## Phase 4: Deterministic Codec

**Status:** planned.

**Goal:** implement parser, encoder, decoder, verifier, renderer and CLI.

**Deliverables:** `parser.py`, `encoder.py`, `decoder.py`, `verify.py`, `hcortex.py`, `cli.py` and tests.

**Non-goals:** no LLM calls inside parse, encode, decode or verify operations.

**Acceptance criteria:** roundtrip tests pass, invalid structures fail clearly and DIAG raw mode is preserved.

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
