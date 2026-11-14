# Changelog

Todos los cambios notables del proyecto se documentan aquí. El proyecto sigue
nombres canónicos sin versión en archivos/esquemas; la versión vive en los
metadatos de cada superficie y en tags de git.

## [Unreleased]

> Cambios posteriores a `1.0.2-rc.1` se acumulan aquí hasta el release final.

## [1.0.2-rc.1] — 2026-11-14

> **RELEASE CANDIDATE.** Versión candidata del próximo release: commit + tag
> `v1.0.2-rc.1` publicados en git. **No es el release final**: queda pendiente la
> publicación a PyPI, el bump a `1.0.2` y la decisión sobre run-002. El dialecto
> 1.0 **no cambia** (sin cambios de gramática ni de hash canónico).

### Añadido

- `loss-report`: campo `coverage` (`{complete, operations, uncovered_operations}`)
  en las **cinco** superficies. `reversible: true` queda ahora acotado: declara
  que sólo cubre `render` y que el tramo `compile` no está modelado, en lugar de
  sobre-afirmar cobertura. Schema `loss-report-1.0.schema.json` actualizado.
- `loss-report`: clase de pérdida `L406_COMPILE_SIDE_DROP` — guardia clasificada
  que detecta ideas perdidas en el roundtrip render→compile (sucesora específica
  de `L499`). Añadida al catálogo cerrado §8.2 de `docs/standard/errors-1.0.md`.
- `docs/standard/errors-1.0.md`: sección de **precedencia determinista de
  diagnósticos** (una misma línea) verificada por `tests/test_diagnostics.py`.
- **API pública de dominio** (`codec_cortex/api.py`, exportada como `cc`):
  `parse`, `validate`, `canonicalize`, `hash`, `hash_source`, `to_hcortex`,
  `from_hcortex` y `CompileError` con `.diagnostics`. Los módulos internos
  siguen importables; el facade es la superficie estable para código nuevo.
- **`cc.emit()`** (`codec_cortex/emit.py`): emisión de líneas de ideas
  válidas y escapadas — shapes `attrs`, `attrs-pos`/`relacion`, `cuerpo` y
  `bloque`, namespaces calificados, validación de sigilos/keys/payloads.
- **Diagnósticos enriquecidos** (`codec_cortex/diagnostics.py`): `I001` ahora
  sugiere sigilos declarados ("Did you mean: …") y `I004` muestra la forma
  esperada por shape. Códigos y precedencia sin cambios.
- **CLI**: `cortex diff <a> <b>` (diff semántico sobre la forma canónica) y
  `cortex verify <file> <expect>` (`sha256:<hex>`, hex desnudo u otro
  `.cortex`). Todo argumento de archivo acepta `-` para leer de stdin.

### Corregido

- Marcador HCORTEX (Python/Go/Node/Rust): aceptaba sólo `\w+::` como namespace y
  nombres `[\w_-]+`, por lo que un namespace con `.`/`-` (p. ej.
  `tenant.x::KNW:alpha`) perdía la idea en el roundtrip render→compile. Ahora
  acepta la gramática CORTEX (`namespace [a-z][a-z0-9_.-]*`, nombre imprimible
  sin espacio/`{}`/`|`), de modo que **las cinco superficies vuelven a coincidir**
  byte a byte. (Bash ya lo hacía.)

### Interno

- Fixtures `conformance/1.0/loss/expected/*.json` regenerados (incluyen `coverage`).
- `docs/LOSS-REPORT.md` y `docs/blp009-hardening-plan.md` actualizados.
- Binarios Go y Rust reconstruidos (gitignored).

### Pendiente para el release final 1.0.2

- **Bump a `1.0.2`** (hoy `1.0.2-rc.1`) y **publicación a PyPI** + tag final.
- **Certificado re-ejecutado sobre el árbol del RC**: PASS (D1 141/141,
  D2 141/141, D2b 70/70, D3 5/5, D3b 101/101, D4 141/141, D5, D6 75/75,
  D7 10/10) — ver `bench/results/certificate.json`.
- **run-002**: preregistro en borrador (`bench/prereg-run-002.draft.yaml`),
  ejecución no autorizada.

