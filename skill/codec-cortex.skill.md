$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
RUL:rule{type:attrs,weight:H,fields:"id:text|rule:text|detail:text",focus:rule,desc:"Regla normativa verificada contra la implementacion de referencia codec-cortex. id es clave unica, rule enuncia la regla, detail referencia spec o modulo."}
TXT:text{type:cuerpo,weight:M,desc:"Texto explicativo breve. Cuerpo libre NFC."}
PRC:proc{type:attrs-pos,weight:H,pos:"step:int|action:text|note:text?",focus:action,desc:"Paso de procedimiento generativo o transaccional."}
EX:example{type:bloque,weight:M,desc:"Ejemplo verbatim de CORTEX o HCORTEX. Bloque preserva bytes exactos."}
API:api{type:attrs,weight:M,fields:"name:text|signature:text|version:atom|status:atom|notes:text?",focus:name,desc:"Superficie publica verificada de codec-cortex (Python)."}
HDL:handler{type:attrs-pos,weight:M,pos:"operation:text|status:atom|scope:text",focus:operation,desc:"Comando CLI o handler publico de codec-cortex."}
TST:test{type:attrs,weight:M,fields:"id:text|command:text|result:atom|scope:text",focus:id,desc:"Evidencia ejecutable de una capacidad."}

$1: ARQUITECTURA:CORE
RUL:codec{id:"codec",rule:"CORTEX es un codec ideatico lineal: lenguaje de maquina para LLM. La unidad semantica es la Idea: SIGIL:nombre + payload conforme al glosario local. Un documento es $0 (glosario) + secciones $1,$2,... con Ideas.",detail:"Las herramientas (parser, c14n, HCORTEX) verifican, canonicalizan y proyectan; no interpretan contenido."}
RUL:dialectos{id:"dialectos",rule:"Dialectos: 0.1 (superficie fundamental, 5 shapes), 0.2 (eje slots ortogonal sobre los mismos shapes), 1.0 (canon unificado: superficie 0.1 + eje slots, aridad posicional estricta). Escritura canonica = cortex:1.0.",detail:"CORTEX-SPEC-1.0.md. 0.1/0.2 permanecen como alias de lectura (spec S11.1). cortex:1 es G007."}
RUL:dispatch{id:"dispatch",rule:"La unica senal de version es $0:format{cortex:X}. parse_cortex(source) la lee y enruta: 0.1 a parse_cortex_01; 0.2 y 1.0 a parse_slots.",detail:"NUNCA inferir version por presencia de ※. En doc 0.1, ※ en strings/cuerpo/bloque es contenido ordinario; ※ estructural dispara I058_MIXED_SURFACE_VERSION."}
RUL:coexistencia{id:"coexistencia",rule:"Un documento se declara una sola vez. Version ausente = G010_FORMAT_REQUIRED; version desconocida = G007_UNSUPPORTED_VERSION.",detail:"dispatcher.py _detect_version(). Valores validos: 0.1, 0.2, 1.0."}
RUL:linea_idea{id:"linea-idea",rule:"Una linea fisica por idea regular. Excepcion: cuerpo/bloque con payload delimitado { ... } siguen siendo UNA idea en varias lineas.",detail:"Spec 1.0 S1 axioma 1, S4.3."}
RUL:arity{id:"arity-strict",rule:"attrs-pos y relacion: celdas entre requeridos y total del contrato (I012_POSITIONAL_ARITY en ambos extremos). La tolerancia 0.1 era un bug; estricto en las 5 superficies.",detail:"Spec 1.0 S4.1. parser.py, parser.go, parser.js, parser.rs, codec-cortex.sh."}
RUL:no_inferencia{id:"no-inferencia",rule:"El transformador no interpreta el contenido ideatico. Solo aplica schemas declarados, contratos, shapes y codificaciones.",detail:"El AST es artefacto interno; la sintaxis no es exposicion mecanica del AST."}
RUL:pipe_quoted{id:"pipe-quoted",rule:"Celda con | interno va string quoted; sin comillas se lee como celdas extra (I012). La correccion es una celda quoted, no mas celdas.",detail:"Spec 1.0 S4.2 + S12.1. Observado: HDL:migrate con 7 celdas vs contrato de 3."}
RUL:idea_unica{id:"idea-unica",rule:"SIGIL:nombre debe ser unico por seccion (I006_DUPLICATE_IDEA_ADDRESS). Secuencias nombran cada elemento: PRC:p1, PRC:p2.",detail:"Spec 1.0 S12.2."}
RUL:densidad{id:"densidad",rule:"Contenido normativo en ideas tipadas (RUL, API, PRC, TST), no en cuerpos prosa. cuerpo es payload semantico; bloque es verbatim (ejemplos, referencias). Un doc que parsea pero diluye reglas en prosa es conforme y aun asi mal formado: la forma tambien es contrato.",detail:"Spec 1.0 S12.5. Leccion del propio skill."}
RUL:declarar_lo_usado{id:"declarar-lo-usado",rule:"La version declara la gramatica del documento, no la del proyecto. Sin slots, cortex:1.0 es escritura canonica; cortex:1 no existe (G007). 0.1/0.2 son alias de lectura.",detail:"Spec 1.0 S11.1 + S12.4."}
RUL:serializar{id:"serializar",rule:"Al escribir: string con newline va escapado (\\n) o rechazado — newline literal rompe la linea de la idea y el artefacto que la contiene.",detail:"Spec 1.0 S12.6. Observado: handoff .arqux corrupto con newline en nombre de archivo."}

