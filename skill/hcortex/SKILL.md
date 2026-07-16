<!-- CODEC-CORTEX
internal_encoding: HCORTEX
source_artifact: codec-cortex.skill.cortex
source_version: 2.0.0
status: specification
derived_from: codec-cortex.skill.cortex
reversible: true
view_schema: 1
view_coverage: 100
-->

**Perfil: CORTEX-FULL**

---

<!-- VIEW:sigils kind=table target="$0:canonical_sigils" reverse=rows_to_entries fields="sigil,name,type,risk,cortex,desc" title="Glosario de sigilos" status=cur -->
## Glosario de sigilos

| Sigilo | Nombre | Tipo | Riesgo | Corteza | Descripción |
|---|---|---|:---:|---|---|
| `IDN` | identity | `attrs` | B | Semantic | Identidad y versión del skill |
| `DOM` | domain | `attrs` | B | Semantic | Dominio y fronteras conceptuales |
| `KNW` | knowledge | `attrs` | B | Semantic | Conocimiento operativo verificable |
| `REF` | reference | `attrs` | B | Semantic | Referencia a fuente o artefacto |
| `CLAIM` | claim | `attrs` | M | Prefrontal | Afirmación de capacidad con evidencia |
| `CNST` | constraint | `attrs` | H | Prefrontal | Restricción no negociable |
| `LIM` | limit | `attrs` | H | Prefrontal | Límite o alcance explícito |
| `RSK` | risk | `attrs` | M | Prefrontal | Riesgo y mitigación |
| `AUD` | audit | `attrs` | M | Prefrontal | Evidencia de verificación |
| `PFL` | pitfall | `attrs` | M | Prefrontal | Antipatrón y prevención |
| `DEP` | dependency | `attrs` | M | Semantic | Componente y dependencia |
| `ERR` | error | `attrs` | M | Working | Código, causa y recuperación |
| `HDL` | handler | `attrs-pos` | M | Semantic | Operación CLI determinista |
| `POL` | policy | `attrs` | M | Prefrontal | Política del motor de aprendizaje |
| `THR` | threshold | `attrs` | M | Semantic | Umbrales deterministas |
| `GTE` | gate | `attrs` | H | Prefrontal | Gate de mutación o elevación |
| `PRT` | protected | `attrs` | H | Prefrontal | Objetivos protegidos |
| `VIEW` | view | `attrs` | M | Semantic | Contrato reversible CORTEX-HCORTEX |
| `!` | rule | `attrs` | H | Prefrontal | Regla compacta obligatoria |

<!-- /VIEW:sigils -->

<!-- VIEW:types kind=kv_table target="$0:type_decls" reverse=row_to_attrs title="Sistema de tipos" status=cur -->
## Sistema de tipos

**Source:** `$0:type_decls`

| Campo | Valor |
|---|---|
| attrs | key:value pairs; una línea canónica |
| attrs_pos | valores posicionales según contrato |
| cuerpo | texto semántico multilínea |
| bloque | contenido verbatim multilínea |
| relación | relación causal dirigida |

<!-- /VIEW:types -->

<!-- VIEW:contracts kind=table target="$0:contracts" reverse=rows_to_entries fields="sigil,pos" title="Contratos posicionales" status=cur -->
## Contratos posicionales

| Sigilo | Campos posicionales |
|---|---|
| `HDL` | operation\|status\|requires\|notes |

<!-- /VIEW:contracts -->

<!-- VIEW:microtokens kind=table target="$0:microtokens" reverse=rows_to_entries fields="token,expand" title="Microtokens" status=cur -->
## Microtokens

| Token | Expansión |
|---|---|
| `cur` | current |
| `pln` | planned |
| `fut` | future |
| `blk` | blocked |
| `min` | minimum |
| `rec` | recovery |
| `wrk` | work |
| `full` | full |
| `ok` | success |
| `fail` | failure |
| `part` | partial |

<!-- /VIEW:microtokens -->

<!-- VIEW:enum_state kind=kv_table target="$0:enum_state" reverse=row_to_attrs title="Estados" status=cur -->
## Estados

**Source:** `$0:enum_state`

| Campo | Valor |
|---|---|
| values | current\|planned\|future\|blocked\|done\|deprecated\|experimental\|specification |

<!-- /VIEW:enum_state -->

<!-- VIEW:enum_severity kind=kv_table target="$0:enum_severity" reverse=row_to_attrs title="Severidad" status=cur -->
## Severidad

**Source:** `$0:enum_severity`

| Campo | Valor |
|---|---|
| values | info\|warning\|blocking |

<!-- /VIEW:enum_severity -->

<!-- VIEW:enum_priority kind=kv_table target="$0:enum_priority" reverse=row_to_attrs title="Prioridad" status=cur -->
## Prioridad

**Source:** `$0:enum_priority`

| Campo | Valor |
|---|---|
| values | low\|medium\|high |

<!-- /VIEW:enum_priority -->

<!-- VIEW:enum_survive kind=kv_table target="$0:enum_survive" reverse=row_to_attrs title="Survive" status=cur -->
## Survive

**Source:** `$0:enum_survive`

| Campo | Valor |
|---|---|
| values | min\|recovery\|work\|full |

<!-- /VIEW:enum_survive -->

<!-- VIEW:enum_plevel kind=kv_table target="$0:enum_plevel" reverse=row_to_attrs title="P-levels" status=cur -->
## P-levels

**Source:** `$0:enum_plevel`

| Campo | Valor |
|---|---|
| values | P0\|P1\|P2\|P3\|P4\|P5 |

<!-- /VIEW:enum_plevel -->

<!-- VIEW:enum_mode kind=kv_table target="$0:enum_mode" reverse=row_to_attrs title="Modos" status=cur -->
## Modos

**Source:** `$0:enum_mode`

| Campo | Valor |
|---|---|
| values | read-only\|editor\|admin |

<!-- /VIEW:enum_mode -->

<!-- VIEW:enum_view_kind kind=kv_table target="$0:enum_view_kind" reverse=row_to_attrs title="VIEW kinds" status=cur -->
## VIEW kinds

**Source:** `$0:enum_view_kind`

| Campo | Valor |
|---|---|
| values | table\|kv_table\|matrix\|list\|numbered_list\|checklist\|prose\|quote\|puml\|code\|callout\|section\|raw |

<!-- /VIEW:enum_view_kind -->

<!-- VIEW:enum_reverse kind=kv_table target="$0:enum_reverse" reverse=row_to_attrs title="Reverse strategies" status=cur -->
## Reverse strategies

**Source:** `$0:enum_reverse`

| Campo | Valor |
|---|---|
| values | rows_to_entries\|row_to_attrs\|columns_to_attrs\|items_to_entries\|items_to_ordered_entries\|items_to_status_entries\|body_to_cuerpo\|verbatim_to_bloque\|callout_to_risk\|callout_to_limit\|preserve_human_block\|ignore_with_warning\|manual_review |

<!-- /VIEW:enum_reverse -->

<!-- VIEW:identity kind=kv_table target="$1:IDN:skill" reverse=row_to_attrs title="Identidad del skill" status=cur -->
## Identidad del skill

**Source:** `IDN:skill`

| Campo | Valor |
|---|---|
| name | CODEC-CORTEX Definitive Agent Skill |
| version | 2.0.0 |
| package_version | 0.3.7 |
| status | specification |
| nature | skill |
| language | es |
| authority | PyPI wheel codec_cortex-0.3.7 plus runtime behavior |

<!-- /VIEW:identity -->

<!-- VIEW:domain kind=kv_table target="$1:DOM:protocol" reverse=row_to_attrs title="Dominio" status=cur -->
## Dominio

**Source:** `DOM:protocol`

| Campo | Valor |
|---|---|
| area | Memoria contextual estructurada para agentes LLM/SLM |
| canonical | CORTEX |
| human_view | HCORTEX |
| conversational_output | CORTEX-OUT |
| execution | CLI determinista sin dependencia de LLM |
| scope | crear, validar, convertir, mutar, auditar y aprender |

<!-- /VIEW:domain -->

<!-- VIEW:sources kind=table target="$1:REF:*" reverse=rows_to_entries fields="path,role,version,status" title="Fuentes" status=cur -->
## Fuentes

| Source | Path | Role | Version | Status |
|---|---|---|---|---|
| `REF:pypi` | https://pypi.org/project/codec-cortex/ | distribución publicada | 0.3.7 | current |
| `REF:wheel` | codec_cortex-0.3.7-py3-none-any.whl | artefacto inspeccionado | sha256:b336464ad3b3279b69ce5fce0cc85dc0d0263a11d5cb5f452eea0d4b76cfd764 | current |
| `REF:repository` | github.com/FidelErnesto03/codec-cortex | repositorio oficial | tag:v0.3.7 | current |
| `REF:upstream_skill` | skill/cortex/SKILL.md | skill canónico del tag | 1.3.0 | current |
| `REF:cli_entry` | cortex.cli.main_e3:main | entry point de consola | 0.3.7 | current |
| `REF:package_root` | cortex/ | implementación Python | 0.3.7 | current |

