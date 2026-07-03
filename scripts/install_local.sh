#!/usr/bin/env bash
# install_local.sh — install the CODEC-CORTEX Learning Engine v0.2.0 into
# an existing checkout of the codec-cortex project.
#
# Usage:
#   ./scripts/install_local.sh /ruta/al/proyecto/codec-cortex
#
# This script is idempotent and safe to re-run. It is also safe to run
# on a tree where v0.1.0 was previously installed — it will detect
# the existing learn registration and only add the session block.

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <path-to-codec-cortex-checkout>" >&2
    exit 2
fi

TARGET="$(cd "$1" && pwd)"
PKG_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Installing CODEC-CORTEX Learning Engine v0.2.0 into: $TARGET"
echo "Package source: $PKG_DIR"
echo

# 1. Validate target
if [[ ! -f "$TARGET/cli/src/cortex/cli/main.py" ]]; then
    echo "ERROR: target does not look like a codec-cortex checkout" >&2
    echo "       expected: $TARGET/cli/src/cortex/cli/main.py" >&2
    exit 1
fi

# 2. Copy the learning package (always overwrite — these are the v0.2.0 sources)
echo "[1/6] copying cortex/learning/ package..."
mkdir -p "$TARGET/cli/src/cortex/learning"
cp "$PKG_DIR/cli/src/cortex/learning/"*.py "$TARGET/cli/src/cortex/learning/"

# 3. Patch main.py to register the learn + session subcommands (idempotent)
echo "[2/6] registering 'learn' + 'session' subcommands in main.py..."
MAIN_PY="$TARGET/cli/src/cortex/cli/main.py"
python3 - "$MAIN_PY" <<'PYEOF'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
text = p.read_text(encoding="utf-8")

# Inject the learn + session subparser registration just before "return p"
# inside build_parser. We anchor on the inspect subparser block (the last
# registered one before our additions).
anchor = '    sp.add_argument("--format", choices=["text", "json"], default="text")\n    sp.set_defaults(func=cmd_v2_inspect.run)\n\n'

learn_block = (
    "    # ------------------------------------------------------------------\n"
    "    # learn  (CODEC-CORTEX Learning Engine / CLE)\n"
    "    # Deterministic, local-first learning engine for .cortex workspaces.\n"
    "    # See SPEC §8 for the full command surface.\n"
    "    # ------------------------------------------------------------------\n"
    "    from ..learning.cli import add_learn_subparser\n"
    "    add_learn_subparser(sub)\n"
    "\n"
)
session_block = (
    "    # ------------------------------------------------------------------\n"
    "    # session  (v0.2.0 — CODEC-CORTEX session lifecycle)\n"
    "    # Wraps the learning engine's session module: start / status /\n"
    "    # consolidate / close. See learning-engine-evolution.md §A.\n"
    "    # ------------------------------------------------------------------\n"
    "    from ..learning.session_cli import add_session_subparser\n"
    "    add_session_subparser(sub)\n"
    "\n"
)

# Determine what's already present
has_learn = "from ..learning.cli import add_learn_subparser" in text
has_session = "from ..learning.session_cli import add_session_subparser" in text

if has_learn and has_session:
    print("  learn + session already registered, skipping.")
elif has_learn and not has_session:
    # Only inject the session block after the existing learn block
    learn_anchor = "    from ..learning.cli import add_learn_subparser\n    add_learn_subparser(sub)\n\n"
    if learn_anchor in text:
        text = text.replace(learn_anchor, learn_anchor + session_block, 1)
        p.write_text(text, encoding="utf-8")
        print("  patched: added session block (learn was already present)")
    else:
        print("ERROR: learn block found but anchor missing", file=sys.stderr)
        sys.exit(1)
elif not has_learn and not has_session:
    # Fresh tree — inject both
    if anchor not in text:
        print("ERROR: could not find anchor in main.py", file=sys.stderr)
        sys.exit(1)
    text = text.replace(anchor, anchor + learn_block + session_block, 1)
    p.write_text(text, encoding="utf-8")
    print("  patched: added learn + session blocks")
else:
    # has_session but not has_learn — unusual but possible; inject learn before session
    session_anchor = "    from ..learning.session_cli import add_session_subparser\n"
    if session_anchor in text:
        text = text.replace(session_anchor, learn_block + session_anchor, 1)
        p.write_text(text, encoding="utf-8")
        print("  patched: added learn block (session was already present)")

