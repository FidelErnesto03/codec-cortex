Perfil: CORTEX-WORK
<!-- cortex-render: hcortex-read; roundtrip: false -->

# HCORTEX-READ

> Non-reversible human view. Profile: WORK (P-levels: P0, P1, P2). Mode: AUDIT. Layout: priority.

## Priority P0

<!-- section: $2 · CNST:honesty · P0 -->
### Constraint: honesty <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| rule | current/planned/future must remain explicit; no unsupported metrics or implementation claims | `CNST:honesty` |
| severity | blocking | `CNST:honesty` |
| survive | min | `CNST:honesty` |

<!-- section: $2 · OBJ:primary · P0 -->
### Objective: primary <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| goal | Ejecutar y aprobar las 6 correcciones HCORTEX (D-01 a D-06) | `OBJ:primary` |
| status | done | `OBJ:primary` |
| success | 13/13 REs approved. 5 reglas en $4, 8 pasos en $10 | `OBJ:primary` |
| survive | min | `OBJ:primary` |

<!-- section: $2 · STP:next · P0 -->
### Next Step: next <sub>[P0]</sub>

| key | value | source |
| --- | --- | --- |
| action | Explorar casos de uso del CLI: verify, render, doctor en .cortex del proyecto | `STP:next` |
| reason | v0.3.0 liberado. Skill local actualizado. Comenzar operacion con el nuevo release. | `STP:next` |
| owner | agent | `STP:next` |
| status | current | `STP:next` |
| survive | min | `STP:next` |

## Priority P1

<!-- section: $2 · OBJ:secondary · P1 -->
### Objective: secondary <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| goal | Integrar CLI v1.1.9 en codec-cortex/cli/ y migrar .cortex a formato canonico para v0.3.0 | `OBJ:secondary` |
| status | done | `OBJ:secondary` |
| success | CLI instalado, 222 tests, 3/3 .cortex migrados y validados con cortex verify --strict | `OBJ:secondary` |
| survive | recovery | `OBJ:secondary` |

<!-- section: $6 · RSK:premature_release · P1 -->
### Risk: premature_release <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| risk | Crear release v0.3.0-spec antes de tener parser o benchmark automatizado | `RSK:premature_release` |
| impact | medium | `RSK:premature_release` |
| mitigation | v0.3.0 como MINOR legitimo: agrega CLI funcional con 222 tests. Survival Core es specification draft documentado como tal | `RSK:premature_release` |
| status | current | `RSK:premature_release` |
| survive | recovery | `RSK:premature_release` |

<!-- section: $6 · RSK:glossary_divergence · P1 -->
### Risk: glossary_divergence <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| risk | brain.cortex y SKILL.cortex $0 pueden divergir nuevamente con nuevos sigilos | `RSK:glossary_divergence` |
| impact | medium | `RSK:glossary_divergence` |
| mitigation | cortex verify compara $0 de cada .cortex contra el glosario canonico de SKILL.cortex. RE-004 establece SKILL.cortex $0 como fuente canonica | `RSK:glossary_divergence` |
| status | current | `RSK:glossary_divergence` |
| survive | recovery | `RSK:glossary_divergence` |

<!-- section: $10 · AUD:last_release · P1 -->
### Audit: last_release <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| event | Release v0.2.3 | `AUD:last_release` |
| evidence | git tag v0.2.3 pushed, GitHub release created, CHANGELOG updated | `AUD:last_release` |
| result | Published on github.com/FidelErnesto03/codec-cortex | `AUD:last_release` |
| date | 2026-06-24 | `AUD:last_release` |

<!-- section: $10 · AUD:session_outcome · P1 -->
### Audit: session_outcome <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| event | Survival Core refinement + HCORTEX corrections session | `AUD:session_outcome` |
| evidence | 13 REs approved (RE-004 through RE-013), quality_contract 10/10 on all, zero DRAFT, PUML validated | `AUD:session_outcome` |
| result | v0.2.3 released. 5 hcortex rules in $4, 8 render steps in $10. Skill migrated to Hermes+DIALECT | `AUD:session_outcome` |
| date | 2026-06-24 | `AUD:session_outcome` |

