Perfil: CORTEX-WORK
<!-- cortex-render: hcortex-read; roundtrip: false -->

# HCORTEX-READ

> Non-reversible human view. Profile: WORK (P-levels: P0, P1, P2). Mode: AUDIT. Layout: priority.

## Priority P0

<!-- section: $2 · CNST:output · P0 -->
### Constraint: output <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| rule | format: HCORTEX. tables_over_prose, puml_over_ascii, prose_as_last_resort | `CNST:output` |
| severity | blocking | `CNST:output` |
| survive | min | `CNST:output` |

<!-- section: $2 · CNST:language · P0 -->
### Constraint: language <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| rule | structural: EN, semantic: ES, output: ES | `CNST:language` |
| severity | blocking | `CNST:language` |
| survive | min | `CNST:language` |

<!-- section: $2 · CNST:re_completeness · P0 -->
### Constraint: re_completeness <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| rule | RE must be 100% complete (quality_contract, ACs, tasks, risks, procedure) before transitioning to open | `CNST:re_completeness` |
| severity | blocking | `CNST:re_completeness` |
| survive | min | `CNST:re_completeness` |

<!-- section: $2 · CNST:learning · P0 -->
### Constraint: learning <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| rule | knowledge matures by USER decision, not counters. promote requires human confirmation. detect_recurrence(threshold=3) -> ask_user -> promote/decay | `CNST:learning` |
| severity | blocking | `CNST:learning` |
| survive | min | `CNST:learning` |

<!-- section: $2 · CNST:cortex_rules · P0 -->
### Constraint: cortex_rules <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| rule | skills self-contained (no MCP, no external tools), structural EN + semantic ES, delete=degrade level (never wipe), GATE exit mandatory | `CNST:cortex_rules` |
| severity | blocking | `CNST:cortex_rules` |
| survive | min | `CNST:cortex_rules` |

<!-- section: $6 · !:output_format · P0 -->
### Rule: output_format <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| cond | always | `!:output_format` |
| acc | Tables > lists > K/V > PUML diagrams > prose. If information fits in a table, it IS a table. Prose is last resort | `!:output_format` |
| status | current | `!:output_format` |

<!-- section: $6 · !:communication · P0 -->
### Rule: communication <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| cond | always | `!:communication` |
| acc | LLM->human is structured, not prose. No ASCII art — PUML exclusively. Documentation without ASCII diagrams | `!:communication` |
| status | current | `!:communication` |

<!-- section: $6 · !:learning_model · P0 -->
### Rule: learning_model <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| cond | always | `!:learning_model` |
| acc | 4-stage cognitive model (unconscious incompetence -> unconscious competence) mapped to SES->LNG->KNW. Maturation: detect_recurrence(3) -> ask_user -> promote/decay | `!:learning_model` |
| status | current | `!:learning_model` |

<!-- section: $6 · !:hcortex_rules · P0 -->
### Rule: hcortex_rules <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| cond | always | `!:hcortex_rules` |
| acc | HCORTEX = decompression rules to standard .md, not an extension. brain.cortex = local brain. AGENTS.md = HCORTEX in user language | `!:hcortex_rules` |
| status | current | `!:hcortex_rules` |

<!-- section: $6 · !:no_model_mention · P0 -->
### Rule: no_model_mention <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| cond | always | `!:no_model_mention` |
| acc | Never mention the LLM model name. No 'running on DeepSeek', 'as a Claude model', etc | `!:no_model_mention` |
| status | current | `!:no_model_mention` |

## Priority P1

<!-- section: $2 · CNST:publication · P1 -->
### Constraint: publication <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| rule | publication with authorship: AUTHORS, CITATION.cff, CODEOWNERS, SPDX, semver | `CNST:publication` |
| severity | warning | `CNST:publication` |
| survive | recovery | `CNST:publication` |

<!-- section: $3 · OBJ:primary · P1 -->
### Objective: primary <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| goal | v0.3.0 release: CLI integrado, .cortex canonicos, docs actualizadas | `OBJ:primary` |
| status | done | `OBJ:primary` |
| success | 17 comandos CLI, 222 tests, 3/3 .cortex cortex verify --strict OK | `OBJ:primary` |
| survive | recovery | `OBJ:primary` |

