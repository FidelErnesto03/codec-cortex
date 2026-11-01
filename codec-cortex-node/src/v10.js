'use strict';

// CORTEX 1.0 / 0.2 slots surface: parser, C14N and HCORTEX 1.0 render/compile.

const {
  Scalar, ParseError, StringCursor, toNfc, emitStringLiteral,
  parseScalar, skipInlineWs, parseStringScalar, parseAttrsPayload,
  ATOM_RE, INT_RE, DEC_RE,
} = require('./scalars');

const {
  Document, Glossary, Section, Idea, SymbolDef, ContractField,
  FormatDecl, MetaDecl, EnumDecl, MicroDecl, NamespaceDecl, ExtensionDecl,
  normalizeLineEndings, parseContractFields, isGlossaryDeclLine,
  parsePipeCells, classifyRawCell,
} = require('./parser');

const SLOT_MARKER = '※';
const SLOT_INDEX_MAX = 1000000;
const HOMOGLYPHS = {
  '•': 'U+2022 BULLET',
  '·': 'U+00B7 MIDDLE DOT',
  '∙': 'U+2219 BULLET OPERATOR',
  '●': 'U+25CF BLACK CIRCLE',
};

const FORMAT_KEY_ORDER = ['cortex', 'encoding', 'language', 'type'];
const SIGIL_KEY_ORDER = ['type', 'encoding', 'weight', 'slots', 'focus', 'schema', 'desc', 'open', 'namespace', 'version'];
const SIGIL_MAP_KEY_ORDER = ['marker', 'codepoint', 'base', 'syntax', 'order'];
const ENUM_KEY_ORDER = ['values'];
const MICRO_KEY_ORDER = ['expand'];
const NS_KEY_ORDER = ['id', 'uri', 'version', 'required', 'desc'];
const EXT_KEY_ORDER = ['namespace', 'id', 'version', 'required', 'desc'];

function attrMap(pairs) {
  const map = new Map();
  for (const [k, v] of pairs) map.set(k, v);
  return map;
}

function pairsGet(pairs, key) {
  for (const [k, v] of pairs) if (k === key) return v;
  return undefined;
}

function hasKey(pairs, key) {
  return pairs.some(([k]) => k === key);
}

function inSet(value, values) {
  return values.includes(value);
}

function utf8Compare(a, b) {
  return Buffer.compare(Buffer.from(toNfc(a), 'utf8'), Buffer.from(toNfc(b), 'utf8'));
}

class SigilMapDecl {
  constructor({ marker = SLOT_MARKER, codepoint = 'U+203B', base = 1, syntax = '※N:valor', order = 'ascending', sourceLine = 1 } = {}) {
    this.marker = marker;
    this.codepoint = codepoint;
    this.base = base;
    this.syntax = syntax;
    this.order = order;
    this.source_line = sourceLine;
  }
}

class V10Parser {
  constructor(source, version = '0.2') {
    this.lines = source.split('\n');
    this.doc = new Document({ cortexVersion: version });
    this.doc.glossary = new Glossary();
    this.inGlossary = false;
    this.current = null;
    this.inBody = false;
    this.bodyLines = [];
    this.bodyIdea = null;
    this.bodyKind = '';
    this.seenSigilMap = false;
    this.seenAnySlots = false;
    this.seenSectionIds = new Set();
    this.seenIdeaAddresses = new Set();
    this.seenSymbolKeys = new Set();
  }

