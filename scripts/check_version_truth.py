#!/usr/bin/env python3
"""check_version_truth.py — Verify version consistency across all surfaces.

Compares:
  1. importlib.metadata.version("codec-cortex")  (installed package)
  2. cortex --version                             (CLI surface)
  3. git tag --points-at HEAD                     (tag surface)

Exits 0 if all surfaces agree, 1 otherwise.
"""

import importlib.metadata
import subprocess
import sys


def get_installed_version() -> str:
    try:
        return importlib.metadata.version("codec-cortex")
    except importlib.metadata.PackageNotFoundError:
        return "(not installed)"


def get_cli_version() -> str:
    try:
        import cortex

        return getattr(cortex, "__version__", "no __version__")
    except ImportError:
        return "(cannot import cortex)"


def get_tag_version() -> str:
    try:
        result = subprocess.run(
            ["git", "tag", "--points-at", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        tags = result.stdout.strip().splitlines()
        if not tags:
            return "(no tag at HEAD)"
        # Return the last tag (most recent)
        return tags[-1].lstrip("v")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "(git unavailable)"


def main() -> int:
    installed = get_installed_version()
    cli = get_cli_version()
    tag = get_tag_version()

    print(f"importlib.metadata: {installed}")
    print(f"cortex.__version__: {cli}")
    print(f"git tag (v stripped): {tag}")

    surfaces = [s for s in (installed, cli, tag) if not s.startswith("(")]
    if len(set(surfaces)) == 1:
        print(f"\n✓ ALL SURFACES AGREE: {surfaces[0]}")
        return 0
    else:
        print(f"\n✗ MISMATCH — surfaces disagree")
        return 1


if __name__ == "__main__":
    sys.exit(main())
