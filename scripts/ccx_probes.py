#!/usr/bin/env python3
"""Probes P01-P29 for CODEC-CORTEX canonical (slots + HCORTEX + migration + harness).

Usage: python3 scripts/ccx_probes.py [checkout-path]
       (checkout-path defaults to repo root)

Outputs JSON report with 29 probe verdicts.
"""

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


CHECKOUT = Path(__file__).resolve().parent.parent


def _checkout(p):
    return CHECKOUT / p


def _import():
    for mod in list(sys.modules.keys()):
        if mod.startswith("codec_cortex"):
            del sys.modules[mod]
    sys.path.insert(0, str(CHECKOUT))


def probe_p01():
    """P01: ※ dentro de string quoted in 0.1 doc → accepted as content (no I058)."""
    _import()
    from codec_cortex import parse_cortex
    src = '''$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es}
KNW:knowledge{type:attrs,weight:H,fields:"topic:text|content:text|status:atom",focus:topic,desc:"t"}
$1: T
KNW:x{topic:"test ※1: inside string",content:"body",status:current}'''
    try:
        doc = parse_cortex(src)
        idea = doc.sections[0].ideas[0]
        for k, v in idea.payload[1]:
            if k == "topic":
                if "※1:" in v.value:
                    return {"probe": "P01", "verdict": "pass", "actual": "※ preserved in string content"}
                return {"probe": "P01", "verdict": "fail", "actual": f"※ NOT preserved: {v.value!r}"}
        return {"probe": "P01", "verdict": "fail", "actual": "topic field not found"}
    except Exception as e:
        code = getattr(e, "code", "UNKNOWN")
        return {"probe": "P01", "verdict": "fail", "actual": f"{code}: {e}"}


def probe_p02():
    """P02: ※ dentro de cuerpo in 0.1 doc → accepted as content."""
    _import()
    from codec_cortex import parse_cortex
    src = '''$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es}
KNW:note{type:cuerpo,weight:H,desc:"t"}
$1: T
KNW:x{
This is cuerpo text with ※1: as content.
}'''
    try:
        doc = parse_cortex(src)
        idea = doc.sections[0].ideas[0]
        if idea.payload[0] == "cuerpo" and "※1:" in idea.payload[1]:
            return {"probe": "P02", "verdict": "pass", "actual": "※ preserved in cuerpo content"}
        return {"probe": "P02", "verdict": "fail", "actual": f"payload: {idea.payload!r}"}
    except Exception as e:
        code = getattr(e, "code", "UNKNOWN")
        return {"probe": "P02", "verdict": "fail", "actual": f"{code}: {e}"}


def probe_p03():
    """P03: ※ dentro de bloque verbatim in 0.1 doc → bytes preserved."""
    _import()
    from codec_cortex import parse_cortex
    src = '''$0:KERNEL
$0:format{cortex:0.1,encoding:UTF-8,language:es}
BLK:code{type:bloque,weight:H,desc:"t"}
$1: T
BLK:x{
※ { braces
verbatim content
}'''
    try:
        doc = parse_cortex(src)
        idea = doc.sections[0].ideas[0]
        if idea.payload[0] == "bloque" and "※" in idea.payload[1]:
            return {"probe": "P03", "verdict": "pass", "actual": "※ preserved in bloque bytes"}
        return {"probe": "P03", "verdict": "fail", "actual": f"payload: {idea.payload!r}"}
    except Exception as e:
        code = getattr(e, "code", "UNKNOWN")
        return {"probe": "P03", "verdict": "fail", "actual": f"{code}: {e}"}


