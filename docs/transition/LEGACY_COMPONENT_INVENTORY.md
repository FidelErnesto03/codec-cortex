# Inventario de componentes heredados v0.6.x

**Document ID:** `CCX-LEGACY-INVENTORY-0001`  
**Source baseline:** `FidelErnesto03/codec-cortex@232fa6f`  
**Security containment baseline:** `ba31cdf`  
**Date:** `2026-07-16`

## Escala de decisión

- `REUSE-CANDIDATE`: lógica pequeña potencialmente reutilizable después de revisión y desacoplamiento.
- `REWRITE`: conservar conocimiento y tests útiles, no copiar implementación como autoridad.
- `EXTRACT`: mover a repositorio o tooling externo.
- `LEGACY-ADAPTER`: mantener solo para migración.
- `REJECT`: no trasladar al nuevo núcleo.
- `EVIDENCE`: conservar como evidencia o corpus, no como código normativo.

## Hallazgos transversales

1. Existen dos árboles de fuente: `cli/src/cortex` y `src/cortex`.
2. El `pyproject.toml` raíz declara `src`, mientras el CI trabaja dentro de `cli`.
3. El repositorio versiona `*.egg-info`, tarballs, PDFs y resultados generados.
4. El paquete integra learning, runtime, CRUD, plantillas cognitivas y seguridad.
5. La documentación presenta learning como parte del codec.
6. La validación actual contiene reglas de gobierno cognitivo y sigilos críticos.
7. La especificación efectiva está dispersa entre SKILL, código, documentación y tests.
8. HCORTEX y VIEW están acoplados a perfiles y formatos heredados.
9. El repositorio contenía códigos de recuperación de PyPI.
10. La línea actual no puede convertirse en Core mediante poda incremental segura; requiere extracción limpia.

## Matriz de componentes

