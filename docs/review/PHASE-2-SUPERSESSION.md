# Declaración de sustitución de Fase 2

`CORTEX-SPEC-0.1-DRAFT-REAL-001` sustituye integralmente:

- `CORTEX_PHASE2_DRAFT_0_1`;
- `CORTEX_PHASE2_DRAFT_0_1_RECONSTRUCTED`;
- gramáticas, schemas, corpus y diagnostics derivados de esas entregas.

## Motivo

Las entregas sustituidas formalizaron un modelo de serialización genérica del AST y se alejaron de las invariantes originales:

- `$0` como glosario canónico local;
- sigilo como función ideática;
- una línea por Idea;
- bare atoms;
- attrs-pos;
- compresión lingüística;
- patrón reproducible amortizado;
- reversibilidad por shape.

## Elementos rescatados

- especificación superior al código;
- AST formal;
- diagnostics estables;
- Unicode;
- namespaces;
- extensiones requeridas/opcionales;
- identidad local vs durable;
- corpus válido/inválido;
- gate de implementaciones independientes.

## Regla de uso

Ningún trabajo futuro debe usar como autoridad los schemas, bytes, hashes o decisiones sintácticas de las entregas sustituidas.
