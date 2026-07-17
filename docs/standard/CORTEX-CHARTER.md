# CORTEX Charter

**Document ID:** `CORTEX-CHARTER-001`  
**Version:** `0.1.0-draft`  
**Status:** `draft-for-ratification`  
**Normative scope:** propósito, dominio, límites y mandato del estándar  
**Authority basis:** `CCX-CORE-PROJECT-PLAN-001`  
**Language:** español  
**Date:** `2026-07-16`

---

## 1. Declaración fundacional

CORTEX es un estándar abierto de representación de contexto estructurado para sistemas SLM/LLM. Su finalidad es definir una forma compacta, determinista, autocontenida, extensible y auditable de expresar contexto, junto con reglas que permitan interpretarlo, validarlo, canonicalizarlo y transformarlo de manera interoperable.

CODEC-CORTEX es una implementación de referencia del estándar. No es la definición del estándar ni su autoridad superior.

HCORTEX es la representación humana canónica del modelo estructural de CORTEX. Debe permitir inspección y edición controlada sin convertirse en una segunda fuente conceptual.

## 2. Problema que se busca resolver

Los formatos genéricos pueden representar datos, pero no resuelven por sí mismos las necesidades específicas del contexto para agentes:

- repetición estructural elevada;
- dificultad para declarar vocabularios locales compactos;
- identidad inestable de unidades contextuales;
- ausencia de una forma humana reversible común;
- pérdida silenciosa durante transformaciones;
- baja portabilidad entre herramientas, agentes y runtimes;
- dependencia accidental de ontologías o productos particulares.

CORTEX busca resolver este problema en el nivel de representación. No pretende resolver el comportamiento del consumidor.

## 3. Misión

La misión del proyecto es producir y mantener:

1. una especificación normativa de CORTEX;
2. una especificación normativa de HCORTEX;
3. reglas inequívocas de canonicalización y equivalencia;
4. un modelo de vocabularios, perfiles, namespaces y extensiones;
5. una suite pública de conformidad;
6. una implementación de referencia independiente de inferencia probabilística;
7. evidencia reproducible de interoperabilidad, fidelidad y eficiencia.

## 4. Dominio de aplicación

CORTEX está orientado a representar, entre otros casos:

- contexto operativo de agentes;
- conocimiento estructurado;
- instrucciones, restricciones y políticas declarativas;
- paquetes de handoff;
- resultados estructurados de herramientas;
- estados de proyectos cuando un perfil externo los defina;
- skills y capacidades cuando un perfil externo los defina;
- comunicación estructurada entre agentes, herramientas y servicios;
- memoria contextual cuando un sistema externo decida utilizarlo con ese fin.

La inclusión de un caso en este dominio no convierte su semántica en parte del núcleo.

## 5. Propiedades obligatorias del estándar

El estándar deberá ser:

- **determinista:** misma entrada, misma versión y mismas opciones normativas producen el mismo resultado estructural;
- **autocontenido:** un documento puede declarar el vocabulario mínimo necesario para parsear e interpretar su estructura;
- **extensible:** perfiles y extensiones pueden agregar semántica sin modificar la gramática base;
- **neutral:** no obliga a adoptar una arquitectura de agentes, memoria, gobierno o aprendizaje;
- **reversible:** la forma HCORTEX canónica conserva el modelo estructural definido por CORTEX;
- **auditable:** toda transformación destructiva o no reversible se declara y reporta;
- **interoperable:** implementaciones independientes pueden reproducir los mismos resultados normativos;
- **pequeño:** el núcleo contiene solo capacidades necesarias para interoperabilidad;
- **estable:** los cambios incompatibles requieren revisión mayor;
- **independiente de LLM:** parsing, validación, canonicalización y conversión no requieren inferencia probabilística.

## 6. Alcance normativo

El estándar podrá normar únicamente materias necesarias para representar y transformar el modelo estructural, incluyendo:

- modelo abstracto del documento;
- sintaxis y gramática;
- tipos estructurales mínimos;
- identidad y direccionamiento;
- vocabularios locales;
- namespaces;
- extensiones;
- reglas de texto y Unicode;
- diagnostics obligatorios;
- canonicalización;
- equivalencia;
- transformación CORTEX ↔ HCORTEX;
- requisitos de conformidad.

## 7. Non-goals

El núcleo de CORTEX y CODEC-CORTEX no implementará ni gobernará:

- runtimes de agentes;
- sesiones o workspaces operativos;
- memoria autónoma;
- aprendizaje, scoring, elevación, decay o feedback;
- políticas de promoción de conocimiento;
- identidad o personalidad de agentes;
- orquestación;
- permisos, roles o aprobación de acciones;
- gobierno de proyectos;
- ArqUX;
- MCP, ACP, LSP u otros servidores de integración;
- bases de datos cognitivas;
- motores de consulta o edición colaborativa;
- firmas, auditoría operativa o supply chain como semántica del formato;
- ontologías obligatorias de agentes;
- protocolos conversacionales como `CORTEX-OUT`.

Estas capacidades pueden existir como proyectos, perfiles, extensiones, adaptadores o tooling externos que consumen el estándar.

