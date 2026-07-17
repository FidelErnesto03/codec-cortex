# Terminología normativa de CORTEX

**Document ID:** `CORTEX-TERMINOLOGY-001`  
**Version:** `0.1.0-draft`  
**Status:** `draft-for-ratification`  
**Normative scope:** vocabulario común del estándar y su ecosistema  
**Authority basis:** `CORTEX-CHARTER-001` y `CORTEX-CONSTITUTION-001`  
**Language:** español con identificadores técnicos en inglés  
**Date:** `2026-07-16`

---

## 1. Convenciones de nombre

- **CORTEX**: nombre del estándar de representación.
- **HCORTEX**: representación humana definida por el estándar.
- **CODEC-CORTEX**: nombre del proyecto o implementación de referencia, no del formato.
- Los nombres normativos se escriben en mayúsculas cuando designan el estándar.
- Los paquetes, módulos, comandos y repositorios se escriben en `monospace`.
- Un término heredado no adquiere autoridad por uso histórico.

## 2. Términos normativos

### AST — Abstract Syntax Tree

Modelo estructural interno y lógico resultante del parsing. No depende de una serialización concreta. Dos implementaciones conformantes pueden usar clases distintas, pero deben representar el mismo AST lógico.

### Bytes canónicos

Secuencia UTF-8 exacta producida por las reglas de canonicalización de una versión. Se utiliza para hashing, comparación, firma y reproducción.

### Canon

Artefacto reconocido como fuente normativa o fuente de verdad dentro de un alcance declarado. El término no debe usarse sin especificar qué autoridad lo establece.

### Canonicalización

Transformación determinista de un documento o AST válido a una única representación de bytes definida por la especificación.

### Codec

Componente determinista capaz de transformar entre representaciones estructurales preservando el modelo definido. En CODEC-CORTEX incluye, según nivel de conformidad, parse, write, canonicalize, validate y transformación HCORTEX.

### CODEC-CORTEX

Implementación de referencia del estándar CORTEX. No es la autoridad normativa y no incluye por definición runtime, learning, ArqUX o perfiles de dominio.

### Compactación estructural

Reducción de bytes, tokens o repetición obtenida por la representación. No implica comprensión, resumen ni pérdida semántica.

### Compatible

Cambio o implementación que conserva las garantías declaradas para el alcance especificado. Debe indicarse si la compatibilidad es sintáctica, estructural, canónica, API, HCORTEX o de perfil.

### Conformance corpus

Colección versionada de casos válidos, inválidos y vectores esperados usados para evaluar implementaciones.

### Conformance suite

Corpus, runner, manifest, reglas de comparación y reportes que permiten emitir evidencia de conformidad.

### Consumidor

Sistema que lee, valida, transforma o utiliza información CORTEX. Puede ser un agente, runtime, herramienta, servicio o producto.

### Contexto

Información estructurada suministrada a un consumidor para orientar interpretación o acción. CORTEX representa contexto, pero no determina cómo debe usarse.

### CORTEX

Estándar de representación canónica, compacta, extensible y autocontenida de contexto estructurado para SLM/LLM y sistemas relacionados.

### CORTEX document

Instancia serializada conforme a una versión de CORTEX. Su extensión de archivo y media type serán definidos normativamente en fases posteriores.

### Decisión de cambio normativo (ArqUX)

Iniciativa formal mediante la cual se propone y decide un cambio normativo, de proceso, perfil, seguridad o arquitectura duradera. Se modela como un Blueprint en el `.arqux/` del proyecto CODEC-CORTEX, con ciclo, tareas y criterios de aceptación. Sustituye al anterior mecanismo CEP/RFC.

### Decoder

Operación que transforma una representación codificada a un modelo estructural o representación destino. El término debe acompañarse del origen y destino para evitar ambigüedad.

### Determinista

Propiedad por la cual la misma entrada, versión y opciones normativas producen el mismo resultado observable.

### Diagnostic

Salida estructurada que describe error, warning, limitación, pérdida o información relevante de procesamiento.

### Documento autocontenido

Documento que declara suficiente información local para reconocer y parsear su estructura sin depender obligatoriamente de un servicio externo.

### Encoder

Operación que transforma un modelo estructural a una representación serializada. El término debe acompañarse del origen y destino.

### Entry — Entrada

Unidad direccionable dentro de una sección. Su identidad, tipo, valor, metadata y extensiones serán definidos por el modelo abstracto.

### Equivalencia canónica

Relación entre dos entradas que producen los mismos bytes canónicos para una versión dada.

### Equivalencia estructural

Relación entre dos representaciones que producen el mismo AST lógico, aunque sus bytes de origen difieran.

### Equivalencia semántica

Claim de significado equivalente bajo un perfil o interpretación externa. No pertenece automáticamente al núcleo y requiere declarar la autoridad semántica.

### Errata

Aclaración que no modifica la semántica normativa ni los resultados conformantes existentes.

### Especificación normativa

