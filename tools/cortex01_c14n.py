#!/usr/bin/env python3
"""Internal non-normative oracle for CORTEX C14N-0.1 REAL.
Authority is the specification and corpus, not this code.
"""
from __future__ import annotations
import json,re,hashlib,unicodedata
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

# ---------- scalar and parsing utilities ----------
@dataclass
class Scalar:
    kind: str
    value: Any
    lexeme: str = ''

@dataclass
class ContractField:
    name: str
    type: str = 'any'
    optional: bool = False

@dataclass
class SymbolDef:
    symbol: str
    label: str
    attrs: dict[str, Scalar]
    shape: str
    contract: list[ContractField]
    focus: str | None
    namespace: str | None = None

@dataclass
class Idea:
    symbol: str
    name: str
    shape: str
    payload: Any
    contract: list[ContractField]
    focus: str | None

@dataclass
class Section:
    id: int
    title: str | None
    ideas: list[Idea] = field(default_factory=list)

@dataclass
class Doc:
    metas: list[tuple[str, dict[str, Scalar]]]
    symbols: list[SymbolDef]
    sections: list[Section]
    microtokens: dict[str, Scalar]

class CortexError(Exception): pass

def split_top(s: str, delim: str) -> list[str]:
    out=[]; buf=[]; quote=False; esc=False; depth=0
    for ch in s:
        if quote:
            buf.append(ch)
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch=='"': quote=False
            continue
        if ch=='"': quote=True; buf.append(ch); continue
        if ch in '[{(': depth+=1
        elif ch in ']})': depth-=1
        if ch==delim and depth==0:
            out.append(''.join(buf)); buf=[]
        else: buf.append(ch)
    out.append(''.join(buf))
    return out

def parse_string(s: str) -> str:
    try: return json.loads(s)
    except Exception as e: raise CortexError(f'invalid string {s!r}: {e}')

def parse_scalar(s: str) -> Scalar:
    s=s.strip()
    if not s: return Scalar('text','',s)
    if s.startswith('"'):
        if not s.endswith('"'): raise CortexError('unclosed string')
        return Scalar('string', parse_string(s), s)
    if s.startswith('['):
        if not s.endswith(']'): raise CortexError('unclosed list')
        inner=s[1:-1]
        if not inner.strip(): return Scalar('list', [], s)
        vals=[parse_scalar(x) for x in split_top(inner, ',')]
        if any(v.kind=='list' for v in vals): raise CortexError('nested lists forbidden')
        return Scalar('list', vals, s)
    if s=='true': return Scalar('bool', True, s)
    if s=='false': return Scalar('bool', False, s)
    if s=='null': return Scalar('null', None, s)
    if re.fullmatch(r'-?(0|[1-9][0-9]*)', s): return Scalar('int', s, s)
    if re.fullmatch(r'-?(0|[1-9][0-9]*)\.[0-9]+', s): return Scalar('dec', s, s)
    return Scalar('atom', s, s)

def parse_attrs(inner: str) -> dict[str, Scalar]:
    attrs={}
    if not inner.strip(): return attrs
    for part in split_top(inner, ','):
        kv=split_top(part, ':')
        if len(kv)<2: raise CortexError(f'invalid attr {part}')
        k=kv[0].strip(); v=':'.join(kv[1:])
        if not re.fullmatch(r'[a-z_][a-z0-9_-]*', k): raise CortexError(f'invalid key {k}')
        if k in attrs: raise CortexError(f'duplicate key {k}')
        attrs[k]=parse_scalar(v)
    return attrs

def parse_contract(text: str) -> list[ContractField]:
    if text=='': return []
    out=[]
    for cell in text.split('|'):
        optional=cell.endswith('?')
        if optional: cell=cell[:-1]
        if ':' in cell: name, typ=cell.split(':',1)
        else: name, typ=cell,'any'
        out.append(ContractField(name,typ,optional))
    return out

def nfc(s: str) -> str: return unicodedata.normalize('NFC', s)

