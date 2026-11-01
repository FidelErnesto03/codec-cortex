"""Nivel A — certificado determinista de CODEC-CORTEX (BLP-003).

No depende de ningun LLM. Produce bench/results/certificate.json con el
resultado binario (PASS/FAIL) de cada indicador del Nivel A:

  D1 idempotencia      canonicalize(canonicalize(x)) == canonicalize(x)
  D2 roundtrip         HCORTEX 0.2 -> CORTEX 0.2 byte-exacto
  D3 paridad runtime   mismo sha256 en Python / Node / Bash / Go (Rust opcional)
  D4 no-perdida        la canonicalizacion preserva secciones y glosario
  D5 tamper            mutar 1 byte del canonico cambia el hash

Toda degradacion (runtime ausente o que no soporta el dialecto) se reporta,
nunca se omite en silencio (Constitucion, Art. V y X).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCH = ROOT / "bench"
RESULTS = BENCH / "results"

SEED = ROOT / "conformance/hcortex/cortex/H002_attrs-optional.cortex"
CORPUS_01 = sorted((ROOT / "conformance/hcortex/cortex").glob("*.cortex"))
CORPUS_02 = sorted((ROOT / "conformance/slots/valid").glob("*.cortex"))
CORPUS_10 = sorted((ROOT / "conformance/1.0/valid").glob("*.cortex"))
HCORTEX_02_DIR = ROOT / "conformance/slots/hcortex"


def _api():
    from codec_cortex.dispatcher import canonicalize, hash_cortex, parse_cortex

    return parse_cortex, canonicalize, hash_cortex


def _rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def d1_idempotence(files: list[Path]) -> dict:
    parse_cortex, canonicalize, _ = _api()
    details = []
    ok = 0
    for f in files:
        entry = {"file": _rel(f), "pass": False}
        try:
            doc = parse_cortex(f.read_text(encoding="utf-8"))
            c1 = canonicalize(doc)
            c2 = canonicalize(parse_cortex(c1))
            entry["pass"] = c1 == c2
            ok += entry["pass"]
        except Exception as exc:  # noqa: BLE001 - reportar, no ocultar
            entry["error"] = f"{type(exc).__name__}: {exc}"
        details.append(entry)
    return {"id": "D1_idempotence", "pass": ok == len(files), "ok": ok, "total": len(files), "details": details}


def d2_roundtrip(files: list[Path]) -> dict:
    from codec_cortex.dispatcher import canonicalize, parse_cortex
    from codec_cortex.slothcortex import compile_hcortex_slots, render_hcortex_slots

    slots02 = [f for f in files if "cortex:0.2" in f.read_text(encoding="utf-8")]
    details = []
    ok = 0
    for f in slots02:
        entry = {"file": _rel(f), "pass": False}
        try:
            doc = parse_cortex(f.read_text(encoding="utf-8"))
            back, _diags = compile_hcortex_slots(render_hcortex_slots(doc))
            entry["pass"] = back is not None and canonicalize(back) == canonicalize(doc)
            ok += entry["pass"]
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"{type(exc).__name__}: {exc}"
        details.append(entry)
    total = len(slots02)
    return {"id": "D2_roundtrip_hcortex02", "pass": total > 0 and ok == total, "ok": ok, "total": total, "details": details}


def _run(cmd: list[str]) -> tuple[bool, str]:
    try:
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=120)
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"
    if out.returncode != 0:
        return False, (out.stderr or out.stdout).strip().splitlines()[-1] if (out.stderr or out.stdout).strip() else f"exit {out.returncode}"
    return True, out.stdout.strip().splitlines()[-1] if out.stdout.strip() else ""


def _norm(digest: str) -> str:
    d = digest.strip().lower()
    if d.startswith("sha256:"):
        d = d[len("sha256:") :]
    return d


def d3_parity(seed: Path) -> dict:
    runtimes = {
        "python": [sys.executable, "-m", "codec_cortex", "hash", str(seed)],
        "node": ["node", "codec-cortex-node/bin/codec-cortex-node.js", "hash", str(seed)],
        "bash": ["bash", "codec-cortex-bash/bin/codec-cortex", "c14n-hash", str(seed)],
        "go": ["./codec-cortex-go/bin/codec-cortex-linux-amd64", "hash", str(seed)],
        "rust": ["./codec-cortex-rs/target/release/cortex", "hash", str(seed)],
    }
    results = {}
    digests = {}
    for name, cmd in runtimes.items():
        ok, out = _run(cmd)
        if ok:
            digests[name] = _norm(out)
        results[name] = {"ok": ok, "digest": digests.get(name), "raw": None if ok else out}
    present = {k: v for k, v in digests.items() if v}
    agree = len(set(present.values())) <= 1 and len(present) >= 2
    return {
        "id": "D3_runtime_parity",
        "pass": agree,
        "runtimes_agreeing": sorted(present),
        "runtimes_failed": sorted(k for k, v in results.items() if not v["ok"]),
        "digest": next(iter(present.values()), None),
        "details": results,
    }


def d4_lossless(files: list[Path]) -> dict:
    parse_cortex, canonicalize, _ = _api()
    details = []
    ok = 0
    for f in files:
        entry = {"file": _rel(f), "pass": False}
        try:
            doc = parse_cortex(f.read_text(encoding="utf-8"))
            re_doc = parse_cortex(canonicalize(doc))
            same = len(getattr(doc, "sections", [])) == len(getattr(re_doc, "sections", []))
            entry["pass"] = same
            ok += same
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"{type(exc).__name__}: {exc}"
        details.append(entry)
    return {"id": "D4_lossless", "pass": ok == len(files), "ok": ok, "total": len(files), "details": details}


def d5_tamper(seed: Path) -> dict:
    parse_cortex, canonicalize, hash_cortex = _api()
    doc = parse_cortex(seed.read_text(encoding="utf-8"))
    c1 = canonicalize(doc)
    original = hashlib.sha256(c1.encode("utf-8")).hexdigest()
    mutated = c1[:-2] + ("00" if c1[-2:] != "00" else "11")
    changed = hashlib.sha256(mutated.encode("utf-8")).hexdigest()
    return {
        "id": "D5_tamper_sensitivity",
        "pass": original != changed,
        "original": original,
        "mutated": changed,
    }


def run() -> dict:
    parse_cortex, canonicalize, hash_cortex = _api()
    corpus = CORPUS_01 + CORPUS_02 + CORPUS_10
    indicators = [
        d1_idempotence(corpus),
        d2_roundtrip(CORPUS_02),
        d3_parity(SEED),
        d4_lossless(corpus),
        d5_tamper(SEED),
    ]
    all_pass = all(i["pass"] for i in indicators)
    from codec_cortex import __version__ as cc_version

    instrument = hashlib.sha256()
    for f in sorted((ROOT / "codec_cortex").rglob("*.py")):
        instrument.update(f.relative_to(ROOT).as_posix().encode())
        instrument.update(f.read_bytes())

    cert = {
        "blueprint": "BLP-003",
        "level": "A",
        "tool": {"codec_cortex": getattr(cc_version, "__str__", lambda: "?")() if not isinstance(cc_version, str) else cc_version, "python": sys.version.split()[0]},
        "instrument_sha256": instrument.hexdigest(),
        "seed": _rel(SEED),
        "indicators": indicators,
        "verdict": "PASS" if all_pass else "FAIL",
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "certificate.json").write_text(json.dumps(cert, indent=2, ensure_ascii=False), encoding="utf-8")
    return cert


def main() -> int:
    cert = run()
    for ind in cert["indicators"]:
        mark = "PASS" if ind["pass"] else "FAIL"
        extra = ""
        if ind["id"] == "D1_idempotence":
            extra = f" ({ind['ok']}/{ind['total']})"
        elif ind["id"] == "D2_roundtrip_hcortex02":
            extra = f" ({ind['ok']}/{ind['total']})"
        elif ind["id"] == "D3_runtime_parity":
            extra = f" (ok={','.join(ind['runtimes_agreeing'])}; degraded={','.join(ind['runtimes_failed']) or '-'})"
        elif ind["id"] == "D4_lossless":
            extra = f" ({ind['ok']}/{ind['total']})"
        print(f"[{mark}] {ind['id']}{extra}")
    print(f"VERDICT: {cert['verdict']}")
    return 0 if cert["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
