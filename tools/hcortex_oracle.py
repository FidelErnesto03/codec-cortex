"""Auditor interno no normativo para HCORTEX Draft 0.1.

La especificación y el corpus son la autoridad; este módulo no lo es.
"""
from __future__ import annotations
import json, os, re, hashlib, copy, textwrap
from pathlib import Path
from typing import Any


# ---------- scalar helpers ----------
def S(value:str): return {"kind":"string","value":value}
def A(value:str): return {"kind":"atom","value":value}
def I(value:int|str): return {"kind":"integer","value":str(value)}
def D(value:str): return {"kind":"decimal","value":value}
def B(value:bool): return {"kind":"boolean","value":value}
def N(): return {"kind":"null","value":None}
def L(*items): return {"kind":"list","items":list(items)}

def contract(fields):
    return [{"name":n,"type":t,"optional":o} for n,t,o in fields]

def symbol(symbol,label,shape,weight='B',focus=None,fields=None,pos=None,desc=None,namespace=None,open_=False):
    return {
        "symbol":symbol,"namespace":namespace,"label":label,"shape":shape,"weight":weight,
        "focus":focus,"fields":fields or [],"pos":pos or [],"desc":desc or label,"open":open_
    }

def idea(symbol,name,value,shape=None,namespace=None):
    return {"symbol":symbol,"namespace":namespace,"name":name,"shape":shape,"value":value}

def section(id_, ideas, title=None):
    return {"id":str(id_),"title":title,"ideas":ideas}

def document(symbols, sections, *, enums=None, micros=None, namespaces=None, extensions=None, language='es', format_extra=None):
    fmt={"cortex":"0.1","encoding":"UTF-8","language":language}
    if format_extra: fmt.update(format_extra)
    return {
        "node":"Document","cortexVersion":"0.1","encoding":"UTF-8","format":fmt,
        "enums":enums or [],"microtokens":micros or [],"namespaces":namespaces or [],
        "extensions":extensions or [],"symbols":symbols,"sections":sections
    }

def qsymbol(obj):
    return f"{obj['namespace']}::{obj['symbol']}" if obj.get('namespace') else obj['symbol']

def contract_text(sym):
    arr = sym['fields'] if sym['shape']=='attrs' else sym['pos']
    return '|'.join(f"{f['name']}:{f['type']}{'?' if f['optional'] else ''}" for f in arr)

def json_string(v:str)->str:
    return json.dumps(v, ensure_ascii=False, separators=(',',':'))

def scalar_cortex(v:dict, *, focus=False, positional=False)->str:
    k=v['kind']
    if k=='string':
        x=v['value']
        if positional and '|' not in x and '\n' not in x and not x.startswith(' ') and not x.endswith(' '):
            return x
        if (not focus) and (not positional) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_./:@+%$-]*', x):
            return x
        return json_string(x)
    if k in ('atom','integer','decimal'): return v['value']
    if k=='boolean': return 'true' if v['value'] else 'false'
    if k=='null': return 'null'
    if k=='list': return '['+','.join(scalar_cortex(x) for x in v['items'])+']'
    raise ValueError(k)

def parse_scalar_lexeme(s:str, declared_type:str='any')->dict:
    s=s.strip()
    if s.startswith('"'):
        try: return S(json.loads(s))
        except Exception as e: raise ValueError('invalid string') from e
    if s.startswith('[') and s.endswith(']'):
        inner=s[1:-1]
        if not inner: return L()
        parts=split_top(inner, ',')
        return L(*(parse_scalar_lexeme(p) for p in parts))
    if s=='true': return B(True)
    if s=='false': return B(False)
    if s=='null': return N()
    if re.fullmatch(r'-?(0|[1-9][0-9]*)',s): return I(s)
    if re.fullmatch(r'-?(0|[1-9][0-9]*)\.[0-9]+',s): return D(s)
    if declared_type=='text': return S(s)
    return A(s)

