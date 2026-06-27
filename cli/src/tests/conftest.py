"""Pytest configuration and shared fixtures."""

import os
import sys
import tempfile

import pytest

# Make the cortex package importable when running tests
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)  # .../cortex/src
if SRC not in sys.path:
    sys.path.insert(0, SRC)


@pytest.fixture
def tmp_cortex_file(tmp_path):
    """Return a path for a temporary .cortex file."""

    return str(tmp_path / "test.cortex")


@pytest.fixture
def brain_doc():
    from cortex.templates import build_brain
    return build_brain()


@pytest.fixture
def skill_doc():
    from cortex.templates import build_skill
    return build_skill()


@pytest.fixture
def package_doc():
    from cortex.templates import build_package
    return build_package()
