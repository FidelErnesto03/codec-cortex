<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

# CODEC-CORTEX — Microtokens Reference

> **STATUS NOTE:** As of v0.3.6 the canonical glossary in `skill/cortex/SKILL.md` $0 defines 30+ microtokens — compact abbreviations that expand to full terms during CORTEX parsing. They MUST be registered in $0 before first use and MUST NOT expand inside words or verbatim blocks.

---

## 1. What are microtokens

Microtokens are single- or multi-character abbreviations declared in `$0` that expand to full terms during CORTEX parsing. They reduce token count while preserving semantics.

**Declaration format:**
```cortex
$0:micro_<id>{expand:<full_term>}
```

**Expansion rule:** Microtokens expand only if delimited by: space, `|`, `,`, `{}`, newline, value-start, or value-end. They MUST NOT expand inside words (e.g. `param_d1` does NOT expand `d1`).

---

## 2. Status microtokens

| Token | Expansion | Purpose |
|:-----:|:---------:|---------|
| `cur` | `current` | Implemented and verified |
| `pln` | `planned` | Designed for a future version |
| `fut` | `future` | Vision beyond current scope |
| `blk` | `blocked` | Blocked by external dependency |

---

## 3. Survival level microtokens

| Token | Expansion | Purpose |
|:-----:|:---------:|---------|
| `min` | `minimum` | Survives under CORTEX-MIN profile |
| `rec` | `recovery` | Survives under CORTEX-RECOVERY |
| `wrk` | `work` | Survives under CORTEX-WORK |
| `full` | `full` | Survives under all profiles |

---

## 4. Status result microtokens

| Token | Expansion | Purpose |
|:-----:|:---------:|---------|
| `ok` | `success` | Operation succeeded |
| `fail` | `failure` | Operation failed |
| `part` | `partial` | Partially completed |

---

## 5. Operation microtokens

| Token | Expansion | Category |
|:-----:|:---------:|:--------:|
| `d1` | `decode` | Core codec |
| `d2` | `detect` | Maturation engine |
| `d3` | `decay` | Maturation engine |
| `c1` | `.cortex` | Format reference |
| `c2` | `HCORTEX` | Format reference |
| `v1` | `validate` | Verification |
| `v2` | `verify` | Verification |

---

## 6. Action microtokens

| Token | Expansion | Category |
|:-----:|:---------:|:--------:|
| `a1` | `file` | Operand |
| `a2` | `files` | Operand (plural) |
| `s1` | `sigil` | Protocol element |
| `s2` | `section` | Structure element |
| `h1` | `handler` | Operational handler |
| `x1` | `extract` | Diagram operation |
| `x2` | `list` | Listing operation |
| `m1` | `modify` | Mutation operation |
| `m2` | `add` | Creation operation |
| `r1` | `remove` | Deletion operation |
| `p1` | `promote` | Maturation operation |
| `f1` | `format` | Formatting operation |
| `t1` | `structure` | Structural operation |

---

## 7. Expansion rules

| Rule | Description |
|------|-------------|
| Delimiter-only expansion | Microtokens expand only when surrounded by delimiters (space, `|`, `,`, `{}`, newline, value edges) |
| No inside-word expansion | `param_d1` does NOT expand `d1`; standalone `d1` does |
| Protection inside DIAG | Microtokens MUST NOT expand inside verbatim PUML blocks |
| Registration required | New microtokens MUST be declared in $0 before first use |
| Glossary extension | New microtokens follow the same registration rule as sigils |

---

## 8. Registration format in `$0`

```cortex
$0:micro_<id>{expand:<full_term>}
```

Where:
- `<id>` is a short alphanumeric token (1–3 chars preferred)
- `<full_term>` is the expansion string

> **See:** [`docs/es/specs/microtokens.md`](../es/specs/microtokens.md) for the Spanish version.
