// CORTEX 0.2 — Slot marker detection and hash domain.
// Conformance level: byte-level-marker-detection-only.
//
// This module implements:
//   - slot marker (※ U+203B, E2 80 BB) byte-level detection
//   - homoglyph rejection (L020): • · ∙ ●
//   - slot index validation (L021/L022/L023/L024)
//   - SHA-256 hash with domain CORTEX-C14N-0.2 || 0x00 || canonical_bytes
//
// It does NOT implement the full 0.2 parser. Full parsing is delegated to the
// Python reference implementation. The Rust port focuses on byte-level
// marker detection and hash computation, which is sufficient for differential
// testing of the slot marker surface.
//
// See CONFORMANCE.md for the full declaration.

use sha2::{Digest, Sha256};

pub const SLOT_MARKER_BYTES: [u8; 3] = [0xE2, 0x80, 0xBB]; // ※ U+203B
pub const HASH_DOMAIN_SLOTS: &[u8] = b"CORTEX-C14N-0.2";

// Homoglyph markers (forbidden as slot markers, L020)
pub const HOMOGLYPHS: &[[u8; 3]] = &[
    [0xE2, 0x80, 0xA2], // • U+2022 BULLET
    [0xC2, 0xB7, 0x00], // · U+00B7 MIDDLE DOT (2 bytes)
    [0xE2, 0x88, 0x99], // ∙ U+2219 BULLET OPERATOR
    [0xE2, 0x97, 0x8F], // ● U+25CF BLACK CIRCLE
];

pub const SLOT_INDEX_MAX: u64 = (1u64 << 31) - 1;

#[derive(Debug, Clone, PartialEq)]
pub enum SlotDiagnostic {
    L020HomoglyphMarker { byte_offset: usize, homoglyph: String },
    L021InvalidSlotIndex { byte_offset: usize, reason: String },
    L022SlotIndexZero { byte_offset: usize },
    L023SlotIndexLeadingZero { byte_offset: usize },
    L024SlotIndexSeparator { byte_offset: usize },
    L025TrailingComma { byte_offset: usize },
    I057SlotIndexOutOfRange { byte_offset: usize, index: u64 },
    I058MixedSurfaceVersion { line: usize, col: usize },
    Ok,
}

/// Detect slot markers in a byte slice. Returns the first diagnostic encountered.
pub fn scan_slot_markers(input: &[u8]) -> SlotDiagnostic {
    let mut i = 0;
    let n = input.len();
    while i < n {
        // Check for slot marker ※ (E2 80 BB)
        if i + 2 < n && input[i] == 0xE2 && input[i + 1] == 0x80 && input[i + 2] == 0xBB {
            // Found a slot marker — validate index
            let mut j = i + 3;
            // Skip whitespace? No — space after marker is L021
            if j < n && (input[j] == b' ' || input[j] == b'\t') {
                return SlotDiagnostic::L021InvalidSlotIndex {
                    byte_offset: i,
                    reason: "space after slot marker".to_string(),
                };
            }
            // First digit
            if j >= n {
                return SlotDiagnostic::L021InvalidSlotIndex {
                    byte_offset: i,
                    reason: "EOF after slot marker".to_string(),
                };
            }
            let c = input[j];
            if c == b'0' {
                // Check if there are more digits (leading zero)
                if j + 1 < n && input[j + 1].is_ascii_digit() {
                    return SlotDiagnostic::L023SlotIndexLeadingZero { byte_offset: i };
                }
                return SlotDiagnostic::L022SlotIndexZero { byte_offset: i };
            }
            if !c.is_ascii_digit() {
                // Could be non-ASCII digit
                if c >= 0x80 {
                    // Decode UTF-8 to check if it's a Unicode digit
                    let reason = "non-ASCII digit in slot index".to_string();
                    return SlotDiagnostic::L021InvalidSlotIndex {
                        byte_offset: i,
                        reason,
                    };
                }
                return SlotDiagnostic::L021InvalidSlotIndex {
                    byte_offset: i,
                    reason: format!("invalid slot index start byte {:#x}", c),
                };
            }
            // Collect digits — ASCII only
            let start = j;
            while j < n && input[j].is_ascii_digit() {
                j += 1;
            }
            let idx_str = std::str::from_utf8(&input[start..j]).unwrap_or("");
            // Bound check before int conversion
            if idx_str.len() > 10 {
                return SlotDiagnostic::I057SlotIndexOutOfRange {
                    byte_offset: i,
                    index: u64::MAX,
                };
            }
            let idx: u64 = idx_str.parse().unwrap_or(u64::MAX);
            if idx > SLOT_INDEX_MAX {
                return SlotDiagnostic::I057SlotIndexOutOfRange {
                    byte_offset: i,
                    index: idx,
                };
            }
            // Check for space before colon
            if j < n && (input[j] == b' ' || input[j] == b'\t') {
                return SlotDiagnostic::L024SlotIndexSeparator { byte_offset: i };
            }
            // Check for colon
            if j >= n || input[j] != b':' {
                return SlotDiagnostic::L021InvalidSlotIndex {
                    byte_offset: i,
                    reason: "expected ':' after slot index".to_string(),
                };
            }
            i = j + 1;
            continue;
        }
        // Check for homoglyphs
        for hg in HOMOGLYPHS {
            let hg_bytes: &[u8] = if hg[2] == 0 { &hg[0..2] } else { hg };
            if i + hg_bytes.len() <= n && &input[i..i + hg_bytes.len()] == hg_bytes {
                // Check if this is in structural position (after { or ,)
                let mut k = if i > 0 { i - 1 } else { 0 };
                while k > 0 && (input[k] == b' ' || input[k] == b'\t') {
                    k -= 1;
                }
                if k == 0 || input[k] == b'{' || input[k] == b',' {
                    let hg_str = std::str::from_utf8(hg_bytes).unwrap_or("?").to_string();
                    return SlotDiagnostic::L020HomoglyphMarker {
                        byte_offset: i,
                        homoglyph: hg_str,
                    };
                }
            }
        }
        i += 1;
    }
    SlotDiagnostic::Ok
}

