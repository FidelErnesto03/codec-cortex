# CODEC-CORTEX

**CORTEX 0.1** — Un lenguaje de máquina para modelos de lenguaje (LLM/SLM).

Codec ideático reversible entre IA y humanos. La IA lee y escribe CORTEX directamente. El humano lee HCORTEX, la representación renderizada mediante 5 esquemas visuales emparejados.

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
$0:format{cortex:0.1,encoding:UTF-8,language:es}
OBJ:task{type:attrs,weight:H,fields:"goal:text|status:%state",focus:goal,schema:table,desc:"Tarea"}
$1:CORE
OBJ:meta{goal:"Aprender HCORTEX",status:current}
OBJ:gate{goal:"Escribir documentacion",status:planned}
```

## Repositorio

| Lenguaje | Directorio | C14N | Publicación |
|---|---|---|---|
| Python (oficial) | `codec_cortex/` | 40/40 | `pip install codec-cortex` |
| Rust | `codec-cortex-rs/` | 40/40 | `cargo add codec-cortex` |
| Go | `codec-cortex-go/` | 40/40 | GitHub Releases |
| Node.js | `codec-cortex-node/` | 40/40 | `npm install @codec-cortex/node` |
| Bash | `codec-cortex-bash/` | 40/40 | GitHub Releases |

## Documentación

- [docs/parser-api.md](docs/parser-api.md) — API del parser Python (instalación, uso, ejemplos)
- [docs/standard/CORTEX-SPEC-0.1.md](docs/standard/CORTEX-SPEC-0.1.md) — Especificación CORTEX
- [docs/standard/hcortex-0.1.md](docs/standard/hcortex-0.1.md) — HCORTEX con 5 esquemas emparejados
- [docs/standard/C14N-0.1.md](docs/standard/C14N-0.1.md) — Canonicalización
- **Creación de sigilos:** [docs/authoring/custom-sigils.md](docs/authoring/custom-sigils.md)
- **Plantillas HCORTEX:** [docs/authoring/hcortex-templates.md](docs/authoring/hcortex-templates.md)
- **Inicio rápido:** [docs/QUICKSTART.md](docs/QUICKSTART.md)

### Skill autocontenido (para LLMs)

El estándar CORTEX escrito en CORTEX. Cualquier modelo lo lee como .md.

[skill/codec-cortex.skill.md](skill/codec-cortex.skill.md) — pip install, parse, render, compile, canonicalize, todo en un archivo.

## Validación empírica

4 pruebas con ~20 ejecuciones en 6 plataformas:
- **Comprensión:** 6/6 modelos entienden CORTEX sin parseo
- **Durabilidad:** 4/5 modelos mantienen directrices 25+ turnos
- **Generación:** 5/5 modelos escriben CORTEX desde cero
- **Benchmark:** CORTEX supera a JSON/YAML/XML en multi-hop

## Licencia

CC0-1.0 — Dominio público.
