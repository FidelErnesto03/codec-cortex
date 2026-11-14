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
| `standard-0x/` | `docs/standard/*` y `docs/spec/` | Especificaciones 0.1/0.2 (CORTEX, C14N, HCORTEX, glosarios, errores) superseded por `CORTEX-SPEC-1.0.md` (BLP-004 T-4.1, 2026-11-14). Cada archivo lleva cabecera `SUPERSEDED`. |
| `examples/` (retirado) | `examples/` | No era un corpus: era una capa de alias por symlinks a `conformance/` (`valid`, `invalid`, `expected-*`, `manifest.json`). Se retiró como la de `docs/spec/`; el corpus real y sellado vive en `conformance/`. |
| `transition/` | `docs/transition/` | Evidencia PHASE0 (manifest y reporte de ejecución) de la transición al repo limpio. Histórico de programa. |
| `profiles-placeholder/` | `profiles/` | Placeholder de "CORTEX Profiles" que nunca se materializó. Fuera de alcance: el codec no incluye runtime de agentes ni perfiles. |
| `cortex-db-line/` | `docs/CORTEX-DB-*.md` | Documentación v0.1 de la línea CORTEX-DB, **delegada a Proyecto_X** (decisiones E-0272/E-0273). Registro de la línea previa; no es autoridad. |
| `docs/spec/` (retirado) | `docs/spec/` | No era un duplicado byte-exacto: era una capa de alias por symlinks a `docs/standard/`. Se retiró para que exista una sola ruta normativa; sus destinos siguen vivos en `docs/standard/`. |

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
4. Los documentos históricos que permanecen fuera del archivo
   (`docs/DIALECT-1.0-RELEVAMIENTO.md`, `docs/EXTERNAL-REVIEW-*`,
   `docs/standard/REV-*`, `F3/F4-CHARTER`, `CHANGELOG.md`) conservan sus
   enlaces originales a `docs/standard/<spec 0.x>`: son registro fechado y no
   se reescriben. Si un enlace no resuelve, el destino real está en
   `archive/2026-11/standard-0x/`.
