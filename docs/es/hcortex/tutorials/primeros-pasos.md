---
view: display-only
reversible: false
profile: HCORTEX-TUTORIAL
source: skill/cortex/SKILL.md §2, docs/cortex/api/
mode: READABLE
---

# Primer uso de CODEC-CORTEX

> **source:** skill/cortex/SKILL.md §2:DESC:purpose · skill/cortex/SKILL.md §9:KNW:profile_*

Este tutorial guía por un ciclo completo: instalar el CLI, crear un cerebro funcional, verificarlo, explorarlo, cerrar una sesión y entender la salida.

---

## 1. Instalación

**Vía PyPI (recomendado):**

```bash
pip install codec-cortex
```

**Desde fuente (desarrollo):**

```bash
cd cli
pip install -e .[dev]
```

**Verificar:**

```bash
cortex --version
# Esperado: 0.4.1 o superior
```

---

## 2. Crear tu primer brain

| Sección | Contenido | source |
|:-------:|-----------|--------|
| `$0` | Glosario (declara sigilos válidos) | `$0:canonical_sigils` |
| `$1` | Identidad (metadatos del proyecto) | `$1:IDN:project` |
| `$2` | Propósito + axiomas | `$2:DESC:purpose` |

```bash
cortex new brain.cortex
cortex inspect brain.cortex
```

---

## 3. Agregar foco y objetivo

```bash
cortex add brain.cortex --section 3 --sigil FCS --name primary \
  --attrs 'what:"Aprender CODEC-CORTEX" priority:high status:current survive:min'

cortex add brain.cortex --section 3 --sigil OBJ --name first \
  --attrs 'goal:"Completar el tutorial" status:current success:"verify pasa" survive:min'

cortex inspect brain.cortex
```

---

## 4. Verificar

```bash
cortex verify --strict brain.cortex
# Esperado: 0 errores, 0 warnings
```

| Problema | source |
|----------|--------|
| Campos requeridos faltantes | `$7:CNST:contract_fcs` |
| Sigilo desconocido | `!:extend_glossary` |

---

## 5. Agregar trabajo y pasos

```bash
cortex add brain.cortex --section 4 --sigil WRK --name tutorial \
  --attrs 'phase:"aprendizaje" current:"siguiendo pasos" status:current survive:work'

cortex add brain.cortex --section 4 --sigil STP --name verificar_setup \
  --attrs 'action:"Ejecutar cortex verify --strict" reason:"confirmar brain válido" owner:user status:current survive:work'
```

---

## 6. Registrar una sesión

```bash
cortex add brain.cortex --section 5 --sigil SES --name primer_tutorial \
  --attrs 'input:"Instalé CLI y creé brain.cortex" \
           output:"Brain verificado pasa strict check" \
           outcome:"Entendí estructura básica .cortex" date:2026-07-01'

cortex add brain.cortex --section 5 --sigil LNG --name verificar_primero \
  --attrs 'type:lesson cause:"Primera ejecución de verify" \
           lesson:"Siempre agregar campos requeridos del contrato" \
           prevention:"Revisar $0:contract_* antes de agregar entradas"'
```

---

## 7. Ejecutar benchmark

| Acción | Comando | source |
|--------|---------|--------|
| Listar suites | `cortex benchmark --list` | `docs/cortex/api/benchmark.cortex` |
| Inspeccionar | `cortex benchmark --inspect v2.0.0` | `docs/cortex/api/benchmark.cortex` |

---

## 8. Generar docstrings

| Acción | Comando | source |
|--------|---------|--------|
| Un comando | `cortex docstring canonicalize` | `docs/cortex/api/docstring.cortex` |
| Todos | `cortex docstring --all` | `docs/cortex/api/docstring.cortex` |

---

## 9. Entender la salida CORTEX-OUT

| Bloque | Contenido | source |
|--------|-----------|--------|
| **Resultado** | Respuesta directa / veredicto | `$12:KNW:out_blocks` |
| **Criterio** | Juicio técnico | `$12:KNW:out_blocks` |
| **Evidencia** | Hechos verificables | `$12:KNW:out_blocks` |
| **Riesgo** | Problemas o límites | `$12:KNW:out_blocks` |
| **Acción** | Próximo paso | `$12:KNW:out_blocks` |
| **Límite** | Qué no se sabe | `$12:KNW:out_blocks` |

---

## 10. Cerrar el ciclo

| Paso | Comando | source |
|:----:|---------|--------|
| 1 | `cortex verify --strict brain.cortex` | `docs/cortex/api/verify.cortex` |
| 2 | `cortex doctor --scan-secrets brain.cortex` | `docs/cortex/api/doctor.cortex` |
| 3 | `cortex verify --strict skill/cortex/SKILL.md` | `docs/cortex/api/verify.cortex` |
| 4 | `cortex verify-view skill/cortex/SKILL.md` | `docs/cortex/api/verify.cortex` |
| 5 | `cortex roundtrip-bidir skill/cortex/SKILL.md` | `docs/cortex/api/convert.cortex` |

---

## Criterio

| Regla | Motivo | source |
|------|--------|--------|
| Usar `docs/README.md` como entrada | No exige conocer el protocolo | `docs/cortex/specs/documentation-protocol.cortex` |
| Usar `docs/es/hcortex/` para humanos | Lectura densa y auditada | `$11:DESC:hcortex_def` |
| Usar `docs/cortex/api/` para agentes | Fuente autocontenida y verificable | `!:docs_source_of_truth` |
