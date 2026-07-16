Perfil: CORTEX-FULL

# HCORTEX-AUDIT — Auditoría técnica del aplicativo `codec-cortex-1.0.0`

## Identidad

| Campo | Valor |
|---|---|
| Artefacto auditado | `codec-cortex-1.0.0.tar.gz` |
| Especificación usada como base normativa | `SKILL.md` v1.1.0-enterprise-candidate |
| Modalidad | Revisión estática + ejecución de pruebas + pruebas dirigidas de brechas |
| Resultado global | Implementación real y modular, pero todavía no plenamente conforme con CODEC-CORTEX como protocolo cognitivo gobernado |
| Estado recomendado | `experimental/current` para parser/AST/render/CRUD básico; `planned` para conformidad normativa completa |

## Foco

Revisar si el CLI implementado corresponde de verdad al modelo de trabajo definido por `SKILL.md`: separación de niveles, autocontención `$0`, codec `.cortex ⇄ HCORTEX`, CRUD, verificación, gobierno de madurez, triaje P0-P5, HCORTEX audit/readable y protección de invariantes cognitivas.

## Objetivo

Determinar:

1. Qué partes del aplicativo sí materializan el SKILL.
2. Qué partes son aproximaciones funcionales pero no conformidad plena.
3. Qué brechas deben cerrarse antes de declarar el CLI como implementación canónica.
4. Qué mejoras priorizar para llevarlo de “CLI funcional” a “codec gobernado CODEC-CORTEX”.

## Resultado ejecutivo

El aplicativo es una base seria. No es un simple generador de texto: incluye AST, lexer, parser, writer canónico, validación, comparación estructural, render HCORTEX, compilación HCORTEX-EDIT, CRUD, transacciones atómicas, plantillas y suite de pruebas. La ejecución local arrojó `61 passed`.

Pero hay una diferencia crítica entre “funciona para fixtures controlados” y “cumple el SKILL como protocolo de memoria cognitiva gobernada”. Hoy el CLI cumple bien la capa sintáctica inicial, pero no gobierna suficientemente la capa semántica/prefrontal del protocolo.

La implementación actual debe considerarse:

| Dimensión | Estado real |
|---|---|
| Parser `.cortex → AST` | Implementado, usable |
| Writer `AST → .cortex` | Implementado, determinista |
| HCORTEX-EDIT reversible | Implementado para casos controlados |
| HCORTEX-READ humano | Implementado, pero incompleto respecto al SKILL |
| CRUD de entradas | Implementado |
| CRUD de glosario y microtokens | Implementado parcialmente |
| Verificación estructural | Implementada parcialmente |
| Separación Nivel 1/2/3 | No suficientemente validada |
| Reglas FCS/OBJ antes de operar | No garantizadas por validador |
| Triaje P0-P5 / perfiles HCORTEX | No implementado realmente |
| CORTEX-OUT | No corresponde al CLI; aparece en opciones pero no tiene efecto real |
| Compatibilidad con `.cortex` históricos del proyecto | Débil; el parser es estricto con la forma nueva |

## Evidencia normativa extraída del SKILL

El SKILL separa responsabilidades: `SKILL.md` especifica, `SKILL.cortex` gobierna sin estado vivo, `brain.cortex` almacena FCS/OBJ/WRK/STP/NXT, los paquetes son contexto transportable, HCORTEX es vista humana y CORTEX-OUT es salida conversacional independiente. Fuente: `SKILL.md:30-41`.

El Nivel 2 debe contener foco y objetivo, y el agente debe validar `FCS` y `OBJ` antes de actuar. Fuente: `SKILL.md:218-220`.

Todo `.cortex` debe iniciar con `$0` local, mínimo y autocontenido. Además, `$0` es la fuente estructural local para sigilos, tipos, contratos, microtokens y reglas de render/recuperación. Fuente: `SKILL.md:306-336`.

La matriz de niveles prohíbe estado vivo en Nivel 1: `FCS`, `OBJ` y `STP` solo como contrato/ejemplo en `SKILL.cortex`; `WRK`, `NXT`, `SES` y `LNG` no corresponden como estado vivo en Nivel 1. Fuente: `SKILL.md:601-629`.

HCORTEX debe declarar perfil, filtrar por P-level/survive, ordenar P0→P5 y en modo auditoría agregar `source`. Fuente: `SKILL.md:720-735`.

