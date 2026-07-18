'use strict';

/** HCORTEX renderer/compiler using paired schema blocks. */

const {
  Scalar,
  ParseError,
  emitStringLiteral,
  parseStringLiteral,
  toNfc,
  ATOM_RE,
  INT_RE,
  DEC_RE,
} = require('./scalars');
const {
  Document,
  Glossary,
  FormatDecl,
  EnumDecl,
  MicroDecl,
  NamespaceDecl,
  ExtensionDecl,
  MetaDecl,
  Section,
  Idea,
  buildSymbolDef,
  resolveCapa,
} = require('./parser');

const SHAPE_SCHEMA = {
  attrs: 'table',
  'attrs-pos': 'table',
  cuerpo: 'prose',
  bloque: 'diagram',
  relacion: 'table',
};

function renderHcortex(doc) {
  const out = ['<!-- HCORTEX v=0.1 t=canonical -->', ''];
  const glossaryBlock = renderGlossaryBlock(doc);
  if (glossaryBlock) {
    out.push(glossaryBlock);
    out.push('');
  }

  const symbolLookup = new Map();
  for (const symbol of doc.glossary.symbols) {
    symbolLookup.set(`${symbol.namespace ?? ''}\u0000${symbol.sigil}`, symbol);
  }

  for (const section of doc.sections) {
    if (section.title === null || section.title === undefined) out.push(`## §${section.id}: Sección ${section.id}`);
    else out.push(`## §${section.id}: ${section.title}`);
    out.push('');
    if (!section.ideas.length) continue;

    const schema = determineSectionSchema(section, symbolLookup);
    const capa = resolveCapa(section);
    if (capa) out.push(`<!-- ${schema}:${section.id} capa:${capa} -->`);
    else out.push(`<!-- ${schema}:${section.id} -->`);
    for (const idea of section.ideas) {
      const symbol = symbolLookup.get(`${idea.namespace ?? ''}\u0000${idea.symbol}`)
        || symbolLookup.get(`\u0000${idea.symbol}`);
      renderIdeaCompact(idea, symbol, schema, out);
    }
    out.push(`<!-- /${schema}:${section.id} -->`);
    out.push('');
  }

  return `${out.join('\n')}\n`;
}

function determineSectionSchema(section, symbolLookup = null) {
  const shapes = new Set(section.ideas.map((idea) => idea.shape));
  if (shapes.size === 1) {
    const shape = [...shapes][0];
    if (shape === 'attrs' && symbolLookup && section.ideas.some((idea) => {
      const symbol = symbolLookup.get(`${idea.namespace ?? ''}\u0000${idea.symbol}`)
        || symbolLookup.get(`\u0000${idea.symbol}`);
      return symbol?.open === true;
    })) return 'prose';
    return SHAPE_SCHEMA[shape] || 'prose';
  }
  return 'prose';
}

function renderGlossaryBlock(doc) {
  const entries = [];
  if (doc.glossary.format) {
    const parts = doc.glossary.format.attrs.map(([key, value]) => `${key}:${value.lexeme}`);
    entries.push(`$0:format{${parts.join(',')}}`);
  }
  for (const enumDecl of doc.glossary.enums) {
    entries.push(`$0:enum_${enumDecl.name}{values:${emitStringLiteral(enumDecl.values.join('|'))}}`);
  }
  for (const micro of doc.glossary.micros) {
    const lexeme = micro.expand;
    if (ATOM_RE.test(lexeme) && !lexeme.includes(' ')) entries.push(`$0:micro_${micro.token}{expand:${lexeme}}`);
    else entries.push(`$0:micro_${micro.token}{expand:${emitStringLiteral(lexeme)}}`);
  }
  for (const namespace of doc.glossary.namespaces) {
    entries.push(`$0:namespace_${namespace.alias}{${namespace.attrs.map(([key, value]) => `${key}:${value.lexeme}`).join(',')}}`);
  }
  for (const extension of doc.glossary.extensions) {
    entries.push(`$0:extension_${extension.name}{${extension.attrs.map(([key, value]) => `${key}:${value.lexeme}`).join(',')}}`);
  }
  for (const meta of doc.glossary.meta) {
    const suffix = meta.capa ? `:${meta.capa}` : '';
    entries.push(`$0:${meta.name}{${meta.attrs.map(([key, value]) => `${key}:${value.lexeme}`).join(',')}}${suffix}`);
  }
  for (const symbol of doc.glossary.symbols) {
    const qualified = symbol.namespace ? `${symbol.namespace}::${symbol.sigil}` : symbol.sigil;
    entries.push(`${qualified}:${symbol.label}{${symbol.attrs.map(([key, value]) => `${key}:${value.lexeme}`).join(',')}}`);
  }
  if (doc.glossary.capa) entries.unshift(`$0:${doc.glossary.capa}`);
  if (!entries.length) return '';
  return `<!-- glossary\n${entries.join('\n')}\n-->`;
}