def parse_doc(raw: bytes) -> Doc:
    if raw.startswith(b'\xef\xbb\xbf'): raise CortexError('BOM forbidden')
    try: text=raw.decode('utf-8')
    except UnicodeDecodeError as e: raise CortexError(str(e))
    text=text.replace('\r\n','\n').replace('\r','\n')
    lines=text.split('\n')
    metas=[]; symbols=[]; sections=[]; current=None; i=0
    symbol_map={}; microtokens={}
    seen_glossary=False
    while i < len(lines):
        rawline=lines[i]; line=rawline.strip(); i+=1
        if not line or line.startswith('#'): continue
        msec=re.fullmatch(r'\$(\d+)(?::[ \t]+(.*))?', line)
        if msec:
            sid=int(msec.group(1)); title=msec.group(2)
            if sid==0:
                if seen_glossary: raise CortexError('duplicate $0')
                if sections: raise CortexError('$0 must be first')
                seen_glossary=True; current=0
            else:
                if not seen_glossary: raise CortexError('$0 required')
                sec=Section(sid,title.strip() if title is not None else None,[])
                sections.append(sec); current=sec
            continue
        if current==0:
            mm=re.fullmatch(r'\$0:([A-Za-z_][A-Za-z0-9_.-]*)\{(.*)\}', line)
            if mm:
                name=mm.group(1); attrs=parse_attrs(mm.group(2)); metas.append((name,attrs))
                if name.startswith('micro_') and 'expand' in attrs:
                    microtokens[name[6:]]=attrs['expand']
                continue
            sm=re.fullmatch(r'((?:[a-z][a-z0-9_.-]*::)?(?:!|[A-Z][A-Z0-9_]{0,15})):([A-Za-z_][A-Za-z0-9_.-]*)\{(.*)\}', line)
            if sm:
                sym,label=sm.group(1),sm.group(2); attrs=parse_attrs(sm.group(3))
                shape=attrs.get('type',Scalar('atom','')).value
                namespace=attrs.get('namespace',Scalar('null',None)).value
                contract=[]
                if shape=='attrs': contract=parse_contract(str(attrs.get('fields',Scalar('string','')).value))
                elif shape in ('attrs-pos','relacion'): contract=parse_contract(str(attrs.get('pos',Scalar('string','')).value))
                focus=attrs.get('focus',Scalar('null',None)).value
                sd=SymbolDef(sym,label,attrs,shape,contract,focus,namespace)
                q=sym if '::' in sym else ((namespace+'::'+sym) if namespace else sym)
                symbol_map[sym]=sd; symbol_map[q]=sd
                symbols.append(sd); continue
            raise CortexError(f'invalid glossary line: {line}')
        if not isinstance(current, Section): raise CortexError('idea outside section')
        hm=re.match(r'^((?:[a-z][a-z0-9_.-]*::)?(?:!|[A-Z][A-Z0-9_]{0,15})):([A-Za-z_][A-Za-z0-9_.-]*)(.*)$', line)
        if not hm: raise CortexError(f'invalid idea head: {line}')
        sym,name,tail=hm.group(1),hm.group(2),hm.group(3)
        if sym not in symbol_map: raise CortexError(f'undeclared symbol {sym}')
        sd=symbol_map[sym]; shape=sd.shape
        if shape=='attrs':
            if not (tail.startswith('{') and tail.endswith('}')): raise CortexError('attrs delimiter mismatch')
            attrs=parse_attrs(tail[1:-1]); payload=coerce_attrs(attrs, sd.contract)
        elif shape in ('attrs-pos','relacion'):
            if not tail.startswith('|'): raise CortexError('pipe delimiter mismatch')
            cells=split_top(tail[1:],'|')
            payload=[parse_scalar_cell(c, sd.contract[idx].type if idx<len(sd.contract) else 'any') for idx,c in enumerate(cells)]
        elif shape in ('cuerpo','bloque'):
            if tail.startswith('{') and tail.endswith('}') and len(tail)>=2:
                payload=tail[1:-1]
            elif tail=='{':
                body=[]; closed=False
                while i<len(lines):
                    if lines[i].strip()=='}': closed=True; i+=1; break
                    body.append(lines[i]); i+=1
                if not closed: raise CortexError('body unclosed')
                payload='\n'.join(body)
            else: raise CortexError('body delimiter mismatch')
        else: raise CortexError(f'unknown shape {shape}')
        current.ideas.append(Idea(sym,name,shape,payload,sd.contract,sd.focus))
    if not seen_glossary: raise CortexError('$0 missing')
    if not metas or metas[0][0] != 'format':
        # parser accepts but structure validator rejects; for this phase hard reject
        raise CortexError('$0:format must be first')
    return Doc(metas,symbols,sections,microtokens)


