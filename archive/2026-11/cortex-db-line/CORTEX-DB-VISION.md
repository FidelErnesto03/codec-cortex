# CORTEX-DB — Documento de Visión

> **Estado:** borrador v0.1 — pendiente de ratificación del Arquitecto.
> **Fecha:** 2026-11-12.
> **Proyecto:** CODEC-CORTEX. El producto evoluciona dentro de este repositorio (decisión del Arquitecto, 2026-11-12).
> **Origen:** conversación de dirección entre el Arquitecto y Alfred (gobernador), sesión SES003, ciclo CYCLE-03.

---

## 1. Tesis

CODEC-CORTEX evoluciona de protocolo a producto: una **base de datos de memoria determinista y auditable**, concebida como una categoría paralela a las bases de datos relacionales, documentales y vectoriales, destinada al trabajo agentico.

Su diferenciador no es velocidad ni escala: es la **verificabilidad de la memoria**. Todo lo que la base almacena es íntegro, reproducible y auditable — hash por entrada y por estado, firmas, esquema versionado con migraciones controladas, y determinismo cross-runtime heredado del códec.

La intención operativa: **centralizar la memoria de los agentes**. Los agentes dejan de depender de archivos dispersos como interfaz; escriben y consultan memoria contra un servicio central. Los archivos `.cortex` quedan como formato de intercambio y snapshot (equivalente a un dump SQL), no como superficie de trabajo.

## 2. Punto de partida: qué somos hoy

El activo existente es un códec maduro y certificado:

| Capacidad | Estado |
|---|---|
| Formato CORTEX 1.0 | Spec draft (`docs/standard/CORTEX-SPEC-1.0.md`), pendiente de ratificación |
| Superficies de implementación | 5 (Python, Go, Node, Rust, Bash) con paridad byte-exacta en canonicalización, render y roundtrip |
| Conformance | Corpus válido 364/364; suite de slots 68/68 PASS; certificado PASS con hashes de instrumento y certificador |
| Auditoría externa | Revisión NEX (Lokky) procesada por capítulos; hallazgos verificados y corregidos (orden canónico de attrs, validación de enums, ASCII-estructural, contrato de firma S7.1) |
| Migración | `slotmigrate` con migración versionada 0.1 → 1.0 (idempotente, byte-exacta) |
| Modelado | Dialectos ($0), niveles de nivel (level metadata), perfiles con niveles-P y mapas de secciones |

**El límite actual:** el documento es la unidad máxima. No existe consulta transversal, ni índice, ni transacciones, ni concurrencia segura — los archivos son la única interfaz y cada aplicación (los handlers de ArqUX) los muta a mano.

## 3. La categoría: base de memoria determinista

| Categoría | Optimiza | Integridad | Esquema | Determinismo |
|---|---|---|---|---|
| Relacional | Consulta transaccional | ACID por motor | Rígido (DDL) | No garantizado |
| Documental | Flexibilidad de forma | Débil / opcional | Flexible | No garantizado |
| Vectorial | Similitud semántica | Ninguna | Ninguno | No garantizado |
| **CORTEX-DB (propuesta)** | **Memoria verificable** | **Hash por entrada y por estado, firmas, journal** | **Versionado y auditable** | **Byte-exacto cross-runtime** |

Las capas de memoria agentica del mercado (Mem0, Letta/MemGPT, Zep y similares) se montan sobre enfoques documentales/vectoriales: ninguna ofrece garantías de integridad, evolución de esquema auditable ni determinismo de representación. *Este es conocimiento general de mercado, no una medición — la demanda de la categoría es una hipótesis a falsificar fuera de esta conversación.*

**Evidencia de dolor propio (dogfooding, no especulación):** el brain de este proyecto es un archivo que ronda los 90 KB y crece sin control; requiere compactaciones manuales de PULSE; sufrió duplicados que hubo que recolectar; y la concurrencia multi-agente sobre archivos produjo incidentes reales (ediciones simultáneas, drift entre disco y memoria de handlers). La base ataca dolores ya vividos.