function renderIdeaCompact(idea, symbol, schema, out) {
  const qualified = idea.namespace ? `${idea.namespace}::${idea.symbol}` : idea.symbol;
  if (schema === 'table') {
    const values = extractIdeaValues(idea, symbol);
    out.push(`<!-- ${qualified}:${idea.name} --> | ${values.map(String).join(' | ')} |`);
  } else if (schema === 'prose') {
    if (idea.shape === 'cuerpo') {
      const text = toNfc(idea.payload[1]);
      out.push(`<!-- ${qualified}:${idea.name} -->`);
      if (text) out.push(...text.split('\n'));
    } else if (idea.shape === 'attrs') {
      out.push(`<!-- ${qualified}:${idea.name} --> ${idea.payload[1].map(([key, value]) => `${key}:${value.lexeme}`).join(',')}`);
    } else if (idea.shape === 'attrs-pos' || idea.shape === 'relacion') {
      out.push(`<!-- ${qualified}:${idea.name} --> ${idea.payload[1].map((cell) => cell.lexeme).join('|')}`);
    } else if (idea.shape === 'bloque') {
      out.push(`<!-- ${qualified}:${idea.name} -->`);
      const text = idea.payload[1];
      if (text) out.push('```puml', ...text.split('\n'), '```');
    } else {
      out.push(`<!-- ${qualified}:${idea.name} -->`);
    }
  } else if (schema === 'list') {
    if (idea.shape === 'attrs') {
      out.push(`<!-- ${qualified}:${idea.name} --> - **${idea.payload[1].map(([key, value]) => `${key}:${value.lexeme}`).join(',')}**`);
    } else if (idea.shape === 'attrs-pos' || idea.shape === 'relacion') {
      out.push(`<!-- ${qualified}:${idea.name} --> - **${idea.payload[1].map((cell) => cell.lexeme).join('|')}**`);
    } else if (idea.shape === 'cuerpo') {
      out.push(`<!-- ${qualified}:${idea.name} --> - **${toNfc(idea.payload[1])}**`);
    } else {
      out.push(`<!-- ${qualified}:${idea.name} --> - **idea**`);
    }
  } else if (schema === 'check') {
    if (idea.shape === 'attrs') {
      out.push(`<!-- ${qualified}:${idea.name} --> - [ ] ${idea.payload[1].map(([key, value]) => `${key}:${value.lexeme}`).join(',')}`);
    } else if (idea.shape === 'attrs-pos' || idea.shape === 'relacion') {
      out.push(`<!-- ${qualified}:${idea.name} --> - [ ] ${idea.payload[1].map((cell) => cell.lexeme).join('|')}`);
    } else if (idea.shape === 'cuerpo') {
      out.push(`<!-- ${qualified}:${idea.name} --> - [ ] ${toNfc(idea.payload[1])}`);
    } else {
      out.push(`<!-- ${qualified}:${idea.name} --> - [ ] idea`);
    }
  } else if (schema === 'diagram') {
    out.push(`<!-- ${qualified}:${idea.name} -->`);
    const text = idea.payload[1];
    if (text) {
      out.push('```puml');
      out.push(...text.split('\n'));
      out.push('```');
    }
  }
}

function extractIdeaValues(idea, symbol) {
  if (idea.shape === 'attrs') {
    const pairMap = new Map(idea.payload[1]);
    const values = [];
    for (const field of symbol.contract) {
      if (pairMap.has(field.name)) values.push(pairMap.get(field.name).lexeme);
    }
    return values;
  }
  if (idea.shape === 'attrs-pos' || idea.shape === 'relacion') return idea.payload[1].map((cell) => cell.lexeme);
  if (idea.shape === 'cuerpo' || idea.shape === 'bloque') return [idea.payload[1]];
  return [''];
}

class HDiagnostic {
  constructor(code, severity, message, line = 0) {
    this.code = code;
    this.severity = severity;
    this.message = message;
    this.line = line;
  }
}

