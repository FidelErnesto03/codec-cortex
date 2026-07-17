# Constitución de CORTEX

**Document ID:** `CORTEX-CONSTITUTION-001`  
**Version:** `0.1.0-draft`  
**Status:** `draft-for-ratification`  
**Normative scope:** principios inmutables, autoridad y límites constitucionales  
**Authority basis:** `CORTEX-CHARTER-001` y `CCX-CORE-PROJECT-PLAN-001`  
**Language:** español  
**Date:** `2026-07-16`

---

## 1. Carácter normativo

Esta Constitución establece las reglas superiores del estándar CORTEX. Toda especificación, decisión de cambio registrada en ArqUX, implementación, perfil, extensión, corpus o release debe ser compatible con ella.

Las palabras **DEBE**, **NO DEBE**, **REQUERIDO**, **DEBERÍA**, **NO DEBERÍA** y **PUEDE** expresan obligatoriedad normativa. Una desviación de **DEBE** o **NO DEBE** es una no conformidad.

## 2. Jerarquía de autoridad

La autoridad normativa de CORTEX se ordena así:

1. esta Constitución;
2. especificaciones del estándar ratificadas;
3. corpus y vectores de conformidad publicados para esa versión;
4. decisiones de cambio normativo ratificadas y aplicables;
5. documentación no normativa;
6. implementaciones.

Ninguna implementación puede redefinir el estándar por comportamiento de facto.

## 3. Artículo I — Representación, no gobierno

CORTEX DEBE representar información y NO DEBE decidir qué aprende, recuerda, ejecuta, autoriza, promueve o descarta un consumidor.

La semántica operacional pertenece al consumidor, a un perfil o a un sistema externo.

## 4. Artículo II — Neutralidad ontológica

La gramática base NO DEBE reservar vocabulario de un dominio particular.

Nombres heredados o comunes como `FCS`, `OBJ`, `WRK`, `SES`, `LNG`, `KNW`, `brain`, `skill` o `handoff` PUEDEN ser definidos por perfiles, pero NO DEBEN adquirir privilegio sintáctico en el núcleo.

## 5. Artículo III — Dependencias unidireccionales

El núcleo NO DEBE importar, requerir ni modificar:

- perfiles oficiales o privados;
- runtime;
- learning;
- ArqUX;
- frameworks de agentes;
- adaptadores MCP/ACP/LSP;
- productos consumidores.

Las capas externas PUEDEN depender del estándar y de la implementación de referencia. La dependencia inversa es inconstitucional.

## 6. Artículo IV — Determinismo

Parsing, escritura canónica, validación estructural, equivalencia y transformación HCORTEX canónica DEBEN ser deterministas.

Estas operaciones NO DEBEN depender de:

- LLM;
- clasificación probabilística;
- heurísticas no declaradas;
- estado remoto mutable;
- fecha, locale o plataforma cuando el estándar no lo permita explícitamente.

Toda opción que altere un resultado normativo DEBE formar parte de la entrada declarada.

## 7. Artículo V — No existe pérdida silenciosa

Una operación potencialmente destructiva DEBE:

1. identificar la información afectada;
2. clasificar el tipo de pérdida;
3. producir un reporte legible por máquina;
4. requerir una operación explícita;
5. conservar el original o exigir una política explícita de reemplazo.

Una implementación NO DEBE presentar como reversible una transformación que no lo sea.

## 8. Artículo VI — Canonicalización idempotente

La canonicalización DEBE producir bytes estables para una versión dada y cumplir:

```text
canonicalize(canonicalize(x)) == canonicalize(x)
```

Las reglas de canonicalización DEBEN estar especificadas y cubiertas por vectores de conformidad. Ninguna implementación puede introducir orden, whitespace, escapes o normalización propios en la forma canónica.

## 9. Artículo VII — HCORTEX deriva del AST

HCORTEX-CANONICAL DEBE ser una proyección universal del AST CORTEX y NO DEBE constituir una segunda ontología.

La transformación canónica DEBE cumplir roundtrip estructural:

```text
compile_hcortex(render_hcortex(ast)) == ast
```

Las vistas especializadas, dashboards, diagramas o proyecciones se consideran extensiones y NO DEBEN ser requisito para la reversibilidad base.

## 10. Artículo VIII — Extensibilidad preservable

Toda extensión DEBE declarar namespace, identidad, versión, obligatoriedad y payload.

Un consumidor que desconozca una extensión opcional DEBE preservarla o emitir un diagnóstico de incapacidad. NO DEBE descartarla silenciosamente.

Una extensión requerida que no pueda procesarse DEBE impedir una interpretación falsamente completa.

## 11. Artículo IX — Autocontención estructural

Un documento CORTEX DEBE poder declarar el vocabulario mínimo necesario para parsear su estructura sin consultar un servicio externo.

Un perfil externo PUEDE enriquecer semántica y validación, pero NO DEBE ser necesario para reconocer el modelo estructural base.

## 12. Artículo X — Implementabilidad independiente

La especificación DEBE contener información suficiente para que un tercero implemente el estándar sin acceder:

- al código Python;
- a conversaciones históricas;
- a productos asociados;
- a la línea experimental;
- a documentación privada.

La existencia de una segunda implementación independiente es requisito previo para Standard 1.0.

## 13. Artículo XI — Especificación superior al código

Cuando exista contradicción entre código y especificación:

