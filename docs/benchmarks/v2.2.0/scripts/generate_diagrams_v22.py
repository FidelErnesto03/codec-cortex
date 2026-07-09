#!/usr/bin/env python3
"""Genera diagramas del benchmark v2.2.0, incluyendo Learning Engine y progresión 4 versiones."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf')
fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
plt.rcParams['font.sans-serif'] = ['Noto Serif SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

BASE = Path("/home/z/my-project/download/benchmark-cortex-v22")
RUNS = BASE / "runs"
DIAG = BASE / "diagrams"
DIAG.mkdir(parents=True, exist_ok=True)

METHOD_LABELS = {
    "recent_tail_raw": "Recent Tail Raw",
    "head_tail_raw": "Head+Tail Raw",
    "head_json": "Head JSON",
    "head_markdown_summary": "Head Markdown",
    "semantic_field_pack": "Semantic Field Pack",
    "keyword_retrieval_raw": "Keyword Retrieval",
    "cortex_priority_pack_v1": "CORTEX PP v1 (CLI v1)",
    "cortex_priority_pack": "CORTEX PP v2 (CLI v0.3.6)",
    "cortex_canonical": "CORTEX Canonical v2",
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
    "cortex_priority_pack": "#7c3aed",
    "cortex_canonical": "#9333ea",
    "cortex_ablation_no_P0": "#dc2626",
    "cortex_ablation_no_temporal": "#b91c1c",
}


def load_summary():
    with open(RUNS / "summary_tasks.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def chart_v22_weighted(summary):
    """Bar chart: weighted score por metodo v2.2.0."""
    methods = sorted(summary, key=lambda x: -float(x["avg_weighted_score"]))
    names = [METHOD_LABELS.get(m["method_id"], m["method_id"]) for m in methods]
    scores = [float(m["avg_weighted_score"]) for m in methods]
    colors = [METHOD_COLORS.get(m["method_id"], "#999") for m in methods]

    fig, ax = plt.subplots(figsize=(13, 6.5), constrained_layout=True)
    bars = ax.barh(names, scores, color=colors, edgecolor="white", linewidth=0.5)
    ax.invert_yaxis()
    ax.set_xlabel("Puntaje ponderado (mayor = mejor)")
    ax.set_title("Benchmark v2.2.0 — Comparativa global (CLI v0.3.6 + Learning Engine v0.1.0)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.1 if score > 0 else bar.get_width() - 0.1,
                bar.get_y() + bar.get_height() / 2,
                f"{score:.2f}", va="center",
                ha="left" if score > 0 else "right", fontsize=9)
    legend_handles = [
        mpatches.Patch(facecolor="#2563eb", label="CODEC-CORTEX v1 (CLI v1)"),
        mpatches.Patch(facecolor="#7c3aed", label="CODEC-CORTEX v2 (CLI v0.3.6)"),
        mpatches.Patch(facecolor="#94a3b8", label="Baselines posicionales"),
        mpatches.Patch(facecolor="#fbbf24", label="Pasivo semántico"),
        mpatches.Patch(facecolor="#f97316", label="Query-dependent"),
        mpatches.Patch(facecolor="#dc2626", label="Ablations"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=8, framealpha=0.9)
    fig.savefig(DIAG / "01_v22_weighted.png", dpi=150)
    plt.close(fig)
    print("  01_v22_weighted.png")


def chart_progression_4_versions():
    """Bar chart: progresión WS de CPP entre v1.0.0, v2.0.0, v2.1.0, v2.2.0."""
    versions = ["v1.0.0\n(CLI v1.1.9)", "v2.0.0\n(CLI v2.4.0)", "v2.1.0\n(CLI v0.3.2)", "v2.2.0\n(CLI v0.3.6)"]
    ws_scores = [7.03, 7.03, 9.31, 9.47]
    view_cov = [0.0, 0.0, 1.00, 1.00]
    reversibility = [0.0, 0.0, 1.0, 1.0]
    learn_c = [0.0, 0.0, 0.0, 1.05]  # v2.2 NEW
    colors = ["#2563eb", "#7c3aed", "#9333ea", "#c026d3"]

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)

    # WS
    ax = axes[0, 0]
    bars = ax.bar(versions, ws_scores, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_ylabel("Weighted Score")
    ax.set_title("Progresión WS de CORTEX Priority Pack", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, score in zip(bars, ws_scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{score:.2f}", ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 11)

    # VIEW coverage
    ax = axes[0, 1]
    bars = ax.bar(versions, view_cov, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_ylabel("VIEW Coverage (0..1)")
    ax.set_title("VIEW Coverage", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, view_cov):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{v:.2f}", ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.15)

    # Reversibility
    ax = axes[1, 0]
    bars = ax.bar(versions, reversibility, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_ylabel("Reversibility (0/1)")
    ax.set_title("Reversibility", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, reversibility):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{v:.0f}", ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.15)

    # Learning candidates (v2.2 NEW)
    ax = axes[1, 1]
    bars = ax.bar(versions, learn_c, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_ylabel("Learning Candidates (avg)")
    ax.set_title("Learning Candidates (NEW v2.2.0)", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, learn_c):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{v:.2f}", ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.2)

    fig.suptitle("Progresión del benchmark: v1.0.0 → v2.0.0 → v2.1.0 → v2.2.0",
                 fontsize=14, fontweight="bold", y=1.01)
    fig.savefig(DIAG / "02_progression_4_versions.png", dpi=150)
    plt.close(fig)
    print("  02_progression_4_versions.png")


def chart_learning_engine(summary):
    """Bar chart: métricas de Learning Engine por método."""
    cortex_methods = [s for s in summary if s["method_id"].startswith("cortex")]
    names = [METHOD_LABELS.get(m["method_id"], m["method_id"]) for m in cortex_methods]
    learn_c = [float(m["avg_learn_candidates"]) for m in cortex_methods]
    learn_p = [float(m["avg_learn_promotion_score"]) for m in cortex_methods]
    learn_e = [float(m["avg_learn_elevations"]) for m in cortex_methods]
    learn_h = [float(m["avg_learn_hotness_avg"]) for m in cortex_methods]

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)

    ax = axes[0, 0]
    bars = ax.barh(names, learn_c, color="#7c3aed", edgecolor="white")
    ax.invert_yaxis()
    ax.set_xlabel("Learning Candidates (avg per run)")
    ax.set_title("Learning Candidates Detected", fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, learn_c):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{v:.2f}", va="center", fontsize=9)

    ax = axes[0, 1]
    bars = ax.barh(names, learn_p, color="#9333ea", edgecolor="white")
    ax.invert_yaxis()
    ax.set_xlabel("Promotion Score (avg, Fibonacci scale)")
    ax.set_title("Learning Promotion Score", fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, learn_p):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{v:.2f}", va="center", fontsize=9)
    # Fibonacci thresholds
    ax.axvline(5, color="#f59e0b", linestyle=":", alpha=0.7, label="candidate (5)")
    ax.axvline(8, color="#dc2626", linestyle=":", alpha=0.7, label="ask_user (8)")
    ax.axvline(13, color="#7c2d12", linestyle=":", alpha=0.7, label="strong (13)")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    bars = ax.barh(names, learn_e, color="#a855f7", edgecolor="white")
    ax.invert_yaxis()
    ax.set_xlabel("Elevation Candidates (avg)")
    ax.set_title("Learning Elevation Candidates", fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, learn_e):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{v:.2f}", va="center", fontsize=9)

    ax = axes[1, 1]
    bars = ax.barh(names, learn_h, color="#c084fc", edgecolor="white")
    ax.invert_yaxis()
    ax.set_xlabel("Hotness Score (avg)")
    ax.set_title("Learning Hotness Score", fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, learn_h):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{v:.2f}", va="center", fontsize=9)

    fig.suptitle("CODEC-CORTEX Learning Engine v0.1.0 — Métricas por método",
                 fontsize=14, fontweight="bold", y=1.01)
    fig.savefig(DIAG / "03_learning_engine.png", dpi=150)
    plt.close(fig)
    print("  03_learning_engine.png")


def chart_learning_per_case():
    """Bar chart: learning candidates por caso del corpus."""
    # Read from pre-computed logs or re-run
    import subprocess
    cases_data = []
    cases = ["devops-k8s-rollout", "ecom-fraud-checkout", "health-medication-alert",
             "fintech-aml-kyc", "iot-hvac-anomaly", "legal-contract-redline",
             "edu-adaptive-lesson", "sec-incident-response", "robotics-warehouse-bot",
             "climate-grid-balancing"]
    # Use cached results from learning_workspaces
    for case_id in cases:
        ws_path = BASE / "learning_workspaces" / case_id
        if not ws_path.exists():
            continue
        try:
            r = subprocess.run(
                ["/home/z/.venv/bin/python", "-m", "cortex", "learn", "scan",
                 "--workspace", str(ws_path), "--json"],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode == 0 and r.stdout.strip():
                try:
                    data = json.loads(r.stdout)
                    entries = data.get("entries", [])
                    if isinstance(entries, list):
                        candidates = len(entries)
                        prom_scores = [e.get("promotion_score", 0) for e in entries if isinstance(e, dict)]
                        elevations = sum(1 for e in entries if isinstance(e, dict) and e.get("suggested_action") == "consider_elevation")
                        avg_prom = sum(prom_scores) / len(prom_scores) if prom_scores else 0
                        cases_data.append({
                            "case": case_id,
                            "candidates": candidates,
                            "avg_prom": avg_prom,
                            "elevations": elevations,
                        })
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

    if not cases_data:
        print("  04_learning_per_case.png (no data)")
        return

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), constrained_layout=True)
    names = [c["case"][:18] for c in cases_data]
    x = list(range(len(names)))

    ax = axes[0]
    bars = ax.bar(x, [c["candidates"] for c in cases_data], color="#7c3aed", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Candidates")
    ax.set_title("Learning Candidates per Case", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, [c["candidates"] for c in cases_data]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                str(v), ha="center", fontsize=8)

    ax = axes[1]
    bars = ax.bar(x, [c["avg_prom"] for c in cases_data], color="#9333ea", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Avg Promotion Score")
    ax.set_title("Avg Promotion Score per Case", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.axhline(5, color="#f59e0b", linestyle=":", alpha=0.7, label="candidate (5)")
    ax.axhline(8, color="#dc2626", linestyle=":", alpha=0.7, label="ask_user (8)")
    ax.legend(fontsize=8)
    for bar, v in zip(bars, [c["avg_prom"] for c in cases_data]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{v:.1f}", ha="center", fontsize=8)

    ax = axes[2]
    bars = ax.bar(x, [c["elevations"] for c in cases_data], color="#a855f7", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Elevation Candidates")
    ax.set_title("Elevation Candidates per Case", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, [c["elevations"] for c in cases_data]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                str(v), ha="center", fontsize=8)

    fig.suptitle("Learning Engine por caso del corpus (CLE v0.1.0, golden_fibonacci_v1)",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.savefig(DIAG / "04_learning_per_case.png", dpi=150)
    plt.close(fig)
    print("  04_learning_per_case.png")


def chart_security_e2(summary):
    """Bar chart: E2 security — secrets detected por método."""
    methods = summary
    names = [METHOD_LABELS.get(m["method_id"], m["method_id"]) for m in methods]
    secrets = [float(m["avg_secret_count"]) for m in methods]
    colors = ["#16a34a" if v == 0 else "#dc2626" for v in secrets]

    fig, ax = plt.subplots(figsize=(11, 5.5), constrained_layout=True)
    bars = ax.barh(names, secrets, color=colors, edgecolor="white", linewidth=0.5)
    ax.invert_yaxis()
    ax.set_xlabel("Secrets Detected (E2 Security, menor = mejor)")
    ax.set_title("E2 Security: Secret Scanner (cortex doctor --scan-secrets)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, secrets):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{v:.0f}", va="center", fontsize=9)
    ax.set_xlim(0, max(secrets) + 1 if max(secrets) > 0 else 1)
    fig.savefig(DIAG / "05_security_e2.png", dpi=150)
    plt.close(fig)
    print("  05_security_e2.png")


def chart_token_vs_score_v22(summary):
    """Scatter: tokens vs score para v2.2.0."""
    fig, ax = plt.subplots(figsize=(11, 6.5), constrained_layout=True)
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
    ax.set_title("v2.2.0 — Trade-off: tokens vs calidad de evidencia",
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, alpha=0.3, linestyle="--")
    xs = [float(m["avg_context_tokens"]) for m in summary]
    ys = [float(m["avg_weighted_score"]) for m in summary]
    ax.axvline(sum(xs) / len(xs), color="#94a3b8", linestyle=":", alpha=0.6)
    ax.axhline(sum(ys) / len(ys), color="#94a3b8", linestyle=":", alpha=0.6)
    fig.savefig(DIAG / "06_token_vs_score_v22.png", dpi=150)
    plt.close(fig)
    print("  06_token_vs_score_v22.png")


def chart_radar_top4_v22(summary):
    """Radar top-4 métodos v2.2.0 con learning metrics."""
    import numpy as np
    methods_sorted = sorted(summary, key=lambda x: -float(x["avg_weighted_score"]))
    top4 = methods_sorted[:4]
    # Normalize learning metrics to 0..1 for radar
    metrics = ["EAS", "P0_survival", "STR", "VIEW_coverage", "reversibility", "learn_norm"]
    metric_labels = ["EAS", "P0 Surv", "Traceab", "VIEW cov", "Reversib", "Learn (norm)"]

    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"projection": "polar"}, constrained_layout=True)
    for m in top4:
        # Normalize learn_candidates (max ~1.05 -> 1.0)
        learn_norm = min(float(m["avg_learn_candidates"]) / 1.5, 1.0)
        vals = [
            float(m["avg_EAS"]),
            float(m["avg_P0_survival"]),
            float(m["avg_STR"]),
            float(m["avg_VIEW_coverage"]),
            float(m["avg_reversibility"]),
            learn_norm,
        ]
        vals += vals[:1]
        ax.plot(angles, vals, marker="o", linewidth=2,
                label=METHOD_LABELS.get(m["method_id"], m["method_id"]),
                color=METHOD_COLORS.get(m["method_id"], "#999"))
        ax.fill(angles, vals, alpha=0.15,
                color=METHOD_COLORS.get(m["method_id"], "#999"))

    ax.set_thetagrids([a * 180 / np.pi for a in angles[:-1]], metric_labels)
    ax.set_ylim(0, 1.05)
    ax.set_title("Radar Top-4 métodos v2.2.0 (incluye Learning Engine)",
                 fontsize=13, fontweight="bold", pad=20)
    ax.legend(loc="lower right", bbox_to_anchor=(1.25, 0.0), fontsize=9)
    ax.grid(True, alpha=0.4)
    fig.savefig(DIAG / "07_radar_top4_v22.png", dpi=150)
    plt.close(fig)
    print("  07_radar_top4_v22.png")


def puml_v22_architecture():
    content = """@startuml