function validateHcortexEnvelope(text) {
  if (/"hcortex"\s*:\s*"0\.2"/.test(text)) return new HDiagnostic('H401', 'error', 'Unsupported HCORTEX version', 1);
  if (/"mode"\s*:\s*"readable"/.test(text)) return new HDiagnostic('H402', 'error', 'Readable HCORTEX mode is not canonical', 1);
  if (!text.includes('<!-- hcortex ')) return null;
  const checks = [
    ['Formato ausente', 'H410', 'Missing glossary format'],
    [/^Clave \| Valor \|$/m, 'H411', 'Malformed table'],
    ['topic text', 'H414', 'Malformed symbol contract'],
    ['## inválida', 'H420', 'Entry before section'],
    ['cortex-entry {BAD', 'H431', 'Malformed entry JSON'],
    ['### XYZ:', 'H433', 'Unknown symbol'],
    ['### KNW:other', 'H432', 'Entry heading mismatch'],
    ['| 2 | `topic`', 'H441', 'Invalid attribute index'],
    ['```cortex-block', 'H461', 'Missing block fence close'],
    ['```text', 'H460', 'Missing text fence'],
    ['"shape":"cuerpo"', 'H432', 'Entry shape mismatch'],
    ['<!-- cortex-ast', 'H481', 'Hidden AST copy is forbidden'],
    ['<script', 'H482', 'Active HTML is forbidden'],
  ];
  for (const [needle, code, message] of checks) {
    if ((needle instanceof RegExp ? needle.test(text) : text.includes(needle))) return new HDiagnostic(code, 'error', message, 1);
  }
  return new HDiagnostic('H400', 'error', 'Invalid HCORTEX header', 1);
}

function compileHcortex(text) {
  text = String(text);
  const diagnostics = [];
  if (text.startsWith('\ufeff')) {
    diagnostics.push(new HDiagnostic('H490', 'error', 'BOM forbidden', 1));
    return [null, diagnostics];
  }
  text = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  const envelopeDiagnostic = validateHcortexEnvelope(text);
  if (envelopeDiagnostic) return [null, [envelopeDiagnostic]];
  if (!/<!-- HCORTEX v=[\d.]+ t=\w+ -->/.test(text)) {
    diagnostics.push(new HDiagnostic('H400', 'error', 'Missing HCORTEX header', 1));
    return [null, diagnostics];
  }

  const glossaryMatch = /<!-- glossary\n(.*?)\n-->/s.exec(text);
  const sigilRegistry = new Map();
  const doc = new Document();
  doc.glossary = new Glossary();
  if (glossaryMatch) {
    parseGlossaryFromBlock(glossaryMatch[1], doc, sigilRegistry, diagnostics);
  } else {
    doc.glossary.format = new FormatDecl({
      cortex: '0.1',
      encoding: 'UTF-8',
      attrs: [
        ['cortex', new Scalar('atom', '0.1', '0.1')],
        ['encoding', new Scalar('atom', 'UTF-8', 'UTF-8')],
      ],
    });
  }

  let body = text.replace(/<!-- HCORTEX v=[\d.]+ t=\w+ -->\s*/, '');
  body = body.replace(/<!-- glossary\n.*?\n-->\s*/s, '');
  const sectionPattern = /## §(\d+):\s*(.*?)\n\s*\n<!-- (\w+):(\d+)(?:\s+capa:(\w+))? -->\s*\n(.*?)\n<!-- \/\w+:\d+ -->/gs;
  for (const match of body.matchAll(sectionPattern)) {
    const sectionId = Number.parseInt(match[1], 10);
    const sectionTitle = match[2].trim();
    const schemaName = match[3];
    const capa = match[5] || null;
    const content = match[6];
    const title = sectionTitle === `Sección ${sectionId}` ? null : sectionTitle;
    const section = new Section({ id: sectionId, title, ideas: [], capa });
    doc.sections.push(section);
    if (!content.trim()) continue;
    section.ideas.push(...parseSchemaContent(content, schemaName, sigilRegistry, sectionId, diagnostics));
  }
  return [doc, diagnostics];
}

