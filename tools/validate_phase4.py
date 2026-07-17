#!/usr/bin/env python3
"""Validador de integridad de la entrega Fase 4.

No certifica independencia. Verifica que especificación, corpus, vectores,
reportes y schemas incluidos sean internamente coherentes y reproducibles.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from hcortex_oracle import (  # noqa: E402
    compile_hcortex,
    logical_normalize,
    render_cortex,
    render_hcortex,
    render_readable,
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_json_schema(instance, schema_path: Path) -> None:
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError("jsonschema es requerido para validar los contratos JSON") from exc
    jsonschema.Draft202012Validator(load_json(schema_path)).validate(instance)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=str(HERE.parent))
    args = ap.parse_args()
    root = Path(args.root).resolve()

    vector_path = root / "vectors/roundtrip-vectors.json"
    data = load_json(vector_path)
    vector_schema = root / "schemas/hcortex-vector.schema.json"
    loss_schema = root / "schemas/loss-report.schema.json"
    metadata_schema = root / "schemas/hcortex-metadata.schema.json"
    for vector_name in ("cortex-to-hcortex-vectors.json", "hcortex-to-cortex-vectors.json", "roundtrip-vectors.json"):
        validate_json_schema(load_json(root / "vectors" / vector_name), vector_schema)
    if data["count"] != len(data["vectors"]):
        raise AssertionError("count de vectores no coincide con el inventario")

    results = {
        "phase": "4",
        "hcortex": "0.1",
        "cortex": "0.1",
        "canonical_cases": 0,
        "compile_pass": 0,
        "ast_roundtrip_pass": 0,
        "cortex_roundtrip_pass": 0,
        "hcortex_idempotence_pass": 0,
        "hash_pass": 0,
        "canonical_loss_report_pass": 0,
        "readable_loss_report_pass": 0,
        "invalid_cases": 0,
        "invalid_diagnostic_pass": 0,
        "view_dependencies_in_gate": 0,
        "failures": [],
    }

    for v in data["vectors"]:
        results["canonical_cases"] += 1
        cid = v["id"]
        try:
            cortex = (root / v["cortex"]).read_text(encoding="utf-8")
            hc = (root / v["hcortex_canonical"]).read_text(encoding="utf-8")
            if "cortex.view" in cortex:
                results["view_dependencies_in_gate"] += 1
            readable = (root / v["hcortex_readable"]).read_text(encoding="utf-8")
            expected_ast = load_json(root / v["ast"])
            compiled = compile_hcortex(hc)
            results["compile_pass"] += 1

            normalized_compiled = json.loads(json.dumps(logical_normalize(compiled), ensure_ascii=False))
            if normalized_compiled != expected_ast:
                raise AssertionError("AST recompilado distinto del golden")
            results["ast_roundtrip_pass"] += 1

            back = render_cortex(compiled)
            if back != cortex:
                raise AssertionError("CORTEX recompilado no es byte-identical")
            results["cortex_roundtrip_pass"] += 1

            hc2 = render_hcortex(compiled)
            if hc2 != hc:
                raise AssertionError("HCORTEX-CANONICAL no es idempotente")
            results["hcortex_idempotence_pass"] += 1

            if sha256_text(cortex) != v["cortex_sha256"]:
                raise AssertionError("hash CORTEX no coincide")
            if sha256_text(hc) != v["hcortex_sha256"]:
                raise AssertionError("hash HCORTEX no coincide")
            if sha256_text(back) != v["roundtrip_cortex_sha256"]:
                raise AssertionError("hash roundtrip no coincide")
            results["hash_pass"] += 1

            creport = load_json(root / v["canonical_loss_report"])
            validate_json_schema(creport, loss_schema)
            if not creport["reversible"] or creport["losses"]:
                raise AssertionError("CANONICAL declara pérdida")
            if creport["source_sha256"] != sha256_text(cortex) or creport["target_sha256"] != sha256_text(hc):
                raise AssertionError("hashes del reporte CANONICAL no coinciden")
            results["canonical_loss_report_pass"] += 1

            rreport = load_json(root / v["readable_loss_report"])
            validate_json_schema(rreport, loss_schema)
            if rreport["reversible"] or not rreport["losses"]:
                raise AssertionError("READABLE no declara pérdida explícita")
            if render_readable(compiled) != readable:
                raise AssertionError("READABLE no es reproducible")
            results["readable_loss_report_pass"] += 1

            # Validate metadata objects exposed by the canonical document.
            first = hc.splitlines()[0]
            top = json.loads(first[len("<!-- hcortex "):-len(" -->")])
            validate_json_schema({"kind": "document", **top}, metadata_schema)
            for line in hc.splitlines():
                if line.startswith("<!-- cortex-entry "):
                    entry = json.loads(line[len("<!-- cortex-entry "):-len(" -->")])
                    validate_json_schema({"kind": "entry", **entry}, metadata_schema)
        except Exception as exc:  # keep complete audit output
            results["failures"].append({"case": cid, "error": f"{type(exc).__name__}: {exc}"})

    invalid_dir = root / "corpus/invalid"
    for path in sorted(invalid_dir.glob("*.md")):
        results["invalid_cases"] += 1
        expected = load_json(root / "corpus/expected-diagnostics" / f"{path.stem}.json")
        try:
            compile_hcortex(path.read_text(encoding="utf-8"))
            results["failures"].append({"case": path.stem, "error": "documento inválido aceptado"})
        except ValueError as exc:
            if str(exc) == expected["required_code"]:
                results["invalid_diagnostic_pass"] += 1
            else:
                results["failures"].append({"case": path.stem, "error": f"diagnóstico {exc}, esperado {expected['required_code']}"})
        except Exception as exc:
            results["failures"].append({"case": path.stem, "error": f"excepción no contractual: {type(exc).__name__}: {exc}"})

    expected_count = data["count"]
    required_equal = [
        "compile_pass", "ast_roundtrip_pass", "cortex_roundtrip_pass",
        "hcortex_idempotence_pass", "hash_pass", "canonical_loss_report_pass",
        "readable_loss_report_pass",
    ]
    ok = not results["failures"] and all(results[k] == expected_count for k in required_equal)
    ok = ok and results["invalid_diagnostic_pass"] == results["invalid_cases"]
    ok = ok and results["view_dependencies_in_gate"] == 0
    results["status"] = "PASS" if ok else "FAIL"

    (root / "validation-results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
