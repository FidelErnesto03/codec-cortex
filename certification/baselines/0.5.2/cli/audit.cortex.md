```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: audit.cortex
source_version: 2.3.1
status: audit
-->

$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"identidad del paquete de auditoría"}
DOM:domain{type:attrs,risk:B,cortex:Semantic,desc:"estado de avance del codec-cortex"}
KNW:knowledge{type:attrs,risk:B,cortex:Semantic,desc:"conocimiento del estado real por capability"}
REF:reference{type:attrs,risk:B,cortex:Semantic,desc:"referencias a artefactos canónicos"}
TAG:tag{type:attrs,risk:B,cortex:Semantic,desc:"metadatos de clasificación de auditoría"}
AUD:audit{type:attrs,risk:M,cortex:Prefrontal,desc:"registro de auditoría por versión"}
RSK:risk{type:attrs,risk:M,cortex:Prefrontal,desc:"riesgo identificado con mitigación"}
LIM:limit{type:attrs,risk:M,cortex:Prefrontal,desc:"límite explícito de madurez"}
DESC:description{type:cuerpo,risk:B,cortex:Semantic,desc:"descripción textual del estado"}

$1
IDN:project{name:"codec-cortex",author:"Fidel Ernesto Lozada A.",version:"2.3.1",license:MIT,spec:"1.2.0-enterprise-candidate",project:"0.3.0",status:"experimental"}
DOM:scope{domain:"CLI determinista para .cortex sin dependencia de LLM",lang_struct:"EN",lang_semantic:"ES",output_human:"HCORTEX=render reversible; CORTEX=denso nativo"}
TAG:meta{category:"AUDIT-PACKAGE",nature:"captura de estado de avance",target:"v2.3.1 corrective hard release"}
REF:art_skill_cortex{path:"skill/cortex/SKILL.md",role:"CORTEX canónico",encoding:CORTEX}
REF:art_skill_hcortex{path:"skill/hcortex/SKILL.md",role:"HCORTEX canónico reversible",encoding:HCORTEX}
REF:art_package_sdist{path:"codec_cortex-2.3.1.tar.gz",role:"sdist instalable",encoding:BINARY}
REF:art_package_full{path:"codec_cortex-2.3.1-full.tar.gz",role:"bundle completo con tests",encoding:BINARY}
REF:art_informe{path:"INFORME_DE_ENTREGA_v2.3.1.md",role:"informe honesto de estado",encoding:TEXT}

$2
DESC:purpose{Este paquete captura el estado de avance real de codec-cortex v2.3.1 tras la auditoría que reclasificó v2.3.0 como prototipo experimental. Sirve como punto de partida verificable para v2.3.2.}
DESC:meta_skill{audit.cortex es un meta-artefacto: no es operacional, es declarativo. Documenta qué funciona, qué no funciona, y qué falta.}
KNW:problem{topic:"CORTEX ⇄ HCORTEX verificable",content:"La promesa fundacional de v2.3.0 no se cumplió. El roundtrip bidireccional perfecto es planned, no current.",status:blocking}
KNW:cortices{topic:"Arquitectura del codec",content:"Parser CORTEX v2 (byte-identical), Writer, VIEW directives (13×13), HCORTEX renderer, HCORTEX parser, Encoder, Equivalence engine (4 niveles)",status:cur}
KNW:maturity{topic:"Madurez real",content:"CORTEX→HCORTEX=current sólido; HCORTEX→CORTEX=experimental (68% entries reconstruidas); Roundtrip bidir perfecto=planned v2.3.2",status:cur}

$3
AUD:v2_3_1{event:"corrective hard release",evidence:"8 P0 cerrados, 4 tests en rojo intencional",result:"experimental — no enterprise-candidate",date:"2026-06-30"}
AUD:v2_3_0{event:"prototipo funcional rechazado",evidence:"roundtrip bidir falla: 421 diffs AST, 33 diffs content",result:"reclasificado a experimental",date:"2026-06-30"}
AUD:v2_2_3{event:"cierre de prerrequisitos PRE-01..PRE-08",evidence:"gate reversible:true, modo display vs canónico, artefactos canónicos publicados",result:"current",date:"2026-06-30"}
AUD:v2_2_2{event:"surgical hardening post v2.2.1",evidence:"SKILL.md migrado con 44 VIEW directives, coverage 100%, --force-write-on-error, --strict, W_VIEW_HETEROGENEOUS_TARGET",result:"current",date:"2026-06-30"}
AUD:v2_2_1{event:"hardening de VIEW directives",evidence:"HCORTEX-R eliminado, reversible por definición, DIAG verbatim, E_VIEW_* rc!=0",result:"current",date:"2026-06-29"}
AUD:v2_2_0{event:"VIEW directives system",evidence:"13 ViewKind × 13 ReverseStrategy, KIND_REVERSE_COMPAT, resolve_target, calculate_view_coverage",result:"current",date:"2026-06-28"}
AUD:v2_0_0{event:"CORTEX v2 parser/writer byte-identical",evidence:"38018 bytes reproducidos, 222 entries, 13 secciones",result:"current",date:"2026-06-25"}

$4
RSK:roundtrip_bidir{risk:"Roundtrip bidireccional perfecto no logrado",impact:"H",mitigation:"4 tests en rojo detectan el gap; v2.3.2 debe resolver tablas sin name, DIAG multilínea, KNW profiles",status:blocking,survive:min}
RSK:encoder_loss{risk:"Encoder pierde 84/266 entries (32%)",impact:"H",mitigation:"Post-write validation E_AST_EQUIVALENCE_FAIL bloquea escritura sin --force-write-on-error",status:cur,survive:min}
RSK:false_claims{risk:"Declarar capacidades no verificadas",impact:"H",mitigation:"v2.3.1 reclasifica todo a experimental; tests honestos fallan si reversibilidad falla",status:mitigated,survive:min}

$5
LIM:maturity{limit:"v2.3.1 es experimental, no enterprise-candidate",scope:"todo el paquete",status:blocking}
LIM:encoder{limit:"Encoder reconstruye 182/266 entries (68%)",scope:"HCORTEX → CORTEX",status:cur}
LIM:hash{limit:"Hash verification estructural, no content-integrity en todos los bloques",scope:"VIEW markers",status:planned}
LIM:coverage_advanced{limit:"Coverage por sigilo/sección/P-level pendiente",scope:"v2-verify-view",status:planned}

$6
IDN:capabilities{name:"Matriz de capacidades v2.3.1",version:"2.3.1",status:"experimental"}
DOM:capability_scope{domain:"CORTEX y HCORTEX v2 con VIEW directives",status:specification}
KNW:cap_cortex_to_hcortex{topic:"CORTEX → HCORTEX",content:"current — 0 errores, 0 warnings, 100% coverage, reversible:true cuando coverage==100",status:cur}
KNW:cap_hcortex_to_cortex{topic:"HCORTEX → CORTEX",content:"experimental — 182/266 entries reconstruidas, post-write validation bloquea CORTEX inválido",status:experimental}
KNW:cap_roundtrip_bidir{topic:"CORTEX ⇄ HCORTEX verificable",content:"planned — T-03/T-04/T-12 en rojo intencional, meta v2.3.2",status:planned}
KNW:cap_view_directives{topic:"VIEW directives (13×13)",content:"current — KIND_REVERSE_COMPAT, resolve_target, calculate_view_coverage",status:cur}
KNW:cap_equivalence{topic:"Motor de equivalencia (4 niveles)",content:"current — byte/AST/semantic/content + diffs por sigilo/sección/VIEW",status:cur}
KNW:cap_errors{topic:"11 errores formales",content:"current — E_HCORTEX_*, E_VIEW_*, E_TABLE_*, E_BLOCK_*, E_AST_EQUIVALENCE_FAIL, W_HCORTEX_DISPLAY_ONLY",status:cur}
KNW:cap_modes{topic:"5 modos de operación",content:"current — normal/strict/audit/recovery/display",status:cur}
KNW:cap_hash{topic:"E_VIEW_HASH_MISMATCH real",content:"current — SHA-256 del contenido vs hash declarado",status:cur}
KNW:cap_cli{topic:"7 comandos CLI v2",content:"current — v2-convert bidir, v2-roundtrip-bidir, v2-compare, v2-verify-view, v2-explain-loss, v2-canonicalize, v2-inspect",status:cur}

$7
DESC:tests_state{Suite actual: 341 passed, 4 failed (intencionales). Los 4 fallos detectan que el roundtrip bidireccional perfecto no se logra. T-03 exige AST-equivalent==True. T-04 exige content-equivalent==True. T-12 exige v2-roundtrip-bidir rc==0. test_cli_v2_convert_hcortex_to_cortex exige 0 errores post-write.}
DESC:next_step{v2.3.2 debe lograr: (1) T-03 pase — AST-equivalent==True, (2) T-04 pase — content-equivalent==True, (3) T-12 pase — v2-roundtrip-bidir rc==0, (4) Reconstruir $6 DIAG, $7 contracts, $9 KNW profiles sin pérdida, (5) Nombres sintéticos reparsables para tablas sin columna name. No avanzar a nuevas funcionalidades hasta que el roundtrip bidireccional perfecto se logre.}
DESC:audit_purpose{Este audit.cortex es el punto de partida verificable para v2.3.2. Captura el estado real sin falsos claims. Cualquier agente que retome el trabajo debe leer este archivo primero.}
