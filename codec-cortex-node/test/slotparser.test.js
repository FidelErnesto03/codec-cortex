// Tests for CORTEX 0.2 slot marker detection in Node.
'use strict';

const test = require('node:test');
const assert = require('node:assert');
const { scanSlotMarkers, checkMixedSurfaceLegacy, hashSlots } = require('../src/slotparser');

test('slot marker OK', () => {
  const input = Buffer.from('$0:format{cortex:0.2} KNW:x{\u203B1:"a"}', 'utf8');
  const diag = scanSlotMarkers(input);
  assert.strictEqual(diag.code, 'OK');
});

test('homoglyph bullet rejected (L020)', () => {
  const input = Buffer.from('KNW:x{\u2022 1:"a"}', 'utf8');
  const diag = scanSlotMarkers(input);
  assert.strictEqual(diag.code, 'L020_HOMOGLYPH_MARKER');
});

test('homoglyph middle-dot rejected (L020)', () => {
  const input = Buffer.from('KNW:x{\u00B7 1:"a"}', 'utf8');
  const diag = scanSlotMarkers(input);
  assert.strictEqual(diag.code, 'L020_HOMOGLYPH_MARKER');
});

test('homoglyph bullet-operator rejected (L020)', () => {
  const input = Buffer.from('KNW:x{\u2219 1:"a"}', 'utf8');
  const diag = scanSlotMarkers(input);
  assert.strictEqual(diag.code, 'L020_HOMOGLYPH_MARKER');
});

test('homoglyph black-circle rejected (L020)', () => {
  const input = Buffer.from('KNW:x{\u25CF 1:"a"}', 'utf8');
  const diag = scanSlotMarkers(input);
  assert.strictEqual(diag.code, 'L020_HOMOGLYPH_MARKER');
});

test('zero index rejected (L022)', () => {
  const input = Buffer.from('KNW:x{\u203B0:"a"}', 'utf8');
  const diag = scanSlotMarkers(input);
  assert.strictEqual(diag.code, 'L022_SLOT_INDEX_ZERO');
});

test('leading zero rejected (L023)', () => {
  const input = Buffer.from('KNW:x{\u203B01:"a"}', 'utf8');
  const diag = scanSlotMarkers(input);
  assert.strictEqual(diag.code, 'L023_SLOT_INDEX_LEADING_ZERO');
});

test('huge index rejected (I057)', () => {
  const input = Buffer.from('KNW:x{\u203B999999999999999:"a"}', 'utf8');
  const diag = scanSlotMarkers(input);
  assert.strictEqual(diag.code, 'I057_SLOT_INDEX_OUT_OF_RANGE');
});

test('hash domain 02 produces 64-hex', () => {
  const h = hashSlots(Buffer.from('$0:KERNEL\n', 'utf8'));
  assert.ok(h.startsWith('sha256:'));
  assert.strictEqual(h.length, 71); // sha256: + 64 hex
});

test('hash domain 02 deterministic', () => {
  const h1 = hashSlots(Buffer.from('test', 'utf8'));
  const h2 = hashSlots(Buffer.from('test', 'utf8'));
  assert.strictEqual(h1, h2);
});

test('hash domain 02 differs from raw SHA-256', () => {
  const h = hashSlots(Buffer.alloc(0));
  // Raw SHA-256 of empty: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  assert.notStrictEqual(h, 'sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');
});

test('I058 structural marker in 0.1 doc', () => {
  const input = Buffer.from('$0:format{cortex:0.1}\nKNW:x{\u203B1:"a"}', 'utf8');
  const diag = checkMixedSurfaceLegacy(input);
  assert.strictEqual(diag.code, 'I058_MIXED_SURFACE_VERSION');
});

test('No I058 for marker in string', () => {
  const input = Buffer.from('$0:format{cortex:0.1}\nKNW:x{topic:"a \u203B b"}', 'utf8');
  const diag = checkMixedSurfaceLegacy(input);
  assert.strictEqual(diag.code, 'OK');
});
