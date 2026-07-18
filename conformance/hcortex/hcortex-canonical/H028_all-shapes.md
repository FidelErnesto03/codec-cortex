<!-- HCORTEX v=0.1 t=canonical -->

<!-- glossary
$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es}
$0:enum_state{values:"current|planned|blocked|done"}
DIAG:diagram{type:bloque,weight:B,desc:"Bloque verbatim"}
HDL:procedure{type:attrs-pos,weight:M,pos:"action:text|status:%state|target:text|constraint:text?",focus:action,desc:"Procedimiento compacto"}
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text|status:%state?|evidence:text?",focus:content,desc:"Conocimiento verificable"}
REL:relation{type:relacion,weight:M,pos:"source:atom|predicate:atom|target:atom|qualifier:text?",focus:predicate,desc:"Relación dirigida"}
TXT:text{type:cuerpo,weight:B,desc:"Texto semántico"}
-->

## §1: Sección 1

<!-- prose:1 capa:KNOW -->
<!-- KNW:k --> topic:Todos,content:"Cobertura de shapes."
<!-- HDL:p --> renderizar|current|AST
<!-- TXT:t -->
Texto humano.
<!-- DIAG:b -->
<!-- REL:r --> $1:KNW:k|supports|$1:TXT:t
<!-- /prose:1 -->

