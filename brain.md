<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->
<!-- source: brain.cortex — HCORTEX human-readable view -->

# brain.md — HCORTEX de alfred (cerebro local)

> **Perfil: CORTEX-FULL** · v0.2.2 · 2026-06-24 · source: brain.cortex

---

## Foco actual

| source | Campo | Valor |
|--------|-------|-------|
| FCS:primary | Qué | Ciclo CORTEX-CONSOLIDATION-001 completado — 13/13 REs approved. HCORTEX render protocol implementado |
| FCS:primary | Prioridad | high |
| FCS:primary | Estado | active |
| FCS:secondary | Qué | v0.2.2 liberado. Core skill + 5 reglas HCORTEX + 8 pasos de render |
| FCS:secondary | Estado | done |

## Objetivo

| source | Meta | Estado | Criterio de éxito |
|--------|------|:-----:|-------------------|
| OBJ:primary | Ejecutar y aprobar las 6 correcciones HCORTEX (D-01 a D-06) | done | 13/13 REs approved. 5 reglas en $4, 8 pasos en $10 |
| OBJ:secondary | Mantener brain.cortex actualizado | in_progress | brain.cortex refleja ciclo completo |

## Estado operativo

| source | Campo | Valor |
|--------|-------|-------|
| WRK:state | Fase | cierre de ciclo |
| WRK:state | Actual | documentación alineada: README v0.2.2, STATUS, summary en .project-control/ |
| WRK:state | Bloqueado | false |
| WRK:repo | URL | github.com/FidelErnesto03/codec-cortex |
| WRK:repo | Branch | main |
| WRK:repo | Tag | v0.2.2 |

## Restricciones

| source | Regla | Severidad |
|--------|-------|:---------:|
| CNST:limits | Output: HCORTEX. Idioma ES, estructural EN. Memoria canónica: .cortex | work |
| CNST:honesty | No métricas no medidas. Sin claims no soportados | blocking |

## Próximo paso

| source | Acción | Responsable |
|--------|--------|:-----------:|
| STP:next | Decidir próximos pasos: parser, benchmarks automatizados, RE-014, o nuevo ciclo | humano |

## Sesiones recientes

| source | Input | Output | Outcome | Fecha |
|--------|-------|--------|:-------:|-------|
| SES:survival_core_refinement | 12 premisas del arquitecto | RE-004/005/006 refinadas | ok | 2026-06-24 |
| SES:codec_cortex_adoption | Activación CODEC-CORTEX | AGENT.cortex, brain.cortex, HCORTEX | adoptado | 2026-06-24 |
| SES:execution_004_005_006 | RE-004/005/006 approved | SKILL.cortex actualizado ($0-$11) | ejecutado | 2026-06-24 |
| SES:release_v021 | Fidel autorizó release | v0.2.1 tag + GitHub release | publicado | 2026-06-24 |
| SES:skill_migration | SKILL.cortex → Hermes + DIALECT | skill v1.3.0 en ambos | migrado | 2026-06-24 |
| SES:re007_diagnosis | Análisis conversión .cortex→HCORTEX | RE-007 con 6 desviaciones | ok | 2026-06-24 |
| SES:hcortex_corrections | RE-008 a RE-013 (D-01 a D-06) | 5 reglas, 8 pasos, 13/13 REs | completado | 2026-06-24 |

## Lecciones aprendidas

| source | Lección |
|--------|---------|
| LNG:survival_core_emerged | CODEC-CORTEX debe evolucionar de formato denso a sistema de supervivencia contextual. "Cuando todo lo demás se pierde, sobreviven FCS, OBJ, CNST, STP" |
| LNG:section7_means_use | Diseño operativo (§7) = uso funcional del entregable, no pasos de ejecución (que van en §10) |
| LNG:load_vs_degrade | Carga: P0→P5. Degradación: P5→P1. P0 nunca se toca |
| LNG:default_profile_by_mode | Sin perfil: auditoría→FULL, recovery→RECOVERY, trabajo→WORK, emergencia→MIN. Auditoría sin presupuesto → segmentado |
| LNG:precedence_over_budget | explícito > presupuesto > modo > WORK |
| LNG:entries_without_priority | Sin P-level/survive → P5 (solo en FULL) |
| LNG:expansion_type_defines_render | Cada tipo de expansión tiene su estrategia. cuerpo no es tabla K/V |
| LNG:render_order_by_priority | P0→P5, no por número de sección |
| LNG:gov_isolation_mandatory | Sin RE IDs en documentos públicos |

## Conocimiento activo

| source | Área | Detalle |
|--------|------|---------|
| KNW:survival_core | RE-004 | survive + 6 sigilos + 5 contratos flexibles |
| KNW:survival_core | RE-005 | P0-P5 + perfiles conceptuales + degradación directa |
| KNW:survival_core | RE-006 | 2 specs + 5 reglas Skill + CHANGELOG |
| KNW:survival_core | RE-007 | 6 desviaciones HCORTEX — todas corregibles sin parser |
| KNW:survival_sigils | Nuevos | STP, AUD, RSK, NXT, CLAIM, LIM |
| KNW:survival_sigils | Postergados | FIND, IMP, VAL, RES, DOC, ART, TBL |
| KNW:priority_pack | P0 | FCS, OBJ, CNST, STP |
| KNW:priority_pack | P1 | WRK, AUD, RSK, NXT |
| KNW:priority_pack | Carga | P0→P5 |
| KNW:priority_pack | Degradación | P5→P1 |
| KNW:release | Versión | 0.2.2 |
| KNW:release | Siguiente | 0.3.0 |

## Riesgos

| source | Riesgo | Impacto | Mitigación |
|--------|--------|:-------:|------------|
| RSK:premature_release | Release v0.3.0-spec antes de parser | medio | v0.2.2 es PATCH legítimo. Survival Core = spec draft |
| RSK:profile_ambiguity | Perfiles conceptuales ambiguos | bajo | Son criterios de prioridad, no inventarios |
| RSK:glossary_divergence | brain.cortex vs SKILL.cortex $0 divergen | medio | SKILL.cortex $0 = fuente canónica única |

## Claims y límites

| source | Afirmación / Límite | Evidencia |
|--------|---------------------|-----------|
| CLAIM:survival_core | Survival Core especificado, ejecutado y liberado como v0.2.2 (PATCH) | 13/13 REs approved. ROADMAP Phase 2.1 spec draft |
| CLAIM:release_v022 | v0.2.2 es PATCH legítimo bajo semver. HCORTEX render protocol completo | CHANGELOG [0.2.2]. 5 reglas, 8 pasos, 6 correcciones |
| LIM:parser_gap | Reglas P0-P5 y survive se aplican manualmente | Fase actual pre-codec |
| LIM:benchmark_gap | Benchmarks 0.1/0.1b/0.2 son offline/proxy | Automatización requiere parser |

## Auditoría

| source | Métrica | Valor |
|--------|---------|-------|
| AUD:last_release | Versión | v0.2.2 |
| AUD:last_release | Branch | main |
| AUD:last_release | GitHub release | creado |
| AUD:session_outcome | REs aprobadas | 13/13 |
| AUD:session_outcome | quality_contract | 10/10 |
| AUD:session_outcome | PUML validados | 0 errores |
| AUD:session_outcome | Reglas HCORTEX | 5 |
| AUD:session_outcome | Pasos render | 8 |