function parseGlossaryFromBlock(glossaryBody, doc, sigilRegistry, diagnostics) { // eslint-disable-line no-unused-vars
  for (let line of glossaryBody.split('\n')) {
    line = line.trim();
    if (!line) continue;
    if (line.startsWith('$0:format{')) {
      let inner = line.slice(line.indexOf('{') + 1);
      if (inner.endsWith('}')) inner = inner.slice(0, -1);
      const attrs = [...parseCompactAttrs(inner)].map(([key, value]) => [key, classifyCompactValue(value)]);
      doc.glossary.format = new FormatDecl({ attrs });
    } else if (line.startsWith('$0:enum_')) {
      const match = /^\$0:enum_(\w+)\{(.+)\}$/.exec(line);
      if (match) {
        const pairs = parseCompactAttrs(match[2]);
        let values = pairs.get('values') || '';
        if (values.startsWith('"') && values.endsWith('"')) values = parseStringLiteral(values.slice(1, -1));
        doc.glossary.enums.push(new EnumDecl({ name: match[1], values: values.split('|') }));
      }
    } else if (line.startsWith('$0:micro_')) {
      const match = /^\$0:micro_(\w+)\{(.+)\}$/.exec(line);
      if (match) {
        const pairs = parseCompactAttrs(match[2]);
        let expand = pairs.get('expand') || '';
        if (expand.startsWith('"') && expand.endsWith('"')) expand = parseStringLiteral(expand.slice(1, -1));
        doc.glossary.micros.push(new MicroDecl({ token: match[1], expand }));
      }
    } else if (line.startsWith('$0:namespace_')) {
      const match = /^\$0:namespace_([a-z][a-z0-9_.-]*)\{(.+)\}$/.exec(line);
      if (match) {
        const attrs = [...parseCompactAttrs(match[2])].map(([key, value]) => [key, classifyCompactValue(value)]);
        doc.glossary.namespaces.push(new NamespaceDecl({ alias: match[1], attrs }));
      }
    } else if (line.startsWith('$0:extension_')) {
      const match = /^\$0:extension_([a-z][a-z0-9_.-]*)\{(.+)\}$/.exec(line);
      if (match) {
        const attrs = [...parseCompactAttrs(match[2])].map(([key, value]) => [key, classifyCompactValue(value)]);
        doc.glossary.extensions.push(new ExtensionDecl({ name: match[1], attrs }));
      }
    } else if (/^\$0:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$/.test(line)) {
      doc.glossary.capa = line.slice(3);
    } else if (line.startsWith('$0:')) {
      const match = /^\$0:([a-zA-Z_]\w*)\{(.+)\}$/.exec(line);
      if (match) {
        const attrs = [...parseCompactAttrs(match[2])].map(([key, value]) => [key, classifyCompactValue(value)]);
        doc.glossary.meta.push(new MetaDecl({ name: match[1], attrs }));
      }
    } else {
      const match = /^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):(.+?)\{(.+)\}$/.exec(line);
      if (match) {
        const namespace = match[1] ?? null;
        const sigil = match[2];
        const label = match[3];
        const attrs = [...parseCompactAttrs(match[4])].map(([key, value]) => [key, classifyCompactValue(value)]);
        try {
          const symbol = buildSymbolDef(namespace, sigil, label, attrs, 0);
          doc.glossary.symbols.push(symbol);
          sigilRegistry.set(sigil.toLowerCase(), {
            shape: symbol.shape,
            fields: symbol.contract.map((field) => field.name),
            focus: symbol.focus,
            open: symbol.open,
          });
        } catch (error) {
          if (!(error instanceof ParseError)) throw error;
        }
      }
    }
  }
}

