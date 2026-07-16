# Plan E2 — Security & Governance

> **Objetivo:** endurecer el CLI y el protocolo contra mal uso, fuga de secretos y mutaciones no autorizadas.
>
> **Versión proyecto:** v0.3.3+
> **Roadmap:** Phase E2 — Status: planned → current
> **Depende de:** E1 completado (CI/CD, PyPI, Makefile, pre-commit)

---

## 1. Resumen de entregables

| ID | Entregable | Tipo | Esfuerzo | Depende de |
|:--:|------------|:----:|:--------:|:----------:|
| E2.1 | Dependabot para dependencias Python | config | 5 min | — |
| E2.2 | Secret scanner en pre-commit + `cortex doctor` | config + código | 30 min | E2.1 |
| E2.3 | Mutation gates: read-only / editor / admin | código | 2-3 días | — |
| E2.4 | Audit log persistente (.cortex-audit.jsonl) | código | 1 día | E2.3 |
| E2.5 | Release signing (SHA256) | script | 30 min | — |
| E2.6 | `cortex verify --signature` | código | 1 día | E2.5 |

---

## 2. E2.1 — Dependabot

### Qué es

Configuración de GitHub Dependabot para mantener las dependencias Python del CLI actualizadas automáticamente (seguridad, compatibilidad).

### Archivo

`.github/dependabot.yml`

### Detalle

- **Ecosystem:** pip
- **Directory:** `/cli`
- **Schedule:** weekly
- **Reviewers:** assignar al maintainer del proyecto
- **Labels:** `dependencies`, `security`

### Criterio de éxito

Dependabot abre PRs semanales con actualizaciones de dependencias. El CI los valida automáticamente.

---

## 3. E2.2 — Secret scanner

### Qué es

Hook de pre-commit que escanea el código en busca de tokens, claves API, contraseñas y secretos antes de cada commit. Complementa y endurece el scanner existente en `cortex doctor`.

### Archivos

- `.pre-commit-config.yaml` — nuevo hook
- `cli/src/cortex/cli/commands/doctor.py` — endurecer scan existente

### Detalle

- Usar `detect-secrets` o `gitleaks` como herramienta de scan
- El hook de pre-commit debe fallar (exit code != 0) si detecta un secreto
- `cortex doctor` debe incluir el mismo scan que el pre-commit
- El CI también debe correr el scan en cada PR
- Los falsos positivos se manejan con archivos `.secrets.baseline`

### Criterio de éxito

Un commit que incluya `ghp_...` o `pypi-...` es bloqueado por pre-commit. `cortex doctor` reporta el mismo hallazgo.

---

## 4. E2.3 — Mutation gates

### Qué es

Sistema de modos de operación del CLI que controla qué operaciones están permitidas según el nivel de autorización. Cada modo gobierna el flag `--force` y las operaciones destructivas.

### Tres modos

| Modo | Operaciones permitidas | `--force` | Uso típico |
|------|----------------------|:---------:|------------|
| **read-only** | `get`, `list`, `verify`, `verify-view`, `inspect`, `diff`, `glossary`, `diagram` | ❌ Bloqueado | CI, revisión, auditoría |
| **editor** | Todas las anteriores + `add`, `update`, `delete`, `move`, `format` | ⚠️ Permitido con confirmación | Trabajo diario del agente |
| **admin** | Todas las anteriores + `--force` sin restricción | ✅ Permitido | Setup inicial, migraciones, recovery |

### Implementación

- Flag global `--mode` (o variable de entorno `CORTEX_MODE`)
- Default: `editor`
- `read-only` bloquea todas las operaciones de escritura antes de tocar el archivo
- `editor` permite escritura pero requiere `--force` adicional para operaciones destructivas (delete, update masivo, overwrite)
- `admin` equivale al comportamiento actual sin restricciones
- El modo se propaga a través de `args.mode` a todos los command handlers

### Comportamiento visual

```bash
cortex --mode read-only delete brain.cortex OBJ:primary
# → Error: E2_MODE_READ_ONLY: cannot delete in read-only mode

cortex --mode editor delete brain.cortex OBJ:primary
# → OK (sin --force, operación normal)

cortex --mode editor delete brain.cortex OBJ:primary --force
# → Warning: --force in editor mode. Confirm? [y/N]
```

### Criterio de éxito

`cortex --mode read-only add ...` falla. `cortex --mode editor delete ... --force` pide confirmación. `cortex --mode admin delete ... --force` ejecuta sin preguntar.

---

## 5. E2.4 — Audit log (bajo demanda)

### Qué es

Registro de operaciones CRUD que SOLO se activa cuando el usuario lo solicita explícitamente. No hay log automático ni persistente. Coherente con el principio CODEC-CORTEX: solo escribir cuando hay valor futuro.

### Controles

```bash
cortex audit on          # Activa logging para la sesión actual
cortex audit off         # Desactiva logging
cortex audit snapshot    # Exporta estado actual de brain.cortex a .cortex-audit.jsonl
cortex audit status      # Muestra si logging está activo
```

### Modos y auditoría

