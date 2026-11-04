# ISSUE: Duplicados de sigil:name silenciosos en dialecto 0.1 (en 1.0 ya lanza I006)
# Severity: low | Status: fixed | Handler: alfred | Date: 2026-11-03

## PROBLEM
Verificación de H2/H6 de la revisión NEX: en `cortex:1.0` el parser ya lanza `I006_DUPLICATE_IDEA_ADDRESS` (slotparser.py:499) — el hallazgo NO reproduce por vía canónica en el dialecto actual; el claim de Lokky probablemente midió el parser legado o una construcción distinta. En `cortex:0.1` sí reproduce: dos `KNW:codec` en la misma sección → `validate` → "valid", exit 0, sin diagnóstico. Decisión pendiente del Arquitecto: backport de I006 al parser 0.1 (el dialecto sigue soportado — migrate, corpus legado) o declarar wontfix-legacy y documentarlo.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-03T23:35:29Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-03

Decision del Arquitecto: backport OK. Implementado en parser.py (0.1): seen_idea_addresses en parse_cortex, duplicado -> I002_DUPLICATE_IDEA_ADDRESS (codigo del catalogo 0.1, errors.md par.4.4). Verificado: dos KNW:codec en misma seccion -> I002 @ 6:0, exit 1. En 1.0 sigue I006.