## [1.0.1] — 2026-11-14

Release de implementación. El **dialecto 1.0 no cambia**: no hay cambios de
gramática ni de hash canónico. Cambia lo que la implementación sabe hacer y lo
que exige.

### Añadido — pérdidas declaradas verificables

- `loss-report`: comando nuevo en las cinco superficies (Python, Go, Node,
  Rust, Bash) que emite el reporte de pérdidas declaradas en JSON canónico,
  byte-idéntico entre superficies.
- Catálogo cerrado §8.2: `L402_COMMENT_DROPPED`, `L403_INTRALINE_WHITESPACE`,
  `L405_OPEN_ATTR_ORDER`; `L499_UNCLASSIFIED_LOSS` como guardia de cierre.
- Certificado: `D6_loss_report_parity` (75 documentos × 5 superficies) y
  `D7_dialect_contract` (contrato 0.1 común a las cinco).

### Cambios incompatibles (breaking, documentados)

- **`$0: <título>` deja de ser válido.** La gramática 1.0 define
  `glossary-header = "$0" | "$0:" capa`; el título se descartaba en silencio y
  ahora se rechaza con `G042_GLOSSARY_HEADER_INVALID`. Migración: reemplazar la
  línea por `$0` o `$0:<CAPA>`. Documentos afectados en el repo, conservados
  intactos por ser corpus de benchmark congelado: `bench/formats/cortex.cortex`
  y `bench/lokky/corpus-migration/cortex.cortex` (`$0: NEXUSCORP KB:KERNEL`).
- **Glosario sin capa**: el renderer emite `$0` desnudo. Antes omitía la línea
  y producía un HCORTEX que su propio compilador rechazaba.
- **CLI `hash` de Python**: imprime `sha256:<hex>` como las otras cuatro
  superficies (antes solo el hex). Los scripts que parseaban el hex desnudo
  deben quitar el prefijo.

### Corregido

- Node y Rust (dialecto 0.1): `G042` con el código correcto y `$0` desnudo en
  el render (antes respondían `S005` y omitían la línea). Cubierto por D7.
- `loss-report` renderiza antes de canonicalizar: C14N muta el AST (expansión
  de microtokens, orden de atributos) y el hash de destino difería entre
  superficies.

## [1.0.0] — 2026-11-01

### Release 1.0.0 — implementación de referencia

- HCORTEX 1.0: envelope `v=1.0` (v=0.2 como alias de lectura), fences opacos
  en ideas y secciones, tablas con pipes entrecomillados.
- Paridad byte-exacta 101/101 en c14n, render y roundtrip en Python, Go,
  Node, Rust y Bash; D3b 101/101 con `degraded=[]`.
- Certificado PASS: D1 141/141, D2/D2b, D3 5/5, D3b, D4 141/141, D5.
- Instrumento atado al certificador (`certifier_sha256`) y preflight de
  binarios para reproducibilidad desde clon limpio.

### Corregido — roundtrip HCORTEX determinista y verdadero (140/140)

- Glosario slots: `pos` ya no se descarta al renderizar — los sigilos
  `attrs-pos`/`relacion` conservan su contrato (eliminaba 9 pérdidas en 1.0)
- Compilador HCORTEX: des-escapado de strings en `_make_scalar` — elimina
  pérdida silenciosa de `\"` y `\n` sin diagnóstico
- Ideas `attrs-pos`/`relacion` se reconstruyen en su forma posicional
  (antes degradaban a `attrs` nombrados); celdas opcionales omitidas ya no
  se materializan como `null`
- Certificado D2 extendido a las 3 superficies: **140/140 AST-exactos y
  140/140 deterministas** (antes solo 30/30 de 0.2, ciego al 79% del corpus)

### Añadido — BLP-004: dialecto CORTEX 1.0 (draft normativo)

- `docs/standard/CORTEX-SPEC-1.0.md` — canon normativo draft que unifica
  0.1 (superficie fundamental) + 0.2 (eje slots) bajo `cortex:1.0`, con
  aridad posicional estricta (I012), catálogo cerrado de errores, pérdidas
  HCORTEX declaradas (L4xx) y contrato de permanencia.
