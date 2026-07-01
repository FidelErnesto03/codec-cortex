<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

# CODEC-CORTEX — Universal Skill Distribution Protocol

> **Versión:** 1.1 · alineada a proyecto v0.3.5 · 2026-07-01
> **Propósito:** Definir cómo distribuir e instalar el SKILL CODEC-CORTEX en cualquier agente LLM/SLM, independientemente de plataforma, modelo o marca.
>
> **NOTA DE ESTADO:** A v0.3.5 el paquete `codec-cortex` está publicado en PyPI (`pip install codec-cortex`) e incluye el CLI canónico, la capa E2 de seguridad y el protocolo E3 de documentación. La distribución manual por plataforma y el script `setup.sh` siguen vigentes como alternativa para entornos sin acceso a `pip`.

---

## 1. Problemática

Cada plataforma de agentes tiene su propio mecanismo de instrucciones: `~/.hermes/skills/`, `CLAUDE.md`, `.cursorrules`, custom instructions, GPTs knowledge, etc. Esto fragmenta la adopción. CODEC-CORTEX necesita un mecanismo único que funcione en **todos** los entornos.

---

## 2. Principios de distribución

| Principio | Descripción |
|-----------|-------------|
| **Universalidad** | Un mismo SKILL se instala en cualquier agente sin modificación |
| **Autocontención** | El SKILL incluye su propio `$0` (glosario). No depende de artefactos externos |
| **Multi-formato** | El SKILL se distribuye en 3 formatos complementarios |
| **Idempotencia** | Instalación repetida no corrompe el estado del agente |

---

## 3. Formatos de distribución

| Formato | Archivo | Propósito | Consumo |
|---------|---------|-----------|---------|
| **SKILL.md** | `skill/SKILL.md` | Especificación humana canónica | Lectura directa por agente o humano |
| **SKILL.cortex** | `skill/SKILL.cortex` | Mente comprimida del protocolo | Parseo por `cortex CLI` o lectura por agente avanzado |
| **SKILL.en.md** | `skill/SKILL.en.md` | Especificación en inglés | Agentes con preferencia EN |
| **AGENT.cortex** | `skill/AGENT.cortex` | Entry point de identidad | Primer `.cortex` que un agente debe leer |
| **AGENT.md** | `skill/AGENT.md` | HCORTEX view del entry point | Humanos que revisan la identidad del agente |
| **brain.cortex** | `brain.cortex` | Cerebro operativo local | Estado vivo del agente (se crea por sesión) |

---

## 4. Mecanismos de instalación por plataforma

| # | Plataforma | Mecanismo | Archivo clave | Comando / Ruta |
|:-:|-----------|-----------|---------------|----------------|
| 1 | **Hermes Agent** | Skills directory | `SKILL.md` | `~/.hermes/skills/codec-cortex/` — copiar `skill/` |
| 2 | **Claude Code (Anthropic)** | CLAUDE.md | `SKILL.md` (adaptado) | `CLAUDE.md` en raíz del repo |
| 3 | **OpenCode** | Skills dir + `.opencode.json` | `SKILL.md` | `~/.opencode/skills/` o skills integrados |
| 4 | **GitHub Copilot** | `.github/copilot-instructions.md` | `SKILL.en.md` (adaptado) | Repo `.github/copilot-instructions.md` |
| 5 | **Cline / Cursor** | `.clinerules` / `.cursorrules` | `SKILL.md` (extracto) | Raíz del proyecto |
| 6 | **OpenAI GPTs** | Custom Instructions + Knowledge | `SKILL.md` + `SKILL.cortex` | Archivos de conocimiento del GPT |
| 7 | **Claude Projects (Anthropic)** | Project Knowledge | `SKILL.md` | Panel de conocimiento del proyecto |
| 8 | **Continue.dev** | `continue.json` / config | `SKILL.cortex` | Configuración del IDE |
| 9 | **Coding agents (genéricos)** | README-based | `skill/AGENT.cortex` | Leer desde instrucción del prompt |
| 10 | **pip install** | CLI package | `SKILL.cortex` | `pip install codec-cortex` → datos del skill en `site-packages/` |

---

## 5. Pipeline de instalación universal (`setup.sh`)

