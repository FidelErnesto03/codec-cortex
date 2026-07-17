# Diagnostics de Canonicalización CORTEX 0.1

**Document ID:** `CORTEX-C14N-ERRORS-0.1-CHARTER-REVIEW-002`  
**Status:** `corrected-normative-draft`

## 1. Contrato

Todo error bloqueante impide producir bytes o hash declarados conformes. Los warnings no alteran el resultado y deben incluir ubicación cuando provengan de fuente.

## 2. Errores E8xx

| Código | Condición | Efecto |
|---|---|---|
| `E801_SOURCE_NOT_STRUCTURE_VALID` | la fuente no alcanza `structure-valid` | abortar |
| `E802_UNSUPPORTED_CORTEX_VERSION` | versión distinta de 0.1 | abortar |
| `E803_PARTIAL_AST` | AST recuperado o incompleto | abortar |
| `E804_UNRESOLVED_SYMBOL` | Idea sin declaración resoluble | abortar |
| `E805_INVALID_CONTRACT_ORDER` | contrato o Idea viola orden obligatorio | abortar |
| `E806_INVALID_SCALAR_FOR_CANONICALIZATION` | scalar fuera del modelo | abortar |
| `E807_INVALID_UNICODE_SCALAR` | surrogate/control inválido | abortar |
| `E808_DUPLICATE_STRUCTURAL_IDENTITY` | dirección local duplicada | abortar |
| `E809_INVALID_EXTENSION_DECLARATION` | extensión no preservable estructuralmente | abortar |
| `E810_INVALID_CANONICAL_NUMBER` | número exacto no serializable | abortar |
| `E811_STRUCTURAL_LOSS_DETECTED` | la operación requeriría eliminar o alterar información del AST | abortar; C14N no admite modo destructivo |
| `E812_CANONICAL_HASH_MISMATCH` | hash esperado no coincide | abortar verificación |
| `E813_GOLDEN_BYTES_MISMATCH` | salida no coincide con vector | fallo de conformidad |
| `E814_STRUCTURAL_PRESERVATION_FAILURE` | parse(C14N(x)) no equivale a parse(x) | fallo de conformidad |
| `E841_CANONICAL_IDEMPOTENCE_FAILURE` | C14N(C14N(x)) difiere | fallo BLOCKER |

## 3. Warnings W8xx de tooling — no normativos

Estos warnings describen fidelidad textual de la fuente. Son opcionales y no participan en hash, equivalencia ni conformidad C14N.


| Código | Condición |
|---|---|
| `W801_SOURCE_FORM_CHANGED` | bytes fuente y canónicos difieren |
| `W802_COMMENTS_REMOVED` | se descartó trivia de comentario |
| `W803_BLANK_LINES_REMOVED` | se descartaron líneas vacías |
| `W804_NEWLINE_NORMALIZED` | CR/CRLF se convirtió a LF |
| `W805_UNICODE_NORMALIZED` | texto lógico fuera de `bloque` cambió a NFC |
| `W806_GLOSSARY_REORDERED` | declaraciones independientes fueron ordenadas |
| `W807_ATTRIBUTES_REORDERED` | claves normalizables cambiaron de orden |
| `W808_MICROTOKEN_EXPANDED` | lexema compacto cambió a valor lógico |
| `W809_STRING_ESCAPE_NORMALIZED` | spelling de escape cambió |
| `W810_INTEGER_SPELLING_NORMALIZED` | spelling entero equivalente cambió; decimales exactos nunca se compactan |

## 4. No pérdida silenciosa

Toda canonicalización exitosa debe producir conceptualmente:

```json
{"structuralLoss": false, "losses": []}
```

`sourceFidelityChanges` y sus warnings, cuando una herramienta los ofrece, describen trivia o spelling y no constituyen pérdida estructural. La reconstrucción byte a byte requiere conservar la fuente o un CST separado; F3-F permanece diferido.