El SKILL declara como contrato planificado comandos `decode`, `encode`, `patch_add`, `patch_update`, `patch_remove`, `diagram`, `promote` y `decay`. Fuente: `SKILL.md:1104-1136` y `SKILL.md:1564-1576`.

## Inventario real del aplicativo

| Capa | Archivos principales | Evaluación |
|---|---|---|
| CLI | `src/cortex/cli/main.py`, `src/cortex/cli/commands/*.py` | Arquitectura clara con subcomandos `new`, `render`, `compile`, `verify`, `get`, `list`, `add`, `update`, `delete`, `move`, `glossary`, `micro`, `doctor`, `diff`, `format`. |
| Core | `ast.py`, `lexer.py`, `parser.py`, `writer.py`, `validator.py`, `compare.py` | Núcleo correcto para un primer codec determinista. |
| HCORTEX | `hcortex/read_renderer.py`, `edit_renderer.py`, `edit_parser.py` | Separa vista humana no reversible y vista editable reversible. Buena decisión. |
| CRUD | `crud/mutations.py`, `selectors.py`, `transactions.py` | Operaciones útiles y escritura atómica con backup. |
| Glosario | `glossary/minimal.py`, `contracts.py`, `resolver.py` | Buen arranque, pero con decisiones que pueden ocultar incumplimientos de `$0`. |
| Plantillas | `templates/brain.py`, `skill.py`, `package.py` | Alineadas con la intención de autocontención mínima. |
| Pruebas | `src/tests/*.py` | 61 pruebas pasan; cubren happy path y errores básicos. |

Métricas de revisión:

| Métrica | Valor |
|---|---:|
| Archivos Python en `src/cortex` | 47 |
| Líneas Python aproximadas en `src/cortex` | 5.561 |
| Líneas de tests | 758 |
| Resultado de test local | 61 passed |
| Tamaño del paquete comprimido | 53 KB |

## Correspondencia con el SKILL

### Correspondencias fuertes

| Requisito del SKILL | Evidencia de implementación | Veredicto |
|---|---|---|
| `.cortex → AST` | `parse_cortex()` construye `CortexDocument`, secciones, entradas y glosario. `src/cortex/core/parser.py:408-498`. | Cumple base. |
| AST canónico | `CortexDocument`, `Section`, `Entry`, `Glossary`, hashes estructurales. `src/cortex/core/ast.py:83-246`, `253-282`. | Cumple base. |
| `$0` primero | Parser rechaza si la primera sección no es `$0`. `src/cortex/core/parser.py:480-492`. | Cumple de forma estricta. |
| Writer determinista | `write_cortex()` regenera `$0` y serializa de forma canónica. `src/cortex/core/writer.py:188-232`. | Cumple base. |
| HCORTEX-EDIT reversible | Renderer agrega metadata `cortex-entry` y parser recompila. `edit_renderer.py:96-158`, `edit_parser.py:250-358`. | Cumple para casos cubiertos. |
| HCORTEX-READ no compilable | Header `roundtrip:false`, parser lo rechaza. `read_renderer.py:121-151`, `edit_parser.py:264-267`. | Cumple. |
| CRUD básico | `add_entry`, `update_entry`, `delete_entry`, `move_entry`. `crud/mutations.py:27-194`. | Cumple base. |
| Escritura atómica | Serializa, reparsea, valida, escribe tmp, backup, replace. `crud/transactions.py:50-138`. | Buena implementación. |
| Verificación y diff | `verify --roundtrip hcortex-edit`, `compare_ast()`. `commands/verify.py:18-88`, `core/compare.py:134-180`. | Cumple parcialmente. |

### Correspondencias parciales

| Requisito del SKILL | Estado real | Brecha |
|---|---|---|
| Glosario `$0` como fuente de verdad local | El parser exige `$0`, pero si faltan tipos o microtokens canónicos los siembra automáticamente. `parser.py:292-299`. | Esto mejora tolerancia, pero puede ocultar archivos incompletos. Debería advertir. |
| `attrs-pos` con contrato | Soporta `GCON` y `# contract:`; valida ausencia de contrato. | No valida exceso de posiciones; ignora campos sobrantes. |
| Contratos mínimos por sigilo | `validator.py` define campos requeridos para FCS/OBJ/WRK/STP/etc. `validator.py:36-49`. | Solo advierte si faltan campos; no valida existencia obligatoria de FCS/OBJ en brain. |
| Protección P0 | `delete_entry()` protege FCS/OBJ/CNST si `survive:min` o `severity:blocking`. `validator.py:53-68`, `mutations.py:143-165`. | Protección puntual, no triaje P0-P5 completo. |
| Madurez de comandos | README declara “implements specification” y “deterministic processor”. `README.md:1-4`. | Hay riesgo de overclaim: no implementa todos los contratos planificados del SKILL. |
| CLI planificada | Tiene `render/compile/add/update/delete`; no `decode/encode/patch_*`. `cli/main.py:60-241`. | Funcionalmente cercano, nominalmente no corresponde al contrato planificado. |

