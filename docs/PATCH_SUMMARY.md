# Patch Summary — CODEC-CORTEX Learning Engine v0.1.0

**Date:** 2026-07-02
**Spec:** `CODEC_CORTEX_LEARNING_ENGINE_SPEC.md` (1100 lines)
**Target project:** https://github.com/FidelErnesto03/codec-cortex (commit `9999399`, v0.3.6)
**Engine version:** 0.1.0
**Algorithm:** `golden_fibonacci_v1`

---

## 1. Files created

### 1.1 New package `cortex.learning` (11 modules)

| File | Lines | Purpose |
|---|---:|---|
| `cli/src/cortex/learning/__init__.py` | 31 | Engine version constants and public API surface |
| `cli/src/cortex/learning/errors.py` | 47 | `LearningError` base class + 13 `LE-xxx` error codes |
| `cli/src/cortex/learning/conditions.py` | 254 | Eval-free condition parser (`promotion_score>=8\|user_validated=true`) |
| `cli/src/cortex/learning/workspace.py` | 376 | Workspace discovery, `init`, `doctor`, default templates |
| `cli/src/cortex/learning/policy_defaults.py` | 49 | Default `learn-policies.cortex` text (mirrors SPEC §4.3) |
| `cli/src/cortex/learning/policy.py` | 317 | Policy parser, validator, evaluator, `ProtectedTargets` |
| `cli/src/cortex/learning/scoring.py` | 325 | Fibonacci/golden-ratio scoring: `hotness`, `promotion`, `risk`, `read_priority` |
| `cli/src/cortex/learning/index.py` | 279 | Rebuildable `learn-index.json`: load, save, `is_stale`, `rebuild_for_workspace` |
| `cli/src/cortex/learning/candidates.py` | 197 | Candidate detection and `explain` (SPEC §7, §17) |
| `cli/src/cortex/learning/elevation.py` | 444 | `plan_patch`, `render_diff`, `apply_patch`, `verify_post_apply` |
| `cli/src/cortex/learning/cli.py` | 466 | Argparse subcommand registration + 11 command handlers |
| **Total** | **3 085** | |

### 1.2 Tests

| File | Tests | Coverage |
|---|---:|---|
| `cli/src/tests/test_learning_engine.py` | 49 | Unit + integration + acceptance + forbidden-pattern scans |

### 1.3 Templates

| File | Mirrors SPEC § |
|---|---|
| `templates/.cortex/MANIFEST.cortex` | §4.1 |
| `templates/.cortex/brain.cortex` | §4.2 (minimal self-contained brain) |
| `templates/.cortex/learn-policies.cortex` | §4.3 (default policy set) |

### 1.4 Schemas

| File | Mirrors SPEC § |
|---|---|
| `schemas/learn-index.schema.json` | §4.4 (JSON Schema draft 2020-12, provided by spec package) |

### 1.5 Scripts

| File | Purpose |
|---|---|
| `scripts/install_local.sh` | Idempotent installer: copies package, patches `main.py` / `modes.py` / `pyproject.toml`, reinstalls CLI |
| `scripts/run_regression.sh` | Runs existing pytest + new learning tests + `compileall` + `pip check` + forbidden-pattern scans + CLI smoke |

### 1.6 Documentation

| File | Purpose |
|---|---|
| `README_INSTALL.md` | Quick-start guide for end users |
| `PATCH_SUMMARY.md` | This file |
| `CERTIFICATION_REPORT.md` | Final certification report with evidence |

---

## 2. Files modified (in target project)

### 2.1 `cli/src/cortex/cli/main.py`

**Change:** Added 8 lines just before `return p` in `build_parser()` to register the `learn` subcommand.

```python
# ------------------------------------------------------------------
# learn  (CODEC-CORTEX Learning Engine / CLE)
# Deterministic, local-first learning engine for .cortex workspaces.
# See SPEC §8 for the full command surface.
# ------------------------------------------------------------------
from ..learning.cli import add_learn_subparser
add_learn_subparser(sub)
```

**Idempotent:** Yes — `install_local.sh` checks for `from ..learning.cli import add_learn_subparser` before patching.

