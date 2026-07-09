<!-- SPDX-License-Identifier: MPL-2.0 -->
<!-- Copyright (c) 2026 Fidel Ernesto Lozada A. -->

# CODEC-CORTEX Learning Engine — Design Evolution

**Documento de diseño · v0.1.0 → v1.0.0 · 2026-07-02**
**Autor:** Alfred (agente CODEC-CORTEX) · **Revisión:** Fidel Ernesto Lozada A.

> Este documento describe cómo el motor de aprendizaje de CODEC-CORTEX debe evolucionar desde su estado actual (v0.1.0, scoring estático + CLI manual) hacia un runtime integrado en el ciclo de vida del agente. Cada funcionalidad se describe con su motivación, diseño detallado, flujo de uso ideal y visión MCP futura.

---

## Tabla de contenidos

1. [A. Ciclo de sesión (`cortex session`)](#a-ciclo-de-sesión-cortex-session)
2. [B. Auto-detección en handlers del agente](#b-auto-detección-en-handlers-del-agente)
3. [C. Decay y enfriamiento (cooling)](#c-decay-y-enfriamiento-cooling)
4. [D. Feedback loop](#d-feedback-loop)
5. [E. Thresholds configurables](#e-thresholds-configurables)
6. [F. Integración completa: cómo lo usaría Alfred](#f-integración-completa-cómo-lo-usaría-alfred)
7. [G. Visión MCP futura](#g-visión-mcp-futura)
8. [H. Plan de implementación por etapas](#h-plan-de-implementación-por-etapas)

---

## A. Ciclo de sesión (`cortex session`)

### A.1 Motivación

Hoy el motor opera sobre archivos estáticos: lee `brain.cortex`, calcula scores, propone candidatos. Pero no sabe **cuándo** empezó una sesión, **cuánto** ha durado, ni **qué** ha cambiado desde la última vez. Sin ciclo de sesión, el motor es un analizador post-mortem, no un compañero de trabajo.

### A.2 Diseño detallado

```
cortex session start   → Abre una sesión. Crea SES:current en brain.cortex.
                          Registra timestamp, hash inicial del brain.

cortex session status  → Muestra: sesión activa, duración, entradas modificadas,
                          candidatos detectados, scores actuales.

cortex session consolidate → Comprime la actividad de la sesión en SES:last.
                              Extrae LNG si hay patrones. Actualiza el índice.

cortex session close   → Cierra la sesión. Escribe SES:last consolidado.
                          Ejecuta decay sobre entradas no usadas.
                          Actualiza MANIFEST.cortex.
```

**Estructura de SES en brain.cortex:**

```cortex
SES:current{id:"2026-07-02-001",start:"2026-07-02T09:00:00Z",brain_hash:"sha256:abc...",
            entries_modified:0,candidates_detected:0,status:"running",survive:"min"}

SES:last{id:"2026-07-01-003",input:"Fidel: ajustar roadmap",output:"ROADMAP actualizado",
         outcome:"5 etapas unificadas",date:"2026-07-01",duration:"3h",score:5,survive:"recovery"}
```

### A.3 Flujo ideal

```text
Mañana, 09:00. Alfred inicia.
  │
  ├── agent_init detecta .cortex/ → activa CODEC-CORTEX
  ├── cortex session start → SES:current creada
  ├── [trabajo durante el día: pre_action/post_action]
  │     │
  │     ├── Cada interacción significativa → SES:current.entries_modified++
  │     ├── Cada patrón detectado → SES:current.candidates_detected++
  │     └── scores se actualizan en learn-index.json
  │
  └── 18:00. Fidel termina.
       │
       ├── cortex session consolidate
       │     ├── SES:current → SES:last con input/output/outcome
       │     ├── Si hubo 3+ modificaciones del mismo sigilo → LNG propuesto
       │     └── Decay: entradas no tocadas en 7+ días → promotion_score -= 1
       │
       └── cortex session close → brain.cortex actualizado, índice regenerado
```

---

## B. Auto-detección en handlers del agente

### B.1 Motivación

Hoy el usuario tiene que ejecutar `cortex learn scan` manualmente. El agente debería detectar patrones **sin que se lo pidan**, como parte natural de su ciclo de trabajo.

### B.2 Diseño detallado

El motor se integra en tres handlers del SKILL:

```text
HDL:agent_init (extendido)
  └── Después de cargar brain.cortex:
      ├── cortex session start (si .cortex/ existe)
      ├── cortex learn index rebuild --if-stale
      └── Cargar learn-policies.cortex en memoria

HDL:pre_action (extendido)
  └── Antes de cada acción:
      ├── detect_signals(entrada_usuario, brain.cortex)
      │     └── ¿Hay recurrencia de tema? → incrementar contador
      │     └── ¿Hay patrón conocido? → registrar similitud
      └── Si signals > threshold → marcar para post_action

HDL:post_action (NUEVO)
  └── Después de cada acción:
      ├── Si la acción modificó brain.cortex → actualizar scores
      ├── Si signals pendientes → evaluar candidatos
      └── Si hay candidatos con score ≥ 5 → notificar al usuario
```

### B.3 Flujo ideal

```text
Fidel: "Alfred, necesito que revises los benchmarks v2.2.2"
  │
  ├── pre_action: detect_signals()
  │     ├── Tema: "benchmarks" → visto 3 veces esta semana
  │     ├── Patrón: revisión de benchmarks es recurrente
  │     └── Signal: promotion_score += 2
  │
  ├── Alfred ejecuta la revisión...
  │
  └── post_action:
        ├── ¿Signals acumulados?
        │     └── "benchmarks" → score 5 → CANDIDATO
        └── Alfred: "He detectado que revisar benchmarks es un patrón
                    recurrente. ¿Quieres que lo registre como lección (LNG)?"
```

---

## C. Decay y enfriamiento (cooling)

### C.1 Motivación

Sin decay, todo lo que alguna vez fue relevante permanece relevante para siempre. El brain se infla. La señal se diluye en ruido.

### C.2 Diseño detallado

**Modelo de cooling exponencial:**

```python
def cooling_factor(days_since_last_access: int) -> float:
    """Factor de enfriamiento: 1.0 (hoy) → 0.13 (30 días)."""
    HALF_LIFE_DAYS = 7
    return 0.5 ** (days_since_last_access / HALF_LIFE_DAYS)

def apply_decay(entry, index, now):
    days = (now - entry.last_accessed).days
    factor = cooling_factor(days)
    index.promotion_score = int(index.promotion_score * factor)
    index.hotness_score = int(index.hotness_score * factor)
```

**Reglas de decay:**

| Score actual | Días sin acceso | Decay aplicado | Resultado |
|:-----------:|:--------------:|:--------------:|-----------|
| 8 (KNW candidate) | 14 | ×0.25 | 2 (vuelve a SES) |
| 5 (LNG) | 7 | ×0.50 | 2 (vuelve a SES) |
| 3 (LNG threshold) | 21 | ×0.125 | 0 (eliminado del índice) |
| 1 (SES) | 30 | ×0.05 | 0 (eliminado) |

**Protección contra decay:**

- Entradas con `survive:"min"` → **nunca decaen**
- Entradas con `survive:"recovery"` → decaen a la mitad de velocidad
- Entradas en `learn-policies.cortex` con `protected: true` → **nunca decaen**

### C.3 Flujo ideal

```text
session_close:
  │
  ├── Para cada entrada en learn-index.json:
  │     ├── Calcular días desde last_accessed
  │     ├── Aplicar cooling_factor
  │     ├── Si promotion_score < 1 → eliminar del índice
  │     └── Si promotion_score bajó de nivel → registrar en AUD
  │
  └── Reporte de decay:
        "3 entradas enfriadas. 1 eliminada (SES:old_decision, 45 días sin acceso).
         2 degradadas: LNG:python_tips (8→5), SES:meeting_notes (3→1)."
```

---

## D. Feedback loop

### D.1 Motivación

Hoy el motor propone candidatos. El usuario acepta o ignora. Pero el motor **no aprende** de esas decisiones. Si el usuario rechaza sistemáticamente cierto tipo de candidato, el motor debería ajustar sus thresholds para ese tipo.

### D.2 Diseño detallado

```text
cortex learn feedback --accept <candidate_id>
  └── El motor registra: "este tipo de candidato fue aceptado"
      └── Baja el threshold para candidatos similares en el futuro

cortex learn feedback --reject <candidate_id> --reason "one-time event"
  └── El motor registra: "este tipo de candidato fue rechazado"
      └── Sube el threshold para candidatos similares
      └── Si el usuario da razón → se almacena como LNG anti-patrón
```

**Modelo de feedback:**

```python
class FeedbackRecord:
    candidate_type: str      # "SES→LNG", "LNG→KNW", etc.
    sigil_pattern: str       # "KNW:benchmark_*"
    decision: bool           # True=accepted, False=rejected
    reason: Optional[str]    # "one-time event", "already known", "not relevant"
    timestamp: datetime

def adjust_thresholds(feedback_history: List[FeedbackRecord]) -> Thresholds:
    """Ajusta thresholds basados en historial de feedback."""
    for sigil_type in group_by_type(feedback_history):
        acceptance_rate = count_accepted / total
        if acceptance_rate > 0.8:
            # Usuario acepta casi todo → bajar threshold 10%
            thresholds[sigil_type] *= 0.9
        elif acceptance_rate < 0.3:
            # Usuario rechaza casi todo → subir threshold 20%
            thresholds[sigil_type] *= 1.2
```

### D.3 Flujo ideal

```text
Alfred: "Detecté 3 candidatos. ¿Revisamos?"

Fidel: "Sí, muéstralos."

Alfred: "Candidato 1: KNW:benchmark_review → promotion_score 8.
         Sugiero promover a LNG. ¿Aceptas?"

Fidel: "Sí, acepto."

Alfred: "✅ KNW:benchmark_review → LNG:benchmark_review_pattern.
         Feedback registrado. Threshold para KNW→LNG ajustado -10%."

---

Fidel: "Candidato 2: SES:quick_fix → promotion_score 5. ¿Aceptas?"

Fidel: "No, fue un evento único."

Alfred: "❌ Rechazado. Razón: one-time event.
         Feedback registrado. Threshold para SES→LNG en 'quick_fix' ajustado +20%.
         No volveré a sugerir este patrón."
```

---

## E. Thresholds configurables

### E.1 Motivación

Hoy los thresholds están hardcodeados (Fibonacci 1, 3, 5, 8, 13). Diferentes proyectos necesitan diferente sensibilidad. Un proyecto rápido quiere detectar patrones en 2 repeticiones. Un proyecto cauteloso quiere 5.

### E.2 Diseño detallado

**Archivo `learn-policies.cortex` extendido:**

```cortex
$1: THRESHOLDS

POL:fibonacci_thresholds{ses:1,lng:3,knw:8,auto_knw:13}
POL:cooling{half_life_days:7,min_score_to_survive:1}
POL:detection{same_sigil_in_window:3,window_hours:72,cross_session:true}
POL:feedback{adaptive:true,adjustment_rate:0.1,min_threshold:1,max_threshold:20}
POL:protected_patterns{patterns:"CNST:*,!:*,FCS:*,OBJ:*"}
```

**Comandos:**

```bash
cortex learn policy set fibonacci_thresholds --ses 2 --lng 5 --knw 10
cortex learn policy set cooling --half-life 14
cortex learn policy set detection --window 48h
cortex learn policy reset --defaults
```

### E.3 Perfiles predefinidos

```text
cortex learn policy profile --aggressive
  → SES:1, LNG:2, KNW:5, half_life:3d
  → "Detecta rápido, olvida rápido. Para proyectos ágiles."

cortex learn policy profile --conservative
  → SES:1, LNG:5, KNW:13, half_life:30d
  → "Detecta lento, recuerda largo. Para compliance/auditoría."

cortex learn policy profile --default
  → Fibonacci estándar (1,3,8,13), half_life:7d
```

---

## F. Integración completa: cómo lo usaría Alfred

### F.1 Un día de trabajo con el motor evolucionado

```text
╔══════════════════════════════════════════════════════════════╗
║ 09:00 — Alfred inicia sesión                                ║
╚══════════════════════════════════════════════════════════════╝

  agent_init:
    ├── .cortex/ detectado → CODEC-CORTEX activado
    ├── cortex session start → SES:current creada
    ├── cortex learn index rebuild → índice actualizado
    └── Perfil: CORTEX-WORK, presupuesto ~4000t

╔══════════════════════════════════════════════════════════════╗
║ 09:15 — Fidel: "Revisemos los benchmarks v2.2.2"           ║
╚══════════════════════════════════════════════════════════════╝

  pre_action:
    ├── detect_signals("benchmarks")
    │     └── Tema recurrente (3ª vez en 72h) → signal +2
    └── Sin bloqueos → proceder

  [Alfred revisa benchmarks...]

  post_action:
    ├── signal acumulado: "benchmarks" = 5
    ├── ¿Candidato? → Sí, promotion_score >= 5
    └── Notificar: "benchmarks es recurrente. ¿Registrar como LNG?"

╔══════════════════════════════════════════════════════════════╗
║ 11:30 — Fidel: "Actualicemos el ROADMAP"                   ║
╚══════════════════════════════════════════════════════════════╝

  pre_action:
    ├── detect_signals("roadmap")
    │     └── Primera vez → signal +1
    └── Sin bloqueos → proceder

  [Alfred actualiza ROADMAP...]

  post_action:
    ├── brain.cortex modificado → regeneration_score += 1
    └── Sin candidatos nuevos

╔══════════════════════════════════════════════════════════════╗
║ 18:00 — Fidel termina la jornada                            ║
╚══════════════════════════════════════════════════════════════╝

  session_close:
    ├── cortex session consolidate
    │     ├── SES:current → SES:last
    │     │     input:  "Revisión benchmarks + actualización ROADMAP"
    │     │     output: "benchmarks v2.2.2 revisados, ROADMAP 5 etapas"
    │     │     outcome:"Documentación actualizada, entrypoint blindado"
    │     │
    │     ├── Candidatos detectados en la sesión: 2
    │     │     ├── "benchmarks" → promotion_score 5 → sugerido como LNG
    │     │     └── "roadmap" → promotion_score 1 → solo SES
    │     │
    │     └── Decay aplicado:
    │           ├── SES:old_meeting (45 días) → promotion_score 0 → eliminado
    │           └── LNG:python_tips (21 días) → 5 → 3 (degradado)
    │
    └── cortex session close
          ├── brain.cortex actualizado
          └── "Sesión cerrada. 2 candidatos pendientes de revisión.
               ¿Los revisamos mañana?"
```

### F.2 Sesiones cruzadas: lo que el motor recuerda

```text
Día 1: Fidel menciona "benchmarks" → signal 1
Día 3: Fidel menciona "benchmarks" → signal 3 (recurrente)
Día 5: Fidel menciona "benchmarks" → signal 5 → CANDIDATO
  └── Alfred: "He notado que revisas benchmarks cada 2 días.
               ¿Quieres registrar esto como patrón de trabajo?"
  └── Fidel: "Sí" → LNG:benchmark_review_pattern creado

Día 30: LNG:benchmark_review_pattern no ha sido accedido en 21 días
  └── Decay: 5 → 3 (enfriamiento)
  └── Si Fidel no vuelve a mencionar "benchmarks" en 14 días más → eliminado
```

---

## G. Visión MCP futura

### G.1 ¿Qué cambia con MCP?

Hoy sin MCP, todo es CLI + archivos. El agente invoca `cortex learn` como comandos de terminal. Con MCP (Etapa 5), el motor se expone como herramientas que cualquier cliente MCP puede llamar:

```text
Sin MCP (hoy):              Con MCP (futuro):
  Alfred ejecuta:               Cliente MCP llama:
  cortex learn scan             mcp__cortex_learn_scan(workspace=".")
  cortex learn candidates       mcp__cortex_learn_candidates(workspace=".")
  cortex learn elevate <id>     mcp__cortex_learn_elevate(candidate_id="...")
```

### G.2 Tool catalog MCP para el motor

```json
{
  "tools": [
    {
      "name": "cortex_session_start",
      "description": "Inicia una sesión de aprendizaje en el workspace.",
      "parameters": { "workspace": "string (default: cwd)" }
    },
    {
      "name": "cortex_learn_scan",
      "description": "Escanea el workspace en busca de señales de aprendizaje.",
      "parameters": { "workspace": "string", "since_session": "bool" }
    },
    {
      "name": "cortex_learn_candidates",
      "description": "Lista candidatos detectados para elevación.",
      "parameters": { "workspace": "string", "min_score": "int (default: 5)" }
    },
    {
      "name": "cortex_learn_elevate",
      "description": "Ejecuta una elevación de candidato.",
      "parameters": { "candidate_id": "string", "confirm": "bool" }
    },
    {
      "name": "cortex_learn_feedback",
      "description": "Registra feedback sobre un candidato (aceptado/rechazado).",
      "parameters": { "candidate_id": "string", "decision": "accept|reject", "reason": "string?" }
    },
    {
      "name": "cortex_session_close",
      "description": "Cierra la sesión, consolida y aplica decay.",
      "parameters": { "workspace": "string", "consolidate": "bool (default: true)" }
    }
  ]
}
```

### G.3 Escenario multi-agente con MCP

```text
┌─────────────────────────────────────────────┐
│              Cliente MCP (Claude Desktop)     │
│                                               │
│  Usuario: "Analiza los últimos 3 benchmarks"  │
│                    │                          │
│      ┌─────────────┼─────────────┐            │
│      ▼             ▼             ▼            │
│  cortex-mcp    cortex-mcp    cortex-mcp       │
│  (agente A)    (agente B)    (agente C)       │
│  benchmarks/   docs/         cli/             │
│                                               │
│  Cada agente:                                 │
│  ├── Detecta su .cortex/ local                │
│  ├── Ejecuta cortex_learn_scan                │
│  ├── Reporta candidatos al orquestador        │
│  └── Orquestador consolida en brain maestra   │
└─────────────────────────────────────────────┘
```

---

## H. Plan de implementación por etapas

| Fase | Funcionalidad | Depende de | Esfuerzo | Entregable |
|:----:|---------------|:----------:|:--------:|------------|
| **4.1** | B. Auto-detección en handlers | — | Bajo | `pre_action` + `post_action` extendidos |
| **4.2** | A. Ciclo de sesión | 4.1 | Medio | `cortex session start/status/close` |
| **4.3** | E. Thresholds configurables | — | Bajo | `learn-policies.cortex` extendido, `cortex learn policy` |
| **4.4** | C. Decay y enfriamiento | 4.1, 4.2 | Medio | `apply_decay()` en `session_close` |
| **4.5** | D. Feedback loop | 4.1, 4.2 | Bajo | `cortex learn feedback` |
| **5.0** | G. MCP server | 4.1–4.5 | Alto | `cortex-mcp` con tool catalog completo |

**Orden recomendado:** 4.1 → 4.2 → 4.3 → 4.4 → 4.5 → 5.0

Las fases 4.3 y 4.5 pueden paralelizarse con 4.2. La fase 4.4 requiere que 4.1 y 4.2 estén listas (necesita timestamps de sesión para calcular decay).

---

## Referencias

- `skill/cortex/SKILL.md` §6 — Conocimiento base (axiomas, cortezas, niveles)
- `skill/cortex/SKILL.md` §8 — Survival Core, P0-P5, reglas `!survive_*`
- `cli/src/cortex/learning/` — Implementación actual v0.1.0
- `docs/en/specs/learning.md` — Especificación del motor (EN)
- `docs/es/specs/aprendizaje.md` — Especificación del motor (ES)
- `docs/ROADMAP.md` — Etapas 4 y 5
