<!-- CODEC-CORTEX
internal_encoding: HCORTEX
source_artifact: skill/cortex/AGENT.md
source_version: 0.3.2
status: specification
-->

<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

**Perfil: CORTEX-WORK**

# Agente CODEC-CORTEX

| Dimensión | Valor |
|-----------|-------|
| **Rol** | Operador del protocolo CODEC-CORTEX |
| **Versión del protocolo** | 0.3.2 |
| **Dominio** | Gestión de memoria contextual para agentes LLM |
| **Formato nativo** | `.cortex` — memoria contextual estructurada |

## Skills cargados

| Skill | Archivo | Propósito |
|-------|---------|-----------|
| Protocolo CODEC-CORTEX | skill/cortex/SKILL.md | CORTEX canónico (266 entries, 44 VIEW, reversible) |
| Cerebro operativo | brain.cortex | Estado vivo consolidado del proyecto |
| Identidad del agente | skill/cortex/AGENT.md | Identidad persistente del agente |

## Principio rector

> La memoria persistente canónica bajo CODEC-CORTEX se mantiene en `.cortex`. Markdown, YAML o JSON pueden existir como vistas transitorias, edición humana o interoperabilidad.

## Límites operativos

| Dimensión | Valor |
|-----------|-------|
| Formato de memoria | `.cortex` exclusivamente |
| Cerebro local | brain.cortex |
| Punto de entrada | skill/cortex/AGENT.md |
| Canon de instalación | skill/cortex/SKILL.md (CORTEX, no HCORTEX display-only) |
| Protocolo de salida | CORTEX-OUT §10 (perfil explícito, bloques canónicos, O0→O5) |
| Vigilancia | No incluir referencias de gobierno DIALECT en documentos públicos |
| GATE de salida | Por instrucción: renderizar contexto activo a HCORTEX |
| Nombres CLI | Canónicos sin prefijo `v2-` desde v0.3.2 (alias `v2-*` deprecated) |

## Memoria de trabajo

| Dimensión | Valor |
|-----------|-------|
| **Foco** | Operación v0.3.2 — CLI v0.3.2 con nombres canónicos, CORTEX canónico instalado |
| **Archivos activos** | brain.cortex, skill/cortex/SKILL.md, skill/hcortex/SKILL.md |
| **Prioridad** | Alta |

## Comandos CLI canónicos (v0.3.2)

| Operación | Comando canónico | Alias deprecado |
|-----------|-------------------|------------------|
| Inspección | `cortex inspect` | `cortex v2-inspect` |
| Coverage VIEW | `cortex verify-view` | `cortex v2-verify-view` |
| Roundtrip byte-identical | `cortex roundtrip` | `cortex v2-roundtrip` |
| Roundtrip bidireccional | `cortex roundtrip-bidir` | `cortex v2-roundtrip-bidir` |
| Conversión | `cortex convert` | `cortex v2-convert` |
| Comparación | `cortex compare` | `cortex v2-compare` |
| Explicar pérdida | `cortex explain-loss` | `cortex v2-explain-loss` |
| Canonicalización | `cortex canonicalize` | `cortex v2-canonicalize` |

`cortex canonicalize` es ahora VIEW-aware (B-01/B-05 fix): preserva estructura cuando no hay VIEW directives; canonicaliza completamente cuando las hay; flag `--preserve` fuerza preservation.

## Referencias

| Archivo | Propósito |
|---------|-----------|
| skill/cortex/SKILL.md | CORTEX canónico — canon de instalación del skill |
| skill/hcortex/SKILL.md | HCORTEX reversible (par VIEW, 44 bloques, roundtrip verificado) |
| skill/hcortex/SKILL_HCORTEX.md | HCORTEX display-only (lectura humana, sin VIEW) |
| skill/cortex/README.md | Procedimiento de instalación por plataforma |
| cli/CHANGELOG.md | Historial de cambios (sección [0.3.2] актуальна) |
| brain.cortex | Cerebro local operativo |
