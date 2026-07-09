<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX -->
<!-- SPDX-License-Identifier: MIT -->

# Reporte de Descubrimiento de Métricas — Benchmark CODEC-CORTEX v1.0.0

> **Perfil: HCORTEX-AUDIT** · source: análisis cualitativo de runs/scored_tasks.csv

## 1. Marco de descubrimiento (§9 del protocolo)

Una métrica nueva nace cuando ocurre al menos una de estas condiciones:

| Condición | Detectada |
|-----------|:---:|
| Patrón de fallo repetido no explicado por métricas actuales | Sí (ver M-CAND-001, M-CAND-002) |
| Dos métodos empatan en métricas globales pero fallan de forma distinta | Sí (ver M-CAND-003) |
| Decisión operacional incorrecta no reflejada en EAS/ETC/F1/DA | Sí (ver M-CAND-004) |
| Regresión no explicable con métricas existentes | No (sin regresiones) |
| Análisis cualitativo detecta contaminación/dilución/pérdida temporal/pérdida de fuente | Sí (ver M-CAND-005, M-CAND-006) |

---

## 2. Métricas candidatas propuestas

### M-CAND-001: Sigil Role Confusion Rate (SRCR)

| Campo | Valor |
|-------|-------|
| **metric_id** | M-CAND-001 |
| **name** | Sigil Role Confusion Rate |
| **status** | candidate |
| **failure_mode** | Múltiples instancias del mismo sigil con roles diferentes son aplanadas como equivalentes |
| **formula** | `SRCR = sum(1 for instance in extracted if role not distinguishable) / total_instances` |
| **required_fields** | `sigil_id`, `instance_name`, `role` |
| **expected_range** | 0..1 |
| **lower_is_better** | True |
| **validation_cases** | `multi_instance_sigil` |
| **rationale** | En el escenario `multi_instance_sigil`, los baselines posicionales tratan FCS:primary, FCS:secondary, FCS:tertiary como una sola señal. CPP los preserva como entradas separadas (P0 para primary, P2/P3 para otros). Sin SRCR, esta diferencia no es visible. |

**Justificación empírica**: En `multi_instance_sigil`, `keyword_retrieval_raw` colapsa múltiples instancias del mismo sigil en un solo chunk relevante. CPP preserva la distinción. Actualmente no hay métrica que capture esto.

### M-CAND-002: Operational Actionability Score (OAS)

| Campo | Valor |
|-------|-------|
| **metric_id** | M-CAND-002 |
| **name** | Operational Actionability Score |
| **status** | candidate |
| **failure_mode** | El contexto preserva información pero no permite ejecutar una acción correcta, segura y auditada |
| **formula** | `OAS = (has_FCS + has_OBJ + has_STP + has_CNST_blocking + has_AUD_or_RSK) / 5` |
| **required_fields** | `FCS`, `OBJ`, `STP`, `CNST:blocking`, `AUD|RSK` |
| **expected_range** | 0..1 |
| **lower_is_better** | False |
| **validation_cases** | `reduced_window_512`, `corrupted_memory_tolerance` |
| **rationale** | EAS y ETC miden si aparece un término, pero no si el contexto permite **ejecutar** una acción. OAS captura si los 5 elementos mínimos para acción operacional están presentes. |

**Justificación empírica**: `head_json` obtiene EAS = 0.971 pero su P0_survival = 0.66, indicando que aunque encuentra términos, no preserva los 5 elementos críticos. OAS haría visible esta brecha.

### M-CAND-003: Family-Conditional Parity Gap (FCPG)

| Campo | Valor |
|-------|-------|
| **metric_id** | M-CAND-003 |
| **name** | Family-Conditional Parity Gap |
| **status** | candidate |
| **failure_mode** | Dos métodos con mismo WS global fallan de forma distinta según familia |
| **formula** | `FCPG = max(|WS_method_A - WS_method_B|) over scenarios where both are in same family` |
| **required_fields** | `method_family`, `scenario_id`, `weighted_score` |
| **expected_range** | 0..max(WS) |
| **lower_is_better** | True |
| **validation_cases** | Comparación entre `recent_tail_raw` y `head_tail_raw` (ambos posicionales) |
| **rationale** | `recent_tail_raw` y `head_tail_raw` empatan en WS global (4.62) pero difieren en Evidence Density (0.0148 vs 0.0079). FCPG capturaría esta diferencia intra-familia. |

### M-CAND-004: Decision-Context Sufficiency (DCS)

| Campo | Valor |
|-------|-------|
| **metric_id** | M-CAND-004 |
| **name** | Decision-Context Sufficiency |
| **status** | candidate |
| **failure_mode** | Decisión operacional incorrecta no reflejada en EAS/ETC/F1/DA |
| **formula** | `DCS = 1 if (CNST_blocking_present AND STP_present AND gold_decision inferable) else 0` |
| **required_fields** | `CNST:blocking`, `STP`, `gold_decision` |
| **expected_range** | 0..1 |
| **lower_is_better** | False |
| **validation_cases** | `blocking_constraint_survival`, tareas tipo `decision` |
| **rationale** | DA en este benchmark es 0.25 para todos los métodos, incluyendo CPP. Esto no significa que CPP falle, sino que la decisión correcta requiere razonamiento LLM. DCS mide si el **contexto** tiene suficiente información para que un LLM pueda decidir correctamente. |

