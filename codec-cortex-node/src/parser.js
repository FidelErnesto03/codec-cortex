'use strict';

/** CORTEX 0.1 parser and AST model. */

const {
  Scalar,
  ParseError,
  StringCursor,
  parseAttrsPayload,
  parseStringScalar,
  emitStringLiteral,
  ATOM_RE,
  INT_RE,
  DEC_RE,
  toNfc,
  pythonRepr,
} = require('./scalars');

class FormatDecl {
  constructor({ cortex = '0.1', encoding = 'UTF-8', attrs = [], sourceLine = 1, source_line } = {}) {
    this.cortex = cortex;
    this.encoding = encoding;
    this.attrs = attrs;
    this.source_line = source_line ?? sourceLine;
  }
}

class MetaDecl {
  constructor({ name, attrs, capa = null, sourceLine = 1, source_line } = {}) {
    this.name = name;
    this.attrs = attrs;
    this.capa = capa;
    this.source_line = source_line ?? sourceLine;
  }
}

class EnumDecl {
  constructor({ name, values, sourceLine = 1, source_line } = {}) {
    this.name = name;
    this.values = values;
    this.source_line = source_line ?? sourceLine;
  }
}

class MicroDecl {
  constructor({ token, expand, sourceLine = 1, source_line } = {}) {
    this.token = token;
    this.expand = expand;
    this.source_line = source_line ?? sourceLine;
  }
}

class NamespaceDecl {
  constructor({ alias, attrs, sourceLine = 1, source_line } = {}) {
    this.alias = alias;
    this.attrs = attrs;
    this.source_line = source_line ?? sourceLine;
  }
}

class ExtensionDecl {
  constructor({ name, attrs, sourceLine = 1, source_line } = {}) {
    this.name = name;
    this.attrs = attrs;
    this.source_line = source_line ?? sourceLine;
  }
}

class ContractField {
  constructor({ name, type, required } = {}) {
    this.name = name;
    this.type = type;
    this.required = required;
  }
}

class SymbolDef {
  constructor({ namespace = null, sigil, label, shape, weight, focus, desc, open = false, contract = [], attrs = [], sourceLine = 1, source_line } = {}) {
    this.namespace = namespace;
    this.sigil = sigil;
    this.label = label;
    this.shape = shape;
    this.weight = weight;
    this.focus = focus;
    this.desc = desc;
    this.open = open;
    this.contract = contract;
    this.attrs = attrs;
    this.source_line = source_line ?? sourceLine;
  }

  get qualified() {
    return this.namespace ? `${this.namespace}::${this.sigil}` : this.sigil;
  }
}

class Idea {
  constructor({ section, namespace = null, symbol, name, shape, payload, sourceLine = 1, source_line } = {}) {
    this.section = section;
    this.namespace = namespace;
    this.symbol = symbol;
    this.name = name;
    this.shape = shape;
    this.payload = payload;
    this.source_line = source_line ?? sourceLine;
  }

  get qualified_symbol() {
    return this.namespace ? `${this.namespace}::${this.symbol}` : this.symbol;
  }

  get qualifiedSymbol() {
    return this.qualified_symbol;
  }

  get address() {
    return `$${this.section}:${this.qualified_symbol}:${this.name}`;
  }
}

class Section {
  constructor({ id, title = null, ideas = [], capa = null } = {}) {
    this.id = id;
    this.title = title;
    this.ideas = ideas;
    this.capa = capa;
  }
}

class Glossary {
  constructor({ format = null, meta = [], enums = [], micros = [], namespaces = [], extensions = [], symbols = [], capa = null } = {}) {
    this.format = format;
    this.meta = meta;
    this.enums = enums;
    this.micros = micros;
    this.namespaces = namespaces;
    this.extensions = extensions;
    this.symbols = symbols;
    this.capa = capa;
  }
}

