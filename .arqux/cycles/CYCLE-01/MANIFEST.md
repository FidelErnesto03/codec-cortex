---
cycle_id: "CYCLE-01"
name: "CYCLE-01"
project_ref: ""
status: "closed"
governor: "alfred"
created_at: "2026-07-17T00:28:12Z"
updated_at: ""
closed_at: "2026-07-17T23:41:02Z"
planned_start: ""
planned_end: ""
quality_gates@: "{"
has_clear_purpose: "true,"
has_explicit_scope: "true,"
has_measurable_objectives: "true,"
has_operational_guidelines: "true,"
has_control_points: "true,"
aligns_with_project: "true,"
_template_ref: "CYCLE_MANIFEST_TEMPLATE.md"
---


# Manifiesto: {name}

> Documento rector del ciclo. Define identidad, alcance, objetivos, directrices y puntos de control. Fuente de verdad para todos los Blueprints dentro de este ciclo.

---

## §1: Propósito

Convertir CORTEX/HCORTEX en un verdadero codec estándar, determinista y autocontenido para representar contexto de agentes SLM/LLM. Este ciclo funda el proyecto sobre una base limpia y establece la constitución normativa del estándar, basándose en `CCX-CORE-PROJECT-PLAN-001`.

**Relación con los objetivos del proyecto:**
Contribuye al objetivo estratégico del plan: crear un estándar abierto, pequeño, estable e independientemente implementable (compacto, determinista, autocontenido, extensible, neutral, reversible, auditable, interoperable, LLM-independent, adecuado para SLM/LLM).


## §2: Alcance y Límites

**Dentro del alcance de este ciclo:**
- Fase 0 — Seguridad, congelación y fork limpio (ya iniciada vía Clean-Root).
- Fase 1 — Constitución del estándar (documentos entregados como draft).
- Repositorio principal reordenado en la raíz `CODEC-CORTEX/` con gobierno ArqUX (`.arqux/`).
- Dirección de dependencias unidireccional aprobada (standard → codec-cortex → profiles/tools → runtime/learning/ArqUX).
- Inventario de componentes heredados v0.6.x y política de imports.
- Ejecución del Gate F1 (revisor externo) o asignación de owner + fecha.

**Fuera del alcance (excluido explícitamente):**
- Fase 2 — Modelo abstracto y gramática Draft 0.1.
- Fase 3 — Canonicalización y equivalencia.
- Fase 4 — HCORTEX Draft 0.1.
- Fase 5 — Implementación de referencia 0.1 (Python).
- Fase 6 — Conformance Suite 0.1.
- Fase 7 — Segunda implementación independiente.
- Fase 8 — Perfiles oficiales.
- Fase 9 — Benchmark científico.
- Fase 10/11 — RC y Standard 1.0.

> Lo que está fuera del alcance NO debe ser abordado por ningún Blueprint de este ciclo.


## §3: Objetivos

Objetivos concretos y medibles del ciclo. Cada Blueprint debe contribuir al menos a uno. Ver CYC-OBJ-1..5 abajo.

- [ ] **CYC-OBJ-1:** Cero secretos en el historial del repositorio (secret scanning + purge) — criterio: scan limpio y recovery codes rotados.
- [ ] **CYC-OBJ-2:** Repositorio histórico v0.6.x congelado y archivado como `codec-cortex-legacy` en estado `historical-experimental / not-standard`.
- [ ] **CYC-OBJ-3:** Charters y constitución del estándar aprobados y versionados con hashes registrados (CORTEX-CHARTER, CORTEX-CONSTITUTION, GOVERNANCE, TERMINOLOGY).
- [ ] **CYC-OBJ-4:** Política de imports / dirección de dependencias documentada y aprobada (sin imports inversos a runtime/learning/ArqUX).
- [ ] **CYC-OBJ-5:** Gate F1 ejecutado — un revisor externo comprende qué es CORTEX sin leer código (owner + fecha si no se cierra en el ciclo).


## §4: Directrices

Directrices operacionales que rigen todos los Blueprints de este ciclo. Ver directrices 1-4 abajo.

1. CODEC-CORTEX es exclusivamente un codec determinista (parser, encoder, decoder, validator, canonicalizer). No runtime, learning, sesiones, memoria, framework de gobierno, orquestador, MCP, ni producto ArqUX.
2. La especificación es autoridad superior al código (P8); el comportamiento del código no normaliza el estándar.
3. El proceso de cambio normativo se modela como Blueprint ArqUX, no como CEP/RFC.
4. Ningún Blueprint se cierra sin ejecutar las validaciones y gates requeridos (P9: sin autocertificación).

