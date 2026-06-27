#!/bin/bash
# Demo of codec-cortex v1.1.7 — null handling + recovery section isolation.
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
run_cortex() { "${CORTEX_CMD[@]}" "$@" 2>/dev/null; return $?; }

OUT="${TMPDIR:-/tmp}/cortex_demo_v1_1_7"
rm -rf "$OUT"; mkdir -p "$OUT"; cd "$OUT"
FAILURES=0
expect_rc_zero() { [ "$2" -ne 0 ] && echo "FAIL: $1 (rc=$2)" && FAILURES=$((FAILURES+1)) || echo "PASS: $1"; }
expect_rc_nonzero() { [ "$2" -eq 0 ] && echo "FAIL: $1 (rc=0)" && FAILURES=$((FAILURES+1)) || echo "PASS: $1"; }

echo "=== P0-1: verify rejects OBJ.success:null ==="
cat > obj_null.cortex <<'EOF'
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective
# CNST | constraint | attrs | H | Prefrontal | Constraint
# WRK | work | attrs | M | Working | Work
# STP | step | attrs | M | Working | Step
# DOM | domain | attrs | B | Semantic | Domain

$1: IDENTITY

IDN:agent{name:"test"}
DOM:workspace{area:"test"}

$2: ACTIVE WORK

FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:null, survive:"min"}
WRK:state{phase:"active", current:"work", blocked:false, survive:"work"}
STP:next{action:"x", reason:"y", owner:"agent", status:"current", survive:"min"}

$3: GOVERNANCE

CNST:self_contained{rule:"test", severity:"blocking", survive:"min"}
EOF
run_cortex verify obj_null.cortex --strict --kind brain >/dev/null 2>&1
expect_rc_nonzero "verify rejects OBJ.success:null" $?
out=$(run_cortex verify obj_null.cortex --strict --kind brain 2>&1)
echo "$out" | grep -q "E034" && echo "PASS: E034 in output" || { echo "FAIL: E034 not in output"; FAILURES=$((FAILURES+1)); }

echo
echo "=== P0-2: verify rejects CNST.rule:null ==="
cat > cnst_null.cortex <<'EOF'
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective
# CNST | constraint | attrs | H | Prefrontal | Constraint
# WRK | work | attrs | M | Working | Work
# STP | step | attrs | M | Working | Step
# DOM | domain | attrs | B | Semantic | Domain

$1: IDENTITY

IDN:agent{name:"test"}
DOM:workspace{area:"test"}

$2: ACTIVE WORK

FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
WRK:state{phase:"active", current:"work", blocked:false, survive:"work"}
STP:next{action:"x", reason:"y", owner:"agent", status:"current", survive:"min"}

$3: GOVERNANCE

CNST:self_contained{rule:null, severity:"blocking", survive:"min"}
EOF
run_cortex verify cnst_null.cortex --strict --kind brain >/dev/null 2>&1
expect_rc_nonzero "verify rejects CNST.rule:null" $?
out=$(run_cortex verify cnst_null.cortex --strict --kind brain 2>&1)
echo "$out" | grep -q "E034" && echo "PASS: E034 in output" || { echo "FAIL: E034 not in output"; FAILURES=$((FAILURES+1)); }

echo
echo "=== P0-3: update --set rule=null blocked ==="
run_cortex new brain --out brain.cortex --force >/dev/null
run_cortex update brain.cortex CNST:self_contained --set rule=null --force >/dev/null 2>&1
expect_rc_nonzero "update --set rule=null blocked" $?
# Verify file not modified
grep -q 'rule:"This brain.cortex' brain.cortex && echo "PASS: file not modified" || { echo "FAIL: file modified"; FAILURES=$((FAILURES+1)); }

echo
echo "=== P1-4: recover uses dedicated section when section 1 exists ==="
cat > mixed_existing.cortex <<'EOF'
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective
# CNST | constraint | attrs | H | Prefrontal | Constraint
# WRK | work | attrs | M | Working | Work
# STP | step | attrs | M | Working | Step
# DOM | domain | attrs | B | Semantic | Domain

IDN:agent{name:"mixed"}
DOM:workspace{area:"existing"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}

$1: EXISTING

DOM:extra{area:"extra"}
EOF
run_cortex recover mixed_existing.cortex --out mixed_fixed.cortex >/dev/null 2>&1
# recover may return non-zero if the brain is not fully conformant
# (e.g. missing $2 section); the important thing is the file is written
# and $99 is used instead of overwriting $1
if [ -f mixed_fixed.cortex ]; then
    echo "PASS: recover wrote output file"
else
    echo "FAIL: recover did not write output file"
    FAILURES=$((FAILURES+1))
fi
# $99 should exist with RECOVERED CONTENT
grep -q 'RECOVERED CONTENT' mixed_fixed.cortex && echo "PASS: RECOVERED CONTENT section created" || { echo "FAIL: no RECOVERED CONTENT"; FAILURES=$((FAILURES+1)); }
# $1 should still be EXISTING
grep -q 'EXISTING' mixed_fixed.cortex && echo "PASS: section 1 preserved" || { echo "FAIL: section 1 overwritten"; FAILURES=$((FAILURES+1)); }

echo
echo "=== P1-5: recover adds RSK for moved live state ==="
out=$(run_cortex recover mixed_existing.cortex --out mixed_fixed2.cortex 2>&1)
echo "$out" | grep -q "W011_RECOVERED_LIVE_STATE" && echo "PASS: W011 warning for moved FCS" || { echo "FAIL: no W011 warning"; FAILURES=$((FAILURES+1)); }

echo
echo "=========================================="
[ "$FAILURES" -eq 0 ] && echo "ALL v1.1.7 FIXES VERIFIED" && exit 0 || echo "FAILED: $FAILURES check(s)" && exit 1
