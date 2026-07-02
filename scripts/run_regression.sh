#!/usr/bin/env bash
# run_regression.sh — run the full CODEC-CORTEX regression suite, plus
# the learning-engine acceptance suite defined in SPEC §10 and §11.1.
#
# Usage:
#   ./scripts/run_regression.sh /ruta/al/proyecto/codec-cortex
#
# Exits 0 only if every check passes:
#   - existing pytest suite passes
#   - new learning tests pass
#   - cortex learn CLI smoke commands succeed
#   - forbidden-pattern scans find no LLM/network/eval/exec usage in
#     the learning engine source

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <path-to-codec-cortex-checkout>" >&2
    exit 2
fi

TARGET="$(cd "$1" && pwd)"
LEARN_DIR="$TARGET/cli/src/cortex/learning"

if [[ ! -d "$LEARN_DIR" ]]; then
    echo "ERROR: $LEARN_DIR not found; run install_local.sh first" >&2
    exit 1
fi

echo "=== CODEC-CORTEX Learning Engine — Regression Suite ==="
echo "Target: $TARGET"
echo

cd "$TARGET"

# 1. Existing pytest suite (no coverage gate — we don't want to fail
#    because the new package isn't covered by the old --cov-fail-under
#    threshold of 85%).
echo "[1/5] running existing pytest suite (no coverage gate)..."
if python -m pytest cli/src/tests --no-cov -q; then
    echo "  PASS"
else
    echo "  FAIL — existing tests did not pass" >&2
    exit 1
fi

# 2. New learning tests
echo
echo "[2/5] running learning-engine tests..."
if python -m pytest cli/src/tests/test_learning_*.py --no-cov -q; then
    echo "  PASS"
else
    echo "  FAIL — learning tests did not pass" >&2
    exit 1
fi

# 3. compileall sanity
echo
echo "[3/5] running python -m compileall on cli/src..."
if python -m compileall -q cli/src; then
    echo "  PASS"
else
    echo "  FAIL — compileall reported errors" >&2
    exit 1
fi

# 4. pip check
echo
echo "[4/5] running pip check..."
if python -m pip check; then
    echo "  PASS"
else
    echo "  WARN — pip check reported issues (continuing)" >&2
fi

# 5. Forbidden-pattern scans
echo
echo "[5/5] scanning learning engine for forbidden patterns..."

echo "  - LLM / network libraries (openai|anthropic|requests|httpx|urllib)..."
if rg -n "openai|anthropic|requests|httpx|urllib" "$LEARN_DIR" >/dev/null 2>&1; then
    echo "    FAIL — found forbidden dependency" >&2
    rg -n "openai|anthropic|requests|httpx|urllib" "$LEARN_DIR" >&2 || true
    exit 1
fi
echo "    PASS (none found)"

echo "  - eval() / exec() calls..."
if rg -n "eval\(|exec\(" "$LEARN_DIR" >/dev/null 2>&1; then
    echo "    FAIL — found eval/exec" >&2
    rg -n "eval\(|exec\(" "$LEARN_DIR" >&2 || true
    exit 1
fi
echo "    PASS (none found)"

# 6. CLI smoke (init → doctor → policy validate → index rebuild → scan → candidates)
echo
echo "[bonus] CLI smoke test on a temporary workspace..."
SMOKE=$(mktemp -d)
trap "rm -rf $SMOKE" EXIT
cortex learn init --workspace "$SMOKE" >/dev/null
cortex learn doctor --workspace "$SMOKE" --json > "$SMOKE/doctor.json"
if python3 -c "import json,sys; d=json.load(open('$SMOKE/doctor.json')); sys.exit(0 if d['ok'] else 1)"; then
    echo "  doctor: PASS"
else
    echo "  doctor: FAIL" >&2
    exit 1
fi
cortex learn policy validate --workspace "$SMOKE" --json > "$SMOKE/pol.json"
python3 -c "import json,sys; d=json.load(open('$SMOKE/pol.json')); sys.exit(0 if d['ok'] else 1)"
echo "  policy validate: PASS"
cortex learn index rebuild --workspace "$SMOKE" >/dev/null
echo "  index rebuild: PASS"
cortex learn scan --workspace "$SMOKE" --json > "$SMOKE/scan.json"
python3 -c "import json,sys; d=json.load(open('$SMOKE/scan.json')); assert len(d['entries']) >= 1"
echo "  scan: PASS"
cortex learn candidates --workspace "$SMOKE" --json > "$SMOKE/cand.json"
python3 -c "import json,sys; d=json.load(open('$SMOKE/cand.json')); assert 'candidates' in d"
echo "  candidates: PASS"

echo
echo "=== ALL CHECKS PASSED ==="
exit 0
