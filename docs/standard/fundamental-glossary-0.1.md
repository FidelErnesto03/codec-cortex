# Glosario fundamental CORTEX 0.1

**Document ID:** `CORTEX-FUNDAMENTAL-GLOSSARY-0.1-001`  
**Status:** `normative-draft`  

## 1. Propósito

Este glosario define únicamente los elementos necesarios para que `$0` pueda describir el lenguaje local. No define vocabulario de agentes, skills, proyectos ni gobierno.

## 2. Meta-sección

| Elemento | Significado |
|---|---|
| `$0` | glosario local, primero y único |
| `$N` | sección ordinaria con entero positivo |
| `$N: Título` | sección ordinaria con título organizativo |

## 3. Meta-declaraciones

| Patrón | Función |
|---|---|
| `$0:format{...}` | versión, encoding y metadata documental |
| `$0:enum_<name>{values:"..."}` | enum local |
| `$0:micro_<token>{expand:...}` | microtoken local |
| `$0:namespace_<alias>{...}` | namespace declarado |
| `$0:extension_<name>{...}` | extensión declarada |
| `$0:<name>{...}` | meta-declaración preservable no fundamental |

## 4. Claves fundamentales de declaración de sigilo

| Clave | Requisito | Significado |
|---|---|---|
| `type` | obligatorio | shape de Ideas |
| `weight` | obligatorio | `B`, `M` o `H` |
| `desc` | obligatorio | descripción humana |
| `fields` | obligatorio para attrs | contrato key/value |
| `pos` | obligatorio para attrs-pos y relacion | contrato posicional |
| `focus` | obligatorio para shapes estructurados | núcleo comunicativo |
| `open` | opcional, default false | admite fields adicionales |
| `namespace` | opcional | identidad namespace del sigilo |
| `version` | opcional | versión del vocabulario |

Claves adicionales se preservan. Una extensión puede atribuirles semántica, pero no alterar la gramática.

## 5. Shapes

```text
attrs
attrs-pos
cuerpo
bloque
relacion
```

## 6. Tipos de fields

```text
any
text
atom
int
dec
bool
null
list
%<enum-local>
```

## 7. Peso funcional

| Token | Lectura |
|---|---|
| `B` | base |
| `M` | material |
| `H` | alta |

El peso es una propiedad de función amortizada en el glosario. No implica por sí mismo política operacional.

## 8. Scalars fundamentales

```text
string
atom
integer
decimal
boolean
null
flat-list
```

## 9. Delimitadores

| Delimitador | Función |
|---|---|
| `:` | función/nombre o key/value |
| `{...}` | attrs o cuerpo breve según glosario |
| `|` | cells posicionales |
| `[...]` | lista plana |
| `"..."` | string |
| `#` | comentario de línea completa |
| `::` | calificación opcional de namespace |

## 10. Prohibiciones

El glosario fundamental no puede incorporar por antecedente histórico:

- sigilos de dominio;
- políticas de runtime;
- learning;
- survive;
- P-levels;
- VIEW obligatorio;
- clases brain/skill/package;
- semántica ArqUX.

Todos estos elementos siguen siendo expresables mediante glosarios, perfiles o extensiones externas.
