# ISSUE: Orden de attrs altera el hash en 1.0 sin declaración de spec (I007 muerto)
# Severity: high | Status: fixed | Handler: alfred | Date: 2026-11-03

## PROBLEM
Reportado por revisión externa NEX (H1) y verificado: en CORTEX 1.0, permutar el orden de attrs de una idea `type:attrs` produce hash distinto (la emisión canónica sigue orden documental — slotc14n.py línea ~301 `for k, v in pairs`). La spec 1.0 fija orden documental para IDEAS (§7.2) pero no declara la semántica del orden de ATTRS en sigilos cerrados. Además `I007_FIELD_ORDER` está declarado en docs/standard/errors.md (0.1) y no está implementado en ninguna parte del paquete (grep: 0 hits). En 0.1 el canónico normaliza a orden de contrato (SPEC-0.1 §590). Impacto: dos emisores que ordenen distinto producen firmas distintas sobre el mismo manifiesto — relevante para el uso firmable que NEX evalúa. Decisión de spec pendiente del Arquitecto: declarar el orden documental de attrs como semántico en 1.0, o restaurar normalización a orden de contrato.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-03T23:35:29Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-03

Decision del Arquitecto: normalizar a orden de contrato (opcion de eficiencia). Implementado: slotc14n.py emite attrs via _sort_keys_canonical(pairs, contract order) — extras open ordenados UTF-8 NFC tras el contrato. Spec §7 punto 4 agregado declarando la regla. Verificado: permutacion de attrs en 1.0 produce mismo hash (63cd37...); corpus 364/364 sin drift canonicos.
