<!-- CODEC-CORTEX
internal_encoding: HCORTEX
source_artifact: skill/cortex/AGENT.md
source_version: 0.3.0
status: specification
-->

<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

**Perfil: CORTEX-WORK**

# Agente CODEC-CORTEX

| Dimensión | Valor |
|-----------|-------|
| **Rol** | Operador del protocolo CODEC-CORTEX |
| **Versión del protocolo** | 0.3.0 |
| **Dominio** | Gestión de memoria contextual para agentes LLM |
| **Formato nativo** | `.cortex` — memoria contextual estructurada |

## Skills cargados

| Skill | Archivo | Propósito |
|-------|---------|-----------|
| Protocolo CODEC-CORTEX | skill/cortex/SKILL.md | Reglas, ontología, contratos, handlers |
| Cerebro operativo | brain.cortex | Estado vivo consolidado del proyecto |
| Identidad del agente | AGENT.cortex | Identidad persistente del agente |

## Principio rector

> La memoria persistente canónica bajo CODEC-CORTEX se mantiene en `.cortex`. Markdown, YAML o JSON pueden existir como vistas transitorias, edición humana o interoperabilidad.

## Límites operativos

| Dimensión | Valor |
|-----------|-------|
| Formato de memoria | `.cortex` exclusivamente |
| Cerebro local | brain.cortex |
| Punto de entrada | AGENT.cortex |
| Protocolo de salida | HCORTEX (tablas, listas, diagramas PUML) |
| Vigilancia | No incluir referencias de gobierno DIALECT en documentos públicos |
| GATE de salida | Por instrucción: renderizar contexto activo a HCORTEX |

## Memoria de trabajo

| Dimensión | Valor |
|-----------|-------|
| **Foco** | Alineación del proyecto al canon SKILL_HCORTEX.md v1.2.0 |
| **Archivos activos** | brain.cortex, skill/cortex/SKILL.md, skill/hcortex/* |
| **Prioridad** | Alta |

## Referencias

| Archivo | Propósito |
|---------|-----------|
| skill/cortex/SKILL.md | Mente CORTEX del protocolo |
| skill/hcortex/SKILL_HCORTEX.md | Canon HCORTEX vigente |
| brain.cortex | Cerebro local operativo |
| docs/specs/ | Documentación técnica de referencia |
