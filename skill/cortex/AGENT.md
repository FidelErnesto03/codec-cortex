<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: skill/cortex/AGENT.md
source_version: 0.5.1
status: current
-->

$0

$1
IDN:agent{}
REF:synthetic_ref_s1_000{skill:"Protocolo CODEC-CORTEX",archivo:"skill/cortex/SKILL.md",propósito:"CORTEX canónico — canon de instalación"}
REF:synthetic_ref_s1_001{skill:"Cerebro operativo",archivo:"brain.cortex",propósito:"Estado vivo consolidado del proyecto"}
REF:synthetic_ref_s1_002{skill:"Identidad del agente",archivo:"skill/cortex/AGENT.md",propósito:"Identidad persistente del agente"}
KNW:inspecci_n{operation:"Inspección",comando:"cortex inspect",desde:"0.3.2"}
KNW:verificaci_n{operation:"Verificación",comando:"cortex verify --strict",desde:"0.3.0"}
KNW:cobertura_view{operation:"Cobertura VIEW",comando:"cortex verify-view",desde:"0.3.2"}
KNW:firma_e2{operation:"Firma (E2)",comando:"cortex verify --signature",desde:"0.3.4"}
KNW:roundtrip{operation:"Roundtrip",comando:"cortex roundtrip",desde:"0.3.2"}
KNW:roundtrip_bidireccional{operation:"Roundtrip bidireccional",comando:"cortex roundtrip-bidir",desde:"0.3.2"}
KNW:conversi_n{operation:"Conversión",comando:"cortex convert",desde:"0.3.2"}
KNW:comparaci_n{operation:"Comparación",comando:"cortex compare",desde:"0.3.2"}
KNW:explicar_p_rdida{operation:"Explicar pérdida",comando:"cortex explain-loss",desde:"0.3.2"}
KNW:canonicalizaci_n{operation:"Canonicalización",comando:"cortex canonicalize",desde:"0.3.2"}
KNW:docstring_e3{operation:"Docstring (E3)",comando:"cortex docstring",desde:"0.3.5"}
KNW:benchmark_e3{operation:"Benchmark (E3)",comando:"cortex benchmark",desde:"0.3.5"}
KNW:diagn_stico{operation:"Diagnóstico",comando:"cortex doctor",desde:"0.3.0"}
KNW:scan_de_secretos_e2{operation:"Scan de secretos (E2)",comando:"cortex doctor --scan-secrets",desde:"0.3.4"}
KNW:auditor_a_e2{operation:"Auditoría (E2)",comando:"cortex audit on/off/status/snapshot",desde:"0.3.4"}
KNW:modos_de_operaci_n_e2{operation:"Modos de operación (E2)",comando:"cortex --mode read-only|editor|admin",desde:"0.3.4"}
KNW:recuperaci_n_legacy{operation:"Recuperación legacy",comando:"cortex recover",desde:"0.3.0"}
REF:synthetic_ref_s1_000{archivo:"skill/cortex/SKILL.md",propósito:"CORTEX canónico — canon de instalación del skill"}
REF:synthetic_ref_s1_001{archivo:"brain.cortex",propósito:"Cerebro local operativo"}
REF:synthetic_ref_s1_002{archivo:"docs/cortex/api/*.cortex",propósito:"Referencia de comandos CLI (fuente de verdad)"}

$2
!synthetic_rule_s2_001{rule:"Al iniciar en cualquier directorio, el agente DEBE ejecutar estas reglas en orden:"}
!synthetic_rule_s2_002{rule:"**Buscar `.cortex/`** subiendo desde el directorio actual (`cwd`) hasta la raíz del sistema de archivos."}
!synthetic_rule_s2_003{rule:"**Si encuentra `.cortex/MANIFEST.cortex` o `.cortex/brain.cortex`:**"}
!synthetic_rule_s2_004{rule:"Activar el skill CODEC-CORTEX automáticamente."}
!synthetic_rule_s2_005{rule:"Cargar `skill/cortex/SKILL.md` (canon de instalación)."}
!synthetic_rule_s2_006{rule:"Leer `brain.cortex` si existe; si no, crearlo desde template."}
!synthetic_rule_s2_007{rule:"Aplicar el flujo `agent_init` del skill."}
!synthetic_rule_s2_008{rule:"**Si NO encuentra `.cortex/`:**"}
!synthetic_rule_s2_009{rule:"Crear el workspace automáticamente: `cortex learn init --workspace ."}
!synthetic_rule_s2_010{rule:"Esto genera `.cortex/` con MANIFEST.cortex, brain.cortex, learn-policies.cortex e index/."}
!synthetic_rule_s2_011{rule:"Activar CODEC-CORTEX y continuar con el flujo `agent_init`."}
!synthetic_rule_s2_012{rule:"**Una vez activado:** toda la memoria del agente se gestiona en formato CORTEX. Las respuestas usan CORTEX-OUT."}
AXM:guiding{> La memoria persistente canónica bajo CODEC-CORTEX se mantiene en `.cortex`. Markdown, YAML o JSON pueden existir como vistas transitorias, edición humana o interoperabilidad. CORTEX-OUT es la respuesta conversacional.}

