# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""CODEC-CORTEX Learning Engine (CLE).

Deterministic, local-first learning engine for CODEC-CORTEX workspaces.
Operates over a canonical ``.cortex/`` workspace without overloading
``brain.cortex`` and without converting the LLM/SLM into a direct memory
mutator.

Public modules:

- :mod:`cortex.learning.workspace`   — workspace discovery and init
- :mod:`cortex.learning.policy`      — policy parser, validator, evaluator
- :mod:`cortex.learning.conditions`  — safe (eval-free) condition parser
- :mod:`cortex.learning.scoring`     — Fibonacci/golden-ratio scoring
- :mod:`cortex.learning.index`       — rebuildable learn-index
- :mod:`cortex.learning.candidates`  — candidate detection / explain
- :mod:`cortex.learning.elevation`   — propose / apply / dry-run patches
- :mod:`cortex.learning.cli`         — argparse subcommand integration

Principles enforced here (see SPEC §1):

1. Deterministic — no LLM, no network, no clock-derived results.
2. Indices are derived and rebuildable — never canonical memory.
3. LLM cannot edit brain or policies directly; all mutations go
   through the engine.
4. ``brain.cortex`` carries no runtime scores and no extensive policies.
5. ``learn-ledger.cortex`` is NOT implemented in this phase.
"""

from __future__ import annotations

ENGINE_VERSION = "0.1.0"
SCHEMA_VERSION = "0.1.0"
ALGORITHM = "golden_fibonacci_v1"

__all__ = ["ENGINE_VERSION", "SCHEMA_VERSION", "ALGORITHM"]
