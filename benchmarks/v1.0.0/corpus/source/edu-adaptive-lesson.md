# edu-adaptive: stu_3301 / algebra-basics

## Identity
- **Agent**: tutor-agent-v2
- **Role**: adaptive learning

## Constraints
- **no_frustration** (blocking): 3 fallos consecutivos => reducir dificultad
- **coppa** (blocking): no PII para estudiantes < 13 anos

## Focus
Adaptar leccion algebra-basics para stu_3301

## Objective
Estudiante alcanza 80% mastery en subtopic eq-lineal

- Status: in_progress
- Success: 3 ejercicios consecutivos correctos

## Work State
- Phase: adaptacion
- Current: 2 fallos consecutivos en eq-lineal-2, dificultad=medium
- Blocked: false

## Next Step
Reducir dificultad a easy y ofrecer hint guiado

## Risks
- **boredom** (medium): 5 aciertos consecutivos sin subir dificultad causa abandono. Mitigation: auto-bump.

## Claims
- Mantener dificultad en zona proximal desarrollo mejora retencion 35% (Vygotsky pilot 2025).

## Limits
- Sesion maximo 30 minutos continuos.
