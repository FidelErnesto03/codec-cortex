---
view: display-only
reversible: false
profile: HCORTEX-TUTORIAL
source: skill/cortex/SKILL.md §2, docs/cortex/api/
mode: READABLE
---

# First use of CODEC-CORTEX

> **source:** skill/cortex/SKILL.md §2:DESC:purpose · skill/cortex/SKILL.md §9:KNW:profile_*

This tutorial walks through a complete first cycle: install the CLI, create a working brain, verify it, explore it, close a session, and understand the output.

---

## 1. Install

**Via PyPI (recommended):**

```bash
pip install codec-cortex
```

**From source (development):**

```bash
cd cli
pip install -e .[dev]
```

**Verify:**

```bash
cortex --version
# Expected: 0.3.7 or later
```

---

## 2. Create your first brain

CODEC-CORTEX uses `.cortex` files to store structured memory. The most important one is `brain.cortex` — your agent's live operational state.

Create a minimal brain:

```bash
cortex new brain.cortex
```

This produces a file with three sections:

| Section | Content | source |
|:-------:|---------|--------|
| `$0` | Glossary (declares which sigils are valid) | `$0:canonical_sigils` |
| `$1` | Identity (project metadata) | `$1:IDN:project` |
| `$2` | Purpose + axioms | `$2:DESC:purpose` |

Inspect it:

```bash
cortex inspect brain.cortex
```

---

## 3. Add focus and objective

A working brain needs at least one active focus (FCS) and one objective (OBJ).

```bash
cortex add brain.cortex --section 3 --sigil FCS --name primary \
  --attrs 'what:"Learn CODEC-CORTEX" priority:high status:current survive:min'

cortex add brain.cortex --section 3 --sigil OBJ --name first \
  --attrs 'goal:"Complete the tutorial" status:current success:"verify passes" survive:min'
```

Inspect again to see the new entries:

```bash
cortex inspect brain.cortex
```

---

## 4. Verify

Every `.cortex` file should pass `verify --strict`:

```bash
cortex verify --strict brain.cortex
# Expected: 0 errors, 0 warnings
```

If there are errors, fix them before continuing. Common issues:

| Issue | source |
|-------|--------|
| Missing required fields | `$7:CNST:contract_fcs` |
| Unknown sigil not declared in `$0` | `!:extend_glossary` |

---

## 5. Add work and steps

Track what you are doing now:

```bash
cortex add brain.cortex --section 4 --sigil WRK --name tutorial \
  --attrs 'phase:"learning" current:"following steps" status:current survive:work'

cortex add brain.cortex --section 4 --sigil STP --name verify_setup \
  --attrs 'action:"Run cortex verify --strict" reason:"confirm brain is valid" owner:user status:current survive:work'
```

---

## 6. Register a session

After completing meaningful work, compress it into a session record (SES):

```bash
cortex add brain.cortex --section 5 --sigil SES --name first_tutorial \
  --attrs 'input:"Installed CLI and created brain.cortex" \
           output:"Verified brain passes strict check" \
           outcome:"Understood basic .cortex structure" date:2026-07-01'
```

If you noticed something useful (a pattern, a lesson, an error), register it as LNG:

```bash
cortex add brain.cortex --section 5 --sigil LNG --name verify_first \
  --attrs 'type:lesson cause:"First run of verify" \
           lesson:"Always add required contract fields" \
           prevention:"Check $0:contract_* before adding entries"'
```

---

## 7. Run a benchmark

| Action | Command | source |
|--------|---------|--------|
| List suites | `cortex benchmark --list` | `docs/cortex/api/benchmark.cortex` |
| Inspect suite | `cortex benchmark --inspect v2.0.0` | `docs/cortex/api/benchmark.cortex` |

Available suites: v1.0.0, v2.0.0, v2.1.0

---

## 8. Generate docstrings

| Action | Command | source |
|--------|---------|--------|
| One command | `cortex docstring canonicalize` | `docs/cortex/api/docstring.cortex` |
| All commands | `cortex docstring --all` | `docs/cortex/api/docstring.cortex` |

---

## 9. Understand CORTEX-OUT output

When the agent responds, it uses CORTEX-OUT — not raw `.cortex` and not free-form prose.

| Block | Content | When present | source |
|-------|---------|--------------|--------|
| **Resultado** | Direct answer / verdict | Always if there is a conclusion | `$12:KNW:out_blocks` |
| **Criterio** | Technical judgment | Analysis or review | `$12:KNW:out_blocks` |
| **Evidencia** | Verifiable facts | Audit or benchmark | `$12:KNW:out_blocks` |
| **Riesgo** | Problems or limits | Critical decisions | `$12:KNW:out_blocks` |
| **Acción** | Next step | Continuity needed | `$12:KNW:out_blocks` |
| **Límite** | What is not known | Uncertainty | `$12:KNW:out_blocks` |

A typical CORTEX-OUT for this tutorial:

```
**Resultado:** Tutorial complete — brain.cortex verified, SES recorded, benchmark listed.

**Acción:** Next: explore cortex docstring --all to see all available references.
```

---

## 10. Close the loop

Before ending a session, always verify your brain:

| Step | Command | source |
|:----:|---------|--------|
| 1 | `cortex verify --strict brain.cortex` | `docs/cortex/api/verify.cortex` |
| 2 | `cortex doctor --scan-secrets brain.cortex` | `docs/cortex/api/doctor.cortex` |
| 3 | `cortex verify --strict skill/cortex/SKILL.md` | `docs/cortex/api/verify.cortex` |
| 4 | `cortex verify-view skill/cortex/SKILL.md` | `docs/cortex/api/verify.cortex` |
| 5 | `cortex roundtrip-bidir skill/cortex/SKILL.md` | `docs/cortex/api/convert.cortex` |

---

## Criteria

| Rule | Reason | source |
|------|--------|--------|
| Use `docs/README.md` as entry point | Does not require protocol knowledge | `docs/cortex/specs/documentation-protocol.cortex` |
| Use `docs/en/hcortex/` for humans | Maintains dense, auditable reading | `$11:DESC:hcortex_def` |
| Use `docs/en/cortex/api/` for agents | Maintains self-contained verifiable source | `!:docs_source_of_truth` |