<!-- /VIEW:sources -->

<!-- VIEW:source_audit kind=table target="$1:AUD:*" reverse=rows_to_entries fields="event,evidence,result,date" title="Evidencia de fuente" status=cur -->
## Evidencia de fuente

| Source | Event | Evidence | Result | Date |
|---|---|---|---|---|
| `AUD:wheel_integrity` | verificación del wheel | SHA256 local coincide con hash publicado b336464ad3b3279b69ce5fce0cc85dc0d0263a11d5cb5f452eea0d4b76cfd764 | success | 2026-07-15 |
| `AUD:static_inventory` | inspección estática del wheel | 93 módulos Python; CLI, core, v2, HCORTEX, CRUD, learning, security y audit inspeccionados | success | 2026-07-15 |
| `AUD:definitive_validation` | gates de aceptación del skill definitivo | verify --kind skill --strict: 0 errores/0 warnings; verify-view: 100% cobertura, 0 errores, 0 warnings; roundtrip: byte-identical; roundtrip-bidir: AST 0 diffs y content 0 diffs; explain-loss: 0 pérdidas | success | 2026-07-15 |

<!-- /VIEW:source_audit -->

<!-- VIEW:source_limits kind=table target="$1:LIM:*" reverse=rows_to_entries fields="limit,scope,status,evidence" title="Límites de procedencia" status=cur -->
## Límites de procedencia

| Source | Limit | Scope | Status | Evidence |
|---|---|---|---|---|
| `LIM:version_text_drift` | La distribución y __version__ son 0.3.7, pero descripción y skill upstream aún mencionan v0.3.6 en algunos campos | Autoridad de ejecución: cortex --version, _version.py y metadata del wheel | current | PyPI 0.3.7; cortex._version.__version__=0.3.7 |

<!-- /VIEW:source_limits -->

<!-- VIEW:source_rules kind=numbered_list target="$1:!:*" reverse=items_to_ordered_entries title="Reglas de autoridad" status=cur -->
## Reglas de autoridad

1. `!:runtime_authority` — Ante divergencia documental, usar la versión instalada y el comportamiento reproducible del CLI como autoridad de ejecución. (survive:min)

<!-- /VIEW:source_rules -->

<!-- VIEW:model_knowledge kind=table target="$2:KNW:*" reverse=rows_to_entries fields="topic,content,status,evidence" title="Model knowledge" status=cur -->
## Model knowledge

| Source | Topic | Content | Status | Evidence |
|---|---|---|---|---|
| `KNW:cortex` | CORTEX | Representación densa nativa; fuente canónica operacional y base de verificación. | current | parser/writer y AST |
| `KNW:hcortex` | HCORTEX | Representación humana derivada; reversible solo bajo contrato VIEW válido. | current | convert y roundtrip-bidir |
| `KNW:view` | VIEW | Contrato declarativo de render y reversión: kind, target, reverse, fields, status y metadatos opcionales. | current | cortex.v2.view |
| `KNW:cortex_out` | CORTEX-OUT | Protocolo conversacional; no participa en parse, AST, encode, verify ni roundtrip. | specification | separación canónica |
| `KNW:ast` | AST | Representación interna única para parser, writer, CRUD, comparación y validación del pipeline core. | current | cortex.core.ast |
| `KNW:skill` | SKILL.cortex | Nivel 1: reglas, contratos y comportamiento; nunca estado vivo. | current | document_kind policy |
| `KNW:brain` | brain.cortex | Nivel 2: estado vivo persistente; requiere FCS y OBJ activos. | current | document_kind policy |
| `KNW:package` | package.cortex | Nivel 3: contexto transportable; la implementación 0.3.7 bloquea estado vivo. | current | E029_LEVEL3_LIVE_STATE |
| `KNW:glossary` | $0 | Glosario local mínimo, primero y exclusivamente estructural. | current | E001 E002 E033 |
| `KNW:canonical_derived` | Canon | CORTEX y políticas explícitas son canónicos; HCORTEX, índice de aprendizaje e imágenes son derivados. | current | writer/index contracts |
| `KNW:determinism` | Determinismo | Misma entrada, política y versión deben producir AST, scores y serialización equivalentes. | current | sin LLM ni eval |
| `KNW:dual_pipeline` | Dos superficies | core atiende render/compile/CRUD; v2 atiende VIEW, convert, equivalencia y roundtrip bidireccional. | current | módulos core y v2 |

<!-- /VIEW:model_knowledge -->

<!-- VIEW:model_constraints kind=table target="$2:CNST:*" reverse=rows_to_entries fields="rule,severity,survive,evidence" title="Model constraints" status=cur -->
## Model constraints

| Source | Rule | Severity | Survive | Evidence |
|---|---|---|---|---|
| `CNST:source_canonical` | No modificar una vista derivada como si fuera la fuente canónica. | blocking | min | CORTEX es fuente operacional |
| `CNST:no_silent_inference` | No inferir tipo de entrada, contrato, cardinalidad, estado o reversibilidad sin declaración o evidencia. | blocking | min | parsers deterministas |
| `CNST:cortex_out_separate` | CORTEX-OUT no debe codificarse ni verificarse como artefacto .cortex. | blocking | min | modelo conceptual |
| `CNST:no_llm_dependency` | La operación del codec no debe depender de razonamiento probabilístico ni servicios LLM. | blocking | min | package design |
| `CNST:derived_rebuildable` | Índices, renders y salidas derivadas deben poder reconstruirse desde fuentes canónicas. | warning | recovery | learning index y HCORTEX |

<!-- /VIEW:model_constraints -->

<!-- VIEW:model_rules kind=numbered_list target="$2:!:*" reverse=items_to_ordered_entries title="Model rules" status=cur -->
## Model rules

1. `!:skill_governs` — SKILL gobierna; brain opera; package transporta; HCORTEX explica; CORTEX-OUT responde. (survive:min)
2. `!:minimum_read` — Leer primero identidad, constraints blocking, foco y objetivo; cargar histórico solo por necesidad. (survive:recovery)
3. `!:evidence_before_maturity` — No declarar current una capacidad sin comando, módulo o prueba reproducible. (survive:min)

<!-- /VIEW:model_rules -->

<!-- VIEW:grammar_knowledge kind=table target="$3:KNW:*" reverse=rows_to_entries fields="topic,content,status,evidence" title="Grammar knowledge" status=cur -->
## Grammar knowledge

| Source | Topic | Content | Status | Evidence |
|---|---|---|---|---|
| `KNW:attrs` | Tipo attrs | Pares key:value; valores bare tipados o strings entre comillas. | current | core.parser.parse_attrs_body |
| `KNW:attrs_pos` | Tipo attrs-pos | Valores ordenados por contrato local; exceso de aridad es error. | current | E007 y E027 |
| `KNW:cuerpo` | Tipo cuerpo | Texto semántico entre llaves; preserva contenido no estructurable. | current | core parser y HCORTEX prose |
| `KNW:bloque` | Tipo bloque | Contenido multilínea verbatim; DIAG debe preservarse sin reinterpretación. | current | Entry.raw y view verbatim |
| `KNW:relacion` | Tipo relación | Forma causal dirigida; usar solo cuando el significado de la relación sea explícito. | current | tipo canónico |
| `KNW:sections` | Secciones | Aceptar 2, $2 o $2: título y normalizar internamente a $2. | current | normalize_section_id |
| `KNW:selector` | Selector | SIGIL:name; calificar por sección cuando exista ambigüedad. | current | crud.selectors |
| `KNW:entry_hash` | Hash de entrada | Hash estructural sobre sigil, name, type y value; bloque incluye raw. | current | compute_entry_hash |
| `KNW:document_hash` | Hash de documento | SHA256 sobre bytes/texto canónico según operación. | current | roundtrip y signature |
| `KNW:microtokens` | Microtokens | Expandir solo por delimitador y nunca dentro de palabras. | current | glossary resolver |
| `KNW:naming` | Nombres | Sigilos en mayúsculas salvo !; instancias en snake_case; aliases públicos sin prefijo v2. | current | canon CLI |
| `KNW:survive` | Survive | min→P0; recovery→P1; work→P2; full→P5. | current | SURVIVE_TO_PLEVEL |
| `KNW:contract_fcs` | Contrato crítico | FCS: what,priority,status,survive | current | cortex.core.validator.REQUIRED_FIELDS |
| `KNW:contract_obj` | Contrato crítico | OBJ: goal,status,success,survive | current | cortex.core.validator.REQUIRED_FIELDS |
| `KNW:contract_wrk` | Contrato crítico | WRK: phase,current,blocked,survive | current | cortex.core.validator.REQUIRED_FIELDS |
| `KNW:contract_stp` | Contrato crítico | STP: action,reason,owner,status,survive | current | cortex.core.validator.REQUIRED_FIELDS |
| `KNW:contract_cnst` | Contrato crítico | CNST: rule,severity,survive | current | cortex.core.validator.REQUIRED_FIELDS |
| `KNW:contract_claim` | Contrato crítico | CLAIM: statement,evidence,status | current | cortex.core.validator.REQUIRED_FIELDS |
| `KNW:contract_lim` | Contrato crítico | LIM: limit,scope,status | current | cortex.core.validator.REQUIRED_FIELDS |
| `KNW:contract_rsk` | Contrato crítico | RSK: risk,impact,mitigation,status,survive | current | cortex.core.validator.REQUIRED_FIELDS |
| `KNW:contract_aud` | Contrato crítico | AUD: event,evidence,result,date | current | cortex.core.validator.REQUIRED_FIELDS |
| `KNW:contract_ses` | Contrato crítico | SES: input,output,outcome,date | current | cortex.core.validator.REQUIRED_FIELDS |
| `KNW:contract_lng` | Contrato crítico | LNG: type,cause,lesson,prevention | current | cortex.core.validator.REQUIRED_FIELDS |
| `KNW:contract_knw` | Contrato crítico | KNW: topic,content,status | current | cortex.core.validator.REQUIRED_FIELDS |

