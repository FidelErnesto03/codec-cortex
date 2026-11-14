# CORTEX-DB — Anexo Competitivo y Propiedades de Fidelidad

> **Estado:** v0.1 — 2026-11-12. Complemento del Documento de Visión (`CORTEX-DB-VISION.md` §14).
> **Tarea:** T-007 (CYCLE-03, sesión SES003).
> **Método:** investigación de mercado con fuentes públicas 2026 + análisis propio. Las cifras citan su fuente; las de fuente única se marcan. Los juicios de posición están separados de los hechos.

---

## 1. El mercado de memoria agentica en 2026

| Dato | Valor | Fuente / confianza |
|---|---|---|
| Tamaño del mercado (2025 → 2030) | ~$6.3B → ~$28.5B proyectado (35% CAGR) | AgentMarketCap — fuente única, tratar como orientación |
| Líderes | Mem0, Zep, Letta, LangMem | Múltiples fuentes convergentes |
| Mem0 | $24M Serie A (oct 2025); 48k+ stars; proveedor de memoria del AWS Agent SDK | Múltiples fuentes |
| Zep | SOC 2 Type II + HIPAA; BYOC/BYOK/BYOM; motor Graphiti open-source | Documentación propia del vendor |
| Señal de absorción | ChatGPT "Dreaming", Claude Memory (mar 2026), Gemini, Grok, Copilot con memoria nativa; Oracle Memory SDK esperado CY2026; consolidación del sector anticipada | Múltiples fuentes |
| Guerra de benchmarks | Disputa pública Mem0-vs-Zep sobre LOCOMO/LongMemEval; veredicto de la industria: los benchmarks entre vendors son marketing adversarial; el estándar recomendado es el benchmark privado sobre query shapes propias | DataAspirant (análisis), papers de ambos vendors |
| Problema abierto | Consistencia multi-agente bajo escrituras concurrentes: memory drift, hallucinated recall, bias propagation — "ningún vendor lo ha resuelto completamente" | arxiv 2603.10062 (mar 2026), citado por AgentMarketCap |
| Brecha de auditoría | Solo 17% de 420 organizaciones con agentes en producción puede reconstruir la secuencia completa de lecturas/decisiones/escrituras de una tarea (encuesta Q1 2026) | Prefactor citando AgentNode — llegó por terceros, orientativa |
| Competidor adyacente | **Jaybase** (jul 2026, open-source, Go): append-only fact store para agentes con datos críticos de negocio; escrituras atribuidas, historial no reescribible, replay. Sin formato canónico, sin conformance multi-runtime, sin gobernanza de esquema | GitHub jaybase, prefactor.tech |

## 2. Líderes: arquitectura y debilidades documentadas

| Líder | Arquitectura | Fortaleza | Debilidad documentada |
|---|---|---|---|
| **Mem0** | Capa drop-in: extracción + consolidación de hechos por LLM; multi-store (vector + grafo + KV); scoping user/agent/run | Integración mínima (2 llamadas + pegar en prompt); comunidad y distribución | La consolidación **sobrescribe el historial** (current-state wins); **procedencia la más débil**; **LLM en cada escritura** (el costo se paga por conversación); complejidad operacional multi-store |
| **Zep/Graphiti** | Grafo bi-temporal: hechos con valid_at/invalid_at (mundo) + created_at/expired_at (sistema); edge invalidation en vez de borrado; episodios verbatim como procedencia | Primera clase en preguntas temporales; provenance estructural; certificaciones reguladas | **Extracción LLM en cada escritura** + grafo (Neo4j/FalkorDB); modelado upfront costoso; el estado almacenado **no es criptográficamente verificable**; formato propietario |
| **Letta (MemGPT)** | Runtime: el agente edita sus propios bloques de memoria (core/recall/archival); sleep-time compute; backends conectables | Memoria auto-gestionada más madura; control enterprise | "No es una librería, es *la app*" — adopción = migración; pricing opaco |
| **LangMem** | SDK de LangChain, storage-agnóstico | Integración LangGraph nativa | Madurez temprana frente a head starts multi-año |
| **Plataformas nativas** | Memoria embebida en ChatGPT/Claude/Gemini/Copilot | Cero fricción para usuario individual | Memorias privadas por persona — no sirven memoria organizacional compartida ni agente enterprise |

