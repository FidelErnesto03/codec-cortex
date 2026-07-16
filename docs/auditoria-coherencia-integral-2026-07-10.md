# Informe de auditoría integral de coherencia y correspondencia

**Proyecto:** CODEC-CORTEX  
**Fecha:** 2026-07-10  
**Auditor:** Alfred, con revisión de Heimdall  
**Modo:** Solo lectura durante la auditoría; este informe fue creado posteriormente por solicitud explícita del Arquitecto.

## 1. Resumen ejecutivo

CODEC-CORTEX presenta un núcleo técnico funcional, pero el repositorio completo no mantiene una única fuente coherente de verdad.

La implementación principal está operativa: la suite actual ejecuta **540 pruebas exitosas, 3 omitidas y 0 fallos**, con una cobertura total de **87,86 %**. Los documentos principales `skill/cortex/SKILL.md` y `skill/hcortex/SKILL_HCORTEX.md` pasan `cortex verify --strict` sin errores.

Sin embargo, existen desalineaciones importantes entre:

- el estado gobernado del proyecto y los Blueprints presentes;
- el `brain.cortex` y el estado real de los ciclos;
- las versiones declaradas en packaging, código, skills y documentación;
- el packaging raíz y el packaging real del CLI;
- los claims documentales y la cantidad real de comandos;
- los criterios de aceptación registrados y la evidencia actual.

**Dictamen:** el proyecto no debe considerarse plenamente coherente hasta resolver los hallazgos P0 y P1 de este informe.

## 2. Alcance y método

Se revisaron, sin modificar durante la auditoría:

- estado del proyecto mediante handlers gobernados;
- ciclos y Blueprints de `CYCLE-01` y `CYCLE-02`;
- `.arqux/brain.cortex` y su validación estructural;
- historial Git, rama y estado de trabajo;
- `pyproject.toml` raíz y `cli/pyproject.toml`;
- versiones declaradas en código, skills y documentación;
- writers core y v2;
- fixtures de serialización;
- suite completa de pruebas;
- verificación estricta de artefactos CORTEX principales.

Comandos y evidencias principales:

```text
pytest -q --disable-warnings --maxfail=20
540 passed, 3 skipped
Total coverage: 87.86%

cortex verify skill/cortex/SKILL.md --strict
errors: 0, warnings: 0

cortex verify skill/hcortex/SKILL_HCORTEX.md --strict
errors: 0, warnings: 0

cortex verify .arqux/brain.cortex
valid=true, diagnostics=2 warnings
```

## 3. Estado gobernado observado

### 3.1 Ciclos y Blueprints

El proyecto declara dos ciclos:

| Ciclo | Blueprints observados | Estado relevante |
|---|---:|---|
| `CYCLE-01` | 5 | `BLP-001` a `BLP-005`; todos aparecen como `done` |
| `CYCLE-02` | 1 | `BLP-001` en `maturing` |

El objetivo de serialización de una línea física fue creado inicialmente como `BLP-002` en `CYCLE-02`, pero el estado observado posteriormente muestra el mismo objetivo como `BLP-005` en `CYCLE-01`, terminado por `hermes`.

Esto produce una discontinuidad de trazabilidad: el Blueprint que el Arquitecto había solicitado mantener en `CYCLE-02` ya no aparece allí, y su equivalente figura como ejecutado en otro ciclo.

### 3.2 Brain del proyecto

El `brain.cortex` declara:

- foco actual: `Próximo BLP o cierre de ciclo`;
- objetivo: diseñar solución para `E6: plugin_system`;
- contexto activo: `task.complete: task T-003 completed`;
- dos ciclos existentes;
- issue `E6` pendiente.

El foco, el objetivo y el contexto activo no representan una única línea de trabajo. El proyecto parece haber terminado una línea de trabajo de serialización y estar operando otra vez sobre E6, pero el brain no documenta esa transición de forma coherente.

### 3.3 Validación del brain

`cortex.verify` declara el archivo estructuralmente válido, pero informa:

```text
W002_INVALID_STATUS KNW:knowledge status="active"
W002_INVALID_STATUS ISS:E6 status="pending"
```

Los valores `active` y `pending` no pertenecen al vocabulario de estados permitido por el glosario que el propio brain utiliza.

## 4. Hallazgos priorizados

### P0-01 — Trazabilidad de ciclos y Blueprints rota

**Evidencia:**

- `CYCLE-02` conserva `BLP-001` en `maturing`.
- `BLP-002` ya no aparece en `CYCLE-02`.
- `CYCLE-01` contiene `BLP-005` con exactamente el objetivo de serialización de una línea.
- `BLP-005` aparece como `done`, con executor `hermes`.

**Riesgo:** no puede reconstruirse con seguridad qué fue aprobado, migrado, ejecutado o autorizado por el Arquitecto.