- `docs/standard/errors-1.0.md` — mapa código↔emisor↔superficie generado
  mecánicamente (83 códigos, 5 runtimes).
- `docs/grammar/cortex-1.0.{ebnf,abnf}` + `docs/schemas/ast-schema-1.0.json`.
- `conformance/1.0/` — 70 vectores válidos migrados + 2 inválidos
  (I012 estricto, G007 `cortex:1`) con manifiesto.
- Dispatcher Python acepta `cortex:1.0` (→ slotparser); parsers Go, Node,
  Rust y Bash aceptan `cortex:1.0` en su subconjunto implementado y
  registran `cortex_version`.
- `slotmigrate to-1.0` — reescritura idempotente de la línea format con
  reporte y verificación de parseo.
- Aridad posicional estricta (`I012_POSITIONAL_ARITY`) implementada en las
  5 superficies — la tolerancia de overflow de 0.1 queda corregida.

### Añadido — archivado

- `archive/2026-11/` — archivo fechado del material deprecado (916
  archivos movidos con `git mv`): evidencia exploratoria pre-BLP-003,
  artefactos de gates F2–F4, herramientas de fase y revisión documental.
  Congelado bajo `archive/2026-11/SHA256SUMS` (915 archivos) con índice y
  reglas propias; los reportes antiguos llevan cabecera de deprecación.
- Punteros al archivo desde `README.md` y `docs/index.md`.

### Cambiado

- `tests/SHA256SUMS` regenerado sobre el corpus vivo `conformance` +
  `examples/`, 829 archivos) tras retirar los reportes archivados del
  sello.
- Documentación pública renovada (commit `fcbfb97`): tabla de
  distribución honesta (solo PyPI publicado), sección Nivel A, evidencia
  exploratoria re-etiquetada.
- Referencias corregidas a rutas archivadas en `codec-cortex-go/README.md`,
  `skill/codec-cortex.skill.md` y specs en `docs/standard/`
  (`REV-PROTOCOL`, `REV-PACKAGE-GUIDE`, `GATE-F2`, `CORTEX-SPEC-0.1`,
  `hcortex-0.1`).

## [1.0.0-rc.1] — 2026-10-10

Publicado en PyPI como `codec-cortex 1.0.0rc1` (pre-release; `latest` en PyPI
permanece en 0.6.2).

### Añadido

- Dialecto **CORTEX 0.2 (SLOTS)**: `slotparser`, `slotc14n`, `slothcortex`,
  `slotmigrate`, `slotharness` + spec `CORTEX-SPEC-SLOTS.md`, `C14N-SLOTS.md`,
  `hcortex-slots.md` + dispatcher por `$0:format{cortex:X}`.
- `bench/` — harness del certificado Nivel A (D1–D6) con preregistro,
  corpus held-out sellado y scorer mecánico (BLP-003).
- `.github/workflows/certificate.yml` — certificado reproducible en CI:
  compila los runtimes Go y Rust antes de medir paridad.
- `tests/SHA256SUMS` — sello del corpus (845 archivos).
- `instrument_sha256` en el certificado — el hash del instrumento queda
  ligado para detectar deriva entre corridas.
- `bench/results/audit.sig` — firma del Nivel A por auditor independiente
  (Heimdall), tras re-ejecución y verificación byte-exacta contra el wheel
  de PyPI (2026-11-01).

### Cambiado

- Licencia ratificada a **Apache-2.0** con atribución obligatoria,
  homologada en las cinco superficies (`LICENSE`, `NOTICE`, `AUTHORS.md`).
- `go.mod` corregido a la ruta real del repositorio
  (`github.com/FidelErnesto03/codec-cortex/codec-cortex-go`).
- URLs de `pyproject.toml` corregidas al repositorio real.
- Paridad D3 ampliada a **5/5 runtimes** (bash, go, node, python, rust).

### Corregido

- Binarios precompilados Go en `bin/` reconstruidos (estaban obsoletos y
  fallaban `S005` sobre el corpus; la fuente era correcta).
- `.pyc` retirados del índice de git.

## [0.6.2] — 2026-07

Última línea estable previa al candidato 1.0. Ver tags `v0.x` para el
historial detallado.
