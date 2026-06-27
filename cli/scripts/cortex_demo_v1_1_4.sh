#!/bin/bash
# Demo of codec-cortex v1.1.4 — portable, no absolute paths, real exit codes.
#
# Tests the 6 fixes of v1.1.4:
#   P0-1: E024 non-bypassable → --force cannot delete FCS from brain
#   P0-2: --force cannot degrade operational P0 (FCS/OBJ/CNST:blocking)
#   P0-3: --unsafe-allow-secret-forensics marks artefact as non_conformant
#   P1-4: pytest declared as dev dependency
#   P1-5: this demo exists and is reproducible
#   P1-6: recover adds general RSK even for canonical sigils

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

OUT="${TMPDIR:-/tmp}/cortex_demo_v1_1_4"
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
echo "=== P0-1: --force cannot delete FCS from brain ==="
# Record original file
cp brain.cortex brain_original.cortex
run_cortex delete brain.cortex FCS:primary --force >/dev/null 2>&1
rc=$?
expect_rc_nonzero "delete FCS:primary --force blocked" $rc
# Verify file unchanged
if diff -q brain.cortex brain_original.cortex >/dev/null 2>&1; then
    echo "PASS: file not modified by blocked delete"
else
    echo "FAIL: file was modified despite blocked delete"
    FAILURES=$((FAILURES + 1))
fi

echo
echo "=== P0-2: --force cannot set FCS to done (removes active focus) ==="
run_cortex update brain.cortex FCS:primary --set status=done --force >/dev/null 2>&1
rc=$?
expect_rc_nonzero "update FCS status=done --force blocked" $rc

echo
echo "=== P0-3: --unsafe-allow-secret-forensics marks non_conformant ==="
out=$(run_cortex add brain.cortex --section '$3' --sigil REF --name secret \
    --value 'provider:"x", password:"abc123456"' \
    --create-section --force --unsafe-allow-secret-forensics 2>/dev/null)
rc=$?
expect_rc_zero "add with --unsafe-allow-secret-forensics" $rc
if echo "$out" | python -c 'import sys,json; d=json.loads(sys.stdin.read()); assert "non_conformant_forensic_artifact" in d.get("warning","")' 2>/dev/null; then
    echo "PASS: artefact marked non_conformant_forensic_artifact"
else
    echo "FAIL: non_conformant marker not in output"
    FAILURES=$((FAILURES + 1))
fi
# File must contain the STAT:forensic_quarantine marker
if grep -q "forensic_quarantine" brain.cortex 2>/dev/null; then
    echo "PASS: STAT:forensic_quarantine in file"
else
    echo "FAIL: STAT:forensic_quarantine not in file"
    FAILURES=$((FAILURES + 1))
fi
# verify --strict must still fail
run_cortex verify brain.cortex --strict >/dev/null 2>&1
rc=$?
expect_rc_nonzero "verify --strict on forensic artefact still fails" $rc

echo
echo "=== P1-4: pytest as dev dependency ==="
if grep -q "\[project.optional-dependencies\]" "$PROJECT_ROOT/pyproject.toml" 2>/dev/null && \
   grep -q "pytest" "$PROJECT_ROOT/pyproject.toml" 2>/dev/null; then
    echo "PASS: pytest declared as dev dependency"
else
    echo "FAIL: pytest not in pyproject.toml"
    FAILURES=$((FAILURES + 1))
fi

echo
echo "=== P1-6: recover adds general RSK even for canonical sigils ==="
cat > legacy_canonical.cortex <<'EOF'
IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
EOF
run_cortex recover legacy_canonical.cortex --out legacy_canonical.fixed.cortex --embed-aud-rsk >/dev/null
expect_rc_zero "recover canonical-sigil file" $?
if grep -q "reconstructed_glossary" legacy_canonical.fixed.cortex 2>/dev/null; then
    echo "PASS: general RSK:reconstructed_glossary present"
else
    echo "FAIL: general RSK not in recovered file"
    FAILURES=$((FAILURES + 1))
fi

echo
echo "=========================================="
if [ "$FAILURES" -eq 0 ]; then
    echo "ALL v1.1.4 FIXES VERIFIED"
    exit 0
else
    echo "FAILED: $FAILURES check(s) did not pass"
    exit 1
fi