### No correspondencias críticas

| Código | Brecha | Impacto |
|---|---|---|
| B-001 | No se valida que `brain.cortex` tenga `FCS` y `OBJ` activos. | Rompe el principio operativo central del Nivel 2. |
| B-002 | No se valida separación de niveles: un `SKILL.cortex` puede contener `WRK` vivo si el sigilo está declarado. | Rompe la arquitectura de 3 niveles. |
| B-003 | HCORTEX-READ no declara `Perfil: CORTEX-<LEVEL>` ni filtra por `survive`/P-level ni ordena P0→P5. | No cumple el render HCORTEX canónico. |
| B-004 | No existe modo `HCORTEX-AUDIT` real; solo `--with-source` en READ. | Auditoría incompleta. |
| B-005 | CORTEX-OUT aparece como opción `--with-cortex-out`, pero no se usa. `cli/main.py:69-72`, `commands/new.py:13-71`. | Opción fantasma; puede confundir madurez. |
| B-006 | El parser no tolera preámbulos antes de `$0` ni glosarios históricos con columna `Expansion` sin `Layer`; falla contra artefactos previos del proyecto. | Riesgo serio de migración. |
| B-007 | El roundtrip de HCORTEX-EDIT rompe valores con pipe `|` escapado en tablas. | Afecta reversibilidad estructural en casos reales. |
| B-008 | `attrs-pos` ignora valores sobrantes en vez de advertir o degradar a `attrs`. | Puede perder información silenciosamente. |
| B-009 | No valida valores de `survive`. | Deja pasar prioridades inválidas. |
| B-010 | No hay comandos `diagram list/extract/validate`, aunque el SKILL los planifica. | Brecha con operación visual/PlantUML. |
| B-011 | No hay `STATUS.md` ni `BENCHMARK.md` en el paquete. | Menor gobernanza de madurez y evidencia. |
| B-012 | No hay `LICENSE` físico aunque `pyproject.toml` declara MIT. | Brecha de empaquetado/legal. |

## Pruebas ejecutadas

### Suite incluida

Comando:

```bash
cd /mnt/data/codec_cortex_audit/src/cortex
python -m pytest -q
```

Resultado:

```text
61 passed in 1.59s
```

Interpretación: la base está estable contra su propia expectativa. Pero la suite prueba mayormente fixtures controlados y no fuerza suficientemente las invariantes cognitivas del SKILL.

### Pruebas dirigidas adicionales