<!-- section: $10 · AUD:brain_currentness · P1 -->
### Audit: brain_currentness <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| event | brain.cortex audit | `AUD:brain_currentness` |
| evidence | Checked all sigils, contracts, survive levels. New sigils: RSK/NXT/CLAIM/LIM. Contracts applied: FCS/OBJ/CNST/STP/WRK | `AUD:brain_currentness` |
| result | brain.cortex reflects complete cycle state post-RE-013 | `AUD:brain_currentness` |
| date | 2026-06-24 | `AUD:brain_currentness` |

<!-- section: $10 · AUD:cli_integration · P1 -->
### Audit: cli_integration <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| event | CLI v1.1.9 integration | `AUD:cli_integration` |
| evidence | codec-cortex-1.1.9.tar.gz extracted to cli/. 222 tests pass. 17 CLI commands functional. | `AUD:cli_integration` |
| result | CLI instalado y funcional. brain.cortex migrado a formato canonico. | `AUD:cli_integration` |
| date | 2026-06-27 | `AUD:cli_integration` |

<!-- section: $10 · AUD:docs_update · P1 -->
### Audit: docs_update <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| event | Documentacion completa v0.3.0 | `AUD:docs_update` |
| evidence | README v0.3.0/beta, CHANGELOG seccion 0.3.0, STATUS actualizado, ROADMAP Phase 4 current. brain.md/alfred-memory.md regenerados. summary.md actualizado. | `AUD:docs_update` |
| result | Documentacion alineada con CLI v1.1.9 y v0.3.0 | `AUD:docs_update` |
| date | 2026-06-27 | `AUD:docs_update` |

<!-- section: $10 · AUD:cortex_migration · P1 -->
### Audit: cortex_migration <sub>[P1]</sub>

| key | value | source |
| --- | --- | --- |
| event | Migracion de .cortex a formato canonico | `AUD:cortex_migration` |
| evidence | brain.cortex, SKILL.cortex, alfred-memory.cortex migrados. cortex verify --strict pasa en los 3 con 0 errores. | `AUD:cortex_migration` |
| result | Todos los .cortex del proyecto en formato canonico $N: headers | `AUD:cortex_migration` |
| date | 2026-06-27 | `AUD:cortex_migration` |

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

<!-- section: $1 · IDN:agent · P2 -->
### Identity: agent <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| name | alfred | `IDN:agent` |
| role | Protocol implementation and documentation agent | `IDN:agent` |
| type | AI coding agent | `IDN:agent` |

<!-- section: $1 · DOM:project · P2 -->
### Domain: project <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| area | CODEC-CORTEX | `DOM:project` |
| protocol | cognitive_memory | `DOM:project` |
| artifact | brain.cortex | `DOM:project` |
| version | 0.3.0 | `DOM:project` |
| repo | github.com/FidelErnesto03/codec-cortex | `DOM:project` |

<!-- section: $2 · CNST:output_format · P2 -->
### Constraint: output_format <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| rule | Output in HCORTEX format: tables > lists > K/V > diagrams > prose. User language: ES. Structural: EN. Canonical memory: .cortex | `CNST:output_format` |
| severity | warning | `CNST:output_format` |
| survive | work | `CNST:output_format` |

<!-- section: $2 · FCS:primary · P2 -->
### Focus: primary <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| what | Operando con v0.3.0. CLI v1.1.9 integrado. Skill local actualizado a v1.2.0. Todos los .cortex en formato canonico. | `FCS:primary` |
| priority | high | `FCS:primary` |
| status | current | `FCS:primary` |
| survive | work | `FCS:primary` |

<!-- section: $2 · FCS:secondary · P2 -->
### Focus: secondary <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| what | Ciclo CORTEX-CONSOLIDATION-001 completado. Release v0.3.0 publicada en GitHub. | `FCS:secondary` |
| priority | medium | `FCS:secondary` |
| status | current | `FCS:secondary` |
| survive | work | `FCS:secondary` |

