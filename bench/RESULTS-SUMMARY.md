# BLP-003 — Informe de cierre de sesión

**Fecha:** 2026-10-04 · **Estado del BLP:** `in_progress` (NO cerrado — ver §5)
**Nivel alcanzado:** **N1** (verificado internamente, reproducible en CI)

---

## 1. Qué se demostró

### 1.1 Nivel A — instrumento determinista (COMPLETO, PASS)

| Indicador | Resultado | Artefacto |
|---|---|---|
| D1 idempotencia | **70/70** | `certificate.json` |
| D2 roundtrip HCORTEX 0.2 | **30/30** | |
| D3 paridad runtime | **py = node = bash** → `4ad4aec9…` | |
| D4 no-pérdida | **70/70** | |
| D5 sensibilidad a tamper | **PASS** | |
| **Veredicto** | **PASS** | |

**Go degradado** (no oculto): el binario precompilado `codec-cortex-go` lanza `S005_CONTENT_OUTSIDE_SECTION` sobre el corpus 0.1. Registrado en `certificate.json → D3.runtimes_failed = ["go"]`. Es un defecto del artefacto distribuido, no del formato. **Pendiente: issue propia.**

### 1.2 Contraste de determinismo D6 (COMPLETO, PASS)

| Lado | Repeticiones | Hashes únicos | Varianza |
|---|---|---|---|
| CORTEX (misma entrada re-parseada y re-canonicalizada) | 5 | 1 | **0** |
| LLM (`xiaomi/mimo-v2.6-pro`, misma prompt) | 5 | 5 | **4** |

`bench/results/determinism.json`

### 1.3 Experimento B — celda piloto (EJECUTADA, NO COMPLETA)

**Una sola celda**: MiMo V2.6 Pro × CORTEX × rep 1.
**Media mecánica: 0.9524** (6 completos, 1 parcial, 1 requiere-humano).
Detalle íntegro en `run-001/raw/mimo_cortex_r1.full.md`.

---

## 2. Falsaciones que se activaron

- **D6 se refutó en el primer intento.** Un probe de eco literal dio varianza **0** también
  en el LLM. Sin cambiar el probe, el contraste habría "probado" que CORTEX y el modelo se
  comportan igual. El probe es parte del instrumento.
- **Un script mío falseó la varianza de CORTEX a 4** al re-etiquetar bytes con un índice.
  Detectado, corregido con `cortex_repeats()` (re-parseo real), regenerado.
- Ambos errores están **preservados** en `determinism.json` bajo `llm_probe_echo_literal`
  y el método está documentado en `cortex_repeats()`.

---

## 3. Lo que NO se logró

- **R=5 no se ejecutó.** Se corrieron 3 celdas de las 90 planificadas
  (6 formatos × 8 preguntas × 2 modelos × R=5): 2 smokes de acceso (MiMo, DeepSeek) y
  1 celda piloto de benchmark.
- **El nivel N2 no fue alcanzado.** N2 exige k/n + IC por celda para C, E y R; solo hay
  una celda piloto.
- **Ningún claim sobre eficiencia/costo (H2), ortogonalidad (H4) o durabilidad (H5/R)** fue
  evaluado.
- **La rúbrica humana nunca se escribió** (T-2.3). Q8 sigue sin puntuación.

---

## 4. Por qué se detuvo

### 4.1 Bloqueo presupuestario (§7.14, §16.2)

| Modelo | Costo por celda | R=5 × 6 formatos |
|---|---|---|
| `xiaomi/mimo-v2.6-pro` | $0.1426 | **$4.28** |
| `deepseek/deepseek-v4.1-flash` | $0.0497 | **$1.49** |

Diseño completo: **~$5.77**. Tope pre-registrado: **$5.00**. El tope se alcanzó al detectar
la brecha, no después de pasarlo.

### 4.2 Dependencia externa (T-2.3)

La rúbrica de evaluación debe escribir un humano (Art. XII, §7.3). Ningún agente puede
sustituirlo sin invalidar la separación de poderes del protocolo.

### 4.3 Auditoría pendiente (P-07)

Heimdall no re-auditó el Nivel A ni firmó `audit.sig`. Sin firma, N4 es inalcanzable.

---

## 5. Estado de tareas

**Completadas (10):** T-1.1, T-1.2, T-1.3, T-1.4, T-1.5, T-2.1, T-2.2, T-2.4, T-2.5, T-3.0

**Pendientes (15):** T-1.6, T-2.3, T-3.1–T-3.6, T-4.1, T-4.2, T-5.1–T-5.3, T-6.1–T-6.3

**ACs verificados (4):** CA-01, CA-02, CA-03, CA-14

---

## 6. Artefactos entregados

```
bench/
├── certify.py              # runner Nivel A (D1–D5)
├── determinism.py          # contraste D6 + helper cortex_repeats()
├── run.py                  # orquestador (contrato de datos; sin claves)
├── scorer.py               # scorer mecánico de exactitud
├── preregistration.yaml    # H1–H4, R=5, N=8, Holm, tope $5
├── models.yaml             # ids exactos + tarifas
├── tokenizer.lock          # tiktoken 0.12.0 / o200k_base
├── rubric.md               # PROCEDIMIENTO (autoría humana pendiente)
├── environment.json        # versiones del entorno
├── corpus-heldout/         # 8 archivos + SHA256SUMS
└── results/
    ├── certificate.json        # Nivel A: PASS
    ├── determinism.json        # D6: PASS
    └── run-001/                # piloto
        ├── cell_mimo_cortex_r1.json
        ├── score_mimo_cortex_r1.json
        └── raw/mimo_cortex_r1.full.md

tests/SHA256SUMS            # 845 archivos, 845/845 verificados
.github/workflows/certificate.yml   # Nivel A en CI
```

---

## 7. Conclusión

CODEC-CORTEX tiene **evidencia reproducible de su capa determinista**: idempotencia,
roundtrip byte-exacto, no-pérdida, paridad cross-runtime, sensibilidad a tamper, y un
contraste medido contra un LLM real donde CORTEX da varianza 0 y el modelo da varianza 4.

Sobre la **comprensión**, hay **una** celda: MiMo V2.6 Pro leyó CORTEX 0.1, encadenó
secciones para responder multi-hop y acertó 0.9524 en 7 preguntas mecánicamente puntuables.
Es un resultado **`con_cell_1`**, no un promedio: **no hay claim publicable todavía** (H1–H4
permanecen abiertas).

La conclusión honesta: **el instrumento funciona, la evidencia es parcial, y el nivel es N1.**
Subirlo exige presupuesto, rúbrica humana y auditoría independiente.