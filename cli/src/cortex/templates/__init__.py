"""Template factories for new ``.cortex`` documents."""

from .minimal_glossary import build_minimal_glossary
from .brain import build_brain
from .skill import build_skill
from .package import build_package

__all__ = ["build_minimal_glossary", "build_brain", "build_skill", "build_package"]