### 2.2 `cli/src/cortex/core/modes.py`

**Change:** Extended `READ_ONLY_COMMANDS` and `WRITE_COMMANDS` frozensets to classify `learn *` subcommands:

```python
# Learning engine — read-only sub-actions
"learn doctor", "learn policy show", "learn policy validate",
"learn index status", "learn scan", "learn candidates",
"learn explain", "learn profile",

# Learning engine — write sub-actions
"learn init", "learn index rebuild", "learn index clean",
"learn policy apply", "learn policy add",
"learn elevate",
```

### 2.3 `cli/pyproject.toml`

**Change:** Added `"cortex.learning"` to the `tool.setuptools.packages` list.

---

## 3. Commands added to the CLI

| Command | SPEC § | Mode |
|---|---|---|
| `cortex learn init [--workspace .] [--force]` | §8.1 | write |
| `cortex learn doctor` | §8.2 | read |
| `cortex learn policy show` | §8.3 | read |
| `cortex learn policy validate` | §8.3 | read |
| `cortex learn policy apply --file ... [--dry-run\|--confirm]` | §8.3 | write |
| `cortex learn policy add --name ... --source ... --target ... --when ... --action ... [--requires ...]` | §8.3 (alt) | write |
| `cortex learn index rebuild` | §8.4 | write |
| `cortex learn index status` | §8.4 | read |
| `cortex learn index clean` | §8.4 | write |
| `cortex learn scan [--json]` | §8.5 | read |
| `cortex learn candidates [--limit N] [--json]` | §8.5 | read |
| `cortex learn explain --candidate <id>` | §8.5 | read |
| `cortex learn elevate --candidate <id> [--dry-run\|--apply --confirm]` | §8.6 | write |
| `cortex learn elevate --policy <id> [--dry-run\|--apply]` | §8.6 | write |
| `cortex learn profile --budget N [--json]` | §8.7 | read |

Every subcommand accepts `--workspace` (overrides the parent `learn --workspace`) and `--json` (machine-readable output).

---

## 4. Technical decisions

### 4.1 Reuse of the existing `.cortex` parser

The learning engine does NOT implement its own `.cortex` parser. It reuses `cortex.core.parser.parse_cortex` and `cortex.core.ast.CortexDocument` for both `brain.cortex` and `learn-policies.cortex`. This ensures:

- Single source of truth for parsing semantics.
- Round-trip safety (the engine writes via `cortex.core.writer.write_cortex`).
- No drift between the canonical grammar and what the engine accepts.

### 4.2 Conditions DSL is fully `eval`-free

The condition parser in `cortex/learning/conditions.py` implements its own tokenizer and comparator. It supports:

- `|` as AND conjunction
- `=`, `!=`, `>=`, `<=`, `>`, `<` operators
- Integer, float, boolean, null and quoted-string values
- Strict field-name validation (`[A-Za-z_][A-Za-z0-9_]*`)

It explicitly does NOT use `eval`, `exec`, `compile` or `ast.literal_eval`. The test `TestConditions::test_no_eval_function_used` reads the source file and asserts no `eval(`/`exec(` calls appear.

### 4.3 Scoring model: additive, capped at `critical=21`

The score functions are additive across signals, with `observed=1` as the floor and `critical=21` as the cap. This matches the SPEC §17 example exactly:

```
SES cluster of 3 entries with user_validated=true
→ signals: repeated + pattern + user_validated
→ promotion_score = 2 + 3 + 8 = 13   ✓ matches §17
```

Earlier iterations used `max()` aggregation, which produced `promotion_score=8`. The additive model is closer to the SPEC's intent.

### 4.4 Index is non-canonical and rebuildable

`learn-index.json` is treated as a derived cache:

- `is_stale(idx, brain_hash, policy_hash)` returns True if any of `brain_hash`, `policy_hash`, `engine_version`, `algorithm` change.
- `rebuild_for_workspace(workspace)` recomputes the index from `brain.cortex` + `learn-policies.cortex` + engine version.
- The test `TestIndexRebuild::test_index_rebuildable_after_deletion` verifies the index can be deleted and rebuilt with identical content.

