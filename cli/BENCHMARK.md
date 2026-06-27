# BENCHMARK — codec-cortex

> Evidencia empírica de capacidades declaradas por `codec-cortex`.
> Per el SKILL.md §15, ningún claim de métrica puede presentarse como
> `measured` sin benchmark reproducible.

## Clasificación obligatoria (SKILL.md §15.1)

| Clasificación | Uso permitido |
|---|---|
| `measured` | Resultado obtenido con benchmark reproducible |
| `target` | Objetivo de diseño aún no demostrado |
| `hypothesis` | Hipótesis razonable pendiente de prueba |
| `illustrative` | Ejemplo didáctico, no evidencia |

## Métricas declaradas

| Métrica | Definición | Clasificación | Valor (v1.1.2) |
|---|---|---|---|
| Roundtrip structural fidelity | Igualdad AST antes/después de `.cortex → HCORTEX-EDIT → .cortex` | `measured` | 100% en fixtures controlados (suite completa: ver "Reproducibilidad") |
| Roundtrip con valores complejos | Pipes, comillas, unicode, bloques PlantUML, attrs-pos | `measured` | 100% tras fix H-04 (1.1.0) + RA-05 (1.1.1) |
| HCORTEX auditability | % de entradas críticas con `source` en modo AUDIT | `measured` | 100% (todas las entradas con `--mode audit`) |
| Recovery completeness | P0/P1 recuperados tras interrupción | `measured` | 100% cuando el preamble no contiene entradas |
| Recovery + embed AUD/RSK + verify --strict | Flujo completo de recuperación con traza embebida pasa verificación estricta | `measured` (v1.1.2) | 100% (test `test_recover_embed_then_verify_strict`) |
| Recovery visibility (HCORTEX) | Entradas recuperadas visibles en `render --mode audit --profile full` (no ocultas en $0) | `measured` (v1.1.5) | 100% (test `test_recover_entry_first_hcortex_shows_payload`) — v1.1.5 P1-6: recovery completeness requiere visibilidad HCORTEX, no solo verify --strict |
| Recovery semantic non-emptiness | Entradas recuperadas tienen campos requeridos no vacíos (no "", "   ", null) | `measured` (v1.1.6) | 100% (test `test_recover_entry_first_hcortex_shows_payload`) — v1.1.6 P1-6: recovery debe producir artefacto semánticamente no vacío |
| Recovery incomplete $0 repair | $0 existente pero incompleto se completa con sigilos usados y AUD/RSK visibles | `measured` (v1.1.9) | 100% (tests `test_recover_repairs_existing_incomplete_glossary`, `test_recover_incomplete_glossary_content_visible_in_hcortex`) |
| Recovery conformant exit code | `cortex recover` retorna non-zero si el artefacto no pasa validate | `measured` (v1.1.6) | 100% (test `test_recover_returns_nonzero_if_not_conformant`) — v1.1.6 P1-5 |
| Critical field emptiness blocked | FCS/OBJ con `what:""` o `goal:""` bloqueados por E034 | `measured` (v1.1.6) | 100% (test `test_e034_empty_field_blocked`) — v1.1.6 P0-1 |
| Token density (renderer) | tokens HCORTEX-READ / tokens `.cortex` | `target` | ~1.4–1.8× (orientativo, no medido con tokeniser LLM) |
| Decision survival | decisiones/restricciones/pasos preservados por token | `target` | No medido — requiere benchmark con LLM real |
| Compression side effects | Omisiones/distorsiones detectadas en roundtrip | `measured` | 0 en fixtures; pendiente suite adversarial |
| Parser throughput | archivos `.cortex` parseados por segundo | `hypothesis` | Estimado ~500–2000 archivos/s en CPU típica; no benchmark formal — requiere dataset controlado, N corridas, media, mediana, desviación estándar (re-audit H-RA-07) |
| Post-mutation validation gate | Mutaciones CRUD que rompen contrato son rechazadas por defecto | `measured` (v1.1.2) | 100% (tests `test_cli_update_blocked_by_validation`, `test_cli_delete_blocked_by_validation`, `test_cli_move_blocked_by_validation`) |