<!-- /VIEW:grammar_knowledge -->

<!-- VIEW:grammar_constraints kind=table target="$3:CNST:*" reverse=rows_to_entries fields="rule,severity,survive,evidence" title="Grammar constraints" status=cur -->
## Grammar constraints

| Source | Rule | Severity | Survive | Evidence |
|---|---|---|---|---|
| `CNST:glossary_required` | Todo artefacto .cortex debe contener $0 local. | blocking | min | E001 |
| `CNST:glossary_first` | $0 debe ser la primera sección. | blocking | min | E002 |
| `CNST:glossary_structural` | $0 no puede contener memoria operacional. | blocking | min | E033 no bypassable |
| `CNST:declare_sigil` | Cada sigilo debe declararse antes de su uso. | blocking | min | E003 |
| `CNST:declare_type` | Cada tipo referenciado debe estar declarado. | blocking | min | E004 |
| `CNST:attrs_pos_contract` | Cada attrs-pos requiere contrato y aridad exacta. | blocking | min | E007 E027 |
| `CNST:critical_complete` | Sigilos críticos deben incluir todos sus campos requeridos. | blocking | min | E032 |
| `CNST:critical_nonempty` | Campos críticos no aceptan vacío ni null-like: null, none, nil, undefined, n/a, tbd, todo, ?, -. | blocking | min | E034 |
| `CNST:no_duplicate` | No duplicar SIGIL:name dentro de la misma sección. | blocking | min | E008 |

<!-- /VIEW:grammar_constraints -->

<!-- VIEW:grammar_rules kind=numbered_list target="$3:!:*" reverse=items_to_ordered_entries title="Grammar rules" status=cur -->
## Grammar rules

1. `!:type_strict` — Resolver el tipo desde $0; no usar heurística de contenido. (survive:min)
2. `!:canonical_write` — Serializar mediante writer o CLI; evitar edición manual cuando una mutación determinista exista. (survive:recovery)
3. `!:unknown_line` — Toda línea no parseada debe corregirse o recuperarse; nunca ignorarla silenciosamente en un artefacto gobernado. (survive:recovery)
4. `!:priority_order` — Cargar P0→P5; al degradar eliminar P5 primero y nunca eliminar P0. (survive:min)

<!-- /VIEW:grammar_rules -->

<!-- VIEW:levels_knowledge kind=table target="$4:KNW:*" reverse=rows_to_entries fields="topic,content,status,evidence" title="Levels knowledge" status=cur -->
## Levels knowledge

| Source | Topic | Content | Status | Evidence |
|---|---|---|---|---|
| `KNW:skill_kind` | Documento skill | IDN:skill o filename skill.*; L1 sin estado vivo. | current | infer_document_kind |
| `KNW:brain_kind` | Documento brain | IDN:agent o FCS+WRK; L2 requiere FCS y OBJ activos. | current | infer_document_kind |
| `KNW:package_kind` | Documento package | IDN:package o CLAIM+LIM sin WRK; L3 sin estado vivo en 0.3.7. | current | infer_document_kind |
| `KNW:generic_kind` | Documento generic | Sin firma suficiente; aplicar solo reglas estructurales comunes. | current | default inference |
| `KNW:inference_order` | Inferencia de kind | IDN.kind/name > filename > firma de sigilos > generic. | current | document_kind.py |
| `KNW:live_state` | Estado vivo | FCS,OBJ,WRK,STP,NXT,SES,LNG; una entrada marcada example/template/non_operational/contract/specification no es viva. | current | _is_live_entry |
| `KNW:active_focus` | Foco activo | FCS y OBJ cuentan como activos solo con status current o blocked; done es cerrado. | current | E024 |

<!-- /VIEW:levels_knowledge -->

<!-- VIEW:levels_constraints kind=table target="$4:CNST:*" reverse=rows_to_entries fields="rule,severity,survive,evidence" title="Levels constraints" status=cur -->
## Levels constraints

| Source | Rule | Severity | Survive | Evidence |
|---|---|---|---|---|
| `CNST:l1_no_live_state` | Skill no puede contener FCS,OBJ,WRK,STP,NXT,SES o LNG vivos. | blocking | min | E023 |
| `CNST:l2_focus_objective` | Brain debe contener al menos un FCS y un OBJ activos. | blocking | min | E024 |
| `CNST:l3_no_live_state` | Package no puede contener estado vivo en la implementación 0.3.7. | blocking | min | E029 |
| `CNST:survive_domain` | survive solo admite min,recovery,work,full. | blocking | min | E025 |
| `CNST:blocking_is_p0` | CNST severity blocking debe usar survive min. | blocking | min | E026 |
| `CNST:explicit_kind_audit` | En auditoría o migración usar verify --kind para evitar inferencia incorrecta. | warning | recovery | CLI override |

<!-- /VIEW:levels_constraints -->

<!-- VIEW:levels_risks kind=table target="$4:RSK:*" reverse=rows_to_entries fields="risk,impact,mitigation,status,survive" title="Levels risks" status=cur -->
## Levels risks

| Source | Risk | Impact | Mitigation | Status | Survive |
|---|---|---|---|---|---|
| `RSK:kind_misclassification` | El filename o firma de sigilos puede inducir kind incorrecto. | Se aplican gates cognitivos inadecuados. | Usar --kind brain\|skill\|package\|generic en verify/doctor y corregir IDN. | current | recovery |

<!-- /VIEW:levels_risks -->

<!-- VIEW:levels_rules kind=numbered_list target="$4:!:*" reverse=items_to_ordered_entries title="Levels rules" status=cur -->
## Levels rules

1. `!:verify_on_load` — Al cargar un artefacto gobernado ejecutar verify --strict con kind explícito cuando sea conocido. (survive:min)
2. `!:verify_before_commit` — Antes de persistir o commitear ejecutar verify/verify-view y el roundtrip aplicable. (survive:min)

<!-- /VIEW:levels_rules -->

<!-- VIEW:security_knowledge kind=table target="$6:KNW:*" reverse=rows_to_entries fields="topic,content,status,evidence" title="Security knowledge" status=cur -->
## Security knowledge

| Source | Topic | Content | Status | Evidence |
|---|---|---|---|---|
| `KNW:mode_read_only` | Modo read-only | Permite lectura, inspección, verificación, render y comparación; bloquea mutaciones. | current | E035 |
| `KNW:mode_editor` | Modo editor | Default; permite escritura y pide confirmación interactiva para --force. | current | modes.py |
| `KNW:mode_admin` | Modo admin | Permite force sin confirmación; debe ser selección consciente y acotada. | current | modes.py |
| `KNW:mode_precedence` | Resolución de modo | --mode > CORTEX_MODE > editor. | current | resolve_mode |
| `KNW:atomic_write` | Escritura atómica | Mutaciones se escriben mediante archivo temporal y replace; fallo produce E015. | current | crud.transactions |
| `KNW:post_validation` | Validación posterior | Mutaciones validan antes de persistir por defecto; strict-write eleva warnings. | current | CRUD commands |
| `KNW:protected_entries` | Entradas protegidas | FCS,OBJ,CNST blocking o survive min requieren force/autorización. | current | is_protected_entry |
| `KNW:secret_scan` | Secret scanner | Doctor escanea claves, passwords, tokens, AWS secrets, private keys y URLs con credenciales. | current | security.secret_scanner |
| `KNW:signature` | Firma SHA256 | verify --signature/--manifest compara input contra SHA256SUMS. | current | security.signature |
| `KNW:audit_log` | Audit log | Opt-in, append-only, rotación diaria, fuera del repo; snapshots one-shot. | current | audit.logger |