<!-- section: $2 · OBJ:release · P2 -->
### Objective: release <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| goal | Release v0.3.0: commit + push + tag en main. Namespace decision pasada. | `OBJ:release` |
| status | done | `OBJ:release` |
| success | Tag v0.3.0 en GitHub. Release notes publicadas. CHANGELOG actualizado. | `OBJ:release` |
| survive | work | `OBJ:release` |

<!-- section: $2 · OBJ:operate · P2 -->
### Objective: operate <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| goal | Operar con v0.3.0. Explorar casos de uso del CLI, tests de roundtrip, benchmarks automatizados. | `OBJ:operate` |
| status | current | `OBJ:operate` |
| success | CLI probado con .cortex reales. Proximo release planeado. | `OBJ:operate` |
| survive | work | `OBJ:operate` |

<!-- section: $2 · WRK:state · P2 -->
### Work State: state <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| phase | Operacion v0.3.0 | `WRK:state` |
| current | Skill local actualizado. Brain.cortex sincronizado. CLI funcional en cli/. | `WRK:state` |
| blocked | false | `WRK:state` |
| survive | work | `WRK:state` |
| active_files | brain.cortex, skill/SKILL.cortex, cli/ | `WRK:state` |

<!-- section: $2 · WRK:repo · P2 -->
### Work State: repo <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| phase | active | `WRK:repo` |
| current | main branch v0.3.0. Tag v0.3.0 en GitHub. CLI v1.1.9 en cli/. | `WRK:repo` |
| blocked | false | `WRK:repo` |
| survive | work | `WRK:repo` |

<!-- section: $4 · LNG:survival_core_emerged · P2 -->
### Lesson: survival_core_emerged <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | architectural_insight | `LNG:survival_core_emerged` |
| cause | 12 premisas del arquitecto durante sesion de refinamiento | `LNG:survival_core_emerged` |
| lesson | CODEC-CORTEX reorientado de formato denso a sistema de supervivencia contextual. Cuando todo lo demas se pierde, todavia sobreviven FCS, OBJ, CNST, STP | `LNG:survival_core_emerged` |
| prevention | Incorporar survive como atributo de primer orden en todos los sigilos criticos | `LNG:survival_core_emerged` |

<!-- section: $4 · LNG:re_before_code · P2 -->
### Lesson: re_before_code <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | process | `LNG:re_before_code` |
| cause | Impulso de implementar parser antes de tener REs refinadas | `LNG:re_before_code` |
| lesson | No escribir codigo ni parser antes de tener las REs refinadas y aprobadas. La especificacion gobierna la implementacion | `LNG:re_before_code` |
| prevention | Gate de REs en open con quality_contract 10/10 antes de cualquier codigo | `LNG:re_before_code` |

<!-- section: $4 · LNG:section7_means_use · P2 -->
### Lesson: section7_means_use <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | documentation | `LNG:section7_means_use` |
| cause | Confusion entre diseno operativo y pasos de ejecucion | `LNG:section7_means_use` |
| lesson | Diseno operativo (§7) debe mostrar uso funcional del entregable en el proyecto, no pasos de ejecucion de la RE. Ejecucion va en §10 | `LNG:section7_means_use` |
| prevention | Template de RE con secciones claramente delimitadas | `LNG:section7_means_use` |

<!-- section: $4 · LNG:load_vs_degrade · P2 -->
### Lesson: load_vs_degrade <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | architecture | `LNG:load_vs_degrade` |
| cause | Discusion sobre orden de carga/descarga de contexto | `LNG:load_vs_degrade` |
| lesson | Carga de contexto: P0->P5 (prioridad primero). Degradacion: P5->P1 (lo menos critico primero). P0 nunca se toca en degradacion | `LNG:load_vs_degrade` |
| prevention | Reglas !survive_degrade y !survive_priority en SKILL.cortex | `LNG:load_vs_degrade` |