class Document {
  constructor({ cortexVersion = '0.1', cortex_version, encoding = 'UTF-8', glossary = new Glossary(), sections = [] } = {}) {
    this.cortex_version = cortex_version ?? cortexVersion;
    this.encoding = encoding;
    this.glossary = glossary;
    this.sections = sections;
  }

  get cortexVersion() {
    return this.cortex_version;
  }

  set cortexVersion(value) {
    this.cortex_version = value;
  }
}

function normalizeLineEndings(value) {
  return String(value).replace(/\r\n/g, '\n').replace(/\r/g, '\n');
}

function parseContractFields(source) {
  const out = [];
  for (let part of String(source).split('|')) {
    part = part.trim();
    if (!part) {
      throw new ParseError('G008_INVALID_CONTRACT', `Empty contract field in ${pythonRepr(source)}`);
    }
    let required;
    if (part.includes('?')) {
      required = false;
      part = Array.from(part).slice(0, -1).join('');
    } else {
      required = true;
    }
    let name;
    let type;
    const colon = part.indexOf(':');
    if (colon >= 0) {
      name = part.slice(0, colon);
      type = part.slice(colon + 1);
    } else {
      name = part;
      type = 'any';
    }
    out.push(new ContractField({ name: name.trim(), type: type.trim(), required }));
  }
  return out;
}

function parseCortex(source) {
  source = String(source);
  if (source.startsWith('\ufeff')) throw new ParseError('U001_BOM_FORBIDDEN', 'BOM forbidden');
  source = normalizeLineEndings(source);
  const lines = source.split('\n');

  const doc = new Document();
  let inGlossary = false;
  let currentSection = null;
  let inBody = false;
  let bodyLines = [];
  let bodyIdea = null;
  let bodyKind = '';

  let i = 0;
  while (i < lines.length) {
    const raw = lines[i];
    const lineNo = i + 1;
    if (inBody) {
      const stripped = raw.trim();
      if (stripped === '}') {
        const text = bodyLines.join('\n');
        bodyIdea.payload = bodyKind === 'cuerpo' ? ['cuerpo', text] : ['bloque', text];
        if (currentSection !== null) currentSection.ideas.push(bodyIdea);
        inBody = false;
        bodyLines = [];
        bodyIdea = null;
        bodyKind = '';
        i += 1;
        continue;
      }
      bodyLines.push(raw);
      i += 1;
      continue;
    }

    const stripped = raw.trim();
    if (!stripped || stripped.startsWith('#')) {
      i += 1;
      continue;
    }

    // $0:CAPA — start glossary with capa
    let m0 = /^\$0:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$/.exec(stripped);
    if (m0) {
      if (inGlossary) throw new ParseError('G002_GLOSSARY_REOPENED', '$0 reopened', lineNo);
      inGlossary = true;
      doc.glossary.capa = m0[1];
      i += 1;
      continue;
    }

    // $N:CAPA — section with capa but no title (N>=1)
    let mn = /^\$([1-9][0-9]*):(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$/.exec(stripped);
    if (mn) {
      const sid = Number.parseInt(mn[1], 10);
      const capa = mn[2];
      currentSection = new Section({ id: sid, title: null, ideas: [], capa });
      doc.sections.push(currentSection);
      inGlossary = false;
      i += 1;
      continue;
    }

    let match = /^\$([0-9]+)(?:\s+(.*))?$/.exec(stripped);
    if (match && !stripped.startsWith('$0:')) {
      const sid = Number.parseInt(match[1], 10);
      if (sid === 0) {
        if (inGlossary) throw new ParseError('G002_GLOSSARY_REOPENED', '$0 reopened', lineNo);
        inGlossary = true;
        i += 1;
        continue;
      }
      const titleRaw = match[2];
      let title = titleRaw !== undefined ? titleRaw.trim() : null;
      let capa = null;
      if (title) {
        const cm = title.match(/:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)\s*$/);
        if (cm) {
          capa = cm[1];
          title = title.slice(0, cm.index).trim();
        }
      }
      currentSection = new Section({ id: sid, title, ideas: [], capa });
      doc.sections.push(currentSection);
      inGlossary = false;
      i += 1;
      continue;
    }

    match = /^\$([1-9][0-9]*):\s+(.*)$/.exec(stripped);
    if (match) {
      const sid = Number.parseInt(match[1], 10);
      let title = match[2].trim();
      let capa = null;
      const cm = title.match(/:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)\s*$/);
      if (cm) {
        capa = cm[1];
        title = title.slice(0, cm.index).trim();
      }
      currentSection = new Section({ id: sid, title, ideas: [], capa });
      doc.sections.push(currentSection);
      inGlossary = false;
      i += 1;
      continue;
    }

    if (inGlossary && (stripped.startsWith('$0:') || isGlossaryDeclLine(stripped))) {
      parseGlossaryDeclaration(stripped, doc, lineNo);
      i += 1;
      continue;
    }

    if (currentSection === null && !inGlossary) {
      throw new ParseError('S005_CONTENT_OUTSIDE_SECTION', `Content outside section: ${pythonRepr(stripped)}`, lineNo);
    }

    if (inGlossary) {
      parseGlossaryDeclaration(stripped, doc, lineNo);
      i += 1;
      continue;
    }

    const idea = parseIdeaLine(stripped, currentSection.id, doc, lineNo);
    if ((idea.shape === 'cuerpo' || idea.shape === 'bloque') && Array.isArray(idea.payload) && idea.payload[0] === '_multiline_body') {
      inBody = true;
      bodyLines = [];
      bodyIdea = idea;
      bodyKind = idea.shape;
      i += 1;
      continue;
    }
    currentSection.ideas.push(idea);
    i += 1;
  }

  return doc;
}

