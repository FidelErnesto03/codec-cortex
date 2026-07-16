# CORTEX Core Charter — Fase 0

**Document ID:** `CCX-CHARTER-0001`  
**Status:** `approved-for-bootstrap`  
**Approved by:** Arquitecto principal  
**Date:** `2026-07-16`

## 1. Propósito

CORTEX será un estándar abierto, determinista y autocontenido para representar contexto estructurado destinado a SLM/LLM y sistemas que intercambian contexto.

CODEC-CORTEX será exclusivamente la implementación de referencia de las operaciones normativas del estándar:

```text
parse
write
canonicalize
validate
to_hcortex
from_hcortex
compare
explain_loss
```

## 2. Alcance del núcleo

El núcleo podrá contener únicamente capacidades necesarias para:

- modelo abstracto y AST;
- sintaxis y gramática;
- parseo y serialización;
- canonicalización y equivalencia;
- validación estructural;
- namespaces y extensiones;
- transformación HCORTEX canónica;
- diagnósticos;
- corpus y runner de conformidad;
- API y CLI mínimas de estas funciones.

## 3. Exclusiones obligatorias

No pertenecen al núcleo:

- runtime de agentes;
- sesiones o workspaces;
- aprendizaje, scoring, decay o elevation;
- memoria autónoma;
- gobierno de proyectos;
- permisos o aprobaciones;
- ArqUX;
- MCP/ACP/LSP como servidores;
- CRUD editorial avanzado;
- firma y supply-chain tooling;
- perfiles Agent, Skill, Handoff o Project State;
- vocabularios como `FCS`, `OBJ`, `WRK`, `SES`, `LNG` o `KNW`.

Pueden existir en repositorios externos que consuman el estándar.

## 4. Principios vinculantes

1. La especificación tiene autoridad superior al código.
2. El formato no gobierna al consumidor.
3. La gramática no incorpora una ontología obligatoria.
4. El núcleo no importa perfiles, runtime, learning ni ArqUX.
5. No existe pérdida silenciosa.
6. La canonicalización es idempotente.
7. HCORTEX canónico es una proyección reversible del AST.
8. Ninguna capacidad depende de inferencia probabilística.
9. Una implementación independiente debe ser posible usando solo la especificación.
10. La misma identidad que implementa no será la única que certifica.

## 5. Presupuesto de complejidad

Una feature solo puede entrar al núcleo si:

- es necesaria para interoperabilidad;
- no puede resolverse como perfil o extensión;
- posee representación canónica;
- posee roundtrip HCORTEX;
- tiene casos de conformidad;
- puede ser implementada por un tercero;
- no introduce dominio específico;
- no introduce inferencia LLM.

Una respuesta negativa mantiene la feature fuera del núcleo.

## 6. Autoridades separadas

```text
CORTEX Standard       -> cortex-standard
HCORTEX Standard      -> cortex-standard
Reference Python      -> codec-cortex
Official Profiles     -> cortex-profiles
Learning              -> cortex-learning
Runtime               -> cortex-runtime
Project Governance    -> arqux
```

## 7. Criterio de aceptación de material heredado

Cada componente requiere:

- origen exacto;
- responsabilidad real;
- dependencias;
- acoplamiento de dominio;
- riesgo;
- cobertura;
- decisión `reuse`, `rewrite` o `reject`;
- evidencia verificable.

No se copiarán paquetes completos.
