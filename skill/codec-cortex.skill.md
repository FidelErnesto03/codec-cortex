$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es}
RUL:rule{type:attrs,weight:H,fields:"id:text|rule:text|detail:text",focus:rule,desc:"Regla normativa verificada contra la implementacion de referencia codec-cortex. id es clave unica, rule enuncia la regla, detail referencia spec o modulo."}
TXT:text{type:cuerpo,weight:M,desc:"Texto explicativo en espanol. Cuerpo libre NFC, foco es el texto completo."}
GEN:generate{type:cuerpo,weight:H,desc:"Instruccion directa de generacion o transformacion para la IA. Pasos accionables conformes a codec-cortex."}
EX:example{type:bloque,weight:M,desc:"Ejemplo verbatim de CORTEX 0.1, CORTEX 0.2, HCORTEX 0.1 o HCORTEX 0.2. Bloque preserva bytes exactos."}
API:api{type:attrs,weight:M,fields:"name:text|signature:text|version:atom|status:atom|notes:text?",focus:name,desc:"Superficie publica verificada de codec-cortex (Python)."}
HDL:handler{type:attrs-pos,weight:M,pos:"operation:text|status:atom|scope:text",focus:operation,desc:"Comando CLI o handler publico de codec-cortex."}
TST:test{type:attrs,weight:M,fields:"id:text|command:text|result:atom|scope:text",focus:id,desc:"Evidencia ejecutable de una capacidad."}

$1: ARQUITECTURA:CORE
TXT:meta{
CORTEX es un codec ideatico lineal: un lenguaje de maquina para modelos de lenguaje (LLM/SLM). La IA lee y escribe CORTEX directamente, sin parser ni AST ni validacion formal. Las herramientas de transformacion (parser, canonicalizador, renderizador HCORTEX) existen para verificar, canonicalizar y proyectar a la representacion humana, no para interpretar el contenido.
La unidad semantica es la Idea: SIGIL:nombre + payload conforme al glosario local. Un documento es $0 (glosario) seguido de secciones $1, $2, ... con Ideas.
CORTEX 0.1 (draft) define 5 shapes fundamentales: attrs, attrs-pos, cuerpo, bloque y relacion. CORTEX 0.2 (normative-draft) anade un eje de codificacion por slots explicitos (marker U+203B) ortogonal a los 5 shapes; no introduce un sexto shape ni reemplaza 0.1.
HCORTEX es la proyeccion humana con esquemas visuales. HCORTEX 0.1 usa 5 schemas (prose, table, list, check, diagram) y envelope v=0.1. HCORTEX 0.2 anade envelope v=0.2, hidden glossary block y la invariante no-hidden-copy (H481).
}
RUL:dispatch{id:"dispatch",rule:"La unica senal de version es $0:format{cortex:X}. El dispatcher parse_cortex(source) lee esa linea y enruta a parse_cortex_01 (0.1) o parse_slots (0.2).",detail:"NUNCA inferir version por la presencia de ※. Un doc 0.1 puede contener ※ en strings/cuerpo/bloque como contenido ordinario. ※ estructural en doc 0.1 dispara I058_MIXED_SURFACE_VERSION."}
RUL:coexistencia{id:"coexistencia",rule:"0.1 y 0.2 coexisten. Un documento se declara una sola vez con $0:format{cortex:0.1|0.2,encoding:UTF-8,...}. Version ausente = G010_FORMAT_REQUIRED; version desconocida = G007_UNSUPPORTED_VERSION.",detail:"dispatcher.py _detect_version(). Solo 0.1 y 0.2 son validos."}
RUL:no_inferencia{id:"no-inferencia",rule:"El transformador no interpreta el contenido ideatico. Solo aplica schemas declarados, contratos, shapes y codificaciones.",detail:"Spec 0.1 seccion 1. El AST es artefacto interno; la sintaxis no es exposicion mecanica del AST."}

