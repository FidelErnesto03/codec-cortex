# Modelo de diagnostics — CORTEX 0.1

**Document ID:** `CORTEX-ERRORS-0.1-001`  
**Status:** `normative-draft`

## 1. Contrato

Todo diagnostic normativo contiene:

```json
{
  "code": "I008_REQUIRED_FIELD_MISSING",
  "severity": "error",
  "span": {"line": 8, "column": 1},
  "message": "Falta campo requerido: content."
}
```

Los mensajes pueden traducirse. El código, severidad mínima y condición no deben cambiar dentro de CORTEX 0.1.

## 2. Severidades

| Severidad | Efecto |
|---|---|
| `error` | impide el nivel de conformidad afectado |
| `warning` | resultado utilizable con riesgo declarado |
| `info` | información sin no conformidad |

## 3. Familias

| Prefijo | Área |
|---|---|
| `L` | lexical y scalar |
| `S` | sintaxis superficial y secciones |
| `G` | glosario y contratos |
| `I` | Idea, shape y payload |
| `X` | extensiones |
| `U` | Unicode y codificación |

## 4. Catálogo normativo

### 4.1 Lexical

| Código | Condición | Recuperación mínima |
|---|---|---|
| `L001_INVALID_SYMBOL` | sigilo fuera de la forma permitida | corregir sigilo o namespace |
| `L002_INVALID_NAME` | nombre estructural inválido | usar identificador permitido |
| `L003_INVALID_KEY` | key inválida | usar lowercase ASCII y `_`/`-` |
| `L005_INVALID_STRING` | string o escape inválido | cerrar y escapar correctamente |
| `L006_EMPTY_VALUE` | valor attrs vacío | declarar scalar explícito |
| `L007_INVALID_LIST` | lista sin cierre o separadores inválidos | corregir `[...]` |
| `L008_NESTED_LIST` | lista anidada | aplanar o usar Ideas separadas |
| `L009_INVALID_NUMBER` | número no conforme | usar integer o decimal permitido |
| `L010_INVALID_ATOM` | atom inválido o texto attrs sin comillas | usar atom permitido o string |

### 4.2 Sintaxis

| Código | Condición | Recuperación mínima |
|---|---|---|
| `S001_EMPTY_DOCUMENT` | documento sin contenido | agregar `$0` y format |
| `S002_DUPLICATE_SECTION` | id de sección repetido | usar id único |
| `S003_INVALID_IDEA_HEAD` | falta `SIGIL:nombre` válido | corregir encabezado |
| `S004_MISSING_PAYLOAD` | Idea sin payload | agregar `{...}` o `|...` |
| `S005_CONTENT_OUTSIDE_SECTION` | contenido fuera de sección | mover bajo `$N` |
| `S006_INVALID_ATTRS` | attrs no separables o desbalanceados | corregir pares y delimitadores |

`S999_INTERNAL_PARSE_FAILURE` es reservado para fallos de implementación y nunca sustituye un código normativo conocido.

### 4.3 Glosario

| Código | Condición | Recuperación mínima |
|---|---|---|
| `G001_GLOSSARY_MISSING_OR_NOT_FIRST` | `$0` ausente o no primero | ubicar `$0` al inicio |
| `G002_GLOSSARY_REOPENED` | `$0` reaparece | consolidar glosario |
| `G003_MULTILINE_GLOSSARY_DECLARATION` | declaración de `$0` ocupa varias líneas | compactar a una línea |
| `G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS` | declaración no usa attrs | usar `{key:value}` |
| `G005_DUPLICATE_SYMBOL` | mismo sigilo declarado dos veces | consolidar contrato o renombrar alias |
| `G006_DUPLICATE_FORMAT` | más de un `$0:format` | conservar uno |
| `G007_UNSUPPORTED_VERSION` | `cortex` distinto de `0.1` | usar parser de la versión declarada |
| `G008_INVALID_CONTRACT` | contrato vacío o mal formado | corregir `field[:type][?]` |
| `G009_DUPLICATE_CONTRACT_FIELD` | field repetido | mantener una definición |
| `G010_FORMAT_REQUIRED` | falta `$0:format` | agregar declaración |
| `G011_ENCODING_REQUIRED` | encoding no es UTF-8 | convertir y declarar UTF-8 |
| `G012_INVALID_MICRO` | microtoken inválido o sin expansión | corregir token/expand |
| `G013_DUPLICATE_MICRO` | microtoken repetido | consolidar declaración |
| `G014_INVALID_ENUM` | enum vacío, duplicado o con values inválidos | corregir values |
| `G015_DUPLICATE_ENUM` | enum local repetido | consolidar declaración |
| `G016_SYMBOL_TYPE_REQUIRED` | sigilo sin `type` | declarar shape |
| `G017_UNKNOWN_SHAPE` | shape fuera del conjunto fundamental | usar shape válido o extensión fuera de gramática |
| `G018_SYMBOL_WEIGHT_REQUIRED` | sigilo sin `weight` | declarar B, M o H |
| `G019_INVALID_WEIGHT` | peso desconocido | usar B, M o H |
| `G020_SYMBOL_DESCRIPTION_REQUIRED` | sigilo sin `desc` | describir función ideática |
| `G021_ATTRS_CONTRACT_REQUIRED` | attrs sin `fields` | declarar contrato |
| `G022_POSITIONAL_CONTRACT_REQUIRED` | attrs-pos/relacion sin `pos` | declarar contrato |
| `G023_RELATION_CONTRACT_TOO_SHORT` | relación con menos de tres fields | declarar source, predicate, target |
| `G024_FOCUS_REQUIRED` | shape estructurado sin `focus` | declarar foco |
| `G025_UNKNOWN_FOCUS_FIELD` | focus no existe en contrato | corregir focus o contrato |
| `G026_UNKNOWN_ENUM_REFERENCE` | contrato referencia enum no declarado | declarar `$0:enum_*` |
| `G027_UNKNOWN_FIELD_TYPE` | tipo de field desconocido | usar tipo fundamental o `%enum` |
| `G028_DUPLICATE_QUALIFIED_SYMBOL` | namespace + sigilo declarados más de una vez | consolidar la declaración cualificada |