def coerce_scalar_to_type(s: Scalar, typ: str) -> Scalar:
    """Project lexical scalars to the logical type declared by the local contract."""
    base = typ[:-1] if typ.endswith('?') else typ
    if base == 'text':
        return Scalar('string', str(s.value), s.lexeme)
    if base == 'integer':
        return Scalar('int', str(s.value), s.lexeme)
    if base == 'decimal':
        return Scalar('dec', str(s.value), s.lexeme)
    if base == 'boolean':
        if s.kind == 'bool': return s
        if str(s.value) == 'true': return Scalar('bool', True, s.lexeme)
        if str(s.value) == 'false': return Scalar('bool', False, s.lexeme)
    if base.startswith('%') or base == 'atom':
        return Scalar('atom', str(s.value), s.lexeme)
    return s

def coerce_attrs(attrs: dict[str, Scalar], contract: list[ContractField]) -> dict[str, Scalar]:
    by_name={f.name:f for f in contract}
    return {k:coerce_scalar_to_type(v, by_name[k].type) if k in by_name else v for k,v in attrs.items()}

def normalize_cuerpo(v: str) -> str:
    # The parser already removes delimiter newlines. Remaining blank lines are
    # semantic content and must survive canonicalization.
    return nfc(v.replace('\r\n','\n').replace('\r','\n'))

def normalize_bloque(v: str) -> str:
    # F3-CHARTER F3-E: bloque is verbatim for Unicode. The parser removes the
    # delimiter boundary; all remaining bytes are content except CRLF→LF.
    return v.replace('\r\n','\n').replace('\r','\n')

def scalar_has_nfc_change(s: Scalar) -> bool:
    if s.kind == 'list': return any(scalar_has_nfc_change(x) for x in s.value)
    if s.kind in ('string','atom'): return nfc(str(s.value)) != str(s.value)
    return False

def doc_has_nfc_change(doc: Doc) -> bool:
    for name,attrs in doc.metas:
        if nfc(name)!=name or any(scalar_has_nfc_change(v) for v in attrs.values()): return True
    for sd in doc.symbols:
        if any(scalar_has_nfc_change(v) for v in sd.attrs.values()): return True
    for sec in doc.sections:
        if sec.title is not None and nfc(sec.title)!=sec.title: return True
        for idea in sec.ideas:
            if idea.shape=='attrs' and any(scalar_has_nfc_change(v) for v in idea.payload.values()): return True
            if idea.shape in ('attrs-pos','relacion') and any(scalar_has_nfc_change(v) for v in idea.payload): return True
            if idea.shape=='cuerpo' and nfc(idea.payload)!=idea.payload: return True
            # bloque intentionally excluded
    return False

def parse_scalar_cell(s: str, typ: str) -> Scalar:
    raw=s
    s=s.strip()
    parsed=parse_scalar(s)
    return coerce_scalar_to_type(parsed, typ)

# ---------- canonicalization ----------
CONTROL_ESC={0x08:'\\b',0x0c:'\\f',0x0a:'\\n',0x0d:'\\r',0x09:'\\t'}
def emit_string(v: str) -> str:
    v=nfc(v); out=['"']
    for ch in v:
        cp=ord(ch)
        if ch=='"': out.append('\\"')
        elif ch=='\\': out.append('\\\\')
        elif cp in CONTROL_ESC: out.append(CONTROL_ESC[cp])
        elif cp<0x20 or cp==0x7f: out.append(f'\\u{cp:04X}')
        else: out.append(ch)
    out.append('"'); return ''.join(out)

