# Contrato del dialecto 0.1 (D7)

Vectores de regresión para los dos casos que la gramática 1.0 fija y que las
cinco superficies deben tratar igual, también en el dialecto 0.1:

| Vector | Contrato |
|---|---|
| `title_header.cortex` | `$0: <texto>` está fuera de gramática (`glossary-header = "$0" \| "$0:" capa`). Toda superficie lo rechaza con `G042_GLOSSARY_HEADER_INVALID`, nunca lo descarta en silencio ni lo confunde con otro código. |
| `bare_glossary.cortex` | `$0` desnudo es válido: el renderer lo emite y el compilador lo acepta. Sin esto, un documento sin capa produce un HCORTEX que la propia superficie rechaza. |

Verificado por `bench/certify.py` → `D7_dialect_contract` (5 superficies).
