# Protocolo de Revisión Externa Independiente — Gate F3 + F4

**Document ID:** `CORTEX-REV-PROTOCOL-001`
**Date:** `2026-07-17`
**Purpose:** Permitir que un implementador externo no vinculado al proyecto verifique de forma independiente el roundtrip CORTEX↔HCORTEX del estándar CORTEX 0.1. La revisión no evalúa la calidad de los parsers — evalúa que la transformación entre formatos sea reversible, idempotente y determinista.

## 1. ¿Qué se revisa?

Dos afirmaciones:

1. **F3 (C14N-0.1):** La canonicalización produce bytes deterministas que permiten el roundtrip CORTEX↔HCORTEX sin pérdida.

2. **F4 (HCORTEX):** El roundtrip CORTEX → AST → HCORTEX → AST → CORTEX es reversible sin pérdida para 40 casos. Un tercero debe poder implementar el pipeline y confirmar 40/40.

## 2. Artefactos normativos (solo estos)

El revisor recibe ÚNICAMENTE estos archivos. Sin acceso al oráculo Python, sin acceso al parser Rust, sin acceso a los resultados de Fase 2.

| Archivo | Propósito |
|---|---|
| `docs/standard/CORTEX-SPEC-0.1.md` | Especificación del formato CORTEX 0.1 (34 secciones) |
| `docs/standard/C14N-0.1.md` | Especificación de canonicalización (20 secciones) |
| `docs/standard/hcortex-0.1.md` | Especificación de HCORTEX (representación humana) |
| `docs/standard/errors.md` | Catálogo de diagnostics |
| `docs/grammar/cortex.ebnf` | Gramática formal EBNF |
| `docs/schemas/ast-schema.json` | Schema del AST |
| `conformance/c14n/corpus/input/` | 40 archivos `.cortex` de entrada |
| `conformance/c14n/corpus/canonical/` | 40 archivos con los bytes canónicos esperados |
| `conformance/c14n/vectors/hash-vectors.json` | 40 vectores de hash canónico |
| `conformance/hcortex/corpus/cortex/` | 40 archivos `.cortex` fuente |
| `conformance/hcortex/corpus/hcortex-canonical/` | 40 HCORTEX esperados |
| `conformance/hcortex/corpus/ast/` | 40 AST JSON esperados |
| `conformance/hcortex/corpus/hcortex-readable/` | 40 HCORTEX-READABLE esperados |
| `conformance/hcortex/vectors/cortex-to-hcortex-vectors.json` | 40 vectores de transformación |
| `conformance/hcortex/vectors/hcortex-to-cortex-vectors.json` | 40 vectores de transformación inversa |
| `conformance/hcortex/vectors/roundtrip-vectors.json` | 40 vectores de roundtrip |
| `conformance/hcortex/corpus/manifest.json` | Índice del corpus HCORTEX |

## 3. Lo que el revisor NO debe usar

- ❌ El archivo `tools/cortex01_c14n.py` (oráculo Python interno)
- ❌ El archivo `tools/hcortex_oracle.py` (oráculo Python interno)
- ❌ El archivo `tools/cortex01_validator.py` (validador de Fase 2)
- ❌ El archivo `tools/validate_phase2.py` (runner de Fase 2)
- ❌ El archivo `tools/validate_phase3.py` (runner de Fase 3)
- ❌ El archivo `tools/validate_phase4.py` (runner de Fase 4)
- ❌ Cualquier implementación existente en `experiments/`
- ❌ `docs/review/` — reportes de diseño y experimentos previos

## 4. Protocolo de revisión — Fase 3 (C14N-0.1)

### 4.1 Implementar un parser CORTEX 0.1

Usando solo los artefactos normativos, implementar un parser que:
- Lea un archivo `.cortex` y produzca un AST JSON según `ast-schema.json`
- Detecte los 5 shapes: `attrs`, `attrs-pos`, `cuerpo`, `bloque`, `relacion`
- Parsee el glosario `$0` con format, enums, microtokens, namespaces, extensions

### 4.2 Implementar canonicalización C14N-0.1

Siguiendo `docs/standard/C14N-0.1.md`, implementar el pipeline:

```
.cortex → parse → orden canónico → normalización → serialización → SHA256
```

Reglas exactas de canonicalización:
- **Orden de $0:** format → enum_* → micro_* → namespace_* → extension_* → otros (alfabético dentro de cada grupo)
- **Orden de símbolos:** alfabético por nombre calificado (namespace::symbol)
- **Orden de attrs:** campos del contrato primero (en orden declarado), luego extras alfabético (NFC)
- **Microtokens:** expandir atom → valor completo
- **Unicode:** NFC para strings lógicos; bloque preserva verbatim
- **Cuerpo:** trim newline inicial/final; blank lines internos preservados
- **Bloque:** preservar verbatim; solo normalizar CRLF → LF
- **Números:** representación decimal exacta preservada (0.750 ≠ 0.75)
- **Serialización:** sin comentarios, sin whitespace extra, sin indentación

El hash canónico se calcula como:
```
hash = sha256("CORTEX-C14N-0.1\x00" + bytes_canónicos)
```

### 4.3 Verificar canonicalización

Para cada archivo en `conformance/c14n/corpus/input/`:

```bash
# Ejecutar el parser con canonicalización
./mi_parser --canonicalize input/H001_minimal-attrs.cortex > output.bin

# Comparar byte a byte contra golden
diff output.bin conformance/c14n/corpus/canonical/H001_minimal-attrs.cortex
```