def canon_int(s: str) -> str:
    i=int(s)
    return str(i)

def canon_dec(s: str) -> str:
    # F3-CHARTER F3-D: decimal precision is significant; preserve the exact
    # valid fixed-point lexeme from the logical AST.
    return s

def atom_safe(s: str) -> bool:
    return bool(re.fullmatch(r'[^\s\[\]{},"|]+', s))

def expand_micro(s: Scalar, micros: dict[str,Scalar]) -> Scalar:
    if s.kind=='atom' and s.value in micros:
        e=micros[s.value]
        return Scalar(e.kind,e.value,e.lexeme)
    if s.kind=='list': return Scalar('list',[expand_micro(v,micros) for v in s.value],s.lexeme)
    return s

def emit_scalar(s: Scalar, micros: dict[str,Scalar]|None=None) -> str:
    if micros is not None: s=expand_micro(s,micros)
    if s.kind=='string': return emit_string(str(s.value))
    if s.kind=='atom':
        val=nfc(str(s.value))
        if not atom_safe(val): return emit_string(val)
        return val
    if s.kind=='int': return canon_int(str(s.value))
    if s.kind=='dec': return canon_dec(str(s.value))
    if s.kind=='bool': return 'true' if s.value else 'false'
    if s.kind=='null': return 'null'
    if s.kind=='list': return '['+','.join(emit_scalar(v,micros) for v in s.value)+']'
    raise CortexError(f'unknown scalar {s.kind}')

META_ORDERS={
 'format':['cortex','encoding','language'],
 'enum':['values'],
 'micro':['expand'],
 'namespace':['id','version','required','desc'],
 'extension':['namespace','id','version','required','desc'],
}
SYMBOL_ORDER=['type','weight','fields','pos','focus','desc','open','namespace','version']

def ordered_keys(attrs: dict[str,Scalar], base: list[str]) -> list[str]:
    return [k for k in base if k in attrs] + sorted([k for k in attrs if k not in base], key=lambda x:nfc(x).encode('utf-8'))

def emit_attrs(attrs: dict[str,Scalar], keys: list[str], micros=None) -> str:
    return '{'+','.join(f'{k}:{emit_scalar(attrs[k],micros)}' for k in keys)+'}'


def emit_idea_attrs(idea: Idea, keys: list[str], micros: dict[str,Scalar]) -> str:
    contract={f.name:f for f in idea.contract}
    parts=[]
    for k in keys:
        val=expand_micro(idea.payload[k], micros)
        typ=contract[k].type if k in contract else 'any'
        if typ=='text':
            text=nfc(str(val.value))
            # Charter invariant I7: focus is quoted. Non-focus text remains bare
            # whenever the grammar can represent it without ambiguity.
            rendered=emit_string(text) if (k==idea.focus or not atom_safe(text)) else text
        else:
            rendered=emit_scalar(val)
        parts.append(f'{k}:{rendered}')
    return '{'+','.join(parts)+'}'

def meta_category(name: str):
    if name=='format': return (0,'')
    for idx,prefix in enumerate(['enum_','micro_','namespace_','extension_'], start=1):
        if name.startswith(prefix): return (idx,name[len(prefix):])
    return (5,name)