Documento ratificado que define requisitos obligatorios y contra el cual se evalúa conformidad.

### Extensión

Payload identificado por namespace, id y versión que amplía un documento sin modificar la gramática base. Puede ser `required` u `optional`.

### Forma preservada

Serialización que intenta conservar aspectos del origen no semánticos, como comentarios o layout, cuando la implementación lo soporta. No debe confundirse con forma canónica.

### Gramática

Conjunto formal de reglas léxicas y sintácticas que determina qué secuencias constituyen documentos válidos.

### HCORTEX

Familia de representaciones humanas derivadas del AST CORTEX mediante reglas definidas.

### HCORTEX-CANONICAL

Representación humana normativa y reversible. Conserva metadata suficiente para reconstruir el AST y tiene una forma canónica propia.

### HCORTEX-READABLE

Representación optimizada para lectura humana. Puede ocultar metadata y no garantiza roundtrip. Debe identificarse como derivada.

### Identidad estructural

Conjunto de componentes que permite distinguir y direccionar una entrada independientemente de su posición física. La composición exacta será definida por la especificación.

### Implementación conformante

Implementación que satisface un nivel de conformidad para versiones declaradas y publica evidencia reproducible.

### Implementación de referencia

Implementación mantenida por el proyecto para demostrar y facilitar el estándar. No es la definición del estándar.

### Implementación independiente

Implementación desarrollada desde la especificación, sin traducción mecánica del código de referencia y con suficiente separación para revelar ambigüedades.

### Implementación definida — implementation-defined

Comportamiento que la especificación permite elegir, pero que la implementación debe documentar. No debe afectar resultados canónicos salvo autorización expresa.

### Interoperabilidad

Capacidad de implementaciones distintas para intercambiar documentos y reproducir resultados normativos equivalentes.

### Legacy bridge

Herramienta externa que detecta y transforma dialectos experimentales anteriores. No forma parte de CORTEX Standard 1.0.

### Loss report

Reporte estructurado de toda información descartada, inferida, degradada, no soportada o transformada de forma no reversible.

### Media type

Identificador registrado o documentado para transportar una representación. Su definición se realizará en la especificación correspondiente.

### Metadata

Información estructural o descriptiva asociada a un documento, sección o entrada sin confundirse con su valor principal.

### Namespace

Identificador que delimita un vocabulario o extensión y evita colisiones entre símbolos de distintos autores o perfiles.

### Non-goal

Capacidad que el proyecto excluye deliberadamente de un alcance. No significa que sea inútil, sino que pertenece a otra capa.

### Núcleo — Core

Conjunto mínimo de capacidades necesarias para interoperabilidad CORTEX. No incluye perfiles, runtime, learning, gobierno de agentes ni tooling de producto.

### Ontología

Modelo de conceptos y relaciones de un dominio. CORTEX permite expresar ontologías mediante perfiles o vocabularios, pero no impone una ontología base de agentes.

### Parser

Componente que transforma bytes o texto CORTEX en AST y diagnostics conforme a la gramática.

### Perfil

Contrato externo y versionado que define vocabulario, campos, semántica y validación para un dominio. Un perfil no modifica la gramática base.

### Pérdida silenciosa

Eliminación, alteración o inferencia de información sin diagnóstico y sin consentimiento explícito. Está prohibida.

### Proyección

Representación derivada de un AST que selecciona o presenta información según reglas. Una proyección no es necesariamente reversible.

### Reversible

Propiedad demostrada por la cual una transformación de ida y vuelta reconstruye el modelo estructural exigido, dentro de un alcance y versión declarados.

### Revisión mayor

Versión normativa que puede introducir incompatibilidades de gramática, AST, canonicalización o garantías.

### Revisión menor

Versión normativa compatible que agrega capacidad sin cambiar resultados existentes dentro de la misma línea mayor.

### Roundtrip

Composición de transformaciones de ida y vuelta evaluada contra una equivalencia definida. Debe especificarse si el criterio es byte, AST, contenido o semántica de perfil.

### Runtime

Sistema externo que administra sesiones, estado transitorio, cache, locks o ejecución. Puede consumir CORTEX, pero no pertenece al núcleo.

### Scalar — Escalar

Valor atómico como string, integer, decimal, boolean o null. El conjunto exacto y su forma canónica se define en la especificación.

### Section — Sección

Contenedor ordenado de entradas con identidad y metadata opcional dentro de un documento.

### SLM/LLM

Modelos de lenguaje pequeños o grandes. CORTEX se optimiza para su contexto, pero sus operaciones normativas no requieren un modelo.

### Source preservation

Capacidad no necesariamente normativa de conservar comentarios, spans o layout del texto original durante parse/write.

### Standard

Especificación ratificada, versionada, implementable y respaldada por conformidad. Un draft no debe presentarse como estándar final.

### Symbol — Símbolo

Identificador declarado en un vocabulario y utilizado por entradas. No debe confundirse con una palabra reservada de la gramática.

### Tooling

