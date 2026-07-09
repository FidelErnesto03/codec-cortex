# Plan E3 — Protocolo de Documentación CODEC-CORTEX

> **Objetivo:** Definir e implementar el protocolo de documentación del proyecto, siguiendo nuestra propia filosofía: HCORTEX para humanos, CORTEX para agentes, documentos centrales en formato estándar para adopción.
>
> **Principio rector:** La documentación del proyecto debe ser la primera en demostrar que CODEC-CORTEX funciona. No escribimos sobre el protocolo — el protocolo es la documentación.
>
> **Versión proyecto:** v0.3.5+

---

## 1. Estructura de `docs/`

```
docs/
├── README.md                 ← CENTRAL (formato estándar industria)
│                                Explica el sistema de documentación,
│                                audiencias, formatos, cómo navegar.
│                                Es la puerta de entrada para cualquier
│                                lector humano.
│
├── hcortex/                  ← PARA HUMANOS (formato HCORTEX)
│   ├── tutorials/              Guías paso a paso, onboarding
│   ├── how-to/                 Recetas para tareas específicas
│   ├── explanations/           Arquitectura, conceptos, filosofía
│   └── reference/              Manual de referencia humana
│       └── cli-ref.cortex      →   docs/cortex/api/ (misma fuente)
│
├── cortex/                   ← PARA AGENTES (formato CORTEX)
│   ├── api/                    API reference en CORTEX con VIEW
│   │   ├── canonicalize.cortex
│   │   ├── convert.cortex
│   │   ├── verify.cortex
│   │   ├── doctor.cortex
│   │   ├── audit.cortex
│   │   ├── modes.cortex
│   │   └── ...                 Un archivo .cortex por comando/herramienta
│   └── specs/                  Especificaciones del protocolo
│
└── plan/                     ← PLANES (formato libre)
    └── e2-*.md, e3-*.md
```

### Reglas de estructura

- **Sin versión en paths.** `docs/cortex/api/canonicalize.cortex`, no `v2/canonicalize.cortex`.
- **HCORTEX para humanos** — tablas > 80%, PUML, perfil declarado, sin $0, sin cursiva.
- **CORTEX para agentes** — $0 glosario, VIEW directives, verify --strict, reversible.
- **El documento central (`docs/README.md`)** es la única excepción: usa Markdown estándar para no exigir conocimiento previo del protocolo.

---

## 2. Cadena de generación de documentación

```
docs/cortex/api/*.cortex          ← FUENTE DE VERDAD
        │
        ├── cortex verify --strict    → validación estructural
        ├── cortex convert             → docs/hcortex/reference/ (humano)
        ├── cortex docstring <cmd>     → __doc__ en Python (help())
        └── cortex render              → HTML para web (futuro)
```

**No se escribe documentación dos veces.** La API reference se escribe una vez en CORTEX y desde ahí se derivan:
- La vista HCORTEX para humanos
- La docstring Python para `help()`
- La validación estructural con `verify --strict`

---

## 3. Componentes

| ID | Componente | Tipo | Descripción |
|:--:|------------|:----:|-------------|
| E3.1 | `docs/README.md` central | documento | Puerta de entrada estándar. Explica audiencias, formatos, navegación. |
| E3.2 | `docs/hcortex/` | estructura | Tutoriales, guías, explicaciones, referencias en HCORTEX puro. |
| E3.3 | `docs/cortex/api/*.cortex` | estructura + contenido | API reference como CORTEX con VIEW. Un archivo por comando. |
| E3.4 | Generador de docstrings | código | `cortex docstring <comando>` que produce __doc__ desde el CORTEX fuente. |
| E3.5 | Coverage gate | configuración | `pytest-cov` con umbral ≥85% en CI. |
| E3.6 | `cortex benchmark` | código | Comando que ejecuta benchmarks desde `benchmarks/`. |
| E3.7 | Docstrings Python | contenido | Docstrings en todos los módulos, derivadas de `docs/cortex/api/`. |

---

## 4. Orden de implementación

