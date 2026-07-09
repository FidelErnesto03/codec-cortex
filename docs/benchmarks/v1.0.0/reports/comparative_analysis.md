<!-- SPDX-FileCopyrightText: 2026 Benchmark CODEC-CORTEX -->
<!-- SPDX-License-Identifier: MIT -->

# Análisis Comparativo Transversal — CODEC-CORTEX vs Alternativas

> **Perfil: HCORTEX-FULL** · source: análisis documental + benchmark empirical results

## 1. Panorama del espacio de diseño

Las tecnologías de memoria para agentes LLM/SLM se distribuyen en **5 familias arquitectónicas** distintas, cada una con objetivos y trade-offs diferentes:

| Familia | Objetivo primario | Ejemplos |
|---------|-------------------|----------|
| **Memoria estructurada determinista** | Preservación auditable de evidencia operacional | CODEC-CORTEX, JSON-Schema Memory |
| **Memoria gestionada por LLM** | Memoria ilimitada vía paginación/recall por LLM | MemGPT/Letta, LangChain Summary Memory |
| **Memoria recuperada (RAG)** | Recuperación por similitud semántica | Vector RAG (ChromaDB/Pinecone), GraphRAG |
| **Memoria episódica enlazada** | Notas autónomas con enlaces semánticos | A-MEM (Zettelkasten AI) |
| **Protocolos de exposición** | Estandarizar cómo se expone contexto al LLM | MCP (Anthropic) |

CODEC-CORTEX pertenece a la primera familia y es **complementario** con las demás: puede consumir RAG para recuperar contexto externo, puede ser expuesto vía MCP, y puede convivir con MemGPT para escenarios de largo plazo.

---

## 2. Tabla comparativa detallada

| Dimensión | CODEC-CORTEX v0.3.0 | MemGPT/Letta | LangChain Memory | Vector RAG | GraphRAG | A-MEM | MCP |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Naturaleza** | Codec estructurado | Memoria paginada LLM | Buffer/Summary/Vector | Recuperación embeddings | Grafo de conocimiento | Notas enlazadas | Protocolo |
| **Determinismo** | Alto (parser) | Bajo (LLM) | Medio | Alto (embedding) | Medio (LLM extrae) | Bajo (LLM enlaza) | Alto (spec) |
| **Requiere LLM en runtime** | No | Sí | Parcial | Sí (indexing) | Sí (entity extraction) | Sí | No |
| **Costo runtime** | Bajo | Alto (LLM calls) | Bajo-Medio | Medio (vector search) | Alto (graph traversal) | Medio | Bajo |
| **Auditabilidad** | Alta (`source:` tags) | Baja (LLM opaco) | Baja | Baja (chunks anónimos) | Alta (entity traceability) | Media (links) | Alta (URIs) |
| **Preservación P0** | Garantizada | No garantizada | No garantizada | No garantizada | No garantizada | No garantizada | N/A |
| **Maneja constraints blocking** | Sí (survive:min) | No explícito | No explícito | No explícito | No explícito | No explícito | N/A |
| **Madurez** | Spec/beta | Production | Production | Production | Production | Research | Specification |
| **Latencia típica** | <1ms (CLI) | 100ms-2s (LLM) | 10-100ms | 50-200ms | 100-500ms | 100-500ms | Depende |
| **Tokens consumidos** | Bajos (densidad alta) | Variables | Medios | Medios (top-k chunks) | Altos (subgraph) | Medios | N/A |
| **Costo de indexación** | Bajo (parser) | Bajo | Bajo | Alto (embeddings) | Muy alto (LLM + graph) | Alto (LLM) | N/A |
| **Caso ideal** | Agentes operacionales con constraints | Asistentes de largo plazo | Chatbots simples | Q&A sobre documentos | Q&A multi-hop | Investigación | Exposición estandarizada |

---

## 3. Análisis por pares

### 3.1 CODEC-CORTEX vs MemGPT/Letta

#### Filosofía

| CODEC-CORTEX | MemGPT/Letta |
|--------------|--------------|
| Estructura primero, compresión cognitiva | Memoria ilimitada vía paginación LLM |
| Determinismo antes que flexibilidad | Flexibilidad antes que determinismo |
| Memoria operacional (corto plazo, alta criticidad) | Memoria conversacional (largo plazo, baja criticidad) |

#### Trade-offs

| Dimensión | Ganador | Razón |
|-----------|---------|-------|
| Determinismo | CODEC-CORTEX | Parser determinista, sin LLM en el codec |
| Auditabilidad | CODEC-CORTEX | HCORTEX con `source:` tags, hashes estructurales |
| Memoria ilimitada | MemGPT | Paginación permite memoria "infinita" |
| Adaptabilidad | MemGPT | LLM decide qué recall según contexto |
| Costo runtime | CODEC-CORTEX | Sin LLM calls |
| Madurez producción | MemGPT | Letta cloud, SDK maduro |

#### Caso de uso ideal

- **CODEC-CORTEX**: Agente que opera un sistema crítico (DevOps, healthcare, fintech) donde omitir un constraint blocking es inaceptable.
- **MemGPT/Letta**: Asistente conversacional de largo plazo donde la flexibilidad y la memoria ilimitada pesan más que el determinismo.