  parse() {
    const lines = this.lines;
    let i = 0;
    while (i < lines.length) {
      const raw = lines[i];
      const lineNo = i + 1;
      if (this.inBody) {
        if (raw.trim() === '}') {
          const text = this.bodyLines.join('\n');
          this.bodyIdea.payload = [this.bodyKind, text];
          if (this.current) this.current.ideas.push(this.bodyIdea);
          this.inBody = false;
          this.bodyLines = [];
          this.bodyIdea = null;
          this.bodyKind = '';
          i += 1;
          continue;
        }
        this.bodyLines.push(raw);
        i += 1;
        continue;
      }
      const stripped = raw.trim();
      if (!stripped) { i += 1; continue; }
      if (stripped.startsWith('#')) { i += 1; continue; }
      let m = /^\$0:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$/.exec(stripped);
      if (m) {
        if (this.inGlossary) throw new ParseError('G002_GLOSSARY_REOPENED', '$0 reopened', lineNo);
        this.inGlossary = true;
        this.doc.glossary.capa = m[1];
        i += 1;
        continue;
      }
      if (/^\$0:\s+/.test(stripped) && !/^\$0:\s*(?:format|enum_|micro_|namespace_|extension_|sigil-map)/.test(stripped)) {
        if (this.inGlossary) throw new ParseError('G002_GLOSSARY_REOPENED', '$0 reopened', lineNo);
        this.inGlossary = true;
        i += 1;
        continue;
      }
      m = /^\$([1-9][0-9]*):(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$/.exec(stripped);
      if (m) {
        this.startSection(Number(m[1]), null, m[2], lineNo);
        i += 1;
        continue;
      }
      m = /^\$([0-9]+)(?:\s+(.*))?$/.exec(stripped);
      if (m && !stripped.startsWith('$0:')) {
        const sid = Number(m[1]);
        if (sid === 0) {
          if (this.inGlossary) throw new ParseError('G002_GLOSSARY_REOPENED', '$0 reopened', lineNo);
          this.inGlossary = true;
          i += 1;
          continue;
        }
        let title = m[2] !== undefined ? m[2].trim() : null;
        let capa = null;
        if (title) {
          const cm = /:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)\s*$/.exec(title);
          if (cm) {
            capa = cm[1];
            title = title.slice(0, cm.index).trim();
          }
        }
        this.startSection(sid, title || null, capa, lineNo);
        i += 1;
        continue;
      }
      m = /^\$([1-9][0-9]*):\s+(.*)$/.exec(stripped);
      if (m) {
        let title = m[2].trim();
        let capa = null;
        const cm = /:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)\s*$/.exec(title);
        if (cm) {
          capa = cm[1];
          title = title.slice(0, cm.index).trim();
        }
        this.startSection(Number(m[1]), title, capa, lineNo);
        i += 1;
        continue;
      }
      if (this.inGlossary && (stripped.startsWith('$0:') || isGlossaryDeclLine(stripped))) {
        this.parseGlossaryDeclaration(stripped, lineNo);
        i += 1;
        continue;
      }
      if (this.current === null && !this.inGlossary) {
        throw new ParseError('S005_CONTENT_OUTSIDE_SECTION', `Content outside section: ${stripped}`, lineNo);
      }
      if (this.inGlossary) {
        this.parseGlossaryDeclaration(stripped, lineNo);
        i += 1;
        continue;
      }
      const idea = this.parseIdeaLine(stripped, this.current.id, lineNo);
      if ((idea.shape === 'cuerpo' || idea.shape === 'bloque') && idea.payload && idea.payload[0] === '_multiline_body') {
        this.inBody = true;
        this.bodyLines = [];
        this.bodyIdea = idea;
        this.bodyKind = idea.shape;
        i += 1;
        continue;
      }
      this.current.ideas.push(idea);
      i += 1;
    }
    if (this.seenAnySlots && !this.seenSigilMap) {
      throw new ParseError('G030_SIGIL_MAP_REQUIRED', '0.2 uses slots but $0:sigil-map is missing');
    }
    if (this.inBody) throw new ParseError('S007_UNCLOSED_BODY', 'Unclosed body');
    return this.doc;
  }

  startSection(sid, title, capa, lineNo) {
    if (this.seenSectionIds.has(sid)) {
      throw new ParseError('S002_DUPLICATE_SECTION', `Duplicate section $${sid}`, lineNo);
    }
    this.seenSectionIds.add(sid);
    if (this.seenAnySlots && !this.seenSigilMap) {
      throw new ParseError('G030_SIGIL_MAP_REQUIRED', '0.2 uses slots but $0:sigil-map is missing', lineNo);
    }
    const section = new Section({ id: sid, title, ideas: [], capa });
    this.doc.sections.push(section);
    this.current = section;
    this.inGlossary = false;
  }

  parseGlossaryDeclaration(line, lineNo) {
    const braceIdx = line.indexOf('{');
    if (braceIdx < 0) {
      throw new ParseError('G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS', `Glossary declaration must use attrs: ${line}`, lineNo);
    }
    let depth = 0;
    let closeIdx = -1;
    for (let i = braceIdx; i < line.length; i += 1) {
      if (line[i] === '{') depth += 1;
      else if (line[i] === '}') {
        depth -= 1;
        if (depth === 0) { closeIdx = i; break; }
      }
    }
    if (closeIdx < 0) throw new ParseError('S006_INVALID_ATTRS', 'Unclosed {', lineNo);
    const head = line.slice(0, braceIdx).trim();
    const payload = line.slice(braceIdx, closeIdx + 1);
    const tail = line.slice(closeIdx + 1).trim();
    let capa = null;
    if (tail) {
      const cm = /^:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$/.exec(tail);
      if (cm) capa = cm[1];
    }
    if (head.startsWith('$0:')) {
      this.addMetaDeclaration(head.slice(3), payload, lineNo, capa);
      return;
    }
    const m = /^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):(.+)$/.exec(head);
    if (!m) throw new ParseError('L001_INVALID_SYMBOL', `Invalid sigil declaration head: ${head}`, lineNo);
    const ns = m[1] || null;
    const sigil = m[2];
    const label = m[3];
    const key = `${ns || ''}\u0000${sigil}`;
    if (this.seenSymbolKeys.has(key)) {
      throw new ParseError('G015_DUPLICATE_SYMBOL', `Duplicate symbol ${ns ? `${ns}::` : ''}${sigil}`, lineNo);
    }
    const attrs = parseAttrsPayload(payload, lineNo);
    const sym = this.buildSymbolDef(ns, sigil, label, attrs, lineNo);
    this.doc.glossary.symbols.push(sym);
    this.seenSymbolKeys.add(key);
  }

  addMetaDeclaration(name, payload, lineNo, capa) {
    const attrs = parseAttrsPayload(payload, lineNo);
    if (name !== 'sigil-map') {
      for (const [k, v] of attrs) {
        if (k.includes(SLOT_MARKER)) {
          throw new ParseError('I050_SLOT_NOT_ALLOWED_IN_GLOSSARY', `※ in $0:${name} key ${k}`, lineNo);
        }
        if (v.kind === 'string' && typeof v.value === 'string' && v.value.includes(SLOT_MARKER)) {
          throw new ParseError('I050_SLOT_NOT_ALLOWED_IN_GLOSSARY', `※ in $0:${name} attr ${k}`, lineNo);
        }
      }
    }
    const map = attrMap(attrs);
    if (name === 'format') {
      if (this.doc.glossary.format !== null) throw new ParseError('G006_DUPLICATE_FORMAT', 'Duplicate $0:format', lineNo);
      const cortex = map.has('cortex') ? map.get('cortex').value : '0.1';
      const encoding = map.has('encoding') ? map.get('encoding').value : 'UTF-8';
      if (cortex !== '0.2' && cortex !== '1.0') {
        throw new ParseError('G007_UNSUPPORTED_VERSION', `Declared cortex ${cortex} != parser version ${this.doc.cortex_version}`, lineNo);
      }
      if (encoding !== 'UTF-8') {
        throw new ParseError('G011_ENCODING_REQUIRED', `Encoding must be UTF-8: ${encoding}`, lineNo);
      }
      this.doc.glossary.format = new FormatDecl({ cortex, encoding, attrs, sourceLine: lineNo });
      return;
    }
    if (name === 'sigil-map') {
      if (this.seenAnySlots) throw new ParseError('G041_SIGIL_MAP_ORDER', '$0:sigil-map must appear before any sigil with encoding:slots', lineNo);
      if (this.seenSigilMap) throw new ParseError('G031_DUPLICATE_SIGIL_MAP', 'More than one $0:sigil-map', lineNo);
      const sm = new SigilMapDecl({
        marker: map.has('marker') ? map.get('marker').value : SLOT_MARKER,
        codepoint: map.has('codepoint') ? map.get('codepoint').value : 'U+203B',
        base: map.has('base') && map.get('base').kind === 'integer' ? Number(map.get('base').value) : 1,
        syntax: map.has('syntax') ? map.get('syntax').value : '※N:valor',
        order: map.has('order') ? map.get('order').value : 'ascending',
        sourceLine: lineNo,
      });
      if (sm.marker !== SLOT_MARKER || sm.codepoint !== 'U+203B' || sm.base !== 1 || sm.syntax !== '※N:valor' || sm.order !== 'ascending') {
        throw new ParseError('G032_INVALID_SIGIL_MAP', 'sigil-map values are not canonical', lineNo);
      }
      this.doc.glossary.sigil_map = sm;
      this.seenSigilMap = true;
      return;
    }
    if (name.startsWith('enum_')) {
      const ename = name.slice(5);
      const v = map.get('values');
      if (!v || v.kind !== 'string') throw new ParseError('G014_INVALID_ENUM', `enum ${ename} missing values string`, lineNo);
      this.doc.glossary.enums.push(new EnumDecl({ name: ename, values: v.value.split('|'), sourceLine: lineNo }));
      return;
    }
    if (name.startsWith('micro_')) {
      const token = name.slice(6);
      const v = map.get('expand');
      if (!v) throw new ParseError('G012_INVALID_MICRO', `micro ${token} missing expand`, lineNo);
      const expand = v.kind === 'atom' || v.kind === 'string' ? v.value : v.lexeme;
      this.doc.glossary.micros.push(new MicroDecl({ token, expand, sourceLine: lineNo }));
      return;
    }
    if (name.startsWith('namespace_')) {
      this.doc.glossary.namespaces.push(new NamespaceDecl({ alias: name.slice(10), attrs, sourceLine: lineNo }));
      return;
    }
    if (name.startsWith('extension_')) {
      this.doc.glossary.extensions.push(new ExtensionDecl({ name: name.slice(10), attrs, sourceLine: lineNo }));
      return;
    }
    this.doc.glossary.meta.push(new MetaDecl({ name, attrs, capa, sourceLine: lineNo }));
  }

  buildSymbolDef(ns, sigil, label, attrs, lineNo) {
    const map = attrMap(attrs);
    const typeV = map.get('type');
    if (!typeV) throw new ParseError('G016_SYMBOL_TYPE_REQUIRED', `sigil ${sigil} missing type`, lineNo);
    const shape = typeV.kind === 'atom' || typeV.kind === 'string' ? typeV.value : typeV.lexeme;
    if (!inSet(shape, ['attrs', 'attrs-pos', 'cuerpo', 'bloque', 'relacion'])) {
      throw new ParseError('G017_UNKNOWN_SHAPE', `Unknown shape: ${shape}`, lineNo);
    }
    const weightV = map.get('weight');
    if (!weightV) throw new ParseError('G018_SYMBOL_WEIGHT_REQUIRED', `sigil ${sigil} missing weight`, lineNo);
    const weight = weightV.kind === 'atom' || weightV.kind === 'string' ? weightV.value : weightV.lexeme;
    if (!inSet(weight, ['B', 'M', 'H'])) throw new ParseError('G019_INVALID_WEIGHT', `Invalid weight: ${weight}`, lineNo);
    const descV = map.get('desc');
    if (!descV) throw new ParseError('G020_SYMBOL_DESCRIPTION_REQUIRED', `sigil ${sigil} missing desc`, lineNo);
    const desc = descV.kind === 'string' ? descV.value : descV.lexeme;
    let isOpen = false;
    if (map.has('open')) {
      const v = map.get('open');
      isOpen = (v.kind === 'boolean' && v.value === true) || (v.kind === 'atom' && v.value === 'true');
    }
    let encoding = null;
    if (map.has('encoding')) {
      const v = map.get('encoding');
      encoding = v.kind === 'atom' || v.kind === 'string' ? v.value : v.lexeme;
      if (encoding !== 'slots') throw new ParseError('G039_ENCODING_SHAPE_MISMATCH', `Unknown encoding: ${encoding}`, lineNo);
      if (!inSet(shape, ['attrs', 'attrs-pos', 'relacion'])) {
        throw new ParseError('G039_ENCODING_SHAPE_MISMATCH', `encoding:slots not valid for shape ${shape}`, lineNo);
      }
      this.seenAnySlots = true;
      if (!this.seenSigilMap) {
        throw new ParseError('G030_SIGIL_MAP_REQUIRED', `sigil ${sigil} uses encoding:slots but $0:sigil-map not yet declared`, lineNo);
      }
    }
    let contract = [];
    if (encoding === 'slots') {
      const slotsV = map.get('slots');
      if (!slotsV) throw new ParseError('G033_SLOT_CONTRACT_REQUIRED', `sigil ${sigil} with encoding:slots missing slots`, lineNo);
      const slotsStr = slotsV.kind === 'string' ? slotsV.value : slotsV.lexeme;
      if (hasKey(attrs, 'fields') || hasKey(attrs, 'pos')) {
        throw new ParseError('G040_CONTRACT_SURFACE_CONFLICT', `sigil ${sigil} cannot have fields/pos + slots`, lineNo);
      }
      contract = parseSlotContract(slotsStr, lineNo);
      if (isOpen) throw new ParseError('G038_SLOTS_OPEN_FORBIDDEN', `sigil ${sigil} slots cannot be open`, lineNo);
    } else if (shape === 'attrs') {
      const fieldsV = map.get('fields');
      if (!fieldsV) throw new ParseError('G021_ATTRS_CONTRACT_REQUIRED', `sigil ${sigil} missing fields`, lineNo);
      contract = parseContractFields(fieldsV.value);
    } else if (shape === 'attrs-pos' || shape === 'relacion') {
      const posV = map.get('pos');
      if (!posV) throw new ParseError('G022_POSITIONAL_CONTRACT_REQUIRED', `sigil ${sigil} missing pos`, lineNo);
      contract = parseContractFields(posV.value);
      if (shape === 'relacion' && contract.length < 3) {
        throw new ParseError('G023_RELATION_CONTRACT_TOO_SHORT', 'relacion needs >=3 fields', lineNo);
      }
    }
    let focus = null;
    if (map.has('focus')) {
      const v = map.get('focus');
      focus = v.kind === 'atom' || v.kind === 'string' ? v.value : v.lexeme;
      if (inSet(shape, ['attrs', 'attrs-pos', 'relacion'])) {
        const field = contract.find((f) => f.name === focus);
        if (!field) {
          if (encoding === 'slots') throw new ParseError('G037_SLOT_FOCUS_UNRESOLVED', `focus ${focus} not in slot contract`, lineNo);
          throw new ParseError('G025_UNKNOWN_FOCUS_FIELD', `focus ${focus} not in contract`, lineNo);
        }
        if (encoding === 'slots' && !field.required) {
          throw new ParseError('G037_SLOT_FOCUS_UNRESOLVED', `focus ${focus} must be a required slot`, lineNo);
        }
      }
    } else if (shape === 'cuerpo' || shape === 'bloque') {
      focus = '$body';
    } else {
      throw new ParseError('G024_FOCUS_REQUIRED', `sigil ${sigil} missing focus`, lineNo);
    }
    const sym = new SymbolDef({ namespace: ns, sigil, label, shape, weight, focus, desc, open: isOpen, contract, attrs, sourceLine: lineNo });
    sym.encoding = encoding;
    return sym;
  }

  parseIdeaLine(line, sectionId, lineNo) {
    const m = /^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):([^{|}\s]+)/.exec(line);
    if (!m) throw new ParseError('S003_INVALID_IDEA_HEAD', `Invalid idea head: ${line}`, lineNo);
    const ns = m[1] || null;
    const sigil = m[2];
    const name = m[3];
    const rest = line.slice(m[0].length);
    const sym = this.doc.glossary.symbols.find((s) => s.sigil === sigil && s.namespace === ns);
    if (!sym) throw new ParseError('I001_UNDECLARED_SYMBOL', `Undeclared sigil: ${sigil}`, lineNo);
    const addr = `$${sectionId}:${ns ? `${ns}::` : ''}${sigil}:${name}`;
    if (this.seenIdeaAddresses.has(addr)) {
      throw new ParseError('I006_DUPLICATE_IDEA_ADDRESS', `Duplicate idea address ${addr}`, lineNo);
    }
    this.seenIdeaAddresses.add(addr);
    if (sym.encoding === 'slots') {
      if (!rest.startsWith('{')) throw new ParseError('I004_SHAPE_DELIMITER_MISMATCH', 'Expected { for slot-encoded Idea', lineNo);
      if (!rest.endsWith('}') || rest.includes('\n')) {
        throw new ParseError('I004_SHAPE_DELIMITER_MISMATCH', 'Slot-encoded Idea must be single-line', lineNo);
      }
      const entries = parseSlotPayload(rest, lineNo);
      const fvs = resolveSlotEntries(entries, sym, lineNo);
      return new Idea({ section: sectionId, namespace: ns, symbol: sigil, name, shape: sym.shape, payload: ['slots', fvs], sourceLine: lineNo });
    }
    return this.parseIdeaLineLegacy(sectionId, lineNo, ns, sigil, name, rest, sym);
  }

  parseIdeaLineLegacy(sectionId, lineNo, ns, sigil, name, rest, sym) {
    const shape = sym.shape;
    if (shape === 'attrs' || shape === 'cuerpo' || shape === 'bloque') {
      if (!rest.startsWith('{')) throw new ParseError('I004_SHAPE_DELIMITER_MISMATCH', `Expected { for shape ${shape}`, lineNo);
      if (rest.endsWith('}') && !rest.includes('\n')) {
        if (shape === 'attrs') {
          const pairs = parseAttrsPayload(rest, lineNo);
          validateAttrsPayload(pairs, sym, lineNo);
          return new Idea({ section: sectionId, namespace: ns, symbol: sigil, name, shape, payload: ['attrs', pairs], sourceLine: lineNo });
        }
        let inner = rest.slice(1, -1);
        if (shape === 'cuerpo') inner = toNfc(inner);
        return new Idea({ section: sectionId, namespace: ns, symbol: sigil, name, shape, payload: [shape, inner], sourceLine: lineNo });
      }
      if (rest.trim() !== '{') throw new ParseError('I004_SHAPE_DELIMITER_MISMATCH', `Expected single { for multiline ${shape}`, lineNo);
      return new Idea({ section: sectionId, namespace: ns, symbol: sigil, name, shape, payload: ['_multiline_body', null], sourceLine: lineNo });
    }
    if (shape === 'attrs-pos' || shape === 'relacion') {
      if (!rest.startsWith('|')) throw new ParseError('I004_SHAPE_DELIMITER_MISMATCH', `Expected | for shape ${shape}`, lineNo);
      const cells = parsePipeCells(rest.slice(1), lineNo);
      const required = sym.contract.filter((f) => f.required).length;
      if (cells.length < required) {
        throw new ParseError('I012_POSITIONAL_ARITY', `shape ${shape} needs ≥${required} cells, got ${cells.length}`, lineNo);
      }
      if (cells.length > sym.contract.length) {
        throw new ParseError('I012_POSITIONAL_ARITY', `shape ${shape} expects ≤${sym.contract.length} cells, got ${cells.length}`, lineNo);
      }
      return new Idea({ section: sectionId, namespace: ns, symbol: sigil, name, shape, payload: [shape, cells], sourceLine: lineNo });
    }
    throw new ParseError('S999_INTERNAL_PARSE_FAILURE', `Cannot parse idea: ${lineNo}`, lineNo);
  }
}

