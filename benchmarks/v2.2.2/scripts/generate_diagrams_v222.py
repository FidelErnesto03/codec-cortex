#!/usr/bin/env python3
"""Genera diagramas del benchmark v2.2.2."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf')
fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
plt.rcParams['font.sans-serif'] = ['Noto Serif SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

BASE = Path("/home/z/my-project/download/benchmark-cortex-v222")
RUNS = BASE / "runs"
DIAG = BASE / "diagrams"
DIAG.mkdir(parents=True, exist_ok=True)


def load_results():
    return json.loads((RUNS / "v222_results.json").read_text())


def chart_bridge_results(data):
    """Bar chart: resultados del bridge benchmark por tipo de tarea."""
    codec_results = data["bridge_benchmark"]["codec_cortex_results"]["tasks"]
    
    # Aggregate by benchmark type
    locomo_tasks = [t for t in codec_results if t["benchmark"] == "LoCoMo-style"]
    longmem_tasks = [t for t in codec_results if t["benchmark"] == "LongMemEval-style"]
    
    categories = ["LoCoMo-style\nsingle_hop", "LoCoMo-style\nmulti_hop", "LongMemEval-style\ntemporal", "LongMemEval-style\ninfo_flow"]
    eas_rates = []
    etc_avgs = []
    f1_avgs = []
    
    for cat_filter in ["single_hop", "multi_hop", "temporal", "information_flow"]:
        subset = [t for t in codec_results if t["task_type"] == cat_filter]
        if subset:
            eas = sum(1 for t in subset if t["EAS"] == 1) / len(subset) * 100
            etc = sum(t["ETC"] for t in subset) / len(subset)
            f1 = sum(t["F1"] for t in subset) / len(subset)
        else:
            eas = etc = f1 = 0
        eas_rates.append(eas)
        etc_avgs.append(etc)
        f1_avgs.append(f1)
    
    x = np.arange(len(categories))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    ax.bar(x - width, eas_rates, width, label='EAS (%)', color='#2563eb', edgecolor='white')
    ax.bar(x, [e*100 for e in etc_avgs], width, label='ETC ×100 (%)', color='#7c3aed', edgecolor='white')
    ax.bar(x + width, [f*100 for f in f1_avgs], width, label='F1 ×100 (%)', color='#16a34a', edgecolor='white')
    
    ax.set_ylabel('Score')
    ax.set_title('Bridge Benchmark: codec-cortex en tareas estilo LoCoMo/LongMemEval', fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylim(0, 115)
    ax.axhline(100, color='#dc2626', linestyle=':', alpha=0.7, label='100% target')
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    for i, (e, t, f) in enumerate(zip(eas_rates, etc_avgs, f1_avgs)):
        ax.text(i - width, e + 1, f'{e:.0f}%', ha='center', fontsize=8, fontweight='bold')
    
    fig.savefig(DIAG / "01_bridge_results.png", dpi=150)
    plt.close(fig)
    print("  01_bridge_results.png")


def chart_resource_metrics(data):
    """Bar chart: throughput y RAM por operación."""
    ops = data["resource_metrics"]["operations"]
    
    op_names = list(ops.keys())
    throughput = [ops[o]["throughput_files_per_s"] for o in op_names]
    ram = [ops[o]["peak_ram_mb"] for o in op_names]
    latency = [ops[o]["avg_time_per_file_ms"] for o in op_names]
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 5), constrained_layout=True)
    
    ax = axes[0]
    bars = ax.bar(op_names, throughput, color='#2563eb', edgecolor='white')
    ax.set_ylabel('Throughput (files/s)')
    ax.set_title('Throughput por operación', fontsize=11, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    for bar, v in zip(bars, throughput):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f'{v:.2f}', ha='center', fontsize=9)
    
    ax = axes[1]
    bars = ax.bar(op_names, latency, color='#f97316', edgecolor='white')
    ax.set_ylabel('Latencia (ms/file)')
    ax.set_title('Latencia por operación', fontsize=11, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    for bar, v in zip(bars, latency):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{v:.0f}', ha='center', fontsize=9)
    
    ax = axes[2]
    bars = ax.bar(op_names, ram, color='#16a34a', edgecolor='white')
    ax.set_ylabel('Peak RAM (MB)')
    ax.set_title('Peak RAM por operación', fontsize=11, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    for bar, v in zip(bars, ram):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001, f'{v:.3f}', ha='center', fontsize=9)
    
    fig.suptitle('Resource Metrics: codec-cortex (10 casos, 4 operaciones)', fontsize=13, fontweight='bold', y=1.02)
    fig.savefig(DIAG / "02_resource_metrics.png", dpi=150)
    plt.close(fig)
    print("  02_resource_metrics.png")


def chart_four_family_comparison(data):
    """Heatmap: comparativa 4 familias + codec-cortex."""
    families = list(data["four_family_matrix"].keys())
    features = ["deterministic", "local_first", "audit_trail", "learning_engine",
                "bidirectional", "vector_search", "knowledge_graph", "temporal_graph",
                "managed_service"]
    feature_labels = ["Determinist", "Local-first", "Audit trail", "Learning",
                      "Bidirect", "Vector", "KG", "Temporal\ngraph", "Managed\nservice"]
    
    matrix = []
    for fam in families:
        row = [1 if data["four_family_matrix"][fam].get(f, False) else 0 for f in features]
        matrix.append(row)
    
    arr = np.array(matrix)
    
    fig, ax = plt.subplots(figsize=(13, 6), constrained_layout=True)
    im = ax.imshow(arr, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    
    ax.set_xticks(range(len(features)))
    ax.set_xticklabels(feature_labels, fontsize=9, ha='center')
    ax.set_yticks(range(len(families)))
    family_labels = [f"{f}\n({data['four_family_matrix'][f]['stars']:,}★)" for f in families]
    ax.set_yticklabels(family_labels, fontsize=9)
    
    for i in range(len(families)):
        for j in range(len(features)):
            v = arr[i, j]
            ax.text(j, i, '✓' if v else '—', ha='center', va='center',
                    color='white' if v == 1 else '#666', fontsize=12, fontweight='bold')
    
    ax.set_title('4 familias de memoria para agentes + codec-cortex: feature matrix',
                 fontsize=13, fontweight='bold', pad=12)
    fig.savefig(DIAG / "03_four_family_matrix.png", dpi=150)
    plt.close(fig)
    print("  03_four_family_matrix.png")


def chart_benchmark_scores(data):
    """Bar chart: scores en benchmarks estándar (LoCoMo, LongMemEval)."""
    families = ["codec-cortex", "Mem0", "Zep/Graphiti", "Letta", "LangMem"]
    locomo = [0, 91.6, 94.7, 74.0, 0]  # codec-cortex N/A (bridge), LangMem N/A
    longmem = [0, 93.4, 90.2, 0, 0]
    
    # For codec-cortex, use bridge benchmark EAS as proxy
    codec_bridge = data["bridge_benchmark"]["codec_cortex_results"]["tasks"]
    codec_eas = sum(1 for t in codec_bridge if t["EAS"] == 1) / len(codec_bridge) * 100
    locomo[0] = codec_eas  # proxy
    
    x = np.arange(len(families))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    bars1 = ax.bar(x - width/2, locomo, width, label='LoCoMo (%)', color='#2563eb', edgecolor='white')
    bars2 = ax.bar(x + width/2, longmem, width, label='LongMemEval (%)', color='#7c3aed', edgecolor='white')
    
    ax.set_ylabel('Score (%)')
    ax.set_title('Benchmarks estándar de memoria agentiva (codec-cortex usa bridge proxy)', fontsize=12, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{f}\n({data['four_family_matrix'][f]['stars']:,}★)" for f in families], fontsize=9)
    ax.set_ylim(0, 115)
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bars in [bars1, bars2]:
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h + 1, f'{h:.1f}%', ha='center', fontsize=8, fontweight='bold')
            else:
                ax.text(bar.get_x() + bar.get_width()/2, 2, 'N/A', ha='center', fontsize=8, color='#94a3b8')
    
    fig.savefig(DIAG / "04_benchmark_scores.png", dpi=150)
    plt.close(fig)
    print("  04_benchmark_scores.png")


def chart_version_audit(data):
    """Bar chart: auditoría de versiones."""
    audit = data["version_audit"]
    
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    categories = ["Surfaces con\nv0.3.6", "Surfaces con\nv0.3.7", "CHANGELOG\nentrada v0.3.7"]
    values = [len(audit["surfaces_declaring_v0.3.6"]), len(audit["surfaces_declaring_v0.3.7"]),
              1 if audit["changelog_has_v0.3.7_entry"] else 0]
    colors = ['#dc2626', '#16a34a', '#dc2626']
    
    bars = ax.bar(categories, values, color=colors, edgecolor='white')
    ax.set_ylabel('Cantidad')
    ax.set_title(f'Auditoría de alineación de versiones\\n(Git tag: {audit["git_tag_latest"]}, PyPI: {audit["pypi_version"]})',
                 fontsize=12, fontweight='bold', pad=12)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, str(v), ha='center', fontsize=11, fontweight='bold')
    ax.axhline(0, color='black', linewidth=0.5)
    
    fig.savefig(DIAG / "05_version_audit.png", dpi=150)
    plt.close(fig)
    print("  05_version_audit.png")


def puml_bridge_architecture():
    content = """@startuml
