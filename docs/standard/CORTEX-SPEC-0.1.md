# CORTEX Draft 0.1 — Modelo ideático y gramática

**Document ID:** `CORTEX-SPEC-0.1-DRAFT-REAL-001`  
**Version del lenguaje:** `0.1`  
**Revisión documental:** `DRAFT-REAL-001`  
**Status:** `draft-for-independent-implementation`  
**Fase:** `2 — Modelo abstracto y gramática`  
**Idioma normativo:** español  
**Codificación:** UTF-8  
**Autoridad superior:** `CORTEX-CONSTITUTION-001`  
**Sustituye:** todas las entregas anteriores de Fase 2  

---

## 1. Naturaleza del Draft

Este documento define CORTEX 0.1 como un **codec ideático lineal: un lenguaje de máquina para modelos de lenguaje (LLM/SLM)**. Los modelos de lenguaje leen y comprenden CORTEX directamente, sin parser, sin AST, sin validación formal. Las herramientas de transformación (parser, canonicalizador, renderizador HCORTEX) existen para facilitar la conversión CORTEX↔HCORTEX — no para interpretar el contenido.

CORTEX no es una serialización textual genérica del AST. El AST existe como artefacto interno de las herramientas de transformación; la sintaxis no debe convertirse en una exposición mecánica del AST.

La unidad semántica principal es una **Idea**. Su unidad superficial preferente es una **línea ideática**:

```text
SIGIL:nombre + payload conforme al glosario local
```

Ejemplo:

```cortex
KNW:determinism{topic:"Determinismo",content:"Misma entrada produce igual estructura.",status:current}
```

La línea expresa función, identidad y contenido sin depender de prosa de enlace.

## 2. Lenguaje normativo

Las palabras **DEBE**, **NO DEBE**, **REQUERIDO**, **DEBERÍA**, **NO DEBERÍA** y **PUEDE** son normativas.

Una implementación solo puede declarar conformidad con una versión y nivel explícitos.

## 3. Objetivo

CORTEX 0.1 define una representación que:

1. transporta su vocabulario necesario;
2. expresa una idea principal por línea;
3. elimina repetición lingüística y estructural innecesaria;
4. mantiene un patrón estable por sigilo;
5. permite ampliar vocabulario sin ampliar gramática;
6. puede transformarse determinísticamente a representaciones humanas;
7. puede ser implementada sin conocer productos, perfiles o código histórico.

## 4. Propiedades rectoras

### 4.1 Portable

Un documento CORTEX conforme DEBE contener en `$0` la información estructural necesaria para interpretar todos los sigilos usados.

Un consumidor NO DEBE necesitar:

- un perfil remoto;
- un registro semántico externo;
- ArqUX;
- un runtime;
- un motor de aprendizaje;
- inferencia de un LLM;
- conocimiento de dialectos históricos.

Un perfil externo PUEDE enriquecer la semántica, pero no reemplazar el glosario local.

### 4.2 Denso

Cada elemento visible DEBE aportar una de estas funciones:

- identificar la función ideática;
- identificar la idea;
- delimitar estructura;
- comunicar contenido;
- expresar peso o contrato;
- preservar información necesaria.

La brevedad sin cierre semántico no constituye densidad.

### 4.3 Compacto

Una línea ideática DEBE comunicar una idea principal sin requerir prosa anterior o posterior para completar su estructura.

Las secciones organizan. NO DEBEN completar silenciosamente el significado de sus líneas.

Una relación PUEDE ampliar una idea, pero una idea regular NO DEBE depender de una cadena de referencias para resultar estructuralmente completa.

### 4.4 Extensible

La extensión primaria de CORTEX ocurre mediante el glosario:

- nuevos sigilos;
- nuevos contratos;
- nuevos enums;
- nuevos microtokens;
- namespaces;
- declaraciones de extensión.

Una extensión NO DEBE introducir una nueva gramática de líneas.

### 4.5 Reproducible

Todas las ideas de un mismo sigilo DEBEN respetar el mismo:

- shape;
- contrato;
- orden de campos;
- tipos de campo;
- foco ideático;
- peso funcional por defecto.

Un lector puede aprender el patrón del documento leyendo `$0` y las primeras ideas, y reutilizarlo sin reinterpretar cada línea desde cero.

### 4.6 Simple

CORTEX 0.1 favorece:

