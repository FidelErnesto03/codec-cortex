<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MPL-2.0 -->

# CODEC-CORTEX — Referencia de Directivas VIEW

> **NOTA DE ESTADO:** A v0.4.1 el SKILL.md canónico contiene 44 directivas VIEW cubriendo las 14 secciones. Este documento resume los tipos de VIEW, sus targets y estrategias de reversión.

---

## 1. Qué es una directiva VIEW

Una directiva VIEW es un contrato declarativo que mapea una sección o entrada de `.cortex` a un tipo de renderizado HCORTEX específico. Vive en `$13` del `skill/cortex/SKILL.md` canónico.

```cortex
VIEW:<nombre>{kind:"<tipo_render>",target:"<selector>",reverse:"<estrategia>",status:cur,title:"<titulo_visible>"}
```

**Campos:**

| Campo | Descripción |
|-------|-------------|
| `name` | Identificador único del VIEW |
| `kind` | Tipo de render HCORTEX: `table`, `kv_table`, `prose`, `puml`, `numbered_list`, `callout` |
| `target` | Selector CORTEX: `$N:SIGIL:name`, `$N:SIGIL:*`, `$N:NAME` |
| `reverse` | Estrategia de reversión: `rows_to_entries`, `row_to_attrs`, `body_to_cuerpo`, `verbatim_to_bloque`, `items_to_ordered_entries`, `callout_to_risk` |
| `status` | `cur` (current), `specification`, `pln` (planned) |
| `title` | Título de sección legible en HCORTEX |
| `fields` (opcional) | Lista explícita de campos para targets heterogéneos |
| `preserve` (opcional) | `verbatim` para bloques PUML |

---

## 2. Tipos de render

| Kind | Genera | Ejemplo |
|------|--------|---------|
| `table` | Tabla Markdown estándar | Lista de sigilos con columnas |
| `kv_table` | Tabla clave-valor | `\| Campo \| Valor \|` |
| `prose` | Párrafo o bloque de prosa | Descripciones de axiomas |
| `puml` | Bloque PUML literales | Diagramas de arquitectura |
| `numbered_list` | Lista ordenada | Secuencias de reglas |
| `callout` | Cita destacada | Declaraciones de riesgo |

---

## 3. Estrategias de reversión

| Estrategia | Operación inversa | Se usa para |
|------------|-------------------|-------------|
| `rows_to_entries` | Cada fila de tabla → una entrada de sigilo | Tablas genéricas de sigilos |
| `row_to_attrs` | Tabla clave-valor → pares attr | Identidad, alcance, enums |
| `body_to_cuerpo` | Bloque de prosa → entrada cuerpo | Descripciones, axiomas |
| `verbatim_to_bloque` | Bloque de código → entrada bloque | Diagramas PUML |
| `items_to_ordered_entries` | Elementos de lista → entradas ordenadas | Secuencias de reglas |
| `callout_to_risk` | Cita destacada → entrada de riesgo | Declaraciones de riesgo |

---

## 4. Resumen de cobertura VIEW

| Sección | VIEWs | Tipos usados |
|:-------:|:-----:|--------------|
| $0 Glosario | 9 | table, kv_table |
| $1 Identidad | 4 | kv_table, table |
| $2 Propósito | 5 | prose, table |
| $3 Handlers | 1 | table |
| $4 Reglas | 1 | numbered_list |
| $5 Constraints | 3 | table, callout |
| $6 Diagramas | 1 | puml |
| $7 Contratos | 1 | table |
| $8 Survive | 2 | kv_table, table |
| $9 Perfiles | 5 | table, prose |
| $10 Degradación | 2 | numbered_list, prose |
| $11 HCORTEX | 5 | table, prose, kv_table |
| $12 CORTEX-OUT | 3 | table, prose, kv_table |
| $13 VIEWS | 2 | table |
| **Total** | **44** | — |

---

## 5. Directivas VIEW seleccionadas

| VIEW | Sección | Kind | Target | Reverse |
|------|:-------:|:----:|--------|---------|
| `sigilos_canonicos` | $0 | table | `$0:canonical_sigils` | rows_to_entries |
| `declaraciones_tipo` | $0 | kv_table | `$0:type_decls` | row_to_attrs |
| `microtokens_decl` | $0 | table | `$0:microtokens` | rows_to_entries |
| `identidad_proyecto` | $1 | kv_table | `$1:IDN:project` | row_to_attrs |
| `handlers` | $3 | table | `$3:HDL:*` | rows_to_entries |
| `reglas_normalizacion` | $4 | numbered_list | `$4:!:*` | items_to_ordered_entries |
| `diagramas` | $6 | puml | `$6:DIAG:*` | verbatim_to_bloque |
| `reglas_survive` | $8 | kv_table | `$8:!:*` | row_to_attrs |
| `modos_hcortex` | $11 | table | `$11:KNW:hc_modes` | rows_to_entries |
| `definicion_out` | $12 | prose | `$12:DESC:out_def` | body_to_cuerpo |
| `bloques_out` | $12 | table | `$12:KNW:out_blocks` | rows_to_entries |

> **Referencia completa:** El conjunto completo de 44 directivas VIEW está definido en `skill/cortex/SKILL.md` §13.
> **Ver también:** [`docs/en/specs/view-directives.md`](../en/specs/view-directives.md) para la versión en inglés.
