'use strict';

/** Scalar value model and lexer for CORTEX 0.1. */

function toNfc(value) {
  return String(value).normalize('NFC');
}

function utf8Bytes(value) {
  return Buffer.from(String(value), 'utf8');
}

function pythonRepr(value) {
  const s = String(value);
  const quote = s.includes("'") && !s.includes('"') ? '"' : "'";
  let out = '';
  for (const ch of s) {
    if (ch === '\\') out += '\\\\';
    else if (ch === quote) out += `\\${ch}`;
    else if (ch === '\n') out += '\\n';
    else if (ch === '\r') out += '\\r';
    else if (ch === '\t') out += '\\t';
    else if (ch === '\b') out += '\\x08';
    else if (ch === '\f') out += '\\x0c';
    else {
      const cp = ch.codePointAt(0);
      if (cp < 0x20 || cp === 0x7f) out += `\\x${cp.toString(16).padStart(2, '0')}`;
      else out += ch;
    }
  }
  return `${quote}${out}${quote}`;
}

class Scalar {
  constructor(kind, value, lexeme) {
    this.kind = kind;
    this.value = value;
    this.lexeme = lexeme;
  }

  clone() {
    if (this.kind === 'list') {
      return new Scalar('list', this.value.map((item) => item.clone()), this.lexeme);
    }
    return new Scalar(this.kind, this.value, this.lexeme);
  }
}

class ParseError extends Error {
  constructor(code, message, line = 0, col = 0) {
    super(`${code} @ ${line}:${col} — ${message}`);
    this.name = 'ParseError';
    this.code = code;
    this.message = message;
    this.line = line;
    this.col = col;
  }
}

const ATOM_BODY_SOURCE = '[_A-Za-z][_A-Za-z0-9./:@+%$-]*';
const ATOM_RE = new RegExp(`^(?:\\$[0-9]+:)?${ATOM_BODY_SOURCE}$`);
const INT_RE = /^-?(0|[1-9][0-9]*)$/;
const DEC_RE = /^-?(0|[1-9][0-9]*)\.[0-9]+$/;