**Pitfall transversal documentado:** los tres líderes corren llamadas LLM en el camino de escritura (extracción, consolidación, tool-calling o extracción de entidades). "El costo de memoria se paga por conversación, no por consulta."

## 3. Diferenciadores reales de CORTEX-DB (mapeados a debilidad documentada)

| # | Diferenciador | Contra qué debilidad | Cómo se demuestra |
|---|---|---|---|
| 1 | **Escritura sin LLM** — canonicalizar + validar + hashear es determinista | Los 3 líderes corren LLM en cada escritura | Conteo de llamadas LLM por escritura: 0 (E3) |
| 2 | **Estado tamper-evident y firmado** — hash-chain por base, firmas, verificación sin contenido | Ninguno ofrece verificación criptográfica del estado; el memory poisoning (ASI06) es su punto ciego declarado | Demo de tamper (E2) |
| 3 | **Estado reproducible byte-exacto cross-runtime** — replay del journal + 5 motores con paridad certificada | La reproducibilidad del mercado es a nivel de hecho temporal (Zep), no del estado del store | Replay en 2 runtimes con hash idéntico (E1) |
| 4 | **Esquema versionado con migración auditable** — dialecto + perfil + arquetipo; mecánica 0.1→1.0 ya probada | Ninguno versiona el esquema ni migra sin romper historial | La maquinaria existe (slotmigrate) |
| 5 | **Formato estándar portable** — export/import byte-exacto; MCP-first | Formatos propietarios; la estandarización MCP es la tendencia del sector | Roundtrip certificado (141/141) |

## 4. Las tres propiedades de fidelidad (observación del Arquitecto, formalizadas)

El Arquitecto identificó (2026-11-12) propiedades que el uso real del códec demuestra y que el mercado no ofrece. Formalización:

| Propiedad | Mecanismo en CORTEX | ¿Lo tienen los líderes? |
|---|---|---|
| **Fidelidad ideática** — lo recuperado son las ideas originales, no un paráfrasis | La compresión es **selección determinista** (perfiles omiten secciones por regla), nunca distorsión: lo cargado llega byte-idéntico a lo escrito (roundtrip certificado) | **No.** Mem0 entrega hechos destilados por LLM (reconstrucción); memoria nativa de plataformas = resumen opaco; Letta se acerca con bloques core always-in-context, pero sin verificación |
| **Dirección determinista** — recall por dirección, no por similitud | El selector devuelve esa entrada o nada; sin ranking; reproducible cross-runtime | **No** como interfaz primaria. Matiz: el grafo de Zep es determinista tras resolver entidades, pero la resolución es extracción LLM (el grafo es destilación probabilística de episodios). En CORTEX la entrada ES el objeto canónico |
| **Retención estructural de axiomas** — las directrices son arquitectura, no suerte de retrieval | Los axiomas viven en sección designada que el bootstrap siempre carga | **Parcial:** Letta (bloques core). Sin hash, sin esquema versionado, sin verificación |

**Síntesis de diseño derivada:** el índice vectorial no es el enemigo — es el **índice derivado y firmado** sobre la verdad canónica. El vector genera punteros hacia direcciones CORTEX; la entrada canónica sigue siendo la única verdad hash-verificada. Recuperación difusa para descubrir, dirección determinista para cargar. Nadie en el mercado ofrece hoy "índice vectorial firmado sobre memoria canónica determinista".

## 5. Donde NO diferenciamos (honestidad estructural)

- **Calidad de recuerdo semántico**: embeddings + grafos + reranking son mesa de entrada que no tenemos (se construye como índice derivado, ver §4).
- **Destilación automática**: el valor central de Mem0/Letta queda deliberadamente fuera del alcance — somos sustrato, no curador.
- **Ecosistema y distribución**: 48k stars, AWS partnership y $24M contra cero.
- **Benchmarks de recall**: LOCOMO/LongMemEval miden recuerdo semántico, no verificabilidad — no es nuestra guerra.

