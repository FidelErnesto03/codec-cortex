<!-- HCORTEX v=0.1 t=canonical -->

<!-- glossary
$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es}
$0:enum_state{values:"current|planned|blocked|done"}
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text|status:%state?|evidence:text?",focus:content,desc:"Conocimiento verificable"}
OBJ:objective{type:attrs,weight:H,fields:"goal:text|status:%state|metric:text?",focus:goal,desc:"Objetivo explícito"}
RSK:risk{type:attrs,weight:H,fields:"risk:text|impact:text|status:%state",focus:risk,desc:"Riesgo explícito"}
-->

## §1: Sección 1

<!-- table:1 capa:CORE -->
<!-- OBJ:goal --> | "Orden canónico." | current |
<!-- RSK:ambiguity --> | "Orden variable." | "Hash distinto." | blocked |
<!-- /table:1 -->

