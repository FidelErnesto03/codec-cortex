# Package REV — Artefactos Normativos para Revisión Externa Independiente

Instrucciones para empaquetar solo los artefactos que un revisor externo necesita,
excluyendo implementaciones existentes, validadores Python, reportes de diseño y experimentos.

## Estructura del paquete

```
rev-package/
├── README.md
├── SPECIFICATION/
│   ├── CORTEX-SPEC-0.1.md
│   ├── C14N-0.1.md
│   ├── hcortex-0.1.md
│   ├── fundamental-glossary-0.1.md
│   ├── errors.md
│   └── GATE-F2.md
├── GRAMMAR/
│   ├── cortex.ebnf
│   └── cortex.abnf
├── SCHEMAS/
│   ├── ast-schema.json
│   ├── canonicalization-report.schema.json
│   ├── hcortex-metadata.schema.json
│   ├── hcortex-vector.schema.json
│   └── loss-report.schema.json
├── CORPUS-C14N/
│   ├── input/        (40 archivos .cortex)
│   ├── canonical/    (40 archivos .cortex — golden bytes)
│   ├── manifest.json
│   └── vectors/
│       └── hash-vectors.json
├── CORPUS-HCORTEX/
│   ├── cortex/            (40 archivos .cortex fuente)
│   ├── ast/               (40 archivos .json — AST esperados)
│   ├── hcortex-canonical/ (40 archivos .md)
│   ├── hcortex-readable/  (40 archivos .md)
│   ├── invalid/           (16 archivos .md inválidos)
│   ├── expected-diagnostics/ (16 archivos .json)
│   ├── loss-reports/      (80 archivos .json)
│   ├── manifest.json
│   └── vectors/
│       ├── cortex-to-hcortex-vectors.json
│       ├── hcortex-to-cortex-vectors.json
│       └── roundtrip-vectors.json
├── REV-PROTOCOL.md
└── SHA256SUMS.txt
```

## Comando para empaquetar

```bash
#!/bin/bash
# Desde la raíz del repositorio CODEC-CORTEX
PKG=/tmp/rev-package
rm -rf "$PKG"
mkdir -p "$PKG"/{SPECIFICATION,GRAMMAR,SCHEMAS,CORPUS-C14N/vectors,CORPUS-HCORTEX/vectors}

# Especificaciones
cp docs/standard/CORTEX-SPEC-0.1.md "$PKG/SPECIFICATION/"
cp docs/standard/C14N-0.1.md "$PKG/SPECIFICATION/"
cp docs/standard/hcortex-0.1.md "$PKG/SPECIFICATION/"
cp docs/standard/fundamental-glossary-0.1.md "$PKG/SPECIFICATION/"
cp docs/standard/errors.md "$PKG/SPECIFICATION/"
cp docs/standard/GATE-F2.md "$PKG/SPECIFICATION/"

# Gramáticas
cp docs/grammar/cortex.ebnf "$PKG/GRAMMAR/"
cp docs/grammar/cortex.abnf "$PKG/GRAMMAR/"

# Schemas
cp docs/schemas/ast-schema.json "$PKG/SCHEMAS/"
cp docs/schemas/canonicalization-report.schema.json "$PKG/SCHEMAS/"
cp docs/schemas/hcortex-metadata.schema.json "$PKG/SCHEMAS/"
cp docs/schemas/hcortex-vector.schema.json "$PKG/SCHEMAS/"
cp docs/schemas/loss-report.schema.json "$PKG/SCHEMAS/"

# Corpus C14N
cp conformance/c14n/corpus/input/*.cortex "$PKG/CORPUS-C14N/"
cp conformance/c14n/corpus/canonical/*.cortex "$PKG/CORPUS-C14N/canonical/"
cp conformance/c14n/corpus/manifest.json "$PKG/CORPUS-C14N/"
cp conformance/c14n/vectors/hash-vectors.json "$PKG/CORPUS-C14N/vectors/"

# Corpus HCORTEX
cp conformance/hcortex/cortex/*.cortex "$PKG/CORPUS-HCORTEX/cortex/"
cp conformance/hcortex/ast/*.json "$PKG/CORPUS-HCORTEX/ast/"
cp conformance/hcortex/hcortex-canonical/*.md "$PKG/CORPUS-HCORTEX/hcortex-canonical/"
cp conformance/hcortex/hcortex-readable/*.md "$PKG/CORPUS-HCORTEX/hcortex-readable/"
cp conformance/hcortex/invalid/*.md "$PKG/CORPUS-HCORTEX/invalid/"
cp conformance/hcortex/expected-diagnostics/*.json "$PKG/CORPUS-HCORTEX/expected-diagnostics/"
cp conformance/hcortex/loss-reports/*.json "$PKG/CORPUS-HCORTEX/loss-reports/"
cp conformance/hcortex/manifest.json "$PKG/CORPUS-HCORTEX/"
cp conformance/hcortex/vectors/*.json "$PKG/CORPUS-HCORTEX/vectors/"

# Protocolo
cp docs/standard/REV-PROTOCOL.md "$PKG/"

# SHA256
cd "$PKG" && find . -type f | sort | xargs sha256sum > SHA256SUMS.txt

echo "Paquete creado en $PKG"
echo "Archivos: $(find "$PKG" -type f | wc -l)"
echo "Tamaño: $(du -sh "$PKG" | cut -f1)"
```

## Lo que NO está en el paquete

| Excluido | Razón |
|---|---|
| `tools/cortex01_c14n.py` | Oráculo Python interno — invalidaría la revisión |
| `tools/hcortex_oracle.py` | Oráculo Python interno — invalidaría la revisión |
| `tools/cortex01_validator.py` | Validador de Fase 2 |
| `tools/validate_phase2.py` | Runner de Fase 2 |
| `tools/validate_phase3.py` | Runner de Fase 3 — usa el oráculo |
| `tools/validate_phase4.py` | Runner de Fase 4 — usa el oráculo |
| `experiments/` | Todas las implementaciones previas |
| `docs/review/` | Reportes de diseño y experimentos previos |
| `docs/standard/F3-CHARTER.md` | Documento de guía interna |
| `docs/standard/F4-CHARTER.md` | Documento de guía interna |
| `conformance/c14n/corpus/reports/` | Reportes de pérdida — dependientes del oráculo |

## Verificación del paquete

Un revisor que recibe este paquete debe poder:

1. Leer las specs en `SPECIFICATION/`
2. Leer las gramáticas en `GRAMMAR/`
3. Implementar un parser + canonicalización + HCORTEX
4. Ejecutar contra `CORPUS-C14N/` y `CORPUS-HCORTEX/`
5. Producir un reporte según `REV-PROTOCOL.md`

Sin necesidad de nada más.
