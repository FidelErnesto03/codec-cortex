# ISSUE: U4: helper publico de emision ideatica (escapado) — SDK writing
# Severity: high | Status: fixed | Handler: Alfred | Date: 2026-11-03

## PROBLEM
Lokky C3-U4: cada consumidor reinventa esc() para comillas/newlines/tabs. emit_string_literal existe en scalars pero no es API publica. Proponer cc.emit(...) de primera clase: produce linea ideatica valida y escapada. Mayor ganancia ergonomica segun revisor.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-04T00:10:28Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-14

FIXED 2026-11-14 (SES004). Implementado codec_cortex/emit.py + export cc.emit en codec_cortex/__init__.py. Soporta attrs, attrs-pos/relacion, cuerpo y bloque; namespaces calificados; validacion de sigilos/namespaces/names/attr-keys segun gramatica real (sin whitespace ni {}| en names; sin : , {} en keys). Escapes via emit_string_literal (comillas, newlines, tabs). Rechaza sigilos invalidos, shapes desconocidos y payloads incorrectos. Tests: tests/test_api.py (EmitTest) — suite 47/47 OK.
