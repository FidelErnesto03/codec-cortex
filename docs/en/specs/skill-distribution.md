<!-- SPDX-FileCopyrightText: 2026 Fidel Ernesto Lozada A. -->
<!-- SPDX-License-Identifier: MIT -->

# CODEC-CORTEX — Universal Skill Distribution Protocol

> **Version:** 1.1 · aligned to project v0.3.7 · 2026-07-01
> **Purpose:** Define how to distribute and install the CODEC-CORTEX SKILL on any LLM/SLM agent, regardless of platform, model, or brand.
>
> **STATUS NOTE:** As of v0.3.7 the `codec-cortex` package is published on PyPI (`pip install codec-cortex`) and includes the canonical CLI, the E2 security layer, and the E3 documentation protocol. Manual distribution per platform and the `setup.sh` script remain available as alternatives for environments without `pip` access.

---

## 1. Problem

Every agent platform has its own instruction mechanism: `~/.hermes/skills/`, `CLAUDE.md`, `.cursorrules`, custom instructions, GPTs knowledge, etc. This fragments adoption. CODEC-CORTEX needs a single mechanism that works in **all** environments.

---

## 2. Distribution principles

| Principle | Description |
|-----------|-------------|
| **Universality** | The same SKILL installs on any agent without modification |
| **Self-containment** | The SKILL includes its own `$0` (glossary). Does not depend on external artifacts |
| **Multi-format** | The SKILL is distributed in complementary formats |
| **Idempotency** | Repeated installation does not corrupt agent state |

---

## 3. Distribution formats

| Format | File | Purpose | Consumption |
|--------|------|---------|-------------|
| **SKILL.md (CORTEX)** | `skill/cortex/SKILL.md` | Canonical CORTEX specification | Direct read by agent or human |
| **SKILL.md (HCORTEX)** | `skill/hcortex/SKILL.md` | Reversible human view of the protocol | HCORTEX-preferring agents or human reading |
| **SKILL_HCORTEX.md** | `skill/hcortex/SKILL_HCORTEX.md` | Detailed HCORTEX specification | Humans auditing the decompression protocol |
| **AGENT.md (CORTEX)** | `skill/cortex/AGENT.md` | CORTEX identity entry point | First `.md` an agent should read |
| **AGENT.md (HCORTEX)** | `skill/hcortex/AGENT.md` | HCORTEX identity entry point | Humans reviewing agent identity |
| **brain.cortex** | `brain.cortex` | Local operative brain | Live agent state (created per session) |

---

## 4. Installation mechanisms per platform

| # | Platform | Mechanism | Key file | Command / Path |
|:-:|----------|-----------|----------|----------------|
| 1 | **Hermes Agent** | Skills directory | `skill/cortex/SKILL.md` | `~/.hermes/skills/codec-cortex/` — copy `skill/` |
| 2 | **Claude Code (Anthropic)** | CLAUDE.md | `skill/cortex/SKILL.md` (adapted) | `CLAUDE.md` at repo root |
| 3 | **OpenCode** | Skills dir + `.opencode.json` | `skill/cortex/SKILL.md` | `~/.opencode/skills/` or built-in skills |
| 4 | **GitHub Copilot** | `.github/copilot-instructions.md` | `skill/cortex/SKILL.md` (extract) | Repo `.github/copilot-instructions.md` |
| 5 | **Cline / Cursor** | `.clinerules` / `.cursorrules` | `skill/cortex/SKILL.md` (extract) | Project root |
| 6 | **OpenAI GPTs** | Custom Instructions + Knowledge | `skill/cortex/SKILL.md` + `skill/hcortex/SKILL.md` | GPT knowledge files |
| 7 | **Claude Projects (Anthropic)** | Project Knowledge | `skill/cortex/SKILL.md` | Project knowledge panel |
| 8 | **Continue.dev** | `continue.json` / config | `skill/cortex/SKILL.md` | IDE configuration |
| 9 | **Coding agents (generic)** | README-based | `skill/cortex/AGENT.md` | Read from prompt instruction |
| 10 | **pip install** | CLI package | `skill/cortex/SKILL.md` | `pip install codec-cortex` → skill data in `site-packages/` |

---

## 5. Universal installation pipeline (`setup.sh`)