def split_top(s:str, sep:str)->list[str]:
    out=[]; cur=[]; depth=0; in_str=False; esc=False
    for ch in s:
        if in_str:
            cur.append(ch)
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch=='"': in_str=False
        else:
            if ch=='"': in_str=True; cur.append(ch)
            elif ch in '[{(': depth+=1; cur.append(ch)
            elif ch in ']})': depth-=1; cur.append(ch)
            elif ch==sep and depth==0: out.append(''.join(cur).strip()); cur=[]
            else: cur.append(ch)
    out.append(''.join(cur).strip())
    return out

def render_cortex(doc:dict)->str:
    lines=['$0']
    fmt=doc['format']
    keys=['cortex','encoding','language']+[k for k in fmt if k not in ('cortex','encoding','language')]
    def render_format_value(k, v):
        if not isinstance(v, str):
            return scalar_cortex(v)
        if k in ('cortex','encoding','language') and re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_./:@+%$-]*', v):
            return v
        return scalar_cortex(S(v))
    lines.append('$0:format{'+','.join(f"{k}:{render_format_value(k, fmt[k])}" for k in keys)+'}')
    for e in sorted(doc['enums'], key=lambda x:x['name']):
        lines.append(f"$0:enum_{e['name']}{{values:{json_string('|'.join(e['values']))}}}")
    for m in sorted(doc['microtokens'], key=lambda x:x['token']):
        lines.append(f"$0:micro_{m['token']}{{expand:{m['expand']}}}")
    for n in sorted(doc['namespaces'], key=lambda x:x['name']):
        attrs=[f"uri:{json_string(n['uri'])}"]
        if n.get('version') is not None: attrs.append(f"version:{json_string(n['version'])}")
        lines.append(f"$0:namespace_{n['name']}{{{','.join(attrs)}}}")
    for x in sorted(doc['extensions'], key=lambda x:(x['namespace'],x['id'],x['version'])):
        attrs=[f"namespace:{x['namespace']}",f"id:{x['id']}",f"version:{x['version']}",f"required:{'true' if x['required'] else 'false'}"]
        if x.get('config'):
            attrs.append('config:'+json_string(json.dumps(x['config'],ensure_ascii=False,separators=(',',':'),sort_keys=True)))
        lines.append(f"$0:extension_{x['id']}{{{','.join(attrs)}}}")
    for sym in sorted(doc['symbols'], key=lambda x:qsymbol(x)):
        attrs=[f"type:{sym['shape']}",f"weight:{sym['weight']}"]
        if sym['shape']=='attrs': attrs.append(f"fields:{json_string(contract_text(sym))}")
        elif sym['shape'] in ('attrs-pos','relacion'): attrs.append(f"pos:{json_string(contract_text(sym))}")
        if sym.get('focus') is not None: attrs.append(f"focus:{sym['focus']}")
        if sym.get('open'): attrs.append('open:true')
        attrs.append(f"desc:{json_string(sym['desc'])}")
        lines.append(f"{qsymbol(sym)}:{sym['label']}{{{','.join(attrs)}}}")
    symmap={qsymbol(s):s for s in doc['symbols']}
    for sec in doc['sections']:
        lines.append(f"${sec['id']}" + (f": {sec['title']}" if sec.get('title') else ''))
        for ent in sec['ideas']:
            q=qsymbol(ent); sym=symmap[q]; shape=ent.get('shape') or sym['shape']; head=f"{q}:{ent['name']}"
            if shape=='attrs':
                vals={k:v for k,v in ent['value']}
                ordered=[]
                for f in sym['fields']:
                    if f['name'] in vals:
                        ordered.append((f['name'], vals.pop(f['name']), f))
                for k in sorted(vals): ordered.append((k,vals[k],{"name":k,"type":"any","optional":True}))
                body=','.join(f"{k}:{scalar_cortex(v, focus=(k==sym.get('focus')))}" for k,v,_ in ordered)
                lines.append(head+'{'+body+'}')
            elif shape in ('attrs-pos','relacion'):
                vals=ent['value']
                lines.append(head+'|'+'|'.join(scalar_cortex(v,positional=True) for v in vals))
            elif shape=='cuerpo':
                text=ent['value']
                if '\n' not in text:
                    lines.append(head+'{'+text+'}')
                else:
                    lines.append(head+'{'); lines.extend(text.split('\n')); lines.append('}')
            elif shape=='bloque':
                text=ent['value']['text']
                lines.append(head+'{'); lines.extend(text.split('\n')); lines.append('}')
            else: raise ValueError(shape)
    return '\n'.join(lines)+'\n'