function isGlossaryDeclLine(source) {
  return /^(?:[a-z][a-z0-9_.-]*::)?(?:!|[A-Z][A-Z0-9_]*):/.test(source);
}

function findMatchingBrace(line, openIdx) {
  let depth = 0;
  let inString = false;
  for (let i = openIdx; i < line.length; i++) {
    const c = line[i];
    if (inString) {
      if (c === '\\') { i += 1; continue; }
      if (c === '"') inString = false;
    } else if (c === '"') {
      inString = true;
    } else if (c === '{') {
      depth++;
    } else if (c === '}') {
      depth--;
      if (depth === 0) return i;
    }
  }
  return -1;
}

function parseGlossaryDeclaration(line, doc, lineNo) {
  const braceIndex = line.indexOf('{');
  if (braceIndex < 0) {
    throw new ParseError('G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS', `Glossary declaration must use attrs: ${pythonRepr(line)}`, lineNo);
  }
  let head = line.slice(0, braceIndex).trim();
  if (head.startsWith('$0:')) {
    const closeBrace = findMatchingBrace(line, braceIndex);
    if (closeBrace < 0) throw new ParseError('L008_UNCLOSED_BRACE', 'Missing closing } in meta declaration', lineNo);
    const attrsString = line.slice(braceIndex, closeBrace + 1);
    const rest = line.slice(closeBrace + 1).trim();
    const attrs = parseAttrsPayload(attrsString, lineNo);
    const name = head.slice(3);
    let capa = null;
    if (rest && /^:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$/.test(rest)) {
      capa = rest.slice(1);
    }
    addMetaDeclaration(name, attrs, capa, doc, lineNo);
    return;
  }
  const match = /^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):(.+)$/.exec(head);
  if (!match) throw new ParseError('L001_INVALID_SYMBOL', `Invalid sigil declaration head: ${pythonRepr(head)}`, lineNo);
  const namespace = match[1] ?? null;
  const sigil = match[2];
  const label = match[3];
  const attrs = parseAttrsPayload(line.slice(braceIndex), lineNo);
  doc.glossary.symbols.push(buildSymbolDef(namespace, sigil, label, attrs, lineNo));
}

