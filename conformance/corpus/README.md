# Corpus CORTEX 0.1 — Fase 2

## Estructura

```text
valid/                 fuentes conformes
expected-ast/          AST lógico esperado
invalid/               fuentes no conformes
expected-diagnostics/  códigos mínimos esperados
manifest.json          inventario ejecutable
```

## Cobertura válida

El corpus cubre:

- attrs;
- attrs-pos;
- cuerpo;
- bloque;
- relacion;
- contratos y opcionalidad;
- foco y peso;
- scalars;
- listas planas;
- enums;
- microtokens;
- comentarios;
- Unicode;
- secciones;
- namespaces;
- extensiones;
- estilo de la skill original.

## Cobertura inválida

Incluye errores lexicales, secciones, glosario, contratos, fields, shapes, aridad, foco, extensions y Unicode.

## Autoridad

Durante Draft 0.1, la especificación resuelve contradicciones. El corpus debe corregirse mediante revisión documentada si contradice inequívocamente la especificación.
