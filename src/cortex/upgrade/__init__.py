# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""UpgradeService -- structural .cortex upgrade lifecycle.

Exports:

- :class:`UpgradeService` -- inspect / plan / apply / rollback
- :class:`InspectResult` -- inspection report data model
- :class:`MigrationPlan` -- migration plan data model
"""

from .service import UpgradeService, InspectResult, MigrationPlan, FileStatus, PlanStep

__all__ = [
    "UpgradeService",
    "InspectResult",
    "MigrationPlan",
    "FileStatus",
    "PlanStep",
]
