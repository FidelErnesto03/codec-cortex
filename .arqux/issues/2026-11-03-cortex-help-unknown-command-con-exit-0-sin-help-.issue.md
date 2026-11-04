# ISSUE: cortex --help → "Unknown command" con exit 0: sin help y sin código de error en CLI
# Severity: medium | Status: fixed | Handler: alfred | Date: 2026-11-03

## PROBLEM
Reportado por revisión externa NEX (H5) y verificado localmente: `python3 -m codec_cortex --help` imprime "Unknown command: --help" y sale con código 0. Dos defectos: (a) no existe comando help/usage — es la primera puerta de todo evaluador externo; (b) comando desconocido devuelve exit 0, lo que rompe scripting y CI (debería ser exit != 0 + usage a stderr). Fix trivial en codec_cortex/__main__.py.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-03T23:35:29Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-03

Lokky C3-U1 suma contexto: es la primera puerta del viaje real del usuario. Sugerencia extra: cortex help <cmd> por comando, no solo help global.

## UPDATE 2026-11-03

--help y help <cmd> implementados en python -m codec_cortex; unknown command sigue exit 2. Pendiente solo el equivalente CLI en superficies no-Python.