$2: DOCUMENTO Y GLOSARIO:CORE
RUL:doc{id:"doc",rule:"Estructura: (1) $0:KERNEL linea 1, (2) $0:format{cortex:X,encoding:UTF-8[,language]} linea 2, (3) meta opcionales ($0:sigil-map,enum_*,micro_*,namespace_*,extension_*), (4) declaracion de cada sigilo usado fuera de $0, (5) secciones $N con Ideas.",detail:"$0 no reaparece (G002). Sigilo no declarado = I001."}
RUL:formato{id:"formato",rule:"$0:format{cortex:1.0,encoding:UTF-8,language:XX}. Una sola declaracion (G006). encoding distinto de UTF-8 = G011. Atributos extra (language, etc.) se preservan.",detail:"dispatcher.py _detect_version() hace bootstrap regex."}
RUL:seccion{id:"seccion",rule:"Secciones: $N: TITULO o $N: TITULO:CAPA. N entero positivo, subsecciones $N.M validas. CAPA opcional: KERNEL|CORE|KNOW|DATA|FLOW|CACHE (metadata, sin semantica runtime; DATA por defecto en N>=2). Id repetido = S002.",detail:"Spec seccion 18."}
RUL:declaracion{id:"declaracion",rule:"Sigilo: SIGIL:nombre{type:SHAPE,weight:B|M|H,focus:CAMPO,fields|pos:CONTRATO,desc:TEXTO,open:B?}. attrs requiere fields (G021); attrs-pos/relacion requieren pos (G022); relacion >=3 campos (G023); cuerpo/bloque focus=$body. open:true permite extras en attrs.",detail:"_build_symbol_def() valida G016-G025."}
RUL:shapes{id:"shapes",rule:"5 shapes: attrs={k:v} una linea; attrs-pos=|celda| una linea; cuerpo={texto} o multilinea (NFC); bloque={...} verbatim multilinea; relacion=|a|b|c| una linea. Delimitador incorrecto = I004.",detail:"Spec seccion 13."}
RUL:attrs{id:"attrs",rule:"attrs: campos en ORDEN del contrato. focus SIEMPRE string quoted. No-focus: quoted si tiene espacios/delimitadores, bare si atom valido.",detail:"Spec 13.1 + C14N seccion 10."}
RUL:pipe{id:"pipe",rule:"attrs-pos/relacion: celdas en ORDEN de pos. Opcionales solo al final. String con | va quoted. Aridad estricta: I012 si celdas fuera de [requeridos, contrato].",detail:"Spec 13.2/13.5 + S4.1."}
RUL:cuerpo_bloque{id:"cuerpo-bloque",rule:"cuerpo/bloque multilinea: SIGIL:nombre{ abre, cierre } en linea propia. Sin cierre = S007_UNCLOSED_BODY. cuerpo=NFC, bloque=verbatim.",detail:"Spec 13.3/13.4."}
RUL:focus{id:"focus",rule:"focus requerido en attrs/attrs-pos/relacion y debe existir en contrato: G024 si falta, G025 si no esta en fields/pos.",detail:"Spec 11.5."}
RUL:contrato{id:"contrato",rule:"fields/pos: campo:tipo separados por |. Tipos: any text atom int dec bool null list %enum. Sufijo ? = opcional. Sin tipo = any.",detail:"Spec seccion 14. parse_contract_fields()."}
RUL:scalares{id:"scalares",rule:"string (escapes \\n \\r \\t \\b \\f \\\" \\\\ \\uXXXX), atom (bare, sin espacios), integer, decimal (lexema exacto: 0.75 != 0.750), boolean, null, list plana. Atom invalido = L010.",detail:"Spec seccion 17."}
RUL:enum{id:"enum",rule:"$0:enum_X{values:\"a|b|c\"}; referencia %X en contrato. Mal formado = G014; referencia no declarada = G026.",detail:"Spec seccion 15."}
RUL:micro{id:"micro",rule:"$0:micro_t{expand:atom}. Expansion en C14N solo; no en strings/keys/nombres/sigilos. Sin expand = G012.",detail:"Spec seccion 16."}
RUL:ns{id:"ns",rule:"$0:namespace_a{...}; uso a::SIGIL:nombre. Namespace no declarado = error. ! es reservado interno.",detail:"Spec seccion 20."}
RUL:ext{id:"ext",rule:"$0:extension_X{namespace,id,version,required,desc}. required:true no soportado = X002_REQUIRED_EXTENSION_UNSUPPORTED.",detail:"Spec seccion 21."}

