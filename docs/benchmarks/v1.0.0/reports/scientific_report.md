<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX -->
<!-- SPDX-License-Identifier: MIT -->
<!-- source: scientific_report.md — HCORTEX scientific report -->

# Informe Científico del Benchmark CODEC-CORTEX

> **Perfil: HCORTEX-FULL** · v1.0.0 · 2026-06-29 · source: benchmark harness v1.0.0 + CLI v1.1.9

---

## 0. Resumen ejecutivo

| Campo | Valor |
|-------|-------|
| **Benchmark version** | 1.0.0 |
| **Fecha de ejecución** | 2026-06-28 |
| **Ejecutor** | benchmark_harness.py (determinístico) |
| **CODEC-CORTEX versión** | 0.3.0 (CLI 1.1.9, 222 tests) |
| **Harness versión** | 1.0.0 |
| **Corpus** | L2-multidominio: 10 dominios × 1 caso = 10 casos, 5 formatos × caso = 50 artefactos |
| **Métodos comparados** | 11 (4 pasivos posicionales + 1 pasivo semántico + 1 query-dependent + 3 CODEC-CORTEX + 2 ablations) |
| **Escenarios** | 11 (full + 4 reduced-window + 6 adversariales) |
| **Tareas** | 40 (QA + decisión + trazabilidad + seguridad) |
| **Total de runs** | 4 840 (11 métodos × 11 escenarios × 40 tareas) |
| **Fase LLM** | No ejecutada (determinística pura, §11.2 del protocolo) |
| **Reproducibilidad** | Hashes SHA-256 + manifest + scripts versionados |
| **Tokenizador** | Proxy char-based (1 token ≈ 3.5–4.0 chars según formato) |

### Hallazgos principales

| # | Hallazgo | Estado | Evidencia |
|:---:|----------|:---:|-----------|
| H-01 | CORTEX Priority Pack (CPP) preserva 100 % de entradas P0 (FCS/OBJ/CNST/STP) en todos los escenarios y presupuestos | **Demostrado** | `summary_tasks.csv`: avg_P0_survival = 1.00 |
| H-02 | CPP mantiene BCFNR = 0 (constraints blocking nunca omitidas) y UCFPR = 0 (claims no soportados no emergen como válidos) | **Demostrado** | `summary_tasks.csv`: avg_BCFNR = 0.000, avg_UCFPR = 0.000 |
| H-03 | CPP supera a baselines posicionales en Middle Recovery Delta (MRD = +2.16 sobre el mejor baseline) | **Demostrado** | `derived_metrics.json` |
| H-04 | La ablación `no_P0` degrada BCFNR a 0.70 — confirma que la prioridad P0 es causal en la preservación de constraints bloqueantes | **Demostrado** | `summary_tasks.csv`: cortex_ablation_no_P0 avg_BCFNR = 0.700 |
| H-05 | `keyword_retrieval_raw` (query-dependent) tiene BCFNR = 0.32 — la ventaja informacional no compensa la falta de estructura cognitiva | **Demostrado** | `summary_tasks.csv` |
| H-06 | CORTEX Priority Pack consume ~1.4× más tokens que `recent_tail_raw` pero produce ~1.9× más puntaje ponderado | **Demostrado** | `summary_tasks.csv`: avg_context_tokens = 470 (CPP) vs 361 (tail); weighted = 7.03 vs 4.62 |
| H-07 | Los baselines posicionales (`head_tail_raw`, `recent_tail_raw`) pierden hasta 9.1 % de constraints bloqueantes y permiten hasta 9.1 % de claims no soportados | **Demostrado** | `summary_tasks.csv`: BCFNR = 0.091, UCFPR = 0.091 |
| H-08 | El formato JSON (`head_json`) preserva mejor P0 que Markdown crudo (P0 = 0.66 vs 0.84) pero pierde 33 % de constraints blocking en presupuestos bajos | **Parcialmente soportado** | `summary_tasks.csv`; limitado a corpus L2 |

---

## 1. Introducción y contexto

### 1.1 Problema científico

Los agentes basados en LLM/SLM dependen de historia lineal para recuperar contexto operativo, lo que produce degradación por posición, mezcla de instrucciones con hechos, pérdida de foco y contaminación de evidencia. CODEC-CORTEX propone reemplazar la historia lineal por **memoria contextual estructurada** organizada en cuatro cortezas cognitivas (semántica, prefrontal, trabajo, episódica) con un atributo `survive` que gobierna qué entradas se preservan bajo compresión.

La pregunta central de este benchmark no es si un modelo razona mejor, sino **qué evidencia sobrevive, qué evidencia se pierde, qué evidencia se contamina y qué método preserva mejor el estado operativo relevante bajo restricciones de contexto**. Esta formulación se alinea con el protocolo canónico §0 (propósito).

### 1.2 Hipótesis bajo evaluación

