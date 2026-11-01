<!-- HCORTEX v=1.0 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
$0:namespace_envx{id:envx,version:1.0,required:false}
envx::SD:deployment_request{type:attrs,weight:H,fields:"goal:text|status:atom",focus:goal,desc:"Solicitud de despliegue"}
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text",focus:content,desc:"Conocimiento"}

<!-- /glossary -->

## §1: Sección 1

<!-- schema:1 capa:KNOW -->
### KNW:context
| topic | content |
|---|---|
| "Gobierno" | "CORTEX no gobierna al consumidor." |

### envx::SD:prod
| goal | status |
|---|---|
| "Desplegar versión aprobada." | planned |

<!-- /schema:1 -->

