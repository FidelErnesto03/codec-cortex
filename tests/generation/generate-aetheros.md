$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es,type:test}
TST:task{type:attrs,weight:H,fields:"id:text|instruction:text",focus:instruction,schema:table,desc:"Tarea del ejercicio de generacion"}
CTX:context{type:cuerpo,weight:M,schema:prose,desc:"Contexto para la tarea"}
VAL:validation{type:attrs,weight:H,fields:"check:text|expected:text|weight:%weight",focus:check,schema:table,desc:"Criterio de validacion del CORTEX generado"}
$1: CONTEXTO:FLOW
CTX:context{Eres el arquitecto de un nuevo sistema operativo llamado "AetherOS". Acabas de terminar la fase de diseño y necesitas documentar el proyecto para tu equipo de 4 ingenieros.}
$2: TAREA:FLOW
TST:task{id:"GEN-1",instruction:"Documenta el proyecto AetherOS en formato CORTEX 0.1. Tu documento debe describir: (1) el equipo de 4 ingenieros con sus roles, (2) 3 objetivos del proyecto con su estado actual, (3) un principio no negociable del diseño, (4) 2 lecciones aprendidas de la fase de diseño, y (5) los riesgos identificados con su nivel de impacto. Usa los sigilos que consideres apropiados. Declara todo en $0."}
$3: REGLAS DE GENERACION:FLOW
TST:task{id:"GEN-2",instruction:"Tu respuesta debe ser UNICAMENTE el documento CORTEX. No añadas explicaciones, markdown, ni texto fuera del formato CORTEX."}
TST:task{id:"GEN-3",instruction:"El documento debe comenzar con $0 y declarar todos los sigilos usados. Cada sigilo debe tener type, fields y focus."}
TST:task{id:"GEN-4",instruction:"Las secciones deben usar $N: TITULO. Opcionalmente $N: TITULO:CAPA con capa KERNEL|CORE|KNOW|DATA|FLOW|CACHE. KERNEL solo en $0."}
$4: VALIDACION — Uso interno, no incluir en la respuesta:CORE
VAL:validation{check:"Comienza con $0",expected:"si",weight:critico}
VAL:validation{check:"Declara al menos 3 sigilos en $0",expected:"si",weight:critico}
VAL:validation{check:"Cada sigilo en $0 tiene type y fields",expected:"si",weight:critico}
VAL:validation{check:"Usa $N: TITULO para secciones (capas opcionales)",expected:"si",weight:critico}
VAL:validation{check:"5 secciones minimo",expected:"si",weight:alto}
VAL:validation{check:"Al menos 8 ideas en total",expected:"si",weight:alto}
VAL:validation{check:"El parser Python codec_cortex lo valida sin errores",expected:"si",weight:critico}
VAL:validation{check:"Usa sigilos semanticos (no genericos como T1, T2)",expected:"si",weight:medio}
VAL:validation{check:"Contiene los 5 elementos pedidos (equipo, objetivos, principio, lecciones, riesgos)",expected:"si",weight:critico}
