# ISSUE: Divergencia 5 superficies: namespace con . / - pierde la idea en render->compile (Python/Go/Node/Rust) pero Bash la con…
# Severity: high | Status: fixed | Handler: alfred | Date: 2026-11-14

## PROBLEM
Al renderizar una idea con namespace que contiene '.' o '-' (p. ej. 'tenant.x::KNW:alpha') el marcador HCORTEX es '### tenant.x::KNW:alpha'. El _IDEA_MARKER_RE de Python/Go/Node/Rust usa '\w+::' y NO reconoce el namespace, por lo que la idea se pierde al recompilar (0 ideas, sin diagnostico). La superficie Bash si la reconoce y conserva la idea. Divergencia PREEXISTENTE al 1.0.1 (verificada con probe: python/go/node/rust emiten L406 (antes L499), bash emite reporte limpio con reversible=true). Impacto: los 5 'surfaces' NO son byte-identicos para entradas con namespace ./-; el corpus certificado (D6 75/75) no usa namespaces con ./- por lo que no se ve afectado. Fix propuesto: ampliar _IDEA_MARKER_RE (y equivalentes) para aceptar namespace '[a-z][a-z0-9_.-]*'. Evidencia: tests/test_lossreport.py::test_compile_side_drop_is_classified.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-14T21:54:43Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-14

Resuelto: se alineo el marcador HCORTEX de Python/Go/Node/Rust a la gramatica CORTEX (namespace [a-z][a-z0-9_.-]*; nombre imprimible), de modo que la idea ya no se pierde y las 5 superficies coinciden (hash 437ad6ef... en las cinco). D6 75/75 PASS; go/rust/node/ python tests OK. L406 queda como guardia clasificada sin disparador en el corpus.