## 8. Frontera del ecosistema

La arquitectura de dependencia deberá mantener la siguiente dirección:

```text
cortex-standard
      ↓
codec-cortex
      ↓
profiles / extensions / adapters / tools
      ↓
runtime / learning / ArqUX / products
```

Quedan prohibidas las dependencias inversas desde el núcleo hacia productos o perfiles.

Repositorios previstos:

- `cortex-standard`: autoridad normativa;
- `codec-cortex`: implementación de referencia;
- `cortex-profiles`: perfiles oficiales opcionales;
- `cortex-learning`: transformaciones semánticas externas;
- `cortex-runtime`: estado y operación externa;
- `arqux`: gobierno de proyectos y agentes;
- `codec-cortex-lab`: archivo histórico experimental;
- `cortex-legacy-import`: puente de migración no normativo.

## 9. Público objetivo

El estándar se dirige a:

- implementadores de parsers y codecs;
- diseñadores de agentes y runtimes;
- desarrolladores de tooling de contexto;
- investigadores de representación y eficiencia de contexto;
- arquitectos que requieran portabilidad y auditoría;
- autores de perfiles y extensiones;
- operadores que necesiten inspección humana mediante HCORTEX.

## 10. Relación entre estándar e implementación

La jerarquía de autoridad es:

1. especificación normativa versionada;
2. corpus y vectores de conformidad;
3. decisiones de cambio normativo ratificadas (registradas en ArqUX);
4. implementación de referencia.

Cuando el código y la especificación difieran, el código es defectuoso hasta que una revisión normativa determine lo contrario.

## 11. Compatibilidad con líneas experimentales

Las líneas `v0.3.x`, `v0.5.x` y `v0.6.x` se consideran experimentales y no definen el estándar 1.0.

El proyecto no promete compatibilidad byte a byte ni conservación automática de toda semántica heredada. La estrategia de compatibilidad será:

- detectar el dialecto legado;
- preservar el original;
- convertir mediante un bridge externo;
- emitir mapping report;
- declarar construcciones inferidas, descartadas o no resueltas;
- requerir revisión humana cuando la transformación no sea inequívoca.

Los conceptos heredados como `brain`, `session`, `learning`, `FCS`, `OBJ`, `WRK`, `VIEW` programable o `CORTEX-OUT` no se incorporan al núcleo por antecedente histórico. Solo podrán reaparecer mediante el proceso formal de cambio operado en ArqUX (Blueprint del proyecto CODEC-CORTEX) y dentro de la frontera correcta.

## 12. Criterio de inclusión en el núcleo

Una capacidad solo podrá incorporarse al núcleo cuando todas las respuestas sean afirmativas:

1. ¿Es necesaria para interoperabilidad?
2. ¿No puede resolverse como perfil?
3. ¿No puede resolverse como extensión?
4. ¿Tiene representación canónica?
5. ¿Tiene transformación HCORTEX definida?
6. ¿Tiene roundtrip verificable?
7. ¿Puede implementarla un tercero desde la especificación?
8. ¿Posee casos de conformidad?
9. ¿Evita inferencia probabilística?
10. ¿Es independiente de un dominio particular?

Una respuesta negativa obliga a mantener la capacidad fuera del núcleo.

## 13. Indicadores de éxito

El charter se considera cumplido cuando:

- dos implementaciones independientes producen el mismo AST lógico y bytes canónicos;
- la canonicalización es idempotente en el corpus completo;
- HCORTEX canónico alcanza roundtrip estructural completo;
- no existen pérdidas silenciosas;
- eliminar perfiles, runtime, learning o ArqUX no altera los tests del núcleo;
- un implementador externo puede construir un parser sin conocer el historial del proyecto;
- las ventajas de tamaño, tokens o rendimiento se publican con corpus neutral y limitaciones;
- existen consumidores externos no vinculados al proyecto original.

## 14. Condiciones de fracaso

El proyecto debe detener o revisar su dirección si:

- el estándar requiere conocimiento histórico para implementarse;
- el núcleo importa perfiles o productos;
- HCORTEX necesita reglas específicas por ontología para ser reversible;
- la canonicalización depende de una implementación particular;
- una transformación pierde información sin reporte;
- los claims de eficiencia no son reproducibles;
- la especificación se adapta retroactivamente para justificar el código existente;
- no puede construirse una segunda implementación equivalente.

## 15. Gate de comprensión externa

La Fase 1 supera su gate cuando un revisor ajeno al código puede responder correctamente, usando solo estos documentos:

- qué es CORTEX;
- qué es CODEC-CORTEX;
- qué es HCORTEX;
- qué pertenece al núcleo;
- qué está expresamente excluido;
- quién puede cambiar el estándar;
- cómo se tramita un cambio;
- qué compatibilidad se promete;
- cuál es la autoridad normativa.

## 16. Ratificación

Este charter entra en vigor cuando sea ratificado conforme a `GOVERNANCE.md`. Hasta entonces su estado es `draft-for-ratification` y no autoriza claims de conformidad o estandarización 1.0.
