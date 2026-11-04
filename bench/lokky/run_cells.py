#!/usr/bin/env python3
"""BLP-003 cell runner — resumable, native cmd transport (devin -p --model).

Usage: python3 run_cells.py [run_dir] [limit]
Reads bench/lokky/cells/cells.json, skips cells already having a response file,
writes run-XXX/<cell_id>.json {cell_id, model, format, question_id, rep,
response, ts, ok}. Idempotent by design: re-run = continue.
"""
import json, os, subprocess, sys, time, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
CELLS = os.path.join(ROOT, "cells", "cells.json")
CLI_MAP = {
    "moonshot/kimi-k2.7": "kimi-k2.7",
    "deepseek/deepseek-v4.1-flash": "deepseek-v4-1-flash-1017-low",
}

def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "run-001")
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    os.makedirs(run_dir, exist_ok=True)
    cells = json.load(open(CELLS))["cells"]
    done = {f[:-5] for f in os.listdir(run_dir) if f.endswith(".json")}
    todo = [c for c in cells if c["cell_id"] not in done]
    if limit:
        todo = todo[:limit]
    print(f"run_dir={run_dir} todo={len(todo)} done={len(done)}")
    for i, c in enumerate(todo):
        model = CLI_MAP.get(c["model"])
        if not model:
            rec = {"cell_id": c["cell_id"], "ok": False,
                   "error": f"no cli map for {c['model']}"}
        else:
            t0 = time.time()
            try:
                r = subprocess.run(
                    ["devin", "-p", c["prompt"], "--model", model],
                    capture_output=True, text=True, timeout=300,
                    cwd="/home/vatrox/workspace/CODEC-CORTEX")
                rec = {"cell_id": c["cell_id"], "model": c["model"],
                       "format": c["format"], "question_id": c["question_id"],
                       "rep": c["rep"], "response": r.stdout.strip(),
                       "stderr": r.stderr.strip()[-500:], "rc": r.returncode,
                       "secs": round(time.time() - t0, 1),
                       "ts": datetime.datetime.utcnow().isoformat() + "Z",
                       "ok": r.returncode == 0}
            except subprocess.TimeoutExpired:
                rec = {"cell_id": c["cell_id"], "ok": False,
                       "error": "timeout-300s", "secs": 300,
                       "ts": datetime.datetime.utcnow().isoformat() + "Z"}
        with open(os.path.join(run_dir, c["cell_id"] + ".json"), "w") as f:
            json.dump(rec, f, ensure_ascii=False, indent=1)
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(todo)}", flush=True)
    print("BATCH DONE")

if __name__ == "__main__":
    main()
