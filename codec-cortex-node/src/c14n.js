'use strict';

/** C14N-0.1 canonicalizer. */

const {
  Scalar,
  emitStringLiteral,
  toNfc,
  utf8Bytes,
  ATOM_RE,
} = require('./scalars');

const FORMAT_KEY_ORDER = ['cortex', 'encoding', 'language'];
const SIGIL_KEY_ORDER = ['type', 'weight', 'fields', 'pos', 'focus', 'desc', 'open', 'namespace', 'version'];
const ENUM_KEY_ORDER = ['values'];
const MICRO_KEY_ORDER = ['expand'];
const NS_KEY_ORDER = ['id', 'uri', 'version', 'required', 'desc'];
const EXT_KEY_ORDER = ['namespace', 'id', 'version', 'required', 'desc'];

function pairsFromAttrs(attrs) {
  if (Array.isArray(attrs)) return [...attrs];
  if (attrs instanceof Map) return [...attrs.entries()];
  return Object.entries(attrs || {});
}

function compareUtf8(left, right) {
  return Buffer.compare(utf8Bytes(toNfc(left)), utf8Bytes(toNfc(right)));
}

function sortKeysCanonical(attrs, order) {
  const items = pairsFromAttrs(attrs);
  const byKey = new Map();
  for (const [key, value] of items) byKey.set(key, value);
  const out = [];
  const used = new Set();
  for (const key of order) {
    if (byKey.has(key)) {
      out.push([key, byKey.get(key)]);
      used.add(key);
    }
  }
  const extras = items.filter(([key]) => !used.has(key));
  extras.sort((a, b) => compareUtf8(a[0], b[0]));
  out.push(...extras);
  return out;
}

function nfcScalar(scalar) {
  if (scalar.kind === 'string') {
    const value = toNfc(scalar.value);
    return new Scalar('string', value, emitStringLiteral(value));
  }
  if (scalar.kind === 'atom') {
    const value = toNfc(scalar.value);
    return new Scalar('atom', value, value);
  }
  if (scalar.kind === 'list') {
    const items = scalar.value.map(nfcScalar);
    return new Scalar('list', items, `[${items.map((item) => item.lexeme).join(',')}]`);
  }
  return scalar;
}

function expandMicrotokens(doc) {
  if (!doc.glossary.micros.length) return;
  const microMap = new Map(doc.glossary.micros.map((micro) => [micro.token, micro.expand]));
  for (const section of doc.sections) {
    for (const idea of section.ideas) {
      if (idea.shape === 'attrs') {
        const pairs = idea.payload[1].map(([key, value]) => {
          if (value.kind === 'atom' && microMap.has(value.value)) {
            const expanded = microMap.get(value.value);
            return [key, new Scalar('atom', expanded, expanded)];
          }
          return [key, value];
        });
        idea.payload = ['attrs', pairs];
      } else if (idea.shape === 'attrs-pos' || idea.shape === 'relacion') {
        const cells = idea.payload[1].map((cell) => {
          if (cell.kind === 'atom' && microMap.has(cell.value)) {
            const expanded = microMap.get(cell.value);
            return new Scalar('atom', expanded, expanded);
          }
          return cell;
        });
        idea.payload = [idea.shape, cells];
      }
    }
  }
}