<!-- section: $9 · RSK:repo_divergence · P1 -->
### Risk: repo_divergence <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| risk | workspace repo and codec-cortex repo may diverge | `RSK:repo_divergence` |
| impact | low | `RSK:repo_divergence` |
| mitigation | codec-cortex has its own git remote; push from there | `RSK:repo_divergence` |
| status | current | `RSK:repo_divergence` |
| survive | recovery | `RSK:repo_divergence` |

<!-- section: $12 · AUD:encoding · P1 -->
### Audit: encoding <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| event | Memory encoding from Hermes persistent store + actualizacion v0.3.0 | `AUD:encoding` |
| evidence | FCS/OBJ/WRK actualizados. DOM version v0.3.0. SES cli_documentation y cortex_migration agregadas. | `AUD:encoding` |
| result | alfred-memory.cortex refleja estado v0.3.0 | `AUD:encoding` |
| date | 2026-06-27 | `AUD:encoding` |

<!-- section: $12 · AUD:session_state · P1 -->
### Audit: session_state <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| event | Session state snapshot v0.3.0 | `AUD:session_state` |
| evidence | CLI integrado, 3/3 .cortex canonicos, documentacion alineada | `AUD:session_state` |
| result | brain.cortex y alfred-memory.cortex sincronizados en v0.3.0 | `AUD:session_state` |
| date | 2026-06-27 | `AUD:session_state` |

## Priority P2

<!-- section: $1 · IDN:human · P2 -->
### Identity: human <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| name | Fidel Ernesto Lozada A. | `IDN:human` |
| role | Creator & Architect | `IDN:human` |
| academic | Systems Engineer / MSc. Management Sciences | `IDN:human` |
| github | FidelErnesto03 | `IDN:human` |
| email | fidelernesto@gmail.com | `IDN:human` |
| git_user | Fidel Lozada | `IDN:human` |
| git_email | fidel.lozada@vatrox.com | `IDN:human` |
| gh_auth | SSH | `IDN:human` |

<!-- section: $1 · IDN:agent · P2 -->
### Identity: agent <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| name | alfred | `IDN:agent` |
| role | Protocol implementation and documentation agent | `IDN:agent` |
| type | AI coding agent | `IDN:agent` |
| home | ~/.hermes/skills/ | `IDN:agent` |
| runtime | Hermes Agent | `IDN:agent` |

<!-- section: $1 · DOM:project · P2 -->
### Domain: project <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| area | CODEC-CORTEX — Cognitive Operational Retrieval & Execution Template | `DOM:project` |
| license | MIT | `DOM:project` |
| repo | github.com/FidelErnesto03/codec-cortex | `DOM:project` |
| version | v0.3.0 | `DOM:project` |
| dialect_cycle | CORTEX-CONSOLIDATION-001 | `DOM:project` |

<!-- section: $3 · FCS:primary · P2 -->
### Focus: primary <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| what | CODEC-CORTEX v0.3.0 — CLI v1.1.9 integrado en cli/. Documentacion completa actualizada. Todos los .cortex en formato canonico validado. | `FCS:primary` |
| priority | high | `FCS:primary` |
| status | current | `FCS:primary` |
| survive | work | `FCS:primary` |

<!-- section: $3 · OBJ:current · P2 -->
### Objective: current <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| goal | Release v0.3.0: commit + push + tag. Brain y alfred-memory sincronizados. | `OBJ:current` |
| status | current | `OBJ:current` |
| success | Tag v0.3.0 creado. CHANGELOG 0.3.0 publicado. | `OBJ:current` |
| survive | work | `OBJ:current` |

<!-- section: $3 · WRK:session · P2 -->
### Work State: session <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| phase | Release v0.3.0 completado | `WRK:session` |
| current | brain.cortex y alfred-memory.cortex actualizados a v0.3.0. Pendiente commit+tag. | `WRK:session` |
| blocked | false | `WRK:session` |
| survive | work | `WRK:session` |
| started | 2026-06-27 | `WRK:session` |