<!-- section: $4 · LNG:skill_first · P2 -->
### Lesson: skill_first <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | messaging | `LNG:skill_first` |
| cause | Narrativa publica inicial enfatizaba compresion sobre memoria | `LNG:skill_first` |
| lesson | CODEC-CORTEX public narrative must open with Universal Skill and contextual memory protocol, not codec-first compression | `LNG:skill_first` |
| prevention | README y SKILL.md abren con Skill universal, no con codec | `LNG:skill_first` |

<!-- section: $4 · LNG:status_honesty · P2 -->
### Lesson: status_honesty <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | messaging | `LNG:status_honesty` |
| cause | Tentacion de declarar capacidades como actuales cuando son planned | `LNG:status_honesty` |
| lesson | Every capability must be current/specification/planned/future when maturity matters | `LNG:status_honesty` |
| prevention | STATUS.md como truth registry con columnas explicitas de madurez | `LNG:status_honesty` |

<!-- section: $4 · LNG:benchmark_integrity · P2 -->
### Lesson: benchmark_integrity <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | quality | `LNG:benchmark_integrity` |
| cause | Claims de densidad sin benchmarks reproducibles | `LNG:benchmark_integrity` |
| lesson | Numeric density or performance claims require reproducible benchmarks before public measured language | `LNG:benchmark_integrity` |
| prevention | Benchmarks automatizados con cortex benchmark antes de cualquier claim numerico | `LNG:benchmark_integrity` |

<!-- section: $4 · LNG:hcortex_deviations · P2 -->
### Lesson: hcortex_deviations <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | implementation | `LNG:hcortex_deviations` |
| cause | Conversion manual .cortex->HCORTEX sin parser | `LNG:hcortex_deviations` |
| lesson | La conversion .cortex->HCORTEX tiene 6 desviaciones sistematicas: sin perfil, sin trazabilidad, multi-instancia aplanada, sin estrategia por tipo, DIAG sin caption, sin orden P0->P5. Todas corregibles hoy sin parser | `LNG:hcortex_deviations` |
| prevention | 10-step HCORTEX render protocol en SKILL.cortex $10 | `LNG:hcortex_deviations` |

<!-- section: $4 · LNG:default_profile_by_mode · P2 -->
### Lesson: default_profile_by_mode <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | configuration | `LNG:default_profile_by_mode` |
| cause | Agente improvisando perfil ante conflicto modo vs presupuesto | `LNG:default_profile_by_mode` |
| lesson | Sin perfil declarado, el default depende del modo: auditoria->FULL, recovery->RECOVERY, trabajo->WORK, emergencia->MIN | `LNG:default_profile_by_mode` |
| prevention | Regla !hcortex_profile con precedencia: explicito > presupuesto > modo > WORK | `LNG:default_profile_by_mode` |

<!-- section: $4 · LNG:precedence_over_budget · P2 -->
### Lesson: precedence_over_budget <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | configuration | `LNG:precedence_over_budget` |
| cause | Conflicto entre modo auditoria y presupuesto bajo | `LNG:precedence_over_budget` |
| lesson | Si auditoria requiere FULL y el presupuesto no alcanza, no degradar silenciosamente — declarar segmentado | `LNG:precedence_over_budget` |
| prevention | HCORTEX segmentado con Segmento: <n>/<total> | `LNG:precedence_over_budget` |

<!-- section: $4 · LNG:entries_without_priority · P2 -->
### Lesson: entries_without_priority <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | architecture | `LNG:entries_without_priority` |
| cause | Asumir que toda entrada es P0 por defecto | `LNG:entries_without_priority` |
| lesson | Entradas .cortex sin P-level ni survive deben tratarse como P5 (incluidas solo en CORTEX-FULL) | `LNG:entries_without_priority` |
| prevention | Regla !p5_filter en SKILL.cortex | `LNG:entries_without_priority` |