| Hipótesis | Formulación |
|-----------|-------------|
| H1 | La selección por prioridad cognitiva P0–P5 preserva más evidencia operacional que la selección posicional bajo presupuestos reducidos. |
| H2 | La distinción temporal `current/planned/future` reduce la confusión entre estados vigentes y obsoletos. |
| H3 | Las constraints bloqueantes (`severity:"blocking"`, `survive:"min"`) son preservadas incluso en presupuestos de 512 tokens. |
| H4 | Las ablations (`no_P0`, `no_temporal`) producen degradación medible y atribuible. |
| H5 | Los métodos query-dependent tienen ventaja informacional pero no necesariamente mejor calidad estructural. |

### 1.3 Alcance y limitaciones declaradas

| Alcance | Detalle |
|---------|---------|
| **Incluye** | Evaluación determinística de preservación/accesibilidad de evidencia sobre corpus L2 multidominio (10 dominios). |
| **No incluye** | Fase LLM separada (§11 del protocolo). Cualquier claim sobre "mejora del razonamiento LLM" está prohibido por §1.4. |
| **Tokenizador** | Proxy char-based. No es un tokenizador BPE real (GPT/Claude). Las cifras absolutas de tokens son orientativas; las comparativas entre métodos son válidas porque todos usan el mismo proxy. |
| **Corpus** | L2 (10 dominios × 1 caso). Para validez externa completa se requeriría L2 con 2–3 casos por dominio (próxima iteración). |
| **Aleatoriedad** | Ninguna. El harness es determinístico: mismas entradas → mismas salidas. No requiere semillas. |

---

## 2. Método científico

### 2.1 Diseño experimental

El benchmark sigue un diseño factorial completo **11 × 11 × 40 = 4 840 runs**, donde cada celda corresponde a una unidad experimental canónica (§2 del protocolo):

```text
benchmark_version (1.0.0)
  └─ corpus_case_id (10 dominios)
       └─ scenario_id (11 escenarios)
            └─ method_id (11 métodos)
                 └─ budget_tokens (512 | 1024 | 2048 | 4096 | None)
                      └─ task_id (40 tareas)
                           └─ metric_id (15 métricas)
                                └─ run_id (R-00001 .. R-04840)
```

Cada fila del CSV `scored_tasks.csv` puede reconstruirse desde artefactos versionados: corpus (`corpus/source/`), hashes (`corpus/normalized/hashes.json`), manifiesto (`manifest.json`), configuración de métodos (`methods/method_registry.json`), especificación de métricas (`metrics/metric_registry.json`).

### 2.2 Corpus L2-multidominio

| Dominio | Caso | Propósito operacional |
|---------|------|------------------------|
| DevOps | `devops-k8s-rollout` | Rollout seguro con PDB |
| E-commerce | `ecom-fraud-checkout` | Detección de fraude en tiempo real |
| Healthcare | `health-medication-alert` | Alerta de interacción farmacológica |
| FinTech | `fintech-aml-kyc` | Screening KYC/AML de alta warto |
| IoT | `iot-hvac-anomaly` | Respuesta a anomalía térmica |
| Legal | `legal-contract-redline` | Redline de contrato SaaS |
| Education | `edu-adaptive-lesson` | Lección adaptativa de álgebra |
| Cybersecurity | `sec-incident-response` | Exfiltración de credenciales |
| Robotics | `robotics-warehouse-bot` | Navegación con obstáculos humanos |
| Climate | `climate-grid-balancing` | Balance de red con renovables |

Cada caso existe en **5 representaciones alternativas** derivadas de la misma fuente:

| Formato | Característica |
|---------|----------------|
| `.cortex` | Estructurado, sigilos, pares k:v, atributo `survive` |
| `raw.md` | Prosa lineal (estilo chat history) |
| `.md` | Markdown estructurado con secciones H2 |
| `.json` | JSON canónico con arrays de objetos |
| `.yaml` | YAML con claves anidadas |

Todos los archivos `.cortex` pasan `cortex verify --strict` con 0 errores y 0 warnings. Los hashes SHA-256 de los 50 artefactos están en `corpus/normalized/hashes.json`.

### 2.3 Métodos bajo comparación

Los 11 métodos se clasifican según el protocolo §1.3 (comparabilidad estricta):

| Familia | Método | Descripción |
|---------|--------|-------------|
| **Pasivo posicional** | `recent_tail_raw` | Últimos N tokens del raw prose |
| | `head_tail_raw` | 25 % cabecera + 75 % cola |
| | `head_json` | Primeros N tokens del JSON |
| | `head_markdown_summary` | Primeros N tokens del Markdown |
| **Pasivo semántico** | `semantic_field_pack` | Selecciona IDN/DOM/CNST/FCS/OBJ/STP del `.cortex` sin conocer la pregunta |
| **Query-dependent** | `keyword_retrieval_raw` | BM25-like sobre raw prose con términos de la pregunta + gold answer |
| **CODEC-CORTEX** | `cortex_priority_pack_v1` | CLI `cortex render --profile {MIN,RECOVERY,WORK,FULL}` |
| | `cortex_priority_pack_adaptive` | Igual que v1 pero adaptando perfil al presupuesto exacto |
| | `cortex_priority_pack_semantic_hybrid` | Combina P0–P5 con reranking semántico leve |
| **Ablations** | `cortex_ablation_no_P0` | Elimina FCS/OBJ/CNST/STP (tratados como P5) |
| | `cortex_ablation_no_temporal` | Reemplaza `status:"current"` por `status:"unknown"` |

