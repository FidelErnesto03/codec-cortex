# Entrega de Fase 1 — Constitución del estándar CORTEX

**Document ID:** `CORTEX-PHASE1-DELIVERY-001`  
**Status:** `complete-draft-set`  
**Date:** `2026-07-16`

## Entregables

| Archivo | Función | Estado |
|---|---|---|
| `CORTEX-CHARTER.md` | propósito, dominio, non-goals, frontera y éxito | draft-for-ratification |
| `CORTEX-CONSTITUTION.md` | principios superiores y prohibiciones del núcleo | draft-for-ratification |
| `GOVERNANCE.md` | roles, autoridad, decisiones, releases y compatibilidad (motor ArqUX) | draft-for-ratification |
| `TERMINOLOGY.md` | vocabulario normativo y términos heredados | draft-for-ratification |

## Cobertura del trabajo de Fase 1

| Requisito del plan | Documento principal |
|---|---|
| propósito | Charter |
| dominio | Charter |
| non-goals | Charter + Constitution |
| terminología | Terminology |
| principios | Constitution |
| modelo de versiones | Governance |
| proceso de cambio normativo | Governance (motor ArqUX: Blueprints del proyecto CODEC-CORTEX) |
| gobierno | Governance |
| compatibilidad | Charter + Governance |

## Decisiones arquitectónicas consolidadas

- CORTEX es estándar de representación, no runtime ni sistema de aprendizaje.
- CODEC-CORTEX es implementación de referencia, no autoridad normativa.
- HCORTEX-CANONICAL deriva universalmente del AST.
- VIEW queda fuera del camino base y solo puede existir como extensión.
- Los vocabularios de agentes son perfiles, no palabras reservadas.
- La implementación Python no puede definir el estándar por comportamiento.
- No existe pérdida silenciosa.
- La canonicalización debe ser idempotente.
- La conformidad requiere revisión independiente.
- La línea experimental se migra mediante bridge externo y loss report.

## Decisiones pendientes que requieren ratificación explícita

1. Licencia final de especificaciones, código y corpus.
2. Identidad de las personas que ocuparán cada rol inicial.
3. Composición efectiva del primer Consejo del Estándar.
4. Repositorios y nombres definitivos.
5. Fecha formal de ratificación.

Estas decisiones no impiden evaluar el Gate F1, pero deben cerrarse antes de aceptar contribuciones externas sustantivas o iniciar un draft normativo ejecutable.

## Gate F1 — Protocolo de evaluación

Un revisor externo debe leer exclusivamente los cinco documentos y responder un cuestionario de comprensión. El gate se aprueba cuando:

- obtiene al menos 90% de respuestas correctas;
- no confunde estándar, codec, HCORTEX, perfiles y runtime;
- identifica todos los non-goals críticos;
- explica la jerarquía normativa;
- describe correctamente el proceso de cambio;
- no necesita consultar código ni historia del proyecto.

### Preguntas mínimas

1. ¿Qué representa CORTEX?
2. ¿Qué diferencia existe entre CORTEX y CODEC-CORTEX?
3. ¿Cuál es la función de HCORTEX-CANONICAL?
4. ¿Puede el núcleo contener learning o sesiones?
5. ¿Son `FCS` y `OBJ` palabras reservadas?
6. ¿Qué autoridad prevalece si el código contradice la especificación?
7. ¿Qué exige una transformación destructiva?
8. ¿Cuándo se requiere una revisión mayor?
9. ¿Quién puede certificar una capacidad implementada por el Arquitecto Principal?
10. ¿Qué compatibilidad se promete con v0.6.x?
11. ¿Cuándo es obligatorio un Blueprint de cambio normativo en ArqUX?
12. ¿Qué diferencia existe entre perfil y extensión?

## Criterio de cierre documental

La Fase 1 puede declararse documentalmente completa cuando:

- los cinco archivos están versionados en `cortex-standard`;
- se registran sus hashes;
- no existen contradicciones entre ellos;
- las decisiones pendientes tienen owner y fecha objetivo;
- un revisor externo supera el Gate F1;
- se emite acta de ratificación o lista de correcciones.