<!-- /VIEW:security_knowledge -->

<!-- VIEW:security_constraints kind=table target="$6:CNST:*" reverse=rows_to_entries fields="rule,severity,survive,evidence" title="Security constraints" status=cur -->
## Security constraints

| Source | Rule | Severity | Survive | Evidence |
|---|---|---|---|---|
| `CNST:no_clear_secrets` | No almacenar secretos en claro; usar REF a proveedor/clave. | blocking | min | E031 no bypassable con force |
| `CNST:read_only_hard` | No ejecutar write commands bajo modo read-only. | blocking | min | E035 |
| `CNST:dry_run_first` | Toda mutación riesgosa o elevación debe mostrar diff/dry-run antes de aplicar. | blocking | min | learning gate y CRUD |
| `CNST:post_write_verify` | Después de mutar, volver a parsear, validar y verificar el gate aplicable. | blocking | min | transactions/elevation |
| `CNST:audit_opt_in` | No afirmar que existe log de auditoría si audit status está off. | warning | recovery | E038 |

<!-- /VIEW:security_constraints -->

<!-- VIEW:security_risks kind=table target="$6:RSK:*" reverse=rows_to_entries fields="risk,impact,mitigation,status,survive" title="Security risks" status=cur -->
## Security risks

| Source | Risk | Impact | Mitigation | Status | Survive |
|---|---|---|---|---|---|
| `RSK:skip_validation` | --no-validate-write puede persistir estructura o gobierno inválidos. | Corrupción semántica o pérdida de continuidad. | Reservar para recuperación controlada; ejecutar verify --strict inmediatamente. | current | recovery |
| `RSK:forensic_secret_bypass` | --unsafe-allow-secret-forensics permite material sensible. | Exposición de credenciales en memoria, logs o repositorio. | Usar solo en entorno aislado, temporal y autorizado; redacción y eliminación posterior. | current | min |

<!-- /VIEW:security_risks -->

<!-- VIEW:security_rules kind=numbered_list target="$6:!:*" reverse=items_to_ordered_entries title="Security rules" status=cur -->
## Security rules

1. `!:mutation_sequence` — Preflight inspect/verify → dry-run/diff → mutación mínima → verify estricto → roundtrip aplicable → audit/evidence. (survive:min)
2. `!:least_privilege` — Usar read-only para auditoría, editor para trabajo normal y admin solo durante la operación que lo exige. (survive:min)

<!-- /VIEW:security_rules -->

<!-- VIEW:views_knowledge kind=table target="$7:KNW:*" reverse=rows_to_entries fields="topic,content,status,evidence" title="Views knowledge" status=cur -->
## Views knowledge

| Source | Topic | Content | Status | Evidence |
|---|---|---|---|---|
| `KNW:profile_min` | HCORTEX MIN | P0; presupuesto aproximado 512 tokens. | current | hcortex.profiles |
| `KNW:profile_recovery` | HCORTEX RECOVERY | P0-P1; presupuesto aproximado 1024 tokens. | current | hcortex.profiles |
| `KNW:profile_work` | HCORTEX WORK | P0-P2; presupuesto aproximado 3072 tokens; default. | current | hcortex.profiles |
| `KNW:profile_full` | HCORTEX FULL | P0-P5; sin presupuesto fijo. | current | hcortex.profiles |
| `KNW:render_readable` | Render readable | Vista humana limpia; default de render core. | current | render --mode readable |
| `KNW:render_edit` | Render edit | Vista compilable de vuelta por compile; conserva metadata. | current | render --mode edit |
| `KNW:render_audit` | Render audit | Incluye source para trazabilidad. | current | render --with-source |
| `KNW:view_kinds` | VIEW kinds | table,kv_table,matrix,list,numbered_list,checklist,prose,quote,puml,code,callout,section,raw. | current | VALID_KINDS |
| `KNW:view_reverse` | Reverse strategies | rows_to_entries,row_to_attrs,columns_to_attrs,items_to_entries,items_to_ordered_entries,items_to_status_entries,body_to_cuerpo,verbatim_to_bloque,callout_to_risk,callout_to_limit,preserve_human_block,ignore_with_warning,manual_review. | current | VALID_REVERSES |
| `KNW:view_target` | VIEW target | $0 special groups; $N; $N:SIGIL:*; $N:SIGIL:name; SIGIL:*; SIGIL:name; HUMAN_BLOCK. | current | resolve_target |
| `KNW:equivalence` | Niveles de equivalencia | byte-identical, AST-equivalent, semantic-equivalent y content-equivalent. | current | v2.equivalence |
| `KNW:display_mode` | Modo display | Produce Markdown sin contrato reversible; nunca declarar reversible true. | current | convert --mode display |
| `KNW:hcortex_r_alias` | Alias hcortex-r | Deprecated; usar hcortex como nombre canónico. | deprecated | convert command |

<!-- /VIEW:views_knowledge -->

<!-- VIEW:views_constraints kind=table target="$7:CNST:*" reverse=rows_to_entries fields="rule,severity,survive,evidence" title="Views constraints" status=cur -->
## Views constraints

| Source | Rule | Severity | Survive | Evidence |
|---|---|---|---|---|
| `CNST:reversible_gate` | reversible true exige cobertura VIEW 100%, cero E_VIEW/E_HCORTEX, modo no display y roundtrip canónico aplicable sin pérdida. | blocking | min | modelo PyPI y comandos v2 |
| `CNST:view_compatibility` | kind y reverse deben pertenecer a la matriz de compatibilidad. | blocking | min | E_VIEW_INCOMPATIBLE_REVERSE |
| `CNST:view_unique` | Cada VIEW name debe ser único y target no vacío. | blocking | min | E_VIEW_DUPLICATE_NAME/E_VIEW_EMPTY_TARGET |
| `CNST:verbatim_integrity` | PUML/code/bloque reversible debe conservar contenido verbatim y hash cuando se declara. | blocking | min | verbatim_to_bloque/E_VIEW_HASH_MISMATCH |
| `CNST:no_write_on_view_error` | convert no debe escribir --out si existen errores VIEW salvo force-write-on-error explícito. | blocking | min | v2_convert |

<!-- /VIEW:views_constraints -->

<!-- VIEW:views_limits kind=table target="$7:LIM:*" reverse=rows_to_entries fields="limit,scope,status,evidence" title="Views limits" status=cur -->
## Views limits

| Source | Limit | Scope | Status | Evidence |
|---|---|---|---|---|
| `LIM:verify_view_scope` | verify-view calcula cobertura y errores de render, pero no ejecuta por sí solo el roundtrip bidireccional. | Gate completo = verify-view --strict + roundtrip-bidir; roundtrip añade fidelidad byte-identical CORTEX. | current | implementación v2_verify_view.py |

<!-- /VIEW:views_limits -->

<!-- VIEW:views_risks kind=table target="$7:RSK:*" reverse=rows_to_entries fields="risk,impact,mitigation,status,survive" title="Views risks" status=cur -->
## Views risks

| Source | Risk | Impact | Mitigation | Status | Survive |
|---|---|---|---|---|---|
| `RSK:force_write_invalid_view` | force-write-on-error puede dejar HCORTEX/CORTEX inválido en disco. | Falsa reversibilidad o pérdida silenciosa. | Usar solo para diagnóstico; ejecutar explain-loss, compare y reparar antes de aceptar. | current | recovery |

<!-- /VIEW:views_risks -->

<!-- VIEW:views_rules kind=numbered_list target="$7:!:*" reverse=items_to_ordered_entries title="Views rules" status=cur -->
## Views rules

1. `!:view_gate_sequence` — inspect → verify-view --strict → convert estricto → roundtrip-bidir → compare cuando exista artefacto esperado. (survive:min)
2. `!:display_not_canonical` — Una salida convertida en mode display es presentación, no HCORTEX canónico reversible. (survive:min)

<!-- /VIEW:views_rules -->

<!-- VIEW:learning_knowledge kind=table target="$8:KNW:*" reverse=rows_to_entries fields="topic,content,status,evidence" title="Learning knowledge" status=cur -->
## Learning knowledge

