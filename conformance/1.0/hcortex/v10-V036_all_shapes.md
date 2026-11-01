<!-- HCORTEX v=1.0 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
$0:enum_state{values:"current|planned"}
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text|status:%state",focus:content,desc:"Conocimiento"}
HDL:handler{type:attrs-pos,weight:M,pos:"operation:text|status:%state",focus:operation,desc:"Operación"}
TXT:statement{type:cuerpo,weight:B,desc:"Texto"}
CODE:code{type:bloque,weight:M,desc:"Bloque"}
REL:relation{type:relacion,weight:M,pos:"source:atom|predicate:atom|target:atom",focus:predicate,desc:"Relación"}

<!-- /glossary -->

## §1: Sección 1

<!-- schema:1 capa:KNOW -->
### KNW:one
| topic | content | status |
|---|---|---|
| "Idea" | "Una línea comunica una idea." | current |

### HDL:parse
| operation | status |
|---|---|
| "convertir texto a AST" | current |

### TXT:explain
Texto humano breve.

### CODE:sample
```
print("cortex")
```

### REL:flow
| source | predicate | target |
|---|---|---|
| source | becomes | target |

<!-- /schema:1 -->

