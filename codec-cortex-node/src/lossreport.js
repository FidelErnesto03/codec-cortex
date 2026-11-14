'use strict';

// CORTEX 1.0 declared loss report (spec §8.2 / §8.3), reference-parity surface.

const crypto = require('node:crypto');
const path = require('node:path');
const { toNfc } = require('./scalars');
const { parseV10, canonicalizeV10, renderHCORTEX10, compileHCORTEX10 } = require('./v10');

const L402 = 'L402_COMMENT_DROPPED';
const L403 = 'L403_INTRALINE_WHITESPACE';
const L405 = 'L405_OPEN_ATTR_ORDER';
const L406 = 'L406_COMPILE_SIDE_DROP';
const L499 = 'L499_UNCLASSIFIED_LOSS';

const PRESERVED = ['blocks', 'identity', 'scalars', 'structure'];

// Coverage declaration (spec §8.2): which pipeline operations the report
// models. The compile pipeline (source -> AST) is not modelled, so declaring
// it explicitly keeps `reversible: true` honest about its scope.
const COVERED_OPERATIONS = ['render'];
const UNCOVERED_OPERATIONS = ['compile'];

const DETAIL = {
  [L402]: 'comment line outside a multiline body is not represented in the AST',
  [L403]: 'intraline whitespace is collapsed by canonicalization',
  [L405]: 'editorial attribute order of an open sigil is not preserved',
  [L406]: 'an idea present in the AST is lost across the render/compile roundtrip (its rendered header does not round-trip)',
  [L499]: 'roundtrip diverges and no declared loss classifies the divergence',
};

const ACTION = {
  [L402]: 'declare-only',
  [L403]: 'declare-only',
  [L405]: 'declare-only',
  [L406]: 'fix-surface',
  [L499]: 'fix-surface',
};

function finding(code, p, category, recoverability) {
  return {
    action: ACTION[code],
    category,
    code,
    detail: DETAIL[code],
    path: p,
    recoverability,
    severity: code === L499 || code === L406 ? 'error' : 'loss',
  };
}

function ideaKeys(doc) {
  const keys = new Set();
  for (const section of doc.sections) {
    for (const idea of section.ideas) {
      keys.add(`${section.id}|${idea.namespace || ''}|${idea.symbol}|${idea.name}`);
    }
  }
  return keys;
}

function sha256(text) {
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
}

function stripQuoted(line) {
  let out = '';
  let i = 0;
  while (i < line.length) {
    if (line[i] !== '"') {
      out += line[i];
      i += 1;
      continue;
    }
    out += '""';
    i += 1;
    while (i < line.length) {
      if (line[i] === '\\') {
        i += 2;
        continue;
      }
      if (line[i] === '"') {
        i += 1;
        break;
      }
      i += 1;
    }
  }
  return out;
}

function lexicalLosses(source) {
  const losses = [];
  let inBody = false;
  const lines = source.split('\n');
  for (let i = 0; i < lines.length; i += 1) {
    const raw = lines[i].endsWith('\r') ? lines[i].slice(0, -1) : lines[i];
    const stripped = raw.trim();
    if (inBody) {
      if (stripped === '}') inBody = false;
      continue;
    }
    if (!stripped) continue;
    if (stripped.startsWith('#')) {
      losses.push(finding(L402, `line:${i + 1}`, 'structure', 'from-source-only'));
      continue;
    }
    if (stripped.endsWith('{') && !stripped.startsWith('$0:')) inBody = true;
    const probe = stripQuoted(raw);
    if (probe !== probe.replace(/[ \t]+$/, '') || probe.includes('\t') || probe.includes('  ')) {
      losses.push(finding(L403, `line:${i + 1}`, 'presentation', 'from-source-only'));
    }
  }
  return losses;
}

