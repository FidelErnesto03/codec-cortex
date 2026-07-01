# Documentación de CODEC-CORTEX

CODEC-CORTEX es un protocolo de memoria contextual para agentes LLM/SLM. Esta documentación está organizada por audiencia, formato y uso operativo.

## Mapa de audiencias

| Audiencia | Entrada recomendada | Formato | Propósito |
|---|---|---|---|
| Usuario nuevo | [Tutoriales ES](es/hcortex/tutorials/) · [Tutorials EN](en/hcortex/tutorials/) | HCORTEX | Aprender instalación, ejecución básica y flujo seguro |
| Operador del CLI | [Referencia API](cortex/api/) | CORTEX | Consultar comandos, argumentos, garantías y límites |
| Contribuidor | [Guías how-to ES](es/hcortex/how-to/) · [How-to guides EN](en/hcortex/how-to/) | HCORTEX | Aplicar tareas concretas sin duplicar criterio |
| Arquitecto o agente | [Specs EN](en/specs/) · [Specs ES](es/specs/) | CORTEX / MD | Mantener reglas autocontenidas y verificables |

## Formatos

| Formato | Audiencia | Regla |
|---|---|---|
| Markdown estándar | Entrada pública | No requiere conocer CODEC-CORTEX |
| HCORTEX | Humanos | Vista densa, tabular, auditable y legible |
| CORTEX | Agentes y CLI | Fuente canónica estructurada, autocontenida y verificable |

## Cómo navegar

| Necesidad | Ruta |
|---|---|
| Instalar y ejecutar por primera vez | `docs/es/hcortex/tutorials/primeros-pasos.md` (ES) · `docs/en/hcortex/tutorials/getting-started.md` (EN) |
| Entender la filosofía documental | `docs/es/hcortex/explanations/protocolo-documentacion.md` (ES) · `docs/en/hcortex/explanations/documentation-protocol.md` (EN) |
| Consultar un comando | `docs/cortex/api/<comando>.cortex` |
| Generar docstring de un comando | `cortex docstring <comando>` |
| Revisar suites benchmark disponibles | `cortex benchmark --list` |

## Cadena documental

```text
docs/cortex/api/*.cortex
        ├── cortex verify --strict
        ├── cortex docstring <comando>
        ├── docs/en/hcortex/reference/ (EN) · docs/es/hcortex/reference/ (ES)
        └── render HTML futuro
```

La referencia API se escribe una sola vez en CORTEX. Las vistas humanas, docstrings y validaciones deben derivarse desde esa fuente.
