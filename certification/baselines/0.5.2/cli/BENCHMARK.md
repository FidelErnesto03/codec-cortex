# BENCHMARK — codec-cortex v2.4.0

## Métricas canónicas v2.4.0

| Métrica | Resultado esperado | Evidencia |
|---|---:|---|
| CORTEX canónico entries | 266 | `cortex v2-inspect skill/cortex/SKILL.md` |
| VIEW directives | 44 | `v2-inspect` / `v2-verify-view` |
| VIEW coverage | 100% | `v2-verify-view` |
| CORTEX → HCORTEX byte-identical contra canónico | Sí | `cmp -s /tmp/skill.generated.hcortex.md skill/hcortex/SKILL.md` |
| HCORTEX → CORTEX entries | 266/266 | `v2-convert --from hcortex --to cortex` |
| CORTEX → HCORTEX → CORTEX | AST-equivalent, 0 diffs | `v2-roundtrip-bidir skill/cortex/SKILL.md` |
| HCORTEX → CORTEX → HCORTEX | content-equivalent, 0 diffs | `v2-roundtrip-bidir skill/hcortex/SKILL.md` |
| Display-only reversible false | Sí | tests T-06/T-07 |
| Hash mismatch declarado | `E_VIEW_HASH_MISMATCH` | test T-09 / prueba con hash explícito |
| Paquete limpio | Sí | `tar tzf ... | grep` sin resultados |

## Comandos reproducibles

```bash
cortex --version
cortex v2-inspect skill/cortex/SKILL.md
cortex v2-verify-view skill/cortex/SKILL.md
cortex v2-convert skill/cortex/SKILL.md --from cortex --to hcortex --out /tmp/skill.generated.hcortex.md
cmp -s /tmp/skill.generated.hcortex.md skill/hcortex/SKILL.md
cortex v2-convert skill/hcortex/SKILL.md --from hcortex --to cortex --out /tmp/skill.recon.cortex.md
cortex v2-inspect /tmp/skill.recon.cortex.md
cortex v2-roundtrip-bidir skill/cortex/SKILL.md
cortex v2-roundtrip-bidir skill/hcortex/SKILL.md
python -m pytest src/tests/test_v2_3_0_acceptance.py -q
```

## Nota de auditoría

La suite completa debe ejecutarse en CI/local del release con `python -m pytest src/tests/ -q`. El conteo de tests no se hardcodea en este archivo — la cifra exacta proviene del runner en vivo. El informe original de v2.4.0 declara `342 passed, 2 skipped`; este documento lista además los comandos críticos de aceptación del núcleo bidireccional.

### Criterios de recuperación

- **Visibilidad HCORTEX:** el roundtrip HCORTEX → CORTEX → HCORTEX verifica que el contenido recuperado es semánticamente no-vacío (semantic non-emptiness).
- **E034 / critical field emptiness:** la suite de validación detecta campos obligatorios vacíos (`E034`) tanto en CORTEX como en HCORTEX reconstruido.