```bash
#!/usr/bin/env bash
# CODEC-CORTEX Universal Skill Installer
# Usage: bash setup.sh [target]
#   target: hermes | claude | opencode | copilot | cursor | all

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILL_SRC="$REPO_ROOT/skill"

install_hermes() {
    mkdir -p ~/.hermes/skills/codec-cortex/references
    cp "$SKILL_SRC/cortex/SKILL.md" ~/.hermes/skills/codec-cortex/
    cp "$SKILL_SRC/cortex/AGENT.md" ~/.hermes/skills/codec-cortex/
    cp "$SKILL_SRC/hcortex/SKILL.md" ~/.hermes/skills/codec-cortex/
    cp "$SKILL_SRC/hcortex/SKILL_HCORTEX.md" ~/.hermes/skills/codec-cortex/
    cp "$SKILL_SRC/hcortex/AGENT.md" ~/.hermes/skills/codec-cortex/
    echo "[OK] Hermes: SKILL installed at ~/.hermes/skills/codec-cortex/"
}

install_claude() {
    if [ -f "$REPO_ROOT/CLAUDE.md" ]; then
        echo "[WARN] CLAUDE.md already exists. Skipping."
    else
        cp "$SKILL_SRC/cortex/AGENT.md" "$REPO_ROOT/CLAUDE.md"
        echo "[OK] Claude Code: CLAUDE.md created at repo root"
    fi
}

install_copilot() {
    mkdir -p "$REPO_ROOT/.github"
    cat > "$REPO_ROOT/.github/copilot-instructions.md" << 'EOF'
# CODEC-CORTEX for GitHub Copilot

CODEC-CORTEX is a structured memory protocol for LLM agents.
Key sigils: FCS (focus), OBJ (objective), WRK (work), CNST (constraint), STP (step).
Memory is stored in .cortex files with $0 glossary, $1 identity, $2 operational state.
HCORTEX is the human-readable view. CLI at cli/ for verify/render/CRUD.
EOF
    echo "[OK] Copilot: instructions created at .github/copilot-instructions.md"
}

install_opencode() {
    mkdir -p ~/.opencode/skills/codec-cortex
    cp "$SKILL_SRC/cortex/SKILL.md" ~/.opencode/skills/codec-cortex/
    cp "$SKILL_SRC/hcortex/SKILL.md" ~/.opencode/skills/codec-cortex/
    echo "[OK] OpenCode: SKILL installed at ~/.opencode/skills/codec-cortex/"
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
        echo "[OK] SKILL installed across all available platforms"
        ;;
    *)
        echo "Usage: bash setup.sh [hermes|claude|copilot|opencode|all]"
        exit 1
        ;;
esac
```

---

## 6. Manual installation (without CLI)

For agents without terminal access (OpenAI GPTs, Claude Projects):

| Step | Action |
|:----:|--------|
| 1 | Download `skill/cortex/SKILL.md` from the repository |
| 2 | Upload as knowledge file for the GPT / project knowledge |
| 3 | Include in system instructions: "Read skill/cortex/SKILL.md as your memory protocol" |
| 4 | (Optional) Include `skill/cortex/AGENT.md` as identity entry point |

---

## 7. Post-installation verification

```bash
cortex verify --strict skill/cortex/SKILL.md   # Full CORTEX canon validation
cortex roundtrip-bidir skill/cortex/SKILL.md   # Bidirectional roundtrip
cortex verify-view skill/cortex/SKILL.md       # VIEW coverage
cortex inspect skill/cortex/SKILL.md           # Inspection (sections, entries, VIEW)
cortex verify --strict skill/hcortex/SKILL.md  # HCORTEX canon validation
cortex roundtrip-bidir skill/hcortex/SKILL.md  # HCORTEX roundtrip
cortex docstring canonicalize                  # E3: docstring from docs/cortex/api/
cortex benchmark --list                        # E3: suite inventory

# Without CLI: manual review
# Verify that skill/cortex/SKILL.md has:
# - $0: GLOSSARY as first section
# - No FCS/OBJ/WRK/STP/NXT entries as live state
# - IDN:skill with correct version
```

---

## 8. PyPI distribution (active since v0.3.3)

The `codec-cortex` package is published on PyPI since v0.3.3 (E1 release). The CLI and SKILL data are packaged together:

```toml
[project]
name = "codec-cortex"
dynamic = ["version"]  # version assigned by setuptools-scm from git tag

[project.scripts]
cortex = "cortex.cli.main_e3:main"

[tool.setuptools.package-data]
cortex = ["py.typed"]
```

```bash
# Installation:
pip install codec-cortex
# SKILL and CLI become available:
cortex --version                       # 0.3.5
cortex doctor --scan-secrets           # E2: secret scanner
cortex docstring canonicalize          # E3: docstring from docs/cortex/api/
cortex benchmark --list                # E3: suite inventory
```

---

## 9. Compatibility matrix

| Platform | SKILL.md (CORTEX) | SKILL.md (HCORTEX) | AGENT.md | CLI verify | CLI render |
|----------|:-----------------:|:------------------:|:--------:|:----------:|:----------:|
| Hermes | ✅ | ✅ | ✅ | ✅ | ✅ |
| Claude Code | ✅ | ⚠️ (manual) | ✅ | ⚠️ (manual) | ⚠️ (manual) |
| OpenCode | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| Copilot | ✅ (extract) | ❌ | ❌ | ❌ | ❌ |
| Cursor | ✅ (extract) | ❌ | ❌ | ⚠️ (terminal) | ⚠️ (terminal) |
| GPTs | ✅ (knowledge) | ✅ (knowledge) | ❌ | ❌ | ❌ |
| Claude Projects | ✅ | ✅ | ❌ | ❌ | ❌ |
| pip + CLI | ✅ | ✅ | ✅ | ✅ | ✅ |

> **Legend:** ✅ = native support · ⚠️ = manual adaptation needed · ❌ = not supported

> **See:** [`docs/es/specs/distribucion-skill.md`](../es/specs/distribucion-skill.md) for the Spanish version.