def canonicalize(raw: bytes) -> tuple[bytes,dict]:
    doc=parse_doc(raw)
    changes=[]
    raw_text=raw.decode('utf-8')
    if '\r' in raw_text: changes.append('newline-normalized')
    if any(l.strip().startswith('#') for l in raw_text.replace('\r\n','\n').replace('\r','\n').split('\n')): changes.append('comments-removed')
    if any(not l.strip() for l in raw_text.replace('\r\n','\n').replace('\r','\n').split('\n')[:-1]): changes.append('blank-lines-removed')
    if doc_has_nfc_change(doc): changes.append('unicode-normalized')

    lines=['$0']
    metas=sorted(doc.metas, key=lambda kv:(meta_category(kv[0]), nfc(kv[0]).encode('utf-8')))
    if [m[0] for m in metas] != [m[0] for m in doc.metas]: changes.append('glossary-order-normalized')
    for name,attrs in metas:
        cat='format' if name=='format' else ('enum' if name.startswith('enum_') else 'micro' if name.startswith('micro_') else 'namespace' if name.startswith('namespace_') else 'extension' if name.startswith('extension_') else 'other')
        base=META_ORDERS.get(cat,[]); keys=ordered_keys(attrs,base)
        if keys!=list(attrs.keys()): changes.append('attribute-order-normalized')
        lines.append(f'$0:{name}'+emit_attrs(attrs,keys))
    syms=sorted(doc.symbols,key=lambda sd:nfc(sd.symbol if '::' in sd.symbol else ((sd.namespace+'::'+sd.symbol) if sd.namespace else sd.symbol)).encode('utf-8'))
    if [s.symbol for s in syms] != [s.symbol for s in doc.symbols]: changes.append('glossary-order-normalized')
    for sd in syms:
        keys=ordered_keys(sd.attrs,SYMBOL_ORDER)
        if keys!=list(sd.attrs.keys()): changes.append('attribute-order-normalized')
        lines.append(f'{sd.symbol}:{sd.label}'+emit_attrs(sd.attrs,keys))
    for sec in doc.sections:
        lines.append(f'${sec.id}' + (f': {nfc(sec.title)}' if sec.title is not None else ''))
        for idea in sec.ideas:
            head=f'{idea.symbol}:{idea.name}'
            if idea.shape=='attrs':
                contract_names=[f.name for f in idea.contract]
                extras=sorted([k for k in idea.payload if k not in contract_names], key=lambda x:nfc(x).encode('utf-8'))
                keys=[k for k in contract_names if k in idea.payload]+extras
                if keys!=list(idea.payload.keys()): changes.append('attribute-order-normalized')
                # micro expansions
                for k in keys:
                    if idea.payload[k].kind=='atom' and idea.payload[k].value in doc.microtokens: changes.append('microtoken-expanded')
                lines.append(head+emit_idea_attrs(idea,keys,doc.microtokens))
            elif idea.shape in ('attrs-pos','relacion'):
                cells=[]
                for idx,s in enumerate(idea.payload):
                    typ=idea.contract[idx].type if idx<len(idea.contract) else 'any'
                    ex=expand_micro(s,doc.microtokens)
                    if s.kind=='atom' and s.value in doc.microtokens: changes.append('microtoken-expanded')
                    if typ=='text':
                        val=nfc(str(ex.value))
                        if val and '|' not in val and '\n' not in val and val==val.strip(' \t') and not val.startswith('"'):
                            cells.append(val)
                        else: cells.append(emit_string(val))
                    else: cells.append(emit_scalar(ex))
                lines.append(head+'|'+'|'.join(cells))
            elif idea.shape=='cuerpo':
                val=normalize_cuerpo(idea.payload)
                if '\n' not in val:
                    lines.append(head+'{'+val+'}')
                else:
                    lines.append(head+'{'); lines.extend(val.split('\n')); lines.append('}')
            elif idea.shape=='bloque':
                val=normalize_bloque(idea.payload)
                lines.append(head+'{'); lines.extend(val.split('\n')); lines.append('}')
    out=('\n'.join(lines)+'\n').encode('utf-8')
    if out!=raw:
        changes.append('source-form-normalized')
    # stable unique order
    changes=list(dict.fromkeys(changes))
    raw_sha=hashlib.sha256(raw).hexdigest(); can_sha=hashlib.sha256(out).hexdigest()
    chash=hashlib.sha256(b'CORTEX-C14N-0.1\x00'+out).hexdigest()
    report={
      'canonicalization':'C14N-0.1','inputSha256':raw_sha,'canonicalSha256':can_sha,
      'canonicalHash':f'sha256:{chash}','changed':out!=raw,
      'structuralLoss':False,'losses':[],'sourceFidelityChanges':changes,
      'diagnostics':[]
    }
    return out, report

