# CODEC-CORTEX — Documentación

Codec ideático determinista. La IA escribe **CORTEX** (canon `1.0`); el humano
lee **HCORTEX**, su proyección renderizada. `0.1` y `0.2` siguen siendo legibles
como alias; la escritura canónica es siempre `cortex:1.0`.

## Primera lectura

| Documento | Contenido |
|---|---|
| [QUICKSTART.md](QUICKSTART.md) | primer documento, HCORTEX y `loss-report` en 5 minutos |
| [parser-api.md](parser-api.md) | API Python y referencia de CLI de las cinco superficies |
| [LOSS-REPORT.md](LOSS-REPORT.md) | qué información no sobrevive el roundtrip y cómo se declara |
| [MIGRATION-1.0.md](MIGRATION-1.0.md) | cambios incompatibles y recetas de migración |

## Especificaciones (canon 1.0)

| Documento | Contenido |
|---|---|
| **[CORTEX-SPEC-1.0.md](standard/CORTEX-SPEC-1.0.md)** | canon normativo: gramática, C14N, HCORTEX, pérdidas, errores, conformidad y permanencia |
| [errors-1.0.md](standard/errors-1.0.md) | catálogo cerrado: código ↔ emisor ↔ superficie, y reservados declarados |
| [grammar/cortex-1.0.ebnf](grammar/cortex-1.0.ebnf) | gramática normativa |
| [schemas/ast-schema-1.0.json](schemas/ast-schema-1.0.json) | esquema del AST |
| [schemas/loss-report-1.0.schema.json](schemas/loss-report-1.0.schema.json) | esquema del reporte de pérdidas |
| [../conformance/1.0/](../conformance/1.0/) | vectores normativos y corpus sellado |

## Authoring

| Documento | Contenido |
|---|---|
| [authoring/custom-sigils.md](authoring/custom-sigils.md) | crear sigilos y secciones personalizadas |
| [authoring/hcortex-templates.md](authoring/hcortex-templates.md) | plantillas HCORTEX bidireccionales |

## Para LLMs

| Documento | Contenido |
|---|---|
| [../skill/codec-cortex.skill.md](../skill/codec-cortex.skill.md) | el estándar en CORTEX: reglas, comandos, catálogo y evidencias |
| [../skill/codec-cortex.skill.hcortex.md](../skill/codec-cortex.skill.hcortex.md) | la misma verdad en HCORTEX |

## Implementaciones

| Lenguaje | Directorio | Ejecutable | Distribución |
|---|---|---|---|
| Python (referencia) | `codec_cortex/` | `python -m codec_cortex` | PyPI `codec-cortex 1.0.0` |
| Go | `codec-cortex-go/` | `codec-cortex` | `go get` + `make dist` |
| Node.js | `codec-cortex-node/` | `codec-cortex-node` | local (`npm install ./codec-cortex-node`) |
| Rust | `codec-cortex-rs/` | `cortex` | `cargo build --release` |
| Bash | `codec-cortex-bash/` | `codec-cortex` | sourceable (`jq`) |

## Benchmark por agentes

| Documento | Contenido |
|---|---|
| [../bench/agent-package/](../bench/agent-package/README.md) | paquete instructivo autocontenido en `.cortex` para medir propiedades, beneficios y posibilidades del codec con protocolo científico |

## Validación

Certificado determinista reproducible en CI y firmado por auditor independiente
([`../bench/results/audit.sig`](../bench/results/audit.sig), auditoría 1.8,
`SIGNED-PASS`):

| Indicador | Resultado |
|---|---|
| D1 idempotencia | 141/141 |
| D2 roundtrip HCORTEX | 141/141 |
| D2b vectores HCORTEX 1.0 | 70/70 |
| D3 paridad cross-runtime | 5/5 |
| D3b paridad de render | 101/101 |
| D4 no-pérdida | 141/141 |
| D5 tamper | PASS |
| D6 paridad de `loss-report` | 75/75 |
| D7 contrato del dialecto 0.1 | 10/10 |

Artefactos: [`bench/results/certificate.json`](../bench/results/certificate.json) ·
[`bench/results/audit.sig`](../bench/results/audit.sig) · corpus sellado en
[`tests/SHA256SUMS`](../tests/SHA256SUMS) · firma verificable con
[`bench/verify_audit.py`](../bench/verify_audit.py).

## Histórico

Las especificaciones 0.1/0.2, HCORTEX 0.x, C14N 0.x, los glosarios previos y el
catálogo anterior de errores están archivados con sello propio en
[archive/2026-11/standard-0x/](../archive/2026-11/standard-0x/). No son
autoridad normativa. Los reportes fechados (relevamiento, revisiones externas,
gates F2–F4) conservan sus rutas originales por regla de archivo.
