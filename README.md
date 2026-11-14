# CODEC-CORTEX

Codec ideático determinista entre máquinas y humanos. La IA lee y escribe
**CORTEX**; el humano lee **HCORTEX**, su proyección renderizada mediante
esquemas visuales emparejados.

El proyecto no es un formato más: es un **contrato de permanencia**. Un documento
`cortex:1.0` válido hoy lo será siempre; el hash canónico depende del significado
y no del formato editorial, y toda pérdida de roundtrip está declarada con
nombre propio y verificada en cinco implementaciones independientes.

## El lenguaje

**CORTEX 1.0** es el canon normativo único. Unifica la superficie fundamental
(0.1) y el eje de codificación por slots (0.2) en un solo dialecto, con aridad
posicional estricta, catálogo de errores cerrado y superficie de pérdida
declarada.

Los dialectos `0.1` y `0.2` siguen siendo **legibles** como alias de lectura;
la escritura canónica es siempre `cortex:1.0`. Los textos 0.x están archivados
como evidencia en [`archive/2026-11/standard-0x/`](archive/2026-11/standard-0x/).

- Canon: [`docs/standard/CORTEX-SPEC-1.0.md`](docs/standard/CORTEX-SPEC-1.0.md)
- Errores: [`docs/standard/errors-1.0.md`](docs/standard/errors-1.0.md)
- Gramática: [`docs/grammar/cortex-1.0.ebnf`](docs/grammar/cortex-1.0.ebnf)
- Vectores normativos: [`conformance/1.0/`](conformance/1.0/)

## Ejemplo

CORTEX es para la IA. HCORTEX es para humanos.

```cortex
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
$0:enum_state{values:"current|planned|done"}
OBJ:task{type:attrs,weight:H,focus:goal,desc:"Tarea",fields:"goal:text|status:%state"}
$1: TAREAS:CORE
OBJ:learn{goal:"Aprender HCORTEX",status:current}
OBJ:docs{goal:"Escribir documentacion",status:planned}
```

```bash
python -m codec_cortex to-hcortex tareas.cortex    # CORTEX -> HCORTEX (humano)
python -m codec_cortex from-hcortex tareas.md      # HCORTEX -> CORTEX (máquina)
python -m codec_cortex loss-report tareas.cortex   # qué se pierde en el viaje
```

Salida exacta de `to-hcortex` para el documento anterior:

```markdown
<!-- HCORTEX v=1.0 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
$0:enum_state{values:"current|planned|done"}
OBJ:task{type:attrs,weight:H,focus:goal,desc:"Tarea",fields:"goal:text|status:%state"}

<!-- /glossary -->

## §1: TAREAS

<!-- schema:1 capa:CORE -->
### OBJ:learn
| goal | status |
|---|---|
| "Aprender HCORTEX" | current |

### OBJ:docs
| goal | status |
|---|---|
| "Escribir documentacion" | planned |

<!-- /schema:1 -->
```

HCORTEX 1.0 se produce como **función pura del AST**: mismo documento, mismos
bytes, en cualquiera de las cinco superficies. Un compilador nunca emite fuente
inválida: si la salida canónica no parsea, falla con el diagnóstico del parser.

## Implementaciones

Cinco superficies con comportamiento equivalente, verificadas por el
certificado del proyecto (D3 y D3b: hash y render byte-exactos entre todas).

| Lenguaje | Directorio | Ejecutable | Distribución |
|---|---|---|---|
| Python (referencia) | `codec_cortex/` | `python -m codec_cortex` | PyPI `codec-cortex 1.0.1` |
| Go | `codec-cortex-go/` | `codec-cortex` | `go get` + `make dist` |
| Node.js | `codec-cortex-node/` | `codec-cortex-node` | local: `npm install ./codec-cortex-node` |
| Rust | `codec-cortex-rs/` | `cortex` | `cargo build --release` (no publicado) |
| Bash | `codec-cortex-bash/` | `codec-cortex` | sourceable, requiere `jq` |

## CLI

Los cinco exponen el mismo núcleo. Python además ofrece `migrate` y
`conformance`; Go y Bash añaden harness histórico; Rust añade `compare` e
`inspect`.

| Comando | Qué hace |
|---|---|
| `parse <file>` | AST en JSON (dispatcher 0.1/0.2/1.0) |
| `validate <file>` | válido → exit 0; inválido → diagnóstico |
| `canonicalize <file>` | bytes canónicos C14N-1.0 |
| `hash <file>` | hash canónico con dominio separado por versión |
| `to-hcortex <file>` | render HCORTEX determinista |
| `from-hcortex <file>` | compila HCORTEX y auto-valida la salida |
| `loss-report <file\|->` | **pérdidas declaradas** en JSON canónico |

