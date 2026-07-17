'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const codec = require('../src');

const SOURCE = `$0
$0:format{cortex:0.1,encoding:UTF-8}
A:Attribute{type:attrs,weight:B,fields:"topic:text|content:text",focus:content,desc:"Attribute"}
$1: Main
A:first{topic:test,content:"hello world"}
`;

test('F3/F4 harness can produce a complete PASS report', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'codec-cortex-node-'));
  const c14n = path.join(temp, 'c14n');
  const hcortex = path.join(temp, 'hcortex');
  fs.mkdirSync(path.join(c14n, 'inputs'), { recursive: true });
  fs.mkdirSync(path.join(c14n, 'canonical'), { recursive: true });
  fs.mkdirSync(path.join(hcortex, 'corpus', 'cortex'), { recursive: true });
  fs.mkdirSync(path.join(hcortex, 'corpus', 'invalid'), { recursive: true });

  const canonical = codec.canonicalize(codec.parseCortex(SOURCE));
  const cases = [];
  for (let index = 1; index <= 40; index += 1) {
    const id = String(index).padStart(3, '0');
    const input = `inputs/${id}.cortex`;
    const golden = `canonical/${id}.cortex`;
    fs.writeFileSync(path.join(c14n, input), SOURCE, 'utf8');
    fs.writeFileSync(path.join(c14n, golden), canonical, 'utf8');
    cases.push({ id, input, canonical: golden });
  }
  fs.writeFileSync(path.join(c14n, 'manifest.json'), JSON.stringify({ cases }), 'utf8');

  const roundtripDoc = codec.parseCortex(SOURCE);
  codec.canonicalize(roundtripDoc);
  const rendered = codec.renderHcortex(roundtripDoc);
  const [compiled] = codec.compileHcortex(rendered);
  const roundtrip = codec.canonicalize(compiled);
  const roundtripSha = codec.sha256Bytes(Buffer.from(roundtrip, 'utf8'));

  fs.writeFileSync(path.join(hcortex, 'corpus', 'cortex', '001_case.cortex'), SOURCE, 'utf8');
  fs.writeFileSync(path.join(hcortex, 'corpus', 'invalid', 'missing-header.md'), 'not hcortex', 'utf8');
  fs.writeFileSync(path.join(hcortex, 'manifest.json'), JSON.stringify({
    canonical: [{ id: '001', title: 'case', cortex_sha256: roundtripSha }],
    invalid: [{ id: 'missing-header', expected_diagnostic: 'H400' }],
  }), 'utf8');

  const logs = [];
  const report = codec.runAllTests(c14n, hcortex, { logger: { log: (line) => logs.push(String(line)) } });
  assert.equal(report.phase3.golden_pass, 40);
  assert.equal(report.phase3.idempotence_pass, 40);
  assert.equal(report.phase4.roundtrip_pass, 1);
  assert.equal(report.phase4.idempotence_pass, 1);
  assert.equal(report.phase4.invalid_diag_pass, 1);
  assert.equal(report.verdict, 'PASS');
  assert.ok(logs.some((line) => line.includes('Verdict: PASS')));

  fs.rmSync(temp, { recursive: true, force: true });
});
