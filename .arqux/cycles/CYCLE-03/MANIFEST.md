---
# Plantilla de Manifiesto de Ciclo (CYCLE_MANIFEST_TEMPLATE.md)
# Copiada por cycle.create() para crear CYCLE-NNN/MANIFEST.md
# Formato HCORTEX — legible por humanos y máquinas

cycle_id: "CYCLE-03"
name: "Remediación BLP-003 capas corticales"
project_ref: ""
status: "draft"
governor: "alfred"
created_at: "2026-07-18T16:11:47Z"
updated_at: ""
closed_at: ""
planned_start: ""
planned_end: ""
quality_gates@: {
  has_clear_purpose: false,
  has_explicit_scope: false,
  has_measurable_objectives: false,
  has_operational_guidelines: false,
  has_control_points: false,
  aligns_with_project: false,
}
_template_ref: "CYCLE_MANIFEST_TEMPLATE.md"
---



# Manifiesto: {name}

> Documento rector del ciclo. Define identidad, alcance, objetivos, directrices y puntos de control. Fuente de verdad para todos los Blueprints dentro de este ciclo.

---

## §1:

Este ciclo gobierna la evolución de CODEC-CORTEX hacia su release candidate: remediar brechas de cobertura y gobernar la incorporación de aportes externos al repo canónico mediante auditoría independiente previa al merge.

**Relación con los objetivos del proyecto:**
Contribuye a OBJ:default (cobertura de capas corticales y cerebro de gobernanza coherente con el filesystem) y a la maduración del codec hacia v1.0.0-rc con evidencia reproducible.
## §2:

**Dentro del alcance de este ciclo:**
- Remediación de cobertura de capas corticales en archivos del proyecto.
- Auditoría y merge canónico del paquete externo codec-cortex-0.2-remediation.

**Fuera del alcance (excluido explícitamente):**
- Publicación a PyPI o cualquier canal de release.
- Cambios a la especificación CORTEX 0.1.
## §3:

- [ ] **CYC-OBJ-1:** Todo aporte externo al repo canónico es auditado por identidad independiente (Heimdall) antes de merge — criterio: veredicto registrado como evidencia.
- [ ] **CYC-OBJ-2:** La superficie del repositorio usa nombres canónicos sin versión embebida — criterio: cero archivos con versión en nombre/referencia tras el merge.
- [ ] **CYC-OBJ-3:** Toda remediación incorporada queda respaldada por evidencia reproducible — criterio: suite 0.1 + conformidad + puertos verdes post-merge.
## §4:

1. Ningún archivo, programa ni esquema declara versión como parte de su nombre, referencia o esquema de implementación. Versión canónica del proyecto: v1.0.0-rc.
2. Ningún Blueprint se cierra sin ejecutar todas las validaciones requeridas.
3. Los Blueprints críticos incluyen plan de reversión (restaurar desde git/backup).
4. Las dependencias entre Blueprints se resuelven antes de que el dependiente comience.

**Directrices para creación de Blueprints:**
1. Cada Blueprint referencia el objetivo del ciclo al que contribuye.
2. Cada Blueprint estima su impacto en los criterios de éxito del ciclo.
## §5:

| ID | Tipo | Fecha Planificada | Descripción | Criterio de Aprobación |
|---|---|---|---|---|
| CP-01 | Control Intermedio | 2026-07-20 | Auditoría Heimdall del paquete 0.2-remediation | Veredicto emitido con evidencia reproducible |
| CP-02 | Revisión Final | 2026-07-20 | Merge canónico por Jarvis | Nombres canónicos sin versión; suite 0.1 + conformidad + puertos verdes |
## §6:

| BLP ID | Título | Estado | Prioridad | Objetivo | Gobernador |
|---|---|---|---|---|---|
| (pendiente) | Se auto-poblará al crear Blueprints | - | - | - | alfred |
## §7:

**Estado actual:** active
**Próximo punto de control:** CP-01 — 2026-07-20
**Iniciado:** 2026-07-18 | **Fin planificado:** 2026-07-21
## §8:

1. Ningún merge al canónico sin veredicto de auditoría registrado como evidencia.
2. Nombres canónicos sin versión en toda la superficie importada.
## §9:

| Compuerta | Estado |
|---|---|
| has_clear_purpose | ✅ |
| has_explicit_scope | ✅ |
| has_measurable_objectives | ✅ |
| has_operational_guidelines | ✅ |
| has_control_points | ✅ |
| aligns_with_project | ✅ |
