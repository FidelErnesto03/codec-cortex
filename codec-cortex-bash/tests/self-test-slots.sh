#!/usr/bin/env bash
# CORTEX 0.2 — Self-test for Bash port.
# Tests slot marker detection under LC_ALL=C and LC_ALL=C.UTF-8.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/../lib"
source "$LIB_DIR/slot-parser.sh"

pass=0
fail=0

assert_eq() {
    local name="$1" actual="$2" expected="$3"
    if [[ "$actual" == "$expected" ]]; then
        pass=$((pass + 1))
        # echo "  ✔ $name"
    else
        fail=$((fail + 1))
        echo "  ✗ $name: expected '$expected', got '$actual'"
    fi
}

run_tests() {
    local locale_name="$1"
    echo "=== Running 0.2 self-test under $locale_name ==="

    local tmpdir
    tmpdir=$(mktemp -d)
    trap "rm -rf $tmpdir" RETURN

    # Test 1: slot marker OK
    printf '$0:format{cortex:0.2} KNW:x{\xe2\x80\xbb1:"a"}' > "$tmpdir/ok.cortex"
    local result
    result=$(cortex_slots_scan_slot_markers "$tmpdir/ok.cortex" | awk '{print $1}')
    assert_eq "slot-marker-ok" "$result" "OK"

    # Test 2: homoglyph bullet (• U+2022)
    printf 'KNW:x{\xe2\x80\xa21:"a"}' > "$tmpdir/hg_bullet.cortex"
    result=$(cortex_slots_scan_slot_markers "$tmpdir/hg_bullet.cortex" | awk '{print $1}')
    assert_eq "homoglyph-bullet" "$result" "L020_HOMOGLYPH_MARKER"

    # Test 3: homoglyph middle dot (· U+00B7)
    printf 'KNW:x{\xc2\xb71:"a"}' > "$tmpdir/hg_mid.cortex"
    result=$(cortex_slots_scan_slot_markers "$tmpdir/hg_mid.cortex" | awk '{print $1}')
    assert_eq "homoglyph-middledot" "$result" "L020_HOMOGLYPH_MARKER"

    # Test 4: homoglyph bullet operator (∙ U+2219)
    printf 'KNW:x{\xe2\x88\x991:"a"}' > "$tmpdir/hg_bop.cortex"
    result=$(cortex_slots_scan_slot_markers "$tmpdir/hg_bop.cortex" | awk '{print $1}')
    assert_eq "homoglyph-bulletop" "$result" "L020_HOMOGLYPH_MARKER"

    # Test 5: homoglyph black circle (● U+25CF)
    printf 'KNW:x{\xe2\x97\x8f1:"a"}' > "$tmpdir/hg_bc.cortex"
    result=$(cortex_slots_scan_slot_markers "$tmpdir/hg_bc.cortex" | awk '{print $1}')
    assert_eq "homoglyph-blackcircle" "$result" "L020_HOMOGLYPH_MARKER"

    # Test 6: zero index
    printf 'KNW:x{\xe2\x80\xbb0:"a"}' > "$tmpdir/zero.cortex"
    result=$(cortex_slots_scan_slot_markers "$tmpdir/zero.cortex" | awk '{print $1}')
    assert_eq "zero-index" "$result" "L022_SLOT_INDEX_ZERO"

    # Test 7: leading zero
    printf 'KNW:x{\xe2\x80\xbb01:"a"}' > "$tmpdir/lz.cortex"
    result=$(cortex_slots_scan_slot_markers "$tmpdir/lz.cortex" | awk '{print $1}')
    assert_eq "leading-zero" "$result" "L023_SLOT_INDEX_LEADING_ZERO"

    # Test 8: huge index
    printf 'KNW:x{\xe2\x80\xbb999999999999999:"a"}' > "$tmpdir/huge.cortex"
    result=$(cortex_slots_scan_slot_markers "$tmpdir/huge.cortex" | awk '{print $1}')
    assert_eq "huge-index" "$result" "I057_SLOT_INDEX_OUT_OF_RANGE"

    # Test 9: hash domain produces 71-char sha256:hex
    printf '$0:KERNEL\n' > "$tmpdir/hash_input.cortex"
    result=$(cortex_slots_hash "$tmpdir/hash_input.cortex")
    local hash_len=${#result}
    assert_eq "hash-length" "$hash_len" "71"
    case "$result" in
        sha256:*) ;;
        *) assert_eq "hash-prefix" "$result" "should-start-with-sha256:";;
    esac

    # Test 10: hash deterministic
    local h1 h2
    h1=$(cortex_slots_hash "$tmpdir/hash_input.cortex")
    h2=$(cortex_slots_hash "$tmpdir/hash_input.cortex")
    assert_eq "hash-deterministic" "$h1" "$h2"

    # Test 11: hash differs from raw SHA-256
    # Raw SHA-256 of empty: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    printf '' > "$tmpdir/empty.cortex"
    result=$(cortex_slots_hash "$tmpdir/empty.cortex")
    if [[ "$result" != "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" ]]; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "  ✗ hash-domain-differs-from-raw: hash matched raw SHA-256 (no domain separation)"
    fi

    # Test 12: I058 structural marker in 0.1 doc
    printf '$0:format{cortex:0.1}\nKNW:x{\xe2\x80\xbb1:"a"}' > "$tmpdir/i058.cortex"
    result=$(cortex_slots_check_mixed_surface_01 "$tmpdir/i058.cortex" | awk '{print $1}')
    assert_eq "i058-structural" "$result" "I058_MIXED_SURFACE_VERSION"

    # Test 13: No I058 for marker in string
    printf '$0:format{cortex:0.1}\nKNW:x{topic:"a \xe2\x80\xbb b"}' > "$tmpdir/no_i058.cortex"
    result=$(cortex_slots_check_mixed_surface_01 "$tmpdir/no_i058.cortex" | awk '{print $1}')
    assert_eq "no-i058-in-string" "$result" "OK"

    echo "  $locale_name: $pass passed, $fail failed"
}

# Run under LC_ALL=C
export LC_ALL=C
run_tests "LC_ALL=C"

# Run under LC_ALL=C.UTF-8 (if available)
pass=0
fail=0
if locale -a 2>/dev/null | grep -q "^C\.UTF-8$"; then
    export LC_ALL=C.UTF-8
    run_tests "LC_ALL=C.UTF-8"
else
    echo "=== Skipping LC_ALL=C.UTF-8 (locale not available) ==="
fi

echo ""
echo "=== Final: $pass passed, $fail failed ==="
if ((fail == 0)); then
    echo "PASS"
    exit 0
else
    echo "FAIL"
    exit 1
fi
