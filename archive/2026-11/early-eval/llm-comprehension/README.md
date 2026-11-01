# Prueba de Comprensión CORTEX 0.1 para Modelos de Lenguaje

**Versión:** 1.0 — 2026-07-17

## Hipótesis

> CORTEX es un lenguaje de máquina para modelos de lenguaje. Un modelo competente lo lee y comprende directamente, sin parseo ni herramientas externas.

## Archivo de prueba

`test.cortex` — 5 secciones, 23 ideas, CORTEX 0.1 válido.

Contiene:
- **§1** — Identificación del modelo
- **§2** — Instrucciones contextuales (qué es CORTEX)
- **§3** — 6 tareas de comprensión (conteo de tokens, inversión, extracción del glosario, listado de secciones, identificación de sigilos)
- **§4** — Formato de respuesta obligatorio (JSON estructurado)
- **§5** — Métricas para el evaluador humano

## Método

1. Adjuntar `test.cortex` al modelo
2. Escribir **solo**: `responde`
3. Guardar la respuesta en `results/<plataforma>-<modelo>.json`
4. Evaluar según los criterios abajo

## Criterios de evaluación

| Nivel | Descripción | Indicadores clave |
|---|---|---|
| **5 — Nativo** | Entiende CORTEX como formato nativo | JSON válido, usa nomenclatura CORTEX en `notes`, respuestas correctas |
| **4 — Competente** | Entiende la estructura pero no la adopta | JSON válido, respuestas correctas, sin referencia a sigilos/secciones |
| **3 — Funcional** | Extrae info correcta, ignora estructura | JSON con errores menores, algunas respuestas correctas |
| **2 — Plano** | Lee como texto, entiende parcialmente | JSON malformado o ausente, respuestas parciales |
| **1 — Confundido** | No entiende el formato | Respuesta sin relación, pregunta "¿qué es esto?" |
| **0 — Incoherente** | No procesa el input | Error, alucinación, o respuesta vacía |

## Métricas

| Métrica | Golden | Fuente |
|---|---|---|
| JSON válido | `true` | ¿Se parsea con `JSON.parse()`? |
| Campos requeridos | model, platform, date, total_tokens, tasks, comprehension_self_assessment | §4 FMT |
| T3.2 (inversión tokens) | "language models for machine language a is CORTEX" | §5 MTR |
| T3.6 (conteo TST) | 6 | §5 MTR |
| comprehension_self_assessment | 1-5 | Auto-declarado por el modelo |
| Adopción nomenclatura | ¿Usa "sigilo", "sección", "$0", "glosario"? | `notes` field |

## Plataformas

- [ ] OpenAI — GPT-4o
- [ ] OpenAI — GPT-4.1
- [ ] Anthropic — Claude Sonnet 4
- [ ] Anthropic — Claude Opus 4
- [ ] Google — Gemini 2.5 Pro
- [ ] DeepSeek — V3
- [ ] DeepSeek — R1
- [ ] Meta — Llama 4
- [ ] xAI — Grok
- [ ] Mistral — Large

## Veredicto

- **HIPÓTESIS CONFIRMADA** si ≥80% de modelos alcanzan nivel ≥4
- **HIPÓTESIS REFUTADA** si ≥50% obtienen nivel ≤2
