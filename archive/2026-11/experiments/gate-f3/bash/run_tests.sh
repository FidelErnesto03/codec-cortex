#!/bin/bash
# Test runner for Bash C14N-0.1 implementation
# Runs all 40 conformance test cases and produces results.json
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
C14N="$SCRIPT_DIR/c14n.sh"
MANIFEST="$REPO_DIR/conformance/c14n/corpus/manifest.json"
CORPUS_DIR="$REPO_DIR/conformance/c14n/corpus"
REPORT_DIR="$SCRIPT_DIR/results"

mkdir -p "$REPORT_DIR"

PASS=0
FAIL=0
TOTAL=0
RESULTS_JSON='{"canonicalization":"C14N-0.1","results":{'

# Parse manifest to get all test cases
CASES=$(python3 -c "
import json
with open('$MANIFEST') as f:
    m = json.load(f)
for c in m['cases']:
    print(c['id'] + '|' + c['input'] + '|' + c['canonical'] + '|' + c['report'])
")

echo "Running C14N-0.1 tests..."
echo "====================="
echo ""

FIRST=true

while IFS='|' read -r case_id input_path canonical_path report_path; do
    [ -z "$case_id" ] && continue

    INPUT_PATH="$REPO_DIR/$input_path"
    CANONICAL_PATH="$REPO_DIR/$canonical_path"
    REPORT_PATH="$REPO_DIR/$report_path"

    TOTAL=$((TOTAL+1))

    # Run c14n.sh and capture output and report
    CANONICAL_OUTPUT=$(bash "$C14N" "$INPUT_PATH" 2>/tmp/c14n_report.json || true)
    CANONICAL_REPORT=$(cat /tmp/c14n_report.json)

    # Read golden canonical
    GOLDEN_OUTPUT=$(cat "$CANONICAL_PATH")
    GOLDEN_REPORT=$(cat "$REPORT_PATH")

    # Compute hashes
    OUTPUT_SHA=$(echo -n "$CANONICAL_OUTPUT" | sha256sum | cut -d' ' -f1)
    GOLDEN_SHA=$(echo -n "$GOLDEN_OUTPUT" | sha256sum | cut -d' ' -f1)

    # Compare
    if [ "$OUTPUT_SHA" = "$GOLDEN_SHA" ]; then
        STATUS="PASS"
        PASS=$((PASS+1))
    else
        STATUS="FAIL"
        FAIL=$((FAIL+1))
    fi

    # Build delta
    DELTA=""
    if [ "$STATUS" = "FAIL" ]; then
        DELTA=$(diff <(echo "$GOLDEN_OUTPUT") <(echo "$CANONICAL_OUTPUT") || true)
        DELTA="${DELTA//$'\n'/\\n}"
        DELTA="${DELTA//\"/\\\"}"
    fi

    [ "$FIRST" = true ] && FIRST=false || RESULTS_JSON+=","
    RESULTS_JSON+="\"$case_id\":{\"status\":\"$STATUS\",\"outputSha256\":\"$OUTPUT_SHA\",\"goldenSha256\":\"$GOLDEN_SHA\""
    [ -n "$DELTA" ] && RESULTS_JSON+=",\"diff\":\"$DELTA\""
    RESULTS_JSON+="}"

    echo "[$STATUS] $case_id"
    if [ "$STATUS" = "FAIL" ]; then
        echo "  Expected: $GOLDEN_SHA"
        echo "  Got:      $OUTPUT_SHA"
    fi
done <<< "$CASES"

RESULTS_JSON+=",\"summary\":{\"total\":$TOTAL,\"passed\":$PASS,\"failed\":$FAIL}}"

# Write results
echo "$RESULTS_JSON" > "$SCRIPT_DIR/results.json"

echo ""
echo "====================="
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
echo "Saved to $SCRIPT_DIR/results.json"
