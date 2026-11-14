# ISSUE: U10: cortex check via stdin
# Severity: low | Status: fixed | Handler: Alfred | Date: 2026-11-03

## PROBLEM
Lokky C3-U10: iterar linea por linea exige crear archivo. cortex check - o stdin: echo 'USR:x{...}' | cortex check -. Ergonomia de prueba rapida.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-04T00:10:37Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-14

FIXED 2026-11-14 (SES004). _read_source() generalizado en __main__.py: cualquier argumento archivo puede ser '-' (lee sys.stdin). Cubre validate, parse, canonicalize, hash, loss-report, to-hcortex, from-hcortex, diff y verify (ambos operandos). Verificado E2E con pipe a 'validate -'. Tests en test_api.py — 47/47 OK.
