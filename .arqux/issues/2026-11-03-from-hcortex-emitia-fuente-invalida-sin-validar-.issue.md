# ISSUE: from-hcortex emitia fuente invalida sin validar: el compilador construia AST directo desde markdown y no chequeaba su s…
# Severity: medium | Status: fixed | Handler: Alfred | Date: 2026-11-03

## PROBLEM
from-hcortex emitia fuente invalida sin validar: el compilador construia AST directo desde markdown y no chequeaba su salida (homoglifo ### USR:аdmin compilaba a USR:аdmin con exit 0). Resuelto via Opcion A del Arquitecto: auto-validacion del canonico emitido en compile_hcortex_slots -> falla con diagnostico del parser. Norma: CORTEX-SPEC-1.0 S8.1. Port pendiente E-0224.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-04T00:02:23Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-03

Implementado: compile_hcortex_slots re-parsea canonicalize(doc) antes de retornar; si falla, devuelve diags con codigo del parser y None. Verificado: homoglifo ### USR:аdmin -> U003 exit 1; roundtrip 100/100 corpus 1.0+slots; skill mirror compila+valida. Spec S8.1 declara la norma. Port go/node/rs/bash -> E-0224.