$3: EJE SLOTS:CORE
RUL:slots_eje{id:"slots-eje",rule:"El eje slots codifica celdas como ※N:valor en attrs/attrs-pos/relacion. Integrado en 1.0 como seccion normativa (no dialecto aparte). cuerpo/bloque nunca usan slots.",detail:"Spec 1.0 S5."}
RUL:marker{id:"marker",rule:"Marker = ※ U+203B. Homoglifos • · ∙ ● prohibidos en posicion estructural (L020). Como contenido en strings/cuerpo/bloque es ordinario.",detail:"slots.py HOMOGLYPHS."}
RUL:indice{id:"indice",rule:"slot-index = digito ASCII 1-9 seguido de digitos. Prohibido: 0 (L022), cero inicial (L023), digito no-ASCII (L021), espacios (L021/L024). Limite implementado 1_000_000 (I057).",detail:"slots.py SLOT_INDEX_MAX."}
RUL:sigil_map{id:"sigil-map",rule:"$0:sigil-map{marker:\"※\",codepoint:\"U+203B\",base:1,syntax:\"※N:valor\",order:\"ascending\"}. Exactamente 5 attrs literales (G032). Antes de todo sigilo encoding:slots (G041). Una sola vez (G031). Requerido (G030).",detail:"slotparser.py."}
RUL:encoding_slots{id:"encoding-slots",rule:"encoding:slots solo en attrs/attrs-pos/relacion. Prohibido en cuerpo/bloque (G039), con fields/pos (G040) u open:true (G038).",detail:"slotparser.py 396-410."}
RUL:slots_attr{id:"slots-attr",rule:"Contrato en attr slots:\"1=name:type?|2=name:type\". Posiciones desde 1 ascendentes sin huecos (G034), unicas (G035), nombres unicos (G036).",detail:"slots.py parse_slot_contract()."}
RUL:slot_focus{id:"slot-focus",rule:"focus en sigilo slots referencia POSICION (entero) de slot requerido. Inexistente u opcional = G037.",detail:"slotparser.py."}
RUL:slot_idea{id:"slot-idea",rule:"Idea slots: SIGIL:nombre{※1:v,※2:v}. Braces siempre, orden ascendente (I054), sin duplicados (I051), sin desconocidos (I052), requeridos presentes (I053), sin attr nombrado (I055), sin pipe (I056).",detail:"slots.py parse_slot_payload()."}
RUL:slot_glossary{id:"slot-glossary",rule:"※ prohibido en $0 (I050). Excepcion: attr marker:\"※\" del sigil-map es string content.",detail:"slotparser.py."}
RUL:mixed_version{id:"mixed-version",rule:"Doc declarado cortex:0.1 no puede tener ※ estructural (I058). Doc 0.2/1.0 puede mezclar sigilos con y sin encoding:slots; no es mixed-version.",detail:"slots.py check_mixed_surface_legacy()."}
RUL:ast_nominal{id:"ast-nominal",rule:"AST nominal: attrs nominal y attrs-slots con mismo contrato logico producen ASTs y hashes distintos.",detail:"Spec 0.2 seccion 9."}