- estructuras planas;
- profundidad mínima;
- delimitadores escasos;
- valores bare cuando son inequívocos;
- contratos amortizados en `$0`;
- una sola gramática de encabezado ideático.

CORTEX 0.1 NO incluye mapas anidados, listas anidadas, herencia implícita, macros ejecutables ni inferencia probabilística.

### 4.7 Reversible

La estructura de una Idea DEBE conservar información suficiente para una proyección HCORTEX determinista.

Las clases base de proyección son directas:

| Shape CORTEX | Clase humana natural |
|---|---|
| `attrs` | ficha o fila tabular |
| `attrs-pos` | fila tabular según contrato |
| `cuerpo` | prosa breve |
| `bloque` | bloque verbatim o código |
| `relacion` | relación tabular o arista de diagrama |

Las reglas completas de HCORTEX pertenecen a Fase 4. Fase 2 únicamente garantiza que el AST no destruya la información necesaria.

## 5. Alcance de Fase 2

Esta especificación define:

- modelo abstracto;
- documento;
- glosario local;
- Idea y línea ideática;
- sigilos;
- identidad local;
- namespaces;
- shapes;
- contratos;
- scalars;
- secciones;
- extensiones;
- comentarios;
- Unicode;
- AST;
- validación estructural;
- diagnostics.

No define:

- bytes canónicos;
- hashes;
- equivalencia final;
- source-preserving writer;
- HCORTEX completo;
- materialización histórica;
- retención;
- proyección bajo presupuesto;
- perfiles de agentes.

Esas materias pertenecen a fases posteriores o extensiones externas.

## 6. Modelo abstracto

```text
Document
├── cortex_version
├── encoding
├── glossary
└── sections[]

Glossary
├── format
├── meta_declarations[]
├── enums[]
├── microtokens[]
├── namespaces[]
├── extensions[]
└── symbols[]

Section
├── id
├── title?
└── ideas[]

Idea
├── local_address
├── function
│   ├── symbol
│   ├── label
│   ├── weight
│   └── focus
├── name
├── shape
└── payload
```

### 6.1 Idea

Una Idea es una unidad contextual identificada que cumple un contrato local.

Una Idea estructurada posee:

1. **función:** expresada por el sigilo;
2. **identidad local:** expresada por el nombre y la sección;
3. **foco:** campo que contiene el núcleo comunicativo;
4. **payload:** contenido conforme al shape y contrato;
5. **peso funcional:** declarado una vez en el glosario.

### 6.2 Línea ideática

Una línea ideática regular ocupa una sola línea física.

Excepciones:

- `cuerpo` puede ocupar un bloque delimitado;
- `bloque` puede ocupar un bloque delimitado.

Estas excepciones continúan representando una sola Idea.

### 6.3 Cierre ideático

Una Idea está estructuralmente cerrada cuando:

- su sigilo está declarado;
- todos los campos requeridos existen;
- el foco existe y no está vacío;
- los valores cumplen el contrato;
- el payload no necesita una regla externa para ser reconocido.

La calidad semántica del contenido no puede determinarse solo por gramática. El autor sigue siendo responsable de que el foco exprese una idea comprensible.

## 7. Estructura del documento

Un documento contiene exactamente:

1. `$0`, primero y único;
2. una declaración `$0:format`;
3. cero o más declaraciones meta;
4. una declaración por cada sigilo utilizado;
5. cero o más secciones `$1`, `$2`, …;
6. Ideas dentro de las secciones no cero.

Ejemplo mínimo:

```cortex
$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es}
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text",focus:content,desc:"Conocimiento verificable"}
$1:KNOW
KNW:codec{topic:"CORTEX",content:"Codec ideático lineal."}
```

## 8. `$0` — Glosario local

### 8.1 Función

`$0` es simultáneamente:

- bootstrap estructural;
- glosario local;
- contrato de reproducibilidad;
- mecanismo principal de extensibilidad;
- evidencia de portabilidad.

`$0` NO contiene estado operativo ordinario.

### 8.2 Posición

`$0` DEBE ser la primera sección y NO DEBE reaparecer.

### 8.3 Declaraciones permitidas

Dentro de `$0` existen dos formas:

```text
$0:nombre{...}          meta-declaración:KERNEL
SIGIL:etiqueta{...}     declaración de función ideática
```

Todas las declaraciones de `$0` DEBEN ocupar una línea física y usar `attrs`.

