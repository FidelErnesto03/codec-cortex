#!/usr/bin/env python3
"""Non-normative CORTEX 0.1 corpus parser/validator.

This utility exists only to validate the Phase 2 corpus. The specification,
grammars and conformance vectors remain authoritative.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
import re
from pathlib import Path
from typing import Any, Iterable

SECTION_RE = re.compile(r'^\$(?P<id>0|[1-9][0-9]*)(?::[ \t]+(?P<title>.*?))?[ \t]*$')
SYMBOL_RE = re.compile(r'^(?:(?P<ns>[a-z][a-z0-9_.-]*)::)?(?P<sigil>!|[A-Z][A-Z0-9_]{0,15})$')
NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_.-]{0,63}$')
KEY_RE = re.compile(r'^[a-z_][a-z0-9_-]{0,63}$')
ATOM_RE = re.compile(r'^(?:\$[0-9]+:)?[A-Za-z_][A-Za-z0-9_./:@+%$-]*$')
INT_RE = re.compile(r'^-?(0|[1-9][0-9]*)$')
DEC_RE = re.compile(r'^-?(0|[1-9][0-9]*)\.[0-9]+$')
CONTRACT_PART_RE = re.compile(r'^(?P<name>[a-z_][a-z0-9_-]*)(?::(?P<type>%?[a-z_][a-z0-9_-]*))?(?P<optional>\?)?$')

SHAPES = {'attrs', 'attrs-pos', 'cuerpo', 'bloque', 'relacion'}
SCALAR_TYPES = {'any', 'text', 'atom', 'int', 'dec', 'bool', 'null', 'list'}
WEIGHTS = {'B', 'M', 'H'}

@dataclass
class Diagnostic:
    code: str
    severity: str
    line: int
    column: int
    message: str

    def as_dict(self) -> dict[str, Any]:
        return {
            'code': self.code,
            'severity': self.severity,
            'span': {'line': self.line, 'column': self.column},
            'message': self.message,
        }

class CortexError(Exception):
    def __init__(self, code: str, line: int, message: str, column: int = 1):
        super().__init__(message)
        self.diagnostic = Diagnostic(code, 'error', line, column, message)


def split_top_level(text: str, sep: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    in_string = False
    escape = False
    bracket = 0
    for ch in text:
        if in_string:
            buf.append(ch)
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            buf.append(ch)
        elif ch == '[':
            bracket += 1
            buf.append(ch)
        elif ch == ']':
            bracket -= 1
            if bracket < 0:
                raise ValueError('unbalanced list')
            buf.append(ch)
        elif ch == sep and bracket == 0:
            parts.append(''.join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if in_string or bracket != 0:
        raise ValueError('unclosed string or list')
    parts.append(''.join(buf).strip())
    return parts


def parse_string(token: str, line: int) -> dict[str, Any]:
    try:
        value = json.loads(token)
    except Exception as exc:
        raise CortexError('L005_INVALID_STRING', line, f'Cadena inválida: {exc}')
    if not isinstance(value, str):
        raise CortexError('L005_INVALID_STRING', line, 'El literal entre comillas debe ser string.')
    return {'node': 'StringValue', 'value': value, 'lexeme': token}


def parse_value(token: str, line: int, micros: dict[str, str] | None = None, *, positional: bool = False) -> dict[str, Any]:
    token = token.strip()
    if token == '':
        if positional:
            return {'node': 'StringValue', 'value': '', 'lexeme': ''}
        raise CortexError('L006_EMPTY_VALUE', line, 'Valor vacío no permitido.')
    if token.startswith('"'):
        if not token.endswith('"') or len(token) < 2:
            raise CortexError('L005_INVALID_STRING', line, 'Cadena sin cierre.')
        return parse_string(token, line)
    if token.startswith('['):
        if not token.endswith(']'):
            raise CortexError('L007_INVALID_LIST', line, 'Lista sin cierre.')
        inner = token[1:-1].strip()
        if inner == '':
            return {'node': 'ListValue', 'items': [], 'lexeme': token}
        try:
            raw_items = split_top_level(inner, ',')
        except ValueError as exc:
            raise CortexError('L007_INVALID_LIST', line, f'Lista inválida: {exc}')
        items = []
        for raw in raw_items:
            if raw.startswith('['):
                raise CortexError('L008_NESTED_LIST', line, 'Las listas anidadas no pertenecen a CORTEX 0.1.')
            items.append(parse_value(raw, line, micros, positional=False))
        return {'node': 'ListValue', 'items': items, 'lexeme': token}
    low = token.lower()
    if low == 'true':
        return {'node': 'BooleanValue', 'value': True, 'lexeme': token}
    if low == 'false':
        return {'node': 'BooleanValue', 'value': False, 'lexeme': token}
    if low == 'null':
        return {'node': 'NullValue', 'value': None, 'lexeme': token}
    if INT_RE.fullmatch(token):
        return {'node': 'IntegerValue', 'value': token, 'lexeme': token}
    if DEC_RE.fullmatch(token):
        try:
            Decimal(token)
        except InvalidOperation:
            raise CortexError('L009_INVALID_NUMBER', line, 'Decimal inválido.')
        return {'node': 'DecimalValue', 'value': token, 'lexeme': token}
    if positional and (' ' in token or '\t' in token):
        return {'node': 'StringValue', 'value': token, 'lexeme': token}
    if not ATOM_RE.fullmatch(token):
        raise CortexError('L010_INVALID_ATOM', line, f'Átomo inválido o texto sin comillas: {token!r}.')
    expanded = micros.get(token, token) if micros else token
    result: dict[str, Any] = {'node': 'AtomValue', 'value': expanded, 'lexeme': token}
    if expanded != token:
        result['micro'] = token
    return result


def scalar_plain(v: dict[str, Any]) -> Any:
    node = v['node']
    if node == 'ListValue':
        return [scalar_plain(i) for i in v['items']]
    return v.get('value')


def split_attrs(inner: str, line: int) -> list[tuple[str, str]]:
    if inner.strip() == '':
        return []
    try:
        chunks = split_top_level(inner, ',')
    except ValueError as exc:
        raise CortexError('S006_INVALID_ATTRS', line, f'Atributos inválidos: {exc}')
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for chunk in chunks:
        in_string = False
        escape = False
        bracket = 0
        idx = None
        for i, ch in enumerate(chunk):
            if in_string:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    in_string = False
            elif ch == '"':
                in_string = True
            elif ch == '[':
                bracket += 1
            elif ch == ']':
                bracket -= 1
            elif ch == ':' and bracket == 0:
                idx = i
                break
        if idx is None:
            raise CortexError('S006_INVALID_ATTRS', line, f'Par sin separador key:value: {chunk!r}.')
        key = chunk[:idx].strip()
        raw = chunk[idx + 1:].strip()
        if not KEY_RE.fullmatch(key):
            raise CortexError('L003_INVALID_KEY', line, f'Clave inválida: {key!r}.')
        if key in seen:
            raise CortexError('I006_DUPLICATE_FIELD', line, f'Campo duplicado: {key}.')
        seen.add(key)
        pairs.append((key, raw))
    return pairs


def parse_attrs(inner: str, line: int, micros: dict[str, str] | None = None) -> list[dict[str, Any]]:
    return [
        {'node': 'AttrPair', 'key': key, 'value': parse_value(raw, line, micros)}
        for key, raw in split_attrs(inner, line)
    ]


def parse_contract(text: str, line: int) -> list[dict[str, Any]]:
    parts = [p.strip() for p in text.split('|')]
    if not parts or any(not p for p in parts):
        raise CortexError('G008_INVALID_CONTRACT', line, 'Contrato vacío o con campo vacío.')
    fields = []
    seen = set()
    for part in parts:
        m = CONTRACT_PART_RE.fullmatch(part)
        if not m:
            raise CortexError('G008_INVALID_CONTRACT', line, f'Campo de contrato inválido: {part!r}.')
        name = m.group('name')
        typ = m.group('type') or 'any'
        optional = bool(m.group('optional'))
        if name in seen:
            raise CortexError('G009_DUPLICATE_CONTRACT_FIELD', line, f'Campo repetido en contrato: {name}.')
        seen.add(name)
        if not typ.startswith('%') and typ not in SCALAR_TYPES:
            raise CortexError('G027_UNKNOWN_FIELD_TYPE', line, f'Tipo de campo desconocido: {typ}.')
        fields.append({'name': name, 'type': typ, 'required': not optional})
    return fields


def parse_head_and_payload(line_text: str, line_no: int) -> tuple[str, str, str]:
    # Returns symbol, name, remaining payload text (including leading { or |)
    brace = line_text.find('{')
    pipe = line_text.find('|')
    candidates = [i for i in (brace, pipe) if i >= 0]
    if not candidates:
        raise CortexError('S004_MISSING_PAYLOAD', line_no, 'La línea de idea no contiene payload.')
    cut = min(candidates)
    head = line_text[:cut]
    payload = line_text[cut:]
    # Last colon separates symbol from name; namespace uses :: and section refs are not heads.
    positions = [i for i, ch in enumerate(head) if ch == ':' and not (i + 1 < len(head) and head[i + 1] == ':') and not (i > 0 and head[i - 1] == ':')]
    if not positions:
        raise CortexError('S003_INVALID_IDEA_HEAD', line_no, 'Falta separador SIGIL:nombre.')
    idx = positions[-1]
    symbol = head[:idx].strip()
    name = head[idx + 1:].strip()
    if not SYMBOL_RE.fullmatch(symbol):
        raise CortexError('L001_INVALID_SYMBOL', line_no, f'Sigilo inválido: {symbol!r}.')
    if not NAME_RE.fullmatch(name):
        raise CortexError('L002_INVALID_NAME', line_no, f'Nombre inválido: {name!r}.')
    return symbol, name, payload


def value_matches(v: dict[str, Any], typ: str, enums: dict[str, set[str]]) -> bool:
    if typ == 'any':
        return True
    node = v['node']
    if typ == 'text':
        return node == 'StringValue'
    if typ == 'atom':
        return node == 'AtomValue'
    if typ == 'int':
        return node == 'IntegerValue'
    if typ == 'dec':
        return node == 'DecimalValue'
    if typ == 'bool':
        return node == 'BooleanValue'
    if typ == 'null':
        return node == 'NullValue'
    if typ == 'list':
        return node == 'ListValue'
    if typ.startswith('%'):
        enum_name = typ[1:]
        return node == 'AtomValue' and v['value'] in enums.get(enum_name, set())
    return False


def attr_value(pairs: list[dict[str, Any]], key: str) -> dict[str, Any] | None:
    for pair in pairs:
        if pair['key'] == key:
            return pair['value']
    return None


def atom_or_string(v: dict[str, Any] | None) -> str | None:
    if not v:
        return None
    if v['node'] in {'AtomValue', 'StringValue', 'IntegerValue', 'DecimalValue'}:
        return str(v['value'])
    return None


def parse_document(text: str, *, supported_extensions: set[str] | None = None) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    supported_extensions = supported_extensions or set()
    diagnostics: list[Diagnostic] = []
    raw_lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    # Reject BOM and forbidden controls.
    if raw_lines and raw_lines[0].startswith('\ufeff'):
        diagnostics.append(Diagnostic('U001_BOM_FORBIDDEN', 'error', 1, 1, 'UTF-8 BOM no permitido.'))
        raw_lines[0] = raw_lines[0].lstrip('\ufeff')
    for i, ln in enumerate(raw_lines, 1):
        for j, ch in enumerate(ln, 1):
            if ord(ch) < 32 and ch not in {'\t'}:
                diagnostics.append(Diagnostic('U002_CONTROL_CHARACTER', 'error', i, j, 'Carácter de control no permitido.'))
    if diagnostics:
        return None, [d.as_dict() for d in diagnostics]

    lines = [(i, ln) for i, ln in enumerate(raw_lines, 1) if ln.strip() and not ln.lstrip().startswith('#')]
    if not lines:
        return None, [Diagnostic('S001_EMPTY_DOCUMENT', 'error', 1, 1, 'Documento vacío.').as_dict()]
    first_no, first = lines[0]
    m0 = SECTION_RE.fullmatch(first)
    if not m0 or int(m0.group('id')) != 0:
        return None, [Diagnostic('G001_GLOSSARY_MISSING_OR_NOT_FIRST', 'error', first_no, 1, '$0 debe ser la primera sección.').as_dict()]

    sections_raw: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    seen_sections: set[int] = set()
    idx = 0
    try:
        while idx < len(lines):
            line_no, line_text = lines[idx]
            sm = SECTION_RE.fullmatch(line_text)
            if sm:
                sid = int(sm.group('id'))
                if sid == 0 and sections_raw:
                    raise CortexError('G002_GLOSSARY_REOPENED', line_no, '$0 no puede reaparecer.')
                if sid in seen_sections:
                    raise CortexError('S002_DUPLICATE_SECTION', line_no, f'Sección duplicada: ${sid}.')
                seen_sections.add(sid)
                current = {'id': sid, 'title': (sm.group('title') or None), 'lines': []}
                sections_raw.append(current)
                idx += 1
                continue
            if current is None:
                raise CortexError('S005_CONTENT_OUTSIDE_SECTION', line_no, 'Contenido fuera de sección.')
            # Gather multiline braced payload if opening line ends with '{'.
            if line_text.rstrip().endswith('{') and not line_text.rstrip().endswith('{}'):
                # Could be malformed attrs spread over lines or body/block; gather until exact }.
                gathered = [line_text]
                j = idx + 1
                while j < len(lines) and lines[j][1].strip() != '}':
                    if SECTION_RE.fullmatch(lines[j][1]):
                        break
                    gathered.append(lines[j][1])
                    j += 1
                if j < len(lines) and lines[j][1].strip() == '}':
                    gathered.append(lines[j][1])
                    current['lines'].append((line_no, '\n'.join(gathered)))
                    idx = j + 1
                    continue
            current['lines'].append((line_no, line_text))
            idx += 1

        if sections_raw[0]['id'] != 0:
            raise CortexError('G001_GLOSSARY_MISSING_OR_NOT_FIRST', sections_raw[0]['lines'][0][0] if sections_raw[0]['lines'] else 1, '$0 debe ser la primera sección.')
        if any(s['id'] == 0 for s in sections_raw[1:]):
            raise CortexError('G002_GLOSSARY_REOPENED', 1, '$0 no puede reaparecer.')

        glossary_raw = sections_raw[0]
        meta_nodes = []
        symbols: dict[str, dict[str, Any]] = {}
        micros: dict[str, str] = {}
        enums: dict[str, set[str]] = {}
        enum_nodes = []
        micro_nodes = []
        namespace_nodes = []
        extension_nodes = []
        format_node = None

        # Re-parse glossary lines because $0 is not a normal symbol head.
        meta_nodes = []
        symbols = {}
        qualified_seen: set[str] = set()
        for line_no, line_text in glossary_raw['lines']:
            if '\n' in line_text:
                raise CortexError('G003_MULTILINE_GLOSSARY_DECLARATION', line_no, 'Las declaraciones de $0 deben ocupar una línea.')
            if line_text.startswith('$0:'):
                if '\n' in line_text:
                    raise CortexError('G003_MULTILINE_GLOSSARY_DECLARATION', line_no, 'Las declaraciones de $0 deben ocupar una línea.')
                brace = line_text.find('{')
                if brace < 0 or not line_text.endswith('}'):
                    raise CortexError('G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS', line_no, 'Meta-declaración inválida.')
                meta_name = line_text[3:brace].strip()
                if not NAME_RE.fullmatch(meta_name):
                    raise CortexError('L002_INVALID_NAME', line_no, f'Nombre meta inválido: {meta_name!r}.')
                pairs = parse_attrs(line_text[brace + 1:-1], line_no, micros)
                meta = {'node': 'MetaDeclaration', 'name': meta_name, 'attributes': pairs, 'sourceLine': line_no}
                meta_nodes.append(meta)
                if meta_name == 'format':
                    if format_node is not None:
                        raise CortexError('G006_DUPLICATE_FORMAT', line_no, '$0:format duplicado.')
                    version = atom_or_string(attr_value(pairs, 'cortex'))
                    encoding = atom_or_string(attr_value(pairs, 'encoding'))
                    if version != '0.1':
                        raise CortexError('G007_UNSUPPORTED_VERSION', line_no, 'cortex debe ser 0.1.')
                    if encoding not in {'UTF-8', 'utf-8'}:
                        raise CortexError('G011_ENCODING_REQUIRED', line_no, 'encoding debe ser UTF-8.')
                    format_node = {'node': 'FormatDeclaration', 'cortex': '0.1', 'encoding': 'UTF-8', 'attributes': pairs, 'sourceLine': line_no}
                elif meta_name.startswith('micro_'):
                    token = meta_name[len('micro_'):]
                    if not ATOM_RE.fullmatch(token):
                        raise CortexError('G012_INVALID_MICRO', line_no, f'Microtoken inválido: {token}.')
                    expand = atom_or_string(attr_value(pairs, 'expand'))
                    if not expand:
                        raise CortexError('G012_INVALID_MICRO', line_no, 'Microtoken sin expand.')
                    if token in micros:
                        raise CortexError('G013_DUPLICATE_MICRO', line_no, f'Microtoken duplicado: {token}.')
                    micros[token] = expand
                    micro_nodes.append({'node': 'MicroDeclaration', 'token': token, 'expand': expand, 'sourceLine': line_no})
                elif meta_name.startswith('enum_'):
                    enum_name = meta_name[len('enum_'):]
                    raw_values = atom_or_string(attr_value(pairs, 'values'))
                    if not raw_values:
                        raise CortexError('G014_INVALID_ENUM', line_no, 'Enum sin values.')
                    values = raw_values.split('|')
                    if any(not ATOM_RE.fullmatch(v) for v in values) or len(set(values)) != len(values):
                        raise CortexError('G014_INVALID_ENUM', line_no, 'Valores de enum inválidos o duplicados.')
                    if enum_name in enums:
                        raise CortexError('G015_DUPLICATE_ENUM', line_no, f'Enum duplicado: {enum_name}.')
                    enums[enum_name] = set(values)
                    enum_nodes.append({'node': 'EnumDeclaration', 'name': enum_name, 'values': values, 'sourceLine': line_no})
                elif meta_name.startswith('namespace_'):
                    ns_name = meta_name[len('namespace_'):]
                    ns_id = atom_or_string(attr_value(pairs, 'id')) or ns_name
                    version = atom_or_string(attr_value(pairs, 'version'))
                    namespace_nodes.append({'node': 'NamespaceDeclaration', 'alias': ns_name, 'id': ns_id, 'version': version, 'attributes': pairs, 'sourceLine': line_no})
                elif meta_name.startswith('extension_'):
                    ext_name = meta_name[len('extension_'):]
                    ns = atom_or_string(attr_value(pairs, 'namespace'))
                    ext_id = atom_or_string(attr_value(pairs, 'id'))
                    version = atom_or_string(attr_value(pairs, 'version'))
                    required_v = attr_value(pairs, 'required')
                    required = bool(required_v and required_v['node'] == 'BooleanValue' and required_v['value'])
                    if not ns or not ext_id or not version or required_v is None or required_v['node'] != 'BooleanValue':
                        raise CortexError('X001_INVALID_EXTENSION_DECLARATION', line_no, 'Extensión requiere namespace,id,version,required.')
                    ext_key = f'{ns}::{ext_id}@{version}'
                    extension_nodes.append({'node': 'ExtensionDeclaration', 'name': ext_name, 'namespace': ns, 'id': ext_id, 'version': version, 'required': required, 'attributes': pairs, 'sourceLine': line_no})
                    if required and ext_key not in supported_extensions:
                        diagnostics.append(Diagnostic('X002_REQUIRED_EXTENSION_UNSUPPORTED', 'error', line_no, 1, f'Extensión requerida no soportada: {ext_key}.'))
                continue

            symbol, label, payload = parse_head_and_payload(line_text, line_no)
            if not payload.startswith('{') or not payload.endswith('}'):
                raise CortexError('G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS', line_no, 'Declaración de sigilo inválida.')
            if symbol in symbols:
                raise CortexError('G005_DUPLICATE_SYMBOL', line_no, f'Sigilo duplicado: {symbol}.')
            pairs = parse_attrs(payload[1:-1], line_no, micros)
            shape = atom_or_string(attr_value(pairs, 'type'))
            weight = atom_or_string(attr_value(pairs, 'weight'))
            desc = atom_or_string(attr_value(pairs, 'desc'))
            focus = atom_or_string(attr_value(pairs, 'focus'))
            open_v = attr_value(pairs, 'open')
            open_contract = bool(open_v and open_v['node'] == 'BooleanValue' and open_v['value'])
            syntax_match = SYMBOL_RE.fullmatch(symbol)
            syntax_namespace = syntax_match.group('ns') if syntax_match else None
            namespace = atom_or_string(attr_value(pairs, 'namespace')) or syntax_namespace
            if shape is None:
                raise CortexError('G016_SYMBOL_TYPE_REQUIRED', line_no, f'{symbol} no declara type.')
            if shape not in SHAPES:
                raise CortexError('G017_UNKNOWN_SHAPE', line_no, f'Tipo de idea desconocido: {shape}.')
            if weight is None:
                raise CortexError('G018_SYMBOL_WEIGHT_REQUIRED', line_no, f'{symbol} no declara weight.')
            if weight not in WEIGHTS:
                raise CortexError('G019_INVALID_WEIGHT', line_no, f'Peso inválido: {weight}.')
            if not desc:
                raise CortexError('G020_SYMBOL_DESCRIPTION_REQUIRED', line_no, f'{symbol} no declara desc.')
            contract: list[dict[str, Any]] = []
            if shape == 'attrs':
                fields_v = attr_value(pairs, 'fields')
                fields_text = atom_or_string(fields_v)
                if not fields_text:
                    raise CortexError('G021_ATTRS_CONTRACT_REQUIRED', line_no, f'{symbol} attrs requiere fields.')
                contract = parse_contract(fields_text, line_no)
            elif shape in {'attrs-pos', 'relacion'}:
                pos_text = atom_or_string(attr_value(pairs, 'pos'))
                if not pos_text:
                    raise CortexError('G022_POSITIONAL_CONTRACT_REQUIRED', line_no, f'{symbol} requiere pos.')
                contract = parse_contract(pos_text, line_no)
                if shape == 'relacion' and len(contract) < 3:
                    raise CortexError('G023_RELATION_CONTRACT_TOO_SHORT', line_no, 'Una relación requiere al menos source|predicate|target.')
            if shape in {'attrs', 'attrs-pos', 'relacion'}:
                if not focus:
                    raise CortexError('G024_FOCUS_REQUIRED', line_no, f'{symbol} requiere focus.')
                if focus not in {f['name'] for f in contract}:
                    raise CortexError('G025_UNKNOWN_FOCUS_FIELD', line_no, f'focus {focus!r} no existe en el contrato.')
            else:
                focus = '$body'
            qualified = symbol if '::' in symbol else (f'{namespace}::{symbol}' if namespace else symbol)
            if qualified in qualified_seen:
                raise CortexError('G028_DUPLICATE_QUALIFIED_SYMBOL', line_no, f'Símbolo calificado duplicado: {qualified}.')
            qualified_seen.add(qualified)
            symbols[symbol] = {
                'node': 'SymbolDefinition',
                'surface': symbol,
                'namespace': namespace,
                'qualified': qualified,
                'label': label,
                'shape': shape,
                'weight': weight,
                'focus': focus,
                'description': desc,
                'open': open_contract,
                'contract': contract,
                'attributes': pairs,
                'sourceLine': line_no,
            }

        if format_node is None:
            raise CortexError('G010_FORMAT_REQUIRED', glossary_raw['lines'][0][0] if glossary_raw['lines'] else 1, '$0:format es obligatorio.')

        # Contract enum references must resolve after all meta declarations.
        for sym in symbols.values():
            for field in sym['contract']:
                typ = field['type']
                if typ.startswith('%') and typ[1:] not in enums:
                    raise CortexError('G026_UNKNOWN_ENUM_REFERENCE', sym['sourceLine'], f'Enum no declarado: {typ}.')

        section_nodes = []
        addresses: set[str] = set()
        for sec in sections_raw[1:]:
            sid = sec['id']
            if sid == 0:
                continue
            ideas = []
            for line_no, line_text in sec['lines']:
                symbol, name, payload_text = parse_head_and_payload(line_text.split('\n', 1)[0], line_no)
                definition = symbols.get(symbol)
                if definition is None:
                    raise CortexError('I001_UNDECLARED_SYMBOL', line_no, f'Sigilo no declarado en $0: {symbol}.')
                address = f'${sid}:{symbol}:{name}'
                if address in addresses:
                    raise CortexError('I002_DUPLICATE_IDEA_ADDRESS', line_no, f'Dirección local duplicada: {address}.')
                addresses.add(address)
                shape = definition['shape']
                contract = definition['contract']
                focus_name = definition['focus']
                payload: dict[str, Any]
                focus_value: dict[str, Any] | None = None
                if shape == 'attrs':
                    if '\n' in line_text:
                        raise CortexError('I003_ATTRS_MUST_BE_ONE_LINE', line_no, 'attrs debe ocupar una línea física.')
                    if not payload_text.startswith('{') or not payload_text.endswith('}'):
                        raise CortexError('I004_SHAPE_DELIMITER_MISMATCH', line_no, 'attrs requiere {...}.')
                    pairs = parse_attrs(payload_text[1:-1], line_no, micros)
                    pair_names = [p['key'] for p in pairs]
                    contract_names = [f['name'] for f in contract]
                    unknown = [k for k in pair_names if k not in contract_names]
                    if unknown and not definition['open']:
                        raise CortexError('I005_UNKNOWN_FIELD', line_no, f'Campo no declarado: {unknown[0]}.')
                    expected_known_order = [n for n in contract_names if n in pair_names]
                    actual_known_order = [n for n in pair_names if n in contract_names]
                    if actual_known_order != expected_known_order:
                        raise CortexError('I007_FIELD_ORDER', line_no, 'Los campos no siguen el contrato declarado.')
                    for field in contract:
                        if field['required'] and field['name'] not in pair_names:
                            raise CortexError('I008_REQUIRED_FIELD_MISSING', line_no, f'Falta campo requerido: {field["name"]}.')
                    for pair in pairs:
                        f = next((f for f in contract if f['name'] == pair['key']), None)
                        if f:
                            is_text_non_focus = (f['type'] == 'text' and f['name'] != focus_name)
                            if is_text_non_focus:
                                if pair['value']['node'] not in ('AtomValue', 'StringValue'):
                                    raise CortexError('I009_FIELD_TYPE_MISMATCH', line_no, f'Valor incompatible en {pair["key"]}: se esperaba atom o string.')
                            elif not value_matches(pair['value'], f['type'], enums):
                                code = 'I010_ENUM_VIOLATION' if f['type'].startswith('%') else 'I009_FIELD_TYPE_MISMATCH'
                                raise CortexError(code, line_no, f'Valor incompatible en {pair["key"]}: requiere {f["type"]}.')

                    focus_value = attr_value(pairs, focus_name)
                    payload = {'node': 'AttrsPayload', 'pairs': pairs}
                elif shape in {'attrs-pos', 'relacion'}:
                    if '\n' in line_text:
                        raise CortexError('I011_PIPE_IDEA_MUST_BE_ONE_LINE', line_no, f'{shape} debe ocupar una línea.')
                    if not payload_text.startswith('|'):
                        raise CortexError('I004_SHAPE_DELIMITER_MISMATCH', line_no, f'{shape} requiere separadores |.')
                    raw_cells = split_top_level(payload_text[1:], '|')
                    min_required = sum(1 for f in contract if f['required'])
                    if len(raw_cells) < min_required or len(raw_cells) > len(contract):
                        code = 'I013_RELATION_ARITY' if shape == 'relacion' else 'I012_POSITIONAL_ARITY'
                        raise CortexError(code, line_no, f'Aridad {len(raw_cells)} incompatible con contrato de {len(contract)} campos.')
                    cells = []
                    for field, raw in zip(contract, raw_cells):
                        if field['type'] == 'text' and not raw.strip().startswith('\"'):
                            value = {'node': 'StringValue', 'value': raw.strip(), 'lexeme': raw.strip()}
                        else:
                            value = parse_value(raw, line_no, micros, positional=True)
                        cells.append(value)
                    bound = []
                    for field, value in zip(contract, cells):
                        if not value_matches(value, field['type'], enums):
                            code = 'I010_ENUM_VIOLATION' if field['type'].startswith('%') else 'I009_FIELD_TYPE_MISMATCH'
                            raise CortexError(code, line_no, f'Valor incompatible en {field["name"]}: requiere {field["type"]}.')
                        bound.append({'field': field['name'], 'value': value})
                        if field['name'] == focus_name:
                            focus_value = value
                    payload = {'node': 'RelationPayload' if shape == 'relacion' else 'PositionalPayload', 'cells': cells, 'bound': bound}
                elif shape in {'cuerpo', 'bloque'}:
                    if payload_text.startswith('{') and payload_text.endswith('}') and '\n' not in line_text:
                        body = payload_text[1:-1]
                    else:
                        full_lines = line_text.split('\n')
                        if not full_lines[0].rstrip().endswith('{') or full_lines[-1].strip() != '}':
                            raise CortexError('I014_UNCLOSED_BODY', line_no, f'{shape} requiere cierre }} en línea propia.')
                        body = '\n'.join(full_lines[1:-1])
                    focus_value = {'node': 'StringValue', 'value': body, 'lexeme': body}
                    payload = {'node': 'BlockPayload' if shape == 'bloque' else 'TextPayload', 'text': body}
                else:
                    raise CortexError('G017_UNKNOWN_SHAPE', line_no, f'Shape desconocido: {shape}.')

                if focus_value is None:
                    raise CortexError('I015_FOCUS_VALUE_MISSING', line_no, f'La idea no materializa su foco {focus_name}.')
                if focus_value['node'] == 'StringValue' and focus_value.get('value') == '':
                    raise CortexError('I016_EMPTY_FOCUS', line_no, 'El foco ideático no puede estar vacío.')
                ideas.append({
                    'node': 'Idea',
                    'address': address,
                    'section': sid,
                    'symbol': symbol,
                    'qualifiedSymbol': definition['qualified'],
                    'name': name,
                    'function': {
                        'label': definition['label'],
                        'weight': definition['weight'],
                        'focus': focus_name,
                    },
                    'shape': shape,
                    'payload': payload,
                    'sourceLine': line_no,
                })
            section_nodes.append({'node': 'Section', 'id': sid, 'title': sec['title'], 'ideas': ideas})

        doc = {
            'node': 'Document',
            'cortexVersion': '0.1',
            'encoding': 'UTF-8',
            'glossary': {
                'node': 'Glossary',
                'format': format_node,
                'meta': meta_nodes,
                'enums': enum_nodes,
                'micros': micro_nodes,
                'namespaces': namespace_nodes,
                'extensions': extension_nodes,
                'symbols': list(symbols.values()),
            },
            'sections': section_nodes,
        }
        if diagnostics:
            return None, [d.as_dict() for d in diagnostics]
        return doc, []
    except CortexError as exc:
        diagnostics.append(exc.diagnostic)
        return None, [d.as_dict() for d in diagnostics]
    except ValueError as exc:
        diagnostics.append(Diagnostic('S999_INTERNAL_PARSE_FAILURE', 'error', 1, 1, str(exc)))
        return None, [d.as_dict() for d in diagnostics]


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=Path)
    parser.add_argument('--ast', action='store_true')
    args = parser.parse_args()
    doc, diagnostics = parse_document(args.file.read_text(encoding='utf-8'))
    if diagnostics:
        print(json.dumps(diagnostics, ensure_ascii=False, indent=2))
        return 1
    if args.ast:
        print(json.dumps(doc, ensure_ascii=False, indent=2))
    else:
        print('valid')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
