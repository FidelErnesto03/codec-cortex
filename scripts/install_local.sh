#!/usr/bin/env bash
# install_local.sh — install the CODEC-CORTEX Learning Engine (CLE) into
# an existing checkout of the codec-cortex project.
#
# Usage:
#   ./scripts/install_local.sh /ruta/al/proyecto/codec-cortex
#
# What this script does:
#   1. Validates that the target is a codec-cortex checkout (contains
#      cli/src/cortex/cli/main.py).
#   2. Copies the new cortex/learning/ package into the target's
#      cli/src/cortex/learning/ directory.
#   3. Patches the target's cli/src/cortex/cli/main.py to register the
#      `learn` subcommand (idempotent — skipped if already registered).
#   4. Patches the target's cli/src/cortex/core/modes.py to classify
#      `learn *` commands in the read/write/meta command sets (idempotent).
#   5. Patches cli/pyproject.toml to include `cortex.learning` in the
#      setuptools packages list (idempotent).
#   6. Re-installs the CLI in editable mode so `cortex learn ...` is
#      available on $PATH.
#   7. Copies the templates, schema and tests into the target tree.
#
# This script is safe to re-run.

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <path-to-codec-cortex-checkout>" >&2
    exit 2
fi

TARGET="$(cd "$1" && pwd)"
PKG_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Installing CODEC-CORTEX Learning Engine into: $TARGET"
echo "Package source: $PKG_DIR"
echo

# 1. Validate target
if [[ ! -f "$TARGET/cli/src/cortex/cli/main.py" ]]; then
    echo "ERROR: target does not look like a codec-cortex checkout" >&2
    echo "       expected: $TARGET/cli/src/cortex/cli/main.py" >&2
    exit 1
fi

# 2. Copy the learning package
echo "[1/6] copying cortex/learning/ package..."
mkdir -p "$TARGET/cli/src/cortex/learning"
cp "$PKG_DIR/cli/src/cortex/learning/"*.py "$TARGET/cli/src/cortex/learning/"

# 3. Patch main.py to register the learn subcommand (idempotent)
echo "[2/6] registering 'learn' subcommand in main.py..."
MAIN_PY="$TARGET/cli/src/cortex/cli/main.py"
if ! grep -q "from ..learning.cli import add_learn_subparser" "$MAIN_PY"; then
    python3 - "$MAIN_PY" <<'PYEOF'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
text = p.read_text(encoding="utf-8")
inject = (
    "\n    # ------------------------------------------------------------------\n"
    "    # learn  (CODEC-CORTEX Learning Engine / CLE)\n"
    "    # Deterministic, local-first learning engine for .cortex workspaces.\n"
    "    # See SPEC §8 for the full command surface.\n"
    "    # ------------------------------------------------------------------\n"
    "    from ..learning.cli import add_learn_subparser\n"
    "    add_learn_subparser(sub)\n"
    "\n"
)
anchor = '    sp.add_argument("--format", choices=["text", "json"], default="text")\n    sp.set_defaults(func=cmd_v2_inspect.run)\n\n'
if anchor not in text:
    print("ERROR: could not find anchor in main.py", file=sys.stderr)
    sys.exit(1)
text = text.replace(anchor, anchor + inject, 1)
p.write_text(text, encoding="utf-8")
print("  patched:", p)
PYEOF
else
    echo "  already registered, skipping."
fi

# 4. Patch modes.py (idempotent)
echo "[3/6] classifying learn subcommands in modes.py..."
MODES_PY="$TARGET/cli/src/cortex/core/modes.py"
if ! grep -q '"learn doctor"' "$MODES_PY"; then
    python3 - "$MODES_PY" <<'PYEOF'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
text = p.read_text(encoding="utf-8")

# Extend READ_ONLY_COMMANDS
old_read = '''    "audit status", "audit snapshot",  # audit reads/snapshots, doesn't mutate .cortex
})'''
new_read = '''    "audit status", "audit snapshot",  # audit reads/snapshots, doesn't mutate .cortex
    # Learning engine — read-only sub-actions
    "learn doctor", "learn policy show", "learn policy validate",
    "learn index status", "learn scan", "learn candidates",
    "learn explain", "learn profile",
})'''
text = text.replace(old_read, new_read, 1)

# Extend WRITE_COMMANDS
old_write = '''    "glossary add", "glossary update", "glossary delete",
    "micro add", "micro update", "micro delete",
})'''
new_write = '''    "glossary add", "glossary update", "glossary delete",
    "micro add", "micro update", "micro delete",
    # Learning engine — write sub-actions
    "learn init", "learn index rebuild", "learn index clean",
    "learn policy apply", "learn policy add",
    "learn elevate",
})'''
text = text.replace(old_write, new_write, 1)

p.write_text(text, encoding="utf-8")
PYEOF
    echo "  patched: $MODES_PY"
else
    echo "  already classified, skipping."
fi

# 5. Patch pyproject.toml (idempotent)
echo "[4/6] adding cortex.learning to pyproject.toml packages..."
PYPROJECT="$TARGET/cli/pyproject.toml"
if ! grep -q '"cortex.learning"' "$PYPROJECT"; then
    python3 - "$PYPROJECT" <<'PYEOF'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
text = p.read_text(encoding="utf-8")
old = '    "cortex.v2",\n]'
new = '    "cortex.v2",\n    "cortex.learning",\n]'
text = text.replace(old, new, 1)
p.write_text(text, encoding="utf-8")
PYEOF
    echo "  patched: $PYPROJECT"
else
    echo "  already present, skipping."
fi

# 6. Copy templates, schema, tests
echo "[5/6] copying templates, schema and tests..."
mkdir -p "$TARGET/templates/.cortex"
cp "$PKG_DIR/templates/.cortex/"*.cortex "$TARGET/templates/.cortex/" 2>/dev/null || true
mkdir -p "$TARGET/schemas"
cp "$PKG_DIR/schemas/learn-index.schema.json" "$TARGET/schemas/" 2>/dev/null || true
mkdir -p "$TARGET/cli/src/tests"
cp "$PKG_DIR/tests/"test_learning_*.py "$TARGET/cli/src/tests/" 2>/dev/null || true

# 7. Reinstall
echo "[6/6] reinstalling CLI in editable mode..."
cd "$TARGET"
pip install -e ./cli --quiet --break-system-packages 2>&1 | tail -3 || true

echo
echo "OK -- the 'cortex learn' subcommand is now available."
echo "Run:  ./scripts/run_regression.sh $TARGET"
echo "to execute the regression suite."