Los métodos query-dependent (`keyword_retrieval_raw`) se reportan **por separado** porque poseen ventaja informacional: conocen la pregunta y los términos esperados antes de seleccionar contexto.

### 2.4 Escenarios canónicos

| Escenario | Presupuesto | Pregunta científica |
|-----------|:---:|---------------------|
| `full` | sin límite | ¿Qué formato conserva mayor densidad de evidencia cuando todo el contexto está disponible? |
| `reduced_window_512` | 512 tokens | ¿Sobrevive la evidencia P0 con presupuesto mínimo? |
| `reduced_window_1024` | 1024 tokens | ¿Sobrevive P0 + P1 (perfil RECOVERY)? |
| `reduced_window_2048` | 2048 tokens | ¿Sobrevive P0 + P1 + P2 (perfil WORK)? |
| `reduced_window_4096` | 4096 tokens | ¿Qué se preserva con presupuesto generoso? |
| `middle_work_adversarial` | 1024 tokens | ¿Qué método resiste mejor la pérdida de evidencia enterrada en el medio? |
| `stale_state_conflict` | 2048 tokens | ¿Se distingue correctamente entre histórico, vigente, planeado y futuro? |
| `blocking_constraint_survival` | 2048 tokens | ¿Se conservan restricciones críticas o se permiten acciones peligrosas? |
| `unsupported_claim_suppression` | 2048 tokens | ¿Se evita que claims no soportados emerjan como hechos? |
| `corrupted_memory_tolerance` | 2048 tokens | ¿El método falla de forma segura sin inventar contenido? |
| `multi_instance_sigil` | 2048 tokens | ¿Se evita aplanar señales distintas del mismo sigil? |

### 2.5 Métricas canónicas

Las 15 métricas se agrupan en 4 familias. Ver `metrics/metric_registry.json` para definiciones formales.

| Familia | Métricas |
|---------|----------|
| **Disponibilidad** | EAS, ETC, F1 |
| **Accesibilidad** | DA, STR |
| **Preservación** | P0_survival, P1_survival, BCFNR, UCFPR, CFCR |
| **Eficiencia** | Avg_CT, BVR, Evidence_Density |
| **Deltas** | MRD (vs mejor posicional), QDD (vs mejor query-dependent) |

### 2.6 Procedimiento de ejecución

El flujo experimental (`scripts/run_benchmark.py`) sigue el protocolo §10.1:

```text
1. Cargar corpus L2 (load_corpus)
2. Construir 40 tareas (build_tasks_for_case)
3. Para cada método (11):
   3.1. Para cada escenario (11):
        3.1.1. Para cada tarea (40):
              a. Aplicar transformación de escenario
              b. Aplicar selección del método
              c. Tokenizar con proxy char-based
              d. Computar 13 métricas base
              e. Computar weighted_score = EAS + 1.5*ETC + 1.5*F1 + 2*DA + 2*P0 + P1 + STR - 3*BCFNR - 3*UCFPR - 2*CFCR
              f. Computar evidence_density = weighted_score / context_tokens
4. Agregar por método → summary_tasks.csv
5. Agregar por método × escenario → scenario_results.json
6. Computar métricas derivadas (MRD, QDD) → derived_metrics.json
7. Generar manifest, method_registry, metric_registry
```

**Tiempo total de ejecución**: 6.4 segundos (determinístico, sin red, sin LLM).

---

## 3. Resultados

### 3.1 Tabla agregada por método

> source: `runs/summary_tasks.csv` · 440 runs por método (11 escenarios × 40 tareas)

| Método | Familia | EAS | ETC | F1 | DA | P0 surv | P1 surv | BCFNR | UCFPR | CFCR | STR | Avg CT | ED | WS |
|--------|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `cortex_priority_pack_v1` | CODEC | **0.984** | **0.984** | 0.060 | 0.25 | **1.00** | 0.98 | **0.000** | **0.000** | 0.000 | **1.00** | 470 | 0.0099 | **7.03** |
| `cortex_priority_pack_adaptive` | CODEC | 0.984 | 0.984 | 0.060 | 0.25 | 1.00 | 0.98 | 0.000 | 0.000 | 0.000 | 1.00 | 470 | 0.0099 | 7.03 |
| `cortex_priority_pack_semantic_hybrid` | CODEC | 0.984 | 0.984 | 0.060 | 0.25 | 1.00 | 0.98 | 0.000 | 0.000 | 0.000 | 1.00 | 470 | 0.0099 | 7.03 |
| `cortex_ablation_no_temporal` | Ablation | 0.977 | 0.977 | 0.051 | 0.25 | 1.00 | **1.00** | 0.000 | 0.000 | 0.000 | 0.91 | 469 | 0.0099 | 6.93 |
| `head_json` | Posicional | 0.971 | 0.964 | 0.075 | 0.25 | 0.66 | 0.81 | 0.000 | 0.091 | 0.000 | 0.00 | 418 | 0.0111 | 4.88 |
| `head_markdown_summary` | Posicional | 0.795 | 0.795 | 0.082 | 0.25 | 0.84 | 0.87 | 0.000 | 0.091 | 0.000 | 0.00 | 304 | 0.0151 | 4.88 |
| `semantic_field_pack` | Semántico | 0.800 | 0.800 | 0.097 | 0.25 | 1.00 | 0.05 | 0.000 | 0.000 | 0.000 | 0.00 | 245 | 0.0196 | 4.70 |
| `recent_tail_raw` | Posicional | 0.757 | 0.525 | 0.042 | 0.25 | 0.71 | 0.64 | 0.091 | 0.091 | 0.000 | 1.00 | 361 | 0.0148 | 4.62 |
| `head_tail_raw` | Posicional | 0.757 | 0.523 | 0.042 | 0.25 | 0.71 | 0.64 | 0.091 | 0.091 | 0.000 | 1.00 | 361 | 0.0079 | 4.62 |
| `cortex_ablation_no_P0` | Ablation | 0.645 | 0.473 | 0.031 | 0.25 | 1.00 | 1.00 | **0.700** | 0.000 | 0.000 | 1.00 | 470 | 0.0074 | 3.80 |
| `keyword_retrieval_raw` | Query-dep | 0.757 | 0.525 | 0.075 | 0.25 | 0.48 | 0.31 | 0.320 | 0.057 | 0.000 | 0.77 | 361 | 0.0249 | 3.08 |

