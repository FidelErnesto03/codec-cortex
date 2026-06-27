#!/bin/bash
# Demo of codec-cortex v1.1.6 — semantic emptiness + recovery conformant exit.
#
# Tests:
#   P0-1: E034 for empty critical fields ("", "   ", null)
#   P0-2: FCS/OBJ with empty fields do not satisfy Nivel 2
#   P1-4: recover moves ops out of $0 even if $0 exists
#   P1-5: recover returns non-zero if not conformant

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

OUT="${TMPDIR:-/tmp}/cortex_demo_v1_1_6"
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

echo "=== Setup ==="
run_cortex new brain --name demo --out brain.cortex --force >/dev/null
expect_rc_zero "new brain" $?

echo
echo "=== P0-1: E034 for empty critical field ==="
# Create a brain with FCS what="" by writing the file directly
# (cortex update --force cannot persist non-bypassable errors, which is correct)
cat > empty_fcs.cortex <<'EOF'
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective
# CNST | constraint | attrs | H | Prefrontal | Constraint
# WRK | work | attrs | M | Working | Work
# STP | step | attrs | M | Working | Step
# STAT | status | attrs | B | Semantic | Status
# REF | reference | attrs | B | Semantic | Reference
# AUD | audit | attrs | M | Prefrontal | Audit
# RSK | risk | attrs | M | Prefrontal | Risk
# NXT | next | attrs | M | Working | Next
# SES | session | attrs | M | Episodic | Session
# LNG | lesson | attrs | M | Episodic | Lesson
# DIAG | diagram | bloque | M | Episodic/Visual | Diagram
# KNW | knowledge | attrs | B | Semantic | Knowledge
# ! | rule | attrs | H | Prefrontal | Rule

$1: IDENTITY

IDN:agent{name:"test"}
DOM:workspace{area:"test"}

$2: ACTIVE WORK

FCS:primary{what:"", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
WRK:state{phase:"active", current:"work", blocked:false, survive:"work"}
STP:next{action:"x", reason:"y", owner:"agent", status:"current", survive:"min"}

$3: GOVERNANCE

CNST:self_contained{rule:"test", severity:"blocking", survive:"min"}
EOF
run_cortex verify empty_fcs.cortex --strict --kind brain >/dev/null 2>&1
rc=$?
expect_rc_nonzero "verify catches empty FCS field (E034)" $rc
out=$(run_cortex verify empty_fcs.cortex --strict --kind brain 2>&1)
if echo "$out" | grep -q "E034"; then
    echo "PASS: E034 in verify output"
else
    echo "FAIL: E034 not in verify output"
    FAILURES=$((FAILURES + 1))
fi

echo
echo "=== P0-2: empty FCS does not satisfy Nivel 2 ==="
if echo "$out" | grep -q "E024"; then
    echo "PASS: E024 fired (empty FCS doesn't count as active)"
else
    echo "FAIL: E024 not fired"
    FAILURES=$((FAILURES + 1))
fi

echo
echo "=== P1-4: recover moves ops from existing $0 ==="
# Reset brain
run_cortex new brain --name demo --out brain2.cortex --force >/dev/null
# Create a file with ops mixed into $0
cat > mixed_zero.cortex <<'EOF'
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective

IDN:agent{name:"mixed"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
EOF
run_cortex recover mixed_zero.cortex --out mixed_fixed.cortex --embed-aud-rsk >/dev/null 2>&1
rc=$?
expect_rc_zero "recover mixed-zero file" $rc
# Check that $1 has the moved entries (HCORTEX shows them)
out=$(run_cortex render mixed_fixed.cortex --mode audit --profile full 2>&1)
if echo "$out" | grep -q "IDN" && echo "$out" | grep -q "FCS" && echo "$out" | grep -q "OBJ"; then
    echo "PASS: moved entries visible in HCORTEX"
else
    echo "FAIL: moved entries not visible in HCORTEX"
    FAILURES=$((FAILURES + 1))
fi

echo
echo "=== P1-5: recover returns non-zero if not conformant ==="
# A file with a critical sigil that has empty required fields
# (recovery cannot fix semantic emptiness — it can only move entries
# and reconstruct $0, not fill in missing content)
cat > unfixable.cortex <<'EOF'
$0: GLOSSARY

# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective

$1: X

IDN:agent{name:"unfixable"}
FCS:primary{what:"", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"", status:"current", success:"z", survive:"min"}
EOF
run_cortex recover unfixable.cortex --out unfixable_fixed.cortex >/dev/null 2>&1
rc=$?
# Recovery moves entries to $1 and reconstructs $0, but E034 (empty fields)
# is non-bypassable and recovery cannot fix it → non-zero exit
expect_rc_nonzero "recover returns non-zero for semantically empty file" $rc

echo
echo "=== P1-5b: recover returns zero for conformant brain ==="
run_cortex recover brain2.cortex --out brain2_recovered.cortex >/dev/null 2>&1
rc=$?
expect_rc_zero "recover returns zero for valid brain" $rc

echo
echo "=========================================="
if [ "$FAILURES" -eq 0 ]; then
    echo "ALL v1.1.6 FIXES VERIFIED"
    exit 0
else
    echo "FAILED: $FAILURES check(s) did not pass"
    exit 1
fi