function isAtomLexeme(value) {
  const s = String(value);
  if (!s) return false;
  if (/[\s\[\]{},"|]/u.test(s)) return false;
  if (Array.from(s).length > 32) return false;
  return ATOM_RE.test(s);
}

const ESCAPE_MAP = new Map([
  ['"', '"'],
  ['\\', '\\'],
  ['n', '\n'],
  ['r', '\r'],
  ['t', '\t'],
  ['b', '\b'],
  ['f', '\f'],
]);

const REV_ESCAPE = new Map([
  ['"', '\\"'],
  ['\\', '\\\\'],
  ['\n', '\\n'],
  ['\r', '\\r'],
  ['\t', '\\t'],
  ['\b', '\\b'],
  ['\f', '\\f'],
]);

function parseStringLiteral(source) {
  const chars = Array.from(String(source));
  const out = [];
  let i = 0;
  while (i < chars.length) {
    const c = chars[i];
    if (c === '\\') {
      if (i + 1 >= chars.length) {
        throw new ParseError('L005_INVALID_STRING', 'Trailing backslash in string');
      }
      const next = chars[i + 1];
      if (ESCAPE_MAP.has(next)) {
        out.push(ESCAPE_MAP.get(next));
        i += 2;
      } else if (next === 'u') {
        const hex = chars.slice(i + 2, i + 6).join('');
        if (hex.length !== 4 || !/^[0-9a-fA-F]{4}$/.test(hex)) {
          throw new ParseError('L005_INVALID_STRING', 'Bad \\u escape');
        }
        out.push(String.fromCharCode(Number.parseInt(hex, 16)));
        i += 6;
      } else if (next === '/') {
        out.push('/');
        i += 2;
      } else {
        throw new ParseError('L005_INVALID_STRING', `Unknown escape \\${next}`);
      }
    } else if (c === '"') {
      throw new ParseError('L005_INVALID_STRING', 'Unescaped quote in string body');
    } else {
      out.push(c);
      i += 1;
    }
  }
  return out.join('');
}

function emitStringLiteral(value) {
  const out = [];
  for (const ch of String(value)) {
    if (REV_ESCAPE.has(ch)) {
      out.push(REV_ESCAPE.get(ch));
      continue;
    }
    const codePoint = ch.codePointAt(0);
    if (codePoint < 0x20) {
      out.push(`\\u${codePoint.toString(16).toUpperCase().padStart(4, '0')}`);
    } else if (codePoint === 0x7f) {
      out.push('\\u007F');
    } else {
      out.push(ch);
    }
  }
  return `"${out.join('')}"`;
}

class StringCursor {
  constructor(source, line = 1, col = 1) {
    this.s = String(source);
    this.chars = Array.from(this.s);
    this.i = 0;
    this.line = line;
    this.col = col;
  }

  eof() {
    return this.i >= this.chars.length;
  }

  peek(offset = 0) {
    const index = this.i + offset;
    return index >= 0 && index < this.chars.length ? this.chars[index] : '';
  }

  next() {
    const c = this.chars[this.i];
    this.i += 1;
    if (c === '\n') {
      this.line += 1;
      this.col = 1;
    } else {
      this.col += 1;
    }
    return c;
  }

  slice(start, end = this.i) {
    return this.chars.slice(start, end).join('');
  }
}

function skipInlineWs(cursor) {
  while (cursor.peek() === ' ' || cursor.peek() === '\t') cursor.next();
}

function parseScalar(cursor, inList = false) { // eslint-disable-line no-unused-vars
  skipInlineWs(cursor);
  const c = cursor.peek();
  if (c === '"') return parseStringScalar(cursor);
  if (c === '[') return parseListScalar(cursor);
  return parseAtomOrNumber(cursor);
}

function parseStringScalar(cursor) {
  if (cursor.peek() !== '"') throw new Error('parseStringScalar requires an opening quote');
  cursor.next();
  const body = [];
  while (true) {
    const c = cursor.peek();
    if (c === '') {
      throw new ParseError('L005_INVALID_STRING', 'Unterminated string', cursor.line, cursor.col);
    }
    if (c === '"') {
      cursor.next();
      break;
    }
    if (c === '\\') {
      body.push(c);
      cursor.next();
      const next = cursor.peek();
      if (next === '') {
        throw new ParseError('L005_INVALID_STRING', 'Trailing backslash', cursor.line, cursor.col);
      }
      body.push(next);
      cursor.next();
      if (next === 'u') {
        for (let j = 0; j < 4; j += 1) {
          const h = cursor.peek();
          if (h === '') {
            throw new ParseError('L005_INVALID_STRING', 'Bad \\u escape', cursor.line, cursor.col);
          }
          body.push(h);
          cursor.next();
        }
      }
    } else {
      body.push(c);
      cursor.next();
    }
  }
  const raw = body.join('');
  const value = parseStringLiteral(raw);
  return new Scalar('string', value, emitStringLiteral(value));
}

function parseListScalar(cursor) {
  if (cursor.peek() !== '[') throw new Error('parseListScalar requires [');
  cursor.next();
  const items = [];
  skipInlineWs(cursor);
  if (cursor.peek() === ']') {
    cursor.next();
    return new Scalar('list', items, '[]');
  }
  while (true) {
    const value = parseScalar(cursor, true);
    items.push(value);
    skipInlineWs(cursor);
    const c = cursor.peek();
    if (c === ',') {
      cursor.next();
      skipInlineWs(cursor);
    } else if (c === ']') {
      cursor.next();
      break;
    } else {
      throw new ParseError('L007_INVALID_LIST', `Expected , or ] got ${pythonRepr(c)}`, cursor.line, cursor.col);
    }
  }
  return new Scalar('list', items, `[${items.map((item) => item.lexeme).join(',')}]`);
}

function parseAtomOrNumber(cursor) {
  const start = cursor.i;
  while (true) {
    const c = cursor.peek();
    if (c === '' || ' \t\r\n,}]|'.includes(c)) break;
    cursor.next();
  }
  const raw = cursor.slice(start, cursor.i);
  if (raw === 'true') return new Scalar('boolean', true, 'true');
  if (raw === 'false') return new Scalar('boolean', false, 'false');
  if (raw === 'null') return new Scalar('null', null, 'null');
  if (INT_RE.test(raw)) {
    const value = raw === '-0' ? '0' : raw;
    return new Scalar('integer', value, value);
  }
  if (DEC_RE.test(raw)) return new Scalar('decimal', raw, raw);
  if (!ATOM_RE.test(raw)) {
    throw new ParseError('L010_INVALID_ATOM', `Invalid atom: ${pythonRepr(raw)}`, cursor.line, cursor.col);
  }
  return new Scalar('atom', raw, raw);
}

function parseAttrsPayload(source, startLine = 1) {
  const cursor = new StringCursor(source, startLine, 1);
  skipInlineWs(cursor);
  if (cursor.peek() !== '{') {
    throw new ParseError('S006_INVALID_ATTRS', 'Expected {', cursor.line, cursor.col);
  }
  cursor.next();
  const pairs = [];
  skipInlineWs(cursor);
  if (cursor.peek() === '}') {
    cursor.next();
    return pairs;
  }
  while (true) {
    skipInlineWs(cursor);
    const keyStart = cursor.i;
    while (cursor.peek() && !' \t:,'.includes(cursor.peek())) {
      if (cursor.peek() === '}') break;
      cursor.next();
    }
    const key = cursor.slice(keyStart, cursor.i);
    if (!key) throw new ParseError('L003_INVALID_KEY', 'Empty key', cursor.line, cursor.col);
    skipInlineWs(cursor);
    if (cursor.peek() !== ':') {
      throw new ParseError('S006_INVALID_ATTRS', 'Expected : after key', cursor.line, cursor.col);
    }
    cursor.next();
    const value = parseScalar(cursor);
    pairs.push([key, value]);
    skipInlineWs(cursor);
    const c = cursor.peek();
    if (c === ',') {
      cursor.next();
      skipInlineWs(cursor);
      if (cursor.peek() === '}') {
        cursor.next();
        break;
      }
    } else if (c === '}') {
      cursor.next();
      break;
    } else {
      throw new ParseError('S006_INVALID_ATTRS', `Expected , or } got ${pythonRepr(c)}`, cursor.line, cursor.col);
    }
  }
  return pairs;
}

module.exports = {
  Scalar,
  ParseError,
  StringCursor,
  ATOM_BODY_SOURCE,
  ATOM_RE,
  INT_RE,
  DEC_RE,
  _INT_RE: INT_RE,
  _DEC_RE: DEC_RE,
  toNfc,
  to_nfc: toNfc,
  utf8Bytes,
  pythonRepr,
  python_repr: pythonRepr,
  utf8_bytes: utf8Bytes,
  isAtomLexeme,
  is_atom_lexeme: isAtomLexeme,
  parseStringLiteral,
  parse_string_literal: parseStringLiteral,
  emitStringLiteral,
  emit_string_literal: emitStringLiteral,
  parseScalar,
  parse_scalar: parseScalar,
  skipInlineWs,
  skip_inline_ws: skipInlineWs,
  parseStringScalar,
  parse_string_scalar: parseStringScalar,
  parseListScalar,
  parse_list_scalar: parseListScalar,
  parseAtomOrNumber,
  parse_atom_or_number: parseAtomOrNumber,
  parseAttrsPayload,
  parse_attrs_payload: parseAttrsPayload,
};
