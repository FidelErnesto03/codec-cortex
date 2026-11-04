# ISSUE: Port de los fixes enum/orden/duplicados a Go/Node/Rust/Bash + vectores invalidos de corpus
# Severity: medium | Status: fixed | Handler: alfred | Date: 2026-11-03

## PROBLEM
Tras los fixes de SES003 (E-0220/E-0221/E-0222), las mismas divergencias siguen vivas en las 4 superficies no-Python: (a) orden de attrs — Go/Node/Rust/Bash probablemente emiten en orden documental aun (paridad rota ante docs con attrs permutados: mismo doc, hash distinto por superficie); (b) enum — I010/G026 solo emiten en Python; (c) duplicados — I006 existe en 1.0 Python; verificar presencia en otras superficies y en el parser 0.1 de cada una. Ademas el corpus normativo no tiene vectores invalidos para I010/G026/I002 — agregarlos exige que las 5 superficies los superen. Alcance: portar los 3 chequeos a las 4 superficies + agregar vectores invalidos (I010_enum_violation, G026_unknown_enum_reference, I002_duplicate_idea_address-0.1) + re-ejecutar certificado D3/D3b y re-sellar. Relacionado con issue del binario Go (E-0211) — conviene hacerlos juntos.

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-03T23:43:05Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-03

Port completo go/node/rs/bash: U003 (nombre, clave, label, decl $0, campo contrato), G014 atom enum, G026+I010 (microtoken expandido), I002/I006 dup, orden contract+extras canonico, self-validation HCORTEX, marcador Unicode-aware. Vectores identicos en las 5; hash 63cd37b7 paridad. Node 24/24, Go tests verde, Bash F3 40/40, skill+catalogos actualizados.
