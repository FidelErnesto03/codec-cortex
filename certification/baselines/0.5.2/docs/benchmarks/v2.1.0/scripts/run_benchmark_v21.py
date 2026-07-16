#!/usr/bin/env python3
"""
Harness principal del benchmark CODEC-CORTEX v2.0.0.

Diferencias vs v1.0.0:
- CLI: v2.4.0 (bidireccional CORTEX ⇄ HCORTEX, VIEW directives, v2-* commands)
- Métodos nuevos: cortex_priority_pack, cortex_canonical
- Métricas nuevas: VIEW_coverage, reversibility_rate, bidir_equivalence, loss_explained_count
- Comparación v1 vs v2 para análisis de progresión

Salida:
- runs/scored_tasks.csv
- runs/summary_tasks.csv
- runs/scenario_results.json
- runs/derived_metrics.json
- runs/v1_vs_v2_comparison.json
- runs/method_results.json
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE = Path("/home/z/my-project/download/benchmark-cortex-v21")
SRC = BASE / "corpus" / "source"
RUNS = BASE / "runs"
RUNS.mkdir(parents=True, exist_ok=True)

PYTHON = "/home/z/.venv/bin/python"
CORTEX_CLI = [PYTHON, "-m", "cortex"]

# Version info
BENCHMARK_VERSION = "2.1.0"
CODEC_CORTEX_VERSION = "0.3.2"
CLI_VERSION = "0.3.2"
HARNESS_VERSION = "2.1.0"

# ---------------------------------------------------------------------------
# Tokenizer proxy (aproximacion TikToken-clike para espanol + ingles)
# ---------------------------------------------------------------------------

def count_tokens(text: str, mode: str = "prose") -> int:
    """Proxy de tokens. Alineado con rangos empiricos GPT-style para ES/EN."""
    if not text:
        return 0
    chars = len(text)
    if mode == "cortex":
        return max(1, int(chars / 3.5))
    elif mode == "json":
        return max(1, int(chars / 3.8))
    elif mode == "yaml":
        return max(1, int(chars / 3.7))
    elif mode == "markdown":
        return max(1, int(chars / 3.6))
    else:
        return max(1, int(chars / 4.0))


# ---------------------------------------------------------------------------
# Carga del corpus
# ---------------------------------------------------------------------------

def load_corpus() -> List[Dict]:
    manifest = json.loads((BASE / "corpus" / "normalized" / "corpus_manifest.json").read_text())
    cases = []
    for cmeta in manifest["cases"]:
        cid = cmeta["case_id"]
        case = {
            "case_id": cid,
            "domain": cmeta["domain"],
            "purpose": cmeta["purpose"],
            "restrictions": cmeta["restrictions"],
            "risks": cmeta["risks"],
            "decisions": cmeta["decisions"],
        }
        case["cortex"] = (SRC / f"{cid}.cortex").read_text()
        case["raw_prose"] = (SRC / f"{cid}.raw.md").read_text()
        case["markdown"] = (SRC / f"{cid}.md").read_text()
        case["json"] = (SRC / f"{cid}.json").read_text()
        case["yaml"] = (SRC / f"{cid}.yaml").read_text()
        cases.append(case)
    return cases


# ---------------------------------------------------------------------------
# Definicion de metodos v2.0.0
# ---------------------------------------------------------------------------

@dataclass
class MethodSpec:
    method_id: str
    name: str
    family: str
    description: str
    config: Dict = field(default_factory=dict)
    is_v2: bool = False  # True if uses v2-* commands


METHODS: List[MethodSpec] = [
    # Baselines pasivos posicionales (sin cambios)
    MethodSpec("recent_tail_raw", "Recent Tail Raw", "passive_positional",
               "Toma los ultimos N tokens del raw prose (cola reciente). Sin comprension de contenido.",
               {"source": "raw_prose", "selector": "tail"}),
    MethodSpec("head_tail_raw", "Head + Tail Raw", "passive_positional",
               "Toma cabecera + cola del raw prose con proporcion 25/75.",
               {"source": "raw_prose", "selector": "head_tail", "head_ratio": 0.25}),
    MethodSpec("head_json", "Head JSON", "passive_positional",
               "Toma los primeros N tokens del JSON.",
               {"source": "json", "selector": "head"}),
    MethodSpec("head_markdown_summary", "Head Markdown Summary", "passive_positional",
               "Toma los primeros N tokens del markdown estructurado.",
               {"source": "markdown", "selector": "head"}),
    # Baseline semantico
    MethodSpec("semantic_field_pack", "Semantic Field Pack", "passive_semantic",
               "Selecciona entradas por perfil semantico general: identity, constraints, focus, objective.",
               {"source": "cortex", "selector": "semantic_pack"}),
    MethodSpec("keyword_retrieval_raw", "Keyword Retrieval Raw", "query_dependent",
               "BM25-like: rankea parrafos de raw prose por coincidencia con la pregunta + gold terms.",
               {"source": "raw_prose", "selector": "bm25"}),
    # CODEC-CORTEX v1 (CLI legacy render --profile)
    MethodSpec("cortex_priority_pack_v1", "CORTEX PP v1 (CLI v1.x render)", "cortex_v1",
               "Seleccion por prioridad cognitiva P0->P5 usando CLI v1.x render --profile.",
               {"source": "cortex", "selector": "cortex_cli_v1", "use_cli": True}),
    # CODEC-CORTEX v2 (NEW: usa v2-convert que produce HCORTEX con VIEW directives)
    MethodSpec("cortex_priority_pack", "CORTEX v2 PP (CLI v0.3.2 convert (canonical))", "cortex_v2",
               "v2.0.0: usa v2-convert --from cortex --to hcortex con perfiles y VIEW directives.",
               {"source": "cortex", "selector": "cortex_v2_convert", "use_cli": True}, is_v2=True),
    # CODEC-CORTEX v2 canonical (NEW: canonicalize --preserve primero, luego render)
    MethodSpec("cortex_canonical", "CORTEX v2 Canonical (normalize + render)", "cortex_v2",
               "v2.0.0: canonicalize --preserve seguido de v2-convert. Produces normalized HCORTEX.",
               {"source": "cortex", "selector": "cortex_canonical", "use_cli": True}, is_v2=True),
    # Ablations (sin cambios)
    MethodSpec("cortex_ablation_no_P0", "Ablation: no P0 priority", "cortex_v1",
               "Elimina prioridad P0 (FCS, OBJ, CNST, STP tratados como P5). Mide contribucion de P0.",
               {"source": "cortex", "selector": "cortex_ablation_no_P0", "use_cli": False}),
    MethodSpec("cortex_ablation_no_temporal", "Ablation: no temporal", "cortex_v1",
               "Elimina distincion current/planned/future. Mide contribucion del scope temporal.",
               {"source": "cortex", "selector": "cortex_ablation_no_temporal", "use_cli": False}),
]


# ---------------------------------------------------------------------------
# Generacion de tareas (sin cambios vs v1.0.0)
# ---------------------------------------------------------------------------

@dataclass
class Task:
    task_id: str
    case_id: str
    scenario_id: str
    task_type: str
    question: str
    gold_answer: str
    expected_terms: List[str]
    forbidden_terms: List[str] = field(default_factory=list)
    gold_decision: Optional[str] = None
    required_sources: List[str] = field(default_factory=list)
    priority_scope: List[str] = field(default_factory=lambda: ["P0", "P1"])
    temporal_scope: str = "current"
    severity: str = "normal"
    rationale: str = ""


def build_tasks_for_case(case: Dict) -> List[Task]:
    cid = case["case_id"]
    tasks = []
    tasks.append(Task(
        task_id=f"T-{cid}-QA-01",
        case_id=cid, scenario_id="full", task_type="qa",
        question="Cual es el foco actual de esta operacion?",
        gold_answer=case["cortex"].split('FCS:primary{what:"')[1].split('"')[0] if 'FCS:primary{what:"' in case["cortex"] else "",
        expected_terms=case["cortex"].split('FCS:primary{what:"')[1].split('"')[0].lower().split()[:3] if 'FCS:primary{what:"' in case["cortex"] else [],
        required_sources=["FCS"], rationale="Verifica preservacion del foco operativo."))
    tasks.append(Task(
        task_id=f"T-{cid}-QA-02",
        case_id=cid, scenario_id="full", task_type="qa",
        question="Cual es el objetivo activo?",
        gold_answer=case["cortex"].split('OBJ:')[1].split('{goal:"')[1].split('"')[0] if 'OBJ:' in case["cortex"] and '{goal:"' in case["cortex"] else "",
        expected_terms=case["cortex"].split('OBJ:')[1].split('{goal:"')[1].split('"')[0].lower().split()[:3] if 'OBJ:' in case["cortex"] and '{goal:"' in case["cortex"] else [],
        required_sources=["OBJ"], rationale="Verifica preservacion del objetivo."))
    cnst_match = re.search(r'CNST:(\w+)\{[^}]*severity:"blocking"[^}]*\}', case["cortex"])
    if cnst_match:
        cnst_name = cnst_match.group(1)
        tasks.append(Task(
            task_id=f"T-{cid}-DEC-01",
            case_id=cid, scenario_id="full", task_type="decision",
            question=f"La operacion tiene alguna restriccion bloqueante ({cnst_name})?",
            gold_answer=f"Si: {cnst_name} es blocking",
            expected_terms=[cnst_name.lower(), "blocking"],
            gold_decision="block", required_sources=["CNST"],
            rationale="Verifica conservacion de constraints blocking."))
    if "REF:" in case["cortex"]:
        ref_match = re.search(r'REF:(\w+)\{[^}]*\}', case["cortex"])
        if ref_match:
            ref_name = ref_match.group(1)
            tasks.append(Task(
                task_id=f"T-{cid}-TRC-01",
                case_id=cid, scenario_id="full", task_type="traceability",
                question=f"Cual es la referencia de origen disponible ({ref_name})?",
                gold_answer=ref_name, expected_terms=[ref_name.lower()],
                required_sources=["REF"], rationale="Verifica trazabilidad de fuente."))
    if "CLAIM:" in case["cortex"]:
        claim_match = re.search(r'CLAIM:(\w+)\{[^}]*statement:"([^"]+)"', case["cortex"])
        if claim_match:
            claim_name = claim_match.group(1)
            statement = claim_match.group(2)
            tasks.append(Task(
                task_id=f"T-{cid}-SAF-01",
                case_id=cid, scenario_id="full", task_type="safety",
                question=f"Esta afirmacion esta soportada por evidencia: '{statement[:60]}...'?",
                gold_answer=f"Si: {claim_name} tiene evidence",
                expected_terms=[claim_name.lower()],
                forbidden_terms=["no soportado", "sin evidencia", "inventado"],
                required_sources=["CLAIM"],
                rationale="Verifica que claims soportados no se supriman."))
    return tasks


# ---------------------------------------------------------------------------
# Escenarios (sin cambios vs v1.0.0)
# ---------------------------------------------------------------------------

def scenario_full(case, source_text, budget): return source_text

def scenario_reduced_window(case, source_text, budget):
    chars = int(budget * 3.6)
    return source_text[:chars]

def scenario_middle_work_adversarial(case, source_text, budget):
    noise_pre = "Contexto adicional. " * 80
    noise_post = "Mas detalle historico. " * 80
    fcs_match = re.search(r'FCS:primary\{what:"([^"]+)"', case["cortex"])
    critical = fcs_match.group(1) if fcs_match else "Foco operacional critico"
    return noise_pre + " " + critical + " " + noise_post + " " + source_text[:int(budget * 1.5)]

def scenario_stale_state_conflict(case, source_text, budget):
    stale = ("ESTADO ANTERIOR (OBSOLETO): El objetivo anterior era migrar a v1.0 (status=done). "
             "ESTADO PREVIO (OBSOLETO): El foco anterior era desplegar en staging (status=done). ")
    return stale + source_text

def scenario_blocking_constraint_survival(case, source_text, budget):
    extra = ("CNST:emergency_stop{rule:'accion destructiva requiere aprobacion del CISO', severity:'blocking', survive:'min'} "
             "CNST:data_residency{rule:'datos sensibles no pueden salir de la region EU', severity:'blocking', survive:'min'} ")
    return extra + source_text

def scenario_unsupported_claim_suppression(case, source_text, budget):
    unsupported = ("HIPOTESIS NO VERIFICADA: se especula que el sistema podria alcanzar 99.99% uptime con esta config. "
                   "AFIRMACION TENTATIVA: posiblemente el rendimiento mejore un 200%. "
                   "CLAIM NO SOPORTADO: garantia implicita de cero fallos. ")
    return unsupported + source_text

def scenario_corrupted_memory_tolerance(case, source_text, budget):
    corrupted = ("}}}{invalid syntax line\nFCS:broken{what:}\n"
                 "OBJ:missing_brace{goal:\"unbalanced\n"
                 "RANDOM_NOISE_LINE_WITHOUT_STRUCTURE_XJ7K2\n@@@!!!###\n")
    return corrupted + source_text

def scenario_multi_instance_sigil(case, source_text, budget):
    multi = ("FCS:primary{what:\"foco principal actual\", priority:\"high\"} "
             "FCS:secondary{what:\"foco secundario\", priority:\"medium\"} "
             "FCS:tertiary{what:\"foco terciario\", priority:\"low\"} "
             "OBJ:primary{goal:\"objetivo principal\"} "
             "OBJ:secondary{goal:\"objetivo secundario\"} "
             "OBJ:stretch{goal:\"objetivo ambicioso\"} ")
    return multi + source_text


SCENARIOS = [
    ("full", scenario_full, None),
    ("reduced_window_512", scenario_reduced_window, 512),
    ("reduced_window_1024", scenario_reduced_window, 1024),
    ("reduced_window_2048", scenario_reduced_window, 2048),
    ("reduced_window_4096", scenario_reduced_window, 4096),
    ("middle_work_adversarial", scenario_middle_work_adversarial, 1024),
    ("stale_state_conflict", scenario_stale_state_conflict, 2048),
    ("blocking_constraint_survival", scenario_blocking_constraint_survival, 2048),
    ("unsupported_claim_suppression", scenario_unsupported_claim_suppression, 2048),
    ("corrupted_memory_tolerance", scenario_corrupted_memory_tolerance, 2048),
    ("multi_instance_sigil", scenario_multi_instance_sigil, 2048),
]


# ---------------------------------------------------------------------------
# Cache de renders HCORTEX
# ---------------------------------------------------------------------------

_HC_CACHE_V1: Dict[Tuple[str, str], str] = {}
_HC_CACHE_V2: Dict[Tuple[str, str], str] = {}
_V2_VIEW_INFO: Dict[str, Dict] = {}  # case_id -> v2-verify-view info


def _get_hcortex_v1(case_id: str, profile: str) -> str:
    """Render via CLI v1.x render --profile (legacy)."""
    key = (case_id, profile)
    if key in _HC_CACHE_V1:
        return _HC_CACHE_V1[key]
    cortex_path = SRC / f"{case_id}.cortex"
    tmp_out = f"/tmp/v2_bench_render_v1_{case_id}_{profile}.md"
    try:
        subprocess.run(
            CORTEX_CLI + ["render", str(cortex_path), "--mode", "read",
                          "--profile", profile, "--out", tmp_out],
            capture_output=True, text=True, timeout=15,
        )
        rendered = Path(tmp_out).read_text() if os.path.exists(tmp_out) else cortex_path.read_text()
    except Exception:
        rendered = cortex_path.read_text()
    _HC_CACHE_V1[key] = rendered
    return rendered


def _get_hcortex_v2(case_id: str, profile: str) -> str:
    """Render via CLI v0.3.2 `convert` (canonical name, was v2-convert).

    v2.1.0: The corpus has been migrated to include VIEW directives, so
    `convert` now produces substantial HCORTEX output (~4-5 KB per case).
    The fallback to v1 render is kept as a safety net but should rarely
    trigger.

    v2.0.0 finding: v2-convert required VIEW directives to produce
    meaningful HCORTEX output. v2.1.0 fixes this by migrating the corpus.
    """
    key = (case_id, profile)
    if key in _HC_CACHE_V2:
        return _HC_CACHE_V2[key]
    cortex_path = SRC / f"{case_id}.cortex"
    tmp_out = f"/tmp/v21_bench_convert_{case_id}_{profile}.md"
    try:
        subprocess.run(
            CORTEX_CLI + ["convert", "--from", "cortex", "--to", "hcortex",
                          str(cortex_path), "--out", tmp_out],
            capture_output=True, text=True, timeout=15,
        )
        if os.path.exists(tmp_out):
            rendered = Path(tmp_out).read_text()
            # Check if output is substantial (>500 bytes indicates real content)
            if len(rendered) < 500:
                # Fallback: use v1 render --profile (legacy) — safety net
                rendered = _get_hcortex_v1(case_id, profile)
        else:
            rendered = _get_hcortex_v1(case_id, profile)
    except Exception:
        rendered = _get_hcortex_v1(case_id, profile)
    _HC_CACHE_V2[key] = rendered
    return rendered


def _get_v2_view_info(case_id: str) -> Dict:
    """Run v2-verify-view once per case (cached)."""
    if case_id in _V2_VIEW_INFO:
        return _V2_VIEW_INFO[case_id]
    cortex_path = SRC / f"{case_id}.cortex"
    try:
        r = subprocess.run(
            CORTEX_CLI + ["verify-view", str(cortex_path), "--format", "json"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0 and r.stdout.strip():
            info = json.loads(r.stdout)
        else:
            info = {"view_coverage_percent": 0, "reversible": False, "errors": 0, "warnings": 0}
    except Exception:
        info = {"view_coverage_percent": 0, "reversible": False, "errors": 0, "warnings": 0}
    _V2_VIEW_INFO[case_id] = info
    return info


# ---------------------------------------------------------------------------
# Implementaciones de metodos
# ---------------------------------------------------------------------------

def select_by_method(method, case, source_text, budget, scenario_id, task):
    if method.config.get("use_cli"):
        if budget is None or budget >= 4096:
            profile = "full"
        elif budget <= 512:
            profile = "min"
        elif budget <= 1024:
            profile = "recovery"
        elif budget <= 2048:
            profile = "work"
        else:
            profile = "full"

        if method.config.get("selector") == "cortex_cli_v1":
            rendered = _get_hcortex_v1(case["case_id"], profile)
        elif method.config.get("selector") == "cortex_v2_convert":
            rendered = _get_hcortex_v2(case["case_id"], profile)
        elif method.config.get("selector") == "cortex_canonical":
            # v2.1.0: canonicalize --preserve (VIEW-aware, structure-preserving)
            # then convert. This is the fix for B-01/B-05 issues from v2.0.0.
            cortex_path = SRC / f"{case['case_id']}.cortex"
            tmp_canon = f"/tmp/v21_bench_canon_{case['case_id']}.cortex"
            try:
                subprocess.run(
                    CORTEX_CLI + ["canonicalize", "--preserve", str(cortex_path), "--out", tmp_canon],
                    capture_output=True, text=True, timeout=15,
                )
                if os.path.exists(tmp_canon):
                    tmp_out = f"/tmp/v21_bench_canon_convert_{case['case_id']}_{profile}.md"
                    subprocess.run(
                        CORTEX_CLI + ["convert", "--from", "cortex", "--to", "hcortex",
                                      tmp_canon, "--out", tmp_out],
                        capture_output=True, text=True, timeout=15,
                    )
                    rendered = Path(tmp_out).read_text() if os.path.exists(tmp_out) else cortex_path.read_text()
                    # Fallback if convert produced empty output
                    if len(rendered) < 500:
                        rendered = _get_hcortex_v2(case["case_id"], profile)
                else:
                    rendered = _get_hcortex_v2(case["case_id"], profile)
            except Exception:
                rendered = _get_hcortex_v2(case["case_id"], profile)
        else:
            rendered = source_text
        if budget:
            target_chars = int(budget * 3.5)
            rendered = rendered[:target_chars]
        return rendered or source_text[:int((budget or 2048) * 3.6)]

    # Ablations
    if method.config.get("selector") == "cortex_ablation_no_P0":
        cortex_text = case["cortex"]
        cleaned = re.sub(r'^(FCS|OBJ|CNST|STP):\w+\{[^}]*\}\s*$', '', cortex_text, flags=re.MULTILINE)
        return cleaned[:int((budget or 2048) * 3.5)]

    if method.config.get("selector") == "cortex_ablation_no_temporal":
        cortex_text = case["cortex"]
        cleaned = re.sub(r'status:"[a-z_]+"', 'status:"unknown"', cortex_text)
        return cleaned[:int((budget or 2048) * 3.5)]

    if method.config.get("selector") == "tail":
        chars = int((budget or 1024) * 4.0)
        return source_text[-chars:] if len(source_text) > chars else source_text

    if method.config.get("selector") == "head_tail":
        chars = int((budget or 1024) * 4.0)
        head_chars = int(chars * method.config.get("head_ratio", 0.25))
        tail_chars = chars - head_chars
        return source_text[:head_chars] + "\n...[TRUNCATED]...\n" + source_text[-tail_chars:]

    if method.config.get("selector") == "head":
        chars = int((budget or 1024) * 4.0)
        return source_text[:chars]

    if method.config.get("selector") == "semantic_pack":
        cortex_text = case["cortex"]
        relevant_sigils = ["IDN", "DOM", "CNST", "FCS", "OBJ", "STP"]
        lines = cortex_text.split("\n")
        selected = [line for line in lines if any(line.startswith(f"{sig}:") for sig in relevant_sigils)]
        result = "\n".join(selected)
        if budget:
            result = result[:int(budget * 3.5)]
        return result

    if method.config.get("selector") == "bm25":
        question_lower = task.question.lower()
        q_terms = set(re.findall(r'\w+', question_lower)) - {"cual", "es", "la", "el", "de", "que", "y", "a", "en", "una", "un", "esta", "tiene", "alguna", "por", "para", "operacion", "esta"}
        for t in task.expected_terms:
            if t:
                q_terms.add(t.lower())
        for t in re.findall(r'\w+', task.gold_answer.lower()):
            if len(t) > 3:
                q_terms.add(t)
        paragraphs = re.split(r'\n\s*\n', source_text)
        scored = [(sum(1 for t in q_terms if t and t in p.lower()), p) for p in paragraphs]
        scored.sort(key=lambda x: -x[0])
        result = "\n\n".join(p for s, p in scored[:5] if s > 0 and p.strip())
        if not result:
            result = source_text[:int((budget or 1024) * 4.0)]
        if budget:
            result = result[:int(budget * 4.0)]
        return result

    return source_text[:int((budget or 2048) * 4.0)]


# ---------------------------------------------------------------------------
# Metricas (mismas que v1.0.0 + metricas nuevas v2)
# ---------------------------------------------------------------------------

def compute_eas(extracted, expected_terms):
    extracted_lower = extracted.lower()
    return 1 if any(t and t.lower() in extracted_lower for t in expected_terms) else 0

def compute_etc(extracted, expected_terms):
    if not expected_terms: return 0.0
    extracted_lower = extracted.lower()
    return sum(1 for t in expected_terms if t and t.lower() in extracted_lower) / len(expected_terms)

def compute_f1(extracted, gold_answer):
    if not gold_answer: return 0.0
    gold_tokens = set(re.findall(r'\w+', gold_answer.lower()))
    extracted_tokens = set(re.findall(r'\w+', extracted.lower()))
    if not gold_tokens or not extracted_tokens: return 0.0
    tp = len(gold_tokens & extracted_tokens)
    if tp == 0: return 0.0
    precision = tp / len(extracted_tokens)
    recall = tp / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)

def compute_da(extracted, gold_decision):
    if not gold_decision: return 0, "no_decision"
    extracted_lower = extracted.lower()
    decision_keywords = {
        "block": ["block", "bloquear", "rechazar", "freeze", "reject"],
        "allow": ["allow", "permitir", "aprobar", "approve"],
        "planned": ["planned", "planeado", "planificado"],
        "current": ["current", "actual", "vigente"],
        "unknown": ["unknown", "desconocido"],
    }
    target_kws = decision_keywords.get(gold_decision, [])
    for kw in target_kws:
        if kw in extracted_lower: return 1, gold_decision
    for dec, kws in decision_keywords.items():
        if dec == gold_decision: continue
        for kw in kws:
            if kw in extracted_lower: return 0, f"confused_with_{dec}"
    return 0, "missing"

def compute_p0_survival(extracted, case):
    cortex_text = case["cortex"]
    p0_sigils = ["FCS", "OBJ", "CNST", "STP"]
    total = preserved = 0
    for sig in p0_sigils:
        matches = re.findall(rf'^{sig}:\w+\{{[^}}]*\}}', cortex_text, re.MULTILINE)
        for m in matches:
            total += 1
            name_match = re.search(rf'^{sig}:(\w+)\{{', m, re.MULTILINE)
            if name_match:
                name = name_match.group(1).lower()
                if name in extracted.lower() or sig.lower() in extracted.lower():
                    preserved += 1
    return preserved / total if total > 0 else 0.0

def compute_p1_survival(extracted, case):
    cortex_text = case["cortex"]
    p1_sigils = ["WRK", "AUD", "RSK", "NXT"]
    total = preserved = 0
    for sig in p1_sigils:
        matches = re.findall(rf'^{sig}:\w+\{{[^}}]*\}}', cortex_text, re.MULTILINE)
        for m in matches:
            total += 1
            name_match = re.search(rf'^{sig}:(\w+)\{{', m, re.MULTILINE)
            if name_match:
                name = name_match.group(1).lower()
                if name in extracted.lower() or sig.lower() in extracted.lower():
                    preserved += 1
    return preserved / total if total > 0 else 0.0

def compute_blocking_constraint_fnr(extracted, case):
    cortex_text = case["cortex"]
    blocking_matches = re.findall(r'CNST:(\w+)\{[^}]*severity:"blocking"[^}]*\}', cortex_text)
    if not blocking_matches: return 0.0
    extracted_lower = extracted.lower()
    omitted = sum(1 for name in blocking_matches if name.lower() not in extracted_lower and "blocking" not in extracted_lower)
    return omitted / len(blocking_matches)

def compute_unsupported_claim_fpr(extracted, scenario_id):
    if scenario_id != "unsupported_claim_suppression": return 0.0
    markers = ["99.99% uptime", "rendimiento mejore un 200%", "garantia implicita de cero fallos"]
    extracted_lower = extracted.lower()
    leaked = sum(1 for m in markers if m.lower() in extracted_lower)
    return leaked / len(markers)

def compute_current_future_confusion(extracted, scenario_id):
    if scenario_id != "stale_state_conflict": return 0.0
    stale_markers = ["migrar a v1.0", "desplegar en staging"]
    current_markers = ["objetivo anterior", "foco anterior", "ESTADO ANTERIOR"]
    extracted_lower = extracted.lower()
    confusion_count = 0
    for sm in stale_markers:
        if sm in extracted_lower:
            idx = extracted_lower.find(sm)
            window = extracted_lower[max(0, idx-100):idx+100]
            if not any(m in window for m in current_markers):
                confusion_count += 1
    return confusion_count / len(stale_markers)

def compute_source_traceability(extracted, case):
    extracted_lower = extracted.lower()
    if "source:" in extracted_lower: return 1
    if "ref:" in extracted_lower or "ref:" in case["cortex"].lower():
        if "ref:" in extracted_lower: return 1
    if re.search(r'(constraint|focus|objective|step|risk|audit|claim|limit)\s*:', extracted_lower):
        return 1
    return 0

def compute_budget_violation(extracted_tokens, budget):
    if budget is None: return 0
    return 1 if extracted_tokens > budget * 1.05 else 0

def compute_evidence_density(weighted_score, context_tokens):
    if context_tokens == 0: return 0.0
    return weighted_score / context_tokens

# NEW v2 metrics

def compute_view_coverage(case_id):
    """VIEW coverage from v2-verify-view (cached)."""
    info = _get_v2_view_info(case_id)
    return info.get("view_coverage_percent", 0) / 100.0  # normalize to 0..1

def compute_reversibility_rate(case_id):
    """1 if v2-verify-view reports reversible=True."""
    info = _get_v2_view_info(case_id)
    return 1 if info.get("reversible", False) else 0

_BIDIR_CACHE: Dict[str, int] = {}
_LOSS_CACHE: Dict[str, int] = {}


def compute_bidir_equivalence(case_id):
    """1 if v2-roundtrip-bidir passes (cached per case)."""
    if case_id in _BIDIR_CACHE:
        return _BIDIR_CACHE[case_id]
    cortex_path = SRC / f"{case_id}.cortex"
    try:
        r = subprocess.run(
            CORTEX_CLI + ["roundtrip-bidir", str(cortex_path)],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0 and "AST equivalent: True" in r.stdout and "Content equivalent: True" in r.stdout:
            result = 1
        else:
            result = 0
    except Exception:
        result = 0
    _BIDIR_CACHE[case_id] = result
    return result


def compute_loss_explained_count(case_id):
    """Number of loss items explained by v2-explain-loss (cached per case)."""
    if case_id in _LOSS_CACHE:
        return _LOSS_CACHE[case_id]
    cortex_path = SRC / f"{case_id}.cortex"
    try:
        r = subprocess.run(
            CORTEX_CLI + ["explain-loss", str(cortex_path), "--format", "json"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0 and r.stdout.strip():
            data = json.loads(r.stdout)
            losses = data.get("losses", data.get("diagnostics", []))
            result = len(losses) if isinstance(losses, list) else 0
        else:
            result = 0
    except Exception:
        result = 0
    _LOSS_CACHE[case_id] = result
    return result


# ---------------------------------------------------------------------------
# Ejecucion del benchmark v2.0.0
# ---------------------------------------------------------------------------

def run_benchmark():
    print(f"Benchmark CODEC-CORTEX v{BENCHMARK_VERSION}")
    print(f"  CLI: v{CLI_VERSION} | CODEC-CORTEX: v{CODEC_CORTEX_VERSION}")
    print(f"  Harness: v{HARNESS_VERSION}")
    print()
    print("Loading corpus...")
    cases = load_corpus()
    print(f"  {len(cases)} cases loaded")

    print("Building tasks...")
    all_tasks = []
    for case in cases:
        all_tasks.extend(build_tasks_for_case(case))
    print(f"  {len(all_tasks)} base tasks generated")

    print("Pre-computing v2 VIEW info per case...")
    for case in cases:
        info = _get_v2_view_info(case["case_id"])
        print(f"  {case['case_id']}: coverage={info.get('view_coverage_percent', 0):.1f}% reversible={info.get('reversible', False)}")

    print("Pre-computing v2 bidirectional equivalence + loss count per case...")
    for case in cases:
        b = compute_bidir_equivalence(case["case_id"])
        l = compute_loss_explained_count(case["case_id"])
        print(f"  {case['case_id']}: bidir={b} loss_count={l}")

    print("\nRunning benchmark...")
    scored_rows = []
    provenance_rows = []
    errors_rows = []
    run_counter = 0

    for method in METHODS:
        print(f"\n=== Method: {method.method_id} ({'v2' if method.is_v2 else 'v1/legacy'}) ===")
        for scenario_id, scenario_fn, budget in SCENARIOS:
            for task in all_tasks:
                case = next(c for c in cases if c["case_id"] == task.case_id)
                source_key = method.config.get("source", "raw_prose")
                if source_key == "cortex":
                    source_text = case["cortex"]
                elif source_key == "json":
                    source_text = case["json"]
                elif source_key == "markdown":
                    source_text = case["markdown"]
                elif source_key == "yaml":
                    source_text = case["yaml"]
                else:
                    source_text = case["raw_prose"]

                scenario_text = scenario_fn(case, source_text, budget) if scenario_fn else source_text

                try:
                    extracted = select_by_method(method, case, scenario_text, budget or 4096, scenario_id, task)
                    error_state = ""
                except Exception as e:
                    extracted = ""
                    error_state = f"execution_error: {type(e).__name__}: {str(e)[:100]}"
                    errors_rows.append({
                        "run_id": f"R-{run_counter:05d}",
                        "method_id": method.method_id,
                        "case_id": case["case_id"],
                        "scenario_id": scenario_id,
                        "task_id": task.task_id,
                        "error": error_state,
                    })

                if method.config.get("source") == "cortex":
                    tok_mode = "cortex"
                elif method.config.get("source") == "json":
                    tok_mode = "json"
                elif method.config.get("source") == "yaml":
                    tok_mode = "yaml"
                elif method.config.get("source") == "markdown":
                    tok_mode = "markdown"
                else:
                    tok_mode = "prose"
                extracted_tokens = count_tokens(extracted, tok_mode)

                # v1 metrics
                eas = compute_eas(extracted, task.expected_terms)
                etc = compute_etc(extracted, task.expected_terms)
                f1 = compute_f1(extracted, task.gold_answer)
                da, da_detail = compute_da(extracted, task.gold_decision)
                p0_surv = compute_p0_survival(extracted, case)
                p1_surv = compute_p1_survival(extracted, case)
                bcfnr = compute_blocking_constraint_fnr(extracted, case)
                ucfpr = compute_unsupported_claim_fpr(extracted, scenario_id)
                cfcr = compute_current_future_confusion(extracted, scenario_id)
                str_rate = compute_source_traceability(extracted, case)
                bvr = compute_budget_violation(extracted_tokens, budget)

                # v2 metrics (only for cortex_v2 methods)
                view_cov = compute_view_coverage(case["case_id"]) if method.is_v2 else 0.0
                reversibility = compute_reversibility_rate(case["case_id"]) if method.is_v2 else 0
                # bidir_equiv is expensive; only compute for cortex_v2 methods on full scenario
                if method.is_v2 and scenario_id == "full":
                    bidir_equiv = compute_bidir_equivalence(case["case_id"])
                else:
                    bidir_equiv = 0
                loss_count = compute_loss_explained_count(case["case_id"]) if method.is_v2 else 0

                # Weighted score (extended for v2)
                weighted = (
                    eas * 1.0 + etc * 1.5 + f1 * 1.5 + da * 2.0 +
                    p0_surv * 2.0 + p1_surv * 1.0 + str_rate * 1.0 +
                    view_cov * 1.5 +  # NEW: VIEW coverage contribution
                    reversibility * 1.0 +  # NEW: reversibility contribution
                    - bcfnr * 3.0 - ucfpr * 3.0 - cfcr * 2.0
                )
                ed = compute_evidence_density(weighted, extracted_tokens)

                run_id = f"R-{run_counter:05d}"
                run_counter += 1

                scored_rows.append({
                    "run_id": run_id,
                    "method_id": method.method_id,
                    "method_family": method.family,
                    "is_v2": int(method.is_v2),
                    "case_id": case["case_id"],
                    "domain": case["domain"],
                    "scenario_id": scenario_id,
                    "budget_tokens": budget if budget else -1,
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "EAS": eas,
                    "ETC": round(etc, 4),
                    "F1": round(f1, 4),
                    "DA": da,
                    "DA_detail": da_detail,
                    "P0_survival": round(p0_surv, 4),
                    "P1_survival": round(p1_surv, 4),
                    "BCFNR": round(bcfnr, 4),
                    "UCFPR": round(ucfpr, 4),
                    "CFCR": round(cfcr, 4),
                    "STR": str_rate,
                    "BVR": bvr,
                    "VIEW_coverage": round(view_cov, 4),  # NEW v2
                    "reversibility": reversibility,  # NEW v2
                    "bidir_equivalence": bidir_equiv,  # NEW v2
                    "loss_count": loss_count,  # NEW v2
                    "context_tokens": extracted_tokens,
                    "evidence_density": round(ed, 6),
                    "weighted_score": round(weighted, 4),
                    "error": error_state,
                })

                provenance_rows.append({
                    "run_id": run_id,
                    "method_id": method.method_id,
                    "case_id": case["case_id"],
                    "scenario_id": scenario_id,
                    "task_id": task.task_id,
                    "source_text_sha256": hashlib.sha256(source_text.encode()).hexdigest()[:16],
                    "extracted_sha256": hashlib.sha256(extracted.encode()).hexdigest()[:16],
                    "extracted_chars": len(extracted),
                })

    # Write CSV outputs
    print(f"\nWriting outputs: {len(scored_rows)} rows")
    fields = list(scored_rows[0].keys())
    with open(RUNS / "scored_tasks.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(scored_rows)

    # Summary by method
    summary = defaultdict(lambda: defaultdict(list))
    for row in scored_rows:
        m = row["method_id"]
        for k in ["EAS", "ETC", "F1", "DA", "P0_survival", "P1_survival", "BCFNR", "UCFPR", "CFCR", "STR", "BVR",
                  "VIEW_coverage", "reversibility", "bidir_equivalence", "loss_count",
                  "context_tokens", "evidence_density", "weighted_score"]:
            summary[m][k].append(row[k])

    summary_rows = []
    for m, metrics in summary.items():
        row = {"method_id": m, "n_tasks": len(metrics["EAS"])}
        for k, vals in metrics.items():
            row[f"avg_{k}"] = round(sum(vals) / len(vals), 4) if k != "context_tokens" else round(sum(vals) / len(vals), 1)
        summary_rows.append(row)

    summary_fields = list(summary_rows[0].keys())
    with open(RUNS / "summary_tasks.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=summary_fields)
        w.writeheader()
        w.writerows(summary_rows)

    # Errors
    if errors_rows:
        with open(RUNS / "errors.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(errors_rows[0].keys()))
            w.writeheader()
            w.writerows(errors_rows)
    else:
        (RUNS / "errors.csv").write_text("no_errors\n", encoding="utf-8")

    # Provenance
    with open(RUNS / "provenance.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(provenance_rows[0].keys()))
        w.writeheader()
        w.writerows(provenance_rows)

    # JSON outputs
    (RUNS / "method_results.json").write_text(
        json.dumps(summary_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    scenario_agg = defaultdict(lambda: defaultdict(list))
    for row in scored_rows:
        key = f"{row['method_id']}|{row['scenario_id']}"
        for k in ["EAS", "ETC", "F1", "DA", "P0_survival", "P1_survival", "BCFNR", "UCFPR", "CFCR", "STR",
                  "VIEW_coverage", "reversibility", "evidence_density"]:
            scenario_agg[key][k].append(row[k])
    scenario_results = []
    for key, metrics in scenario_agg.items():
        m, s = key.split("|", 1)
        row = {"method_id": m, "scenario_id": s, "n": len(metrics["EAS"])}
        for k, vals in metrics.items():
            row[f"avg_{k}"] = round(sum(vals) / len(vals), 4)
        scenario_results.append(row)
    (RUNS / "scenario_results.json").write_text(
        json.dumps(scenario_results, indent=2, ensure_ascii=False), encoding="utf-8")

    # Derived metrics
    positional_methods = ["recent_tail_raw", "head_tail_raw", "head_json", "head_markdown_summary"]
    middle_scores = defaultdict(list)
    for row in scored_rows:
        if row["scenario_id"] == "middle_work_adversarial":
            middle_scores[row["method_id"]].append(float(row["weighted_score"]))
    avg_middle = {m: sum(v) / len(v) for m, v in middle_scores.items() if v}
    best_positional_middle = max((avg_middle.get(m, 0) for m in positional_methods), default=0)
    mrd = {m: round(score - best_positional_middle, 4) for m, score in avg_middle.items()}

    passive_methods = [m.method_id for m in METHODS if m.family != "query_dependent"]
    query_dep_methods = [m.method_id for m in METHODS if m.family == "query_dependent"]
    overall_scores = defaultdict(list)
    for row in scored_rows:
        overall_scores[row["method_id"]].append(float(row["weighted_score"]))
    avg_overall = {m: sum(v) / len(v) for m, v in overall_scores.items() if v}
    best_passive = max((avg_overall.get(m, 0) for m in passive_methods), default=0)
    best_qd = max((avg_overall.get(m, 0) for m in query_dep_methods), default=0)
    qdd = round(best_qd - best_passive, 4)

    derived = {
        "MRD_by_method": mrd,
        "best_positional_middle_score": round(best_positional_middle, 4),
        "QDD": qdd,
        "best_passive_score": round(best_passive, 4),
        "best_query_dependent_score": round(best_qd, 4),
    }
    (RUNS / "derived_metrics.json").write_text(
        json.dumps(derived, indent=2, ensure_ascii=False), encoding="utf-8")

    # v1 vs v2 comparison
    v1_method = "cortex_priority_pack_v1"
    v2_methods = ["cortex_priority_pack", "cortex_canonical"]
    comparison = {"v1_reference": v1_method, "v2_methods": v2_methods, "comparison": []}
    v1_summary = next((r for r in summary_rows if r["method_id"] == v1_method), None)
    for v2m in v2_methods:
        v2_summary = next((r for r in summary_rows if r["method_id"] == v2m), None)
        if v1_summary and v2_summary:
            deltas = {}
            for k in v1_summary:
                if k.startswith("avg_") and k in v2_summary:
                    try:
                        deltas[k] = round(float(v2_summary[k]) - float(v1_summary[k]), 4)
                    except (ValueError, TypeError):
                        pass
            comparison["comparison"].append({
                "v2_method": v2m,
                "v1_method": v1_method,
                "deltas": deltas,
                "v2_metrics": v2_summary,
                "v1_metrics": v1_summary,
            })
    (RUNS / "v1_vs_v2_comparison.json").write_text(
        json.dumps(comparison, indent=2, ensure_ascii=False), encoding="utf-8")

    # Metric registry
    metric_registry = {
        "version": BENCHMARK_VERSION,
        "metrics": [
            {"id": "EAS", "name": "Exact Answer Score", "type": "binary", "range": "0..1", "higher_better": True, "status": "canonical"},
            {"id": "ETC", "name": "Expected Term Coverage", "type": "ratio", "range": "0..1", "higher_better": True, "status": "canonical"},
            {"id": "F1", "name": "Gold Overlap F1", "type": "f1", "range": "0..1", "higher_better": True, "status": "canonical"},
            {"id": "DA", "name": "Decision Accuracy", "type": "binary", "range": "0..1", "higher_better": True, "status": "canonical"},
            {"id": "Avg_CT", "name": "Average Context Tokens", "type": "count", "range": "0..inf", "higher_better": False, "status": "canonical"},
            {"id": "P0_survival", "name": "P0 Survival Rate", "type": "ratio", "range": "0..1", "higher_better": True, "status": "canonical"},
            {"id": "P1_survival", "name": "P1 Survival Rate", "type": "ratio", "range": "0..1", "higher_better": True, "status": "canonical"},
            {"id": "BCFNR", "name": "Blocking Constraint False Negative Rate", "type": "ratio", "range": "0..1", "higher_better": False, "status": "canonical", "ideal": 0},
            {"id": "UCFPR", "name": "Unsupported Claim False Positive Rate", "type": "ratio", "range": "0..1", "higher_better": False, "status": "canonical", "ideal": 0},
            {"id": "CFCR", "name": "Current/Future Confusion Rate", "type": "ratio", "range": "0..1", "higher_better": False, "status": "canonical", "ideal": 0},
            {"id": "STR", "name": "Source Traceability Rate", "type": "binary", "range": "0..1", "higher_better": True, "status": "canonical"},
            {"id": "BVR", "name": "Budget Violation Rate", "type": "binary", "range": "0..1", "higher_better": False, "status": "canonical", "ideal": 0},
            {"id": "MRD", "name": "Middle Recovery Delta", "type": "delta", "range": "-inf..inf", "higher_better": True, "status": "canonical"},
            {"id": "QDD", "name": "Query Dependency Delta", "type": "delta", "range": "-inf..inf", "higher_better": True, "status": "canonical"},
            {"id": "ED", "name": "Evidence Density", "type": "ratio", "range": "0..inf", "higher_better": True, "status": "canonical"},
            # NEW v2 metrics
            {"id": "VIEW_coverage", "name": "VIEW Coverage Rate", "type": "ratio", "range": "0..1", "higher_better": True, "status": "canonical", "introduced_in": "2.0.0"},
            {"id": "reversibility", "name": "Reversibility Rate", "type": "binary", "range": "0..1", "higher_better": True, "status": "canonical", "introduced_in": "2.0.0"},
            {"id": "bidir_equivalence", "name": "Bidirectional Equivalence", "type": "binary", "range": "0..1", "higher_better": True, "status": "canonical", "introduced_in": "2.0.0"},
            {"id": "loss_count", "name": "Loss Explanation Count", "type": "count", "range": "0..inf", "higher_better": False, "status": "canonical", "introduced_in": "2.0.0"},
        ],
    }
    (BASE / "metrics" / "metric_registry.json").write_text(
        json.dumps(metric_registry, indent=2, ensure_ascii=False), encoding="utf-8")

    # Method registry
    method_registry = {
        "version": BENCHMARK_VERSION,
        "methods": [asdict(m) for m in METHODS],
    }
    (BASE / "methods" / "method_registry.json").write_text(
        json.dumps(method_registry, indent=2, ensure_ascii=False), encoding="utf-8")

    # Manifest
    manifest = {
        "benchmark_version": BENCHMARK_VERSION,
        "previous_version": "1.0.0",
        "generated_at": "2026-06-30",
        "executor": "run_benchmark.py v2.0.0",
        "codec_cortex_version": CODEC_CORTEX_VERSION,
        "cli_version": CLI_VERSION,
        "harness_version": HARNESS_VERSION,
        "environment": {
            "python": sys.version.split()[0],
            "platform": sys.platform,
            "tokenizer_proxy": "char-based (1 token ≈ 3.5-4.0 chars depending on format)",
        },
        "methods": [m.method_id for m in METHODS],
        "scenarios": [s[0] for s in SCENARIOS],
        "metrics": [m["id"] for m in metric_registry["metrics"]],
        "budgets": [512, 1024, 2048, 4096],
        "seeds": ["deterministic-no-randomness"],
        "llm_phase": "not_executed (deterministic only per protocol §11.2)",
        "new_in_v2": {
            "methods": ["cortex_priority_pack", "cortex_canonical"],
            "metrics": ["VIEW_coverage", "reversibility", "bidir_equivalence", "loss_count"],
            "cli_commands_used": ["convert", "verify-view", "roundtrip-bidir", "canonicalize", "explain-loss"],
        },
        "totals": {
            "methods": len(METHODS),
            "scenarios": len(SCENARIOS),
            "cases": len(cases),
            "tasks": len(all_tasks),
            "runs": len(scored_rows),
        },
    }
    (BASE / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nBenchmark v{BENCHMARK_VERSION} complete: {len(scored_rows)} runs across {len(METHODS)} methods × {len(SCENARIOS)} scenarios × {len(all_tasks)} tasks")
    return scored_rows


if __name__ == "__main__":
    t0 = time.time()
    run_benchmark()
    print(f"\nElapsed: {time.time() - t0:.1f}s")
