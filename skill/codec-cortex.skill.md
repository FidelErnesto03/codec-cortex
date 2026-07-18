$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es,type:skill}
RUL:rule{type:attrs,weight:H,fields:"id:text|rule:text|detail:text",focus:rule,schema:prose,desc:"Regla del formato CORTEX"}
GEN:generate{type:cuerpo,weight:H,schema:prose,desc:"Instruccion de generacion"}
$1: IDENTIDAD:CORE
RUL:rule{id:"que-es",rule:"CODEC-CORTEX es un codec ideatico reversible. La IA lee y escribe CORTEX. El humano lee HCORTEX.",detail:"version 1.0.0-rc.1 CC0-1.0"}
$2: SINTAXIS DE CORTEX:CORE
RUL:rule{id:"gramatica",rule:"3 partes: $0 glosario, $N: TITULO secciones, SIGILO:nombre{atributos} ideas.",detail:"Cada idea en su linea. Siguiente $N inicia nueva seccion."}
RUL:rule{id:"formato",rule:"$0:format{cortex:0.1,encoding:UTF-8,language:es} en linea 2.",detail:"type opcional para metadato."}
RUL:rule{id:"secciones",rule:"$N: TITULO. N entero positivo. Titulo opcional. $N.M subsecciones validas. Opcionalmente $N: TITULO:CAPA.",detail:"Orden significativo. CAPA: KERNEL|CORE|KNOW|DATA|FLOW|CACHE."}
$8: CAPAS DE PROFUNDIDAD CORTICAL:CORE
AXM:kernel_siempre{Todo .cortex tiene al menos KERNEL. $0 siempre es KERNEL. Sin KERNEL no es .cortex.}
AXM:kernel_inamovible{KERNEL no se comprime, no se evicciona, no se negocia. Es lo que el archivo ES.}
RUL:capa_kernel{id:"KERNEL",significado:"Esencia funcional del archivo. Identidad. Inamovible.",restriccion:"Solo $0 y secciones que definan identidad funcional."}
RUL:capa_core{id:"CORE",significado:"Reglas, restricciones (LIM), alertas. Gobierna la operacion.",restriccion:"Cualquier $N."}
RUL:capa_know{id:"KNOW",significado:"Conocimiento estrategico y tactico procesado. Skills, lecciones (LNG).",restriccion:"Cualquier $N."}
RUL:capa_data{id:"DATA",significado:"Datos de referencia. Informacion estructurada consultable.",restriccion:"Cualquier $N."}
RUL:capa_flow{id:"FLOW",significado:"Sesion activa. WRK:current, tareas, decisiones en curso.",restriccion:"Cualquier $N."}
RUL:capa_cache{id:"CACHE",significado:"Transitorio. Handoff, PULSE, SES. Se consume y descarta.",restriccion:"Cualquier $N."}
RUL:capa_eviccion{id:"eviccion",rule:"Orden de sacrificio bajo presion: CACHE → FLOW → DATA → KNOW → CORE → KERNEL.",detail:"KERNEL nunca se evicciona."}
$3: GLOSARIO EN $0:CORE
RUL:rule{id:"declaracion",rule:"SIGILO:nombre{type:VALOR,weight:VALOR,fields:CAMPOS,focus:CAMPO,schema:VALOR,desc:TEXTO}",detail:"type attrs attrs-pos cuerpo bloque relacion. weight H M B. schema table prose list check diagram."}
RUL:rule{id:"fields",rule:"campo1:tipo1|campo2:tipo2. Tipos: text number %bool %enum.",detail:"? sufijo opcional."}
$4: HCORTEX — 5 ESQUEMAS:CORE
RUL:rule{id:"hcortex-entrada",rule:"<!-- HCORTEX v=0.1 t=canonical k=TIPO -->",detail:"TIPO: brain mission skill test corpus"}
RUL:rule{id:"hcortex-pares",rule:"<!-- schema:N -->...<!-- /schema:N --> por seccion. Sin anidamiento.",detail:"N coincide con numero de seccion. $0 no se renderiza."}
RUL:rule{id:"hcortex-compile",rule:"Si hay <!-- glossary --> reconstruir $0. Tablas a attrs, listas a attrs-pos, prose a cuerpo, fence a bloque.",detail:"Roundtrip preserva significado no bytes."}
$5: GENERACION:FLOW
GEN:generate{Para generar CORTEX: $0 con sigilos. $N secciones. SIGILO:nombre{k:v} cada idea. Atributos separados por comas. Numeros y booleanos sin comillas. Texto con espacios usa comillas dobles.}
GEN:generate{Para generar HCORTEX: <!-- HCORTEX v=0.1 -->. Schema por seccion: attrs → table, cuerpo → prose, bloque → diagram, items → list, check → check. Envuelve en <!-- schema:N -->...<!-- /schema:N -->.}
$6: USO DEL PARSER:CORE
RUL:rule{id:"instalacion",rule:"pip install codec-cortex. Sin dependencias externas.",detail:"Python 3.10+"}
RUL:rule{id:"parsear",rule:"from codec_cortex.parser import parse_cortex; doc=parse_cortex(open('archivo.cortex').read())",detail:"doc.sections para secciones. doc.sections[0].ideas para ideas."}
RUL:rule{id:"hcortex-render",rule:"from codec_cortex.hcortex import render_hcortex; hc=render_hcortex(doc)",detail:"hc es string con schemas emparejados."}
RUL:rule{id:"hcortex-compile-api",rule:"from codec_cortex.hcortex import compile_hcortex; doc2,diags=compile_hcortex(hc_string)",detail:"doc2 es Document. diags son advertencias."}
RUL:rule{id:"canonicalizar",rule:"from codec_cortex.c14n import canonicalize; canon=canonicalize(doc)",detail:"canon es string con bytes canonicos deterministas."}
$7: IMPLEMENTACIONES:FLOW
GEN:generate{Python oficial: codec_cortex. Rust: codec-cortex-rs. Go: codec-cortex-go. Node: codec-cortex-node. Bash: codec-cortex-bash. Todas con C14N 40/40.}
