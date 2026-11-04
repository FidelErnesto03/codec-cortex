"""BLP-003 — estadística de scoring (sin dependencias)."""
import json, math, sys
from pathlib import Path

def wilson(k, n, z=1.96):
    if n==0: return (0,0,0)
    p=k/n; d=1+z*z/n
    c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (round(p,4), round(c-h,4), round(c+h,4))

def holm(pvals):
    order=sorted(range(len(pvals)), key=lambda i:pvals[i])
    adj=[0]*len(pvals); m=len(pvals)
    for rank,i in enumerate(order): adj[i]=min(1,pvals[i]*(m-rank))
    return adj

def by_cell(scores_dir):
    """scores_dir: carpeta con score_*.json de un run completo."""
    cells={}
    for f in Path(scores_dir).glob("score_*.json"):
        s=json.loads(f.read_text())
        cells.setdefault(s.get("format","?"),[]).append(s)
    return cells

def report(scores_dir):
    cells=by_cell(scores_dir)
    out={}
    for fmt,ss in cells.items():
        vals=[s["score"] for s in ss if s.get("score") is not None]
        n=len(vals); k=sum(vals)
        out[fmt]={"n":n,"k":k,"p_ci":wilson(k,n)}
    return out

if __name__=="__main__":
    print(json.dumps(report(sys.argv[1] if len(sys.argv)>1 else "."),indent=1))