# Also patch the canonical_cmd sub_action list to include learn/session dests
old_canonical = (
    '    sub_action = getattr(args, "glossary_command", None) or \\\n'
    '                 getattr(args, "micro_command", None) or \\\n'
    '                 getattr(args, "diagram_command", None) or \\\n'
    '                 getattr(args, "audit_command", None)\n'
)
new_canonical = (
    '    sub_action = getattr(args, "glossary_command", None) or \\\n'
    '                 getattr(args, "micro_command", None) or \\\n'
    '                 getattr(args, "diagram_command", None) or \\\n'
    '                 getattr(args, "audit_command", None) or \\\n'
    '                 getattr(args, "learn_command", None) or \\\n'
    '                 getattr(args, "policy_command", None) or \\\n'
    '                 getattr(args, "index_command", None) or \\\n'
    '                 getattr(args, "session_command", None)\n'
)
text = p.read_text(encoding="utf-8")
if old_canonical in text:
    text = text.replace(old_canonical, new_canonical, 1)
    p.write_text(text, encoding="utf-8")
    print("  patched canonical_cmd sub_action list")
PYEOF

# 4. Patch modes.py (idempotent)
echo "[3/6] classifying learn + session subcommands in modes.py..."
MODES_PY="$TARGET/cli/src/cortex/core/modes.py"
if ! grep -q '"learn feedback-show"' "$MODES_PY"; then
    python3 - "$MODES_PY" <<'PYEOF'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
text = p.read_text(encoding="utf-8")

# v0.1.0 baseline — these may already be present
v01_read_old = '''    "learn doctor", "learn policy show", "learn policy validate",
    "learn index status", "learn scan", "learn candidates",
    "learn explain", "learn profile",
})'''
v01_read_new = '''    "learn doctor", "learn policy show", "learn policy validate",
    "learn index status", "learn scan", "learn candidates",
    "learn explain", "learn profile",
    "learn feedback-show", "learn pre-action", "learn post-action",
    # v0.2.0 — session read-only
    "session status",
})'''
if v01_read_old in text:
    text = text.replace(v01_read_old, v01_read_new, 1)
else:
    # Maybe v0.1.0 baseline isn't there either — try injecting from scratch
    base_old = '''    "audit status", "audit snapshot",  # audit reads/snapshots, doesn't mutate .cortex
})'''
    base_new = '''    "audit status", "audit snapshot",  # audit reads/snapshots, doesn't mutate .cortex
    # Learning engine — read-only sub-actions
    "learn doctor", "learn policy show", "learn policy validate",
    "learn index status", "learn scan", "learn candidates",
    "learn explain", "learn profile",
    "learn feedback-show", "learn pre-action", "learn post-action",
    "session status",
})'''
    if base_old in text:
        text = text.replace(base_old, base_new, 1)

# WRITE_COMMANDS — v0.1.0 baseline may be present
v01_write_old = '''    "learn init", "learn index rebuild", "learn index clean",
    "learn policy apply", "learn policy add",
    "learn elevate",
})'''
v01_write_new = '''    "learn init", "learn index rebuild", "learn index clean",
    "learn policy apply", "learn policy add",
    "learn policy set", "learn policy profile", "learn policy reset",
    "learn elevate", "learn feedback",
    # v0.2.0 — session mutations
    "session start", "session consolidate", "session close",
})'''
if v01_write_old in text:
    text = text.replace(v01_write_old, v01_write_new, 1)
else:
    base_old = '''    "glossary add", "glossary update", "glossary delete",
    "micro add", "micro update", "micro delete",
})'''
    base_new = '''    "glossary add", "glossary update", "glossary delete",
    "micro add", "micro update", "micro delete",
    # Learning engine — write sub-actions
    "learn init", "learn index rebuild", "learn index clean",
    "learn policy apply", "learn policy add",
    "learn policy set", "learn policy profile", "learn policy reset",
    "learn elevate", "learn feedback",
    "session start", "session consolidate", "session close",
})'''
    if base_old in text:
        text = text.replace(base_old, base_new, 1)

p.write_text(text, encoding="utf-8")
print("  patched: $MODES_PY")
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
echo "OK -- CODEC-CORTEX Learning Engine v0.2.0 is installed."
echo
echo "Verify with:"
echo "  cortex learn --help"
echo "  cortex session --help"
echo
echo "Run:  ./scripts/run_regression.sh $TARGET"
echo "to execute the regression suite."
