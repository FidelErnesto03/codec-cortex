# Mapa de evolución desde `codec-cortex.skill.cortex`

**Propósito:** orientar migración conceptual sin declarar compatibilidad automática.

## 1. Declaraciones de sigilo

Experimental:

```cortex
KNW:knowledge{type:attrs,risk:B,cortex:Semantic,desc:"Conocimiento operativo verificable"}
```

Draft 0.1 REAL:

```cortex
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text|status:atom|evidence:text?",focus:content,desc:"Conocimiento operativo verificable"}
```

Cambios:

- `risk` se separa de peso funcional;
- `cortex:Semantic` se elimina del Core;
- se formaliza el patrón que las líneas ya repetían;
- las líneas KNW ordinarias no requieren cambio superficial.

## 2. Contratos posicionales

Experimental:

```cortex
$0:contract_hdl{pos:"operation|status|requires|notes"}
HDL:version|reportar versión|current|ninguno|cortex --version
```

Draft 0.1 REAL:

```cortex
HDL:handler{type:attrs-pos,weight:M,pos:"operation:text|status:atom|requires:text|notes:text?",focus:operation,desc:"Operación CLI"}
HDL:version|reportar versión|current|ninguno|cortex --version
```

El contrato queda junto al sigilo y tipado. El uso permanece.

## 3. Microtokens

Forma preservada:

```cortex
$0:micro_cur{expand:current}
```

Se limita a values atom y se conserva el lexema.

## 4. Enums

Forma preservada:

```cortex
$0:enum_state{values:"current|planned|future|blocked"}
```

Los contratos los referencian como `%state`.

## 5. Secciones

Forma canónica de Draft:

```cortex
$2
$2: Conocimiento
```

La forma histórica `2` sin `$` queda como legacy, no como sintaxis 0.1.

## 6. VIEW

Las líneas VIEW históricas pueden migrarse a una extensión de presentación.

La reversibilidad base no depende de VIEW: el shape y contrato ya determinan una proyección humana universal.

## 7. Tipos de documento y learning

No son parte de Fase 2. Pueden definirse en `cortex-profiles`, `cortex-runtime` o `cortex-learning`.

## 8. Estrategia de migración futura

Un bridge debería:

1. preservar original;
2. detectar sigilos y patrones recurrentes;
3. inferir propuesta de `fields` desde líneas y VIEW;
4. exigir confirmación si el foco no es inequívoco;
5. mapear `risk` a `weight` solo con política explícita;
6. extraer ontología externa a perfiles;
7. emitir mapping report y loss report.
