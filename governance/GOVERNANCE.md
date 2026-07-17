# Gobierno del estándar CORTEX

**Document ID:** `CORTEX-GOVERNANCE-001`  
**Version:** `0.2.0-draft`  
**Status:** `draft-for-ratification`  
**Normative scope:** autoridad, roles, decisiones, releases y compatibilidad  
**Authority basis:** `CORTEX-CONSTITUTION-001`  
**Governance engine:** ArqUX (proyecto CODEC-CORTEX en `CODEC-CORTEX/.arqux/`)  
**Language:** español  
**Date:** `2026-07-16`

---

## 1. Objetivo del gobierno

El gobierno de CORTEX debe proteger cuatro propiedades:

1. especificación superior al código;
2. neutralidad del núcleo;
3. decisiones trazables;
4. conformidad no autocertificada.

El proceso debe ser suficientemente riguroso para un estándar interoperable y suficientemente pequeño para no convertir el proyecto en una burocracia improductiva.

## 2. Ámbito

Este documento gobierna:

- `codec-cortex` (repositorio del estándar y su implementación de referencia);
- especificaciones CORTEX y HCORTEX;
- canonicalización;
- modelo de extensiones y perfiles;
- conformance corpus;
- releases normativas;
- decisiones de cambio del estándar;
- claims oficiales de compatibilidad y conformidad.

Los repositorios de runtime, learning, perfiles o productos pueden tener gobierno propio, pero no pueden alterar el estándar sin seguir este proceso.

## 3. Motor de gobernanza: ArqUX

El proceso de cambio, decisión y trazabilidad del estándar CORTEX se opera mediante **ArqUX**, específicamente el proyecto `CODEC-CORTEX` ubicado en `CODEC-CORTEX/.arqux/`.

El mecanismo formal de cambio del estándar es el **Blueprint ArqUX** (no un proceso CEP/RFC externo). Cada iniciativa normativa, corrección o release se modela como un Blueprint con:

- ciclo (`CYCLE-NN`) que agrupa el trabajo;
- tareas con procedimiento y criterios de aceptación (`AC`);
- identidades/roles ArqUX asignados como responsables y aprobadores;
- verificación de `AC` como gate de aceptación.

### 3.1 Mapeo de estados

| Estado Blueprint ArqUX | Significado normativo |
|---|---|
| `draft` | idea o propuesta en elaboración, sin autoridad |
| `ready` | completitud verificada por el Editor, lista para ejecución |
| `in_progress` | en ejecución y revisión |
| `done` | aceptada e integrada en la especificación/corpus |
| `blocked` | requiere resolución antes de continuar |

### 3.2 Mapeo de criterios

Los `AC` del Blueprint son los criterios de aceptación normativa (equiv. al cuestionario de aceptación del estándar). Un `AC` abierto bloquea el paso a `done`.

### 3.3 Aprobaciones

Las aprobaciones requeridas se registran como responsables/verificadores del Blueprint y sus tareas, según la clase de decisión (§6). El autor de la implementación no puede ser el único aprobador de su propia capacidad.

## 4. Autoridad normativa

La autoridad se resuelve en el siguiente orden:

1. Constitución de CORTEX;
2. especificación ratificada correspondiente;
3. corpus de conformidad de esa versión;
4. erratas publicadas;
5. documentación explicativa;
6. implementación de referencia.

Un test de implementación no adquiere carácter normativo por sí mismo.

ArqUX es el sistema que *registra y ejecuta* las decisiones, pero no es fuente de autoridad normativa: cuando un Blueprint ArqUX contradice la Constitución o la especificación ratificada, prevalece el texto normativo.

## 5. Estructura mínima de gobierno

### 5.1 Arquitecto Principal

Responsable de:

- visión y coherencia del ecosistema;
- frontera del núcleo;
- aprobación final de alcance;
- priorización pre-1.0;
- aceptación o rechazo de cambios junto con los revisores requeridos;
- designación o remoción de responsables de rol.

