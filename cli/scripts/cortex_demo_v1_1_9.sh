#!/bin/bash
# Demo of codec-cortex v1.1.9 — incomplete $0 repair + hardened sentinel checks.
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
run_cortex() { "${CORTEX_CMD[@]}" "$@"; return $?; }
OUT="${TMPDIR:-/tmp}/cortex_demo_v1_1_9"; rm -rf "$OUT"; mkdir -p "$OUT"; cd "$OUT" || exit 2
FAILURES=0
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; FAILURES=$((FAILURES+1)); }

safe_name() { printf '%s' "$1" | tr -c 'A-Za-z0-9_' '_'; }

printf '%s\n' "=== Fix 1: recover repairs existing but incomplete \$0 ==="
cat > incomplete_glossary.cortex <<'EOF'
$0: GLOSSARY
# IDN | identity | attrs | B | Semantic | Identity

$1: CONTENT
IDN:package{name:"legacy"}
KNW:topic{topic:"x", content:"y", status:"current"}
EOF
json_out=$(run_cortex recover incomplete_glossary.cortex --out fixed_incomplete.cortex --embed-aud-rsk --format json 2>&1)
rc=$?
[ "$rc" -eq 0 ] && pass "recover returns 0 for repaired incomplete glossary" || fail "recover rc=$rc: $json_out"
echo "$json_out" | grep -q 'W012_INCOMPLETE_GLOSSARY_REPAIRED' && pass "W012 diagnostic emitted" || fail "W012 diagnostic missing"
run_cortex verify fixed_incomplete.cortex --strict >/tmp/v119_verify_incomplete.log 2>&1
[ "$?" -eq 0 ] && pass "repaired artifact verifies strict" || fail "repaired artifact does not verify: $(cat /tmp/v119_verify_incomplete.log)"
run_cortex render fixed_incomplete.cortex --mode audit --profile full > fixed_incomplete.md 2>/tmp/v119_render.log
[ "$?" -eq 0 ] && grep -q 'KNW:topic' fixed_incomplete.md && pass "recovered KNW visible in HCORTEX" || fail "recovered KNW not visible"
grep -q 'AUD:recovery' fixed_incomplete.md && pass "AUD recovery visible" || fail "AUD recovery missing"
grep -q 'RSK:incomplete_glossary_repaired' fixed_incomplete.md && pass "RSK incomplete glossary visible" || fail "RSK incomplete glossary missing"

printf '\n%s\n' "=== Fix 2: recover chooses a truly free section ==="
cat > many_sections.cortex <<'EOF'
$0: GLOSSARY
# IDN | identity | attrs | B | Semantic | Identity
# FCS | focus | attrs | H | Working | Focus
# OBJ | objective | attrs | H | Working | Objective

IDN:agent{name:"legacy"}
FCS:primary{what:"x", priority:"high", status:"current", survive:"min"}
OBJ:main{goal:"y", status:"current", success:"z", survive:"min"}
EOF
for i in $(seq 1 100); do printf '\n$%s: EXISTING %s\n' "$i" "$i" >> many_sections.cortex; done
run_cortex recover many_sections.cortex --out many_fixed.cortex >/tmp/v119_recover_many.log 2>&1
[ "$?" -eq 0 ] && grep -q '^\$101: RECOVERED CONTENT' many_fixed.cortex && pass "RECOVERED CONTENT uses first free section \$101" || fail "RECOVERED CONTENT did not use free section: $(cat /tmp/v119_recover_many.log)"

printf '\n%s\n' "=== Fix 3: sentinel demo validates E034 explicitly ==="
for sentinel in null none nil undefined n/a tbd '???' '-' '--'; do
    fname="sentinel_$(safe_name "$sentinel").cortex"
    cat > "$fname" <<CORTEX_EOF
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
    verify_out=$(run_cortex verify "$fname" --strict --kind brain 2>&1)
    rc=$?
    if [ "$rc" -ne 0 ] && echo "$verify_out" | grep -q 'E034_CRITICAL_REQUIRED_FIELD_EMPTY'; then
        pass "verify rejects CNST.rule:${sentinel} with E034"
    else
        fail "expected E034 for sentinel ${sentinel}; rc=$rc; output=$verify_out"
    fi
done

printf '\n%s\n' "=========================================="
[ "$FAILURES" -eq 0 ] && echo "ALL v1.1.9 FIXES VERIFIED" && exit 0 || echo "FAILED: $FAILURES check(s)" && exit 1
