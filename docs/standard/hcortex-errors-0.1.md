# HCORTEX Draft 0.1 — Diagnostics y pérdidas

**Document ID:** `HCORTEX-ERRORS-0.1-001`  
**Status:** `normative-draft`

## 1. Contrato

Todo error debe contener al menos:

```text
code
severity
message
location o structural path
```

No existe recuperación silenciosa en modo conforme.

## 2. Errores de documento

| Código | Severidad | Condición |
|---|---:|---|
| `H400` | error | falta metadata raíz HCORTEX |
| `H401` | error | JSON raíz inválido o versión no soportada |
| `H402` | error | modo distinto de `canonical` usado con compiler canónico |
| `H403` | error | encoding o CORTEX version contradictorios |
| `H404` | error | BOM o UTF-8 inválido |

## 3. Errores de glosario

| Código | Severidad | Condición |
|---|---:|---|
| `H410` | error | sección o tabla obligatoria ausente |
| `H411` | error | tabla Markdown mal formada |
| `H412` | error | encabezado de tabla incorrecto |
| `H413` | error | fila centinela mezclada con datos reales |
| `H414` | error | contrato de sigilo inválido |
| `H415` | error | sigilo, enum, namespace o extensión duplicados |
| `H416` | error | shape, peso o foco inválidos |
| `H417` | error | JSON de config de extensión inválido |

## 4. Errores de secciones e Ideas

| Código | Severidad | Condición |
|---|---:|---|
| `H420` | error | Idea fuera de una sección |
| `H421` | error | ID de sección inválido o duplicado |
| `H422` | error | orden estructural no representable |
| `H431` | error | JSON `cortex-entry` inválido |
| `H432` | error | metadata y encabezado visible contradictorios |
| `H433` | error | symbol no declarado |
| `H434` | error | etiqueta visible no coincide con glosario |
| `H435` | error | identidad local duplicada en la misma sección/sigilo |
| `H436` | error | namespace no declarado cuando es requerido |

## 5. Errores por shape

| Código | Severidad | Condición |
|---|---:|---|
| `H440` | error | tabla attrs ausente o con columnas incorrectas |
| `H441` | error | índice attrs no continuo |
| `H442` | error | campo duplicado, desconocido o fuera de contrato |
| `H443` | error | campo requerido ausente |
| `H444` | error | scalar incompatible con contrato |
| `H450` | error | tabla posicional ausente |
| `H451` | error | índice posicional no continuo |
| `H452` | error | campo posicional no coincide con contrato |
| `H453` | error | opcional intermedio omitido |
| `H460` | error | fence `hcortex-text` ausente o incorrecto |
| `H461` | error | fence `cortex-block` ausente, incorrecto o no cerrado |
| `H462` | error | bloque sin `media_type` |
| `H470` | error | relación con menos de tres celdas |
| `H471` | error | referencia local no resuelta |
| `H472` | error | referencia de identidad mal formada |

## 6. Canonicalidad y edición

| Código | Severidad | Condición |
|---|---:|---|
| `H480` | error | documento parseable pero no canónico en modo estricto |
| `H481` | error | payload oculto o copia de AST detectada |
| `H482` | error | HTML activo o directiva ejecutable en zona estructural |
| `H483` | error | metadata obligatoria eliminada |
| `H484` | error | cambio de shape sin actualización coherente de glosario |
| `H485` | error | READABLE usado como entrada canónica |
| `H490` | error | límite de recursos excedido |

## 7. Códigos de pérdida READABLE

| Código | Tipo | Significado |
|---|---:|---|
| `L410_GLOSSARY_COLLAPSED` | loss | glosario completo no emitido |
| `L411_MACHINE_METADATA_REMOVED` | loss | identidad de reconstrucción omitida |
| `L412_TYPE_INFORMATION_REMOVED` | loss | tipos o lexemas no reconstruibles |
| `L413_EXTENSION_DETAIL_REMOVED` | loss | extensión reducida para presentación |
| `L414_ORDER_COLLAPSED` | loss | orden significativo alterado o agrupado |
| `L415_VIEW_PROJECTION` | loss | VIEW produjo una proyección no equivalente |
| `W412_DISPLAY_NORMALIZED` | warning | valor normalizado solo para lectura |
| `W413_NONCANONICAL_LAYOUT` | warning | input tolerado pero renderer lo reescribirá |

## 8. Reparación

Una propuesta de reparación debe:

1. conservar el input original;
2. generar patch explícito;
3. identificar toda inferencia;
4. no convertir valores desconocidos en hechos certificados;
5. volver a ejecutar roundtrip antes de declarar éxito.