def md_escape(s:str)->str:
    return s.replace('\\','\\\\').replace('|','\\|').replace('\n','<br>')

def md_unescape(s:str)->str:
    return s.replace('<br>','\n').replace('\\|','|').replace('\\\\','\\')

def code_cell(s:str)->str:
    # Canonical corpus avoids embedded backtick scalar lexemes; block payload handles arbitrary runs.
    return '`'+md_escape(s)+'`'

def strip_code_cell(s:str)->str:
    s=s.strip()
    if len(s)>=2 and s[0]=='`' and s[-1]=='`': return md_unescape(s[1:-1])
    return md_unescape(s)

def table(headers:list[str], rows:list[list[str]])->list[str]:
    return ['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |'] + ['| '+' | '.join(r)+' |' for r in rows]

def split_md_row(line:str)->list[str]:
    s=line.strip()
    if not (s.startswith('|') and s.endswith('|')): raise ValueError('not table row')
    s=s[1:-1]
    cells=[]; cur=[]; esc=False; in_code=False
    for ch in s:
        if esc:
            cur.append('\\'+ch); esc=False
        elif ch=='\\': esc=True
        elif ch=='`': in_code=not in_code; cur.append(ch)
        elif ch=='|' and not in_code:
            cells.append(''.join(cur).strip()); cur=[]
        else: cur.append(ch)
    cells.append(''.join(cur).strip())
    return cells