## 9. Declaración de formato

La primera meta-declaración normativa es:

```cortex
$0:format{cortex:0.1,encoding:UTF-8,language:es}
```

Requisitos:

- `cortex` DEBE ser `0.1`;
- `encoding` DEBE ser `UTF-8`;
- `language` PUEDE indicar idioma humano predominante;
- atributos adicionales DEBEN preservarse;
- solo puede existir una declaración `format`.

La versión se expresa dentro de CORTEX para conservar portabilidad. El parser conoce la forma meta fundamental, no una ontología de dominio.

## 10. Glosario fundamental

CORTEX posee un glosario fundamental pequeño. Define:

- `$0`;
- `format`;
- `enum_`;
- `micro_`;
- `namespace_`;
- `extension_`;
- claves de declaración de sigilo;
- shapes;
- tipos escalares;
- pesos `B`, `M`, `H`.

El glosario fundamental no contiene `KNW`, `OBJ`, `FCS`, `WRK`, `CNST` ni vocabulario de dominio.

El documento `fundamental-glossary-0.1.md` es parte normativa de esta entrega.

## 11. Sigilos

### 11.1 Naturaleza

Un sigilo representa una **función ideática**, no una clase privilegiada del runtime.

Ejemplos posibles definidos localmente:

```text
KNW  conocimiento
OBJ  objetivo
CNST restricción
RSK  riesgo
AUD  evidencia de auditoría
```

CORTEX no reserva estos significados.

### 11.2 Forma

Un sigilo local es:

- `!`; o
- una letra ASCII mayúscula seguida de hasta quince letras mayúsculas, dígitos o `_`.

Ejemplos válidos:

```text
KNW
OBJ
RE_1
!
```

### 11.3 Declaración

```cortex
KNW:knowledge{type:attrs,weight:B,fields:"topic:text|content:text|status:%state|evidence:text?",focus:content,desc:"Conocimiento verificable"}
```

Claves requeridas:

| Clave | Función |
|---|---|
| `type` | shape de todas las Ideas del sigilo |
| `weight` | peso funcional por defecto |
| `desc` | descripción humana suficiente |
| `fields` | contrato para `attrs` |
| `pos` | contrato para `attrs-pos` y `relacion` |
| `focus` | campo que contiene el núcleo de la idea |

`fields`, `pos` y `focus` dependen del shape.

### 11.4 Peso

El peso funcional expresa cuánto condiciona la lectura contextual de una función:

- `B` — base: información estable o descriptiva;
- `M` — material: información que puede alterar interpretación o acción;
- `H` — alta: objetivo, restricción, riesgo crítico o decisión dominante.

El peso se amortiza en `$0`. No se repite en cada Idea.

El peso no es automáticamente prioridad, riesgo, retención ni política de memoria. Un perfil puede definir esas nociones mediante campos explícitos.

### 11.5 Foco

`focus` identifica el campo que contiene la afirmación, acción, objetivo o relación principal.

Ejemplos:

```text
KNW → content
OBJ → goal
CNST → rule
RSK → risk
HDL → operation
REL → predicate
```

El foco DEBE ser requerido. Para `cuerpo` y `bloque`, el cuerpo completo es el foco implícito `$body`.

## 12. Anatomía superficial de una Idea

Toda Idea comienza con:

```text
symbol:name
```

- `symbol` declara la función;
- `name` identifica la Idea dentro de la sección y sigilo;
- el payload sigue inmediatamente.

Ejemplos:

```cortex
KNW:determinism{topic:"Determinismo",content:"Misma entrada produce igual AST."}
HDL:verify|validar el documento|current|archivo .cortex
REL:parser_ast|parser|produces|AST
```

No existe terminador `;` en CORTEX 0.1.

## 13. Shapes fundamentales

### 13.1 `attrs`

Forma:

```text
SIGIL:nombre{key:value,key:value}
```

Propiedades:

- una línea física;
- pares ordenados por el contrato;
- claves únicas;
- sin mapas anidados;
- valores escalares o listas planas;
- campos desconocidos prohibidos salvo `open:true`.

Ejemplo:

```cortex
OBJ:f2{goal:"Formalizar el formato.",status:current,evidence:"corpus"}
```

### 13.2 `attrs-pos`

Forma:

```text
SIGIL:nombre|valor|valor|valor
```

