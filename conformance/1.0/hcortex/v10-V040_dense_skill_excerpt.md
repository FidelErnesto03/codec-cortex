<!-- HCORTEX v=1.0 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
$0:enum_state{values:"current|planned|future|blocked"}
$0:enum_severity{values:"info|warning|blocking"}
$0:micro_cur{expand:current}
IDN:identity{type:attrs,weight:B,fields:"name:text|version:text|status:%state",focus:name,desc:"Identidad"}
CNST:constraint{type:attrs,weight:H,fields:"rule:text|severity:%severity|evidence:text?",focus:rule,desc:"Restricción"}
HDL:handler{type:attrs-pos,weight:M,pos:"operation:text|status:%state|requires:text|notes:text?",focus:operation,desc:"Operación"}

<!-- /glossary -->

## §1: Sección 1

<!-- schema:1 capa:KNOW -->
### IDN:skill
| name | version | status |
|---|---|---|
| "CODEC-CORTEX" | "0.1" | cur |

### CNST:line
| rule | severity | evidence |
|---|---|---|
| "Una línea expresa una idea principal." | blocking | "canon ideático" |

<!-- /schema:1 -->

## §2: Sección 2

<!-- schema:2 capa:DATA -->
### HDL:validate
| operation | status | requires | notes |
|---|---|---|---|
| "validar estructura y contrato" | cur | "documento CORTEX" | "diagnósticos deterministas" |

<!-- /schema:2 -->

