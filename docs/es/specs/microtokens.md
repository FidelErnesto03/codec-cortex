<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

# CODEC-CORTEX — Referencia de Microtokens

> **NOTA DE ESTADO:** A v0.3.7 el glosario canónico en `skill/cortex/SKILL.md` $0 define 30+ microtokens — abreviaturas compactas que se expanden a términos completos durante el parseo CORTEX. DEBEN registrarse en $0 antes del primer uso y NO DEBEN expandirse dentro de palabras o bloques verbatim.

---

## 1. Qué son los microtokens

Los microtokens son abreviaturas de uno o varios caracteres declaradas en `$0` que se expanden a términos completos durante el parseo CORTEX. Reducen el conteo de tokens mientras preservan la semántica.

**Formato de declaración:**
```cortex
$0:micro_<id>{expand:<termino_completo>}
```

**Regla de expansión:** Los microtokens se expanden solo si están delimitados por: espacio, `|`, `,`, `{}`, salto de línea, inicio-de-valor, fin-de-valor. NO DEBEN expandirse dentro de palabras (ej. `param_d1` NO expande `d1`).

---

## 2. Microtokens de estado

| Token | Expansión | Propósito |
|:-----:|:---------:|-----------|
| `cur` | `current` | Implementado y verificado |
| `pln` | `planned` | Diseñado para versión futura |
| `fut` | `future` | Visión más allá del alcance actual |
| `blk` | `blocked` | Bloqueado por dependencia externa |

---

## 3. Microtokens de nivel de supervivencia

| Token | Expansión | Propósito |
|:-----:|:---------:|-----------|
| `min` | `minimum` | Sobrevive bajo perfil CORTEX-MIN |
| `rec` | `recovery` | Sobrevive bajo CORTEX-RECOVERY |
| `wrk` | `work` | Sobrevive bajo CORTEX-WORK |
| `full` | `full` | Sobrevive bajo todos los perfiles |

---

## 4. Microtokens de resultado

| Token | Expansión | Propósito |
|:-----:|:---------:|-----------|
| `ok` | `success` | Operación exitosa |
| `fail` | `failure` | Operación fallida |
| `part` | `partial` | Parcialmente completado |

---

## 5. Microtokens de operación

| Token | Expansión | Categoría |
|:-----:|:---------:|:---------:|
| `d1` | `decode` | Codec central |
| `d2` | `detect` | Motor de maduración |
| `d3` | `decay` | Motor de maduración |
| `c1` | `.cortex` | Referencia de formato |
| `c2` | `HCORTEX` | Referencia de formato |
| `v1` | `validate` | Verificación |
| `v2` | `verify` | Verificación |

---

## 6. Microtokens de acción

| Token | Expansión | Categoría |
|:-----:|:---------:|:---------:|
| `a1` | `file` | Operando |
| `a2` | `files` | Operando (plural) |
| `s1` | `sigil` | Elemento del protocolo |
| `s2` | `section` | Elemento estructural |
| `h1` | `handler` | Handler operacional |
| `x1` | `extract` | Operación de diagrama |
| `x2` | `list` | Operación de listado |
| `m1` | `modify` | Operación de mutación |
| `m2` | `add` | Operación de creación |
| `r1` | `remove` | Operación de eliminación |
| `p1` | `promote` | Operación de maduración |
| `f1` | `format` | Operación de formateo |
| `t1` | `structure` | Operación estructural |

---

## 7. Reglas de expansión

| Regla | Descripción |
|-------|-------------|
| Expansión por delimitador | Los microtokens se expanden solo cuando están rodeados por delimitadores (espacio, `|`, `,`, `{}`, nueva línea, bordes de valor) |
| Sin expansión dentro de palabras | `param_d1` NO expande `d1`; `d1` standalone sí |
| Protección dentro de DIAG | Los microtokens NO DEBEN expandirse dentro de bloques PUML literales |
| Registro requerido | Los nuevos microtokens DEBEN declararse en $0 antes del primer uso |
| Extensión de glosario | Los nuevos microtokens siguen la misma regla de registro que los sigilos |

---

## 8. Formato de registro en `$0`

```cortex
$0:micro_<id>{expand:<termino_completo>}
```

Donde:
- `<id>` es un token alfanumérico corto (1–3 caracteres preferido)
- `<termino_completo>` es la expansión

> **Ver también:** [`docs/en/specs/microtokens.md`](../en/specs/microtokens.md) para la versión en inglés.