function validateAttrsPayload(pairs, sym, lineNo) {
  const seen = new Set();
  for (const [k] of pairs) {
    if (seen.has(k)) throw new ParseError('I006_DUPLICATE_FIELD', `Duplicate field ${k}`, lineNo);
    seen.add(k);
  }
  if (!sym.open) {
    const names = new Set(sym.contract.map((f) => f.name));
    for (const [k] of pairs) {
      if (!names.has(k)) throw new ParseError('I005_UNKNOWN_FIELD', `Unknown field ${k}`, lineNo);
    }
  }
  for (const f of sym.contract) {
    if (f.required && !seen.has(f.name)) throw new ParseError('I008_REQUIRED_FIELD_MISSING', `Required field ${f.name} missing`, lineNo);
  }
}

function parseSlotContract(source, line) {
  const out = [];
  if (!source) return out;
  for (const rawPart of source.split('|')) {
    const part = rawPart.trim();
    if (!part) throw new ParseError('G008_INVALID_CONTRACT', `Empty slot-contract entry in ${source}`, line);
    const eq = part.indexOf('=');
    if (eq < 0) throw new ParseError('G008_INVALID_CONTRACT', `Slot entry missing '=': ${part}`, line);
    const posStr = part.slice(0, eq).trim();
    let rest = part.slice(eq + 1);
    if (!/^[1-9][0-9]*$/.test(posStr)) throw new ParseError('G008_INVALID_CONTRACT', `Invalid slot position ${posStr}`, line);
    const position = Number(posStr);
    if (position === 0) throw new ParseError('L022_SLOT_ZERO_FORBIDDEN', 'Slot position 0 forbidden', line);
    if (position > SLOT_INDEX_MAX) throw new ParseError('I057_SLOT_INDEX_LIMIT', `Slot position ${position} exceeds max`, line);
    let required = true;
    if (rest.endsWith('?')) { required = false; rest = rest.slice(0, -1); }
    let name = rest;
    let type = 'any';
    const colon = rest.indexOf(':');
    if (colon >= 0) { name = rest.slice(0, colon); type = rest.slice(colon + 1); }
    name = name.trim();
    type = type.trim();
    if (!name) throw new ParseError('G008_INVALID_CONTRACT', `Empty slot name in ${part}`, line);
    const field = new ContractField({ name, type, required });
    field.position = position;
    out.push(field);
  }
  const seenPos = new Set();
  const seenName = new Set();
  for (const f of out) {
    if (seenPos.has(f.position)) throw new ParseError('G035_DUPLICATE_SLOT_POSITION', `Duplicate slot position ${f.position}`, line);
    if (seenName.has(f.name)) throw new ParseError('G036_DUPLICATE_SLOT_NAME', `Duplicate slot name ${f.name}`, line);
    seenPos.add(f.position);
    seenName.add(f.name);
  }
  const sorted = [...out].sort((a, b) => a.position - b.position);
  let expected = 1;
  for (const f of sorted) {
    if (f.position !== expected) throw new ParseError('G034_SLOT_CONTRACT_GAP', `Slot positions not contiguous: expected ${expected}, got ${f.position}`, line);
    expected += 1;
  }
  return out;
}

