#!/usr/bin/env python3
"""
Genera diagramas del benchmark v2.0.0, incluyendo comparación v1 vs v2.
"""

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
plt.rcParams['font.sans-serif'] = ['Noto Serif SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

BASE = Path("/home/z/my-project/download/benchmark-cortex-v2")
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
    "cortex_v2_priority_pack": "CORTEX v2 PP (CLI v2.4)",
    "cortex_v2_canonical": "CORTEX v2 Canonical",
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
    "cortex_v2_priority_pack": "#7c3aed",  # purple for v2
    "cortex_v2_canonical": "#9333ea",  # darker purple
    "cortex_ablation_no_P0": "#dc2626",
    "cortex_ablation_no_temporal": "#b91c1c",
}


def load_summary():
    with open(RUNS / "summary_tasks.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_scored():
    with open(RUNS / "scored_tasks.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def chart_v1_vs_v2_weighted(summary):
    """Bar chart comparando v1 vs v2 methods."""
    methods_order = [
        "cortex_priority_pack_v1",
        "cortex_v2_priority_pack",
        "cortex_v2_canonical",
    ]
    methods = [next(s for s in summary if s["method_id"] == m) for m in methods_order]
    names = [METHOD_LABELS.get(m["method_id"], m["method_id"]) for m in methods]
    scores = [float(m["avg_weighted_score"]) for m in methods]
    colors = [METHOD_COLORS.get(m["method_id"], "#999") for m in methods]

    fig, ax = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
    bars = ax.barh(names, scores, color=colors, edgecolor="white", linewidth=0.5)
    ax.invert_yaxis()
    ax.set_xlabel("Puntaje ponderado (mayor = mejor)")
    ax.set_title("CODEC-CORTEX v1 vs v2 — Comparativa directa",
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{score:.2f}", va="center", fontsize=10)
    fig.savefig(DIAG / "01_v1_vs_v2_weighted.png", dpi=150)
    plt.close(fig)
    print("  01_v1_vs_v2_weighted.png")


def chart_all_methods_v2(summary):
    """Bar chart: weighted score por metodo (incluye v2)."""
    methods = sorted(summary, key=lambda x: -float(x["avg_weighted_score"]))
    names = [METHOD_LABELS.get(m["method_id"], m["method_id"]) for m in methods]
    scores = [float(m["avg_weighted_score"]) for m in methods]
    colors = [METHOD_COLORS.get(m["method_id"], "#999") for m in methods]

    fig, ax = plt.subplots(figsize=(12, 6.5), constrained_layout=True)
    bars = ax.barh(names, scores, color=colors, edgecolor="white", linewidth=0.5)
    ax.invert_yaxis()
    ax.set_xlabel("Puntaje ponderado (mayor = mejor)")
    ax.set_title("Benchmark v2.0.0 — Comparativa global de métodos (CLI v2.4.0)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.1 if score > 0 else bar.get_width() - 0.1,
                bar.get_y() + bar.get_height() / 2,
                f"{score:.2f}", va="center",
                ha="left" if score > 0 else "right", fontsize=9)
    # Legend
    from matplotlib.patches import Patch
    legend_handles = [
        Patch(facecolor="#2563eb", label="CODEC-CORTEX v1 (CLI v1)"),
        Patch(facecolor="#7c3aed", label="CODEC-CORTEX v2 (CLI v2.4)"),
        Patch(facecolor="#94a3b8", label="Baselines posicionales"),
        Patch(facecolor="#fbbf24", label="Pasivo semántico"),
        Patch(facecolor="#f97316", label="Query-dependent"),
        Patch(facecolor="#dc2626", label="Ablations"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=8, framealpha=0.9)
    fig.savefig(DIAG / "02_all_methods_v2.png", dpi=150)
    plt.close(fig)
    print("  02_all_methods_v2.png")


def chart_v2_metrics_radar(summary):
    """Radar comparando v1 vs v2 en métricas clave."""
    import numpy as np
    methods = ["cortex_priority_pack_v1", "cortex_v2_priority_pack"]
    metrics = ["EAS", "P0_survival", "P1_survival", "STR", "BCFNR_inv", "ED_norm"]
    metric_labels = ["EAS", "P0 Surv", "P1 Surv", "Traceab", "BCFNR (inv)", "ED (norm)"]

    # BCFNR inverted (1 - BCFNR) so higher = better
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"projection": "polar"}, constrained_layout=True)
    for m_id in methods:
        m = next((s for s in summary if s["method_id"] == m_id), None)
        if not m: continue
        vals = [
            float(m["avg_EAS"]),
            float(m["avg_P0_survival"]),
            float(m["avg_P1_survival"]),
            float(m["avg_STR"]),
            1.0 - float(m["avg_BCFNR"]),  # invert
            min(float(m["avg_evidence_density"]) * 100, 1.0),  # normalize
        ]
        vals += vals[:1]
        ax.plot(angles, vals, marker="o", linewidth=2,
                label=METHOD_LABELS.get(m_id, m_id),
                color=METHOD_COLORS.get(m_id, "#999"))
        ax.fill(angles, vals, alpha=0.15,
                color=METHOD_COLORS.get(m_id, "#999"))

    ax.set_thetagrids([a * 180 / np.pi for a in angles[:-1]], metric_labels)
    ax.set_ylim(0, 1.05)
    ax.set_title("Radar comparativo: CORTEX PP v1 vs v2",
                 fontsize=13, fontweight="bold", pad=20)
    ax.legend(loc="lower right", bbox_to_anchor=(1.25, 0.0), fontsize=9)
    ax.grid(True, alpha=0.4)
    fig.savefig(DIAG / "03_v1_vs_v2_radar.png", dpi=150)
    plt.close(fig)
    print("  03_v1_vs_v2_radar.png")


def chart_view_coverage(summary):
    """Bar chart: VIEW coverage y reversibility por metodo v2."""
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
    ax.set_title("Métricas v2: VIEW Coverage y Reversibility\n(corpus v1.0.0 sin VIEW directives → 0%)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.set_ylim(0, 1.1)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    fig.savefig(DIAG / "04_view_coverage.png", dpi=150)
    plt.close(fig)
    print("  04_view_coverage.png")


def chart_cli_version_timeline():
    """Diagrama timeline: v1.0.0 (CLI v1.1.9) → v2.0.0 (CLI v2.4.0)."""
    fig, ax = plt.subplots(figsize=(12, 5), constrained_layout=True)

    # Timeline data
    events = [
        ("v1.0.0\nCLI v1.1.9", 0, "#2563eb"),
        ("v2.0.0\nCLI v2.4.0", 1, "#7c3aed"),
    ]
    for label, x, color in events:
        ax.scatter(x, 0, s=400, color=color, zorder=5, edgecolor="white", linewidth=2)
        ax.text(x, 0.3, label, ha="center", va="bottom", fontsize=11, fontweight="bold", color=color)

    # Arrow
    ax.annotate("", xy=(1, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color="#475569", lw=2))

    # Changes between versions
    changes = [
        "CLI: v1.1.9 → v2.4.0",
        "Bidireccionalidad CORTEX ⇄ HCORTEX",
        "VIEW directives (44 en skill canónico)",
        "v2-convert, v2-verify-view, v2-roundtrip-bidir",
        "v2-canonicalize, v2-explain-loss, v2-inspect",
        "Nuevas métricas: VIEW_coverage, reversibility, bidir_equiv",
    ]
    for i, c in enumerate(changes):
        ax.text(0.5, -0.3 - i * 0.12, f"• {c}", ha="center", va="top", fontsize=9, color="#475569")

    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(-1.2, 0.6)
    ax.axis("off")
    ax.set_title("Evolución del benchmark: v1.0.0 → v2.0.0",
                 fontsize=14, fontweight="bold", pad=20)
    fig.savefig(DIAG / "05_cli_timeline.png", dpi=150)
    plt.close(fig)
    print("  05_cli_timeline.png")


def chart_v2_failure_modes(summary):
    """Bar chart: modos de fallo v2 (BCFNR, etc)."""
    methods = sorted(summary, key=lambda x: float(x["avg_BCFNR"]))
    names = [METHOD_LABELS.get(m["method_id"], m["method_id"]) for m in methods]
    bcfnr = [float(m["avg_BCFNR"]) for m in methods]
    colors = ["#16a34a" if v == 0 else "#dc2626" if v > 0.5 else "#f59e0b" for v in bcfnr]

    fig, ax = plt.subplots(figsize=(11, 5.5), constrained_layout=True)
    bars = ax.barh(names, bcfnr, color=colors, edgecolor="white", linewidth=0.5)
    ax.invert_yaxis()
    ax.set_xlabel("BCFNR (menor = mejor, 0 = sin omisiones)")
    ax.set_title("Blocking Constraint False Negative Rate — v2.0.0",
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", alpha=0.3, linestyle="--")
    for bar, v in zip(bars, bcfnr):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{v:.3f}", va="center", fontsize=9)
    fig.savefig(DIAG / "06_v2_failure_modes.png", dpi=150)
    plt.close(fig)
    print("  06_v2_failure_modes.png")


def puml_v2_architecture():
    content = """@startuml
title Arquitectura Benchmark v2.0.0 — CLI v2.4.0

skinparam rectangle {
  BackgroundColor<<cortex_v1>> #DBEAFE
  BackgroundColor<<cortex_v2>> #EDE9FE
  BackgroundColor<<baseline>> #F1F5F9
  BackgroundColor<<metric>> #FEF3C7
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Corpus L2\\n10 dominios (v1.0.0 reusable)\\nFormatos: .cortex, raw, md, json, yaml" as corpus <<baseline>>

package "Metodos v1 (CLI v1.1.9)" {
  rectangle "Pasivos Posicionales\\nrecent_tail, head_tail,\\nhead_json, head_md" as positional <<baseline>>
  rectangle "Pasivo Semantico\\nsemantic_field_pack" as semantic <<baseline>>
  rectangle "Query-Dependent\\nkeyword_retrieval (BM25)" as qd <<baseline>>
  rectangle "CODEC-CORTEX v1\\nCPP v1 (render --profile)" as cortex_v1 <<cortex_v1>>
  rectangle "Ablations\\nno_P0, no_temporal" as ablation <<baseline>>
}

package "Metodos v2 NUEVOS (CLI v2.4.0)" {
  rectangle "CODEC-CORTEX v2 PP\\nv2-convert + fallback v1\\n(sin VIEW -> fallback)" as cortex_v2_pp <<cortex_v2>>
  rectangle "CODEC-CORTEX v2 Canonical\\nv2-canonicalize + v2-convert\\n(FALLA: sin VIEW)" as cortex_v2_canon <<cortex_v2>>
}

package "Metricas v2 NUEVAS" {
  rectangle "VIEW_coverage\\nReversibility\\nBidir_equivalence\\nLoss_count" as v2_metrics <<metric>>
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

note right of cortex_v2_pp
  v2-convert produce HCORTEX
  vacio sin VIEW directives.
  Fallback a v1 render --profile.
end note

note right of cortex_v2_canon
  v2-canonicalize reescribe .cortex
  perdiendo compatibilidad con
  v1 render. BCFNR = 1.0.
end note

note right of v2_metrics
  VIEW_coverage = 0% en corpus v1.0.0
  Reversibility = 0 (sin VIEW)
  Bidir_equiv = 0 (roundtrip falla)
end note
@enduml
"""
    (DIAG / "07_v2_architecture.puml").write_text(content, encoding="utf-8")
    print("  07_v2_architecture.puml")


def puml_v2_findings():
    content = """@startuml
title Hallazgos clave del benchmark v2.0.0

skinparam rectangle {
  BackgroundColor<<positive>> #D1FAE5
  BackgroundColor<<neutral>> #FEF3C7
  BackgroundColor<<negative>> #FEE2E2
  BackgroundColor<<finding>> #DBEAFE
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Hallazgos positivos" as pos <<positive>> {
  rectangle "CPP v1 mantiene 100% P0\\ny BCFNR=0 en v2.0.0\\n(igual que v1.0.0)" as f1
  rectangle "CPP v2 con fallback\\nproduce resultados identicos\\na CPP v1 (Δ=0.0)" as f2
  rectangle "QDD = -3.95\\nestructura cognitiva supera\\na query-dependent" as f3
}

rectangle "Hallazgos neutrales" as neu <<neutral>> {
  rectangle "VIEW_coverage = 0%\\nen corpus v1.0.0\\n(sin VIEW directives)" as f4
  rectangle "Reversibility = 0\\nen corpus v1.0.0\\n(requiere migracion a v2)" as f5
}

rectangle "Hallazgos negativos" as neg <<negative>> {
  rectangle "v2_canonical falla:\\nBCFNR=1.0, WS=-2.73\\n(v2-canonicalize rompe\\ncompatibilidad)" as f6
  rectangle "v2-convert produce\\nHCORTEX vacio (251 bytes)\\nsin VIEW directives" as f7
}

rectangle "Implicacion cientifica" as imp <<finding>> {
  rectangle "La bidireccionalidad CORTEX⇄HCORTEX\\nREQUIERE migrar artefactos a v2\\ncon VIEW directives explicitas\\n(formato $N/SIGIL:name en entries)" as f8
}

f1 --> imp
f2 --> imp
f4 --> imp
f5 --> imp
f6 --> imp
f7 --> imp

note right of imp
  Conclusion: v2.4.0 es funcionalmente
  superior pero requiere migracion
  del corpus para explotar sus
  capacidades bidireccionales.
end note
@enduml
"""
    (DIAG / "08_v2_findings.puml").write_text(content, encoding="utf-8")
    print("  08_v2_findings.puml")


def render_puml_files():
    """Render PUML files to PNG via plantweb."""
    from plantweb.plantuml import plantuml
    from pathlib import Path
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
    scored = load_scored()
    print(f"  {len(summary)} summary rows, {len(scored)} scored rows")

    print("\nGenerating v2.0.0 diagrams...")
    chart_v1_vs_v2_weighted(summary)
    chart_all_methods_v2(summary)
    chart_v2_metrics_radar(summary)
    chart_view_coverage(summary)
    chart_cli_version_timeline()
    chart_v2_failure_modes(summary)

    print("\nGenerating PUML diagrams...")
    puml_v2_architecture()
    puml_v2_findings()
    render_puml_files()

    print(f"\nAll v2.0.0 diagrams written to: {DIAG}")


if __name__ == "__main__":
    main()
