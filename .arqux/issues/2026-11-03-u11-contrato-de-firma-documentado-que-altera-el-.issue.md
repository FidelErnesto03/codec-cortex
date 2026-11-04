# ISSUE: U11: contrato de firma documentado — que altera el hash y que no
# Severity: high | Status: fixed | Handler: Alfred | Date: 2026-11-03

## PROBLEM
Lokky C3-U11: hoy los hechos de hash (orden attrs normalizado, extras open UTF-8 NFC, whitespace ignora, NFC normaliza, dialecto separa) estan dispersos en C14N-0.1 y SPEC-1.0 S7. Un firmante no debe descubrirlos empiricamente. Documento normativo unico: tabla que altera/no altera el hash. Prerequisito de confianza para firmar.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-04T00:10:28Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-03

Cerrado via BLP-004 fase B: nueva seccion spec S7.1 Contrato de firma — altera/no altera el hash + consecuencia operativa (verificar=canonicalizar+rehash; diff de firma=diff canonico). Bug colateral: dominio de hash en S7.6 era incorrecto ('CORTEX\x00' vs CORTEX-C14N-0.x real) — corregido.