| Source | Topic | Content | Status | Evidence |
|---|---|---|---|---|
| `KNW:workspace_manifest` | Workspace | .cortex/MANIFEST.cortex es canónico y referencia brain, policy e índice. | current | learn init |
| `KNW:workspace_brain` | Workspace | .cortex/brain.cortex es memoria operacional canónica. | current | learn init |
| `KNW:workspace_policy` | Workspace | .cortex/learn-policies.cortex define thresholds, policies, gates y protegidos. | current | learn init |
| `KNW:workspace_index` | Workspace | .cortex/index/learn-index.json es derivado, hash-aware y reconstruible. | current | learn index |
| `KNW:workspace_cache` | Workspace | .cortex/cache es derivado y no canónico. | current | learn init |
| `KNW:signals` | Señales | observed,repeated,pattern,decision_relevant,user_validated,risk_preventing,critical. | current | learning.scoring |
| `KNW:hotness` | Score hotness | Recurrencia, validación y criticidad; floor observed y cap critical. | current | score_hotness |
| `KNW:promotion` | Score promotion | Repetición, patrón, decisión, validación, prevención y criticidad acotada. | current | score_promotion |
| `KNW:risk_weight` | Score risk | Costo de omitir/degradar; decisiones, prevención, protección y baseline por sigilo. | current | score_risk |
| `KNW:read_priority` | Read priority | P0 bloqueo/foco/paso activo; P1 crítico; P2 fuerte/KNW/LNG; P3 candidato; P4 repetido; P5 frío. | current | derive_read_priority |
| `KNW:candidate_targets` | Elevaciones | WRK→SES; SES→LNG; LNG→KNW; RSK→CNST; NXT→STP. | current | candidates._DEFAULT_TARGET |
| `KNW:candidate_cluster` | Clustering | Agrupa por sigilo y primer atributo disponible: topic,outcome,lesson,risk,statement; fallback nombre. | current | _cluster_key_for |
| `KNW:condition_dsl` | Policy condition DSL | Cláusulas AND separadas por \|; operadores =,!=,>=,<=,>,<; tipos seguros. | current | learning.conditions |
| `KNW:fingerprint` | Fingerprint | SHA256 del payload normalizado; cambios cosméticos no invalidan índice. | current | stable_fingerprint |
| `KNW:elevation_patch` | Patch de elevación | Plan determinista con diff, target, reason, policy, score y affected_files. | current | learning.elevation |

<!-- /VIEW:learning_knowledge -->

<!-- VIEW:learning_constraints kind=table target="$8:CNST:*" reverse=rows_to_entries fields="rule,severity,survive,evidence" title="Learning constraints" status=cur -->
## Learning constraints

| Source | Rule | Severity | Survive | Evidence |
|---|---|---|---|---|
| `CNST:learning_deterministic` | Mismo brain, policy y versión deben producir los mismos fingerprints, scores y candidatos. | blocking | min | scoring side-effect free |
| `CNST:no_dynamic_eval` | Policy DSL no puede usar eval, exec, compile ni evaluación AST dinámica. | blocking | min | LE011 y conditions.py |
| `CNST:index_not_memory` | El índice no es memoria canónica y puede borrarse/reconstruirse. | blocking | min | MANIFEST constraint |
| `CNST:critical_protected` | Objetivos protegidos no pueden elevarse o mutarse por política común. | blocking | min | LE007 |
| `CNST:apply_confirmed` | Elevación apply requiere confirmación; dry-run es el default. | blocking | min | LE013 |

<!-- /VIEW:learning_constraints -->

<!-- VIEW:learning_rules kind=numbered_list target="$8:!:*" reverse=items_to_ordered_entries title="Learning rules" status=cur -->
## Learning rules

1. `!:learning_cycle` — learn doctor → policy validate → scan/index → candidates → explain → elevate dry-run → confirm/apply → verify brain+index. (survive:min)
2. `!:policy_authority` — Una política puede proponer o aplicar solo dentro de sus condiciones y gates; protección y confirmación prevalecen. (survive:min)

<!-- /VIEW:learning_rules -->

<!-- VIEW:workflow_knowledge kind=table target="$9:KNW:*" reverse=rows_to_entries fields="topic,content,status,evidence" title="Workflow knowledge" status=cur -->
## Workflow knowledge

| Source | Topic | Content | Status | Evidence |
|---|---|---|---|---|
| `KNW:startup` | Startup | cortex --version → inspect → detectar kind → verify --strict → cargar P0/P1 → operar. | current | preflight |
| `KNW:create_skill` | Crear skill | new skill → completar $0/IDN/DOM/CNST → verify --kind skill --strict → render audit. | current | core pipeline |
| `KNW:create_brain` | Crear brain | new brain o learn init → completar FCS/OBJ/WRK/STP → verify --kind brain --strict. | current | L2 gate |
| `KNW:read_artifact` | Lectura | inspect/list/get → render readable/audit según audiencia → no mutar. | current | read-only mode |
| `KNW:mutate_artifact` | Mutación | inspect+verify → dry-run → add/update/delete/move → verify estricto → diff/roundtrip. | current | transaction gate |
| `KNW:v2_conversion` | Conversión reversible | verify-view --strict → convert strict → roundtrip-bidir → compare. | current | VIEW gate |
| `KNW:recovery` | Recuperación | recover --embed-aud-rsk → inspect → doctor --strict → corregir → verify/roundtrip. | current | recovery pipeline |
| `KNW:security` | Seguridad | doctor --scan-secrets → eliminar secretos → verify signature cuando exista manifest. | current | E2 |
| `KNW:learning` | Aprendizaje | learn doctor → validate policy → scan → candidates → explain → dry-run → confirm apply. | current | learning engine |
| `KNW:audit` | Auditoría | audit on solo si se requiere → operar → status/snapshot → audit off → prune según política. | current | opt-in audit |
| `KNW:release` | Cierre | tests → verify/roundtrip → secret scan → signature → evidencia AUD → publicar artefacto derivado. | current | release gate |

<!-- /VIEW:workflow_knowledge -->

<!-- VIEW:workflow_rules kind=numbered_list target="$9:!:*" reverse=items_to_ordered_entries title="Workflow rules" status=cur -->
## Workflow rules

1. `!:read_before_write` — Nunca mutar un artefacto que no haya sido inspeccionado y validado en la sesión actual. (survive:min)
2. `!:smallest_patch` — Aplicar el cambio estructural mínimo; no reformatear ni reescribir contenido no relacionado. (survive:min)
3. `!:stop_on_blocking` — Ante error blocking o gate no satisfecho, detener escritura y devolver causa+recuperación. (survive:min)
4. `!:truthful_status` — No declarar verificación, render o reversibilidad si el comando correspondiente no fue ejecutado. (survive:min)
5. `!:derived_after_canon` — Generar HCORTEX, índices, diagramas o reportes después de estabilizar la fuente canónica. (survive:min)

<!-- /VIEW:workflow_rules -->

<!-- VIEW:architecture_limits kind=table target="$11:LIM:*" reverse=rows_to_entries fields="limit,scope,status,evidence" title="Architecture limits" status=cur -->
## Architecture limits

| Source | Limit | Scope | Status | Evidence |
|---|---|---|---|---|
| `LIM:no_sdist` | Release 0.3.7 publica wheel pero no source distribution. | Auditoría de procedencia debe usar wheel+tag/repositorio. | current | PyPI download files |
| `LIM:docs_not_bundled` | El wheel no incluye docs/cortex/api ni benchmark corpus. | docstring/benchmark requieren paths externos cuando no están instalados. | current | wheel inventory |
| `LIM:dual_canonicalizers` | format pertenece al pipeline core; canonicalize pertenece a v2 y es VIEW-aware. | Elegir según formato y gate; no intercambiarlos ciegamente. | current | CLI router |
| `LIM:doctor_v2_gap` | doctor 0.3.7 usa el parser core y no interpreta correctamente sigil_decl ni attrs-pos del artefacto CORTEX v2, aunque verify E3, inspect, verify-view y roundtrips v2 sí lo aceptan. | Para skills v2 usar verify --kind skill --strict y gates v2; usar doctor sobre artefactos core o tratar su salida v2 como incompatibilidad conocida. | current | ejecución reproducible contra codec-cortex 0.3.7 |

<!-- /VIEW:architecture_limits -->

<!-- VIEW:architecture_rules kind=numbered_list target="$11:!:*" reverse=items_to_ordered_entries title="Architecture rules" status=cur -->
## Architecture rules

1. `!:installed_runtime_wins` — Para ejecutar, la API y CLI del wheel instalado prevalecen sobre ejemplos o documentación desfasada. (survive:min)
2. `!:future_not_current` — No asumir MCP u otra capacidad future como disponible; comprobar comando/módulo/evidencia. (survive:min)

<!-- /VIEW:architecture_rules -->