title Benchmark v2.2.2 — Bridge a LoCoMo/LongMemEval + 4 familias

skinparam rectangle {
  BackgroundColor<<bridge>> #DBEAFE
  BackgroundColor<<family>> #EDE9FE
  BackgroundColor<<metric>> #FEF3C7
  BackgroundColor<<audit>> #FEE2E2
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Bridge Benchmark\\n(NEW v2.2.2)" as bridge <<bridge>> {
  rectangle "30 tareas estilo\\nLoCoMo + LongMemEval\\n(single/multi-hop,\\ntemporal, info-flow)" as tasks
  rectangle "codec-cortex: 100% EAS\\n(30/30 tareas pasan)" as codec_bridge
}

rectangle "4 Familias comparadas" as fams <<family>> {
  rectangle "codec-cortex\\n(determinista, local)\\n0★, 120 commits" as f1
  rectangle "Mem0\\n(memory layer, LLM)\\n60k★, 2432 commits\\nLoCoMo=91.6%" as f2
  rectangle "Zep/Graphiti\\n(temporal KG)\\n28.3k★, 881 commits\\nLoCoMo=94.7%" as f3
  rectangle "Letta\\n(stateful harness)\\n23.6k★, 7466 commits\\nLoCoMo=74.0%" as f4
  rectangle "LangMem\\n(LangGraph SDK)\\n1.5k★, 135 commits" as f5
}

