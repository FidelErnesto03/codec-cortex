# CODEC-CORTEX — Documentación

CORTEX 0.1 es un codec ideático reversible entre IA y humanos.

---

## Primera lectura

- [QUICKSTART.md](QUICKSTART.md) — Guía de 5 minutos con ejemplo funcional
- [parser-api.md](parser-api.md) — API del parser Python (instalación, uso)

### Para LLMs (skill autocontenido)

- [skill/codec-cortex.skill.md](../skill/codec-cortex.skill.md) — El estándar escrito en CORTEX. Leer + responder produce CORTEX válido.

## Especificaciones

- [CORTEX-SPEC-0.1.md](standard/CORTEX-SPEC-0.1.md) — Formato CORTEX 0.1 completo
- [hcortex-0.1.md](standard/hcortex-0.1.md) — HCORTEX con 5 esquemas emparejados
- [C14N-0.1.md](standard/C14N-0.1.md) — Canonicalización (hash determinista)

## Authoring (creación de contenido)

- [authoring/custom-sigils.md](authoring/custom-sigils.md) — Crear sigilos y secciones personalizadas
- [authoring/hcortex-templates.md](authoring/hcortex-templates.md) — Plantillas HCORTEX bidireccionales

## Implementaciones

| Lenguaje | Directorio | C14N |
|---|---|---|
| Python | `codec_cortex/` | 40/40 |
| Rust | `codec-cortex-rs/` | 40/40 |
| Go | `codec-cortex-go/` | 40/40 |
| Node.js | `codec-cortex-node/` | 40/40 |
| Bash | `codec-cortex-bash/` | 40/40 |

## Validación

4 pruebas con ~20 ejecuciones en 6 plataformas. Ver [tests/](../tests/).
