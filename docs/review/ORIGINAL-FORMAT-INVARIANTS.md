# Invariantes del formato original preservadas

## 1. Evidencia de origen

La skill experimental `codec-cortex.skill.cortex` demuestra operativamente:

- `$0` como glosario local;
- sigilos como funciones ideáticas;
- `SIGIL:nombre{...}`;
- `attrs-pos` con `|`;
- bare values;
- microtokens locales;
- enums locales;
- una línea recurrente por Idea;
- proyecciones humanas tabulares, listas, prosa, bloques y diagramas.

La nueva Fase 2 no copia su ontología de dominio. Extrae y formaliza el mecanismo.

## 2. Preservado sin cambio de naturaleza

| Original | Draft 0.1 REAL |
|---|---|
| `$0` primero | `$0` obligatorio, primero y único |
| declaración `SIGIL:meaning{...}` | misma forma, contrato endurecido |
| uso `SIGIL:name{...}` | misma forma |
| positional `SIGIL:name|...` | misma forma |
| values bare | atoms normados |
| microtokens | meta-declaraciones normadas |
| enums | meta-declaraciones normadas |
| secciones `$N` | misma forma, título desambiguado |
| cuerpo/bloque | shapes fundamentales |
| relación dirigida | shape fundamental |

## 3. Evolución necesaria

| Debilidad experimental | Evolución |
|---|---|
| fields attrs implícitos | `fields` obligatorio |
| foco inferido | `focus` obligatorio |
| peso mezclado con risk/cortex region | `weight` neutral |
| versión externa o narrativa | `$0:format` |
| namespaces no normados | namespace local o calificado |
| extensiones de facto | declaración explícita |
| errores dependientes de implementación | códigos normativos |
| AST orientado a producto | AST ideático neutral |
| VIEW requerido para reversibilidad | shape suficiente; VIEW opcional |

## 4. Elementos no trasladados al Core

- `FCS`, `OBJ`, `KNW`, `CNST` como palabras reservadas;
- `Semantic`, `Prefrontal`, `Working`;
- `survive`;
- learning;
- brain/skill/package;
- runtime;
- gobierno;
- CORTEX-OUT;
- CLI histórica;
- VIEW programable como requisito base.

Todos continúan siendo expresables en un glosario o perfil externo.

## 5. Prueba conceptual

El siguiente documento es CORTEX 0.1 válido sin que el Core conozca el dominio:

```cortex
$0
$0:format{cortex:0.1,encoding:UTF-8,language:es}
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text|status:atom",focus:content,desc:"Conocimiento"}
CNST:constraint{type:attrs,weight:H,fields:"rule:text|severity:atom",focus:rule,desc:"Restricción"}
$1
KNW:codec{topic:"CORTEX",content:"Codec ideático lineal.",status:current}
CNST:portable{rule:"El documento transporta su vocabulario.",severity:blocking}
```

El parser solo conoce declaraciones, contratos y shapes. El documento comunica el significado local.