$2: CORTEX 0.1:CORE
TXT:intro_01{
CORTEX 0.1 es la superficie fundamental. Todo lo valido en 0.1 permanece valido en 0.2 salvo donde 0.2 anade reglas especificas para slots. Esta seccion cubre la estructura completa de un documento 0.1: glosario, secciones, sigilos, shapes, contratos, escalares, enum, microtokens, namespaces y extensiones.
}
RUL:doc_01{id:"doc-01",rule:"Un documento CORTEX 0.1 tiene: (1) $0 como primera seccion unica, (2) $0:format{cortex:0.1,encoding:UTF-8} en la siguiente linea, (3) declaracion de cada sigilo usado fuera de $0, (4) secciones $1,$2,... con Ideas.",detail:"Spec 0.1 seccion 7. $0 no reaparece (G002). Cada sigilo usado fuera de $0 debe declararse en $0 (I001 si falta)."}
RUL:formato_01{id:"formato-01",rule:"$0:format{cortex:0.1,encoding:UTF-8,language:XX}. Atributos extra se preservan (language, etc.). Solo una declaracion format por documento. Sin $0:format el dispatcher lanza G010_FORMAT_REQUIRED. Version distinta de 0.1 o 0.2 lanza G007_UNSUPPORTED_VERSION. encoding distinto de UTF-8 lanza G011_ENCODING_REQUIRED.",detail:"Spec 0.1 seccion 9. dispatcher.py _detect_version() hace bootstrap con regex multilinea."}
RUL:seccion{id:"seccion",rule:"Secciones: $N: TITULO o $N: TITULO:CAPA. N entero positivo. Subsecciones $N.M validas. CAPA opcional: KERNEL|CORE|KNOW|DATA|FLOW|CACHE. El parser asigna DATA por defecto a N>=2 sin capa.",detail:"Spec 0.1 seccion 18. CAPA es metadata (Section.capa), sin semantica de runtime, eviccion o memoria. Id repetido = S002_DUPLICATE_SECTION."}
RUL:glosario{id:"glosario",rule:"$0 contiene: (a) $0:KERNEL (o $0:NOMBRE) como encabezado, (b) $0:format{...}, (c) meta-declaraciones opcionales ($0:enum_X, $0:micro_X, $0:namespace_X, $0:extension_X), (d) declaraciones de sigilo SIGIL:nombre{...}. TODAS usan attrs {k:v} en UNA linea fisica.",detail:"Spec 0.1 seccion 3 (glossary). No hay separacion formal entre meta y sigilos en $0."}
RUL:declaracion{id:"declaracion",rule:"Declaracion de sigilo: SIGIL:nombre{type:SHAPE,weight:B|M|H,focus:CAMPO,fields:CONTRATO|pos:CONTRATO,desc:TEXTO}. Para attrs: fields obligatorio. Para attrs-pos/relacion: pos obligatorio. Para cuerpo/bloque: focus opcional ($body por defecto). open:true permite campos extras en attrs.",detail:"Spec 0.1 seccion 11. _build_symbol_def() valida G016-G025."}
RUL:shapes{id:"shapes",rule:"5 shapes: attrs = {k:v,k:v} una linea; attrs-pos = |celda|celda| una linea; cuerpo = {texto} corto o {\\n...\\n} multilinea; bloque = {\\n...\\n} verbatim; relacion = |source|pred|target| una linea. Delimitador incorrecto = I004_SHAPE_DELIMITER_MISMATCH.",detail:"Spec 0.1 seccion 13."}
RUL:attrs{id:"attrs",rule:"attrs: SIGIL:nombre{clave:valor,clave:valor}. Campos en ORDEN del contrato (fields). focus SIEMPRE string quoted. Texto no-focus: quoted si tiene espacios o delimitadores, bare si es atom valido. open:true permite campos extras.",detail:"Spec 0.1 seccion 13.1 + C14N-0.1 seccion 10."}
RUL:pipe{id:"pipe",rule:"attrs-pos y relacion: SIGIL:nombre|celda|celda|celda. Campos en ORDEN del contrato (pos). Opcionales solo al final. Strings con | van quoted. relacion requiere minimo 3 celdas (G023_RELATION_CONTRACT_TOO_SHORT).",detail:"Spec 0.1 seccion 13.2/13.5."}
RUL:cuerpo_bloque{id:"cuerpo-bloque",rule:"cuerpo y bloque: SIGIL:nombre{contenido} para una linea, o SIGIL:nombre{\\n...\\n} para multilinea. El cierre } en su propia linea. cuerpo = texto semantico (NFC). bloque = verbatim (sin NFC, preserva bytes). Cuerpo/bloque sin cierre = S007_UNCLOSED_BODY.",detail:"Spec 0.1 seccion 13.3/13.4."}
RUL:focus{id:"focus",rule:"focus es REQUERIDO para attrs, attrs-pos, relacion. El focus debe existir en el contrato. Error G024_FOCUS_REQUIRED si falta, G025_UNKNOWN_FOCUS_FIELD si no esta en fields/pos. El focus es el unico campo que se escribe string quoted en attrs (salvo necesidad gramatical).",detail:"Spec 0.1 seccion 11.5."}
RUL:contrato{id:"contrato",rule:"fields/pos: campo1:tipo1|campo2:tipo2|campo3?. Tipos: any text atom int dec bool null list %enum. ? = opcional. Sin tipo = any. parser usa parse_contract_fields() en parser.py.",detail:"Spec 0.1 seccion 14."}
RUL:scalares{id:"scalares",rule:"Scalares: string \"texto\" con escapes (\\n \\r \\t \\b \\f \\\" \\\\ \\uXXXX), atom (bare, [A-Za-z_][A-Za-z0-9_./:\\-@+%$]*, max 32 chars, sin espacios), integer (0 o -?[1-9][0-9]*), decimal (-?[0-9]+\\.[0-9]+ lexema exacto preservado: 0.75 y 0.750 NO son equivalentes), boolean (true|false), null (null), list ([e1,e2] planas, sin anidamiento). Atom invalido = L010_INVALID_ATOM.",detail:"Spec 0.1 seccion 17 + C14N-0.1 seccion 17."}
RUL:enum{id:"enum",rule:"$0:enum_estado{values:\"a|b|c\"}. Referencia en contrato: %estado. Valores unicos, orden significativo. Sin values o mal formado = G014_INVALID_ENUM. Enum referenciado no declarado = G026_UNKNOWN_ENUM_REFERENCE.",detail:"Spec 0.1 seccion 15."}
RUL:micro{id:"micro",rule:"$0:micro_cur{expand:current}. Atom cur se expande a current en C14N. NO en strings, keys, nombres, sigilos. Micro sin expand = G012_INVALID_MICRO.",detail:"Spec 0.1 seccion 16. C14N-0.1 seccion 19."}
RUL:ns{id:"ns",rule:"$0:namespace_alias{id:X,version:Y,required:B}. Uso: alias::SIGIL:nombre. O namespace en declaracion de sigilo. Namespace no declarado = G011_NAMESPACE_UNDECLARED.",detail:"Spec 0.1 seccion 20."}
RUL:ext{id:"ext",rule:"$0:extension_X{namespace:X,id:Y,version:Z,required:B,desc:T}. Campos obligatorios: namespace, id, version, required. Si required:true y no soportado -> interpretation-incomplete (X002_REQUIRED_EXTENSION_UNSUPPORTED).",detail:"Spec 0.1 seccion 21."}