**Criterio de aceptación:** ≥38/40 bytes idénticos (C14N-0.1 es byte-determinista).

### 4.4 Verificar idempotencia

```bash
./mi_parser --canonicalize output.bin > output2.bin
diff output.bin output2.bin  # Debe ser idéntico
```

**Criterio de aceptación:** 40/40 idempotente.

### 4.5 Verificar hash

```bash
python3 -c "import hashlib; h=hashlib.sha256(b'CORTEX-C14N-0.1\x00'+open('output.bin','rb').read()); print(h.hexdigest())"
```

Comparar contra `conformance/c14n/vectors/hash-vectors.json`.

**Criterio de aceptación:** ≥38/40 hashes coinciden.

## 5. Protocolo de revisión — Fase 4 (HCORTEX)

### 5.1 Implementar HCORTEX

Siguiendo `docs/standard/hcortex-0.1.md`, implementar:

```
CORTEX canónico → AST → HCORTEX-CANONICAL → HCORTEX-READABLE
```

### 5.2 Verificar roundtrip

Para cada vector en `conformance/hcortex/vectors/roundtrip-vectors.json`:

```bash
# 1. Compilar HCORTEX → AST
./mi_parser --compile-hcortex input.md > ast.json

# 2. Comparar AST contra golden
diff ast.json conformance/hcortex/corpus/ast/H001_expected.json

# 3. Renderizar AST → HCORTEX
./mi_parser --render-hcortex ast.json > output.md

# 4. Comparar contra golden canonical
diff output.md conformance/hcortex/corpus/hcortex-canonical/H001_canonical.md

# 5. Roundtrip completo: HCORTEX → AST → CORTEX → comparar contra original
./mi_parser --hcortex-to-cortex input.md > roundtrip.cortex
diff roundtrip.cortex conformance/hcortex/corpus/cortex/H001_source.cortex
```

**Criterio de aceptación:** 40/40 compile, 40/40 AST roundtrip, 40/40 CORTEX byte roundtrip.

### 5.3 Verificar idempotencia HCORTEX

```bash
./mi_parser --render-hcortex ast.json > h1.md
./mi_parser --compile-hcortex h1.md > ast2.json
./mi_parser --render-hcortex ast2.json > h2.md
diff h1.md h2.md  # Debe ser idéntico
```

**Criterio de aceptación:** 40/40 idempotente.

### 5.4 Verificar diagnostics inválidos

Para cada caso en `conformance/hcortex/corpus/invalid/`:

```bash
./mi_parser --compile-hcortex invalid/I001_bad_format.md 2>&1 | grep -c "H4..."
```

**Criterio de aceptación:** 16/16 diagnostics emitidos correctamente.

### 5.5 Verificar 0 dependencias VIEW

```bash
grep -c "cortex.view\|@view\|view:" conformance/hcortex/corpus/manifest.json
```

**Criterio de aceptación:** 0.

## 6. Lenguajes aceptables

El revisor puede usar cualquier lenguaje. El estándar CORTEX no favorece ninguno. Las implementaciones existentes están en Python, Rust, Go, Node.js y Bash — pero el revisor no debe basarse en ninguna de ellas ni consultar sus fuentes.

## 7. Formato del reporte

El revisor debe producir un reporte JSON con esta estructura:

```json
{
  "reviewer": {
    "name": "Nombre o alias",
    "language": "Lenguaje usado",
    "started_at": "ISO 8601",
    "completed_at": "ISO 8601"
  },
  "phase3": {
    "golden_pass": 40,
    "idempotence_pass": 40,
    "hash_pass": 40,
    "total": 40,
    "failures": [],
    "status": "PASS"
  },
  "phase4": {
    "compile_pass": 40,
    "ast_roundtrip_pass": 40,
    "cortex_roundtrip_pass": 40,
    "hcortex_idempotence_pass": 40,
    "invalid_diagnostic_pass": 16,
    "view_dependencies": 0,
    "failures": [],
    "status": "PASS"
  },
  "findings": [
    {
      "severity": "BLOCKER | MAJOR | MINOR | COMMENT",
      "section": "C14N-0.1 §X o hcortex-0.1 §X",
      "description": "Descripción del hallazgo",
      "recommendation": "Sugerencia de corrección"
    }
  ],
  "verdict": "PASS | FAIL | CONDITIONAL_PASS"
}
```

## 8. Criterios de veredicto

| Veredicto | Condición |
|---|---|
| **PASS** | ≥38/40 en F3 + 40/40 en F4 + 0 BLOCKERs |
| **CONDITIONAL_PASS** | ≥36/40 en F3 + ≥38/40 en F4 + 0 BLOCKERs |
| **FAIL** | Cualquier BLOCKER o <36/40 en F3 |

## 9. Dónde empezar

1. Leer `docs/standard/CORTEX-SPEC-0.1.md` (la especificación base)
2. Leer `docs/standard/C14N-0.1.md` (canonicalización)
3. Leer `docs/standard/hcortex-0.1.md` (HCORTEX)
4. Implementar parser + canonicalización + HCORTEX
5. Ejecutar contra el corpus
6. Producir reporte JSON

## 10. Contacto

Este protocolo es auto-contenido. No se requiere contacto con los autores del estándar. El reporte puede entregarse en cualquier formato público (issue, PR, PDF, correo).

---

*Fin del protocolo. El estándar se prueba a sí mismo cuando un implementador externo produce los mismos bytes que el oráculo interno sin haberlo visto.*
