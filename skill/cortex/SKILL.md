```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: skill/hcortex/SKILL.md
source_version: 1.2.0-enterprise-candidate
status: specification
-->

$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identidad de proyecto/autoría/protocolo/artefacto"}
DOM:domain{type:attrs,risk:B,cortex:Semantic,desc:"alcance, dominio, contexto de adopción"}
KNW:knowledge{type:attrs,risk:B,cortex:Semantic,desc:"conocimiento base o promovido"}
REF:reference{type:attrs,risk:B,cortex:Semantic,desc:"referencia a documento/archivo/repositorio"}
TAG:tag{type:attrs,risk:B,cortex:Semantic,desc:"metadatos de clasificación"}
AXM:axiom{type:cuerpo,risk:H,cortex:Prefrontal,desc:"principio no negociable"}
CNST:constraint{type:attrs,risk:H,cortex:Prefrontal,desc:"restricción dura o límite operativo"}
!:rule{type:attrs,risk:H,cortex:Prefrontal,desc:"regla operacional compacta"}
CLAIM:claim{type:attrs,risk:M,cortex:Prefrontal,desc:"afirmación verificable con evidencia"}
LIM:limit{type:attrs,risk:M,cortex:Prefrontal,desc:"límite explícito de uso o madurez"}
AUD:audit{type:attrs,risk:M,cortex:Prefrontal,desc:"registro de verificación/auditoría/evidencia"}
RSK:risk{type:attrs,risk:M,cortex:Prefrontal,desc:"riesgo identificado con mitigación"}
FCS:focus{type:attrs,risk:H,cortex:Working,desc:"anclaje de atención activo"}
OBJ:objective{type:attrs,risk:H,cortex:Working,desc:"meta activa con criterio de éxito"}
WRK:work{type:attrs,risk:B,cortex:Working,desc:"estado de ejecución actual"}
STP:step{type:attrs,risk:M,cortex:Working,desc:"próxima acción inmediata"}
NXT:next{type:attrs,risk:M,cortex:Working,desc:"acción en cola con disparador"}
SES:session{type:attrs,risk:M,cortex:Episodic,desc:"episodio comprimido I/O/R"}
LNG:lesson{type:attrs,risk:M,cortex:Episodic,desc:"lección aprendida o patrón operativo"}
DIAG:diagram{type:bloque,risk:M,cortex:"Episodic/Visual",desc:"diagrama PlantUML o bloque visual verbatim"}
HDL:handler{type:attrs-pos,risk:M,cortex:Semantic,desc:"descriptor de operación o contrato de interfaz"}
PFL:pitfall{type:attrs,risk:M,cortex:Prefrontal,desc:"antipatrón conocido y prevención"}
DEP:dependency{type:attrs,risk:M,cortex:Semantic,desc:"dependencia entre artefactos/módulos"}
DESC:description{type:cuerpo,risk:B,cortex:Semantic,desc:"descripción textual estructurada"}
ERR:error{type:attrs,risk:M,cortex:Prefrontal,desc:"error conocido con causa y solución"}
$0:type_attrs{rule:"pares clave:valor o clave:\"valor\" dentro de {}"}
$0:type_cuerpo{rule:"texto literal entre {}"}
$0:type_bloque{rule:"multilinea verbatim"}
$0:type_attrs_pos{rule:"valores posicionales separados por |; orden definido en $0"}
$0:type_relacion{rule:"forma causal A -> B"}
$0:contract_hdl{pos:"operation|status|requires|notes"}
$0:contract_fcs{pos:"what|priority|status|survive"}
$0:contract_obj{pos:"goal|status|success|survive"}
$0:contract_wrk{pos:"phase|current|blocked|survive"}
$0:contract_stp{pos:"action|reason|owner|status|survive"}
$0:contract_cnst{pos:"rule|severity|survive"}
$0:contract_claim{pos:"statement|evidence|status"}
$0:contract_lim{pos:"limit|scope|status"}
$0:contract_rsk{pos:"risk|impact|mitigation|status|survive"}
$0:contract_aud{pos:"event|evidence|result|date"}
$0:contract_ses{pos:"input|output|outcome|date"}
$0:contract_lng{pos:"type|cause|lesson|prevention"}
$0:contract_knw{pos:"topic|content|status"}
$0:contract_diag{pos:"bloque verbatim valido"}
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
$0:micro_d1{expand:decode}
$0:micro_d2{expand:detect}
$0:micro_d3{expand:decay}
$0:micro_c1{expand:.cortex}
$0:micro_c2{expand:HCORTEX}
$0:micro_v1{expand:validate}
$0:micro_v2{expand:verify}
$0:micro_a1{expand:file}
$0:micro_a2{expand:files}
$0:micro_s1{expand:sigil}
$0:micro_s2{expand:section}
$0:micro_h1{expand:handler}
$0:micro_x1{expand:extract}
$0:micro_x2{expand:list}
$0:micro_m1{expand:modify}
$0:micro_m2{expand:add}
$0:micro_r1{expand:remove}
$0:micro_p1{expand:promote}
$0:micro_f1{expand:format}
$0:micro_t1{expand:structure}
$0:enum_state{values:"cur,specification,pln,fut,experimental,deprecated,blk,done"}
$0:enum_severity{values:"blocking,warning,info"}
$0:enum_priority{values:"high,medium,low"}
$0:enum_risk_level{values:"B,M,H"}
$0:delimiters{values:"espacio | , { } salto_de_linea inicio_de_valor fin_de_valor"}

$1
IDN:project{name:"CODEC-CORTEX",author:"Fidel Ernesto Lozada A.",version:"1.2.0-enterprise-candidate",license:MIT,spec:"1.2.0-enterprise-candidate",project:"0.3.2"}
DOM:scope{domain:"protocolo de memoria contextual para agentes LLM/SLM",lang_struct:"EN",lang_semantic:"idioma del dominio o usuario",output_human:"HCORTEX=render memoria; CORTEX-OUT=respuesta conversacional"}
TAG:meta{category:"META-SKILL",nature:"gobierno cognitivo",target:"LLM/SLM agents"}
REF:art_skill_root{path:"SKILL.md",role:"spec humana canónica"}
REF:art_skill_cortex{path:"skill/cortex/SKILL.md",role:"mente CORTEX del protocolo",encoding:CORTEX}
REF:art_skill_hcortex{path:"skill/hcortex/SKILL.md",role:"vista humana canónica",encoding:HCORTEX}
REF:art_brain{path:"brain.cortex",role:"estado persistente de trabajo"}
REF:art_packages{path:"*.cortex",role:"paquetes de contexto transportables"}
REF:art_status{path:"STATUS.md",role:"registro de verdad"}
REF:art_benchmark{path:"BENCHMARK.md",role:"evidencia empírica"}

$2
DESC:purpose{CODEC-CORTEX no es un prompt ni solo un formato de archivo. Es un protocolo de memoria contextual para agentes LLM/SLM que reemplaza historia lineal por estado cognitivo estructurado, auditable y gobernable. El sistema se apoya en siete componentes: 1:Mente(skill/cortex/SKILL.md)=reglas,ontología,contratos,algoritmos en codificación CORTEX | 2:Cerebro(brain.cortex+nativa)=estado vivo | 3:Paquetes(*.cortex)=payloads transportables | 4:Autocontención $0=glosario local mínimo para arranque seguro | 5:HCORTEX=vista humana de memoria | 6:CORTEX-OUT=respuesta conversacional eficiente | 7:Codec/runtime/MCP=automatización plan/future, nunca asumida si no existe.}
AXM:canon{SKILL gobierna. brain opera. package inyecta. HCORTEX explica. CORTEX-OUT responde con densidad. codec automatiza cuando exista. runtime madura cuando exista. MCP expone empresarialmente cuando exista.}
AXM:guiding{Memoria contextual estructurada antes que historia lineal. $0 dicta la sintaxis. Nivel 2 contiene el estado vivo. HCORTEX permite auditoría humana de memoria. CORTEX-OUT gobierna la respuesta saliente sin participar en el codec. La automatización determinista pertenece al codec/runtime cuando esté implementada y verificada.}
DESC:meta_skill{CODEC-CORTEX es un META-SKILL: habilidad de gobierno cognitivo que orienta cómo el agente gestiona memoria nativa, contexto de trabajo, continuidad, aprendizaje, límites y salida conversacional para cualquier actividad solicitada. No reemplaza habilidades de dominio del agente. Gobierna cómo el agente conserva foco, objetivo, restricciones, evidencia, riesgos y próximos pasos. Aplica separación entre memoria persistente (brain.cortex), contexto transportable (*.cortex) y memoria nativa transitoria. Permite que múltiples agentes operen sobre el mismo proyecto sin insertar su identidad funcional en la identidad canónica del proyecto. Debe estar activo por defecto cuando el agente trabaje en continuidad, memoria, contexto largo, aprendizaje operativo o claims de madurez.}
KNW:problem{topic:"problema resuelto",content:"agentes LLM/SLM pierden continuidad cuando dependen de historial plano. Historial plano mezcla instrucciones, hechos, decisiones, riesgos, progreso, evidencia y referencias produciendo ruido, amnesia, contradicción, pérdida de foco y degradación por posición. CODEC-CORTEX impone separación de responsabilidades, prioridad cognitiva, render humano auditable y comunicación saliente eficiente",status:cur}
KNW:cortices{topic:"ontología cognitiva 4 cortezas",content:"Semantic(IDN,DOM,KNW,REF,TAG):identidad,dominio,conocimiento,referencias,persistencia:larga | Prefrontal(AXM,CNST,!,CLAIM,LIM,AUD,RSK):gobierno,límites,riesgos,reglas,evidencia,persistencia:alta | Working(FCS,OBJ,WRK,STP,NXT):foco,meta,progreso,siguiente acción,persistencia:viva | Episodic(SES,LNG,DIAG histórico):experiencia,lecciones,memoria destilada,persistencia:variable. Relaciones:Prefrontal gobierna Working, Semantic aporta a Working, Working destila a Episodic, Episodic promueve a Semantic, Prefrontal impone límites a Semantic",status:cur}
KNW:normative_lang{topic:"lenguaje normativo",content:"MUST/DEBE=obligatorio, incumplimiento rompe conformidad | MUST NOT/NO DEBE=prohibición obligatoria | SHOULD/DEBERÍA=recomendación fuerte, omisión requiere justificación explícita | MAY/PUEDE=opcional",status:cur}
KNW:maturity{topic:"madurez de claims",content:"cur=ejecutable por lectura disciplinada, puede declararse capacidad actual:si | specification=definido normativamente no necesariamente automatizado, puede declararse:parcial con aclaración | pln=para fase posterior requiere implementación, puede declararse:no | fut=visión empresarial posterior, puede declararse:no | experimental=existe no estable ni canónico, puede declararse:no sin advertencia | deprecated=compatibilidad no recomendado, puede declararse:no",status:cur}
CNST:container{rule:".md optimiza lectura e indexación por agentes estándar. internal_encoding:CORTEX indica interpretar con reglas .cortex. internal_encoding:HCORTEX indica vista humana no canónica. HCORTEX NO DEBE usarse como fuente de roundtrip/decode/encode/verify. Derivados DEBEN declarar source_artifact+source_version. Plantillas/ejemplos DEBEN usar <protocol_version> o marcarse example/template/non_operational. No DEBEN usar versión literal que pueda confundirse con vigente",severity:blocking,survive:min}
CNST:honesty{rule:"ningún documento, agente, README, salida HCORTEX, salida CORTEX-OUT o interfaz comercial DEBE presentar como cur algo pln, fut o no verificado",severity:blocking,survive:min}
CNST:identity{rule:"IDN DEBE corresponder a proyecto/autoría/protocolo/artefacto. NO DEBE representar identidad funcional del agente ejecutor. Múltiples agentes pueden operar sobre el mismo proyecto sin formar parte de su identidad canónica. Versión normativa se declara en este documento. Derivados NO DEBEN inventar versión propia salvo ciclo de release independiente",severity:blocking,survive:min}
KNW:level_matrix{topic:"matriz ubicación permitida por sigilo",content:"L1(SKILL):IDN✓ DOM✓ AXM✓ CNST✓ !✓ FCS:contrato/ejemplo OBJ:contrato/ejemplo WRK:✗ STP:contrato/ejemplo NXT:✗ SES:✗ LNG:✗ KNW:protocolo✓ REF✓ DIAG:normativo✓ AUD:spec✓ RSK:protocolo✓ CLAIM✓ LIM✓ | L2(brain):IDN✓ DOM✓ AXM:limitado CNST✓ !:limitado FCS✓ OBJ✓ WRK✓ STP✓ NXT✓ SES✓ LNG✓ KNW✓ REF✓ DIAG:operativo✓ AUD✓ RSK✓ CLAIM✓ LIM✓ | L3(package):IDN✓ DOM✓ AXM:limitado CNST✓ FCS:no rec OBJ:no rec WRK:✗ STP:no rec NXT:no rec SES:histórico✓ LNG:histórico✓ KNW✓ REF✓ DIAG✓ AUD✓ RSK✓ CLAIM✓ LIM✓",status:cur}

$3
HDL:agent_init|specification|SKILL.md,brain.cortex|leer SKILL.md(CORTEX o HCORTEX); identificar reglas Nivel 1; leer brain.cortex si existe; si FCS y OBJ explícitos→usar estado activo; si no→derivar FCS/OBJ provisionales desde instrucciones actuales, mantener en memoria nativa transitoria; aplicar CNST; seleccionar perfil CORTEX; actuar o responder
HDL:pre_action|specification|brain.cortex o anclajes|verificar FCS activo/provisional; verificar OBJ activo/provisional; verificar CNST:blocking activos; verificar LIM relevantes; verificar claims de madurez; verificar RSK activos; verificar STP si aplica; si contradicción usuario vs CNST:blocking→detener o explicar incompatibilidad
HDL:absorb_pkg|specification|package.cortex,brain.cortex|recibir package.cortex; validar $0 o herencia de glosario; identificar propósito,fuente,alcance; si contiene estado vivo→marcar advertencia, no absorber WRK/FCS/OBJ como vivo sin confirmación; clasificar entradas por corteza; resolver conflictos con brain.cortex; integrar KNW/REF/DIAG/CLAIM/LIM útiles; registrar AUD de absorción
HDL:session_close|specification|brain.cortex|producir/actualizar SES:last con input,output,outcome,date; producir LNG si hubo error o patrón relevante; producir AUD si se verificó algo; producir RSK si quedó riesgo activo; producir NXT si queda acción pendiente; producir HCORTEX de cierre si humano necesita auditoría
HDL:hcortex_render|specification|.cortex o AST,perfil activo|10 pasos: 1)resolver perfil(explícito>presupuesto>modo>CORTEX-WORK) 2)declarar Perfil:CORTEX-LEVEL primera línea 3)filtrar por P-level/survive, sin P-level→P5, por entrada no por sección 4)resolver tipo desde $0(attrs→tabla,cuerpo→bloque indentado,bloque→verbatim) 5)renderizar entradas filtradas aplicando estrategia por tipo 6)si auditoría con presupuesto insuficiente→Perfil:CORTEX-FULL (segmentado) Segmento:n/total, nunca degradar silenciosamente 7)agregar source a tablas P0/P1, PUML 'source:DIAG:name primer comentario, falta→WARNING:missing source 8)múltiples instancias mismo sigilo→sub-secciones ### SIGIL:name preservar orden fuente 9)aplicar estrategia por tipo 10)ordenar P0→P5, sin P-level→después de P5, mismo nivel→orden fuente
HDL:recovery_missing_0|specification|.cortex sin $0|no ejecutar decisiones operativas basadas en ese archivo; leer solo en modo recuperación; identificar sigilos aparentes; reconstruir $0 mínimo local; marcar ambigüedades como RSK o AUD; solicitar confirmación humana si riesgo semántico; reemitir archivo reparado con $0 local antes de usar como memoria confiable

$4
!type_strict{rule:"attrs MUST usar pares clave/valor; attrs-pos MUST cumplir orden posicional exacto del contrato $0; attrs-pos sin campos completos SHOULD degradar a attrs explícito; DIAG MUST preservar bit a bit; parser MUST NOT inferir tipos por heurística si $0 los define",survive:min}
!section_normalize{rule:"parser SHOULD aceptar 2, $2, $2:CONTEXT, #--$2:CONTEXT-- y normalizar internamente a $2",survive:full}
!id_format{rule:"instancias en snake_case(FCS:primary, RSK:premature_claim); sigilos en MAYÚSCULAS salvo ! y operadores registrados en $0",survive:full}
!micro_delimit{rule:"micro-tokens se expanden solo si delimitados por espacio | , { } salto_de_linea inicio_de_valor fin_de_valor; MUST NOT expandirse dentro de palabras(param_d1 no se expande; \"d1\" se expande si modo permite)",survive:full}
!extend_glossary{rule:"nuevo sigilo→registrar en $0 antes primer uso; nuevo micro-token→registrar en $0 antes primer uso; nuevo tipo→registrar en $0 antes primer uso; attrs-pos→declarar contrato posicional en $0; sigilos existentes→NO redefinir silenciosamente; tipo→NO cambiar para sigilo ya usado en archivo; micro-tokens→NO expandir dentro de bloque o DIAG; sigilo desconocido→tratar como no confiable hasta registrar/confirmar",survive:min}
!hcortex_expand{rule:"attrs→tabla, cuerpo→bloque indentado, bloque→verbatim; tipo resuelto desde $0 no por heurística",survive:min}
!hcortex_source{rule:"P0/P1 attrs→columna source con SIGIL:name; PUML→' source:DIAG:name como primer comentario; cuerpo→línea source:SIGIL:name bajo bloque; falta source en P0/P1→WARNING:missing source",survive:min}
!hcortex_multi{rule:"múltiples instancias mismo sigilo→sub-secciones ### SIGIL:name, preservar orden fuente",survive:full}
!hcortex_order{rule:"ordenar secciones P0→P5, sin P-level→después de P5, mismo P-level→orden fuente, nunca truncar por posición→eliminar por valor cognitivo",survive:min}

$5
CNST:sep_l1{rule:"L1 MUST NOT almacenar estado vivo de sesión. FCS/OBJ/WRK/STP/NXT prohibidos como estado activo en skill/cortex/SKILL.md; permitidos solo como contrato/ejemplo marcado example/template/non_operational o en sección normativa/tabla de campos",severity:blocking,survive:min}
CNST:sep_l2{rule:"L2 MUST contener foco y objetivo para operación persistente; DEBE validar FCS y OBJ antes de actuar, si faltan→detener o derivar provisional; para tareas acotadas sin brain.cortex MAY operar con anclajes provisionales en memoria nativa transitoria; escritura solo si usuario pide .cortex, proyecto opera con brain.cortex, o cierre de sesión aprobado",severity:blocking,survive:min}
CNST:sep_l3{rule:"L3 MUST NOT madurar por sí mismo, MUST NOT reclamar ciclo de vida propio, MUST NOT mutar por sí mismo; SHOULD incluir procedencia, propósito y alcance; maduración solo si se absorbe formalmente en Nivel 2",severity:warning,survive:min}
CNST:sep_hcortex{rule:"HCORTEX MUST NOT reemplazar .cortex como persistencia canónica; es vista humana no fuente de roundtrip",severity:blocking,survive:min}
CNST:sep_runtime{rule:"Runtime/CLI/MCP MUST NOT asumirse existente sin confirmación de STATUS.md o herramienta real",severity:blocking,survive:min}
CNST:pre_action{rule:"agente DEBE verificar FCS,OBJ,CNST:blocking,LIM,claims de madurez,RSK activos,STP antes de cada acción; contradicción usuario vs CNST:blocking→detener o explicar incompatibilidad",severity:blocking,survive:min}
LIM:maturity{limit:"presupuestos de perfil son orientativos, no medidos sin benchmark reproducible",scope:"CORTEX-OUT perfiles y HCORTEX perfiles",status:cur}
LIM:codec{limit:"codec/runtime/MCP son planned/future, nunca asumidos si no existen",scope:"automatización",status:cur}
RSK:attrs_pos_broken{risk:"attrs-pos sin contrato estable produce decodificación errónea",impact:"alto, corrupción de estado",mitigation:"solo activar cuando $0 declare contrato posicional canónico o local validado",status:cur,survive:min}
PFL:no_0{pattern:"archivo .cortex sin $0",effect:"no conforme, no debe usarse como fuente operativa confiable",prevention:"ejecutar recovery_missing_0: reconstruir $0 mínimo, marcar ambigüedades como RSK/AUD, reemitir reparado antes de usar",survive:min}
PFL:silent_redefine{pattern:"redefinir sigilo existente sin declarar en $0 o cambiar tipo de expansión ya usado",effect:"desincronización entre parser y semántica",prevention:"extensión local DEBE registrar antes del primer uso, redefinición silenciosa prohibida por !extend_glossary",survive:min}
PFL:live_in_l1{pattern:"FCS/OBJ/WRK/STP/NXT como estado vivo en skill/cortex/SKILL.md",effect:"violación de separación de niveles, estado fantasma en mente del protocolo",prevention:"solo permitido como contrato/ejemplo marcado example/template/non_operational",survive:min}
PFL:hcortex_as_source{pattern:"usar archivo HCORTEX como fuente de roundtrip/decode/encode/verify",effect:"vista tratada como canon, pérdida de integridad del codec",prevention:"HCORTEX es vista humana, NO participa en decode/encode/verify/roundtrip",survive:min}
PFL:out_as_cortex{pattern:"tratar CORTEX-OUT como .cortex o parsearlo con reglas .cortex",effect:"respuesta conversacional contaminando memoria canónica",prevention:"CORTEX-OUT no participa en decode/encode/verify/AST/$0/contratos/roundtrip/persistencia canónica",survive:min}
PFL:false_maturity{pattern:"presentar capacidad pln/fut/experimental como cur",effect:"engaño al usuario, degradación de confianza del sistema",prevention:"regla de honestidad: ningún documento/agente/salida/interfaz DEBE presentar como cur algo no verificado",survive:min}

$6
DIAG:arq_niveles{
@startuml
skinparam componentStyle rectangle
skinparam shadowing false
title CODEC-CORTEX — Arquitectura de 3 Niveles

package "Nivel 1 — MENTE\nskill/cortex/SKILL.md\ninternal_encoding:CORTEX" as L1 {
  rectangle "Ontología" as L1A
  rectangle "Sigilos y contratos" as L1B
  rectangle "Reglas y axiomas" as L1C
  rectangle "Políticas de triaje" as L1D
  note right of L1
    Define el CÓMO.
    Read-only para estado.
    No contiene FCS/OBJ/WRK vivos.
  end note
}

package "Nivel 2 — CEREBRO\nbrain.cortex + memoria nativa" as L2 {
  rectangle "FCS / OBJ / WRK" as L2A
  rectangle "STP / NXT / AUD / RSK" as L2B
  rectangle "SES / LNG / KNW activo" as L2C
  rectangle "Triage P0-P5" as L2D
  note right of L2
    Define el DÓNDE y CUÁNDO.
    Aquí vive el trabajo.
    Perfiles y degradación.
  end note
}

package "Nivel 3 — PAQUETES\n*.cortex" as L3 {
  rectangle "Contexto transportable" as L3A
  rectangle "Referencias" as L3B
  rectangle "Diagramas" as L3C
  note right of L3
    Define el QUÉ.
    No madura ni aprende solo.
    Debe absorberse en Nivel 2.
  end note
}

rectangle "HCORTEX" as HC
rectangle "CORTEX-OUT" as CO
rectangle "Usuario" as HU
rectangle "Codec/Runtime/MCP\nplanned/future" as RT

L1 --> L2 : gobierna
L3 --> L2 : inyecta si se absorbe
L2 --> HC : renderiza memoria
L2 --> CO : produce respuesta
HC --> HU : audita/lee
CO --> HU : responde
RT ..> L1 : implementa reglas
RT ..> L2 : automatiza gestión
RT ..> L3 : valida paquetes
@enduml
}
DIAG:ontologia{
@startuml
skinparam componentStyle rectangle
skinparam shadowing false
title CODEC-CORTEX — Ontología Cognitiva

rectangle "Semantic Cortex\nIDN DOM KNW REF TAG" as SEM
rectangle "Prefrontal Cortex\nAXM CNST ! CLAIM LIM AUD RSK" as PRE
rectangle "Working Memory\nFCS OBJ WRK STP NXT" as WRK
rectangle "Episodic Memory\nSES LNG DIAG historical" as EPI

PRE -down-> WRK : gobierna acción
SEM -right-> WRK : aporta conocimiento
WRK -down-> EPI : destila experiencia
EPI -up-> SEM : promueve aprendizaje validado
PRE -right-> SEM : impone límites
@enduml
}
DIAG:agent_init{
@startuml
skinparam componentStyle rectangle
skinparam shadowing false
title CODEC-CORTEX — Inicio Operativo

start
:Leer SKILL.md (CORTEX o HCORTEX);
:Identificar reglas Nivel 1;
:Leer brain.cortex si existe;
if (FCS y OBJ explícitos?) then (sí)
  :Usar estado activo;
else (no)
  :Derivar FCS/OBJ provisionales;
  :Mantener en memoria nativa transitoria;
endif
:Aplicar CNST;
:Seleccionar perfil CORTEX;
:Actuar o responder;
stop
@enduml
}
DIAG:absorb_pkg{
@startuml
skinparam componentStyle rectangle
skinparam shadowing false
title CODEC-CORTEX — Absorción Nivel 3

start
:Recibir package.cortex;
:Validar $0 o herencia;
:Identificar propósito, fuente, alcance;
if (contiene estado vivo?) then (sí)
  :Marcar advertencia;
  :No absorber WRK/FCS/OBJ sin confirmación;
endif
:Clasificar por corteza;
:Resolver conflictos con brain.cortex;
:Integrar KNW/REF/DIAG/CLAIM/LIM;
:Registrar AUD de absorción;
stop
@enduml
}
DIAG:hcortex_render{
@startuml
skinparam componentStyle rectangle
skinparam shadowing false
title CODEC-CORTEX — Render HCORTEX

rectangle "Nivel 2\nbrain.cortex / nativa" as B
rectangle "Filtro de perfil\nMIN RECOVERY WORK FULL" as F
rectangle "Orden P0→P5" as O
rectangle "Render por tipo\nattrs cuerpo bloque" as R
rectangle "HCORTEX-READABLE" as HR
rectangle "HCORTEX-AUDIT" as HA

B --> F
F --> O
O --> R
R --> HR : sin source
R --> HA : con source + advertencias
@enduml
}

$7
CNST:contract_fcs{rule:"FCS requiere what,priority,status,survive",severity:blocking,survive:min}
CNST:contract_obj{rule:"OBJ requiere goal,status,success,survive",severity:blocking,survive:min}
CNST:contract_wrk{rule:"WRK requiere phase,current,blocked,survive",severity:blocking,survive:min}
CNST:contract_stp{rule:"STP requiere action,reason,owner,status,survive",severity:blocking,survive:min}
CNST:contract_cnst{rule:"CNST requiere rule,severity,survive; severity:blocking debe ser P0/min",severity:blocking,survive:min}
CNST:contract_claim{rule:"CLAIM requiere statement,evidence,status; no usar métricas no medidas como actuales",severity:warning,survive:min}
CNST:contract_lim{rule:"LIM requiere limit,scope,status; no omitir límites de madurez",severity:warning,survive:min}
CNST:contract_rsk{rule:"RSK requiere risk,impact,mitigation,status,survive; no registrar riesgo sin mitigación",severity:warning,survive:min}
CNST:contract_aud{rule:"AUD requiere event,evidence,result,date; no usar como sustituto de benchmark",severity:warning,survive:full}
CNST:contract_ses{rule:"SES requiere input,output,outcome,date; no promover a KNW sin criterio",severity:warning,survive:full}
CNST:contract_lng{rule:"LNG requiere type,cause,lesson,prevention; no convertir experiencia aislada en axioma",severity:warning,survive:full}
CNST:contract_knw{rule:"KNW requiere topic,content,status; no mezclar con estado transitorio",severity:warning,survive:full}
CNST:contract_hdl{rule:"HDL requiere posición definida por $0 (operation|status|requires|notes); no presentar handler planificado como implementado",severity:warning,survive:min}
CNST:contract_diag{rule:"DIAG requiere bloque verbatim válido; no reformatear bit a bit",severity:blocking,survive:min}

$8
!survive_priority{rule:"P0→min, P1→rec, P2→wrk, P3→reduced, P4→basic, P5→full",survive:min}
!survive_degrade{rule:"al reducir presupuesto descartar P5→P1, P0 nunca se elimina; al expandir recuperar inversamente",survive:min}
!p5_filter{rule:"en presupuesto >3000t o FULL: incluir P5 solo con survive, KNW companion o valor operacional",survive:full}
KNW:p_levels{topic:"prioridad cognitiva P0→P5",content:"P0:FCS,OBJ,CNST:blocking,STP→sobrevive en MIN/RECOVERY/WORK/FULL, nunca se elimina | P1:WRK,AUD,RSK,NXT→sobrevive en RECOVERY/WORK/FULL, último antes de P0 | P2:CLAIM,LIM,KNW:active,LNG:critical→sobrevive en WORK/FULL, tras P1 | P3:SES:last,STAT→sobrevive en FULL(WORK si espacio), tras P2 | P4:REF:critical,DOC,ART→sobrevive en FULL, tras P3 | P5:DIAG,TBL,histórico,comentarios→sobrevive en FULL, primero en eliminar. Reglas: carga P0→P5, degradación P5→P1, mismo P-level→orden fuente, sin P-level→después de P5, nunca truncar por posición",status:cur}

$9
KNW:profile_min{topic:"CORTEX-MIN",content:"presupuesto ~300t, P-level:P0, uso:emergencia/bloqueo, contenido:solo FCS+OBJ+CNST+STP",status:cur}
KNW:profile_recovery{topic:"CORTEX-RECOVERY",content:"presupuesto ~1000t, P-level:P0+P1, uso:reconexión tras interrupción",status:cur}
KNW:profile_work{topic:"CORTEX-WORK",content:"presupuesto ~3000t, P-level:P0+P1+P2, uso:trabajo estándar (default)",status:cur}
KNW:profile_full{topic:"CORTEX-FULL",content:"sin límite presupuesto, P-level:P0-P5, uso:spec completa/auditoría/gate de salida",status:cur}
KNW:out_profile_min{topic:"OUT-MIN",content:"80-180t, uso:confirmación/bloqueo/respuesta simple, bloques:Resultado+Acción",status:cur}
KNW:out_profile_work{topic:"OUT-WORK",content:"250-700t, uso:análisis/diseño/recomendación/revisión normal, bloques:Resultado+Criterio+Acción",status:cur}
KNW:out_profile_audit{topic:"OUT-AUDIT",content:"700-1500t, uso:coherencia/arquitectura/seguridad/legal/benchmark/decisión crítica, bloques:Resultado+Evidencia+Riesgo+Acción",status:cur}
KNW:out_profile_full{topic:"OUT-FULL",content:"variable, uso:documento/spec/informe/contrato/entrega reutilizable, bloques:Entrega+Criterio+Control",status:cur}
KNW:o_levels{topic:"prioridad salida CORTEX-OUT O0→O5",content:"O0:resultado directo/decisión→nunca eliminar | O1:acción siguiente→solo si no aplica | O2:riesgo/límite/incertidumbre crítica→nunca si hay riesgo real | O3:evidencia mínima→puede omitirse en OUT-MIN si no crítica | O4:contexto explicativo→eliminar bajo presión de tokens | O5:desarrollo extendido/ejemplos/historia→primero en eliminar",status:cur}
KNW:out_selection{topic:"selección perfil CORTEX-OUT",content:"pregunta simple→OUT-MIN | confirmación/veredicto rápido→OUT-MIN | análisis/diseño→OUT-WORK | revisión coherencia→OUT-AUDIT | seguridad/legal/benchmark/arquitectura crítica→OUT-AUDIT | documento/skill/contrato/informe→OUT-FULL",status:cur}

$10
!degrade_context{rule:"al reducir presupuesto: descartar P5→P1, P0 nunca; recuperar inversamente al expandir; si presupuesto insuficiente para perfil requerido→Perfil:CORTEX-LEVEL (segmentado) Segmento:n/total, nunca degradar silenciosamente",survive:min}
!degrade_out{rule:"eliminar O5→O4→O3, preservar O0 siempre, preservar O2 cuando exista riesgo/incertidumbre material o límite operativo",survive:min}

$11
DESC:hcortex_def{HCORTEX es el protocolo de render humano de memoria .cortex hacia Markdown. Objetivo: comprensión, auditoría y edición asistida. No es reconstrucción textual literal. No es persistencia canónica. No gobierna respuesta conversacional ordinaria (eso es CORTEX-OUT).}
KNW:hc_modes{topic:"modos HCORTEX",content:"READABLE:lectura ejecutiva limpia, sigilos ocultos por defecto | AUDIT:auditoría/trazabilidad/depuración, sigilos visibles como source | RECOVERY:reconexión tras pérdida de contexto, solo P0-P2 relevantes | FULL:exportación amplia/gate de salida, todo lo permitido por perfil FULL",status:cur}
KNW:hc_gate{topic:"gate de salida",content:"antes de abandonar CODEC-CORTEX SHOULD generar HCORTEX-FULL desde Nivel 2; preserva comprensión humana, evita lock-in, NO promete reconstrucción literal de todos los mensajes originales, debe declarar límites de pérdida semántica u omisión",status:cur}
!d1{rule:"minimizar prosa; usar solo cuando tabla/lista/diagrama no capturen la información; prosa expandida diluye densidad cognitiva",survive:full}
!d2{rule:"tablas por defecto para información con múltiples atributos compartiendo dominio; lectura vertical escaneable, columnas=dimensiones, filas=instancias",survive:full}
!d3{rule:"listas con viñetas para conjuntos paralelos; numeración para secuencia/prioridad/pasos; cada ítem=unidad cognitiva independiente",survive:full}
!d4{rule:"arquitectura/secuencia/decisión/relación/flujo→PlantUML; 20 líneas PUML reemplazan 200+ de prosa; diagrama declarativo=compresión natural",survive:full}
!d5{rule:"sin ASCII art, usar PUML en su lugar; ASCII art no es parseable, no declarativo, rompe portabilidad",survive:full}
!d6{rule:"una idea por bloque; no mezclar temas en tabla/lista/párrafo; bloques atómicos permiten filtrar por P-level sin perder contexto",survive:full}
!d7{rule:"jerarquía visual estricta: Título→Perfil→secciones P0→P5→anexos; orden de lectura=orden de importancia cognitiva",survive:full}
!d8{rule:"eliminar muletillas sin valor informativo: cabe destacar, es importante mencionar, como se puede observar, en este sentido y equivalentes",survive:full}
!d9{rule:"cross-reference (Ver también:§X) en vez de repetir contenido; una fuente de verdad; duplicación se desincroniza",survive:full}
!d10{rule:"status/priority/severity como columnas estándar con valores del glosario; consistencia de filtrado, escaneo vertical por columna",survive:full}
!d11{rule:"sin cursiva; **negrita** para énfasis estructural, nunca *cursiva* ni _cursiva_; cursiva reduce legibilidad en bloques densos",survive:full}
!d12{rule:"definir sigilos donde se usan por primera vez, no en glosario separado; el lector no debe saltar a otra sección",survive:full}
KNW:hc_format{topic:"jerarquía formato por tipo de contenido",content:"datos multi-atributo(2+ attrs compartiendo dominio)→tabla | secuencia ordenada→lista numerada | conjunto paralelo→lista viñetas | regla cond+acción→tabla compacta | arquitectura/flujo→PUML rectangle | principio inmutable→cita indentada > | código/template→bloque verbatim | prosa→párrafo breve solo cuando ningún otro formato aplica",status:cur}
KNW:hc_puml{topic:"reglas PUML estrictas para HCORTEX",content:"1:solo rectangle para componentes | 2:skinparam componentStyle rectangle obligatorio | 3:skinparam shadowing false obligatorio | 4:title obligatorio | 5:sin {}[]* en labels | 6:saltos de línea con \\n | 7:@startuml/@enduml balanceados(mismo conteo) | 8:preservar verbatim no reformatear no reordenar | 9:note para aclaraciones laterales | 10:' source:DIAG:name en modo audit como primer comentario",status:cur}
KNW:hc_vs_out{topic:"separación HCORTEX vs CORTEX-OUT",content:"HCORTEX:origen=.cortex/AST decodificado,propósito=vista humana memoria persistente,participa en codec=sí,usa $0=indirectamente(tipos expansión),define sigilos=no,requiere roundtrip=no,perfiles=MIN/RECOVERY/WORK/FULL | CORTEX-OUT:origen=razonamiento agente,propósito=respuesta conversacional eficiente,participa en codec=no,usa $0=no,define sigilos=no,requiere roundtrip=no,perfiles=OUT-MIN/OUT-WORK/OUT-AUDIT/OUT-FULL",status:cur}
PFL:ha1{pattern:"párrafos largos multi-tema",effect:"imposible filtrar por P-level, lector se pierde",prevention:"D6 una idea por bloque",survive:full}
PFL:ha2{pattern:"información solo en prosa",effect:"3x-5x más tokens que tabla equivalente",prevention:"D2 tablas por defecto",survive:full}
PFL:ha3{pattern:"arquitectura descrita en texto",effect:"200+ líneas de prosa donde 20 PUML bastan",prevention:"D4 diagrama antes que prosa",survive:full}
PFL:ha4{pattern:"sin declaración de perfil",effect:"lector no sabe qué esperar ni qué se omitió",prevention:"§9 perfiles: primera línea Perfil:CORTEX-LEVEL",survive:full}
PFL:ha5{pattern:"degradación silenciosa",effect:"información crítica ausente sin advertencia",prevention:"§9 perfiles: segmentado explícito cuando presupuesto insuficiente",survive:full}
PFL:ha6{pattern:"$0 en documento HCORTEX",effect:"metadato de IA en vista humana",prevention:"$0 solo en .cortex y skill/cortex/",survive:full}
PFL:ha7{pattern:"cursiva en texto denso",effect:"reduce legibilidad en bloques compactos",prevention:"D11 solo negrita",survive:full}
PFL:ha8{pattern:"muletillas narrativas",effect:"tokens sin valor informativo",prevention:"D8 eliminar sin piedad",survive:full}
PFL:ha9{pattern:"duplicación entre secciones",effect:"desincronización garantizada en ≤3 ediciones",prevention:"D9 cross-reference",survive:full}
PFL:ha10{pattern:"ASCII art en lugar de PUML",effect:"no parseable, no portable, ilegible en fuentes variables",prevention:"D5 PUML declarativo",survive:full}
PFL:ha11{pattern:"truncar por posición",effect:"pierde P0 por estar al final del archivo",prevention:"§9 P-levels: degradar por valor cognitivo no por posición",survive:full}
PFL:ha12{pattern:"prometer reconstrucción literal",effect:"claim falso, HCORTEX es vista no bitcopy",prevention:"§9.1 no prometer reconstrucción literal",survive:full}
CNST:hc_c1{rule:"Perfil:CORTEX-LEVEL como primera línea de contenido",severity:warning,survive:full}
CNST:hc_c2{rule:"sin $0 salvo auditoría estructural explícita",severity:warning,survive:full}
CNST:hc_c3{rule:"tablas para >80% de datos multi-atributo",severity:info,survive:full}
CNST:hc_c4{rule:"PUML para cada tema de arquitectura/flujo",severity:info,survive:full}
CNST:hc_c5{rule:"sin ASCII art (caracteres ┤┐└┴┬├)",severity:warning,survive:full}
CNST:hc_c6{rule:"sin cursiva",severity:info,survive:full}
CNST:hc_c7{rule:"sin muletillas narrativas",severity:info,survive:full}
CNST:hc_c8{rule:"orden P0→P5 en secciones",severity:warning,survive:full}
CNST:hc_c9{rule:"source en tablas P0/P1 en modo audit con formato SIGIL:name",severity:warning,survive:full}
CNST:hc_c10{rule:"omisiones declaradas explícitamente (segmentado/omitido/no incluido)",severity:warning,survive:full}
CNST:hc_c11{rule:"PUML: solo rectangle, title presente, skinparam correcto",severity:warning,survive:full}
CNST:hc_c12{rule:"@startuml/@enduml balanceados (mismo conteo)",severity:warning,survive:full}
CNST:hc_c13{rule:"sin promesa de reconstrucción literal o sin pérdida",severity:warning,survive:full}
CNST:hc_c14{rule:"una idea por bloque (tabla/lista/párrafo atómico)",severity:info,survive:full}
CNST:hc_c15{rule:"cross-references donde hay solapamiento entre secciones",severity:info,survive:full}

$12
DESC:out_def{CORTEX-OUT es el protocolo de salida conversacional de CODEC-CORTEX. Nombre canónico: CORTEX-OUT. El término HCORTEX-OUT PUEDE aparecer como referencia histórica o descriptiva de diseño pero NO DEBE usarse como nombre canónico porque induce a confundirlo con HCORTEX. HCORTEX=.cortex/AST→Markdown humano auditable. CORTEX-OUT=razonamiento del agente→respuesta humana eficiente. CORTEX-OUT NO participa en: decode, encode, verify, AST, $0, contratos de sigilos, roundtrip, persistencia canónica.}
AXM:out_guiding{La comunicación saliente debe maximizar utilidad cognitiva por token sin ocultar incertidumbre, riesgo, límites, evidencia crítica ni restricciones de seguridad.}
!out_independence{rule:"CORTEX-OUT MUST permanecer fuera del pipeline .cortex→AST→HCORTEX",survive:min}
!out_density{rule:"SHOULD eliminar relleno, recapitulación innecesaria y cierre decorativo",survive:full}
!out_action{rule:"SHOULD priorizar resultado, criterio, riesgo y acción",survive:full}
!out_honesty{rule:"MUST NOT ahorrar tokens ocultando incertidumbre o límites relevantes",survive:min}
!out_adaptive{rule:"SHOULD ajustar extensión según intención, criticidad y necesidad de evidencia",survive:full}
!out_no_parse{rule:"MUST NOT tratarse como .cortex; MUST NOT crear sigilos, alterar $0, ni requerir contratos de parseo",survive:min}
CNST:out_naming{rule:"nombre canónico CORTEX-OUT; HCORTEX-OUT NO DEBE usarse como nombre canónico",severity:warning,survive:full}
KNW:out_blocks{topic:"bloques canónicos CORTEX-OUT",content:"Resultado:respuesta directa/veredicto, siempre que haya conclusión | Criterio:juicio técnico/decisión razonada, diseño/análisis/revisión | Evidencia:hechos/citas/datos verificables, auditoría/benchmark/revisión crítica | Riesgo:problemas/incoherencias/límites/impacto, decisiones críticas o incertidumbre | Acción:próximo paso/instrucción/recomendación, cuando exista continuidad operativa | Límite:qué no se sabe/no se hizo/no debe asumirse, incertidumbre o falta de evidencia | Entrega:artefacto final/código/texto/tabla/documento, OUT-FULL o artefactos reutilizables | Control:qué se modificó/qué pendiente/qué validar, cierre de trabajos largos. Usar solo bloques que agreguen valor; 1-2 bloques es correcto si resuelve la tarea",status:cur}

$13
VIEW:sigils_canonicos{kind:"table",target:"$0:canonical_sigils",reverse:"rows_to_entries",status:cur,title:"Sigilos Canónicos"}
VIEW:type_decls{kind:"kv_table",target:"$0:type_decls",reverse:"row_to_attrs",status:cur,title:"Declaraciones de Tipo"}
VIEW:contracts_decl{kind:"table",target:"$0:contracts",reverse:"rows_to_entries",status:cur,title:"Contratos Posicionales"}
VIEW:microtokens_decl{kind:"table",target:"$0:microtokens",reverse:"rows_to_entries",status:cur,title:"Microtokens"}
VIEW:enum_state_decl{kind:"kv_table",target:"$0:enum_state",reverse:"row_to_attrs",status:cur,title:"Enum: state"}
VIEW:enum_severity_decl{kind:"kv_table",target:"$0:enum_severity",reverse:"row_to_attrs",status:cur,title:"Enum: severity"}
VIEW:enum_priority_decl{kind:"kv_table",target:"$0:enum_priority",reverse:"row_to_attrs",status:cur,title:"Enum: priority"}
VIEW:enum_risk_level_decl{kind:"kv_table",target:"$0:enum_risk_level",reverse:"row_to_attrs",status:cur,title:"Enum: risk_level"}
VIEW:delimiters_decl{kind:"kv_table",target:"$0:delimiters",reverse:"row_to_attrs",status:cur,title:"Delimiters"}
VIEW:axiom_canonical_decl{kind:"prose",target:"$0:AXM:axiom",reverse:"body_to_cuerpo",status:cur,title:"AXM (canonical declaration)"}
VIEW:desc_canonical_decl{kind:"prose",target:"$0:DESC:description",reverse:"body_to_cuerpo",status:cur,title:"DESC (canonical declaration)"}
VIEW:diag_canonical_decl{kind:"puml",target:"$0:DIAG:diagram",reverse:"verbatim_to_bloque",status:cur,title:"DIAG (canonical declaration)",preserve:"verbatim"}
VIEW:project_identity{kind:"kv_table",target:"$1:IDN:project",reverse:"row_to_attrs",status:cur,title:"Identidad del Proyecto"}
VIEW:project_scope{kind:"kv_table",target:"$1:DOM:scope",reverse:"row_to_attrs",status:cur,title:"Alcance del Proyecto"}
VIEW:project_meta_tags{kind:"kv_table",target:"$1:TAG:meta",reverse:"row_to_attrs",status:cur,title:"Meta Tags"}
VIEW:project_refs{kind:"table",target:"$1:REF:*",reverse:"rows_to_entries",status:cur,fields:"path,role,encoding",title:"Referencias de Artefactos"}
VIEW:purpose_desc{kind:"prose",target:"$2:DESC:purpose",reverse:"body_to_cuerpo",status:cur,title:"Propósito"}
VIEW:meta_skill_desc{kind:"prose",target:"$2:DESC:meta_skill",reverse:"body_to_cuerpo",status:cur,title:"Naturaleza Meta-Skill"}
VIEW:axiom_canon{kind:"prose",target:"$2:AXM:canon",reverse:"body_to_cuerpo",status:cur,title:"Axima Canon"}
VIEW:axiom_guiding{kind:"prose",target:"$2:AXM:guiding",reverse:"body_to_cuerpo",status:cur,title:"Axima Guía"}
VIEW:knowledge_base{kind:"table",target:"$2:KNW:*",reverse:"rows_to_entries",status:cur,fields:"topic,content,status",title:"Conocimiento Base"}
VIEW:constraints_purpose{kind:"table",target:"$2:CNST:*",reverse:"rows_to_entries",status:cur,fields:"rule,severity,survive",title:"Constraints de Propósito"}
VIEW:handlers{kind:"table",target:"$3:HDL:*",reverse:"rows_to_entries",status:cur,fields:"operation,status,requires,notes",title:"Handlers Operacionales"}
VIEW:rules_normalization{kind:"numbered_list",target:"$4:!:*",reverse:"items_to_ordered_entries",status:cur,fields:"rule,survive",title:"Reglas de Normalización"}
VIEW:constraints_separators{kind:"table",target:"$5:CNST:*",reverse:"rows_to_entries",status:cur,fields:"rule,severity,survive",title:"Constraints de Separadores"}
VIEW:limits_op{kind:"table",target:"$5:LIM:*",reverse:"rows_to_entries",status:cur,fields:"limit,scope,status",title:"Límites Operacionales"}
VIEW:risks_op{kind:"callout",target:"$5:RSK:*",reverse:"callout_to_risk",status:cur,fields:"risk,impact,mitigation,status,survive",title:"Riesgos Operacionales"}
VIEW:pitfalls_op{kind:"table",target:"$5:PFL:*",reverse:"rows_to_entries",status:cur,fields:"pattern,prevention,severity",title:"Pitfalls Operacionales"}
VIEW:diagrams{kind:"puml",target:"$6:DIAG:*",reverse:"verbatim_to_bloque",status:cur,title:"Diagramas Arquitectónicos",preserve:"verbatim"}
VIEW:contracts_full{kind:"table",target:"$7:CNST:*",reverse:"rows_to_entries",status:cur,fields:"rule,severity,survive",title:"Contratos Completos"}
VIEW:survive_rules{kind:"list",target:"$8:!:*",reverse:"items_to_entries",status:cur,fields:"rule,survive",title:"Reglas de Survive"}
VIEW:survive_knowledge{kind:"kv_table",target:"$8:KNW:*",reverse:"row_to_attrs",status:cur,title:"Conocimiento de Survive"}
VIEW:profiles{kind:"table",target:"$9:KNW:*",reverse:"rows_to_entries",status:cur,fields:"topic,content,status",title:"Perfiles Cognitivos"}
VIEW:degrade_rules{kind:"list",target:"$10:!:*",reverse:"items_to_entries",status:cur,fields:"rule,survive",title:"Reglas de Degradación"}
VIEW:hcortex_def{kind:"prose",target:"$11:DESC:hcortex_def",reverse:"body_to_cuerpo",status:cur,title:"Definición HCORTEX"}
VIEW:hcortex_knowledge{kind:"kv_table",target:"$11:KNW:*",reverse:"row_to_attrs",status:cur,title:"Conocimiento HCORTEX"}
VIEW:hcortex_rules{kind:"list",target:"$11:!:*",reverse:"items_to_entries",status:cur,fields:"rule,survive",title:"Reglas HCORTEX"}
VIEW:hcortex_constraints{kind:"table",target:"$11:CNST:*",reverse:"rows_to_entries",status:cur,fields:"rule,severity,survive",title:"Constraints HCORTEX"}
VIEW:hcortex_pitfalls{kind:"table",target:"$11:PFL:*",reverse:"rows_to_entries",status:cur,fields:"pattern,prevention,severity",title:"Pitfalls HCORTEX"}
VIEW:out_def{kind:"prose",target:"$12:DESC:out_def",reverse:"body_to_cuerpo",status:cur,title:"Definición CORTEX-OUT"}
VIEW:out_axiom{kind:"prose",target:"$12:AXM:out_guiding",reverse:"body_to_cuerpo",status:cur,title:"Axima CORTEX-OUT"}
VIEW:out_rules{kind:"list",target:"$12:!:*",reverse:"items_to_entries",status:cur,fields:"rule,survive",title:"Reglas CORTEX-OUT"}
VIEW:out_constraints{kind:"kv_table",target:"$12:CNST:out_naming",reverse:"row_to_attrs",status:cur,title:"Constraints CORTEX-OUT"}
VIEW:out_knowledge{kind:"kv_table",target:"$12:KNW:out_blocks",reverse:"row_to_attrs",status:cur,title:"Conocimiento CORTEX-OUT"}
```