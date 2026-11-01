# CODEC-CORTEX — Documentación

Codec ideático reversible entre IA y humanos. Dialectos: **CORTEX 0.1** y **CORTEX 0.2 (SLOTS)**.

---

## Primera lectura

- [QUICKSTART.md](QUICKSTART.md) — Guía de 5 minutos con ejemplo funcional
- [parser-api.md](parser-api.md) — API del parser Python (instalación, uso)

### Para LLMs (skill autocontenido)

- [skill/codec-cortex.skill.md](../skill/codec-cortex.skill.md) — El estándar escrito en CORTEX (0.1 + 0.2). Leer + responder produce CORTEX válido.

## Especificaciones

- **[CORTEX 1.0](standard/CORTEX-SPEC-1.0.md)** — canon normativo draft (unifica 0.1+0.2)
- [Errores 1.0](standard/errors-1.0.md) — catalogo cerrado codigo-emisor-superficie
- [Gramatica 1.0](grammar/cortex-1.0.ebnf) + [AST schema](schemas/ast-schema-1.0.json)
- [Vectores 1.0](../conformance/1.0/) — corpus normativo

- [CORTEX-SPEC-0.1.md](standard/CORTEX-SPEC-0.1.md) — Formato CORTEX 0.1 completo
- [CORTEX-SPEC-SLOTS.md](standard/CORTEX-SPEC-SLOTS.md) — CORTEX 0.2 (SLOTS)
- [hcortex-0.1.md](standard/hcortex-0.1.md) — HCORTEX con 5 esquemas emparejados
- [hcortex-slots.md](standard/hcortex-slots.md) — HCORTEX 0.2
- [C14N-0.1.md](standard/C14N-0.1.md) — Canonicalización (hash determinista)
- [C14N-SLOTS.md](standard/C14N-SLOTS.md) — Canonicalización 0.2

## Authoring (creación de contenido)

- [authoring/custom-sigils.md](authoring/custom-sigils.md) — Crear sigilos y secciones personalizadas
- [authoring/hcortex-templates.md](authoring/hcortex-templates.md) — Plantillas HCORTEX bidireccionales

## Implementaciones

| Lenguaje | Directorio | Distribución |
|---|---|---|
| Python (referencia) | `codec_cortex/` | PyPI `codec-cortex 1.0.0rc1` |
| Rust | `codec-cortex-rs/` | No publicado — `cargo build --release` |
| Go | `codec-cortex-go/` | `go get github.com/FidelErnesto03/codec-cortex/codec-cortex-go` |
| Node.js | `codec-cortex-node/` | No publicado — `npm install ./codec-cortex-node` |
| Bash | `codec-cortex-bash/` | Sourceable: `bin/codec-cortex` |

## Validación

Certificado Nivel A reproducible en CI y firmado por auditor independiente:
D1 idempotencia 140/140 · D2 roundtrip HCORTEX 140/140 · D3 paridad
cross-runtime 5/5 · D4 no-pérdida 70/70 · D5 tamper PASS · D6 contraste
determinismo CORTEX varianza 0.

Artefactos: [`bench/results/certificate.json`](../bench/results/certificate.json) ·
[`bench/results/audit.sig`](../bench/results/audit.sig) · corpus sellado en
[`tests/SHA256SUMS`](../tests/SHA256SUMS).

Material histórico supersedido (evidencia exploratoria pre-BLP-003, gates
F2–F4, herramientas de fase): [`archive/2026-11/`](../archive/2026-11/README.md),
congelado bajo su propio sello.