`loss-report` es la novedad del canon 1.0: nombra toda información de la fuente
que no sobrevive al viaje CORTEX → HCORTEX → CORTEX, con catálogo cerrado y
guardia `L499_UNCLASSIFIED_LOSS`. Ver [`docs/LOSS-REPORT.md`](docs/LOSS-REPORT.md).

## Certificado determinista

[`bench/certify.py`](bench/certify.py) no depende de ningún LLM: re-ejecuta el
corpus sellado y produce [`bench/results/certificate.json`](bench/results/certificate.json).

| Indicador | Qué verifica | Resultado |
|---|---|---|
| D1 | idempotencia de C14N | 141/141 |
| D2 | roundtrip HCORTEX byte-exacto | 141/141 |
| D2b | vectores HCORTEX 1.0 | 70/70 |
| D3 | paridad cross-runtime (hash) | 5/5 superficies |
| D3b | paridad de render HCORTEX | 101/101 |
| D4 | no-pérdida estructural | 141/141 |
| D5 | sensibilidad a tamper | PASS |
| D6 | paridad de `loss-report` en las 5 superficies | 75/75 |
| D7 | contrato del dialecto 0.1 (G042 + `$0` desnudo) | 10/10 |

Reproducir:

```bash
python -m bench.certify          # emite certificate.json + veredicto
sha256sum -c --quiet tests/SHA256SUMS   # sello del corpus (986 entradas)
```

El certificado se ejecuta en CI
([`.github/workflows/certificate.yml`](.github/workflows/certificate.yml)) y está
**firmado por un auditor independiente** en
[`bench/results/audit.sig`](bench/results/audit.sig) (auditoría 1.8,
`SIGNED-PASS`). La firma es verificable por recomputo:

```bash
python bench/verify_audit.py     # exit 0 = firma y artefactos consistentes
```

## Documentación

| Documento | Para qué |
|---|---|
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | primer documento en 5 minutos |
| [docs/standard/CORTEX-SPEC-1.0.md](docs/standard/CORTEX-SPEC-1.0.md) | canon normativo (gramática, C14N, HCORTEX, errores, conformidad) |
| [docs/standard/errors-1.0.md](docs/standard/errors-1.0.md) | catálogo de errores cerrado (código ↔ emisor ↔ superficie) |
| [docs/LOSS-REPORT.md](docs/LOSS-REPORT.md) | pérdidas declaradas: catálogo, JSON, límites |
| [docs/MIGRATION-1.0.md](docs/MIGRATION-1.0.md) | cambios incompatibles y recetas de migración |
| [docs/parser-api.md](docs/parser-api.md) | API Python y referencia de CLI |
| [bench/agent-package/](bench/agent-package/README.md) | paquete instructivo `.cortex` para que un agente autónomo benchmarkee el codec |
| [docs/authoring/custom-sigils.md](docs/authoring/custom-sigils.md) | crear sigilos y secciones |
| [docs/authoring/hcortex-templates.md](docs/authoring/hcortex-templates.md) | plantillas HCORTEX bidireccionales |
| [archive/2026-11/](archive/2026-11/README.md) | material histórico congelado bajo sello |

### Skill autocontenido (para LLMs)

El estándar escrito en CORTEX: cualquier modelo lo lee como `.md` y responde
CORTEX válido. Cubre 1.0, el catálogo de pérdidas y los comandos.

- [`skill/codec-cortex.skill.md`](skill/codec-cortex.skill.md) — fuente
- [`skill/codec-cortex.skill.hcortex.md`](skill/codec-cortex.skill.hcortex.md) — misma verdad en HCORTEX

## Evidencia exploratoria (pre-BLP-003)

Pruebas informales anteriores al benchmark riguroso (~20 ejecuciones, modelos
sin identificar nominalmente, sin repeticiones ni intervalos de confianza)
sugirieron comprensión, durabilidad y generación favorables de CORTEX frente a
JSON/YAML/XML.

**Estado:** evidencia exploratoria, no conforme a Art. XVII. Está siendo
re-medida con rigor (pre-registro, R=5, IC, auditoría ciega) bajo
[`bench/preregistration.yaml`](bench/preregistration.yaml). Las únicas
afirmaciones con respaldo reproducible hoy son las del certificado.

## Licencia

**Apache License 2.0** — ver [`LICENSE`](LICENSE).

Uso comercial, modificación y redistribución permitidos, sin copyleft. La
redistribución **debe** mantener la atribución a **Fidel Ernesto Lozada A.** como
autor original: requisito obligatorio por la sección 4(d) de la licencia y por
[`NOTICE`](NOTICE), que debe acompañar a toda distribución.

El proyecto no puede presentarse como obra propia. Los colaboradores se
registran en [`AUTHORS.md`](AUTHORS.md).