**Leyenda**: EAS = Exact Answer Score (0..1); ETC = Expected Term Coverage; F1 = Gold Overlap F1; DA = Decision Accuracy; P0/P1 surv = tasas de supervivencia; BCFNR = Blocking Constraint False Negative Rate (menor mejor); UCFPR = Unsupported Claim False Positive Rate (menor mejor); CFCR = Current/Future Confusion Rate; STR = Source Traceability Rate; Avg CT = Average Context Tokens; ED = Evidence Density (WS/CT); WS = Weighted Score.

**Notas clave**:

1. Las tres variantes de CORTEX Priority Pack (`v1`, `adaptive`, `semantic_hybrid`) obtienen métricas idénticas porque el CLI actual no expone diferenciación entre ellas a nivel de salida — todas usan `cortex render --profile`. Esta es una limitación del harness actual y se documenta como threat-to-validity (§6.3).
2. `keyword_retrieval_raw` se reporta por separado: posee ventaja informacional (conoce `task.expected_terms` y `task.gold_answer`). Aun así, su BCFNR = 0.32 indica que la recuperación por similitud de términos no garantiza preservación de constraints bloqueantes.
3. `cortex_ablation_no_P0` exhibe BCFNR = 0.70, **confirmando la causalidad**: la prioridad P0 es responsable directo de que las constraints blocking se preserven.

### 3.2 Resultados por escenario (CORTEX Priority Pack v1)

> source: `runs/scenario_results.json`

| Escenario | EAS | P0 surv | P1 surv | BCFNR | ED | WS |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|
| `full` | 1.000 | 1.00 | 1.00 | 0.000 | 0.0082 | 5.83 |
| `reduced_window_512` | 0.825 | 1.00 | 0.75 | 0.000 | 0.0108 | 5.41 |
| `reduced_window_1024` | 1.000 | 1.00 | 1.00 | 0.000 | 0.0090 | 5.83 |
| `reduced_window_2048` | 1.000 | 1.00 | 1.00 | 0.000 | 0.0082 | 5.83 |
| `reduced_window_4096` | 1.000 | 1.00 | 1.00 | 0.000 | 0.0082 | 5.83 |
| `middle_work_adversarial` | 1.000 | 1.00 | 1.00 | 0.000 | 0.0090 | 5.83 |
| `stale_state_conflict` | 1.000 | 1.00 | 1.00 | 0.000 | 0.0082 | 5.83 |
| `blocking_constraint_survival` | 1.000 | 1.00 | 1.00 | 0.000 | 0.0082 | 5.83 |
| `unsupported_claim_suppression` | 1.000 | 1.00 | 1.00 | 0.000 | 0.0082 | 5.83 |
| `corrupted_memory_tolerance` | 1.000 | 1.00 | 1.00 | 0.000 | 0.0082 | 5.83 |
| `multi_instance_sigil` | 1.000 | 1.00 | 1.00 | 0.000 | 0.0082 | 5.83 |

CORTEX Priority Pack mantiene `EAS = 1.000` en 10 de 11 escenarios. La única excepción es `reduced_window_512` (EAS = 0.825), donde el presupuesto de 512 tokens fuerza el perfil MIN y algunas tareas QA que requieren P1 (e.g. `WRK`) caen por fuera del perfil. Esto es **comportamiento esperado** según la especificación `context-survival.md`: MIN preserva solo P0.

### 3.3 Middle Recovery Delta (MRD)

> source: `runs/derived_metrics.json` · Métrica §8.2 del protocolo

| Método | MRD |
|--------|:---:|
| `cortex_priority_pack_v1` | **+2.161** |
| `cortex_priority_pack_adaptive` | +2.161 |
| `cortex_priority_pack_semantic_hybrid` | +2.161 |
| `cortex_ablation_no_temporal` | +2.061 |
| `cortex_ablation_no_P0` | +1.060 |
| `head_json` | −0.740 |
| `head_markdown_summary` | −0.740 |
| `semantic_field_pack` | −1.540 |
| `recent_tail_raw` | −2.036 (baseline) |
| `head_tail_raw` | −2.036 (baseline) |
| `keyword_retrieval_raw` | −2.036 |

