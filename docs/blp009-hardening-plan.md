# BLP-009 — Plan de hardening del toolchain 1.0.1 (T-9.2.1 / T-9.2.2 / T-9.2.3)

> Estado: **diseño + implementación (Opción B) completa a nivel local**. Este documento es entregable de T-9.2.x.
> No modifica canon ni `run-001`.
>
> **Release DIFERIDO:** los cambios están *staged* (sin commit/release), pendientes de incluir más antes de la
> próxima versión. Sin bump (sigue 1.0.1) ni re-firma de certificado todavía. Ver `CHANGELOG.md` → `[Unreleased]`.
>
> ## Estado de implementación (2026-11-14)
> - **Implementado (Opción B):** campo `coverage` en el `loss-report` de las **5 superficies** (Python, Go, Node, Rust, Bash),
>   con `{complete, operations:["render"], uncovered_operations:["compile"]}`. `reversible:true` ya declara explícitamente
>   que sólo cubre `render`; el tramo `compile` queda declarado como no cubierto (deja de ser un sobre-claim silencioso).
>   Actualizados: `docs/schemas/loss-report-1.0.schema.json`, `conformance/1.0/loss/expected/*.json`, `docs/LOSS-REPORT.md`,
>   `tests/test_lossreport.py` (test `test_coverage_declares_compile_gap`). Binarios Go y Rust reconstruidos.
> - **Implementado (T-9.2.1 completo, firmado por el Arquitecto):** guardia compile-side **L406_COMPILE_SIDE_DROP** en las
>   5 superficies. Detecta ideas presentes en el AST que se pierden en el roundtrip render→compile (se comparan las
>   direcciones de ideas de fuente vs. recompilado) y **reemplaza al genérico L499** en ese caso (severidad `error`,
>   exit 1). Añadido a `docs/standard/errors-1.0.md` (aditivo, ratificado) y a `docs/LOSS-REPORT.md`.
>   Verificación: D6 75/75 PASS; unittest 11/11; node 9/9; go/rust tests ok; catálogo cerrado (104).
> - **Hallazgo resuelto (2026-11-14):** el disparador era un namespace con `.`/`-`
>   (p. ej. `tenant.x::KNW:alpha`): Python/Go/Node/Rust perdían la idea (su `_IDEA_MARKER_RE` usaba `\w+::`), Bash no.
>   **Fix aplicado:** el marcador HCORTEX de las cuatro superficies se alineó a la gramática CORTEX
>   (`namespace [a-z][a-z0-9_.-]*`; nombre imprimible sin espacio/`{}`/`|`) → la idea ya no se pierde y **las 5 superficies
>   coinciden** (hash `437ad6ef…` en las cinco). L406 queda como guardia clasificada (sucesor de L499) sin disparador en el corpus.
> Trazabilidad: consolidación de `bench/results/cortex/Qwen_cortex_20261114_p5jkx65xu.cortex`
> (sha256 `ec125b87bb6b707843246f6a65a8baa3b8fd31edc05117d3099a4488f570aa00`) y
> `bench/results/cortex/run-001-gap-closure.cortex`
> (sha256 `fe2a83d8d6e3230eb30a7db64af28055c84bcde4f9ee67ebd4b2dc55c1083453`).
> Canon 1.0 congelado; `run-001` sellado e inmutable.

## 1. Evidencia del problema

