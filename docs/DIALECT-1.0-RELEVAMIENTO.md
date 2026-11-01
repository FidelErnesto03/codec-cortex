# Relevamiento — Camino al dialecto CORTEX 1.0

**Fecha:** 2026-11-01 · **Autor:** Alfred (loop A-H) · **Alcance:** dialectos CORTEX, HCORTEX, C14N, implementaciones, corpus, errores.
**Propósito:** determinar qué existe, qué funciona con excelencia, qué falta, y cómo debe escribirse el canon definitivo 1.0 — incluido el HCORTEX producido determinísticamente por los conversores.

---

## 1. Lo que hay (inventario verificado en ejecución)

### 1.1 Dialectos y documentos normativos

| Artefacto | Estado declarado | Realidad |
|---|---|---|
| `CORTEX-SPEC-0.1.md` | `draft-for-independent-implementation` | **Borrador** — §32 pendiente de Gate F2; § canónico "pendiente de Fase 3" |
| `CORTEX-SPEC-SLOTS.md` (0.2) | `normative-draft` | Borrador normativo |
| `C14N-0.1.md`, `C14N-SLOTS.md` | canonización por dialecto | Implementada, hash dominio-separado |
| `hcortex-0.1.md`, `hcortex-slots.md` | proyección humana | Implementada, envelope v=0.1/v=0.2 |
| `docs/grammar/` | `cortex.{ebnf,abnf}`, `cortex-slots.{ebnf,abnf}` | Gramática machine-readable por dialecto |
| `docs/schemas/` | 7 esquemas JSON (AST, diagnósticos, hcortex, loss-report) | Contratos de artefactos |
| Catálogos `errors*.md` (4) | 144 prefijos de código catalogados | Ver §3.2 |

### 1.2 Implementaciones (5 superficies)

| Superficie | Parser 0.1 | Parser 0.2 | C14N | HCORTEX↔CORTEX | CLI |
|---|---|---|---|---|---|
| Python `codec_cortex` | ✅ | ✅ slotparser | ✅ c14n+slotc14n | ✅ hcortex+slothcortex | 9 comandos |
| Go | ✅ | ✅ slotparser.go | ✅ | ✅ hcortex.go | 8 comandos |
| Node | ✅ | ✅ slotparser.js | ✅ slotc14n.js | ✅ | 6 comandos |
| Rust | ✅ | ✅ slotparser.rs | ✅ | ✅ hcortex.rs | clap subcomandos |
| Bash | ✅ | ✅ slot-parser.sh | ✅ slot-c14n.sh | ✅ | librería `ccx_*` |

Paridad D3 medida en certificado: **5/5 runtimes** sobre el mismo digest canónico.

### 1.3 Corpus de conformidad (sellado, 829 archivos)

`conformance/corpus/valid` 40 · `slots/valid` 30 · `slots/invalid` 35 · `hcortex` 281 · `c14n` 187 — los 70 casos del certificado D1/D4 (40+30 válidos) más 8 archivos held-out del benchmark. Probes P01–P29: 29/29. Conformance slots: 67/67.

### 1.4 Conversores (los que producen el canon)

`parse` · `validate` · `canonicalize` · `hash` · `to-hcortex` · `from-hcortex` · `migrate` · `conformance` · `explain-loss` · `harness` (legacy F3/F4).

---

## 2. Lo que funciona con excelencia

1. **Determinismo verificado end-to-end**: canonicalización idempotente byte-exacta (`canon(canon(x))==canon(x)`), hash dominio-separado estable, render HCORTEX byte-estable entre corridas.
2. **Paridad real 5/5**: cinco implementaciones producen el mismo digest canónico — verificado en CI por un tercero (GitHub Actions) y firmado por auditor independiente (`bench/results/audit.sig`).
3. **Dispatch por versión correcto**: `cortex:X` es la única señal; sin inferencia por `※` (I058).
4. **Corpus sellado + instrumento ligado**: `tests/SHA256SUMS` + `instrument_sha256` — deriva detectable.
5. **El skill es ejemplo vivo**: parsea bajo ambos dialectos tras el fix de aridad (commit `8edbac3`).
6. **Catálogo de errores sin códigos huérfanos**: los 69 códigos emitidos por el código existen todos en el catálogo.

## 3. Lo que debemos mejorar (gaps verificados)

