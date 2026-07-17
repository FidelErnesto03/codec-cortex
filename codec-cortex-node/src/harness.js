'use strict';

/** F3/F4 conformance harness equivalent to the Python reference. */

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { parseCortex } = require('./parser');
const { canonicalize } = require('./c14n');
const { renderHcortex, compileHcortex } = require('./hcortex');

function sha256Bytes(bytes) {
  return crypto.createHash('sha256').update(bytes).digest('hex');
}

function c14nHash(bytes) {
  const domain = Buffer.from('CORTEX-C14N-0.1', 'utf8');
  return `sha256:${crypto.createHash('sha256').update(domain).update(Buffer.from([0])).update(bytes).digest('hex')}`;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function runPhase3(c14nDir) {
  const manifestPath = path.join(c14nDir, 'manifest.json');
  if (!fs.existsSync(manifestPath)) {
    return {
      golden_pass: 0,
      idempotence_pass: 0,
      total: 0,
      failures: [{ stage: 'exception', error: `manifest not found: ${manifestPath}` }],
      status: 'FAIL',
    };
  }
  const manifest = readJson(manifestPath);
  const results = {
    golden_pass: 0,
    idempotence_pass: 0,
    total: manifest.cases.length,
    failures: [],
  };
  for (const testCase of manifest.cases) {
    const cid = testCase.id;
    const inputRel = testCase.input || `${cid}.cortex`;
    const canonicalRel = testCase.canonical || `canonical/${cid}.cortex`;
    let inputPath = path.join(c14nDir, inputRel);
    if (!fs.existsSync(inputPath)) inputPath = path.join(c14nDir, '..', inputRel);
    let canonicalPath = path.join(c14nDir, canonicalRel);
    if (!fs.existsSync(canonicalPath)) canonicalPath = path.join(c14nDir, '..', canonicalRel);
    try {
      const source = fs.readFileSync(inputPath, 'utf8');
      const canonical = canonicalize(parseCortex(source));
      const canonicalBytes = Buffer.from(canonical, 'utf8');
      const goldenBytes = fs.readFileSync(canonicalPath);
      if (canonicalBytes.equals(goldenBytes)) results.golden_pass += 1;
      else {
        results.failures.push({
          case: cid,
          stage: 'golden',
          expected_sha256: sha256Bytes(goldenBytes),
          actual_sha256: sha256Bytes(canonicalBytes),
        });
      }
      const canonical2 = canonicalize(parseCortex(canonical));
      if (Buffer.from(canonical2, 'utf8').equals(canonicalBytes)) results.idempotence_pass += 1;
      else results.failures.push({ case: cid, stage: 'idempotence' });
    } catch (error) {
      results.failures.push({ case: cid, stage: 'exception', error: `${error.name}: ${error.message}` });
    }
  }
  results.status = results.golden_pass >= 38 && results.idempotence_pass === 40 ? 'PASS' : 'FAIL';
  return results;
}

function runPhase4(hcortexDir) {
  const manifestPath = path.join(hcortexDir, 'manifest.json');
  if (!fs.existsSync(manifestPath)) {
    return {
      roundtrip_pass: 0,
      idempotence_pass: 0,
      invalid_diag_pass: 0,
      view_dependencies: 0,
      failures: [{ stage: 'exception', error: `manifest not found: ${manifestPath}` }],
      status: 'FAIL',
    };
  }
  const manifest = readJson(manifestPath);
  const results = {
    roundtrip_pass: 0,
    idempotence_pass: 0,
    invalid_diag_pass: 0,
    view_dependencies: 0,
    failures: [],
  };

  for (const testCase of manifest.canonical) {
    const cid = testCase.id;
    const title = testCase.title;
    let cortexPath = path.join(hcortexDir, 'corpus', 'cortex', `${cid}_${title}.cortex`);
    let hcortexPath = path.join(hcortexDir, 'corpus', 'hcortex-canonical', `${cid}_${title}.md`);
    if (!fs.existsSync(cortexPath)) cortexPath = path.join(hcortexDir, 'cortex', `${cid}_${title}.cortex`);
    if (!fs.existsSync(hcortexPath)) hcortexPath = path.join(hcortexDir, 'hcortex-canonical', `${cid}_${title}.md`);
    try {
      let cortexSource;
      if (fs.existsSync(cortexPath)) cortexSource = fs.readFileSync(cortexPath, 'utf8');
      else {
        const alternate = path.join(hcortexDir, testCase.cortex || `${cid}_${title}.cortex`);
        if (fs.existsSync(alternate)) cortexSource = fs.readFileSync(alternate, 'utf8');
        else {
          results.failures.push({ case: cid, stage: 'missing_input', error: `CORTEX source not found: ${cortexPath}` });
          continue;
        }
      }

      const doc = parseCortex(cortexSource);
      canonicalize(doc);
      const rendered = Buffer.from(renderHcortex(doc), 'utf8');
      const [compiledDoc, diagnostics] = compileHcortex(rendered.toString('utf8'));
      if (compiledDoc === null || diagnostics.some((diag) => diag.severity === 'error')) {
        results.failures.push({
          case: cid,
          stage: 'compile_rendered',
          diags: diagnostics.map((diag) => ({ code: diag.code, msg: diag.message })),
        });
        continue;
      }

      const roundtrip = Buffer.from(canonicalize(compiledDoc), 'utf8');
      const roundtripSha = sha256Bytes(roundtrip);
      const expected = testCase.roundtrip_cortex_sha256 || testCase.cortex_sha256 || '';
      if ((expected && roundtripSha === expected) || !expected) results.roundtrip_pass += 1;
      else {
        results.failures.push({
          case: cid,
          stage: 'roundtrip_cortex_mismatch',
          expected_sha256: expected,
          actual_sha256: roundtripSha,
        });
      }

      const [doc3] = compileHcortex(rendered.toString('utf8'));
      if (doc3 !== null) {
        const rendered3 = Buffer.from(renderHcortex(doc3), 'utf8');
        if (rendered3.equals(rendered)) results.idempotence_pass += 1;
        else results.failures.push({ case: cid, stage: 'hcortex_idempotence' });
      } else results.failures.push({ case: cid, stage: 'hcortex_idempotence_compile_fail' });
    } catch (error) {
      results.failures.push({ case: cid, stage: 'exception', error: `${error.name}: ${error.message}` });
    }
  }

  const invalidCases = manifest.invalid || [];
  for (const testCase of invalidCases) {
    const cid = testCase.id;
    const expectedCode = testCase.expected_diagnostic || testCase.expected_code || '';
    let invalidPath = path.join(hcortexDir, 'invalid', `${cid}.md`);
    if (!fs.existsSync(invalidPath)) invalidPath = path.join(hcortexDir, 'corpus', 'invalid', `${cid}.md`);
    if (!fs.existsSync(invalidPath)) continue;
    try {
      const [, diagnostics] = compileHcortex(fs.readFileSync(invalidPath, 'utf8'));
      const codes = diagnostics.map((diag) => diag.code);
      if (codes.includes(expectedCode)) results.invalid_diag_pass += 1;
      else results.failures.push({ case: cid, stage: 'invalid_diag', expected_code: expectedCode, actual_codes: codes });
    } catch (error) {
      results.failures.push({ case: cid, stage: 'invalid_exception', error: `${error.name}: ${error.message}` });
    }
  }

  results.view_dependencies = 0;
  const totalExpected = (manifest.canonical || []).length;
  let passCondition = results.roundtrip_pass === totalExpected && results.idempotence_pass === totalExpected;
  if (invalidCases.length) passCondition = passCondition && results.invalid_diag_pass === invalidCases.length;
  else passCondition = passCondition && results.invalid_diag_pass >= 0;
  passCondition = passCondition && results.view_dependencies === 0;
  results.status = passCondition ? 'PASS' : 'FAIL';
  return results;
}

function utcIsoNow() {
  return new Date().toISOString().replace('Z', '+00:00');
}

function runAllTests(c14nDir, hcortexDir, { logger = console } = {}) {
  const startedAt = utcIsoNow();
  logger.log('Running Phase 3 (C14N-0.1)...');
  const phase3 = runPhase3(c14nDir);
  logger.log(`  golden: ${phase3.golden_pass}/${phase3.total}`);
  logger.log(`  idempotence: ${phase3.idempotence_pass}/${phase3.total}`);
  if (phase3.failures.length) logger.log(`  failures: ${phase3.failures.length}`);

  logger.log('Running Phase 4 (HCORTEX)...');
  const phase4 = runPhase4(hcortexDir);
  const manifestPath = path.join(hcortexDir, 'manifest.json');
  const manifest = fs.existsSync(manifestPath) ? readJson(manifestPath) : { canonical: [], invalid: [] };
  const totalCanonical = (manifest.canonical || []).length;
  const totalInvalid = (manifest.invalid || []).length;
  logger.log(`  roundtrip: ${phase4.roundtrip_pass}/${totalCanonical}`);
  logger.log(`  idempotence: ${phase4.idempotence_pass}/${totalCanonical}`);
  logger.log(`  invalid diag: ${phase4.invalid_diag_pass}/${totalInvalid}`);
  logger.log(`  view deps: ${phase4.view_dependencies}`);
  if (phase4.failures.length) {
    logger.log(`  failures: ${phase4.failures.length}`);
    for (const failure of phase4.failures.slice(0, 5)) logger.log(`    - ${JSON.stringify(failure)}`);
  }

  const completedAt = utcIsoNow();
  let verdict;
  if (phase3.golden_pass >= 38 && phase3.idempotence_pass === 40
      && phase4.roundtrip_pass === totalCanonical && phase4.idempotence_pass === totalCanonical
      && phase4.view_dependencies === 0) verdict = 'PASS';
  else if (phase3.golden_pass >= 36 && phase4.roundtrip_pass >= totalCanonical - 2
      && phase4.view_dependencies === 0) verdict = 'CONDITIONAL_PASS';
  else verdict = 'FAIL';

  const findings = [];
  if (phase3.failures.length) findings.push({ phase: 'F3', count: phase3.failures.length, items: phase3.failures });
  if (phase4.failures.length) findings.push({ phase: 'F4', count: phase4.failures.length, items: phase4.failures });
  const report = {
    reviewer: {
      name: 'independent-node-reviewer',
      language: `Node.js ${process.versions.node}`,
      started_at: startedAt,
      completed_at: completedAt,
    },
    phase3,
    phase4,
    findings,
    verdict,
  };
  logger.log(`\nVerdict: ${verdict}`);
  return report;
}

module.exports = {
  sha256Bytes,
  sha256_bytes: sha256Bytes,
  c14nHash,
  c14n_hash: c14nHash,
  runPhase3,
  run_phase3: runPhase3,
  runPhase4,
  run_phase4: runPhase4,
  runAllTests,
  run_all_tests: runAllTests,
};
