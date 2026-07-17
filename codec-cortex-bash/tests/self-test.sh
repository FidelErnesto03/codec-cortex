#!/usr/bin/env bash
set -u -o pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/bin/codec-cortex"
tmp=$(mktemp -d "${TMPDIR:-/tmp}/ccx-selftest.XXXXXX")
trap 'rm -rf "$tmp"' EXIT INT TERM
fail=0
"$BIN" canonicalize "$ROOT/tests/fixtures/quick.cortex" >"$tmp/canonical.cortex" || exit $?
cmp -s "$tmp/canonical.cortex" "$ROOT/tests/fixtures/quick.canonical.cortex" || { echo 'FAIL canonical parity'; fail=1; }
"$BIN" to-hcortex "$ROOT/tests/fixtures/quick.cortex" >"$tmp/hcortex.md" || exit $?
cmp -s "$tmp/hcortex.md" "$ROOT/tests/fixtures/quick.hcortex.md" || { echo 'FAIL HCORTEX render parity'; fail=1; }
"$BIN" from-hcortex "$tmp/hcortex.md" >"$tmp/roundtrip.cortex" || exit $?
cmp -s "$tmp/roundtrip.cortex" "$ROOT/tests/fixtures/quick.roundtrip.cortex" || { echo 'FAIL HCORTEX compile parity'; fail=1; }
printf '# missing header\n' >"$tmp/bad.md"
"$BIN" parse-hcortex "$tmp/bad.md" >"$tmp/bad.json"
jq -e 'any(.diagnostics[];.code=="H400")' "$tmp/bad.json" >/dev/null || { echo 'FAIL H400 diagnostic'; fail=1; }
((fail==0)) || exit 1
echo 'PASS: parser, C14N, HCORTEX render/compile and diagnostics match Python goldens.'
