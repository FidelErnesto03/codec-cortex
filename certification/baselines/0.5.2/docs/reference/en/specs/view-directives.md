<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MPL-2.0 -->

# CODEC-CORTEX — VIEW Directives Reference

> **STATUS NOTE:** As of v0.4.1 the canonical SKILL.md contains 44 VIEW directives covering all 14 sections. This document summarizes the VIEW directive kinds, targets, and reverse strategies.

---

## 1. What is a VIEW directive

A VIEW directive is a declarative contract that maps a `.cortex` section or entries to a specific HCORTEX rendering kind. It lives in `$13` of the canonical `skill/cortex/SKILL.md`.

```cortex
VIEW:<name>{kind:"<render_kind>",target:"<selector>",reverse:"<strategy>",status:cur,title:"<display_title>"}
```

**Fields:**

| Field | Description |
|-------|-------------|
| `name` | Unique identifier for the VIEW |
| `kind` | HCORTEX render kind: `table`, `kv_table`, `prose`, `puml`, `numbered_list`, `callout` |
| `target` | CORTEX selector: `$N:SIGIL:name`, `$N:SIGIL:*`, `$N:NAME` |
| `reverse` | Reverse strategy: `rows_to_entries`, `row_to_attrs`, `body_to_cuerpo`, `verbatim_to_bloque`, `items_to_ordered_entries`, `callout_to_risk` |
| `status` | `cur` (current), `specification`, `pln` (planned) |
| `title` | Human-readable section title in HCORTEX output |
| `fields` (optional) | Explicit field list for heterogeneous targets |
| `preserve` (optional) | `verbatim` for PUML blocks |

---

## 2. Render kinds

| Kind | Generates | Example |
|------|-----------|---------|
| `table` | Standard Markdown table | Sigil list with columns |
| `kv_table` | Key-value table | `| Field | Value |` |
| `prose` | Paragraph or prose block | Axiom descriptions |
| `puml` | Verbatim PUML code block | Architecture diagrams |
| `numbered_list` | Ordered list | Rule sequences |
| `callout` | Blockquote callout | Risk declarations |

---

## 3. Reverse strategies

| Strategy | Reverse operation | Used for |
|----------|-------------------|----------|
| `rows_to_entries` | Each table row → one sigil entry | Generic sigil tables |
| `row_to_attrs` | Key-value table → attr pairs | Identity, scope, enums |
| `body_to_cuerpo` | Prose block → cuerpo entry | Descriptions, axioms |
| `verbatim_to_bloque` | Code block → bloque entry | PUML diagrams |
| `items_to_ordered_entries` | List items → ordered entries | Rule sequences |
| `callout_to_risk` | Blockquote → risk entry | Risk declarations |

---

## 4. VIEW coverage summary

| Section | VIEWs | Kinds used |
|:-------:|:-----:|------------|
| $0 Glossary | 9 | table, kv_table |
| $1 Identity | 4 | kv_table, table |
| $2 Purpose | 5 | prose, table |
| $3 Handlers | 1 | table |
| $4 Rules | 1 | numbered_list |
| $5 Constraints | 3 | table, callout |
| $6 Diagrams | 1 | puml |
| $7 Contracts | 1 | table |
| $8 Survive | 2 | kv_table, table |
| $9 Profiles | 5 | table, prose |
| $10 Degradation | 2 | numbered_list, prose |
| $11 HCORTEX | 5 | table, prose, kv_table |
| $12 CORTEX-OUT | 3 | table, prose, kv_table |
| $13 VIEWS | 2 | table |
| **Total** | **44** | — |

---

## 5. Key VIEW directives (selected)

| VIEW | Section | Kind | Target | Reverse |
|------|:-------:|:----:|--------|---------|
| `sigils_canonicos` | $0 | table | `$0:canonical_sigils` | rows_to_entries |
| `type_decls` | $0 | kv_table | `$0:type_decls` | row_to_attrs |
| `microtokens_decl` | $0 | table | `$0:microtokens` | rows_to_entries |
| `project_identity` | $1 | kv_table | `$1:IDN:project` | row_to_attrs |
| `handlers` | $3 | table | `$3:HDL:*` | rows_to_entries |
| `rules_normalization` | $4 | numbered_list | `$4:!:*` | items_to_ordered_entries |
| `diagrams` | $6 | puml | `$6:DIAG:*` | verbatim_to_bloque |
| `survive_rules` | $8 | kv_table | `$8:!:*` | row_to_attrs |
| `hcortex_modes` | $11 | table | `$11:KNW:hc_modes` | rows_to_entries |
| `cortex_out_def` | $12 | prose | `$12:DESC:out_def` | body_to_cuerpo |
| `out_blocks` | $12 | table | `$12:KNW:out_blocks` | rows_to_entries |

> **Full reference:** The complete set of 44 VIEW directives is defined in `skill/cortex/SKILL.md` §13.
> **See:** [`docs/es/specs/directivas-view.md`](../es/specs/directivas-view.md) for the Spanish version.
