# Arquitectura de codec-cortex-rs

## Frontera del núcleo

El crate implementa únicamente representación, transformación, validación sintáctica y conformidad del codec.

```text
source CORTEX
      ↓
parser + scalars
      ↓
AST tipado (`model`)
  ↙             ↘
C14N           HCORTEX
  ↓              ↕
bytes          Markdown canónico
```

No existen dependencias hacia perfiles, runtime, learning, sesiones, agentes o ArqUX.

## Modelo

`Document` contiene `Glossary` y `Section[]`. El glosario contiene formato, metadata, enums, microtokens, namespaces, extensiones y símbolos. Cada `Idea` conserva:

- sección;
- namespace opcional;
- símbolo;
- nombre;
- shape;
- payload tipado;
- línea de origen.

Los escalares conservan simultáneamente el valor lógico y el lexema normalizado. Esto permite distinguir semántica de representación durante parsing y canonicalización.

## Parser

El parser es determinista y no depende de inferencia. Normaliza finales de línea, rechaza BOM, procesa `$0`, registra contratos y luego valida las ideas contra el shape declarado.

La API devuelve `Result<Document, ParseError>`. `ParseError` conserva código, mensaje, línea y columna.

## Canonicalización

C14N realiza:

1. NFC en valores no verbatim;
2. expansión de microtokens atómicos;
3. orden normativo del glosario;
4. orden de campos contractuales;
5. orden UTF-8/NFC para extras permitidos;
6. normalización de quoting y escalares;
7. LF único final.

`canonicalize(&Document)` no altera el AST del llamador. `canonicalize_in_place(&mut Document)` expone explícitamente la variante mutante.

## HCORTEX

El renderer conserva el formato emparejado usado por Python:

```html
<!-- HCORTEX v=0.1 t=canonical -->
<!-- glossary
...
-->

## §1: Título

<!-- table:1 -->
<!-- OBJ:item --> | valor | 1 |
<!-- /table:1 -->
```

El compiler devuelve `(Option<Document>, Vec<HDiagnostic>)`, manteniendo los diagnósticos `H400` y `H490` del contrato original.

## Harness

El harness reproduce los gates y umbrales del paquete Python, incluso el umbral fijo de 40 casos para F3. Esta decisión es paridad, no una recomendación de diseño. Una futura versión normativa debería derivar el umbral del manifiesto.