def render_hcortex(doc:dict)->str:
    meta={"hcortex":"0.1","mode":"canonical","cortex":"0.1","encoding":"UTF-8"}
    lines=[f"<!-- hcortex {json.dumps(meta,separators=(',',':'),sort_keys=True)} -->",'# HCORTEX · CORTEX 0.1','', '## Glosario','', '### Formato']
    lines += table(['Clave','Valor'], [[code_cell(k),code_cell(str(v))] for k,v in doc['format'].items()])
    lines += ['', '### Enums']
    lines += table(['Nombre','Valores'], [[code_cell(e['name']),code_cell(json.dumps(e['values'],ensure_ascii=False,separators=(',',':')))] for e in sorted(doc['enums'],key=lambda x:x['name'])] or [[code_cell('—'),code_cell('[]')]])
    lines += ['', '### Microtokens']
    lines += table(['Token','Expansión'], [[code_cell(m['token']),code_cell(m['expand'])] for m in sorted(doc['microtokens'],key=lambda x:x['token'])] or [[code_cell('—'),code_cell('—')]])
    lines += ['', '### Namespaces']
    lines += table(['Nombre','URI','Versión'], [[code_cell(n['name']),code_cell(n['uri']),code_cell(n.get('version') or '—')] for n in sorted(doc['namespaces'],key=lambda x:x['name'])] or [[code_cell('—'),code_cell('—'),code_cell('—')]])
    lines += ['', '### Extensiones']
    erows=[]
    for x in sorted(doc['extensions'], key=lambda x:(x['namespace'],x['id'],x['version'])):
        erows.append([code_cell(x['namespace']),code_cell(x['id']),code_cell(x['version']),code_cell('true' if x['required'] else 'false'),code_cell(json.dumps(x.get('config',{}),ensure_ascii=False,separators=(',',':'),sort_keys=True))])
    lines += table(['Namespace','ID','Versión','Requerida','Config'], erows or [[code_cell('—')]*5])
    lines += ['', '### Sigilos']
    srows=[]
    for s in sorted(doc['symbols'], key=lambda x:qsymbol(x)):
        srows.append([code_cell(s.get('namespace') or '—'),code_cell(s['symbol']),code_cell(s['label']),code_cell(s['shape']),code_cell(s['weight']),code_cell(contract_text(s) or '—'),code_cell(s.get('focus') or '$body'),code_cell('true' if s.get('open') else 'false'),md_escape(s['desc'])])
    lines += table(['Namespace','Sigilo','Nombre','Shape','Peso','Contrato','Foco','Open','Descripción'],srows)
    symmap={qsymbol(s):s for s in doc['symbols']}
    for sec in doc['sections']:
        lines += ['', '---', '', f"## ${sec['id']}" + (f" · {sec['title']}" if sec.get('title') else '')]
        for ent in sec['ideas']:
            q=qsymbol(ent); sym=symmap[q]; shape=ent.get('shape') or sym['shape']
            emeta={"section":sec['id'],"symbol":ent['symbol'],"namespace":ent.get('namespace'),"name":ent['name'],"shape":shape}
            if shape=='bloque': emeta['media_type']=ent['value']['media_type']
            lines += ['', f"<!-- cortex-entry {json.dumps(emeta,separators=(',',':'),sort_keys=True)} -->",f"### {q}:{ent['name']} · {sym['label']}",'']
            if shape=='attrs':
                vals={k:v for k,v in ent['value']}; rows=[]
                for f in sym['fields']:
                    if f['name'] in vals:
                        rows.append([str(len(rows)+1),code_cell(f['name']),code_cell(scalar_cortex(vals.pop(f['name']), focus=(f['name']==sym.get('focus'))))])
                for k in sorted(vals): rows.append([str(len(rows)+1),code_cell(k),code_cell(scalar_cortex(vals[k]))])
                lines += table(['#','Campo','Valor'],rows)
            elif shape in ('attrs-pos','relacion'):
                rows=[]
                for idx,v in enumerate(ent['value']):
                    f=sym['pos'][idx] if idx < len(sym['pos']) else {"name":f"extra_{idx+1}"}
                    rows.append([str(idx+1),code_cell(f['name']),code_cell(scalar_cortex(v,positional=True))])
                lines += table(['#','Campo','Valor'],rows)
            elif shape=='cuerpo':
                lines.append('```hcortex-text'); lines.extend(ent['value'].split('\n')); lines.append('```')
            elif shape=='bloque':
                text=ent['value']['text']; maxrun=max([len(x) for x in re.findall(r'`+',text)] or [0]); fence='`'*max(3,maxrun+1)
                lines.append(fence+'cortex-block'); lines.extend(text.split('\n')); lines.append(fence)
    return '\n'.join(lines).rstrip()+'\n'

def parse_table(lines:list[str], i:int):
    if i+1>=len(lines) or not lines[i].startswith('| '): raise ValueError('H411')
    headers=split_md_row(lines[i]); i+=2; rows=[]
    while i<len(lines) and lines[i].startswith('| '): rows.append(split_md_row(lines[i])); i+=1
    return headers,rows,i

