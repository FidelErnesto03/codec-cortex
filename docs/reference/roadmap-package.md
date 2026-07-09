<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MPL-2.0 -->

# CODEC-CORTEX Roadmap

**v0.4.0 · MPL-2.0 · 464 tests · 35+ comandos CLI · 2026-07-02**

---

## Resumen

| # | Etapa | Estado | Kernel |
|:-:|-------|:------:|--------|
| 1 | **Protocolo universal** | ✅ | SKILL v1.3.0, 25 sigilos, $0 autocontenido, Survival Core P0-P5, HCORTEX + CORTEX-OUT |
| 2 | **Codec determinista** | ✅ | CLI v0.4.0, parser, verifier, renderer, roundtrip, CI/CD + PyPI + security (E1+E2) |
| 3 | **Documentación y distribución** | ✅ | Docs EN/ES (12+12 specs), wiki, legal (MPL-2.0), benchmarks v1.0→v2.2.2, API reference |
| 4 | **Motor de aprendizaje** | 🔄 | Learning engine v0.1.0: scoring Fibonacci, candidates, elevation, policies, index |
| 5 | **Runtime y MCP enterprise** | ⏳ | MCP server (`cortex-mcp`), session lifecycle, auto-promote/decay, multi-agente |

---

## Etapa 1: Protocolo universal

**Estado:** ✅ current. **Versión:** SKILL v1.3.0.

**Qué es:** el protocolo que cualquier agente carga para gobernar su memoria. Define la ontología, los sigilos, los contratos posicionales, los handlers operacionales y las reglas de supervivencia contextual.

**Entregables:**
- `skill/cortex/SKILL.md` — 250 entries, 38 VIEW directives, 13 secciones.
- `skill/hcortex/SKILL.md` — HCORTEX canónico reversible con 35 VIEW markers.
- 25 sigilos canónicos con contratos posicionales en `$0`.
- Survival Core: `survive`, prioridad P0-P5, perfiles MIN/RECOVERY/WORK/FULL, degradación.
- HCORTEX: 12 reglas de densidad, 15 constraints, 12 anti-patrones, 4 modos de render.
- CORTEX-OUT: protocolo de salida conversacional con 5 perfiles.
- Diagrama PUML operativo del ciclo de vida del agente.

**Criterio:** un agente que carga este SKILL puede gestionar foco, objetivos, restricciones y memoria sin depender de historial lineal.

---

## Etapa 2: Codec determinista

**Estado:** ✅ current. **Versión:** CLI v0.4.0.

**Qué es:** el CLI que procesa archivos `.cortex` de forma determinista, sin dependencia de LLM. Incluye parser, encoder, decoder, verifier, renderer HCORTEX, y el pipeline completo de CI/CD + seguridad.

**Entregables:**
- **CLI `cortex`** — 35+ comandos: CRUD (add, update, delete, move, list, get), codec v2 (convert, verify-view, roundtrip-bidir, inspect, canonicalize, compare, explain-loss), E2 security (doctor --scan-secrets, audit, verify --signature), E3 docs (docstring, benchmark).
- **Parser dual** — v1 para comandos CRUD y `verify --strict`, v2 para codec y VIEW. `load_doc()` v2-aware.
- **Codec bidireccional** — CORTEX ⇄ HCORTEX con 38 VIEW directives. Cobertura 100%.
- **CI/CD** — GitHub Actions: lint + test (3.9–3.12) + verify-view + build + publish a PyPI en tag.
- **Seguridad** — secret scanner (12 patrones), mutation gates (`--mode`), audit log on-demand, release signing.
- **464 tests** — 415 core + 49 learning engine. Ruff 0 errores.

**Criterio:** todo `.cortex` pasa `cortex verify --strict` con 0 errores. `pip install codec-cortex` funciona. CI publica en cada tag.

---

## Etapa 3: Documentación y distribución

**Estado:** ✅ current. **Versión:** v0.4.0.

**Qué es:** documentación completa bilingüe, benchmarks científicos reproducibles, wiki pública, y transición legal a MPL-2.0.

