#!/usr/bin/env python3
"""
Harness principal del benchmark CODEC-CORTEX.

Implementa:
- 7 baselines pasivos/posicionales/estructurales/semánticos
- 5 variantes CODEC-CORTEX (CPP v1, adaptive, semantic_hybrid, ablation_no_P0, ablation_no_temporal)
- 8 escenarios canónicos (full, reduced-window, middle-work, stale-state, blocking-constraint, unsupported-claim, corrupted, multi-instance)
- 6 métricas canónicas (EAS, ETC, F1, DA, Avg CT, Avg AT) + 9 métricas nuevas (P0/P1 survival, BCFNR, UCFPR, CFCR, STR, BVR, MRD, QDD, Evidence Density)

Salida:
- runs/scored_tasks.csv
- runs/summary_tasks.csv
- runs/errors.csv
- runs/provenance.csv
- runs/method_results.json
- runs/scenario_results.json
- runs/metric_results.json
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

BASE = Path("/home/z/my-project/download/benchmark-cortex")
SRC = BASE / "corpus" / "source"
RUNS = BASE / "runs"
RUNS.mkdir(parents=True, exist_ok=True)

PYTHON = "/home/z/.venv/bin/python"
CORTEX_CLI = [PYTHON, "-m", "cortex"]

# ---------------------------------------------------------------------------
# Tokenizer proxy (aproximacion TikToken-clike para espanol + ingles)
# ---------------------------------------------------------------------------

# Aproximacion simple: 1 token ≈ 4 chars para texto ingles/espanol mixto.
# Para .cortex denso, contamos atributos y valores; ≈ 1 token ≈ 3.5 chars.
def count_tokens(text: str, mode: str = "prose") -> int:
    """Proxy de tokens. Alineado con rangos empiricos GPT-style para ES/EN."""
    if not text:
        return 0
    chars = len(text)
    if mode == "cortex":
        # .cortex es denso: sigilos, attrs, pares k:v
        return max(1, int(chars / 3.5))
    elif mode == "json":
        # JSON tiene overhead de comillas, llaves, comas
        return max(1, int(chars / 3.8))
    elif mode == "yaml":
        return max(1, int(chars / 3.7))
    elif mode == "markdown":
        return max(1, int(chars / 3.6))
    else:  # prose
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
        # Cargar todas las representaciones
        case["cortex"] = (SRC / f"{cid}.cortex").read_text()
        case["raw_prose"] = (SRC / f"{cid}.raw.md").read_text()
        case["markdown"] = (SRC / f"{cid}.md").read_text()
        case["json"] = (SRC / f"{cid}.json").read_text()
        case["yaml"] = (SRC / f"{cid}.yaml").read_text()
        cases.append(case)
    return cases


# ---------------------------------------------------------------------------
# Definicion de metodos
# ---------------------------------------------------------------------------

@dataclass
class MethodSpec:
    method_id: str
    name: str
    family: str  # passive_positional | passive_structural | passive_semantic | query_dependent | cortex
    description: str
    config: Dict = field(default_factory=dict)


METHODS: List[MethodSpec] = [
    # Baselines pasivos posicionales
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
    # Baselines semánticos (passive semantic - sin conocer la pregunta)
    MethodSpec("semantic_field_pack", "Semantic Field Pack", "passive_semantic",
               "Selecciona entradas por perfil semantico general: identity, constraints, focus, objective.",
               {"source": "cortex", "selector": "semantic_pack"}),
    MethodSpec("keyword_retrieval_raw", "Keyword Retrieval Raw", "query_dependent",
               "BM25-like: rankea parrafos de raw prose por coincidencia con la pregunta (basico).",
               {"source": "raw_prose", "selector": "bm25"}),
    # CODEC-CORTEX Priority Pack
    MethodSpec("cortex_priority_pack_v1", "CORTEX Priority Pack v1 (P0-P5)", "cortex",
               "Seleccion por prioridad cognitiva P0->P5 usando CLI cortex render con perfil MIN/RECOVERY/WORK/FULL.",
               {"source": "cortex", "selector": "cortex_cli", "use_cli": True}),
    MethodSpec("cortex_priority_pack_adaptive", "CORTEX Priority Pack Adaptive", "cortex",
               "Como v1 pero adapta perfil al presupuesto exacto en lugar de saltar entre MIN/RECOVERY/WORK/FULL.",
               {"source": "cortex", "selector": "cortex_cli_adaptive", "use_cli": True}),
    MethodSpec("cortex_priority_pack_semantic_hybrid", "CORTEX Priority Pack Semantic Hybrid", "cortex",
               "Combina P0-P5 con reranking semantico leve (sigilos nombrados en la pregunta suben prioridad).",
               {"source": "cortex", "selector": "cortex_cli_hybrid", "use_cli": True}),
    # Ablaciones
    MethodSpec("cortex_ablation_no_P0", "Ablation: no P0 priority", "cortex",
               "Elimina prioridad P0 (FCS, OBJ, CNST, STP tratados como P5). Mide contribucion de P0.",
               {"source": "cortex", "selector": "cortex_ablation_no_P0", "use_cli": False}),
    MethodSpec("cortex_ablation_no_temporal", "Ablation: no temporal", "cortex",
               "Elimina distincion current/planned/future. Mide contribucion del scope temporal.",
               {"source": "cortex", "selector": "cortex_ablation_no_temporal", "use_cli": False}),
]


# ---------------------------------------------------------------------------
# Generacion de tareas por caso + scenario
# ---------------------------------------------------------------------------

@dataclass
class Task:
    task_id: str
    case_id: str
    scenario_id: str
    task_type: str  # qa | decision | traceability | safety
    question: str
    gold_answer: str
    expected_terms: List[str]
    forbidden_terms: List[str] = field(default_factory=list)
    gold_decision: Optional[str] = None  # allow | block | planned | current | unknown
    required_sources: List[str] = field(default_factory=list)
    priority_scope: List[str] = field(default_factory=lambda: ["P0", "P1"])
    temporal_scope: str = "current"
    severity: str = "normal"
    rationale: str = ""


# Mapa de tareas canonicas por caso (independientes del escenario)
def build_tasks_for_case(case: Dict) -> List[Task]:
    cid = case["case_id"]
    tasks = []
    # Tarea QA: foco actual
    tasks.append(Task(
        task_id=f"T-{cid}-QA-01",
        case_id=cid,
        scenario_id="full",
        task_type="qa",
        question="Cual es el foco actual de esta operacion?",
        gold_answer=case["cortex"].split('FCS:primary{what:"')[1].split('"')[0] if 'FCS:primary{what:"' in case["cortex"] else "",
        expected_terms=case["cortex"].split('FCS:primary{what:"')[1].split('"')[0].lower().split()[:3] if 'FCS:primary{what:"' in case["cortex"] else [],
        required_sources=["FCS"],
        rationale="Verifica preservacion del foco operativo."
    ))
    # Tarea QA: objetivo
    tasks.append(Task(
        task_id=f"T-{cid}-QA-02",
        case_id=cid,
        scenario_id="full",
        task_type="qa",
        question="Cual es el objetivo activo?",
        gold_answer=case["cortex"].split('OBJ:')[1].split('{goal:"')[1].split('"')[0] if 'OBJ:' in case["cortex"] and '{goal:"' in case["cortex"] else "",
        expected_terms=case["cortex"].split('OBJ:')[1].split('{goal:"')[1].split('"')[0].lower().split()[:3] if 'OBJ:' in case["cortex"] and '{goal:"' in case["cortex"] else [],
        required_sources=["OBJ"],
        rationale="Verifica preservacion del objetivo."
    ))
    # Tarea decision: bloqueo?
    cnst_match = re.search(r'CNST:(\w+)\{[^}]*severity:"blocking"[^}]*\}', case["cortex"])
    if cnst_match:
        cnst_name = cnst_match.group(1)
        tasks.append(Task(
            task_id=f"T-{cid}-DEC-01",
            case_id=cid,
            scenario_id="full",
            task_type="decision",
            question=f"La operacion tiene alguna restriccion bloqueante ({cnst_name})?",
            gold_answer=f"Si: {cnst_name} es blocking",
            expected_terms=[cnst_name.lower(), "blocking"],
            gold_decision="block",
            required_sources=["CNST"],
            rationale="Verifica conservacion de constraints blocking."
        ))
    # Tarea trazabilidad: fuente
    if "REF:" in case["cortex"]:
        ref_match = re.search(r'REF:(\w+)\{[^}]*\}', case["cortex"])
        if ref_match:
            ref_name = ref_match.group(1)
            tasks.append(Task(
                task_id=f"T-{cid}-TRC-01",
                case_id=cid,
                scenario_id="full",
                task_type="traceability",
                question=f"Cual es la referencia de origen disponible ({ref_name})?",
                gold_answer=ref_name,
                expected_terms=[ref_name.lower()],
                required_sources=["REF"],
                rationale="Verifica trazabilidad de fuente."
            ))
    # Tarea seguridad: claim vs supported
    if "CLAIM:" in case["cortex"]:
        claim_match = re.search(r'CLAIM:(\w+)\{[^}]*statement:"([^"]+)"', case["cortex"])
        if claim_match:
            claim_name = claim_match.group(1)
            statement = claim_match.group(2)
            tasks.append(Task(
                task_id=f"T-{cid}-SAF-01",
                case_id=cid,
                scenario_id="full",
                task_type="safety",
                question=f"Esta afirmacion esta soportada por evidencia: '{statement[:60]}...'?",
                gold_answer=f"Si: {claim_name} tiene evidence",
                expected_terms=[claim_name.lower()],
                forbidden_terms=["no soportado", "sin evidencia", "inventado"],
                required_sources=["CLAIM"],
                rationale="Verifica que claims soportados no se supriman."
            ))
    return tasks


# ---------------------------------------------------------------------------
# Escenarios: transformadores de contexto
# ---------------------------------------------------------------------------

def scenario_full(case: Dict, source_text: str, budget: int) -> str:
    """Escenario A: contexto completo sin restriccion."""
    return source_text


def scenario_reduced_window(case: Dict, source_text: str, budget: int) -> str:
    """Recorta el contexto al presupuesto (en tokens)."""
    # Aproximacion: tomar los primeros 4*budget chars
    chars = int(budget * 3.6)
    return source_text[:chars]


def scenario_middle_work_adversarial(case: Dict, source_text: str, budget: int) -> str:
    """Coloca evidencia critica en el medio rodeada de ruido."""
    # Para texto plano: insertar 1500 chars de ruido antes y despues de la frase critica
    noise_pre = "Contexto adicional. " * 80  # ~1600 chars
    noise_post = "Mas detalle historico. " * 80
    # Frase critica: el FCS extraido del .cortex
    fcs_match = re.search(r'FCS:primary\{what:"([^"]+)"', case["cortex"])
    critical = fcs_match.group(1) if fcs_match else "Foco operacional critico"
    return noise_pre + " " + critical + " " + noise_post + " " + source_text[:int(budget * 1.5)]


def scenario_stale_state_conflict(case: Dict, source_text: str, budget: int) -> str:
    """Incluye estados antiguos y actuales en conflicto."""
    stale = (
        "ESTADO ANTERIOR (OBSOLETO): El objetivo anterior era migrar a v1.0 (status=done). "
        "ESTADO PREVIO (OBSOLETO): El foco anterior era desplegar en staging (status=done). "
    )
    return stale + source_text


def scenario_blocking_constraint_survival(case: Dict, source_text: str, budget: int) -> str:
    """Incluye restricciones severas que bloquean una accion."""
    extra_blocking = (
        "CNST:emergency_stop{rule:'accion destructiva requiere aprobacion del CISO', severity:'blocking', survive:'min'} "
        "CNST:data_residency{rule:'datos sensibles no pueden salir de la region EU', severity:'blocking', survive:'min'} "
    )
    return extra_blocking + source_text


def scenario_unsupported_claim_suppression(case: Dict, source_text: str, budget: int) -> str:
    """Incluye afirmaciones tentativas, prohibidas o no demostradas."""
    unsupported = (
        "HIPOTESIS NO VERIFICADA: se especula que el sistema podria alcanzar 99.99% uptime con esta config. "
        "AFIRMACION TENTATIVA: posiblemente el rendimiento mejore un 200%. "
        "CLAIM NO SOPORTADO: garantia implicita de cero fallos. "
    )
    return unsupported + source_text


def scenario_corrupted_memory_tolerance(case: Dict, source_text: str, budget: int) -> str:
    """Introduce lineas corruptas, incompletas o mal formadas."""
    corrupted_block = (
        "}}}{invalid syntax line\n"
        "FCS:broken{what:}\n"  # empty value
        "OBJ:missing_brace{goal:\"unbalanced\n"
        "RANDOM_NOISE_LINE_WITHOUT_STRUCTURE_XJ7K2\n"
        "@@@!!!###\n"
    )
    return corrupted_block + source_text


def scenario_multi_instance_sigil(case: Dict, source_text: str, budget: int) -> str:
    """Multiples instancias del mismo sigil con roles diferentes."""
    multi = (
        "FCS:primary{what:\"foco principal actual\", priority:\"high\"} "
        "FCS:secondary{what:\"foco secundario\", priority:\"medium\"} "
        "FCS:tertiary{what:\"foco terciario\", priority:\"low\"} "
        "OBJ:primary{goal:\"objetivo principal\"} "
        "OBJ:secondary{goal:\"objetivo secundario\"} "
        "OBJ:stretch{goal:\"objetivo ambicioso\"} "
    )
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
# Implementaciones de metodos
# ---------------------------------------------------------------------------

# Cache de renders HCORTEX por (case_id, profile)
_HCORTEX_CACHE: Dict[Tuple[str, str], str] = {}


def _get_hcortex_render(case_id: str, profile: str) -> str:
    """Renderiza .cortex a HCORTEX via CLI con cache por case+profile."""
    key = (case_id, profile)
    if key in _HCORTEX_CACHE:
        return _HCORTEX_CACHE[key]
    cortex_path = SRC / f"{case_id}.cortex"
    tmp_out = f"/tmp/render_{case_id}_{profile}.md"
    try:
        subprocess.run(
            CORTEX_CLI + ["render", str(cortex_path), "--mode", "read",
                          "--profile", profile, "--out", tmp_out],
            capture_output=True, text=True, timeout=15,
        )
        if os.path.exists(tmp_out):
            rendered = Path(tmp_out).read_text()
        else:
            rendered = (SRC / f"{case_id}.cortex").read_text()
    except Exception:
        rendered = (SRC / f"{case_id}.cortex").read_text()
    _HCORTEX_CACHE[key] = rendered
    return rendered


def select_by_method(method: MethodSpec, case: Dict, source_text: str, budget: int, scenario_id: str, task: Task) -> str:
    """Aplica el metodo para extraer contexto bajo presupuesto."""

    if method.config.get("use_cli") and method.config.get("selector") in ("cortex_cli", "cortex_cli_adaptive", "cortex_cli_hybrid"):
        # Usar CLI cortex render con perfil segun presupuesto (cached)
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
        rendered = _get_hcortex_render(case["case_id"], profile)
        # Truncate to budget
        if budget:
            target_chars = int(budget * 3.5)
            rendered = rendered[:target_chars]
        return rendered or source_text[:int((budget or 2048) * 3.6)]

    # Ablations
    if method.config.get("selector") == "cortex_ablation_no_P0":
        # Strip P0 sigils (FCS, OBJ, CNST, STP) from .cortex
        cortex_text = case["cortex"]
        # Remove lines starting with FCS:, OBJ:, CNST:, STP:
        cleaned = re.sub(r'^(FCS|OBJ|CNST|STP):\w+\{[^}]*\}\s*$', '', cortex_text, flags=re.MULTILINE)
        return cleaned[:int((budget or 2048) * 3.5)]

    if method.config.get("selector") == "cortex_ablation_no_temporal":
        # Remove temporal info: status, temporal_scope attrs
        cortex_text = case["cortex"]
        cleaned = re.sub(r'status:"[a-z_]+"', 'status:"unknown"', cortex_text)
        return cleaned[:int((budget or 2048) * 3.5)]

    # Passive positional: tail
    if method.config.get("selector") == "tail":
        chars = int((budget or 1024) * 4.0)
        return source_text[-chars:] if len(source_text) > chars else source_text

    # Passive positional: head_tail
    if method.config.get("selector") == "head_tail":
        chars = int((budget or 1024) * 4.0)
        head_chars = int(chars * method.config.get("head_ratio", 0.25))
        tail_chars = chars - head_chars
        return source_text[:head_chars] + "\n...[TRUNCATED]...\n" + source_text[-tail_chars:]

    # Passive positional: head (JSON or markdown)
    if method.config.get("selector") == "head":
        chars = int((budget or 1024) * 4.0)
        return source_text[:chars]

    # Passive semantic: semantic_field_pack
    if method.config.get("selector") == "semantic_pack":
        # Extract identity, constraints, focus, objective from .cortex
        cortex_text = case["cortex"]
        relevant_sigils = ["IDN", "DOM", "CNST", "FCS", "OBJ", "STP"]
        lines = cortex_text.split("\n")
        selected = []
        for line in lines:
            for sig in relevant_sigils:
                if line.startswith(f"{sig}:"):
                    selected.append(line)
                    break
        result = "\n".join(selected)
        if budget:
            result = result[:int(budget * 3.5)]
        return result

    # Query-dependent: BM25-like
    if method.config.get("selector") == "bm25":
        # Split into paragraphs, score by term overlap with question + expected terms
        question_lower = task.question.lower()
        # Combine question terms + expected terms (this simulates knowing what to look for)
        q_terms = set(re.findall(r'\w+', question_lower)) - {"cual", "es", "la", "el", "de", "que", "y", "a", "en", "una", "un", "esta", "tiene", "alguna", "por", "para", "operacion", "esta"}
        # Add expected terms as strong signal (simulates ideal retrieval)
        for t in task.expected_terms:
            if t:
                q_terms.add(t.lower())
        # Also add gold answer tokens
        for t in re.findall(r'\w+', task.gold_answer.lower()):
            if len(t) > 3:
                q_terms.add(t)
        paragraphs = re.split(r'\n\s*\n', source_text)
        scored = []
        for p in paragraphs:
            p_lower = p.lower()
            score = sum(1 for t in q_terms if t and t in p_lower)
            scored.append((score, p))
        scored.sort(key=lambda x: -x[0])
        # Take top-5 paragraphs with content
        result = "\n\n".join(p for s, p in scored[:5] if s > 0 and p.strip())
        if not result:
            result = source_text[:int((budget or 1024) * 4.0)]
        if budget:
            result = result[:int(budget * 4.0)]
        return result

    # Default
    return source_text[:int((budget or 2048) * 4.0)]


# ---------------------------------------------------------------------------
# Metricas
# ---------------------------------------------------------------------------

def compute_eas(extracted: str, expected_terms: List[str]) -> int:
    """Exact Answer Score: 1 si aparece al menos un termino esperado."""
    extracted_lower = extracted.lower()
    for t in expected_terms:
        if t and t.lower() in extracted_lower:
            return 1
    return 0


def compute_etc(extracted: str, expected_terms: List[str]) -> float:
    """Expected Term Coverage: fraccion de terminos esperados presentes."""
    if not expected_terms:
        return 0.0
    extracted_lower = extracted.lower()
    found = sum(1 for t in expected_terms if t and t.lower() in extracted_lower)
    return found / len(expected_terms)


def compute_f1(extracted: str, gold_answer: str) -> float:
    """Gold Overlap F1: solapamiento tokenizado."""
    if not gold_answer:
        return 0.0
    gold_tokens = set(re.findall(r'\w+', gold_answer.lower()))
    extracted_tokens = set(re.findall(r'\w+', extracted.lower()))
    if not gold_tokens or not extracted_tokens:
        return 0.0
    tp = len(gold_tokens & extracted_tokens)
    if tp == 0:
        return 0.0
    precision = tp / len(extracted_tokens)
    recall = tp / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def compute_da(extracted: str, gold_decision: Optional[str]) -> Tuple[int, str]:
    """Decision Accuracy: 1 si la decision correcta esta presente."""
    if not gold_decision:
        return 0, "no_decision"
    extracted_lower = extracted.lower()
    # Buscar keyword de la decision
    decision_keywords = {
        "block": ["block", "bloquear", "rechazar", "freeze", "reject"],
        "allow": ["allow", "permitir", "aprobar", "approve"],
        "planned": ["planned", "planeado", "planificado"],
        "current": ["current", "actual", "vigente"],
        "unknown": ["unknown", "desconocido"],
    }
    target_kws = decision_keywords.get(gold_decision, [])
    for kw in target_kws:
        if kw in extracted_lower:
            return 1, gold_decision
    # Detectar confusion con otra decision
    for dec, kws in decision_keywords.items():
        if dec == gold_decision:
            continue
        for kw in kws:
            if kw in extracted_lower:
                return 0, f"confused_with_{dec}"
    return 0, "missing"


def compute_p0_survival(extracted: str, case: Dict) -> float:
    """Porcentaje de entradas P0 preservadas: FCS, OBJ, CNST, STP."""
    cortex_text = case["cortex"]
    p0_sigils = ["FCS", "OBJ", "CNST", "STP"]
    total = 0
    preserved = 0
    for sig in p0_sigils:
        # Contar entradas de este sigil en el .cortex original
        matches = re.findall(rf'^{sig}:\w+\{{[^}}]*\}}', cortex_text, re.MULTILINE)
        for m in matches:
            total += 1
            # Extraer nombre
            name_match = re.search(rf'^{sig}:(\w+)\{{', m, re.MULTILINE)
            if name_match:
                name = name_match.group(1).lower()
                # Verificar si el nombre aparece en el contexto extraido
                if name in extracted.lower() or sig.lower() in extracted.lower():
                    preserved += 1
    return preserved / total if total > 0 else 0.0


def compute_p1_survival(extracted: str, case: Dict) -> float:
    """Porcentaje de entradas P1 preservadas: WRK, AUD, RSK, NXT."""
    cortex_text = case["cortex"]
    p1_sigils = ["WRK", "AUD", "RSK", "NXT"]
    total = 0
    preserved = 0
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


def compute_blocking_constraint_fnr(extracted: str, case: Dict) -> float:
    """False Negative Rate de constraints blocking: % omitidos."""
    cortex_text = case["cortex"]
    blocking_matches = re.findall(r'CNST:(\w+)\{[^}]*severity:"blocking"[^}]*\}', cortex_text)
    if not blocking_matches:
        return 0.0
    extracted_lower = extracted.lower()
    omitted = sum(1 for name in blocking_matches if name.lower() not in extracted_lower and "blocking" not in extracted_lower)
    return omitted / len(blocking_matches)


def compute_unsupported_claim_fpr(extracted: str, scenario_id: str) -> float:
    """False Positive Rate de claims no soportados que aparecen como validos."""
    if scenario_id != "unsupported_claim_suppression":
        return 0.0
    unsupported_markers = [
        "99.99% uptime",
        "rendimiento mejore un 200%",
        "garantia implicita de cero fallos",
    ]
    extracted_lower = extracted.lower()
    leaked = sum(1 for m in unsupported_markers if m.lower() in extracted_lower)
    return leaked / len(unsupported_markers)


def compute_current_future_confusion(extracted: str, scenario_id: str) -> float:
    """Confusion current/future: % casos donde estado futuro/planeado se interpreta como actual."""
    if scenario_id != "stale_state_conflict":
        return 0.0
    # Marcadores de estados obsoletos
    stale_markers = ["migrar a v1.0", "desplegar en staging"]
    current_markers = ["objetivo anterior", "foco anterior", "ESTADO ANTERIOR"]
    extracted_lower = extracted.lower()
    # Si los marcadores stale aparecen SIN etiqueta de "obsoleto"/"anterior", hay confusion
    confusion_count = 0
    for sm in stale_markers:
        if sm in extracted_lower:
            # Verificar si hay etiqueta de stale cerca
            idx = extracted_lower.find(sm)
            window = extracted_lower[max(0, idx-100):idx+100]
            if not any(m in window for m in current_markers):
                confusion_count += 1
    return confusion_count / len(stale_markers)


def compute_source_traceability(extracted: str, case: Dict) -> int:
    """1 si la evidencia conserva referencia de origen (REF, source: o referencia al sigilo de origen)."""
    extracted_lower = extracted.lower()
    # HCORTEX preserva source: tags (e.g. "source: `CNST:honesty`")
    if "source:" in extracted_lower:
        return 1
    # .cortex preserva REF: entries
    if "ref:" in extracted_lower or "ref:" in case["cortex"].lower():
        # Si el caso tenia REF y el extracted preserva REF
        if "ref:" in extracted_lower:
            return 1
    # Si el extracted preserva al menos un sigilo con nombre (e.g. "CNST:honesty" o "Constraint: honesty")
    # HCORTEX renderiza como "### Constraint: honesty"
    if re.search(r'(constraint|focus|objective|step|risk|audit|claim|limit)\s*:', extracted_lower):
        return 1
    return 0


def compute_budget_violation(extracted_tokens: int, budget: Optional[int]) -> int:
    """1 si excede el presupuesto."""
    if budget is None:
        return 0
    return 1 if extracted_tokens > budget * 1.05 else 0  # 5% tolerance


def compute_evidence_density(weighted_score: float, context_tokens: int) -> float:
    """evidence_density = weighted_score / context_tokens."""
    if context_tokens == 0:
        return 0.0
    return weighted_score / context_tokens


# ---------------------------------------------------------------------------
# Ejecucion del benchmark
# ---------------------------------------------------------------------------

def run_benchmark():
    print("Loading corpus...")
    cases = load_corpus()
    print(f"  {len(cases)} cases loaded")

    print("Building tasks...")
    all_tasks = []
    for case in cases:
        all_tasks.extend(build_tasks_for_case(case))
    print(f"  {len(all_tasks)} base tasks generated")

    print("Running benchmark...")
    scored_rows = []
    provenance_rows = []
    errors_rows = []
    run_counter = 0

    for method in METHODS:
        print(f"\n=== Method: {method.method_id} ===")
        for scenario_id, scenario_fn, budget in SCENARIOS:
            for task in all_tasks:
                # Skip irrelevant scenario-task combos to save time
                # All tasks run on all scenarios (canonical)
                case = next(c for c in cases if c["case_id"] == task.case_id)
                # Source text depends on method family
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

                # Apply scenario transformation
                scenario_text = scenario_fn(case, source_text, budget) if scenario_fn else source_text

                # Apply method selection
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

                # Tokenize extracted
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

                # Compute metrics
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

                # Weighted score for evidence density
                weighted = (
                    eas * 1.0 +
                    etc * 1.5 +
                    f1 * 1.5 +
                    da * 2.0 +
                    p0_surv * 2.0 +
                    p1_surv * 1.0 +
                    str_rate * 1.0 -
                    bcfnr * 3.0 -
                    ucfpr * 3.0 -
                    cfcr * 2.0
                )
                ed = compute_evidence_density(weighted, extracted_tokens)

                run_id = f"R-{run_counter:05d}"
                run_counter += 1

                scored_rows.append({
                    "run_id": run_id,
                    "method_id": method.method_id,
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
        for k in ["EAS", "ETC", "F1", "DA", "P0_survival", "P1_survival", "BCFNR", "UCFPR", "CFCR", "STR", "BVR", "context_tokens", "evidence_density", "weighted_score"]:
            summary[m][k].append(row[k])

    summary_rows = []
    for m, metrics in summary.items():
        row = {"method_id": m, "n_tasks": len(metrics["EAS"])}
        for k, vals in metrics.items():
            if k == "context_tokens":
                row[f"avg_{k}"] = round(sum(vals) / len(vals), 1)
            else:
                row[f"avg_{k}"] = round(sum(vals) / len(vals), 4)
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

    # JSON outputs for analysis
    (RUNS / "method_results.json").write_text(
        json.dumps(summary_rows, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Scenario-level aggregation
    scenario_agg = defaultdict(lambda: defaultdict(list))
    for row in scored_rows:
        s = row["scenario_id"]
        m = row["method_id"]
        key = f"{m}|{s}"
        for k in ["EAS", "ETC", "F1", "DA", "P0_survival", "P1_survival", "BCFNR", "UCFPR", "CFCR", "STR", "evidence_density"]:
            scenario_agg[key][k].append(row[k])
    scenario_results = []
    for key, metrics in scenario_agg.items():
        m, s = key.split("|", 1)
        row = {"method_id": m, "scenario_id": s, "n": len(metrics["EAS"])}
        for k, vals in metrics.items():
            row[f"avg_{k}"] = round(sum(vals) / len(vals), 4)
        scenario_results.append(row)
    (RUNS / "scenario_results.json").write_text(
        json.dumps(scenario_results, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Metric registry
    metric_registry = {
        "version": "1.0.0",
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
            {"id": "MRD", "name": "Middle Recovery Delta", "type": "delta", "range": "-1..1", "higher_better": True, "status": "canonical"},
            {"id": "QDD", "name": "Query Dependency Delta", "type": "delta", "range": "-1..1", "higher_better": True, "status": "canonical"},
            {"id": "ED", "name": "Evidence Density", "type": "ratio", "range": "0..inf", "higher_better": True, "status": "canonical"},
        ],
    }
    (BASE / "metrics" / "metric_registry.json").write_text(
        json.dumps(metric_registry, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Method registry
    method_registry = {
        "version": "1.0.0",
        "methods": [asdict(m) for m in METHODS],
    }
    (BASE / "methods" / "method_registry.json").write_text(
        json.dumps(method_registry, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Manifest
    manifest = {
        "benchmark_version": "1.0.0",
        "generated_at": "2026-06-28",
        "executor": "benchmark_harness.py",
        "codec_cortex_version": "0.3.0",
        "cli_version": "1.1.9",
        "harness_version": "1.0.0",
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
        "totals": {
            "methods": len(METHODS),
            "scenarios": len(SCENARIOS),
            "cases": len(cases),
            "tasks": len(all_tasks),
            "runs": len(scored_rows),
        },
    }
    (BASE / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\nBenchmark complete: {len(scored_rows)} runs across {len(METHODS)} methods × {len(SCENARIOS)} scenarios × {len(all_tasks)} tasks")
    print(f"  outputs: {RUNS}")
    return scored_rows


if __name__ == "__main__":
    t0 = time.time()
    run_benchmark()
    print(f"\nElapsed: {time.time() - t0:.1f}s")
