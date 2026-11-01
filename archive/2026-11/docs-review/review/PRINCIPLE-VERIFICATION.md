# Verificación de principios — Fase 3 corregida

**Document ID:** `CORTEX-F3-PRINCIPLES-CHARTER-002`

| Principio | Prueba ejecutable | Resultado |
|---|---|---|
| Portable | `$0` completo participa en canonical bytes y hash | PASS |
| Denso | canonical form conserva una Idea por línea regular | PASS estructural |
| Compacto | no se introduce serialización genérica del AST | PASS |
| Extensible | metadata y extensiones opcionales se preservan | PASS |
| Reproducible | 40 golden + 40 hashes | PASS interno |
| Simple | misma gramática de Fase 2 | PASS |
| Reversible | shape, contrato, foco, identidad y orden conservados | PASS preparatorio; HCORTEX pendiente |
| Sin pérdida silenciosa | `structuralLoss=false`, `losses=[]` en 40/40 | PASS |
| Neutral | corpus con dominio desconocido y cero reglas de agente | PASS |
| Determinista | Python y Node producen mismos bytes en 40/40 | PASS auxiliar |

La densidad de tokens o ventaja frente a JSON/YAML no se declara probada. Eso corresponde al benchmark científico de Fase 9.