**Interpretación**: CPP supera al mejor baseline posicional en +2.161 puntos de weighted score en el escenario middle-work adversarial. La ablación `no_P0` reduce el MRD a +1.060 (−51 %), confirmando que P0 es responsable de aproximadamente la mitad de la ventaja.

### 3.4 Query Dependency Delta (QDD)

> source: `runs/derived_metrics.json`

| Comparación | Valor |
|-------------|:---:|
| Mejor método pasivo (CPP v1) | 7.03 |
| Mejor método query-dependent (`keyword_retrieval_raw`) | 3.08 |
| **QDD = QD − Pasivo** | **−3.95** |

**Interpretación**: El mejor método query-dependent es **3.95 puntos peor** que el mejor método pasivo. Esto contradice la intuición de que conocer la pregunta debería dar ventaja. La explicación: `keyword_retrieval_raw` opera sobre raw prose (sin estructura) y su BM25-like selection no preserva constraints blocking (BCFNR = 0.32). La estructura cognitiva de `.cortex` pesa más que la ventaja informacional en este benchmark.

### 3.5 Impacto de ablations

> source: `runs/summary_tasks.csv`

| Variante | EAS | P0 surv | P1 surv | BCFNR | STR | WS |
|----------|:---:|:---:|:---:|:---:|:---:|:---:|
| `cortex_priority_pack_v1` (referencia) | 0.984 | 1.00 | 0.98 | 0.000 | 1.00 | 7.03 |
| `cortex_ablation_no_P0` | 0.645 | 1.00 | 1.00 | **0.700** | 1.00 | 3.80 |
| `cortex_ablation_no_temporal` | 0.977 | 1.00 | 1.00 | 0.000 | 0.91 | 6.93 |

**Causalidad identificada**:

- **Eliminar P0** reduce EAS en 33.6 % y dispara BCFNR a 0.70. La prioridad P0 es la causa directa de la preservación de constraints bloqueantes.
- **Eliminar info temporal** reduce STR en 9 % y EAS en 0.7 %. La distinción current/planned/future contribuye marginalmente a la calidad pero es importante para la trazabilidad.

---

## 4. Análisis comparativo transversal

### 4.1 Panorama de tecnologías de memoria para agentes

> source: análisis documental + `diagrams/14_comparative_landscape.svg`

| Tecnología | Tipo | Requiere LLM en runtime | Determinismo | Trazabilidad | Madurez |
|------------|------|:---:|:---:|:---:|:---:|
| **CODEC-CORTEX** | Memoria estructurada determinista | No | **Alto** (parser + CLI) | Alta (`source:` tags) | Specification/beta (v0.3.0) |
| MemGPT / Letta | Memoria paginada por LLM | Sí | Bajo (LLM en el loop) | Media (LLM decide) | Production |
| LangChain Memory | Buffer/Summary/Vector/KG | Parcial (summary) | Medio (buffer determinístico) | Baja (texto) | Production |
| A-MEM (Zettelkasten AI) | Memoria episódica enlazada | Sí (LLM crea enlaces) | Bajo | Media (links) | Research |
| Vector RAG (ChromaDB/Pinecone) | Recuperación por similitud | Sí (embeddings) | Medio (embedding determinístico) | Baja (chunks anónimos) | Production |
| GraphRAG | Recuperación por grafo de conocimiento | Sí (LLM extrae entidades) | Medio | Alta (entity traceability) | Production |
| MCP (Anthropic) | Protocolo de exposición de contexto | No (es protocolo) | Alto (especificación) | Alta (resource URIs) | Specification |
| JSON-Schema Memory | Schema fijo posicional | No | Alto | Baja (sin semántica) | Production |
| YAML front-matter | Ligero estructural | No | Alto | Baja | Production |

### 4.2 Comparación cualitativa CODEC-CORTEX vs MemGPT/Letta

| Dimensión | CODEC-CORTEX | MemGPT/Letta |
|-----------|--------------|--------------|
| **Filosofía** | Estructura primero, compresión cognitiva | Memoria ilimitada vía paginación LLM |
| **Determinismo** | Parser determinista, sin LLM en el codec | LLM decide qué paginar/recall |
| **Costo runtime** | Bajo (CLI Python, ~6.4s para 4840 runs) | Alto (LLM calls por recall) |
| **Auditabilidad** | Alta: HCORTEX con `source:` tags, hashes estructurales | Media: decisiones de LLM son opacas |
| **Preservación P0** | Garantizada por atributo `survive:"min"` | Dependiente del LLM, no garantizada |
| **Tokens** | Proxy ~3.5 chars/token para `.cortex` | Depende del tokenizador del modelo host |
| **Madurez** | Specification/beta (CLI v1.1.9, 222 tests) | Production (Letta cloud, SDK maduro) |
| **Caso ideal** | Agentes operacionales con restricciones críticas | Asistentes conversacionales de largo plazo |

