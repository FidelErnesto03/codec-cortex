<!-- HCORTEX v=1.0 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
REL:relation{type:relacion,weight:M,pos:"source:atom|predicate:atom|target:atom",focus:predicate,desc:"Relación dirigida explícita"}
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text",focus:content,desc:"Conocimiento"}

<!-- /glossary -->

## §1: Sección 1

<!-- schema:1 capa:KNOW -->
### KNW:parser
| topic | content |
|---|---|
| "Parser" | "Transforma texto en AST." |

### KNW:ast
| topic | content |
|---|---|
| "AST" | "Modelo estructural." |

### REL:parser_ast
| source | predicate | target |
|---|---|---|
| KNW:parser | produces | KNW:ast |

<!-- /schema:1 -->