<!-- VIEW:output_knowledge kind=table target="$12:KNW:*" reverse=rows_to_entries fields="topic,content,status,evidence" title="Output knowledge" status=cur -->
## Output knowledge

| Source | Topic | Content | Status | Evidence |
|---|---|---|---|---|
| `KNW:out_min` | OUT-MIN | Resultado + acción; interacción directa y bajo presupuesto. | specification | CORTEX-OUT |
| `KNW:out_work` | OUT-WORK | Resultado + criterio + acción + límite; operación normal. | specification | CORTEX-OUT |
| `KNW:out_audit` | OUT-AUDIT | Resultado + evidencia + riesgo + control + trazabilidad. | specification | CORTEX-OUT |
| `KNW:out_full` | OUT-FULL | Reporte completo y artefactos reutilizables. | specification | CORTEX-OUT |
| `KNW:out_error` | OUT-ERROR | Código + causa + recuperación accionable. | specification | CORTEX-OUT |
| `KNW:blocks` | Bloques | Resultado,Criterio,Evidencia,Riesgo,Acción,Límite,Entrega,Control según intención. | specification | upstream skill |

<!-- /VIEW:output_knowledge -->

<!-- VIEW:output_rules kind=numbered_list target="$12:!:*" reverse=items_to_ordered_entries title="Output rules" status=cur -->
## Output rules

1. `!:out_independent` — CORTEX-OUT permanece fuera del pipeline CORTEX-HCORTEX. (survive:recovery)
2. `!:out_no_sigils` — La respuesta humana no debe exponer sintaxis interna salvo que el usuario solicite el artefacto. (survive:recovery)
3. `!:out_honesty` — No ocultar incertidumbre, límites, riesgo, errores o verificaciones pendientes. (survive:recovery)
4. `!:out_density` — Priorizar resultado, criterio, evidencia crítica y próximo paso; eliminar recapitulación inútil. (survive:recovery)

<!-- /VIEW:output_rules -->

<!-- VIEW:handlers kind=table target="$5:HDL:*" reverse=rows_to_entries fields="operation,status,requires,notes" title="Router CLI" status=cur -->
## Router CLI

| Source | Operación | Estado | Requiere | Notas |
|---|---|---|---|---|
| `HDL:version` | reportar versión instalada | current | ninguno | cortex --version; autoridad primaria de versión |
| `HDL:new` | crear artefacto desde template | current | kind y --out | brain,skill,package,generic; minimal,standard,enterprise; --with-diagrams |
| `HDL:render` | decodificar CORTEX core a HCORTEX | current | input .cortex | alias decode; readable/edit/audit/recovery/full; profile y layout |
| `HDL:compile` | codificar HCORTEX-EDIT a CORTEX core | current | input HCORTEX-EDIT y --out | alias encode; requiere metadatos editables |
| `HDL:verify` | validar estructura y gobierno | current | input | --strict; --kind; --roundtrip; --signature/--manifest |
| `HDL:get` | obtener una entrada | current | input y selector | text o json; calificar selector si es ambiguo |
| `HDL:list` | listar entradas | current | input | filtros --section y --sigil; text o json |
| `HDL:add` | agregar entrada | current | input, section, sigil, name, value | dry-run; validación post-write; flags de recuperación explícitos |
| `HDL:update` | actualizar entrada | current | input y selector | --set repetible o --body; --append; dry-run |
| `HDL:delete` | eliminar entrada | current | input y selector | protecciones; dry-run; force solo autorizado |
| `HDL:move` | mover entrada de sección | current | input, selector, --to-section | validación posterior y dry-run |
| `HDL:glossary` | CRUD de sigilos en $0 | current | subcomando list/add/update/delete | no eliminar sigilo reservado o en uso |
| `HDL:micro` | CRUD de microtokens | current | subcomando list/add/update/delete | no eliminar token en uso |
| `HDL:doctor` | diagnóstico profundo | current | input | strict/kind; secret scan; paths adicionales; baseline |
| `HDL:diff` | comparar documentos core | current | left y right | profiles structural,semantic,governance |
| `HDL:format` | serializar canónicamente pipeline core | current | input | --out o in-place; dry-run |
| `HDL:recover` | recuperar artefacto legacy/no conforme | current | input | --strict; --embed-aud-rsk; revisar salida antes de aceptar |
| `HDL:diagram` | operar entradas DIAG | current | list,extract,validate | extracción verbatim y validación de integridad |
| `HDL:audit` | controlar auditoría opt-in | current | on,off,status,snapshot,prune | logging apagado por defecto; JSONL fuera del repo |
| `HDL:roundtrip` | verificar roundtrip CORTEX v2 | current | input CORTEX v2 | comparación byte-identical |
| `HDL:convert` | convertir CORTEX v2 y HCORTEX | current | --from y --to | normal,strict,audit,recovery,display; hcortex-r deprecated |
| `HDL:roundtrip_bidir` | verificar CORTEX-HCORTEX bidireccional | current | input con header CODEC-CORTEX | AST-equivalent y content-equivalent |
| `HDL:compare` | comparar equivalencia v2 | current | left y right | byte, AST, semantic y content; --verbose |
| `HDL:verify_view` | validar VIEW | current | input CORTEX v2 | cobertura, errores y warnings; no sustituye roundtrip-bidir |
| `HDL:explain_loss` | explicar pérdida/no reversibilidad | current | input CORTEX o HCORTEX | reporta omisión, fallback y contenido no reversible |
| `HDL:canonicalize` | normalizar artefacto v2 | current | input | VIEW-aware; --preserve conserva estructura y normaliza whitespace/orden |
| `HDL:inspect` | inspeccionar AST y VIEW | current | input | secciones, sigilos, tipos, cobertura, formato y diagnósticos |
| `HDL:docstring` | derivar documentación CLI | current | command o --all | lee docs/cortex/api cuando están disponibles |
| `HDL:benchmark` | inventariar suites benchmark | current | --root/--suite/--list | no ejecuta modelos; inventaria suites |
| `HDL:learn` | motor de aprendizaje local | current | workspace y subcomando | init,doctor,policy,index,scan,candidates,explain,elevate,profile |
| `HDL:learn_init` | inicializar workspace de aprendizaje | current | --workspace | crea MANIFEST, brain, policies, index y cache |
| `HDL:learn_doctor` | validar workspace de aprendizaje | current | --workspace | comprueba directorio, manifest, brain, policy e índice |
| `HDL:learn_policy` | gestionar políticas | current | show,validate,apply,add | apply requiere archivo; dry-run y confirm |
| `HDL:learn_index` | gestionar índice derivado | current | rebuild,status,clean | índice no canónico y reconstruible |
| `HDL:learn_scan` | puntuar brain e indexar | current | --workspace | genera scores deterministas y hash de brain/policy |
| `HDL:learn_candidates` | listar candidatos | current | --workspace | orden por promotion y hotness; --limit |
| `HDL:learn_explain` | explicar candidato | current | --candidate | muestra fuentes, scores, policy y thresholds |
| `HDL:learn_elevate` | planificar/aplicar elevación | current | --candidate o --policy | dry-run por defecto; --apply y --confirm para escribir |
| `HDL:learn_profile` | crear perfil de carga | current | --budget | selecciona por read_priority dentro del presupuesto |

<!-- /VIEW:handlers -->

<!-- VIEW:learning_thresholds kind=kv_table target="$8:THR:golden_fibonacci" reverse=row_to_attrs title="Umbrales Fibonacci" status=cur -->
## Umbrales Fibonacci

**Source:** `THR:golden_fibonacci`

| Campo | Valor |
|---|---|
| observed | 1 |
| repeated | 2 |
| pattern | 3 |
| candidate | 5 |
| ask_user | 8 |
| strong_candidate | 13 |
| critical | 21 |

<!-- /VIEW:learning_thresholds -->

<!-- VIEW:learning_protected kind=kv_table target="$8:PRT:critical_sigils" reverse=row_to_attrs title="Targets protegidos" status=cur -->
## Targets protegidos

**Source:** `PRT:critical_sigils`

| Campo | Valor |
|---|---|
| items | IDN\|AXM\|CNST:blocking\|CLAIM\|LIM |
| mutation | explicit_user_confirmation |
| status | current |

<!-- /VIEW:learning_protected -->

<!-- VIEW:learning_policies kind=table target="$8:POL:*" reverse=rows_to_entries fields="origin,target,when,action,requires" title="Políticas de aprendizaje" status=cur -->
## Políticas de aprendizaje