<!-- section: $4 · LNG:source_column_cost_justified · P2 -->
### Lesson: source_column_cost_justified <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | tradeoff | `LNG:source_column_cost_justified` |
| cause | Preocupacion por overhead de tokens de columna source | `LNG:source_column_cost_justified` |
| lesson | La columna source en HCORTEX agrega ~10-15% de tokens, pero en MIN el overhead es minimo porque solo hay P0. El costo se justifica por auditabilidad | `LNG:source_column_cost_justified` |
| prevention | Columna source obligatoria en P0/P1 en modo auditoria | `LNG:source_column_cost_justified` |

<!-- section: $4 · LNG:expansion_type_defines_render · P2 -->
### Lesson: expansion_type_defines_render <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | implementation | `LNG:expansion_type_defines_render` |
| cause | Renderizar reglas (!) como tablas K/V genericas | `LNG:expansion_type_defines_render` |
| lesson | El tipo de expansion no es metadata decorativa — define la estrategia de render. Una regla (!, tipo cuerpo) no debe renderizarse como tabla K/V | `LNG:expansion_type_defines_render` |
| prevention | HCORTEX render strategy por tipo: attrs->tabla, cuerpo->quote, bloque->PUML | `LNG:expansion_type_defines_render` |

<!-- section: $4 · LNG:render_order_by_priority · P2 -->
### Lesson: render_order_by_priority <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | implementation | `LNG:render_order_by_priority` |
| cause | Ordenar HCORTEX por numero de seccion del .cortex fuente | `LNG:render_order_by_priority` |
| lesson | Las secciones HCORTEX deben ordenarse por prioridad cognitiva (P0->P5), no por numero de seccion del .cortex fuente | `LNG:render_order_by_priority` |
| prevention | Regla !hcortex_order: P0 primero, P5 ultimo | `LNG:render_order_by_priority` |

<!-- section: $4 · LNG:gov_isolation_mandatory · P2 -->
### Lesson: gov_isolation_mandatory <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | security | `LNG:gov_isolation_mandatory` |
| cause | Referencias de gobierno (RE-IDs, nombres de ciclo) en documentos publicos | `LNG:gov_isolation_mandatory` |
| lesson | Ningun documento publico del proyecto debe contener referencias de gobierno. Violacion: strip antes de push | `LNG:gov_isolation_mandatory` |
| prevention | Regla !gov_isolation en workbook. Pre-push grep check | `LNG:gov_isolation_mandatory` |

<!-- section: $4 · LNG:cortex_md_sync · P2 -->
### Lesson: cortex_md_sync <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | process | `LNG:cortex_md_sync` |
| cause | brain.cortex existia sin brain.md correspondiente | `LNG:cortex_md_sync` |
| lesson | Todo archivo .cortex con estado operativo debe tener su correspondiente .md HCORTEX sincronizado. El .md es la vista legible humana del .cortex | `LNG:cortex_md_sync` |
| prevention | cortex render brain.cortex -> brain.md automatico | `LNG:cortex_md_sync` |

<!-- section: $4 · LNG:version_centralization · P2 -->
### Lesson: version_centralization <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| type | process | `LNG:version_centralization` |
| cause | Versiones divergentes entre superficies (SKILL.cortex vs pyproject.toml vs brain.cortex) | `LNG:version_centralization` |
| lesson | Version unica para todas las superficies. SKILL no tiene version independiente — hereda la del proyecto | `LNG:version_centralization` |
| prevention | grep -rn version_string antes de cada tag | `LNG:version_centralization` |

<!-- section: $5 · KNW:survival_core · P2 -->
### Knowledge: survival_core <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | Survival Core Architecture | `KNW:survival_core` |
| content | RE-004: nucleo minimo — survive + 6 sigilos + 5 contratos. RE-005: priority pack P0-P5 + perfiles + degradacion. RE-006: 2 specs + 5 reglas Skill. RE-007: 6 desviaciones HCORTEX corregibles | `KNW:survival_core` |
| status | current | `KNW:survival_core` |