def compile_hcortex(text:str)->dict:
    lines=text.replace('\r\n','\n').replace('\r','\n').split('\n')
    if not lines or not lines[0].startswith('<!-- hcortex '): raise ValueError('H400')
    try: meta=json.loads(lines[0][len('<!-- hcortex '):-len(' -->')])
    except Exception as e: raise ValueError('H401') from e
    if meta.get('hcortex')!='0.1': raise ValueError('H401')
    if meta.get('mode')!='canonical': raise ValueError('H402')
    for line in lines[1:]:
        if line.startswith('<!--') and not line.startswith('<!-- cortex-entry '):
            raise ValueError('H481')
        if re.search(r'<\/?(?:script|iframe|object|embed|style|link|meta|img)\b', line, flags=re.IGNORECASE):
            raise ValueError('H482')
    try: i=lines.index('### Formato')+1
    except ValueError as e: raise ValueError('H410') from e
    while i<len(lines) and lines[i]=='': i+=1
    _,rows,i=parse_table(lines,i); fmt={strip_code_cell(r[0]):strip_code_cell(r[1]) for r in rows}
    def seek(title, start):
        try: j=lines.index(title,start)+1
        except ValueError as e: raise ValueError('H410') from e
        while j<len(lines) and lines[j]=='': j+=1
        return j
    i=seek('### Enums',i); _,rows,i=parse_table(lines,i)
    enums=[]
    for r in rows:
        n=strip_code_cell(r[0]); v=strip_code_cell(r[1])
        if n!='—': enums.append({"name":n,"values":json.loads(v)})
    i=seek('### Microtokens',i); _,rows,i=parse_table(lines,i)
    micros=[]
    for r in rows:
        t=strip_code_cell(r[0]); e=strip_code_cell(r[1])
        if t!='—': micros.append({"token":t,"expand":e})
    i=seek('### Namespaces',i); _,rows,i=parse_table(lines,i)
    namespaces=[]
    for r in rows:
        n=strip_code_cell(r[0])
        if n!='—': namespaces.append({"name":n,"uri":strip_code_cell(r[1]),"version":None if strip_code_cell(r[2])=='—' else strip_code_cell(r[2])})
    i=seek('### Extensiones',i); _,rows,i=parse_table(lines,i)
    extensions=[]
    for r in rows:
        ns=strip_code_cell(r[0])
        if ns!='—': extensions.append({"namespace":ns,"id":strip_code_cell(r[1]),"version":strip_code_cell(r[2]),"required":strip_code_cell(r[3])=='true',"config":json.loads(strip_code_cell(r[4]))})
    i=seek('### Sigilos',i); _,rows,i=parse_table(lines,i)
    symbols=[]
    for r in rows:
        ns=strip_code_cell(r[0]); shape=strip_code_cell(r[3]); ct=strip_code_cell(r[5]); arr=[]
        if ct!='—':
            for item in ct.split('|'):
                m=re.fullmatch(r'([A-Za-z_][A-Za-z0-9_-]*):([^?]+)(\?)?',item)
                if not m: raise ValueError('H414')
                arr.append({"name":m.group(1),"type":m.group(2),"optional":bool(m.group(3))})
        symbols.append({"namespace":None if ns=='—' else ns,"symbol":strip_code_cell(r[1]),"label":strip_code_cell(r[2]),"shape":shape,"weight":strip_code_cell(r[4]),"fields":arr if shape=='attrs' else [],"pos":arr if shape in ('attrs-pos','relacion') else [],"focus":None if strip_code_cell(r[6])=='$body' else strip_code_cell(r[6]),"open":strip_code_cell(r[7])=='true',"desc":md_unescape(r[8])})
    doc=document(symbols,[],enums=enums,micros=micros,namespaces=namespaces,extensions=extensions,language=fmt.get('language','es'))
    doc['format']=fmt
    symmap={qsymbol(s):s for s in symbols}
    sections=[]; current=None; idx=0
    while idx < len(lines):
        m=re.fullmatch(r'## \$([1-9][0-9]*)(?: · (.*))?',lines[idx])
        if m:
            current={"id":m.group(1),"title":m.group(2),"ideas":[]}; sections.append(current); idx+=1; continue
        if lines[idx].startswith('<!-- cortex-entry '):
            if current is None: raise ValueError('H420')
            try: emeta=json.loads(lines[idx][len('<!-- cortex-entry '):-len(' -->')])
            except Exception as e: raise ValueError('H431') from e
            if idx+1>=len(lines): raise ValueError('H432')
            hm=re.fullmatch(r'### ((?:[a-z][a-z0-9_.-]*::)?[A-Z!][A-Z0-9_]*):([A-Za-z_][A-Za-z0-9_.-]*) · (.+)',lines[idx+1])
            if not hm: raise ValueError('H432')
            q=hm.group(1); name=hm.group(2)
            if q not in symmap: raise ValueError('H433')
            sym=symmap[q]; shape=sym['shape']
            if emeta.get('shape')!=shape or emeta.get('name')!=name or emeta.get('section')!=current['id']: raise ValueError('H432')
            idx+=2
            while idx<len(lines) and lines[idx]=='': idx+=1
            ent={"symbol":sym['symbol'],"namespace":sym.get('namespace'),"name":name,"shape":shape}
            if shape in ('attrs','attrs-pos','relacion'):
                _,rows,idx=parse_table(lines,idx)
                vals=[]
                if shape=='attrs':
                    pairs=[]
                    fmap={f['name']:f for f in sym['fields']}
                    expected=1
                    for r in rows:
                        if int(r[0])!=expected: raise ValueError('H441')
                        key=strip_code_cell(r[1]); lex=strip_code_cell(r[2]); f=fmap.get(key,{"type":"any"})
                        pairs.append((key,parse_scalar_lexeme(lex,f.get('type','any')))); expected+=1
                    ent['value']=pairs
                else:
                    expected=1
                    for r in rows:
                        if int(r[0])!=expected: raise ValueError('H451')
                        f=sym['pos'][expected-1] if expected-1 < len(sym['pos']) else {"type":"any"}
                        vals.append(parse_scalar_lexeme(strip_code_cell(r[2]),f.get('type','any'))); expected+=1
                    ent['value']=vals
            elif shape in ('cuerpo','bloque'):
                if idx>=len(lines) or not lines[idx].startswith('```'): raise ValueError('H460' if shape=='cuerpo' else 'H461')
                fence=re.match(r'(`{3,})',lines[idx]).group(1)
                info=lines[idx][len(fence):]
                if shape=='cuerpo' and info!='hcortex-text': raise ValueError('H460')
                if shape=='bloque' and info!='cortex-block': raise ValueError('H461')
                idx+=1; body=[]
                while idx<len(lines) and lines[idx]!=fence: body.append(lines[idx]); idx+=1
                if idx>=len(lines): raise ValueError('H461')
                idx+=1; val='\n'.join(body)
                if shape=='cuerpo': ent['value']=val
                else: ent['value']={"media_type":emeta.get('media_type','text/plain'),"text":val}
            current['ideas'].append(ent)
            continue
        idx+=1
    doc['sections']=sections
    return doc

