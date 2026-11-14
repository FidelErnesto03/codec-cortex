# Pérdidas declaradas — `loss-report`

Un codec honesto no promete que nada se pierde: **nombra lo que se pierde**.
`loss-report` es el comando que hace esa promesa verificable.

---

## Qué es una pérdida declarada

Una **pérdida declarada** es información presente en la fuente que no se
representa en el AST y que, por tanto, no se recupera al volver:

```
canonicalize(from_hcortex(render(doc)))  ≠  información original de la fuente
```

El canon 1.0 prohíbe que un render esconda información semántica sin declararla
(**H481**, sin copia oculta) y exige que toda divergencia de roundtrip pertenezca
a una clase del catálogo. Si aparece una divergencia que ninguna clase explica,
se emite `L499_UNCLASSIFIED_LOSS`, el comando **falla** y el canon queda
señalado como incompleto.

## Catálogo cerrado (spec §8.2)

| Código | Qué se pierde | Disparador | `path` |
|---|---|---|---|
| `L402_COMMENT_DROPPED` | comentarios `#` | línea cuyo primer carácter no-espacio es `#`, fuera de cuerpo/bloque (también dentro del glosario) | `line:<n>` |
| `L403_INTRALINE_WHITESPACE` | formato intra-línea | tab, espacio final o 2+ espacios consecutivos fuera de literales entrecomillados | `line:<n>` |
| `L405_OPEN_ATTR_ORDER` | orden editorial de atributos | idea de sigilo `open:true` cuyo orden en fuente ≠ orden de contrato + extras por clave UTF-8 | `$N` |
| `L406_COMPILE_SIDE_DROP` | idea perdida en render→compile | una idea del AST no se recupera al recompilar (su header `### ns::SIGIL:name` no vuelve a parsear) — **error**, exit 1 | `$` |
| `L499_UNCLASSIFIED_LOSS` | divergencia sin clase | roundtrip no equivalente sin causa catalogada (**error**, exit 1) | `$` |

**Retirados como pérdida** (spec §8.3, con evidencia): `L401` (marcador de fence
en bloque — sobrevive el roundtrip en las cinco superficies) y `L404` (CAPA
ausente — la ausencia se preserva; `$0` desnudo es gramática válida).

Una pérdida **no es un error**: el documento es válido. El reporte describe qué
información se queda en la fuente y no viaja al AST.

## Formato del reporte

Schema normativo: [`schemas/loss-report-1.0.schema.json`](schemas/loss-report-1.0.schema.json).
La salida es **JSON canónico**: claves ordenadas, indent 2, UTF-8 sin escapes,
newline final. Las cinco superficies emiten **bytes idénticos**.

```json
{
  "case": "L402_comment",
  "coverage": {
    "complete": false,
    "operations": ["render"],
    "uncovered_operations": ["compile"]
  },
  "losses": [
    {
      "action": "declare-only",
      "category": "structure",
      "code": "L402_COMMENT_DROPPED",
      "detail": "comment line outside a multiline body is not represented in the AST",
      "path": "line:4",
      "recoverability": "from-source-only",
      "severity": "loss"
    }
  ],
  "mode": "canonical",
  "operation": "render",
  "preserved": ["blocks", "identity", "scalars", "structure"],
  "reversible": true,
  "schema_version": "1.0",
  "source_format": "cortex:1.0",
  "source_sha256": "60e36332…",
  "structural_equivalence": true,
  "target_format": "hcortex:1.0",
  "target_sha256": "82dade9a…",
  "warnings": []
}
```

| Campo | Significado |
|---|---|
| `coverage.complete` | La cobertura declarada modela **todos** los tramos del pipeline. Hoy `false`: el tramo `compile` (fuente → AST) no está modelado |
| `coverage.operations` | Tramos cuyas pérdidas sí modela el reporte (`["render"]`) |
| `coverage.uncovered_operations` | Tramos sin clase de pérdida asociada (`["compile"]`). Declararlo evita que `reversible: true` sobre-afirme: un documento puede ser reversible en `render` aun cuando la compilación descartó contenido que ninguna clase describe |
| `reversible` / `structural_equivalence` | `canonicalize(fuente) == canonicalize(roundtrip)`: el AST va y vuelve intacto (alcance: `render`) |
| `losses` | pérdidas de **fuente**, ordenadas por `(path, code)` y sin duplicados |
| `source_sha256` | hash del texto de entrada |
| `target_sha256` | hash del HCORTEX renderizado |
| `preserved` | lo que el pipeline garantiza preservar |

## Uso

```bash
python -m codec_cortex loss-report doc.cortex
cat doc.cortex | python -m codec_cortex loss-report -     # case = "stdin"
```

| Superficie | Invocación |
|---|---|
| Python | `python -m codec_cortex loss-report <file\|->` |
| Go | `codec-cortex loss-report <file\|->` |
| Node | `codec-cortex-node loss-report <file\|->` |
| Rust | `cortex loss-report <file\|->` |
| Bash | `codec-cortex loss-report <file\|->` |

**Exit codes:** `0` reporte emitido · `1` `L499`, parse o compilación fallida ·
`2` uso incorrecto.

Solo acepta `cortex:1.0`; sobre otro dialecto responde `G007`.

## Cómo se verifica

| Indicador | Qué exige |
|---|---|
| **D6_loss_report_parity** | vectores con reporte esperado exacto **y** corpus 1.0 completo con salida idéntica en las 5 superficies, sin `L499` (75/75) |
| **D7_dialect_contract** | contrato de cabecera y glosario sin capa en las 5 superficies (10/10) |

Vectores: [`conformance/1.0/loss/`](../conformance/1.0/loss/) (5 fixtures +
reportes esperados, sellados) y [`conformance/0.1-contract/`](../conformance/0.1-contract/).

## Cómo leerlo sin convertirlo en ruido

Medición sobre **217 documentos `cortex:1.0` reales** fuera del corpus (2026-11-14):

| Código | Apariciones | Lectura |
|---|---|---|
| `L402` comentarios | 3447 | ubicuo en documentos de gobierno; **informativo, nunca métrica de compuerta** |
| `L405` orden de attrs | 342 | señal útil de normalización |
| `L403` whitespace | 1 | no es ruido |

Regla práctica: `loss-report` dice la verdad documento por documento. Para
decidir calidad de un corpus, la compuerta es **D4/D6** (reversibilidad y
paridad), no el conteo de `L402`.

## Añadir una pérdida

El catálogo es cerrado. Añadir, retirar o redefinir una clase exige:

1. texto normativo en `CORTEX-SPEC-1.0.md` §8.2 (nueva versión de spec);
2. implementación en las **cinco** superficies;
3. vector en `conformance/1.0/loss/` con su reporte esperado;
4. `D6` en verde y nueva auditoría firmada.

Las tres patas en lockstep, siempre.