### 4.4 Ideas

| Código | Condición | Recuperación mínima |
|---|---|---|
| `I001_UNDECLARED_SYMBOL` | Idea usa sigilo ausente de `$0` | declarar el sigilo localmente |
| `I002_DUPLICATE_IDEA_ADDRESS` | dirección local repetida | cambiar name o sección |
| `I003_ATTRS_MUST_BE_ONE_LINE` | attrs distribuido en varias líneas | compactar la Idea |
| `I004_SHAPE_DELIMITER_MISMATCH` | delimitador no coincide con shape | usar braces o pipe correcto |
| `I005_UNKNOWN_FIELD` | field no declarado en contrato cerrado | declarar field o eliminarlo |
| `I006_DUPLICATE_FIELD` | field repetido en attrs | mantener un valor |
| `I007_FIELD_ORDER` | fields fuera del orden contractual | reordenar según `$0` |
| `I008_REQUIRED_FIELD_MISSING` | falta field requerido | agregarlo |
| `I009_FIELD_TYPE_MISMATCH` | scalar no cumple tipo | corregir literal o contrato |
| `I010_ENUM_VIOLATION` | atom fuera de enum | usar value declarado |
| `I011_PIPE_IDEA_MUST_BE_ONE_LINE` | attrs-pos/relacion multilínea | compactar a una línea |
| `I012_POSITIONAL_ARITY` | cells incompatibles con contrato | corregir aridad |
| `I013_RELATION_ARITY` | relación incompleta o excedida | cumplir contrato |
| `I014_UNCLOSED_BODY` | cuerpo/bloque sin cierre | agregar línea `}` |
| `I015_FOCUS_VALUE_MISSING` | payload no materializa focus | incluir field/cell de foco |
| `I016_EMPTY_FOCUS` | foco textual vacío | expresar la idea principal |

### 4.5 Extensiones

| Código | Condición | Recuperación mínima |
|---|---|---|
| `X001_INVALID_EXTENSION_DECLARATION` | falta namespace, id, version o required | completar declaración |
| `X002_REQUIRED_EXTENSION_UNSUPPORTED` | extensión requerida no soportada | instalar soporte o rechazar interpretación completa |

### 4.6 Unicode

| Código | Condición | Recuperación mínima |
|---|---|---|
| `U001_BOM_FORBIDDEN` | UTF-8 BOM presente | eliminar BOM |
| `U002_CONTROL_CHARACTER` | control no permitido | eliminar o escapar |

### 4.7 Glosario (glossary-valid)

| Código | Condición | Recuperación mínima |
|---|---|---|
| `G001_GLOSSARY_MISSING_OR_NOT_FIRST` | $0 ausente o no es la primera sección | agregar o mover $0 al inicio |
| `G002_FORMAT_REQUIRED` | falta $0:format con cortex y encoding | agregar declaración de formato |
| `G003_UNSUPPORTED_VERSION` | versión de cortex distinta de 0.1 | actualizar a 0.1 |
| `G004_DUPLICATE_SYMBOL` | mismo sigilo declarado más de una vez | eliminar duplicado |
| `G005_UNDECLARED_SYMBOL` | sigilo usado en Idea sin declaración en $0 | declarar sigilo en $0 |
| `G006_INVALID_CONTRACT` | fields/pos con sintaxis incorrecta | corregir contrato |
| `G007_DUPLICATE_CONTRACT_FIELD` | field duplicado en contrato | eliminar duplicado |
| `G008_CONTRACT_FIELD_TYPE_UNKNOWN` | tipo de campo no reconocido | usar tipo válido |
| `G009_ENUM_UNDECLARED` | contrato referencia enum inexistente | declarar enum |
| `G010_MICRO_UNDECLARED` | microtoken usado sin declaración | declarar en $0:micro_* |
| `G011_NAMESPACE_UNDECLARED` | namespace usado sin declaración | declarar en $0:namespace_* |
| `G012_EXTENSION_MISSING_FIELDS` | extensión sin namespace/id/version/required | completar campos obligatorios |
| `G013_DUPLICATE_META` | meta-declaración duplicada ($0:format, etc.) | eliminar duplicado |
| `G014_SHAPE_UNKNOWN` | shape declarado no es uno de los 5 válidos | usar attrs/attrs-pos/cuerpo/bloque/relacion |
| `G015_FOCUS_FIELD_NOT_IN_CONTRACT` | focus declarado no existe en fields/pos | corregir focus o agregar field |

## 5. Orden de prioridad

Cuando varias no conformidades se solapan, una implementación debería reportar primero:

1. decodificación y controles;
2. estructura de secciones;
3. glosario;
4. contrato;
5. Idea y payload;
6. interpretación de extensión.

Puede emitir más de un diagnostic si no inventa resultados derivados de una estructura no parseable.

## 6. Extensión del catálogo

Una implementación puede agregar códigos propios con prefijo de proveedor, pero:

- no puede reutilizar un código normativo con otra condición;
- no puede degradar un `error` normativo a warning;
- debe preservar los códigos requeridos por el corpus.
