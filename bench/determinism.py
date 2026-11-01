"""T-1.4 — contraste de determinismo (CORTEX vs LLM).

CORTEX: varianza de hash = 0 (garantizado por D1, sin LLM).
LLM:    se mide la varianza sobre R repeticiones de la misma entrada; se espera > 0.

Este modulo NO llama al LLM: consume la serie de hashes crudos que produce el
orquestador (bench.run / sub-agentes) y calcula el veredicto. Asi el calculo
es determinista y auditable; solo la obtencion de la muestra usa el modelo.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"


def hash_series(series: list[str]) -> dict:
    h = [hashlib.sha256(s.encode("utf-8")).hexdigest() for s in series]
    uniq = sorted(set(h))
    return {"n": len(h), "unique": len(uniq), "variance": len(uniq) - 1, "digests": uniq}


def verdict(cortex_series: list[str], llm_series: list[str]) -> dict:
    c = hash_series(cortex_series)
    l = hash_series(llm_series)
    return {
        "id": "D6_determinism_contrast",
        "cortex": c,
        "llm": l,
        "pass": c["variance"] == 0 and l["variance"] > 0,
        "criterion": "CORTEX varianza=0 y LLM varianza>0",
    }


def cortex_repeats(source: str, times: int = 5) -> list[str]:
    """Serie CORTEX: re-parsear y re-canonicalizar la MISMA entrada `times` veces.

    No re-etiquetar los bytes con un indice: la repeticion debe venir de ejecutar
    el pipeline completo sobre la misma entrada, si no la varianza measures el
    error del harness y no la del formato.
    """
    from codec_cortex.dispatcher import canonicalize, parse_cortex

    runs = []
    for _ in range(times):
        runs.append(canonicalize(parse_cortex(source)))
    return runs


def save(raw_llm: list[str], raw_cortex: list[str]) -> dict:
    v = verdict(raw_cortex, raw_llm)
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "determinism.json").write_text(json.dumps(v, indent=2, ensure_ascii=False), encoding="utf-8")
    return v