$3
WRK:entry{}
HDL:synthetic_hdl_s3_001{rule:"agent_init` — Al cargar el skill: leer SKILL.md, identificar reglas Nivel 1, leer brain.cortex, derivar FCS/OBJ si no existen, aplicar CNST, seleccionar perfil CORTEX."}
HDL:synthetic_hdl_s3_002{rule:"pre_action` — Antes de cada acción: verificar FCS activo, OBJ, CNST:blocking, LIM, RSK, STP. Si hay contradicción con CNST:blocking → detener."}
HDL:synthetic_hdl_s3_003{rule:"absorb_pkg` — Al recibir un paquete `.cortex`: validar $0, identificar propósito, no absorber WRK/FCS/OBJ como vivo sin confirmación, integrar KNW/REF/DIAG/CLAIM/LIM, registrar AUD."}
HDL:synthetic_hdl_s3_004{rule:"session_close` — Al cerrar sesión: producir SES (input/output/outcome), LNG si hubo error, AUD si se verificó, RSK si hay riesgo, NXT si hay acción pendiente."}
HDL:synthetic_hdl_s3_005{rule:"hcortex_render` — Para renderizar memoria a HCORTEX: resolver perfil, filtrar por survive, resolver tipo desde $0, agregar source, ordenar P0→P5."}
HDL:synthetic_hdl_s3_006{rule:"recovery_missing_0` — Si el `.cortex` no tiene $0: no ejecutar decisiones operativas, reconstruir $0 mínimo, marcar ambigüedades como RSK/AUD."}

$4
!startup_verify{rule:"Al cargar el skill: ejecutar `cortex verify --strict skill/cortex/SKILL.md`."}
!precommit_verify{rule:"Antes de commit .cortex: `cortex verify --strict <archivo>`."}
!secret_scan{rule:"Antes de commit: `cortex doctor --scan-secrets <archivo>`."}
!output_cortex_out{rule:"Las respuestas del agente usan CORTEX-OUT (no prosa libre)."}
!canonical_names{rule:"Usar nombres canónicos sin prefijo `v2-`."}
!mutation_mode{rule:"Respetar `--mode read-only|editor|admin` y env `$CORTEX_MODE`."}
!docs_source_of_truth{rule:"La ayuda CLI deriva de `docs/cortex/api/*.cortex`."}

$5
LIM:entry{}

$12
KNW:synthetic_knw_s12_000{perfil:"OUT-MIN",bloques:"Resultado + Acción",cuándo:"Presupuesto <500t"}
KNW:synthetic_knw_s12_001{perfil:"OUT-WORK",bloques:"Resultado + Criterio + Acción + Límite",cuándo:"Respuesta operativa"}
KNW:synthetic_knw_s12_002{perfil:"OUT-AUDIT",bloques:"Todos + trazabilidad",cuándo:"Verificación o auditoría"}
KNW:synthetic_knw_s12_003{perfil:"OUT-FULL",bloques:"Todos expandidos",cuándo:"Reporte completo de sesión"}
KNW:synthetic_knw_s12_004{perfil:"OUT-ERROR",bloques:"Código error + causa + recuperación",cuándo:"Error o advertencia"}

$13
VIEW:perfil_agente{kind:"kv_table",target:"$1:IDN:agent",reverse:"row_to_attrs",status:cur,fields:"dimension,valor",title:"Perfil del Agente"}
VIEW:skills_cargados{kind:"table",target:"$1:REF:*",reverse:"rows_to_entries",status:cur,fields:"skill,archivo,proposito",title:"Skills Cargados"}
VIEW:entrypoint{kind:"numbered_list",target:"$2:!:auto_*",reverse:"items_to_ordered_entries",status:cur,title:"Entrypoint — Autodescubrimiento"}
VIEW:principio_rector{kind:"prose",target:"$2:AXM:guiding",reverse:"body_to_cuerpo",status:cur,title:"Principio Rector"}
VIEW:limites_operativos{kind:"kv_table",target:"$5:LIM:*",reverse:"row_to_attrs",status:cur,fields:"dimension,valor",title:"Límites Operativos"}
VIEW:memoria_trabajo{kind:"kv_table",target:"$3:WRK:*",reverse:"row_to_attrs",status:cur,fields:"dimension,valor",title:"Memoria de Trabajo"}
VIEW:handlers_agente{kind:"numbered_list",target:"$3:HDL:*",reverse:"items_to_ordered_entries",status:cur,title:"Handlers del Agente"}
VIEW:comandos_cli{kind:"table",target:"$1:KNW:commands",reverse:"rows_to_entries",status:cur,fields:"operacion,comando,version",title:"Comandos CLI"}
VIEW:perfiles_salida{kind:"table",target:"$12:KNW:out_profile_*",reverse:"rows_to_entries",status:cur,fields:"perfil,bloques,cuando",title:"Perfiles de Salida CORTEX-OUT"}
VIEW:reglas_obligatorias{kind:"numbered_list",target:"$4:!:*",reverse:"items_to_ordered_entries",status:cur,title:"Reglas Obligatorias"}
VIEW:referencias_agente{kind:"table",target:"$1:REF:*",reverse:"rows_to_entries",status:cur,fields:"archivo,proposito",title:"Referencias"}
