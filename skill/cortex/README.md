<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: skill/cortex/README.md
source_version: 1.2.0-enterprise-candidate
status: current
-->

**Perfil: CORTEX-WORK**

# CORTEX Containers

This directory stores `.md` containers whose internal content is encoded as `CORTEX`.

The `.md` extension exists for standard agent compatibility. The header declares that the content must be interpreted with CODEC-CORTEX structural memory rules.

## Canonical installation artifact

**`SKILL.md`** in this directory is the canonical CORTEX artifact for skill installation. Any agent, platform or runtime that installs CODEC-CORTEX as a skill MUST use `skill/cortex/SKILL.md` as the source file. Do NOT derive from HCORTEX views, display-only Markdown, or non-canonical copies.

| Property | Value |
|----------|-------|
| Path | `skill/cortex/SKILL.md` |
| Format | CORTEX (internal_encoding: CORTEX) |
| Entries | 266 |
| VIEW directives | 44 |
| VIEW coverage | 100% |
| Reversible | True |
| Source spec | `skill/hcortex/SKILL.md` (HCORTEX with VIEW) |
| Human spec | `skill/hcortex/SKILL_HCORTEX.md` (display-only) |

## Installation procedure

```
# Hermes
cp skill/cortex/SKILL.md ~/.hermes/skills/codec-cortex/SKILL.cortex

# Claude Code
echo '{"instructions": "..."}' > .claude/skills.json

# Cursor / Windsurf
cp skill/cortex/SKILL.md .cursor/rules/codec-cortex.mdc

# Generic — copy or symlink
cp skill/cortex/SKILL.md ~/my-agent-skills/codec-cortex.cortex.md
```

## Verification

After installation, verify the artifact is intact:

```bash
cortex v2-inspect skill/cortex/SKILL.md          # 14 sections, 266 entries, 44 VIEW, 100%
cortex v2-roundtrip-bidir skill/cortex/SKILL.md   # rc=0, 0 diffs
cortex verify --strict skill/cortex/SKILL.md      # 0 errors, 0 warnings
```

**Canonical HCORTEX spec (human reference):** `skill/hcortex/SKILL_HCORTEX.md` — v1.2.0-enterprise-candidate.

