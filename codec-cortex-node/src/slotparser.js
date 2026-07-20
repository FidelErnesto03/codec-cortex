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

'use strict';

const crypto = require('crypto');

const SLOT_MARKER_BYTES = Buffer.from([0xE2, 0x80, 0xBB]); // ※ U+203B
const HASH_DOMAIN_SLOTS = Buffer.from('CORTEX-C14N-0.2', 'utf8');
const SLOT_INDEX_MAX = (1n << 31n) - 1n;

// Homoglyph markers (forbidden as slot markers, L020)
const HOMOGLYPHS = [
  { bytes: Buffer.from([0xE2, 0x80, 0xA2]), name: 'U+2022 BULLET' },
  { bytes: Buffer.from([0xC2, 0xB7]), name: 'U+00B7 MIDDLE DOT' },
  { bytes: Buffer.from([0xE2, 0x88, 0x99]), name: 'U+2219 BULLET OPERATOR' },
  { bytes: Buffer.from([0xE2, 0x97, 0x8F]), name: 'U+25CF BLACK CIRCLE' },
];

function scanSlotMarkers(input) {
  // input: Buffer
  const n = input.length;
  let i = 0;
  while (i < n) {
    // Check for slot marker ※ (E2 80 BB)
    if (i + 2 < n && input[i] === 0xE2 && input[i + 1] === 0x80 && input[i + 2] === 0xBB) {
      let j = i + 3;
      // Space after marker = L021
      if (j < n && (input[j] === 0x20 || input[j] === 0x09)) {
        return { code: 'L021_INVALID_SLOT_INDEX', byteOffset: i, reason: 'space after slot marker' };
      }
      if (j >= n) {
        return { code: 'L021_INVALID_SLOT_INDEX', byteOffset: i, reason: 'EOF after slot marker' };
      }
      const c = input[j];
      if (c === 0x30) { // '0'
        if (j + 1 < n && input[j + 1] >= 0x30 && input[j + 1] <= 0x39) {
          return { code: 'L023_SLOT_INDEX_LEADING_ZERO', byteOffset: i };
        }
        return { code: 'L022_SLOT_INDEX_ZERO', byteOffset: i };
      }
      if (c < 0x31 || c > 0x39) { // not nonzero ASCII digit
        if (c >= 0x80) {
          return { code: 'L021_INVALID_SLOT_INDEX', byteOffset: i, reason: 'non-ASCII digit in slot index' };
        }
        return { code: 'L021_INVALID_SLOT_INDEX', byteOffset: i, reason: `invalid slot index start byte 0x${c.toString(16)}` };
      }
      // Collect digits
      const start = j;
      while (j < n && input[j] >= 0x30 && input[j] <= 0x39) {
        j++;
      }
      const idxStr = input.slice(start, j).toString('ascii');
      if (idxStr.length > 10) {
        return { code: 'I057_SLOT_INDEX_OUT_OF_RANGE', byteOffset: i, index: 'overflow' };
      }
      const idx = BigInt(idxStr);
      if (idx > SLOT_INDEX_MAX) {
        return { code: 'I057_SLOT_INDEX_OUT_OF_RANGE', byteOffset: i, index: idxStr };
      }
      if (j < n && (input[j] === 0x20 || input[j] === 0x09)) {
        return { code: 'L024_SLOT_INDEX_SEPARATOR', byteOffset: i };
      }
      if (j >= n || input[j] !== 0x3A) { // ':'
        return { code: 'L021_INVALID_SLOT_INDEX', byteOffset: i, reason: "expected ':' after slot index" };
      }
      i = j + 1;
      continue;
    }
    // Check for homoglyphs in structural position (after { or ,)
    for (const hg of HOMOGLYPHS) {
      const hb = hg.bytes;
      if (i + hb.length <= n && input.slice(i, i + hb.length).equals(hb)) {
        let k = i > 0 ? i - 1 : 0;
        while (k > 0 && (input[k] === 0x20 || input[k] === 0x09)) {
          k--;
        }
        if (k === 0 || input[k] === 0x7B || input[k] === 0x2C) {
          return { code: 'L020_HOMOGLYPH_MARKER', byteOffset: i, homoglyph: hg.name };
        }
      }
    }
    i++;
  }
  return { code: 'OK' };
}

function checkMixedSurfaceLegacy(input) {
  // input: Buffer
  const n = input.length;
  let i = 0;
  while (i < n) {
    if (i + 2 < n && input[i] === 0xE2 && input[i + 1] === 0x80 && input[i + 2] === 0xBB) {
      let k = i > 0 ? i - 1 : 0;
      while (k > 0 && (input[k] === 0x20 || input[k] === 0x09)) {
        k--;
      }
      if (k === 0 || input[k] === 0x7B || input[k] === 0x2C) {
        // Compute line/col
        let line = 1, col = 1;
        for (let idx = 0; idx < i; idx++) {
          if (input[idx] === 0x0A) {
            line++;
            col = 1;
          } else {
            col++;
          }
        }
        return { code: 'I058_MIXED_SURFACE_VERSION', line, col };
      }
    }
    i++;
  }
  return { code: 'OK' };
}

function hashSlots(canonicalBytes) {
  const h = crypto.createHash('sha256');
  h.update(HASH_DOMAIN_SLOTS);
  h.update(Buffer.from([0x00]));
  h.update(canonicalBytes);
  return 'sha256:' + h.digest('hex');
}

module.exports = {
  SLOT_MARKER_BYTES,
  HASH_DOMAIN_SLOTS,
  SLOT_INDEX_MAX,
  HOMOGLYPHS,
  scanSlotMarkers,
  checkMixedSurfaceLegacy,
  hashSlots,
};