## 4. Modelo de datos: el modelo es un documento versionado

Un **modelo** en CORTEX-DB es la composición de tres capas, todas presentes hoy en el códec como convención, formalizadas aquí como contrato:

| Capa | Qué declara | Ejemplo |
|---|---|---|
| **Dialecto** | El vocabulario: qué sigilos existen, su tipo, riesgo y capa cognitiva | Glosario $0 (AXM, LNG, FCS…) |
| **Perfil** | La estructura: qué secciones existen, qué niveles-P se permiten, qué se omite | Perfil CORTEX-WORK (P0–P2) del brain |
| **Arquetipo** | La forma nativa de aplicación: la semántica del documento como producto | brain, skill, paquete, sesión, timelog, blueprint, issue |

**Modelo = dialecto + perfil + arquetipo, versionado como documento CORTEX almacenado dentro de la propia base.** La base se autodescribe: sus esquemas son documentos CORTEX con hash y firma, y su evolución usa la mecánica de migración ya probada (0.1 → 0.2 → 1.0).

Propiedades derivadas:

- **Arquetipos nativos**: el producto incluye los arquetipos que ArqUX ya modeló (brain, skill, sesión, timelog, blueprint, issue), versionados y migrables.
- **Extensión por negocio**: cada negocio clona y extiende el arquetipo según su propia visión de la corteza prefrontal del agente — "estructurados según se desee" sin inventar un lenguaje nuevo.
- **Validación en escritura**: cada entrada se valida contra el dialecto/perfil/arquetipo de su modelo usando el motor del códec — mismas G-codes, mismas I-codes, mismo hash canónico.

## 5. Topología: instancia central, bases por ámbito

- **Servicio central, un nodo, no distribuido.** Un solo escritor autorizado produce un **orden total de escrituras** — es lo que extiende la garantía del códec del documento al estado completo.
- **Journal append-only con hash-chain**: hash por entrada, hash-chain por base, hash de estado global por transacción. Snapshot verificable, tamper-evidente, replayable.
- **Bases lógicas separadas por ámbito** (gobernanza, un negocio, un área de trabajo) — no por proyecto técnico. Cada base tiene su(s) modelo(s) declarados y su propia cadena; el orden total es de la instancia.
- **Almacenamiento interno y opaco**: el medio físico es un detalle del motor. La interfaz del agente es la API, nunca el file system. `export`/`import` de snapshots `.cortex` cubre respaldo, portabilidad y migración.
- **Time-travel**: el journal append-only hace que cada estado histórico sea reproducible (replay) — la base entera es consultable a cualquier instante pasado.

## 6. Garantías

1. **Integridad**: hash canónico por entrada (heredado del códec), por base y por estado global.
2. **Determinismo**: mismas garantías del códec, extendidas del documento al estado de la base — dos motores que repliquen el journal llegan al mismo estado byte-exacto.
3. **Auditabilidad**: journal inmutable, firmas, y verificación de integridad **sin acceso al contenido** (el auditor verifica con hashes).
4. **Migración versionada**: modelos y datos evolucionan con la mecánica 0.1 → 1.0 ya probada; sin historial roto.
5. **Portabilidad**: export/import de snapshots con roundtrip byte-exacto — la base puede reconstruirse desde su export.

## 7. Roles y permisos

Conjunto base de roles a **curar, estandarizar y nomenclar** para adopción fácil (decisión del Arquitecto: no heredar tal cual los roles de ArqUX). Strawman de partida:

| Rol | Gobierna | Analogía |
|---|---|---|
| **admin** | La instancia: crear/eliminar bases, asignar roles, configuración | superusuario |
| **curador** | Los modelos: declarar, versionar y migrar dialectos/perfiles/arquetipos | DDL |
| **agente** | La memoria: escribir y consultar según permisos | DML |
| **lector** | Solo consulta | read-only |
| **auditor** | La integridad: verificar hashes, cadena, snapshots | verificador |