## 6. Debilidades propias frente al mercado

1. **GDPR vs. append-only**: el journal inmutable choca con el derecho al olvido — requiere crypto-shredding por usuario/ámbito diseñado desde el día uno.
2. **Certificaciones**: SOC 2 / HIPAA son la puerta del comprador regulado; Zep y Mem0 ya las tienen; nos llevan un año de camino. La cuña apunta a ese comprador — tensión GTM real.
3. **Escala sin probar**, single-node, comunidad cero.
4. **Rampa de adopción**: el mercado mide ergonomía en "2 llamadas"; la nuestra exige comprender dialectos, secciones y niveles (ver revisión de ergonomía — documento hermano).

## 7. Experimentos de falsificación (la línea abre con esto)

| # | Experimento | Qué prueba o mata | Estado |
|---|---|---|---|
| E1 | **Replay byte-exacto multi-motor**: mismo corpus → reconstruir el estado en Python y Go → hash idéntico | Diferenciador 3 (reproducibilidad cross-runtime) | Instrumental existente en el códec |
| E2 | **Tamper demo**: alterar un byte del estado → detección por hash-chain | Diferenciador 2 (integridad) | Por construir en F2 |
| E3 | **Costo de escritura**: LLM-calls por escritura — líderes ≥1 (documentado) vs CORTEX-DB 0 | Diferenciador 1 (costo/velocidad de write path) | Medible contra sus papers/docs |
| E4 | **Benchmark privado de memoria estructural**: 50–100 query shapes propias contra candidatos | Calidad real en nuestro caso de uso (protocolo recomendado por la industria) | Por diseñar |
| E5 | **Fidelidad maratónica**: misma tarea gobernada, dos brazos — reanudación vía checkpoint CORTEX vs vía resumen LLM; scoring con aserciones chequeables (adherencia a axiomas, continuidad de estado, lecciones citadas) | La propiedad de fidelidad del §4 a nivel de conducta, no de bytes | Por diseñar |
| E6 | **Determinismo de recuperación**: selectores CORTEX vs índice vectorial (p.ej. sqlite-vec) sobre el mismo corpus — precision@k, reproducibilidad entre corridas, tasa de fallo crítico en directrices | Propiedad de dirección determinista (§4) | Por diseñar |

## 8. Posicionamiento

> **"El sustrato verificable bajo la memoria del agente."**

Para organizaciones donde la memoria es un registro (governance multi-agente, industrias reguladas, soberanía de datos): lo que Mem0/Zep/Letta curan semánticamente puede montarse encima de CORTEX-DB y quedar firmado e íntegro; lo que nadie les exige — probar qué sabía el agente en el instante T, sin alteración posible, en formato estándar portable — es nuestro producto.

- **Contra Zep** (rival más cercano en audiencia): integridad criptográfica del estado, escritura sin LLM, formato estándar multi-runtime.
- **Contra Jaybase** (validador de demanda): estándar auto-descripto con arquetipos de memoria agentica, gobernanza de esquema y conformance multi-runtime.
- **Contra las plataformas**: memoria organizacional compartida, permisos, soberanía — lo que la memoria de consumidor no da.

## 9. Lo que este anexo NO resuelve

La demanda sigue siendo hipótesis: las cifras de mercado orientan, no certifican; los experimentos E1–E6 son la falsificación pendiente. El GTM regulado choca con certificaciones inexistentes. Y la cuña puede ser demasiado estrecha para sostener una fundación sola — o exactamente el nicho defendible donde nadie está parado. Eso lo decide la ejecución de los experimentos, no este documento.

---

*Fuentes principales: papers de vendors (arxiv 2504.19413 Mem0, 2501.13956 Zep, 2310.08560 MemGPT), repos open-source (letta-ai/letta, getzep/graphiti, kyle-visner/jaybase), análisis comparativos 2026 (DataAspirant, AgentMarketCap, Cognee, prefactor.tech) y documentación oficial de cada vendor. Cada cifra cita su fuente; las de fuente única están marcadas.*