title Arquitectura Benchmark v2.2.0 — CLI v0.3.6 + Learning Engine v0.1.0

skinparam rectangle {
  BackgroundColor<<cortex_v1>> #DBEAFE
  BackgroundColor<<cortex_v2>> #EDE9FE
  BackgroundColor<<baseline>> #F1F5F9
  BackgroundColor<<learning>> #DCFCE7
  BackgroundColor<<security>> #FEF3C7
  BackgroundColor<<metric>> #FCE7F3
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Corpus L2 v2.1 (VIEW migrated)\\n10 dominios, 108 VIEW directives\\n100% coverage, reversible" as corpus <<baseline>>

package "Metodos (11)" {
  rectangle "Pasivos (4) + Semantico (1)\\n+ Query-Dep (1)" as baselines <<baseline>>
  rectangle "CODEC-CORTEX v1\\nCPP v1 (render --profile)" as cortex_v1 <<cortex_v1>>
  rectangle "CODEC-CORTEX v2 (2)\\nCPP v2 + Canonical\\n(convert + canonicalize)" as cortex_v2 <<cortex_v2>>
  rectangle "Ablations (2)\\nno_P0, no_temporal" as ablation <<baseline>>
}

package "NUEVO v2.2.0: Learning Engine" {
  rectangle "CODEC-CORTEX Learning Engine\\n(CLE) v0.1.0" as cle <<learning>>
  rectangle "cortex learn scan\\ncortex learn candidates\\ncortex learn elevate" as learn_cmds <<learning>>
  rectangle "golden_fibonacci_v1\\nscoring algorithm\\n(observed=1, repeated=2,\\npattern=3, candidate=5,\\nask_user=8, strong=13)" as scoring <<learning>>
}

package "NUEVO v2.2.0: E2 Security" {
  rectangle "cortex doctor --scan-secrets\\n(12 patrones)" as secrets <<security>>
  rectangle "cortex audit on/off/status\\ncortex --mode read-only|editor|admin\\ncortex verify --signature" as audit <<security>>
}

package "Metricas (24)" {
  rectangle "v1.0 (15): EAS, ETC, F1, DA,\\nP0/P1, BCFNR, UCFPR, CFCR,\\nSTR, BVR, MRD, QDD, ED, Avg CT" as m1 <<metric>>
  rectangle "v2.0 (4): VIEW_cov, reversibility,\\nbidir_equiv, loss_count" as m2 <<metric>>
  rectangle "v2.2 NEW (5): learn_candidates,\\nlearn_promotion_score, learn_elevations,\\nlearn_hotness_avg, secret_count" as m3 <<metric>>
}

corpus --> baselines
corpus --> cortex_v1
corpus --> cortex_v2
corpus --> ablation
corpus --> cle
cle --> learn_cmds
cle --> scoring
corpus --> secrets
corpus --> audit

cortex_v2 --> m1
cortex_v2 --> m2
cortex_v2 --> m3
cle --> m3
secrets --> m3

note right of cle
  NUEVO en v0.3.6:
  Learning Engine determinista,
  local-first, sin LLM.
  Detecta candidatos de
  elevacion SES/LNG -> KNW.
end note

note right of scoring
  Fibonacci thresholds:
  5=candidate, 8=ask_user,
  13=strong_candidate, 21=critical.
  Promedio corpus: 0.65 (sobre 1.05
  candidates por run).
end note
@enduml
"""
    (DIAG / "08_v22_architecture.puml").write_text(content, encoding="utf-8")
    print("  08_v22_architecture.puml")


def puml_v22_findings():
    content = """@startuml
title Hallazgos clave del benchmark v2.2.0

skinparam rectangle {
  BackgroundColor<<positive>> #D1FAE5
  BackgroundColor<<neutral>> #FEF3C7
  BackgroundColor<<new>> #DCFCE7
  BackgroundColor<<finding>> #EDE9FE
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Novedades v2.2.0" as nov <<new>> {
  rectangle "Learning Engine v0.1.0\\n(cortex learn scan/candidates/elevate)\\nFunciona: 1.05 candidates/run\\n0.65 promotion_score" as n1
  rectangle "E2 Security\\n0 secrets en corpus limpio\\naudit + scan-secrets + --mode" as n2
  rectangle "SKILL v1.3.0\\nReescrito en HCORTEX\\n35 VIEW directives\\nAGENT.md con KNW CLI" as n3
}

rectangle "Resultados positivos" as pos <<positive>> {
  rectangle "CORTEX PP v2 = ganador\\nWS = 9.47 (+2.29 vs v1)\\n(+0.16 vs v2.1.0)" as r1
  rectangle "Learning metrics activas\\nen todos los metodos CODEC\\n(1.05, 0.65, 0.58, 0.0)" as r2
  rectangle "MRD = +4.38\\n(igual que v2.1.0)\\nVentaja mantenida" as r3
  rectangle "QDD = -6.39\\n(vs -6.24 en v2.1.0)\\nLigera ampliacion" as r4
  rectangle "BCFNR = 0 mantenido\\n0 secrets detectados\\nCorpus seguro" as r5
}

rectangle "Trade-offs" as trade <<neutral>> {
  rectangle "EAS 0.950 (mantiene v2.1)\\nNombres canonicos v2\\nPersiste vs v1" as t1
  rectangle "+130 tokens vs v1\\n(menos que v2.1: +396)\\nPor learning scan en full" as t2
}

rectangle "Issues pendientes" as pend <<neutral>> {
  rectangle "roundtrip-bidir direction 1\\nE_TABLE_SCHEMA_MISMATCH\\n(known limitation, CI non-blocking)" as p1
  rectangle "SKILL canónico 21% VIEW coverage\\n(synthetic_knw entries no cubiertas)\\n vs corpus 100%" as p2
}

nov --> pos
pos --> trade
pos --> pend

note right of nov
  v0.3.6 anade:
  - Learning Engine (CLE v0.1.0)
  - E2 Security (secret scanner)
  - SKILL v1.3.0 (HCORTEX)
  - AGENT.md actualizado
end note
@enduml
"""
    (DIAG / "09_v22_findings.puml").write_text(content, encoding="utf-8")
    print("  09_v22_findings.puml")


def puml_learning_flow():
    content = """@startuml
title Flujo del Learning Engine (CLE v0.1.0)

skinparam activity {
  BackgroundColor #DCFCE7
  BorderColor #16A34A
}
skinparam shadowing false

start
:cortex learn init --workspace;
:Creates .cortex/ with:
- MANIFEST.cortex
- brain.cortex
- learn-policies.cortex
- index/ dir
- cache/ dir;

:cortex learn scan --workspace;
:Scans brain.cortex entries;
:Applies golden_fibonacci_v1 scoring;
:Signals: observed, repeated, pattern, candidate;

if (Promotion score >= 5?) then (yes)
  :Mark as candidate;
  if (Promotion score >= 8?) then (yes)
    :Suggest elevation (ask_user);
    if (Promotion score >= 13?) then (yes)
      :Strong candidate;
    else (no)
      :Regular candidate;
    endif
  else (no)
    :Track for future;
  endif
else (no)
  :No elevation yet;
endif

:cortex learn candidates;
:List all candidates with:
- source_entries
- target (e.g., NXT->STP)
- promotion_score
- hotness_score
- suggested_action;

if (User confirms?) then (yes)
  :cortex learn elevate;
  :Apply policy-driven mutation;
  :SES -> LNG (if score >= 8);
  :LNG -> KNW (if score >= 13);
  :Update brain.cortex;
  :Log AUD entry;
else (no)
  :Keep tracking;
endif

stop

note right
  Deterministic, local-first.
  No LLM, no network.
  Indices rebuildable.
  LLM cannot edit brain directly.
end note
@enduml
"""
    (DIAG / "10_learning_flow.puml").write_text(content, encoding="utf-8")
    print("  10_learning_flow.puml")


def render_puml_files():
    from plantweb.plantuml import plantuml
    for p in sorted(DIAG.glob("*.puml")):
        try:
            content = p.read_text()
            out = plantuml('http://www.plantuml.com/plantuml', 'png', content)
            out_bytes = out if isinstance(out, bytes) else out.encode('utf-8')
            out_path = p.with_suffix('.png')
            out_path.write_bytes(out_bytes)
            print(f"  {p.name} -> {out_path.name}")
        except Exception as e:
            print(f"  FAIL: {p.name}: {e}")


def main():
    print("Loading data...")
    summary = load_summary()
    print(f"  {len(summary)} summary rows")

    print("\nGenerating v2.2.0 diagrams...")
    chart_v22_weighted(summary)
    chart_progression_4_versions()
    chart_learning_engine(summary)
    chart_learning_per_case()
    chart_security_e2(summary)
    chart_token_vs_score_v22(summary)
    chart_radar_top4_v22(summary)

    print("\nGenerating PUML diagrams...")
    puml_v22_architecture()
    puml_v22_findings()
    puml_learning_flow()
    render_puml_files()

    print(f"\nAll v2.2.0 diagrams written to: {DIAG}")


if __name__ == "__main__":
    main()