No puede certificar en solitario una capacidad que haya implementado.

### 5.2 Editor del Estándar

Responsable de:

- lenguaje normativo;
- consistencia entre especificaciones;
- terminología;
- versionado del estándar;
- control de erratas;
- registro de decisiones en ArqUX;
- preparación de drafts y release candidates.

Puede bloquear una release por ambigüedad normativa.

### 5.3 Implementador de Referencia

Responsable de:

- implementación Python;
- API y CLI;
- packaging;
- tests propios;
- trazabilidad entre cláusulas normativas y código.

No define el estándar mediante su implementación.

### 5.4 Implementador Independiente

Responsable de:

- implementar desde la especificación;
- evitar traducción mecánica desde el código de referencia;
- reportar ambigüedades;
- ejecutar pruebas diferenciales.

Su independencia es una condición de Standard 1.0.

### 5.5 Responsable de Conformance

Responsable de:

- corpus válido e inválido;
- vectores canónicos;
- expected AST;
- diagnostics obligatorios;
- runner y manifest;
- reportes reproducibles.

Puede bloquear una release si la evidencia no reproduce el texto normativo.

### 5.6 Revisor de Seguridad

Responsable de:

- threat model;
- fuzzing;
- resource exhaustion;
- supply chain;
- secret scanning;
- divulgación coordinada.

Puede imponer embargo temporal sobre una vulnerabilidad activa.

### 5.7 Revisor Externo

Debe ser independiente de la implementación o decisión auditada. Su función es:

- evaluar comprensibilidad externa;
- detectar acoplamiento histórico;
- revisar claims críticos;
- aprobar gates donde exista conflicto de autoría.

## 6. Consejo del Estándar

Mientras el proyecto sea pequeño, el Consejo del Estándar está compuesto por:

- Arquitecto Principal;
- Editor del Estándar;
- Responsable de Conformance.

El Revisor de Seguridad participa con voto en decisiones de seguridad. El Revisor Externo participa con voto cuando la Constitución o el proceso de gobierno lo exige.

Una persona puede cubrir más de un rol, pero una decisión no puede considerarse independiente cuando todos los votos efectivos pertenecen al autor del cambio.

## 7. Clases de decisión

| Clase | Ejemplos | Autoridad mínima |
|---|---|---|
| Operativa | organización, CI, estilo no normativo | responsable del repositorio |
| Editorial | corrección de redacción sin semántica | Editor del Estándar |
| Errata | aclaración normativa sin cambiar resultado | Editor + Conformance |
| Normativa compatible | capacidad compatible, nuevo diagnóstico opcional | Arquitecto + Editor + Conformance |
| Normativa incompatible | gramática, AST o bytes canónicos | Blueprint con revisión mayor + revisor externo |
| Constitucional | cambio de principios o frontera | proceso de reforma constitucional |
| Seguridad urgente | vulnerabilidad activa | Seguridad + Arquitecto; revisión posterior obligatoria |

## 8. Método de decisión

La preferencia es consenso documentado. Cuando no exista consenso:

- una decisión operativa se resuelve por el responsable del área;
- una decisión normativa requiere mayoría del Consejo y ausencia de veto constitucional del Editor;
- una decisión incompatible requiere aprobación explícita del Arquitecto, Editor, Conformance y un revisor independiente;
- una decisión constitucional sigue `CORTEX-CONSTITUTION.md`.

Toda decisión debe registrarse como Blueprint/tarea en ArqUX con su criterio, evidencia, objeciones y efectos de compatibilidad.

## 9. Conflicto de interés y autocertificación

Una persona se considera conflictuada cuando:

- escribió la mayor parte de la capacidad evaluada;
- mantiene el producto que depende de su aceptación;
- produce el benchmark usado para justificarla sin revisión externa;
- sería el único aprobador efectivo.