<!-- section: $5 · KNW:survival_sigils · P2 -->
### Knowledge: survival_sigils <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | Survival Sigils Inventory | `KNW:survival_sigils` |
| content | new: STP/AUD/RSK/NXT/CLAIM/LIM. postponed: FIND/IMP/VAL/RES/DOC/ART/TBL. contracts: FCS/OBJ/CNST/STP/WRK. survive_levels: min/recovery/work/full | `KNW:survival_sigils` |
| status | current | `KNW:survival_sigils` |

<!-- section: $5 · KNW:priority_pack · P2 -->
### Knowledge: priority_pack <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | Priority Pack P0-P5 | `KNW:priority_pack` |
| content | P0: FCS/OBJ/CNST/STP. P1: WRK/AUD/RSK/NXT. P2: CLAIM/LIM/KNW:active/LNG:critical. load_order: P0->P5. degrade_order: P5->P1 | `KNW:priority_pack` |
| status | current | `KNW:priority_pack` |

<!-- section: $5 · KNW:canonical_stack · P2 -->
### Knowledge: canonical_stack <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | CODEC-CORTEX Canonical Stack | `KNW:canonical_stack` |
| content | order: Universal Skill -> .cortex contextual memory -> HCORTEX human view -> deterministic codec planned -> memory runtime future -> enterprise MCP future | `KNW:canonical_stack` |
| status | current | `KNW:canonical_stack` |

<!-- section: $5 · KNW:release · P2 -->
### Knowledge: release <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | Release History | `KNW:release` |
| content | version: 0.2.3, tag: v0.2.3, previous: v0.2.2, next: 0.3.0, type: PATCH (HCORTEX views sync + docs alignment + recovery REs drafted) | `KNW:release` |
| status | current | `KNW:release` |

<!-- section: $5 · KNW:paths · P2 -->
### Knowledge: paths <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | Project Paths | `KNW:paths` |
| content | repo: ~/Projects/workspace/CODEC-CORTEX/codec-cortex/, public: github.com/FidelErnesto03/codec-cortex, cli: cli/ | `KNW:paths` |
| status | current | `KNW:paths` |

<!-- section: $5 · KNW:compression_rules · P2 -->
### Knowledge: compression_rules <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | HCORTEX Compression Rules | `KNW:compression_rules` |
| content | hcortex_compact: !hcortex_profile, !hcortex_source, !hcortex_multi, !hcortex_expand, !hcortex_order. survive_rules: !survive_priority, !survive_degrade, !survive_status. filter: !p5_filter | `KNW:compression_rules` |
| status | current | `KNW:compression_rules` |

<!-- section: $5 · KNW:skill_architecture_knowledge · P2 -->
### Knowledge: skill_architecture_knowledge <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | SKILL Architecture Knowledge | `KNW:skill_architecture_knowledge` |
| content | 6-layer stack: Skill->.cortex->HCORTEX->Codec->Runtime->MCP. .cortex tiene survive P0-P5 + attrs-pos + 10-step HCORTEX | `KNW:skill_architecture_knowledge` |
| status | current | `KNW:skill_architecture_knowledge` |

<!-- section: $5 · KNW:degradation_flow_knowledge · P2 -->
### Knowledge: degradation_flow_knowledge <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| topic | Degradation Flow Knowledge | `KNW:degradation_flow_knowledge` |
| content | Degradacion FULL->MIN: drop P5->P4->P3 en WORK, keep KNW:LNG activos, solo P0 en MIN. CNST:blocking nunca desaparece. Bidireccional en recuperacion | `KNW:degradation_flow_knowledge` |
| status | current | `KNW:degradation_flow_knowledge` |

<!-- section: $6 · RSK:profile_ambiguity · P2 -->
### Risk: profile_ambiguity <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| risk | Perfiles conceptuales sin listas cerradas pueden ser ambiguos para agentes | `RSK:profile_ambiguity` |
| impact | low | `RSK:profile_ambiguity` |
| mitigation | Los perfiles son criterios de prioridad, no inventarios. Se refinan con benchmarks | `RSK:profile_ambiguity` |
| status | current | `RSK:profile_ambiguity` |
| survive | work | `RSK:profile_ambiguity` |

