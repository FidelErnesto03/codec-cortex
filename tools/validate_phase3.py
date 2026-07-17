#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib, subprocess, sys
from pathlib import Path
from cortex01_c14n import canonicalize, parse_doc

ROOT=Path(__file__).resolve().parents[1]
fail=[]
manifest=json.loads((ROOT/'corpus/manifest.json').read_text())
hash_data=json.loads((ROOT/'vectors/hash-vectors.json').read_text())
hashes={v['id']:v for v in hash_data['vectors']}

golden=idem=reports=hashpass=0
for case in manifest['cases']:
    raw=(ROOT/case['input']).read_bytes(); expected=(ROOT/case['canonical']).read_bytes()
    actual,report=canonicalize(raw)
    if actual!=expected: fail.append(f"{case['id']}: golden mismatch")
    else: golden+=1
    again,_=canonicalize(actual)
    if again!=actual: fail.append(f"{case['id']}: idempotence")
    else: idem+=1
    parse_doc(actual)
    hv=hashes.get(case['id'])
    if not hv:
        fail.append(f"{case['id']}: missing hash vector")
    elif (hashlib.sha256(actual).hexdigest()!=hv['canonicalSha256'] or report['canonicalHash']!=hv['canonicalHash']):
        fail.append(f"{case['id']}: hash mismatch")
    else: hashpass+=1
    stored=json.loads((ROOT/case['report']).read_text())
    if stored!=report: fail.append(f"{case['id']}: report mismatch")
    elif report['structuralLoss'] is False and report.get('losses')==[]: reports+=1
    else: fail.append(f"{case['id']}: non-empty structural loss")

eqs=json.loads((ROOT/'vectors/equivalence-vectors.json').read_text())['vectors']
eqpass=0; eq_actual={}
for v in eqs:
    l=(ROOT/v['left']).read_bytes(); r=(ROOT/v['right']).read_bytes()
    lc,_=canonicalize(l); rc,_=canonicalize(r)
    actual=lc==rc; eq_actual[v['id']]=actual
    if actual!=v['expected']['canonicalEquivalent']: fail.append(f"{v['id']}: equivalence")
    else: eqpass+=1

# Charter-specific executable assertions.
charter_checks={
  'CE-1-idempotence-40': len(manifest['cases'])==40 and idem==40,
  'CE-3-glossary-order-independent': eq_actual.get('E026_glossary_order') is True,
  'CE-4-microtoken-logical-expansion': eq_actual.get('E031_microtoken_positional') is True and eq_actual.get('E007_microtoken') is True,
  'CE-5-unicode-nfc-logical-text': eq_actual.get('E004_unicode_nfc') is True,
  'CE-5-block-unicode-verbatim-exception': eq_actual.get('E030_bloque_nfc_nfd') is False,
  'F3-D-decimal-precision-preserved': eq_actual.get('E027_decimal_precision') is False and b'value:0.750' in (ROOT/'corpus/canonical/C035_decimal_precision_preserved.cortex').read_bytes(),
  'CE-6-empty-loss-report': reports==len(manifest['cases']),
}
for name,ok in charter_checks.items():
    if not ok: fail.append(f'{name}: failed')

# Optional second-codebase differential evidence. It does not satisfy CE-2,
# because the Charter explicitly requires an independent Rust implementation.
node_result=None
try:
    proc=subprocess.run(['node',str(ROOT/'implementations/node/validate.mjs')],cwd=ROOT,text=True,capture_output=True,check=False)
    node_result=json.loads(proc.stdout) if proc.stdout.strip() else {'status':'ERROR','stderr':proc.stderr}
    if proc.returncode!=0 or node_result.get('status')!='PASS': fail.append('node differential implementation failed')
except (FileNotFoundError,json.JSONDecodeError) as e:
    node_result={'status':'UNAVAILABLE','reason':str(e)}

# optional schema validation
try:
    import jsonschema
    schema=json.loads((ROOT/'schemas/canonicalization-report.schema.json').read_text())
    for case in manifest['cases']:
        jsonschema.validate(json.loads((ROOT/case['report']).read_text()),schema)
except ImportError:
    pass

internal_ok=not fail
result={
  'phase':'3',
  'canonicalization':'C14N-0.1',
  'authority':'CORTEX-F3-CHARTER-001',
  'upstream':'CORTEX-SPEC-0.1-DRAFT-REAL-001',
  'canonicalCases':len(manifest['cases']),
  'goldenPass':golden,
  'idempotencePass':idem,
  'hashPass':hashpass,
  'emptyLossReportPass':reports,
  'equivalenceVectors':len(eqs),
  'equivalencePass':eqpass,
  'charterChecks':charter_checks,
  'auxiliaryNodeDifferential':node_result,
  'gateDependencies':{
    'CE-2-python-rust-independent':'BLOCKED_NOT_EXECUTED',
    'CE-7-hcortex-roundtrip':'BLOCKED_PENDING_PHASE_4',
    'externalReview':'BLOCKED_PENDING'
  },
  'failures':fail,
  'internalStatus':'PASS' if internal_ok else 'FAIL',
  'gateStatus':'BLOCKED'
}
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(0 if internal_ok else 1)