function parseSlotPayload(source, startLine) {
  const cur = new StringCursor(source, startLine, 1);
  skipInlineWs(cur);
  if (cur.peek() !== '{') throw new ParseError('S006_INVALID_ATTRS', 'Expected { for slot payload', cur.line, cur.col);
  cur.next();
  const entries = [];
  skipInlineWs(cur);
  if (cur.peek() === '}') { cur.next(); return entries; }
  checkSlotStart(cur);
  while (true) {
    skipInlineWs(cur);
    checkSlotStart(cur);
    const index = parseSlotRef(cur);
    skipInlineWs(cur);
    const value = parseScalar(cur);
    entries.push([index, value]);
    skipInlineWs(cur);
    const c = cur.peek();
    if (c === ',') {
      cur.next();
      skipInlineWs(cur);
      if (cur.peek() === '}') { cur.next(); throw new ParseError('S006_INVALID_ATTRS', 'Trailing comma before } in slot payload', cur.line, cur.col); }
    } else if (c === '}') {
      cur.next();
      break;
    } else {
      throw new ParseError('S006_INVALID_ATTRS', `Expected , or } got ${c}`, cur.line, cur.col);
    }
  }
  return entries;
}

function checkSlotStart(cur) {
  const ch = cur.peek();
  if (ch === '') return;
  if (ch === SLOT_MARKER) return;
  if (HOMOGLYPHS[ch]) throw new ParseError('L020_INVALID_SLOT_MARKER', `Slot marker is not ※ (got ${HOMOGLYPHS[ch]})`, cur.line, cur.col);
  if (ch === '|') throw new ParseError('I056_PIPE_PAYLOAD_IN_SLOT_IDEA', 'Pipe payload not allowed in slot-encoded Idea', cur.line, cur.col);
  if (/[A-Za-z_]/.test(ch)) {
    const save = [cur.i, cur.line, cur.col];
    while (cur.peek() && !' \t:,'.includes(cur.peek())) {
      if (cur.peek() === '}') break;
      cur.next();
    }
    if (cur.peek() === ':') throw new ParseError('I055_NAMED_ATTR_IN_SLOT_IDEA', 'Named key:value not allowed in slot-encoded Idea', save[1], save[2]);
    [cur.i, cur.line, cur.col] = save;
  }
}

