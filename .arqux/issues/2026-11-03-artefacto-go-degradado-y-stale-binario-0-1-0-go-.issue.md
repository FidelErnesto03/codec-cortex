# ISSUE: Artefacto Go degradado y stale: binario 0.1.0-go falla en corpus 0.1 (S005) tras release 1.0.0
# Severity: high | Status: fixed | Handler: alfred | Date: 2026-11-03

## PROBLEM
Reportado por revisión externa NEX (Lokky, 2026-11-03) y ya declarado en bench/RESULTS-SUMMARY.md: el binario precompilado codec-cortex-go lanza S005_CONTENT_OUTSIDE_SECTION sobre el corpus 0.1 y figura en certificate.json → D3.runtimes_failed=["go"]. Además el binario en bin/ reporta versión `0.1.0-go` cuando el release es 1.0.0 — artefacto distribuido stale que corroe el certificado por ósmosis. Verificado localmente: el binario actual corre y produce hash idéntico a Python en docs 1.0, pero el artefacto publicado está degradado y desactualizado. La propia nota del bench dice "pendiente: issue propia" y nunca se creó. Acción: rebuild de binarios Go desde fuente limpia, re-ejecutar conformidad, actualizar versión del artefacto y re-sellar.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-03T23:35:29Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-03

Go 1.0 port completado: U003, G014, G026, I010, I002, orden canonico de attrs, dominio de hash por version, auto-validacion HCORTEX, marcador Unicode-aware. Binarios reconstruidos 5 plataformas (1.0.0-go + SHA256SUMS). go test verde; hash paridad 63cd37b7.
