# CODEC-CORTEX Learning Engine (CLE) — Installation Guide

**Version:** 0.1.0
**Algorithm:** `golden_fibonacci_v1`
**Spec:** `CODEC_CORTEX_LEARNING_ENGINE_SPEC.md`

This package adds a deterministic, local-first **learning engine** to the
[CODEC-CORTEX](https://github.com/FidelErnesto03/codec-cortex) CLI. The
engine scans `brain.cortex`, computes Fibonacci/golden-ratio scores,
detects elevation candidates, and applies user-confirmed or
policy-authorized mutations — all without calling any LLM or network
service.

---

## 1. Prerequisites

- Python ≥ 3.10
- `pip` available on `$PATH`
- A local checkout of `codec-cortex` (tested against v0.4.1 / commit `9999399`)

---

## 2. Install

```bash
# Extract the package
tar -xzf codec-cortex-learning-engine-0.1.0.tar.gz
cd codec-cortex-learning-engine-0.1.0

# Install into your codec-cortex checkout
./scripts/install_local.sh /ruta/al/proyecto/codec-cortex
```

The installer is **idempotent** — safe to re-run. It will:

1. Copy the `cortex/learning/` package into `cli/src/cortex/learning/`.
2. Patch `cli/src/cortex/cli/main.py` to register the `learn` subcommand.
3. Patch `cli/src/cortex/core/modes.py` to classify `learn *` commands in the read/write sets.
4. Patch `cli/pyproject.toml` to include `cortex.learning` in the packages list.
5. Copy templates, schema and tests into the target tree.
6. Re-install the CLI in editable mode (`pip install -e ./cli`).

After installation, `cortex learn --help` is available on `$PATH`.

---

## 3. Verify

```bash
# Run the full regression suite
./scripts/run_regression.sh /ruta/al/proyecto/codec-cortex
```

Expected output:

```text
=== CODEC-CORTEX Learning Engine — Regression Suite ===
...
[1/5] running existing pytest suite (no coverage gate)...
464 passed, 3 skipped
  PASS
[2/5] running learning-engine tests...
49 passed
  PASS
[3/5] running python -m compileall on cli/src...
  PASS
[4/5] running pip check...
No broken requirements found.
  PASS
[5/5] scanning learning engine for forbidden patterns...
  - LLM / network libraries ...  PASS (none found)
  - eval() / exec() calls ...    PASS (none found)
[bonus] CLI smoke test ...
  doctor: PASS
  policy validate: PASS
  index rebuild: PASS
  scan: PASS
  candidates: PASS
=== ALL CHECKS PASSED ===
```

---

## 4. Quick start

```bash
# Initialise a .cortex/ workspace in the current directory
cortex learn init --workspace .

# Validate the workspace
cortex learn doctor

# Inspect the default policy set
cortex learn policy show
cortex learn policy validate

# Build the learn-index
cortex learn index rebuild
cortex learn index status

# Scan the brain and list elevation candidates
cortex learn scan --json
cortex learn candidates --limit 10 --json

# Explain a single candidate in detail
cortex learn explain --candidate cand_001

# Dry-run an elevation (produces a diff, does NOT mutate brain)
cortex learn elevate --candidate cand_001 --dry-run

# Apply an elevation authorised by a policy (requires --confirm)
cortex learn elevate --policy auto_ses_to_lng --apply --confirm

# Produce a load profile within a token budget
cortex learn profile --budget 1000 --json
```

---

## 5. Workspace layout

After `cortex learn init`, your project will contain:

```text
.cortex/
  MANIFEST.cortex             # canonical artefact map
  brain.cortex                # operational memory (NOT modified by scans)
  learn-policies.cortex       # external learning policy set
  index/
    learn-index.json          # rebuildable performance index
  cache/                      # reserved for future caches
```

The index is **derived** and **rebuildable** — deleting it and running
`cortex learn index rebuild` produces a byte-identical file (verified by
`TestIndexRebuild::test_index_rebuildable_after_deletion`).

---

## 6. What the engine will NEVER do

Per SPEC §1 (Principios no negociables):

- It will **not** call any LLM (OpenAI, Anthropic, …).
- It will **not** make any network request (`requests`, `httpx`, `urllib`).
- It will **not** use `eval()` or `exec()` to evaluate policy conditions.
- It will **not** mutate `brain.cortex` during `learn scan` / `learn candidates` / `learn explain`.
- It will **not** allow common policies to elevate protected sigils (`IDN`, `AXM`, `CNST:blocking`, `CLAIM`, `LIM`).
- It will **not** implement `learn-ledger.cortex` (excluded per SPEC §1.6).

Every one of these guarantees is enforced by an automated test in
`tests/test_learning_engine.py` (`TestForbiddenPatterns` class).

---

## 7. Documentation

- `PATCH_SUMMARY.md` — Files created/modified, technical decisions, deviations.
- `CERTIFICATION_REPORT.md` — Full certification transcript with evidence.
- `CODEC_CORTEX_LEARNING_ENGINE_SPEC.md` — The authoritative specification (1100 lines).

---

## 8. Uninstall

To remove the learning engine from a codec-cortex checkout:

```bash
cd /ruta/al/proyecto/codec-cortex
rm -rf cli/src/cortex/learning
rm -f cli/src/tests/test_learning_engine.py
# Revert the three patched files (use git or your backup)
git checkout cli/src/cortex/cli/main.py cli/src/cortex/core/modes.py cli/pyproject.toml
# Reinstall the CLI
pip install -e ./cli
```

---

## 9. License

The learning engine is distributed under the same MIT license as the
codec-cortex project.
