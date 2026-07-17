# Decisiones de diseño — Fase 2 REAL

**Document ID:** `CORTEX-F2-DESIGN-REAL-001`  
**Status:** `record-of-draft-decisions`

## D-001 — La unidad fundamental es la Idea

**Decisión:** `Idea`, no `Entry` genérico, es la unidad principal del AST.

**Razón:** CORTEX comprime comunicación contextual. La función del sigilo, el foco y el peso forman parte del significado estructural.

**Descartado:** serializar directamente un árbol genérico de values.

## D-002 — `$0` continúa siendo central

**Decisión:** todo sigilo usado se declara localmente en `$0`.

**Razón:** portabilidad y ausencia de registros externos.

**Límite:** `$0` define estructura y vocabulario; no impone ontología de agente.

## D-003 — El glosario amortiza la precisión

**Decisión:** shape, contrato, foco, descripción y peso se declaran una vez por sigilo.

**Razón:** repetirlos en cada Idea destruiría compacidad; omitirlos destruiría reproducibilidad.

## D-004 — Una línea regular, una Idea

**Decisión:** attrs, attrs-pos y relación ocupan una línea física.

**Excepciones:** cuerpo y bloque, por necesidad semántica o verbatim.

**Razón:** lectura selectiva y cierre local.

## D-005 — Se preservan shapes originales

**Decisión:** `attrs`, `attrs-pos`, `cuerpo`, `bloque`, `relacion`.

**Razón:** representan formas ideáticas distintas y tienen proyecciones humanas directas.

**Descartado:** `encoded`, tuples genéricas y wrappers del AST visibles en la sintaxis.

## D-006 — Contratos también para attrs

**Decisión:** attrs declara `fields`, tipos, opcionalidad y `focus`.

**Razón:** la skill original repetía patrones de facto; el estándar los vuelve verificables.

**Compatibilidad:** requiere enriquecer `$0`, no reescribir las líneas ordinarias.

## D-007 — Bare atoms permanecen

**Decisión:** values compactos como `current`, `blocking` y selectors simples siguen siendo atoms.

**Razón:** son parte central de la compresión lingüística.

**Control:** texto con espacios dentro de attrs exige quotes; positional admite texto raw por contrato.

## D-008 — Microtokens son declarativos

**Decisión:** `$0:micro_x{expand:y}`.

**Razón:** compresión local portable.

**Prohibición:** no son macros ejecutables ni se aplican a claves o sigilos.

## D-009 — Weight reemplaza acoplamientos cognitivos

**Decisión:** `weight:B|M|H` es metadata funcional neutral.

**Razón:** conserva “peso claro” sin importar `Semantic`, `Prefrontal`, `Working`, risk o políticas de memory.

## D-010 — Namespace sin impuesto de repetición

**Decisión:** namespace puede declararse en el sigilo local y derivarse en AST; la forma calificada es opcional.

**Razón:** evita colisiones sin agregar prefijos a todas las líneas.

## D-011 — Extensiones amplían glosario, no gramática

**Decisión:** ninguna extensión puede introducir un nuevo encabezado de Idea o delimitador.

**Razón:** reproducibilidad e implementación independiente.

## D-012 — Dirección local no es identidad durable

**Decisión:** `$section:symbol:name` identifica dentro del documento.

**Razón:** mover una Idea entre secciones no debería definir por accidente su identidad histórica.

**Frontera:** stable IDs son campos o extensiones posteriores.

## D-013 — No hay terminador `;`

**Decisión:** newline delimita líneas regulares.

**Razón:** `;` no aporta significado y en el formato original podía formar parte de texto positional.

## D-014 — Secciones no heredan semántica

**Decisión:** títulos y ubicación organizan; no completan fields faltantes.

**Razón:** una línea debe ser legible selectivamente.

## D-015 — AST ideático y neutral

**Decisión:** el AST deriva `function.label`, `weight` y `focus`, pero no conoce sigilos concretos.

**Razón:** preservar intención sin convertir perfiles en Core.

## D-016 — Fase 2 no canonicaliza

**Decisión:** preserva lexemas y orden; Fase 3 define bytes, normalización y hashes.

**Razón:** respetar la frontera original del plan.

## D-017 — Reversibilidad preparada, no simulada

**Decisión:** cada shape conserva información para proyección HCORTEX directa.

**Razón:** Fase 4 necesita un AST suficiente, no VIEW obligatorio ni render creativo.