**Entregables:**
- **Docs EN/ES** — 12 specs en inglés, 12 specs en español con STATUS NOTES. 4 HCORTEX en cada idioma (tutorial, how-to, explicación, referencia).
- **API reference** — 9 archivos `.cortex` autocontenidos en `docs/cortex/api/`.
- **Benchmarks** — 6 versiones (v1.0.0 → v2.2.2), 11 dominios, 4,840 runs cada una. Corpus fuente versionable.
- **Wiki** — 8 páginas en github.com/FidelErnesto03/codec-cortex/wiki.
- **Legal** — MPL-2.0 con SPDX headers en 150+ archivos. `docs/legal/`: license.md, trademark-policy.md, legacy-mit-notice.md. `docs/security/privacy.md`.
- `cortex docstring` — deriva docstrings desde API reference.
- `cortex benchmark` — inventario de suites.

**Criterio:** cobertura documental completa. Navegación clara desde `docs/README.md`. Benchmarks reproducibles con scripts versionados.

---

## Etapa 4: Motor de aprendizaje

**Estado:** 🔄 learning engine v0.1.0. Runtime completo → futuro.

**Qué es:** sistema determinista de scoring, detección de candidatos y elevación de conocimiento sobre workspaces `.cortex/`.

**Entregables actuales (v0.1.0):**
- `cortex learn` — 10 subcomandos: init, doctor, policy, index, scan, candidates, explain, elevate, profile, workspace.
- Algoritmo `golden_fibonacci_v1`: hotness, promotion_score, risk_weight, read_priority.
- Workspace `.cortex/` con brain, learn-policies, MANIFEST, index, cache.
- Policies: condiciones evaluables (`promotion_score>=8|user_validated=true`).
- Elevación controlada: `plan_patch` → `render_diff` → `apply_patch` → `verify_post_apply`.
- 49 tests dedicados.

**Entregables futuros (runtime completo):**
- `cortex session start/close/status` — ciclo de vida WRK.
- `cortex session consolidate` — SES desde historial.
- Auto-promote/decay con confirmación humana.
- `cortex profile --budget N` — triage P0-P5 automático.

**Criterio:** transiciones explícitas, auditables y con confirmación humana para promociones a KNW.

---

## Etapa 5: Runtime y MCP enterprise

**Estado:** ⏳ future.

**Qué es:** exponer el codec y el motor de aprendizaje como servidor MCP para orquestación multi-agente empresarial, con ciclo de vida de sesión completo.

**Entregables planeados:**
- `cortex-mcp` — entry point stdio (local) + HTTP/SSE (cloud).
- Auth: API key, bearer token.
- Tool catalog: `cortex_list`, `cortex_verify`, `cortex_render`, `cortex_get`, `cortex_diff`, `cortex_learn_*`, `cortex_session_*`.
- Ciclo de vida: `cortex session start/close/consolidate`, `cortex lesson extract`.
- Auto-promoción con políticas confirmadas: `detect_recurrence → ask_user → promote/decay`.
- Auditoría: cada tool call emite `AUD` estructurado.

**Criterio:** `cortex-mcp` se conecta a cualquier cliente MCP. Cada operación es auditable. Las promociones requieren confirmación humana.

---

## Historial de versiones

| Versión | Fecha | Hito |
|---------|-------|------|
| v0.4.0 | 2026-07-02 | Etapa 3 completa: documentación, wiki, legal, licencia MPL-2.0 |
| v0.4.1 | 2026-07-02 | Etapa 4 parcial: learning engine v0.1.0 + benchmarks v2.2.x |
| v0.3.6 | 2026-07-01 | Etapa 1 refinada: SKILL v1.3.0, parser v2-aware, docs EN/ES |
| v0.3.5 | 2026-07-01 | Etapa 3 iniciada: protocolo de documentación E3 |
| v0.3.4 | 2026-06-30 | Etapa 2: seguridad E2 (secret scanner, mutation gates, audit) |
| v0.3.3 | 2026-06-29 | Etapa 2: CI/CD E1 (PyPI, GitHub Actions, ruff) |
| v0.3.2 | 2026-06-28 | Etapa 2: codec v2, VIEW migration, canonical naming |
| v0.3.1 | 2026-06-27 | Etapa 2: CLI v2 codec, benchmark v1.0.0 |
| v0.3.0 | 2026-06-27 | Etapa 2 iniciada: CLI integration, .cortex canónicos |
| v0.2.x | 2026-06-24 | Etapa 1: Survival Core, HCORTEX, DIALECT |
