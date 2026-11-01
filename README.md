# CODEC-CORTEX

Codec ideático reversible entre IA y humanos. La IA lee y escribe **CORTEX** directamente; el humano lee **HCORTEX**, la representación renderizada mediante esquemas visuales emparejados.

Dialectos soportados: **CORTEX 0.1** (superficie fundamental) y **CORTEX 0.2 — SLOTS** (eje de codificación por slots explícitos, ortogonal a 0.1). El dialecto se declara con `$0:format{cortex:X}` y el despachador enruta automáticamente.

## Ejemplo

CORTEX es para la IA. HCORTEX es para humanos.

Así se ve un HCORTEX (humano):

```markdown
<!-- HCORTEX v=0.1 t=canonical k=corpus -->

## §1: TAREAS

<!-- table:1 -->
| Aprender HCORTEX | current |
| Escribir documentacion | planned |
<!-- /table:1 -->
```

Ese HCORTEX se compila a CORTEX (que la IA entiende):

```cortex
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:es}
OBJ:task{type:attrs,weight:H,fields:"goal:text|status:%state",focus:goal,schema:table,desc:"Tarea"}
$1:CORE
OBJ:meta{goal:"Aprender HCORTEX",status:current}
OBJ:gate{goal:"Escribir documentacion",status:planned}
```

## Implementaciones

Cinco superficies funcionalmente equivalentes. Paridad verificada por el
certificado Nivel A (ver abajo): las cinco producen el mismo hash
`CORTEX-C14N-0.1` sobre el vector semilla.

| Lenguaje | Directorio | Distribución |
|---|---|---|
| Python (referencia) | `codec_cortex/` | `pip install codec-cortex` (PyPI: `1.0.0rc1`) |
| Rust | `codec-cortex-rs/` | No publicado en crates.io — compilar con `cargo build --release` |
| Go | `codec-cortex-go/` | `go get github.com/FidelErnesto03/codec-cortex/codec-cortex-go` — binarios vía `make dist` |
| Node.js | `codec-cortex-node/` | No publicado en npm — usar local: `npm install ./codec-cortex-node` |
| Bash | `codec-cortex-bash/` | Sourceable: `bin/codec-cortex` |

## Nivel A — certificado determinista

`bench/certify.py` ejecuta el certificado del Nivel A (sin dependencia de
ningún LLM) y emite `bench/results/certificate.json`:

| Indicador | Resultado |
|---|---|
| D1 idempotencia C14N | 70/70 |
| D2 roundtrip HCORTEX 0.2 byte-exacto | 30/30 |
| D3 paridad cross-runtime | 5/5 (bash, go, node, python, rust) |
| D4 no-pérdida | 70/70 |
| D5 sensibilidad a tamper | PASS |
| D6 contraste de determinismo | CORTEX varianza 0 vs LLM varianza > 0 (R=5) |

El certificado se genera en CI ([`.github/workflows/certificate.yml`](.github/workflows/certificate.yml)),
es reproducible por terceros y está firmado por auditor independiente
(`bench/results/audit.sig`). El hash del instrumento
(`instrument_sha256`) queda ligado en el certificado para detectar
deriva entre corridas.

## Documentación

- [docs/parser-api.md](docs/parser-api.md) — API del parser Python (instalación, uso, ejemplos)
- [docs/standard/CORTEX-SPEC-0.1.md](docs/standard/CORTEX-SPEC-0.1.md) — Especificación CORTEX 0.1
- [docs/standard/CORTEX-SPEC-SLOTS.md](docs/standard/CORTEX-SPEC-SLOTS.md) — CORTEX 0.2 (SLOTS)
- [docs/standard/hcortex-0.1.md](docs/standard/hcortex-0.1.md) — HCORTEX 0.1 (5 esquemas emparejados)
- [docs/standard/hcortex-slots.md](docs/standard/hcortex-slots.md) — HCORTEX 0.2
- [docs/standard/C14N-0.1.md](docs/standard/C14N-0.1.md) — Canonicalización
- **Creación de sigilos:** [docs/authoring/custom-sigils.md](docs/authoring/custom-sigils.md)
- **Plantillas HCORTEX:** [docs/authoring/hcortex-templates.md](docs/authoring/hcortex-templates.md)
- **Inicio rápido:** [docs/QUICKSTART.md](docs/QUICKSTART.md)

### Skill autocontenido (para LLMs)

El estándar CORTEX escrito en CORTEX — cubre 0.1 y 0.2. Cualquier modelo lo lee como `.md`.

[skill/codec-cortex.skill.md](skill/codec-cortex.skill.md) — pip install, parse, render, compile, canonicalize, todo en un archivo.

## Evidencia exploratoria (pre-BLP-003)

Pruebas informales anteriores al benchmark riguroso (~20 ejecuciones,
modelos sin identificar nominalmente, sin repeticiones ni intervalos de
confianza) sugirieron comprensión, durabilidad y generación favorables de
CORTEX frente a JSON/YAML/XML.

**Estado:** evidencia exploratoria, no conforme a Art. XVII. Está siendo
re-medida con rigor (pre-registro, R=5, IC, auditoría ciega) bajo
[`bench/preregistration.yaml`](bench/preregistration.yaml). Las únicas
afirmaciones con respaldo reproducible hoy son las del
[certificado Nivel A](#nivel-a--certificado-determinista).

Los reportes originales y demás material supersedido (gates F2–F4,
herramientas de fase, revisión documental) están congelados bajo sello en
[`archive/2026-11/`](archive/2026-11/README.md) — evidencia histórica, no
autoridad vigente.

## Licencia

**Apache License 2.0** — ver [`LICENSE`](LICENSE).

Uso comercial, modificación y redistribución permitidos, sin copyleft.
La redistribución **debe** mantener la atribución a **Fidel Ernesto Lozada A.**
como autor original. Ese requisito es obligatorio por la sección 4(d) de la
licencia y por [`NOTICE`](NOTICE), que debe acompañar a toda distribución.

El proyecto no puede presentarse como obra propia. Los colaboradores se
registran en [`AUTHORS.md`](AUTHORS.md).