<!-- section: $3 · STP:next · P2 -->
### Next Step: next <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| action | Commit + tag v0.3.0 o esperar decision de namespace | `STP:next` |
| reason | Integracion completa. Brain cortex actualizado. | `STP:next` |
| owner | human | `STP:next` |
| status | current | `STP:next` |
| survive | work | `STP:next` |

<!-- section: $4 · KNW:dialect_workspace · P2 -->
### Knowledge: dialect_workspace <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | DIALECT Workspace | `KNW:dialect_workspace` |
| content | workspace_id: WORKSPACE. root: ~/Projects/workspace. dialect_version: 5.5. projects_governed: 12. projects_ungoverned: 24 | `KNW:dialect_workspace` |
| status | current | `KNW:dialect_workspace` |

<!-- section: $4 · KNW:project_cortex · P2 -->
### Knowledge: project_cortex <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | Project CODEC-CORTEX | `KNW:project_cortex` |
| content | project_id: CODEC-CORTEX. project_root: ~/Projects/workspace/CODEC-CORTEX. repo_path: ~/Projects/workspace/CODEC-CORTEX/codec-cortex/ | `KNW:project_cortex` |
| status | current | `KNW:project_cortex` |

<!-- section: $4 · KNW:prjf_convention · P2 -->
### Knowledge: prjf_convention <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | PRJF Convention | `KNW:prjf_convention` |
| content | origin must include CYCLE/RE-ID for traceability. r5: closed cycle -> verify PRJ_F of all REs -> archive in workbook -> clear $7+ | `KNW:prjf_convention` |
| status | current | `KNW:prjf_convention` |

<!-- section: $4 · KNW:workbook_format · P2 -->
### Knowledge: workbook_format <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | Workbook Format | `KNW:workbook_format` |
| content | location: CODEC-CORTEX/.project-control/workbook.md. format: compact machine-first (no prose). purpose: cross-session operational reference | `KNW:workbook_format` |
| status | current | `KNW:workbook_format` |

<!-- section: $5 · KNW:skill_hermes · P2 -->
### Knowledge: skill_hermes <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | Skill in Hermes | `KNW:skill_hermes` |
| content | name: codec-cortex. version: 0.2.3. location: ~/.hermes/skills/codec-cortex/. status: loaded and active | `KNW:skill_hermes` |
| status | current | `KNW:skill_hermes` |

<!-- section: $5 · KNW:skill_development · P2 -->
### Knowledge: skill_development <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | Skill Development | `KNW:skill_development` |
| content | name: codec-cortex-development. version: 1.0.0. location: ~/.hermes/skills/coding/. status: loaded | `KNW:skill_development` |
| status | current | `KNW:skill_development` |

<!-- section: $5 · KNW:dialect_support · P2 -->
### Knowledge: dialect_support <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | DIALECT Support | `KNW:dialect_support` |
| content | protocol: 2-phase diagnostico+reparacion. handlers: 96 handlers post-dlf_tool cleanup | `KNW:dialect_support` |
| status | current | `KNW:dialect_support` |

<!-- section: $5 · KNW:repo_state · P2 -->
### Knowledge: repo_state <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | Repository State | `KNW:repo_state` |
| content | commits: 5. tag: v0.2.0. files: 32. outstanding: PR Awesome-LLM #681 pending | `KNW:repo_state` |
| status | current | `KNW:repo_state` |

<!-- section: $8 · LNG:survival_core_direction · P2 -->
### Lesson: survival_core_direction <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | architectural_insight | `LNG:survival_core_direction` |
| cause | 12 premisas del arquitecto | `LNG:survival_core_direction` |
| lesson | CODEC-CORTEX must evolve from dense format to contextual survival system. When everything else is lost, FCS/OBJ/CNST/STP still survive | `LNG:survival_core_direction` |
| prevention | survive attribute in all critical sigils | `LNG:survival_core_direction` |

<!-- section: $8 · LNG:section7_means_use · P2 -->
### Lesson: section7_means_use <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | process | `LNG:section7_means_use` |
| cause | Confusion between design and execution | `LNG:section7_means_use` |
| lesson | Design operativo (§7) must show functional use of the deliverable in the project, NOT RE execution steps. Execution goes in §10 | `LNG:section7_means_use` |
| prevention | RE template with clear section boundaries | `LNG:section7_means_use` |

