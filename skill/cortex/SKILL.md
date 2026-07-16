```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: codec-cortex.skill.cortex
source_version: 2.0.0
status: specification
-->

$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"Identidad y versión del skill"}
DOM:domain{type:attrs,risk:B,cortex:Semantic,desc:"Dominio y fronteras conceptuales"}
KNW:knowledge{type:attrs,risk:B,cortex:Semantic,desc:"Conocimiento operativo verificable"}
REF:reference{type:attrs,risk:B,cortex:Semantic,desc:"Referencia a fuente o artefacto"}
CLAIM:claim{type:attrs,risk:M,cortex:Prefrontal,desc:"Afirmación de capacidad con evidencia"}
CNST:constraint{type:attrs,risk:H,cortex:Prefrontal,desc:"Restricción no negociable"}
LIM:limit{type:attrs,risk:H,cortex:Prefrontal,desc:"Límite o alcance explícito"}
RSK:risk{type:attrs,risk:M,cortex:Prefrontal,desc:"Riesgo y mitigación"}
AUD:audit{type:attrs,risk:M,cortex:Prefrontal,desc:"Evidencia de verificación"}
PFL:pitfall{type:attrs,risk:M,cortex:Prefrontal,desc:"Antipatrón y prevención"}
DEP:dependency{type:attrs,risk:M,cortex:Semantic,desc:"Componente y dependencia"}
ERR:error{type:attrs,risk:M,cortex:Working,desc:"Código, causa y recuperación"}
HDL:handler{type:attrs-pos,risk:M,cortex:Semantic,desc:"Operación CLI determinista"}
POL:policy{type:attrs,risk:M,cortex:Prefrontal,desc:"Política del motor de aprendizaje"}
THR:threshold{type:attrs,risk:M,cortex:Semantic,desc:"Umbrales deterministas"}
GTE:gate{type:attrs,risk:H,cortex:Prefrontal,desc:"Gate de mutación o elevación"}
PRT:protected{type:attrs,risk:H,cortex:Prefrontal,desc:"Objetivos protegidos"}
VIEW:view{type:attrs,risk:M,cortex:Semantic,desc:"Contrato reversible CORTEX-HCORTEX"}
!:rule{type:attrs,risk:H,cortex:Prefrontal,desc:"Regla compacta obligatoria"}
$0:type_decls{attrs:"key:value pairs; una línea canónica",attrs_pos:"valores posicionales según contrato",cuerpo:"texto semántico multilínea",bloque:"contenido verbatim multilínea",relación:"relación causal dirigida"}
$0:contract_hdl{pos:"operation|status|requires|notes"}
$0:micro_cur{expand:current}
$0:micro_pln{expand:planned}
$0:micro_fut{expand:future}
$0:micro_blk{expand:blocked}
$0:micro_min{expand:minimum}
$0:micro_rec{expand:recovery}
$0:micro_wrk{expand:work}
$0:micro_full{expand:full}
$0:micro_ok{expand:success}
$0:micro_fail{expand:failure}
$0:micro_part{expand:partial}
$0:enum_state{values:"current|planned|future|blocked|done|deprecated|experimental|specification"}
$0:enum_severity{values:"info|warning|blocking"}
$0:enum_priority{values:"low|medium|high"}
$0:enum_survive{values:"min|recovery|work|full"}
$0:enum_plevel{values:"P0|P1|P2|P3|P4|P5"}
$0:enum_mode{values:"read-only|editor|admin"}
$0:enum_view_kind{values:"table|kv_table|matrix|list|numbered_list|checklist|prose|quote|puml|code|callout|section|raw"}
$0:enum_reverse{values:"rows_to_entries|row_to_attrs|columns_to_attrs|items_to_entries|items_to_ordered_entries|items_to_status_entries|body_to_cuerpo|verbatim_to_bloque|callout_to_risk|callout_to_limit|preserve_human_block|ignore_with_warning|manual_review"}

$1
IDN:skill{name:"CODEC-CORTEX Definitive Agent Skill",version:"2.0.0",package_version:"0.3.7",status:specification,nature:"skill",language:"es",authority:"PyPI wheel codec_cortex-0.3.7 plus runtime behavior"}
DOM:protocol{area:"Memoria contextual estructurada para agentes LLM/SLM",canonical:"CORTEX",human_view:"HCORTEX",conversational_output:"CORTEX-OUT",execution:"CLI determinista sin dependencia de LLM",scope:"crear, validar, convertir, mutar, auditar y aprender"}
REF:pypi{path:"https://pypi.org/project/codec-cortex/",role:"distribución publicada",version:"0.3.7",status:current}
REF:wheel{path:"codec_cortex-0.3.7-py3-none-any.whl",role:"artefacto inspeccionado",version:"sha256:b336464ad3b3279b69ce5fce0cc85dc0d0263a11d5cb5f452eea0d4b76cfd764",status:current}
REF:repository{path:"github.com/FidelErnesto03/codec-cortex",role:"repositorio oficial",version:"tag:v0.3.7",status:current}
REF:upstream_skill{path:"skill/cortex/SKILL.md",role:"skill canónico del tag",version:"1.3.0",status:current}
REF:cli_entry{path:"cortex.cli.main_e3:main",role:"entry point de consola",version:"0.3.7",status:current}
REF:package_root{path:"cortex/",role:"implementación Python",version:"0.3.7",status:current}
AUD:wheel_integrity{event:"verificación del wheel",evidence:"SHA256 local coincide con hash publicado b336464ad3b3279b69ce5fce0cc85dc0d0263a11d5cb5f452eea0d4b76cfd764",result:"success",date:"2026-07-15"}
AUD:static_inventory{event:"inspección estática del wheel",evidence:"93 módulos Python; CLI, core, v2, HCORTEX, CRUD, learning, security y audit inspeccionados",result:"success",date:"2026-07-15"}
LIM:version_text_drift{limit:"La distribución y __version__ son 0.3.7, pero descripción y skill upstream aún mencionan v0.3.6 en algunos campos",scope:"Autoridad de ejecución: cortex --version, _version.py y metadata del wheel",status:current,evidence:"PyPI 0.3.7; cortex._version.__version__=0.3.7"}
!runtime_authority{rule:"Ante divergencia documental, usar la versión instalada y el comportamiento reproducible del CLI como autoridad de ejecución.",survive:min}
AUD:definitive_validation{event:"gates de aceptación del skill definitivo",evidence:"verify --kind skill --strict: 0 errores/0 warnings; verify-view: 100% cobertura, 0 errores, 0 warnings; roundtrip: byte-identical; roundtrip-bidir: AST 0 diffs y content 0 diffs; explain-loss: 0 pérdidas",result:"success",date:"2026-07-15"}

$2
KNW:cortex{topic:"CORTEX",content:"Representación densa nativa; fuente canónica operacional y base de verificación.",status:current,evidence:"parser/writer y AST"}
KNW:hcortex{topic:"HCORTEX",content:"Representación humana derivada; reversible solo bajo contrato VIEW válido.",status:current,evidence:"convert y roundtrip-bidir"}
KNW:view{topic:"VIEW",content:"Contrato declarativo de render y reversión: kind, target, reverse, fields, status y metadatos opcionales.",status:current,evidence:"cortex.v2.view"}
KNW:cortex_out{topic:"CORTEX-OUT",content:"Protocolo conversacional; no participa en parse, AST, encode, verify ni roundtrip.",status:specification,evidence:"separación canónica"}
KNW:ast{topic:"AST",content:"Representación interna única para parser, writer, CRUD, comparación y validación del pipeline core.",status:current,evidence:"cortex.core.ast"}
KNW:skill{topic:"SKILL.cortex",content:"Nivel 1: reglas, contratos y comportamiento; nunca estado vivo.",status:current,evidence:"document_kind policy"}
KNW:brain{topic:"brain.cortex",content:"Nivel 2: estado vivo persistente; requiere FCS y OBJ activos.",status:current,evidence:"document_kind policy"}
KNW:package{topic:"package.cortex",content:"Nivel 3: contexto transportable; la implementación 0.3.7 bloquea estado vivo.",status:current,evidence:"E029_LEVEL3_LIVE_STATE"}
KNW:glossary{topic:"$0",content:"Glosario local mínimo, primero y exclusivamente estructural.",status:current,evidence:"E001 E002 E033"}
KNW:canonical_derived{topic:"Canon",content:"CORTEX y políticas explícitas son canónicos; HCORTEX, índice de aprendizaje e imágenes son derivados.",status:current,evidence:"writer/index contracts"}
KNW:determinism{topic:"Determinismo",content:"Misma entrada, política y versión deben producir AST, scores y serialización equivalentes.",status:current,evidence:"sin LLM ni eval"}
KNW:dual_pipeline{topic:"Dos superficies",content:"core atiende render/compile/CRUD; v2 atiende VIEW, convert, equivalencia y roundtrip bidireccional.",status:current,evidence:"módulos core y v2"}
CNST:source_canonical{rule:"No modificar una vista derivada como si fuera la fuente canónica.",severity:blocking,survive:min,evidence:"CORTEX es fuente operacional"}
CNST:no_silent_inference{rule:"No inferir tipo de entrada, contrato, cardinalidad, estado o reversibilidad sin declaración o evidencia.",severity:blocking,survive:min,evidence:"parsers deterministas"}
CNST:cortex_out_separate{rule:"CORTEX-OUT no debe codificarse ni verificarse como artefacto .cortex.",severity:blocking,survive:min,evidence:"modelo conceptual"}
CNST:no_llm_dependency{rule:"La operación del codec no debe depender de razonamiento probabilístico ni servicios LLM.",severity:blocking,survive:min,evidence:"package design"}
CNST:derived_rebuildable{rule:"Índices, renders y salidas derivadas deben poder reconstruirse desde fuentes canónicas.",severity:warning,survive:recovery,evidence:"learning index y HCORTEX"}
!skill_governs{rule:"SKILL gobierna; brain opera; package transporta; HCORTEX explica; CORTEX-OUT responde.",survive:min}
!minimum_read{rule:"Leer primero identidad, constraints blocking, foco y objetivo; cargar histórico solo por necesidad.",survive:recovery}
!evidence_before_maturity{rule:"No declarar current una capacidad sin comando, módulo o prueba reproducible.",survive:min}

$3
KNW:attrs{topic:"Tipo attrs",content:"Pares key:value; valores bare tipados o strings entre comillas.",status:current,evidence:"core.parser.parse_attrs_body"}
KNW:attrs_pos{topic:"Tipo attrs-pos",content:"Valores ordenados por contrato local; exceso de aridad es error.",status:current,evidence:"E007 y E027"}
KNW:cuerpo{topic:"Tipo cuerpo",content:"Texto semántico entre llaves; preserva contenido no estructurable.",status:current,evidence:"core parser y HCORTEX prose"}
KNW:bloque{topic:"Tipo bloque",content:"Contenido multilínea verbatim; DIAG debe preservarse sin reinterpretación.",status:current,evidence:"Entry.raw y view verbatim"}
KNW:relacion{topic:"Tipo relación",content:"Forma causal dirigida; usar solo cuando el significado de la relación sea explícito.",status:current,evidence:"tipo canónico"}
KNW:sections{topic:"Secciones",content:"Aceptar 2, $2 o $2: título y normalizar internamente a $2.",status:current,evidence:"normalize_section_id"}
KNW:selector{topic:"Selector",content:"SIGIL:name; calificar por sección cuando exista ambigüedad.",status:current,evidence:"crud.selectors"}
KNW:entry_hash{topic:"Hash de entrada",content:"Hash estructural sobre sigil, name, type y value; bloque incluye raw.",status:current,evidence:"compute_entry_hash"}
KNW:document_hash{topic:"Hash de documento",content:"SHA256 sobre bytes/texto canónico según operación.",status:current,evidence:"roundtrip y signature"}
KNW:microtokens{topic:"Microtokens",content:"Expandir solo por delimitador y nunca dentro de palabras.",status:current,evidence:"glossary resolver"}
KNW:naming{topic:"Nombres",content:"Sigilos en mayúsculas salvo !; instancias en snake_case; aliases públicos sin prefijo v2.",status:current,evidence:"canon CLI"}
KNW:survive{topic:"Survive",content:"min→P0; recovery→P1; work→P2; full→P5.",status:current,evidence:"SURVIVE_TO_PLEVEL"}
KNW:contract_fcs{topic:"Contrato crítico",content:"FCS: what,priority,status,survive",status:current,evidence:"cortex.core.validator.REQUIRED_FIELDS"}
KNW:contract_obj{topic:"Contrato crítico",content:"OBJ: goal,status,success,survive",status:current,evidence:"cortex.core.validator.REQUIRED_FIELDS"}
KNW:contract_wrk{topic:"Contrato crítico",content:"WRK: phase,current,blocked,survive",status:current,evidence:"cortex.core.validator.REQUIRED_FIELDS"}
KNW:contract_stp{topic:"Contrato crítico",content:"STP: action,reason,owner,status,survive",status:current,evidence:"cortex.core.validator.REQUIRED_FIELDS"}
KNW:contract_cnst{topic:"Contrato crítico",content:"CNST: rule,severity,survive",status:current,evidence:"cortex.core.validator.REQUIRED_FIELDS"}
KNW:contract_claim{topic:"Contrato crítico",content:"CLAIM: statement,evidence,status",status:current,evidence:"cortex.core.validator.REQUIRED_FIELDS"}
KNW:contract_lim{topic:"Contrato crítico",content:"LIM: limit,scope,status",status:current,evidence:"cortex.core.validator.REQUIRED_FIELDS"}
KNW:contract_rsk{topic:"Contrato crítico",content:"RSK: risk,impact,mitigation,status,survive",status:current,evidence:"cortex.core.validator.REQUIRED_FIELDS"}
KNW:contract_aud{topic:"Contrato crítico",content:"AUD: event,evidence,result,date",status:current,evidence:"cortex.core.validator.REQUIRED_FIELDS"}
KNW:contract_ses{topic:"Contrato crítico",content:"SES: input,output,outcome,date",status:current,evidence:"cortex.core.validator.REQUIRED_FIELDS"}
KNW:contract_lng{topic:"Contrato crítico",content:"LNG: type,cause,lesson,prevention",status:current,evidence:"cortex.core.validator.REQUIRED_FIELDS"}
KNW:contract_knw{topic:"Contrato crítico",content:"KNW: topic,content,status",status:current,evidence:"cortex.core.validator.REQUIRED_FIELDS"}
CNST:glossary_required{rule:"Todo artefacto .cortex debe contener $0 local.",severity:blocking,survive:min,evidence:"E001"}
CNST:glossary_first{rule:"$0 debe ser la primera sección.",severity:blocking,survive:min,evidence:"E002"}
CNST:glossary_structural{rule:"$0 no puede contener memoria operacional.",severity:blocking,survive:min,evidence:"E033 no bypassable"}
CNST:declare_sigil{rule:"Cada sigilo debe declararse antes de su uso.",severity:blocking,survive:min,evidence:"E003"}
CNST:declare_type{rule:"Cada tipo referenciado debe estar declarado.",severity:blocking,survive:min,evidence:"E004"}
CNST:attrs_pos_contract{rule:"Cada attrs-pos requiere contrato y aridad exacta.",severity:blocking,survive:min,evidence:"E007 E027"}
CNST:critical_complete{rule:"Sigilos críticos deben incluir todos sus campos requeridos.",severity:blocking,survive:min,evidence:"E032"}
CNST:critical_nonempty{rule:"Campos críticos no aceptan vacío ni null-like: null, none, nil, undefined, n/a, tbd, todo, ?, -.",severity:blocking,survive:min,evidence:"E034"}
CNST:no_duplicate{rule:"No duplicar SIGIL:name dentro de la misma sección.",severity:blocking,survive:min,evidence:"E008"}
!type_strict{rule:"Resolver el tipo desde $0; no usar heurística de contenido.",survive:min}
!canonical_write{rule:"Serializar mediante writer o CLI; evitar edición manual cuando una mutación determinista exista.",survive:recovery}
!unknown_line{rule:"Toda línea no parseada debe corregirse o recuperarse; nunca ignorarla silenciosamente en un artefacto gobernado.",survive:recovery}
!priority_order{rule:"Cargar P0→P5; al degradar eliminar P5 primero y nunca eliminar P0.",survive:min}

$4
KNW:skill_kind{topic:"Documento skill",content:"IDN:skill o filename skill.*; L1 sin estado vivo.",status:current,evidence:"infer_document_kind"}
KNW:brain_kind{topic:"Documento brain",content:"IDN:agent o FCS+WRK; L2 requiere FCS y OBJ activos.",status:current,evidence:"infer_document_kind"}
KNW:package_kind{topic:"Documento package",content:"IDN:package o CLAIM+LIM sin WRK; L3 sin estado vivo en 0.3.7.",status:current,evidence:"infer_document_kind"}
KNW:generic_kind{topic:"Documento generic",content:"Sin firma suficiente; aplicar solo reglas estructurales comunes.",status:current,evidence:"default inference"}
KNW:inference_order{topic:"Inferencia de kind",content:"IDN.kind/name > filename > firma de sigilos > generic.",status:current,evidence:"document_kind.py"}
KNW:live_state{topic:"Estado vivo",content:"FCS,OBJ,WRK,STP,NXT,SES,LNG; una entrada marcada example/template/non_operational/contract/specification no es viva.",status:current,evidence:"_is_live_entry"}
KNW:active_focus{topic:"Foco activo",content:"FCS y OBJ cuentan como activos solo con status current o blocked; done es cerrado.",status:current,evidence:"E024"}
CNST:l1_no_live_state{rule:"Skill no puede contener FCS,OBJ,WRK,STP,NXT,SES o LNG vivos.",severity:blocking,survive:min,evidence:"E023"}
CNST:l2_focus_objective{rule:"Brain debe contener al menos un FCS y un OBJ activos.",severity:blocking,survive:min,evidence:"E024"}
CNST:l3_no_live_state{rule:"Package no puede contener estado vivo en la implementación 0.3.7.",severity:blocking,survive:min,evidence:"E029"}
CNST:survive_domain{rule:"survive solo admite min,recovery,work,full.",severity:blocking,survive:min,evidence:"E025"}
CNST:blocking_is_p0{rule:"CNST severity blocking debe usar survive min.",severity:blocking,survive:min,evidence:"E026"}
CNST:explicit_kind_audit{rule:"En auditoría o migración usar verify --kind para evitar inferencia incorrecta.",severity:warning,survive:recovery,evidence:"CLI override"}
RSK:kind_misclassification{risk:"El filename o firma de sigilos puede inducir kind incorrecto.",impact:"Se aplican gates cognitivos inadecuados.",mitigation:"Usar --kind brain|skill|package|generic en verify/doctor y corregir IDN.",status:current,survive:recovery}
!verify_on_load{rule:"Al cargar un artefacto gobernado ejecutar verify --strict con kind explícito cuando sea conocido.",survive:min}
!verify_before_commit{rule:"Antes de persistir o commitear ejecutar verify/verify-view y el roundtrip aplicable.",survive:min}

$5
HDL:version|reportar versión instalada|current|ninguno|cortex --version; autoridad primaria de versión
HDL:new|crear artefacto desde template|current|kind y --out|brain,skill,package,generic; minimal,standard,enterprise; --with-diagrams
HDL:render|decodificar CORTEX core a HCORTEX|current|input .cortex|alias decode; readable/edit/audit/recovery/full; profile y layout
HDL:compile|codificar HCORTEX-EDIT a CORTEX core|current|input HCORTEX-EDIT y --out|alias encode; requiere metadatos editables
HDL:verify|validar estructura y gobierno|current|input|--strict; --kind; --roundtrip; --signature/--manifest
HDL:get|obtener una entrada|current|input y selector|text o json; calificar selector si es ambiguo
HDL:list|listar entradas|current|input|filtros --section y --sigil; text o json
HDL:add|agregar entrada|current|input, section, sigil, name, value|dry-run; validación post-write; flags de recuperación explícitos
HDL:update|actualizar entrada|current|input y selector|--set repetible o --body; --append; dry-run
HDL:delete|eliminar entrada|current|input y selector|protecciones; dry-run; force solo autorizado
HDL:move|mover entrada de sección|current|input, selector, --to-section|validación posterior y dry-run
HDL:glossary|CRUD de sigilos en $0|current|subcomando list/add/update/delete|no eliminar sigilo reservado o en uso
HDL:micro|CRUD de microtokens|current|subcomando list/add/update/delete|no eliminar token en uso
HDL:doctor|diagnóstico profundo|current|input|strict/kind; secret scan; paths adicionales; baseline
HDL:diff|comparar documentos core|current|left y right|profiles structural,semantic,governance
HDL:format|serializar canónicamente pipeline core|current|input|--out o in-place; dry-run
HDL:recover|recuperar artefacto legacy/no conforme|current|input|--strict; --embed-aud-rsk; revisar salida antes de aceptar
HDL:diagram|operar entradas DIAG|current|list,extract,validate|extracción verbatim y validación de integridad
HDL:audit|controlar auditoría opt-in|current|on,off,status,snapshot,prune|logging apagado por defecto; JSONL fuera del repo
HDL:roundtrip|verificar roundtrip CORTEX v2|current|input CORTEX v2|comparación byte-identical
HDL:convert|convertir CORTEX v2 y HCORTEX|current|--from y --to|normal,strict,audit,recovery,display; hcortex-r deprecated
HDL:roundtrip_bidir|verificar CORTEX-HCORTEX bidireccional|current|input con header CODEC-CORTEX|AST-equivalent y content-equivalent
HDL:compare|comparar equivalencia v2|current|left y right|byte, AST, semantic y content; --verbose
HDL:verify_view|validar VIEW|current|input CORTEX v2|cobertura, errores y warnings; no sustituye roundtrip-bidir
HDL:explain_loss|explicar pérdida/no reversibilidad|current|input CORTEX o HCORTEX|reporta omisión, fallback y contenido no reversible
HDL:canonicalize|normalizar artefacto v2|current|input|VIEW-aware; --preserve conserva estructura y normaliza whitespace/orden
HDL:inspect|inspeccionar AST y VIEW|current|input|secciones, sigilos, tipos, cobertura, formato y diagnósticos
HDL:docstring|derivar documentación CLI|current|command o --all|lee docs/cortex/api cuando están disponibles
HDL:benchmark|inventariar suites benchmark|current|--root/--suite/--list|no ejecuta modelos; inventaria suites
HDL:learn|motor de aprendizaje local|current|workspace y subcomando|init,doctor,policy,index,scan,candidates,explain,elevate,profile
HDL:learn_init|inicializar workspace de aprendizaje|current|--workspace|crea MANIFEST, brain, policies, index y cache
HDL:learn_doctor|validar workspace de aprendizaje|current|--workspace|comprueba directorio, manifest, brain, policy e índice
HDL:learn_policy|gestionar políticas|current|show,validate,apply,add|apply requiere archivo; dry-run y confirm
HDL:learn_index|gestionar índice derivado|current|rebuild,status,clean|índice no canónico y reconstruible
HDL:learn_scan|puntuar brain e indexar|current|--workspace|genera scores deterministas y hash de brain/policy
HDL:learn_candidates|listar candidatos|current|--workspace|orden por promotion y hotness; --limit
HDL:learn_explain|explicar candidato|current|--candidate|muestra fuentes, scores, policy y thresholds
HDL:learn_elevate|planificar/aplicar elevación|current|--candidate o --policy|dry-run por defecto; --apply y --confirm para escribir
HDL:learn_profile|crear perfil de carga|current|--budget|selecciona por read_priority dentro del presupuesto

$6
KNW:mode_read_only{topic:"Modo read-only",content:"Permite lectura, inspección, verificación, render y comparación; bloquea mutaciones.",status:current,evidence:"E035"}
KNW:mode_editor{topic:"Modo editor",content:"Default; permite escritura y pide confirmación interactiva para --force.",status:current,evidence:"modes.py"}
KNW:mode_admin{topic:"Modo admin",content:"Permite force sin confirmación; debe ser selección consciente y acotada.",status:current,evidence:"modes.py"}
KNW:mode_precedence{topic:"Resolución de modo",content:"--mode > CORTEX_MODE > editor.",status:current,evidence:"resolve_mode"}
KNW:atomic_write{topic:"Escritura atómica",content:"Mutaciones se escriben mediante archivo temporal y replace; fallo produce E015.",status:current,evidence:"crud.transactions"}
KNW:post_validation{topic:"Validación posterior",content:"Mutaciones validan antes de persistir por defecto; strict-write eleva warnings.",status:current,evidence:"CRUD commands"}
KNW:protected_entries{topic:"Entradas protegidas",content:"FCS,OBJ,CNST blocking o survive min requieren force/autorización.",status:current,evidence:"is_protected_entry"}
KNW:secret_scan{topic:"Secret scanner",content:"Doctor escanea claves, passwords, tokens, AWS secrets, private keys y URLs con credenciales.",status:current,evidence:"security.secret_scanner"}
KNW:signature{topic:"Firma SHA256",content:"verify --signature/--manifest compara input contra SHA256SUMS.",status:current,evidence:"security.signature"}
KNW:audit_log{topic:"Audit log",content:"Opt-in, append-only, rotación diaria, fuera del repo; snapshots one-shot.",status:current,evidence:"audit.logger"}
CNST:no_clear_secrets{rule:"No almacenar secretos en claro; usar REF a proveedor/clave.",severity:blocking,survive:min,evidence:"E031 no bypassable con force"}
CNST:read_only_hard{rule:"No ejecutar write commands bajo modo read-only.",severity:blocking,survive:min,evidence:"E035"}
CNST:dry_run_first{rule:"Toda mutación riesgosa o elevación debe mostrar diff/dry-run antes de aplicar.",severity:blocking,survive:min,evidence:"learning gate y CRUD"}
CNST:post_write_verify{rule:"Después de mutar, volver a parsear, validar y verificar el gate aplicable.",severity:blocking,survive:min,evidence:"transactions/elevation"}
CNST:audit_opt_in{rule:"No afirmar que existe log de auditoría si audit status está off.",severity:warning,survive:recovery,evidence:"E038"}
RSK:skip_validation{risk:"--no-validate-write puede persistir estructura o gobierno inválidos.",impact:"Corrupción semántica o pérdida de continuidad.",mitigation:"Reservar para recuperación controlada; ejecutar verify --strict inmediatamente.",status:current,survive:recovery}
RSK:forensic_secret_bypass{risk:"--unsafe-allow-secret-forensics permite material sensible.",impact:"Exposición de credenciales en memoria, logs o repositorio.",mitigation:"Usar solo en entorno aislado, temporal y autorizado; redacción y eliminación posterior.",status:current,survive:min}
!mutation_sequence{rule:"Preflight inspect/verify → dry-run/diff → mutación mínima → verify estricto → roundtrip aplicable → audit/evidence.",survive:min}
!least_privilege{rule:"Usar read-only para auditoría, editor para trabajo normal y admin solo durante la operación que lo exige.",survive:min}

$7
KNW:profile_min{topic:"HCORTEX MIN",content:"P0; presupuesto aproximado 512 tokens.",status:current,evidence:"hcortex.profiles"}
KNW:profile_recovery{topic:"HCORTEX RECOVERY",content:"P0-P1; presupuesto aproximado 1024 tokens.",status:current,evidence:"hcortex.profiles"}
KNW:profile_work{topic:"HCORTEX WORK",content:"P0-P2; presupuesto aproximado 3072 tokens; default.",status:current,evidence:"hcortex.profiles"}
KNW:profile_full{topic:"HCORTEX FULL",content:"P0-P5; sin presupuesto fijo.",status:current,evidence:"hcortex.profiles"}
KNW:render_readable{topic:"Render readable",content:"Vista humana limpia; default de render core.",status:current,evidence:"render --mode readable"}
KNW:render_edit{topic:"Render edit",content:"Vista compilable de vuelta por compile; conserva metadata.",status:current,evidence:"render --mode edit"}
KNW:render_audit{topic:"Render audit",content:"Incluye source para trazabilidad.",status:current,evidence:"render --with-source"}
KNW:view_kinds{topic:"VIEW kinds",content:"table,kv_table,matrix,list,numbered_list,checklist,prose,quote,puml,code,callout,section,raw.",status:current,evidence:"VALID_KINDS"}
KNW:view_reverse{topic:"Reverse strategies",content:"rows_to_entries,row_to_attrs,columns_to_attrs,items_to_entries,items_to_ordered_entries,items_to_status_entries,body_to_cuerpo,verbatim_to_bloque,callout_to_risk,callout_to_limit,preserve_human_block,ignore_with_warning,manual_review.",status:current,evidence:"VALID_REVERSES"}
KNW:view_target{topic:"VIEW target",content:"$0 special groups; $N; $N:SIGIL:*; $N:SIGIL:name; SIGIL:*; SIGIL:name; HUMAN_BLOCK.",status:current,evidence:"resolve_target"}
KNW:equivalence{topic:"Niveles de equivalencia",content:"byte-identical, AST-equivalent, semantic-equivalent y content-equivalent.",status:current,evidence:"v2.equivalence"}
KNW:display_mode{topic:"Modo display",content:"Produce Markdown sin contrato reversible; nunca declarar reversible true.",status:current,evidence:"convert --mode display"}
KNW:hcortex_r_alias{topic:"Alias hcortex-r",content:"Deprecated; usar hcortex como nombre canónico.",status:deprecated,evidence:"convert command"}
CNST:reversible_gate{rule:"reversible true exige cobertura VIEW 100%, cero E_VIEW/E_HCORTEX, modo no display y roundtrip canónico aplicable sin pérdida.",severity:blocking,survive:min,evidence:"modelo PyPI y comandos v2"}
CNST:view_compatibility{rule:"kind y reverse deben pertenecer a la matriz de compatibilidad.",severity:blocking,survive:min,evidence:"E_VIEW_INCOMPATIBLE_REVERSE"}
CNST:view_unique{rule:"Cada VIEW name debe ser único y target no vacío.",severity:blocking,survive:min,evidence:"E_VIEW_DUPLICATE_NAME/E_VIEW_EMPTY_TARGET"}
CNST:verbatim_integrity{rule:"PUML/code/bloque reversible debe conservar contenido verbatim y hash cuando se declara.",severity:blocking,survive:min,evidence:"verbatim_to_bloque/E_VIEW_HASH_MISMATCH"}
CNST:no_write_on_view_error{rule:"convert no debe escribir --out si existen errores VIEW salvo force-write-on-error explícito.",severity:blocking,survive:min,evidence:"v2_convert"}
LIM:verify_view_scope{limit:"verify-view calcula cobertura y errores de render, pero no ejecuta por sí solo el roundtrip bidireccional.",scope:"Gate completo = verify-view --strict + roundtrip-bidir; roundtrip añade fidelidad byte-identical CORTEX.",status:current,evidence:"implementación v2_verify_view.py"}
RSK:force_write_invalid_view{risk:"force-write-on-error puede dejar HCORTEX/CORTEX inválido en disco.",impact:"Falsa reversibilidad o pérdida silenciosa.",mitigation:"Usar solo para diagnóstico; ejecutar explain-loss, compare y reparar antes de aceptar.",status:current,survive:recovery}
!view_gate_sequence{rule:"inspect → verify-view --strict → convert estricto → roundtrip-bidir → compare cuando exista artefacto esperado.",survive:min}
!display_not_canonical{rule:"Una salida convertida en mode display es presentación, no HCORTEX canónico reversible.",survive:min}

$8
THR:golden_fibonacci{observed:"1",repeated:"2",pattern:"3",candidate:"5",ask_user:"8",strong_candidate:"13",critical:"21"}
PRT:critical_sigils{items:"IDN|AXM|CNST:blocking|CLAIM|LIM",mutation:"explicit_user_confirmation",status:current}
POL:candidate_detection{target:"index",when:"scan_sigils=WRK,SES,LNG,RSK,NXT,CLAIM,LIM",action:"score",requires:"golden_fibonacci_v1",origin:"brain"}
POL:candidate_elevation{target:"LNG|KNW",when:"promotion_score>=8",action:"propose",requires:"user_confirmation",origin:"SES|LNG"}
POL:auto_ses_to_lng{target:"LNG",when:"promotion_score>=8|user_validated=true",action:"apply",requires:"policy_authorized",origin:"SES"}
POL:auto_lng_to_knw{target:"KNW",when:"promotion_score>=13|user_validated=true|risk_weight>=8",action:"apply",requires:"admin_policy",origin:"LNG"}
GTE:default_mutation{action:"mutate_brain",default:"dry_run_first",targets:"all",status:current}
GTE:critical_mutation{action:"mutate_brain",default:"block_unless_admin_policy",targets:"IDN|AXM|CNST:blocking|CLAIM|LIM|KNW",status:current}
KNW:workspace_manifest{topic:"Workspace",content:".cortex/MANIFEST.cortex es canónico y referencia brain, policy e índice.",status:current,evidence:"learn init"}
KNW:workspace_brain{topic:"Workspace",content:".cortex/brain.cortex es memoria operacional canónica.",status:current,evidence:"learn init"}
KNW:workspace_policy{topic:"Workspace",content:".cortex/learn-policies.cortex define thresholds, policies, gates y protegidos.",status:current,evidence:"learn init"}
KNW:workspace_index{topic:"Workspace",content:".cortex/index/learn-index.json es derivado, hash-aware y reconstruible.",status:current,evidence:"learn index"}
KNW:workspace_cache{topic:"Workspace",content:".cortex/cache es derivado y no canónico.",status:current,evidence:"learn init"}
KNW:signals{topic:"Señales",content:"observed,repeated,pattern,decision_relevant,user_validated,risk_preventing,critical.",status:current,evidence:"learning.scoring"}
KNW:hotness{topic:"Score hotness",content:"Recurrencia, validación y criticidad; floor observed y cap critical.",status:current,evidence:"score_hotness"}
KNW:promotion{topic:"Score promotion",content:"Repetición, patrón, decisión, validación, prevención y criticidad acotada.",status:current,evidence:"score_promotion"}
KNW:risk_weight{topic:"Score risk",content:"Costo de omitir/degradar; decisiones, prevención, protección y baseline por sigilo.",status:current,evidence:"score_risk"}
KNW:read_priority{topic:"Read priority",content:"P0 bloqueo/foco/paso activo; P1 crítico; P2 fuerte/KNW/LNG; P3 candidato; P4 repetido; P5 frío.",status:current,evidence:"derive_read_priority"}
KNW:candidate_targets{topic:"Elevaciones",content:"WRK→SES; SES→LNG; LNG→KNW; RSK→CNST; NXT→STP.",status:current,evidence:"candidates._DEFAULT_TARGET"}
KNW:candidate_cluster{topic:"Clustering",content:"Agrupa por sigilo y primer atributo disponible: topic,outcome,lesson,risk,statement; fallback nombre.",status:current,evidence:"_cluster_key_for"}
KNW:condition_dsl{topic:"Policy condition DSL",content:"Cláusulas AND separadas por |; operadores =,!=,>=,<=,>,<; tipos seguros.",status:current,evidence:"learning.conditions"}
KNW:fingerprint{topic:"Fingerprint",content:"SHA256 del payload normalizado; cambios cosméticos no invalidan índice.",status:current,evidence:"stable_fingerprint"}
KNW:elevation_patch{topic:"Patch de elevación",content:"Plan determinista con diff, target, reason, policy, score y affected_files.",status:current,evidence:"learning.elevation"}
CNST:learning_deterministic{rule:"Mismo brain, policy y versión deben producir los mismos fingerprints, scores y candidatos.",severity:blocking,survive:min,evidence:"scoring side-effect free"}
CNST:no_dynamic_eval{rule:"Policy DSL no puede usar eval, exec, compile ni evaluación AST dinámica.",severity:blocking,survive:min,evidence:"LE011 y conditions.py"}
CNST:index_not_memory{rule:"El índice no es memoria canónica y puede borrarse/reconstruirse.",severity:blocking,survive:min,evidence:"MANIFEST constraint"}
CNST:critical_protected{rule:"Objetivos protegidos no pueden elevarse o mutarse por política común.",severity:blocking,survive:min,evidence:"LE007"}
CNST:apply_confirmed{rule:"Elevación apply requiere confirmación; dry-run es el default.",severity:blocking,survive:min,evidence:"LE013"}
!learning_cycle{rule:"learn doctor → policy validate → scan/index → candidates → explain → elevate dry-run → confirm/apply → verify brain+index.",survive:min}
!policy_authority{rule:"Una política puede proponer o aplicar solo dentro de sus condiciones y gates; protección y confirmación prevalecen.",survive:min}

$9
KNW:startup{topic:"Startup",content:"cortex --version → inspect → detectar kind → verify --strict → cargar P0/P1 → operar.",status:current,evidence:"preflight"}
KNW:create_skill{topic:"Crear skill",content:"new skill → completar $0/IDN/DOM/CNST → verify --kind skill --strict → render audit.",status:current,evidence:"core pipeline"}
KNW:create_brain{topic:"Crear brain",content:"new brain o learn init → completar FCS/OBJ/WRK/STP → verify --kind brain --strict.",status:current,evidence:"L2 gate"}
KNW:read_artifact{topic:"Lectura",content:"inspect/list/get → render readable/audit según audiencia → no mutar.",status:current,evidence:"read-only mode"}
KNW:mutate_artifact{topic:"Mutación",content:"inspect+verify → dry-run → add/update/delete/move → verify estricto → diff/roundtrip.",status:current,evidence:"transaction gate"}
KNW:v2_conversion{topic:"Conversión reversible",content:"verify-view --strict → convert strict → roundtrip-bidir → compare.",status:current,evidence:"VIEW gate"}
KNW:recovery{topic:"Recuperación",content:"recover --embed-aud-rsk → inspect → doctor --strict → corregir → verify/roundtrip.",status:current,evidence:"recovery pipeline"}
KNW:security{topic:"Seguridad",content:"doctor --scan-secrets → eliminar secretos → verify signature cuando exista manifest.",status:current,evidence:"E2"}
KNW:learning{topic:"Aprendizaje",content:"learn doctor → validate policy → scan → candidates → explain → dry-run → confirm apply.",status:current,evidence:"learning engine"}
KNW:audit{topic:"Auditoría",content:"audit on solo si se requiere → operar → status/snapshot → audit off → prune según política.",status:current,evidence:"opt-in audit"}
KNW:release{topic:"Cierre",content:"tests → verify/roundtrip → secret scan → signature → evidencia AUD → publicar artefacto derivado.",status:current,evidence:"release gate"}
!read_before_write{rule:"Nunca mutar un artefacto que no haya sido inspeccionado y validado en la sesión actual.",survive:min}
!smallest_patch{rule:"Aplicar el cambio estructural mínimo; no reformatear ni reescribir contenido no relacionado.",survive:min}
!stop_on_blocking{rule:"Ante error blocking o gate no satisfecho, detener escritura y devolver causa+recuperación.",survive:min}
!truthful_status{rule:"No declarar verificación, render o reversibilidad si el comando correspondiente no fue ejecutado.",survive:min}
!derived_after_canon{rule:"Generar HCORTEX, índices, diagramas o reportes después de estabilizar la fuente canónica.",survive:min}

$10
ERR:e001_missing_glossary{code:"E001_MISSING_GLOSSARY",cause:"Falta $0.",recovery:"Agregar glosario local mínimo como primera sección.",severity:blocking}
ERR:e002_glossary_not_first{code:"E002_GLOSSARY_NOT_FIRST",cause:"$0 no es primera sección.",recovery:"Mover $0 al inicio y volver a parsear.",severity:blocking}
ERR:e003_unknown_sigil{code:"E003_UNKNOWN_SIGIL",cause:"Sigilo usado no declarado.",recovery:"Declararlo en $0 antes del uso.",severity:blocking}
ERR:e004_unknown_type{code:"E004_UNKNOWN_TYPE",cause:"Tipo de sigilo no declarado.",recovery:"Registrar tipo canónico en $0.",severity:blocking}
ERR:e005_unbalanced_braces{code:"E005_UNBALANCED_BRACES",cause:"Llaves sin balance.",recovery:"Corregir el primer bloque abierto/cerrado incorrectamente.",severity:blocking}
ERR:e006_invalid_attrs{code:"E006_INVALID_ATTRS",cause:"Cuerpo attrs inválido.",recovery:"Corregir pares key:value, comillas y separadores.",severity:blocking}
ERR:e007_attrs_pos_contract_missing{code:"E007_ATTRS_POS_CONTRACT_MISSING",cause:"attrs-pos sin contrato.",recovery:"Agregar contract_<sigil> con pos exacto.",severity:blocking}
ERR:e008_duplicate_entry{code:"E008_DUPLICATE_ENTRY",cause:"SIGIL:name duplicado en sección.",recovery:"Renombrar, fusionar o eliminar duplicado.",severity:blocking}
ERR:e009_protected_entry{code:"E009_PROTECTED_ENTRY",cause:"Mutación sobre entrada protegida.",recovery:"Revisar impacto y usar autorización/force solo si procede.",severity:blocking}
ERR:e010_hcortex_read_not_compilable{code:"E010_HCORTEX_READ_NOT_COMPILABLE",cause:"Vista readable no compilable.",recovery:"Generar HCORTEX edit y usar compile.",severity:blocking}
ERR:e011_hcortex_edit_metadata_missing{code:"E011_HCORTEX_EDIT_METADATA_MISSING",cause:"HCORTEX edit perdió metadata.",recovery:"Regenerar vista edit y preservar marcadores.",severity:blocking}
ERR:e012_roundtrip_failed{code:"E012_ROUNDTRIP_FAILED",cause:"Roundtrip no equivalente.",recovery:"Ejecutar compare/explain-loss y reparar primera diferencia.",severity:blocking}
ERR:e013_not_found{code:"E013_NOT_FOUND",cause:"Archivo o candidato inexistente.",recovery:"Corregir path/selector/id y repetir.",severity:blocking}
ERR:e014_ambiguous_selector{code:"E014_AMBIGUOUS_SELECTOR",cause:"Selector coincide con varias entradas.",recovery:"Calificar con sección o selector exacto.",severity:blocking}
ERR:e015_atomic_write_failed{code:"E015_ATOMIC_WRITE_FAILED",cause:"Falló escritura atómica.",recovery:"Revisar permisos, espacio y archivo temporal; no aceptar parcial.",severity:blocking}
ERR:e016_invalid_section_header{code:"E016_INVALID_SECTION_HEADER",cause:"Header de sección inválido.",recovery:"Normalizar a $N o $N: TÍTULO.",severity:blocking}
ERR:e017_unparsed_line{code:"E017_UNPARSED_LINE",cause:"Línea no reconocida.",recovery:"Codificarla como entrada/comentario válido o recuperar.",severity:blocking}
ERR:e018_protected_sigil{code:"E018_PROTECTED_SIGIL",cause:"Intento de borrar sigilo reservado.",recovery:"Mantenerlo o migrar con procedimiento explícito.",severity:blocking}
ERR:e019_sigil_in_use{code:"E019_SIGIL_IN_USE",cause:"Sigilo aún referenciado.",recovery:"Migrar/eliminar instancias antes de quitar declaración.",severity:blocking}
ERR:e020_micro_in_use{code:"E020_MICRO_IN_USE",cause:"Microtoken aún usado.",recovery:"Expandir o migrar usos antes de borrarlo.",severity:blocking}
ERR:e021_invalid_value{code:"E021_INVALID_VALUE",cause:"Valor/opción fuera de contrato.",recovery:"Usar enum, formato o combinación soportada.",severity:blocking}
ERR:e022_template_unknown{code:"E022_TEMPLATE_UNKNOWN",cause:"Template inexistente.",recovery:"Elegir minimal, standard o enterprise.",severity:blocking}
ERR:e023_level1_live_state{code:"E023_LEVEL1_LIVE_STATE",cause:"Skill contiene estado vivo.",recovery:"Eliminarlo o marcarlo contract/example/specification.",severity:blocking}
ERR:e024_level2_missing_focus{code:"E024_LEVEL2_MISSING_FOCUS",cause:"Brain sin FCS/OBJ activos.",recovery:"Crear entradas completas status current|blocked.",severity:blocking}
ERR:e025_invalid_survive{code:"E025_INVALID_SURVIVE",cause:"survive fuera de dominio.",recovery:"Usar min,recovery,work o full.",severity:blocking}
ERR:e026_blocking_not_p0{code:"E026_BLOCKING_NOT_P0",cause:"CNST blocking no usa survive min.",recovery:"Cambiar survive a min.",severity:blocking}
ERR:e027_attrs_pos_arity{code:"E027_ATTRS_POS_ARITY",cause:"Aridad excede contrato.",recovery:"Ajustar valores o contrato sin pérdida.",severity:blocking}
ERR:e028_secret_in_clear{code:"E028_SECRET_IN_CLEAR",cause:"Secreto en claro.",recovery:"Eliminarlo y usar REF; rotar credencial si fue expuesta.",severity:blocking}
ERR:e029_level3_live_state{code:"E029_LEVEL3_LIVE_STATE",cause:"Package contiene estado vivo.",recovery:"Retirar estado operativo o moverlo a brain.",severity:blocking}
ERR:e030_recovery_incomplete{code:"E030_RECOVERY_INCOMPLETE",cause:"Recuperación dejó ambigüedad/pérdida.",recovery:"Revisión humana y evidencia AUD/RSK antes de aceptar.",severity:blocking}
ERR:e031_secret_not_bypassable{code:"E031_SECRET_NOT_BYPASSABLE",cause:"Secreto no bypassable por force.",recovery:"Redactar y usar REF; forensic flag solo en entorno autorizado.",severity:blocking}
ERR:e032_critical_sigil_incomplete{code:"E032_CRITICAL_SIGIL_INCOMPLETE",cause:"Faltan campos críticos.",recovery:"Completar contrato requerido antes de persistir.",severity:blocking}
ERR:e033_zero_section_memory_entry{code:"E033_ZERO_SECTION_MEMORY_ENTRY",cause:"Entrada operacional oculta en $0.",recovery:"Moverla a $1+; $0 es solo metadata/glosario.",severity:blocking}
ERR:e034_critical_required_field_empty{code:"E034_CRITICAL_REQUIRED_FIELD_EMPTY",cause:"Campo crítico vacío/null-like.",recovery:"Proveer valor semántico real.",severity:blocking}
ERR:e035_mode_read_only{code:"E035_MODE_READ_ONLY",cause:"Write command en read-only.",recovery:"Cambiar conscientemente a editor/admin.",severity:blocking}
ERR:e036_mode_editor_confirm{code:"E036_MODE_EDITOR_CONFIRM",cause:"Force sin confirmación interactiva.",recovery:"Confirmar, usar --yes o admin autorizado.",severity:blocking}
ERR:e037_mode_unknown{code:"E037_MODE_UNKNOWN",cause:"Modo no reconocido.",recovery:"Usar read-only, editor o admin.",severity:blocking}
ERR:e038_audit_logging_off{code:"E038_AUDIT_LOGGING_OFF",cause:"Se esperaba audit pero está off.",recovery:"Ejecutar audit on o declarar ausencia de log.",severity:blocking}
ERR:e039_signature_mismatch{code:"E039_SIGNATURE_MISMATCH",cause:"SHA256 no coincide con manifest.",recovery:"Detener; verificar archivo, manifest y procedencia.",severity:blocking}
ERR:e040_secret_detected{code:"E040_SECRET_DETECTED",cause:"Secret scanner detectó hallazgo alto.",recovery:"Redactar/rotar o justificar en baseline controlado.",severity:blocking}
ERR:le001_workspace_not_found{code:"LE001_WORKSPACE_NOT_FOUND",cause:"Workspace .cortex no encontrado.",recovery:"Ejecutar learn init o indicar --workspace correcto.",severity:blocking}
ERR:le002_manifest_missing{code:"LE002_MANIFEST_MISSING",cause:"Falta MANIFEST.cortex.",recovery:"Restaurar/recrear manifest canónico.",severity:blocking}
ERR:le003_brain_missing{code:"LE003_BRAIN_MISSING",cause:"Falta brain.cortex.",recovery:"Crear brain válido y completar FCS/OBJ.",severity:blocking}
ERR:le004_policy_invalid{code:"LE004_POLICY_INVALID",cause:"Policy estructuralmente inválida.",recovery:"Ejecutar policy validate y corregir entrada indicada.",severity:blocking}
ERR:le005_condition_invalid{code:"LE005_CONDITION_INVALID",cause:"Condición DSL inválida.",recovery:"Usar cláusulas seguras field op value separadas por |.",severity:blocking}
ERR:le006_index_stale{code:"LE006_INDEX_STALE",cause:"Hash de brain/policy no coincide.",recovery:"Rebuild/scan del índice.",severity:blocking}
ERR:le007_protected_sigil{code:"LE007_PROTECTED_SIGIL",cause:"Target protegido.",recovery:"Requerir confirmación o admin_policy válida.",severity:blocking}
ERR:le008_elevation_blocked{code:"LE008_ELEVATION_BLOCKED",cause:"Gate/policy bloqueó elevación.",recovery:"Inspeccionar explain, protected y policy conditions.",severity:blocking}
ERR:le009_candidate_not_found{code:"LE009_CANDIDATE_NOT_FOUND",cause:"Candidate id inexistente.",recovery:"Regenerar/listar candidates y usar id actual.",severity:blocking}
ERR:le010_policy_not_found{code:"LE010_POLICY_NOT_FOUND",cause:"Policy id inexistente.",recovery:"Mostrar policies y seleccionar una válida.",severity:blocking}
ERR:le011_forbidden_eval{code:"LE011_FORBIDDEN_EVAL",cause:"Se intentó evaluación dinámica.",recovery:"Eliminar eval/exec/compile; usar DSL segura.",severity:blocking}
ERR:le012_index_hash_mismatch{code:"LE012_INDEX_HASH_MISMATCH",cause:"Índice no corresponde a fuentes.",recovery:"Borrar/reconstruir índice.",severity:blocking}
ERR:le013_dry_run_required{code:"LE013_DRY_RUN_REQUIRED",cause:"Apply sin dry-run/confirm.",recovery:"Mostrar diff y repetir con confirmación explícita.",severity:blocking}
ERR:e_view_unknown_kind{code:"E_VIEW_UNKNOWN_KIND",cause:"VIEW kind ausente/desconocido.",recovery:"Elegir kind de VALID_KINDS.",severity:blocking}
ERR:e_view_empty_target{code:"E_VIEW_EMPTY_TARGET",cause:"VIEW target vacío.",recovery:"Definir selector resoluble.",severity:blocking}
ERR:e_view_unknown_reverse{code:"E_VIEW_UNKNOWN_REVERSE",cause:"Reverse ausente/desconocido.",recovery:"Elegir estrategia válida.",severity:blocking}
ERR:e_view_incompatible_reverse{code:"E_VIEW_INCOMPATIBLE_REVERSE",cause:"kind/reverse incompatibles.",recovery:"Usar matriz KIND_REVERSE_COMPAT.",severity:blocking}
ERR:e_view_duplicate_name{code:"E_VIEW_DUPLICATE_NAME",cause:"VIEW name duplicado.",recovery:"Renombrar para unicidad global.",severity:blocking}
ERR:e_view_hash_mismatch{code:"E_VIEW_HASH_MISMATCH",cause:"Contenido no coincide con hash VIEW.",recovery:"Detener y revisar modificación/preservación.",severity:blocking}
ERR:e_view_reverse_unsupported{code:"E_VIEW_REVERSE_UNSUPPORTED",cause:"Reverse reconocido pero no implementado en encoder.",recovery:"Usar estrategia implementada o manual_review explícito.",severity:blocking}
ERR:w_view_unused_entry{code:"W_VIEW_UNUSED_ENTRY",cause:"Entrada elegible sin VIEW.",recovery:"Agregar target; cobertura debe llegar a 100% para reversibilidad.",severity:warning}
ERR:w_view_unknown_status{code:"W_VIEW_UNKNOWN_STATUS",cause:"Status VIEW desconocido.",recovery:"Usar cur, planned, deprecated, human_only, generated o edited.",severity:warning}
ERR:w_hcortex_display_only{code:"W_HCORTEX_DISPLAY_ONLY",cause:"Salida display sin contrato reversible.",recovery:"No declarar reversible; regenerar en modo normal/strict.",severity:warning}

$11
DEP:core{component:"cortex.core",requires:"lexer, parser, AST, writer, validator, compare, modes, errors, document_kind",status:current,evidence:"wheel modules"}
DEP:glossary{component:"cortex.glossary",requires:"$0 model, resolver, minimal glossary y contracts",status:current,evidence:"wheel modules"}
DEP:hcortex{component:"cortex.hcortex",requires:"READ/EDIT renderers, parser, profiles y recovery",status:current,evidence:"wheel modules"}
DEP:crud{component:"cortex.crud",requires:"selectors, mutations y transacciones atómicas",status:current,evidence:"wheel modules"}
DEP:templates{component:"cortex.templates",requires:"factories brain, skill, package y glosario",status:current,evidence:"wheel modules"}
DEP:v2{component:"cortex.v2",requires:"parser/writer, VIEW, encoder, HCORTEX parser/renderer y equivalencia",status:current,evidence:"wheel modules"}
DEP:learning{component:"cortex.learning",requires:"workspace, policy, scoring, index, candidates y elevation",status:current,evidence:"wheel modules"}
DEP:security{component:"cortex.security",requires:"secret scanner y signature SHA256",status:current,evidence:"wheel modules"}
DEP:audit{component:"cortex.audit",requires:"logging opt-in, snapshots, rotation y prune",status:current,evidence:"wheel modules"}
DEP:cli{component:"cortex.cli",requires:"argparse router, commands y E3 wrapper",status:current,evidence:"entry point"}
CLAIM:distribution{statement:"PyPI distribuye codec-cortex 0.3.7 para Python >=3.9.",evidence:"METADATA y cortex --version",status:current}
CLAIM:core_parser{statement:"El pipeline core parsea, valida, serializa y muta artefactos .cortex.",evidence:"cortex.core y smoke tests",status:current}
CLAIM:v2_roundtrip{statement:"El pipeline v2 soporta roundtrip byte-identical y bidireccional bajo VIEW válido.",evidence:"roundtrip y roundtrip-bidir",status:current}
CLAIM:view_contract{statement:"VIEW implementa cobertura, render reversible, targets y estrategias de reversión.",evidence:"cortex.v2.view/view_renderer/encoder",status:current}
CLAIM:learning_engine{statement:"El motor de aprendizaje local determinista está implementado en 0.3.7.",evidence:"cortex learn --help y módulos learning",status:current}
CLAIM:security_governance{statement:"Secret scan, mutation modes, signature y audit opt-in están implementados.",evidence:"doctor, verify, audit",status:current}
CLAIM:e3_docs_benchmark{statement:"docstring y benchmark inventory están implementados como comandos E3.",evidence:"main_e3.py",status:current}
CLAIM:mcp{statement:"Servidor MCP no está implementado en el wheel 0.3.7.",evidence:"PyPI maturity table y ausencia de módulo",status:future}
LIM:no_sdist{limit:"Release 0.3.7 publica wheel pero no source distribution.",scope:"Auditoría de procedencia debe usar wheel+tag/repositorio.",status:current,evidence:"PyPI download files"}
LIM:docs_not_bundled{limit:"El wheel no incluye docs/cortex/api ni benchmark corpus.",scope:"docstring/benchmark requieren paths externos cuando no están instalados.",status:current,evidence:"wheel inventory"}
LIM:dual_canonicalizers{limit:"format pertenece al pipeline core; canonicalize pertenece a v2 y es VIEW-aware.",scope:"Elegir según formato y gate; no intercambiarlos ciegamente.",status:current,evidence:"CLI router"}
PFL:edit_hcortex_read{pattern:"Compilar una vista readable.",effect:"E010 o pérdida de metadata.",prevention:"Usar render --mode edit antes de compile.",status:current}
PFL:verify_view_only{pattern:"Tratar verify-view como gate completo.",effect:"Puede faltar prueba bidireccional.",prevention:"Añadir roundtrip-bidir y roundtrip byte-identical.",status:current}
PFL:index_as_memory{pattern:"Versionar o editar learn-index como canon.",effect:"Deriva y stale hashes.",prevention:"Editar brain/policy y rebuild index.",status:current}
PFL:admin_default{pattern:"Operar siempre en admin.",effect:"Bypass accidental de protecciones.",prevention:"Default editor; read-only para auditoría.",status:current}
PFL:silent_force_output{pattern:"Aceptar force-write-on-error como resultado final.",effect:"Artefacto inválido persistido.",prevention:"Reservar para diagnóstico y reparar antes de promover.",status:current}
PFL:manual_mass_edit{pattern:"Reescribir .cortex manualmente a gran escala.",effect:"Drift, errores de comillas y pérdida de contratos.",prevention:"Usar CRUD/canonicalize/format y comparar.",status:current}
PFL:trust_narrative_version{pattern:"Usar versión mencionada en prose sobre runtime.",effect:"Operación contra contrato equivocado.",prevention:"Usar cortex --version y wheel metadata.",status:current}
!installed_runtime_wins{rule:"Para ejecutar, la API y CLI del wheel instalado prevalecen sobre ejemplos o documentación desfasada.",survive:min}
!future_not_current{rule:"No asumir MCP u otra capacidad future como disponible; comprobar comando/módulo/evidencia.",survive:min}
LIM:doctor_v2_gap{limit:"doctor 0.3.7 usa el parser core y no interpreta correctamente sigil_decl ni attrs-pos del artefacto CORTEX v2, aunque verify E3, inspect, verify-view y roundtrips v2 sí lo aceptan.",scope:"Para skills v2 usar verify --kind skill --strict y gates v2; usar doctor sobre artefactos core o tratar su salida v2 como incompatibilidad conocida.",status:current,evidence:"ejecución reproducible contra codec-cortex 0.3.7"}

$12
KNW:out_min{topic:"OUT-MIN",content:"Resultado + acción; interacción directa y bajo presupuesto.",status:specification,evidence:"CORTEX-OUT"}
KNW:out_work{topic:"OUT-WORK",content:"Resultado + criterio + acción + límite; operación normal.",status:specification,evidence:"CORTEX-OUT"}
KNW:out_audit{topic:"OUT-AUDIT",content:"Resultado + evidencia + riesgo + control + trazabilidad.",status:specification,evidence:"CORTEX-OUT"}
KNW:out_full{topic:"OUT-FULL",content:"Reporte completo y artefactos reutilizables.",status:specification,evidence:"CORTEX-OUT"}
KNW:out_error{topic:"OUT-ERROR",content:"Código + causa + recuperación accionable.",status:specification,evidence:"CORTEX-OUT"}
KNW:blocks{topic:"Bloques",content:"Resultado,Criterio,Evidencia,Riesgo,Acción,Límite,Entrega,Control según intención.",status:specification,evidence:"upstream skill"}
!out_independent{rule:"CORTEX-OUT permanece fuera del pipeline CORTEX-HCORTEX.",survive:recovery}
!out_no_sigils{rule:"La respuesta humana no debe exponer sintaxis interna salvo que el usuario solicite el artefacto.",survive:recovery}
!out_honesty{rule:"No ocultar incertidumbre, límites, riesgo, errores o verificaciones pendientes.",survive:recovery}
!out_density{rule:"Priorizar resultado, criterio, evidencia crítica y próximo paso; eliminar recapitulación inútil.",survive:recovery}

$13
VIEW:sigils{kind:"table",target:"$0:canonical_sigils",reverse:"rows_to_entries",status:cur,title:"Glosario de sigilos",fields:"sigil,name,type,risk,cortex,desc"}
VIEW:types{kind:"kv_table",target:"$0:type_decls",reverse:"row_to_attrs",status:cur,title:"Sistema de tipos"}
VIEW:contracts{kind:"table",target:"$0:contracts",reverse:"rows_to_entries",status:cur,title:"Contratos posicionales",fields:"sigil,pos"}
VIEW:microtokens{kind:"table",target:"$0:microtokens",reverse:"rows_to_entries",status:cur,title:"Microtokens",fields:"token,expand"}
VIEW:enum_state{kind:"kv_table",target:"$0:enum_state",reverse:"row_to_attrs",status:cur,title:"Estados"}
VIEW:enum_severity{kind:"kv_table",target:"$0:enum_severity",reverse:"row_to_attrs",status:cur,title:"Severidad"}
VIEW:enum_priority{kind:"kv_table",target:"$0:enum_priority",reverse:"row_to_attrs",status:cur,title:"Prioridad"}
VIEW:enum_survive{kind:"kv_table",target:"$0:enum_survive",reverse:"row_to_attrs",status:cur,title:"Survive"}
VIEW:enum_plevel{kind:"kv_table",target:"$0:enum_plevel",reverse:"row_to_attrs",status:cur,title:"P-levels"}
VIEW:enum_mode{kind:"kv_table",target:"$0:enum_mode",reverse:"row_to_attrs",status:cur,title:"Modos"}
VIEW:enum_view_kind{kind:"kv_table",target:"$0:enum_view_kind",reverse:"row_to_attrs",status:cur,title:"VIEW kinds"}
VIEW:enum_reverse{kind:"kv_table",target:"$0:enum_reverse",reverse:"row_to_attrs",status:cur,title:"Reverse strategies"}
VIEW:identity{kind:"kv_table",target:"$1:IDN:skill",reverse:"row_to_attrs",status:cur,title:"Identidad del skill"}
VIEW:domain{kind:"kv_table",target:"$1:DOM:protocol",reverse:"row_to_attrs",status:cur,title:"Dominio"}
VIEW:sources{kind:"table",target:"$1:REF:*",reverse:"rows_to_entries",status:cur,title:"Fuentes",fields:"path,role,version,status"}
VIEW:source_audit{kind:"table",target:"$1:AUD:*",reverse:"rows_to_entries",status:cur,title:"Evidencia de fuente",fields:"event,evidence,result,date"}
VIEW:source_limits{kind:"table",target:"$1:LIM:*",reverse:"rows_to_entries",status:cur,title:"Límites de procedencia",fields:"limit,scope,status,evidence"}
VIEW:source_rules{kind:"numbered_list",target:"$1:!:*",reverse:"items_to_ordered_entries",status:cur,title:"Reglas de autoridad"}
VIEW:model_knowledge{kind:"table",target:"$2:KNW:*",reverse:"rows_to_entries",status:cur,title:"Model knowledge",fields:"topic,content,status,evidence"}
VIEW:model_constraints{kind:"table",target:"$2:CNST:*",reverse:"rows_to_entries",status:cur,title:"Model constraints",fields:"rule,severity,survive,evidence"}
VIEW:model_rules{kind:"numbered_list",target:"$2:!:*",reverse:"items_to_ordered_entries",status:cur,title:"Model rules"}
VIEW:grammar_knowledge{kind:"table",target:"$3:KNW:*",reverse:"rows_to_entries",status:cur,title:"Grammar knowledge",fields:"topic,content,status,evidence"}
VIEW:grammar_constraints{kind:"table",target:"$3:CNST:*",reverse:"rows_to_entries",status:cur,title:"Grammar constraints",fields:"rule,severity,survive,evidence"}
VIEW:grammar_rules{kind:"numbered_list",target:"$3:!:*",reverse:"items_to_ordered_entries",status:cur,title:"Grammar rules"}
VIEW:levels_knowledge{kind:"table",target:"$4:KNW:*",reverse:"rows_to_entries",status:cur,title:"Levels knowledge",fields:"topic,content,status,evidence"}
VIEW:levels_constraints{kind:"table",target:"$4:CNST:*",reverse:"rows_to_entries",status:cur,title:"Levels constraints",fields:"rule,severity,survive,evidence"}
VIEW:levels_risks{kind:"table",target:"$4:RSK:*",reverse:"rows_to_entries",status:cur,title:"Levels risks",fields:"risk,impact,mitigation,status,survive"}
VIEW:levels_rules{kind:"numbered_list",target:"$4:!:*",reverse:"items_to_ordered_entries",status:cur,title:"Levels rules"}
VIEW:security_knowledge{kind:"table",target:"$6:KNW:*",reverse:"rows_to_entries",status:cur,title:"Security knowledge",fields:"topic,content,status,evidence"}
VIEW:security_constraints{kind:"table",target:"$6:CNST:*",reverse:"rows_to_entries",status:cur,title:"Security constraints",fields:"rule,severity,survive,evidence"}
VIEW:security_risks{kind:"table",target:"$6:RSK:*",reverse:"rows_to_entries",status:cur,title:"Security risks",fields:"risk,impact,mitigation,status,survive"}
VIEW:security_rules{kind:"numbered_list",target:"$6:!:*",reverse:"items_to_ordered_entries",status:cur,title:"Security rules"}
VIEW:views_knowledge{kind:"table",target:"$7:KNW:*",reverse:"rows_to_entries",status:cur,title:"Views knowledge",fields:"topic,content,status,evidence"}
VIEW:views_constraints{kind:"table",target:"$7:CNST:*",reverse:"rows_to_entries",status:cur,title:"Views constraints",fields:"rule,severity,survive,evidence"}
VIEW:views_limits{kind:"table",target:"$7:LIM:*",reverse:"rows_to_entries",status:cur,title:"Views limits",fields:"limit,scope,status,evidence"}
VIEW:views_risks{kind:"table",target:"$7:RSK:*",reverse:"rows_to_entries",status:cur,title:"Views risks",fields:"risk,impact,mitigation,status,survive"}
VIEW:views_rules{kind:"numbered_list",target:"$7:!:*",reverse:"items_to_ordered_entries",status:cur,title:"Views rules"}
VIEW:learning_knowledge{kind:"table",target:"$8:KNW:*",reverse:"rows_to_entries",status:cur,title:"Learning knowledge",fields:"topic,content,status,evidence"}
VIEW:learning_constraints{kind:"table",target:"$8:CNST:*",reverse:"rows_to_entries",status:cur,title:"Learning constraints",fields:"rule,severity,survive,evidence"}
VIEW:learning_rules{kind:"numbered_list",target:"$8:!:*",reverse:"items_to_ordered_entries",status:cur,title:"Learning rules"}
VIEW:workflow_knowledge{kind:"table",target:"$9:KNW:*",reverse:"rows_to_entries",status:cur,title:"Workflow knowledge",fields:"topic,content,status,evidence"}
VIEW:workflow_rules{kind:"numbered_list",target:"$9:!:*",reverse:"items_to_ordered_entries",status:cur,title:"Workflow rules"}
VIEW:architecture_limits{kind:"table",target:"$11:LIM:*",reverse:"rows_to_entries",status:cur,title:"Architecture limits",fields:"limit,scope,status,evidence"}
VIEW:architecture_rules{kind:"numbered_list",target:"$11:!:*",reverse:"items_to_ordered_entries",status:cur,title:"Architecture rules"}
VIEW:output_knowledge{kind:"table",target:"$12:KNW:*",reverse:"rows_to_entries",status:cur,title:"Output knowledge",fields:"topic,content,status,evidence"}
VIEW:output_rules{kind:"numbered_list",target:"$12:!:*",reverse:"items_to_ordered_entries",status:cur,title:"Output rules"}
VIEW:handlers{kind:"table",target:"$5:HDL:*",reverse:"rows_to_entries",status:cur,title:"Router CLI",fields:"operation,status,requires,notes"}
VIEW:learning_thresholds{kind:"kv_table",target:"$8:THR:golden_fibonacci",reverse:"row_to_attrs",status:cur,title:"Umbrales Fibonacci"}
VIEW:learning_protected{kind:"kv_table",target:"$8:PRT:critical_sigils",reverse:"row_to_attrs",status:cur,title:"Targets protegidos"}
VIEW:learning_policies{kind:"table",target:"$8:POL:*",reverse:"rows_to_entries",status:cur,title:"Políticas de aprendizaje",fields:"origin,target,when,action,requires"}
VIEW:learning_gates{kind:"table",target:"$8:GTE:*",reverse:"rows_to_entries",status:cur,title:"Gates de aprendizaje",fields:"action,default,targets,status"}
VIEW:error_atlas{kind:"table",target:"$10:ERR:*",reverse:"rows_to_entries",status:cur,title:"Atlas de errores",fields:"code,cause,recovery,severity"}
VIEW:dependencies{kind:"table",target:"$11:DEP:*",reverse:"rows_to_entries",status:cur,title:"Arquitectura de módulos",fields:"component,requires,status,evidence"}
VIEW:claims{kind:"table",target:"$11:CLAIM:*",reverse:"rows_to_entries",status:cur,title:"Capacidades y madurez",fields:"statement,evidence,status"}
VIEW:pitfalls{kind:"table",target:"$11:PFL:*",reverse:"rows_to_entries",status:cur,title:"Antipatrones",fields:"pattern,effect,prevention,status"}
```