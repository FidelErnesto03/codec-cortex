# ISSUE: U8+U5: diagnosticos con sugerencia — did-you-mean y forma esperada
# Severity: medium | Status: fixed | Handler: Alfred | Date: 2026-11-03

## PROBLEM
Lokky C3-U8+U5: I001 no dice que sigilos SI existen (did-you-mean por edicion o listado); I004 dice el shape pero no la forma esperada (Expected { for shape bloque -> BLQ:name{...}). Sugerencias contextuales en diagnosticos G/I.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-04T00:10:37Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-14

FIXED 2026-11-14 (SES004). Nuevo codec_cortex/diagnostics.py: undeclared_sigil_message (did-you-mean via difflib.get_close_matches, determinista — pool y resultados ordenados; fallback 'Declared sigils: ...') y expected_form (forma concreta por shape: attrs/cuerpo/bloque/attrs-pos/relacion + slots). Aplicado en parser.py (0.1), slotparser.py y slotc14n.py (I001 en canonicalize). Codigos y orden de precedencia intactos — solo mejora el mensaje. Verificado E2E: 'Undeclared sigil: KNZ. Did you mean: KNW?'. Tests: test_api.py DiagnosticMessageTest + test_diagnostics.py precedencia — 47/47 OK.
