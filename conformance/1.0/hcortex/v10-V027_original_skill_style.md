<!-- HCORTEX v=1.0 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
$0:enum_state{values:"current|planned|future"}
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text|status:%state|evidence:text?",focus:content,desc:"Conocimiento operativo verificable"}
CNST:constraint{type:attrs,weight:H,fields:"rule:text|severity:atom|evidence:text?",focus:rule,desc:"Restricción no negociable"}

<!-- /glossary -->

## §1: Sección 1

<!-- schema:1 capa:KNOW -->
### KNW:cortex
| topic | content | status | evidence |
|---|---|---|---|
| "CORTEX" | "Representación densa nativa y fuente canónica." | current | "parser y AST" |

### CNST:no_llm
| rule | severity | evidence |
|---|---|---|
| "El codec no depende de inferencia probabilística." | blocking | "diseño determinista" |

<!-- /schema:1 -->

