# PROTOCOLO CANÓNICO DE BENCHMARK CIENTÍFICO

## CODEC-CORTEX · Evaluación de preservación de evidencia bajo compresión contextual

### 0. Propósito

Este protocolo define un marco canónico, reproducible y extensible para evaluar CODEC-CORTEX y métodos alternativos de preservación, compresión, recuperación y selección de memoria operacional en agentes LLM/SLM.

El objetivo principal no es demostrar que un modelo razona mejor, sino medir con precisión científica qué evidencia sobrevive, qué evidencia se pierde, qué evidencia se contamina y qué método preserva mejor el estado operativo relevante bajo restricciones de contexto.

La evaluación debe poder ser ejecutada por agentes autónomos sin intervención interpretativa humana, manteniendo trazabilidad completa sobre corpus, versiones, tareas, métodos, métricas, resultados y conclusiones permitidas.

---

## 1. Principios científicos obligatorios

### 1.1 Separación entre evidencia y razonamiento

Todo benchmark debe distinguir entre:

* **Disponibilidad de evidencia:** si el contexto generado contiene información suficiente para responder.
* **Accesibilidad de evidencia:** si la información aparece en forma recuperable, trazable y no ambigua.
* **Razonamiento del modelo:** si un LLM utiliza correctamente esa evidencia para producir una respuesta.
* **Calidad operacional:** si la respuesta resultante permite ejecutar una acción correcta, segura y auditada.

Los benchmarks determinísticos solo pueden reclamar resultados sobre disponibilidad, accesibilidad y preservación de evidencia. Los benchmarks con LLM deben declararse como una fase separada.

### 1.2 Reproducibilidad antes que optimización

Ninguna mejora algorítmica debe aceptarse como avance si antes no se puede reproducir el estado de referencia aplicable. La reproducibilidad incluye:

* mismos archivos de corpus;
* mismos hashes;
* mismas tareas;
* mismo tokenizer o proxy de tokens;
* mismos métodos;
* mismos presupuestos;
* mismos resultados agregados;
* mismos resultados por tarea o diferencia explicada.

### 1.3 Comparabilidad estricta

Los métodos pasivos, activos y query-dependent no deben compararse como si fueran equivalentes.

Clasificación obligatoria:

* **Pasivo posicional:** selecciona por posición, sin comprender contenido.
* **Pasivo estructural:** selecciona por estructura, prioridad o sigil.
* **Pasivo semántico:** selecciona por perfil semántico general, sin conocer la pregunta.
* **Activo query-dependent:** selecciona usando la pregunta o intención específica.
* **LLM-assisted:** usa un modelo para resumir, reordenar, juzgar o seleccionar.

Los métodos query-dependent deben reportarse por separado porque poseen ventaja informacional.

### 1.4 No sobreafirmación

Todo informe debe clasificar sus conclusiones en cuatro niveles:

* **Demostrado:** soportado directamente por resultados reproducibles.
* **Parcialmente soportado:** visible en datos, pero limitado por corpus, métrica o escenario.
* **Hipótesis razonable:** sugerido por los resultados, pero requiere experimento adicional.
* **No soportado:** no evaluado o contradicho por los datos.

Está prohibido afirmar que CODEC-CORTEX mejora agentes LLM/SLM si solo se ejecutó evaluación determinística.

---

## 2. Unidad experimental

La unidad experimental mínima es una combinación de:

```text
benchmark_version
corpus_case_id
scenario_id
method_id
budget_tokens
task_id
metric_id
run_id
```

Cada fila de resultado debe poder reconstruirse desde artefactos versionados.

---

## 3. Artefactos obligatorios

Todo benchmark debe producir, como mínimo:

```text
/benchmark/
  manifest.json
  corpus/
    source/
    normalized/
    hashes.json
  tasks/
    tasks.jsonl
    gold_answers.jsonl
    gold_decisions.jsonl
  methods/
    method_registry.json
    method_configs/
  metrics/
    metric_registry.json
    metric_specs/
  runs/
    scored_tasks.csv
    summary_tasks.csv
    errors.csv
    provenance.csv
  reports/
    scientific_report.md
    claim_matrix.md
    regression_report.md
    metric_discovery_report.md
```

### 3.1 manifest.json

Debe incluir:

* versión del benchmark;
* fecha;
* autor o agente ejecutor;
* commit o hash del proyecto;
* versión de CODEC-CORTEX;
* versión del harness;
* versión de SKILL.cortex usada;
* versión de brain.cortex usada, si aplica;
* entorno de ejecución;
* tokenizer o proxy de tokens;
* lista de métodos;
* lista de escenarios;
* lista de métricas;
* presupuesto de tokens;
* semillas, si hay aleatoriedad;
* configuración LLM, si existe fase LLM.

---

## 4. Corpus

