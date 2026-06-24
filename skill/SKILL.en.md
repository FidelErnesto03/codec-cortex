<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

<p align="center">
  <strong>CODEC-CORTEX</strong> — Cognitive Operational Retrieval & Execution Template
  <br>
  <sub>SPECIFICATION · v1.1.0 · MIT · <a href="../AUTHORS.md">Fidel Ernesto Lozada A.</a></sub>
</p>

---

**Abstract:** Universal skill specification for deterministic structural compression of LLM agent cognitive memory. Defines the `.cortex` format with 20 cognitive sigils, HCORTEX human-readable output protocol, golden ratio (φ=1.618) memory distribution, continuous context management cycle, and user-driven maturation engine.

| | |
|---|---|
| **Author** | Fidel Ernesto Lozada A. — Systems Engineer / MSc. Managerial Sciences |
| **Repository** | [github.com/FidelErnesto03/codec-cortex](https://github.com/FidelErnesto03/codec-cortex) |
| **License** | [MIT](../LICENSE) |
| **Version** | 1.1.0 |
| **Language** | Structural: EN · Semantic: ES · Output: HCORTEX (user language) · Source: [SKILL.md](SKILL.md) (Spanish) |

---

## When to Use

- **You need persistent memory** for LLM agents without accumulating linear context
- **You use SLMs** with limited windows (4k-8k tokens)
- **You suffer "Lost in the Middle"** in long contexts
- **You want to reduce API costs** by eliminating redundant tokens
- **You implement CAG** (Cognitive Augmented Generation)
- **You need cross-framework integration** (Hermes, Claude, Codex, Qwen)

### Immediate Adoption Directive

> ⚠️ **First directive — non-negotiable.**
> From the moment you assume this skill, your persistent memory system restructures to the `.cortex` format.
>
> 1. **Current memory:** Migrate to `.cortex` using `encode()`.
> 2. **Future memory:** All new entries are stored in `.cortex`.
> 3. **Identity:** `AGENT.cortex` as entry point.
> 4. **Architecture:** `brain.cortex` as local brain with golden ratio distribution. **By convention, `brain.cortex` lives at the project root** — it is the agent's local operational state, not a skill artifact. The generic template is at `skill/brain.cortex`.
> 5. **Communication:** HCORTEX (tables, lists, K/V, PUML diagrams).
> 6. **De-adoption:** Exit GATE — `decode --format hcortex` over all `.cortex`.

```puml
@startuml
title Ciclo de Gestión de Contextos CORTEX

start
:Contexto CORTEX activo\n(.cortex cargado);

repeat
  :**Operar** — Agente usa el contexto\ncomo memoria de trabajo;

  if (¿WRK >70% ventana?) then (sí)
    :**Consolidar** — compress()\nWRK → SES + LNG;
  endif

  :**Verificar** — cortex verify;

  if (¿verify OK?) then (sí)
    :Estructuralmente sano ✅;
  else (no)
    :Reparar; Re-verificar;
  endif

  :**Detectar** — cortex detect;

  if (¿Patrones recurrentes?) then (sí)
    :**Consultar** — ask_user()\n¿Promover a KNW?;
    if (sí) then
      :**Madurar** — promote()\nSES/LNG → KNW;
    endif
  endif

  :**Degradar** — cortex decay;
  if (¿KNW >30 días sin uso?) then (sí)
    :KNW → SES;
  endif

  :**Auditar** — cortex diagram list;
  
  if (¿Usuario solicita eliminar?) then (sí)
    :**Eliminar** — degradar 1 nivel\nKNW → SES → archive;
  endif

  if (¿Usuario solicita desadoptar?) then (sí)
    :**GATE de Salida** — decode hcortex\ntodos los .cortex → .md;
    stop
  endif

repeat while (contexto activo)
stop
@enduml
```

### Do Not Use For

- **Systems with less than 500 tokens** of context window
- **Agents without local file reading capability**
- **Non-textual data processing** (images, audio without transcription)
- **Tasks that do not require persistence between sessions**

---

## Overview

CODEC-CORTEX is a deterministic structural compression protocol. Unlike JSON, YAML, or ML, the `.cortex` format is not a markup language — it is a **cognitive codec**: an ultra-dense representation of agent memory that preserves 100% of operational semantics with 70-85% fewer tokens.

**Guiding principle:** *"Structure over Semantics. The Glossary ($0) dictates syntax, not meaning. PUML diagrams are native compression. Knowledge matures by user decision, not by counters."*

### Architecture

```puml
@startuml
title CODEC-CORTEX Architecture

package "CORTEX Format" {
  rectangle "$0 Glossary" as g
  rectangle "$1 Identity" as i
  rectangle "$2 Context" as c
  rectangle "$3 Handlers" as h
  rectangle "$4 Rules" as r
  rectangle "$5 Pitfalls" as p
  rectangle "$6 Diagrams" as d
  rectangle "$7 Metrics" as m
}

package "Codec Operations" {
  rectangle "decode()" as dec
  rectangle "encode()" as enc
  rectangle "verify()" as ver
  rectangle "patch_*()" as pat
  rectangle "glossary_*()" as glo
  rectangle "promote()" as pro
  rectangle "decay()" as dey
}

g --> dec
dec --> enc
enc --> ver
ver --> pat
pat --> glo
glo --> pro
pro --> dey
@enduml
```

---

## Universal Cognitive Glossary ($0)

### Sigils

| Sigil | Name | Expansion | Risk | Description |
|--------|--------|-----------|:------:|-------------|
| `IDN` | identity | `attrs` | B | Skill identity |
| `DOM` | domain | `attrs` | B | Application scope |
| `KNW` | knowledge | `attrs` | B | Tools and capabilities |
| `AXM` | axiom | `body` | H | Immutable guiding principle |
| `CNST` | constraint | `attrs` | M | Operational limit |
| `OBJ` | objective | `attrs` | B | Active goal |
| `WRK` | work | `attrs` | B | Current execution state |
| `FCS` | focus | `attrs` | H | Attention anchor (critical) |
| `REF` | reference | `attrs` | B | Link to documentation |
| `SES` | session | `attrs` | B | Compressed episode (I→O→R) |
| `LNG` | lesson | `content` | M | Learned heuristic |
| `HDL` | handler | `attrs-pos` | M | ORDER: command\|description |
| `!` | rule | `body` | H | Mandatory operational rule |
| `ERR` | error | `attrs` | M | Known error + solution |
| `DIAG` | diagram | `block` | M | PUML diagram (verbatim) |
| `→` | transition | `relation` | - | Causal relationship |
| `PFL` | pitfall | `content` | M | Known domain error |
| `TAG` | tag | `attrs` | B | Classification metadata |
| `DESC` | description | `content` | B | Semantic description |
| `DEP` | dependency | `attrs` | M | Dependency between modules |

### Expansion Types

| Type | Meaning | Limitations |
|------|-------------|--------------|
| `attrs` | Key:value pairs separated by `,` or `\|` | Robust |
| `attrs-pos` | Positional attributes without keys. Order defined in $0. Separator `\|` | Requires $0 |
| `body` | Literal text (axioms, rules) | Robust |
| `content` | Structured composite content | Careful with `:` and `,` |
| `block` | Exact multiline block (verbatim) | Only multiline fragments |
| `relation` | Causal relationship between two elements | Only direct flows |

### Micro-Glossary of Values ($0)

| Prefix | Semantics | Tokens | Example |
|---------|-----------|--------|---------|
| `d_` | Actions | d1=decode, d2=detect, d3=decay | `d1 c1 <a1>` |
| `c_` | Format | c1=.cortex | `c1 v1` |
| `v_` | Validation | v1=validate | `v1 structure` |
| `a_` | Files | a1=file, a2=files | `a1 c1` |
| `s_` | Structure | s1=sigil, s2=section | `m2 s1 a $0` |
| `h_` | Handlers | h1=handler | `h1 list` |
| `x_` | Extraction | x1=extract, x2=list | `x1 diagram` |
| `m_` | Modification | m1=modify, m2=add | `m1 entry` |
| `r_` | Removal | r1=remove | `r1 by name` |
| `p_` | Promotion | p1=promote | `p1 SES→KNW` |
| `f_` | Format | f1=format | `--f1 hcortex` |
| `t_` | Terms | t1=structure | `t1 check` |

**Delimiting rules:** Micro-tokens are expanded only when delimited by space, `|`, `,`, `{`, `}`, `\n`, start or end of value. They are not expanded inside words (`param_d1` → `param_d1`) nor after `_` or `-`.

### Glossary Rules

1. Every `.cortex` MUST have a glossary in `$0` as the first section.
2. The glossary in `$0` prevails — it is the single source of structural truth.
3. Sigils without an entry in `$0` are interpreted as `attrs`.
4. The content of `$0` is NOT interpreted as cognitive memory.
5. Labels, keywords, handlers, and micro-tokens in **English**. Semantic content in domain language.

---

## Cognitive Compiler Principles

1. **Compression, not summarization.** `.cortex` preserves 100% of operational semantics. `encode()` transforms — it does not summarize or lose.
2. **Pure determinism.** `decode(encode(content)) == content` always. Zero hallucinations, zero fabrications.
3. **The glossary is the contract.** New sigil = new entry in `$0`. If not in `$0`, it is treated as `attrs` by default.
4. **Structure over semantics.** The parser is a 6-state character automaton. Zero ML, zero complex regex, zero ambiguity.
5. **Expansion types governed by the glossary.** A parser must not infer whether a value is `attrs` or `content`. `$0` rules.
6. **LLM independence.** The codec does not use, invoke, or depend on any LLM. It is a standard Python library.
7. **Ecosystem portability.** The `.cortex` format is plain text, line-oriented, parseable with stdlib. Framework-independent.
8. **Self-creation of sections.** If `patch_add` references a section that does not exist, it creates it automatically.
9. **PUML diagrams are native compression.** A 20-line `DIAG` communicates flows, relationships, and processes that would occupy 200+ lines of prose.
10. **Diagrams are preserved intact; companion sigils enrich them.** A `DIAG` is of type `block` (verbatim). Sigils sharing the same name provide interpretive context.
11. **Maturation is by user decision.** The engine detects recurring patterns and asks. The user decides whether to promote to KNW.
12. **The system can make the user aware.** If the engine detects a pattern the user had not identified, the system's question reveals something about themselves.
13. **The LLM responds in structured format.** Tables, key/value pairs, lists, and PUML diagrams are the output language to the human.
14. **HCORTEX is the decompression protocol for humans — $0 not included.** `decode(format=hcortex)` produces markdown with tables, lists, K/V, and diagrams. The $0 glossary is AI-only structural metadata; HCORTEX output omits $0 and only includes semantic sections ($1+).
15. **Collapse of redundant attributes.** When $0 defines `attrs-pos`, explicit keys are removed. Savings: 15-20% of tokens.
16. **Atomicity via micro-glossary.** Frequent terms are tokenized as 1-3 character sigils. Additional savings: 30-40%.
17. **English as the base language of `.cortex`.** Structural in English. Semantic in domain language. HCORTEX in user language.
18. **Multi-actor identity.** `brain.cortex` supports multiple actors: `IDN:human{...}`, `IDN:agent{...}`, or custom roles. Each actor has its own entry. As many as needed.
19. **Multiple operational states.** `FCS`, `OBJ`, and `WRK` support multiple named entries (`:primary`, `:secondary`, custom). Each represents an independent focus, goal, or work stream.

---

## Validation Cycle

### Pipeline

```puml
@startuml
title CODEC-CORTEX Pipeline

rectangle ".cortex" as cortex
rectangle "AST (dict)" as ast
rectangle "YAML-Edit" as yaml
rectangle "PUML" as puml
rectangle "HCORTEX" as hc
rectangle "User" as user

cortex --> ast : decode()
ast --> yaml : ast_a_yaml_edit()
ast --> puml : ast_a_puml()
ast --> hc : decode(format=hcortex)
yaml --> ast : encode()
ast --> cortex : ast_a_cortex()
cortex --> ast : verify() deep-compare
hc --> user : tables, lists, K/V, PUML
note right of hc : Human-readable output.\nNo proprietary format.
@enduml
```

The validation cycle guarantees **100% reversibility**: `verify(input, encode(decode(input)))` must return `True`. If not, there is a bug in the parser or compiler.

### Key Functions

| Function | Input | Output | Purpose |
|---------|---------|--------|-----------|
| `cortex_a_ast()` | `.cortex` content (str) | `{ast, glossary, meta}` | Parse .cortex to AST |
| `ast_a_yaml_edit()` | AST (dict) | YAML-Edit (str) | Convert AST to readable format |
| `ast_a_puml()` | AST (dict) | PUML (str) | Extract PUML blocks |
| `ast_a_hcortex()` | AST (dict) | HCORTEX Markdown (str) | Decompress to human format |
| `yaml_edit_a_ast()` | YAML-Edit (str) | AST (dict) | Parse YAML-Edit to AST |
| `ast_a_cortex()` | AST (dict) | `.cortex` (str) | Compile AST to .cortex format |
| `verify()` | Original AST + new | `{ok: bool, diffs: [...]}` | Deep structural compare |

### CLI

| Command | Description |
|---------|-------------|
| `cortex decode <file>` | Decode .cortex to YAML-Edit |
| `cortex decode <file> --format hcortex` | Decode to HCORTEX markdown |
| `cortex encode <file>` | Encode context to .cortex |
| `cortex verify <file>` | Validate structure and glossary |
| `cortex patch_add <file> --section N --sigil S --name n --value v` | Add entry |
| `cortex patch_remove <file> --sigil S --name n` | Remove entry |
| `cortex patch_update <file> --sigil S --name n --value v` | Modify entry |
| `cortex glossary_add <file> --sigil S --expansion exp` | Add sigil to $0 |
| `cortex glossary_remove <file> --sigil S` | Remove sigil from $0 |
| `cortex glossary_update <file> --sigil S --expansion exp` | Modify sigil in $0 |
| `cortex diagram extract <file> --name N` | Extract PUML diagram |
| `cortex diagram list <file>` | List diagrams |
| `cortex diagram validate <file> --name N` | Validate PUML syntax |
| `cortex promote <file> --sigil S --name N` | Promote SES/LNG to KNW |
| `cortex detect <file>` | Detect recurring patterns |
| `cortex decay <file>` | Degrade KNW by disuse |

### Python API

```python
from codec_cortex import cortex_a_ast, ast_a_cortex, verify

# Decode
result = cortex_a_ast(content)
yaml_edit = ast_a_yaml_edit(result["ast"])

# Encode
new_ast = yaml_edit_a_ast(yaml_edit)
new_content = ast_a_cortex(new_ast)

# Verify (100% reversible)
r = verify(result["ast"], new_ast)
assert r["ok"]

# HCORTEX output
human = ast_a_hcortex(result["ast"])  # Markdown: tables, lists, K/V, diagrams
```

### Modules

| Module | Function |
|--------|---------|
| `cortex.patch` | `patch_add`, `patch_remove`, `patch_update` — entry mutation |
| `cortex.glossary` | `glossary_add`, `glossary_remove`, `glossary_update` — $0 management |
| `cortex.diagram` | `diagram_extract`, `diagram_list`, `diagram_validate` — PUML management |
| `cortex.maturity` | `detect_recurrence`, `promote`, `decay` — maturation engine |
| `cortex.hcortex` | `ast_a_hcortex` — decompression to human format |

---

## Performance Metrics

| Metric | Target | Method |
|---------|:-------:|--------|
| Compression vs prose | ≥85% | .cortex tokens / prose tokens |
| Compression vs dense prose (specs) | ≥70% | Measured with SKILL.md → SKILL.cortex |
| Reversibility | 100% | `verify(input, encode(decode(input)))` |
| Parse time | <50ms for 10KB | `timeit cortex_a_ast(content)` |
| Glossary lookup | O(log n) | Dict lookups with `$0` as index |
| Positional collapse | 15-20% | Reduction in handler sections |
| Micro-glossary | 30-40% additional | Reduction in repetitive values |
| Combined (collapse + micro) | 40-52% total | Both techniques applied |

---

## Memory Operational FSM

```puml
@startuml
title FSM — Ciclo de Vida de Memoria CORTEX

state IDLE : Agente inactivo
state INGEST : Ingestando historial
state COMPACT : Comprimiendo
state STORED : .cortex válido
state ACTIVE : AST en memoria
state WRK : Memoria de trabajo

[*] --> IDLE
IDLE --> INGEST : ingest($RAW_CONTEXT)
INGEST --> COMPACT : compress()
COMPACT --> STORED : verify() OK
STORED --> ACTIVE : decode()
ACTIVE --> WRK : extraer FCS+OBJ
WRK --> COMPACT : overflow (70% ventana)
note right of WRK : Guardia: FCS y OBJ\nrequeridos para operar
@enduml
```

**Fundamental rule:** The agent does not act without explicit `FCS` and `OBJ` in active working memory.

### Maturation FSM (Learning Cycle)

```puml
@startuml
title FSM de Maduración Cognitiva

state RAW : Datos crudos\n(sin clasificar)
state WRK : Memoria de trabajo\n(FCS + OBJ + WRK)
state SES_LNG : Episodios + Lecciones\n(experiencia comprimida)
state CANDIDATO : Patrón recurrente\ndetectado
state KNW : Conocimiento base\n(competencia inconsciente)
state ARCHIVE : Memoria archivada\n(latente)

RAW --> WRK : ingest()
WRK --> SES_LNG : compress()
SES_LNG --> CANDIDATO : detect_recurrence()
CANDIDATO --> KNW : promote() — usuario confirma
CANDIDATO --> SES_LNG : usuario rechaza
KNW --> SES_LNG : decay() >30 días
SES_LNG --> ARCHIVE : archivar si nunca usado

note right of CANDIDATO
  Umbral: N repeticiones.
  ask_user() decide.
  El contador pregunta.
  El usuario responde.
end note

note right of KNW
  Instantáneo.
  El LLM lo incorpora
  en la siguiente lectura.
  Sin práctica.
end note
@enduml
```

---

## Common Pitfalls

| # | Error | Cause | Solution |
|---|-------|-------|----------|
| 1 | `{` `}` unescaped | Special characters in values | `_extract_braces()` respects `\{` and `\}`. `BraceError` with line |
| 2 | Shallow deep compare | Compares strings, not tuples | `(sigil, name, json.dumps(value, sort_keys=True))` |
| 3 | Inconsistent sections | Parser does not accept `2`, `$2`, `2_NAME` | Normalize: extract only number |
| 4 | MCP bridge sync→async | Synchronous handlers, async registration | Wrapper with closure capture |
| 5 | $0 is not the first section | Glossary in incorrect position | Force $0 as initial section |
| 6 | REFs to directories | PATH points to folder, not file | `REF:name{PATH:path/file.cortex}` |
| 7 | Building .cortex by hand | Editing compiled format directly | Edit source YAML-Edit or use handlers |
| 8 | FCS and OBJ absent | Agent operates without focus or objective | Validate before every action |
| 9 | DIAG with invalid syntax | Malformed `@startuml` | `cortex diagram validate` |
| 10 | Textual deep compare of DIAG | Compares raw instead of structure | Compare participants and relations as sets |
| 11 | Modifying raw DIAG | Codec reformats content | DIAG is verbatim — preserve bit by bit |
| 12 | Micro-tokens in words | `parametro_d1` → `parametro_decodificar` | Expand only delimited |
| 13 | Incorrect positional collapse | 3 fields in 2-field `attrs-pos` | Degrade to explicit `attrs` |
| 14 | Language mixing | Structural tags in Spanish | Structural = English, semantic = domain |

---

## Verification Checklist

- [ ] `$0` (glossary) is the first section
- [ ] `FCS` and `OBJ` are present in active working memory
- [ ] `REFs` point to specific `.cortex` files
- [ ] No unescaped `{`/`}` in values
- [ ] `verify()` returns `{"ok": true}` after encode→decode
- [ ] Deep compare uses `json.dumps(value, sort_keys=True)`
- [ ] `DIAG` blocks have valid PUML syntax
- [ ] Deep compare of diagrams compares structure, not raw text
- [ ] Companion sigils share name with their DIAG
- [ ] The encode→decode→encode cycle does not modify raw DIAG
- [ ] Micro-tokens in $0 follow semantic nomenclature (d_, c_, v_, etc.)
- [ ] Parser only expands delimited micro-tokens
- [ ] `attrs-pos` handlers with correct number of fields
- [ ] Structural labels in English, semantic in domain
- [ ] Agent has migrated memory to `.cortex` and uses HCORTEX
- [ ] detect_recurrence scans SES and LNG
- [ ] promote only with human confirmation
- [ ] decay applied to KNW >30 days without use
- [ ] Exit GATE available for de-adoption
