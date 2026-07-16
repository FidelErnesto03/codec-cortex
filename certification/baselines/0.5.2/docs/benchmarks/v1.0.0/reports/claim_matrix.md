<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX -->
<!-- SPDX-License-Identifier: MIT -->

# Matriz de Claims — Benchmark CODEC-CORTEX v1.0.0

> **Perfil: HCORTEX-AUDIT** · source: scientific_report.md §6 + runs/summary_tasks.csv

## 1. Clasificación obligatoria (§1.4 del protocolo)

| Estado | Significado |
|--------|-------------|
| **Demostrado** | Soportado directamente por resultados reproducibles |
| **Parcialmente soportado** | Visible en datos, pero limitado por corpus, métrica o escenario |
| **Hipótesis razonable** | Sugerido por los resultados, pero requiere experimento adicional |
| **No soportado** | No evaluado o contradicho por los datos |

---

## 2. Matriz de claims

| # | Claim | Status | Evidence | Limitations | Allowed wording | Forbidden wording |
|:---:|-------|:---:|----------|-------------|-----------------|-------------------|
| C-01 | CORTEX Priority Pack preserva 100 % de entradas P0 en todos los escenarios | **Demostrado** | `summary_tasks.csv`: avg_P0_survival = 1.00 para cortex_priority_pack_v1/adaptive/hybrid en los 11 escenarios | Limitado a corpus L2 (10 dominios × 1 caso) | "CPP preserva entradas P0 en el corpus L2 evaluado" | "CPP preserva P0 en todos los casos concebibles" |
| C-02 | CPP mantiene BCFNR = 0 (constraints blocking nunca omitidas) | **Demostrado** | `summary_tasks.csv`: avg_BCFNR = 0.000 | Validado en 11 escenarios; no stress-tested con corpus L3 adversarial | "CPP no omitió constraints blocking en el corpus L2" | "CPP garantiza cero omisiones de constraints en cualquier escenario" |
| C-03 | CPP mantiene UCFPR = 0 (claims no soportados no emergen como válidos) | **Demostrado** | `summary_tasks.csv`: avg_UCFPR = 0.000 | Validado solo en escenario `unsupported_claim_suppression` | "CPP no dejó emerger claims no soportados en el escenario evaluado" | "CPP elimina toda invención de claims" |
| C-04 | CPP supera a baselines posicionales en Middle Recovery Delta | **Demostrado** | `derived_metrics.json`: MRD = +2.161 | Comparación contra 4 baselines posicionales; no incluye GraphRAG ni MemGPT | "CPP supera a baselines posicionales en MRD en el corpus L2" | "CPP es superior a todos los métodos de memoria" |
| C-05 | La prioridad P0 es causal en la preservación de constraints blocking | **Demostrado** | `summary_tasks.csv`: cortex_ablation_no_P0 avg_BCFNR = 0.700 (vs 0.000 con P0) | Causalidad limitada al mecanismo de prioridad; no aísla otros factores | "Eliminar P0 degrada BCFNR a 0.70" | "P0 es la única causa de preservación de constraints" |
| C-06 | Los métodos query-dependent no superan a la estructura cognitiva | **Demostrado** | `derived_metrics.json`: QDD = −3.95 | Comparado con 1 método query-dependent (BM25-like); no incluye Vector RAG real ni GraphRAG | "BM25-like query-dependent no superó a CPP en este benchmark" | "La estructura cognitiva siempre supera al retrieval semántico" |
| C-07 | CPP consume ~1.4× más tokens que truncamiento posicional pero produce ~1.9× más score | **Demostrado** | `summary_tasks.csv`: avg_context_tokens = 470 (CPP) vs 361 (tail); WS = 7.03 vs 4.62 | Proxy char-based; no medido con tokenizador BPE real | "CPP consume más tokens pero produce mayor calidad de evidencia" | "CPP es más eficiente en tokens que cualquier baseline" |
| C-08 | La distinción temporal `current/planned/future` mejora trazabilidad | **Parcialmente soportado** | `summary_tasks.csv`: ablation `no_temporal` reduce STR de 1.00 a 0.91 | CFCR = 0 en ambos casos (corpus L2 no stressa suficientemente esta dimensión) | "La distinción temporal contribuye a la trazabilidad" | "La distinción temporal elimina toda confusión current/future" |
| C-09 | CPP es adecuado para agentes operacionales con restricciones críticas | **Parcialmente soportado** | Preservación P0 = 100 %, BCFNR = 0, UCFPR = 0 | No evaluado en producción con agentes reales; solo en corpus sintético controlado | "CPP muestra características deseables para agentes operacionales" | "CPP es la mejor solución para agentes operacionales" |
| C-10 | Los baselines posicionales son inaceptables para sistemas con restricciones de seguridad | **Parcialmente soportado** | `summary_tasks.csv`: BCFNR = 0.091, UCFPR = 0.091 para `recent_tail_raw` y `head_tail_raw` | 9.1 % de omisiones puede ser aceptable en sistemas no críticos; depende del caso de uso | "Baselines posicionales pierden hasta 9.1 % de constraints blocking" | "Baselines posicionales son siempre inaceptables" |
| C-11 | Los beneficios de CPP se mantendrán en corpus L3 adversarial | **Hipótesis razonable** | CPP preserva P0 en 11 escenarios incluyendo corrupted_memory y multi_instance | L3 no ejecutado; casos extremos pueden romper invariantes | "Es razonable esperar que CPP mantenga beneficios en L3" | "CPP mantendrá beneficios en cualquier corpus adversarial" |
| C-12 | Los beneficios de CPP se mantendrán en fase LLM | **Hipótesis razonable** | CPP preserva evidencia accesible; si la evidencia está disponible, el LLM puede usarla | No evaluado con LLM; el LLM puede fallar incluso con evidencia correcta | "CPP podría mejorar respuestas LLM al preservar evidencia" | "CPP mejora el razonamiento LLM" |
| C-13 | CPP mejora el razonamiento LLM | **No soportado** | No evaluado (fase LLM no ejecutada por §11.2) | Prohibido por protocolo §1.4 | (no claim permitido) | "CODEC-CORTEX mejora agentes LLM/SLM" (sin fase LLM) |
| C-14 | CPP comprime sin pérdida | **No soportado** | La especificación declarada en README.md dice "literal reconstruction of every original message is not promised" | Especificación explícita del proyecto | "CPP ofrece reversibilidad estructural para codec y reversibilidad contextual vía HCORTEX" | "CPP comprime sin pérdida" |
| C-15 | CPP es superior a MemGPT/Letta en todos los casos | **No soportado** | No se ejecutó comparación directa con MemGPT/Letta | MemGPT tiene diferentes objetivos (memoria ilimitada vs preservación determinista) | "CPP y MemGPT son complementarios con diferentes trade-offs" | "CPP es superior a MemGPT" |
| C-16 | El proxy char-based de tokens equivale a un tokenizador BPE real | **No soportado** | Proxy declarado en manifest; diferencias conocidas para español (acentos, ñ) | Las comparaciones relativas entre métodos son válidas; las absolutas no | "Tokens medidos con proxy char-based (1 token ≈ 3.5–4.0 chars)" | "Tokens medidos con tokenizador GPT-4" |