<!-- section: $7 · NXT:approve_res · P2 -->
### Queued Action: approve_res <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| action | Fidel revisa y aprueba RE-004, RE-005, RE-006 | `NXT:approve_res` |
| priority | high | `NXT:approve_res` |
| trigger | after_execution | `NXT:approve_res` |
| status | done | `NXT:approve_res` |
| survive | work | `NXT:approve_res` |

<!-- section: $7 · NXT:execute_res · P2 -->
### Queued Action: execute_res <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| action | Ejecutar RE-004 (modificar SKILL.cortex) | `NXT:execute_res` |
| priority | high | `NXT:execute_res` |
| trigger | after_approval | `NXT:execute_res` |
| status | done | `NXT:execute_res` |
| depends_on | NXT:approve_res | `NXT:execute_res` |
| survive | work | `NXT:execute_res` |

<!-- section: $7 · NXT:execute_re5 · P2 -->
### Queued Action: execute_re5 <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| action | Ejecutar RE-005 (agregar P0-P5 y perfiles a SKILL.cortex) | `NXT:execute_re5` |
| priority | high | `NXT:execute_re5` |
| trigger | after_RE004_done | `NXT:execute_re5` |
| status | done | `NXT:execute_re5` |
| depends_on | NXT:execute_res | `NXT:execute_re5` |
| survive | work | `NXT:execute_re5` |

<!-- section: $7 · NXT:execute_re6 · P2 -->
### Queued Action: execute_re6 <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| action | Ejecutar RE-006 (crear specs + reglas Skill) | `NXT:execute_re6` |
| priority | high | `NXT:execute_re6` |
| trigger | after_RE005_done | `NXT:execute_re6` |
| status | done | `NXT:execute_re6` |
| depends_on | NXT:execute_re5 | `NXT:execute_re6` |
| survive | work | `NXT:execute_re6` |

<!-- section: $7 · NXT:review_re007 · P2 -->
### Queued Action: review_re007 <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| action | Fidel revisa RE-007 y decide correcciones de conversion HCORTEX | `NXT:review_re007` |
| priority | high | `NXT:review_re007` |
| trigger | after_diagnosis | `NXT:review_re007` |
| status | done | `NXT:review_re007` |
| survive | work | `NXT:review_re007` |

<!-- section: $7 · NXT:migrate_cortex_files · P2 -->
### Queued Action: migrate_cortex_files <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| action | Migrar brain.cortex + SKILL.cortex + alfred-memory.cortex a formato canonico con $N: headers | `NXT:migrate_cortex_files` |
| priority | high | `NXT:migrate_cortex_files` |
| trigger | now | `NXT:migrate_cortex_files` |
| status | done | `NXT:migrate_cortex_files` |
| survive | work | `NXT:migrate_cortex_files` |

<!-- section: $7 · NXT:decide_namespace · P2 -->
### Queued Action: decide_namespace <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| action | Fidel decide namespace final del paquete CLI (cortex vs codec_cortex) | `NXT:decide_namespace` |
| priority | medium | `NXT:decide_namespace` |
| trigger | after_migration_validated | `NXT:decide_namespace` |
| status | done | `NXT:decide_namespace` |
| survive | work | `NXT:decide_namespace` |

<!-- section: $7 · NXT:release_v030 · P2 -->
### Queued Action: release_v030 <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| action | Commit + push + tag v0.3.0 en main | `NXT:release_v030` |
| priority | high | `NXT:release_v030` |
| trigger | after_docs_complete | `NXT:release_v030` |
| status | done | `NXT:release_v030` |
| survive | work | `NXT:release_v030` |

<!-- section: $7 · NXT:explore_cli · P2 -->
### Queued Action: explore_cli <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| action | Probar cortex verify, render, doctor en .cortex del proyecto | `NXT:explore_cli` |
| priority | medium | `NXT:explore_cli` |
| trigger | after_release | `NXT:explore_cli` |
| status | current | `NXT:explore_cli` |
| survive | work | `NXT:explore_cli` |