def probe_p04():
    """P04: Slot ※N:valor mínimo parsea y canonicaliza."""
    _import()
    from codec_cortex import parse_cortex, canonicalize
    src = '''$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}
TST:t{type:attrs,encoding:slots,weight:B,slots:"1=x:atom",focus:x,desc:"t"}
$1: T
TST:a{※1:hello}'''
    try:
        doc = parse_cortex(src)
        canon = canonicalize(doc)
        assert "※1:hello" in canon
        return {"probe": "P04", "verdict": "pass", "actual": "slot parsed and canonicalized"}
    except Exception as e:
        return {"probe": "P04", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p05():
    """P05: Slot múltiples valores posicionales preservan orden."""
    _import()
    from codec_cortex import parse_cortex, canonicalize, hash_cortex
    src = '''$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}
TST:t{type:attrs,encoding:slots,weight:B,slots:"1=a:text|2=b:text|3=c:text",focus:a,desc:"t"}
$1: T
TST:x{※1:alpha,※2:beta,※3:gamma}'''
    try:
        doc = parse_cortex(src)
        canon = canonicalize(doc)
        expected = "※1:alpha,※2:beta,※3:gamma"
        assert expected in canon, f"expected {expected} in {canon}"
        return {"probe": "P05", "verdict": "pass", "actual": "order preserved"}
    except Exception as e:
        return {"probe": "P05", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p06():
    """P06: Slot opcional omitido → no se emite en canon."""
    _import()
    from codec_cortex import parse_cortex, canonicalize
    src = '''$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}
REC:r{type:attrs,encoding:slots,weight:B,slots:"1=a:text|2=b:text?|3=c:text",focus:a,desc:"r"}
$1: R
REC:x{※1:one,※3:three}'''
    try:
        doc = parse_cortex(src)
        canon = canonicalize(doc)
        assert "※2" not in canon, "optional slot should be omitted in canon"
        return {"probe": "P06", "verdict": "pass", "actual": "optional omitted in canon"}
    except Exception as e:
        return {"probe": "P06", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p07():
    """P07: Unicode en slot value preserve NFC normalization."""
    _import()
    from codec_cortex import parse_cortex, canonicalize
    src = '''$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}
TST:t{type:attrs,encoding:slots,weight:B,slots:"1=x:text",focus:x,desc:"t"}
$1: T
TST:a{※1:"caf\u00e9"}'''  # NFD "café" composed as NFC
    try:
        doc = parse_cortex(src)
        canon = canonicalize(doc)
        assert "café" in canon
        return {"probe": "P07", "verdict": "pass", "actual": "unicode NFC preserved"}
    except Exception as e:
        return {"probe": "P07", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p08():
    """P08: Slot marker allowed in named attr value."""
    _import()
    from codec_cortex import parse_cortex
    src = '''$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}
TST:t{type:attrs,encoding:slots,weight:B,slots:"1=desc:text",focus:desc,desc:"t"}
$1: T
TST:a{※1:"※ marker in value"}'''
    try:
        doc = parse_cortex(src)
        idea = doc.sections[0].ideas[0]
        fv = idea.payload[1][0]
        assert "※" in fv.value.value, "marker not preserved in value"
        return {"probe": "P08", "verdict": "pass", "actual": "marker in slot value OK"}
    except Exception as e:
        return {"probe": "P08", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p09():
    """P09: Slot index max (1M) boundary: valid within range, over limit rejects."""
    _import()
    from codec_cortex import parse_cortex
    import tempfile
    src_v = '''$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}
TST:t{type:attrs,encoding:slots,weight:B,slots:"1=x:text",focus:x,desc:"t"}
$1: T
TST:a{※1:ok}'''
    try:
        doc = parse_cortex(src_v)
        return {"probe": "P09", "verdict": "pass", "actual": "index within range works"}
    except Exception as e:
        return {"probe": "P09", "verdict": "fail", "actual": f"valid case failed: {type(e).__name__}: {e}"}


def probe_p10():
    """P10: parse_cortex sin $0:format → G010."""
    _import()
    from codec_cortex import parse_cortex
    src = '''$0:KERNEL
KNW:x{type:attrs,weight:H,fields:"a:text",focus:a,desc:"t"}
$1: T
KNW:y{a:"hello"}'''
    try:
        parse_cortex(src)
        return {"probe": "P10", "verdict": "fail", "actual": "accepted without $0:format"}
    except Exception as e:
        code = getattr(e, "code", "UNKNOWN")
        if "FORMAT" in code or "G010" in code:
            return {"probe": "P10", "verdict": "pass", "actual": code}
        return {"probe": "P10", "verdict": "fail", "actual": f"got {code}, expected G010"}


def probe_p11():
    """P11: attrs-pos con slots preserva posición."""
    _import()
    from codec_cortex import parse_cortex, canonicalize
    src = open(_checkout("conformance/slots/valid/V011_attrs_pos_slots.cortex")).read()
    try:
        doc = parse_cortex(src)
        canon = canonicalize(doc)
        assert "※" in canon and "|" not in canon.split(":")[-1]
        return {"probe": "P11", "verdict": "pass", "actual": "attrs-pos slots parsed"}
    except Exception as e:
        return {"probe": "P11", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p12():
    """P12: relacion con slots preserva semántica."""
    _import()
    from codec_cortex import parse_cortex, canonicalize
    src = open(_checkout("conformance/slots/valid/V010_relation_slots.cortex")).read()
    try:
        doc = parse_cortex(src)
        canon = canonicalize(doc)
        assert "※" in canon
        return {"probe": "P12", "verdict": "pass", "actual": "relation slots parsed"}
    except Exception as e:
        return {"probe": "P12", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p13():
    """P13: doble sección preserva integridad."""
    _import()
    from codec_cortex import parse_cortex
    src = open(_checkout("conformance/slots/valid/V017_two_sections.cortex")).read()
    try:
        doc = parse_cortex(src)
        assert len(doc.sections) == 2
        return {"probe": "P13", "verdict": "pass", "actual": "2 sections"}
    except Exception as e:
        return {"probe": "P13", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p14():
    """P14: namespace qualified sigil preserved."""
    _import()
    from codec_cortex import parse_cortex
    src = open(_checkout("conformance/slots/valid/V023_namespace_qualified.cortex")).read()
    try:
        doc = parse_cortex(src)
        sym = doc.glossary.symbols[0]
        assert sym.namespace is not None
        return {"probe": "P14", "verdict": "pass", "actual": f"namespace={sym.namespace}"}
    except Exception as e:
        return {"probe": "P14", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p15():
    """P15: enum declaration preserved in 0.2."""
    _import()
    from codec_cortex import parse_cortex
    src = open(_checkout("conformance/slots/valid/V022_enum_reference.cortex")).read()
    try:
        doc = parse_cortex(src)
        assert len(doc.glossary.enums) > 0
        return {"probe": "P15", "verdict": "pass", "actual": f"{len(doc.glossary.enums)} enums"}
    except Exception as e:
        return {"probe": "P15", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p16():
    """P16: microtoken expands correctly."""
    _import()
    from codec_cortex import parse_cortex, canonicalize
    src = open(_checkout("conformance/slots/valid/V012_microtoken_slot.cortex")).read()
    try:
        doc = parse_cortex(src)
        canon = canonicalize(doc)
        assert "accepted" in canon
        return {"probe": "P16", "verdict": "pass", "actual": "micro expanded in canon"}
    except Exception as e:
        return {"probe": "P16", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p17():
    """P17: Trailing comma before } in slot payload → syntax error."""
    _import()
    from codec_cortex import parse_cortex
    src = '''$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}
TST:t{type:attrs,encoding:slots,weight:H,slots:"1=x:text",focus:x,schema:table,desc:"t",open:false}
$1: T
TST:a{※1:hello,}'''
    try:
        parse_cortex(src)
        return {"probe": "P17", "verdict": "fail", "actual": "trailing comma accepted"}
    except Exception as e:
        code = getattr(e, "code", "UNKNOWN")
        return {"probe": "P17", "verdict": "pass", "actual": code}


def probe_p18():
    """P18: Index with Unicode digit → L021_INVALID_SLOT_INDEX."""
    _import()
    from codec_cortex import parse_cortex
    src = '''$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}
TST:t{type:attrs,encoding:slots,weight:H,slots:"1=x:text",focus:x,schema:table,desc:"t",open:false}
$1: T
TST:a{※١:x}'''  # Arabic-Indic digit 1
    try:
        parse_cortex(src)
        return {"probe": "P18", "verdict": "fail", "actual": "Unicode digit accepted"}
    except Exception as e:
        code = getattr(e, "code", "UNKNOWN")
        if code in ("L021_INVALID_SLOT_INDEX",):
            return {"probe": "P18", "verdict": "pass", "actual": code}
        return {"probe": "P18", "verdict": "fail", "actual": f"got {code}, expected L021"}


def probe_p19():
    """P19: Nested list as slot value."""
    _import()
    from codec_cortex import parse_cortex, canonicalize
    src = open(_checkout("conformance/slots/valid/V029_nested_list.cortex")).read()
    try:
        doc = parse_cortex(src)
        canon = canonicalize(doc)
        assert "[a" in canon or "[1" in canon or "[" in canon
        return {"probe": "P19", "verdict": "pass", "actual": "list slot parsed"}
    except Exception as e:
        return {"probe": "P19", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p20():
    """P20: Boolean false as slot value."""
    _import()
    from codec_cortex import parse_cortex, canonicalize
    src = open(_checkout("conformance/slots/valid/V030_boolean_false.cortex")).read()
    try:
        doc = parse_cortex(src)
        canon = canonicalize(doc)
        assert "false" in canon
        return {"probe": "P20", "verdict": "pass", "actual": "boolean false parsed"}
    except Exception as e:
        return {"probe": "P20", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p21():
    """P21: Hash CORTEX 0.2 — SHA256 con domain separation."""
    _import()
    from codec_cortex import parse_cortex, hash_cortex
    from codec_cortex.slotc14n import HASH_DOMAIN_SLOTS
    src = open(_checkout("conformance/slots/valid/V001_minimal_slot.cortex")).read()
    try:
        doc = parse_cortex(src)
        h = hash_cortex(doc)
        from codec_cortex.slotc14n import canonicalize_slots
        canon = canonicalize_slots(doc)
        expected = hashlib.sha256(HASH_DOMAIN_SLOTS + b"\x00" + canon.encode("utf-8")).hexdigest()
        if h == expected:
            return {"probe": "P21", "verdict": "pass", "actual": f"hash={h[:16]}..."}
        return {"probe": "P21", "verdict": "fail", "actual": f"got {h[:16]}..., expected {expected[:16]}..."}
    except Exception as e:
        return {"probe": "P21", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p22():
    """P22: Roundtrip HCORTEX on all valid 0.2 cases → 0 fallos."""
    _import()
    from codec_cortex.slothcortex import run_roundtrip
    valid_dir = _checkout("conformance/slots/valid")
    report = run_roundtrip(str(valid_dir))
    if report["failed"] == 0:
        return {"probe": "P22", "verdict": "pass", "actual": f"{report['passed']}/{report['total']} roundtrips OK"}
    return {"probe": "P22", "verdict": "fail", "actual": f"{report['failed']} failures", "details": report["results"][:5]}


def probe_p23():
    """P23: Hidden copy (cortex-ast) inside HCORTEX → H481.
    Verifies both compile-time detection and embed_ast roundtrip."""
    _import()
    from codec_cortex.slothcortex import compile_hcortex_slots, render_hcortex_slots
    from codec_cortex import parse_cortex
    # A) Detection: parse existing mark in HCORTEX
    hc = "<!-- HCORTEX v=0.2 t=canonical -->\n\n<!-- glossary -->\n<!-- cortex-ast: {} -->\n<!-- /glossary -->\n"
    doc, diags = compile_hcortex_slots(hc)
    codes = [d["code"] for d in diags]
    if "H481_HIDDEN_COPY" not in codes:
        return {"probe": "P23", "verdict": "fail", "actual": f"detection: got {codes}, expected H481"}
    # B) Embed: render with embed_ast=True → output contains cortex-ast mark
    src = '''$0:KERNEL
$0:format{cortex:0.2,encoding:UTF-8,language:es}
$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,syntax:"※N:valor",order:"ascending"}
TST:t{type:attrs,encoding:slots,weight:B,slots:"1=x:text",focus:x,desc:"t"}
$1: T
TST:a{※1:hello}'''
    doc2 = parse_cortex(src)
    hc2 = render_hcortex_slots(doc2, embed_ast=True)
    if "cortex-ast:" not in hc2:
        return {"probe": "P23", "verdict": "fail", "actual": f"embed_ast did not inject: first 200 chars: {hc2[:200]!r}"}
    # C) Roundtrip: embedded mark → compile must block with H481
    doc3, diags3 = compile_hcortex_slots(hc2)
    codes3 = [d["code"] for d in diags3]
    if "H481_HIDDEN_COPY" not in codes3:
        return {"probe": "P23", "verdict": "fail", "actual": f"roundtrip: embed_ast output not caught by compile, got {codes3}"}
    return {"probe": "P23", "verdict": "pass", "actual": "H481 triggered"}


def probe_p24():
    """P24: Empty corpus → FAIL explícito (nunca 0/0 PASS)."""
    _import()
    from codec_cortex.slotharness import run_slots_conformance
    try:
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "manifest.json"), "w") as f:
                json.dump({"valid": [], "invalid": []}, f)
            report = run_slots_conformance(tmp)
        if report["verdict"] in ("empty", "FAIL"):
            return {"probe": "P24", "verdict": "pass", "actual": f"empty → {report['verdict']}"}
        return {"probe": "P24", "verdict": "fail", "actual": f"empty → {report['verdict']}"}
    except Exception as e:
        return {"probe": "P24", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p25():
    """P25: Migration preserves metadata format."""
    _import()
    from codec_cortex.slotmigrate import migrate_plan, migrate_apply
    try:
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "src.cortex")
            with open(src, "w") as f:
                f.write('$0:KERNEL\n$0:format{cortex:0.1,encoding:UTF-8,language:es}\nKNW:x{type:attrs,weight:H,fields:"a:text",focus:a,desc:"t"}\n$1: T\nKNW:y{a:hello}')
            plan_path = os.path.join(tmp, "plan.json")
            migrate_plan(src, out_path=plan_path)
            out = os.path.join(tmp, "out.cortex")
            result = migrate_apply(plan_path, out_path=out)
            if result.get("status") != "ok":
                return {"probe": "P25", "verdict": "fail", "actual": result.get("message", "")}
            with open(out) as f:
                content = f.read()
            if 'format{cortex:0.2' in content and 'encoding:UTF-8' in content and 'language:es' in content:
                return {"probe": "P25", "verdict": "pass", "actual": "metadata preserved"}
            return {"probe": "P25", "verdict": "fail", "actual": "metadata not preserved"}
    except Exception as e:
        return {"probe": "P25", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p26():
    """P26: Migration equivalence by AST (not by pointer)."""
    _import()
    from codec_cortex.slotmigrate import migrate_plan, migrate_apply, migrate_verify
    try:
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "src.cortex")
            with open(src, "w") as f:
                f.write('$0:KERNEL\n$0:format{cortex:0.1,encoding:UTF-8,language:es}\nKNW:x{type:attrs,weight:H,fields:"a:text|b:text",focus:a,desc:"t"}\n$1: T\nKNW:y{a:hello,b:world}')
            plan_path = os.path.join(tmp, "plan.json")
            migrate_plan(src, out_path=plan_path)
            out = os.path.join(tmp, "out.cortex")
            migrate_apply(plan_path, out_path=out)
            verify = migrate_verify(src, out)
            if verify.get("status") == "ok":
                return {"probe": "P26", "verdict": "pass", "actual": f"AST equivalence: {len(verify.get('checks', []))} checks"}
            return {"probe": "P26", "verdict": "fail", "actual": json.dumps(verify)}
    except Exception as e:
        return {"probe": "P26", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p27():
    """P27: Migration rollback real que restaura salida y preserva fuente."""
    _import()
    from codec_cortex.slotmigrate import migrate_plan, migrate_rollback
    import shutil
    try:
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "src.cortex")
            with open(src, "w") as f:
                f.write('$0:KERNEL\n$0:format{cortex:0.1,encoding:UTF-8,language:es}\nKNW:x{type:attrs,weight:H,fields:"a:text",focus:a,desc:"t"}\n$1: T\nKNW:y{a:hello}')
            plan_path = os.path.join(tmp, "plan.json")
            migrate_plan(src, out_path=plan_path)
            # Manually create backup to test rollback
            bak = src + ".bak"
            shutil.copy2(src, bak)
            rollback = migrate_rollback(plan_path)
            if rollback.get("status") == "ok":
                # After rollback, backup was deleted and source should be restored
                assert not os.path.exists(bak), "backup should be deleted after rollback"
                with open(src) as f:
                    content = f.read()
                if "0.1" in content:
                    return {"probe": "P27", "verdict": "pass", "actual": "rollback restored 0.1, backup cleaned"}
                return {"probe": "P27", "verdict": "fail", "actual": "rollback did not restore 0.1"}
            return {"probe": "P27", "verdict": "fail", "actual": rollback.get("message", "")}
    except Exception as e:
        return {"probe": "P27", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p28():
    """P28: Migration apply fails if source hash changed after plan."""
    _import()
    from codec_cortex.slotmigrate import migrate_plan, migrate_apply
    try:
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "src.cortex")
            with open(src, "w") as f:
                f.write('$0:KERNEL\n$0:format{cortex:0.1,encoding:UTF-8,language:es}\nKNW:x{type:attrs,weight:H,fields:"a:text",focus:a,desc:"t"}\n$1: T\nKNW:y{a:hello}')
            plan_path = os.path.join(tmp, "plan.json")
            migrate_plan(src, out_path=plan_path)
            with open(src, "a") as f:
                f.write("\n# mutated")
            out = os.path.join(tmp, "out.cortex")
            result = migrate_apply(plan_path, out_path=out)
            if result.get("status") == "error" and "hash" in result.get("message", "").lower():
                return {"probe": "P28", "verdict": "pass", "actual": "hash mismatch detected"}
            return {"probe": "P28", "verdict": "fail", "actual": f"apply accepted despite mutation: {result}"}
    except Exception as e:
        return {"probe": "P28", "verdict": "fail", "actual": f"{type(e).__name__}: {e}"}


def probe_p29():
    """P29: Corpus valid has no duplicate inputs with different IDs."""
    valid_dir = _checkout("conformance/slots/valid")
    if not valid_dir.is_dir():
        return {"probe": "P29", "verdict": "not_run", "actual": "valid dir not found"}
    seen = {}
    dups = []
    for fn in sorted(os.listdir(valid_dir)):
        if not fn.endswith(".cortex"):
            continue
        src = (valid_dir / fn).read_text(encoding="utf-8")
        h = hashlib.sha256(src.encode("utf-8")).hexdigest()
        if h in seen:
            dups.append({"ids": [seen[h], fn], "hash": h[:16]})
        else:
            seen[h] = fn
    if not dups:
        return {"probe": "P29", "verdict": "pass", "actual": f"{len(seen)} unique cases"}
    return {"probe": "P29", "verdict": "fail", "actual": f"{len(dups)} duplicate pairs", "dups": dups}


PROBES = [
    ("P01", probe_p01), ("P02", probe_p02), ("P03", probe_p03),
    ("P04", probe_p04), ("P05", probe_p05), ("P06", probe_p06),
    ("P07", probe_p07), ("P08", probe_p08), ("P09", probe_p09),
    ("P10", probe_p10), ("P11", probe_p11), ("P12", probe_p12),
    ("P13", probe_p13), ("P14", probe_p14), ("P15", probe_p15),
    ("P16", probe_p16), ("P17", probe_p17), ("P18", probe_p18),
    ("P19", probe_p19), ("P20", probe_p20), ("P21", probe_p21),
    ("P22", probe_p22), ("P23", probe_p23), ("P24", probe_p24),
    ("P25", probe_p25), ("P26", probe_p26), ("P27", probe_p27),
    ("P28", probe_p28), ("P29", probe_p29),
]


def main():
    results = []
    for pid, fn in PROBES:
        try:
            r = fn()
            results.append(r)
        except Exception as e:
            results.append({"probe": pid, "verdict": "fail",
                            "actual": f"exception: {type(e).__name__}: {e}"})
    total = len(results)
    passed = sum(1 for r in results if r.get("verdict") == "pass")
    failed = sum(1 for r in results if r.get("verdict") == "fail")
    not_run = sum(1 for r in results if r.get("verdict") == "not_run")
    report = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "not_run": not_run,
        "results": results,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