---

## 3. Resumen de claims por estado

| Estado | Cantidad | % |
|--------|:---:|:---:|
| Demostrado | 7 | 44 % |
| Parcialmente soportado | 4 | 25 % |
| Hipótesis razonable | 2 | 13 % |
| No soportado | 3 | 19 % |
| **Total** | **16** | **100 %** |

---

## 4. Wording permitido vs prohibido (anti-overclaim §1.4)

### 4.1 Wording permitido

| Contexto | Frase permitida |
|----------|-----------------|
| General | "CODEC-CORTEX busca preservación determinista de evidencia operacional" |
| Sobre P0 | "CPP preserva entradas P0 en el corpus L2 evaluado" |
| Sobre constraints | "CPP no omitió constraints blocking en los 11 escenarios evaluados" |
| Sobre MemGPT/RAG | "CPP y MemGPT son complementarios con diferentes trade-offs" |
| Sobre fase LLM | "Requiere fase LLM separada para validar mejora en razonamiento" |

### 4.2 Wording prohibido

| Contexto | Frase prohibida |
|----------|-----------------|
| General | "CODEC-CORTEX mejora agentes LLM/SLM" (sin fase LLM) |
| Sobre P0 | "CPP garantiza P0 en cualquier escenario concebible" |
| Sobre constraints | "CPP elimina toda omisión de constraints" |
| Sobre MemGPT/RAG | "CPP es superior a MemGPT/RAG" (sin comparación directa) |
| Sobre fase LLM | "CPP mejora el razonamiento del modelo" |
| Sobre compresión | "CPP comprime sin pérdida" |

---

## 5. Threats to validity declarados

| Threat | Severidad | Mitigación |
|--------|:---:|------------|
| Corpus L2 con 1 caso por dominio | Media | Próxima iteración: 2–3 casos por dominio |
| Sin tokenizador BPE real | Baja | Proxy declarado; comparaciones relativas válidas |
| Sin fase LLM | Alta (para claims LLM) | Por diseño; claims LLM prohibidos |
| 3 variantes CPP idénticas en outputs | Baja | Limitación del CLI v1.1.9; documentado |
| DA bajo en todos los métodos (~0.25) | Media | Indica que tareas de decisión requieren LLM; esperado en fase determinística |
| BM25-like sobre raw prose no representa RAG vectorial real | Media | Proxy declarado; comparación con RAG real queda como trabajo futuro |