$3: CORTEX 0.2 SLOTS:CORE
TXT:intro_02{
CORTEX 0.2 extiende 0.1 con un eje de codificacion explicito por slots, ortogonal a los 5 shapes. Un slot es una posicion nombrada y enumerada dentro de la superficie de una Idea. Se activa con encoding:slots en la declaracion del sigilo. 0.2 NO convierte automaticamente attrs 0.1 a slots: la migracion preserva la estructura nominal salvo que el autor invoque explicitamente el migrador.
El marker de slot es el caracter Unicode ※ U+203B (3 bytes UTF-8: E2 80 BB). Es el unico marker normativo. Cuatro caracteres visualmente confundibles estan PROHIBIDOS como marker estructural (L020): U+2022 BULLET, U+00B7 MIDDLE DOT, U+2219 BULLET OPERATOR, U+25CF BLACK CIRCLE. Aparecer como contenido ordinario en strings/cuerpo/bloque es permitido.
}
RUL:marker{id:"marker",rule:"Marker estructural = ※ U+203B, seguido inmediatamente por indice ASCII positivo sin cero inicial y :valor. No usar •, ·, ∙ ni ● (L020_INVALID_SLOT_MARKER).",detail:"slots.py HOMOGLYPHS, detect_homoglyph(). El marker estructural se valida solo en posicion estructural; en strings/cuerpo/bloque es contenido."}
RUL:indice{id:"indice",rule:"slot-index = nonzero-digit *DIGIT (ASCII 0-9 unicamente). Prohibido: indice 0 (L022_SLOT_ZERO_FORBIDDEN), cero inicial (L023_SLOT_LEADING_ZERO), digito Unicode no-ASCII como ٠١٢ (L021_INVALID_SLOT_INDEX), espacio entre marker e indice (L021), espacio entre indice y : (L024_SLOT_SEPARATOR_REQUIRED). Limite implementado: 1_000_000. Excederlo dispara I057_SLOT_INDEX_LIMIT.",detail:"slots.py SLOT_INDEX_MAX = 1_000_000. Spec dice 2^31-1 pero el codigo impone 1M; prevalece el codigo."}
RUL:sigil_map{id:"sigil-map",rule:"$0:sigil-map{marker:\"※\",codepoint:\"U+203B\",base:1,syntax:\"※N:valor\",order:\"ascending\"}. Exactamente 5 attrs con valores canonicos literales. Cualquier desviacion dispara G032_INVALID_SIGIL_MAP. Declarar ANTES de cualquier sigilo con encoding:slots (G041_SIGIL_MAP_ORDER). Una sola vez (G031_DUPLICATE_SIGIL_MAP).",detail:"slotparser.py lineas 306-334. IMPORTANTE: el codigo NO usa la forma del spec $0:sigil-map{KNW:\"1=topic:text|...\"}. El contrato por-sigilo va en el attr slots:\"...\" de la declaracion del sigilo."}
RUL:encoding_slots{id:"encoding-slots",rule:"encoding:slots se declara en la sigilo. Valido solo para attrs, attrs-pos, relacion. PROHIBIDO en cuerpo o bloque (G039_ENCODING_SHAPE_MISMATCH). PROHIBIDO combinar con fields (G040_CONTRACT_SURFACE_CONFLICT). PROHIBIDO combinar con open:true (G038_SLOTS_OPEN_FORBIDDEN). Requiere $0:sigil-map previo (G030_SIGIL_MAP_REQUIRED).",detail:"slotparser.py lineas 396-410."}
RUL:slots_attr{id:"slots-attr",rule:"El contrato por-sigilo va en attr slots:\"1=name:type?|2=name:type|...\" dentro de la declaracion del sigilo. Posiciones ascendentes desde 1 sin huecos (G034_SLOT_CONTRACT_GAP). Posiciones unicas (G035_DUPLICATE_SLOT_POSITION). Nombres unicos (G036_DUPLICATE_SLOT_NAME).",detail:"slotparser.py _parse_symbol_decl(). parse_slot_contract() en slots.py."}
RUL:slot_focus{id:"slot-focus",rule:"focus en sigilo encoding:slots referencia la POSICION (entero) de un slot requerido. Focus inexistente o referenciando slot opcional = G037_SLOT_FOCUS_UNRESOLVED. Focus como nombre textual = G025_UNKNOWN_FOCUS_FIELD.",detail:"slotparser.py lineas 453-470."}
RUL:slot_idea{id:"slot-idea",rule:"Idea slot-encoded: SIGIL:nombre{※1:valor,※2:valor}. SIEMPRE braces. Slots en orden ascendente (I054_SLOT_OUT_OF_ORDER). Sin duplicados (I051_DUPLICATE_SLOT). Sin slots desconocidos al contrato (I052_UNKNOWN_SLOT). Slots requeridos presentes (I053_MISSING_REQUIRED_SLOT). Sin attr nombrado dentro (I055_NAMED_ATTR_IN_SLOT_IDEA). Sin pipe dentro (I056_PIPE_PAYLOAD_IN_SLOT_IDEA).",detail:"slots.py parse_slot_payload()."}
RUL:slot_glossary{id:"slot-glossary",rule:"NO usar ※ en $0 (glosario). $0 es nominal y no se slotifica. Violacion = I050_SLOT_NOT_ALLOWED_IN_GLOSSARY. Excepcion: el valor del attr marker:\"※\" en $0:sigil-map es contenido string, no estructural.",detail:"slotparser.py lineas 280-289."}
RUL:mixed_version{id:"mixed-version",rule:"Un documento declarado cortex:0.1 NO DEBE contener ※ en posicion estructural (tras { o , en braced payload). Violacion = I058_MIXED_SURFACE_VERSION. ※ en strings/cuerpo/bloque de un doc 0.1 es contenido ordinario. Un documento 0.2 puede usar superficies 0.1 (attrs nominales, pipes) en sigilos sin encoding:slots; no es mixed-version.",detail:"slots.py check_mixed_surface_legacy(). Solo dispara en 0.1 declarado."}
RUL:ast_nominal{id:"ast-nominal",rule:"El AST 0.2 es nominal: dos documentos con campos/posiciones equivalentes pero distinto encoding NO son structural-equivalent. Un attrs-0.1 y un attrs-slots-0.2 con el mismo contrato logico producen ASTs distintos y hashes distintos. Idea.payload[0]==\"slots\" vs \"attrs\" distingue.",detail:"Spec 0.2 seccion 9. dispatcher.hash_cortex usa dominio CORTEX-C14N-0.2 vs CORTEX-C14N-0.1."}

