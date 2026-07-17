import subprocess
import sys
import tempfile
from pathlib import Path
import shutil

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER = REPO_ROOT / "tooling" / "ci" / "check_boundaries.py"
POLICY = REPO_ROOT / "governance" / "dependency-policy.json"


def _run_on_tree(tmp: Path) -> int:
    out = subprocess.run(
        [sys.executable, str(CHECKER), "--policy", str(POLICY), "--root", str(tmp)],
        capture_output=True, text=True,
    )
    return out.returncode


def test_allowed_tree_passes():
    """A tree that respects boundaries must return exit code 0."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "standard").mkdir()
        (root / "standard" / "core.py").write_text("x = 1\n")
        (root / "implementations").mkdir()
        (root / "implementations" / "python").mkdir()
        (root / "implementations" / "python" / "codec.py").write_text(
            "import sys\nfrom standard.core import x\n"
        )
        assert _run_on_tree(root) == 0, "allowed tree must pass"


def test_forbidden_import_fails():
    """standard importing implementations must return non-zero."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "standard").mkdir()
        (root / "standard" / "core.py").write_text(
            "from implementations.python.codec import x\n"
        )
        (root / "implementations").mkdir()
        (root / "implementations" / "python").mkdir()
        (root / "implementations" / "python" / "codec.py").write_text("x = 1\n")
        rc = _run_on_tree(root)
        assert rc != 0, "forbidden import must fail boundary check"


def test_forbidden_path_fails():
    """A standard path containing implementations/ must fail."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "standard").mkdir()
        (root / "standard" / "core").mkdir(parents=True)
        (root / "standard" / "core" / "implementations").mkdir(parents=True)
        (root / "standard" / "core" / "implementations" / "leak.py").write_text("x = 1\n")
        rc = _run_on_tree(root)
        assert rc != 0, "forbidden path layout must fail boundary check"


if __name__ == "__main__":
    test_allowed_tree_passes()
    test_forbidden_import_fails()
    test_forbidden_path_fails()
    print("ALL BOUNDARY TESTS PASSED")
