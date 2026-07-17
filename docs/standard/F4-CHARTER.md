# F4-CHARTER — Carta de Navegación HCORTEX

**Document ID:** `CORTEX-F4-CHARTER-001`
**Status:** `active`
**Date:** `2026-07-17`

## 1. Visión

CORTEX es un **lenguaje de máquina para modelos de lenguaje**. Los LLMs lo leen y comprenden directamente — sin parser, sin AST, sin validación formal. HCORTEX es su **representación humana**, transformada mediante reglas deterministas según schemas explícitos.

El codec reversible:

```text
CORTEX (IA) ←──→ HCORTEX (humano)
```

## 2. Los 9 pilares

| # | Pilar | Descripción |
|---|---|---|
| 1 | `$0` = glosario | Siempre primero. No se renderiza en HCORTEX. Solo para IA. |
| 2 | Secciones | `$N:Título` → `## §N:Título`. Por patrón, sin schema. |
| 3 | Dos niveles de parseo | Nivel sección (patrón) + nivel Idea (contrato en $0). |
| 4 | Estructura única | Cada sigilo define un contrato fijo. Innegociable. |
| 5 | Schema en `$0` | Campo obligatorio del contrato. 7 esquemas fijos y cerrados. |
| 6 | Sigilo = registro | Una fila, un item, un bloque. No una tabla completa. |
| 7 | Parser de una línea | Verifica conformidad contra contrato. No interpreta. |
| 8 | Roundtrip determinista | Sin inferencia. Schema explícito → transformación directa. |
| 9 | Encabezado HCORTEX | `<!-- HCORTEX v=0.1 t=canonical k=brain -->` |

## 3. Los 7 esquemas de visualización

| Schema | Shape CORTEX | Un sigilo es | Reversible |
|---|---|---|---|
| `table` | attrs / attrs-pos | Fila con columnas | ✅ |
| `list` | attrs / attrs-pos | Item de lista | ✅ |
| `puml` | bloque | Diagrama PlantUML | ✅ |
| `code` | bloque | Código fuente | ✅ |
| `body` | cuerpo | Párrafo | ✅ |
| `prosa` | cuerpo | Texto libre (red de seguridad) | ✅ |
| `rel` | relacion | Relación dirigida | ✅ |

## 4. Principios rectores

1. **CORTEX es el formato nativo de la IA.** Los modelos de lenguaje leen CORTEX sin parseo.
2. **HCORTEX existe para el humano.** Transforma Ideas en representaciones visuales sin pérdida.
3. **El roundtrip es determinista.** CORTEX→HCORTEX→CORTEX produce el mismo significado.
4. **El transformador no interpreta.** Aplica reglas según schema. Sin inferencia.
5. **`$0` no se renderiza.** El glosario es exclusivo para la IA.

## 5. Criterios de éxito F4

- ✅ Especificación HCORTEX completa con 9 pilares
- ⬜ Transformador HCORTEX implementado con 7 schemas
- ⬜ Corpus HCORTEX con schemas explícitos generado
- ⬜ Roundtrip verificado: 40/40 reversible + idempotente
- ⬜ Segunda implementación independiente del transformador
