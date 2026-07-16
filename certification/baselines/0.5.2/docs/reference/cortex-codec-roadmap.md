# CODEC-CORTEX — Roadmap de Protocolo de Comunicación Universal para IAs

> Documento de visión y hoja de ruta.
> Formato: HCORTEX-READ | Perfil: FULL | Versión: 1.0

---

## §1: ¿Qué es un CODEC para IAs?

Un **codec** de video (H.264, AV1, VP9) toma frames en bruto y los comprime en un bitstream que puede transmitirse, almacenarse y descomprimirse con pérdida mínima.

**CODEC-CORTEX** hace lo mismo con el **estado de conocimiento** de una IA:

| Aspecto | Codec de Video | Codec CORTEX |
|---|---|---|
| Entrada | Frames (pixeles) | Estado cognitivo (texto, contexto, lecciones) |
| Compresor | H.264 encoder | `cortex.parse` + `cortex.learn` |
| Stream | Bitstream .h264 | Archivo `.cortex` / stream MCP |
| Decompresor | H.264 decoder | `cortex.render` (HCORTEX) |
| Tasa típica | 50:1 | ~8:1 (28 tokens vs 250 tokens) |
| Consumidor | GPU/reproductor | LLM/SLM |

### Principio Fundamental

CODEC-CORTEX no es un sistema de archivos.  
CODEC-CORTEX es un **protocolo de compresión de conocimiento** para comunicación entre IAs.

El formato `.cortex` es solo la **representación en disco** del codec.  
El **verdadero codec** es el ciclo: `parse → learn → elevate → render`.

---

## §2: Las 3 Capas del Codec

```
┌───────────────────────────────────────────────────┐
│              CODEC-CORTEX PROTOCOL               │
├───────────────────────────────────────────────────┤
│                                                   │
│  ┌─────────────────────────────────────────────┐  │
│  │  Capa 3: Conocimiento (Knowledge)          │  │
│  │  ─────────────────────────────────────────  │  │
│  │  Múltiples lecciones → KNW (compresión     │  │
│  │  semántica: muchas LNG en un KNW)          │  │
│  │  engine: cortex.learn / elevate            │  │
│  └─────────────────────────────────────────────┘  │
│                          ↑                        │
│  ┌─────────────────────────────────────────────┐  │
│  │  Capa 2: Transporte (Stream/File)          │  │
│  │  ─────────────────────────────────────────  │  │
│  │  MCP como transporte en tiempo real        │  │
│  │  Archivos .cortex como persistencia        │  │
│  │  ACP para delegación entre agentes         │  │
│  └─────────────────────────────────────────────┘  │
│                          ↑                        │
│  ┌─────────────────────────────────────────────┐  │
│  │  Capa 1: Representación (Syntax/Sigil)     │  │
│  │  ─────────────────────────────────────────  │  │
│  │  Sigilos: FCS, OBJ, WRK, LNG, KNW...       │  │
│  │  Tipos: attrs, cuerpo, attrs-pos            │  │
│  │  Secciones: $0, $1... $N                    │  │
│  └─────────────────────────────────────────────┘  │
│                                                   │
└───────────────────────────────────────────────────┘
```

### Capa 1 — Representación (Syntax)

El formato base: sigilos + secciones + tipos.  
Es el "alfabeto" del codec. Cualquier estado puede expresarse.

### Capa 2 — Transporte (Stream/File)

Cómo viaja el codec:

| Transporte | Propósito | Estado Actual |
|---|---|---|
| Archivos `.cortex` | Persistencia en disco | ✅ Implementado |
| **MCP** | Streaming a agentes IA | 🚧 Fase 2 |
| ACP | Delegación entre agentes | 📋 Futuro |
| LSP | Edición humana | 📋 Futuro |
| Database | Consultas sigilares | 🔮 Visión |

### Capa 3 — Conocimiento (Knowledge)

La compresión **semántica** del codec.

Aquí es donde el learning engine convierte:

```
5 lecciones específicas (LNG)
  "BLP-002 falló por..."
  "BLP-004 necesitó..."
  "E3 se resolvió..."
  "E4 se descartó..."
  "Handler resolvió mal ID..."
         ↓ cortex.learn / elevate
1 conocimiento general (KNW)
  "Los handlers de ArqUX tienen bugs
   de resolución de ciclo. Verificar
   archivo en disco tras blueprint.create"
```

Esa es la **compresión real**: 5 lecciones → 1 conocimiento. ~150 tokens → ~30 tokens.

---

## §3: Fases del Roadmap

### Fase 1: File CODEC (✅ Actual)

**Estado:** Implementado y operativo.

| Componente | Status |
|---|---|
| Parser core (v1) | ✅ Estable |
| Parser v2 (sigilos locales, VIEW) | ✅ Estable |
| HCORTEX render (READ, EDIT, DISPLAY) | ✅ Estable |
| Learning engine (cortex.learn) | ✅ Operativo |
| Validación (E023, E024, E029, etc.) | ✅ Operativo |
| Auto-numeración secuencial | 🚧 En ejecución (BLP-003) |

**Forma de consumo:** Archivos `.cortex` en disco.  
**Usuarios:** Agentes IA bajo ArqUX governance.

---

### Fase 2: Stream CODEC (🚧 Siguiente)

**Estado:** En diseño.

CODEC-CORTEX se presenta como **MCP Server**.  
No es un plugin — es el **codificador/decodificador** en tiempo real.

#### Herramientas MCP

| Tool | Función | Equivalente codec |
|---|---|---|
| `cortex.encode` | Estado → sigilos CORTEX | Compresión |
| `cortex.decode` | Sigilos CORTEX → estado | Descompresión |
| `cortex.validate` | Validar integridad | Control de calidad |
| `cortex.learn` | LNG → KNW (elevar) | Compresión semántica |
| `cortex.render` | Sigilos → HCORTEX legible | Presentación |

