#!/usr/bin/env python3
"""Pre-genera todos los renders HCORTEX necesarios en paralelo."""
import subprocess
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

SRC = Path("/home/z/my-project/download/benchmark-cortex/corpus/source")
CASES = [p.stem for p in SRC.glob("*.cortex")]
PROFILES = ["min", "recovery", "work", "full"]
PYTHON = "/home/z/.venv/bin/python"


def render_one(args):
    case_id, profile = args
    out = f"/tmp/render_{case_id}_{profile}.md"
    cortex_file = str(SRC / f"{case_id}.cortex")
    r = subprocess.run(
        [PYTHON, "-m", "cortex", "render", cortex_file,
         "--mode", "read", "--profile", profile, "--out", out],
        capture_output=True, text=True, timeout=30,
    )
    return (case_id, profile, r.returncode, os.path.exists(out))


def main():
    tasks = [(c, p) for c in CASES for p in PROFILES]
    print(f"Pre-rendering {len(tasks)} HCORTEX files in parallel...")
    done = 0
    with ProcessPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(render_one, t) for t in tasks]
        for f in as_completed(futures):
            case_id, profile, rc, exists = f.result()
            done += 1
            if not exists:
                print(f"  FAIL: {case_id}/{profile} rc={rc}")
            if done % 10 == 0:
                print(f"  {done}/{len(tasks)} done")
    print(f"Done: {done}/{len(tasks)}")


if __name__ == "__main__":
    main()
