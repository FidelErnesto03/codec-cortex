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
// Python reference implementation.

package cortex

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"math/big"
)

var SlotMarkerBytes = []byte{0xE2, 0x80, 0xBB} // ※ U+203B
var HashDomainSlots = []byte("CORTEX-C14N-0.2")

var SlotIndexMax = new(big.Int).Sub(new(big.Int).Lsh(big.NewInt(1), 31), big.NewInt(1))

// Homoglyphs forbidden as slot markers (L020)
var Homoglyphs = []struct {
	Bytes []byte
	Name  string
}{
	{[]byte{0xE2, 0x80, 0xA2}, "U+2022 BULLET"},         // •
	{[]byte{0xC2, 0xB7}, "U+00B7 MIDDLE DOT"},           // ·
	{[]byte{0xE2, 0x88, 0x99}, "U+2219 BULLET OPERATOR"}, // ∙
	{[]byte{0xE2, 0x97, 0x8F}, "U+25CF BLACK CIRCLE"},   // ●
}

type SlotDiagnostic struct {
	Code        string
	ByteOffset  int
	Reason      string
	Homoglyph   string
	Line        int
	Col         int
	IndexValue  string
}

// ScanSlotMarkers scans input bytes for slot marker syntax errors.
// Returns the first diagnostic encountered, or {Code: "OK"} if clean.
func ScanSlotMarkers(input []byte) SlotDiagnostic {
	n := len(input)
	i := 0
	for i < n {
		// Check for slot marker ※ (E2 80 BB)
		if i+2 < n && input[i] == 0xE2 && input[i+1] == 0x80 && input[i+2] == 0xBB {
			j := i + 3
			if j < n && (input[j] == ' ' || input[j] == '\t') {
				return SlotDiagnostic{Code: "L021_INVALID_SLOT_INDEX", ByteOffset: i, Reason: "space after slot marker"}
			}
			if j >= n {
				return SlotDiagnostic{Code: "L021_INVALID_SLOT_INDEX", ByteOffset: i, Reason: "EOF after slot marker"}
			}
			c := input[j]
			if c == '0' {
				if j+1 < n && input[j+1] >= '0' && input[j+1] <= '9' {
					return SlotDiagnostic{Code: "L023_SLOT_INDEX_LEADING_ZERO", ByteOffset: i}
				}
				return SlotDiagnostic{Code: "L022_SLOT_INDEX_ZERO", ByteOffset: i}
			}
			if c < '1' || c > '9' {
				if c >= 0x80 {
					return SlotDiagnostic{Code: "L021_INVALID_SLOT_INDEX", ByteOffset: i, Reason: "non-ASCII digit in slot index"}
				}
				return SlotDiagnostic{Code: "L021_INVALID_SLOT_INDEX", ByteOffset: i, Reason: fmt.Sprintf("invalid slot index start byte 0x%x", c)}
			}
			start := j
			for j < n && input[j] >= '0' && input[j] <= '9' {
				j++
			}
			idxStr := string(input[start:j])
			if len(idxStr) > 10 {
				return SlotDiagnostic{Code: "I057_SLOT_INDEX_OUT_OF_RANGE", ByteOffset: i, IndexValue: "overflow"}
			}
			idx := new(big.Int)
			idx.SetString(idxStr, 10)
			if idx.Cmp(SlotIndexMax) > 0 {
				return SlotDiagnostic{Code: "I057_SLOT_INDEX_OUT_OF_RANGE", ByteOffset: i, IndexValue: idxStr}
			}
			if j < n && (input[j] == ' ' || input[j] == '\t') {
				return SlotDiagnostic{Code: "L024_SLOT_INDEX_SEPARATOR", ByteOffset: i}
			}
			if j >= n || input[j] != ':' {
				return SlotDiagnostic{Code: "L021_INVALID_SLOT_INDEX", ByteOffset: i, Reason: "expected ':' after slot index"}
			}
			i = j + 1
			continue
		}
		// Check for homoglyphs in structural position
		for _, hg := range Homoglyphs {
			hb := hg.Bytes
			if i+len(hb) <= n && string(input[i:i+len(hb)]) == string(hb) {
				// Check structural position
				k := i - 1
				for k > 0 && (input[k] == ' ' || input[k] == '\t') {
					k--
				}
				if k == 0 || input[k] == '{' || input[k] == ',' {
					return SlotDiagnostic{Code: "L020_HOMOGLYPH_MARKER", ByteOffset: i, Homoglyph: hg.Name}
				}
			}
		}
		i++
	}
	return SlotDiagnostic{Code: "OK"}
}

// CheckMixedSurface01 detects ※ in structural position in a 0.1-declared doc (I058).
func CheckMixedSurface01(input []byte) SlotDiagnostic {
	n := len(input)
	i := 0
	for i < n {
		if i+2 < n && input[i] == 0xE2 && input[i+1] == 0x80 && input[i+2] == 0xBB {
			k := i - 1
			for k > 0 && (input[k] == ' ' || input[k] == '\t') {
				k--
			}
			if k == 0 || input[k] == '{' || input[k] == ',' {
				line, col := 1, 1
				for idx := 0; idx < i; idx++ {
					if input[idx] == '\n' {
						line++
						col = 1
					} else {
						col++
					}
				}
				return SlotDiagnostic{Code: "I058_MIXED_SURFACE_VERSION", Line: line, Col: col}
			}
		}
		i++
	}
	return SlotDiagnostic{Code: "OK"}
}

// HashSlots computes SHA-256(CORTEX-C14N-0.2 || 0x00 || canonicalBytes).
func HashSlots(canonicalBytes []byte) string {
	h := sha256.New()
	h.Write(HashDomainSlots)
	h.Write([]byte{0x00})
	h.Write(canonicalBytes)
	return "sha256:" + hex.EncodeToString(h.Sum(nil))
}
