# Limitaciones y deuda de paridad

## KPL-001 — Pérdida de atributos abiertos en HCORTEX table

**Severidad:** alta  
**Origen:** Python  
**Reproducido en Rust:** sí, para mantener paridad

Cuando un símbolo `attrs` declara `open:true`, C14N conserva campos extra. Sin embargo, `render_hcortex` usa exclusivamente el orden del contrato para producir la fila:

```text
fields: "topic:text|count:integer"
idea:   {topic:x,count:1,extra:z}
HCORTEX table: | x | 1 |
```

Al compilar HCORTEX, `extra:z` ya no existe. El fixture `examples/full.reference.json` conserva el diff exacto.

**Corrección correcta:** no debe parchearse solo en Rust. Requiere una decisión normativa sobre representación de extras, actualización sincronizada del renderer/compiler Python y Rust, y nuevos vectores de conformidad.

## KPL-002 — Mixed shapes degradan a prose

Una sección con shapes diferentes usa schema `prose`. Un `bloque` dentro de esa sección no recibe fenced block y puede degradarse a marcador sin payload durante render.

## KPL-003 — Secciones vacías no hacen roundtrip completo

El renderer emite el heading, pero omite un schema pair. El regex del compiler solo reconstruye secciones que poseen bloque emparejado.

## KPL-004 — Glosario HCORTEX tolerante

El compiler ignora silenciosamente declaraciones de símbolo inválidas dentro del bloque de glosario, porque Python captura `ParseError` y continúa. No produce diagnóstico específico.

## KPL-005 — Umbrales F3 codificados

El gate F3 exige `golden_pass >= 38` e `idempotence_pass == 40`, independientemente de la cantidad declarada por el manifiesto.

## KPL-006 — Parser no valida cardinalidad contractual de ideas

El parser confirma shape y delimitador, pero no comprueba todos los campos requeridos, duplicados, extras con `open:false` ni cantidad exacta de posiciones.

## Política

Estas limitaciones están documentadas, fijadas por pruebas y no se presentan como garantías inexistentes. Deben resolverse mediante una revisión de estándar o una versión `strict` explícita, nunca mediante pérdida silenciosa adicional.