La persona conflictuada puede explicar y corregir, pero no puede ser el único voto de aceptación.

## 10. Repositorios y propiedad normativa

### `codec-cortex`

Contiene texto normativo, grammar, schemas, conformance y governance. Es la autoridad principal del estándar. Su gobernanza operativa (ciclos, blueprints, tareas) vive en `CODEC-CORTEX/.arqux/`.

### `codec-cortex` (implementación)

Contiene la implementación de referencia. Sus issues pueden descubrir problemas normativos, pero las correcciones al estándar ocurren vía Blueprint en el `.arqux/` del proyecto.

### Repositorios externos

`cortex-learning`, `cortex-runtime`, `arqux`, adaptadores y productos no poseen autoridad normativa sobre CORTEX.

## 11. Política de cambios

### 11.1 Cambio editorial

Corrige ortografía, enlaces o presentación sin modificar interpretación. No cambia versión semántica del estándar.

### 11.2 Errata

Aclara un texto cuya única interpretación correcta ya estaba determinada por el resto de la especificación y el corpus.

Una errata no puede:

- aceptar antes un documento inválido;
- rechazar antes un documento válido;
- cambiar bytes canónicos;
- cambiar AST;
- alterar roundtrip.

### 11.3 Revisión menor

Puede agregar capacidades compatibles, diagnostics opcionales o extensiones normativas que no modifiquen resultados existentes.

### 11.4 Revisión mayor

Es obligatoria cuando cambia:

- gramática incompatible;
- modelo abstracto;
- identidad;
- orden semántico;
- bytes canónicos;
- interpretación de extensiones existentes;
- roundtrip HCORTEX;
- requisitos de conformidad de forma incompatible;
- Constitución.

Toda revisión mayor se modela como un Blueprint `in_progress` con revisión externa registrada en ArqUX.

## 12. Versionado separado

Cada artefacto mantiene su versión:

- `CORTEX Standard X.Y`;
- `HCORTEX Standard X.Y`;
- `Canonicalization X.Y`;
- `codec-cortex-python A.B.C`;
- `conformance X.Y.Z`;
- perfiles con su propio SemVer.

Una implementación debe declarar qué versiones normativas implementa y qué nivel de conformidad acredita.

## 13. Política de compatibilidad

Antes de 1.0, los drafts pueden cambiar de forma incompatible, pero cada release debe:

- declarar el cambio;
- ofrecer migración o rationale;
- actualizar corpus y ejemplos;
- conservar artefactos de la versión anterior;
- evitar presentar el draft como estable.

Desde 1.0:

- una revisión menor no puede cambiar la interpretación de documentos 1.x válidos;
- una revisión mayor debe publicar guía de migración;
- la compatibilidad con dialectos experimentales no es garantía del estándar;
- el legacy bridge debe reportar toda inferencia o pérdida.

## 14. Ciclo de release normativa

Una release normativa pasa por Blueprints ArqUX con los siguientes gates:

```text
draft → ready → in_progress → done (ratified) → superseded
```

### Gate de Draft

- alcance definido;
- texto normativo completo para el objetivo;
- decisiones abiertas identificadas;
- ejemplos iniciales.

### Gate de Ready (revisión de completitud)

- metadatos de Blueprint completos;
- lenguaje normativo consistente;
- secciones obligatorias presentes;
- declaración de compatibilidad;
- ausencia de claims sin evidencia.

### Gate de in_progress (revisión técnica)

- gramática y ambigüedad;
- AST;
- canonicalización;
- identidad y orden;
- extensiones desconocidas;
- HCORTEX;
- loss report;
- seguridad;
- conformance;
- migración.

Un blocker abierto impide aceptación.

### Gate de Done (ratificación)

- aprobaciones requeridas registradas en ArqUX;
- artefactos inmutables y hashes;
- changelog;
- fecha de entrada en vigencia;
- registro de limitaciones.