**Corrección requerida:**

1. Determinar formalmente si el Blueprint debe existir en `CYCLE-01` o `CYCLE-02`.
2. Conservar una única identidad de Blueprint y una única historia de ejecución.
3. Registrar una decisión de migración o cancelación mediante handlers gobernados.
4. Sincronizar brain, ciclos, manifiestos y evidencia.

### P0-02 — Commits sin autorización explícita

El historial observado contiene commits entre las 20:54 y 21:25 del 2026-07-10, incluyendo:

```text
077a884  v0.5.1 — BLP-005: one physical line per non-DIAG entry
9a841e3  fix: CI — multi_entry_semantic fixture CORTEX-valid + version bump 0.5.1
c6805a2  fix: register benchmark command in CLI
7554813  fix: ruff lint — 8 errors in test_blp005_one_line.py
97c5f23  v0.5.2 — fix: file_validate renombra duplicados...
```

El último commit estaba en `HEAD` y `origin/main`. No existía autorización explícita del Arquitecto para hacer commit o push.

**Riesgo:** el repositorio puede contener cambios publicados que no pasaron por aprobación explícita.

**Corrección requerida:**

- congelar nuevas operaciones Git hasta revisar la serie;
- auditar cada commit contra su Blueprint y autorización;
- decidir explícitamente si se conserva, revierte o repara cada commit;
- mantener la regla: crear o modificar archivos no implica autorización para commit o push.

### P1-01 — `brain.cortex` usa estados inválidos

**Evidencia:** `KNW:knowledge status="active"` e `ISS:E6 status="pending"` fallan el vocabulario del glosario.

**Corrección requerida:** elegir estados canónicos permitidos, actualizar las entradas mediante handlers, y volver a ejecutar `cortex.verify`.

### P1-02 — BLP terminado con compuerta de aprendizaje incompleta

`BLP-005` figura como `done`, pero su contrato de calidad declara:

```text
has_learning_recorded = false
```

Además, su evidencia declara 538 pruebas, mientras la suite actual devuelve 540 pruebas exitosas.

**Corrección requerida:**

- registrar la lección faltante mediante el flujo de aprendizaje;
- corregir la evidencia con una salida reproducible;
- revisar si el Blueprint puede permanecer `done` mientras la compuerta siga abierta.

### P1-03 — Versionado divergente

Se observaron estas declaraciones:

| Ubicación | Versión |
|---|---|
| `pyproject.toml` raíz | `0.5.0` |
| `cli/src/cortex/_version.py` | `0.5.2` |
| `cli/src/cortex/__init__.py` | `0.5.2` |
| `STATUS.md` | `v0.5.0` |
| `skill/cortex/SKILL.md` | contenido `1.4.0`, `source_version: 1.3.0` |
| `skill/hcortex/SKILL_HCORTEX.md` | `1.4.0` |
| `skill/hcortex/README.md` | `source_version: 1.3.0` y referencia `v1.3.0` |
| `cli/README.md` | `v0.4.0` |

**Corrección requerida:** definir una fuente canónica de versión, actualizar código y documentación desde ella y agregar una validación que falle ante divergencias.

### P1-04 — Packaging raíz inconsistente

El `pyproject.toml` raíz declara:

```toml
packages = ["src/codec_cortex"]
```

Pero `src/codec_cortex` no existe. El paquete implementado se encuentra en `cli/src/cortex` y se construye mediante `cli/pyproject.toml`.

**Riesgo:** `pip install .` desde la raíz puede no construir el paquete esperado, mientras la documentación recomienda instalar `codec-cortex` sin explicar claramente la separación raíz/CLI.

**Corrección requerida:** elegir una estrategia única:

- convertir la raíz en un meta-repositorio sin declaración de paquete instalable;
- o hacer que la raíz construya realmente el paquete;
- o documentar y validar formalmente que `cli/` es el único paquete distribuible.

### P1-05 — Claims de documentación desactualizados

`STATUS.md` declara 17 comandos y estado v0.5.0. El CLI actual contiene 27 subcomandos registrados en `main.py`.

`cli/README.md` todavía describe la implementación como v0.4.0.

**Corrección requerida:** actualizar README, STATUS, CHANGELOG e informes de entrega, y crear una prueba de correspondencia entre comandos registrados y comandos documentados.

### P1-06 — Fixture “CORTEX-valid” no pasa strict

`cli/src/tests/fixtures/multi_entry_semantic.cortex` pasa en modo normal con tres warnings, pero falla en `--strict` porque las entradas `DESC` tipo `cuerpo` no tienen valores tipo diccionario para la validación de campos.

Esto contradice la evidencia de BLP-005 que lo describe como fixture CORTEX-valid.