function isAtomSafeBare(value) {
  const s = String(value);
  if (!s) return false;
  return !/[\s\[\]{},"|]/u.test(s);
}

function isTextSafeBare(value) {
  const s = String(value);
  if (!s || s.includes('\n') || s.includes('\r') || s.includes('|')) return false;
  if (s !== s.trim() || s.startsWith('"')) return false;
  return true;
}

function emitScalarAttrs(value, isFocusText, isTextField) {
  if (value.kind === 'string') {
    if (isFocusText) return value.lexeme;
    if (isTextField) {
      if (isAtomSafeBare(value.value) && ATOM_RE.test(value.value)) return value.value;
      return value.lexeme;
    }
    return value.lexeme;
  }
  if (value.kind === 'atom') {
    if (isAtomSafeBare(value.value)) return value.value;
    return emitStringLiteral(value.value);
  }
  return value.lexeme;
}

function emitScalarPositional(value, isTextField) {
  if (value.kind === 'string') {
    if (isTextField) {
      if (isTextSafeBare(value.value)) return value.value;
      return value.lexeme;
    }
    return value.lexeme;
  }
  if (value.kind === 'atom') {
    if (isAtomSafeBare(value.value)) return value.value;
    return emitStringLiteral(value.value);
  }
  return value.lexeme;
}

function emitGlossaryAttrs(attrs) {
  return `{${attrs.map(([key, value]) => `${key}:${value.lexeme}`).join(',')}}`;
}

function emitMetaAttrs(attrs) {
  return emitGlossaryAttrs(attrs);
}

function formatCanonical(formatDecl) {
  return `$0:format${emitGlossaryAttrs(sortKeysCanonical(formatDecl.attrs, FORMAT_KEY_ORDER))}`;
}

function enumCanonical(enumDecl, attrsLookup) {
  return `$0:enum_${enumDecl.name}${emitGlossaryAttrs(sortKeysCanonical(attrsLookup, ENUM_KEY_ORDER))}`;
}

function microCanonical(micro, attrsLookup) {
  return `$0:micro_${micro.token}${emitGlossaryAttrs(sortKeysCanonical(attrsLookup, MICRO_KEY_ORDER))}`;
}

function namespaceCanonical(namespace, attrsLookup) {
  return `$0:namespace_${namespace.alias}${emitGlossaryAttrs(sortKeysCanonical(attrsLookup, NS_KEY_ORDER))}`;
}

function extensionCanonical(extension, attrsLookup) {
  return `$0:extension_${extension.name}${emitGlossaryAttrs(sortKeysCanonical(attrsLookup, EXT_KEY_ORDER))}`;
}

function symbolCanonical(symbol) {
  const qualified = symbol.namespace ? `${symbol.namespace}::${symbol.sigil}` : symbol.sigil;
  return `${qualified}:${symbol.label}${emitGlossaryAttrs(sortKeysCanonical(symbol.attrs, SIGIL_KEY_ORDER))}`;
}

function metaCanonical(meta) {
  const attrs = [...meta.attrs].sort((a, b) => compareUtf8(a[0], b[0]));
  return `$0:${meta.name}${emitMetaAttrs(attrs)}`;
}

function ideaCanonical(idea, symbol) {
  const qualified = idea.namespace ? `${idea.namespace}::${idea.symbol}` : idea.symbol;
  const head = `${qualified}:${idea.name}`;
  if (idea.shape === 'attrs') {
    const pairs = idea.payload[1];
    const fieldOrder = symbol.contract.map((field) => field.name);
    const pairMap = new Map();
    for (const [key, value] of pairs) pairMap.set(key, value);
    const outPairs = [];
    const used = new Set();
    for (const fieldName of fieldOrder) {
      if (pairMap.has(fieldName)) {
        outPairs.push([fieldName, pairMap.get(fieldName)]);
        used.add(fieldName);
      }
    }
    if (symbol.open) {
      const extras = pairs.filter(([key]) => !used.has(key));
      extras.sort((a, b) => compareUtf8(a[0], b[0]));
      outPairs.push(...extras);
    }
    const fieldTypes = new Map(symbol.contract.map((field) => [field.name, field.type]));
    const parts = outPairs.map(([key, value]) => {
      const fieldType = fieldTypes.get(key) || 'any';
      const isText = fieldType === 'text';
      const isFocusText = key === symbol.focus && isText;
      return `${key}:${emitScalarAttrs(value, isFocusText, isText)}`;
    });
    return `${head}{${parts.join(',')}}`;
  }
  if (idea.shape === 'attrs-pos' || idea.shape === 'relacion') {
    const cells = idea.payload[1];
    const fieldTypes = symbol.contract.map((field) => field.type);
    const parts = cells.map((cell, index) => emitScalarPositional(cell, (fieldTypes[index] || 'any') === 'text'));
    return `${head}|${parts.join('|')}`;
  }
  if (idea.shape === 'cuerpo') {
    const text = toNfc(idea.payload[1]);
    return text.includes('\n') ? `${head}{\n${text}\n}` : `${head}{${text}}`;
  }
  if (idea.shape === 'bloque') {
    return `${head}{\n${idea.payload[1]}\n}`;
  }
  return head;
}

function canonicalize(doc) {
  if (doc.glossary.format) {
    doc.glossary.format.attrs = doc.glossary.format.attrs.map(([key, value]) => [key, nfcScalar(value)]);
  }
  for (const enumDecl of doc.glossary.enums) enumDecl.values = enumDecl.values.map(toNfc);
  for (const micro of doc.glossary.micros) micro.expand = toNfc(micro.expand);
  for (const namespace of doc.glossary.namespaces) namespace.attrs = namespace.attrs.map(([key, value]) => [key, nfcScalar(value)]);
  for (const extension of doc.glossary.extensions) extension.attrs = extension.attrs.map(([key, value]) => [key, nfcScalar(value)]);
  for (const meta of doc.glossary.meta) meta.attrs = meta.attrs.map(([key, value]) => [key, nfcScalar(value)]);
  for (const symbol of doc.glossary.symbols) {
    symbol.attrs = symbol.attrs.map(([key, value]) => [key, nfcScalar(value)]);
    symbol.desc = toNfc(symbol.desc);
  }
  for (const section of doc.sections) {
    for (const idea of section.ideas) {
      if (idea.shape === 'attrs') {
        idea.payload = ['attrs', idea.payload[1].map(([key, value]) => [key, nfcScalar(value)])];
      } else if (idea.shape === 'attrs-pos' || idea.shape === 'relacion') {
        idea.payload = [idea.shape, idea.payload[1].map(nfcScalar)];
      } else if (idea.shape === 'cuerpo') {
        idea.payload = ['cuerpo', toNfc(idea.payload[1])];
      }
    }
    if (section.title !== null && section.title !== undefined) section.title = toNfc(section.title);
  }

  expandMicrotokens(doc);

  const lines = ['$0'];
  lines.push(formatCanonical(doc.glossary.format));

  const enums = [...doc.glossary.enums].sort((a, b) => compareUtf8(a.name, b.name));
  for (const enumDecl of enums) {
    const joined = enumDecl.values.join('|');
    lines.push(enumCanonical(enumDecl, { values: new Scalar('string', joined, emitStringLiteral(joined)) }));
  }

  const micros = [...doc.glossary.micros].sort((a, b) => compareUtf8(a.token, b.token));
  for (const micro of micros) {
    const scalar = ATOM_RE.test(micro.expand)
      ? new Scalar('atom', micro.expand, micro.expand)
      : new Scalar('string', micro.expand, emitStringLiteral(micro.expand));
    lines.push(microCanonical(micro, { expand: scalar }));
  }

  const namespaces = [...doc.glossary.namespaces].sort((a, b) => compareUtf8(a.alias, b.alias));
  for (const namespace of namespaces) lines.push(namespaceCanonical(namespace, new Map(namespace.attrs)));

  const extensions = [...doc.glossary.extensions].sort((a, b) => compareUtf8(a.name, b.name));
  for (const extension of extensions) lines.push(extensionCanonical(extension, new Map(extension.attrs)));

  const metas = [...doc.glossary.meta].sort((a, b) => compareUtf8(a.name, b.name));
  for (const meta of metas) lines.push(metaCanonical(meta));

  const symbols = [...doc.glossary.symbols].sort((a, b) => {
    const namespaceCompare = compareUtf8(a.namespace || '', b.namespace || '');
    if (namespaceCompare !== 0) return namespaceCompare;
    const sigilCompare = compareUtf8(a.sigil, b.sigil);
    if (sigilCompare !== 0) return sigilCompare;
    return compareUtf8(a.label, b.label);
  });
  for (const symbol of symbols) lines.push(symbolCanonical(symbol));

  const symbolLookup = new Map();
  for (const symbol of doc.glossary.symbols) symbolLookup.set(`${symbol.namespace ?? ''}\u0000${symbol.sigil}`, symbol);
  for (const section of doc.sections) {
    if (section.title === null || section.title === undefined) lines.push(`$${section.id}`);
    else lines.push(`$${section.id}: ${section.title.trim()}`);
    for (const idea of section.ideas) {
      let symbol = symbolLookup.get(`${idea.namespace ?? ''}\u0000${idea.symbol}`);
      if (!symbol) symbol = symbolLookup.get(`\u0000${idea.symbol}`);
      lines.push(ideaCanonical(idea, symbol));
    }
  }

  return `${lines.join('\n')}\n`;
}

module.exports = {
  FORMAT_KEY_ORDER,
  SIGIL_KEY_ORDER,
  ENUM_KEY_ORDER,
  MICRO_KEY_ORDER,
  NS_KEY_ORDER,
  EXT_KEY_ORDER,
  sortKeysCanonical,
  _sort_keys_canonical: sortKeysCanonical,
  nfcScalar,
  _nfc_scalar: nfcScalar,
  expandMicrotokens,
  _expand_microtokens: expandMicrotokens,
  isAtomSafeBare,
  _is_atom_safe_bare: isAtomSafeBare,
  isTextSafeBare,
  _is_text_safe_bare: isTextSafeBare,
  emitScalarAttrs,
  _emit_scalar_attrs: emitScalarAttrs,
  emitScalarPositional,
  _emit_scalar_positional: emitScalarPositional,
  canonicalize,
};
