# Impacto obligatorio sobre Fase 3

La Fase 3 debe reconstruirse contra `CORTEX-SPEC-0.1-DRAFT-REAL-001`.

## Debe conservar

- unidad ideática;
- `$0` y contratos locales;
- bare atoms;
- attrs-pos;
- microtokens;
- shapes originales;
- neutralidad de sigilos.

## Debe definir

- forma canónica de `$0:format`;
- orden canónico de meta-declaraciones y símbolos;
- si el writer conserva o expande microtokens en canonical form;
- quoting canónico de strings y positional cells;
- numeric form exacta;
- Unicode NFC;
- whitespace y LF final;
- canonical bytes de cuerpo y bloque;
- equivalencia de namespace local vs sigilo calificado, si se admite;
- hash del AST ideático.

## No debe reintroducir

- `encoded` visible;
- wrappers de logical type;
- metadata de materialización como sintaxis Core;
- identidad durable obligatoria;
- retención o presupuestos;
- profiles como requisito de parsing.

## Clasificación de Fase 3 ampliada

Si se mantienen materialización o proyección bajo presupuesto, deben publicarse como extensiones estándar separadas de la canonicalización Core.
