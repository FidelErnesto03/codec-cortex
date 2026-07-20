// Integration tests for CORTEX 0.2 slot marker detection in Rust.

use codec_cortex::slotparser::{scan_slot_markers, check_mixed_surface_legacy, hash_slots, SlotDiagnostic};

#[test]
fn test_slot_marker_ok() {
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
fn test_hash_domain_slots() {
    let h = hash_slots(b"$0:KERNEL\n");
    assert!(h.starts_with("sha256:"));
    assert_eq!(h.len(), 71);
    // Verify not all zeros (real hash)
    assert_ne!(h, "sha256:0000000000000000000000000000000000000000000000000000000000000000");
}

#[test]
fn test_hash_domain_slots_deterministic() {
    let h1 = hash_slots(b"test");
    let h2 = hash_slots(b"test");
    assert_eq!(h1, h2);
}

#[test]
fn test_hash_domain_differs_from_raw() {
    // Hash with domain should differ from raw SHA-256
    let h = hash_slots(b"");
    // Raw SHA-256 of empty: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    assert_ne!(h, "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
}

#[test]
fn test_i058_structural_marker_in_01_doc() {
    let input = b"$0:format{cortex:0.1}\nKNW:x{\xE2\x80\xBB1:\"a\"}";
    let diag = check_mixed_surface_legacy(input);
    assert!(matches!(diag, SlotDiagnostic::I058MixedSurfaceVersion { .. }));
}

#[test]
fn test_no_i058_for_marker_in_string() {
    let input = b"$0:format{cortex:0.1}\nKNW:x{topic:\"a \xE2\x80\xBB b\"}";
    let diag = check_mixed_surface_legacy(input);
    assert_eq!(diag, SlotDiagnostic::Ok);
}
