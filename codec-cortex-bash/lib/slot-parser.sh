#!/usr/bin/env bash
# CORTEX 0.2 — Slot marker byte-level detection in Bash.
# Conformance level: byte-level-marker-detection-only.
#
# This module implements:
#   - slot marker (※ U+203B, E2 80 BB) byte-level detection (LC_ALL=C safe)
#   - homoglyph rejection (L020): • · ∙ ●
#   - slot index validation (L022/L023)
#   - SHA-256 hash with domain CORTEX-C14N-0.2 || 0x00 || canonical_bytes
#
# It does NOT implement the full 0.2 parser. Full parsing is delegated to the
# Python reference implementation.

# Force C locale for byte-level safety
export LC_ALL=C

# Slot marker bytes: E2 80 BB (※ U+203B)
# Homoglyph bytes:
#   • U+2022 = E2 80 A2
#   · U+00B7 = C2 B7
#   ∙ U+2219 = E2 88 99
#   ● U+25CF = E2 97 8F

# scan_slot_markers <input_file>
# Outputs: OK or <CODE> <byte_offset> <detail>
cortex_slots_scan_slot_markers() {
    local input_file="$1"
    if [[ ! -f "$input_file" ]]; then
        echo "IO_ERROR 0 file-not-found: $input_file"
        return 1
    fi
    # Read file as bytes
    local content
    content=$(cat "$input_file" | od -An -tx1 | tr -d ' \n')
    local len=${#content}
    len=$((len / 2))

    local i=0
    while ((i + 5 < len * 2)); do
        # Get 3 bytes starting at i
        local b1 b2 b3
        b1=$(cortex_slots_get_byte "$content" "$i")
        b2=$(cortex_slots_get_byte "$content" "$((i + 1))")
        b3=$(cortex_slots_get_byte "$content" "$((i + 2))")

        # Check for slot marker ※ (e2 80 bb)
        if [[ "$b1" == "e2" && "$b2" == "80" && "$b3" == "bb" ]]; then
            local j=$((i + 3))
            local c
            c=$(cortex_slots_get_byte "$content" "$j")
            # Space/tab after marker = L021
            if [[ "$c" == "20" || "$c" == "09" ]]; then
                echo "L021_INVALID_SLOT_INDEX $i space-after-marker"
                return 0
            fi
            # Zero index
            if [[ "$c" == "30" ]]; then
                local nxt
                nxt=$(cortex_slots_get_byte "$content" "$((j + 1))")
                # Check if next is a digit (leading zero)
                case "$nxt" in
                    30|31|32|33|34|35|36|37|38|39)
                        echo "L023_SLOT_INDEX_LEADING_ZERO $i"
                        return 0
                        ;;
                esac
                echo "L022_SLOT_INDEX_ZERO $i"
                return 0
            fi
            # Nonzero digit check
            case "$c" in
                31|32|33|34|35|36|37|38|39)
                    # Collect digits
                    local start=$j
                    while true; do
                        c=$(cortex_slots_get_byte "$content" "$j")
                        case "$c" in
                            30|31|32|33|34|35|36|37|38|39) j=$((j + 1));;
                            *) break;;
                        esac
                    done
                    local idx_len=$((j - start))
                    if ((idx_len > 10)); then
                        echo "I057_SLOT_INDEX_OUT_OF_RANGE $i overflow"
                        return 0
                    fi
                    # Check for space before colon
                    if [[ "$c" == "20" || "$c" == "09" ]]; then
                        echo "L024_SLOT_INDEX_SEPARATOR $i"
                        return 0
                    fi
                    if [[ "$c" != "3a" ]]; then
                        echo "L021_INVALID_SLOT_INDEX $i expected-colon"
                        return 0
                    fi
                    i=$((j + 1))
                    continue
                    ;;
            esac
            # Non-ASCII byte — could be Unicode digit
            if [[ "$c" > "7f" ]]; then
                echo "L021_INVALID_SLOT_INDEX $i non-ascii-digit"
                return 0
            fi
            echo "L021_INVALID_SLOT_INDEX $i invalid-start-byte-$c"
            return 0
        fi

        # Check for homoglyphs in structural position (after { or ,)
        # • U+2022 = e2 80 a2
        if [[ "$b1" == "e2" && "$b2" == "80" && "$b3" == "a2" ]]; then
            if cortex_slots_is_structural "$content" "$i"; then
                echo "L020_HOMOGLYPH_MARKER $i U+2022-BULLET"
                return 0
            fi
        fi
        # · U+00B7 = c2 b7
        if [[ "$b1" == "c2" && "$b2" == "b7" ]]; then
            if cortex_slots_is_structural "$content" "$i"; then
                echo "L020_HOMOGLYPH_MARKER $i U+00B7-MIDDLE-DOT"
                return 0
            fi
        fi
        # ∙ U+2219 = e2 88 99
        if [[ "$b1" == "e2" && "$b2" == "88" && "$b3" == "99" ]]; then
            if cortex_slots_is_structural "$content" "$i"; then
                echo "L020_HOMOGLYPH_MARKER $i U+2219-BULLET-OPERATOR"
                return 0
            fi
        fi
        # ● U+25CF = e2 97 8f
        if [[ "$b1" == "e2" && "$b2" == "97" && "$b3" == "8f" ]]; then
            if cortex_slots_is_structural "$content" "$i"; then
                echo "L020_HOMOGLYPH_MARKER $i U+25CF-BLACK-CIRCLE"
                return 0
            fi
        fi

        i=$((i + 1))
    done

    echo "OK"
    return 0
}