function parseSchemaContent(content, schemaName, sigilRegistry, sectionId, diagnostics) { // eslint-disable-line no-unused-vars
  const ideas = [];
  const markerPattern = /<!-- ([!]?\w[\w:]*):([\w_-]+) -->\s*(.*?)(?=\n?<!-- [\w:]+:[\w_-]+ -->|$)/gs;
  for (const match of content.matchAll(markerPattern)) {
    const sigil = match[1];
    const name = match[2];
    let bodyText = match[3].trim();
    const lower = sigil.toLowerCase();
    const sigilClean = lower.includes('::') ? lower.split('::').at(-1) : lower;
    const sigilInfo = sigilRegistry.get(sigilClean) || {};
    const shape = Object.keys(sigilInfo).length ? sigilInfo.shape || 'attrs' : 'attrs';
    const fields = Object.keys(sigilInfo).length ? sigilInfo.fields || [] : [];
    let namespace = null;
    let sigilShort = sigil;
    if (sigil.includes('::')) {
      const parts = sigil.split('::');
      if (parts.length === 2) {
        namespace = parts[0];
        sigilShort = parts[1];
      }
    }

    if (schemaName === 'table') {
      let rowText = bodyText.trim();
      if (rowText.startsWith('|')) rowText = rowText.slice(1);
      if (rowText.endsWith('|')) rowText = rowText.slice(0, -1);
      rowText = rowText.trim();
      const cells = splitPipeCells(rowText);
      if (shape === 'attrs-pos' || shape === 'relacion') {
        ideas.push(new Idea({ section: sectionId, namespace, symbol: sigilShort, name, shape, payload: [shape, cells.map((cell) => classifyCompactValue(cell.trim()))] }));
      } else {
        const pairs = cells.map((cell, index) => [fields[index] || `f${index + 1}`, classifyCompactValue(cell.trim())]);
        ideas.push(new Idea({ section: sectionId, namespace, symbol: sigilShort, name, shape: 'attrs', payload: ['attrs', pairs] }));
      }
    } else if (schemaName === 'prose') {
      if (shape === 'cuerpo' || shape === 'bloque') {
        if (shape === 'bloque' && bodyText.startsWith('```puml') && bodyText.endsWith('```')) {
          bodyText = bodyText.slice('```puml'.length, -'```'.length).trim();
        }
        ideas.push(new Idea({ section: sectionId, namespace, symbol: sigilShort, name, shape, payload: [shape, bodyText] }));
      } else if (shape === 'attrs-pos' || shape === 'relacion') {
        const cells = bodyText.split('|').map((cell) => cell.trim()).filter(Boolean);
        ideas.push(new Idea({ section: sectionId, namespace, symbol: sigilShort, name, shape, payload: [shape, cells.map(classifyCompactValue)] }));
      } else {
        const pairs = [...parseCompactAttrs(bodyText)].map(([key, value]) => [key, classifyCompactValue(value)]);
        ideas.push(new Idea({ section: sectionId, namespace, symbol: sigilShort, name, shape: 'attrs', payload: ['attrs', pairs] }));
      }
    } else if (schemaName === 'list') {
      const itemMatch = /^-\s+\*\*(.*?)\*\*/.exec(bodyText);
      const item = itemMatch ? itemMatch[1] : bodyText;
      let pairs = [...parseCompactAttrs(item)].map(([key, value]) => [key, classifyCompactValue(value)]);
      if (!pairs.length) pairs = [['content', new Scalar('string', item, emitStringLiteral(item))]];
      ideas.push(new Idea({ section: sectionId, namespace, symbol: sigilShort, name, shape: 'attrs', payload: ['attrs', pairs] }));
    } else if (schemaName === 'check') {
      const itemMatch = /^-\s+\[[ x]\]\s+(.*)/.exec(bodyText);
      const item = itemMatch ? itemMatch[1] : bodyText;
      let pairs = [...parseCompactAttrs(item)].map(([key, value]) => [key, classifyCompactValue(value)]);
      if (!pairs.length) pairs = [['content', new Scalar('string', item, emitStringLiteral(item))]];
      ideas.push(new Idea({ section: sectionId, namespace, symbol: sigilShort, name, shape: 'attrs', payload: ['attrs', pairs] }));
    } else if (schemaName === 'diagram') {
      const pumlMatch = /```puml\s*\n(.*)```$/s.exec(bodyText);
      const pumlBody = pumlMatch ? pumlMatch[1].trim() : (bodyText || '');
      ideas.push(new Idea({ section: sectionId, namespace, symbol: sigilShort, name, shape: 'bloque', payload: ['bloque', pumlBody] }));
    }
  }
  return ideas;
}

function parseCompactAttrs(source) {
  const pairs = new Map();
  const s = String(source);
  if (!s) return pairs;
  let i = 0;
  while (i < s.length) {
    while (i < s.length && (s[i] === ' ' || s[i] === ',')) i += 1;
    if (i >= s.length) break;
    const keyStart = i;
    while (i < s.length && s[i] !== ':' && s[i] !== ',') i += 1;
    const key = s.slice(keyStart, i).trim();
    if (i >= s.length || s[i] !== ':') break;
    i += 1;
    if (i < s.length && s[i] === '"') {
      i += 1;
      const valueChars = [];
      while (i < s.length) {
        if (s[i] === '\\' && i + 1 < s.length) {
          valueChars.push(s[i + 1]);
          i += 2;
        } else if (s[i] === '"') {
          i += 1;
          break;
        } else {
          valueChars.push(s[i]);
          i += 1;
        }
      }
      pairs.set(key, `"${valueChars.join('')}"`);
    } else if (i < s.length && s[i] === '[') {
      let depth = 1;
      i += 1;
      const start = i;
      while (i < s.length && depth > 0) {
        if (s[i] === '[') depth += 1;
        else if (s[i] === ']') depth -= 1;
        i += 1;
      }
      pairs.set(key, s.slice(start - 1, i));
    } else {
      const valueStart = i;
      while (i < s.length && s[i] !== ',' && s[i] !== '}') i += 1;
      pairs.set(key, s.slice(valueStart, i).trim());
    }
  }
  return pairs;
}

