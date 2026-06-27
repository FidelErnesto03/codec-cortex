"""CODEC-CORTEX CLI — modular deterministic processor for .cortex files.

This package implements the CODEC-CORTEX specification: a structural,
LLM-independent CLI that parses, renders, compiles, verifies and mutates
.cortex files as canonical cognitive memory artefacts.

The package is organized in layers:

- ``core``      : lexer, parser, AST, writer, validator, compare, errors
- ``glossary``  : $0 local glossary model, resolver, minimal, contracts
- ``hcortex``   : HCORTEX-READ and HCORTEX-EDIT renderers and parsers
- ``crud``      : selectors, mutations, atomic transactions
- ``templates`` : brain, skill, package, minimal glossary factories
- ``cli``       : argparse-based command-line entry point
"""

__version__ = "1.1.9"
__all__ = ["__version__"]
