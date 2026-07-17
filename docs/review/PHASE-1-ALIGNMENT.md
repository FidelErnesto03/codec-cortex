# Alineación con Fase 1

## 1. Compatibilidad constitucional

La Fase 2 REAL mantiene:

- representación, no gobierno;
- neutralidad ontológica;
- dependencias unidireccionales;
- determinismo;
- no pérdida silenciosa;
- extensiones preservables;
- autocontención;
- implementación independiente;
- HCORTEX derivado del AST.

## 2. Refinamiento terminológico

Fase 1 utilizó `Entry` como término abstracto. Fase 2 concreta la unidad CORTEX como `Idea` y la superficie preferente como `Idea Line`.

Propuesta de errata no bloqueante para `TERMINOLOGY.md`:

```text
Idea — Unidad contextual identificada que expresa una función, un foco y un payload conforme a un contrato local.
Idea Line — Representación superficial preferente de una Idea en una línea CORTEX.
Entry — Término genérico no preferido; en CORTEX 0.1 la entrada semántica es Idea.
```

## 3. Autocontención reforzada

Fase 1 permitía vocabulario local o de perfil. Fase 2 exige declaración local de todo sigilo usado. Un perfil puede generar o validar el glosario, pero no reemplazarlo.

Esto no viola la neutralidad: el Core no conoce los significados declarados.

## 4. VIEW

VIEW permanece fuera del camino base. Las capacidades históricas pueden existir como extensión de presentación. Los shapes fundamentales bastan para el mapping universal de Fase 4.