### 4.1 Requisitos mínimos

Cada corpus case debe contener:

* fuente original;
* representación `.cortex`;
* representación humana o auditable, si existe;
* representación alternativa comparable: raw prose, markdown, JSON, YAML-like u otra;
* metadatos de dominio;
* propósito operacional;
* estado actual;
* restricciones;
* riesgos;
* decisiones;
* referencias;
* trazas de fuente.

### 4.2 Hashes obligatorios

Todo archivo usado en el benchmark debe tener hash SHA-256 registrado.

El agente autónomo debe fallar la ejecución si:

* falta un hash;
* un hash no coincide;
* se modifica un corpus sin actualizar versión;
* se mezclan corpus de versiones distintas sin declararlo.

### 4.3 Corpus mínimo por madurez

Nivel 0 — Interno:

* 3 a 5 casos del propio proyecto.
* Útil para desarrollo inicial.
* No permite claims de generalización.

Nivel 1 — Operacional controlado:

* 8 a 12 casos.
* 2 o más dominios.
* Permite claims internos moderados.

Nivel 2 — Multidominio:

* mínimo 10 dominios;
* 2 a 3 casos por dominio;
* formatos alternativos derivados de la misma fuente.
* Permite evaluar validez externa.

Nivel 3 — Adversarial:

* incluye casos corruptos, conflictivos, ambiguos, incompletos y con evidencia enterrada.
* Permite evaluar robustez.

---

## 5. Tareas

### 5.1 Tipos de tareas

Cada benchmark debe incluir al menos cuatro tipos:

#### QA factual

Evalúa si el contexto conserva información necesaria para responder una pregunta concreta.

#### Decisión operacional

Evalúa si el método conserva evidencia suficiente para clasificar una acción como:

```text
allow
block
planned
current
unknown
```

#### Trazabilidad

Evalúa si el contexto conserva fuente, origen, referencia o justificación.

#### Seguridad contra invención

Evalúa si el contexto evita convertir afirmaciones futuras, prohibidas, obsoletas o no soportadas en hechos actuales.

### 5.2 Esquema canónico de tarea

```json
{
  "task_id": "T-0001",
  "case_id": "brain",
  "scenario_id": "reduced_window",
  "task_type": "qa",
  "question": "What is the current objective?",
  "gold_answer": "Preserve operational evidence under compression",
  "expected_terms": ["preserve", "operational evidence", "compression"],
  "forbidden_terms": ["improves LLM reasoning"],
  "gold_decision": null,
  "required_sources": ["OBJ", "FCS"],
  "priority_scope": ["P0", "P1"],
  "temporal_scope": "current",
  "severity": "normal",
  "rationale": "Tests preservation of objective under restricted context."
}
```

### 5.3 Reglas de oro

Toda tarea debe tener:

* respuesta esperada;
* términos esperados;
* términos prohibidos, si aplica;
* fuente o sigil esperado;
* prioridad esperada;
* alcance temporal;
* criterio de scoring;
* justificación.

Las tareas sin gold verificable deben excluirse o marcarse como exploratorias.

---

## 6. Escenarios obligatorios

### 6.1 Full-context comparison

Evalúa representaciones completas sin restricción de tokens.

Pregunta científica:
¿Qué formato conserva mayor densidad de evidencia cuando todo el contexto está disponible?

Métodos típicos:

* full_cortex;
* full_hcortex;
* full_raw_prose;
* full_md_summary;
* full_json;
* full_yaml_like.

### 6.2 Reduced-window compression

Evalúa selección bajo presupuesto limitado.

Presupuestos canónicos:

```text
256, 384, 512, 768, 1024, 1536, 2048, 3072, 4096, 6144, 8192
```

Pregunta científica:
¿Qué evidencia crítica sobrevive cuando el contexto no cabe completo?

### 6.3 Middle-work adversarial

Coloca evidencia crítica en el centro del contexto, rodeada de ruido anterior y posterior.

Pregunta científica:
¿Qué método resiste mejor la pérdida de información enterrada en el medio?

### 6.4 Stale-state conflict

Incluye estados antiguos y actuales en conflicto.

Pregunta científica:
¿El método distingue correctamente entre histórico, vigente, planeado y futuro?

### 6.5 Blocking-constraint survival

Incluye restricciones severas que bloquean una acción.

Pregunta científica:
¿El método conserva restricciones críticas o permite acciones peligrosas?

### 6.6 Unsupported-claim suppression

Incluye afirmaciones tentativas, prohibidas o no demostradas.

Pregunta científica:
¿El método evita que claims no soportados emerjan como hechos?

### 6.7 Corrupted-memory tolerance

Introduce líneas corruptas, incompletas o mal formadas.

Pregunta científica:
¿El método falla de forma segura sin inventar contenido?

### 6.8 Multi-instance sigil preservation