| Source | Origin | Target | When | Action | Requires |
|---|---|---|---|---|---|
| `POL:candidate_detection` | brain | index | scan_sigils=WRK,SES,LNG,RSK,NXT,CLAIM,LIM | score | golden_fibonacci_v1 |
| `POL:candidate_elevation` | SES\|LNG | LNG\|KNW | promotion_score>=8 | propose | user_confirmation |
| `POL:auto_ses_to_lng` | SES | LNG | promotion_score>=8\|user_validated=true | apply | policy_authorized |
| `POL:auto_lng_to_knw` | LNG | KNW | promotion_score>=13\|user_validated=true\|risk_weight>=8 | apply | admin_policy |

<!-- /VIEW:learning_policies -->

<!-- VIEW:learning_gates kind=table target="$8:GTE:*" reverse=rows_to_entries fields="action,default,targets,status" title="Gates de aprendizaje" status=cur -->
## Gates de aprendizaje

| Source | Action | Default | Targets | Status |
|---|---|---|---|---|
| `GTE:default_mutation` | mutate_brain | dry_run_first | all | current |
| `GTE:critical_mutation` | mutate_brain | block_unless_admin_policy | IDN\|AXM\|CNST:blocking\|CLAIM\|LIM\|KNW | current |

<!-- /VIEW:learning_gates -->

<!-- VIEW:error_atlas kind=table target="$10:ERR:*" reverse=rows_to_entries fields="code,cause,recovery,severity" title="Atlas de errores" status=cur -->
## Atlas de errores

| Source | Code | Cause | Recovery | Severity |
|---|---|---|---|---|
| `ERR:e001_missing_glossary` | E001_MISSING_GLOSSARY | Falta $0. | Agregar glosario local mínimo como primera sección. | blocking |
| `ERR:e002_glossary_not_first` | E002_GLOSSARY_NOT_FIRST | $0 no es primera sección. | Mover $0 al inicio y volver a parsear. | blocking |
| `ERR:e003_unknown_sigil` | E003_UNKNOWN_SIGIL | Sigilo usado no declarado. | Declararlo en $0 antes del uso. | blocking |
| `ERR:e004_unknown_type` | E004_UNKNOWN_TYPE | Tipo de sigilo no declarado. | Registrar tipo canónico en $0. | blocking |
| `ERR:e005_unbalanced_braces` | E005_UNBALANCED_BRACES | Llaves sin balance. | Corregir el primer bloque abierto/cerrado incorrectamente. | blocking |
| `ERR:e006_invalid_attrs` | E006_INVALID_ATTRS | Cuerpo attrs inválido. | Corregir pares key:value, comillas y separadores. | blocking |
| `ERR:e007_attrs_pos_contract_missing` | E007_ATTRS_POS_CONTRACT_MISSING | attrs-pos sin contrato. | Agregar contract_<sigil> con pos exacto. | blocking |
| `ERR:e008_duplicate_entry` | E008_DUPLICATE_ENTRY | SIGIL:name duplicado en sección. | Renombrar, fusionar o eliminar duplicado. | blocking |
| `ERR:e009_protected_entry` | E009_PROTECTED_ENTRY | Mutación sobre entrada protegida. | Revisar impacto y usar autorización/force solo si procede. | blocking |
| `ERR:e010_hcortex_read_not_compilable` | E010_HCORTEX_READ_NOT_COMPILABLE | Vista readable no compilable. | Generar HCORTEX edit y usar compile. | blocking |
| `ERR:e011_hcortex_edit_metadata_missing` | E011_HCORTEX_EDIT_METADATA_MISSING | HCORTEX edit perdió metadata. | Regenerar vista edit y preservar marcadores. | blocking |
| `ERR:e012_roundtrip_failed` | E012_ROUNDTRIP_FAILED | Roundtrip no equivalente. | Ejecutar compare/explain-loss y reparar primera diferencia. | blocking |
| `ERR:e013_not_found` | E013_NOT_FOUND | Archivo o candidato inexistente. | Corregir path/selector/id y repetir. | blocking |
| `ERR:e014_ambiguous_selector` | E014_AMBIGUOUS_SELECTOR | Selector coincide con varias entradas. | Calificar con sección o selector exacto. | blocking |
| `ERR:e015_atomic_write_failed` | E015_ATOMIC_WRITE_FAILED | Falló escritura atómica. | Revisar permisos, espacio y archivo temporal; no aceptar parcial. | blocking |
| `ERR:e016_invalid_section_header` | E016_INVALID_SECTION_HEADER | Header de sección inválido. | Normalizar a $N o $N: TÍTULO. | blocking |
| `ERR:e017_unparsed_line` | E017_UNPARSED_LINE | Línea no reconocida. | Codificarla como entrada/comentario válido o recuperar. | blocking |
| `ERR:e018_protected_sigil` | E018_PROTECTED_SIGIL | Intento de borrar sigilo reservado. | Mantenerlo o migrar con procedimiento explícito. | blocking |
| `ERR:e019_sigil_in_use` | E019_SIGIL_IN_USE | Sigilo aún referenciado. | Migrar/eliminar instancias antes de quitar declaración. | blocking |
| `ERR:e020_micro_in_use` | E020_MICRO_IN_USE | Microtoken aún usado. | Expandir o migrar usos antes de borrarlo. | blocking |
| `ERR:e021_invalid_value` | E021_INVALID_VALUE | Valor/opción fuera de contrato. | Usar enum, formato o combinación soportada. | blocking |
| `ERR:e022_template_unknown` | E022_TEMPLATE_UNKNOWN | Template inexistente. | Elegir minimal, standard o enterprise. | blocking |
| `ERR:e023_level1_live_state` | E023_LEVEL1_LIVE_STATE | Skill contiene estado vivo. | Eliminarlo o marcarlo contract/example/specification. | blocking |
| `ERR:e024_level2_missing_focus` | E024_LEVEL2_MISSING_FOCUS | Brain sin FCS/OBJ activos. | Crear entradas completas status current\|blocked. | blocking |
| `ERR:e025_invalid_survive` | E025_INVALID_SURVIVE | survive fuera de dominio. | Usar min,recovery,work o full. | blocking |
| `ERR:e026_blocking_not_p0` | E026_BLOCKING_NOT_P0 | CNST blocking no usa survive min. | Cambiar survive a min. | blocking |
| `ERR:e027_attrs_pos_arity` | E027_ATTRS_POS_ARITY | Aridad excede contrato. | Ajustar valores o contrato sin pérdida. | blocking |
| `ERR:e028_secret_in_clear` | E028_SECRET_IN_CLEAR | Secreto en claro. | Eliminarlo y usar REF; rotar credencial si fue expuesta. | blocking |
| `ERR:e029_level3_live_state` | E029_LEVEL3_LIVE_STATE | Package contiene estado vivo. | Retirar estado operativo o moverlo a brain. | blocking |
| `ERR:e030_recovery_incomplete` | E030_RECOVERY_INCOMPLETE | Recuperación dejó ambigüedad/pérdida. | Revisión humana y evidencia AUD/RSK antes de aceptar. | blocking |
| `ERR:e031_secret_not_bypassable` | E031_SECRET_NOT_BYPASSABLE | Secreto no bypassable por force. | Redactar y usar REF; forensic flag solo en entorno autorizado. | blocking |
| `ERR:e032_critical_sigil_incomplete` | E032_CRITICAL_SIGIL_INCOMPLETE | Faltan campos críticos. | Completar contrato requerido antes de persistir. | blocking |
| `ERR:e033_zero_section_memory_entry` | E033_ZERO_SECTION_MEMORY_ENTRY | Entrada operacional oculta en $0. | Moverla a $1+; $0 es solo metadata/glosario. | blocking |
| `ERR:e034_critical_required_field_empty` | E034_CRITICAL_REQUIRED_FIELD_EMPTY | Campo crítico vacío/null-like. | Proveer valor semántico real. | blocking |
| `ERR:e035_mode_read_only` | E035_MODE_READ_ONLY | Write command en read-only. | Cambiar conscientemente a editor/admin. | blocking |
| `ERR:e036_mode_editor_confirm` | E036_MODE_EDITOR_CONFIRM | Force sin confirmación interactiva. | Confirmar, usar --yes o admin autorizado. | blocking |
| `ERR:e037_mode_unknown` | E037_MODE_UNKNOWN | Modo no reconocido. | Usar read-only, editor o admin. | blocking |
| `ERR:e038_audit_logging_off` | E038_AUDIT_LOGGING_OFF | Se esperaba audit pero está off. | Ejecutar audit on o declarar ausencia de log. | blocking |
| `ERR:e039_signature_mismatch` | E039_SIGNATURE_MISMATCH | SHA256 no coincide con manifest. | Detener; verificar archivo, manifest y procedencia. | blocking |
| `ERR:e040_secret_detected` | E040_SECRET_DETECTED | Secret scanner detectó hallazgo alto. | Redactar/rotar o justificar en baseline controlado. | blocking |
| `ERR:le001_workspace_not_found` | LE001_WORKSPACE_NOT_FOUND | Workspace .cortex no encontrado. | Ejecutar learn init o indicar --workspace correcto. | blocking |
| `ERR:le002_manifest_missing` | LE002_MANIFEST_MISSING | Falta MANIFEST.cortex. | Restaurar/recrear manifest canónico. | blocking |
| `ERR:le003_brain_missing` | LE003_BRAIN_MISSING | Falta brain.cortex. | Crear brain válido y completar FCS/OBJ. | blocking |
| `ERR:le004_policy_invalid` | LE004_POLICY_INVALID | Policy estructuralmente inválida. | Ejecutar policy validate y corregir entrada indicada. | blocking |
| `ERR:le005_condition_invalid` | LE005_CONDITION_INVALID | Condición DSL inválida. | Usar cláusulas seguras field op value separadas por \|. | blocking |
| `ERR:le006_index_stale` | LE006_INDEX_STALE | Hash de brain/policy no coincide. | Rebuild/scan del índice. | blocking |
| `ERR:le007_protected_sigil` | LE007_PROTECTED_SIGIL | Target protegido. | Requerir confirmación o admin_policy válida. | blocking |
| `ERR:le008_elevation_blocked` | LE008_ELEVATION_BLOCKED | Gate/policy bloqueó elevación. | Inspeccionar explain, protected y policy conditions. | blocking |
| `ERR:le009_candidate_not_found` | LE009_CANDIDATE_NOT_FOUND | Candidate id inexistente. | Regenerar/listar candidates y usar id actual. | blocking |
| `ERR:le010_policy_not_found` | LE010_POLICY_NOT_FOUND | Policy id inexistente. | Mostrar policies y seleccionar una válida. | blocking |
| `ERR:le011_forbidden_eval` | LE011_FORBIDDEN_EVAL | Se intentó evaluación dinámica. | Eliminar eval/exec/compile; usar DSL segura. | blocking |
| `ERR:le012_index_hash_mismatch` | LE012_INDEX_HASH_MISMATCH | Índice no corresponde a fuentes. | Borrar/reconstruir índice. | blocking |
| `ERR:le013_dry_run_required` | LE013_DRY_RUN_REQUIRED | Apply sin dry-run/confirm. | Mostrar diff y repetir con confirmación explícita. | blocking |
| `ERR:e_view_unknown_kind` | E_VIEW_UNKNOWN_KIND | VIEW kind ausente/desconocido. | Elegir kind de VALID_KINDS. | blocking |
| `ERR:e_view_empty_target` | E_VIEW_EMPTY_TARGET | VIEW target vacío. | Definir selector resoluble. | blocking |
| `ERR:e_view_unknown_reverse` | E_VIEW_UNKNOWN_REVERSE | Reverse ausente/desconocido. | Elegir estrategia válida. | blocking |
| `ERR:e_view_incompatible_reverse` | E_VIEW_INCOMPATIBLE_REVERSE | kind/reverse incompatibles. | Usar matriz KIND_REVERSE_COMPAT. | blocking |
| `ERR:e_view_duplicate_name` | E_VIEW_DUPLICATE_NAME | VIEW name duplicado. | Renombrar para unicidad global. | blocking |
| `ERR:e_view_hash_mismatch` | E_VIEW_HASH_MISMATCH | Contenido no coincide con hash VIEW. | Detener y revisar modificación/preservación. | blocking |
| `ERR:e_view_reverse_unsupported` | E_VIEW_REVERSE_UNSUPPORTED | Reverse reconocido pero no implementado en encoder. | Usar estrategia implementada o manual_review explícito. | blocking |
| `ERR:w_view_unused_entry` | W_VIEW_UNUSED_ENTRY | Entrada elegible sin VIEW. | Agregar target; cobertura debe llegar a 100% para reversibilidad. | warning |
| `ERR:w_view_unknown_status` | W_VIEW_UNKNOWN_STATUS | Status VIEW desconocido. | Usar cur, planned, deprecated, human_only, generated o edited. | warning |
| `ERR:w_hcortex_display_only` | W_HCORTEX_DISPLAY_ONLY | Salida display sin contrato reversible. | No declarar reversible; regenerar en modo normal/strict. | warning |