$4: HCORTEX:CORE
RUL:hcortex{id:"hcortex",rule:"HCORTEX es la proyeccion humana determinista de CORTEX: render(doc) es funcion pura del AST — mismo AST, mismos bytes en las 5 superficies. Clases: LOSSLESS o DECLARED-LOSS (catalogo L4xx).",detail:"Spec 1.0 S8. Invariante sin-copia-oculta H481: ningun render valido esconde AST."}
RUL:hcortex_env_01{id:"hcortex-env-01",rule:"HCORTEX 0.1: <!-- HCORTEX v=0.1 t=canonical -->. Sin envelope = H400; BOM = H404.",detail:"hcortex-0.1.md seccion 3."}
RUL:hcortex_schemas_01{id:"hcortex-schemas-01",rule:"5 schemas: prose, table, list, check, diagram en <!-- schema:N -->. Shape determina schema: attrs/pos/relacion=table, cuerpo=prose, bloque=diagram.",detail:"hcortex-0.1.md seccion 4."}
RUL:hcortex_glossary_01{id:"hcortex-glossary-01",rule:"$0 no es contenido visible; para roundtrip incluir <!-- glossary ... --> con glosario textual completo.",detail:"hcortex-0.1.md seccion 6."}
RUL:hcortex_env_02{id:"hcortex-env-02",rule:"HCORTEX 0.2: <!-- HCORTEX v=0.2 t=canonical k=corpus -->. Sin envelope = H401; version != 0.2 = H401; BOM = H490.",detail:"slothcortex.py ENVELOPE_RE."}
RUL:hcortex_glossary_02{id:"hcortex-glossary-02",rule:"Requiere <!-- glossary --> completo (format, sigil-map, sigilos). Hidden pero NO shadow copy: es el glosario textual para recompilar. Ausente = H403.",detail:"slothcortex.py GLOSSARY_RE."}
RUL:hcortex_no_hidden{id:"hcortex-no-hidden",rule:"Rechaza payloads ocultos: <!-- cortex-ast:|base64:|shadow:|ast:|internal: = H481_HIDDEN_COPY. No usar --embed-ast para roundtrip.",detail:"slothcortex.py HIDDEN_COPY_RE."}
RUL:hcortex_schema_02{id:"hcortex-schema-02",rule:"<!-- schema:N --> por seccion. Idea = ### SIGIL:nombre + tabla (attrs/pos/relacion) | prose (cuerpo) | fence (bloque).",detail:"slothcortex.py _render_idea_slots()."}
RUL:hcortex_roundtrip{id:"hcortex-roundtrip",rule:"0.2: canonicalize(compile(render(D))) == canonicalize(D), byte-exacto en 5 shapes. 0.1: roundtrip estructural, no byte-exacto — perdidas declaradas en L4xx.",detail:"slothcortex.py run_roundtrip(). Spec 1.0 S8.1-S8.2."}
RUL:loss{id:"loss-catalog",rule:"Perdidas declaradas (cerradas): L401 fence bloque, L402 comentarios fuera de glosario, L403 whitespace intralinea, L404 CAPA ausente, L405 orden attrs open. loss-report conforme a schema.",detail:"Spec 1.0 S8.2 + errors-1.0.md."}

