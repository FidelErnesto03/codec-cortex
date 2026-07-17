# Gate F2 v2 — Mini Gate F2 post correcciones (BLP-005)

**Date:** 2026-07-17
**Spec baseline:** CORTEX 0.1 DRAFT-REAL-001 (post BLP-004: focus-only quotes, atom formal, glossary-valid)

## Descripción

Segundo experimento de implementabilidad independiente, replicando el diseño del v1 pero con la especificación corregida tras los hallazgos del primer experimento. Tres agentes genéricos recibieron orden de misión en CORTEX (`mission-current.cortex`).

## Resultados

| Implementación | Válidos | Inválidos | Estado |
|---|---|---|---|
| **Rust** | **39/40 (97.5%)** | 35/57 (61%) | ✅ Primera impl. independiente funcional |
| Go | 33/40 (82.5%) | 50/57 (87.7%) | ✅ Parser reescrito, requiere debugging |
| Bash | 30/40 (75%) | 57/57 (100%) | ✅ Shell scripting |

## Hallazgos

- **0 defectos de especificación.** Todos los fallos son bugs de implementación (Rust: 1 falso positivo, Go: 2 familias de bugs, Bash: limitaciones de shell)
- Las correcciones de BLP-004 (comillas, atom, glossary-valid) validadas experimentalmente
- CORTEX como formato de handoff entre agentes: CONFIRMADO

## Contenido

| Archivo | Descripción |
|---|---|
| `mission-rust-v2.cortex` | Orden de misión para agente Rust v2 |
| `mission-go-v2.cortex` | Orden de misión para agente Go v2 |
| `mission-bash-v2.cortex` | Orden de misión para agente Bash v2 |
| `mission-current.cortex` | Orden activa del experimento |
| `go-v2/` | Parser Go v2 (reescrito, con bugs de multilínea/namespace) |
| `rust/` | Parser Rust v2 (~2100 líneas, compilado, 97.5%) |
| `bash-v2/` | Parser Bash v2 (~550 líneas, 30/40 válidos) |
| `GATE-F2-V2-REPORT.md` | Reporte con análisis de fallos (copia) |

> El reporte canónico de este experimento está en `docs/review/GATE-F2-V2-REPORT.md`.