- **Matriz de permisos**: rol × base × operación (consultar / escribir / administrar / verificar), con granularidad opcional hasta sección o arquetipo.
- **Búsqueda federada permisada** (decisión del Arquitecto: sí se consulta entre bases): la búsqueda recorre todas las bases pero solo surfacea lo visible para quien pregunta — nunca filtra datos ni la existencia de registros que no corresponden.
- **Desacoplamiento integridad/confidencialidad**: los permisos controlan visibilidad; la cadena prueba integridad. El auditor no necesita leer contenido para certificarlo.
- **Identidad**: concepto de identidad propio de la instancia, con federación (hoy: las identidades del equipo ArqUX — Alfred, Jarvis, Heimdall, Seshat).

## 8. API y ergonomía

Orden de protocolos (decisión del Arquitecto): **MCP primero** (el canal que los agentes ya hablan), **CLI** para humanos, **HTTP** después.

Tres primitivas ergonómicas, pensadas para agente:

1. **Catálogo** — introspección: qué bases existen, qué modelos usan, qué arquetipos hay disponibles.
2. **Consulta uniforme** — un solo lenguaje sobre todas las bases: selectores CORTEX ($N/SIGIL:nombre, atributos) elevados con filtros, rangos temporales (PULSE/timelog) y referencias entre entradas.
3. **Contexto** — la primitiva que más cambia el día a día: la base sabe armar el *paquete de contexto de trabajo* (foco, objetivos, lecciones, riesgos, sesión) sin que el agente conozca la estructura interna. Hoy eso lo hace cada handler a mano sobre archivos; mañana es un servicio.

## 9. Alcance y no-alcance

**Sí entra:**
- Memoria agentica diversa y rica: brains, sesiones, timelogs, blueprints, issues, skills, PULSE.
- Modelos propios por negocio/ámbito, clonando y extendiendo arquetipos.
- Integridad, versionado, migración y consulta como producto.

**No entra (explícito):**
- Datos transaccionales de negocio (decisión del Arquitecto: la memoria puede ser diversa, pero no reemplaza a una base operacional).
- Búsqueda semántica/vectorial nativa — convive con un índice vectorial si algún día hace falta; no lo reemplaza.
- Clusters distribuidos / multi-nodo.

## 10. Fases de construcción (propuesta)

| Fase | Contenido | Nota |
|---|---|---|
| **F0** | Ratificar el canon 1.0: cerrar nota B1, fases C–H de BLP-004, ratificación del Arquitecto | Prerrequisito: la DB consume el formato 1.0, no lo reabre |
| **F1** | CORTEX-DB Spec 0.1: documento estándar en `docs/standard/` (modelo de datos, journal, garantías, API) + diseño del journal | El estándar primero, replicando el modelo del códec |
| **F2** | Núcleo en Python (librería): write path con validación por modelo, journal hash-chain, snapshots export/import | Motor antes que servicio |
| **F3** | Servicio central + API MCP: catálogo, consulta uniforme, paquetes de contexto | El tangible operativo |
| **F4** | Roles/permisos completos + migración dogfooding: los brains de ArqUX como primer dataset | Usuario real desde el día uno |
| **F5** | Conformance cross-runtime: ports Go/Node/Rust/Bash del motor, replicando el modelo de certificación del códec | Determinismo demostrado, no prometido |

## 11. Riesgos y preguntas abiertas

