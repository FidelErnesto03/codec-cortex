# Auditoría de la entrega contra F3-CHARTER

**Document ID:** `CORTEX-F3-CHARTER-AUDIT-002`  
**Verdict:** `CORRECTED_INTERNAL_PASS / GATE_BLOCKED`

## 1. Hallazgos sobre la entrega anterior

| ID | Hallazgo | Severidad | Corrección |
|---|---|---:|---|
| A-01 | Corpus de 32, Charter exige 40 | BLOCKER | ampliado a 40 casos |
| A-02 | `0.750` canonicalizaba a `0.75` | BLOCKER | precisión decimal exacta preservada |
| A-03 | `bloque` recibía NFC | BLOCKER | composición Unicode verbatim preservada |
| A-04 | Source preservation era requisito normativo | HIGH | diferido; reporte de trivia queda opcional |
| A-05 | Se declaró `READY_FOR_GATE` sin Rust independiente | BLOCKER | estado cambiado a `GATE_BLOCKED` |
| A-06 | No existía evidencia CE-7 | BLOCKER | dependencia explícita a Fase 4; sin claim falso |
| A-07 | Quoting no aplicaba I7 | HIGH | emisión contract-aware de payload `attrs` |
| A-08 | CE-4 mezclaba equivalencia de Idea y documento | HIGH | niveles separados y documentados |

## 2. Matriz de invariantes

| Invariante | Resultado | Evidencia |
|---|---|---|
| I1 Idea fundamental | PASS | parser/oracle y corpus conservan `Idea` |
| I2 cinco shapes | PASS | `C031_all_shapes` |
| I3 `$0` primero y único | PASS | precondición y todos los golden |
| I4 vocabulario transportado | PASS | glosario participa en bytes/hash |
| I5 línea ideática | PASS | golden outputs |
| I6 sin encoded wrapper | PASS | búsqueda e inventario del paquete |
| I7 quoting contract-aware | PASS con alcance | `E032_nonfocus_text_quote` |
| I8 orden observado | PASS | E011–E014 negativos; E025/E026 normalizables |
| O1 AST sirve al formato | PASS | salida conserva superficie `$0`/sigilos |
| O2 sin pérdida silenciosa | PASS | 40/40 `losses=[]` |
| O3 idempotencia | PASS interno | 40/40 |
| O4 HCORTEX deriva del AST | PENDING F4 | no se inventa segunda ontología |
| O5 sin dependencias variables | PASS | Python y Node sin red/locale/fecha |
| O6 Core neutral | PASS | `C032_neutral_unknown_domain` |
| O7 derivado no sustituye canon | PASS | source y canonical se separan |

## 3. Criterios de éxito

| Criterio | Estado | Resultado |
|---|---|---|
| CE-1 idempotencia en 40 | PASS interno | 40/40 |
| CE-2 Python + Rust independiente | BLOCKED | Node 40/40 es evidencia auxiliar, no sustituto |
| CE-3 orden `$0` independiente del autor | PASS interno | E026 |
| CE-4 expansión microtoken | PASS con distinción | igualdad de valor; glosario sigue estructural |
| CE-5 NFC/NFD | PASS interno | E004; excepción verbatim E030 |
| CE-6 loss report vacío | PASS interno | 40/40 |
| CE-7 HCORTEX roundtrip | BLOCKED F4 | no implementado en F3 |

## 4. Dictamen

La especificación y corpus corregidos están internamente consistentes. No se autoriza `F3 PASSED` ni `READY_FOR_GATE` porque CE-2, CE-7 y la revisión externa siguen pendientes.
