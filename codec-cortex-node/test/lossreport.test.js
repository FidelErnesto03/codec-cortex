'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const { buildLossReport, dumpsCanonical, lossCaseName } = require('../src/lossreport');

const ROOT = path.resolve(__dirname, '..', '..');
const LOSS_DIR = path.join(ROOT, 'conformance', '1.0', 'loss');
const manifest = JSON.parse(fs.readFileSync(path.join(LOSS_DIR, 'manifest.json'), 'utf8'));

function readFixture(relative) {
  return fs.readFileSync(path.join(LOSS_DIR, relative), 'utf8');
}

for (const fixture of manifest.fixtures) {
  test(`loss-report ${fixture.id} is byte-identical to the expected report`, () => {
    const source = readFixture(fixture.file);
    const report = buildLossReport(source, fixture.id);
    assert.strictEqual(dumpsCanonical(report), readFixture(fixture.expected));
    assert.deepStrictEqual(report.losses.map((item) => item.code), fixture.codes);
  });
}

test('dotted namespace roundtrips without loss', () => {
  const source = readFixture('clean.cortex')
    .replace('KNW:knowledge', 'tenant.x::KNW:knowledge')
    .replace('KNW:alpha', 'tenant.x::KNW:alpha');
  const report = buildLossReport(source, 'nsdot');
  assert.deepStrictEqual(report.losses, []);
  assert.strictEqual(report.reversible, true);
});

test('loss-report case name strips the directory and extension', () => {
  assert.strictEqual(lossCaseName('/tmp/dir/doc.cortex'), 'doc');
  assert.strictEqual(lossCaseName('-'), 'stdin');
});

test('glossary title is rejected with G042', () => {
  const source = readFixture('clean.cortex').replace('$0:KERNEL', '$0: Titulo');
  assert.throws(
    () => buildLossReport(source, 'title'),
    (error) => error.code === 'G042_GLOSSARY_HEADER_INVALID',
  );
});

test('bare glossary emits $0 and roundtrips', () => {
  const source = readFixture('bare_glossary.cortex');
  const report = buildLossReport(source, 'bare');
  assert.strictEqual(report.reversible, true);
  assert.deepStrictEqual(report.losses, []);
});
