'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const codec = require('../src');
const root = path.resolve(__dirname, '..');

function read(name) {
  return fs.readFileSync(path.join(root, 'examples', name), 'utf8');
}

test('public API exposes Python-compatible and Node-style names', () => {
  assert.equal(codec.parse_cortex, codec.parseCortex);
  assert.equal(codec.render_hcortex, codec.renderHcortex);
  assert.equal(codec.compile_hcortex, codec.compileHcortex);
  assert.equal(codec.run_all_tests, codec.runAllTests);
  assert.equal(typeof codec.Scalar, 'function');
  assert.equal(typeof codec.Document, 'function');
});

test('scalar strings, lists, numbers and clone behavior', () => {
  assert.equal(codec.parseStringLiteral('a\\n\\u00E1'), 'a\ná');
  assert.equal(codec.emitStringLiteral('a\ná'), '"a\\ná"');
  const pairs = codec.parseAttrsPayload('{a:-0,b:1.20,c:true,d:null,e:[x,"y z"]}');
  assert.deepEqual(pairs.map(([key, value]) => [key, value.kind, value.lexeme]), [
    ['a', 'integer', '0'],
    ['b', 'decimal', '1.20'],
    ['c', 'boolean', 'true'],
    ['d', 'null', 'null'],
    ['e', 'list', '[x,"y z"]'],
  ]);
  const cloned = pairs.at(-1)[1].clone();
  assert.notEqual(cloned, pairs.at(-1)[1]);
  assert.notEqual(cloned.value[0], pairs.at(-1)[1].value[0]);
});

test('full vector canonicalizes byte-for-byte like Python reference', () => {
  const document = codec.parseCortex(read('full.cortex'));
  const canonical = codec.canonicalize(document);
  assert.equal(canonical, read('full.canonical.cortex'));
  assert.equal(`${codec.c14nHash(Buffer.from(canonical, 'utf8'))}\n`, read('full.hash.txt'));
});

test('HCORTEX render, compile and reverse canonicalization match golden vectors', () => {
  const document = codec.parseCortex(read('full.cortex'));
  codec.canonicalize(document);
  const hcortex = codec.renderHcortex(document);
  assert.equal(hcortex, read('full.hcortex.md'));
  const [restored, diagnostics] = codec.compileHcortex(hcortex);
  assert.deepEqual(diagnostics, []);
  assert.ok(restored);
  assert.equal(codec.canonicalize(restored), read('full.roundtrip.cortex'));
});

test('canonicalization is idempotent', () => {
  const first = codec.canonicalize(codec.parseCortex(read('full.cortex')));
  const second = codec.canonicalize(codec.parseCortex(first));
  assert.equal(second, first);
});

test('reference error codes and locations are preserved', () => {
  assert.throws(
    () => codec.parseCortex('\ufeff$0\n'),
    (error) => error instanceof codec.ParseError && error.code === 'U001_BOM_FORBIDDEN' && error.line === 0,
  );
  assert.throws(
    () => codec.parseCortex('outside'),
    (error) => error.code === 'S005_CONTENT_OUTSIDE_SECTION' && error.line === 1,
  );
  const invalid = '$0\n$0:format{cortex:0.1,encoding:UTF-8}\nA:X{type:attrs,weight:B,fields:"x:text",focus:y,desc:"d"}\n';
  assert.throws(
    () => codec.parseCortex(invalid),
    (error) => error.code === 'G025_UNKNOWN_FOCUS_FIELD' && error.message === "focus 'y' not in contract",
  );
});

test('HCORTEX diagnostics match the reference', () => {
  const [missingDoc, missing] = codec.compileHcortex('plain markdown');
  assert.equal(missingDoc, null);
  assert.deepEqual(missing.map((diag) => diag.code), ['H400']);
  const [bomDoc, bom] = codec.compileHcortex('\ufeff<!-- HCORTEX v=0.1 t=canonical -->');
  assert.equal(bomDoc, null);
  assert.deepEqual(bom.map((diag) => diag.code), ['H490']);
});

test('CLI canonicalize and hash commands are operational', () => {
  const input = path.join(root, 'examples', 'full.cortex');
  const cli = path.join(root, 'bin', 'codec-cortex-node.js');
  const canonical = spawnSync(process.execPath, [cli, 'canonicalize', input], { encoding: 'utf8' });
  assert.equal(canonical.status, 0, canonical.stderr);
  assert.equal(canonical.stdout, read('full.canonical.cortex'));
  const hash = spawnSync(process.execPath, [cli, 'hash', input], { encoding: 'utf8' });
  assert.equal(hash.status, 0, hash.stderr);
  assert.equal(hash.stdout, read('full.hash.txt'));
});
