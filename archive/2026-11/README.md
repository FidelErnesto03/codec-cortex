# Archive — ciclo 2026-11

Material **deprecado o supersedido** del proyecto, conservado como evidencia
histórica congelada. Nada aquí es autoridad normativa ni dependencia de
runtime. El estado vigente vive fuera de este directorio.

Integridad del archivo: [`SHA256SUMS`](SHA256SUMS) (sello propio de este ciclo).

## Contenido

| Ruta | Origen | Por qué se archivó |
|---|---|---|
| `early-eval/benchmark/` | `tests/benchmark/` | Benchmark informal (~20 ejecuciones, modelos sin identificar). No conforme a Art. XVII — supersedido por `bench/` + certificado Nivel A (BLP-003). |
| `early-eval/durability/` | `tests/durability/` | Control CORTEX-vs-texto nunca ejecutado; diseño re-hecho en preregistro BLP-003. |
| `early-eval/generation/` | `tests/generation/` | Misma generación de evidencia informal. |
| `early-eval/llm-comprehension/` | `tests/llm-comprehension/` | Evaluó modelos 2025 (DeepSeek-V3, GPT-5.6, Gemini, Qwen, GLM) — fuera de fecha frente a los modelos 2026 del preregistro. |
| `early-eval/hardening/` | `tests/hardening/` | `diagnosis.json` único, era pre-hardening. |
| `experiments/` | `experiments/` | Artefactos de gates de desarrollo F2-v1/F2-v2/F3/F4 (corpus, vectors, resultados). Evidencia de proceso, no superficie vigente. |
| `tools-legacy/` | `tools/` | Validadores de fase 2/3/4, `cortex_rev`, `hcortex_oracle`, `hcortex_transformer.py.legacy` — supersedidos por `conformance/`, `scripts/ccx_probes.py` y `bench/certify.py`. |
| `docs-review/` | `docs/review/` | Reportes de gates F2/F3/F4 y notas de cierre de fase — historial de revisión fechado. |
| `rev-report.json` | `./rev-report.json` | Artefacto generado (reporte F3/F4) de ejecución antigua. Regenerable. |

## Reglas del archivo

1. **Lectura permitida, edición prohibida** — el archivo es evidencia
   congelada; corregir un reporte histórico falsificaría la evidencia.
2. **Nada del archivo entra al build, a los tests ni a dependencias de
   runtime del paquete.** Excepción documentada: los harness *legacy*
   F3/F4 (`python -m codec_cortex` y `codec-cortex` Go sin subcomando)
   usan `archive/2026-11/experiments/` como corpus por defecto (o
   `$REV_PACKAGE`) — es su entrada canónica histórica, uso opt-in, no una
   dependencia. El resto de referencias vivas al archivo es un bug.
3. Próximos ciclos de archivo: `archive/YYYY-MM/` con su propio
   `SHA256SUMS` y `README.md`.
