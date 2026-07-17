#!/usr/bin/env node
/**
 * Independent experimental C14N-0.1 implementation in Node.js.
 * It is differential evidence only; it does not satisfy the Charter's
 * Python+Rust independent-review requirement.
 */
import crypto from 'node:crypto';

const nfc = (s) => s.normalize('NFC');
const fail = (m) => { throw new Error(m); };

function splitTop(s, delim) {
  const out=[]; let buf=''; let quote=false, esc=false, depth=0;
  for (const ch of s) {
    if (quote) {
      buf += ch;
      if (esc) esc=false;
      else if (ch==='\\') esc=true;
      else if (ch==='"') quote=false;
      continue;
    }
    if (ch==='"') { quote=true; buf+=ch; continue; }
    if ('[{('.includes(ch)) depth++;
    else if (']})'.includes(ch)) depth--;
    if (ch===delim && depth===0) { out.push(buf); buf=''; }
    else buf+=ch;
  }
  out.push(buf); return out;
}

function scalar(kind,value,lexeme='') { return {kind,value,lexeme}; }
function parseScalar(src) {
  const s=src.trim();
  if (!s) return scalar('text','',src);
  if (s.startsWith('"')) {
    if (!s.endsWith('"')) fail('unclosed string');
    return scalar('string',JSON.parse(s),s);
  }
  if (s.startsWith('[')) {
    if (!s.endsWith(']')) fail('unclosed list');
    const inner=s.slice(1,-1);
    const vals=inner.trim()?splitTop(inner,',').map(parseScalar):[];
    if (vals.some(v=>v.kind==='list')) fail('nested list');
    return scalar('list',vals,s);
  }
  if (s==='true') return scalar('bool',true,s);
  if (s==='false') return scalar('bool',false,s);
  if (s==='null') return scalar('null',null,s);
  if (/^-?(0|[1-9][0-9]*)$/.test(s)) return scalar('int',s,s);
  if (/^-?(0|[1-9][0-9]*)\.[0-9]+$/.test(s)) return scalar('dec',s,s);
  return scalar('atom',s,s);
}

function parseAttrs(inner) {
  const attrs=new Map();
  if (!inner.trim()) return attrs;
  for (const part of splitTop(inner,',')) {
    const kv=splitTop(part,':');
    if (kv.length<2) fail(`invalid attr ${part}`);
    const key=kv.shift().trim();
    if (!/^[a-z_][a-z0-9_-]*$/.test(key)) fail(`invalid key ${key}`);
    if (attrs.has(key)) fail(`duplicate key ${key}`);
    attrs.set(key,parseScalar(kv.join(':')));
  }
  return attrs;
}

function parseContract(text) {
  if (!text) return [];
  return text.split('|').map(cell=>{
    let optional=cell.endsWith('?'); if (optional) cell=cell.slice(0,-1);
    const idx=cell.indexOf(':');
    return idx<0?{name:cell,type:'any',optional}:{name:cell.slice(0,idx),type:cell.slice(idx+1),optional};
  });
}

function coerce(v,typ) {
  const base=typ.endsWith('?')?typ.slice(0,-1):typ;
  if (base==='text') return scalar('string',String(v.value),v.lexeme);
  if (base==='integer') return scalar('int',String(v.value),v.lexeme);
  if (base==='decimal') return scalar('dec',String(v.value),v.lexeme);
  if (base==='boolean') {
    if (v.kind==='bool') return v;
    if (String(v.value)==='true') return scalar('bool',true,v.lexeme);
    if (String(v.value)==='false') return scalar('bool',false,v.lexeme);
  }
  if (base.startsWith('%') || base==='atom') return scalar('atom',String(v.value),v.lexeme);
  return v;
}

function coerceAttrs(attrs,contract) {
  const by=new Map(contract.map(f=>[f.name,f]));
  const out=new Map();
  for (const [k,v] of attrs) out.set(k,by.has(k)?coerce(v,by.get(k).type):v);
  return out;
}