#### Complementariedad

CODEC-CORTEX puede usarse como **capa de memoria operacional** dentro de un agente MemGPT: la memoria activa (main context) sería un `.cortex` con perfiles P0–P5, mientras que la memoria archivada usaría el mecanismo de paginación de MemGPT.

### 3.2 CODEC-CORTEX vs LangChain Memory

#### Filosofía

| CODEC-CORTEX | LangChain Memory |
|--------------|------------------|
| Estructura cognitiva explícita | Buffers y summaries flexibles |
| Codec determinista | Módulos configurables |
| Define qué preservar por prioridad | Define cómo almacenar (buffer/summary/vector) |

#### Comparación por tipo de memoria LangChain

| Tipo LangChain | Equivalente CODEC-CORTEX | Diferencia clave |
|----------------|--------------------------|------------------|
| `ConversationBufferMemory` | `SES:session{...}` en `.cortex` | CPP prioriza, buffer no |
| `ConversationSummaryMemory` | `LNG:lesson{...}` + `KNW:knowledge{...}` | CPP destila por tipo cognitivo, summary es monolítico |
| `VectorStoreRetrieverMemory` | N/A (CODEC-CORTEX no hace retrieval) | Complementario: RAG para recuperar, `.cortex` para activo |
| `ConversationKGMemory` | `KNW:knowledge{...}` con refs | CPP más estructurado, KG más flexible |

#### Trade-offs

| Dimensión | Ganador | Razón |
|-----------|---------|-------|
| Flexibilidad | LangChain | Múltiples módulos configurables |
| Estructura cognitiva | CODEC-CORTEX | Ontología de 4 cortezas |
| Preservación P0 | CODEC-CORTEX | Atributo `survive:"min"` garantizado |
| Ecosistema | LangChain | Integración con cientos de tools |
| Determinismo | CODEC-CORTEX | Sin LLM en el codec |

### 3.3 CODEC-CORTEX vs Vector RAG

#### Filosofía

| CODEC-CORTEX | Vector RAG |
|--------------|------------|
| Selección por prioridad cognitiva (P0–P5) | Selección por similitud semántica (cosine) |
| Sin conocimiento de la pregunta | Conocimiento de la pregunta (query-dependent) |
| Preserva estructura | Preserva chunks anónimos |

#### Hallazgo empírico del benchmark

| Método | BCFNR | UCFPR | WS |
|--------|:---:|:---:|:---:|
| `cortex_priority_pack_v1` (pasivo) | **0.000** | **0.000** | **7.03** |
| `keyword_retrieval_raw` (proxy BM25-like) | 0.320 | 0.057 | 3.08 |

La diferencia es **3.95 puntos** en weighted score (QDD = −3.95). Esto contradice la intuición de que conocer la pregunta debería dar ventaja. La explicación: BM25 opera sobre raw prose (sin estructura) y no prioriza constraints blocking. Un Vector RAG real con embeddings de alta calidad podría mejorar el ranking pero **no garantizaría preservación de P0**, porque la similitud semántica no distingue entre una constraint blocking y una nota histórica.

#### Cuándo usar cada uno

- **CODEC-CORTEX**: Memoria operacional donde constraints y decisiones críticas deben preservarse.
- **Vector RAG**: Recuperación de documentos extensos donde la similitud semántica es el criterio primario.

#### Híbrido recomendado

Usar **CODEC-CORTEX como memoria operacional activa** + **Vector RAG como memoria documental externa**. El agente consulta `.cortex` para estado operativo y RAG para conocimiento factual. Esta es la arquitectura recomendada por el proyecto CODEC-CORTEX en `docs/specs/adoption.md`.

### 3.4 CODEC-CORTEX vs GraphRAG

#### Filosofía

| CODEC-CORTEX | GraphRAG |
|--------------|----------|
| Estructura cognitiva fija (sigilos) | Grafo de conocimiento extraído por LLM |
| Determinista | LLM-dependent en entity extraction |
| Bajo costo de indexación | Alto costo (LLM por documento) |
| Ontología cerrada | Ontología emergente |

#### Trade-offs

| Dimensión | Ganador | Razón |
|-----------|---------|-------|
| Determinismo | CODEC-CORTEX | Sin LLM en indexing |
| Flexibilidad ontológica | GraphRAG | Adapta ontología al dominio |
| Costo de indexación | CODEC-CORTEX | Parser Python vs LLM calls masivos |
| Trazabilidad de entidades | GraphRAG | Grafo explícito de relaciones |
| Preservación de constraints | CODEC-CORTEX | P0 garantizado; GraphRAG no distingue |

### 3.5 CODEC-CORTEX vs A-MEM (Zettelkasten AI)

#### Filosofía

| CODEC-CORTEX | A-MEM |
|--------------|-------|
| Estructura cognitiva jerárquica | Notas autónomas enlazadas |
| Determinista | LLM crea enlaces |
| Ontología cerrada | Estructura emergente tipo Zettelkasten |