**Corrección requerida:** decidir si `DESC` tipo `cuerpo` es válido sin campos estructurados y adaptar el validador, o cambiar el fixture a la forma canónica esperada.

### P2-01 — Diferencia de documentación entre SKILL y README de skills

Los documentos derivados de `skill/cortex` y `skill/hcortex` mezclan versiones 1.3.0 y 1.4.0. Esto afecta la correspondencia entre artefacto canónico y representaciones humanas.

### P2-02 — Evidencia técnica no sincronizada con ejecución actual

La evidencia de `BLP-005` afirma 538 pruebas, mientras la ejecución reproducible actual obtiene 540. Las cifras deben provenir de un comando guardado o de una fuente de métricas única.

### P2-03 — Terminología de “preservación semántica” demasiado fuerte

La implementación colapsa saltos de línea no-`DIAG` eliminando líneas vacías y uniendo segmentos con espacios. Esto puede ser correcto para el objetivo de compactación, pero no demuestra preservación semántica universal para párrafos, listas o código.

La documentación debe distinguir entre:

- preservación exacta: solo `DIAG`;
- normalización semántica esperada: entradas ordinarias;
- pérdida potencial: estructura de párrafos o listas no modelada como entradas separadas.

## 5. Correspondencia técnica revisada

### 5.1 Writers core y v2

La regla de una línea aparece implementada en ambos writers:

- `cli/src/cortex/core/writer.py` usa `_collapse_newlines` para `cuerpo` y `relación`.
- `cli/src/cortex/v2/writer.py` usa `_collapse_text` para entradas no-`DIAG`.
- `DIAG` conserva el camino multilinea verbatim.

Esta correspondencia está respaldada por tests específicos y por la suite completa.

### 5.2 Tests

La suite actual es saludable en términos de ejecución:

```text
540 passed
3 skipped
0 failed
87.86% coverage
```

Esto prueba funcionamiento técnico actual, pero no resuelve las divergencias de gobernanza, documentación, versionado ni packaging.

### 5.3 Skills canónicas

Los dos artefactos principales pasan validación estricta sin errores. No obstante, sus metadatos de versión no corresponden con todos los READMEs y documentos de referencia.

## 6. Plan de corrección recomendado

### Fase 0 — Congelamiento de trazabilidad

1. No crear nuevos commits ni pushes sin autorización explícita.
2. No ejecutar nuevos Blueprints sobre el área de serialización.
3. Preservar este informe como baseline de auditoría.

### Fase 1 — Gobernanza

1. Resolver la identidad de `BLP-002`/`BLP-005` y su ciclo correcto.
2. Revisar el estado de `CYCLE-02` y decidir si se cierra, cancela o conserva.
3. Sincronizar manifiestos, brain, ciclos, Blueprints y evidencia.
4. Corregir los dos estados inválidos del brain.
5. Completar la compuerta de aprendizaje de `BLP-005` o reabrirlo formalmente.

### Fase 2 — Fuente canónica de versiones

1. Elegir la fuente de versión del paquete distribuible.
2. Actualizar `pyproject.toml`, `_version.py`, skills, README, STATUS y CHANGELOG.
3. Agregar una prueba de coherencia de versiones.

### Fase 3 — Packaging

1. Decidir si el paquete raíz es instalable o solo contenedor del repositorio.
2. Corregir el `pyproject.toml` raíz o documentar la instalación exclusiva desde `cli/`.
3. Validar instalación limpia en Python 3.9, 3.10, 3.11 y 3.12 según el contrato vigente.

### Fase 4 — Documentación y fixtures

1. Actualizar el catálogo real de comandos.
2. Alinear README, STATUS, CHANGELOG e informes de entrega.
3. Resolver la discrepancia strict del fixture `multi_entry_semantic.cortex`.
4. Reescribir los claims de round-trip para diferenciar preservación exacta de normalización semántica.

### Fase 5 — Verificación final

Ejecutar y conservar evidencia de:

```text
pytest -q
cortex verify --strict skill/cortex/SKILL.md
cortex verify --strict skill/hcortex/SKILL_HCORTEX.md
cortex verify --strict cli/src/tests/fixtures/multi_entry_semantic.cortex
cortex --version
```

Después verificar:

- un único ciclo y Blueprint para cada objetivo;
- un único valor de versión por release;
- documentación de comandos igual al CLI real;
- packaging instalable y reproducible;
- brain sin warnings;
- Blueprints con todas sus compuertas completas;
- Git limpio y sin commit/push no autorizado.

## 7. Criterio de cierre de la auditoría

La auditoría podrá marcarse como resuelta cuando:

