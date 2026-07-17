# Arquitectura

```text
bin/codec-cortex
        ↓
lib/codec-cortex.sh
  ├─ scalar lexer/parser
  ├─ CORTEX parser → AST JSON
  ├─ C14N writer
  ├─ HCORTEX renderer/compiler
  ├─ diagnostics
  └─ F3/F4 harness
```

## AST

El modelo conserva la estructura Python:

```text
Document
├── cortex_version
├── encoding
├── glossary
│   ├── format
│   ├── meta[]
│   ├── enums[]
│   ├── micros[]
│   ├── namespaces[]
│   ├── extensions[]
│   └── symbols[]
└── sections[]
    └── ideas[]
```

Los atributos se representan como arrays `{key,value}` y no como objetos JSON para preservar orden y duplicados fuente.

## Determinismo

- `LC_ALL` no decide el significado del formato.
- Unicode textual se normaliza mediante ICU NFC.
- El orden canónico se produce desde reglas explícitas.
- Cada writer termina con un único LF.
- El hash C14N usa `CORTEX-C14N-0.1 || NUL || bytes`.

## Dependencias

`jq` gestiona transformaciones estructurales del AST. `uconv` evita delegar Unicode a heurísticas del locale. Ninguna dependencia interpreta semántica CORTEX por su cuenta.