<!-- section: $8 · LNG:load_vs_degrade · P2 -->
### Lesson: load_vs_degrade <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | architecture | `LNG:load_vs_degrade` |
| cause | Discussion about load/degrade order | `LNG:load_vs_degrade` |
| lesson | Context loading: P0->P5 (priority first). Degradation: P5->P1 (least critical first). P0 never touched during degradation | `LNG:load_vs_degrade` |
| prevention | !survive_degrade and !survive_priority rules | `LNG:load_vs_degrade` |

<!-- section: $8 · LNG:no_release_without_parser · P2 -->
### Lesson: no_release_without_parser <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | process | `LNG:no_release_without_parser` |
| cause | Impulse to tag before implementation exists | `LNG:no_release_without_parser` |
| lesson | Do not tag v0.3.0-spec before parser or automated benchmark exists. CHANGELOG uses [Unreleased] | `LNG:no_release_without_parser` |
| prevention | Pre-release checklist in workbook | `LNG:no_release_without_parser` |

<!-- section: $9 · RSK:awesome_pr_stale · P2 -->
### Risk: awesome_pr_stale <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| risk | PR Awesome-LLM #681 may go stale without follow-up | `RSK:awesome_pr_stale` |
| impact | medium | `RSK:awesome_pr_stale` |
| mitigation | monitor and update PR if needed | `RSK:awesome_pr_stale` |
| status | current | `RSK:awesome_pr_stale` |
| survive | work | `RSK:awesome_pr_stale` |

<!-- section: $10 · CLAIM:survival_core_status · P2 -->
### Claim: survival_core_status <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| statement | RE-004, RE-005, RE-006 are in open status with quality_contract 10/10 and zero DRAFT items | `CLAIM:survival_core_status` |
| evidence | DIALECT MCP confirms all 3 REs in open with valid state transitions | `CLAIM:survival_core_status` |
| status | current | `CLAIM:survival_core_status` |

<!-- section: $10 · CLAIM:cortex_adopted · P2 -->
### Claim: cortex_adopted <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| statement | CODEC-CORTEX is the active memory format for this session | `CLAIM:cortex_adopted` |
| evidence | brain.cortex updated, alfred-memory.cortex created, HCORTEX output active | `CLAIM:cortex_adopted` |
| status | current | `CLAIM:cortex_adopted` |

<!-- section: $10 · LIM:parser_gap · P2 -->
### Limit: parser_gap <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| limit | survive and P0-P5 rules are applied manually by instruction, not by automation. Parser is planned, not implemented | `LIM:parser_gap` |
| scope | current pre-codec phase | `LIM:parser_gap` |
| status | current | `LIM:parser_gap` |

<!-- section: $10 · LIM:benchmark_gap · P2 -->
### Limit: benchmark_gap <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| limit | survival benchmarks 0.1/0.1b/0.2 are offline/proxy artifacts. Automated benchmark methodology requires parser | `LIM:benchmark_gap` |
| scope | current pre-codec phase | `LIM:benchmark_gap` |
| status | current | `LIM:benchmark_gap` |

## Omissions by profile

The following entries were omitted by profile **WORK** (allowed P-levels: P0, P1, P2):

| section | sigil | name | plevel | reason |
| --- | --- | --- | --- | --- |
| $1 | TAG | memory | P5 | excluded by profile WORK |
| $7 | SES | dialect_bootstrap | P3 | excluded by profile WORK |
| $7 | SES | cortex_foundation | P3 | excluded by profile WORK |
| $7 | SES | survival_core | P3 | excluded by profile WORK |
| $7 | SES | brain_update | P3 | excluded by profile WORK |
| $7 | SES | hcortex_corrections | P3 | excluded by profile WORK |
| $7 | SES | recovery_res | P3 | excluded by profile WORK |
| $7 | SES | cli_documentation | P3 | excluded by profile WORK |
| $7 | SES | cortex_migration | P3 | excluded by profile WORK |
| $11 | REF | workbook | P4 | excluded by profile WORK |
| $11 | REF | brain | P4 | excluded by profile WORK |
| $11 | REF | skill | P4 | excluded by profile WORK |
| $11 | REF | repo | P4 | excluded by profile WORK |