## Metodología de los benchmarks `measured`

### Roundtrip structural fidelity

```bash
# Reproducible desde la raíz del proyecto:
cd codec-cortex
python -m pytest src/tests/test_acceptance.py::test_criterion_13_roundtrip_verify -v
python -m pytest src/tests/test_audit_gates.py -v
python -m pytest src/tests/test_reaudit_gates.py -v
```

Dataset: 3 fixtures canónicos (`src/tests/fixtures/brain.cortex`,
`package.cortex`, `skill.cortex`) + fixtures inválidos
(`src/tests/invalid/`).

Resultado: 100% de los fixtures válidos producen AST idéntico tras
`.cortex → HCORTEX-EDIT → .cortex`.

### HCORTEX auditability

```bash
cortex render brain.cortex --mode audit --out brain.audit.md
grep -c "source" brain.audit.md  # debe ser ≥ entradas en $1..$N
```

### Recovery completeness

```bash
# Desde un directorio temporal (no usa rutas absolutas del entorno):
cat > /tmp/legacy.cortex <<'EOF'
<!-- SPDX -->
# Heading
$1: X
IDN:agent{name:"legacy"}
EOF
cortex recover /tmp/legacy.cortex --out /tmp/fixed.cortex
cortex verify /tmp/fixed.cortex  # debe reportar el $0 reconstruido + diagnostics
```

### Recovery + embed AUD/RSK + verify --strict (v1.1.2)

```bash
cat > /tmp/legacy.cortex <<'EOF'
$1: X
IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
EOF
cortex recover /tmp/legacy.cortex --out /tmp/fixed.cortex --embed-aud-rsk
cortex verify /tmp/fixed.cortex --strict  # rc=0; AUD/RSK declarados en $0
```

### Post-mutation validation gate (v1.1.2)

```bash
cortex new brain --out /tmp/brain.cortex --force
# update que rompería CNST:blocking → survive:min debe ser rechazado:
cortex update /tmp/brain.cortex CNST:self_contained --set survive=work
# rc=1, no se persiste el cambio
```

## Limites declarados

- **Sin tokeniser LLM**: la densidad de tokens y la supervivencia de
  decisiones por token son `target` porque medirlas requiere invocar
  un tokeniser de modelo específico. No se finge medir lo que no se midió.
- **Sin benchmark adversarial**: el suite actual cubre happy path +
  errores comunes. Una suite adversarial con corpus histórico amplio
  queda como `planned` (ver `STATUS.md`).
- **Throughput hypothesis (re-audit H-RA-07)**: el rango 500–2000
  archivos/s es una hipótesis razonable basada en ejecución local,
  NO un benchmark formal. Para reclasificar a `measured` se requiere:
  dataset controlado, hardware declarado, N corridas, media, mediana,
  desviación estándar e intervalo de confianza.

## Anti-overclaim (SKILL.md §15.3)

Permitido decir:

> `codec-cortex` busca reversibilidad estructural para operaciones de
> codec implementadas y verificadas. HCORTEX ofrece reversibilidad
> contextual, no reconstrucción textual literal.

NO permitido decir:

> `codec-cortex` comprime sin pérdida.

## Reproducibilidad

Todos los benchmarks `measured` son reproducibles desde la raíz del
proyecto extraído del tarball, sin rutas absolutas del entorno:

```bash
# Extraer el tarball en cualquier directorio
tar xzf codec-cortex-<version>.tar.gz
cd codec-cortex

# Instalar (editable o no)
pip install -e .

# Verificar la suite completa
python -m pytest src/tests/ -v

# Demo end-to-end (usa `cortex` del PATH o PYTHONPATH)
bash scripts/cortex_demo_v1_1_2.sh
```

El conteo exacto de tests se obtiene con:

```bash
python -m pytest src/tests/ -q 2>&1 | tail -1
```

No se hardcodea el número de tests en este documento para evitar
desincronización (re-audit H-RA-07: antes decía 61/61, luego 88/88,
ambos desactualizados al crecer la suite).