function openAttrOrderLosses(doc) {
  const losses = [];
  for (const section of doc.sections) {
    for (const idea of section.ideas) {
      if (idea.shape !== 'attrs' || !idea.payload || idea.payload[0] !== 'attrs') continue;
      const sym = doc.glossary.symbols.find(
        (s) => s.sigil === idea.symbol && (s.namespace || null) === (idea.namespace || null),
      );
      if (!sym || !sym.open) continue;
      const keys = idea.payload[1].map(([k]) => k);
      const contract = sym.contract.map((f) => f.name);
      const expected = contract.filter((name) => keys.includes(name));
      const extras = keys.filter((k) => !contract.includes(k));
      extras.sort((a, b) => Buffer.compare(Buffer.from(toNfc(a), 'utf8'), Buffer.from(toNfc(b), 'utf8')));
      expected.push(...extras);
      if (keys.join('\u0000') !== expected.join('\u0000')) {
        losses.push(finding(L405, `$${section.id}`, 'order', 'from-source-only'));
      }
    }
  }
  return losses;
}

function dedupe(losses) {
  const seen = new Set();
  const out = [];
  for (const item of losses) {
    const key = `${item.path}\u0000${item.code}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(item);
  }
  out.sort((a, b) => {
    if (a.path !== b.path) return a.path < b.path ? -1 : 1;
    if (a.code !== b.code) return a.code < b.code ? -1 : 1;
    return 0;
  });
  return out;
}

function buildLossReport(source, caseName) {
  const doc = parseV10(source, '1.0');
  if (doc.cortex_version !== '1.0') {
    throw new Error(`loss-report requires cortex:1.0 (declared: ${doc.cortex_version})`);
  }
  // Render and detect source-order losses before canonicalizing: C14N mutates
  // the AST in place (microtoken expansion, attribute normalization).
  const attrLosses = openAttrOrderLosses(doc);
  const srcIdeas = ideaKeys(doc);
  const rendered = renderHCORTEX10(doc);
  const canonicalSource = canonicalizeV10(doc);
  const { doc: roundtrip, diags } = compileHCORTEX10(rendered);
  if (!roundtrip || (diags && diags.length)) throw new Error('HCORTEX roundtrip compilation failed');
  const rtIdeas = ideaKeys(roundtrip);
  const canonicalRoundtrip = canonicalizeV10(roundtrip);

  let dropped = false;
  for (const key of srcIdeas) {
    if (!rtIdeas.has(key)) {
      dropped = true;
      break;
    }
  }
  const losses = lexicalLosses(source).concat(attrLosses);
  const equivalent = canonicalSource === canonicalRoundtrip;
  if (dropped) losses.push(finding(L406, '$', 'structure', 'irrecoverable'));
  if (!equivalent && !dropped) losses.push(finding(L499, '$', 'structure', 'irrecoverable'));

  return {
    case: caseName,
    coverage: {
      complete: UNCOVERED_OPERATIONS.length === 0 && equivalent,
      operations: COVERED_OPERATIONS.slice(),
      uncovered_operations: UNCOVERED_OPERATIONS.slice(),
    },
    losses: dedupe(losses),
    mode: 'canonical',
    operation: 'render',
    preserved: PRESERVED.slice(),
    reversible: equivalent,
    schema_version: '1.0',
    source_format: 'cortex:1.0',
    source_sha256: sha256(source),
    structural_equivalence: equivalent,
    target_format: 'hcortex:1.0',
    target_sha256: sha256(rendered),
    warnings: [],
  };
}

function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === 'object') {
    const out = {};
    for (const key of Object.keys(value).sort()) out[key] = stable(value[key]);
    return out;
  }
  return value;
}

function dumpsCanonical(report) {
  return `${JSON.stringify(stable(report), null, 2)}\n`;
}

function lossCaseName(file) {
  if (!file || file === '-') return 'stdin';
  const stem = path.basename(file);
  const idx = stem.lastIndexOf('.');
  return idx > 0 ? stem.slice(0, idx) : stem;
}

module.exports = { buildLossReport, dumpsCanonical, lossCaseName };
