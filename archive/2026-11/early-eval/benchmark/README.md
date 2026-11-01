# Benchmark de Estrés — CORTEX vs Formatos de Contexto Estructurado

**Versión:** 1.0 — 2026-07-17
**Archivo:** `benchmark.cortex`
**Prompt:** `compara`

---

## Hipótesis

> CORTEX 0.1 es más eficiente que JSON, YAML, Markdown, texto plano y XML como formato de contexto estructurado para LLMs, medido en precisión de recuperación, tokens consumidos y resistencia a preguntas multi-hop de alta complejidad.

## Diseño

### Datos

**40 items idénticos** sobre NexusCorp, una empresa de infraestructura cloud:

| Categoría | Items |
|---|---|
| Equipo | 8 miembros con roles, proyectos, seniority |
| Proyectos | 5 proyectos con deadlines, presupuestos, criticidad |
| Dependencias | 7 dependencias entre proyectos |
| Riesgos | 6 riesgos con impacto, probabilidad, mitigación |
| Decisiones | 5 decisiones de arquitectura con trazabilidad |
| Incidentes | 4 incidentes con severidad y estado |
| Proveedores | 5 proveedores con costos y proyectos asociados |

### Formatos

Los mismos 40 items en 6 formatos:

| # | Formato | Densidad esperada |
|---|---|---|
| 1 | CORTEX 0.1 | Alta — sigilos + attrs |
| 2 | JSON | Alta — anidado |
| 3 | YAML | Alta — indentación |
| 4 | Markdown Tables | Media — visual |
| 5 | Plain Text | Baja — narrativo |
| 6 | XML | Baja — verbosidad de tags |

### Preguntas

8 preguntas de dificultad creciente:

| # | Tipo | Secciones requeridas |
|---|---|---|
| Q1 | Simple | 1 sección |
| Q2 | Multi-sección | 2 secciones |
| Q3 | Multi-hop | 3 secciones |
| Q4 | Agregación | 2 secciones |
| Q5 | Multi-hop profundo | 3 secciones |
| Q6 | Causal | 3 secciones |
| Q7 | Transversal | 4 secciones |
| Q8 | Síntesis | 5 secciones (todas) |

## Método

1. Adjuntar `benchmark.cortex`
2. Escribir solo: `compara`
3. El modelo responde 48 veces (8 preguntas × 6 formatos)
4. Para cada respuesta anota: precisión, tokens estimados, dificultad percibida
5. Emite reporte comparativo al final

## Métricas

| Métrica | Qué mide |
|---|---|
| **Precisión por formato** | % de respuestas correctas |
| **Tokens estimados** | Cuánto contexto inspeccionó para responder |
| **Eficiencia multi-hop** | Precisión en Q5-Q8 vs Q1-Q4 |
| **Formato ganador** | Mejor balance precisión/tokens |
| **Densidad** | Información recuperable / tokens del formato |

## Interpretación

| Resultado | Significado |
|---|---|
| CORTEX lidera en ≥4/8 preguntas | CORTEX es el formato óptimo para contexto estructurado |
| CORTEX = JSON/YAML | CORTEX no ofrece ventaja sobre formatos existentes |
| CORTEX < texto plano | La estructura no ayuda — los LLMs prefieren narrativa |
| Ningún formato destaca | La elección de formato es irrelevante |

## Archivos

```
tests/benchmark/
├── README.md              ← Este protocolo
├── benchmark.cortex        ← Archivo de prueba (1237 líneas, 40KB)
├── benchmark-data.md       ← Datos en 6 formatos (referencia)
└── results/                ← Resultados de ejecución
```

## Ejecución

```bash
# Por plataforma:
# 1. Adjuntar benchmark.cortex
# 2. Escribir: compara
# 3. Guardar respuesta en results/<plataforma>.md
```
