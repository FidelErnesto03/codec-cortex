# bench/lokky — ejecución parcial de BLP-003 (Lokky/NEX)

**Fecha:** 2026-11-03 · **Ejecutor:** Lokky (voz NEX, agente externo a ArqUX)
**Alcance:** todo lo determinista y estadístico de BLP-003, llevado hasta donde el
transporte `conexion-nativa-cmd` no es requisito. Las celdas LLM quedan listas para
que la sesión de Alfred las materialice (ver §3).

## 1 · Entregables

| Artefacto | Contenido |
|---|---|
| `cells/cells.json` | **480 specs de celda** — 2 modelos × 6 formatos × 8 preguntas × R=5, con el prompt material ya embebido (corpus + pregunta). Contrato compatible con `bench/run.py::Cell` |
| `tokens/token-accounting.json` | conteo neutral `tiktoken/o200k_base` por formato + estimación del run completo |
| `seal/SHA256SUMS` | sellado del corpus `formats/` (6 formatos + questions.json) — verificable con `sha256sum -c` |
| `stats/stats.py` | Wilson CI + Holm-Bonferroni sobre `score_*.json` de un run completo — sin dependencias |
| `verify/corpus-regression.txt` | regresión del corpus sellado bajo el parser endurecido |
| `corpus-migration/` | `cortex.cortex` migrado a identificadores ASCII + `NOTES.md` con la decisión pendiente |

## 2 · Hallazgos que ya emergen de los artefactos

**H-A · Regresión real (bloqueante para el run):**
`formats/cortex.cortex` — el corpus sellado — **no parsea** bajo el parser
endurecido: `U003_NON_ASCII_IDENTIFIER @ 14:0`. Dos nombres de idea llevan
tilde (`Lucía_Rojas`, `Sofía_Márquez`). El corpus de corpus-heldout (v0.1)
sí pasa íntegro (8/8). Migración propuesta en `corpus-migration/` —
transliterar solo la posición de nombre; scoring no se afecta
(`scorer.norm()` ya hace NFKD). **Decisión del Arquitecto:** re-sellar con
el corpus migrado o mantener legado.

**H-B · El claim H2 (tokens) puede falsarse vs Markdown:**
conteo neutral o200k del corpus actual:

| Formato | tokens | vs cortex |
|---|---|---|
| **markdown** | **1332** | **−30%** |
| plaintext | 1601 | −16% |
| yaml | 1793 | −6% |
| cortex | 1902 | — |
| json | 2385 | +25% |
| xml | 3239 | +70% |

CORTEX no es el más compacto en tokens (markdown gana por los nombres de
campo no repetidos). H1 (comprensión multi-hop) sigue abierto — pero si el
valor real es determinismo/integridad/sigilos-tipados, H2 falsándose vs MD
es información útil, no derrota.

**H-C · Estimación del run:** ~480 celdas ≈ 960K tokens de entrada totales
(≈2K tokens/celda de corpus + prompt). Con los precios de models.yaml,
ingesta ≈ $0.14–0.42 — holgadamente dentro del presupuesto $5 del
pre-registro (salida aparte).

## 3 · Lo que queda — y quién lo ejecuta

| Paso | Responsable | Estado |
|---|---|---|
| Materializar las 480 celdas (lanzar sub-agentes con modelo fijado) | **Alfred/cmd** — transporte nativo | listo: leer `cells/cells.json`, escribir `results/run-XXX/raw/` |
| Scoring mecánico por celda | `scorer.py` (ya existe) o Lokky | listo |
| Estadística (IC, Holm) por familia | `stats/stats.py` aquí | listo |
| Re-sellar corpus migrado | Arquitecto decide | pendiente H-A |
| Auditoría final (N4) | Heimdall | pendiente |
| Modelo control no-2026 | acceso pendiente (P-04 anota) | bloqueado por catálogo |

## 4 · Método y honestidad

- Todo lo producido es reproducible: `cells.json` se regenera con un script
  de ~40 líneas sobre `formats/` + `questions.json`.
- No ejecuté `certify.py` porque escribe sobre `results/certificate.json`
  (registro Heimdall-firmado) — fuera de mi alcance como ejecutor externo.
- Mi sesgo declarado: evaluador favorable a CORTEX como formato de firma;
  los números de tokens los reporté tal cual salieron, incluyendo el que
  desfavorece a CORTEX vs markdown.