| Modo | Auditoría automática | Auditoría manual |
|------|:-------------------:|:----------------:|
| **read-only** | ❌ No aplica | ❌ No aplica |
| **editor** | ❌ Desactivada por defecto | ✅ `cortex audit on` la activa para la sesión |
| **admin** | ❌ Desactivada por defecto | ✅ `cortex audit on` la activa |

### Formato del log (cuando se activa)

`~/.codec-cortex/audit/YYYY-MM-DD.jsonl` — append-only por día, fuera del repo.

```jsonl
{"t":"2026-07-01T12:00:00Z","op":"add","file":"brain.cortex","mode":"editor","result":"ok"}
```

### Reglas

- Sin `cortex audit on` previo → no se escribe nada
- `cortex audit snapshot` exporta un punto único (no un stream continuo)
- El archivo se almacena en `~/.codec-cortex/audit/` (home del usuario, no en el repo)
- `cortex audit off` detiene el logging; lo escrito hasta ese momento se conserva

### Criterio de éxito

`cortex audit status` → "logging: off". `cortex audit on` → "logging: on for this session". 
`cortex add ...` con logging on → línea escrita. `cortex add ...` con logging off → sin línea.
`cortex audit snapshot` → archivo único en `~/.codec-cortex/audit/`.

---

## 6. E2.5 — Release signing

### Qué es

Generar y publicar hashes SHA256 de todos los artefactos publicados en cada GitHub Release, permitiendo verificar integridad.

### Implementación

- Script `scripts/sign_release.py` que genera `SHA256SUMS` para:
  - `codec_cortex-X.Y.Z-py3-none-any.whl`
  - Tarball del skill completo (si se distribuye)
- El script se ejecuta en CI después del build, antes del publish
- El archivo `SHA256SUMS` se sube como artefacto del release

### Formato SHA256SUMS

```
699ad1f424f830264bb580ed0198b3c9bdedf2c9ef5755a218bd0cd93f083b18  codec_cortex-0.3.3-py3-none-any.whl
```

### Criterio de éxito

Cada GitHub Release contiene un archivo `SHA256SUMS` con los hashes de los artefactos publicados.

---

## 7. E2.6 — `cortex verify --signature`

### Qué es

Comando que verifica la integridad de un artefacto `.cortex` o `.whl` contra su hash SHA256 publicado.

### Uso

```bash
cortex verify --signature brain.cortex --manifest SHA256SUMS
# → OK: hash matches
# → ERROR: hash mismatch (file may be tampered)
```

### Comportamiento

- Lee el `SHA256SUMS` del release asociado (local o remoto)
- Calcula el hash del archivo local
- Compara: si coincide → OK, si no → ERROR
- En modo strict: exit code 1 si no hay firma disponible

### Criterio de éxito

`cortex verify --signature codec_cortex-0.3.3.whl --manifest SHA256SUMS` reporta OK para artefactos legítimos y ERROR para artefactos modificados.

---

## 8. Orden de ejecución recomendado

```
Fase 1: Configuración (sin código)
├── E2.1 Dependabot           → 5 min
├── E2.2 Secret scanner        → 30 min (config + endurecer doctor)
└── E2.5 Release signing       → 30 min (script + CI step)

Fase 2: Núcleo de código
├── E2.3 Mutation gates        → 2-3 días
│   ├── main.py: flag --mode
│   ├── core/modes.py: lógica de autorización
│   ├── commands/*: propagar modo
│   └── tests: test_modes.py
└── E2.4 Audit log             → 1 día
    ├── audit/logger.py: escritura append-only
    ├── audit/reader.py: consultas
    ├── cli/commands/audit.py: comando cortex audit
    └── tests: test_audit.py

Fase 3: Integración
├── E2.6 cortex verify --signature  → 1 día
└── Tests de integración E2          → 1 día
```

## 9. Criterios de aceptación generales

- [ ] Pre-commit hooks bloquean secretos (ghp_, pypi-, etc.)
- [ ] `cortex doctor` incluye scan de secretos
- [ ] `cortex --mode read-only` bloquea todas las escrituras
- [ ] `cortex --mode editor --force` pide confirmación
- [ ] Cada mutación CRUD solo se loguea si `cortex audit on` está activo
- [ ] `cortex audit status` muestra estado del logging
- [ ] `cortex audit snapshot` exporta punto único a `~/.codec-cortex/audit/`
- [ ] SHA256SUMS se genera y publica en cada release
- [ ] `cortex verify --signature` verifica integridad
- [ ] Dependabot abre PRs semanales
- [ ] 341+ tests siguen pasando (sin regresión)
- [ ] Ruff 0 errores

## 10. Riesgos

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Mutation gates rompen scripts existentes que usan `--force` | Medio | Default = editor (comportamiento actual). Solo afecta a quien use `--mode read-only` explícitamente. |
| Audit log crece sin control | Bajo | Rotación a 10MB, `.gitignore`, comando `cortex audit prune` |
| Secret scanner falsos positivos | Bajo | Baseline file para ignorar patrones conocidos |
| verify --signature sin conexión | Bajo | Modo offline: usar SHA256SUMS local, no remoto |
