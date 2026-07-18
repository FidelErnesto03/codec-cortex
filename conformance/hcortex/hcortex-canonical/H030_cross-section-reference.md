<!-- HCORTEX v=0.1 t=canonical -->

<!-- glossary
$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es}
$0:enum_state{values:"current|planned|blocked|done"}
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text|status:%state?|evidence:text?",focus:content,desc:"Conocimiento verificable"}
REL:relation{type:relacion,weight:M,pos:"source:atom|predicate:atom|target:atom|qualifier:text?",focus:predicate,desc:"Relación dirigida"}
-->

## §1: Sección 1

<!-- table:1 capa:KNOW -->
<!-- KNW:parser --> | Parser | "Produce AST." |
<!-- /table:1 -->

## §2: Sección 2

<!-- prose:2 capa:KNOW -->
<!-- KNW:ast --> topic:AST,content:"Modelo ideático."
<!-- REL:link --> $1:KNW:parser|produces|$2:KNW:ast
<!-- /prose:2 -->

