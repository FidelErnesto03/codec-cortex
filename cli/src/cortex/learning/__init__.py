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
- :mod:`cortex.learning.session`     — session lifecycle (v0.2.0)
- :mod:`cortex.learning.decay`       — exponential cooling / decay (v0.2.0)
- :mod:`cortex.learning.feedback`    — feedback loop & adaptive thresholds (v0.2.0)
- :mod:`cortex.learning.handlers`    — pre_action / post_action handlers (v0.2.0)

Principles enforced here (see SPEC §1):

1. Deterministic — no LLM, no network. Clock-derived values are allowed
   only for explicitly sessional fields (SES:current.start, last_accessed)
   and never influence score computation for static brain entries.
2. Indices are derived and rebuildable — never canonical memory.
3. LLM cannot edit brain or policies directly; all mutations go
   through the engine.
4. ``brain.cortex`` carries no runtime scores and no extensive policies.
5. ``learn-ledger.cortex`` is NOT implemented as a dependency.

v0.2.0 adds (see ``learning-engine-evolution.md``):

- A. Ciclo de sesión (``cortex session start/status/consolidate/close``)
- B. Auto-detección en handlers (``cortex learn pre-action/post-action``)
- C. Decay y enfriamiento (cooling exponencial, survive rules)
- D. Feedback loop (``cortex learn feedback``, thresholds adaptativos)
- E. Thresholds configurables (perfiles aggressive/conservative/default)
"""

from __future__ import annotations

ENGINE_VERSION = "0.2.0"
SCHEMA_VERSION = "0.2.0"
ALGORITHM = "golden_fibonacci_v1"

__all__ = ["ENGINE_VERSION", "SCHEMA_VERSION", "ALGORITHM"]