<!-- /VIEW:error_atlas -->

<!-- VIEW:dependencies kind=table target="$11:DEP:*" reverse=rows_to_entries fields="component,requires,status,evidence" title="Arquitectura de módulos" status=cur -->
## Arquitectura de módulos

| Source | Component | Requires | Status | Evidence |
|---|---|---|---|---|
| `DEP:core` | cortex.core | lexer, parser, AST, writer, validator, compare, modes, errors, document_kind | current | wheel modules |
| `DEP:glossary` | cortex.glossary | $0 model, resolver, minimal glossary y contracts | current | wheel modules |
| `DEP:hcortex` | cortex.hcortex | READ/EDIT renderers, parser, profiles y recovery | current | wheel modules |
| `DEP:crud` | cortex.crud | selectors, mutations y transacciones atómicas | current | wheel modules |
| `DEP:templates` | cortex.templates | factories brain, skill, package y glosario | current | wheel modules |
| `DEP:v2` | cortex.v2 | parser/writer, VIEW, encoder, HCORTEX parser/renderer y equivalencia | current | wheel modules |
| `DEP:learning` | cortex.learning | workspace, policy, scoring, index, candidates y elevation | current | wheel modules |
| `DEP:security` | cortex.security | secret scanner y signature SHA256 | current | wheel modules |
| `DEP:audit` | cortex.audit | logging opt-in, snapshots, rotation y prune | current | wheel modules |
| `DEP:cli` | cortex.cli | argparse router, commands y E3 wrapper | current | entry point |

<!-- /VIEW:dependencies -->

<!-- VIEW:claims kind=table target="$11:CLAIM:*" reverse=rows_to_entries fields="statement,evidence,status" title="Capacidades y madurez" status=cur -->
## Capacidades y madurez

| Source | Statement | Evidence | Status |
|---|---|---|---|
| `CLAIM:distribution` | PyPI distribuye codec-cortex 0.3.7 para Python >=3.9. | METADATA y cortex --version | current |
| `CLAIM:core_parser` | El pipeline core parsea, valida, serializa y muta artefactos .cortex. | cortex.core y smoke tests | current |
| `CLAIM:v2_roundtrip` | El pipeline v2 soporta roundtrip byte-identical y bidireccional bajo VIEW válido. | roundtrip y roundtrip-bidir | current |
| `CLAIM:view_contract` | VIEW implementa cobertura, render reversible, targets y estrategias de reversión. | cortex.v2.view/view_renderer/encoder | current |
| `CLAIM:learning_engine` | El motor de aprendizaje local determinista está implementado en 0.3.7. | cortex learn --help y módulos learning | current |
| `CLAIM:security_governance` | Secret scan, mutation modes, signature y audit opt-in están implementados. | doctor, verify, audit | current |
| `CLAIM:e3_docs_benchmark` | docstring y benchmark inventory están implementados como comandos E3. | main_e3.py | current |
| `CLAIM:mcp` | Servidor MCP no está implementado en el wheel 0.3.7. | PyPI maturity table y ausencia de módulo | future |

<!-- /VIEW:claims -->

<!-- VIEW:pitfalls kind=table target="$11:PFL:*" reverse=rows_to_entries fields="pattern,effect,prevention,status" title="Antipatrones" status=cur -->
## Antipatrones

| Source | Pattern | Effect | Prevention | Status |
|---|---|---|---|---|
| `PFL:edit_hcortex_read` | Compilar una vista readable. | E010 o pérdida de metadata. | Usar render --mode edit antes de compile. | current |
| `PFL:verify_view_only` | Tratar verify-view como gate completo. | Puede faltar prueba bidireccional. | Añadir roundtrip-bidir y roundtrip byte-identical. | current |
| `PFL:index_as_memory` | Versionar o editar learn-index como canon. | Deriva y stale hashes. | Editar brain/policy y rebuild index. | current |
| `PFL:admin_default` | Operar siempre en admin. | Bypass accidental de protecciones. | Default editor; read-only para auditoría. | current |
| `PFL:silent_force_output` | Aceptar force-write-on-error como resultado final. | Artefacto inválido persistido. | Reservar para diagnóstico y reparar antes de promover. | current |
| `PFL:manual_mass_edit` | Reescribir .cortex manualmente a gran escala. | Drift, errores de comillas y pérdida de contratos. | Usar CRUD/canonicalize/format y comparar. | current |
| `PFL:trust_narrative_version` | Usar versión mencionada en prose sobre runtime. | Operación contra contrato equivocado. | Usar cortex --version y wheel metadata. | current |

<!-- /VIEW:pitfalls -->

---

<!-- VIEW coverage: 100.0% (356 entries covered) -->
