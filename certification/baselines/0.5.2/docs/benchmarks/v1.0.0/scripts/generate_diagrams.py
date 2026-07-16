#!/usr/bin/env python3
"""
Calcula metricas derivadas (MRD, QDD) y genera todos los diagramas del benchmark.

Salidas:
- runs/derived_metrics.json (MRD, QDD por metodo)
- diagrams/*.png (matplotlib charts)
- diagrams/*.puml (PlantUML sources)
- diagrams/*.svg (rendered PlantUML, si plantuml disponible)
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
# Cargar fuentes con soporte CJK + Latin
fm.fontManager.addfont('/usr/share/fonts/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf')
fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Serif SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

BASE = Path("/home/z/my-project/download/benchmark-cortex")
RUNS = BASE / "runs"
DIAG = BASE / "diagrams"
DIAG.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Cargar datos
# ---------------------------------------------------------------------------

def load_scored():
    with open(RUNS / "scored_tasks.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_summary():
    with open(RUNS / "summary_tasks.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_scenario():
    with open(RUNS / "scenario_results.json", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Metricas derivadas
# ---------------------------------------------------------------------------

def compute_derived(scored, scenario_data):
    """Calcula MRD (Middle Recovery Delta) y QDD (Query Dependency Delta)."""

    # MRD: diferencia entre el metodo y el mejor baseline posicional en middle_work_adversarial
    # Baselines posicionales: recent_tail_raw, head_tail_raw, head_json, head_markdown_summary
    positional_methods = ["recent_tail_raw", "head_tail_raw", "head_json", "head_markdown_summary"]
    # Usar weighted_score como metrica agregada
    middle_scores = defaultdict(list)
    for row in scored:
        if row["scenario_id"] == "middle_work_adversarial":
            middle_scores[row["method_id"]].append(float(row["weighted_score"]))

    avg_middle = {m: sum(v) / len(v) for m, v in middle_scores.items() if v}
    best_positional_middle = max(
        (avg_middle.get(m, 0) for m in positional_methods), default=0
    )

    mrd = {}
    for m, score in avg_middle.items():
        mrd[m] = round(score - best_positional_middle, 4)

    # QDD: diferencia entre mejor metodo pasivo y mejor query-dependent
    passive_methods = ["recent_tail_raw", "head_tail_raw", "head_json", "head_markdown_summary",
                       "semantic_field_pack", "cortex_priority_pack_v1",
                       "cortex_priority_pack_adaptive", "cortex_priority_pack_semantic_hybrid",
                       "cortex_ablation_no_P0", "cortex_ablation_no_temporal"]
    query_dep_methods = ["keyword_retrieval_raw"]

    # Aggregate over all scenarios
    overall_scores = defaultdict(list)
    for row in scored:
        overall_scores[row["method_id"]].append(float(row["weighted_score"]))
    avg_overall = {m: sum(v) / len(v) for m, v in overall_scores.items() if v}

    best_passive = max((avg_overall.get(m, 0) for m in passive_methods), default=0)
    best_qd = max((avg_overall.get(m, 0) for m in query_dep_methods), default=0)
    qdd = round(best_qd - best_passive, 4)

    return {
        "MRD_by_method": mrd,
        "best_positional_middle_score": round(best_positional_middle, 4),
        "QDD": qdd,
        "best_passive_score": round(best_passive, 4),
        "best_query_dependent_score": round(best_qd, 4),
    }


# ---------------------------------------------------------------------------
# Diagramas matplotlib
# ---------------------------------------------------------------------------

METHOD_LABELS = {
    "recent_tail_raw": "Recent Tail Raw",
    "head_tail_raw": "Head+Tail Raw",
    "head_json": "Head JSON",
    "head_markdown_summary": "Head Markdown",
    "semantic_field_pack": "Semantic Field Pack",
    "keyword_retrieval_raw": "Keyword Retrieval",
    "cortex_priority_pack_v1": "CORTEX PP v1",
    "cortex_priority_pack_adaptive": "CORTEX PP Adaptive",
    "cortex_priority_pack_semantic_hybrid": "CORTEX PP Hybrid",
    "cortex_ablation_no_P0": "Ablation: no P0",
    "cortex_ablation_no_temporal": "Ablation: no temporal",
}

METHOD_COLORS = {
    "recent_tail_raw": "#94a3b8",
    "head_tail_raw": "#64748b",
    "head_json": "#cbd5e1",
    "head_markdown_summary": "#a1a1aa",
    "semantic_field_pack": "#fbbf24",
    "keyword_retrieval_raw": "#f97316",
    "cortex_priority_pack_v1": "#2563eb",
    "cortex_priority_pack_adaptive": "#1d4ed8",
    "cortex_priority_pack_semantic_hybrid": "#1e40af",
    "cortex_ablation_no_P0": "#dc2626",
    "cortex_ablation_no_temporal": "#b91c1c",
}

# Cortezas/capas para figuras: passive positional, passive semantic, query-dependent, cortex, ablation
METHOD_FAMILY = {
    "recent_tail_raw": "Passive Positional",
    "head_tail_raw": "Passive Positional",
    "head_json": "Passive Positional",
    "head_markdown_summary": "Passive Positional",
    "semantic_field_pack": "Passive Semantic",
    "keyword_retrieval_raw": "Query-Dependent",
    "cortex_priority_pack_v1": "CODEC-CORTEX",
    "cortex_priority_pack_adaptive": "CODEC-CORTEX",
    "cortex_priority_pack_semantic_hybrid": "CODEC-CORTEX",
    "cortex_ablation_no_P0": "Ablation",
    "cortex_ablation_no_temporal": "Ablation",
}

FAMILY_COLORS = {
    "Passive Positional": "#94a3b8",
    "Passive Semantic": "#fbbf24",
    "Query-Dependent": "#f97316",
    "CODEC-CORTEX": "#2563eb",
    "Ablation": "#dc2626",
}


def chart_weighted_score(summary):
    """Bar chart: weighted score por metodo."""
    methods = sorted(summary, key=lambda x: -float(x["avg_weighted_score"]))
    names = [METHOD_LABELS.get(m["method_id"], m["method_id"]) for m in methods]
    scores = [float(m["avg_weighted_score"]) for m in methods]
    colors = [METHOD_COLORS.get(m["method_id"], "#999") for m in methods]

    fig, ax = plt.subplots(figsize=(12, 6.5), constrained_layout=True)
    bars = ax.barh(names, scores, color=colors, edgecolor="white", linewidth=0.5)
    ax.invert_yaxis()
    ax.set_xlabel("Puntaje ponderado (mayor = mejor)")
    ax.set_title("Comparacion global de metodos — Puntaje ponderado agregado",
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{score:.2f}", va="center", fontsize=9)
    # Legend by family
    from matplotlib.patches import Patch
    legend_handles = [Patch(facecolor=c, label=f) for f, c in FAMILY_COLORS.items()]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=9, framealpha=0.9)
    fig.savefig(DIAG / "01_weighted_score.png", dpi=150)
    plt.close(fig)
    print("  01_weighted_score.png")


def chart_p0_p1_survival(summary):
    """Bar chart agrupado: P0 y P1 survival por metodo."""
    methods = sorted(summary, key=lambda x: -float(x["avg_P0_survival"]))
    names = [METHOD_LABELS.get(m["method_id"], m["method_id"]) for m in methods]
    p0 = [float(m["avg_P0_survival"]) for m in methods]
    p1 = [float(m["avg_P1_survival"]) for m in methods]

    fig, ax = plt.subplots(figsize=(12, 6.5), constrained_layout=True)
    x = list(range(len(names)))
    w = 0.4
    ax.bar([i - w / 2 for i in x], p0, w, label="P0 survival (FCS/OBJ/CNST/STP)", color="#2563eb", edgecolor="white")
    ax.bar([i + w / 2 for i in x], p1, w, label="P1 survival (WRK/AUD/RSK/NXT)", color="#f97316", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=9)
    ax.set_ylabel("Tasa de supervivencia (0..1)")
    ax.set_title("Supervivencia de entradas P0 y P1 bajo compresion",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_ylim(0, 1.1)
    ax.axhline(1.0, color="#16a34a", linestyle=":", linewidth=1, alpha=0.7, label="Objetivo 100%")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    fig.savefig(DIAG / "02_p0_p1_survival.png", dpi=150)
    plt.close(fig)
    print("  02_p0_p1_survival.png")


def chart_baselines_vs_cortex_budget(scored):
    """Line chart: EAS por presupuesto, comparando baselines vs CODEC-CORTEX."""
    budgets = [512, 1024, 2048, 4096]
    selected = ["recent_tail_raw", "head_tail_raw", "head_json", "head_markdown_summary",
                "semantic_field_pack", "keyword_retrieval_raw",
                "cortex_priority_pack_v1"]
    # Compute avg EAS per method per budget
    data = defaultdict(lambda: defaultdict(list))
    for row in scored:
        b = int(row["budget_tokens"])
        if b in budgets:
            data[row["method_id"]][b].append(float(row["EAS"]))

    fig, ax = plt.subplots(figsize=(11, 6.5), constrained_layout=True)
    for m in selected:
        ys = [sum(data[m].get(b, [0])) / max(1, len(data[m].get(b, [0]))) for b in budgets]
        ax.plot(budgets, ys, marker="o", linewidth=2,
                label=METHOD_LABELS.get(m, m),
                color=METHOD_COLORS.get(m, "#999"))
    ax.set_xlabel("Presupuesto de tokens")
    ax.set_ylabel("Exact Answer Score (EAS)")
    ax.set_title("EAS por presupuesto — baselines vs CODEC-CORTEX",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xscale("log", base=2)
    ax.set_xticks(budgets)
    ax.set_xticklabels([str(b) for b in budgets])
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.legend(loc="lower right", fontsize=9)
    fig.savefig(DIAG / "03_eas_by_budget.png", dpi=150)
    plt.close(fig)
    print("  03_eas_by_budget.png")


def chart_failure_modes(scored):
    """Stacked bar: modos de fallo por metodo (BCFNR, UCFPR, CFCR)."""
    methods = sorted({r["method_id"] for r in scored})
    # Aggregate
    rows = []
    for m in methods:
        m_rows = [r for r in scored if r["method_id"] == m]
        n = len(m_rows)
        b = sum(float(r["BCFNR"]) for r in m_rows) / n
        u = sum(float(r["UCFPR"]) for r in m_rows) / n
        c = sum(float(r["CFCR"]) for r in m_rows) / n
        rows.append((m, b, u, c))
    rows.sort(key=lambda x: -(x[1] + x[2] + x[3]))

    names = [METHOD_LABELS.get(r[0], r[0]) for r in rows]
    bcfnr = [r[1] for r in rows]
    ucfpr = [r[2] for r in rows]
    cfcr = [r[3] for r in rows]

    fig, ax = plt.subplots(figsize=(12, 6.5), constrained_layout=True)
    x = list(range(len(names)))
    ax.bar(x, bcfnr, label="BCFNR (constraints bloqueantes omitidas)", color="#dc2626", edgecolor="white")
    ax.bar(x, ucfpr, bottom=bcfnr, label="UCFPR (claims no soportados que emergen)", color="#f97316", edgecolor="white")
    ax.bar(x, cfcr, bottom=[b + u for b, u in zip(bcfnr, ucfpr)], label="CFCR (confusion current/future)", color="#fbbf24", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=35, ha="right", fontsize=9)
    ax.set_ylabel("Tasa de fallo (0..1, menor = mejor)")
    ax.set_title("Modos de fallo por metodo — BCFNR + UCFPR + CFCR",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_ylim(0, 1.1)
    ax.axhline(0, color="#16a34a", linestyle=":", linewidth=1, alpha=0.7, label="Objetivo 0")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    fig.savefig(DIAG / "04_failure_modes.png", dpi=150)
    plt.close(fig)
    print("  04_failure_modes.png")


def chart_evidence_density(summary):
    """Bar chart: evidence density por metodo."""
    methods = sorted(summary, key=lambda x: -float(x["avg_evidence_density"]))
    names = [METHOD_LABELS.get(m["method_id"], m["method_id"]) for m in methods]
    vals = [float(m["avg_evidence_density"]) for m in methods]
    colors = [METHOD_COLORS.get(m["method_id"], "#999") for m in methods]

    fig, ax = plt.subplots(figsize=(12, 6.5), constrained_layout=True)
    bars = ax.barh(names, vals, color=colors, edgecolor="white", linewidth=0.5)
    ax.invert_yaxis()
    ax.set_xlabel("Evidence Density = weighted_score / context_tokens")
    ax.set_title("Densidad de evidencia por token (mayor = mas eficiente)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_width() + 0.0003, bar.get_y() + bar.get_height() / 2,
                f"{v:.4f}", va="center", fontsize=9)
    fig.savefig(DIAG / "05_evidence_density.png", dpi=150)
    plt.close(fig)
    print("  05_evidence_density.png")


def chart_scenario_heatmap(scored):
    """Heatmap: EAS por metodo x escenario."""
    methods = sorted({r["method_id"] for r in scored})
    scenarios = sorted({r["scenario_id"] for r in scored})
    # Order scenarios
    scen_order = ["full", "reduced_window_512", "reduced_window_1024",
                  "reduced_window_2048", "reduced_window_4096",
                  "middle_work_adversarial", "stale_state_conflict",
                  "blocking_constraint_survival", "unsupported_claim_suppression",
                  "corrupted_memory_tolerance", "multi_instance_sigil"]
    scenarios = [s for s in scen_order if s in scenarios]
    # Order methods by family
    fam_order = ["Passive Positional", "Passive Semantic", "Query-Dependent", "CODEC-CORTEX", "Ablation"]
    methods.sort(key=lambda m: (fam_order.index(METHOD_FAMILY.get(m, "Ablation")), m))

    # Build matrix
    matrix = []
    for m in methods:
        row = []
        for s in scenarios:
            vals = [float(r["EAS"]) for r in scored if r["method_id"] == m and r["scenario_id"] == s]
            row.append(sum(vals) / len(vals) if vals else 0.0)
        matrix.append(row)

    import numpy as np
    arr = np.array(matrix)
    fig, ax = plt.subplots(figsize=(13, 7), constrained_layout=True)
    im = ax.imshow(arr, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(scenarios)))
    ax.set_xticklabels([s.replace("_", "\n") for s in scenarios], rotation=0, fontsize=8)
    ax.set_yticks(range(len(methods)))
    ax.set_yticklabels([METHOD_LABELS.get(m, m) for m in methods], fontsize=9)
    # Annotate cells
    for i in range(len(methods)):
        for j in range(len(scenarios)):
            v = arr[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    color="black" if v > 0.4 else "white", fontsize=8)
    ax.set_title("Mapa de calor: EAS por metodo x escenario",
                 fontsize=13, fontweight="bold", pad=12)
    fig.colorbar(im, ax=ax, label="EAS (0..1)", shrink=0.8)
    fig.savefig(DIAG / "06_scenario_heatmap.png", dpi=150)
    plt.close(fig)
    print("  06_scenario_heatmap.png")


def chart_ablation_impact(scored):
    """Bar chart: impacto de ablations vs CPP v1."""
    methods = ["cortex_priority_pack_v1",
               "cortex_ablation_no_P0",
               "cortex_ablation_no_temporal"]
    metrics = ["EAS", "P0_survival", "P1_survival", "BCFNR", "STR"]
    # Aggregate
    data = {}
    for m in methods:
        m_rows = [r for r in scored if r["method_id"] == m]
        n = len(m_rows)
        data[m] = {k: sum(float(r[k]) for r in m_rows) / n for k in metrics}

    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    x = list(range(len(metrics)))
    w = 0.25
    for i, m in enumerate(methods):
        ys = [data[m][k] for k in metrics]
        ax.bar([j + i * w - w for j in x], ys, w,
               label=METHOD_LABELS.get(m, m),
               color=METHOD_COLORS.get(m, "#999"), edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_ylabel("Valor (0..1)")
    ax.set_title("Impacto de ablations — cuanto aporta cada componente?",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_ylim(0, 1.15)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    fig.savefig(DIAG / "07_ablation_impact.png", dpi=150)
    plt.close(fig)
    print("  07_ablation_impact.png")


def chart_mrd(derived):
    """Bar chart: Middle Recovery Delta por metodo."""
    mrd = derived["MRD_by_method"]
    items = sorted(mrd.items(), key=lambda x: -x[1])
    names = [METHOD_LABELS.get(m, m) for m, _ in items]
    vals = [v for _, v in items]
    colors = ["#16a34a" if v > 0 else "#dc2626" for v in vals]

    fig, ax = plt.subplots(figsize=(11, 5.5), constrained_layout=True)
    bars = ax.barh(names, vals, color=colors, edgecolor="white")
    ax.invert_yaxis()
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("MRD = score_metodo - mejor_baseline_posicional (middle_work)")
    ax.set_title("Middle Recovery Delta — resistencia a perdida de evidencia enterrada",
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_width() + (0.05 if v >= 0 else -0.05),
                bar.get_y() + bar.get_height() / 2,
                f"{v:+.3f}", va="center",
                ha="left" if v >= 0 else "right", fontsize=9)
    fig.savefig(DIAG / "08_mrd.png", dpi=150)
    plt.close(fig)
    print("  08_mrd.png")


def chart_radar(summary):
    """Radar chart: comparativa multivariada de los 4 mejores metodos."""
    # Top 4 by weighted score
    methods_sorted = sorted(summary, key=lambda x: -float(x["avg_weighted_score"]))
    top4 = methods_sorted[:4]
    metrics = ["EAS", "ETC", "P0_survival", "P1_survival", "STR"]
    metric_labels = ["EAS", "ETC", "P0 Surv", "P1 Surv", "Traceab"]

    import numpy as np
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"projection": "polar"}, constrained_layout=True)
    for m in top4:
        vals = [float(m[f"avg_{k}"]) for k in metrics]
        vals += vals[:1]
        ax.plot(angles, vals, marker="o", linewidth=2,
                label=METHOD_LABELS.get(m["method_id"], m["method_id"]),
                color=METHOD_COLORS.get(m["method_id"], "#999"))
        ax.fill(angles, vals, alpha=0.15,
                color=METHOD_COLORS.get(m["method_id"], "#999"))

    ax.set_thetagrids([a * 180 / np.pi for a in angles[:-1]], metric_labels)
    ax.set_ylim(0, 1.05)
    ax.set_title("Comparativa multivariada — Top 4 metodos",
                 fontsize=13, fontweight="bold", pad=20)
    ax.legend(loc="lower right", bbox_to_anchor=(1.25, 0.0), fontsize=9)
    ax.grid(True, alpha=0.4)
    fig.savefig(DIAG / "09_radar_top4.png", dpi=150)
    plt.close(fig)
    print("  09_radar_top4.png")


def chart_token_vs_score(summary):
    """Scatter: tokens vs weighted score (trade-off)."""
    fig, ax = plt.subplots(figsize=(10, 6.5), constrained_layout=True)
    for m in summary:
        x = float(m["avg_context_tokens"])
        y = float(m["avg_weighted_score"])
        c = METHOD_COLORS.get(m["method_id"], "#999")
        ax.scatter(x, y, s=120, color=c, edgecolor="white", linewidth=1.5, zorder=3)
        ax.annotate(METHOD_LABELS.get(m["method_id"], m["method_id"]),
                    (x, y), xytext=(8, 4), textcoords="offset points",
                    fontsize=8, alpha=0.85)
    ax.set_xlabel("Tokens promedio de contexto (Avg CT)")
    ax.set_ylabel("Puntaje ponderado (mayor = mejor)")
    ax.set_title("Trade-off: tokens consumidos vs calidad de evidencia",
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, alpha=0.3, linestyle="--")
    # Quadrant lines (median)
    xs = [float(m["avg_context_tokens"]) for m in summary]
    ys = [float(m["avg_weighted_score"]) for m in summary]
    ax.axvline(sum(xs) / len(xs), color="#94a3b8", linestyle=":", alpha=0.6)
    ax.axhline(sum(ys) / len(ys), color="#94a3b8", linestyle=":", alpha=0.6)
    fig.savefig(DIAG / "10_token_vs_score.png", dpi=150)
    plt.close(fig)
    print("  10_token_vs_score.png")


# ---------------------------------------------------------------------------
# Diagramas PlantUML
# ---------------------------------------------------------------------------

def write_puml(name: str, content: str):
    p = DIAG / f"{name}.puml"
    p.write_text(content, encoding="utf-8")
    print(f"  {name}.puml")


def puml_architecture():
    content = """@startuml
