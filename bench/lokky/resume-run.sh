#!/bin/bash
# BLP-003 run-001 resume: idempotent — skips cells already written.
cd /home/vatrox/workspace/CODEC-CORTEX
n=$(ls bench/lokky/run-001/*.json 2>/dev/null | wc -l)
if [ "$n" -lt 480 ]; then
  echo "run-001 at $n/480 — resuming"
  nohup python3 bench/lokky/run_cells.py bench/lokky/run-001 >> bench/lokky/run-001.log 2>&1 &
  echo "relaunched PID=$!"
else
  echo "run-001 complete ($n/480) — run stats/stats.py"
fi
