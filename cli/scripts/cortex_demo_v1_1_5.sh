#!/bin/bash
# Demo of codec-cortex v1.1.5 — $0 section integrity.
#
# Tests the fixes:
#   P0-1: verify --strict rejects operational entries in $0 (E033)
#   P0-2: FCS/OBJ under $0 do not satisfy Nivel 2
#   P0-3: recover entry-first moves payload to $1: RECOVERED CONTENT
#   P0-4: cortex add --section $0 rejects operational entries
#   P1-5: HCORTEX warns when $0 contains operational entries

set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT=""
for candidate in "$SCRIPT_DIR/.." "$SCRIPT_DIR/../.." "$SCRIPT_DIR" "."; do
    candidate_abs="$(cd "$candidate" 2>/dev/null && pwd)"
    if [ -d "$candidate_abs/src/cortex" ] && [ -f "$candidate_abs/BENCHMARK.md" ]; then
        PROJECT_ROOT="$candidate_abs"
        break
    fi
done

if [ -n "$PROJECT_ROOT" ]; then
    export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
    CORTEX_CMD=(python -m cortex)
elif command -v cortex >/dev/null 2>&1; then
    CORTEX_CMD=(cortex)
else
    echo "ERROR: cannot locate cortex CLI." >&2
    exit 2
fi

run_cortex() {
    "${CORTEX_CMD[@]}" "$@" 2>/dev/null
    return $?
}

OUT="${TMPDIR:-/tmp}/cortex_demo_v1_1_5"
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

echo "=== P0-1: verify rejects operational entries in section zero ==="
cat > bad_zero.cortex <<'EOF'
$0: BAD GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective

IDN:agent{name:"bad-brain"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
EOF
run_cortex verify bad_zero.cortex --strict --kind brain >/dev/null 2>&1
rc=$?
expect_rc_nonzero "verify rejects FCS/OBJ in section zero" $rc

echo
echo "=== P0-2: FCS/OBJ under section zero do not satisfy Nivel 2 ==="
# verify output should mention E024 (no active FCS/OBJ outside section zero)
out=$(run_cortex verify bad_zero.cortex --strict --kind brain 2>&1)
if echo "$out" | grep -q "E024"; then
    echo "PASS: E024 fired (FCS/OBJ in section zero don't count)"
else
    echo "FAIL: E024 not fired"
    FAILURES=$((FAILURES + 1))
fi

echo
echo "=== P0-3: recover entry-first moves payload to section one ==="
cat > legacy_entry.cortex <<'EOF'
IDN:package{name:"legacy"}
KNW:topic{topic:"x", content:"y", status:"current"}
EOF
run_cortex recover legacy_entry.cortex --out legacy_fixed.cortex --embed-aud-rsk >/dev/null
expect_rc_zero "recover entry-first" $?
run_cortex verify legacy_fixed.cortex --strict >/dev/null 2>&1
expect_rc_zero "verify --strict on recovered entry-first" $?
# Check HCORTEX shows the payload
out=$(run_cortex render legacy_fixed.cortex --mode audit --profile full 2>&1)
if echo "$out" | grep -q "IDN" && echo "$out" | grep -q "KNW"; then
    echo "PASS: HCORTEX shows recovered payload"
else
    echo "FAIL: HCORTEX does not show recovered payload"
    FAILURES=$((FAILURES + 1))
fi

echo
echo "=== P0-4: add --section zero rejects operational entries ==="
run_cortex new brain --out brain.cortex --force >/dev/null
run_cortex add brain.cortex --section '$0' --sigil NXT --name bad \
    --value 'action:"x", trigger:"y", status:"current", survive:"min"' --force >/dev/null 2>&1
rc=$?
expect_rc_nonzero "add NXT to section zero rejected" $rc

echo
echo "=== P1-5: HCORTEX warns about section zero operational entries ==="
out=$(run_cortex render bad_zero.cortex --mode audit --profile full 2>&1)
if echo "$out" | grep -qi "WARNING"; then
    echo "PASS: HCORTEX warns about section zero entries"
else
    echo "FAIL: HCORTEX does not warn about section zero entries"
    FAILURES=$((FAILURES + 1))
fi

echo
echo "=========================================="
if [ "$FAILURES" -eq 0 ]; then
    echo "ALL v1.1.5 FIXES VERIFIED"
    exit 0
else
    echo "FAILED: $FAILURES check(s) did not pass"
    exit 1
fi
