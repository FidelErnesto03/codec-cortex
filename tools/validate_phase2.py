#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cortex01_validator', ROOT/'tools/cortex01_validator.py')
mod=importlib.util.module_from_spec(spec); sys.modules['cortex01_validator']=mod; spec.loader.exec_module(mod)


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    manifest=load(ROOT/'examples/manifest.json')
    ast_validator=Draft202012Validator(load(ROOT/'schemas/ast-schema.json'))
    diag_validator=Draft202012Validator(load(ROOT/'schemas/diagnostic-schema.json'))
    failures=[]
    valid_count=0
    invalid_count=0

    for case in manifest['valid']:
        source=ROOT/'examples'/case['source']
        expected_path=ROOT/'examples'/case['expectedAst']
        ast,diags=mod.parse_document(source.read_text(encoding='utf-8'))
        if diags:
            failures.append(f"{case['id']}: valid rejected {diags}")
            continue
        expected=load(expected_path)
        if ast != expected:
            failures.append(f"{case['id']}: AST mismatch")
        schema_errors=list(ast_validator.iter_errors(ast))
        if schema_errors:
            failures.append(f"{case['id']}: AST schema {schema_errors[0].message}")
        valid_count+=1

    for case in manifest['invalid']:
        source=ROOT/'examples'/case['source']
        expected=load(ROOT/'examples'/case['expectedDiagnostics'])
        ast,diags=mod.parse_document(source.read_text(encoding='utf-8'))
        if ast is not None or not diags:
            failures.append(f"{case['id']}: invalid accepted")
            continue
        codes={d['code'] for d in diags}
        missing=set(expected['requiredCodes'])-codes
        if missing:
            failures.append(f"{case['id']}: missing diagnostics {sorted(missing)}; got {sorted(codes)}")
        for d in diags:
            schema_errors=list(diag_validator.iter_errors(d))
            if schema_errors:
                failures.append(f"{case['id']}: diagnostic schema {schema_errors[0].message}")
        invalid_count+=1

    required=[
        ROOT/'spec/cortex-0.1.md', ROOT/'spec/fundamental-glossary-0.1.md',
        ROOT/'spec/errors.md', ROOT/'grammar/cortex.abnf', ROOT/'grammar/cortex.ebnf',
        ROOT/'schemas/ast-schema.json', ROOT/'schemas/diagnostic-schema.json'
    ]
    for p in required:
        if not p.is_file() or p.stat().st_size == 0:
            failures.append(f"missing or empty: {p.relative_to(ROOT)}")

    report={
        'phase':'2', 'cortexVersion':'0.1', 'revision':'DRAFT-REAL-001',
        'validCases':len(manifest['valid']), 'validExecuted':valid_count,
        'invalidCases':len(manifest['invalid']), 'invalidExecuted':invalid_count,
        'failures':failures,
        'status':'PASS' if not failures else 'FAIL'
    }
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if not failures else 1

if __name__=='__main__':
    raise SystemExit(main())
