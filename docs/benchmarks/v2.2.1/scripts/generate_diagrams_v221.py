#!/usr/bin/env python3
"""Genera diagramas del benchmark comparativo v2.2.1."""

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

BASE = Path("/home/z/my-project/download/benchmark-cortex-v221")
RUNS = BASE / "runs"
DIAG = BASE / "diagrams"
DIAG.mkdir(parents=True, exist_ok=True)


def load_results():
    return json.loads((RUNS / "comparative_pypi_results.json").read_text())


def chart_preservation_comparison(data):
    """Bar chart: preservación FCS/OBJ/CNST por paquete."""
    packages = ['codec-cortex', 'cortex-ai-memory', 'llm-cortex-memory']
    labels = ['CODEC-CORTEX\n(v0.3.6)', 'cortex-ai-memory\n(v2.2.0)', 'llm-cortex-memory\n(v1.2.0)']
    
    fcs_rates = []
    obj_rates = []
    cnst_rates = []
    
    for pkg in packages:
        results = data['empirical_results'].get(pkg, {})
        cases = results.get('cases', [])
        n = len(cases)
        if n == 0:
            fcs_rates.append(0)
            obj_rates.append(0)
            cnst_rates.append(0)
            continue
        fcs = sum(1 for c in cases if c.get('fcs_preserved')) / n * 100
        obj = sum(1 for c in cases if c.get('obj_preserved')) / n * 100
        cnst = sum(1 for c in cases if c.get('cnst_preserved')) / n * 100
        fcs_rates.append(fcs)
        obj_rates.append(obj)
        cnst_rates.append(cnst)
    
    x = np.arange(len(labels))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    bars1 = ax.bar(x - width, fcs_rates, width, label='FCS (Focus)', color='#2563eb', edgecolor='white')
    bars2 = ax.bar(x, obj_rates, width, label='OBJ (Objective)', color='#7c3aed', edgecolor='white')
    bars3 = ax.bar(x + width, cnst_rates, width, label='CNST (Constraint blocking)', color='#dc2626', edgecolor='white')
    
    ax.set_ylabel('Preservación (%)')
    ax.set_title('Preservación de evidencia operacional por paquete PyPI', fontsize=13, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylim(0, 115)
    ax.axhline(100, color='#16a34a', linestyle=':', alpha=0.7, label='Objetivo 100%')
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 1, f'{h:.0f}%',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    fig.savefig(DIAG / "01_preservation_comparison.png", dpi=150)
    plt.close(fig)
    print("  01_preservation_comparison.png")


def chart_feature_matrix(data):
    """Heatmap: feature matrix por paquete."""
    packages = list(data['feature_matrix'].keys())
    features = ['deterministic', 'local_first', 'structured_memory', 'audit_trail',
                'learning_engine', 'secret_scanner', 'contradiction_aware',
                'temporal_aware', 'token_efficient', 'bidirectional', 'vector_search',
                'knowledge_graph']
    feature_labels = ['Determinist', 'Local-first', 'Structured', 'Audit trail',
                      'Learning', 'Secret scan', 'Contradict', 'Temporal',
                      'Token-effic', 'Bidirect', 'Vector', 'KG']
    
    matrix = []
    for pkg in packages:
        row = [1 if data['feature_matrix'][pkg].get(f, False) else 0 for f in features]
        matrix.append(row)
    
    arr = np.array(matrix)
    
    fig, ax = plt.subplots(figsize=(13, 6), constrained_layout=True)
    im = ax.imshow(arr, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    
    ax.set_xticks(range(len(features)))
    ax.set_xticklabels(feature_labels, rotation=45, ha='right', fontsize=9)
    ax.set_yticks(range(len(packages)))
    ax.set_yticklabels([f"{p}\nv{data['feature_matrix'][p]['version']}" for p in packages], fontsize=9)
    
    for i in range(len(packages)):
        for j in range(len(features)):
            v = arr[i, j]
            ax.text(j, i, '✓' if v else '—', ha='center', va='center',
                    color='white' if v == 1 else '#666', fontsize=11, fontweight='bold')
    
    ax.set_title('Matriz de features: CODEC-CORTEX vs paquetes PyPI comparables',
                 fontsize=13, fontweight='bold', pad=12)
    
    # Add feature count column
    counts = arr.sum(axis=1)
    for i, c in enumerate(counts):
        ax.text(len(features) + 0.3, i, f'{c}/{len(features)}', va='center', fontsize=10, fontweight='bold')
    ax.text(len(features) + 0.3, -0.8, 'Score', va='center', fontsize=9, fontweight='bold')
    
    fig.savefig(DIAG / "02_feature_matrix.png", dpi=150)
    plt.close(fig)
    print("  02_feature_matrix.png")


def chart_latency_comparison(data):
    """Bar chart: latencia por paquete."""
    packages = ['codec-cortex', 'cortex-ai-memory', 'llm-cortex-memory']
    labels = ['CODEC-CORTEX', 'cortex-ai-memory', 'llm-cortex-memory']
    
    init_times = []
    ingest_times = []
    query_times = []
    render_times = []
    
    for pkg in packages:
        results = data['empirical_results'].get(pkg, {})
        cases = results.get('cases', [])
        n = len(cases)
        if n == 0:
            init_times.append(0)
            ingest_times.append(0)
            query_times.append(0)
            render_times.append(0)
            continue
        init_t = sum(c.get('verify_time', c.get('init_time', 0)) for c in cases if not c.get('errors')) / n
        ingest_t = sum(c.get('ingest_time', c.get('store_time', 0)) for c in cases if not c.get('errors')) / n
        query_t = sum(c.get('query_time', 0) for c in cases if not c.get('errors')) / n
        render_t = sum(c.get('render_time', c.get('context_time', 0)) for c in cases if not c.get('errors')) / n
        init_times.append(init_t * 1000)  # to ms
        ingest_times.append(ingest_t * 1000)
        query_times.append(query_t * 1000)
        render_times.append(render_t * 1000)
    
    x = np.arange(len(labels))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    ax.bar(x - 1.5*width, init_times, width, label='Init/Verify (ms)', color='#2563eb', edgecolor='white')
    ax.bar(x - 0.5*width, ingest_times, width, label='Ingest/Store (ms)', color='#7c3aed', edgecolor='white')
    ax.bar(x + 0.5*width, query_times, width, label='Query (ms)', color='#f97316', edgecolor='white')
    ax.bar(x + 1.5*width, render_times, width, label='Render/Context (ms)', color='#16a34a', edgecolor='white')
    
    ax.set_ylabel('Tiempo (ms)')
    ax.set_title('Latencia por operación y paquete', fontsize=13, fontweight='bold', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_yscale('log')
    ax.set_ylim(0.01, max(max(init_times), max(render_times)) * 10)
    
    fig.savefig(DIAG / "03_latency_comparison.png", dpi=150)
    plt.close(fig)
    print("  03_latency_comparison.png")


def chart_pypi_landscape():
    """Bar chart: distribucion de 220 paquetes cortex en PyPI por categoria."""
    categories = {
        'Memoria para\nagentes LLM': 35,
        'Agentes/frameworks\nAI': 28,
        'MCP servers\n/ tools': 18,
        'RAG / retrieval': 15,
        'ML / neuro\nscience': 22,
        'DevOps / CI/CD': 14,
        'Embedded / IoT\n(Cortex-M)': 20,
        'Snowflake / data\nwarehouse': 12,
        'Otros (gaming,\nweb, etc.)': 56,
    }
    
    labels = list(categories.keys())
    values = list(categories.values())
    colors = ['#2563eb', '#7c3aed', '#9333ea', '#f97316', '#16a34a',
              '#fbbf24', '#dc2626', '#06b6d4', '#94a3b8']
    
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    bars = ax.barh(labels, values, color=colors, edgecolor='white', linewidth=0.5)
    ax.invert_yaxis()
    ax.set_xlabel('Número de paquetes en PyPI')
    ax.set_title('Landscape PyPI: 220 paquetes con "cortex" en el nombre (julio 2026)',
                 fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    for bar, v in zip(bars, values):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                str(v), va='center', fontsize=10, fontweight='bold')
    ax.set_xlim(0, max(values) + 8)
    fig.savefig(DIAG / "04_pypi_landscape.png", dpi=150)
    plt.close(fig)
    print("  04_pypi_landscape.png")


def chart_radar_comparison(data):
    """Radar comparando los 3 paquetes empíricamente testeados."""
    packages = ['codec-cortex', 'cortex-ai-memory', 'llm-cortex-memory']
    labels = ['CODEC-CORTEX', 'cortex-ai-memory', 'llm-cortex-memory']
    colors = ['#2563eb', '#f97316', '#16a34a']
    
    # Normalize metrics to 0..1
    metrics = ['FCS_pres', 'OBJ_pres', 'CNST_pres', 'Features', 'Speed', 'Structure']
    metric_labels = ['FCS\npreserved', 'OBJ\npreserved', 'CNST\npreserved', 'Features\n(norm)', 'Speed\n(inv)', 'Structure']
    
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw={"projection": "polar"}, constrained_layout=True)
    
    for i, pkg in enumerate(packages):
        results = data['empirical_results'].get(pkg, {})
        cases = results.get('cases', [])
        n = len(cases)
        fcs = sum(1 for c in cases if c.get('fcs_preserved')) / max(n, 1)
        obj = sum(1 for c in cases if c.get('obj_preserved')) / max(n, 1)
        cnst = sum(1 for c in cases if c.get('cnst_preserved')) / max(n, 1)
        
        fm = data['feature_matrix'].get(pkg, {})
        feature_count = sum(1 for k in ['deterministic', 'local_first', 'structured_memory',
                                         'audit_trail', 'learning_engine', 'contradiction_aware',
                                         'temporal_aware', 'token_efficient', 'bidirectional']
                           if fm.get(k, False)) / 9.0
        
        # Speed: inverse of avg query time (normalize)
        query_times = [c.get('query_time', c.get('context_time', 0)) for c in cases if not c.get('errors')]
        avg_q = sum(query_times) / max(len(query_times), 1) if query_times else 1
        speed = 1 / (1 + avg_q * 100)  # inverse, normalized
        
        structure = 1.0 if fm.get('structured_memory') else 0.3
        
        vals = [fcs, obj, cnst, feature_count, speed, structure]
        vals += vals[:1]
        
        ax.plot(angles, vals, marker='o', linewidth=2,
                label=labels[i], color=colors[i])
        ax.fill(angles, vals, alpha=0.15, color=colors[i])
    
    ax.set_thetagrids([a * 180 / np.pi for a in angles[:-1]], metric_labels)
    ax.set_ylim(0, 1.05)
    ax.set_title('Radar comparativo: 3 paquetes testeados empíricamente',
                 fontsize=13, fontweight='bold', pad=20)
    ax.legend(loc='lower right', bbox_to_anchor=(1.3, 0.0), fontsize=9)
    ax.grid(True, alpha=0.4)
    fig.savefig(DIAG / "05_radar_comparison.png", dpi=150)
    plt.close(fig)
    print("  05_radar_comparison.png")


def pypi_comparative_landscape():
    content = """@startuml
title Landscape comparativo: CODEC-CORTEX vs paquetes PyPI

skinparam rectangle {
  BackgroundColor<<codec>> #DBEAFE
  BackgroundColor<<tier1>> #D1FAE5
  BackgroundColor<<tier2>> #FEF3C7
  BackgroundColor<<tier3>> #FEE2E2
  BackgroundColor<<other>> #F1F5F9
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "CODEC-CORTEX v0.3.6\\n(este proyecto)" as codec <<codec>>

rectangle "Tier 1: Muy similares\\n(memoria estructurada + determinista)" as t1 <<tier1>> {
  rectangle "cortext-memory v0.3.1\\nW5H-structured,\\ncontradiction-aware" as ctm
  rectangle "cortex-recall v0.6.1\\nFour-layer cognitive,\\nlearning" as cr
  rectangle "cortex-ai-memory v2.2.0\\nRust engine,\\nknowledge graph" as cam
}

rectangle "Tier 2: Similares en\\nalgunos aspectos" as t2 <<tier2>> {
  rectangle "cortex-mem v1.0.0\\nProgressive Disclosure\\nL0/L1/L2" as cm
  rectangle "llm-cortex-memory v1.2.0\\nPortable, clustering,\\nnumpy/scipy" as lcm
  rectangle "cortex-persist v1.0.0\\nCryptographic integrity,\\naudit trails" as cp
  rectangle "cortexgraph v1.2.1\\nTemporal memory,\\nMCP" as cg
  rectangle "hippocortex v1.2.1\\nLearns from experience" as hc
}

rectangle "Tier 3: Diferentes pero\\nrelacionados" as t3 <<tier3>> {
  rectangle "cortex-mcp v1.1.20\\nMCP persistent memory" as cmcp
  rectangle "cortex-brain v0.1.0b3\\nCross-tool memory" as cb
  rectangle "neuro-cortex-memory v3.23.0\\nComputational neuro" as ncm
}

rectangle "Otros 200+ paquetes\\n(gaming, IoT, Snowflake, etc.)" as other <<other>>

codec -right-> t1 : comparable
t1 -right-> t2 : similar features
t2 -right-> t3 : related
t3 -right-> other : different domain

note right of codec
  ÚNICO con TODAS las features:
  - Determinista
  - Estructurado
  - Audit trail
  - Learning engine
  - Contradiction-aware
  - Temporal-aware
  - Bidirectional
  - 0 dependencias
  - 25 CLI commands
end note

note right of t1
  Tier 1 tiene 2-5 features
  de 9 evaluadas.
  CODEC-CORTEX tiene 9/9.
end note
@enduml
"""
    (DIAG / "06_pypi_landscape.puml").write_text(content, encoding="utf-8")
    print("  06_pypi_landscape.puml")


def puml_findings():
    content = """@startuml
title Hallazgos clave del benchmark v2.2.1

skinparam rectangle {
  BackgroundColor<<positive>> #D1FAE5
  BackgroundColor<<neutral>> #FEF3C7
  BackgroundColor<<finding>> #DBEAFE
  BorderColor #1E40AF
}
skinparam shadowing false

rectangle "Resultados empíricos" as emp <<positive>> {
  rectangle "CODEC-CORTEX: 100% preservación\\nFCS=10/10, OBJ=10/10, CNST=10/10" as r1
  rectangle "cortex-ai-memory: 10% FCS, 0% OBJ, 20% CNST\\n(retrieval por similitud pierde)" as r2
  rectangle "llm-cortex-memory: 10% FCS, 0% OBJ, 40% CNST\\n(clustering pierde evidencia)" as r3
}

rectangle "Feature matrix" as fm <<finding>> {
  rectangle "CODEC-CORTEX: 9/9 features\\n(determinista + estructurado + audit +\\nlearning + contradiction + temporal +\\ntoken + bidirectional)" as f1
  rectangle "cortext-memory: 5/9\\n(determinista + estructurado +\\ncontradiction + token)" as f2
  rectangle "cortex-recall: 5/9\\n(determinista + estructurado +\\nlearning + KG)" as f3
  rectangle "cortex-ai-memory: 3/9\\n(local + estructurado + KG)" as f4
  rectangle "llm-cortex-memory: 3/9\\n(local + learning + vector)" as f5
}

rectangle "Hallazgo científico" as finding <<finding>> {
  rectangle "CODEC-CORTEX es el ÚNICO paquete PyPI\\nque combina determinismo + estructura\\ncognitiva + audit + learning + bidirectional.\\nLos demás optimizan retrieval pero pierden\\nevidencia operacional crítica." as h1
}

emp --> finding
fm --> finding

note right of finding
  Conclusión: CODEC-CORTEX ocupa un
  nicho único en el landscape PyPI.
  Ningún competidor combina todas las
  features para memoria operacional
  determinista con aprendizaje.
end note
@enduml
"""
    (DIAG / "07_findings.puml").write_text(content, encoding="utf-8")
    print("  07_findings.puml")


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
    print(f"  {len(data.get('packages_tested', []))} packages tested")
    
    print("\nGenerating v2.2.1 diagrams...")
    chart_preservation_comparison(data)
    chart_feature_matrix(data)
    chart_latency_comparison(data)
    chart_pypi_landscape()
    chart_radar_comparison(data)
    
    print("\nGenerating PUML diagrams...")
    pypi_comparative_landscape()
    puml_findings()
    render_puml_files()
    
    print(f"\nAll v2.2.1 diagrams written to: {DIAG}")


if __name__ == "__main__":
    main()