**Directrices para creación de Blueprints:**
1. Cada Blueprint debe referenciar el objetivo del ciclo (CYC-OBJ-N) al que contribuye.
2. Los Blueprints críticos deben incluir un plan de reversión.
3. Cada Blueprint debe respetar los principios constitucionales P1–P10 del plan.


## §5: Puntos de Control

Hitos, revisiones y puntos de validación. La ejecución se detiene en cada punto.

| ID | Tipo | Fecha Planificada | Descripción | Criterio de Aprobación |
|---|---|---|---|---|
| CP-01 | Revisión de Seguridad | 2026-07-17 | Cierre de incidente de credenciales y scan limpio | Sin secretos en historial; recovery codes rotados |
| CP-02 | Control de Constitución | 2026-07-17 | Documentos Fase 1 versionados con hashes | CHARTER/CONSTITUTION/GOVERNANCE/TERMINOLOGY en repo + SHA256 |
| CP-03 | Revisión Final / Gate F1 | por definir | Aprobación de ciclo y ejecución de Gate F1 | Cero BLOCKER/HIGH; F1 con owner+fecha o superado |

> Los puntos de control son obligatorios. El gobernador debe informar al Arquitecto al aproximarse a uno.


## §6: Blueprints (Índice)

Índice breve de los Blueprints asignados a este ciclo.

| BLP ID | Título | Estado | Prioridad | Objetivo | Gobernador |
|---|---|---|---|---|---|
| BLP-001 | Fase 0 + Fase 1 completadas | done | high | CYC-OBJ-2/CYC-OBJ-3 | alfred |
| BLP-002 | Fase 2 — Integracion CORTEX 0.1 REAL | done | high | CYC-OBJ-3 | alfred |
| BLP-003 | Mini Gate F2 — 3 agentes + orden CORTEX | done | high | CYC-OBJ-5 | alfred |
| BLP-004 | Correccion spec: comillas, atom, glossary-valid | done | high | CYC-OBJ-3 | alfred |
| BLP-005 | Mini Gate F2 v2 — Post correcciones | done | high | CYC-OBJ-5 | alfred |
| BLP-006 | Fase 3 — Integracion canonicalizacion C14N-0.1 | done | high | CYC-OBJ-3 | alfred |
| BLP-007 | CE-2 — Implementacion Rust C14N-0.1 | done | high | CYC-OBJ-3 | alfred |
| BLP-008 | Fase 4 — Integracion HCORTEX Draft 0.1 | done | high | CYC-OBJ-3 | alfred |
| BLP-009 | Correccion bugs alta prioridad — REV F3+F4 | done | high | CYC-OBJ-3 | alfred |
| BLP-010 | Redefinicion HCORTEX — esquemas explicitos | done | high | CYC-OBJ-3 | alfred |
| BLP-011 | Transformer HCORTEX bidireccional + roundtrip | done | high | CYC-OBJ-3 | alfred |


## §7: Estado y Métricas

**Estado actual:** draft
**Total Blueprints:** 0 | **Draft:** 0 | **Madurando:** 0 | **Ready:** 0 | **En Progreso:** 0 | **Done:** 0
**Progreso:** 0%
**Próximo punto de control:** CP-03 — Gate F1
**Iniciado:** 2026-07-17 | **Fin planificado:** por definir


## §8: Reglas del Ciclo

Reglas específicas de este ciclo.

1. El proceso de cambio normativo se modela como Blueprint ArqUX, no como CEP/RFC.
2. La especificación es autoridad superior al código (P8 del plan).
3. Todo Blueprint debe mapear a un objetivo CYC-OBJ del ciclo.
4. Ningún Blueprint se cierra sin ejecutar los gates requeridos (P9: sin autocertificación).
5. CYCLE-01 NO se cierra hasta la completitud de las 11 fases del CCX-CORE-PROJECT-PLAN-001 (F0→F10). Cada fase se entrega como BLP; el ciclo sólo cierra cuando la última fase (F10) esté en `done`.


## §9: Contrato de Calidad

| Compuerta | Estado |
|---|---|
| has_clear_purpose | ✅ |
| has_explicit_scope | ✅ |
| has_measurable_objectives | ✅ |
| has_operational_guidelines | ✅ |
| has_control_points | ✅ |
| aligns_with_project | ✅ |

> Todas las compuertas deben estar en ✅ antes de cycle.ready(). Ver blueprint-workflow skill, §4.1.