#### Recursos MCP

| Resource | Devuelve |
|---|---|
| `cortex://schema` | Glosario de sigilos disponible |
| `cortex://state/{id}` | Estado codificado de un agente/proyecto |
| `cortex://stream/{id}` | Stream continuo de actualizaciones |

#### Flujo

```
Agente IA                          MCP Server (CODEC-CORTEX)
    │                                       │
    │──── cortex.encode(estado) ──────────→│
    │←──── sigilos CORTEX ────────────────│
    │                                       │
    │──── cortex.decode(sigilos) ─────────→│
    │←──── estado reconstruido ───────────│
    │                                       │
    │──── cortex.learn(LNGs) ─────────────→│
    │←──── KNW elevado ───────────────────│
```

**Forma de consumo:** MCP stdio/HTTP.  
**Usuarios:** Cualquier agente IA, no solo ArqUX.

---

### Fase 3: Database CODEC (🔮 Visión)

**Estado:** Conceptual.

CODEC-CORTEX como capa de almacenamiento:

| Capacidad | Descripción |
|---|---|
| Consultas sigilares | `GET KNW:* WHERE status=active` |
| Índices semánticos | Búsqueda por contenido de sigilos |
| Streaming entre IAs | Un agente escribe, otro lee en tiempo real |
| Transacciones | Atomicidad en escritura de estado |
| Replicación | Estado compartido entre agentes |

**Forma de consumo:** Cliente de base de datos + stream MCP.  
**Usuarios:** Ecosistemas multi-agente, sistemas distribuidos de IA.

---

## §4: Mapa de Transportes

```
                     ┌──────────────────┐
                     │  CODEC-CORTEX    │
                     │  (Protocolo)     │
                     └────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
         ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
         │   MCP   │    │   ACP   │    │   LSP   │
         ├─────────┤    ├─────────┤    ├─────────┤
         │ Tiempo  │    │ Entre   │    │ Editor  │
         │ real    │    │ agentes │    │ humano  │
         │ encode/ │    │ delega  │    │ resalta │
         │ decode  │    │ tareas  │    │ .cortex │
         └─────────┘    └─────────┘    └─────────┘
              │               │               │
              ▼               ▼               ▼
         Agentes IA     Orquestador      VS Code /
         (primario)     multi-agente     Vim / JetBrains
```

| Protocolo | Prioridad | Propósito | Consumidor |
|---|---|---|---|
| **MCP** | 1ª | Transporte principal del codec | Agentes IA |
| **ACP** | 2ª | Delegación multi-agente | Orquestadores |
| **LSP** | 3ª | Edición humana de .cortex | Developers |

---

## §5: La Compresión del Learning Engine

El corazón del codec no es la sintaxis — es el **ciclo de aprendizaje**.

```
         ┌─────────────────────────────────┐
         │         SES (Sesiones)          │
         │  Múltiples interacciones        │
         │  con el Arquitecto              │
         └────────────┬────────────────────┘
                      │ cortex.learn
                      ▼
         ┌─────────────────────────────────┐
         │      LNG (Lecciones)            │  ← Compresión 1:
         │  Patrones extraídos             │    sesiones → lecciones
         │  "cuando X pasa, hacer Y"       │    (~8:1)
         └────────────┬────────────────────┘
                      │ elevate (cortex.learn)
                      ▼
         ┌─────────────────────────────────┐
         │      KNW (Conocimiento)         │  ← Compresión 2:
         │  Reglas generales               │    lecciones → conocimiento
         │  "siempre verificar X"          │    (~5:1 sobre LNG)
         └────────────┬────────────────────┘
                      │ render
                      ▼
         ┌─────────────────────────────────┐
         │   HCORTEX (Texto legible)       │
         │  Listo para humano o IA         │
         └─────────────────────────────────┘
```

**Tasa de compresión total:** ~40:1  
(250 tokens de sesión → ~6 tokens de KNW)

Esto es lo que hace único a CODEC-CORTEX como codec:  
No solo comprime **sintaxis** — comprime **significado**.

---

## §6: Próximos Pasos Inmediatos

| # | Acción | Ciclo |
|---|---|---|
| 1 | Completar BLP-003 (auto-numeración) | CYCLE-01 |
| 2 | Definir interfaz MCP de CODEC-CORTEX | CYCLE-02 |
| 3 | Implementar `cortex.encode` y `cortex.decode` como tools MCP | CYCLE-02 |
| 4 | Implementar `cortex.learn` como tool MCP | CYCLE-02 |
| 5 | Integrar con ArqUX vía MCP | CYCLE-03 |
| 6 | Investigar ACP para delegación | CYCLE-04 |
| 7 | Investigar LSP para editor | CYCLE-05 |

---

## §7: Principios Rectores

1. **CODEC-CORTEX es protocolo, no plataforma**  
   No construye un ecosistema cerrado. Expone interfaces estándar (MCP, ACP, LSP).

2. **La compresión semántica es el valor real**  
   La sintaxis sigil es solo el medio. El fin es LNG → KNW.

3. **Universal no significa único**  
   Cualquier IA puede implementar el codec. No requiere ArqUX.

4. **Stream antes que database**  
   Primero MCP (streaming), luego Database (consulta).  
   No saltarse fases.

5. **El learning engine ES el codec**  
   Sin elevate, es solo un formato de archivo.  
   Con elevate, es un verdadero codec de conocimiento.

---

> Documento HCORTEX-READ.  
> Versión: 1.0 — 2026-07-09.  
> Visión: Arquitecto. Síntesis: Alfred.
