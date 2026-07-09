#!/usr/bin/env bash
# run_regression.sh — run the full CODEC-CORTEX Learning Engine v0.2.0
# regression suite.
#
# Usage:
#   ./scripts/run_regression.sh /ruta/al/proyecto/codec-cortex
#
# Exits 0 only if every check passes.

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

echo "=== CODEC-CORTEX Learning Engine v0.2.0 — Regression Suite ==="
echo "Target: $TARGET"
echo

cd "$TARGET"

# 1. Existing pytest suite (v0.1.0 + base)
echo "[1/6] running existing pytest suite (no coverage gate)..."
if python -m pytest cli/src/tests --no-cov -q --ignore=cli/src/tests/test_learning_engine_v02.py; then
    echo "  PASS"
else
    echo "  FAIL — existing tests did not pass" >&2
    exit 1
fi

# 2. v0.2.0 learning tests
echo
echo "[2/6] running v0.2.0 learning-engine tests..."
if python -m pytest cli/src/tests/test_learning_engine_v02.py --no-cov -q; then
    echo "  PASS"
else
    echo "  FAIL — v0.2.0 tests did not pass" >&2
    exit 1
fi

# 3. compileall sanity
echo
echo "[3/6] running python -m compileall on cli/src..."
if python -m compileall -q cli/src; then
    echo "  PASS"
else
    echo "  FAIL — compileall reported errors" >&2
    exit 1
fi

# 4. pip check
echo
echo "[4/6] running pip check..."
if python -m pip check; then
    echo "  PASS"
else
    echo "  WARN — pip check reported issues (continuing)" >&2
fi

# 5. Forbidden-pattern scans
echo
echo "[5/6] scanning learning engine for forbidden patterns..."

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

# 6. CLI smoke (v0.2.0 session lifecycle)
echo
echo "[6/6] CLI smoke test on a temporary workspace..."
SMOKE=$(mktemp -d)
trap "rm -rf $SMOKE" EXIT

cortex learn init --workspace "$SMOKE" >/dev/null
cortex learn doctor --workspace "$SMOKE" --json > "$SMOKE/doctor.json"
python3 -c "import json,sys; d=json.load(open('$SMOKE/doctor.json')); sys.exit(0 if d['ok'] else 1)"
echo "  doctor: PASS"

cortex learn index rebuild --workspace "$SMOKE" >/dev/null
echo "  index rebuild: PASS"

# v0.2.0 — session lifecycle
cortex session start --workspace "$SMOKE" --input "smoke" --json > "$SMOKE/start.json"
python3 -c "import json,sys; d=json.load(open('$SMOKE/start.json')); sys.exit(0 if d['started'] else 1)"
echo "  session start: PASS"

cortex session status --workspace "$SMOKE" --json > "$SMOKE/status.json"
python3 -c "import json,sys; d=json.load(open('$SMOKE/status.json')); sys.exit(0 if d['active'] else 1)"
echo "  session status: PASS"

cortex session close --workspace "$SMOKE" --input "i" --output "o" --outcome "k" --no-decay --json > "$SMOKE/close.json"
python3 -c "import json,sys; d=json.load(open('$SMOKE/close.json')); sys.exit(0 if d['closed'] else 1)"
echo "  session close: PASS"

# v0.2.0 — policy profile
cortex learn policy profile aggressive --workspace "$SMOKE" --confirm >/dev/null
cortex learn policy show --workspace "$SMOKE" --json > "$SMOKE/pol.json"
python3 -c "
import json,sys
d=json.load(open('$SMOKE/pol.json'))
assert 'lng:2' in d['text'], 'aggressive profile not applied'
"
echo "  policy profile aggressive: PASS"

# v0.2.0 — feedback
cortex learn init --workspace "$SMOKE" --force >/dev/null
cat > "$SMOKE/.cortex/brain.cortex" <<'BRAIN'
# -- $0: GLOSSARY --
GSIG:SES{sigil:"SES", name:"session", type:"attrs", risk:"B", description:"session"}
GSIG:LNG{sigil:"LNG", name:"lesson", type:"attrs", risk:"M", description:"lesson"}
GSIG:CNST{sigil:"CNST", name:"constraint", type:"attrs", risk:"H", description:"hard rule"}
GSIG:IDN{sigil:"IDN", name:"identity", type:"attrs", risk:"B", description:"id"}
GSIG:DOM{sigil:"DOM", name:"domain", type:"attrs", risk:"B", description:"domain"}

# -- $1: IDENTITY --
IDN:agent{name:"a", role:"r"}
DOM:workspace{area:"x", protocol:"CODEC-CORTEX", artifact:"brain.cortex"}

# -- $2: SESSIONS --
SES:foo_1{topic:"foo", outcome:"bar", user_validated:true}
SES:foo_2{topic:"foo", outcome:"bar", user_validated:true}
SES:foo_3{topic:"foo", outcome:"bar", user_validated:true}

# -- $3: GOVERNANCE --
CNST:br{rule:"no", severity:"blocking", survive:"min"}
BRAIN
cortex learn index rebuild --workspace "$SMOKE" >/dev/null
cortex learn feedback --accept --candidate cand_001 --workspace "$SMOKE" --json > "$SMOKE/fb.json"
python3 -c "import json,sys; d=json.load(open('$SMOKE/fb.json')); sys.exit(0 if d['recorded'] else 1)"
echo "  feedback accept: PASS"

cortex learn pre-action --input "benchmarks benchmarks" --workspace "$SMOKE" --json > "$SMOKE/pre.json"
python3 -c "import json,sys; d=json.load(open('$SMOKE/pre.json')); assert 'benchmarks' in d['themes_detected']"
echo "  pre-action: PASS"

cortex learn post-action --workspace "$SMOKE" --json > "$SMOKE/post.json"
python3 -c "import json,sys; d=json.load(open('$SMOKE/post.json')); assert 'candidates_above_threshold' in d"
echo "  post-action: PASS"

echo
echo "=== ALL CHECKS PASSED ==="
exit 0
