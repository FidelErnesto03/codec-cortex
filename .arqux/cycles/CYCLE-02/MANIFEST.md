---
cycle_id: "CYCLE-02"
name: "Hardening"
project_ref: "CODEC-CORTEX"
status: "closed"
governor: "alfred"
created_at: "2026-07-17T23:41:12Z"
quality_gates@: "{"
has_clear_purpose: "true,"
has_explicit_scope: "true,"
has_measurable_objectives: "true,"
has_operational_guidelines: "true,"
has_control_points: "true,"
aligns_with_project: "true,"
closed_at: "2026-07-18T14:57:04Z"
---


# Manifiesto: CYCLE-02 — Hardening

## §1: Propósito

Endurecer CODEC-CORTEX para su publicación. CYCLE-01 definió el formato y demostró su validez. CYCLE-02 cierra deudas técnicas: parser Python débil (23/40), documentación insuficiente, y ausencia de release público.

## §2: Alcance

**Dentro:**
- Robustecer parser Python a 40/40
- Documentación pública para adopción externa
- Publicar release v1.0.0-rc.1 en PyPI y GitHub

**Fuera:**
- Nuevas features (VIEW, Fase 5)
- Más implementaciones en otros lenguajes
- Revisiones externas (se dejan a la comunidad)

## §3: Objetivos

- [ ] **CYC-OBJ-1:** Parser Python alcanza 40/40 en corpus F4
- [ ] **CYC-OBJ-2:** Documentación pública lista para adopción externa
- [ ] **CYC-OBJ-3:** Release v1.0.0-rc.1 publicado en PyPI y GitHub

## §4: Directrices

1. Toda corrección debe validarse contra los 40 casos del corpus F4
2. El parser Go es referencia viva — consultar su lógica ante duda
3. No cambiar la API pública de parse_cortex()

## §5: Puntos de Control

| ID | Tipo | Descripción | Criterio |
|---|---|---|---|
| CP-01 | Validación | Parser 40/40 | 40 casos F4 sin error |
| CP-02 | Validación | Documentación | README + skill completos |
| CP-03 | Release | Publicación | PyPI + GitHub tag |

## §6: Blueprints

| BLP ID | Título | Estado | Prioridad | Objetivo | Gobernador |
|---|---|---|---|---|---|
| BLP-001 | Parser Python 40/40 | draft | high | CYC-OBJ-1 | alfred |
| BLP-002 | Documentación pública | pending | high | CYC-OBJ-2 | alfred |
| BLP-003 | Publicar release v1.0.0-rc.1 | pending | high | CYC-OBJ-3 | alfred |

## §7: Reglas del Ciclo

1. No usar `patch` directo en archivos de gobernanza — solo MCP handlers
2. Cada BLP debe completarse en una sola pasada, sin placeholders
3. El Arquitecto revisa y aprueba cada BLP antes de ejecución