$4: HCORTEX:CORE
TXT:hcortex_intro{
HCORTEX es la representacion humana de CORTEX. CORTEX es el formato nativo de la IA; HCORTEX existe para el humano. Existen dos versiones: HCORTEX 0.1 (legacy, 5 schemas: prose, table, list, check, diagram) y HCORTEX 0.2 (slots surface, con hidden glossary block y la invariante no-hidden-copy).
El roundtrip es deterministico: compile(render(ast)) == ast en significado estructural. NO es byte-identico en 0.1 (el render puede reorganizar $0). En 0.2 el roundtrip es byte-exacto en los 5 shapes con y sin encoding:slots.
}
RUL:hcortex_env_01{id:"hcortex-env-01",rule:"HCORTEX 0.1 envelope: <!-- HCORTEX v=0.1 t=canonical --> en linea 1. t=canonical (reversible) o readable (solo visual, no compilable). Sin envelope = H400. BOM = H404. Encoding invalido = H403.",detail:"hcortex-0.1.md seccion 3. hcortex.py compile_hcortex()."}
RUL:hcortex_schemas_01{id:"hcortex-schemas-01",rule:"5 schemas: prose:N (parrafos), table:N (tabla |...|), list:N (- bullet), check:N (- [ ] checkbox), diagram:N (```puml). Cada bloque envuelto en <!-- schema:N --> y <!-- /schema:N -->. Sin anidamiento. Subsecciones §N.M validas con su propio schema. Schema se determina AUTOMATICAMENTE por shape: attrs/attrs-pos/relacion -> table, cuerpo -> prose, bloque -> diagram.",detail:"hcortex-0.1.md seccion 4. hcortex.py _determine_section_schema()."}
RUL:hcortex_glossary_01{id:"hcortex-glossary-01",rule:"$0 NO se renderiza como contenido visible en HCORTEX 0.1. Para roundtrip, incluir bloque <!-- glossary ... --> al inicio con $0:KERNEL, $0:format, y todas las declaraciones de sigilos. El compilador extrae el glosario y reconstruye el AST.",detail:"hcortex-0.1.md seccion 6."}
RUL:hcortex_capa{id:"hcortex-capa",rule:"CAPA se renderiza como <!-- schema:N capa:CAPA --> o en heading ## §N: Titulo [CAPA]. El compilador extrae la capa y la asigna a Section.capa. Al compilar se restaura $N: TITULO:CAPA.",detail:"hcortex-0.1.md seccion 5. slothcortex.py _render_glossary_slots() emite capa_attr."}
RUL:hcortex_env_02{id:"hcortex-env-02",rule:"HCORTEX 0.2 envelope: <!-- HCORTEX v=0.2 t=canonical k=corpus --> en linea 1. v=0.2 obligatorio. Sin envelope = H401_MISSING_ENVELOPE. Version no soportada = H401_UNSUPPORTED_HCORTEX_VERSION. BOM = H490.",detail:"slothcortex.py ENVELOPE_RE. compile_hcortex_slots()."}
RUL:hcortex_glossary_02{id:"hcortex-glossary-02",rule:"HCORTEX 0.2 requiere bloque <!-- glossary --> ... <!-- /glossary --> con el glosario CORTEX 0.2 textual completo (format, sigil-map, sigilos con encoding/slots). Es hidden (HTML comment) pero NO es shadow copy del AST: es el glosario textual necesario para recompilar. Sin glossary block = H403_MISSING_GLOSSARY_BLOCK.",detail:"slothcortex.py GLOSSARY_RE. hcortex-slots.md seccion 3."}
RUL:hcortex_no_hidden{id:"hcortex-no-hidden",rule:"HCORTEX 0.2 RECHAZA payloads ocultos. El compilador detecta regex <!--\\s*(cortex-ast:|base64:|payload-shadow:|shadow:|ast:|internal:) y dispara H481_HIDDEN_COPY. No produce Document. NO usar --embed-ast para roundtrip: genera cortex-ast: de provenance y compile_hcortex_slots lo rechaza.",detail:"slothcortex.py HIDDEN_COPY_RE. hcortex-slots.md seccion 7."}
RUL:hcortex_schema_02{id:"hcortex-schema-02",rule:"HCORTEX 0.2 usa <!-- schema:N --> ... <!-- /schema:N --> por seccion. Mapping shape -> schema: attrs/attrs-pos/relacion (default o slots) -> table con columnas = slot names o field names; cuerpo -> prose; bloque -> fence (``` ... ```). Cada Idea se renderiza como ### SIGIL:nombre seguido de la tabla/prose/fence.",detail:"slothcortex.py _render_idea_slots(). hcortex-slots.md seccion 4-5."}
RUL:hcortex_roundtrip{id:"hcortex-roundtrip",rule:"Roundtrip HCORTEX 0.2 <-> CORTEX 0.2: canonicalize(compile_hcortex_slots(render_hcortex_slots(D))) == canonicalize(D). Byte-exacto en los 5 shapes con y sin encoding:slots. HCORTEX 0.1 roundtrip es estructural, no byte-exacto.",detail:"slothcortex.py run_roundtrip(). hcortex-slots.md seccion 8."}

$5: C14N Y HASH:CORE
TXT:c14n_intro{
C14N es la canonicalizacion: estructura CORTEX valida -> bytes UTF-8 canonicos. El hash se calcula sobre los bytes canonicos con un domain tag que separa versiones. C14N-0.1 y C14N-0.2 comparten reglas de quoting, NFC y orden; difieren en el domain tag y en el manejo de slots.
}
RUL:c14n01{id:"c14n01",rule:"C14N-0.1: NFC fuera de bloque, expansion de microtokens, quoting contract-aware (focus siempre quoted, text no-focus bare si atom valido), sin comentarios/blank-lines/trailing-spaces, un LF final exactamente, sin BOM, sin CR, sin TAB estructural fuera de bloque. Dominio: CORTEX-C14N-0.1.",detail:"c14n.py canonicalize(). C14N-0.1.md seccion 22."}
RUL:c14n02{id:"c14n02",rule:"C14N-0.2: hereda 0.1 + emision de slots en orden ascendente por posicion, microtoken expansion aplicada a slot atoms, bloque verbatim (sin NFC, ※ preservado como contenido), cuerpo NFC (※ preservado como contenido). Dominio: CORTEX-C14N-0.2.",detail:"slotc14n.py canonicalize_slots(). C14N-SLOTS.md seccion 4-7."}
RUL:hash{id:"hash",rule:"hash = SHA-256( b\"CORTEX-C14N-X\" + b\"\\x00\" + canonical_bytes ) donde X es 0.1 o 0.2. Representacion textual: sha256:<64 hex lowercase>. dispatcher.hash_cortex(doc) selecciona dominio por doc.cortex_version. Docs 0.1 y 0.2 con bytes canonicos identicos producen hashes distintos porque el domain tag difiere.",detail:"slotc14n.py hash_slots/hash_legacy. C14N-SLOTS.md seccion 5/13."}
RUL:idempotencia{id:"idempotencia",rule:"Exigir canonicalize(canonicalize(x)) == canonicalize(x). Y para x, y bajo misma version: x ≡structural y si y solo si canonicalize(x) == canonicalize(y). Comparar AST o bytes, no apariencia.",detail:"C14N-0.1.md seccion 2. C14N-SLOTS.md seccion 2."}
RUL:c14n_orden{id:"c14n-orden",rule:"Orden canonico del glosario: (1) $0:KERNEL, (2) $0:format con claves cortex,encoding,language,extras, (3) $0:sigil-map (solo 0.2, si hay sigilos encoding:slots), (4) $0:enum_* por nombre, (5) $0:micro_* por token, (6) $0:namespace_* por alias, (7) $0:extension_* por nombre, (8) $0:otras_meta por nombre, (9) sigilos por namespace+sigil+label. Claves de sigilo 0.1: type,weight,fields,pos,focus,desc,open,namespace,version,extras. Claves de sigilo 0.2: type,encoding,weight,fields,pos,slots,focus,desc,open,namespace,version,extras.",detail:"C14N-0.1.md seccion 8. C14N-SLOTS.md seccion 9-11."}