Herramientas no normativas como CRUD, query, editor, LSP, firma, migración o integración. Pueden usar el codec sin ampliar el núcleo.

### Transformación destructiva

Operación que puede eliminar, fusionar, inferir o degradar información. Requiere loss report y acción explícita.

### Unspecified — No especificado

Comportamiento sobre el cual el estándar no impone requisito. No debe utilizarse para decisiones que afecten interoperabilidad canónica.

### Validator

Componente que evalúa requisitos sintácticos, estructurales, de vocabulario, extensión o perfil y emite diagnostics.

### Vector de conformidad

Caso con input y resultados esperados, como AST, bytes canónicos, diagnostics, HCORTEX o hash.

### VIEW

Nombre legado para proyecciones especializadas. En la nueva arquitectura solo puede existir como extensión opcional, no como requisito de CORTEX ↔ HCORTEX.

### Vocabulary — Vocabulario

Conjunto declarado de símbolos, nombres, tipos y descripciones que permiten interpretar entradas. Puede ser local o provisto por un perfil.

### Writer

Componente que serializa AST a CORTEX, ya sea en forma canónica o en una forma preservada admitida.

## 3. Términos externos al núcleo

### Agent Context Profile

Perfil opcional que puede definir foco, objetivo, trabajo, restricciones, riesgos, sesión, lecciones o conocimiento. Sus símbolos no son reservados por CORTEX.

### ArqUX

Sistema externo de gobierno de proyectos, agentes, aprendizaje y experiencia del arquitecto. Produce y consume CORTEX; no forma parte del estándar.

### CORTEX Learning

Proyecto externo que transforma documentos mediante políticas, algoritmos y provenance. No puede escribir de forma autoritativa sin un consumidor que acepte el cambio.

### CORTEX Runtime

Proyecto externo para sesiones, workspaces y estado transitorio. Puede usar formatos internos diferentes de CORTEX.

### CORTEX-OUT

Protocolo conversacional heredado. No participa en parse, AST, canonicalización, HCORTEX ni conformidad del estándar.

## 4. Términos heredados no normativos

Los siguientes términos pueden aparecer en migración o perfiles, pero no definen el núcleo:

- `brain.cortex`;
- `package.cortex`;
- `SKILL.cortex` como clase privilegiada;
- `FCS`, `OBJ`, `WRK`, `STP`, `NXT`, `SES`, `LNG`, `KNW`;
- `survive`, `P0–P5`;
- políticas de elevación;
- Golden Fibonacci thresholds;
- modos `read-only`, `editor`, `admin` como semántica del formato;
- `VIEW` como contrato obligatorio;
- `CORTEX-OUT`.

Su conservación en un perfil o herramienta requiere namespace, versión y contrato externo.

## 5. Claims que deben evitarse

No debe utilizarse sin precisión:

- “CORTEX comprende el contexto”;
- “CORTEX aprende”;
- “CORTEX gobierna agentes”;
- “CORTEX es una memoria”;
- “CORTEX reemplaza JSON/YAML”;
- “HCORTEX siempre es reversible”;
- “sin pérdida”;
- “más eficiente”;
- “token compression”;
- “estándar” para un draft;
- “conforme” sin versión y nivel.

Formas recomendadas:

- “CORTEX representa contexto estructurado”.
- “Este perfil usa CORTEX para memoria contextual”.
- “HCORTEX-CANONICAL es reversible bajo CORTEX X.Y y HCORTEX X.Y”.
- “La implementación obtuvo `canonical-conformant` contra corpus X.Y.Z”.
- “En el corpus identificado se observó una reducción media de N%, con estas limitaciones”.

## 6. Distinciones obligatorias

### Sintaxis vs semántica

La sintaxis determina estructura válida. La semántica de dominio puede pertenecer a un perfil.

### Canonicalización vs formatting

Formatting mejora presentación. Canonicalización produce una forma única normativa.

### Reversibilidad vs legibilidad

Una vista legible puede no conservar metadata. Solo HCORTEX-CANONICAL puede reclamar reversibilidad base.

### Compresión vs pérdida

Reducir repetición estructural no autoriza descartar información.

### Estándar vs implementación

La especificación determina requisitos. La implementación demuestra una forma de cumplirlos.

### Perfil vs extensión

Un perfil define un contrato semántico reusable. Una extensión agrega payload o capacidad identificada a un documento. La especificación deberá cerrar sus fronteras exactas.

### Error vs warning

Un error impide conformidad para la operación. Un warning señala riesgo o limitación sin necesariamente invalidar el documento.

## 7. Decisiones terminológicas pendientes de Fase 2

Este documento no fija todavía:

- sintaxis exacta de namespaces;
- forma final de selectors;
- nombres definitivos de tipos;
- case sensitivity;
- extensión de archivo;
- media types;
- spelling normativo de boolean/null;
- términos de diagnostics específicos.

Estas decisiones deben resolverse mediante especificación o decisión de cambio registrada en ArqUX sin contradecir las definiciones aquí establecidas.