Los nombres y tipos de los campos se declaran una vez en `pos`.

Ejemplo:

```cortex
HDL:verify|validar estructura|current|archivo .cortex|sin inferencia
```

Propiedades:

- una línea física;
- `|` separa celdas;
- texto sin `|` puede escribirse sin comillas;
- una celda con `|` DEBE escribirse como string quoted;
- los campos opcionales solo pueden omitirse desde el final;
- los campos opcionales en un contrato posicional DEBERÍAN ser trailing.

### 13.3 `cuerpo`

Forma breve:

```cortex
TXT:purpose{CORTEX comunica una idea estructurada.}
```

Forma multilínea:

```cortex
TXT:purpose{
CORTEX elimina conectores repetitivos.
La estructura conserva el significado.
}
```

El cierre es una línea cuyo contenido, ignorando espacios horizontales, es exactamente `}`.

`cuerpo` contiene texto semántico. No se interpreta como attrs.

### 13.4 `bloque`

Usa la misma delimitación que `cuerpo`, pero preserva el contenido interno como verbatim.

```cortex
DIAG:flow{
@startuml
parser --> AST
@enduml
}
```

En Fase 2 el AST preserva el texto. Las reglas de newline canónico pertenecen a Fase 3.

### 13.5 `relacion`

Forma:

```text
SIGIL:nombre|source|predicate|target[|qualifier...]
```

El contrato DEBE contener al menos tres campos requeridos equivalentes a origen, predicado y destino.

Ejemplo:

```cortex
REL:parser_ast|parser|produces|AST|contrato del codec
```

Una relación expresa un vínculo explícito. No debe utilizarse para ocultar el contenido principal de Ideas que deberían ser autocontenidas.

## 14. Contratos

### 14.1 Propósito

El contrato hace reproducibles las líneas del mismo sigilo.

### 14.2 Sintaxis

```text
field[:type][?]
```

Los campos se separan mediante `|`.

Ejemplo:

```cortex
fields:"topic:text|content:text|status:%state|evidence:text?"
```

- `?` marca campo opcional;
- sin tipo, el tipo es `any`;
- `%name` referencia un enum local.
- El campo designado como **focus** del sigilo (§11.5) es el ÚNICO que se escribe como string quoted.
- Todos los demás campos se escriben como atoms, independientemente de su tipo en el contrato.
- El tipo `text` en el contrato informa la naturaleza semántica del campo, no impone un requisito sintáctico de comillas.

### 14.3 Tipos de contrato

| Tipo | Valor aceptado |
|---|---|
| `any` | cualquier scalar de CORTEX 0.1 |
| `text` | string quoted en attrs; texto de celda en positional |
| `atom` | atom bare |
| `int` | integer |
| `dec` | decimal exacto |
| `bool` | `true` o `false` |
| `null` | `null` |
| `list` | lista plana |
| `%enum` | atom perteneciente al enum declarado |

### 14.4 Orden

En `attrs`, los campos conocidos DEBEN aparecer en el orden del contrato. Los opcionales omitidos no alteran el orden relativo.

En `attrs-pos`, la posición es el contrato.

Esta regla no busca estética; reduce reinterpretación y hace reconocible el patrón.

### 14.5 Contrato cerrado y abierto

El valor por defecto es:

```text
open:false
```

Con `open:false`, todo campo debe estar declarado.

`open:true` permite campos adicionales preservables, pero reduce reproducibilidad y DEBERÍA reservarse para portadores de metadata o extensiones explícitas.

## 15. Enums

Forma:

```cortex
$0:enum_state{values:"current|planned|blocked|done"}
```

El nombre del enum es el sufijo después de `enum_`.

Un contrato lo referencia mediante `%state`.

Los valores:

- son atoms;
- deben ser únicos;
- mantienen orden declarado;
- no crean palabras reservadas globales.

## 16. Microtokens

Forma:

```cortex
$0:micro_cur{expand:current}
```

El token `cur` se expande a `current` únicamente cuando aparece como valor atom.

Los microtokens:

- no se aplican a sigilos;
- no se aplican a nombres;
- no se aplican a claves;
- no operan dentro de strings;
- deben declararse localmente;
- se preservan como lexema de fuente cuando el AST lo soporte;
- no pueden ejecutar funciones.

Los microtokens son compresión lingüística declarativa, no macros.

## 17. Scalars

### 17.1 String

