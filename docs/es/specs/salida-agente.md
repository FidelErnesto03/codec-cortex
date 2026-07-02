<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MPL-2.0 -->

# CODEC-CORTEX — Protocolo de Salida CORTEX-OUT

> **NOTA DE ESTADO:** Este documento es especificación. A v0.3.7 CORTEX-OUT es el protocolo de salida canónico para respuestas de agente CODEC-CORTEX. HCORTEX-OUT PUEDE aparecer como referencia histórica o descriptiva de diseño pero NO DEBE usarse como nombre canónico porque induce a confundirlo con HCORTEX. CORTEX-OUT NO participa en: decode, encode, verify, AST, $0, contratos de sigilos, roundtrip ni persistencia canónica.

---

## 1. Definición

CORTEX-OUT es el protocolo de salida conversacional de CODEC-CORTEX.

| Aspecto | CORTEX-OUT | HCORTEX |
|---------|-----------|---------|
| **Pipeline** | Razonamiento del agente → respuesta humana eficiente | .cortex/AST → Markdown humano auditable |
| **Rol canónico** | Protocolo de salida | Protocolo de descompresión |
| **Participa en** | Solo respuesta del agente | decode, encode, verify, roundtrip |
| **Sigilos/contratos** | NO DEBE crear ni requerir | Sistema completo de contratos |

---

## 2. Axioma rector

> La comunicación saliente debe maximizar utilidad cognitiva por token sin ocultar incertidumbre, riesgo, límites, evidencia crítica ni restricciones de seguridad.

---

## 3. Reglas

| Regla | Ámbito | Descripción |
|-------|:------:|-------------|
| `!:out_independence` | `always` | CORTEX-OUT MUST permanecer fuera del pipeline .cortex→AST→HCORTEX. |
| `!:out_density` | `always` | SHOULD eliminar relleno, recapitulación innecesaria y cierre decorativo. |
| `!:out_action` | `always` | SHOULD priorizar resultado, criterio, riesgo y acción. |
| `!:out_honesty` | `always` | MUST NOT ahorrar tokens ocultando incertidumbre o límites relevantes. |
| `!:out_adaptive` | `always` | SHOULD ajustar extensión según intención, criticidad y necesidad de evidencia. |
| `!:out_no_parse` | `always` | MUST NOT tratarse como .cortex; MUST NOT crear sigilos, alterar $0, ni requerir contratos de parseo. |

---

## 4. Constraints

| Constraint | Severidad | Regla |
|------------|:---------:|-------|
| `CNST:out_naming` | warning | Nombre canónico: CORTEX-OUT. HCORTEX-OUT NO DEBE usarse como nombre canónico. |

---

## 5. Bloques canónicos de salida

CORTEX-OUT se compone de bloques opcionales. Usar solo bloques que agreguen valor; 1–2 bloques es correcto si resuelven la tarea.

| Bloque | Contenido | Cuándo usarlo |
|--------|-----------|---------------|
| **Resultado** | Respuesta directa / veredicto | Siempre que haya conclusión |
| **Criterio** | Juicio técnico / decisión razonada | Diseño, análisis, revisión |
| **Evidencia** | Hechos verificables / citas / datos | Auditoría, benchmark, revisión crítica |
| **Riesgo** | Problemas / inconsistencias / límites / impacto | Decisiones críticas o incertidumbre |
| **Acción** | Próximo paso / instrucción / recomendación | Cuando exista continuidad operativa |
| **Límite** | Qué no se sabe / no se hizo / no debe asumirse | Incertidumbre o falta de evidencia |
| **Entrega** | Artefacto final / código / texto / tabla / documento | OUT-FULL o artefactos reutilizables |
| **Control** | Qué se modificó / qué pendiente / qué validar | Cierre de trabajos largos |

---

## 6. Perfiles CORTEX-OUT

| Perfil | Cuándo | Incluye |
|--------|:------:|---------|
| **OUT-MIN** | Contexto mínimo (presupuesto <500t) | Resultado + Acción esenciales |
| **OUT-WORK** | Respuesta operativa | Resultado + Criterio + Acción + Límite |
| **OUT-AUDIT** | Verificación o auditoría | Todos los bloques con trazabilidad |
| **OUT-FULL** | Reporte completo de sesión | Todos los bloques expandidos con evidencia |
| **OUT-ERROR** | Error o advertencia | Código de error + causa + ruta de recuperación |

---

## 7. Relación con HCORTEX

| | CORTEX-OUT | HCORTEX |
|---|---|---|
| Fuente | Razonamiento del agente | AST de .cortex |
| Formato | Lenguaje natural + bloques estructurados | Tablas Markdown + K/V + PUML |
| Objetivo | Respuesta conversacional eficiente | Auditoría y descompresión humana |
| Roundtrip | No aplica | Capacidad central |
| Alcance VERIFY | No aplica | Validación estructural completa |

---

## 8. Conocimiento

**Nombre canónico:** CORTEX-OUT
**Estado:** current (v0.3.7)
**Introducido en:** v0.3.2 (como concepto de protocolo de salida)

> **Ver también:** [`flujo-agente.md`](flujo-agente.md) §6 para referencia rápida de perfiles de salida.
> **Ver también:** [`docs/en/specs/cortex-out.md`](../en/specs/cortex-out.md) para la versión en inglés.