## 15. Niveles de conformidad

Los claims oficiales son:

- `parser-conformant`;
- `canonical-conformant`;
- `hcortex-conformant`;
- `full-codec-conformant`;
- `profile-conformant:<profile-id>`.

Cada claim debe estar ligado a:

- versión del estándar;
- versión del corpus;
- reporte de ejecución;
- hashes de artefactos;
- plataforma y configuración.

## 16. Política de claims

No se permite afirmar:

- "estándar" antes de ratificación;
- "reversible" sin roundtrip correspondiente;
- "sin pérdida" sin loss report vacío y corpus pertinente;
- "más compacto" sin benchmark neutral;
- "conforme" sin suite de conformidad publicada;
- "seguro" como propiedad absoluta.

Los claims deben usar alcance y evidencia concretos.

## 17. Seguridad

Las vulnerabilidades se reportan mediante un canal privado designado por el proyecto. Una corrección urgente puede aplicarse antes de una discusión pública cuando la divulgación aumente el riesgo.

Toda excepción de seguridad debe:

- quedar registrada bajo embargo;
- limitarse al mínimo;
- evitar cambios normativos encubiertos;
- pasar revisión posterior;
- publicar advisory cuando sea seguro.

## 18. Transparencia y registros

Deben ser públicos, salvo embargo de seguridad:

- Blueprints y tareas de cambio normativo;
- decisiones y votos;
- objeciones técnicas;
- erratas;
- conformance reports;
- changelogs;
- criterios de release;
- conflictos de interés declarados.

Las conversaciones informales no sustituyen el registro de decisión en ArqUX.

## 19. Licenciamiento

El licenciamiento definitivo es una decisión de ratificación pendiente y debe resolverse antes de aceptar contribuciones externas sustantivas o publicar el primer draft ejecutable.

Recomendación para ratificación, no decisión automática:

- especificaciones y documentación normativa: `CC BY 4.0` o licencia documental equivalente;
- código y corpus ejecutable: `Apache-2.0`;
- ejemplos: licencia compatible y explícita.

La selección final debe registrarse como decisión de gobierno y verificar compatibilidad entre texto, código y contribuciones.

## 20. Contribuciones

Toda contribución debe:

- declarar licencia compatible;
- incluir tests cuando modifica comportamiento;
- identificar impacto normativo;
- evitar dependencias inversas;
- registrarse como Blueprint/tarea en ArqUX cuando tiene impacto normativo;
- aceptar revisión de seguridad y conformidad.

El merge de código no implica aceptación normativa.

## 21. Remoción y sucesión de roles

Un rol puede reasignarse por:

- renuncia;
- inactividad prolongada;
- conflicto persistente no declarado;
- incumplimiento de la Constitución;
- decisión documentada del Consejo.

La reasignación debe preservar continuidad, accesos, firmas, registros y separación de funciones.

## 22. Gobierno pre-1.0

Hasta Standard 1.0:

- el Arquitecto Principal mantiene decisión final de alcance;
- el Editor puede bloquear ambigüedades;
- Conformance puede bloquear claims no demostrados;
- toda incompatibilidad debe registrarse;
- ninguna feature se acepta solo por existir en la línea experimental.

## 23. Gobierno post-1.0

Después de 1.0:

- la estabilidad compatible tiene prioridad;
- las revisiones mayores requieren migración y revisión externa;
- los consumidores externos deben disponer de ventana pública de revisión;
- el poder de una implementación de referencia debe disminuir, no aumentar.

## 24. Ratificación de documentos de Fase 1

Los documentos de Fase 1 se ratifican como conjunto vía decisión registrada en ArqUX (Blueprint de ratificación). La decisión debe registrar:

- versión exacta de cada archivo;
- decisiones abiertas aceptadas o bloqueantes;
- identidad de aprobadores;
- resultado del Gate F1;
- fecha de entrada en vigor.
