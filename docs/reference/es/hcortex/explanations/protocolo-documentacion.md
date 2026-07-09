---
view: display-only
reversible: false
profile: HCORTEX-EXPLANATION
source: skill/cortex/SKILL.md §11, §12, §2, §8, §9
mode: READABLE
---

# Protocolo Documental E3 — Explicación Profunda

> **source:** skill/cortex/SKILL.md §11:DESC:hcortex_def · §12:DESC:out_def · §8:!:survive_priority · §9:KNW:profile_*

Este documento explica el porqué detrás de la arquitectura documental de CODEC-CORTEX.

---

## 1. Por qué dos formatos

| Aspecto | CORTEX | HCORTEX | source |
|---------|--------|---------|--------|
| Audiencia | Agentes y CLI | Humanos | `$11:DESC:hcortex_def` |
| Formato | Estructurado denso | Tablas Markdown, listas, PUML | `$11:DESC:hcortex_def` |
| Fuente de verdad | ✅ Sí | No (derivado) | `!hcortex_expand` |
| Roundtrip | ✅ Sí | ✅ Sí (vía VIEW) | `$13:VIEW:*` |
| Autocontenido | ✅ Sí ($0) | No | `$11:DESC:hcortex_def` |

| Limitación Markdown | Por qué importa | source |
|---------------------|----------------|--------|
| Sin sistema de contratos | Sin validación de tipos | `$7:CNST:contract_*` |
| Parseo no determinista | Agentes no pueden parsear | `!type_strict` |
| Sin roundtrip | No se puede verificar fidelidad | `$13:VIEW:*` |
| Sin glosario/sigilos | Sin vocabulario estructurado | `$0:canonical_sigils` |

---

## 2. La cadena de verdad

| Capa | Formato | Verificable | source |
|:----:|:-------:|:-----------:|--------|
| Protocolo (`skill/cortex/SKILL.md`) | CORTEX | ✅ | `$1:REF:*` |
| API (`docs/cortex/api/*.cortex`) | CORTEX | ✅ | `$1:REF:*` |
| Referencia HCORTEX | HCORTEX | ✅ (vía VIEW) | `$11:KNW:hc_modes` |
| Tutoriales / How-to / Explicaciones | HCORTEX (display) | ❌ | `$11:KNW:hc_modes` |

---

## 3. Por qué no hay LLM en el codec

| Operación | Usa LLM? | source |
|-----------|:--------:|--------|
| Parsear `.cortex` → AST | ❌ No | `!type_strict` |
| Codificar AST → `.cortex` | ❌ No | `!type_strict` |
| Verificar estructura | ❌ No | `!:precommit_verify` |
| Renderizar HCORTEX | ❌ No | `!hcortex_expand` |
| `cortex docstring` | ❌ No | `docs/cortex/api/docstring.cortex` |
| Respuesta CORTEX-OUT | ✅ Sí | `$12:DESC:out_def` |

---

## 4. Modelo de maduración (4 etapas)

| Etapa | Puede producir | Puede verificar | source |
|-------|---------------|:---------------:|--------|
| Novato | `.cortex` básico con FCS/OBJ | `verify --strict` | `$8:!:survive_priority` |
| Avanzado | SES, LNG, WRK, STP | roundtrip-bidir | `$3:HDL:session_close` |
| Competente | Brain completo | Suite completa | `$5:CNST:sep_l2` |
| Proficiente | Gestión autónoma | Todos los gates | `$5:CNST:sep_l2` |

**Umbrales Fibonacci:** score 1→SES, 3→LNG, 5→candidato, 8→confirmación humana, 13→KNW, 21→crítico.

---

## 5. Survival Core P0-P5

| Nivel | Presupuesto | Preserva | source |
|:-----:|:-----------:|----------|--------|
| P0 | ~300t | FCS, OBJ, CNST, STP | `$8:!:survive_priority` |
| P1 | ~600t | WRK, AUD, RSK, NXT | `$8:!:survive_priority` |
| P2 | ~1Kt | CLAIM, LIM, KNW:active | `$8:!:survive_priority` |
| P3-P5 | 2Kt+ | SES, REF, DIAG, historial | `$8:!:survive_priority` |

---

## 6. CORTEX-OUT vs HCORTEX

| | HCORTEX | CORTEX-OUT | source |
|---|---|---|---|
| Fuente | AST de `.cortex` | Razonamiento del agente | `$11:DESC:hcortex_def` · `$12:DESC:out_def` |
| Roundtrip | ✅ Sí | ❌ No aplica | `$12:!:out_independence` |
| Salida | Tablas + PUML | Lenguaje natural + bloques | `$12:KNW:out_blocks` |

---

## 7. Riesgos controlados

| Riesgo | Control | source |
|--------|---------|--------|
| Referencia API duplicada | Fuente única en `docs/cortex/api/` | `!:docs_source_of_truth` |
| Barrera de adopción humana | `docs/README.md` en Markdown | `docs/cortex/specs/documentation-protocol.cortex` |
| Ayuda CLI desalineada | `cortex docstring` deriva de CORTEX | `docs/cortex/api/docstring.cortex` |
| Alucinación en verificación | Codec determinista | `!type_strict` |