function parseDoc(bytes) {
  if (bytes.length>=3 && bytes[0]===0xef && bytes[1]===0xbb && bytes[2]===0xbf) fail('BOM');
  let text=new TextDecoder('utf-8',{fatal:true}).decode(bytes).replace(/\r\n/g,'\n').replace(/\r/g,'\n');
  const lines=text.split('\n');
  const metas=[],symbols=[],sections=[],micros=new Map(),symMap=new Map();
  let current=null, seen=false, i=0;
  while (i<lines.length) {
    const raw=lines[i++], line=raw.trim();
    if (!line || line.startsWith('#')) continue;
    let m=line.match(/^\$(\d+)(?::[ \t]+(.*))?$/);
    if (m) {
      const id=Number(m[1]),title=m[2];
      if (id===0) { if (seen||sections.length) fail('duplicate/misplaced $0'); seen=true; current=0; }
      else { if(!seen) fail('$0 required'); current={id,title:title===undefined?null:title.trim(),ideas:[]}; sections.push(current); }
      continue;
    }
    if (current===0) {
      m=line.match(/^\$0:([A-Za-z_][A-Za-z0-9_.-]*)\{(.*)\}$/);
      if (m) {
        const attrs=parseAttrs(m[2]); metas.push({name:m[1],attrs});
        if (m[1].startsWith('micro_') && attrs.has('expand')) micros.set(m[1].slice(6),attrs.get('expand'));
        continue;
      }
      m=line.match(/^((?:[a-z][a-z0-9_.-]*::)?(?:!|[A-Z][A-Z0-9_]{0,15})):([A-Za-z_][A-Za-z0-9_.-]*)\{(.*)\}$/);
      if (m) {
        const attrs=parseAttrs(m[3]); const shape=attrs.get('type')?.value??'';
        const ns=attrs.get('namespace')?.value??null;
        let contract=[];
        if (shape==='attrs') contract=parseContract(String(attrs.get('fields')?.value??''));
        else if (shape==='attrs-pos'||shape==='relacion') contract=parseContract(String(attrs.get('pos')?.value??''));
        const sd={symbol:m[1],label:m[2],attrs,shape,contract,focus:attrs.get('focus')?.value??null,namespace:ns};
        const q=m[1].includes('::')?m[1]:(ns?`${ns}::${m[1]}`:m[1]);
        symMap.set(m[1],sd); symMap.set(q,sd); symbols.push(sd); continue;
      }
      fail(`invalid glossary line: ${line}`);
    }
    if (!current || current===0) fail('idea outside section');
    m=line.match(/^((?:[a-z][a-z0-9_.-]*::)?(?:!|[A-Z][A-Z0-9_]{0,15})):([A-Za-z_][A-Za-z0-9_.-]*)(.*)$/);
    if (!m) fail(`invalid idea: ${line}`);
    const sym=m[1],name=m[2],tail=m[3],sd=symMap.get(sym); if(!sd) fail(`undeclared ${sym}`);
    let payload;
    if (sd.shape==='attrs') {
      if (!(tail.startsWith('{')&&tail.endsWith('}'))) fail('attrs delimiter');
      payload=coerceAttrs(parseAttrs(tail.slice(1,-1)),sd.contract);
    } else if (sd.shape==='attrs-pos'||sd.shape==='relacion') {
      if (!tail.startsWith('|')) fail('pipe delimiter');
      payload=splitTop(tail.slice(1),'|').map((c,idx)=>coerce(parseScalar(c.trim()),sd.contract[idx]?.type??'any'));
    } else if (sd.shape==='cuerpo'||sd.shape==='bloque') {
      if (tail.startsWith('{')&&tail.endsWith('}')&&tail.length>=2) payload=tail.slice(1,-1);
      else if (tail==='{') {
        const body=[]; let closed=false;
        while (i<lines.length) { if (lines[i].trim()==='}') {i++;closed=true;break;} body.push(lines[i++]); }
        if(!closed) fail('body unclosed'); payload=body.join('\n');
      } else fail('body delimiter');
    } else fail(`unknown shape ${sd.shape}`);
    current.ideas.push({symbol:sym,name,shape:sd.shape,payload,contract:sd.contract,focus:sd.focus});
  }
  if (!seen) fail('$0 missing');
  if (!metas.length||metas[0].name!=='format') fail('$0:format first');
  return {metas,symbols,sections,micros};
}