function pairsToMap(pairs) {
  const map = new Map();
  for (const [key, value] of pairs) map.set(key, value);
  return map;
}

function addMetaDeclaration(name, attrs, capa, doc, lineNo) {
  if (name === 'format') {
    if (doc.glossary.format !== null) throw new ParseError('G006_DUPLICATE_FORMAT', 'Duplicate $0:format', lineNo);
    const attrMap = pairsToMap(attrs);
    const cortex = attrMap.get('cortex');
    const encoding = attrMap.get('encoding');
    const cortexValue = cortex ? cortex.value : '0.1';
    const encodingValue = encoding ? encoding.value : 'UTF-8';
    if (cortexValue !== '0.1') throw new ParseError('G007_UNSUPPORTED_VERSION', `Unsupported cortex version: ${cortexValue}`, lineNo);
    if (encodingValue !== 'UTF-8') throw new ParseError('G011_ENCODING_REQUIRED', `Encoding must be UTF-8: ${encodingValue}`, lineNo);
    doc.glossary.format = new FormatDecl({ cortex: cortexValue, encoding: encodingValue, attrs, sourceLine: lineNo });
    return;
  }

  if (name.startsWith('enum_')) {
    const enumName = name.slice(5);
    const values = pairsToMap(attrs).get('values');
    if (!values || values.kind !== 'string') throw new ParseError('G014_INVALID_ENUM', `enum ${enumName} missing values string`, lineNo);
    doc.glossary.enums.push(new EnumDecl({ name: enumName, values: values.value.split('|'), sourceLine: lineNo }));
    return;
  }

  if (name.startsWith('micro_')) {
    const token = name.slice(6);
    const expand = pairsToMap(attrs).get('expand');
    if (!expand) throw new ParseError('G012_INVALID_MICRO', `micro ${token} missing expand`, lineNo);
    const expandValue = expand.kind === 'atom' || expand.kind === 'string' ? expand.value : expand.lexeme;
    doc.glossary.micros.push(new MicroDecl({ token, expand: expandValue, sourceLine: lineNo }));
    return;
  }

  if (name.startsWith('namespace_')) {
    doc.glossary.namespaces.push(new NamespaceDecl({ alias: name.slice(10), attrs, sourceLine: lineNo }));
    return;
  }

  if (name.startsWith('extension_')) {
    doc.glossary.extensions.push(new ExtensionDecl({ name: name.slice(10), attrs, sourceLine: lineNo }));
    return;
  }

  doc.glossary.meta.push(new MetaDecl({ name, attrs, capa, sourceLine: lineNo }));
}