def logical_normalize(doc:dict)->dict:
    # Normalize only representation-neutral defaults; preserve semantic order.
    d=copy.deepcopy(doc)
    d['enums']=sorted(d['enums'],key=lambda x:x['name'])
    d['microtokens']=sorted(d['microtokens'],key=lambda x:x['token'])
    for n in d['namespaces']:
        n.setdefault('version', None)
    d['namespaces']=sorted(d['namespaces'],key=lambda x:x['name'])
    for x in d['extensions']:
        x.setdefault('config', {})
    d['extensions']=sorted(d['extensions'],key=lambda x:(x['namespace'],x['id'],x['version']))
    for sym in d['symbols']:
        if sym.get('focus') == '$body': sym['focus'] = None
        sym.setdefault('namespace', None)
        sym.setdefault('fields', [])
        sym.setdefault('pos', [])
        sym.setdefault('open', False)
    d['symbols']=sorted(d['symbols'],key=lambda x:qsymbol(x))
    sm={qsymbol(x):x for x in d['symbols']}
    for sec in d['sections']:
        for ent in sec['ideas']:
            ent.setdefault('namespace', None)
            if ent.get('shape') is None:
                ent['shape']=sm[qsymbol(ent)]['shape']
            sym=sm[qsymbol(ent)]
            if ent['shape']=='attrs':
                values={k:v for k,v in ent['value']}
                ordered=[]
                for field in sym['fields']:
                    if field['name'] in values:
                        ordered.append((field['name'], values.pop(field['name'])))
                ordered.extend((k, values[k]) for k in sorted(values))
                ent['value']=ordered
    return d

