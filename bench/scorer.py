"""BLP-003 — Scorer mechanico de exactitud (Nivel B).

La mayoria de las preguntas del benchmark NexusCorp tienen una respuesta
OBJETIVA y UNICA (un nombre, un id, un numero). Eso permite puntuar por
comparacion exacta SIN LLM y SIN r rubrica subjetiva: no se necesita un
evaluador humano para verificar correct/incorrecto.

Solo las respuestas que exigen justificacion o sintesis (Q8) quedan fuera del
scorer mecanico y se marcan como `requires_human` (bloqueadas por Art. XII).

Criterio: una respuesta puntua 1 si contiene el valor exacto esperado
(comparacion insensible a mayusculas/espacios); 0 en caso contrario.
Corte parcial: `partial` cuando el valor principal acierta y falta el accesorio.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

QUESTIONS = json.loads((Path(__file__).resolve().parent / "formats/questions.json").read_text(encoding="utf-8"))

# Respuestas exactas verificadas contra el corpus (NexusCorp, 40 items, §4 del benchmark)
GOLD: dict[str, dict] = {
    "Q1": {"must": ["Marco_Silva"], "any": ["SRE Lead"], "desc": "responsable de Nebula"},
    "Q2": {"must": ["R01", "R04"], "desc": "riesgos con impacto critico (deadline mas cercano = Atlas 2026-07-30, ya vencido)"},
    "Q3": {"must": ["ComplianceAudit", "OAuth2", "AR02"], "desc": "proveedor I-004 + decision AR02"},
    "Q4": {"must": ["Sofía_Márquez", "Daniel_Ortega"], "any": ["Aisha_Okafor"], "desc": ">1 proyecto simultaneo"},
    "Q5": {"must": ["R01"], "desc": "riesgo critico de mayor probabilidad: R01 0.35 vs R04 0.20"},
    "Q6": {"must": ["AR02", "I-004", "OAuth2"], "desc": "incidente mas reciente I-004 -> AR02"},
    "Q7": {"must": ["R01", "Horizon", "Nebula", "CloudShield"], "any": ["R03"], "desc": "riesgo multi-proyecto"},
    "Q8": {"requires_human": True, "desc": "sintesis justificada (criterio cualitativo)"},
}

FOLDERS = {"cortex": "cortex", "json": "json", "yaml": "yaml", "markdown": "md", "plaintext": "txt", "xml": "xml"}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[\s_\-]+", " ", s).strip().lower()


def score(question_id: str, answer: str) -> dict:
    spec = GOLD.get(question_id)
    if spec is None:
        return {"q": question_id, "status": "sin_gold", "score": 0.0}
    if spec.get("requires_human"):
        return {"q": question_id, "status": "requires_human", "score": None, "desc": spec["desc"]}

    a = norm(answer)
    if not a:
        return {"q": question_id, "status": "vacia", "score": 0.0, "desc": spec["desc"]}

    must = [norm(m) for m in spec.get("must", [])]
    any_ = [norm(x) for x in spec.get("any", [])]

    hit_must = [m for m in must if m in a]
    hit_any = [x for x in any_ if x in a]
    total = len(must) + len(any_)
    got = len(hit_must) + len(hit_any)

    if not must:
        status = "n/a"
        score = 0.0
    elif got == total:
        status, score = "completo", 1.0
    elif hit_must and len(hit_must) == len(must):
        status, score = "parcial_any", 0.75
    elif hit_must:
        status, score = "parcial", round(len(hit_must) / len(must), 3)
    else:
        status, score = "incorrecto", 0.0

    return {
        "q": question_id,
        "status": status,
        "score": score,
        "must_found": hit_must,
        "any_found": hit_any,
        "desc": spec["desc"],
    }


def score_cell(answer_block: str) -> dict:
    """answer_block: texto con las respuestas, idealmente 'Q1: ... Q2: ...'."""
    out = {}
    for q in QUESTIONS:
        qid = q["id"]
        m = re.search(rf"{qid}\s*[:.\)-]\s*(.*?)(?=\s*Q[1-8]\s*[:.\)-]|\Z)", answer_block, re.S | re.I)
        out[qid] = score(qid, m.group(1) if m else "")
    scored = [v["score"] for v in out.values() if isinstance(v.get("score"), (int, float))]
    return {"per_question": out, "n_scored": len(scored), "mean": round(sum(scored) / len(scored), 4) if scored else 0.0}