'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { parseV10, canonicalizeV10, renderHCORTEX10, compileHCORTEX10 } = require('../src/v10');

const ROOT = path.resolve(__dirname, '..', '..');

function read(file) {
  return fs.readFileSync(file, 'utf8');
}

test('CORTEX 1.0/0.2 roundtrip over the corpus', () => {
  const cases = [
    ['conformance/1.0/valid', '1.0'],
    ['conformance/slots/valid', '0.2'],
  ];
  let total = 0;
  for (const [dir, version] of cases) {
    for (const name of fs.readdirSync(path.join(ROOT, dir)).filter((f) => f.endsWith('.cortex')).sort()) {
      const source = read(path.join(ROOT, dir, name));
      const expected = canonicalizeV10(parseV10(source, version));
      const render = renderHCORTEX10(parseV10(source, version));
      const { doc, diags } = compileHCORTEX10(render);
      assert.deepStrictEqual(diags, [], `${name} diagnostics`);
      assert.strictEqual(canonicalizeV10(doc), expected, `${name} roundtrip`);
      total += 1;
    }
  }
  assert.ok(total >= 100, `expected corpus, got ${total}`);
});

test('HCORTEX 1.0 normative vectors compile to their source', () => {
  const vectors = fs.readdirSync(path.join(ROOT, 'conformance/1.0/hcortex')).filter((f) => f.endsWith('.md')).sort();
  assert.ok(vectors.length > 0, 'no HCORTEX 1.0 vectors');
  for (const name of vectors) {
    const { doc, diags } = compileHCORTEX10(read(path.join(ROOT, 'conformance/1.0/hcortex', name)));
    assert.deepStrictEqual(diags, [], `${name} diagnostics`);
    const source = read(path.join(ROOT, 'conformance/1.0/valid', name.replace(/\.md$/, '.cortex')));
    assert.strictEqual(canonicalizeV10(doc), canonicalizeV10(parseV10(source, '1.0')), `${name} vector`);
  }
});
