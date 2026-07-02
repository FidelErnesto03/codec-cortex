#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A.
# SPDX-License-Identifier: MPL-2.0
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

echo "CODEC-CORTEX Universal Skill Installer v0.3.5"
echo "Source: $SKILL_SRC"
echo "---"

install_hermes() {
    local target="$HOME/.hermes/skills/codec-cortex"
    mkdir -p "$target/references"
    cp "$SKILL_SRC/cortex/SKILL.md" "$target/"
    cp "$SKILL_SRC/cortex/AGENT.md" "$target/"
    cp "$SKILL_SRC/hcortex/SKILL.md" "$target/"
    cp "$SKILL_SRC/hcortex/SKILL_HCORTEX.md" "$target/"
    cp "$SKILL_SRC/hcortex/AGENT.md" "$target/"
    echo "[OK] Hermes: SKILL instalado en $target"
}

install_claude() {
    if [ -f "$REPO_ROOT/CLAUDE.md" ]; then
        echo "[WARN] CLAUDE.md ya existe. Saltando."
    else
        cp "$SKILL_SRC/cortex/AGENT.md" "$REPO_ROOT/CLAUDE.md"
        echo "[OK] Claude Code: CLAUDE.md creado en raíz del repo"
    fi
}

install_copilot() {
    mkdir -p "$REPO_ROOT/.github"
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
    cp "$SKILL_SRC/cortex/SKILL.md" ~/.opencode/skills/codec-cortex/
    cp "$SKILL_SRC/hcortex/SKILL.md" ~/.opencode/skills/codec-cortex/
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