const control=new Map([[8,'\\b'],[12,'\\f'],[10,'\\n'],[13,'\\r'],[9,'\\t']]);
function emitString(v) {
  let out='"'; for (const ch of nfc(v)) { const cp=ch.codePointAt(0);
    if(ch==='"') out+='\\"'; else if(ch==='\\') out+='\\\\'; else if(control.has(cp)) out+=control.get(cp);
    else if(cp<32||cp===127) out+=`\\u${cp.toString(16).toUpperCase().padStart(4,'0')}`; else out+=ch;
  } return out+'"';
}
const atomSafe=(s)=>/^[^\s\[\]{} ,"|]+$/.test(s);
function expand(v,micros) {
  if(v.kind==='atom'&&micros.has(v.value)) { const e=micros.get(v.value); return scalar(e.kind,e.value,e.lexeme); }
  if(v.kind==='list') return scalar('list',v.value.map(x=>expand(x,micros)),v.lexeme);
  return v;
}
function emitScalar(v,micros=null) {
  if(micros) v=expand(v,micros);
  if(v.kind==='string') return emitString(String(v.value));
  if(v.kind==='atom') { const x=nfc(String(v.value)); return atomSafe(x)?x:emitString(x); }
  if(v.kind==='int') return String(BigInt(v.value));
  if(v.kind==='dec') return String(v.value);
  if(v.kind==='bool') return v.value?'true':'false';
  if(v.kind==='null') return 'null';
  if(v.kind==='list') return `[${v.value.map(x=>emitScalar(x,micros)).join(',')}]`;
  fail(`unknown scalar ${v.kind}`);
}

const metaOrders={format:['cortex','encoding','language'],enum:['values'],micro:['expand'],namespace:['id','version','required','desc'],extension:['namespace','id','version','required','desc']};
const symOrder=['type','weight','fields','pos','focus','desc','open','namespace','version'];
const cmp=(a,b)=>Buffer.compare(Buffer.from(nfc(a),'utf8'),Buffer.from(nfc(b),'utf8'));
function orderedKeys(attrs,base) { return [...base.filter(k=>attrs.has(k)),...[...attrs.keys()].filter(k=>!base.includes(k)).sort(cmp)]; }
function emitAttrs(attrs,keys,micros=null) { return `{${keys.map(k=>`${k}:${emitScalar(attrs.get(k),micros)}`).join(',')}}`; }
function emitIdeaAttrs(idea,keys,micros) {
  const contract=new Map(idea.contract.map(f=>[f.name,f]));
  return `{${keys.map(k=>{ const v=expand(idea.payload.get(k),micros); const typ=contract.get(k)?.type??'any';
    let rendered;
    if(typ==='text') { const t=nfc(String(v.value)); rendered=(k===idea.focus||!atomSafe(t))?emitString(t):t; }
    else rendered=emitScalar(v);
    return `${k}:${rendered}`; }).join(',')}}`;
}
function metaCat(name) { if(name==='format')return[0,'']; for(const [idx,p] of ['enum_','micro_','namespace_','extension_'].entries())if(name.startsWith(p))return[idx+1,name.slice(p.length)]; return[5,name]; }

export function canonicalize(bytes) {
  const doc=parseDoc(bytes),lines=['$0'];
  const metas=[...doc.metas].sort((a,b)=>{const aa=metaCat(a.name),bb=metaCat(b.name);return aa[0]-bb[0]||cmp(aa[1],bb[1]);});
  for(const {name,attrs} of metas) {
    const cat=name==='format'?'format':name.startsWith('enum_')?'enum':name.startsWith('micro_')?'micro':name.startsWith('namespace_')?'namespace':name.startsWith('extension_')?'extension':'other';
    lines.push(`$0:${name}${emitAttrs(attrs,orderedKeys(attrs,metaOrders[cat]??[]))}`);
  }
  const syms=[...doc.symbols].sort((a,b)=>cmp(a.symbol.includes('::')?a.symbol:(a.namespace?`${a.namespace}::${a.symbol}`:a.symbol),b.symbol.includes('::')?b.symbol:(b.namespace?`${b.namespace}::${b.symbol}`:b.symbol)));
  for(const sd of syms) lines.push(`${sd.symbol}:${sd.label}${emitAttrs(sd.attrs,orderedKeys(sd.attrs,symOrder))}`);
  for(const sec of doc.sections) {
    lines.push(`$${sec.id}${sec.title!==null?`: ${nfc(sec.title)}`:''}`);
    for(const idea of sec.ideas) {
      const head=`${idea.symbol}:${idea.name}`;
      if(idea.shape==='attrs') {
        const contractNames=idea.contract.map(f=>f.name),extras=[...idea.payload.keys()].filter(k=>!contractNames.includes(k)).sort(cmp);
        const keys=[...contractNames.filter(k=>idea.payload.has(k)),...extras];
        lines.push(head+emitIdeaAttrs(idea,keys,doc.micros));
      } else if(idea.shape==='attrs-pos'||idea.shape==='relacion') {
        const cells=idea.payload.map((v,idx)=>{ const typ=idea.contract[idx]?.type??'any',ex=expand(v,doc.micros);
          if(typ==='text'){const t=nfc(String(ex.value));return t&&!t.includes('|')&&!t.includes('\n')&&t===t.trim()&&!t.startsWith('"')?t:emitString(t);} return emitScalar(ex); });
        lines.push(`${head}|${cells.join('|')}`);
      } else if(idea.shape==='cuerpo') {
        const v=nfc(idea.payload.replace(/\r\n/g,'\n').replace(/\r/g,'\n'));
        if(!v.includes('\n')) lines.push(`${head}{${v}}`); else {lines.push(`${head}{`);lines.push(...v.split('\n'));lines.push('}');}
      } else if(idea.shape==='bloque') {
        const v=idea.payload.replace(/\r\n/g,'\n').replace(/\r/g,'\n'); lines.push(`${head}{`);lines.push(...v.split('\n'));lines.push('}');
      }
    }
  }
  const out=Buffer.from(lines.join('\n')+'\n','utf8');
  const canonicalSha256=crypto.createHash('sha256').update(out).digest('hex');
  const canonicalHash='sha256:'+crypto.createHash('sha256').update(Buffer.from('CORTEX-C14N-0.1\0','utf8')).update(out).digest('hex');
  return {bytes:out,canonicalSha256,canonicalHash};
}

if(import.meta.url===`file://${process.argv[1]}`){
  const fs=await import('node:fs'); const input=fs.readFileSync(process.argv[2]); const r=canonicalize(input); process.stdout.write(r.bytes);
}
