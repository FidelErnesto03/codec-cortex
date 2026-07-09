#!/usr/bin/env python3
"""Genera diagramas del benchmark v2.1.0, incluyendo progresión v1.0.0 → v2.0.0 → v2.1.0."""

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

BASE = Path("/home/z/my-project/download/benchmark-cortex-v21")
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
    "cortex_priority_pack": "CORTEX PP v2 (CLI v0.3.2)",
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


def chart_v21_weighted(summary):
    """Bar chart: weighted score por metodo v2.1.0."""
    methods = sorted(summary, key=lambda x: -float(x["avg_weighted_score"]))
    names = [METHOD_LABELS.get(m["method_id"], m["method_id"]) for m in methods]
    scores = [float(m["avg_weighted_score"]) for m in methods]
    colors = [METHOD_COLORS.get(m["method_id"], "#999") for m in methods]

    fig, ax = plt.subplots(figsize=(12, 6.5), constrained_layout=True)
    bars = ax.barh(names, scores, color=colors, edgecolor="white", linewidth=0.5)
    ax.invert_yaxis()
    ax.set_xlabel("Puntaje ponderado (mayor = mejor)")
    ax.set_title("Benchmark v2.1.0 — Comparativa global (CLI v0.3.2, corpus migrado a VIEW)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.1 if score > 0 else bar.get_width() - 0.1,
                bar.get_y() + bar.get_height() / 2,
                f"{score:.2f}", va="center",
                ha="left" if score > 0 else "right", fontsize=9)
    legend_handles = [
        mpatches.Patch(facecolor="#2563eb", label="CODEC-CORTEX v1 (CLI v1)"),
        mpatches.Patch(facecolor="#7c3aed", label="CODEC-CORTEX v2 (CLI v0.3.2)"),
        mpatches.Patch(facecolor="#94a3b8", label="Baselines posicionales"),
        mpatches.Patch(facecolor="#fbbf24", label="Pasivo semántico"),
        mpatches.Patch(facecolor="#f97316", label="Query-dependent"),
        mpatches.Patch(facecolor="#dc2626", label="Ablations"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=8, framealpha=0.9)
    fig.savefig(DIAG / "01_v21_weighted.png", dpi=150)
    plt.close(fig)
    print("  01_v21_weighted.png")


def chart_progression_v1_v2_v21():
    """Bar chart: progresión WS de CPP entre v1.0.0, v2.0.0, v2.1.0."""
    versions = ["v1.0.0\n(CLI v1.1.9)", "v2.0.0\n(CLI v2.4.0)", "v2.1.0\n(CLI v0.3.2)"]
    # CPP scores per version
    ws_scores = [7.03, 7.03, 9.31]  # v1, v2.0 (fallback), v2.1
    view_cov = [0.0, 0.0, 1.00]
    reversibility = [0.0, 0.0, 1.0]
    colors = ["#2563eb", "#7c3aed", "#9333ea"]

    fig, axes = plt.subplots(1, 3, figsize=(14, 5), constrained_layout=True)

    # WS
    ax = axes[0]
    bars = ax.bar(versions, ws_scores, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_ylabel("Weighted Score")
    ax.set_title("Progresión WS de CORTEX Priority Pack", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, score in zip(bars, ws_scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{score:.2f}", ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 11)

    # VIEW coverage
    ax = axes[1]
    bars = ax.bar(versions, view_cov, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_ylabel("VIEW Coverage (0..1)")
    ax.set_title("VIEW Coverage", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, view_cov):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{v:.2f}", ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.15)

    # Reversibility
    ax = axes[2]
    bars = ax.bar(versions, reversibility, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_ylabel("Reversibility (0/1)")
    ax.set_title("Reversibility", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, reversibility):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{v:.0f}", ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.15)

    fig.suptitle("Progresión del benchmark: v1.0.0 → v2.0.0 → v2.1.0",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.savefig(DIAG / "02_progression_v1_v2_v21.png", dpi=150)
    plt.close(fig)
    print("  02_progression_v1_v2_v21.png")


def chart_v2_metrics_activated(summary):
    """Bar chart: métricas v2 ahora activadas (VIEW, reversibility) vs v2.0.0."""
    v2_methods = [s for s in summary if int(s.get("is_v2", 0)) == 1]
    names = [METHOD_LABELS.get(m["method_id"], m["method_id"]) for m in v2_methods]
    view_cov = [float(m["avg_VIEW_coverage"]) for m in v2_methods]
    revers = [float(m["avg_reversibility"]) for m in v2_methods]

    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    x = list(range(len(names)))
    w = 0.35
    ax.bar([i - w/2 for i in x], view_cov, w, label="VIEW coverage", color="#7c3aed", edgecolor="white")
    ax.bar([i + w/2 for i in x], revers, w, label="Reversibility", color="#9333ea", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9)
    ax.set_ylabel("Tasa (0..1)")
    ax.set_title("Métricas v2 ACTIVADAS en v2.1.0 (corpus migrado a VIEW directives)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.set_ylim(0, 1.15)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    # Annotate
    for i, (v, r) in enumerate(zip(view_cov, revers)):
        ax.text(i - w/2, v + 0.02, f"{v:.2f}", ha="center", fontsize=9, fontweight="bold")
        ax.text(i + w/2, r + 0.02, f"{r:.0f}", ha="center", fontsize=9, fontweight="bold")
    fig.savefig(DIAG / "03_v2_metrics_activated.png", dpi=150)
    plt.close(fig)
    print("  03_v2_metrics_activated.png")


def chart_canonical_fix():
    """Comparativa: cortex_canonical v2.0.0 (falla) vs v2.1.0 (funciona)."""
    versions = ["v2.0.0\ncortex_v2_canonical\n(sin --preserve)", "v2.1.0\ncortex_canonical\n(--preserve)"]
    ws = [-2.73, 9.31]
    bcfnr = [1.0, 0.0]
    p0 = [0.0, 0.98]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), constrained_layout=True)
    colors = ["#dc2626", "#16a34a"]

    ax = axes[0]
    bars = ax.bar(versions, ws, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_ylabel("Weighted Score")
    ax.set_title("WS: canonical", fontsize=11, fontweight="bold")
    ax.axhline(0, color="black", linewidth=0.5)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, ws):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + (0.2 if v >= 0 else -0.5),
                f"{v:.2f}", ha="center", fontsize=10, fontweight="bold")

    ax = axes[1]
    bars = ax.bar(versions, bcfnr, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_ylabel("BCFNR (menor = mejor)")
    ax.set_title("BCFNR: canonical", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, bcfnr):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{v:.2f}", ha="center", fontsize=10, fontweight="bold")

    ax = axes[2]
    bars = ax.bar(versions, p0, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_ylabel("P0 Survival")
    ax.set_title("P0 Survival: canonical", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, p0):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{v:.2f}", ha="center", fontsize=10, fontweight="bold")

    fig.suptitle("Fix de `canonicalize` en v0.3.2 (issues B-01/B-05)",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.savefig(DIAG / "04_canonical_fix.png", dpi=150)
    plt.close(fig)
    print("  04_canonical_fix.png")


def chart_token_vs_score_v21(summary):
    """Scatter: tokens vs score para v2.1.0."""
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
    ax.set_title("v2.1.0 — Trade-off: tokens vs calidad de evidencia",
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(True, alpha=0.3, linestyle="--")
    xs = [float(m["avg_context_tokens"]) for m in summary]
    ys = [float(m["avg_weighted_score"]) for m in summary]
    ax.axvline(sum(xs) / len(xs), color="#94a3b8", linestyle=":", alpha=0.6)
    ax.axhline(sum(ys) / len(ys), color="#94a3b8", linestyle=":", alpha=0.6)
    fig.savefig(DIAG / "05_token_vs_score_v21.png", dpi=150)
    plt.close(fig)
    print("  05_token_vs_score_v21.png")


def chart_radar_top4_v21(summary):
    """Radar top-4 métodos v2.1.0."""
    import numpy as np
    methods_sorted = sorted(summary, key=lambda x: -float(x["avg_weighted_score"]))
    top4 = methods_sorted[:4]
    metrics = ["EAS", "P0_survival", "P1_survival", "STR", "VIEW_coverage", "reversibility"]
    metric_labels = ["EAS", "P0 Surv", "P1 Surv", "Traceab", "VIEW cov", "Reversib"]

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
    ax.set_title("Radar Top-4 métodos v2.1.0",
                 fontsize=13, fontweight="bold", pad=20)
    ax.legend(loc="lower right", bbox_to_anchor=(1.25, 0.0), fontsize=9)
    ax.grid(True, alpha=0.4)
    fig.savefig(DIAG / "06_radar_top4_v21.png", dpi=150)
    plt.close(fig)
    print("  06_radar_top4_v21.png")


def puml_v21_architecture():
    content = """@startuml
title Arquitectura Benchmark v2.1.0 — CLI v0.3.2 + corpus migrado a VIEW

skinparam rectangle {
  BackgroundColor<<cortex_v1>> #DBEAFE
  BackgroundColor<<cortex_v2>> #EDE9FE
  BackgroundColor<<baseline>> #F1F5F9
  BackgroundColor<<metric>> #FEF3C7
  BackgroundColor<<fix>> #D1FAE5
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Corpus L2 v2.1\\n10 dominios CON VIEW directives\\n10-13 VIEW por caso\\n100% coverage, reversible" as corpus <<fix>>

package "Metodos v1 (CLI v1.x render)" {
  rectangle "Pasivos Posicionales (4)\\nrecent_tail, head_tail,\\nhead_json, head_md" as positional <<baseline>>
  rectangle "Pasivo Semantico\\nsemantic_field_pack" as semantic <<baseline>>
  rectangle "Query-Dependent\\nkeyword_retrieval (BM25)" as qd <<baseline>>
  rectangle "CODEC-CORTEX v1\\nCPP v1 (render --profile)" as cortex_v1 <<cortex_v1>>
  rectangle "Ablations\\nno_P0, no_temporal" as ablation <<baseline>>
}

package "Metodos v2 (CLI v0.3.2 canonical)" {
  rectangle "CORTEX PP v2\\nconvert --from cortex --to hcortex\\nVIEW-aware, reversible" as cortex_v2_pp <<cortex_v2>>
  rectangle "CORTEX Canonical v2\\ncanonicalize --preserve + convert\\nFIX: ya no falla (B-01/B-05)" as cortex_v2_canon <<cortex_v2>>
}

package "Metricas v2 ACTIVADAS" {
  rectangle "VIEW_coverage = 100%\\nReversibility = 1.0\\nBidir_equivalence = 0*\\nLoss_count = 0" as v2_metrics <<metric>>
}

corpus --> positional
corpus --> semantic
corpus --> qd
corpus --> cortex_v1
corpus --> ablation
corpus --> cortex_v2_pp
corpus --> cortex_v2_canon

cortex_v2_pp --> v2_metrics
cortex_v2_canon --> v2_metrics

note right of corpus
  FIXES v2.0.0 issues:
  - Corpus migrado a VIEW
  - Header CODEC-CORTEX añadido
  - status:cur -> status:"current"
end note

note right of cortex_v2_canon
  FIX v0.3.2:
  canonicalize --preserve
  es VIEW-aware, no rompe
  compatibilidad con v1.
end note

note right of v2_metrics
  * Bidir_equivalence = 0 por
  E_TABLE_SCHEMA_MISMATCH
  en roundtrip-bidir (issue
  pendiente para v2.2.0).
end note
@enduml
"""
    (DIAG / "07_v21_architecture.puml").write_text(content, encoding="utf-8")
    print("  07_v21_architecture.puml")


def puml_v21_findings():
    content = """@startuml
title Hallazgos clave del benchmark v2.1.0

skinparam rectangle {
  BackgroundColor<<positive>> #D1FAE5
  BackgroundColor<<neutral>> #FEF3C7
  BackgroundColor<<fix>> #DBEAFE
  BackgroundColor<<finding>> #EDE9FE
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Fixes v2.0.0 issues" as fixes <<fix>> {
  rectangle "FIX 1: Corpus migrado a VIEW\\n10 casos con 10-13 VIEW cada uno\\n100% coverage, reversible=True" as fix1
  rectangle "FIX 2: canonicalize --preserve\\nYa no rompe compatibilidad\\nWS: -2.73 → +9.31" as fix2
  rectangle "FIX 3: Nombres canónicos CLI\\nv2-convert -> convert\\n(v2-* deprecated)" as fix3
}

rectangle "Resultados positivos" as pos <<positive>> {
  rectangle "CORTEX PP v2 = ganador\\nWS = 9.31 (+2.28 vs v1)\\nVIEW=100%, rev=1.0" as r1
  rectangle "MRD = +4.38\\n(vs +2.16 en v2.0.0)\\nVentaja se amplía" as r2
  rectangle "QDD = -6.24\\n(vs -3.95 en v2.0.0)\\nEstructura > query-dep" as r3
  rectangle "BCFNR = 0 mantenido\\nConstraints blocking\\nnunca omitidos" as r4
}

rectangle "Trade-offs" as trade <<neutral>> {
  rectangle "EAS baja 0.984 → 0.950\\nFormato HCORTEX v2 usa\\nnombres canónicos de campos" as t1
  rectangle "+396 tokens promedio\\nHCORTEX v2 más verbose\\npero mejor score" as t2
}

rectangle "Pendiente" as pend <<neutral>> {
  rectangle "Bidir_equivalence = 0\\nE_TABLE_SCHEMA_MISMATCH\\nen roundtrip-bidir\\n(issue para v2.2.0)" as p1
}

fixes --> pos
pos --> trade
pos --> pend

note right of fixes
  v0.3.2 aborda los 3 issues
  principales que v2.0.0 señalaba.
end note

note right of pend
  Queda 1 issue menor:
  roundtrip-bidir falla por
  schema mismatch en VIEW
  directives (fields declaran
  más columnas que header).
end note
@enduml
"""
    (DIAG / "08_v21_findings.puml").write_text(content, encoding="utf-8")
    print("  08_v21_findings.puml")


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

    print("\nGenerating v2.1.0 diagrams...")
    chart_v21_weighted(summary)
    chart_progression_v1_v2_v21()
    chart_v2_metrics_activated(summary)
    chart_canonical_fix()
    chart_token_vs_score_v21(summary)
    chart_radar_top4_v21(summary)

    print("\nGenerating PUML diagrams...")
    puml_v21_architecture()
    puml_v21_findings()
    render_puml_files()

    print(f"\nAll v2.1.0 diagrams written to: {DIAG}")


if __name__ == "__main__":
    main()
