#!/usr/bin/env python3
"""E2.5 (v0.3.4) — Generate SHA256SUMS manifest for release artifacts.

Scans a directory (default: ``cli/dist/``) for build artifacts
(``*.whl``, ``*.tar.gz``) and produces a ``SHA256SUMS`` file in the
same directory listing each artifact's SHA256 hash.

The output format is the standard ``sha256sum`` format::

    <hash>  <filename>

Usage::

    python scripts/sign_release.py                    # uses cli/dist/
    python scripts/sign_release.py --dist-dir /tmp/x  # custom dir
    python scripts/sign_release.py --check            # verify instead of generate

Exit codes:
    0 — manifest generated/verified successfully
    1 — error (missing dir, no artifacts, hash mismatch)
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

DEFAULT_DIST_DIR = Path(__file__).resolve().parent.parent / "cli" / "dist"
MANIFEST_NAME = "SHA256SUMS"
ARTIFACT_GLOBS = ("*.whl", "*.tar.gz")


def sha256_file(path: Path) -> str:
    """Compute the SHA256 hex digest of ``path``."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_artifacts(dist_dir: Path) -> list[Path]:
    """List build artifacts in ``dist_dir`` (sorted)."""
    if not dist_dir.is_dir():
        return []
    artifacts: list[Path] = []
    for pattern in ARTIFACT_GLOBS:
        artifacts.extend(dist_dir.glob(pattern))
    seen: set[Path] = set()
    unique: list[Path] = []
    for p in sorted(artifacts):
        if p in seen or p.name == MANIFEST_NAME:
            continue
        seen.add(p)
        unique.append(p)
    return unique


def generate_manifest(dist_dir: Path) -> Path:
    """Generate ``SHA256SUMS`` in ``dist_dir``. Returns the manifest path."""
    artifacts = find_artifacts(dist_dir)
    if not artifacts:
        print(
            f"ERROR: no artifacts (*.{', *.'.join(ARTIFACT_GLOBS)}) found in {dist_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    manifest_path = dist_dir / MANIFEST_NAME
    lines: list[str] = []
    for art in artifacts:
        digest = sha256_file(art)
        lines.append(f"{digest}  {art.name}")
        print(f"  signed: {art.name} -> {digest}")

    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nManifest written: {manifest_path}")
    print(f"Total artifacts signed: {len(artifacts)}")
    return manifest_path


def verify_manifest(dist_dir: Path, manifest_path: Path | None = None) -> int:
    """Verify artifacts in ``dist_dir`` against a SHA256SUMS manifest."""
    if manifest_path is None:
        manifest_path = dist_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    failures = 0
    verified = 0
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            print(f"  MALFORMED: {line}", file=sys.stderr)
            failures += 1
            continue
        expected_hash, filename = parts
        filename = filename.lstrip("*")
        artifact_path = dist_dir / filename
        if not artifact_path.is_file():
            print(f"  MISSING: {filename}", file=sys.stderr)
            failures += 1
            continue
        actual_hash = sha256_file(artifact_path)
        if actual_hash == expected_hash:
            print(f"  OK:       {filename} ({actual_hash})")
            verified += 1
        else:
            print(
                f"  MISMATCH: {filename}\n"
                f"    expected: {expected_hash}\n"
                f"    actual:   {actual_hash}",
                file=sys.stderr,
            )
            failures += 1

    print(f"\nVerified: {verified}, failures: {failures}")
    return 0 if failures == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="sign_release",
        description="Generate or verify SHA256SUMS manifest for release artifacts.",
    )
    parser.add_argument(
        "--dist-dir",
        default=str(DEFAULT_DIST_DIR),
        help=f"directory containing artifacts (default: {DEFAULT_DIST_DIR})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify artifacts against existing SHA256SUMS (instead of generating)",
    )
    parser.add_argument(
        "--manifest",
        default=None,
        help="path to a specific SHA256SUMS file (default: <dist-dir>/SHA256SUMS)",
    )
    args = parser.parse_args()

    dist_dir = Path(args.dist_dir).resolve()
    if not dist_dir.is_dir():
        print(f"ERROR: dist dir does not exist: {dist_dir}", file=sys.stderr)
        return 1

    if args.check:
        manifest = Path(args.manifest) if args.manifest else None
        return verify_manifest(dist_dir, manifest)
    else:
        generate_manifest(dist_dir)
        return 0


if __name__ == "__main__":
    sys.exit(main())
