# ISSUE: Enum %name no valida dominio en 1.0 pese a spec §77 (spec↔impl divergentes)
# Severity: high | Status: fixed | Handler: alfred | Date: 2026-11-03

## PROBLEM
Detectado durante la verificación de la revisión NEX (excede su sugerencia B3 de strict-mode): la spec 1.0 §77 declara "Enum valida contra enum_<n>" pero el slotparser solo registra la declaración (`doc.glossary.enums`) y nunca valida el valor. Prueba: `status:maybe` en campo `status:%state` con `$0:enum_state{values:"active|done"}` → `validate` devuelve "valid", exit 0. Campos requeridos sí se chequean (I008 verificado). Divergencia spec↔implementación: o se implementa la validación de dominio enum, o se corrige la spec. Prioridad alta porque el claim de "manifiesto verificable" depende de esto.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-03T23:35:29Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-03

Decision del Arquitecto: implementar lo prometido. Implementado en slotparser.py: _check_enum_value resuelve microtokens antes de comparar dominio; I010_ENUM_VIOLATION en paths attrs/slots/attrs-pos; G026_UNKNOWN_ENUM_REFERENCE en _post_validate para referencias %enum no declaradas. errors-1.0.md actualizado (G026+I010 emitidos, G026 sale de reservados). Verificado: status:maybe->I010, %nodeclared->G026, micro cur->current pasa.