| Hallazgo (fuente) | Descripción | Estado en 1.0.1 |
|---|---|---|
| f04 (Qwen) | Aceptación silenciosa: rendimiento OK con contenido no representado | `loss-report` sólo cubre `operation: render` (AST→HCORTEX→AST); no declara cobertura de la compilación fuente→AST |
| f05/f06 (Qwen) | Guardia precompile / cobertura compile-side ausente | No existe; el parser rechaza prosa/dup/undeclared, pero no cuantifica contenido no representado |
| f07 (Qwen) | Catálogo/precedencia de errores y precisión de mensajes | `scripts/ccx_error_catalog.py` cierra a 103 códigos; precedencia multi-diagnóstico no verificada |
| f08 (Qwen) | Conformance empaquetado/reproducible | `conformance/slots` 68/68 PASS; falta vector específico de cobertura de pérdida |
| g01 (run-001-gap) | Brazo cortex de `run-001` es dialecto 0.1 (`G042` bajo 1.0.1) | Registrado; requiere baseline 1.0 válido (protocolo run-002, ver prereg) |
| g02 (run-001-gap) | Asimetría de prompt confunde h5 (0.375 vs 0.875) | Registrado; corrección en protocolo run-002 (simetría ±10% tokens) |
| — | `loss-report` puede reportar `reversible: true` sin declarar cobertura | `reversible` == equivalencia estructural render; no declara clases cubiertas/no cubiertas |

**Resumen:** el defecto central es de *cobertura honesta*: `loss-report` no declara qué clases de pérdida modela ni su completitud, y no existe un análisis compile-side (fuente→AST) cuantificado. El segundo frente es el protocolo `run-002` (prereg separado).

## 2. Restricciones de diseño (no negociables)

1. **Paridad byte-exacta en 5 superficies.** `bench/certify.py::d6_loss_report_parity` compara la salida de `loss-report` de Python, Go, Node, Rust y Bash **byte a byte**, y además contra los fixtures `conformance/1.0/loss/expected/*.json`.
2. **Schema cerrado.** `docs/schemas/loss-report-1.0.schema.json` declara `additionalProperties: false`; un campo nuevo sin actualizar el schema invalida el reporte.
3. **Canon 1.0 congelado.** Sólo evolución **aditiva 1.x** o dialecto 2.0. Este cambio es aditivo 1.x (campo nuevo opcional / subcomando nuevo), nunca mutación silenciosa.
4. **`run-001` inmutable**; no tocar `conformance/1.0/loss/expected` sin regenerarlos de forma auditada.
5. Cada claim queda hash-trazable.

## 3. Propuesta técnica

### T-9.2.1 — Guardia compile-side y cobertura de `loss-report`

**Objetivo:** que `reversible: true` sea honesto respecto de la cobertura.

- **Opción A (recomendada, 1.x aditiva): subcomando/flag `coverage`.**
  - Nuevo `cortex loss-report --coverage <file>` (o `cortex coverage <file>`) que emite un objeto `coverage` **separado**, sin cambiar el JSON por defecto de `loss-report` (no rompe D6 ni los fixtures).
  - `coverage = { modeled_classes: ["L402","L403","L405","L406"], uncovered_classes: ["compile:source->ast:prose-in-body", ...], complete: bool, source_bytes_represented, source_bytes_total }`.
  - `complete: true` sólo si no quedan clases no modeladas.
- **Opción B (formato):** añadir campos `coverage` al reporte por defecto → exige tocar 5 superficies + schema + expected/; **no recomendada** en este ciclo (alto blast-radius, coordinar paridad y regenerar fixtures).
- **Guardia compile-side (independiente de formato):** en el parser/referencia, detectar y declarar como **L406 (nueva clase, declare-only)** el contenido de cuerpo de sección no representado (p.ej. marcador HCORTEX `###` interpretado como comentario en fuente CORTEX, o cuerpo sin ideas). Requiere:
  1. Definir L406 en `codec_cortex/lossreport.py` + catálogo (`scripts/ccx_error_catalog.py`) + `docs/standard/errors-1.0.md` (aditivo).
  2. Replicar en las 4 superficies no-Python (`codec-cortex-go/cortex/lossreport.go`, `codec-cortex-node/src/lossreport.js`, `codec-cortex-rs/src/...`, `codec-cortex-bash/...`).
  3. Regenerar `conformance/1.0/loss/expected/*.json` y añadir un vector `L406_*`.
  4. Actualizar `docs/schemas/loss-report-1.0.schema.json` (código L406 ya encaja en el patrón `^L[0-9]{3}_[A-Z0-9_]+$`; no requiere cambio si no se añade campo).

  **Riesgo:** L406 cambia la salida de fixtures existentes que hoy caen en ese caso → regeneración auditada + actualización de `docs/LOSS-REPORT.md`.

