$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es}
RUL:rule{type:attrs,weight:H,fields:"id:text|rule:text|detail:text",focus:rule,desc:"Regla normativa del formato CORTEX. id es clave unica, rule enuncia la regla, detail referencia a la spec."}
TXT:text{type:cuerpo,weight:M,desc:"Texto explicativo en espanol. Cuerpo libre, el foco es el texto completo."}
GEN:generate{type:cuerpo,weight:H,desc:"Instruccion directa de generacion para la IA. Siga estos pasos al producir CORTEX."}
EX:example{type:bloque,weight:M,desc:"Ejemplo de bloque verbatim con un documento CORTEX o HCORTEX completo."}
HDL:handler{type:attrs-pos,weight:M,pos:"operation:text|status:atom|scope:text",focus:operation,desc:"Demo de sigilo con shape attrs-pos (sintaxis pipe)."}
$1: CORTEX:CORE
TXT:meta{
CORTEX 0.1 (draft) es un codec ideatico de maquina para modelos de lenguaje.
La IA lee CORTEX directamente. HCORTEX es la proyeccion humana con esquemas visuales.
Este skill es una guia completa para producir CORTEX valido. La implementacion de referencia es codec-cortex (Python).
}
RUL:doc{id:"doc",rule:"Un documento CORTEX tiene: (1) $0 como primera seccion unica, (2) $0:format{cortex:0.1,encoding:UTF-8} en linea 2, (3) declaracion de cada sigilo usado en $0, (4) secciones $1,$2,... con Ideas.",detail:"Spec $7. $0 no reaparece. Cada sigilo usado FUERA de $0 debe declararse EN $0 (I001 si falta)."}
RUL:formato{id:"formato",rule:"$0:format debe tener cortex:0.1 y encoding:UTF-8. Atributos extra se preservan. Solo una declaracion format por documento. Sin $0:format el parser lanza G010_FORMAT_REQUIRED. Version distinta de 0.1 lanza G007.",detail:"Spec $9."}
RUL:seccion{id:"seccion",rule:"Secciones: $N: TITULO o $N: TITULO:CAPA. N entero positivo. Subsecciones $N.M validas. CAPA opcional: KERNEL|CORE|KNOW|DATA|FLOW|CACHE. El parser asigna DATA por defecto a N>=2 sin capa.",detail:"Spec $18. CAPA es metadata (Section.capa). Sin semantica de runtime, eviccion o memoria."}
RUL:glosario{id:"glosario",rule:"$0 contiene: (a) $0:KERNEL como encabezado, (b) $0:format{...}, (c) meta-declaraciones opcionales ($0:enum_X, $0:micro_X, $0:namespace_X, $0:extension_X), (d) declaraciones de sigilo SIGIL:nombre{...}. TODAS usan attrs {k:v} en UNA linea fisica.",detail:"Glossary $3. No hay separacion formal entre meta y sigilos en $0."}
RUL:declaracion{id:"declaracion",rule:"Declaracion de sigilo: SIGIL:nombre{type:SHAPE,weight:B|M|H,focus:CAMPO,desc:TEXTO}. Para attrs: fields:CAMPO:TIPO|...| obligatorio. Para attrs-pos/relacion: pos:CAMPO:TIPO|...| obligatorio. Para cuerpo/bloque: focus opcional ($body por defecto).",detail:"Spec $11. _build_symbol_def() en parser.py valida G016-G025."}
RUL:shapes{id:"shapes",rule:"5 shapes: attrs = {k:v,k:v} una linea; attrs-pos = |celda|celda| una linea; cuerpo = {texto} corto o {\\n...\\n} multilinea; bloque = {\\n...\\n} verbatim; relacion = |source|pred|target| una linea. Delimitador incorrecto = I004.",detail:"Spec $13."}
RUL:attrs{id:"attrs",rule:"attrs: SIGIL:nombre{clave:valor,clave:valor}. Campos en ORDEN del contrato (fields). focus SIEMPRE string quoted. Texto no-focus: quoted si tiene espacios o delimitadores, bare si es atom valido. open:true permite campos extras.",detail:"Spec $13.1 + C14N $10."}
RUL:pipe{id:"pipe",rule:"attrs-pos y relacion: SIGIL:nombre|celda|celda|celda. Campos en ORDEN del contrato (pos). Opcionales solo al final. Strings con | van quoted.",detail:"Spec $13.2/13.5."}
RUL:cuerpo_bloque{id:"cuerpo-bloque",rule:"cuerpo y bloque: SIGIL:nombre{contenido} para una linea, o SIGIL:nombre{\\n...\\n} para multilinea. El cierre } en su propia linea. cuerpo = texto semantico (NFC). bloque = verbatim (sin NFC).",detail:"Spec $13.3/13.4."}
RUL:focus{id:"focus",rule:"focus es REQUERIDO para attrs, attrs-pos, relacion. El focus debe existir en el contrato. Error G024 si falta, G025 si no esta en fields/pos. El focus es el unico campo que se escribe string quoted en attrs (salvo necesidad gramatical).",detail:"Spec $11.5."}
RUL:contrato{id:"contrato",rule:"fields/pos: campo1:tipo1|campo2:tipo2|campo3?. Tipos: any text atom int dec bool null list %enum. ? = opcional. Sin tipo = any. El parser usa parse_contract_fields() en parser.py.",detail:"Spec $14."}
RUL:scalares{id:"scalares",rule:"Scalares: string \"texto\" con escapes (\\n \\r \\t \\b \\f \\\" \\\\ \\uXXXX), atom (bare, [A-Za-z_][A-Za-z0-9_./:\\-@+%$]*, max 32 chars, sin espacios), integer (0 o -?[1-9][0-9]*), decimal (-?[0-9]+\\.[0-9]+ lexema exacto preservado: 0.75 y 0.750 NO son equivalentes), boolean (true|false), null (null), list ([e1,e2] planas). Atom invalido = L010.",detail:"Spec $17 + C14N $17."}
RUL:enum{id:"enum",rule:"$0:enum_estado{values:\"a|b|c\"}. Referencia en contrato: %estado. Valores unicos, orden significativo. Sin values o mal formado = G014.",detail:"Spec $15."}
RUL:micro{id:"micro",rule:"$0:micro_cur{expand:current}. Atom cur se expande a current en C14N. NO en strings, keys, nombres, sigilos. Micro sin expand = G012.",detail:"Spec $16. C14N $19."}
RUL:ns{id:"ns",rule:"$0:namespace_alias{id:X,version:Y,required:B}. Uso: alias::SIGIL:nombre. O namespace en declaracion de sigilo.",detail:"Spec $20."}
RUL:ext{id:"ext",rule:"$0:extension_X{namespace:X,id:Y,version:Z,required:B,desc:T}. Campos obligatorios: namespace, id, version, required. Si required:true y no soportado -> interpretation-incomplete.",detail:"Spec $21."}
RUL:diags{id:"diags",rule:"Codigos: L (lexical, L001-L010), S (sintaxis, S001-S006), G (glosario, G001-G028), I (Idea, I001-I016), X (extension, X001-X002), U (Unicode, U001-U002). Catalogo en spec/errors.md.",detail:"Spec $27."}
RUL:c14n{id:"c14n",rule:"C14N-0.1: NFC fuera de bloque, expansion de microtokens, quoting contract-aware (I7), sin comentarios/blank-lines/trailing-spaces, un LF final. Hash: SHA-256(\"CORTEX-C14N-0.1\" || 0x00 || bytes). Idempotente. Gate F3 bloqueado.",detail:"C14N-0.1.md $22. Solo Python con internal-c14n-evidence."}
RUL:c14n_orden{id:"c14n-orden",rule:"Orden canonico en $0: (1) $0:KERNEL, (2) $0:format con claves cortex,encoding,language,extras, (3) $0:enum_* por nombre, (4) $0:micro_* por token, (5) $0:namespace_* por alias, (6) $0:extension_* por nombre, (7) $0:otras_meta por nombre, (8) sigilos por namespace+sigil+label. Claves de sigilo: type,weight,fields,pos,focus,desc,open,namespace,version,extras.",detail:"C14N-0.1.md $8. El parser no exige este orden; solo C14N y el hash."}
RUL:recuperacion{id:"recuperacion",rule:"Si el parser lanza I001 (sigilo no declarado) -> declare el sigilo en $0 con type,weight,focus,fields/pos,desc. Si lanza G024 (focus faltante) -> agregue focus al sigilo. Si lanza G021/G022 (contrato faltante) -> agregue fields o pos. Si lanza I008 (campo requerido faltante) -> incluya el campo en la Idea. Si lanza L010 (atom invalido) -> use comillas dobles alrededor del valor.",detail:"Mapeo directo de error del parser a accion correctiva."}
HDL:verify|validar documento|current|skill
GEN:cortex{
Para generar CORTEX valido:

Paso 1: $0:KERNEL en linea 1.
Paso 2: $0:format{cortex:0.1,encoding:UTF-8,language:XX} en linea 2.
Paso 3: Declare TODOS los sigilos que usara. Por cada uno:
  SIGIL:nombre{type:SHAPE,weight:B|M|H,focus:CAMPO,fields:CONTRATO,desc:TEXTO}
  - type: attrs|attrs-pos|cuerpo|bloque|relacion
  - weight: B (base), M (material), H (alta)
  - focus: campo principal del sigilo (obligatorio para attrs/attrs-pos/relacion)
  - fields: solo para attrs (formato campo:tipo|campo:tipo|...)
  - pos: solo para attrs-pos/relacion (mismo formato)
  - desc: descripcion humana
Paso 4: Use secciones $1:, $2:, etc. Opcional: $N: TITULO:CAPA.
Paso 5: Las Ideas usan el shape declarado:
  - attrs: SIGIL:nombre{campo:"focus",campo:atom}
  - attrs-pos/relacion: SIGIL:nombre|celda|celda|
  - cuerpo/bloque: SIGIL:nombre{texto}
Paso 6: TODO sigilo usado fuera de $0 DEBE estar declarado en $0. Si falta, el parser lanza I001.
Paso 7: El focus del sigilo se escribe entre comillas dobles. Demas campos como atoms (sin comillas) si son valores simples.
Paso 8: Errores comunes al generar: I001 (sigilo no declarado), G024 (focus faltante), G021/G022 (contrato fields/pos faltante), G025 (focus no existe en contrato), I008 (campo requerido faltante), L010 (atom invalido).
}
EX:minimo{
$0
$0:format{cortex:0.1,encoding:UTF-8,language:es}
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text",focus:content,desc:"Conocimiento verificado"}
$1: KNOWLEDGE
KNW:cortex{topic:"CORTEX",content:"Codec ideatico reversible para LLM."}
KNW:parser{topic:"Parser",content:"codec_cortex.parser.parse_cortex()."}
}
$2: HCORTEX:CORE
TXT:hcortex{
HCORTEX es la representacion humana de CORTEX con esquemas visuales.
Cada seccion se envuelve en apertura schema:N y cierre /schema:N.
$0 NO se renderiza como contenido visible. Se conserva en bloque glossary para roundtrip.
}
RUL:hcortex_h{id:"hcortex-h",rule:"Cabecera: <!-- HCORTEX v=0.1 t=canonical -->. v=0.1, t=canonical (reversible) o readable (solo visual, no compilable). Sin cabecera el compilador lanza H400.",detail:"hcortex-0.1.md $3."}
RUL:hcortex_s{id:"hcortex-s",rule:"5 schemas: prose:N (parrafos), table:N (tabla |...|...|), list:N (- bullet), check:N (- [ ] checkbox), diagram:N (```puml). Cada bloque envuelto en schema:N y /schema:N.",detail:"hcortex-0.1.md $4."}
RUL:hcortex_m{id:"hcortex-m",rule:"El schema se determina AUTOMATICAMENTE por shape de las Ideas: attrs/attrs-pos/relacion -> table, cuerpo -> prose, bloque -> diagram. Si alguna Idea usa sigilo con open:true -> prose forzado. Shapes mixtos en misma seccion -> prose.",detail:"_determine_section_schema() en hcortex.py. No se declara manualmente."}
RUL:hcortex_g{id:"hcortex-g",rule:"$0 se serializa en bloque <!-- glossary\\n...\\n--> al inicio del HCORTEX. No visible en lectura humana normal. Incluye format, sigilos, enums, micros, etc. Obligatorio para recompilar a CORTEX.",detail:"hcortex-0.1.md $6."}
RUL:hcortex_r{id:"hcortex-r",rule:"Roundtrip: compile_hcortex(render_hcortex(ast)) == ast (significado estructural). NO es byte-identico: el render puede reorganizar $0. HCORTEX->CORTEX->HCORTEX puede cambiar whitespace y orden de glosario.",detail:"hcortex-0.1.md $7. Verificado en tests."}
RUL:hcortex_c{id:"hcortex-c",rule:"CAPA se renderiza como <!-- schema:N capa:CAPA -->. El compilador extrae la capa y la asigna a Section.capa. Al compilar se restaura $N: TITULO:CAPA.",detail:"hcortex.py compile_hcortex()."}
RUL:hcortex_err{id:"hcortex-err",rule:"Errores del compilador HCORTEX: H400-H404 (documento: header/encoding/BOM), H410-H417 (glosario), H420-H436 (secciones/Ideas), H440-H472 (shape/pipe/bloque), H480-H490 (canonicidad). Errores comunes: H400 (falta header), H404 (BOM), H433 (sigilo no declarado), H460/H461 (fence mal cerrado).",detail:"hcortex-errors-0.1.md."}
GEN:hcortex{
Para generar HCORTEX valido:

Paso 1: Inicie con <!-- HCORTEX v=0.1 t=canonical --> en linea 1.
Paso 2: Incluya bloque <!-- glossary ... --> con $0:KERNEL, $0:format, y metadata del documento.

Paso 3: Por cada seccion, genere:
  ## $N: Titulo (o ## $N: Seccion N si no tiene titulo)
  [schema] contenido [schema] ...

Paso 4: Los titulos ## y subtitulos ### van SIEMPRE FUERA de schema tags.
  Los ### deben numerarse como §N.M: (N=seccion, M=subseccion).
  Ej: ### §2.1: Preparacion en vez de ### Preparacion.

Paso 5: Cada schema tag contiene UN SOLO TIPO:
  - prose:N     -> solo texto corrido, bold, blockquotes (>). Sin listas, sin diagramas.
  - list:N      -> bullets (- item) y listas numeradas (1. item, 2. item).
  - check:N     -> checkboxes (- [ ] item).
  - table:N     -> tablas pipe (| celda | celda |).
  - diagram:N   -> bloques ```puml ... ```.

Paso 6: Si una seccion tiene contenido MIXTO (ej: texto + lista + diagrama),
  divida en MULTIPLES schemas secuenciales:
  ## §1: Titulo
  <!-- prose:1 -->
  Texto explicativo...
  <!-- /prose:1 -->
  <!-- list:2 -->
  - Item 1
  - Item 2
  <!-- /list:2 -->
  <!-- diagram:3 -->
  ```puml...```
  <!-- /diagram:3 -->

Paso 7: Los numeros N son SECUENCIALES del 1 al total en todo el documento.
  No hay reinicios por seccion. No hay saltos numericos.

Paso 8: NUNCA genere schemas vacios (<!-- prose:N --><!-- /prose:N -->).
  Si una seccion no tiene contenido, omita el schema.

Paso 9: El schema se determina por shape del contenido:
  - Linea empieza con | y contiene | -> table
  - Linea empieza con - [ -> check
  - Linea empieza con - o * -> list
  - Linea empieza con digito+.). -> list (numerada)
  - Contiene ```puml -> diagram
  - Cualquier otra cosa -> prose

Paso 10: NO renderice $0 como tabla visible. Solo en bloque <!-- glossary -->.

Paso 11: compile_hcortex() reconstruye el AST desde HCORTEX.
  compile_hcortex(render_hcortex(ast)) == ast (significado, no byte-identico).
}
EX:hcortex_minimo{
## $1: KNOWLEDGE
apertura table:1
marcador KNW:cortex | CORTEX | Codec ideatico reversible.
cierre /table:1
}
