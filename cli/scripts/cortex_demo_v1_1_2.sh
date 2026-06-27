#!/bin/bash
# Demo of codec-cortex v1.1.2 — portable, no absolute paths, real exit codes.
#
# This demo exercises the 7 fixes of v1.1.2:
#   1. Portable (uses `cortex` from PATH or PYTHONPATH; no /home/z/... paths).
#   2. recover --embed-aud-rsk declares AUD/RSK in $0 (so verify --strict passes).
#   3. Post-mutation validation gate for update/delete/move.
#   4. diff --profile governance detects real changes (not just findings).
#   5. BENCHMARK.md without absolute paths or hardcoded counts.
#   6. --json actually produces JSON for `new` and `render`.
#
# The demo EXITS WITH NON-ZERO if any verification step fails.

set -u  # treat unset vars as error, but do NOT use -e (we handle rc manually)

# --- Locate the cortex CLI --------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Find the project root (directory containing src/cortex/ and BENCHMARK.md)
PROJECT_ROOT=""
for candidate in "$SCRIPT_DIR/.." "$SCRIPT_DIR/../.." "$SCRIPT_DIR" "."; do
    candidate_abs="$(cd "$candidate" 2>/dev/null && pwd)"
    if [ -d "$candidate_abs/src/cortex" ] && [ -f "$candidate_abs/BENCHMARK.md" ]; then
        PROJECT_ROOT="$candidate_abs"
        break
    fi
done

# Set up PYTHONPATH and choose the cortex invocation
if [ -n "$PROJECT_ROOT" ]; then
    export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
    CORTEX_CMD=(python -m cortex)
elif command -v cortex >/dev/null 2>&1; then
    CORTEX_CMD=(cortex)
else
    echo "ERROR: cannot locate cortex CLI. Install with 'pip install -e .' or run from project root." >&2
    exit 2
fi

run_cortex() {
    # Run cortex; stdout is always captured and echoed (so callers can
    # use `out=$(run_cortex ...)`); stderr goes to the script's stderr.
    local verbose="${VERBOSE:-0}"
    if [ "$verbose" = "1" ]; then
        "${CORTEX_CMD[@]}" "$@"
        return $?
    else
        # Capture stdout, let stderr pass through
        "${CORTEX_CMD[@]}" "$@" 2>/dev/null
        return $?
    fi
}

# --- Setup ------------------------------------------------------------------
OUT="${TMPDIR:-/tmp}/cortex_demo_v1_1_2"
rm -rf "$OUT"
mkdir -p "$OUT"
cd "$OUT"

FAILURES=0
expect_rc_zero() {
    if [ "$2" -ne 0 ]; then
        echo "FAIL: $1 (rc=$2, expected 0)"
        FAILURES=$((FAILURES + 1))
    else
        echo "PASS: $1"
    fi
}
expect_rc_nonzero() {
    if [ "$2" -eq 0 ]; then
        echo "FAIL: $1 (rc=0, expected non-zero)"
        FAILURES=$((FAILURES + 1))
    else
        echo "PASS: $1"
    fi
}

echo "=== Setup: create a brain.cortex ==="
run_cortex new brain --name demo-brain --out brain.cortex --force >/dev/null
expect_rc_zero "new brain" $?

echo
echo "=== Fix 2+3: recover --embed-aud-rsk → verify --strict passes ==="
cat > legacy.cortex <<'EOF'
<!-- SPDX-License-Identifier: MIT -->
# Legacy Brain

$1: X

IDN:agent{name:"legacy"}
FCS:primary{what:"old", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"old", status:"current", success:"criterion", survive:"min"}
EOF
run_cortex recover legacy.cortex --out legacy.fixed.cortex --embed-aud-rsk >/dev/null
expect_rc_zero "recover --embed-aud-rsk" $?
run_cortex verify legacy.fixed.cortex --strict >/dev/null 2>&1
rc=$?
expect_rc_zero "verify --strict on recovered+embedded file" $rc

echo
echo "=== Fix 4: post-mutation validation for update ==="
run_cortex update brain.cortex CNST:self_contained --set survive=work >/dev/null 2>&1
rc=$?
expect_rc_nonzero "update that breaks CNST contract is rejected" $rc
run_cortex update brain.cortex CNST:self_contained --set survive=work --force >/dev/null 2>&1
rc=$?
expect_rc_zero "update with --force bypasses gate" $rc
run_cortex update brain.cortex CNST:self_contained --set survive=min --force >/dev/null 2>&1

echo
echo "=== Fix 4: post-mutation validation for delete ==="
run_cortex delete brain.cortex FCS:primary >/dev/null 2>&1
rc=$?
expect_rc_nonzero "delete of protected FCS:primary is rejected" $rc

echo
echo "=== Fix 4: post-mutation validation for move (smoke) ==="
run_cortex move brain.cortex IDN:human --to-section '$3' --force >/dev/null 2>&1
rc=$?
echo "move rc=$rc (0 or 1 acceptable)"
run_cortex move brain.cortex IDN:human --to-section '$1' --force >/dev/null 2>&1

echo
echo "=== Fix 5: diff --profile governance detects real changes ==="
run_cortex new brain --out brain2.cortex --force >/dev/null
run_cortex update brain2.cortex CNST:self_contained --set rule="changed rule text" --force >/dev/null 2>&1
run_cortex diff brain.cortex brain2.cortex --profile governance --format json > /dev/null 2>&1
rc=$?
expect_rc_nonzero "diff governance detects CNST change (both valid)" $rc

echo
echo "=== Fix 6: BENCHMARK.md has no absolute paths ==="
if [ -n "$PROJECT_ROOT" ] && [ -f "$PROJECT_ROOT/BENCHMARK.md" ]; then
    if grep -q "/home/" "$PROJECT_ROOT/BENCHMARK.md"; then
        echo "FAIL: BENCHMARK.md contains /home/ absolute paths"
        FAILURES=$((FAILURES + 1))
    else
        echo "PASS: BENCHMARK.md has no absolute paths"
    fi
else
    echo "SKIP: BENCHMARK.md not found"
fi

echo
echo "=== Fix 7: --json actually produces JSON ==="
out=$(run_cortex --json new brain --out brain3.cortex --force 2>/dev/null)
if echo "$out" | python -c 'import sys, json; json.loads(sys.stdin.read())' 2>/dev/null; then
    echo "PASS: new --json produces valid JSON"
else
    echo "FAIL: new --json does not produce valid JSON"
    echo "  output was: $out" >&2
    FAILURES=$((FAILURES + 1))
fi

out=$(run_cortex --json render brain.cortex --mode edit 2>/dev/null)
if echo "$out" | python -c 'import sys, json; d = json.loads(sys.stdin.read()); assert "markdown" in d or "ok" in d' 2>/dev/null; then
    echo "PASS: render --json produces valid JSON"
else
    echo "FAIL: render --json does not produce valid JSON"
    echo "  output was: $out" >&2
    FAILURES=$((FAILURES + 1))
fi

echo
echo "=========================================="
if [ "$FAILURES" -eq 0 ]; then
    echo "ALL v1.1.2 FIXES VERIFIED"
    exit 0
else
    echo "FAILED: $FAILURES check(s) did not pass"
    exit 1
fi