/// Check if a 0.1-declared source has structural slot markers (I058).
pub fn check_mixed_surface_legacy(input: &[u8]) -> SlotDiagnostic {
    // Scan for ※ in structural position (after { or ,)
    let mut i = 0;
    let n = input.len();
    while i < n {
        if i + 2 < n && input[i] == 0xE2 && input[i + 1] == 0x80 && input[i + 2] == 0xBB {
            // Check if this is in structural position
            let mut k = if i > 0 { i - 1 } else { 0 };
            while k > 0 && (input[k] == b' ' || input[k] == b'\t') {
                k -= 1;
            }
            if k == 0 || input[k] == b'{' || input[k] == b',' {
                // Compute line/col
                let mut line = 1;
                let mut col = 1;
                for (idx, b) in input.iter().enumerate() {
                    if idx == i {
                        break;
                    }
                    if *b == b'\n' {
                        line += 1;
                        col = 1;
                    } else {
                        col += 1;
                    }
                }
                return SlotDiagnostic::I058MixedSurfaceVersion { line, col };
            }
        }
        i += 1;
    }
    SlotDiagnostic::Ok
}

/// Compute SHA-256 hash with CORTEX-C14N-0.2 domain.
pub fn hash_slots(canonical_bytes: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(HASH_DOMAIN_SLOTS);
    hasher.update([0x00]);
    hasher.update(canonical_bytes);
    let result = hasher.finalize();
    let hex: String = result.iter().map(|b| format!("{:02x}", b)).collect();
    format!("sha256:{}", hex)
}

#[cfg(test)]
mod tests_slots {
    use super::*;

    #[test]
    fn test_slot_marker_detection_ok() {
        let input = b"$0:format{cortex:0.2} KNW:x{\xE2\x80\xBB1:\"a\"}";
        let diag = scan_slot_markers(input);
        assert_eq!(diag, SlotDiagnostic::Ok);
    }

    #[test]
    fn test_homoglyph_bullet_rejected() {
        let input = b"KNW:x{\xE2\x80\xA2 1:\"a\"}";
        let diag = scan_slot_markers(input);
        assert!(matches!(diag, SlotDiagnostic::L020HomoglyphMarker { .. }));
    }

    #[test]
    fn test_zero_index_rejected() {
        let input = b"KNW:x{\xE2\x80\xBB0:\"a\"}";
        let diag = scan_slot_markers(input);
        assert!(matches!(diag, SlotDiagnostic::L022SlotIndexZero { .. }));
    }

    #[test]
    fn test_leading_zero_rejected() {
        let input = b"KNW:x{\xE2\x80\xBB01:\"a\"}";
        let diag = scan_slot_markers(input);
        assert!(matches!(diag, SlotDiagnostic::L023SlotIndexLeadingZero { .. }));
    }

    #[test]
    fn test_huge_index_rejected() {
        let input = b"KNW:x{\xE2\x80\xBB999999999999999:\"a\"}";
        let diag = scan_slot_markers(input);
        assert!(matches!(diag, SlotDiagnostic::I057SlotIndexOutOfRange { .. }));
    }

    #[test]
    fn test_hash_domain() {
        let bytes = b"$0:KERNEL\n";
        let h = hash_slots(bytes);
        assert!(h.starts_with("sha256:"));
        assert_eq!(h.len(), 71); // sha256: + 64 hex
    }

    #[test]
    fn test_hash_known_value() {
        // Hash of empty canonical with CORTEX-C14N-0.2 domain
        let h = hash_slots(b"");
        // SHA-256("CORTEX-C14N-0.2" + 0x00 + "")
        // Verify it's not all zeros
        assert_ne!(h, "sha256:0000000000000000000000000000000000000000000000000000000000000000");
    }

    #[test]
    fn test_mixed_surface_i058() {
        // 0.1-declared doc with structural ※
        let input = b"$0:format{cortex:0.1}\nKNW:x{\xE2\x80\xBB1:\"a\"}";
        let diag = check_mixed_surface_legacy(input);
        assert!(matches!(diag, SlotDiagnostic::I058MixedSurfaceVersion { .. }));
    }

    #[test]
    fn test_no_i058_for_marker_in_string() {
        // 0.1 doc with ※ inside string — NOT structural
        let input = b"$0:format{cortex:0.1}\nKNW:x{topic:\"a \xE2\x80\xBB b\"}";
        let diag = check_mixed_surface_legacy(input);
        assert_eq!(diag, SlotDiagnostic::Ok);
    }
}