$6: MIGRACION 0.1 -> 0.2:FLOW
GEN:migrate{
La migracion 0.1 -> 0.2 es una operacion transaccional de 5 fases. Ejecutar explicitamente:

Paso 1: migrate_inspect(source_path). Lee $0:format, valida cortex=0.1, lista sigilos y sus contratos. Si el doc ya es 0.2, retorna status:skip.

Paso 2: migrate_plan(source_path, to_version='0.2', out_path=plan.json). Captura source_sha256 (SHA-256 del archivo fuente). Si source cambia entre plan y apply, aborta.

Paso 3: migrate_apply(plan_path, out_path). Verifica source_sha256 (P28). Construye Document 0.2 preservando TODO el metadata de format (P25: language, type extras). Escribe temp + fsync + rename atomico (sin estado parcial). Produce salida completa o ninguna. Crea backup source.bak. Si verify falla, restaura source.

Paso 4: migrate_verify(source_path, migrated_path). Parsea ambos, compara AST profundo (NO solo addresses): sections, ideas, payloads, scalars, glosario. Pasa solo si idea_equivalence es pass.

Paso 5: migrate_rollback(plan_path). Borra backup y restaura source desde .bak. NO toca el output; el caller puede borrarlo.

Politica de perdida: 0.1 -> 0.2 NO es lossy. El migrador convierte attrs/attrs-pos/relacion a slots automaticamente (sigilos sin open:true), preservando cuerpos y bloques. Si el autor no quiere slots, puede editar el output y quitar encoding:slots manualmente.
}
HDL:migrate_inspect|migrate inspect <file>|current|JSON con sigilos y contratos
HDL:migrate_plan|migrate plan <file> [plan.json]|current|Plan con source_sha256
HDL:migrate_apply|migrate apply <plan.json> [out.cortex]|current|Escribe 0.2 atomico
HDL:migrate_verify|migrate verify <source> <migrated>|current|Verifica equivalencia AST
HDL:migrate_rollback|migrate rollback <plan.json>|current|Restaura source desde .bak

$7: API PYTHON:DATA
API:parse_cortex{name:"parse_cortex",signature:"parse_cortex(source: str) -> Document",version:python,status:current,notes:"Entrada dual recomendada. Lee $0:format{cortex:X} y enruta a parse_cortex_01 (0.1) o parse_slots (0.2). BOM -> U001_BOM_FORBIDDEN."}
API:parse_cortex_01{name:"parse_cortex_01",signature:"parse_cortex_01(source: str) -> Document",version:python,status:current,notes:"Parser 0.1 explicito. Importado como parse_cortex desde parser.py."}
API:parse_slots{name:"parse_slots",signature:"parse_slots(source: str) -> Document",version:python,status:current,notes:"Parser 0.2 explicito. slotparser.py."}
API:canonicalize{name:"canonicalize",signature:"canonicalize(doc: Document) -> str",version:python,status:current,notes:"Dispatcher. doc.cortex_version selecciona canonicalize_01 o canonicalize_slots."}
API:canonicalize_01{name:"canonicalize_01",signature:"canonicalize_01(doc) -> str",version:python,status:current,notes:"C14N-0.1 canonico. Importado desde c14n.py."}
API:canonicalize_slots{name:"canonicalize_slots",signature:"canonicalize_slots(doc) -> str",version:python,status:current,notes:"C14N-0.2 canonico. slotc14n.py."}
API:hash_cortex{name:"hash_cortex",signature:"hash_cortex(doc) -> str",version:python,status:current,notes:"Dispatcher. Devuelve sha256:<64hex>. Dominio CORTEX-C14N-0.1 o CORTEX-C14N-0.2."}
API:hash_legacy{name:"hash_legacy",signature:"hash_legacy(doc) -> str",version:python,status:current,notes:"Hash 0.1 explicito. slotc14n.py."}
API:hash_slots{name:"hash_slots",signature:"hash_slots(doc) -> str",version:python,status:current,notes:"Hash 0.2 explicito. slotc14n.py."}
API:render_hcortex{name:"render_hcortex",signature:"render_hcortex(doc) -> str",version:python,status:current,notes:"Renderer HCORTEX 0.1 (legacy). hcortex.py."}
API:compile_hcortex{name:"compile_hcortex",signature:"compile_hcortex(text) -> (Document, [HDiagnostic])",version:python,status:current,notes:"Compilador HCORTEX 0.1. hcortex.py."}
API:render_hcortex_slots{name:"render_hcortex_slots",signature:"render_hcortex_slots(doc, embed_ast=False) -> str",version:python,status:current,notes:"Renderer HCORTEX 0.2. embed_ast=True inyecta <!-- cortex-ast: HASH --> para provenance (NO usar para roundtrip). slothcortex.py."}
API:compile_hcortex_slots{name:"compile_hcortex_slots",signature:"compile_hcortex_slots(text) -> (Document|None, [diags])",version:python,status:current,notes:"Compilador HCORTEX 0.2. Rechaza H481_HIDDEN_COPY, H401_MISSING_ENVELOPE, H403_MISSING_GLOSSARY_BLOCK, H490 BOM. slothcortex.py."}
API:run_roundtrip{name:"run_roundtrip",signature:"run_roundtrip(valid_dir) -> dict",version:python,status:current,notes:"Valida roundtrip byte-exacto en un directorio de .cortex 0.2."}
API:migrate_inspect_api{name:"migrate_inspect",signature:"migrate_inspect(source_path) -> dict",version:python,status:current,notes:"slotmigrate.py."}
API:migrate_plan_api{name:"migrate_plan",signature:"migrate_plan(source_path, to_version='0.2', out_path=None) -> dict",version:python,status:current,notes:"Captura source_sha256 y escribe plan JSON."}
API:migrate_apply_api{name:"migrate_apply",signature:"migrate_apply(plan_path, out_path=None) -> dict",version:python,status:current,notes:"Atomic write + verify. Restaura source si falla."}
API:migrate_verify_api{name:"migrate_verify",signature:"migrate_verify(source_path, migrated_path) -> dict",version:python,status:current,notes:"Equivalencia AST profunda."}
API:migrate_rollback_api{name:"migrate_rollback",signature:"migrate_rollback(plan_path) -> dict",version:python,status:current,notes:"Restaura source desde .bak."}

