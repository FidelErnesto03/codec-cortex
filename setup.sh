#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A.
# SPDX-License-Identifier: MIT
#
# CODEC-CORTEX Universal Skill Installer
# Installs the CODEC-CORTEX SKILL across multiple agent platforms.
#
# Uso: bash setup.sh [target]
#   target: hermes | claude | copilot | opencode | all (default)
#
# See docs/specs/skill-distribution.md for details.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILL_SRC="$REPO_ROOT/skill"
VERSION="0.3.0"

echo "CODEC-CORTEX Universal Skill Installer v$VERSION"
echo "Source: $SKILL_SRC"
echo "---"

install_hermes() {
    local target="$HOME/.hermes/skills/codec-cortex"
    mkdir -p "$target/references"
    cp "$SKILL_SRC/SKILL.md" "$target/"
    cp "$SKILL_SRC/SKILL.cortex" "$target/"
    cp "$SKILL_SRC/SKILL.en.md" "$target/"
    cp "$SKILL_SRC/AGENT.cortex" "$target/" 2>/dev/null || true
    cp "$SKILL_SRC/AGENT.md" "$target/" 2>/dev/null || true
    echo "[OK] Hermes: SKILL instalado en $target"
}

install_claude() {
    if [ -f "$REPO_ROOT/CLAUDE.md" ]; then
        echo "[WARN] Claude Code: CLAUDE.md ya existe. No se sobrescribe."
    else
        cp "$SKILL_SRC/AGENT.md" "$REPO_ROOT/CLAUDE.md" 2>/dev/null || {
            echo "[WARN] Claude Code: AGENT.md no encontrado, saltando."
            return
        }
        echo "[OK] Claude Code: CLAUDE.md creado en raíz del repo"
    fi
}

install_copilot() {
    mkdir -p "$REPO_ROOT/.github"
    local target="$REPO_ROOT/.github/copilot-instructions.md"
    if [ -f "$target" ]; then
        echo "[WARN] Copilot: instrucciones ya existen. No se sobrescriben."
        return
    fi
    cat > "$target" << 'EOF'
# CODEC-CORTEX para GitHub Copilot

CODEC-CORTEX is a structured memory protocol for LLM agents.
Key sigils: FCS (focus), OBJ (objective), WRK (work), CNST (constraint), STP (step).
Memory is stored in .cortex files with $0 glossary, $1 identity, $2 operational state.
HCORTEX is the human-readable view. CLI at cli/ for verify/render/CRUD.
EOF
    echo "[OK] Copilot: instrucciones creadas en $target"
}

install_opencode() {
    local target="$HOME/.opencode/skills/codec-cortex"
    mkdir -p "$target"
    cp "$SKILL_SRC/SKILL.md" "$target/"
    echo "[OK] OpenCode: SKILL instalado en $target"
}

case "${1:-all}" in
    hermes)   install_hermes ;;
    claude)   install_claude ;;
    copilot)  install_copilot ;;
    opencode) install_opencode ;;
    all)
        install_hermes
        install_claude
        install_copilot
        install_opencode
        echo "---"
        echo "[OK] CODEC-CORTEX SKILL instalado en todas las plataformas disponibles"
        ;;
    *)
        echo "Uso: bash setup.sh [hermes | claude | copilot | opencode | all]"
        exit 1
        ;;
esac
