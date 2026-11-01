#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {canonicalize} from './c14n.mjs';
const root=path.resolve(path.dirname(new URL(import.meta.url).pathname),'../..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'corpus/manifest.json'),'utf8'));
const failures=[]; let golden=0,idempotence=0;
for(const c of manifest.cases){
  const input=fs.readFileSync(path.join(root,c.input));
  const expected=fs.readFileSync(path.join(root,c.canonical));
  const r=canonicalize(input);
  if(Buffer.compare(r.bytes,expected)!==0) failures.push(`${c.id}: golden`); else golden++;
  const r2=canonicalize(r.bytes);
  if(Buffer.compare(r.bytes,r2.bytes)!==0) failures.push(`${c.id}: idempotence`); else idempotence++;
}
const eq=JSON.parse(fs.readFileSync(path.join(root,'vectors/equivalence-vectors.json'),'utf8'));
let equivalence=0;
for(const v of eq.vectors){
  const l=canonicalize(fs.readFileSync(path.join(root,v.left))).bytes;
  const r=canonicalize(fs.readFileSync(path.join(root,v.right))).bytes;
  const actual=Buffer.compare(l,r)===0;
  if(actual!==v.expected.canonicalEquivalent) failures.push(`${v.id}: equivalence`); else equivalence++;
}
const result={implementation:'node-independent-experimental',canonicalCases:manifest.cases.length,goldenPass:golden,idempotencePass:idempotence,equivalenceVectors:eq.vectors.length,equivalencePass:equivalence,failures,status:failures.length?'FAIL':'PASS'};
console.log(JSON.stringify(result,null,2)); process.exit(failures.length?1:0);
