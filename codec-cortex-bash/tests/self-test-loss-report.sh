#!/usr/bin/env bash
# Self-test: bash surface emits the reference loss report byte-for-byte.
set -u
SELF_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SELF_DIR/../.." && pwd)"
BIN="$ROOT/codec-cortex-bash/bin/codec-cortex"
LOSS="$ROOT/conformance/1.0/loss"
passed=0
failed=0

check() { # label expected_file actual_file
  if cmp -s "$2" "$3"; then
    printf 'PASS %s\n' "$1"; passed=$((passed + 1))
  else
    printf 'FAIL %s\n' "$1"; diff "$2" "$3" | head -10; failed=$((failed + 1))
  fi
}

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

for fixture in clean L402_comment L403_whitespace L405_open_attr_order bare_glossary; do
  "$BIN" loss-report "$LOSS/$fixture.cortex" >"$tmp/$fixture.json" 2>"$tmp/$fixture.err"
  check "loss-report $fixture" "$LOSS/expected/$fixture.json" "$tmp/$fixture.json"
done

# G042: a glossary title is not 1.0 grammar.
sed 's/^\$0:KERNEL$/$0: Titulo/' "$LOSS/clean.cortex" >"$tmp/title.cortex"
if "$BIN" validate "$tmp/title.cortex" 2>"$tmp/title.err"; then
  printf 'FAIL glossary title rejected\n'; failed=$((failed + 1))
else
  if grep -q G042_GLOSSARY_HEADER_INVALID "$tmp/title.err"; then
    printf 'PASS glossary title rejected\n'; passed=$((passed + 1))
  else
    printf 'FAIL glossary title rejected (wrong error)\n'; failed=$((failed + 1))
  fi
fi

printf '\n=== Final: %s passed, %s failed ===\n' "$passed" "$failed"
[[ $failed -eq 0 ]] && printf 'PASS\n' && exit 0
exit 1
