<!-- HCORTEX v=1.0 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
$0:enum_state{values:"current|planned|blocked|done"}
$0:enum_severity{values:"info|warning|blocking"}
$0:micro_cur{expand:current}
$0:micro_blk{expand:blocked}
OBJ:objective{type:attrs,weight:H,fields:"goal:text|status:%state|evidence:text?",focus:goal,desc:"Objetivo"}
RSK:risk{type:attrs,weight:M,fields:"risk:text|impact:text|mitigation:text|status:%state",focus:risk,desc:"Riesgo y mitigación"}
CNST:constraint{type:attrs,weight:H,fields:"rule:text|severity:%severity|evidence:text?",focus:rule,desc:"Restricción"}

<!-- /glossary -->

## §1: Contexto

<!-- schema:1 capa:CORE -->
### OBJ:phase2
| goal | status | evidence |
|---|---|---|
| "Definir CORTEX Draft 0.1 real." | cur | "entregables F2" |

### RSK:drift
| risk | impact | mitigation | status |
|---|---|---|---|
| "Convertir CORTEX en un formato genérico." | "Pérdida de identidad y densidad." | "Mantener sigilos, glosario y línea ideática." | blk |

### CNST:portable
| rule | severity |
|---|---|
| "El documento transporta el vocabulario necesario." | blocking |

<!-- /schema:1 -->