$5: C14N Y HASH:CORE
RUL:c14n01{id:"c14n01",rule:"C14N: NFC fuera de bloque, expansion microtokens, quoting contract-aware (focus siempre quoted), sin comentarios/blank/trailing-spaces, un LF final, sin BOM/CR. Dominio CORTEX-C14N-0.1 (0.1) / C14N-0.2 (0.2/1.0).",detail:"c14n.py / slotc14n.py."}
RUL:c14n_orden{id:"c14n-orden",rule:"Orden canonico: $0 primero; secciones $N ascendente; ideas en ORDEN DOCUMENTAL (fijado en 1.0). Glosario en orden de declaracion.",detail:"Spec 1.0 S7. Cierra el pendiente de 0.1."}
RUL:hash{id:"hash",rule:"hash = SHA-256(dominio + 0x00 + canonical_bytes), sha256:<64hex>. Docs con mismo contenido pero distinta version producen hashes distintos (dominio difiere).",detail:"dispatcher.hash_cortex por doc.cortex_version."}
RUL:idempotencia{id:"idempotencia",rule:"canonicalize(canonicalize(x)) == canonicalize(x). Misma version: x identico a y sii canonicalize(x)==canonicalize(y).",detail:"Vector D1 del certificado."}

$6: MIGRACION:FLOW
PRC:mig_p1|1|"migrate_inspect(source_path): lee format, lista sigilos y contratos"|"JSON"
PRC:mig_p2|2|"migrate_plan(source, to_version, plan.json): captura source_sha256"|"aborta si source cambia"
PRC:mig_p3|3|"migrate_apply(plan.json, out): verifica sha256, escribe atomico + backup .bak"|"restaura si verify falla"
PRC:mig_p4|4|"migrate_verify(source, out): equivalencia AST profunda"|"idea_equivalence=pass"
PRC:mig_p5|5|"migrate_rollback(plan.json): restaura source desde .bak"|"no toca output"
PRC:mig_p6|6|"migrate to-1.0 <file> [out]: reescribe format a cortex:1.0, idempotente, verifica parseo"|"0.1/0.2 a 1.0 sin rescribir estructura"
RUL:mig_perdida{id:"mig-perdida",rule:"0.1 -> 0.2 (slots) convierte attrs/pos/relacion a slots automaticamente (sin open:true). a 1.0 solo cambia la declaracion: la union acepta la superficie completa.",detail:"slotmigrate.py _perform_migration + migrate_to_1_0."}

$7: API PYTHON:DATA
API:parse_cortex{name:"parse_cortex",signature:"parse_cortex(source: str) -> Document",version:python,status:current,notes:"Entrada dual. Lee $0:format y enruta 0.1->parser.py, 0.2/1.0->slotparser.py. BOM = U001."}
API:parse_slots{name:"parse_slots",signature:"parse_slots(source: str, version='0.2') -> Document",version:python,status:current,notes:"Parser slots/1.0. slotparser.py."}
API:canonicalize{name:"canonicalize",signature:"canonicalize(doc) -> str",version:python,status:current,notes:"Dispatcher por doc.cortex_version: 0.1->c14n, 0.2/1.0->slotc14n."}
API:hash_cortex{name:"hash_cortex",signature:"hash_cortex(doc) -> str",version:python,status:current,notes:"sha256:<64hex>, dominio por version."}
API:render_hcortex_slots{name:"render_hcortex_slots",signature:"render_hcortex_slots(doc, embed_ast=False) -> str",version:python,status:current,notes:"Render HCORTEX 0.2. embed_ast=True inyecta cortex-ast (NO para roundtrip: H481)."}
API:compile_hcortex_slots{name:"compile_hcortex_slots",signature:"compile_hcortex_slots(text) -> (Document|None, [diags])",version:python,status:current,notes:"Compilador HCORTEX 0.2. Rechaza H481/H401/H403/H490."}
API:migrate_to_1_0{name:"migrate_to_1_0",signature:"migrate_to_1_0(source_path, out_path=None) -> dict",version:python,status:current,notes:"Idempotente, reescribe format a 1.0 y verifica parseo. slotmigrate.py."}
API:migrate_apply_api{name:"migrate_apply",signature:"migrate_apply(plan_path, out_path=None) -> dict",version:python,status:current,notes:"Migracion transaccional 0.1->0.2 atomica."}