| # | Gap | Evidencia |
|---|---|---|
| 1 | **Specs en borrador** — 0.1 `draft-for-independent-implementation`, 0.2 `normative-draft`; orden canónico marcado "pendiente" | No hay base normativa firmada para llamar "1.0" |
| 2 | **Parser 0.1 laxo en aridad posicional** — acepta más celdas que el contrato; 0.2 lo rechaza (`I012`) | Hallazgo real hoy: `HDL:migrate` (7 celdas/3 campos) pasaba en 0.1 |
| 3 | **67 códigos catalogados sin emisor Python** (familia H4xx, L41x, I002–I016, G-reservados) | `comm` de catálogo vs fuentes — pueden vivir en otras superficies o ser reservados; falta mapa canónico código↔superficie |
| 4 | **Roundtrip HCORTEX con pérdida declarada** — `from-hcortex` pierde bloques ```` ``` ```` en casos 0.1 (existe `explain-loss` para declararlas) | Pérdida conocida pero sin catálogo cerrado de casos aceptables |
| 5 | **`docs/spec/` duplicado byte-exacto** de `docs/standard/` | Confirmado por `diff -q` → archivar |
| 6 | **Dialecto `.arqux` interno** — glosarios solo en comentarios; no pasa parser estricto | Deuda del framework ArqUX (handlers) |
| 7 | **Nombrado inconsistente** — spec 0.2 se llama `CORTEX-SPEC-SLOTS.md` (por feature), no `CORTEX-SPEC-0.2.md` (por versión) | Confunde el mapa de versiones |
| 8 | **Sin spec 1.0** — no existe documento que declare congelación, deprecación y contrato de permanencia | Es el entregable siguiente |

## 4. Cómo debe escribirse el canon definitivo 1.0

### 4.1 Principios de congelación

- **CORTEX 1.0 = unión normativa de 0.1 + 0.2** sin dialectos nuevos: `$0:format{cortex:1.0}` acepta la superficie 0.1 y el eje slots como *un solo* lenguaje. 0.1/0.2 quedan como alias de lectura hacia atrás.
- **Una señal de versión, una sola vez** — se conserva el dispatch por `$0:format`.
- **Congelación significa**: ninguna regla puede cambiar sin bump de versión; todo lo válido en 1.0 es válido siempre.

### 4.2 Contratos que el canon debe cerrar (hoy abiertos)

1. **Aridad posicional estricta** — adoptar el comportamiento 0.2 (`I012`) como norma 1.0; el laxismo 0.1 se declara bug, no feature.
2. **Catálogo de errores cerrado** — cada código DEBE tener: emisor en ≥1 superficie de referencia, sección spec, y entrada en el mapa código↔superficie. Los 67 sin emisor: o se implementan o se retiran del canon.
3. **Superficie de pérdida HCORTEX declarada** — el canon 1.0 DEBE enumerar las transformaciones con pérdida permitida (como el bloque fence), cada una con justificación y código `L4xx`. `explain-loss` pasa de diagnóstico a **parte del contrato**.
4. **Orden canónico final** — el punto "pendiente de Fase 3" debe resolverse y fijarse por texto + vector dorado.

### 4.3 El canon HCORTEX determinista (requisito del Arquitecto)

El HCORTEX "producido de forma determinística por los programas de conversión" exige en el canon:

- **Render = función pura del AST**: mismo documento CORTEX → mismos bytes HCORTEX siempre, en las 5 superficies. Hoy Python lo cumple; el canon DEBE exigirlo cross-runtime con vector de paridad en CI.
- **Orden fijado**: secciones por `$N` ascendente, ideas por orden de documento, glosario por orden de declaración — sin ordenación por hash ni por azar de iteración.
- **Roundtrip con clase**: canon declara dos clases — `LOSSLESS` (byte-exacto tras canonicalize) y `DECLARED-LOSS` (cada pérdida nombrada con código). Nada intermedio.
- **Sin copia oculta** (H481) — la regla ya existe; el canon la eleva a invariante normativa: ningún render válido puede esconder AST para fingir reversibilidad.
- **Vector de conformidad HCORTEX**: para cada archivo `.cortex` del corpus, su `.md` esperado byte-exacto — hoy existe en `conformance/hcortex` (281 archivos); el canon los promueve a **vectores normativos 1.0**.

### 4.4 Estructura propuesta del documento 1.0

`CORTEX-SPEC-1.0.md` = fusión normativa (no copia) de: gramática única, shapes, eje slots, escalares, glosario, namespaces, extensiones, canonicalización C14N-1.0, HCORTEX-1.0 (render + compilación + pérdida declarada), catálogo de errores cerrado, conformidad y niveles de implementación. Las specs 0.1/0.2 se archivan como históricas con sello — mismo patrón que `archive/2026-11/`.

## 5. Ruta sugerida (para decisión del Arquitecto)

1. BLP nuevo: "Dialecto 1.0" — congelación + fusión de specs + cierre de los 4 contratos abiertos.
2. Fix `I012` en parser 0.1 (rompe pocos casos reales: el skill fue el único hallado).
3. Mapa código↔superficie de errores + poda del catálogo.
4. Vectores de paridad HCORTEX cross-runtime en CI (extender D3 a render).
5. Renombrar/alinear `CORTEX-SPEC-SLOTS.md` → convenio por versión.
6. `docs/spec/` → `archive/`.

*Bloqueo conocido:* la firma de la spec 1.0 y la promoción de borradores a normativo es decisión del Arquitecto (Gate), no del ejecutor.
