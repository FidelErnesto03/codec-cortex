# CODEC-CORTEX

Implementación de referencia del estándar CORTEX — un codec ideático lineal para contexto estructurado de SLM/LLM.

## Estructura del repositorio

```
docs/
├── standard/       → Especificación normativa CORTEX 0.1 (spec, glossary, errors, GATE-F2, F3-CHARTER)
├── grammar/        → Gramáticas formales ABNF + EBNF
├── schemas/        → Schemas JSON del AST y diagnostics
├── spec/           → Symlinks a standard/ (para validadores)
└── review/         → Reportes de revisión, hallazgos y documentos de diseño

experiments/
├── gate-f2-v1/     → Mini Gate F2 (BLP-003) — experimento pre-correcciones
└── gate-f2-v2/     → Mini Gate F2 v2 (BLP-005) — experimento post-correcciones

conformance/        → Corpus de prueba (40 válidos + 57 inválidos + golden outputs)
examples/           → Symlinks a conformance/ (para validadores)

tools/              → Validadores (validate_phase2.py, cortex01_validator.py, compare_all.py)
governance/         → GOVERNADANCE.md del estándar + ADRs
profiles/           → Perfiles oficiales del estándar
security/           → Documentación de seguridad
tooling/            → Herramientas del ecosistema
```

## Estado del estándar

**CORTEX 0.1 — DRAFT-REAL-001** · Status: `draft-for-independent-implementation`

| Fase | Estado | BLP |
|---|---|---|
| F0 — Seguridad y fork | ✅ Done | BLP-001 |
| F1 — Constitución | ✅ Done | BLP-001 |
| F2 — Modelo abstracto y gramática | ✅ Done | BLP-002 |
| F2 correcciones (comillas, atom, glossary-valid) | ✅ Done | BLP-004 |
| Mini Gate F2 (implementabilidad) | ✅ Done | BLP-003 + BLP-005 |
| F3 — Canonicalización | ⬜ Pendiente | — |

Experimentación: Rust 39/40 (97.5%), Go 33/40, Bash 30/40. 0 defectos de especificación.

## Lectura recomendada

1. `docs/standard/CORTEX-SPEC-0.1.md` — La especificación
2. `docs/standard/F3-CHARTER.md` — Guía para Fase 3
3. `experiments/gate-f2-v2/README.md` — Resultados del último experimento
4. `docs/review/GATE-F2-V2-REPORT.md` — Reporte detallado