| Prueba | Resultado | Lectura crítica |
|---|---|---|
| Eliminar `FCS` y `OBJ` de un brain generado | `validate(doc) == []` | Falta regla de conformidad de Nivel 2. |
| Insertar `WRK` vivo en `SKILL.cortex` declarando el sigilo | `validate(doc) == []` | Falta validación de separación de niveles. |
| Cambiar `CNST:blocking` a `survive:"work"` | `validate(doc) == []` | No se obliga a que bloqueo sea P0/min. |
| Usar `survive:"forever"` | `validate(doc) == []` | No hay dominio permitido para `survive`. |
| `HDL:op{decode | current | file | unexpected}` | El cuarto campo se pierde sin diagnóstico. | Riesgo de pérdida silenciosa en `attrs-pos`. |
| Valor `what:"A | B"` en HCORTEX-EDIT | Roundtrip no igual; queda `A \`. | Bug real de escape/unescape de tabla Markdown. |
| Verificar `.cortex` históricos presentes en entorno | Muchos errores y 0 sigilos detectados. | El parser está calibrado para la nueva forma, no para migración histórica. |

## Diagnóstico por componente

### Parser y lexer

Fortalezas:

- Buen manejo de braces balanceados y strings.
- Rechazo correcto de `$0` ausente o no primero.
- Soporta secciones `$N`, headers comentados y markdown-friendly.
- Construye AST con metadata y hashes.

Problemas:

- El parser exige que `$0` sea la primera sección real. Esto sigue el SKILL nuevo, pero no tolera encabezados SPDX/Markdown antes de `$0`, presentes en artefactos históricos.
- El regex de glosario espera `Sigil | Name | Type | Risk | Layer | Description`; no admite glosarios previos `Sigil | Name | Expansion | Risk | Description`.
- Se siembran tipos y microtokens canónicos aunque `$0` no los declare. Esto debe ser modo `compat`, no modo normal silencioso.
- `parse_attrs_body()` no soporta listas ni objetos anidados reales; los trata como bare strings o falla según el caso. Algunos `.cortex` históricos usan `items:[...]` y mapas anidados.

Criterio: suficiente para v0 funcional, insuficiente para migración robusta.

### AST y writer

Fortalezas:

- Modelo simple y correcto.
- Hash estructural razonable.
- Writer determinista.
- `$0` se regenera desde `doc.glossary`, lo cual estabiliza salida.

Problemas:

- Regenerar `$0` puede borrar comentarios normativos locales no representados en el modelo.
- `raw_lines` existe pero no se escribe; líneas no parseadas se pierden en formato.
- `bloque` promete verbatim, pero el valor se normaliza con `strip("\n")`; esto puede alterar bloques que dependen de saltos iniciales/finales.

Criterio: muy buena base, pero falta política explícita entre “normalización canónica” y “preservación bit a bit”.

### Validator

Fortalezas:

- Detecta sigilos desconocidos.
- Detecta tipos desconocidos.
- Detecta `attrs-pos` sin contrato.
- Revisa campos requeridos en sigilos críticos.
- Revisa status/severity/priority.
- Detecta duplicados dentro de una sección.

Problemas críticos:

- La mayoría de violaciones semánticas se expresan como warning, no como error.
- No hay detección de tipo de documento (`skill`, `brain`, `package`) para aplicar reglas por nivel.
- No valida presencia obligatoria de `FCS` y `OBJ` en Nivel 2.
- No valida prohibición de estado vivo en Nivel 1.
- No valida que Nivel 3 no tenga ciclo de vida propio o estado vivo no confirmado.
- No valida `survive` ni P0/P1/P2.
- No valida secretos en claro.
- No valida claims de madurez contra `STATUS.md`.

Criterio: validador sintáctico/estructural inicial, no validador cognitivo completo.

### HCORTEX

Fortalezas:

- Separación correcta entre READ no reversible y EDIT reversible.
- READ omite `$0` por defecto, alineado con el SKILL.
- EDIT incluye metadata de sección/entrada y glosario.

Problemas:

- READ no empieza con `Perfil: CORTEX-<LEVEL>`.
- No existen perfiles `MIN`, `RECOVERY`, `WORK`, `FULL` como filtros reales.
- No ordena por P0→P5.
- `--with-source` no equivale a `HCORTEX-AUDIT`; no agrega columna `source` en tablas, sino un subscript en el header.
- No declara omisiones por presupuesto.
- Bug de roundtrip con pipes en valores Markdown.

Criterio: HCORTEX-EDIT está bien encaminado; HCORTEX-READ/AUDIT aún no cumple el canon.

### CRUD y transacciones

Fortalezas:

- API limpia para add/update/delete/move.
- Selectores simples y útiles.
- Escritura atómica con backup.
- Bloqueo de borrado para FCS/OBJ/CNST cuando son protegidos.

Problemas:

- `add_entry()` permite agregar sigilos no declarados; solo serán diagnosticados luego. Para operación segura debería fallar salvo `--force` o `--recovery`.
- `update_entry()` no valida si el cambio rompe contratos mínimos.
- `move_entry()` no controla separación de niveles ni destino permitido.
- No se registra `AUD` automáticamente para cambios críticos.
- No hay patch transaccional declarativo tipo `patch_add/patch_update/patch_remove` como contrato del SKILL.

Criterio: CRUD técnico correcto; CRUD gobernado todavía pendiente.

### CLI

Fortalezas:

- Buen set de comandos operativos.
- `render`/`compile` cubren el caso `.cortex → HCORTEX-EDIT → .cortex`.
- `verify --roundtrip hcortex-edit` es un avance real respecto a la especificación planificada.
- `doctor` y `diff` son decisiones útiles.

Problemas:

- La nomenclatura no corresponde al contrato planificado (`decode`, `encode`, `patch_*`). Puede aceptarse como UX alternativa, pero debe documentarse como alias o decisión de diseño.
- `--json` global se maneja de forma inconsistente: algunos comandos usan `args.format`, otros inspeccionan `sys.argv`.
- `render` revisa si el archivo de salida existe, pero el bloque no hace nada con esa condición.
- `--with-cortex-out` existe en parser CLI, pero no se consume.
- Usar `python -m cortex.cli.main` produce warning de `runpy`; `python -m cortex` es más limpio.

Criterio: CLI usable para desarrollo, aún no pulido como herramienta empresarial.

## Brechas por severidad

### Severidad alta

| ID | Brecha | Recomendación |
|---|---|---|
| H-01 | No se valida presencia de `FCS` y `OBJ` en brain. | Implementar `document_kind` y reglas hard por tipo. |
| H-02 | No se valida separación Nivel 1/2/3. | Agregar `LevelPolicyValidator`. |
| H-03 | HCORTEX no aplica perfiles ni P0-P5. | Crear `ProfileResolver` y `PriorityClassifier`. |
| H-04 | Bug de pipes en HCORTEX-EDIT. | Implementar parser de tabla Markdown con escape `\|` real. |
| H-05 | `attrs-pos` pierde campos sobrantes. | Error o warning fuerte; nunca pérdida silenciosa. |
| H-06 | Compatibilidad débil con `.cortex` previos. | Modo `recover/migrate` para glosarios legacy y preámbulos. |

### Severidad media

| ID | Brecha | Recomendación |
|---|---|---|
| M-01 | Tipos/microtokens canónicos se inyectan sin advertencia. | Separar `strict` vs `compat`; advertir en compat. |
| M-02 | Warnings contractuales no fallan verificación. | Añadir `--strict` y niveles de severidad configurables. |
| M-03 | No hay validación de secretos. | Scanner de patrones: keys, tokens, passwords, URLs con credenciales. |
| M-04 | No hay `AUD` automático en cambios críticos. | `--audit` por defecto en mutations que toquen FCS/OBJ/CNST/CLAIM/KNW. |
| M-05 | Ausencia de `STATUS.md`/`BENCHMARK.md`. | Agregar documentos de madurez y evidencia. |
| M-06 | README overclaim. | Cambiar a “implements a first functional subset”. |

### Severidad baja

| ID | Brecha | Recomendación |
|---|---|---|
| L-01 | Falta `LICENSE` físico. | Agregar MIT LICENSE. |
| L-02 | Warning con `python -m cortex.cli.main`. | Documentar `python -m cortex` o ajustar imports. |
| L-03 | Tipos `template`, `language` poco usados. | Implementar efecto real o retirar temporalmente. |
| L-04 | No hay benchmarks de rendimiento/densidad. | Añadir suite mínima de benchmarks reproducibles. |

## Recomendaciones prioritarias TOP 10

1. Implementar `document_kind` inferido por `IDN`/`DOM`/nombre de archivo: `skill`, `brain`, `package`, `generic`.
2. Crear `LevelPolicyValidator` con reglas duras: Nivel 1 sin estado vivo; Nivel 2 requiere FCS/OBJ; Nivel 3 no madura ni contiene WRK vivo salvo modo recovery.
3. Implementar `survive` como dominio validado: `min|recovery|work|full`.
4. Implementar `PriorityClassifier`: P0/P1/P2/P3/P4/P5 desde sigilo + atributos (`survive`, `severity`, `status`).
5. Rehacer HCORTEX-READ como `render_hcortex(profile, mode)` con `READABLE`, `AUDIT`, `RECOVERY`, `FULL`.
6. Corregir escape/unescape de tablas Markdown para HCORTEX-EDIT.
7. Añadir modo `recover`/`migrate` para `.cortex` históricos: preámbulo antes de `$0`, columna `Expansion`, ausencia de `Layer`, `contenido` como alias de `cuerpo`, objetos/listas simples.
8. Hacer que `attrs-pos` con número incorrecto de campos genere error o degrade explícitamente a `attrs`, según el SKILL.
9. Normalizar comandos o aliases: `decode=render`, `encode=compile`, `patch_add=add`, `patch_update=update`, `patch_remove=delete`.
10. Ajustar README y pyproject para declarar madurez exacta: “functional subset / experimental codec CLI”, no conformidad plena.

## Roadmap propuesto

### Fase 1 — Hardening de conformidad mínima

Objetivo: que `verify --strict` capture las violaciones centrales del SKILL.

Entregables:

- `DocumentKind`.
- `LevelPolicyValidator`.
- Validación hard de `FCS/OBJ` en brain.
- Validación hard de estado vivo prohibido en skill.
- Dominio de `survive`.
- `CNST:severity=blocking` obliga `survive:min` o diagnóstico hard.
- Tests de regresión para todas estas reglas.

### Fase 2 — HCORTEX canónico

Objetivo: que HCORTEX cumpla el procedimiento del SKILL.

Entregables:

- `--profile min|recovery|work|full`.
- `--mode readable|audit|edit`.
- Primera línea `Perfil: CORTEX-<LEVEL>` en READ/AUDIT/FULL.
- Orden P0→P5.
- Omisiones explícitas.
- `source` como columna real en AUDIT.
- Corrección de tabla Markdown reversible.

### Fase 3 — Migración y compatibilidad

Objetivo: poder absorber artefactos históricos sin romper la continuidad del proyecto.

Entregables:

- `cortex recover <file>`.
- `cortex migrate <file> --from legacy-skill-alpha`.
- Soporte de `$0` con `Expansion`.
- Alias de tipo `contenido → cuerpo`.
- Preambles SPDX antes de `$0` como metadata o warning.
- Reporte de ambigüedades `RSK/AUD`.

### Fase 4 — Operación CLI canónica

Objetivo: alinear contratos del SKILL con UX real.

Entregables:

- Aliases `decode/encode/patch_*`.
- `diagram list/extract/validate`.
- `doctor --strict --kind brain|skill|package`.
- `verify --roundtrip cortex|hcortex-edit`.
- `diff --profile structural|semantic|governance`.

### Fase 5 — Gobernanza empresarial

Objetivo: evitar overclaim y preparar madurez pública.

Entregables:

- `STATUS.md`.
- `BENCHMARK.md`.
- `CHANGELOG.md`.
- `LICENSE`.
- Matrix de conformidad generada automáticamente.
- Benchmarks reproducibles de roundtrip, preservación P0/P1 y densidad.

## Criterios de aceptación propuestos

| Gate | Criterio | Debe fallar si... |
|---|---|---|
| G1 | `verify --strict brain.cortex` | Falta FCS u OBJ activo. |
| G2 | `verify --strict SKILL.cortex` | Contiene WRK/NXT/SES/LNG vivo no marcado como ejemplo/contrato. |
| G3 | `render --mode audit --profile recovery` | No incluye source o no limita a P0/P1. |
| G4 | `roundtrip hcortex-edit` | Cambia valores con pipes, comillas, unicode, bloques PlantUML o attrs-pos. |
| G5 | `recover legacy.cortex` | No reconstruye `$0` mínimo o no marca riesgos. |
| G6 | `doctor --strict` | Warnings críticos quedan como warning cuando rompen conformidad. |
| G7 | `diagram extract` | No preserva bloque DIAG verbatim. |
| G8 | `benchmark` | Declara measured sin dataset/script reproducible. |

## Juicio técnico final

El agente que desarrolló el aplicativo hizo una implementación valiosa y técnicamente defendible para una primera versión. La arquitectura es modular y está bien encaminada. La decisión más fuerte es el uso de AST como representación interna única, porque eso permite codec, diff, verify, patch y HCORTEX sin depender de heurística conversacional.

Pero todavía no puede declararse “implementación conforme completa de CODEC-CORTEX”. Lo correcto es decir:

> `codec-cortex-1.0.0` implementa un subconjunto funcional del codec CODEC-CORTEX: parser, AST, writer, HCORTEX-EDIT, HCORTEX-READ básico, verificación estructural inicial y CRUD. Aún requiere hardening de políticas cognitivas, perfiles HCORTEX, triaje P0-P5, separación de niveles, migración legacy y benchmarks para ser considerado implementación canónica del SKILL.

La brecha no es de cantidad de código. La brecha es de gobierno: hoy el CLI manipula archivos `.cortex`; todavía no protege completamente la disciplina cognitiva que hace que CODEC-CORTEX sea más que un formato.

## Próxima acción recomendada

Ejecutar primero el hardening del validador. Sin eso, cualquier mejora de render, CRUD o UX puede producir una herramienta cómoda pero permisiva. La prioridad correcta es:

```text
Validator de conformidad → HCORTEX canónico → Recovery/Migration → Aliases CLI → Benchmarks/Gobernanza
```