Se delimita con `"`.

Escapes mínimos:

```text
\\" \\\\ \\n \\r \\t \\b \\f \\uXXXX
```

El string quoted se usa exclusivamente para el campo **focus** del sigilo y para contenido textual en metadata o extensiones. Los valores en campos no-foco son atoms y no llevan comillas.

### 17.2 Atom

Un atom es un valor bare compacto y no contiene espacios.

Gramática formal:
```text
atom = ALPHA / "_" / (ALPHA / "_" 0*31 (ALPHA / DIGIT / "_" / "." / "/" / ":" / "-"))
```

Un atom:
- Comienza con letra ASCII mayúscula/minúscula o `_`
- Continúa con letras, dígitos, `_`, `.`, `/`, `:`, `-`
- Máximo 32 caracteres
- No contiene espacios
- No comienza con dígito

Un atom que no cumpla estas reglas DEBE escribirse como string quoted o el parser debe emitir `L010_INVALID_ATOM`.

Ejemplos:

```text
current
blocking
cortex.core/parser
KNW:ast
$2:OBJ:release:DATA
```

Los atoms no adquieren significado global. Su semántica proviene del contrato, enum, microtoken o contenido local.

### 17.3 Integer

```text
0
3
-3
```

No se permiten `+`, exponentes ni ceros iniciales no necesarios.

### 17.4 Decimal

```text
0.75
-0.25
```

El AST conserva su representación decimal exacta como texto. No debe forzarse a float binario.

### 17.5 Boolean

```text
true
false
```

### 17.6 Null

```text
null
```

### 17.7 Lista

```text
[portable,denso,"texto humano",3,true]
```

Las listas son ordenadas y planas. CORTEX 0.1 no permite listas anidadas ni mapas dentro de listas.

## 18. Secciones

Forma:

```text
$1:DATA
$2: Título humano opcional:DATA
```

Para evitar colisión con meta-declaraciones, un título requiere al menos un espacio después de `:`.

Las secciones:

- organizan lectura y selección;
- preservan orden;
- no declaran semántica heredada;
- no reemplazan datos requeridos en las Ideas.

`$0` está reservado al glosario. Las demás secciones usan enteros positivos.

## 19. Identidad y direccionamiento

### 19.1 Dirección local

La dirección local de una Idea es:

```text
$section:symbol:name
```

Ejemplo:

```text
$2:KNW:determinism:KNOW
```

Debe ser única dentro del documento.

### 19.2 Identidad durable

La dirección local no constituye identidad durable entre documentos, revisiones o movimientos de sección.

Una identidad durable PUEDE declararse mediante un campo de perfil o extensión, por ejemplo `stable_id`, pero no forma parte obligatoria del Core 0.1.

Esta separación evita que una decisión editorial de sección se convierta en identidad histórica.

### 19.3 Selectores como atoms

Un selector puede aparecer como atom:

```text
KNW:ast
$2:KNW:ast:DATA
```

Fase 2 preserva el valor. La resolución avanzada y los selectores con wildcard pertenecen a tooling o especificaciones posteriores.

## 20. Namespaces

### 20.1 Objetivo

Los namespaces evitan colisiones sin obligar a repetir prefijos en todas las líneas.

### 20.2 Declaración

```cortex
$0:namespace_agent{id:agent,version:1.0,required:false}
```

### 20.3 Uso compacto

Un sigilo local puede declarar su namespace:

```cortex
FCS:focus{type:attrs,weight:H,fields:"what:text|status:atom",focus:what,desc:"Foco",namespace:agent}
```

Las Ideas continúan usando:

```cortex
FCS:primary{what:"Formalizar el codec.",status:current}
```

El AST puede derivar `agent::FCS` sin imponerlo a cada línea.

### 20.4 Uso calificado

Cuando sea necesario, el sigilo superficial puede ser calificado:

```cortex
agent::FCS:focus{type:attrs,weight:H,fields:"what:text",focus:what,desc:"Foco"}
$1:DATA
agent::FCS:primary{what:"Objetivo"}
```

Un documento debe utilizar consistentemente la forma declarada.

## 21. Extensiones

### 21.1 Principio

Una extensión agrega contratos o semántica, no gramática.

### 21.2 Declaración

```cortex
$0:extension_trace{namespace:trace,id:provenance,version:0.1,required:false,desc:"Procedencia opcional"}
```