Incluye múltiples instancias del mismo sigil con roles diferentes.

Pregunta científica:
¿El método evita aplanar señales distintas como si fueran equivalentes?

---

## 7. Métodos bajo comparación

### 7.1 Baselines obligatorios

Todo benchmark debe incluir:

* `recent_tail_raw`
* `head_tail_raw`
* `head_json`
* `head_markdown_summary`
* `semantic_field_pack`
* `keyword_retrieval_raw`
* `cortex_priority_pack`

### 7.2 Métodos CODEC-CORTEX

Cada variante debe nombrarse explícitamente:

```text
cortex_priority_pack_v1
cortex_priority_pack_adaptive
cortex_priority_pack_semantic_hybrid
cortex_priority_pack_ablation_no_P0
cortex_priority_pack_ablation_no_temporal
```

Ninguna variante debe reemplazar silenciosamente a otra.

### 7.3 Ablaciones obligatorias

Para entender causalidad, deben ejecutarse variantes con partes removidas:

* sin prioridad P0/P1;
* sin información temporal;
* sin severidad;
* sin trazabilidad de fuente;
* sin constraints;
* sin riesgos;
* sin auditoría.

Si CPP gana, debe poder explicarse por qué gana.

---

## 8. Métricas canónicas

### 8.1 Métricas actuales

#### Exact Answer Score — EAS

Valor binario. Retorna 1 si aparece al menos un término esperado.

#### Expected Term Coverage — ETC

Fracción de términos esperados presentes.

#### Gold Overlap F1

Solapamiento tokenizado entre respuesta extraída y gold answer.

#### Decision Accuracy — DA

Porcentaje de decisiones clasificadas correctamente.

#### Average Context Tokens — Avg CT

Cantidad promedio de tokens usados por el contexto generado.

#### Average Answer Tokens — Avg AT

Cantidad promedio de tokens usados por la respuesta o evidencia extraída.

### 8.2 Métricas obligatorias nuevas

#### P0 Survival Rate

Porcentaje de entradas P0 preservadas bajo presupuesto.

#### P1 Survival Rate

Porcentaje de entradas P1 preservadas bajo presupuesto.

#### Blocking Constraint False Negative Rate

Porcentaje de restricciones bloqueantes omitidas cuando debían conservarse.

Objetivo ideal: 0.

#### Unsupported Claim False Positive Rate

Porcentaje de claims no soportados que aparecen como evidencia válida.

Objetivo ideal: 0.

#### Current/Future Confusion Rate

Porcentaje de casos donde un estado futuro, planeado o tentativo se interpreta como actual.

#### Source Traceability Rate

Porcentaje de respuestas donde la evidencia conserva referencia de origen.

#### Budget Violation Rate

Porcentaje de ejecuciones que exceden el presupuesto de tokens.

Objetivo obligatorio: 0.

#### Middle Recovery Delta

Diferencia entre el método evaluado y el mejor baseline posicional en escenario middle-work.

#### Query Dependency Delta

Diferencia entre el mejor método pasivo y el mejor método query-dependent.

#### Evidence Density

Relación entre evidencia útil y tokens consumidos.

Forma recomendada:

```text
evidence_density = weighted_score / context_tokens
```

Reportar también por cada 1.000 tokens.

---

## 9. Incorporación de métricas por descubrimiento empírico

El benchmark debe permitir que agentes autónomos propongan nuevas métricas, pero no deben incorporarlas automáticamente como métricas canónicas.

### 9.1 Ciclo de descubrimiento

Una métrica nueva nace cuando ocurre al menos una de estas condiciones:

* aparece un patrón de fallo repetido no explicado por métricas actuales;
* dos métodos empatan en métricas globales pero fallan de forma distinta;
* una decisión operacional incorrecta no queda reflejada en EAS, ETC, F1 o DA;
* una regresión no puede explicarse con métricas existentes;
* el análisis cualitativo detecta contaminación, dilución, pérdida temporal o pérdida de fuente.

### 9.2 Registro de métrica candidata

Toda métrica nueva debe registrarse así:

```json
{
  "metric_id": "M-CAND-001",
  "name": "Temporal Polarity Error Rate",
  "status": "candidate",
  "failure_mode": "planned state interpreted as current",
  "formula": "...",
  "required_fields": ["temporal_scope", "gold_decision"],
  "expected_range": "0..1",
  "lower_is_better": true,
  "validation_cases": ["stale_state_conflict"],
  "rationale": "Existing decision accuracy hides temporal polarity errors."
}
```

### 9.3 Estados de una métrica

```text
candidate
experimental
validated
canonical
deprecated
rejected
```

### 9.4 Criterios de promoción

Una métrica pasa a `validated` si:

* detecta fallos reales no visibles por métricas existentes;
* es reproducible en dos ejecuciones;
* no depende de interpretación subjetiva;
* puede calcularse automáticamente;
* tiene valor diagnóstico claro;
* no incentiva comportamiento artificial o sobreajuste.

Pasa a `canonical` si además:

* se mantiene útil en al menos dos versiones de benchmark;
* aplica a más de un corpus o escenario;
* mejora la capacidad de explicar regresiones;
* tiene umbrales interpretables.

---

## 10. Ejecución autónoma por agentes

### 10.1 Flujo obligatorio

El agente autónomo debe ejecutar:

```text
1. Leer SKILL.cortex.
2. Leer manifest.json del benchmark.
3. Validar hashes del corpus.
4. Validar compatibilidad de tareas.
5. Validar registro de métodos.
6. Validar registro de métricas.
7. Ejecutar dry-run.
8. Ejecutar benchmark completo.
9. Generar scored_tasks.csv.
10. Generar summary_tasks.csv.
11. Generar regression_report.md.
12. Generar metric_discovery_report.md.
13. Generar claim_matrix.md.
14. Emitir conclusión limitada por evidencia.
```

### 10.2 Reglas de seguridad científica

El agente debe detenerse si:

* no puede verificar hashes;
* falta gold answer;
* una métrica no tiene fórmula;
* un método query-dependent está mezclado con métodos pasivos sin separación;
* se excede presupuesto de tokens;
* se detecta cambio no declarado en corpus;
* se intenta reclamar mejora LLM sin fase LLM.

### 10.3 Comportamiento ante ambigüedad

Si una tarea es ambigua, el agente no debe inferir una respuesta. Debe clasificarla como:

```text
invalid_task
ambiguous_gold
missing_source
metric_inapplicable
```

---

## 11. Evaluación LLM separada

La fase LLM es opcional, pero si se ejecuta debe estar separada.

### 11.1 Diseño mínimo

* mínimo tres modelos;
* mínimo tres plantillas de prompt;
* temperatura 0.0 como baseline;
* análisis adicional con temperatura 0.3 y 0.7;
* mínimo cinco repeticiones si hay aleatoriedad;
* evaluación de correctness, completeness y hallucination rate;
* juez humano o LLM-as-judge con rúbrica fija;
* reporte estadístico separado.

### 11.2 Prohibición de mezcla

No se deben mezclar resultados determinísticos y LLM en una sola métrica global.

El informe debe distinguir:

```text
Deterministic Evidence Preservation
Model-Based Response Quality
Operational Safety Outcome
```

---

## 12. Análisis de regresión

### 12.1 Tipos de regresión

#### Regresión de harness

Mismos inputs, mismo método, diferente output. Es grave.

#### Regresión de corpus

El nuevo corpus es más difícil. No necesariamente es negativa.

#### Regresión de algoritmo

El método cambió y perdió rendimiento comparable.

#### Regresión de métrica

Cambió la fórmula, tokenización o agregación.

#### Regresión esperada

Se endureció el benchmark para medir fallos antes invisibles.

### 12.2 Reporte obligatorio

Toda regresión debe explicar:

* qué cambió;
* dónde cambió;
* cuántas tareas cambiaron;
* qué prioridades fueron afectadas;
* qué escenarios fueron afectados;
* si la pérdida es aceptable;
* si requiere rollback, ajuste o aceptación documentada.

---

## 13. Criterios de aceptación

Un benchmark se considera científicamente válido si:

* reproduce fixtures históricas;
* declara corpus y hashes;
* separa métodos pasivos/query-dependent;
* separa evaluación determinística/LLM;
* reporta métricas conocidas;
* documenta métricas candidatas;
* identifica amenazas a la validez;
* genera claim matrix;
* permite reconstrucción por tarea;
* no sobreafirma.

---

## 14. Claim matrix obligatoria

Todo informe final debe contener:

```text
Claim
Status
Evidence
Limitations
Allowed wording
Forbidden wording
```

Ejemplo:

```text
Claim: CPP outperforms positional truncation in middle-work.
Status: Supported.
Evidence: Middle Recovery Delta positive across budgets.
Allowed wording: CPP mitigates middle-buried evidence loss.
Forbidden wording: CODEC-CORTEX solves agent memory.
```

---

## 15. Resultado esperado

El resultado del benchmark no es solo una tabla de scores. Debe producir una explicación científica sobre:

* qué método preserva evidencia;
* qué método pierde evidencia;
* qué tipo de evidencia se pierde;
* qué presupuesto es óptimo;
* dónde aparece ruido;
* qué claims son legítimos;
* qué claims siguen sin soporte;
* qué métrica nueva se justifica;
* qué debe cambiar en el protocolo.

Este protocolo debe permitir que cada nueva ejecución sea más informativa que la anterior, sin sacrificar reproducibilidad, objetividad ni capacidad evolutiva.