function parseSlotRef(cur) {
  const ch = cur.peek();
  if (ch !== SLOT_MARKER) {
    if (HOMOGLYPHS[ch]) throw new ParseError('L020_INVALID_SLOT_MARKER', `Slot marker is not ※ (got ${HOMOGLYPHS[ch]})`, cur.line, cur.col);
    throw new ParseError('L020_INVALID_SLOT_MARKER', `Expected ※ at start of slot ref, got ${ch}`, cur.line, cur.col);
  }
  cur.next();
  const digits = [];
  while (/[0-9]/.test(cur.peek())) { digits.push(cur.peek()); cur.next(); }
  if (!digits.length) throw new ParseError('L021_INVALID_SLOT_INDEX', 'Missing integer after ※', cur.line, cur.col);
  const raw = digits.join('');
  if (raw.length > 1 && raw[0] === '0') throw new ParseError('L023_SLOT_LEADING_ZERO', `Slot index has leading zero: ※${raw}`, cur.line, cur.col);
  if (raw === '0') throw new ParseError('L022_SLOT_ZERO_FORBIDDEN', 'Slot index 0 is forbidden', cur.line, cur.col);
  const index = Number(raw);
  if (index > SLOT_INDEX_MAX) throw new ParseError('I057_SLOT_INDEX_LIMIT', `Slot index ${index} exceeds max`, cur.line, cur.col);
  if (cur.peek() !== ':') throw new ParseError('L024_SLOT_SEPARATOR_REQUIRED', `Missing ':' after slot index ※${raw}`, cur.line, cur.col);
  cur.next();
  return index;
}

function resolveSlotEntries(entries, sym, lineNo) {
  const seen = new Set();
  const out = [];
  let last = 0;
  for (const [index, value] of entries) {
    if (seen.has(index)) throw new ParseError('I051_DUPLICATE_SLOT', `slot ※${index} duplicated`, lineNo);
    seen.add(index);
    if (index <= last) throw new ParseError('I054_SLOT_OUT_OF_ORDER', `slots not in ascending order (※${index} after ※${last})`, lineNo);
    last = index;
    const field = sym.contract.find((f) => f.position === index);
    if (!field) throw new ParseError('I052_UNKNOWN_SLOT', `slot ※${index} not declared in contract`, lineNo);
    out.push({ position: index, name: field.name, type: field.type, required: field.required, value });
  }
  for (const f of sym.contract) {
    if (f.required && !seen.has(f.position)) throw new ParseError('I053_MISSING_REQUIRED_SLOT', `missing required slot ※${f.position} (${f.name})`, lineNo);
  }
  return out;
}

function parseV10(source, version = '0.2') {
  if (source.startsWith('\ufeff')) throw new ParseError('U001_BOM_FORBIDDEN', 'BOM forbidden');
  return new V10Parser(normalizeLineEndings(source), version).parse();
}

// ---------------------------------------------------------------------------
// C14N 1.0
// ---------------------------------------------------------------------------

function nfcScalar(s) {
  if (s.kind === 'string') {
    const v = toNfc(s.value);
    return new Scalar('string', v, emitStringLiteral(v));
  }
  if (s.kind === 'atom') {
    const v = toNfc(s.value);
    return new Scalar('atom', v, v);
  }
  if (s.kind === 'list') {
    const items = s.value.map(nfcScalar);
    return new Scalar('list', items, `[${items.map((i) => i.lexeme).join(',')}]`);
  }
  return s;
}

function preNormalize(doc) {
  const gl = doc.glossary;
  if (gl.format) gl.format.attrs = gl.format.attrs.map(([k, v]) => [k, nfcScalar(v)]);
  for (const e of gl.enums) e.values = e.values.map(toNfc);
  for (const m of gl.micros) m.expand = toNfc(m.expand);
  for (const ns of gl.namespaces) ns.attrs = ns.attrs.map(([k, v]) => [k, nfcScalar(v)]);
  for (const ext of gl.extensions) ext.attrs = ext.attrs.map(([k, v]) => [k, nfcScalar(v)]);
  for (const md of gl.meta) md.attrs = md.attrs.map(([k, v]) => [k, nfcScalar(v)]);
  for (const sym of gl.symbols) {
    sym.attrs = sym.attrs.map(([k, v]) => [k, nfcScalar(v)]);
    sym.desc = toNfc(sym.desc);
  }
  const micro = new Map(gl.micros.map((m) => [m.token, m.expand]));
  for (const sec of doc.sections) {
    for (const idea of sec.ideas) {
      if (!idea.payload) continue;
      const kind = idea.payload[0];
      if (kind === 'attrs') {
        idea.payload = ['attrs', idea.payload[1].map(([k, v]) => [k, nfcScalar(v)])];
      } else if (kind === 'attrs-pos' || kind === 'relacion') {
        idea.payload = [kind, idea.payload[1].map(nfcScalar)];
      } else if (kind === 'slots') {
        idea.payload = ['slots', idea.payload[1].map((fv) => {
          let v = fv.value;
          if (v.kind === 'atom' && micro.has(v.value)) {
            const ex = micro.get(v.value);
            v = new Scalar('atom', ex, ex);
          }
          return { ...fv, value: nfcScalar(v) };
        })];
      } else if (kind === 'cuerpo') {
        idea.payload = ['cuerpo', toNfc(idea.payload[1])];
      }
    }
    if (sec.title !== null && sec.title !== undefined) sec.title = toNfc(sec.title);
  }
}

function sortKeysCanonical(pairs, order) {
  const byKey = new Map(pairs);
  const out = [];
  const used = new Set();
  for (const k of order) {
    if (byKey.has(k)) { out.push([k, byKey.get(k)]); used.add(k); }
  }
  const extras = pairs.filter(([k]) => !used.has(k));
  extras.sort((a, b) => utf8Compare(a[0], b[0]));
  return out.concat(extras);
}