Campos requeridos:

- `namespace`;
- `id`;
- `version`;
- `required`.

### 21.3 Autocontención

Aunque una extensión esté declarada, todo sigilo que use debe conservar una declaración estructural local suficiente para parsear su shape y contrato.

### 21.4 Extensión desconocida

- Si `required:false`, un consumidor puede preservar el documento y declarar interpretación parcial.
- Si `required:true`, un consumidor que no soporte la extensión debe emitir error de interpretación y no declarar éxito completo.
- En ningún caso puede descartarse información silenciosamente.

## 22. Comentarios

Un comentario comienza con `#` después de espacios horizontales y ocupa una línea completa.

```cortex
# Esta línea no altera el AST semántico.
```

CORTEX 0.1 no define comentarios inline.

Los comentarios no forman parte del AST semántico. Source preservation pertenece a Fase 3.

## 23. Unicode y texto

Requisitos:

- entrada UTF-8 válida;
- sin BOM;
- LF como newline normativo de procesamiento;
- CRLF debe normalizarse a LF durante lectura;
- caracteres de control prohibidos salvo TAB y newline donde corresponda;
- strings admiten Unicode;
- sigilos, claves, contratos y nombres estructurales usan el subconjunto ASCII definido;
- contenido humano puede usar Unicode completo.

La forma canónica NFC y las reglas exactas de emisión pertenecen a Fase 3. Un parser debe preservar el contenido lógico sin sustitución silenciosa.

## 24. Procesamiento en tres pasos

CORTEX se procesa determinísticamente:

### Paso 1 — Bootstrap

1. decodificar UTF-8;
2. reconocer `$0`;
3. leer `$0:format`;
4. construir glosario, enums, microtokens, namespaces y extensiones;
5. validar contratos.

**Resultado:** `glossary-valid` o error. Un glosario inválido BLOQUEA todo procesamiento posterior.

### Paso 2 — Glossary-valid

6. Verificar coherencia del glosario:
   - Cada sigilo usado tiene declaración en $0
   - Los contratos referencian enums existentes
   - Los microtokens referencian atoms existentes
   - Los namespaces referencian declaraciones de namespace
   - Las extensiones required están soportadas o bloquean