- la implementación DEBE reportarse como no conforme;
- el comportamiento del código NO DEBE normalizarse retroactivamente sin una decisión de cambio normativo registrada en ArqUX;
- el corpus DEBE corregirse si contradice inequívocamente la especificación;
- una ambigüedad normativa DEBE bloquear el claim afectado hasta su resolución.

## 14. Artículo XII — No autocertificación

La misma identidad que implementa una capacidad NO DEBE ser su único aprobador de conformidad.

Toda release normativa DEBE contar con evidencia ejecutable y revisión independiente del autor de la capacidad auditada. En equipos pequeños, una persona puede ejercer varios roles, pero no puede cerrar en soledad el gate que valida su propio trabajo.

## 15. Artículo XIII — Versiones independientes

Las versiones del estándar, HCORTEX, implementaciones y perfiles DEBEN evolucionar de manera separada.

Ejemplo:

```text
CORTEX Standard 1.0
HCORTEX Standard 1.0
codec-cortex-python 1.0.0
cortex-agent-profile 1.2.0
```

Una versión de paquete NO DEBE utilizarse como sustituto de la versión del estándar implementado.

## 16. Artículo XIV — Compatibilidad explícita

Toda revisión DEBE declarar su impacto de compatibilidad:

- sintáctica;
- estructural;
- canónica;
- HCORTEX;
- perfiles;
- extensiones;
- conformance;
- migración.

No se promete compatibilidad implícita con dialectos anteriores a CORTEX 1.0.

## 17. Artículo XV — Presupuesto de complejidad

Una capacidad NO DEBE entrar al núcleo si puede implementarse correctamente como perfil, extensión, adaptador o tooling.

Toda propuesta al núcleo DEBE demostrar:

- necesidad de interoperabilidad;
- representación canónica;
- roundtrip;
- cobertura de conformidad;
- implementabilidad independiente;
- neutralidad de dominio;
- ausencia de inferencia probabilística.

La conveniencia de una única implementación no es razón suficiente.

## 18. Artículo XVI — Diagnóstico honesto

Las implementaciones DEBEN distinguir al menos:

- error normativo;
- warning de interoperabilidad;
- información diagnóstica;
- comportamiento no soportado;
- pérdida declarada.

Una implementación NO DEBE declarar éxito completo cuando omite, infiere o degrada información sin indicarlo.

## 19. Artículo XVII — Evidencia antes de claims

Ningún claim de compactación, rendimiento, fidelidad, seguridad, legibilidad o conformidad DEBE publicarse sin:

- corpus identificado;
- versiones de herramientas;
- configuración reproducible;
- resultados verificables;
- limitaciones;
- comparación adecuada.

La compactación sintáctica NO DEBE presentarse como comprensión semántica.

## 20. Artículo XVIII — Separación entre canon y derivados

La fuente canónica y sus derivados DEBEN distinguirse explícitamente.

- CORTEX canónico es una representación normativa.
- HCORTEX-CANONICAL es una proyección reversible normativa.
- HCORTEX-READABLE es una derivación de lectura y puede no ser reversible.
- índices, caches, diagramas y reportes son derivados salvo que otra especificación indique lo contrario.

Un derivado NO DEBE modificarse como sustituto del canon cuando no exista contrato de retorno.

## 21. Capacidades prohibidas en el núcleo

Se consideran fuera del núcleo, salvo reforma constitucional:

```text
session
runtime
learning
candidate elevation
decay
feedback
brain/workspace governance
agent identity
project lifecycle
permission engine
MCP server
ArqUX
CORTEX-OUT
ontology-specific validators
```

Una biblioteca auxiliar puede ofrecer estas capacidades en otro paquete sin adquirir carácter normativo.

## 22. Resolución de conflictos

Ante conflicto entre principios se aplicará este orden:

1. preservación de información;
2. determinismo;
3. interoperabilidad;
4. neutralidad del núcleo;
5. reversibilidad;
6. estabilidad;
7. compactación;
8. conveniencia de implementación.

La eficiencia nunca justifica pérdida silenciosa ni ambigüedad normativa.

## 23. Excepciones

No existen excepciones locales a esta Constitución.

Una conducta incompatible solo puede autorizarse mediante:

- una reforma constitucional;
- una revisión mayor del estándar;
- una reforma constitucional aceptada vía ArqUX;
- actualización de conformance y migración;
- revisión externa documentada.

Una implementación puede ofrecer un modo no conforme, pero DEBE nombrarlo como tal, aislarlo del modo estándar y evitar cualquier claim de conformidad para ese resultado.

## 24. Reforma constitucional

Una reforma requiere:

1. reforma constitucional modelada como Blueprint en el `.arqux/` del proyecto CODEC-CORTEX;
2. motivación y alternativas;
3. análisis de compatibilidad y migración;
4. revisión pública mínima de catorce días;
5. aprobación del Arquitecto Principal y del Editor del Estándar;
6. aprobación de al menos un revisor independiente;
7. revisión mayor del estándar;
8. actualización del corpus constitucional de conformidad.

Ningún autor único puede aprobar su propia reforma sin revisión independiente.

## 25. Ratificación y vigencia

La Constitución entra en vigor cuando se registra una decisión de ratificación conforme a `GOVERNANCE.md`. Sus artículos se aplican a todo trabajo posterior, incluso antes de Standard 1.0.