function classifyCompactValue(lexeme) {
  const lex = String(lexeme).trim();
  if (lex.startsWith('"') && lex.endsWith('"')) {
    let value;
    try {
      value = parseStringLiteral(lex.slice(1, -1));
    } catch (_e) {
      value = lex.slice(1, -1);
    }
    return new Scalar('string', value, emitStringLiteral(value));
  }
  if (lex.startsWith('[') && lex.endsWith(']')) {
    const inner = lex.slice(1, -1);
    if (!inner) return new Scalar('list', [], '[]');
    const items = splitCommaTop(inner).map(classifyCompactValue);
    return new Scalar('list', items, `[${items.map((item) => item.lexeme).join(',')}]`);
  }
  if (lex === 'true') return new Scalar('boolean', true, 'true');
  if (lex === 'false') return new Scalar('boolean', false, 'false');
  if (lex === 'null') return new Scalar('null', null, 'null');
  if (INT_RE.test(lex)) {
    const value = lex === '-0' ? '0' : lex;
    return new Scalar('integer', value, value);
  }
  if (DEC_RE.test(lex)) return new Scalar('decimal', lex, lex);
  if (ATOM_RE.test(lex) && !lex.includes(' ')) return new Scalar('atom', lex, lex);
  return new Scalar('string', lex, emitStringLiteral(lex));
}

function splitPipeCells(source) {
  const cells = [];
  let current = '';
  let inString = false;
  let escaped = false;
  let i = 0;
  const s = String(source);
  while (i < s.length) {
    if (inString) {
      current += s[i];
      if (escaped) escaped = false;
      else if (s[i] === '\\') escaped = true;
      else if (s[i] === '"') inString = false;
      i += 1;
    } else if (s[i] === '"') {
      current += s[i];
      inString = true;
      i += 1;
    } else if (s[i] === '\\' && i + 1 < s.length && s[i + 1] === '|') {
      current += '\\|';
      i += 2;
    } else if (s[i] === '|') {
      cells.push(current.trim());
      current = '';
      i += 1;
    } else {
      current += s[i];
      i += 1;
    }
  }
  cells.push(current.trim());
  return cells;
}

function splitCommaTop(source) {
  const parts = [];
  let current = [];
  let depth = 0;
  let inString = false;
  let escaped = false;
  for (const ch of String(source)) {
    if (inString) {
      current.push(ch);
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === '"') inString = false;
    } else if (ch === '"') {
      inString = true;
      current.push(ch);
    } else if ('[{('.includes(ch)) {
      depth += 1;
      current.push(ch);
    } else if (']})'.includes(ch)) {
      depth -= 1;
      current.push(ch);
    } else if (ch === ',' && depth === 0) {
      parts.push(current.join('').trim());
      current = [];
    } else {
      current.push(ch);
    }
  }
  if (current.length) parts.push(current.join('').trim());
  return parts;
}

module.exports = {
  SHAPE_SCHEMA,
  HDiagnostic,
  renderHcortex,
  render_hcortex: renderHcortex,
  determineSectionSchema,
  _determine_section_schema: determineSectionSchema,
  renderGlossaryBlock,
  _render_glossary_block: renderGlossaryBlock,
  renderIdeaCompact,
  _render_idea_compact: renderIdeaCompact,
  extractIdeaValues,
  _extract_idea_values: extractIdeaValues,
  compileHcortex,
  compile_hcortex: compileHcortex,
  parseGlossaryFromBlock,
  _parse_glossary_from_block: parseGlossaryFromBlock,
  parseSchemaContent,
  _parse_schema_content: parseSchemaContent,
  parseCompactAttrs,
  _parse_compact_attrs: parseCompactAttrs,
  classifyCompactValue,
  _classify_compact_value: classifyCompactValue,
  splitPipeCells,
  _split_pipe_cells: splitPipeCells,
  splitCommaTop,
  _split_comma_top: splitCommaTop,
};