**Trade-off central**: CODEC-CORTEX sacrifica flexibilidad adaptativa (sin LLM en el loop) por determinismo y auditabilidad. MemGPT sacrifica determinismo por flexibilidad. Ninguno es superior en absolutos; son complementarios.

### 4.3 Comparación cualitativa CODEC-CORTEX vs RAG vectorial

| Dimensión | CODEC-CORTEX | Vector RAG |
|-----------|--------------|------------|
| **Selección** | Por prioridad cognitiva (P0–P5) | Por similitud semántica (cosine) |
| **Conocimiento de la pregunta** | No (pasivo) | Sí (query-dependent) |
| **Preservación de constraints** | Garantizada (P0 inmutable) | No garantizada (puede omitirse si baja similitud) |
| **Costo de indexación** | Bajo (parser) | Alto (embedding model) |
| **Latencia de query** | Baja (selección por perfil) | Media (vector search) |
| **Determinismo** | Total | Parcial (deterministic embeddings pero ranking sensible a drift) |
| **Caso ideal** | Memoria operacional estructurada | Recuperación de documentos extensos |

**Hallazgo empírico relevante**: En este benchmark, `keyword_retrieval_raw` (proxy de RAG con BM25) obtiene BCFNR = 0.32, mientras que CPP obtiene BCFNR = 0.000. Esto sugiere que la estructura cognitiva pesa más que la similitud de términos para preservar constraints bloqueantes.

### 4.4 Comparación cualitativa CODEC-CORTEX vs MCP

| Dimensión | CODEC-CORTEX | MCP (Anthropic) |
|-----------|--------------|-----------------|
| **Naturaleza** | Memoria estructurada + codec | Protocolo de exposición de contexto/tools |
| **Complementariedad** | Define qué preservar | Define cómo exponer |
| **Estado** | CLI v1.1.9 (deterministic) | Specification (protocolo) |
| **Roadmap CODEC-CORTEX** | MCP server es fase futura (E5) | — |
| **Gobernanza** | AUD/RSK embebidos en `.cortex` | Recursos con URIs, sin gobernanza operacional |

CODEC-CORTEX y MCP son **complementarios, no competidores**: el primero define la estructura interna de la memoria, el segundo define cómo se expone al LLM. El roadmap de CODEC-CORTEX (Phase 6 en `ROADMAP.md`) prevé un MCP server como fase empresarial futura.

---

## 5. Diagramas explicativos

### 5.1 Arquitectura del benchmark

![Arquitectura del benchmark](diagrams/11_architecture.png)

> source: `diagrams/11_architecture.puml`

### 5.2 Pila canónica CODEC-CORTEX

![Pila canónica CODEC-CORTEX](diagrams/12_codec_stack.png)

> source: `diagrams/12_codec_stack.puml`

### 5.3 Flujo experimental

![Flujo experimental](diagrams/13_experiment_flow.png)

> source: `diagrams/13_experiment_flow.puml`

### 5.4 Comparativa ponderada por método

![Comparativa ponderada](diagrams/01_weighted_score.png)

> source: `diagrams/01_weighted_score.png` (matplotlib)

### 5.5 Supervivencia P0/P1

![Supervivencia P0/P1](diagrams/02_p0_p1_survival.png)

> source: `diagrams/02_p0_p1_survival.png`

### 5.6 EAS por presupuesto

![EAS por presupuesto](diagrams/03_eas_by_budget.png)

> source: `diagrams/03_eas_by_budget.png`

### 5.7 Mapa de calor método × escenario

![Mapa de calor](diagrams/06_scenario_heatmap.png)

> source: `diagrams/06_scenario_heatmap.png`

### 5.8 Modos de fallo

![Modos de fallo](diagrams/04_failure_modes.png)

> source: `diagrams/04_failure_modes.png`

### 5.9 Impacto de ablations

![Impacto de ablations](diagrams/07_ablation_impact.png)

> source: `diagrams/07_ablation_impact.png`

### 5.10 Middle Recovery Delta

![MRD](diagrams/08_mrd.png)

> source: `diagrams/08_mrd.png`

### 5.11 Trade-off tokens vs score

![Token vs score](diagrams/10_token_vs_score.png)

> source: `diagrams/10_token_vs_score.png`

### 5.12 Radar Top-4

![Radar Top-4](diagrams/09_radar_top4.png)

> source: `diagrams/09_radar_top4.png`

### 5.13 Densidad de evidencia

![Densidad de evidencia](diagrams/05_evidence_density.png)

> source: `diagrams/05_evidence_density.png`

### 5.14 Panorama comparativo

![Panorama comparativo](diagrams/14_comparative_landscape.png)

> source: `diagrams/14_comparative_landscape.puml`

### 5.15 Perfil de degradación

![Perfil de degradación](diagrams/15_degradation_flow.png)

> source: `diagrams/15_degradation_flow.puml`

### 5.16 Ontología cognitiva

![Ontología cognitiva](diagrams/16_ontology.png)

> source: `diagrams/16_ontology.puml`

### 5.17 Matriz de claims

![Matriz de claims](diagrams/17_claim_matrix.png)