$8: CLI:DATA
HDL:parse|parse <file>|current|AST JSON por dispatcher (0.1 o 0.2)
HDL:validate|validate <file>|current|Valida CORTEX 0.1/0.2; exit 0 si valido
HDL:canonicalize|canonicalize <file>|current|Bytes canonicos por dispatcher
HDL:hash|hash <file>|current|Hash canonico sha256:...
HDL:harness|harness [C14N_DIR] [HCORTEX_DIR]|current|Legacy F3/F4 harness (0.1)
HDL:conformance|conformance [MANIFEST_DIR]|current|Slots conformance harness (0.2)
HDL:tohcortex|to-hcortex [--embed-ast] <file>|current|Render HCORTEX 0.2 desde CORTEX 0.2
HDL:fromhcortex|from-hcortex <file>|current|Compila HCORTEX 0.2 a CORTEX 0.2 canonico
HDL:migrate|migrate <cmd> <file> [args]|current|inspect|plan|apply|verify|rollback
RUL:embed_warning{id:"embed-warning",rule:"NO usar --embed-ast para roundtrip.",detail:"Genera <!-- cortex-ast: HASH --> de provenance. compile_hcortex_slots lo rechaza con H481_HIDDEN_COPY. Solo para verificacion unidireccional (no roundtrip)."}

$9: CATALOGO DE ERRORES:DATA
TXT:errores_intro{
Catalogo verificable contra el codigo. Las familias son: L (lexical), S (sintaxis), G (glosario), I (Idea), X (extension), U (Unicode), H (HCORTEX). 0.1 hereda todos los codigos L001-L010, S001-S007, G001-G028, I001-I016, X001-X002, U001-U002. 0.2 anade L020-L025, G030-G041, I050-I058, H401-H406, H481. Los nombres exactos abajo provienen del codigo (slotparser.py, slots.py, slothcortex.py), no del spec prose; donde difieren, prevalece el codigo.
}
RUL:err_L_01{id:"err-L-01",rule:"L001_INVALID_SYMBOL, L002_INVALID_NAME, L003_INVALID_KEY, L005_INVALID_STRING, L006_EMPTY_VALUE, L007_INVALID_LIST, L008_NESTED_LIST, L009_INVALID_NUMBER, L010_INVALID_ATOM.",detail:"parser.py / scalars.py. Spec errors.md seccion 4.1."}
RUL:err_S_01{id:"err-S-01",rule:"S001_EMPTY_DOCUMENT, S002_DUPLICATE_SECTION, S003_INVALID_IDEA_HEAD, S004_MISSING_PAYLOAD, S005_CONTENT_OUTSIDE_SECTION, S006_INVALID_ATTRS, S007_UNCLOSED_BODY (alias 0.2 de I014_UNCLOSED_BODY).",detail:"parser.py / slotparser.py."}
RUL:err_G_01{id:"err-G-01",rule:"G001_GLOSSARY_MISSING_OR_NOT_FIRST, G002_GLOSSARY_REOPENED, G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS, G006_DUPLICATE_FORMAT, G007_UNSUPPORTED_VERSION, G008_INVALID_CONTRACT, G010_FORMAT_REQUIRED, G011_ENCODING_REQUIRED, G012_INVALID_MICRO, G014_INVALID_ENUM, G015_DUPLICATE_SYMBOL, G016_SYMBOL_TYPE_REQUIRED, G017_UNKNOWN_SHAPE, G018_SYMBOL_WEIGHT_REQUIRED, G019_INVALID_WEIGHT, G020_SYMBOL_DESCRIPTION_REQUIRED, G021_ATTRS_CONTRACT_REQUIRED, G022_POSITIONAL_CONTRACT_REQUIRED, G023_RELATION_CONTRACT_TOO_SHORT, G024_FOCUS_REQUIRED, G025_UNKNOWN_FOCUS_FIELD, G026_UNKNOWN_ENUM_REFERENCE, G027_UNKNOWN_FIELD_TYPE.",detail:"parser.py."}
RUL:err_I_01{id:"err-I-01",rule:"I001_UNDECLARED_SYMBOL, I002_DUPLICATE_IDEA_ADDRESS, I003_ATTRS_MUST_BE_ONE_LINE, I004_SHAPE_DELIMITER_MISMATCH, I005_UNKNOWN_FIELD, I006_DUPLICATE_FIELD, I006_DUPLICATE_IDEA_ADDRESS, I007_FIELD_ORDER, I008_REQUIRED_FIELD_MISSING, I009_FIELD_TYPE_MISMATCH, I010_ENUM_VIOLATION, I011_PIPE_IDEA_MUST_BE_ONE_LINE, I012_POSITIONAL_ARITY (0.1) | I012_TYPE_MISMATCH (0.2 alias), I013_RELATION_ARITY, I014_UNCLOSED_BODY, I015_FOCUS_VALUE_MISSING, I016_EMPTY_FOCUS.",detail:"parser.py / slotparser.py."}
RUL:err_XU_01{id:"err-XU-01",rule:"X001_INVALID_EXTENSION_DECLARATION, X002_REQUIRED_EXTENSION_UNSUPPORTED, U001_BOM_FORBIDDEN, U002_CONTROL_CHARACTER.",detail:"parser.py."}
RUL:err_L_02{id:"err-L-02",rule:"L020_INVALID_SLOT_MARKER (homoglyph), L021_INVALID_SLOT_INDEX (digito Unicode no-ASCII o espacio marker-indice), L022_SLOT_ZERO_FORBIDDEN, L023_SLOT_LEADING_ZERO, L024_SLOT_SEPARATOR_REQUIRED (espacio entre indice y :).",detail:"slots.py. Nombres exactos del codigo."}
RUL:err_G_02{id:"err-G-02",rule:"G030_SIGIL_MAP_REQUIRED (no _MISSING), G031_DUPLICATE_SIGIL_MAP, G032_INVALID_SIGIL_MAP (no _INVALID_VALUES; valores deben ser exactamente marker=※, codepoint=U+203B, base=1, syntax=※N:valor, order=ascending), G033_SLOT_CONTRACT_REQUIRED (no _SLOTS_CONTRACT_MISSING), G034_SLOT_CONTRACT_GAP (no _SLOT_POSITION_GAP), G035_DUPLICATE_SLOT_POSITION, G036_DUPLICATE_SLOT_NAME, G037_SLOT_FOCUS_UNRESOLVED (no _UNKNOWN_FOCUS_SLOT), G038_SLOTS_OPEN_FORBIDDEN (no _OPEN_SLOTS_CONTRACT), G039_ENCODING_SHAPE_MISMATCH (no _SLOTS_ENCODING_ON_BODY_SHAPE), G040_CONTRACT_SURFACE_CONFLICT, G041_SIGIL_MAP_ORDER.",detail:"slotparser.py lineas 280-470. Nombres exactos del codigo."}
RUL:err_I_02{id:"err-I-02",rule:"I050_SLOT_NOT_ALLOWED_IN_GLOSSARY (no _SLOT_IN_GLOSSARY), I051_DUPLICATE_SLOT, I052_UNKNOWN_SLOT, I053_MISSING_REQUIRED_SLOT (no _REQUIRED_SLOT_MISSING), I054_SLOT_OUT_OF_ORDER, I055_NAMED_ATTR_IN_SLOT_IDEA, I056_PIPE_PAYLOAD_IN_SLOT_IDEA (no _PIPE_IN_SLOT_IDEA), I057_SLOT_INDEX_LIMIT (no _OUT_OF_RANGE; > 1_000_000), I058_MIXED_SURFACE_VERSION.",detail:"slotparser.py / slots.py. Nombres exactos del codigo."}
RUL:err_H_02{id:"err-H-02",rule:"HCORTEX 0.2: H401_MISSING_ENVELOPE, H401_UNSUPPORTED_HCORTEX_VERSION (version != 0.2), H403_MISSING_GLOSSARY_BLOCK, H481_HIDDEN_COPY (regex cortex-ast:|base64:|payload-shadow:|shadow:|ast:|internal:), H490 (BOM). HCORTEX 0.1: H400-H404 documento, H410-H417 glosario, H420-H436 secciones/Ideas, H440-H472 shape, H480-H490 canonicalidad.",detail:"slothcortex.py. hcortex-errors-0.1.md."}
RUL:err_recuperacion{id:"err-recuperacion",rule:"Mapeo directo error -> accion correctiva: I001 declarar sigilo en $0; G024 agregar focus; G021/G022 agregar fields/pos; G025 corregir focus o contrato; I008 agregar campo requerido; L010 usar comillas dobles; G030 declarar $0:sigil-map antes del sigilo encoding:slots; G032 usar valores canonicos exactos del sigil-map; G039 quitar encoding:slots de cuerpo/bloque; G040 elegir fields o encoding:slots (no ambos); G041 mover $0:sigil-map antes del sigilo; I050 quitar ※ del glosario; I053 agregar slot requerido; I054 reordenar slots ascendentes; I058 cambiar $0:format a 0.2 o quitar ※ estructural; H481 quitar cortex-ast:/base64:/shadow:.",detail:"Mapeo verificado contra el codigo."}