```
Fase 1: docs/README.md central + docs/hcortex/ + docs/cortex/api/
├── docs/README.md           → explicar el sistema de documentación
├── docs/hcortex/tutorials/  → primer tutorial (cómo instalar y usar)
├── docs/hcortex/explanations/ → filosofía, arquitectura
├── docs/cortex/api/         → 1 archivo .cortex por comando (empezar con
│                               canonicalize, convert, verify, doctor,
│                               audit, modes — los módulos E2)
└── docs/cortex/api/README.md → índice de la API en CORTEX

Fase 2: Generador de docstrings
├── cortex docstring         → comando que lee docs/cortex/api/ y genera
│                               docstring Python para help()
├── Integrar en main.py      → cada comando usa cortex docstring
└── Tests para generador

Fase 3: Coverage gate
├── pytest-cov               → medir cobertura actual
├── .coveragerc              → umbral 85%
├── CI step                  → bloquear si coverage < 85%
└── Reporte de brechas       → qué módulos necesitan tests

Fase 4: cortex benchmark
├── Comando cortex benchmark → leer benchmarks/, ejecutar suite
├── CI benchmark step        → benchmark en cada PR
└── Reporte comparativo
```

---

## 5. `docs/README.md` — Documento central (borrador de estructura)

```markdown
# Documentación de CODEC-CORTEX

CODEC-CORTEX es un protocolo de memoria contextual para agentes LLM/SLM.
Esta documentación está organizada por audiencia y formato.

## Para humanos

| Sección | Formato | Contenido |
|---------|---------|-----------|
| [Tutoriales](hcortex/tutorials/) | HCORTEX | Guías paso a paso |
| [Guías](hcortex/how-to/) | HCORTEX | Recetas para tareas específicas |
| [Conceptos](hcortex/explanations/) | Arquitectura y filosofía |
| [Referencia](hcortex/reference/) | Manual de referencia |

## Para agentes y CLI

| Sección | Formato | Validación |
|---------|---------|------------|
| [API Reference](cortex/api/) | CORTEX | `cortex verify --strict` |
| [Especificaciones](cortex/specs/) | CORTEX | `cortex verify --strict` |

## Cómo usar esta documentación

- **Primera vez?** Comienza por [Tutoriales](hcortex/tutorials/)
- **Buscas un comando?** `cortex --help` o [API Reference](cortex/api/)
- **Quieres contribuir?** Revisa [CONTRIBUTING.md](../CONTRIBUTING.md)
```

---

## 6. `cortex docstring` — Generador de docstrings

### Uso

```bash
cortex docstring canonicalize
# → Genera docstring para cortex canonicalize desde
#   docs/cortex/api/canonicalize.cortex

cortex docstring --all
# → Genera docstrings para todos los comandos

cortex docstring --install
# → Escribe las docstrings directamente en los .py
```

### Funcionamiento

1. Lee `docs/cortex/api/<comando>.cortex`
2. Extrae $0 (metadata), $1 (argumentos), HDL (operación)
3. Renderiza como docstring en formato HCORTEX compacto
4. Si `--install`, parchea el archivo `.py` correspondiente

### Formato de la docstring generada

```python
def run(args):
    """
    **Perfil: HCORTEX-REF**

    | Comando | `cortex canonicalize` |
    |---|---|
    | Status | current |
    | Requiere | cortex 0.3.2+ |

    Normaliza .cortex preservando VIEW directives.

    | Argumento | Req | Descripción |
    |---|---|---|
    | input | sí | Archivo .cortex a normalizar |
    | --out | no | Archivo de salida (default: stdout) |
    | --preserve | no | Preserva estructura original. v0.3.2+ |
    """
```

---

## 7. Criterios de aceptación

- [ ] `docs/README.md` existe y explica el sistema de documentación (audiencias, formatos, navegación)
- [ ] `docs/hcortex/` contiene al menos un tutorial en HCORTEX puro
- [ ] `docs/cortex/api/` contiene archivos .cortex por comando, todos pasan `verify --strict`
- [ ] Ningún path en docs/ contiene `v1/`, `v2/`, `v3/` — los nombres son canónicos
- [ ] `cortex docstring canonicalize` genera docstring válida
- [ ] CI tiene gate de coverage ≥85%
- [ ] `cortex benchmark` ejecuta suite desde `benchmarks/`
- [ ] 409+ tests siguen pasando
- [ ] Ruff 0 errores