| Componente heredado | Responsabilidad observada | Acoplamiento | Decisión | Destino / tratamiento |
|---|---|---:|---|---|
| `core/ast.py` | AST actual y glosario | medio/alto | REWRITE | Diseñar AST mínimo desde la especificación; rescatar tests de spans/identidad |
| `core/lexer.py` | tokenización heredada | medio | REUSE-CANDIDATE | Extraer reglas útiles y revalidarlas contra ABNF/EBNF |
| `core/parser.py` | source → AST v1 | alto | REWRITE | No copiar como definición; usar como fuente de casos legacy |
| `core/writer.py` | AST → texto v1 | alto | REWRITE | Sustituir por writer normativo + canonical writer |
| `core/validator.py` | estructura + gobierno cognitivo | muy alto | REWRITE | Separar validación estructural de perfiles |
| `core/errors.py` | diagnósticos y reglas operativas | alto | REWRITE | Conservar idea de códigos estables; eliminar CRUD/gobierno/secretos del núcleo |
| `core/schema.py` | glosario local + fallback canónico | alto | REWRITE | Rehacer como vocabulario local neutral y profile hooks |
| `core/document_kind.py` | clasificación cognitiva | alto | REJECT | Pertenece a perfiles o tooling |
| `core/modes.py` | modos de operación/editor | medio | EXTRACT | Editor/tooling externo |
| `core/repair.py` | reparación de legacy | alto | LEGACY-ADAPTER | Mover a `cortex-legacy-import` |
| `core/transactions.py` | CAS y escritura atómica | alto | EXTRACT | `cortex-editor` o runtime; no codec normativo |
| `core/compare.py` | comparación estructural | medio | REUSE-CANDIDATE | Redefinir sobre equivalencia normativa |
| `v2/ir.py` | IR alternativo | medio | REWRITE | Evaluar ideas para nuevo AST, sin copiar arquitectura completa |
| `v2/parser.py` | parser v2 | alto | LEGACY-ADAPTER | Casos de migración y pruebas diferenciales |
| `v2/writer.py` | writer v2 | alto | LEGACY-ADAPTER | Solo importación/compatibilidad |
| `v2/encoder.py` | encoder actual | medio | REWRITE | Redefinir API desde modelo abstracto |
| `v2/equivalence.py` | equivalencia | medio | REUSE-CANDIDATE | Validar semántica e idempotencia |
| `v2/diagnostics.py` | diagnósticos v2 | bajo/medio | REUSE-CANDIDATE | Unificar con modelo normativo |
| `v2/hcortex_*` | roundtrip HCORTEX heredado | alto | REWRITE | HCORTEX universal desde AST |
| `v2/view*` | proyecciones VIEW | muy alto | EXTRACT | `cortex-view-extension` |
| `hcortex/edit_parser.py` | edición reversible heredada | alto | REWRITE | Conservar casos difíciles como corpus |
| `hcortex/edit_renderer.py` | render editable | alto | REWRITE | Sustituir por HCORTEX-CANONICAL |
| `hcortex/read_renderer.py` | render legible | medio | EXTRACT | HCORTEX-READABLE no normativo o módulo separado |
| `hcortex/profiles.py` | layouts/perfiles | muy alto | EXTRACT | `cortex-profiles` o VIEW |
| `hcortex/recovery.py` | recuperación | alto | LEGACY-ADAPTER | `cortex-legacy-import` |
| `glossary/*` | vocabulario local | medio/alto | REWRITE | Modelo neutral de vocabulario/namespaces |
| `crud/*` | selectores y mutaciones | alto | EXTRACT | `cortex-crud` / `cortex-editor` |
| `learning/*` | candidates, scoring, elevation, decay, feedback, session, workspace | total | EXTRACT | `cortex-learning`; prohibido en Core |
| `runtime/*` | estado transitorio y sesión | total | EXTRACT | `cortex-runtime` |
| `templates/brain.py` | cerebro de agente | total | REJECT | Perfil Agent o ejemplo externo |
| `templates/skill.py` | plantilla Skill | alto | EXTRACT | `cortex-profiles/skill` |
| `templates/package.py` | paquete contextual | alto | EXTRACT | Perfil opcional |
| `templates/minimal_glossary.py` | glosario por defecto | alto | REWRITE | El Core no impone sigilos |
| `security/secret_scanner.py` | escaneo de secretos | bajo respecto al formato | EXTRACT | tooling de release/CI |
| `security/signature.py` | firma | medio | EXTRACT | `cortex-sign`; no gramática base |
| `audit/logger.py` | logging operacional | medio | EXTRACT | tooling; conservar diagnósticos puros en Core |
| `cli/commands/add|update|delete|move|get|list` | CRUD | alto | EXTRACT | CLI externa |
| `cli/commands/recover` | legacy repair | alto | LEGACY-ADAPTER | `cortex-legacy-import` |
| `cli/commands/diagram` | diagramas | alto | EXTRACT | VIEW/tooling |
| `cli/commands/benchmark` | benchmark | bajo | EXTRACT | repositorio benchmark/conformance |
| `cli/commands/v2_*` | compatibilidad v2 | alto | LEGACY-ADAPTER | puente de migración |
| `cli/commands/verify|format|compile|render` | operaciones codec | medio | REWRITE | Rehacer sobre API pública mínima |
| `skill/cortex/*` | vocabulario y adopción Agent | total | EXTRACT | `cortex-profiles/agent-context` |
| `skill/hcortex/*` | especificación humana heredada | alto | EVIDENCE | Fuente para RFC HCORTEX, no autoridad |
| `docs/reference/SKILL*` | especificación dispersa | alto | EVIDENCE | Extraer requisitos y contradicciones |
| `docs/reference/learning-*` | learning | total | EXTRACT | `cortex-learning` |
| `docs/benchmarks/*` | corpus y resultados | mixto | EVIDENCE | Selección neutral; no copiar claims sin revalidación |
| `certification/*` | planes y baselines | mixto | EVIDENCE | Reusar estructura, regenerar evidencia |
| `src/tests/test_learning*` | pruebas learning | total | EXTRACT | `cortex-learning` |
| tests de parser/writer/roundtrip | comportamiento heredado | medio | EVIDENCE | Convertir en corpus legacy y casos de regresión |
| `src/codec_cortex.egg-info/*` | artefactos generados | ninguno | REJECT | No versionar |
| `docs/archive/*.tar.gz` | artefactos binarios históricos | alto riesgo | REJECT/ARCHIVE | Almacenamiento externo inmutable, tras scan |
| PDFs y PNGs generados | resultados históricos | bajo | EVIDENCE | Separar del repositorio normativo |
| `.secrets.baseline` manual | baseline sin ejecución demostrada | medio | REWRITE | Generar automáticamente en CI |
| `.github/workflows/ci.yml` | CI mezclado y rutas inconsistentes | alto | REWRITE | Nuevo CI por repositorio |
| `pyproject.toml` | paquete único con claims learning | alto | REWRITE | Nuevo paquete mínimo, metadatos neutrales |
| `README.md` | posicionamiento de protocolo + learning | total | REWRITE | README del laboratorio; nuevo README por autoridad |
| `GOVERNANCE.md` | gobierno BDFL y SKILL como canon | alto | REWRITE | Gobierno del estándar separado de implementación |

## Importación autorizada inicialmente

Solo se autoriza transportar conocimiento, no módulos completos, de:

- lexer;
- source spans;
- AST/value tests;
- comparación estructural;
- diagnósticos estables;
- casos de Unicode;
- casos de roundtrip;
- fixtures válidos e inválidos;
- resultados de benchmark reproducibles que puedan regenerarse.

## Importación prohibida inicialmente

- paquetes `learning`, `runtime`, `crud`, `templates`;
- vocabularios Agent;
- VIEW;
- código de sesión/workspace;
- lógica de elevación o memoria;
- artefactos generados;
- metadatos `egg-info`;
- historial Git;
- releases y tags heredados;
- secretos, baselines manuales o archivos de recuperación.

## Requisito por componente

Toda aceptación futura deberá crear una ficha con:

```text
source commit
source path
purpose
dependencies
domain coupling
security risk
test evidence
decision
reviewer
target path
```