$10: GENERACION:FLOW
GEN:cortex_01{
Para generar CORTEX 0.1 valido:

Paso 1: $0:KERNEL en linea 1.
Paso 2: $0:format{cortex:0.1,encoding:UTF-8,language:XX} en linea 2.
Paso 3: Declare TODOS los sigilos que usara. Por cada uno:
  SIGIL:nombre{type:SHAPE,weight:B|M|H,focus:CAMPO,fields:CONTRATO|pos:CONTRATO,desc:TEXTO}
  - type: attrs|attrs-pos|cuerpo|bloque|relacion
  - weight: B (base), M (material), H (alta)
  - focus: obligatorio para attrs/attrs-pos/relacion (campo del contrato)
  - fields: solo attrs (formato campo:tipo|campo:tipo|...)
  - pos: solo attrs-pos/relacion (mismo formato, minimo 3 para relacion)
  - desc: descripcion humana
  - open:true opcional para attrs (permite extras)
Paso 4: Use secciones $1:, $2:, etc. Opcional: $N: TITULO:CAPA.
Paso 5: Las Ideas usan el shape declarado:
  - attrs: SIGIL:nombre{campo:"focus",campo:atom}
  - attrs-pos/relacion: SIGIL:nombre|celda|celda|
  - cuerpo/bloque: SIGIL:nombre{texto} o SIGIL:nombre{\n...\n}
Paso 6: TODO sigilo usado fuera de $0 DEBE estar declarado en $0. Si falta, I001.
Paso 7: El focus del sigilo se escribe entre comillas dobles. Demas campos como atoms si son valores simples.
Paso 8: Errores comunes: I001, G024, G021/G022, G025, I008, L010.
}
GEN:cortex_02{
Para generar CORTEX 0.2 con slots:

Paso 1: $0:KERNEL en linea 1.
Paso 2: $0:format{cortex:0.2,encoding:UTF-8,language:es} en linea 2.
Paso 3: $0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"} en linea 3. EXACTAMENTE estos 5 attrs con estos valores literales. Cualquier desviacion = G032.
Paso 4: Declare enums, micros, namespaces, extensions opcionales.
Paso 5: Declare sigilos. Para sigilos con slots:
  SIGIL:nombre{type:attrs,encoding:slots,weight:H,slots:"1=name:type?|2=name:type",focus:1,schema:table,desc:"...",open:false}
  - type: attrs|attrs-pos|relacion (NO cuerpo ni bloque: G039)
  - encoding:slots obligatorio
  - slots: contrato por-sigilo como string quoted, posiciones ascendentes desde 1 sin huecos
  - focus: entero (posicion del slot requerido que es el focus)
  - open:false obligatorio (G038 si open:true)
  - schema: table (recomendado para HCORTEX)
Paso 6: Use secciones $1:, $2:, etc.
Paso 7: Las Ideas slot-encoded usan braces:
  SIGIL:nombre{※1:"valor",※2:atom,※3:42}
  - Slots en orden ascendente (I054 si no)
  - Sin duplicados (I051)
  - Slots requeridos presentes (I053)
  - Sin attr nombrado (I055)
  - Sin pipe (I056)
Paso 8: Un documento 0.2 puede mezclar sigilos con encoding:slots y sigilos sin encoding:slots (attrs nominales, pipes). No es mixed-version.
Paso 9: ※ en strings, cuerpo y bloque es contenido ordinario.
Paso 10: NO uses ※ en $0 (glosario). Solo el attr marker:"※" del sigil-map es excepcion (es string content).
}
GEN:hcortex_02{
Para generar HCORTEX 0.2 valido:

Paso 1: <!-- HCORTEX v=0.2 t=canonical k=corpus --> en linea 1.
Paso 2: <!-- glossary --> ... <!-- /glossary --> con el glosario CORTEX 0.2 completo (format, sigil-map, sigilos con encoding/slots).
Paso 3: Por cada seccion:
  ## §N: Titulo
  <!-- schema:N capa:CAPA -->
  ### SIGIL:nombre
  | name1 | name2 |
  |---|---|
  | valor1 | valor2 |
  <!-- /schema:N -->
Paso 4: Cuerpo se renderiza como texto despues de ### SIGIL:nombre (prose).
Paso 5: Bloque se renderiza como fence ``` ... ``` despues de ### SIGIL:nombre.
Paso 6: NUNCA incluyas cortex-ast:, base64:, shadow:, ast:, internal: en el HCORTEX. H481.
Paso 7: NUNCA uses --embed-ast si necesitas roundtrip.
Paso 8: Para roundtrip, valida: canonicalize(compile_hcortex_slots(render_hcortex_slots(doc))) == canonicalize(doc).
}

