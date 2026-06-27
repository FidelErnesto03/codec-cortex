#!/bin/bash
# Demo of codec-cortex v1.1.8 — free section, RSK embed, AUD description, null-like sentinels.
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT=""
for candidate in "$SCRIPT_DIR/.." "$SCRIPT_DIR/../.." "$SCRIPT_DIR" "."; do
    candidate_abs="$(cd "$candidate" 2>/dev/null && pwd)"
    if [ -d "$candidate_abs/src/cortex" ] && [ -f "$candidate_abs/BENCHMARK.md" ]; then
        PROJECT_ROOT="$candidate_abs"; break
    fi
done
if [ -n "$PROJECT_ROOT" ]; then
    export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
    CORTEX_CMD=(python -m cortex)
elif command -v cortex >/dev/null 2>&1; then
    CORTEX_CMD=(cortex)
else
    echo "ERROR: cannot locate cortex CLI." >&2; exit 2
fi
run_cortex() { "${CORTEX_CMD[@]}" "$@" 2>/dev/null; return $?; }
OUT="${TMPDIR:-/tmp}/cortex_demo_v1_1_8"; rm -rf "$OUT"; mkdir -p "$OUT"; cd "$OUT"
FAILURES=0
expect_rc_zero() { [ "$2" -ne 0 ] && echo "FAIL: $1 (rc=$2)" && FAILURES=$((FAILURES+1)) || echo "PASS: $1"; }
expect_rc_nonzero() { [ "$2" -eq 0 ] && echo "FAIL: $1 (rc=0)" && FAILURES=$((FAILURES+1)) || echo "PASS: $1"; }

echo "=== Fix 1: recover finds free section when 1 and 99 exist ==="
cat > full_sections.cortex <<'EOF'
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus

IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}

$1: EXISTING

DOM:workspace{area:"existing"}

$99: EXISTING SPECIAL

DOM:special{area:"special"}
EOF
run_cortex recover full_sections.cortex --out full_fixed.cortex --embed-aud-rsk >/dev/null 2>&1
if [ -f full_fixed.cortex ]; then
    echo "PASS: recover wrote output"
else
    echo "FAIL: recover did not write output"; FAILURES=$((FAILURES+1))
fi
# $1 and $99 should be untouched
grep -q 'EXISTING$' full_fixed.cortex && echo "PASS: section 1 preserved" || { echo "FAIL: section 1 contaminated"; FAILURES=$((FAILURES+1)); }
grep -q 'EXISTING SPECIAL' full_fixed.cortex && echo "PASS: section 99 preserved" || { echo "FAIL: section 99 contaminated"; FAILURES=$((FAILURES+1)); }
# RECOVERED CONTENT should be in a free section (not $1 or $99)
grep -q 'RECOVERED CONTENT' full_fixed.cortex && echo "PASS: RECOVERED CONTENT created" || { echo "FAIL: no RECOVERED CONTENT"; FAILURES=$((FAILURES+1)); }

echo
echo "=== Fix 2+3: embed-aud-rsk inserts RSK and AUD describes real event ==="
out=$(run_cortex recover full_sections.cortex --out full_fixed2.cortex --embed-aud-rsk 2>&1)
# Check AUD event is NOT just glossary_reconstruction
if echo "$out" | grep -q "reconstructed \$0: False"; then
    echo "PASS: reconstructed_glossary is False (not reconstructed)"
else
    echo "FAIL: reconstructed_glossary flag not reported"; FAILURES=$((FAILURES+1))
fi
# Check the file has RSK entries for recovered live state
grep -q 'RSK:recovered_live_fcs' full_fixed2.cortex && echo "PASS: RSK for recovered FCS embedded" || { echo "FAIL: no RSK for FCS"; FAILURES=$((FAILURES+1)); }

echo
echo "=== Fix 4: null-like sentinels blocked ==="
for sentinel in none nil undefined n/a tbd; do
    cat > "null_${sentinel}.cortex" <<CORTEX_EOF
\$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective
# CNST | constraint | attrs | H | Prefrontal | Constraint
# WRK | work | attrs | M | Working | Work
# STP | step | attrs | M | Working | Step
# DOM | domain | attrs | B | Semantic | Domain

\$1: IDENTITY

IDN:agent{name:"test"}
DOM:workspace{area:"test"}

\$2: ACTIVE WORK

FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
WRK:state{phase:"active", current:"work", blocked:false, survive:"work"}
STP:next{action:"x", reason:"y", owner:"agent", status:"current", survive:"min"}

\$3: GOVERNANCE

CNST:self_contained{rule:${sentinel}, severity:"blocking", survive:"min"}
CORTEX_EOF
    run_cortex verify "null_${sentinel}.cortex" --strict --kind brain >/dev/null 2>&1
    rc=$?
    expect_rc_nonzero "verify rejects CNST.rule:${sentinel}" $rc
done

echo
echo "=========================================="
[ "$FAILURES" -eq 0 ] && echo "ALL v1.1.8 FIXES VERIFIED" && exit 0 || echo "FAILED: $FAILURES check(s)" && exit 1