### T-9.2.2 — Catálogo/precedencia de errores y conformance

- Definir y documentar **precedencia determinista** de diagnósticos cuando una línea viola varias reglas (p.ej. `S003` vs `I001`), en `docs/standard/errors-1.0.md` (aditivo) + test que fija el orden.
- Añadir vector(es) de conformance para precedencia y para la guardia compile-side en `conformance/1.0/loss/` y `conformance/slots/`.
- Verificar paridad de mensajes entre superficies (no sólo códigos).

### T-9.2.3 — Sellado y operación

- Definir "artefacto canónico por render" (hash de salida + hash de fuente + versión + dialecto) y sellado hash-trazable reutilizando el patrón del certificado.
- Controles operativos: logs acotados (truncado), prohibición de secretos en artefactos, tope de coste declarado (aplicable al benchmark externo, no al codec).

## 4. Plan de verificación (local, sin celdas ni gasto)

| Paso | Comando | Criterio |
|---|---|---|
| Unidad loss-report + precedencia | `python3 -m unittest discover -s tests -p 'test_*.py'` | 100% verde; tests de coverage, ns con punto y precedencia |
| Conformance slots | `python3 -m codec_cortex conformance` | PASS (hoy 68/68) |
| Catálogo cerrado | `python3 scripts/ccx_error_catalog.py` | OK (hoy 104 códigos) |
| Probes núcleo | `python3 scripts/ccx_probes.py` | todos PASS |
| Paridad 5 superficies | `python bench/certify.py` (D6) | byte-exacto en las 5 superficies + fixtures |
| No regresión canon | `git diff -- docs/standard/CORTEX-SPEC-1.0.md` y `run-001` | vacío |

## 5. Reversión

- Código: `git restore -- codec_cortex codec-cortex-* conformance docs/schemas`.
- Fixtures: restaurar `conformance/1.0/loss/expected/` desde git.
- Gobernanza: revertir vía handlers MCP; nunca editar `.arqux/` a mano.

## 6. Decisiones tomadas (antes "preguntas abiertas")

1. **Alcance multi-superficie:** implementado en las **5 superficies** (Python/Go/Node/Rust/Bash), con rebuild de Go y Rust.
2. **Cobertura:** Opción **B** (campo `coverage` en el reporte por defecto) — decidida por el Arquitecto.
3. **Spec:** adición aditiva a `docs/standard/errors-1.0.md` (L406) **firmada por el Arquitecto** (2026-11-14).
4. **Benchmark `run-002`:** externo y posterior (fuera de este BLP en esta fase).

## 7. Artefacto canónico por render, sellado y operación (T-9.2.3)

**Artefacto canónico por render.** Un render queda descrito por el vector determinista
`seal = {dialect, codec_version, operation, source_sha256, target_sha256, coverage}`.
Todos sus campos ya los emite `loss-report` (`source_sha256`, `target_sha256`,
`coverage`, `operation`, dialecto 1.0) → el sello es **derivable sin cómputo extra**.

**Sellado hash-trazable.** El sello se sella como `sha256(canonical_json(report))` sobre la
salida canónica de `loss-report` (claves ordenadas, 2 espacios, UTF-8, newline final),
que ya es byte-idéntica en las 5 superficies. Un resultado de benchmark adjunta su sello para
detección de deriva; dos corridas con el mismo sello son indistinguibles a nivel de codec.

**Controles operativos (declarados).**
- *Logs acotados:* truncado determinista en artefactos/logs (sin volcar payloads completos).
- *Sin secretos:* ningún artefacto, sello o log incluye tokens/claves; los artefactos se revisan antes de sellar.
- *Tope de coste:* `max_usd` declarado en el preregistro; al alcanzarlo, DETENER (§16). Aplica al benchmark externo, no al codec.
- *Reversión:* todo cambio de código reversible por `git restore`/`git revert`; fixtures restaurables desde git.