rectangle "Resource Metrics\\n(NEW v2.2.2)" as res <<metric>> {
  rectangle "Throughput: 4.7 files/s\\nLatency: 214 ms/file\\nPeak RAM: 0.06 MB" as res_data
}

rectangle "Version Audit\\n(NEW v2.2.2)" as ver <<audit>> {
  rectangle "42 surfaces con v0.3.6\\n0 surfaces con v0.3.7\\nCHANGELOG sin entrada v0.3.7" as ver_data
}

tasks --> codec_bridge
codec_bridge --> f1
f1 ..> f2 : diferente familia
f1 ..> f3 : diferente familia
f1 ..> f4 : diferente familia
f1 ..> f5 : diferente familia

note right of bridge
  Aborda recomendación #1
  del informe analítico:
  bridge a benchmarks
  estándar de memoria.
end note

note right of res
  Aborda recomendación #3:
  métricas de throughput,
  RAM y CPU no especificadas
  en versiones anteriores.
end note

note right of ver
  Aborda recomendación #1:
  alinear versiones v0.3.6
  → v0.3.7 en todas las
  superficies del repo.
end note
@enduml
"""
    (DIAG / "06_bridge_architecture.puml").write_text(content, encoding="utf-8")
    print("  06_bridge_architecture.puml")


def puml_threat_model():
    content = """@startuml
title Threat Model — codec-cortex v0.3.7

skinparam rectangle {
  BackgroundColor<<threat>> #FEE2E2
  BackgroundColor<<mitigated>> #D1FAE5
  BackgroundColor<<unmitigated>> #FEF3C7
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Amenazas mitigadas" as mitigated <<mitigated>> {
  rectangle "T-01: Secret leakage\\nMitigation: E2 secret scanner (12 patrones)\\nStatus: implemented v0.3.4" as t01
  rectangle "T-02: Unauthorized mutation\\nMitigation: --mode read-only|editor|admin\\nStatus: implemented v0.3.4" as t02
  rectangle "T-03: Tampered artefacts\\nMitigation: SHA256SUMS, verify --signature\\nStatus: implemented v0.3.4" as t03
  rectangle "T-04: Irreversible HCORTEX\\nMitigation: VIEW coverage, reversible gate\\nStatus: implemented v0.3.2" as t04
  rectangle "T-05: LLM direct editing\\nMitigation: CLE dry_run_first, gates\\nStatus: implemented v0.3.6" as t05
  rectangle "T-06: Privacy exfiltration\\nMitigation: local-first, no telemetry\\nStatus: implemented by design" as t06
}

rectangle "No mitigadas" as unmit <<unmitigated>> {
  rectangle "No formal threat model\\nin repo (this benchmark)" as u1
  rectangle "No specific privacy\\npolicy document" as u2
  rectangle "MCP server (future E5)\\nwill need network\\nthreat model" as u3
}

note right of mitigated
  6 amenazas identificadas,
  todas con mitigación
  implementada en E2 (v0.3.4)
  o por diseño local-first.
end note

note right of unmit
  3 gaps documentales:
  threat model formal,
  privacy policy, y
  MCP network surface.
end note
@enduml
"""
    (DIAG / "07_threat_model.puml").write_text(content, encoding="utf-8")
    print("  07_threat_model.puml")


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
    print("Loading results...")
    data = load_results()
    
    print("\nGenerating v2.2.2 diagrams...")
    chart_bridge_results(data)
    chart_resource_metrics(data)
    chart_four_family_comparison(data)
    chart_benchmark_scores(data)
    chart_version_audit(data)
    
    print("\nGenerating PUML diagrams...")
    puml_bridge_architecture()
    puml_threat_model()
    render_puml_files()
    
    print(f"\nAll v2.2.2 diagrams written to: {DIAG}")


if __name__ == "__main__":
    main()
