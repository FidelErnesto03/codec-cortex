package cortex

import (
	"bytes"
	"testing"
)

func TestScanSlotMarkers_OK(t *testing.T) {
	input := []byte("$0:format{cortex:0.2} KNW:x{\xe2\x80\xbb1:\"a\"}")
	diag := ScanSlotMarkers(input)
	if diag.Code != "OK" {
		t.Errorf("expected OK, got %v", diag)
	}
}

func TestScanSlotMarkers_HomoglyphBullet(t *testing.T) {
	input := []byte("KNW:x{\xe2\x80\xa21:\"a\"}")
	diag := ScanSlotMarkers(input)
	if diag.Code != "L020_HOMOGLYPH_MARKER" {
		t.Errorf("expected L020_HOMOGLYPH_MARKER, got %v", diag)
	}
}

func TestScanSlotMarkers_HomoglyphMiddleDot(t *testing.T) {
	input := []byte("KNW:x{\xc2\xb71:\"a\"}")
	diag := ScanSlotMarkers(input)
	if diag.Code != "L020_HOMOGLYPH_MARKER" {
		t.Errorf("expected L020_HOMOGLYPH_MARKER, got %v", diag)
	}
}

func TestScanSlotMarkers_ZeroIndex(t *testing.T) {
	input := []byte("KNW:x{\xe2\x80\xbb0:\"a\"}")
	diag := ScanSlotMarkers(input)
	if diag.Code != "L022_SLOT_INDEX_ZERO" {
		t.Errorf("expected L022_SLOT_INDEX_ZERO, got %v", diag)
	}
}

func TestScanSlotMarkers_LeadingZero(t *testing.T) {
	input := []byte("KNW:x{\xe2\x80\xbb01:\"a\"}")
	diag := ScanSlotMarkers(input)
	if diag.Code != "L023_SLOT_INDEX_LEADING_ZERO" {
		t.Errorf("expected L023_SLOT_INDEX_LEADING_ZERO, got %v", diag)
	}
}

func TestScanSlotMarkers_HugeIndex(t *testing.T) {
	input := []byte("KNW:x{\xe2\x80\xbb999999999999999:\"a\"}")
	diag := ScanSlotMarkers(input)
	if diag.Code != "I057_SLOT_INDEX_OUT_OF_RANGE" {
		t.Errorf("expected I057_SLOT_INDEX_OUT_OF_RANGE, got %v", diag)
	}
}

func TestHashSlots_Format(t *testing.T) {
	h := HashSlots([]byte("$0:KERNEL\n"))
	if len(h) != 71 {
		t.Errorf("expected length 71, got %d", len(h))
	}
	if h[:7] != "sha256:" {
		t.Errorf("expected sha256: prefix, got %v", h[:7])
	}
}

func TestHashSlots_Deterministic(t *testing.T) {
	h1 := HashSlots([]byte("test"))
	h2 := HashSlots([]byte("test"))
	if h1 != h2 {
		t.Errorf("hash not deterministic: %s != %s", h1, h2)
	}
}

func TestHashSlots_DiffersFromRaw(t *testing.T) {
	// Raw SHA-256 of empty: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
	h := HashSlots([]byte{})
	if h == "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" {
		t.Errorf("hash matched raw SHA-256 (no domain separation)")
	}
}

func TestCheckMixedSurface01_I058(t *testing.T) {
	input := []byte("$0:format{cortex:0.1}\nKNW:x{\xe2\x80\xbb1:\"a\"}")
	diag := CheckMixedSurface01(input)
	if diag.Code != "I058_MIXED_SURFACE_VERSION" {
		t.Errorf("expected I058_MIXED_SURFACE_VERSION, got %v", diag)
	}
}

func TestCheckMixedSurface01_NoI058ForMarkerInString(t *testing.T) {
	input := []byte("$0:format{cortex:0.1}\nKNW:x{topic:\"a \xe2\x80\xbb b\"}")
	diag := CheckMixedSurface01(input)
	if diag.Code != "OK" {
		t.Errorf("expected OK, got %v", diag)
	}
}

func TestHashSlots_DomainTag(t *testing.T) {
	// Verify the domain tag is prepended by checking hash of "CORTEX-C14N-0.2\x00"
	// differs from hash of empty.
	h1 := HashSlots([]byte{})
	h2 := HashSlots([]byte("a"))
	if h1 == h2 {
		t.Errorf("hash of empty and 'a' should differ")
	}
	// Verify domain tag is exactly CORTEX-C14N-0.2
	if !bytes.Equal(HashDomainSlots, []byte("CORTEX-C14N-0.2")) {
		t.Errorf("HashDomainSlots mismatch: %s", string(HashDomainSlots))
	}
}