#### Trade-offs

| Dimensión | Ganador | Razón |
|-----------|---------|-------|
| Determinismo | CODEC-CORTEX | Sin LLM en mantenimiento |
| Adaptabilidad | A-MEM | Estructura emerge del uso |
| Madurez | CODEC-CORTEX | CLI v1.1.9 vs research prototype |
| Innovación | A-MEM | Enfoque novedoso |

### 3.6 CODEC-CORTEX vs MCP (Anthropic)

#### Filosofía

| CODEC-CORTEX | MCP |
|--------------|-----|
| Memoria estructurada interna | Protocolo de exposición externa |
| Define qué preservar y cómo | Define cómo exponer al LLM |
| Codec + CLI + formato | Specification (protocolo) |

#### Complementariedad

CODEC-CORTEX y MCP **no compiten**: el primero define la estructura interna de la memoria, el segundo define cómo se expone al LLM. De hecho, el roadmap de CODEC-CORTEX (Phase 6 en `ROADMAP.md`) prevé un **MCP server como fase empresarial futura**: los artefactos `.cortex` se expondrían vía MCP, combinando la preservación determinista de CODEC-CORTEX con la estandarización de MCP.

#### Caso de uso conjunto

Un agente podría:

1. Mantener su memoria operacional como `brain.cortex` (CODEC-CORTEX).
2. Exponer `brain.cortex` (o perfiles derivados) como recursos MCP.
3. Permitir que otros agentes consulten esa memoria vía MCP estandarizado.

Esta arquitectura es la visión dePhase 6 del proyecto.

---

## 4. Matriz de decisión: cuándo usar qué

| Caso de uso | Recomendación primaria | Complementario |
|-------------|------------------------|----------------|
| Agente operacional con constraints críticos (DevOps, healthcare, fintech) | **CODEC-CORTEX** | Vector RAG para docs externos |
| Asistente conversacional de largo plazo | **MemGPT/Letta** | CODEC-CORTEX para sesión activa |
| Chatbot simple con memoria corta | **LangChain Buffer** | — |
| Q&A sobre base documental extensa | **Vector RAG** | CODEC-CORTEX para memoria operacional del Q&A |
| Q&A multi-hop con entidades relacionadas | **GraphRAG** | CODEC-CORTEX para constraints del dominio |
| Investigación de memoria episódica autónoma | **A-MEM** | — |
| Exposición estandarizada de contexto a múltiples LLMs | **MCP** | CODEC-CORTEX como backend de memoria |

---

## 5. Posicionamiento de CODEC-CORTEX

### 5.1 Fortalezas únicas

1. **Determinismo total en el codec**: ningún competidor ofrece parser determinista con 222 tests.
2. **Prioridad cognitiva P0–P5 con `survive`**: ningún competidor distingue entre P0 inmutable y P5 descartable.
3. **HCORTEX como render humano auditable**: ningún competidor tiene una vista humana con `source:` tags por entrada.
4. **CLI maduro (v1.1.9, 17 comandos)**: ningún competidor tiene CLI tan completo para mantenimiento de memoria.

### 5.2 Debilidades

1. **Sin runtime de maduración**: el roadmap prevé promoción/decaimiento automático (WRK→SES→LNG→KNW) pero no está implementado.
2. **Sin fase LLM**: el benchmark actual no evalúa mejora del razonamiento.
3. **Sin MCP server**: la exposición empresarial vía MCP es futura.
4. **Ecosistema limitado**: comparado con LangChain (cientos de integraciones), CODEC-CORTEX es joven.

### 5.3 Oportunidades

1. **Nicho de agentes operacionales críticos**: pocos competidores abordan este caso de uso.
2. **Complementariedad con MCP**: el roadmap Phase 6 los alinea, no los enfrenta.
3. **Adopción incremental**: SKILL universal puede adoptarse sin instalar nada (solo leyendo el spec).

### 5.4 Amenazas

1. **MemGPT/Letta podría agregar estructura cognitiva** en futuras versiones.
2. **LangChain podría estandarizar un schema similar** si la demanda crece.
3. **MCP podría evolucionar para incluir memoria estructurada** como parte del protocolo.

---

## 6. Conclusión comparativa

CODEC-CORTEX ocupa un **nicho específico y valioso** en el espacio de memoria para agentes: la preservación determinista y auditable de evidencia operacional con prioridad cognitiva. No compite directamente con MemGPT/Letta (memoria ilimitada), RAG (recuperación documental) ni MCP (exposición), sino que los complementa.

El benchmark empírico confirma que, **en su nicho**, CODEC-CORTEX supera a baselines posicionales (MRD = +2.16) y a un proxy de RAG (QDD = +3.95 a favor de CPP), preservando 100 % de P0 y manteniendo BCFNR = 0 en todos los escenarios evaluados.

La adopción exitosa depende de:

1. Completar el roadmap (runtime de maduración, MCP server).
2. Ampliar el benchmark (fase LLM, corpus L3 adversarial).
3. Construir integraciones con el ecosistema (LangChain Memory adapter, MemGPT plugin, MCP server).
