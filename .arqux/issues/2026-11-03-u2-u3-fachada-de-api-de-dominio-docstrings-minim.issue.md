# ISSUE: U2+U3: fachada de API de dominio + docstrings minimos
# Severity: medium | Status: fixed | Handler: Alfred | Date: 2026-11-03

## PROBLEM
Lokky C3-U2: API Python expone internals (compile_hcortex_slots devuelve tupla doc|None+diags, modulos por nombre de archivo). Fachada cc.parse/cc.from_hcortex/cc.to_hcortex/cc.hash con nombres de dominio; capa actual queda interna. Incluye U3: docstrings de una linea por funcion publica.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-04T00:10:33Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-14

FIXED 2026-11-14 (SES004). Fachada de dominio en codec_cortex/api.py: parse, validate, canonicalize, hash, hash_source, to_hcortex, from_hcortex + CompileError con .diagnostics. Modulos internos (parser, slotparser, slothcortex, hcortex) preservados. Docstrings de una linea en funciones publicas del facade y wrappers clave (slothcortex, lossreport). Tests: tests/test_api.py — 47/47 OK.