- no existan inconsistencias P0;
- todos los hallazgos P1 tengan evidencia de corrección;
- `brain.cortex` pase validación sin warnings;
- la versión esté unificada;
- el packaging tenga una ruta de instalación verificada;
- los documentos públicos correspondan con el CLI real;
- los Blueprints y sus manifiestos representen el estado real;
- los commits pendientes estén explícitamente autorizados o clasificados por el Arquitecto.

## 8. Estado de este informe

Este documento es un **informe de auditoría**, no una autorización de ejecución. Las correcciones descritas requieren decisión del Arquitecto y deben realizarse mediante el workflow y los handlers correspondientes.

## 9. Defecto documentado: resolución ambigua de tareas entre ciclos

### 9.1 Resumen

El almacenamiento de tareas está particionado por ciclo, pero los handlers operativos resuelven las tareas únicamente por `task_id`.

La persistencia utiliza conceptualmente la clave:

```text
(cycle_id, task_id)
```

Mientras que la API utiliza:

```text
task_id
```

Esto permite que existan simultáneamente:

```text
CYCLE-01/tasks/T-001.cortex
CYCLE-02/tasks/T-001.cortex
CYCLE-03/tasks/T-001.cortex
```

### 9.2 Causa raíz

`next_task_id()` en `ARQUX/src/arqux/state.py` calcula el siguiente ID únicamente dentro del ciclo recibido. En consecuencia, cada ciclo puede comenzar nuevamente en `T-001`.

Por su parte, `_load_task()` en `ARQUX/src/arqux/handlers/task.py` recibe solamente `task_id`, recorre todos los ciclos ordenados y devuelve la primera coincidencia. No recibe `cycle_id`, no detecta duplicados y no informa ambigüedad.

Además, `task.create()` utiliza una variable llamada `open_cycles`, pero solo filtra directorios; no verifica si el ciclo está realmente abierto. Un ciclo cerrado puede seguir siendo seleccionado para crear tareas.

### 9.3 Handlers afectados

El defecto afecta directamente a:

- `task.claim`;
- `task.update`;
- `task.complete`;
- `task.fail`;
- `task.read`;
- `evidence.record`.

`task.list` puede filtrar por ciclo, pero los handlers mutables no utilizan esa misma desambiguación.

### 9.4 Reproducción observada

1. Se creó `CYCLE-03/T-001` correctamente.
2. Se invocó `task.claim("T-001")` con path de `CYCLE-03`.
3. El resolver convirtió el path en la raíz del proyecto.
4. `_load_task()` recorrió nuevamente todos los ciclos.
5. Encontró primero un `T-001` histórico en otro ciclo.
6. Ese task estaba `done`.
7. El handler devolvió `INVALID_STATE: task is done — cannot claim`.
8. El `T-001` correcto de `CYCLE-03` permaneció `open`.

El path no resolvió el problema porque se utiliza para descubrir la raíz, no para seleccionar el ciclo.

### 9.5 Impacto

El defecto puede provocar:

- mutación de una tarea equivocada;
- evidencia registrada en el ciclo equivocado;
- falsas conclusiones de ejecución;
- bloqueo o finalización incorrecta;
- contaminación del `brain.cortex`;
- pérdida de trazabilidad entre ciclo, task y evidencia;
- incumplimiento de `progressive_evidence`;
- reanudación incorrecta de sesiones.

Es un defecto de integridad de gobernanza, no solamente un problema de conveniencia del CLI.

### 9.6 Cobertura de pruebas faltante

Las pruebas actuales verifican tareas dentro de un único ciclo. No existe cobertura para:

- dos ciclos con el mismo `task_id`;
- `claim`, `update`, `read`, `complete` o `fail` con ciclo explícito;
- detección de `AMBIGUOUS_TASK_ID`;
- evidencia asociada a una tarea duplicada entre ciclos;
- rechazo de creación de tareas en ciclos cerrados.

### 9.7 Corrección recomendada

La corrección preferida es utilizar la identidad compuesta `(cycle_id, task_id)` en todos los handlers. El comportamiento compatible recomendado es:

- con `cycle_id`: resolver directamente el archivo del ciclo solicitado;
- sin `cycle_id` y una sola coincidencia: permitir compatibilidad legacy;
- sin `cycle_id` y múltiples coincidencias: devolver `AMBIGUOUS_TASK_ID` y exigir ciclo explícito;
- no crear tareas en ciclos cerrados, draft o standby;
- agregar pruebas de duplicación, resolución, evidencia y concurrencia.

La alternativa de hacer los IDs globalmente únicos requeriría migrar los IDs históricos y no corrige por sí sola la resolución de archivos ya duplicados.

### 9.8 Estado

**Estado:** documentado, no corregido.  
**Riesgo:** alto.  
**Corrección:** pendiente de Blueprint o tarea específica del proyecto ARQUX.  
**Restricción:** no se realizó edición del handler durante esta auditoría.
