#!/usr/bin/env python3
"""check_boundaries.py — enforce CODEC-CORTEX dependency and path boundaries.

Pure Python stdlib. Analyzes imports via AST and checks path layout against
governance/dependency-policy.json. Exits non-zero on any violation so it can
serve as a required GitHub status check.

This is a structural gate. It does NOT scan for secrets (that is Gitleaks).
"""
import argparse
import ast
import json
import os
import sys
from pathlib import Path

# Map a directory under the repo root to a logical domain.
DOMAIN_DIRS = {
    "standard": "standard",
    "implementations": "implementations",
    "profiles": "profiles",
    "skill": "skill",
}


def domain_of(path: str) -> str:
    parts = Path(path).parts
    for i, part in enumerate(parts):
        if part in DOMAIN_DIRS and i < len(parts) - 1:
            # e.g. implementations/python/foo.py -> implementations
            return DOMAIN_DIRS[part]
    return "any"


def load_policy(policy_path: str) -> dict:
    with open(policy_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def find_py_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        # skip hidden and vendor dirs
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in ("node_modules", "__pycache__")]
        for fn in filenames:
            if fn.endswith(".py"):
                yield Path(dirpath) / fn


def imports_of(py_file: Path):
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    mods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mods.append(node.module)
    return mods


def _path_violates(rel: str, pattern: str) -> bool:
    """Match a gitignore-style pattern with '**' against a repo-relative path.

    'standard/**/implementations/**' means: path starts with 'standard/'
    and contains an 'implementations/' segment somewhere after it.
    """
    parts = Path(rel).parts
    patt = [p for p in Path(pattern).parts]
    if "**" in patt:
        # split into prefix and suffix around '**'
        idx = patt.index("**")
        prefix = patt[:idx]
        suffix = patt[idx + 1:]
        suffix = [s for s in suffix if s != "**"]
        if tuple(parts[:len(prefix)]) != tuple(prefix):
            return False
        # require suffix segments to appear in order somewhere after prefix
        si = 0
        for part in parts[len(prefix):]:
            if si < len(suffix) and part == suffix[si]:
                si += 1
        return si == len(suffix)
    return tuple(parts) == tuple(patt)


def check(root: Path, policy: dict):
    violations = []

    # Path-layout violations
    for forbidden in policy.get("forbidden_paths", []):
        for py in find_py_files(root):
            rel = str(py.relative_to(root))
            if _path_violates(rel, forbidden):
                violations.append(f"FORBIDDEN_PATH:{rel} matches {forbidden}")

    # Import-direction violations
    forbidden_imports = policy.get("forbidden_imports", [])
    for py in find_py_files(root):
        src_domain = domain_of(str(py.relative_to(root)))
        for mod in imports_of(py):
            for rule in forbidden_imports:
                frm = rule.get("from", "any")
                to = rule.get("to")
                if to and mod.startswith(to) and (frm == "any" or frm == src_domain):
                    violations.append(
                        f"FORBIDDEN_IMPORT:{str(py.relative_to(root))} "
                        f"domain={src_domain} imports {mod} (rule {frm}->{to}: {rule.get('reason','')})"
                    )

    return violations


def main():
    ap = argparse.ArgumentParser(description="CODEC-CORTEX boundary checker")
    ap.add_argument("--policy", required=True, help="path to dependency-policy.json")
    ap.add_argument("--root", required=True, help="repo root to scan")
    args = ap.parse_args()

    policy = load_policy(args.policy)
    root = Path(args.root)
    violations = check(root, policy)

    if violations:
        sys.stderr.write("BOUNDARY VIOLATIONS:\n")
        for v in violations:
            sys.stderr.write(f"  - {v}\n")
        sys.stderr.write(f"total={len(violations)}\n")
        return 1
    sys.stdout.write("BOUNDARY OK: no violations\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