<!-- section: $8 · CLAIM:survival_core · P2 -->
### Claim: survival_core <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| statement | CODEC-CORTEX Survival Core esta especificado, ejecutado y liberado como v0.3.0 (MINOR). CLI v1.1.9 integrado con 222 tests. | `CLAIM:survival_core` |
| evidence | CLI en cli/. 3/3 .cortex validados. SKILL.md v1.2.0. CHANGELOG 0.3.0. | `CLAIM:survival_core` |
| status | current | `CLAIM:survival_core` |

<!-- section: $8 · CLAIM:release_v030 · P2 -->
### Claim: release_v030 <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| statement | v0.3.0 es un release MINOR legitimo bajo semver. Agrega CLI funcional con 17 comandos, parser determinista, verifier y renderer HCORTEX. | `CLAIM:release_v030` |
| evidence | CHANGELOG [0.3.0] con CLI integration. 222 tests pasan. cortex verify --strict pasa en todos los .cortex. | `CLAIM:release_v030` |
| status | current | `CLAIM:release_v030` |

<!-- section: $8 · LIM:parser_gap · P2 -->
### Limit: parser_gap <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| limit | Sin parser, las reglas P0-P5 y survive se aplican manualmente por instruccion, no por automatizacion | `LIM:parser_gap` |
| scope | fase actual pre-codec | `LIM:parser_gap` |
| status | current | `LIM:parser_gap` |

<!-- section: $8 · LIM:benchmark_gap · P2 -->
### Limit: benchmark_gap <sub>[P2]</sub>

| key | value | source |
| --- | --- | --- |
| limit | Los benchmarks 0.1/0.1b/0.2 son offline/proxy. La automatizacion requiere parser | `LIM:benchmark_gap` |
| scope | fase actual | `LIM:benchmark_gap` |
| status | current | `LIM:benchmark_gap` |

## Omissions by profile

The following entries were omitted by profile **WORK** (allowed P-levels: P0, P1, P2):

| section | sigil | name | plevel | reason |
| --- | --- | --- | --- | --- |
| $3 | SES | survival_core_refinement | P3 | excluded by profile WORK |
| $3 | SES | codec_cortex_adoption | P3 | excluded by profile WORK |
| $3 | SES | reorientation | P3 | excluded by profile WORK |
| $3 | SES | release_v020 | P3 | excluded by profile WORK |
| $3 | SES | execution_004_005_006 | P3 | excluded by profile WORK |
| $3 | SES | release_v021 | P3 | excluded by profile WORK |
| $3 | SES | skill_migration | P3 | excluded by profile WORK |
| $3 | SES | re007_diagnosis | P3 | excluded by profile WORK |
| $3 | SES | re007_approved | P3 | excluded by profile WORK |
| $3 | SES | hcortex_corrections | P3 | excluded by profile WORK |
| $3 | SES | cli_integration | P3 | excluded by profile WORK |
| $3 | SES | cli_documentation | P3 | excluded by profile WORK |
| $3 | SES | cortex_migration | P3 | excluded by profile WORK |
| $3 | SES | skill_update_v030 | P3 | excluded by profile WORK |
| $5 | DIAG | skill_architecture | P5 | excluded by profile WORK |
| $5 | DIAG | survival_degradation | P5 | excluded by profile WORK |
| $9 | REF | skill_cortex | P4 | excluded by profile WORK |
| $9 | REF | skill_md | P4 | excluded by profile WORK |
| $9 | REF | skill_en | P4 | excluded by profile WORK |
| $9 | REF | readme | P4 | excluded by profile WORK |
| $9 | REF | status | P4 | excluded by profile WORK |
| $9 | REF | roadmap | P4 | excluded by profile WORK |
| $9 | REF | changelog | P4 | excluded by profile WORK |
| $9 | REF | brain_md | P4 | excluded by profile WORK |
| $10 | TAG | brain | P5 | excluded by profile WORK |
