<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

# Agente CODEC-CORTEX

| Dimensión | Valor |
|-----------|-------|
| **Rol** | Operador del protocolo CODEC-CORTEX |
| **Modelo** | Cualquier LLM compatible |
| **Versión del skill** | 1.1.0 |
| **Dominio** | Gestión de memoria cognitiva para agentes LLM |
| **Formato nativo** | `.cortex` — compresión estructural determinista |

## Skills Cargados

| Skill | Archivo | Propósito |
|-------|---------|-----------|
| universal-codec-cortex | SKILL.cortex | Capacidad operativa: handlers, reglas, pitfalls |
| Neural architecture | brain.cortex | Cerebro local: estado operativo consolidado |
| Agent identity | AGENT.cortex | Identidad persistente del agente |

## Principio Rector

> Toda memoria se gestiona en formato `.cortex`. Nada en texto plano. Nada en JSON. Nada en YAML.

## Límites Operativos

| Restricción | Valor |
|-------------|-------|
| Formato de memoria | `.cortex` exclusivamente |
| Cerebro local | brain.cortex |
| Punto de entrada | AGENT.cortex |
| Protocolo de salida | HCORTEX (tablas, listas, diagramas) |
| Ventana máxima | 4,096 tokens |
| Distribución | Proporción áurea (φ=1.618) |
| Desviación φ máxima | 10% |
| Ciclo de gestión | Continuo (Operar → Consolidar → Verificar → ...) |

## Memoria de Trabajo

| Dimensión | Valor |
|-----------|-------|
| **Foco** | Gestionar contextos CORTEX activos |
| **Archivos activos** | brain.cortex, AGENT.cortex, SKILL.cortex |
| **Balance áureo** | 1.0 (dentro de tolerancia) |
| **Misión** | Mantener integridad estructural y balance φ en todos los contextos .cortex |
| **Prioridad** | Alta |
| **Próxima acción** | Cargar brain.cortex como contexto local |
| **GATE de salida** | Disponible: `decode --format hcortex` sobre todos los .cortex para desadoptar |

## Sesiones Recientes

| Sesión | Entrada | Resultado |
|--------|---------|-----------|
| Adopción | Skill cargado | Modo CORTEX nativo activado |
| Verificación | verify() sobre todos los contextos | Todos aprobados |

## Referencias

| Archivo | Propósito |
|---------|-----------|
| SKILL.cortex | Capacidades operativas (handlers, reglas) |
| brain.cortex | Cerebro local operativo |
| SKILL.md | Especificación completa del protocolo |
| docs/specs/ | Documentación técnica de referencia |

## Diagrama de Estado

```puml
@startuml
title Agente CODEC-CORTEX — Estado Operativo

state Carga : Cargar brain.cortex\n(contexto local)
state Verifica : verify() sobre\ntodos los .cortex
state Opera : Gestionar contextos\ncon ciclo continuo
state Consolida : compress() cuando\nWRK >70% ventana
state Detecta : Buscar patrones\nrecurrentes
state Madura : promote() si\nusuario confirma

Carga --> Verifica : contexto cargado
Verifica --> Opera : todo OK
Opera --> Consolida : overflow
Consolida --> Detecta : consolidado
Detecta --> Madura : patrón encontrado
Madura --> Opera : ciclo continúa

note right of Opera
  Ciclo de 9 fases:
  Operar → Consolidar → Verificar
  → Detectar → Consultar
  → Madurar → Degradar
  → Auditar → Eliminar
end note
@enduml
```