**Resultado:** `glossary-valid` o error específico (códigos G###). Un error en este paso impide alcanzar `structure-valid`.

### Paso 3 — Ideas

1. reconocer sección;
2. reconocer `symbol:name`;
3. resolver el sigilo en el glosario;
4. seleccionar shape;
5. parsear payload;
6. expandir microtokens;
7. validar contrato, foco y dirección local;
8. producir AST o diagnostics.

El procesamiento en dos pasos no requiere inferencia. El propio documento transporta las reglas.

## 25. Niveles de resultado

Una implementación debe distinguir:

### 25.1 `syntax-valid`

La superficie cumple la gramática. El parser reconoce tokens, secciones y estructura superficial.

### 25.2 `glossary-valid`

`$0` es completo y coherente:
- Formato válido (`cortex:0.1`, `encoding:UTF-8`)
- Todos los sigilos usados están declarados
- Los contratos referencian enums y tipos existentes
- No hay contradicciones entre $0 y la gramática base

Un documento `syntax-valid` pero `glossary-invalid` no puede procesar Ideas correctamente.

### 25.3 `structure-valid`

El glosario, shapes, contratos, scalars y direcciones son válidos. Las Ideas cumplen los contratos declarados en `$0`.

### 25.4 `interpretation-complete`

Todas las extensiones requeridas y reglas declaradas son soportadas.

Un documento puede ser sintácticamente parseable y no alcanzar interpretación completa.

## 26. AST normativo

El esquema `schemas/ast-schema.json` es parte de Fase 2.

### 26.1 Principios

El AST:

- representa Ideas, no objetos genéricos sin función;
- conserva orden de secciones e Ideas;
- conserva orden contractual de attrs;
- conserva lexemas de microtokens;
- conserva representación decimal exacta;
- distingue `cuerpo` y `bloque`;
- conserva declaraciones de extensión;
- deriva función, peso y foco desde `$0`;
- no incorpora runtime, learning ni perfiles de agente.

### 26.2 Neutralidad

El AST conoce `SymbolDefinition` e `Idea`. No conoce de manera privilegiada `KNW`, `OBJ`, `FCS`, `CNST` ni otros sigilos.

### 26.3 Orden

En Fase 2:

- orden de secciones: preservado y comunicativamente significativo;
- orden de Ideas: preservado y comunicativamente significativo;
- orden de listas: significativo;
- orden de fields: definido por contrato;
- orden de declaraciones: preservado;
- orden canónico final: pendiente de Fase 3.

## 27. Diagnostics

Toda no conformidad debe producir al menos:

- código estable;
- severidad;
- línea y columna;
- mensaje accionable.

El catálogo normativo está en `spec/errors.md` y el esquema en `schemas/diagnostic-schema.json`.

Una implementación puede agregar diagnostics, pero no omitir códigos obligatorios del corpus.

## 28. Reversibilidad futura con HCORTEX

Fase 2 establece estas garantías preparatorias:

1. todo sigilo posee descripción y función;
2. todo shape es explícito en `$0`;
3. `attrs` y `attrs-pos` poseen nombres de campo;
4. `cuerpo` y `bloque` están diferenciados;
5. `relacion` posee contrato dirigido;
6. orden y lexemas relevantes se conservan;
7. extensiones no se descartan.

Fase 4 determinará render y compile. VIEW no es necesario para la reversibilidad base; podrá existir como extensión de presentación especializada.

## 29. Seguridad y límites de recursos

Una implementación DEBE ofrecer límites configurables para:

- bytes de documento;
- número de secciones;
- número de sigilos;
- número de Ideas;
- longitud de línea;
- longitud de string;
- tamaño de cuerpo y bloque;
- número de fields y cells;
- tamaño de listas.

Exceder un límite debe emitir diagnóstico. No debe truncarse silenciosamente.

Los valores específicos son implementation-defined durante Draft 0.1 y no pueden alterar documentos dentro de los límites publicados por la implementación.

## 30. Compatibilidad con el formato experimental

CORTEX 0.1 preserva el ADN superficial del formato original:

```text
$0:KERNEL
SIGIL:meaning{...}
$N
SIGIL:name{...}
SIGIL:name|...|...
```

Evoluciones intencionales:

- `$0:format` obligatorio;
- contratos explícitos para `attrs` además de `attrs-pos`;
- `focus` obligatorio;
- `weight` neutral reemplaza dependencias cognitivas heredadas;
- tipos de fields explícitos;
- namespaces y extensiones formalizados;
- diagnostics estables;
- AST ideático neutral.

No se promete compatibilidad byte a byte con dialectos experimentales. La migración debe conservar el original y producir mapping/loss report cuando corresponda.

## 31. Frontera con Fase 3

Fase 3 deberá definir, sobre este AST y no sobre borradores anteriores:

- quoting canónico;
- expansión o preservación canónica de microtokens;
- orden canónico del glosario;
- normalización Unicode NFC;
- números canónicos;
- whitespace y newline final;
- equivalencia estructural;
- canonical hash;
- source preservation.

Fase 3 NO debe cambiar la unidad ideática ni convertir el formato en serialización genérica.

## 32. Conformidad de parser parcial — Gate F2

Dos implementadores independientes deben poder, leyendo únicamente esta entrega:

1. aceptar los casos de `examples/valid`;
2. producir AST lógicamente equivalente al esperado;
3. rechazar `examples/invalid`;
4. emitir los códigos obligatorios;
5. no incorporar reglas específicas de sigilos de dominio.

La utilidad `tools/cortex01_validator.py` es no normativa y no satisface por sí sola la independencia del gate.

## 33. Invariantes normativas resumidas

```text
I1  $0 es primero, único y estructural.
I2  El documento transporta el vocabulario usado.
I3  Una línea regular expresa una Idea principal.
I4  Todo sigilo declara shape, weight, desc y foco aplicable.
I5  Todo sigilo estructurado declara un contrato reproducible.
I6  Las Ideas cumplen el mismo patrón de su sigilo.
I7  Las secciones organizan; no completan significado.
I8  Las extensiones amplían vocabulario, no gramática.
I9  No existe pérdida silenciosa.
I10 El Core no conoce ontologías de agente.
I11 El AST sirve al formato ideático.
I12 La representación conserva información para HCORTEX.
```

## 34. Estado del Draft

Esta entrega está lista para evaluación de Gate F2, no para claim de estándar final.

El gate continúa pendiente de dos implementaciones independientes y revisión de ambigüedad externa.
