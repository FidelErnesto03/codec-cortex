# Gate F2 v1 — Mini Gate F2 (BLP-003)

**Date:** 2026-07-17
**Spec baseline:** CORTEX 0.1 DRAFT-REAL-001 (pre-correcciones BLP-004)

## Descripción

Primer experimento de implementabilidad independiente. Tres agentes genéricos recibieron orden de misión en CORTEX y construyeron parsers usando solo los artefactos normativos, sin acceso al validador Python.

## Resultados

| Implementación | Válidos | Inválidos | Estado |
|---|---|---|---|
| Go | 37/40 (92%) | 51/57 (89%) | ✅ Funcional |
| Rust | — | — | Código completo, sin compilar (no rustc) |
| Bash | — | — | Timeout |

## Hallazgos

- 9 discrepancias contra golden outputs
- F2-F001: regla de comillas incorrecta (solo focus debe llevar quotes)
- 6 casos inválidos aceptados como válidos por Go

## Contenido

| Archivo | Descripción |
|---|---|
| `mission-rust.cortex` | Orden de misión para agente Rust |
| `mission-go.cortex` | Orden de misión para agente Go |
| `mission-bash.cortex` | Orden de misión para agente Bash |
| `go/` | Parser Go v1 (~1500 líneas, binario compilado) |
| `rust/` | Código fuente Rust v1 (~79KB, no compiló) |
| `GATE-F2-MINI-REPORT.md` | Reporte del experimento (copia) |

> El reporte canónico de este experimento está en `docs/review/GATE-F2-MINI-REPORT.md`.
