# Authoring CORTEX — Creación de sigilos personalizados

Guía para humanos que quieren crear sus propios sigilos y secciones en CORTEX.

---

## ¿Qué es un sigilo?

Un sigilo es el **tipo** de una Idea. Como una clase en programación.

```cortex
OBJ:mi_objetivo{goal:"Aprender.",status:current}
 ^-- sigilo
```

## Estructura de una declaración

En el glosario ($0), cada sigilo se declara así:

```cortex
SIGILO:nombre{type:TIPO,weight:PESO,fields:"CAMPOS",focus:CAMPO,schema:ESQUEMA,desc:"DESCRIPCION"}
```

Ejemplo real (de un proyecto personal):

```cortex
LIBRO:lectura{type:attrs,weight:H,fields:"titulo:text|autor:text|paginas:number|estado:%estado",focus:titulo,schema:table,desc:"Libro en mi lista de lectura"}
```

## Campos obligatorios

| Campo | Qué define | Valores posibles |
|---|---|---|
| **type** | Forma del payload | attrs, attrs-pos, cuerpo, bloque, relacion |
| **weight** | Importancia | H (alta), M (media), B (baja) |
| **fields** | Contrato de atributos | "campo:tipo\|campo2:tipo2" |
| **focus** | Campo principal | Debe existir en fields |
| **schema** | Visualización en HCORTEX | table, prose, list, check, diagram |
| **desc** | Descripción del sigilo | Texto libre |

## Tipos de fields

| Tipo | Descripción | Ejemplo |
|---|---|---|
| text | Texto libre (con o sin comillas) | `nombre:text` |
| number | Entero o decimal | `presupuesto:number` |
| %bool | true/false | `activo:%bool` |
| %ENUM | Enum declarado en $0 | `estado:%state` |

Los enums se declaran aparte:

```cortex
$0:enum_state{values:"current|planned|done"}
$0:enum_estado{values:"pendiente|leyendo|terminado"}
```

## Schemas disponibles

| Schema | Cuándo usarlo | Apariencia en HCORTEX |
|---|---|---|
| **table** | Datos tabulares (varias ideas del mismo tipo) | Tabla markdown |
| **prose** | Texto libre, párrafos, descripciones | Texto corrido |
| **list** | Items con bullet | Lista |
| **check** | Checklist | - [ ] |
| **diagram** | PUML en fence | Bloque de código |

## Ejemplo completo

Declaración:

```cortex
$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es}
$0:enum_prioridad{values:"baja|media|alta|critica"}
RECETA:plato{type:attrs,weight:M,fields:"nombre:text|dificultad:%prioridad|tiempo:number|calorias:number",focus:nombre,schema:table,desc:"Plato de cocina"}
PASO:instruccion{type:attrs-pos,weight:H,fields:"orden:number|desc:text|duracion:number",pos:"0|1|2",focus:desc,schema:list,desc:"Paso de preparacion"}
NOTA:comentario{type:cuerpo,weight:M,schema:prose,desc:"Nota libre sobre la receta"}

$1: PLATOS:DATA
RECETA:paella{nombre:"Paella valenciana",dificultad:alta,tiempo:60,calorias:480}
RECETA:tortilla{nombre:"Tortilla de patatas",dificultad:media,tiempo:30,calorias:320}

$2: PASOS:DATA
NOTA:comentario{Para la paella, lo importante es el socarrat.}
```

## Reglas importantes

1. **Declara en $0 todo sigilo que uses.** Si usas RECETA, declara RECETA en $0
2. **No dupliques sigilos.** Cada sigilo se declara una sola vez
3. **focus debe coincidir con un campo de fields** exactamente
4. **Los enums se declaran antes** de usarlos en fields
5. **5 values tiene un sigilo:** type, weight, fields, focus, schema (desc opcional)

## Capas de profundidad cortical

Cada sección `$N: TITULO` puede incluir opcionalmente una capa que define su
resiliencia en la ventana de contexto:

```cortex
$N: TITULO:CAPA
```

| Capa    | Significado                                      | Resiliencia  |
|---------|--------------------------------------------------|-------------|
| KERNEL  | Esencia funcional. Identidad. Inamovible.        | Nunca       |
| CORE    | Reglas, restricciones (LIM), alertas.            | Muy alta    |
| KNOW    | Conocimiento procesado (skills, lecciones LNG).   | Alta        |
| DATA    | Datos de referencia consultable.                  | Media       |
| FLOW    | Sesión activa, WRK:current, tareas en curso.      | Media-baja  |
| CACHE   | Transitorio (handoff, PULSE, SES).               | Baja        |

**Reglas:**
1. KERNEL es obligatorio: `$0` siempre es KERNEL
2. KERNEL solo se asigna a `$0` y secciones que definan identidad funcional
3. Las demás capas son opcionales, se usan solo donde aplica
4. Orden de evicción bajo presión de contexto: CACHE → FLOW → DATA → KNOW → CORE → KERNEL
5. KERNEL nunca se compacta ni se evicciona