$8: CLI:DATA
HDL:parse|parse <file>|current|AST JSON por dispatcher (0.1/0.2/1.0)
HDL:validate|validate <file>|current|Valida doc; exit 0 si valido
HDL:canonicalize|canonicalize <file>|current|Bytes canonicos por dispatcher
HDL:hash|hash <file>|current|Hash canonico sha256:...
HDL:conformance|conformance [MANIFEST_DIR]|current|Slots conformance harness (0.2)
HDL:tohcortex|to-hcortex [--embed-ast] <file>|current|Render HCORTEX 0.2
HDL:fromhcortex|from-hcortex <file>|current|Compila HCORTEX 0.2
HDL:migrate|migrate <cmd> <file> [args]|current|"inspect|plan|apply|verify|rollback|to-1.0"

$9: ERRORES:DATA
RUL:err_familias{id:"err-familias",rule:"Familias: L lexico, S sintaxis, G glosario, I idea, X extension, U unicode, H hcortex, L4xx perdida declarada. Catalogo cerrado 1.0: codigo con emisor en >=1 superficie o reserved.",detail:"errors-1.0.md: mapa mecanico 83 codigos x 5 superficies."}
RUL:err_g{id:"err-g",rule:"G001,G002,G004,G006,G007,G008,G010,G011,G012,G014,G015,G016,G017,G018,G019,G020,G021,G022,G023,G024,G025,G026,G027; slots: G030,G031,G032,G033,G034,G035,G036,G037,G038,G039,G040,G041.",detail:"errors-1.0.md."}
RUL:err_i{id:"err-i",rule:"I001-I016 (incluye I012_POSITIONAL_ARITY estricto en 1.0); slots: I050-I058.",detail:"parser.py / slotparser.py."}
RUL:err_h{id:"err-h",rule:"H400-H404 doc 0.1, H410-H472 por capa, H401/H403/H481/H490 en 0.2. Perdidas: L401-L405.",detail:"slothcortex.py + spec S8.2."}
RUL:err_recuperacion{id:"err-recuperacion",rule:"Mapeo error -> correccion: I001 declarar sigilo; G024 agregar focus; G021/G022 agregar fields/pos; I012 ajustar celdas al contrato o corregir contrato; G030 declarar sigil-map antes; I050 quitar ※ de $0; I058 migrar declaracion o quitar ※ estructural; H481 quitar cortex-ast:/base64:/shadow:.",detail:"errors-1.0.md."}

$10: GENERACION:FLOW
PRC:gen_p1|1|"$0:KERNEL en linea 1"|"un $0 unico"
PRC:gen_p2|2|"$0:format{cortex:1.0,encoding:UTF-8,language:XX} en linea 2"|"escritura canonica"
PRC:gen_p3|3|"Opcional: $0:sigil-map con los 5 attrs literales si habra encoding:slots"|"G032 si se desvia"
PRC:gen_p4|4|"Declarar enums, micros, namespaces, extensions opcionales"|
PRC:gen_p5|5|"Declarar cada sigilo: type,weight,focus,fields|pos|slots,desc"|"contrato completo"
PRC:gen_p6|6|"Secciones $1:,$2: con Ideas conformes al shape declarado"|"una linea por idea"
PRC:gen_p7|7|"Verificar: parse + validate + canonicalize idempotente"|"sin errores"
RUL:gen_errores{id:"gen-errores",rule:"Errores frecuentes en generacion: I001 (sigilo no declarado), G024 (focus), G021/G022 (contrato), I012 (aridad), L010 (atom invalido), I050 (※ en glosario).",detail:"Verificar contra errors-1.0.md."}