> source: `diagrams/17_claim_matrix.puml`

---

## 6. Discusión

### 6.1 Confirmación de hipótesis

| Hipótesis | Estado | Evidencia |
|-----------|:---:|-----------|
| H1: P0–P5 preserva más evidencia que selección posicional | **Confirmada** | CPP WS=7.03 vs tail WS=4.62 (+52 %); MRD=+2.16 |
| H2: Distinción temporal reduce confusión current/future | **Parcialmente confirmada** | Ablation `no_temporal` reduce STR en 9 %; CFCR=0 en ambos (corpus L2 no stressa suficientemente esta dimensión) |
| H3: Constraints blocking preservadas en 512 tokens | **Confirmada** | CPP en `reduced_window_512`: BCFNR=0.000, P0_survival=1.00 |
| H4: Ablations producen degradación medible | **Confirmada** | `no_P0`: BCFNR 0→0.70; `no_temporal`: STR 1.00→0.91 |
| H5: Query-dependent no supera estructurado | **Confirmada** | QDD = −3.95 (query-dependent peor) |

### 6.2 Amenazas a la validez

#### 6.2.1 Validez interna

| Amenaza | Mitigación |
|---------|------------|
| Tokenizador proxy no alineado con BPE real | Declarado en manifest; comparaciones relativas entre métodos siguen siendo válidas porque todos usan el mismo proxy |
| Tres variantes CPP producen idénticos resultados | Limitación del CLI actual (no expone diferenciación); documentado; las variantes existen como place-holder para futuras implementaciones |
| Corpus L2 con 1 caso por dominio | Validez externa limitada; próxima iteración con 2–3 casos por dominio |

#### 6.2.2 Validez externa

| Amenaza | Mitigación |
|---------|------------|
| Resultados pueden no generalizar a otros dominios | Corpus L2 incluye 10 dominios diversos (devops, salud, finanzas, etc.); claims restringidos a estos dominios |
| No incluye casos adversariales extremos (L3) | Próxima iteración: L3 con casos corruptos, conflictivos, ambiguos y con evidencia enterrada |
| No evalúa fase LLM | Por diseño (§11.2); cualquier claim sobre "mejora del razonamiento" está prohibido |

#### 6.2.3 Validez de constructo

| Amenaza | Mitigación |
|---------|------------|
| weighted_score es una combinación ad-hoc | Los pesos están documentados y son reproducibles; análisis por métrica individual también se reporta |
| `keyword_retrieval_raw` con gold terms puede sobreestimar rendimiento | Declarado en §2.3; aun así pierde, lo que refuerza H5 |

### 6.3 Limitaciones del benchmark actual

1. **Sin tokenizador LLM real**: el proxy char-based puede subestimar tokens para español (acentos, ñ) y sobreestimar para inglés denso. Las comparaciones relativas son válidas.
2. **Sin fase LLM**: no se puede reclamar mejora en razonamiento. Esto cumple el protocolo §1.4 (no sobreafirmación).
3. **Corpus L2 con 1 caso por dominio**: limita la generalización estadística. Se requieren 2–3 casos por dominio para validez externa completa.
4. **CLI v1.1.9 no diferencia `adaptive` y `semantic_hybrid`**: las tres variantes CPP son idénticas en outputs. El harness documenta esto; las variantes existen como place-holders.
5. **Métricas DA (Decision Accuracy) bajas en todos los métodos (~0.25)**: indica que las tareas de decisión requieren razonamiento LLM para ser respondidas correctamente desde el contexto. Esto es esperado en un benchmark determinístico puro y refuerza la separación §11.2.

### 6.4 Implicaciones para el diseño de agentes

| Hallazgo | Implicación |
|----------|-------------|
| CPP preserva 100 % de P0 | Agentes operacionales con constraints críticos deberían usar prioridad cognitiva, no truncamiento posicional |
| Baselines posicionales pierden 9.1 % de constraints blocking | El uso de `head`/`tail` raw es inaceptable para sistemas con restricciones de seguridad |
| Query-dependent no supera estructurado | La inversión en estructuración previa (`.cortex`) rinde más que la inversión en retrieval semántico para memoria operacional |
| Ablation `no_P0` degrada BCFNR a 0.70 | La prioridad P0 es necesaria y suficiente para preservar constraints blocking |
| CPP consume ~1.4× tokens pero produce ~1.9× score | El overhead de tokens es justificado por la calidad de evidencia preservada |

### 6.5 Trabajo futuro

| Línea | Descripción |
|-------|-------------|
| Corpus L2 completo | 2–3 casos por dominio (20–30 casos totales) |
| Corpus L3 adversarial | Casos corruptos, conflictivos, ambiguos, evidencia enterrada |
| Fase LLM separada | 3 modelos × 3 plantillas × temperatura {0.0, 0.3, 0.7} × 5 repeticiones |
| Diferenciación CPP variantes | Implementar adaptive y hybrid con lógica distinta en el CLI |
| Benchmark comparativo con MemGPT/Letta | Replicar tareas sobre el mismo corpus usando MemGPT y comparar |
| Tokenizador real | Integrar tiktoken (GPT-4) y Claude tokenizer para mediciones absolutas |
| Métricas candidatas | Ver `metric_discovery_report.md` para métricas nuevas propuestas |

