$0
$0:format{cortex:0.1,encoding:UTF-8,language:es,type:test}
TST:task{type:attrs,weight:H,fields:"id:text|question:text|output:text|format:%fmt",focus:question,schema:table,desc:"Tarea de comprension"}
MTR:metric{type:attrs,weight:H,fields:"name:text|value:text",focus:value,schema:table,desc:"Metrica auto-declarada por el modelo"}
INS:instruction{type:cuerpo,weight:H,schema:prose,desc:"Instruccion en lenguaje natural"}
FMT:format{type:attrs,weight:H,fields:"field:text|type:%type|required:%bool",focus:field,schema:table,desc:"Campo del formato de respuesta"}
$1: IDENTIDAD
TST:task{id:"ID.1",question:"Identificate.",output:"Nombre del modelo y plataforma que te ejecuta.",format:texto_libre}
$2: INSTRUCCIONES
INS:contexto{Eres un modelo de lenguaje procesando un archivo en formato CORTEX 0.1. CORTEX es un lenguaje de máquina para modelos de lenguaje. Debes leerlo directamente, sin herramientas externas. Este archivo ES la prueba.}
INS:formato{El glosario $0 declara los sigilos: TST para tareas, MTR para metricas, INS para instrucciones, FMT para formato. Las secciones ($1, $2...) agrupan Ideas por contexto. Cada Idea tiene forma SIGILO:nombre{atributos}.}
$3: TAREAS
TST:task{id:"T3.1",question:"Cuenta el numero total de tokens usados en esta interaccion completa (system + user + assistant).",output:"Numero entero de tokens.",format:numero}
TST:task{id:"T3.2",question:"Toma el texto 'CORTEX es un lenguaje de máquina para modelos de lenguaje' e invierte el orden de sus tokens (no caracteres). Traduce el resultado al ingles.",output:"Texto con tokens invertidos y traducido.",format:texto_libre}
TST:task{id:"T3.3",question:"Extrae del glosario ($0) de este documento la definicion del sigilo MTR.",output:"Definicion completa: nombre, tipo, peso, campos, foco, schema.",format:texto_libre}
TST:task{id:"T3.4",question:"Lista los titulos de todas las secciones ($1, $2...) declaradas en este documento.",output:"Lista de secciones con su titulo.",format:lista}
TST:task{id:"T3.5",question:"¿Que sigilo se usa para definir el formato de respuesta en este documento? Describe sus campos.",output:"Nombre del sigilo y descripcion de sus campos.",format:texto_libre}
TST:task{id:"T3.6",question:"¿Cuantas tareas (sigilo TST) estan declaradas en este documento?",output:"Numero entero de tareas.",format:numero}
$4: FORMATO DE RESPUESTA
INS:formato_respuesta{Responde UNICAMENTE con el siguiente bloque JSON. No añadas texto antes ni despues.}
FMT:format{field:"model",type:texto,required:true}
FMT:format{field:"platform",type:texto,required:true}
FMT:format{field:"date",type:texto,required:true}
FMT:format{field:"total_tokens",type:numero,required:true}
FMT:format{field:"tasks",type:tabla,required:true}
FMT:format{field:"comprehension_self_assessment",type:numero,required:true}
FMT:format{field:"notes",type:texto,required:false}
INS:json_ejemplo{Responde UNICAMENTE con un objeto JSON como este: {"model":"Nombre","platform":"Plataforma","date":"YYYY-MM-DD","total_tokens":0000,"tasks":[{"id":"ID.1","answer":"..."},{"id":"T3.1","answer":"..."},{"id":"T3.2","answer":"..."},{"id":"T3.3","answer":"..."},{"id":"T3.4","answer":"..."},{"id":"T3.5","answer":"..."},{"id":"T3.6","answer":"..."}],"comprehension_self_assessment":5,"notes":"Opcional"}}
$5: METRICAS
MTR:metric{name:"Nivel de comprension CORTEX auto-evaluado",value:"Ver campo comprehension_self_assessment en la respuesta JSON"}
MTR:metric{name:"Cumplimiento de formato",value:"Verificar que la respuesta es JSON valido con los campos declarados en FMT"}
MTR:metric{name:"Precision T3.2",value:"Comparar con golden: 'language models for machine language a is CORTEX'"}
MTR:metric{name:"Precision T3.6",value:"Golden: 8 (ID.1 + T3.1 a T3.6 + comprehension_self_assessment? No: solo TST. Respuesta correcta: 6)"}
MTR:metric{name:"Adopcion de nomenclatura CORTEX",value:"¿El modelo usa terminos como 'sigilo', 'seccion', '$0', 'glosario' en notes?"}
