# Authoring CORTEX 1.0 — sigilos y secciones

Guía para crear sigilos propios sin romper el canon.

---

## Qué es un sigilo

El **tipo** de una idea. Se declara una vez en `$0` y se usa en las secciones.

```cortex
OBJ:mi_objetivo{goal:"Aprender.",status:current}
 ^-- sigilo        ^-- nombre de la idea
```

## Declaración

```cortex
SIGILO:nombre{type:TIPO,weight:PESO,CONTRATO,focus:CAMPO,desc:"ETIQUETA"}
```

Donde `CONTRATO` es **uno** de:

| Forma | Atributo | Uso |
|---|---|---|
| por nombre | `fields:"a:text|b:int"` | shape `attrs` |
| por posición | `pos:"a:text|b:int"` | shapes `attrs-pos` y `relacion` |
| por slots | `slots:"1=a:text|2=b:int"` + `encoding:slots` | eje slots (0.2/1.0) |

## Atributos

| Atributo | Obligatorio | Valores |
|---|---|---|
| `type` | sí | `attrs`, `attrs-pos`, `relacion`, `cuerpo`, `bloque` |
| `weight` | sí | `H`, `M`, `B` |
| `fields` \| `pos` \| `slots` | según shape | contrato de campos |
| `focus` | sí | nombre del campo (o posición, en slots) |
| `desc` | sí | etiqueta de 1–3 palabras |
| `open` | no | `true` permite campos fuera del contrato |
| `encoding` | no | `slots` para el eje de codificación |

`open:true` es la única forma legítima de llevar campos extra: C14N los ordena
por clave UTF-8 después de los del contrato, y el orden editorial se declara
como pérdida `L405_OPEN_ATTR_ORDER`.

## Tipos de campo

| Tipo | Qué acepta |
|---|---|
| `text` | texto libre (con o sin comillas) |
| `atom` | átomo sin espacios |
| `int` / `dec` | entero / decimal |
| `bool` | `true` / `false` |
| `null` | ausencia declarada |
| `list` | `[a,b,c]` |
| `any` | sin restricción |
| `%enum` | valor de un enum declarado en `$0` |

Los enums se declaran en el glosario, antes de usarse:

```cortex
$0:enum_state{values:"current|planned|done"}
```

## HCORTEX: el schema se deriva, no se declara

En 1.0 el autor **no elige** el schema: lo determina el shape.

| Shape | Schema de render |
|---|---|
| `attrs`, `attrs-pos`, `relacion` | `table` (tabla) |
| `cuerpo` | `prose` (texto) |
| `bloque` | `diagram` (fence) |

`list` y `check` pertenecen a HCORTEX 0.1 y no los produce el renderer 1.0.
Declarar `schema:...` en un sigilo 1.0 es ruido: no cambia el render.

## Ejemplo completo

```cortex
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
$0:enum_prioridad{values:"baja|media|alta|critica"}
RECETA:plato{type:attrs,weight:M,focus:nombre,desc:"Plato",fields:"nombre:text|dificultad:%prioridad|tiempo:int|calorias:int"}
PASO:instruccion{type:attrs-pos,weight:H,focus:desc,desc:"Paso",pos:"orden:int|desc:text|duracion:int"}
NOTA:comentario{type:cuerpo,weight:M,desc:"Nota"}
$1: PLATOS:DATA
RECETA:paella{nombre:"Paella valenciana",dificultad:alta,tiempo:60,calorias:480}
RECETA:tortilla{nombre:"Tortilla de patatas",dificultad:media,tiempo:30,calorias:320}
$2: PASOS:DATA
PASO:p1|1|"Sofreir la base"|20
PASO:p2|2|"Anadir el arroz"|25
$3: NOTAS:KNOW
NOTA:socarrat{
Para la paella, lo importante es el socarrat.
}
```

Verificación:

```bash
python -m codec_cortex validate receta.cortex
python -m codec_cortex loss-report receta.cortex
```

## Sigilos con slots

El eje slots codifica el contrato por posición y exige `$0:sigil-map`:

```cortex
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8}
$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}
TST:test{type:attrs,encoding:slots,weight:H,slots:"1=id:text|2=result:atom",focus:id,desc:"Prueba"}
$1: RESULTADOS:DATA
TST:t1{※1:"corpus",※2:pass}
```

Reglas: `※` prohibido en `$0` (`I050`), índices ascendentes (`I054`), sin
duplicados (`I051`) y sin desconocidos (`I052`).

## Reglas

1. Todo sigilo usado se declara en `$0`; todo sigilo declarado tiene contrato
   completo (`fields`/`pos`/`slots` + `focus`).
2. `focus` debe existir en el contrato (nombre o posición según shape).
3. Los enums se declaran antes de usarse (`G026` si no).
4. La aridad posicional es estricta en 1.0 (`I012_POSITIONAL_ARITY`).
5. Una idea por línea; `cuerpo` y `bloque` son la única excepción multilínea.

## Capas de profundidad cortical

Cada sección `$N: TITULO` admite una capa que declara su resiliencia:

```cortex
$N: TITULO:CAPA
```

| Capa | Significado | Resiliencia |
|---|---|---|
| KERNEL | esencia funcional, identidad | nunca se evicciona |
| CORE | reglas y restricciones | muy alta |
| KNOW | conocimiento procesado | alta |
| DATA | datos de referencia | media |
| FLOW | sesión activa, tareas en curso | media-baja |
| CACHE | transitorio (handoff, pulse) | baja |

`$0` es siempre KERNEL. Orden de evicción bajo presión de contexto:
CACHE → FLOW → DATA → KNOW → CORE → KERNEL.