function isAtomSafeBare(s) {
  return s !== '' && !/[\s[\]{},"|]/.test(s);
}

function emitScalarAttrs(v, isFocusText, isTextField) {
  if (v.kind === 'string') {
    if (isFocusText) return v.lexeme;
    if (isTextField && isAtomSafeBare(v.value) && ATOM_RE.test(v.value)) return v.value;
    return v.lexeme;
  }
  if (v.kind === 'atom') {
    if (isAtomSafeBare(v.value)) return v.value;
    return emitStringLiteral(v.value);
  }
  return v.lexeme;
}

function emitGlossaryAttrs(pairs) {
  return `{${pairs.map(([k, v]) => `${k}:${v.lexeme}`).join(',')}}`;
}

function canonicalizeV10(doc) {
  preNormalize(doc);
  const lines = [];
  lines.push(doc.glossary.capa ? `$0:${doc.glossary.capa}` : '$0');
  if (doc.glossary.format) lines.push(`$0:format${emitGlossaryAttrs(sortKeysCanonical(doc.glossary.format.attrs, FORMAT_KEY_ORDER))}`);
  const anySlots = doc.glossary.symbols.some((s) => s.encoding === 'slots');
  if (anySlots && doc.glossary.sigil_map) {
    const sm = doc.glossary.sigil_map;
    const attrs = [
      ['marker', new Scalar('string', sm.marker, emitStringLiteral(sm.marker))],
      ['codepoint', new Scalar('string', sm.codepoint, emitStringLiteral(sm.codepoint))],
      ['base', new Scalar('integer', String(sm.base), String(sm.base))],
      ['syntax', new Scalar('string', sm.syntax, emitStringLiteral(sm.syntax))],
      ['order', new Scalar('string', sm.order, emitStringLiteral(sm.order))],
    ];
    lines.push(`$0:sigil-map${emitGlossaryAttrs(sortKeysCanonical(attrs, SIGIL_MAP_KEY_ORDER))}`);
  }
  const enums = [...doc.glossary.enums].sort((a, b) => utf8Compare(a.name, b.name));
  for (const e of enums) {
    const values = e.values.join('|');
    lines.push(`$0:enum_${e.name}${emitGlossaryAttrs(sortKeysCanonical([['values', new Scalar('string', values, emitStringLiteral(values))]], ENUM_KEY_ORDER))}`);
  }
  const micros = [...doc.glossary.micros].sort((a, b) => utf8Compare(a.token, b.token));
  for (const m of micros) {
    const v = ATOM_RE.test(m.expand) ? new Scalar('atom', m.expand, m.expand) : new Scalar('string', m.expand, emitStringLiteral(m.expand));
    lines.push(`$0:micro_${m.token}${emitGlossaryAttrs(sortKeysCanonical([['expand', v]], MICRO_KEY_ORDER))}`);
  }
  const nss = [...doc.glossary.namespaces].sort((a, b) => utf8Compare(a.alias, b.alias));
  for (const ns of nss) lines.push(`$0:namespace_${ns.alias}${emitGlossaryAttrs(sortKeysCanonical(ns.attrs, NS_KEY_ORDER))}`);
  const exts = [...doc.glossary.extensions].sort((a, b) => utf8Compare(a.name, b.name));
  for (const e of exts) lines.push(`$0:extension_${e.name}${emitGlossaryAttrs(sortKeysCanonical(e.attrs, EXT_KEY_ORDER))}`);
  const meta = [...doc.glossary.meta].sort((a, b) => utf8Compare(a.name, b.name));
  for (const m of meta) {
    const attrs = [...m.attrs].sort((a, b) => utf8Compare(a[0], b[0]));
    let line = `$0:${m.name}${emitGlossaryAttrs(attrs)}`;
    if (m.capa) line += `:${m.capa}`;
    lines.push(line);
  }
  const syms = [...doc.glossary.symbols].sort((a, b) => {
    if ((a.namespace || '') !== (b.namespace || '')) return utf8Compare(a.namespace || '', b.namespace || '');
    if (a.sigil !== b.sigil) return utf8Compare(a.sigil, b.sigil);
    return utf8Compare(a.label, b.label);
  });
  for (const s of syms) {
    lines.push(`${s.qualified}:${s.label}${emitGlossaryAttrs(sortKeysCanonical(s.attrs, SIGIL_KEY_ORDER))}`);
  }
  for (const sec of doc.sections) {
    if (sec.title === null || sec.title === undefined) {
      lines.push(sec.capa ? `$${sec.id}:${sec.capa}` : `$${sec.id}`);
    } else {
      lines.push(sec.capa ? `$${sec.id}: ${sec.title}:${sec.capa}` : `$${sec.id}: ${sec.title}`);
    }
    for (const idea of sec.ideas) lines.push(ideaCanonicalV10(idea, doc));
  }
  return `${lines.join('\n')}\n`;
}

function ideaCanonicalV10(idea, doc) {
  const head = `${idea.qualified_symbol}:${idea.name}`;
  const sym = doc.glossary.symbols.find((s) => s.sigil === idea.symbol && (s.namespace || null) === (idea.namespace || null));
  if (idea.payload && idea.payload[0] === 'slots') {
    if (!sym) throw new ParseError('I001_UNDECLARED_SYMBOL', `Undeclared sigil in canonicalize: ${idea.symbol}`);
    const types = new Map(sym.contract.map((f) => [f.position, f.type]));
    const focusField = sym.contract.find((f) => f.name === sym.focus);
    const focusPos = focusField ? focusField.position : null;
    const parts = idea.payload[1].map((fv) => {
      const ftype = types.get(fv.position) || 'any';
      const isText = ftype === 'text';
      const isFocusText = fv.position === focusPos && ftype === 'text';
      return `※${fv.position}:${emitScalarAttrs(fv.value, isFocusText, isText)}`;
    });
    return `${head}{${parts.join(',')}}`;
  }
  if (idea.payload && idea.shape === 'attrs') {
    if (!sym) throw new ParseError('I001_UNDECLARED_SYMBOL', `Undeclared sigil in canonicalize: ${idea.symbol}`);
    const types = new Map(sym.contract.map((f) => [f.name, f.type]));
    const parts = idea.payload[1].map(([k, v]) => {
      const ftype = types.get(k) || 'any';
      return `${k}:${emitScalarAttrs(v, k === sym.focus && ftype === 'text', ftype === 'text')}`;
    });
    return `${head}{${parts.join(',')}}`;
  }
  if (idea.payload && (idea.shape === 'attrs-pos' || idea.shape === 'relacion')) {
    return `${head}|${idea.payload[1].map((c) => c.lexeme).join('|')}`;
  }
  if (idea.payload && idea.shape === 'cuerpo') {
    const text = toNfc(idea.payload[1]);
    return text.includes('\n') ? `${head}{\n${text}\n}` : `${head}{${text}}`;
  }
  if (idea.payload && idea.shape === 'bloque') {
    return `${head}{\n${idea.payload[1]}\n}`;
  }
  return head;
}

// ---------------------------------------------------------------------------
// HCORTEX 1.0 render
// ---------------------------------------------------------------------------

function renderHCORTEX10(doc) {
  const out = [];
  const version = doc.cortex_version === '0.2' ? '0.2' : '1.0';
  out.push(`<!-- HCORTEX v=${version} t=canonical k=corpus -->`);
  out.push('');
  out.push('<!-- glossary -->');
  out.push(renderGlossary(doc));
  out.push('<!-- /glossary -->');
  out.push('');
  const lookup = new Map(doc.glossary.symbols.map((s) => [`${s.namespace || ''}\u0000${s.sigil}`, s]));
  for (const sec of doc.sections) {
    out.push(`## §${sec.id}: ${sec.title || `Sección ${sec.id}`}`);
    out.push('');
    out.push(`<!-- schema:${sec.id}${sec.capa ? ` capa:${sec.capa}` : ''} -->`);
    for (const idea of sec.ideas) {
      const sym = lookup.get(`${idea.namespace || ''}\u0000${idea.symbol}`);
      out.push(...renderIdea(idea, sym));
      out.push('');
    }
    out.push(`<!-- /schema:${sec.id} -->`);
    out.push('');
  }
  return `${out.join('\n')}\n`;
}

function renderGlossary(doc) {
  const gl = doc.glossary;
  const lines = [];
  if (gl.capa) lines.push(`$0:${gl.capa}`);
  if (gl.format) lines.push(`$0:format{${gl.format.attrs.map(([k, v]) => `${k}:${v.lexeme}`).join(',')}}`);
  for (const e of gl.enums) lines.push(`$0:enum_${e.name}{values:"${e.values.join('|')}"}`);
  for (const m of gl.micros) {
    let expand = m.expand;
    if (expand.startsWith('"') && expand.endsWith('"') && expand.length >= 2) expand = expand.slice(1, -1);
    lines.push(expand.includes(' ') || expand === '' ? `$0:micro_${m.token}{expand:"${expand}"}` : `$0:micro_${m.token}{expand:${expand}}`);
  }
  for (const ns of gl.namespaces) lines.push(`$0:namespace_${ns.alias}{${ns.attrs.map(([k, v]) => `${k}:${v.lexeme}`).join(',')}}`);
  for (const ext of gl.extensions) lines.push(`$0:extension_${ext.name}{${ext.attrs.map(([k, v]) => `${k}:${v.lexeme}`).join(',')}}`);
  for (const md of gl.meta) {
    let line = `$0:${md.name}{${md.attrs.map(([k, v]) => `${k}:${v.lexeme}`).join(',')}}`;
    if (md.capa) line += `:${md.capa}`;
    lines.push(line);
  }
  const anySlots = gl.symbols.some((s) => s.encoding === 'slots');
  if (anySlots && gl.sigil_map) {
    const sm = gl.sigil_map;
    const cp = String(sm.codepoint).replace(/^U\+/, '').padStart(4, '0');
    lines.push(`$0:sigil-map{marker:"${sm.marker}",codepoint:"U+${cp}",base:${sm.base},syntax:"${sm.syntax}",order:"${sm.order}"}`);
  }
  for (const s of gl.symbols) {
    const parts = [];
    const seen = new Set();
    for (const [k, v] of s.attrs) {
      if (k === 'contract' || seen.has(k)) continue;
      seen.add(k);
      parts.push(`${k}:${v.lexeme}`);
    }
    const openAttr = s.attrs.find(([k]) => k === 'open');
    if (openAttr && !seen.has('open')) parts.push(`open:${openAttr[1].lexeme}`);
    lines.push(`${s.qualified}:${s.label}{${parts.join(',')}}`);
  }
  return `${lines.join('\n')}\n`;
}

function renderIdea(idea, sym) {
  const out = [`### ${idea.qualified_symbol}:${idea.name}`];
  if (idea.payload && idea.payload[0] === 'slots') {
    const headers = sym ? sym.contract.map((f) => f.name) : [];
    const row = sym ? sym.contract.map((f) => {
      const fv = idea.payload[1].find((x) => x.position === f.position);
      return fv ? fv.value.lexeme : '';
    }) : [];
    out.push(...renderTable(headers, row));
    return out;
  }
  if (idea.shape === 'attrs') {
    let headers = [];
    let row = [];
    if (sym && sym.encoding === 'slots') {
      headers = sym.contract.map((f) => f.name);
      row = sym.contract.map((f) => {
        const pair = idea.payload[1].find(([k]) => k === f.name);
        return pair ? pair[1].lexeme : '';
      });
    } else {
      headers = idea.payload[1].map(([k]) => k);
      row = idea.payload[1].map(([, v]) => v.lexeme);
    }
    out.push(...renderTable(headers, row));
  } else if (idea.shape === 'attrs-pos' || idea.shape === 'relacion') {
    const cells = idea.payload[1];
    const headers = sym ? cells.map((_, idx) => (sym.contract[idx] ? sym.contract[idx].name : `c${idx + 1}`)) : [];
    out.push(...renderTable(headers, cells.map((c) => c.lexeme)));
  } else if (idea.shape === 'cuerpo') {
    out.push(idea.payload[1]);
  } else if (idea.shape === 'bloque') {
    out.push('```');
    out.push(idea.payload[1]);
    out.push('```');
  }
  return out;
}

function renderTable(headers, row) {
  return [
    `| ${headers.join(' | ')} |`,
    `|${'---|'.repeat(headers.length)}`,
    `| ${row.join(' | ')} |`,
  ];
}

// ---------------------------------------------------------------------------
// HCORTEX 1.0 compile
// ---------------------------------------------------------------------------

function fenceMask(lines) {
  const mask = new Array(lines.length).fill(false);
  let i = 0;
  while (i < lines.length) {
    if (lines[i].trimStart().startsWith('```')) {
      let j = i + 1;
      while (j < lines.length && !lines[j].trimStart().startsWith('```')) j += 1;
      if (j < lines.length) {
        for (let k = i; k <= j; k += 1) mask[k] = true;
        i = j + 1;
        continue;
      }
    }
    i += 1;
  }
  return mask;
}

function compileHCORTEX10(text) {
  const diags = [];
  if (text.startsWith('\ufeff')) return { doc: null, diags: [{ code: 'H490', message: 'BOM forbidden' }] };
  text = normalizeLineEndings(text);
  if (/<!--\s*(cortex-ast:|base64:|payload-shadow:|shadow:|ast:|internal:)/.test(text)) {
    return { doc: null, diags: [{ code: 'H481_HIDDEN_COPY', message: 'HCORTEX contains hidden CORTEX/AST copy' }] };
  }
  const vm = /<!--\s*HCORTEX\s+v=([0-9.]+)\s+t=(\w+)(?:\s+k=(\w+))?\s*-->/.exec(text);
  if (!vm) return { doc: null, diags: [{ code: 'H401_MISSING_ENVELOPE', message: 'Missing or malformed HCORTEX envelope' }] };
  const version = vm[1];
  if (version !== '0.2' && version !== '1.0') {
    return { doc: null, diags: [{ code: 'H401_UNSUPPORTED_HCORTEX_VERSION', message: `Unsupported HCORTEX version: ${version}` }] };
  }
  const gm = /<!--\s*glossary\s*-->\n([\s\S]*?)\n<!--\s*\/glossary\s*-->/.exec(text);
  if (!gm) return { doc: null, diags: [{ code: 'H403_MISSING_GLOSSARY_BLOCK', message: 'Missing glossary block' }] };
  let doc;
  try {
    doc = parseV10(`${gm[1].trim()}\n`, version);
  } catch (err) {
    return { doc: null, diags: [{ code: err.code || 'S999', message: `Glossary parse failed: ${err.message}` }] };
  }
  doc.cortex_version = version;
  const lookup = new Map(doc.glossary.symbols.map((s) => [`${s.namespace || ''}\u0000${s.sigil}`, s]));
  const lines = text.split('\n');
  const fenced = fenceMask(lines);
  let i = 0;
  while (i < lines.length) {
    let m = null;
    if (!fenced[i]) m = /^##\s*§(\d+):\s*(.*?)\s*$/.exec(lines[i]);
    if (m && i + 2 < lines.length && lines[i + 1].trim() === '') {
      const sm = /^<!--\s*schema:(\d+)(?:\s+capa:(\w+))?\s*-->$/.exec(lines[i + 2]);
      if (sm) {
        let j = i + 3;
        while (j < lines.length) {
          if (!fenced[j] && /^<!--\s*\/schema:\d+\s*-->$/.test(lines[j])) break;
          j += 1;
        }
        if (j < lines.length) {
          const id = Number(m[1]);
          const title = m[2].trim();
          const section = new Section({ id, title: title === `Sección ${id}` ? null : title, ideas: [], capa: sm[2] || null });
          const body = lines.slice(i + 3, j).join('\n');
          if (body.trim()) section.ideas = parseIdeas(body, id, lookup);
          doc.sections.push(section);
          i = j + 1;
          continue;
        }
      }
    }
    i += 1;
  }
  return { doc, diags };
}

function parseIdeas(body, sectionId, lookup) {
  const lines = body.split('\n');
  const fenced = fenceMask(lines);
  const markers = [];
  for (let i = 0; i < lines.length; i += 1) {
    if (fenced[i]) continue;
    const m = /^### ([!]?(?:\w+::)?[!\w]+):([\w_-]+)\s*$/.exec(lines[i]);
    if (m) markers.push({ line: i, qualified: m[1], name: m[2] });
  }
  const ideas = [];
  for (let idx = 0; idx < markers.length; idx += 1) {
    const mk = markers[idx];
    const end = idx + 1 < markers.length ? markers[idx + 1].line : lines.length;
    const rest = lines.slice(mk.line + 1, end).join('\n').trim();
    let ns = null;
    let sigil = mk.qualified;
    if (mk.qualified.includes('::')) [ns, sigil] = mk.qualified.split('::');
    const sym = lookup.get(`${ns || ''}\u0000${sigil}`) || lookup.get(`\u0000${sigil}`);
    const shape = sym ? sym.shape : 'attrs';
    const encoding = sym ? sym.encoding : null;
    const { rows, order } = parseTableRows(rest);
    if (rows && !(sym && (shape === 'bloque' || shape === 'cuerpo'))) {
      if (encoding === 'slots' && sym) {
        const fvs = [];
        for (const f of sym.contract) {
          const col = rows.get(f.name) || '';
          if (col !== '') fvs.push({ position: f.position, name: f.name, type: f.type, required: f.required, value: makeScalarCell(col) });
        }
        if (fvs.length) ideas.push(new Idea({ section: sectionId, namespace: ns, symbol: sigil, name: mk.name, shape: 'attrs', payload: ['slots', fvs] }));
      } else if (sym && shape === 'cuerpo') {
        ideas.push(new Idea({ section: sectionId, namespace: ns, symbol: sigil, name: mk.name, shape, payload: ['cuerpo', rest] }));
      } else if (sym && shape === 'bloque') {
        ideas.push(new Idea({ section: sectionId, namespace: ns, symbol: sigil, name: mk.name, shape, payload: ['bloque', extractFence(rest)] }));
      } else if (sym && (shape === 'attrs-pos' || shape === 'relacion')) {
        const cells = [];
        for (const f of sym.contract) {
          const val = rows.get(f.name) || '';
          if (val === '' && !f.required) break;
          cells.push(makeScalarCell(val));
        }
        ideas.push(new Idea({ section: sectionId, namespace: ns, symbol: sigil, name: mk.name, shape, payload: [shape, cells] }));
      } else {
        const pairs = order.map((h) => [h, makeScalarCell(rows.get(h) || '')]);
        ideas.push(new Idea({ section: sectionId, namespace: ns, symbol: sigil, name: mk.name, shape: 'attrs', payload: ['attrs', pairs] }));
      }
    } else if (sym && shape === 'cuerpo') {
      ideas.push(new Idea({ section: sectionId, namespace: ns, symbol: sigil, name: mk.name, shape, payload: ['cuerpo', rest] }));
    } else if (sym && shape === 'bloque') {
      ideas.push(new Idea({ section: sectionId, namespace: ns, symbol: sigil, name: mk.name, shape, payload: ['bloque', extractFence(rest)] }));
    } else {
      ideas.push(new Idea({ section: sectionId, namespace: ns, symbol: sigil, name: mk.name, shape, payload: ['attrs', []] }));
    }
  }
  return ideas;
}

function extractFence(rest) {
  const m = /```\s*\n([\s\S]*?)```/.exec(rest);
  return m ? m[1].trim() : rest;
}

function parseTableRows(text) {
  const lines = text.split('\n').map((l) => l.trim()).filter((l) => l !== '');
  const table = lines.filter((l) => l.startsWith('|') && l.endsWith('|'));
  if (table.length < 2) return { rows: null, order: null };
  const headers = splitTableRow(table[0]);
  let data = null;
  for (const line of table.slice(1)) {
    const cells = splitTableRow(line);
    const sep = cells.every((c) => c === '' || /^[-:]+$/.test(c));
    if (sep) continue;
    data = cells;
    break;
  }
  if (!data) return { rows: null, order: null };
  const rows = new Map();
  headers.forEach((h, i) => rows.set(h, i < data.length ? data[i] : ''));
  return { rows, order: headers };
}

function splitTableRow(line) {
  let s = line.trim();
  if (s.startsWith('|')) s = s.slice(1);
  if (s.endsWith('|')) s = s.slice(0, -1);
  const cells = [];
  let buf = '';
  let inQuotes = false;
  let escaped = false;
  for (const ch of s) {
    if (escaped) { buf += ch; escaped = false; continue; }
    if (ch === '\\' && inQuotes) { buf += ch; escaped = true; continue; }
    if (ch === '"') { inQuotes = !inQuotes; buf += ch; continue; }
    if (ch === '|' && !inQuotes) { cells.push(buf.trim()); buf = ''; continue; }
    buf += ch;
  }
  cells.push(buf.trim());
  return cells;
}

function makeScalarCell(lex) {
  lex = lex.trim();
  if (lex === '') return new Scalar('null', null, 'null');
  if (lex.startsWith('"') && lex.endsWith('"') && lex.length >= 2) {
    try {
      const inner = parseStringLiteralSafe(lex.slice(1, -1));
      return new Scalar('string', inner, emitStringLiteral(inner));
    } catch (_) { /* fall through */ }
  }
  if (lex === 'true') return new Scalar('boolean', true, 'true');
  if (lex === 'false') return new Scalar('boolean', false, 'false');
  if (lex === 'null') return new Scalar('null', null, 'null');
  if (lex.startsWith('[') && lex.endsWith(']')) {
    const inner = lex.slice(1, -1).trim();
    if (inner === '') return new Scalar('list', [], '[]');
    const items = inner.split(',').map(makeScalarCell);
    return new Scalar('list', items, `[${items.map((i) => i.lexeme).join(',')}]`);
  }
  return classifyRawCell(lex, 0);
}

function parseStringLiteralSafe(inner) {
  // Reuse the scalar cursor parser on a quoted literal to get escapes right.
  const cur = new StringCursor(`"${inner}"`, 1, 1);
  return parseStringScalar(cur).value;
}

module.exports = {
  parseV10,
  parse_v10: parseV10,
  canonicalizeV10,
  canonicalize_v10: canonicalizeV10,
  renderHCORTEX10,
  render_hcortex10: renderHCORTEX10,
  compileHCORTEX10,
  compile_hcortex10: compileHCORTEX10,
  SigilMapDecl,
};
