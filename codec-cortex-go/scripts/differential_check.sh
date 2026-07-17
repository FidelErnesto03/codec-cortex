#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PYTHONPATH="$ROOT/reference/python" python3 - "$ROOT/testdata/full.cortex" "$TMP" <<'PY'
from pathlib import Path
import sys
from codec_cortex import parse_cortex, canonicalize, render_hcortex, compile_hcortex

source = Path(sys.argv[1]).read_text(encoding="utf-8")
out = Path(sys.argv[2])
doc = parse_cortex(source)
canonical = canonicalize(doc)
hcortex = render_hcortex(doc)
round_doc, diags = compile_hcortex(hcortex)
if any(d.severity == "error" for d in diags):
    raise SystemExit(diags)
(out / "python.canonical").write_text(canonical, encoding="utf-8")
(out / "python.hcortex").write_text(hcortex, encoding="utf-8")
(out / "python.roundtrip").write_text(canonicalize(round_doc), encoding="utf-8")
PY

go run ./cmd/codec-cortex canonicalize "$ROOT/testdata/full.cortex" > "$TMP/go.canonical"
go run ./cmd/codec-cortex to-hcortex "$ROOT/testdata/full.cortex" > "$TMP/go.hcortex"
go run ./cmd/codec-cortex from-hcortex "$TMP/go.hcortex" > "$TMP/go.roundtrip"

cmp "$TMP/python.canonical" "$TMP/go.canonical"
cmp "$TMP/python.hcortex" "$TMP/go.hcortex"
cmp "$TMP/python.roundtrip" "$TMP/go.roundtrip"

echo "PASS: Python and Go outputs are byte-identical for canonical, HCORTEX and roundtrip fixtures."