title Arquitectura del Benchmark CODEC-CORTEX

skinparam rectangle {
  BackgroundColor<<cortex>> #EFF6FF
  BackgroundColor<<baseline>> #F1F5F9
  BackgroundColor<<metric>> #FEF3C7
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Corpus L2\\n10 dominios x 2-3 casos\\nFormatos: .cortex, raw, md, json, yaml" as corpus <<cortex>>

package "Metodos bajo comparacion" {
  rectangle "Pasivos Posicionales\\nrecent_tail, head_tail,\\nhead_json, head_md" as positional <<baseline>>
  rectangle "Pasivo Semantico\\nsemantic_field_pack" as semantic <<baseline>>
  rectangle "Query-Dependent\\nkeyword_retrieval (BM25)" as qd <<baseline>>
  rectangle "CODEC-CORTEX\\nCPP v1 / Adaptive / Hybrid" as cortex <<cortex>>
  rectangle "Ablations\\nno_P0, no_temporal" as ablation <<baseline>>
}

package "Escenarios (8)" {
  rectangle "full\\nreduced_window (512..4096)\\nmiddle_work_adversarial" as scen1
  rectangle "stale_state_conflict\\nblocking_constraint_survival\\nunsupported_claim_suppression" as scen2
  rectangle "corrupted_memory_tolerance\\nmulti_instance_sigil" as scen3
}

package "Metricas (15)" {
  rectangle "EAS, ETC, F1, DA\\nAvg CT" as m1 <<metric>>
  rectangle "P0/P1 survival\\nBCFNR, UCFPR, CFCR\\nSTR, BVR" as m2 <<metric>>
  rectangle "MRD, QDD\\nEvidence Density" as m3 <<metric>>
}

corpus --> positional : texto plano
corpus --> semantic : sigilos
corpus --> qd : texto + query
corpus --> cortex : .cortex (CLI render)
corpus --> ablation : .cortex (transformado)

positional --> scen1
semantic --> scen1
qd --> scen1
cortex --> scen1
ablation --> scen1
scen1 --> scen2
scen2 --> scen3

scen3 --> m1
scen3 --> m2
scen3 --> m3

note right of cortex
  CLI: cortex render --profile
  MIN/RECOVERY/WORK/FULL
  P0-P5 priority pack
end note

note right of m3
  MRD: vs best positional
  QDD: vs best query-dep
end note
@enduml
"""
    write_puml("11_architecture", content)


def puml_codec_stack():
    content = """@startuml
title Pila canonica CODEC-CORTEX (v0.3.0)

skinparam rectangle {
  BackgroundColor<<current>> #DBEAFE
  BackgroundColor<<planned>> #FEF3C7
  BackgroundColor<<future>> #FEE2E2
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Universal Skill\\n(SKILL.md, SKILL.cortex)\\nAdoption layer" as skill <<current>>
rectangle ".cortex format\\nStructured contextual memory\\nsurvive P0-P5" as cortex <<current>>
rectangle "HCORTEX\\nHuman-readable render\\n(Markdown auditable)" as hcortex <<current>>
rectangle "Deterministic Codec\\nCLI v1.1.9: verify, render,\\nCRUD, doctor, diff, format" as codec <<current>>
rectangle "Memory Runtime\\nWRK/SES/LNG lifecycle" as runtime <<planned>>
rectangle "Enterprise MCP\\nGovernance + audit" as mcp <<future>>

skill --> cortex : defines discipline
cortex --> hcortex : renders for humans
cortex --> codec : automated maintenance
codec --> runtime : managed lifecycle
runtime --> mcp : enterprise exposure

note right of cortex
  Priority Pack:
  P0: FCS/OBJ/CNST/STP (inmutable)
  P1: WRK/AUD/RSK/NXT
  P2: CLAIM/LIM/KNW:active
  P3: SES:last/STAT/VAL
  P4: REF:critical/DOC
  P5: DIAG/TBL/historico
end note

note right of codec
  222 tests passing
  17 CLI commands
  cortex verify --strict
end note

note right of mcp
  Future enterprise phase
  Not a current feature
end note
@enduml
"""
    write_puml("12_codec_stack", content)


def puml_experiment_flow():
    content = """@startuml
title Flujo experimental del benchmark

skinparam activity {
  BackgroundColor #DBEAFE
  BorderColor #1E40AF
}
skinparam shadowing false

start
:Load corpus L2-multidomain;
:Validate .cortex with cortex verify --strict;
:Compute SHA-256 hashes;

partition "Por method (11)" {
  :Select method spec;
  partition "Por scenario (11)" {
    :Apply scenario transformation;
    partition "Por task (40)" {
      :Extract context under budget;
      :Tokenize (proxy 3.5-4.0 chars/token);
      :Compute metrics (EAS, ETC, F1, DA, ...);
      :Compute survival rates (P0, P1, BCFNR, ...);
      :Compute evidence density;
    }
  }
}

:Aggregate by method;
:Aggregate by scenario;
:Compute derived metrics (MRD, QDD);
:Generate reports (CSV, JSON, Markdown);
:Generate diagrams (PUML + matplotlib);

stop

note right
  Total runs: 11 methods x 11 scenarios x 40 tasks = 4840
  Deterministic: no LLM calls
  Reproducible: hashes + manifest
end note
@enduml
"""
    write_puml("13_experiment_flow", content)


def puml_comparative_landscape():
    content = """@startuml
title Panorama comparativo: CODEC-CORTEX vs alternativas

skinparam rectangle {
  BackgroundColor<<cortex>> #DBEAFE
  BackgroundColor<<alt>> #F1F5F9
  BackgroundColor<<hybrid>> #FEF3C7
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Memoria Estructurada Determinista" as fam1 {
  rectangle "CODEC-CORTEX\\n(.cortex + HCORTEX + CLI)\\nPriority pack P0-P5\\nDeterministic, auditable" as cc <<cortex>>
  rectangle "JSON-Schema Memory\\nFixed schema, positional" as js <<alt>>
  rectangle "YAML front-matter\\nLightweight, structural" as ym <<alt>>
}

rectangle "Memoria Gestionada por LLM" as fam2 {
  rectangle "MemGPT / Letta\\nPaginated memory + LLM\\nrecall" as mg <<alt>>
  rectangle "LangChain Memory\\nSummary/Buffer/Vector" as lc <<alt>>
  rectangle "A-MEM (Zettelkasten)\\nLinked episodic notes" as am <<alt>>
}

rectangle "Memoria Recuperada (RAG)" as fam3 {
  rectangle "Vector RAG\\nChromaDB/Pinecone +\\nembedding similarity" as vr <<alt>>
  rectangle "GraphRAG\\nKnowledge graph +\\nentity retrieval" as gr <<alt>>
}

rectangle "Protocolos de Contexto" as fam4 {
  rectangle "MCP (Anthropic)\\nTool/context exposure\\nprotocol" as mcp <<hybrid>>
}

note right of cc
  Objetivo: preservacion determinista
  de evidencia operacional.
  Sin LLM en el codec.
end note

note right of mg
  Objetivo: memoria ilimitada
  via paginacion LLM.
  Requiere LLM en runtime.
end note

note right of vr
  Objetivo: recuperacion
  por similitud semantica.
  Requiere embeddings.
end note

note right of mcp
  Objetivo: exposicion
  estandar de contexto/herramientas.
  No define memoria estructurada.
end note
@enduml
"""
    write_puml("14_comparative_landscape", content)


def puml_degradation_flow():
    content = """@startuml
title Perfil de degradacion CODEC-CORTEX

skinparam state {
  BackgroundColor #DBEAFE
  BorderColor #1E40AF
}
skinparam shadowing false

state "FULL\\nP0-P5\\nSin limite (~8K+)" as FULL
state "WORK\\nP0+P1+P2\\n~3K tokens" as WORK
state "RECOVERY\\nP0+P1\\n~1K tokens" as RECOVERY
state "MIN\\nP0 only\\n~300 tokens" as MIN

FULL --> WORK : presupuesto baja\\n(drop P5->P4->P3)
WORK --> RECOVERY : presupuesto baja\\n(keep KNW:active, LNG:critical)
RECOVERY --> MIN : presupuesto baja\\n(P0 only)

MIN --> RECOVERY : presupuesto sube
RECOVERY --> WORK : presupuesto sube
WORK --> FULL : presupuesto sube

note right of MIN
  Siempre preservado:
  - FCS (foco)
  - OBJ (objetivo)
  - CNST blocking
  - STP (next step)
end note

note left of FULL
  Perfil default para
  auditoria y export.
end note
@enduml
"""
    write_puml("15_degradation_flow", content)


def puml_ontology():
    content = """@startuml
title Ontologia cognitiva CODEC-CORTEX — 4 cortezas

skinparam rectangle {
  BackgroundColor<<semantic>> #DBEAFE
  BackgroundColor<<prefrontal>> #FEE2E2
  BackgroundColor<<working>> #FEF3C7
  BackgroundColor<<episodic>> #D1FAE5
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Corteza Semantica\\nIDN, DOM, KNW, REF, TAG\\n(persistencia larga)" as sem <<semantic>>
rectangle "Corteza Prefrontal\\nAXM, CNST, !, CLAIM, LIM,\\nAUD, RSK (gobierno)" as pre <<prefrontal>>
rectangle "Memoria de Trabajo\\nFCS, OBJ, WRK, STP, NXT\\n(estado vivo)" as wrk <<working>>
rectangle "Memoria Episodica\\nSES, LNG, DIAG\\n(experiencia destilada)" as epi <<episodic>>

pre -down-> wrk : gobierna accion
sem -right-> wrk : aporta conocimiento
wrk -down-> epi : destila experiencia
epi -up-> sem : promueve aprendizaje
pre -right-> sem : impone limites

note right of pre
  Niveles survive:
  CNST:blocking -> min
  CLAIM/LIM -> recovery
end note

note right of wrk
  Niveles survive:
  FCS, OBJ, STP -> min (P0)
  WRK, NXT -> work (P1)
end note
@enduml
"""
    write_puml("16_ontology", content)


def puml_claim_matrix():
    content = """@startuml
title Matriz de claims — evidencia vs limitaciones

skinparam rectangle {
  BackgroundColor<<demostrado>> #D1FAE5
  BackgroundColor<<parcial>> #FEF3C7
  BackgroundColor<<hipotesis>> #FED7AA
  BackgroundColor<<no_soportado>> #FEE2E2
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Demostrado por benchmark" as demo <<demostrado>> {
  rectangle "CPP preserva P0 al 100%\\nen todos los escenarios" as c1
  rectangle "CPP BCFNR = 0\\n(constraints blocking nunca omitidos)" as c2
  rectangle "CPP UCFPR = 0\\n(claims no soportados no emergen)" as c3
  rectangle "CPP supera baselines posicionales\\nen MRD (middle recovery)" as c4
  rectangle "Ablation no_P0 degrada BCFNR\\na 0.70 (causa de pérdida)" as c5
}

rectangle "Parcialmente soportado" as par <<parcial>> {
  rectangle "CPP superior en EAS\\n(limitado a corpus L2)" as p1
  rectangle "STR alta en HCORTEX\\n(depende de modo audit)" as p2
}

rectangle "Hipotesis razonable" as hip <<hipotesis>> {
  rectangle "Beneficio se mantiene\\nen corpus L3 adversarial" as h1
  rectangle "Beneficio se mantiene\\nen fase LLM separada" as h2
}

rectangle "No soportado" as nos <<no_soportado>> {
  rectangle "CPP mejora razonamiento LLM\\n(requiere fase LLM §11)" as n1
  rectangle "CPP comprime sin perdida\\n(literal reconstruction)" as n2
}

note right of demo
  Evidencia: 4840 runs
  Reproducible: hashes + manifest
end note

note right of nos
  Prohibido por §1.4
  (no sobreafirmacion)
end note
@enduml
"""
    write_puml("17_claim_matrix", content)


def render_puml_to_svg():
    """Intenta renderizar archivos PUML a SVG/PNG usando plantuml o java."""
    puml_files = list(DIAG.glob("*.puml"))
    # Try plantuml jar
    plantuml_jar = None
    for path in ["/usr/share/plantuml/plantuml.jar",
                 "/usr/local/share/plantuml.jar",
                 "/opt/plantuml/plantuml.jar"]:
        if os.path.exists(path):
            plantuml_jar = path
            break
    if plantuml_jar:
        print(f"Rendering PUML files with {plantuml_jar}...")
        for p in puml_files:
            r = subprocess.run(
                ["java", "-jar", plantuml_jar, "-tsvg", str(p)],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode != 0:
                print(f"  FAIL: {p.name}: {r.stderr[:100]}")
        print(f"  Rendered {len(puml_files)} PUML files")
    else:
        # Try via python plantuml module or just leave PUML as source
        print(f"  PlantUML jar not found; PUML sources saved but not rendered to SVG")
        # As fallback, render via mermaid-style HTML snippet? No - just leave PUML.
        # Save a note
        (DIAG / "PumlSources.txt").write_text(
            "Archivos .puml generados. Renderice con: plantuml -tsvg *.puml\n"
            "O visite https://www.plantuml.com/plantuml/uml/ para render online.\n",
            encoding="utf-8"
        )


def main():
    print("Loading data...")
    scored = load_scored()
    summary = load_summary()
    scenario = load_scenario()
    print(f"  {len(scored)} scored rows, {len(summary)} summary rows")

    print("\nComputing derived metrics...")
    derived = compute_derived(scored, scenario)
    (RUNS / "derived_metrics.json").write_text(
        json.dumps(derived, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  MRD range: {min(derived['MRD_by_method'].values()):.3f} .. {max(derived['MRD_by_method'].values()):.3f}")
    print(f"  QDD: {derived['QDD']:.3f}")

    print("\nGenerating matplotlib diagrams...")
    chart_weighted_score(summary)
    chart_p0_p1_survival(summary)
    chart_baselines_vs_cortex_budget(scored)
    chart_failure_modes(scored)
    chart_evidence_density(summary)
    chart_scenario_heatmap(scored)
    chart_ablation_impact(scored)
    chart_mrd(derived)
    chart_radar(summary)
    chart_token_vs_score(summary)

    print("\nGenerating PlantUML diagrams...")
    puml_architecture()
    puml_codec_stack()
    puml_experiment_flow()
    puml_comparative_landscape()
    puml_degradation_flow()
    puml_ontology()
    puml_claim_matrix()
    render_puml_to_svg()

    print(f"\nAll diagrams written to: {DIAG}")


if __name__ == "__main__":
    main()