**Justificación empírica**: CPP preserva CNST blocking (BCFNR = 0) y STP (P0_survival = 1.0), por lo que DCS = 1 para CPP. `keyword_retrieval_raw` pierde constraints (BCFNR = 0.32), por lo que DSC sería menor.

### M-CAND-005: Source Dilution Rate (SDR)

| Campo | Valor |
|-------|-------|
| **metric_id** | M-CAND-005 |
| **name** | Source Dilution Rate |
| **status** | candidate |
| **failure_mode** | La referencia de origen (`source:`) está presente pero diluida entre ruido |
| **formula** | `SDR = 1 - (source_tags_in_extracted / source_tags_in_full_cortex)` |
| **required_fields** | `source:`, sigil_id |
| **expected_range** | 0..1 |
| **lower_is_better** | True |
| **validation_cases** | `reduced_window_512`, `middle_work_adversarial` |
| **rationale** | STR es binario (1 si hay `source:`, 0 si no). Pero `source:` puede estar presente en solo 2 de 10 entradas, dando STR = 1 aunque se haya perdido 80 % de la trazabilidad. SDR mediría la fracción de fuentes preservadas. |

### M-CAND-006: Temporal Polarity Error Rate (TPER)

| Campo | Valor |
|-------|-------|
| **metric_id** | M-CAND-006 |
| **name** | Temporal Polarity Error Rate |
| **status** | candidate |
| **failure_mode** | Estado planeado o futuro interpretado como actual |
| **formula** | `TPER = sum(1 for entry in extracted if temporal_label_wrong) / total_temporal_entries` |
| **required_fields** | `temporal_scope`, `gold_decision` |
| **expected_range** | 0..1 |
| **lower_is_better** | True |
| **validation_cases** | `stale_state_conflict` |
| **rationale** | CFCR mide confusión current/future pero es muy gruesa (0.000 para todos los métodos en este benchmark). TPER sería más fino: detectaría si `OBJ:primary status:planned` es tratado como `current`. |

---

## 3. Estados del ciclo de vida (§9.3)

| Estado | Significado | Métricas en este estado |
|--------|-------------|------------------------|
| **candidate** | Recién propuesta, requiere validación | M-CAND-001, M-CAND-002, M-CAND-003, M-CAND-004, M-CAND-005, M-CAND-006 |
| **experimental** | Implementada pero no estable | (ninguna) |
| **validated** | Detecta fallos reales, reproducible, no subjetiva | (ninguna — requiere segunda ejecución) |
| **canonical** | Estable, multi-corpus, multi-versión | (las 15 ya canónicas en `metric_registry.json`) |
| **deprecated** | Reemplazada | (ninguna) |
| **rejected** | Descartada tras validación | (ninguna) |

---

## 4. Criterios de promoción (§9.4)

Para que una métrica candidata pase a `validated`, debe cumplir:

| Criterio | M-CAND-001 | M-CAND-002 | M-CAND-003 | M-CAND-004 | M-CAND-005 | M-CAND-006 |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|
| Detecta fallos reales no visibles por métricas existentes | Sí | Sí | Sí | Sí | Sí | Sí |
| Reproducible en dos ejecuciones | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| No depende de interpretación subjetiva | Sí | Sí | Sí | Sí | Sí | Sí |
| Puede calcularse automáticamente | Sí | Sí | Sí | Sí | Sí | Sí |
| Tiene valor diagnóstico claro | Sí | Sí | Sí | Sí | Sí | Sí |
| No incentiva sobreajuste | Sí | Sí | Sí | Sí | Sí | Sí |

Para pasar a `canonical`, además debe:

| Criterio | Estado |
|----------|--------|
| Mantenerse útil en al menos dos versiones de benchmark | Pendiente (primera versión) |
| Aplicar a más de un corpus o escenario | Sí para todas (excepto M-CAND-001 limitada a multi_instance) |
| Mejorar capacidad de explicar regresiones | Sí para M-CAND-002, M-CAND-004 |
| Tener umbrales interpretables | Pendiente de calibración |

---

## 5. Plan de validación

| Paso | Acción | Plazo |
|------|--------|-------|
| 1 | Implementar las 6 métricas candidatas en el harness | Próxima iteración |
| 2 | Re-ejecutar benchmark con métricas candidatas | Próxima iteración |
| 3 | Verificar que aportan información no redundante (correlación < 0.7 con métricas canónicas) | Próxima iteración |
| 4 | Si validan, promover a `validated` | Tras paso 3 |
| 5 | Tras 2 versiones de benchmark estables, promover a `canonical` | Versión 1.2.0+ |

---

## 6. Conclusión

Se proponen **6 métricas candidatas** que capturan fallos no visibles con las 15 métricas canónicas actuales. Las más prometedoras son:

1. **M-CAND-002 (OAS)**: mide accionabilidad operacional, complementa EAS/ETC.
2. **M-CAND-004 (DCS)**: mide suficiencia de contexto para decisión, complementa DA.
3. **M-CAND-005 (SDR)**: mide dilución de fuente, complementa STR binario.

Estas tres métricas requieren validación en la próxima iteración del benchmark (corpus L2 expandido + re-ejecución).
