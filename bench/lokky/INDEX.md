# bench/lokky — puerta única · ejecución externa BLP-003 + escenarios C4/C5

**Ejecutor:** Lokky (voz NEX, agente externo a ArqUX) · **Fecha:** 2026-11-03
**Regla:** todo aquí es reproducible; lo que requiere transporte `cmd` queda
como celda lista para Alfred — nada está simulado donde el diseño exige LLM.

## Estado del programa

| Pieza | Dónde | Estado |
|---|---|---|
| Celdas BLP-003 (480 = 2 mod × 6 fmt × 8Q × R5) | `cells/cells.json` | **listas para materializar** |
| Sellado corpus `formats/` | `seal/SHA256SUMS` | hecho — `sha256sum -c` |
| Conteo tokens o200k | `tokens/token-accounting.json` | hecho (ver tabla abajo) |
| Stats Wilson CI + Holm | `stats/stats.py` | lista — corre sobre `run-XXX/` |
| **Corpus migrado a ASCII (post-U003)** | `corpus-migration/` | **decisión Arquitecto pendiente** |
| Regresión corpus | `verify/corpus-regression.txt` | documentado |
| C4 costo multi-turno | `c4/` (sim + 40 celdas) | modelo hecho, LLM pendiente |
| C5 supervivencia compresión | `c5/` (40 celdas) | truncamiento **medido**, compaction pendiente |

## Datos ya firmes (sin LLM)

**Tokens por documento (o200k):** md 1332 · txt 1601 · yaml 1793 ·
cortex 1902 · json 2385 · xml 3239 → CORTEX 4º de 6 en lectura única.

**Truncamiento (ideas recuperables al cortar % del doc):**

| % | cortex | md | json | xml | yaml |
|---|---|---|---|---|---|
| 25 | 3 | 2 | 0 | 0 | 0 |
| 50 | 18 | 4 | 0 | 0 | 0 |
| 75 | 29 | 6 | 0 | 0 | 0 |

→ Único formato que sigue parseando truncado (atomicidad de línea + señal
de integridad). MD queda legible pero sin señal; JSON/XML/YAML mueren enteros.

**Modelo multi-turno (C4):** md 7104/23532 tok vs cortex 2077/2613 tok
en K=5/K=20 → 3.4–9× a favor si el agente usa direcciones `SIGILO:nombre`.

## Bloqueantes activos

1. **H-A (regresión):** `formats/cortex.cortex` sellado falla con
   `U003` (nombres con tilde). Migración lista → Arquitecto decide
   re-sellar o mantener legacy.
2. **Celdas LLM:** 480 + 40 + 40 listas; necesitan sub-agentes con
   modelo fijado (transporte nativo Alfred — `conexion-nativa-cmd`).
3. **Auditoría N4:** Heimdall, al final.
4. **Modelo control:** pendiente de catálogo (P-04).

## Hipótesis abiertas con criterio de falsación

| Hipótesis | Predicción | Muere si |
|---|---|---|
| C4-H costo sesión | cortex −30%+ tokens totales a K=20 | md iguala a K=20 |
| C5-H compaction | valores exactos sobreviven mejor en sigilo | md preserva igual o más |
| posicionamiento | "contexto durable" | ambas mueren → queda "verificable" |

## Nota de método

Sesgo declarado: evaluador favorable a CORTEX como formato de firma — por
eso cada número aquí tiene script reproducible y cada hipótesis su condición
de muerte escrita *antes* de la medición.
