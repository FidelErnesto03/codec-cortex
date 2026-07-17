# Aplicación rectora de F3-CHARTER

**Authority:** `CORTEX-F3-CHARTER-001`  
**Applied to:** `CORTEX-CANONICALIZATION-0.1-DRAFT-CHARTER-REVIEW-002`  
**Status:** `applied-with-explicit-gate-blockers`

## Mandato

La Fase 3 responde exclusivamente:

> ¿Cuándo dos documentos CORTEX son equivalentes?

La implementación y el corpus se organizan según:

```text
F3-A orden
F3-B whitespace
F3-C microtokens
F3-D números exactos
F3-E Unicode NFC con excepción verbatim
F3-G hash canónico
```

F3-F, preservación exacta de fuente, queda diferida a Fase 5 o tooling.

## Invariantes aplicadas

- Idea como unidad fundamental del AST.
- Cinco shapes: `attrs`, `attrs-pos`, `cuerpo`, `bloque`, `relacion`.
- `$0` primero, único y estructural.
- Vocabulario local transportado por el documento.
- Una Idea principal por línea regular.
- Sin wrapper `encoded` ni nueva gramática.
- Orden observado preservado donde es comunicativamente significativo.
- Canonicalización sin LLM, red, fecha, locale, runtime o perfiles.
- Sin pérdida estructural silenciosa.

## Interpretaciones necesarias

### I7 — comillas

Se aplica al payload de Ideas `attrs`: `focus:text` se emite quoted. Un `text` no-focus se emite bare cuando es inequívoco; se permite quoted únicamente cuando whitespace o delimitadores lo hacen necesario. Las strings estructurales del glosario (`fields`, `desc`) permanecen quoted.

### CE-4 — microtokens

La Idea con `cur` y la Idea con `current` poseen el mismo valor lógico cuando el microtoken está declarado. El documento completo conserva su glosario; por ello, retirar una declaración cambia el documento aunque el payload expandido coincida.

### CE-7 — HCORTEX

Se conserva como dependencia de aceptación, pero su especificación y roundtrip corresponden a Fase 4. Fase 3 no introduce una implementación ficticia para aparentar cumplimiento.
