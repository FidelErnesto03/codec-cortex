#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORTEX 0.1 → 0.2 migration module.

Transforms a 0.1 document to 0.2 slots format:
  - Changes format version
  - Derives slot contracts from field/pos contracts
  - Adds sigil-map
  - Rewrites attrs payloads to slots format
  - Transactinal: plan → verify → apply → verify → commit/rollback

Public API:
    migrate_inspect(source_path) -> dict
    migrate_plan(source_path, to_version, out_path) -> dict
    migrate_apply(plan_path, out_path) -> dict
    migrate_verify(source_path, out_path) -> dict
    migrate_rollback(plan_path) -> dict
"""

import os
import json
import hashlib
import shutil
import tempfile
from typing import Optional

from .scalars import Scalar


class MigrationError(Exception):
    pass


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_source(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write_atomic(path: str, content: str):
    dirname = os.path.dirname(path) or "."
    os.makedirs(dirname, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dirname, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        shutil.move(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def migrate_inspect(source_path: str) -> dict:
    from .dispatcher import parse_cortex

    if not os.path.exists(source_path):
        return {"status": "error", "message": f"Source not found: {source_path}"}
    try:
        src = _read_source(source_path)
        doc = parse_cortex(src)
    except Exception as e:
        code = getattr(e, "code", "PARSE_ERROR")
        return {"status": "error", "message": f"Parse failed: {code}: {e}"}

    if doc.cortex_version != "0.1":
        return {"status": "skip", "message": f"Document is already version {doc.cortex_version}"}

    symbols = []
    for s in doc.glossary.symbols:
        info = {"sigil": s.sigil, "label": s.label, "shape": s.shape}
        if s.shape == "attrs":
            field_names = [f.name for f in s.contract]
            info["fields"] = field_names
            info["slots"] = [f"{i+1}={f.name}:{f.type}{'?' if not f.required else ''}"
                             for i, f in enumerate(s.contract)]
        elif s.shape in ("attrs-pos", "relacion"):
            pos_names = [f.name for f in s.contract]
            info["positions"] = pos_names
            info["slots"] = [f"{i+1}={f.name}:{f.type}{'?' if not f.required else ''}"
                             for i, f in enumerate(s.contract)]
        elif s.shape in ("cuerpo", "bloque"):
            info["note"] = "no migration needed (body content)"
        symbols.append(info)

    return {
        "status": "ok",
        "version": doc.cortex_version,
        "capa": getattr(doc.glossary, "capa", None),
        "symbols": symbols,
        "symbol_count": len(doc.glossary.symbols),
        "section_count": len(doc.sections),
    }


def migrate_plan(source_path: str, to_version: str = "0.2",
                 out_path: Optional[str] = None) -> dict:
    if to_version != "0.2":
        return {"status": "error", "message": f"Unsupported target version: {to_version}"}

    inspect = migrate_inspect(source_path)
    if inspect.get("status") != "ok":
        return inspect

    source_hash = _sha256_file(source_path)
    plan = {
        "version": 1,
        "source_path": os.path.abspath(source_path),
        "source_hash": source_hash,
        "to_version": to_version,
        "inspect": inspect,
        "created_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
    }

    if out_path:
        plan_dir = os.path.dirname(out_path) or "."
        os.makedirs(plan_dir, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        return {"status": "ok", "plan_path": os.path.abspath(out_path),
                "plan": plan}

    return {"status": "ok", "plan": plan}


def migrate_apply(plan_path: str, out_path: Optional[str] = None) -> dict:
    if not os.path.exists(plan_path):
        return {"status": "error", "message": f"Plan not found: {plan_path}"}

    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)

    source_path = plan.get("source_path", "")
    if not source_path or not os.path.exists(source_path):
        return {"status": "error", "message": f"Source not found: {source_path}"}

    planned_hash = plan.get("source_hash", "")
    current_hash = _sha256_file(source_path)
    if current_hash != planned_hash:
        return {"status": "error", "message":
                f"Source hash changed since plan created "
                f"(planned={planned_hash[:16]}..., "
                f"actual={current_hash[:16]}...). "
                f"Re-run migrate_plan first."}

    from .dispatcher import parse_cortex, canonicalize

    try:
        src = _read_source(source_path)
        doc = parse_cortex(src)
    except Exception as e:
        code = getattr(e, "code", "PARSE_ERROR")
        return {"status": "error", "message": f"Parse failed: {code}: {e}"}

    if doc.cortex_version != "0.1":
        return {"status": "skip", "message":
                f"Document is already version {doc.cortex_version}"}

    migrated_src = _perform_migration(doc, src)
    result_path = out_path or source_path

    src_backup = source_path + ".bak"
    shutil.copy2(source_path, src_backup)

    try:
        _write_atomic(result_path, migrated_src)
    except Exception as e:
        shutil.move(src_backup, source_path)
        return {"status": "error", "message":
                f"Write failed, source restored: {e}"}

    try:
        verify = migrate_verify(source_path, result_path)
        if verify.get("status") in ("ok", "identical"):
            if os.path.exists(src_backup):
                os.unlink(src_backup)
            return {
                "status": "ok",
                "message": f"Migration applied to {result_path}",
                "result_path": os.path.abspath(result_path),
                "verify": verify,
            }
        else:
            shutil.move(src_backup, source_path)
            if result_path != source_path and os.path.exists(result_path):
                os.unlink(result_path)
            return {"status": "error", "message":
                    f"Verification failed after migration: "
                    f"{verify.get('message', '')}. Source restored."}
    except Exception as e:
        shutil.move(src_backup, source_path)
        if result_path != source_path and os.path.exists(result_path):
            os.unlink(result_path)
        return {"status": "error", "message":
                f"Verification exception: {e}. Source restored."}


def migrate_verify(source_path: str, migrated_path: str) -> dict:
    from .dispatcher import parse_cortex, canonicalize

    if not os.path.exists(source_path):
        return {"status": "error", "message": f"Source not found: {source_path}"}
    if not os.path.exists(migrated_path):
        return {"status": "error", "message":
                f"Migrated file not found: {migrated_path}"}

    try:
        src = _read_source(source_path)
        doc0 = parse_cortex(src)
    except Exception as e:
        code = getattr(e, "code", "PARSE_ERROR")
        return {"status": "error", "message":
                f"Source parse failed: {code}: {e}"}

    try:
        migrated = _read_source(migrated_path)
        doc1 = parse_cortex(migrated)
    except Exception as e:
        code = getattr(e, "code", "PARSE_ERROR")
        return {"status": "error", "message":
                f"Migrated parse failed: {code}: {e}"}

    if doc1.cortex_version != "0.2":
        return {"status": "error", "message":
                f"Migrated doc version is {doc1.cortex_version}, expected 0.2"}

    checks = []

    if len(doc0.sections) == len(doc1.sections):
        checks.append({"check": "section_count", "status": "pass"})
    else:
        checks.append({"check": "section_count", "status": "fail",
                        "expected": len(doc0.sections),
                        "actual": len(doc1.sections)})

    # Compare symbol count
    if len(doc0.glossary.symbols) == len(doc1.glossary.symbols):
        checks.append({"check": "symbol_count", "status": "pass"})
    else:
        checks.append({"check": "symbol_count", "status": "fail",
                        "expected": len(doc0.glossary.symbols),
                        "actual": len(doc1.glossary.symbols)})

    # Compare idea count per section
    all_ideas_match = True
    for i, (sec0, sec1) in enumerate(zip(doc0.sections, doc1.sections)):
        if len(sec0.ideas) != len(sec1.ideas):
            checks.append({"check": f"section_{i}_idea_count", "status": "fail",
                            "expected": len(sec0.ideas),
                            "actual": len(sec1.ideas)})
            all_ideas_match = False
            continue
        for j, (idea0, idea1) in enumerate(zip(sec0.ideas, sec1.ideas)):
            if idea0.symbol != idea1.symbol or idea0.name != idea1.name:
                checks.append({"check": f"s{i}_idea{j}_identity", "status": "fail",
                                "expected": f"{idea0.symbol}:{idea0.name}",
                                "actual": f"{idea1.symbol}:{idea1.name}"})
                all_ideas_match = False
                continue
            if idea0.shape == "cuerpo" or idea0.shape == "bloque":
                if idea0.payload[1] != idea1.payload[1]:
                    checks.append({"check": f"s{i}_idea{j}_body", "status": "fail"})
                    all_ideas_match = False
            elif idea0.shape in ("attrs", "attrs-pos", "relacion"):
                vals0 = []
                vals1 = []
                if idea0.payload[0] == "attrs":
                    for k, v in idea0.payload[1]:
                        val = v.value
                        if isinstance(val, list):
                            val = tuple(x.value if hasattr(x, 'value') else x for x in val)
                        vals0.append([k, val])
                if idea1.payload[0] == "slots":
                    from .slots import FieldValue
                    for fv in idea1.payload[1]:
                        val = fv.value.value
                        if isinstance(val, list):
                            val = tuple(x.value if hasattr(x, 'value') else x for x in val)
                        vals1.append([fv.name, val])
                elif idea1.payload[0] == "attrs":
                    for k, v in idea1.payload[1]:
                        val = v.value
                        if isinstance(val, list):
                            val = tuple(x.value if hasattr(x, 'value') else x for x in val)
                        vals1.append([k, val])
                vals0_set = set(tuple(x) for x in vals0)
                vals1_set = set(tuple(x) for x in vals1)
                if vals0_set and vals0_set != vals1_set:
                    checks.append({"check": f"s{i}_idea{j}_values", "status": "fail",
                                    "expected_values": vals0,
                                    "actual_values": vals1})
                    all_ideas_match = False

    if all_ideas_match:
        checks.append({"check": "idea_equivalence", "status": "pass"})

    all_pass = all(c.get("status") == "pass" for c in checks)
    return {
        "status": "ok" if all_pass else "verification_failed",
        "checks": checks,
        "version_original": doc0.cortex_version,
        "version_migrated": doc1.cortex_version,
    }


def migrate_rollback(plan_path: str) -> dict:
    if not os.path.exists(plan_path):
        return {"status": "error", "message": f"Plan not found: {plan_path}"}
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)

    source_path = plan.get("source_path", "")
    backup = source_path + ".bak"
    if not os.path.exists(backup):
        return {"status": "error", "message":
                f"No backup found at {backup}. Cannot rollback."}

    shutil.copy2(backup, source_path)
    os.unlink(backup)
    return {"status": "ok", "message": f"Rolled back {source_path} from backup"}


def _perform_migration(doc, source: str) -> str:
    gl = doc.glossary
    lines = []
    lines.append("$0:KERNEL")
    fmt_attrs = []
    for k, v in gl.format.attrs:
        if k == "cortex":
            fmt_attrs.append("cortex:0.2")
        else:
            fmt_attrs.append(f"{k}:{v.lexeme}")
    lines.append("$0:format{" + ",".join(fmt_attrs) + "}")

    can_slot = any(
        s.shape in ("attrs", "attrs-pos", "relacion") and not s.open
        for s in gl.symbols
    )
    if can_slot:
        lines.append(
            '$0:sigil-map{marker:"※",codepoint:"U+203B",base:1,'
            'syntax:"※N:valor",order:"ascending"}'
        )

    for e in gl.enums:
        vals_str = "|".join(e.values)
        lines.append(f'$0:enum_{e.name}{{values:"{vals_str}"}}')
    for m in gl.micros:
        ex = m.expand
        if " " in ex or not ex:
            lines.append(f'$0:micro_{m.token}{{expand:"{ex}"}}')
        else:
            lines.append(f'$0:micro_{m.token}{{expand:{ex}}}')
    for ns in gl.namespaces:
        parts = [f"{k}:{v.lexeme}" for k, v in ns.attrs]
        lines.append(f"$0:namespace_{ns.alias}{{{','.join(parts)}}}")
    for ext in gl.extensions:
        parts = [f"{k}:{v.lexeme}" for k, v in ext.attrs]
        lines.append(f"$0:extension_{ext.name}{{{','.join(parts)}}}")
    for md in gl.meta:
        parts = [f"{k}:{v.lexeme}" for k, v in md.attrs]
        line = f"$0:{md.name}{{{','.join(parts)}}}"
        if md.capa:
            line += f":{md.capa}"
        lines.append(line)

    for s in gl.symbols:
        qualified = f"{s.namespace}::{s.sigil}" if s.namespace else s.sigil
        attrs_parts = [f"type:{s.shape}"]

        use_slots = (
            s.shape in ("attrs", "attrs-pos", "relacion")
            and not s.open
            and can_slot
        )

        if use_slots:
            contract = s.contract
            slot_parts = []
            for i, f in enumerate(contract):
                slot_parts.append(
                    f"{i+1}={f.name}:{f.type}{'?' if not f.required else ''}"
                )
            slot_contract_str = "|".join(slot_parts)
            attrs_parts.append("encoding:slots")
            attrs_parts.append(f'slots:"{slot_contract_str}"')
        elif s.shape == "attrs" and s.contract:
            fields_parts = [
                f"{f.name}:{f.type}{'?' if not f.required else ''}"
                for f in s.contract
            ]
            attrs_parts.append(f'fields:"{"|".join(fields_parts)}"')
        elif s.shape in ("attrs-pos", "relacion") and s.contract:
            pos_parts = [
                f"{f.name}:{f.type}{'?' if not f.required else ''}"
                for f in s.contract
            ]
            attrs_parts.append(f'pos:"{"|".join(pos_parts)}"')

        for k, v in s.attrs:
            if k in ("type", "contract", "pos", "fields", "encoding"):
                continue
            attrs_parts.append(f"{k}:{v.lexeme}")

        if any(k == "open" for k, _ in s.attrs):
            open_val = next(v.lexeme for k, v in s.attrs if k == "open")
            attrs_parts.append(f"open:{open_val}")

        lines.append(f"{qualified}:{s.label}{{{','.join(attrs_parts)}}}")

    for sec in doc.sections:
        capa = getattr(sec, "capa", None)
        title = sec.title or f"Sección {sec.id}"
        if capa:
            lines.append(f"${sec.id}: {title}:{capa}")
        else:
            lines.append(f"${sec.id}: {title}")

        for idea in sec.ideas:
            qualified = f"{idea.namespace}::{idea.symbol}" if idea.namespace else idea.symbol
            sym = next((x for x in gl.symbols if x.sigil == idea.symbol), None)
            use_slots = (
                sym is not None
                and sym.shape in ("attrs", "attrs-pos", "relacion")
                and not sym.open
                and can_slot
            )

            if idea.payload and idea.payload[0] in ("cuerpo", "bloque"):
                body = idea.payload[1]
                if "\n" in body:
                    lines.append(f"{qualified}:{idea.name}{{")
                    for bl in body.split("\n"):
                        lines.append(bl)
                    lines.append("}")
                else:
                    lines.append(f"{qualified}:{idea.name}{{{body}}}")
            elif use_slots and sym and sym.contract:
                if idea.payload[0] in ("attrs-pos", "relacion"):
                    cells = idea.payload[1]
                    slot_parts = []
                    for i, f in enumerate(sym.contract):
                        v = cells[i] if i < len(cells) else None
                        if v is not None:
                            slot_parts.append(f"※{i+1}:{v.lexeme}")
                    lines.append(
                        f"{qualified}:{idea.name}{{{','.join(slot_parts)}}}"
                    )
                elif idea.payload[0] == "attrs":
                    pairs = idea.payload[1]
                    pair_map = {k: v for k, v in pairs}
                    slot_parts = []
                    for i, f in enumerate(sym.contract):
                        v = pair_map.get(f.name)
                        if v is not None:
                            slot_parts.append(f"※{i+1}:{v.lexeme}")
                    lines.append(
                        f"{qualified}:{idea.name}{{{','.join(slot_parts)}}}"
                    )
            elif idea.payload and idea.payload[0] in ("attrs-pos", "relacion"):
                cells = idea.payload[1]
                cells_str = "|".join(c.lexeme for c in cells)
                lines.append(f"{qualified}:{idea.name}|{cells_str}")
            elif idea.payload and idea.payload[0] == "attrs":
                pairs = idea.payload[1]
                pair_strs = [f"{k}:{v.lexeme}" for k, v in pairs]
                lines.append(f"{qualified}:{idea.name}{{{','.join(pair_strs)}}}")
            else:
                lines.append(f"{qualified}:{idea.name}")

    return "\n".join(lines) + "\n"


def main_cli(argv=None):
    import sys
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2:
        print("Usage: python3 -m codec_cortex.slotmigrate <command> <file> [options]",
              file=sys.stderr)
        print("Commands: inspect, plan, apply, verify, rollback", file=sys.stderr)
        return 2
    cmd = argv[0]
    if cmd == "inspect":
        result = migrate_inspect(argv[1])
    elif cmd == "plan":
        out_path = argv[2] if len(argv) > 2 else None
        result = migrate_plan(argv[1], out_path=out_path)
    elif cmd == "apply":
        out_path = argv[2] if len(argv) > 2 else None
        result = migrate_apply(argv[1], out_path)
    elif cmd == "verify":
        if len(argv) < 3:
            print("Usage: verify <source> <migrated>", file=sys.stderr)
            return 2
        result = migrate_verify(argv[1], argv[2])
    elif cmd == "rollback":
        result = migrate_rollback(argv[1])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        return 2
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") == "ok" else 1