function buildSymbolDef(namespace, sigil, label, attrs, lineNo) {
  const attrMap = pairsToMap(attrs);
  const typeValue = attrMap.get('type');
  if (!typeValue) throw new ParseError('G016_SYMBOL_TYPE_REQUIRED', `sigil ${sigil} missing type`, lineNo);
  const shape = typeValue.kind === 'atom' || typeValue.kind === 'string' ? typeValue.value : typeValue.lexeme;
  if (!['attrs', 'attrs-pos', 'cuerpo', 'bloque', 'relacion'].includes(shape)) {
    throw new ParseError('G017_UNKNOWN_SHAPE', `Unknown shape: ${shape}`, lineNo);
  }
  const weightValue = attrMap.get('weight');
  if (!weightValue) throw new ParseError('G018_SYMBOL_WEIGHT_REQUIRED', `sigil ${sigil} missing weight`, lineNo);
  const weight = weightValue.kind === 'atom' || weightValue.kind === 'string' ? weightValue.value : weightValue.lexeme;
  if (!['B', 'M', 'H'].includes(weight)) throw new ParseError('G019_INVALID_WEIGHT', `Invalid weight: ${weight}`, lineNo);
  const descValue = attrMap.get('desc');
  if (!descValue) throw new ParseError('G020_SYMBOL_DESCRIPTION_REQUIRED', `sigil ${sigil} missing desc`, lineNo);
  const desc = descValue.kind === 'string' ? descValue.value : descValue.lexeme;
  const openValue = attrMap.get('open');
  let isOpen = false;
  if (openValue) {
    isOpen = (openValue.kind === 'boolean' && openValue.value === true) || (openValue.kind === 'atom' && openValue.value === 'true');
  }

  let contract = [];
  if (shape === 'attrs') {
    const fields = attrMap.get('fields');
    if (!fields) throw new ParseError('G021_ATTRS_CONTRACT_REQUIRED', `sigil ${sigil} missing fields`, lineNo);
    contract = parseContractFields(fields.value);
  } else if (shape === 'attrs-pos' || shape === 'relacion') {
    const pos = attrMap.get('pos');
    if (!pos) throw new ParseError('G022_POSITIONAL_CONTRACT_REQUIRED', `sigil ${sigil} missing pos`, lineNo);
    contract = parseContractFields(pos.value);
    if (shape === 'relacion' && contract.length < 3) {
      throw new ParseError('G023_RELATION_CONTRACT_TOO_SHORT', 'relacion needs >=3 fields', lineNo);
    }
  }

  const focusValue = attrMap.get('focus');
  let focus;
  if (!focusValue) {
    if (shape === 'cuerpo' || shape === 'bloque') focus = '$body';
    else throw new ParseError('G024_FOCUS_REQUIRED', `sigil ${sigil} missing focus`, lineNo);
  } else {
    focus = focusValue.kind === 'atom' || focusValue.kind === 'string' ? focusValue.value : focusValue.lexeme;
    if (['attrs', 'attrs-pos', 'relacion'].includes(shape) && !contract.some((field) => field.name === focus)) {
      throw new ParseError('G025_UNKNOWN_FOCUS_FIELD', `focus ${pythonRepr(focus)} not in contract`, lineNo);
    }
  }

  return new SymbolDef({ namespace, sigil, label, shape, weight, focus, desc, open: isOpen, contract, attrs, sourceLine: lineNo });
}

function parseIdeaLine(line, sectionId, doc, lineNo) {
  line = line.trim();
  const match = /^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):([^{|}\s]+)/.exec(line);
  if (!match) throw new ParseError('S003_INVALID_IDEA_HEAD', `Invalid idea head: ${pythonRepr(line)}`, lineNo);
  const namespace = match[1] ?? null;
  const sigil = match[2];
  const name = match[3];
  const rest = line.slice(match[0].length);

  let symbol = null;
  for (const candidate of doc.glossary.symbols) {
    if (candidate.sigil === sigil && candidate.namespace === namespace) {
      symbol = candidate;
      break;
    }
    if (candidate.sigil === sigil && candidate.namespace === null && namespace === null) {
      symbol = candidate;
      break;
    }
  }
  if (!symbol) throw new ParseError('I001_UNDECLARED_SYMBOL', `Undeclared sigil: ${sigil}`, lineNo);

  const shape = symbol.shape;
  if (shape === 'attrs' || shape === 'cuerpo' || shape === 'bloque') {
    if (!rest.startsWith('{')) throw new ParseError('I004_SHAPE_DELIMITER_MISMATCH', `Expected { for shape ${shape}`, lineNo);
    if (rest.endsWith('}') && !rest.includes('\n')) {
      if (shape === 'attrs') {
        return new Idea({ section: sectionId, namespace, symbol: sigil, name, shape, payload: ['attrs', parseAttrsPayload(rest, lineNo)], sourceLine: lineNo });
      }
      let inner = rest.slice(1, -1);
      if (shape === 'cuerpo') inner = toNfc(inner);
      return new Idea({ section: sectionId, namespace, symbol: sigil, name, shape, payload: [shape, inner], sourceLine: lineNo });
    }
    if (rest.trim() !== '{') throw new ParseError('I004_SHAPE_DELIMITER_MISMATCH', `Expected single { for multiline ${shape}`, lineNo);
    return new Idea({ section: sectionId, namespace, symbol: sigil, name, shape, payload: ['_multiline_body', null], sourceLine: lineNo });
  }

  if (shape === 'attrs-pos' || shape === 'relacion') {
    if (!rest.startsWith('|')) throw new ParseError('I004_SHAPE_DELIMITER_MISMATCH', `Expected | for shape ${shape}`, lineNo);
    const cells = parsePipeCells(rest.slice(1), lineNo);
    return new Idea({ section: sectionId, namespace, symbol: sigil, name, shape, payload: [shape, cells], sourceLine: lineNo });
  }
  throw new ParseError('S999_INTERNAL_PARSE_FAILURE', `Cannot parse idea: ${pythonRepr(line)}`, lineNo);
}