$11: VALIDACION:DATA
TST:probes{id:"P01-P29",command:"python scripts/ccx_probes.py",result:pass,scope:"0.1/0.2, slots, HCORTEX, migration, I058"}
TST:conformance{id:"conformance",command:"python -m codec_cortex conformance",result:pass,scope:"Corpus slots manifest: 67/67"}
TST:certificate{id:"level-A",command:"PYTHONPATH=. python bench/certify.py",result:pass,scope:"D1 140/140, D2 140/140, D3 5/5, D4 140/140, D5 pass"}
TST:node{id:"node-tests",command:"node --test codec-cortex-node/test/*.test.js",result:pass,scope:"Paridad Node.js 22/22"}
TST:vectors_1_0{id:"vectors-1.0",command:"parse corpus conformance/1.0",result:pass,scope:"70 valid + 2 invalid (I012, G007)"}
RUL:evidencia{id:"evidencia",rule:"No declarar Gate listo, Standard ratificado ni conformidad completa sin evidencia independiente reproducible. Capacidad implementada != capacidad certificada.",detail:"audit.sig Nivel A firmado por auditor independiente."}

$12: EJEMPLOS:KNOW
EX:minimo_1_0{
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
KNW:knowledge{type:attrs,weight:M,fields:"topic:text|content:text",focus:content,desc:"Conocimiento verificado"}
$1: KNOWLEDGE
KNW:cortex{topic:"CORTEX",content:"Codec ideatico lineal para LLM."}
}
EX:slots_1_0{
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8}
$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}
KNW:knowledge{type:attrs,encoding:slots,weight:H,slots:"1=topic:text|2=content:text?",focus:1,schema:table,desc:"Conocimiento",open:false}
$1: KNOW
KNW:codec{※1:"CORTEX",※2:"Codec ideatico lineal"}
}
EX:hcortex_02{
<!-- HCORTEX v=0.2 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}
KNW:knowledge{type:attrs,encoding:slots,weight:H,slots:"1=topic:text|2=content:text?",focus:1,schema:table,desc:"Conocimiento",open:false}
<!-- /glossary -->

## §1: KNOW

<!-- schema:1 -->
### KNW:codec
| topic | content |
|---|---|
| CORTEX | Codec ideatico lineal |
<!-- /schema:1 -->
}
EX:mixed_version_invalid{
$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es}
KNW:knowledge{type:attrs,weight:H,fields:"topic:text|content:text",focus:content,desc:"Invalido"}
$1: KNOW
KNW:codec{topic:※1:"CORTEX"}

RESULTADO: I058_MIXED_SURFACE_VERSION. Un doc 0.1 no puede tener ※ estructural. Solucion: declarar cortex:1.0 con $0:sigil-map, o quitar el ※.
}
EX:migration_cmd{
python -m codec_cortex.slotmigrate inspect old.cortex
python -m codec_cortex.slotmigrate plan old.cortex plan.json
python -m codec_cortex.slotmigrate apply plan.json new.cortex
python -m codec_cortex.slotmigrate verify old.cortex new.cortex
python -m codec_cortex.slotmigrate rollback plan.json
python -m codec_cortex.slotmigrate to-1.0 doc.cortex
}

$13: REFERENCIAS:KNOW
EX:paths{
Specs: docs/standard/CORTEX-SPEC-1.0.md (canon draft), CORTEX-SPEC-0.1.md, CORTEX-SPEC-SLOTS.md, C14N-0.1.md, C14N-SLOTS.md, hcortex-0.1.md, hcortex-slots.md
Errores: docs/standard/errors-1.0.md (mapa cerrado), errors.md, errors-slots.md
Gramatica: docs/grammar/cortex-1.0.ebnf|abnf
Esquemas: docs/schemas/ast-schema-1.0.json
Corpus: conformance/1.0 (vectores normativos)
API: codec_cortex/ dispatcher.py parser.py slotparser.py c14n.py slotc14n.py hcortex.py slothcortex.py slotmigrate.py
Certificado: bench/certify.py + .github/workflows/certificate.yml
}