def sha(s:str)->str: return hashlib.sha256(s.encode('utf-8')).hexdigest()

def readable_scalar(v):
    if v['kind']=='string': return v['value']
    if v['kind']=='list': return ', '.join(readable_scalar(x) for x in v['items'])
    if v['kind']=='boolean': return 'sí' if v['value'] else 'no'
    if v['kind']=='null': return '—'
    return v['value']

def render_readable(doc:dict)->str:
    lines=['# Contexto CORTEX','']
    symmap={qsymbol(s):s for s in doc['symbols']}
    for sec in doc['sections']:
        lines.append(f"## {sec.get('title') or 'Sección '+sec['id']}"); lines.append('')
        for ent in sec['ideas']:
            sym=symmap[qsymbol(ent)]; lines.append(f"### {sym['label']}: {ent['name']}"); lines.append('')
            sh=sym['shape']
            if sh=='attrs':
                for k,v in ent['value']: lines.append(f"- **{k}:** {readable_scalar(v)}")
            elif sh in ('attrs-pos','relacion'):
                for idx,v in enumerate(ent['value']):
                    f=sym['pos'][idx]['name'] if idx<len(sym['pos']) else str(idx+1)
                    lines.append(f"- **{f}:** {readable_scalar(v)}")
            elif sh=='cuerpo': lines.append(ent['value'])
            elif sh=='bloque':
                lang=ent['value']['media_type'].split('/')[-1].replace('x-','')
                lines.append(f"```{lang}"); lines.extend(ent['value']['text'].split('\n')); lines.append('```')
            lines.append('')
    return '\n'.join(lines).rstrip()+'\n'

def loss_report(case_id, cortex, hc, readable):
    return {
      "schema_version":"0.1","case":case_id,"operation":"render","source_format":"cortex-0.1",
      "target_format":"hcortex-0.1","mode":"canonical","reversible":True,
      "structural_equivalence":True,"source_sha256":sha(cortex),"target_sha256":sha(hc),
      "losses":[],"warnings":[],"preserved":["document-format","local-glossary","section-order","idea-order","identity","shape","contract","scalar-kind","decimal-precision","unicode","verbatim-block"]
    }

def readable_loss_report(case_id,cortex,readable):
    return {
      "schema_version":"0.1","case":case_id,"operation":"render","source_format":"cortex-0.1",
      "target_format":"hcortex-0.1","mode":"readable","reversible":False,
      "structural_equivalence":False,"source_sha256":sha(cortex),"target_sha256":sha(readable),
      "losses":[
        {"code":"L410_GLOSSARY_COLLAPSED","severity":"loss","category":"structure","path":"/$0","detail":"El glosario completo no se emite en READABLE.","recoverability":"from-source-only","action":"Conservar CORTEX o HCORTEX-CANONICAL."},
        {"code":"L411_MACHINE_METADATA_REMOVED","severity":"loss","category":"identity","path":"/sections/*/ideas/*","detail":"Se omite metadata de reconstrucción.","recoverability":"from-source-only","action":"No compilar READABLE como canon."}
      ],
      "warnings":[{"code":"W412_DISPLAY_NORMALIZED","severity":"warning","category":"lexeme","path":"/sections/*","detail":"Valores se muestran para lectura, no como lexemas canónicos.","recoverability":"not-applicable","action":"Usar CANONICAL para roundtrip."}],
      "preserved":["human-content","section-sequence","idea-sequence"]
    }