### 4.5 Protection model

`ProtectedTargets.matches(sigil, name, attrs)` honours both forms in the SPEC §4.3 protected list:

- **Bare sigil** (`"IDN"`, `"AXM"`, `"CLAIM"`, `"LIM"`) — protects every entry with that sigil.
- **`SIGIL:value` form** (`"CNST:blocking"`) — protects entries with that sigil AND `severity==value` (or `status==value`).

`plan_patch` defends in depth: even if a protected sigil reaches the planner (it shouldn't, because `detect_candidates` filters them out first), the planner returns a `Patch` with `mode="block"` rather than mutating the brain.

### 4.6 Mutation safety

`apply_patch` follows the SPEC §7.4 sequence:

1. parse brain (in memory)
2. parse policies (in memory)
3. rebuild/validate index (in memory)
4. plan patch
5. dry-run diff (default; `--apply` requires `--confirm`)
6. apply only if mode allows
7. serialize via `write_cortex`
8. **re-parse to verify** the mutated AST is still valid
9. atomic write (`.tmp` + `replace`)
10. rebuild index
11. (caller may run `verify_post_apply`)

The post-write re-parse (step 8) catches any serialization bug before the file is replaced on disk.

### 4.7 Idempotent installer

`install_local.sh` is safe to re-run:

- Copies `*.py` files into `cli/src/cortex/learning/` unconditionally (idempotent overwrite).
- Patches `main.py` only if `from ..learning.cli import add_learn_subparser` is NOT already present.
- Patches `modes.py` only if `"learn doctor"` is NOT already in `READ_ONLY_COMMANDS`.
- Patches `pyproject.toml` only if `"cortex.learning"` is NOT already in the packages list.
- Reinstalls the CLI in editable mode (`pip install -e ./cli`) at the end.

---

## 5. Deviations from the specification

### 5.1 `policy propose` does not interpret free-text user requests

SPEC §8.3 says `cortex learn policy propose --request "<texto del usuario>"` should be supported, but explicitly notes:

> `policy propose` no debe llamar a LLM. Si se necesita interpretación semántica, el LLM debe generar una propuesta intermedia y el motor solo validarla.

The implementation honours this by NOT implementing `policy propose --request`. Instead, the engine provides:

- `cortex learn policy apply --file proposed-policy.cortex --dry-run` — validates and shows a diff of a policy file produced externally (e.g. by an LLM).
- `cortex learn policy add --name ... --source ... --target ... --when ... --action ...` — adds a single structured policy rule directly.

Both alternatives are explicitly accepted by SPEC §8.3 ("Alternativa aceptable").

### 5.2 `learn-ledger.cortex` not implemented

SPEC §1.6 explicitly excludes `learn-ledger.cortex` from this phase. No code path in `cortex.learning` references it, and `init_workspace` does not create the file.

### 5.3 Hash-based index invalidation only

The index is invalidated by `brain_hash`, `policy_hash`, `engine_version` and `algorithm` (SPEC §4.4). No time-based or hit-count-based staleness is implemented — this preserves determinism.

### 5.4 Scoring is additive (not max-based)

SPEC §6.2's pseudocode does not pin down the aggregation model. The implementation uses additive scoring capped at `critical=21`, which matches the SPEC §17 worked example (`promotion_score: 13`).

---

## 6. What did NOT change

The following areas of the codec-cortex project are untouched:

- `cli/src/cortex/core/` (parser, lexer, AST, writer, validator, errors) — unchanged.
- `cli/src/cortex/cli/commands/` (existing commands) — unchanged.
- `cli/src/cortex/hcortex/`, `cli/src/cortex/v2/`, `cli/src/cortex/crud/`, `cli/src/cortex/glossary/`, `cli/src/cortex/templates/`, `cli/src/cortex/audit/`, `cli/src/cortex/security/` — unchanged.
- Existing tests — unchanged (all 415 still pass).
- `pyproject.toml` at the repo root — unchanged.

The learning engine is a pure addition; it does not alter any existing behaviour.