```bash
#!/usr/bin/env bash
# CODEC-CORTEX Universal Skill Installer
# Uso: bash setup.sh [target]
#   target: hermes | claude | opencode | copilot | cursor | all

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_SRC="$REPO_ROOT/skill"

install_hermes() {
    mkdir -p ~/.hermes/skills/codec-cortex/references
    cp "$SKILL_SRC/SKILL.md" ~/.hermes/skills/codec-cortex/
    cp "$SKILL_SRC/SKILL.cortex" ~/.hermes/skills/codec-cortex/
    cp "$SKILL_SRC/SKILL.en.md" ~/.hermes/skills/codec-cortex/
    cp "$SKILL_SRC/AGENT.cortex" ~/.hermes/skills/codec-cortex/
    cp "$SKILL_SRC/AGENT.md" ~/.hermes/skills/codec-cortex/
    echo "[OK] Hermes: SKILL instalado en ~/.hermes/skills/codec-cortex/"
}

install_claude() {
    # Claude Code: CLAUDE.md en raíz del repo
    if [ -f "$REPO_ROOT/CLAUDE.md" ]; then
        echo "[WARN] CLAUDE.md ya existe. Saltando."
    else
        cp "$SKILL_SRC/AGENT.md" "$REPO_ROOT/CLAUDE.md"
        echo "[OK] Claude Code: CLAUDE.md creado en raíz del repo"
    fi
}

install_copilot() {
    mkdir -p "$REPO_ROOT/.github"
    # Extracto ejecutivo del SKILL para Copilot
    cat > "$REPO_ROOT/.github/copilot-instructions.md" << 'EOF'
# CODEC-CORTEX para GitHub Copilot

CODEC-CORTEX is a structured memory protocol for LLM agents.
Key sigils: FCS (focus), OBJ (objective), WRK (work), CNST (constraint), STP (step).
Memory is stored in .cortex files with $0 glossary, $1 identity, $2 operational state.
HCORTEX is the human-readable view. CLI at cli/ for verify/render/CRUD.
EOF
    echo "[OK] Copilot: instrucciones creadas en .github/copilot-instructions.md"
}

install_opencode() {
    mkdir -p ~/.opencode/skills/codec-cortex
    cp "$SKILL_SRC/SKILL.md" ~/.opencode/skills/codec-cortex/
    echo "[OK] OpenCode: SKILL instalado en ~/.opencode/skills/codec-cortex/"
}

case "${1:-all}" in
    hermes)    install_hermes ;;
    claude)    install_claude ;;
    copilot)   install_copilot ;;
    opencode)  install_opencode ;;
    all)
        install_hermes
        install_claude
        install_copilot
        install_opencode
        echo "[OK] SKILL instalado en todas las plataformas disponibles"
        ;;
    *)
        echo "Uso: bash setup.sh [hermes|claude|copilot|opencode|all]"
        exit 1
        ;;
esac
```

---

## 6. Instalación manual (sin CLI)

Para agentes sin acceso a terminal (OpenAI GPTs, Claude Projects):

| Paso | Acción |
|:----:|--------|
| 1 | Descargar `skill/SKILL.md` del repositorio |
| 2 | Subir como archivo de conocimiento del GPT / project knowledge |
| 3 | Incluir en las instrucciones del sistema: "Lee SKILL.md y SKILL.cortex como tu protocolo de memoria" |
| 4 | (Opcional) Incluir `skill/AGENT.cortex` como entry point de identidad |

---

## 7. Verificación post-instalación

```bash
# v0.3.5 — nombres canónicos (los alias v2-* siguen aceptados con WARNING):
cortex doctor skill/SKILL.cortex            # Diagnóstico del skill
cortex verify --strict skill/SKILL.cortex   # Validación completa
cortex inspect skill/SKILL.cortex           # Inspección (secciones, entries, VIEW)
cortex verify-view skill/SKILL.cortex       # Coverage VIEW
cortex roundtrip-bidir skill/SKILL.cortex   # Roundtrip bidireccional

# Sin CLI: revisión manual
# Verificar que SKILL.cortex tenga:
# - $0: GLOSSARY como primera sección
# - Sin entradas FCS/OBJ/WRK/STP/NXT como estado vivo
# - IDN:skill con version correcta
```

---

## 8. Distribución vía PyPI (actual desde v0.3.3)

El paquete `codec-cortex` se publica en PyPI desde v0.3.3 (release E1). El CLI y los datos del SKILL se empaquetan juntos:

```toml
# pyproject.toml del paquete
[project]
name = "codec-cortex"
version = "0.3.5"

# Los datos del SKILL se empaquetan como package data:
[tool.setuptools.package-data]
cortex = ["skill/*.md", "skill/*.cortex", "benchmarks/*.md"]
```

```bash
# Instalación:
pip install codec-cortex
# El SKILL queda disponible en:
# site-packages/cortex/skill/SKILL.md
# site-packages/cortex/skill/SKILL.cortex

# Y el comando cortex queda disponible globalmente
cortex --version    # 0.3.5
cortex doctor --scan-secrets skill/SKILL.cortex   # E2: secret scanner
cortex docstring canonicalize                      # E3: docstring desde docs/cortex/api/
cortex benchmark --list                            # E3: inventario de suites
```

---

## 9. Matriz de compatibilidad

| Plataforma | SKILL.md | SKILL.cortex | AGENT.cortex | CLI verify | CLI render |
|-----------|:--------:|:------------:|:------------:|:----------:|:----------:|
| Hermes | ✅ | ✅ | ✅ | ✅ | ✅ |
| Claude Code | ✅ | ⚠️ (manual) | ✅ | ⚠️ (manual) | ⚠️ (manual) |
| OpenCode | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| Copilot | ✅ (extracto) | ❌ | ❌ | ❌ | ❌ |
| Cursor | ✅ (extracto) | ❌ | ❌ | ⚠️ (terminal) | ⚠️ (terminal) |
| GPTs | ✅ (knowledge) | ✅ (knowledge) | ❌ | ❌ | ❌ |
| Claude Projects | ✅ | ✅ | ❌ | ❌ | ❌ |
| pip + CLI | ✅ | ✅ | ✅ | ✅ | ✅ |

> **Leyenda:** ✅ = soporte nativo · ⚠️ = con adaptación manual · ❌ = no soportado

---

## 10. Recomendaciones

1. **Priorizar `pip install codec-cortex`** como método universal — el CLI trae el SKILL embebido.
2. **Para agentes sin CLI**, distribuir `skill/SKILL.md` + `skill/AGENT.cortex` como archivos de conocimiento.
3. **Para equipos enterprise**, el `setup.sh` automatiza la instalación en múltiples plataformas.
4. **Siempre verificar** con `cortex verify --strict skill/SKILL.cortex` después de instalar.