- **Demanda de mercado**: el diferenciador técnico es demostrable hoy; que la categoría sea pagable es una hipótesis a falsificar fuera de esta conversación.
- **Expresividad del modelo**: dialecto + perfil + arquetipo puede no alcanzar para constraints tipados o reglas de negocio complejas — decidir si el modelo crece (campos tipados, constraints) o si el CORTEX estructural basta.
- **Rendimiento**: validar cada escritura contra el motor del códec tiene costo — medir en F2 y definir política de validación (estricta por transacción vs. estricta por snapshot).
- **Operación**: centralizar introduce operación (backup, disponibilidad, monitoreo) que el modelo de archivos no exigía.
- **Coexistencia con ArqUX**: los handlers hoy mutan archivos; la migración define el puente (F4) sin corte abrupto.
- **Nomenclatura y adopción**: la curación de roles, comandos y nombre del producto es parte del trabajo de F1.
- **Competitivo**: absorción por plataformas (memoria nativa en ChatGPT/Claude/Gemini/Copilot durante 2026; Oracle Memory SDK esperado) y consolidación anticipada del sector. Detalle y mapa de líderes en el anexo competitivo (`CORTEX-DB-COMPETITIVE-ANNEX-2026-11.md`).
- **GDPR vs. append-only**: el journal inmutable exige crypto-shredding por usuario/ámbito diseñado desde el día uno.

## 12. Decisiones registradas del Arquitecto (2026-11-12)

1. **Servicio central, no distribuido**, que permita mantener modelos internos estructurados según se desee; almacenamiento interno opaco — los archivos solo como export/import.
2. **Modelos como dialectos versionados**, con la corrección del Arquitecto: el dialecto solo no alcanza — la estructura nativa (brain ≠ skill ≠ paquete aún compartiendo dialecto) es una forma propia de modelar que debe considerarse → modelo = dialecto + perfil + arquetipo.
3. **Memoria agentica diversa y rica**; sin datos transaccionales de negocio; cada negocio posee una visión propia de su corteza prefrontal.
4. **Instancia central con bases separadas por ámbito** (área de trabajo), no necesariamente por proyecto, con ergonomía de consulta fácil y dinámica para los agentes.
5. **Protocolo de acceso**: MCP primero, CLI, HTTP después.
6. **Roles**: conjunto base curado, estandarizado y nomenclado para adopción fácil (no heredar los roles de ArqUX tal cual).
7. **Consulta entre bases con búsqueda permisada**: como cualquier base de datos, considerar quién puede o no acceder a determinados datos.
8. **El producto evoluciona dentro de CODEC-CORTEX** (sin repo nuevo).

## 13. Próximos pasos propuestos

1. Ratificación (o correcciones) de este documento por el Arquitecto.
2. Cierre del canon 1.0 (F0): nota B1, fases C–H de BLP-004, ratificación de CORTEX-SPEC-1.0.
3. Apertura de la línea F1: CORTEX-DB Spec 0.1 como BLP en el ciclo correspondiente.

## 14. Propiedades de fidelidad y anexo competitivo (2026-11-12)

El uso real del códec en sesiones maratónicas demuestra tres propiedades que formalizamos como parte de la visión (identificadas por el Arquitecto, formalizadas por Alfred):

1. **Fidelidad ideática** — la compresión es selección determinista (perfiles), nunca distorsión: lo cargado llega byte-idéntico a lo escrito.
2. **Dirección determinista** — el recall es por dirección (selector), no por similitud estadística; reproducible cross-runtime.
3. **Retención estructural de axiomas** — las directrices viven en sección designada que el bootstrap siempre carga; son arquitectura, no suerte de retrieval.

**Síntesis de diseño:** el índice vectorial se adopta como *índice derivado y firmado* sobre la verdad canónica — el vector genera punteros hacia direcciones CORTEX; la entrada canónica es la única verdad hash-verificada. Recuperación difusa para descubrir, dirección determinista para cargar.

Análisis de mercado, mapa de líderes con debilidades documentadas, diferenciadores y los seis experimentos de falsificación (E1–E6): **anexo competitivo** (`CORTEX-DB-COMPETITIVE-ANNEX-2026-11.md`). Revisión de ergonomía desde la práctica del equipo agentico: **revisión de ergonomía** (`CORTEX-DB-ERGONOMICS-REVIEW-2026-11.md`).

---

*Documento redactado por Alfred (gobernador) a dirección del Arquitecto. Toda afirmación sobre el códec está respaldada por el registro de evidencia del proyecto (PULSE, certificados, auditorías); las afirmaciones de mercado están marcadas como conocimiento general, no como medición.*