# Get byte at index from hex string
cortex_slots_get_byte() {
    local hex="$1"
    local idx="$2"
    local pos=$((idx * 2))
    echo "${hex:$pos:2}"
}

# Check if position i is preceded by { or , (skipping whitespace)
cortex_slots_is_structural() {
    local hex="$1"
    local i="$2"
    local k=$((i - 1))
    while ((k >= 0)); do
        local b
        b=$(cortex_slots_get_byte "$hex" "$k")
        if [[ "$b" == "20" || "$b" == "09" ]]; then
            k=$((k - 1))
            continue
        fi
        if [[ "$b" == "7b" || "$b" == "2c" ]]; then
            return 0
        fi
        return 1
    done
    return 0  # start of file is structural
}

# check_mixed_surface_01 <input_file>
# Detects ※ in structural position within a 0.1-declared doc (I058)
cortex_slots_check_mixed_surface_01() {
    local input_file="$1"
    if [[ ! -f "$input_file" ]]; then
        echo "IO_ERROR 0 file-not-found: $input_file"
        return 1
    fi
    local content
    content=$(cat "$input_file" | od -An -tx1 | tr -d ' \n')
    local len=${#content}
    len=$((len / 2))

    local i=0
    while ((i + 5 < len * 2)); do
        local b1 b2 b3
        b1=$(cortex_slots_get_byte "$content" "$i")
        b2=$(cortex_slots_get_byte "$content" "$((i + 1))")
        b3=$(cortex_slots_get_byte "$content" "$((i + 2))")
        if [[ "$b1" == "e2" && "$b2" == "80" && "$b3" == "bb" ]]; then
            if cortex_slots_is_structural "$content" "$i"; then
                # Compute line/col
                local line=1 col=1 idx=0
                while ((idx < i)); do
                    local b
                    b=$(cortex_slots_get_byte "$content" "$idx")
                    if [[ "$b" == "0a" ]]; then
                        line=$((line + 1))
                        col=1
                    else
                        col=$((col + 1))
                    fi
                    idx=$((idx + 1))
                done
                echo "I058_MIXED_SURFACE_VERSION $line $col"
                return 0
            fi
        fi
        i=$((i + 1))
    done
    echo "OK"
    return 0
}

# cortex_slots_hash <canonical_bytes_file>
# Outputs: sha256:<64 hex lowercase>
cortex_slots_hash() {
    local input_file="$1"
    if [[ ! -f "$input_file" ]]; then
        echo "IO_ERROR"
        return 1
    fi
    # Build: SHA-256("CORTEX-C14N-0.2" + 0x00 + canonical_bytes)
    # Use printf to construct the domain prefix, then append file bytes, then sha256sum
    local prefix
    prefix=$(printf 'CORTEX-C14N-0.2\x00' | od -An -tx1 | tr -d ' \n')
    # Combine prefix + file content as binary, hash
    local hash
    hash=$( { printf 'CORTEX-C14N-0.2\x00'; cat "$input_file"; } | sha256sum | awk '{print $1}')
    echo "sha256:$hash"
    return 0
}
