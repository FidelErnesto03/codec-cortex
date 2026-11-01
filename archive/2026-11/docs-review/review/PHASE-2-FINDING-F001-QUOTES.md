# Hallazgo F2-F001 — Comillas forzosas en campos tipo `text`

**Severidad propuesta:** MAJOR
**Fuente:** Experimento de integración BLP-002 + análisis de misión CORTEX
**Fecha:** 2026-07-17
**Autor:** Alfred (governor CODEC-CORTEX), aprobado por Arquitecto

## Descripción

La especificación CORTEX 0.1 REAL define que los campos de tipo `text` en el contrato requieren comillas dobles en su valor:

```cortex
CRIT:C01{id:"C01", ...}   # id es text → comillas forzosas
```

Sin embargo, el diseño ideático de CORTEX contempla que **solo el foco** (el campo que contiene la idea principal del sigilo) contiene texto con espacios. Todos los demás campos — identificadores, tipos, severidades, referencias — son atoms compactos.

## Manifestación

Durante la construcción de `mission.cortex`, tres correcciones fueron necesarias porque el validador rechazó atoms en campos `text`:

| Línea | Valor | Corrección | ¿Era necesario? |
|---|---|---|---|
| `id:BLP-003` | Guión en valor | `id:"BLP-003"` | Sí (el guión rompe el atom) |
| `id:C01` | Atom sin espacios | `id:"C01"` | No |
| `target:90pct` | Empieza con dígito | debate quotes vs atom | No |

## Análisis

### Regla actual (spec §14.2)

```
type: text  → requiere comillas dobles
type: atom  → valor bare
```

### Problema

Esta regla trata todos los campos `text` como si fueran contenido libre. Pero en la práctica CORTEX 0.1, los únicos campos que realmente contienen texto libre son **el foco** (`focus`) de cada sigilo. Los demás campos son estructurales: ids, referencias, enums, tipos.

### Propuesta

**Solo el foco lleva comillas.** Todos los demás campos son atoms:

```cortex
# Actual (spec vigente):
CRIT:C01{id:"C01",desc:"Parser accepts >= 36/40...",target:pct90}

# Propuesto:
CRIT:C01{id:C01,desc:"Parser accepts >= 36/40...",target:pct90}
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ ← foco, lleva comillas
```

### Regla propuesta

```
El campo designado como 'focus' en el sigilo (spec §11.5):
  → DEBE ser string quoted
  → Es el ÚNICO campo textual

Todos los demás campos del contrato:
  → Son atoms
  → Solo necesitan comillas si contienen caracteres prohibidos en atoms
  → El tipo 'text' en el contrato define el foco, no un requisito sintáctico
```

### Impacto

| Dimensión | Actual | Propuesto |
|---|---|---|
| Número de comillas | Por campo `text` | Solo foco |
| Complejidad del parser | Validar tipo+contenido | Validar posición (focus) |
| Densidad | Menor | Mayor |
| Consistencia con D-007 (bare atoms) | Inconsistente | Consistente |
| Cambio en spec | — | §14.2, §17.1 |
| Cambio en validador | — | Eliminar validación I009 para campos no-foco |

## Estado

Hallazgo registrado antes de completar el experimento. Si los agentes Rust, Go y Bash confirman esta fricción (lo harán), se eleva a recomendación de corrección de la especificación.

**Acción propuesta:** BLP de corrección de CORTEX-SPEC-0.1.md §14.2 y actualización del validador `cortex01_validator.py` para relajar la regla de comillas en campos no-foco, o crear CEP formal.