$11: VALIDACION:DATA
TST:probes{id:"P01-P29",command:"python scripts/ccx_probes.py",result:pass,scope:"CORTEX 0.1/0.2, slots, HCORTEX 0.1/0.2, migration, mixed-version I058"}
TST:node{id:"node-tests",command:"node --test codec-cortex-node/test/*.test.js",result:pass,scope:"Paridad Node.js con Python, slots 0.2"}
TST:pytest{id:"pytest",command:"python -m pytest -q",result:diagnostic,scope:"Collection path requiere reparacion en experiments/gate-f3/rust/test_c14n.py; no bloquea conformidad"}
TST:conformance{id:"conformance",command:"python -m codec_cortex conformance",result:pass,scope:"Corpus slots 0.2 con manifest.json"}
TST:roundtrip{id:"roundtrip",command:"python -m codec_cortex.slothcortex (run_roundtrip)",result:pass,scope:"Roundtrip byte-exacto HCORTEX 0.2 <-> CORTEX 0.2 en 5 shapes"}
TXT:evidence{
Revision verificada: P01-P29 = 29/29, Node = 22/22, conformance slots 0.2 = pass, roundtrip HCORTEX 0.2 = pass. pytest global falla durante collection por una ruta de corpus inconsistente en experiments/gate-f3/rust/test_c14n.py; no afecta la conformidad nuclear.
Gate F3/F4 distingue INTERNAL_PASS de certificacion independiente. No declarar Gate listo, Standard ratificado o conformidad completa sin evidencia independiente. La capacidad implementada (Python, Rust, Go, Node, Bash) tiene C14N 40/40 en cada lenguaje.
}

$12: EJEMPLOS:KNOW
EX:minimo_01{
$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es}
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text",focus:content,desc:"Conocimiento verificado"}
$1: KNOWLEDGE
KNW:cortex{topic:"CORTEX",content:"Codec ideatico reversible para LLM."}
KNW:parser{topic:"Parser",content:"codec_cortex.parser.parse_cortex()."}
}
EX:minimo_02_slots{
$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
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
KNW:knowledge{type:attrs,encoding:slots,weight:H,slots:"1=topic:text|2=content:text?",focus:1,schema:table,desc:"Invalido",open:false}
$1: KNOW
KNW:codec{※1:"CORTEX",※2:"Codec"}

RESULTADO: I058_MIXED_SURFACE_VERSION. Un doc 0.1 no puede tener ※ estructural. Solucion: cambiar $0:format a cortex:0.2 y agregar $0:sigil-map.
}
EX:migration_cmd{
# Inspect
python -m codec_cortex migrate inspect old_01.cortex

# Plan
python -m codec_cortex migrate plan old_01.cortex plan.json

# Apply (atomic, crea old_01.cortex.bak)
python -m codec_cortex migrate apply plan.json new_02.cortex

# Verify (equivalencia AST profunda)
python -m codec_cortex migrate verify old_01.cortex new_02.cortex

# Rollback si necesario
python -m codec_cortex migrate rollback plan.json
}

$13: REFERENCIAS:KNOW
EX:paths{
Specs:
  CORTEX 0.1: docs/standard/CORTEX-SPEC-0.1.md
  CORTEX 0.2: docs/standard/CORTEX-SPEC-SLOTS.md
  HCORTEX 0.1: docs/standard/hcortex-0.1.md
  HCORTEX 0.2: docs/standard/hcortex-slots.md
  C14N 0.1: docs/standard/C14N-0.1.md
  C14N 0.2: docs/standard/C14N-SLOTS.md
  Errores 0.1: docs/standard/errors.md
  Errores 0.2: docs/standard/errors-slots.md
  HCORTEX errores 0.1: docs/standard/hcortex-errors-0.1.md

API Python: codec_cortex/
  dispatcher.py: parse_cortex, canonicalize, hash_cortex
  parser.py: parse_cortex_01, Document, Section, Idea, SymbolDef
  slotparser.py: parse_slots, SigilMapDecl, GlossarySlots
  slots.py: SLOT_MARKER, HOMOGLYPHS, SLOT_INDEX_MAX, FieldValue
  c14n.py: canonicalize_01
  slotc14n.py: canonicalize_slots, hash_slots, hash_legacy
  hcortex.py: render_hcortex, compile_hcortex
  slothcortex.py: render_hcortex_slots, compile_hcortex_slots, run_roundtrip
  slotmigrate.py: migrate_inspect, migrate_plan, migrate_apply, migrate_verify, migrate_rollback
  __main__.py: CLI entry point

Implementaciones hermanas (C14N 40/40 cada una):
  Rust: codec-cortex-rs/
  Go: codec-cortex-go/
  Node.js: codec-cortex-node/
  Bash: codec-cortex-bash/

Corpus conformance:
  Slots 0.2 validos: conformance/slots/valid/V001-V030.cortex
  Slots 0.2 invalidos: conformance/slots/invalid/
  HCORTEX 0.2: conformance/slots/hcortex/
  Manifest: conformance/slots/manifest.json

Probes:
  scripts/ccx_probes.py (P01-P29)
}