function parsePipeCells(source, lineNo) {
  const chars = Array.from(source);
  const cells = [];
  let i = 0;
  const n = chars.length;
  while (i <= n) {
    if (i < n && chars[i] === '"') {
      const cursor = new StringCursor(chars.slice(i).join(''), lineNo, 1);
      const scalar = parseStringScalar(cursor);
      cells.push(scalar);
      i += cursor.i;
      while (i < n && (chars[i] === ' ' || chars[i] === '\t')) i += 1;
      if (i >= n) return cells;
      if (chars[i] !== '|') throw new ParseError('S006_INVALID_ATTRS', 'Expected | after quoted cell', lineNo, i);
      i += 1;
    } else {
      let j = i;
      while (j < n && chars[j] !== '|') j += 1;
      const raw = chars.slice(i, j).join('');
      const trimmed = raw.trim();
      if (trimmed === '' && j >= n) return cells;
      cells.push(classifyRawCell(trimmed, lineNo));
      i = j;
      if (i < n && chars[i] === '|') i += 1;
      else return cells;
    }
  }
  return cells;
}

function resolveCapa(section) {
  if (section.capa !== null && section.capa !== undefined) return section.capa;
  if (section.id >= 2) return 'DATA';
  return null;
}

function classifyRawCell(raw, lineNo) { // eslint-disable-line no-unused-vars
  if (INT_RE.test(raw)) {
    const value = raw === '-0' ? '0' : raw;
    return new Scalar('integer', value, value);
  }
  if (DEC_RE.test(raw)) return new Scalar('decimal', raw, raw);
  if (raw === 'true') return new Scalar('boolean', true, 'true');
  if (raw === 'false') return new Scalar('boolean', false, 'false');
  if (raw === 'null') return new Scalar('null', null, 'null');
  if (ATOM_RE.test(raw) && !raw.includes(' ')) return new Scalar('atom', raw, raw);
  return new Scalar('string', raw, emitStringLiteral(raw));
}

module.exports = {
  FormatDecl,
  MetaDecl,
  EnumDecl,
  MicroDecl,
  NamespaceDecl,
  ExtensionDecl,
  ContractField,
  SymbolDef,
  Idea,
  Section,
  Glossary,
  Document,
  normalizeLineEndings,
  _normalize_line_endings: normalizeLineEndings,
  parseContractFields,
  parse_contract_fields: parseContractFields,
  parseCortex,
  parse_cortex: parseCortex,
  isGlossaryDeclLine,
  _is_glossary_decl_line: isGlossaryDeclLine,
  parseGlossaryDeclaration,
  _parse_glossary_declaration: parseGlossaryDeclaration,
  addMetaDeclaration,
  _add_meta_declaration: addMetaDeclaration,
  buildSymbolDef,
  _build_symbol_def: buildSymbolDef,
  parseIdeaLine,
  _parse_idea_line: parseIdeaLine,
  parsePipeCells,
  _parse_pipe_cells: parsePipeCells,
  classifyRawCell,
  _classify_raw_cell: classifyRawCell,
  resolveCapa,
  resolve_capa: resolveCapa,
};
