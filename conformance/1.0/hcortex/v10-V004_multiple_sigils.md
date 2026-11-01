<!-- HCORTEX v=1.0 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
$0:enum_state{values:"current|planned|blocked"}
OBJ:objective{type:attrs,weight:H,fields:"goal:text|status:%state|evidence:text?",focus:goal,desc:"Objetivo verificable"}
CNST:constraint{type:attrs,weight:H,fields:"rule:text|severity:atom|evidence:text?",focus:rule,desc:"Restricción no negociable"}

<!-- /glossary -->

## §1: Dirección

<!-- schema:1 capa:CORE -->
### OBJ:f2
| goal | status |
|---|---|
| "Definir CORTEX Draft 0.1 real." | current |

### CNST:no_external_profile
| rule | severity | evidence |
|---|---|---|
| "El documento no depende de un perfil externo para comprenderse." | blocking | "glosario local" |

<!-- /schema:1 -->