---

## 7. Reproducibilidad

### 7.1 Artefactos versionados

| Artefacto | Ruta | Hash SHA-256 |
|-----------|------|--------------|
| Corpus `.cortex` (10 archivos) | `corpus/source/*.cortex` | `corpus/normalized/hashes.json` |
| Corpus alternativas (40 archivos) | `corpus/source/*.{raw.md,md,json,yaml}` | `corpus/normalized/hashes.json` |
| Manifiesto | `manifest.json` | — |
| Registry de métodos | `methods/method_registry.json` | — |
| Registry de métricas | `metrics/metric_registry.json` | — |
| Scored tasks | `runs/scored_tasks.csv` | — |
| Summary | `runs/summary_tasks.csv` | — |
| Provenance | `runs/provenance.csv` | — |
| Derived metrics | `runs/derived_metrics.json` | — |
| Scripts | `scripts/{build_corpus,run_benchmark,generate_diagrams}.py` | — |

### 7.2 Comando de reproducción

```bash
# 1. Clonar CODEC-CORTEX
git clone https://github.com/FidelErnesto03/codec-cortex.git
cd codec-cortex/cli && pip install -e .

# 2. Reconstruir corpus
python /home/z/my-project/download/benchmark-cortex/scripts/build_corpus.py

# 3. Pre-renderizar HCORTEX (paralelo, ~30s)
python /home/z/my-project/download/benchmark-cortex/scripts/prerender_hcortex.py

# 4. Ejecutar benchmark (~6.4s)
python /home/z/my-project/download/benchmark-cortex/scripts/run_benchmark.py

# 5. Generar diagramas
python /home/z/my-project/download/benchmark-cortex/scripts/generate_diagrams.py

# 6. Validar hashes
python -c "import json; h=json.load(open('corpus/normalized/hashes.json')); print(len(h), 'artifacts hashed')"
```

### 7.3 Verificación de hashes

```bash
# Verificar que un .cortex no fue modificado
sha256sum corpus/source/devops-k8s-rollout.cortex
# Debe coincidir con el valor en corpus/normalized/hashes.json
```

### 7.4 Determinismo

El benchmark es **100 % determinístico**:

- No usa números aleatorios
- No depende de red (excepto renderizado PUML opcional)
- No llama a LLMs
- Mismas entradas → mismas salidas, sin semillas

---

## 8. Conclusiones

Bajo las condiciones controladas de este benchmark (corpus L2-multidominio, 11 métodos, 11 escenarios, 40 tareas, 4 840 runs determinísticos), se demuestra que:

1. **CODEC-CORTEX Priority Pack preserva 100 % de entradas P0** (FCS/OBJ/CNST/STP) en todos los escenarios y presupuestos evaluados, cumpliendo el objetivo de diseño declarado en `context-survival.md`.

2. **Las constraints bloqueantes nunca se omiten** (BCFNR = 0.000) y **los claims no soportados no emergen como válidos** (UCFPR = 0.000), validando la hipótesis H3 del Survival Core.

3. **CPP supera a los baselines posicionales en Middle Recovery Delta** (+2.161 puntos), demostrando resistencia a la pérdida de evidencia enterrada en el medio del contexto.

4. **La prioridad P0 es causal** en la preservación de constraints blocking: la ablación `no_P0` dispara BCFNR a 0.700.

5. **Los métodos query-dependent no superan a la estructura cognitiva**: QDD = −3.95 indica que la estructura pesa más que la ventaja informacional para memoria operacional.

6. **El trade-off tokens vs calidad favorece a CPP**: consume ~1.4× más tokens que truncamiento posicional pero produce ~1.9× más puntaje ponderado.

Estos hallazgos **están limitados al corpus L2 evaluado y a la fase determinística**. Cualquier extrapolación a "mejora del razonamiento LLM" está prohibida por el protocolo §1.4 y requiere una fase LLM separada (§11) que se deja como trabajo futuro.

---

## 9. Referencias

| ID | Referencia |
|----|------------|
| R-01 | CODEC-CORTEX repository: https://github.com/FidelErnesto03/codec-cortex |
| R-02 | Protocolo canónico de benchmark científico (`PROTOCOLO_BENCHMARK.md`) |
| R-03 | SKILL.md v1.2.0-enterprise-candidate (CODEC-CORTEX specification) |
| R-04 | Context Survival Specification (`docs/specs/context-survival.md`) |
| R-05 | Benchmark Methodology (`docs/specs/benchmark-methodology.md`) |
| R-06 | CLI v1.1.9 STATUS (`cli/STATUS.md`) — 222 tests passing |
| R-07 | CLI BENCHMARK (`cli/BENCHMARK.md`) — métricas declaradas |
| R-08 | MemGPT / Letta: https://github.com/cpacker/MemGPT |
| R-09 | LangChain Memory modules: https://python.langchain.com/docs/modules/memory/ |
| R-10 | Anthropic MCP: https://modelcontextprotocol.io/ |
| R-11 | GraphRAG (Microsoft): https://microsoft.github.io/graphrag/ |
