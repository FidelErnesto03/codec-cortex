# EQUIVALENCE — Niveles de equivalencia CORTEX ⇄ HCORTEX

**Versión:** v2.4.0  
**Estado:** current para los artefactos canónicos `skill/cortex/SKILL.md` y `skill/hcortex/SKILL.md`.

v2.4.0 no exige identidad byte-a-byte entre CORTEX y HCORTEX porque son formatos distintos. Exige equivalencia verificable según el sentido del roundtrip.

## Niveles

| Nivel | Definición | Aplicación |
|---|---|---|
| byte-identical | Bytes exactamente iguales | CORTEX → CORTEX; HCORTEX generado vs HCORTEX canónico cuando aplica |
| AST-equivalent | Misma estructura lógica: secciones, entries, tipos, campos y bloques | CORTEX → HCORTEX → CORTEX |
| semantic-equivalent | Mismo significado operativo con diferencias toleradas explícitamente | migraciones o canonicalize |
| content-equivalent | Mismo contenido humano por bloques VIEW | HCORTEX → CORTEX → HCORTEX |

## Gates v2.4.0

| Gate | Criterio canónico |
|---|---|
| CORTEX → HCORTEX → CORTEX | `AST equivalent: True`, `0 diffs` |
| HCORTEX → CORTEX → HCORTEX | `Content equivalent: True`, `0 diffs` |
| CORTEX canónico | 14 secciones, 266 entries, 44 VIEW |
| HCORTEX canónico | reversible true, roundtrip válido |
| DIAG / verbatim | preservación literal interna |
| VIEW coverage | 100% |

## CLI

```bash
cortex v2-compare left.cortex.md right.cortex.md
cortex v2-roundtrip-bidir skill/cortex/SKILL.md
cortex v2-roundtrip-bidir skill/hcortex/SKILL.md
```

## Resultado esperado en v2.4.0

```text
byte_identical: False        # normal entre CORTEX reconstruido y fuente si hay normalización textual
ast_equivalent: True
semantic_equivalent: True
content_equivalent: False    # normal si se comparan dos CORTEX como contenido HCORTEX
diff_count: 0
```

Para `v2-roundtrip-bidir`, ambos artefactos canónicos deben reportar `rc=0` y 0 diffs.

## Reversibilidad

`reversible:true` requiere:

1. `view_coverage == 100%`;
2. cero errores de VIEW/HCORTEX;
3. no estar en modo display-only;
4. roundtrip aplicable sin pérdida no declarada.
