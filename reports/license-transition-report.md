<!-- SPDX-License-Identifier: MPL-2.0 -->
<!-- Copyright (c) 2026 Fidel Ernesto Lozada A. -->

# License Transition Report

## Repository

- **Name:** CODEC-CORTEX
- **URL:** github.com/FidelErnesto03/codec-cortex
- **Previous license:** MIT
- **New license:** Mozilla Public License 2.0 (MPL-2.0)
- **Transition version:** v0.4.0
- **MIT final tag:** v0.3.7-mit-final

## Authorship Audit

| Metric | Result |
|--------|--------|
| Sole author | ✅ Fidel Ernesto Lozada A. |
| External contributors | 0 |
| Forks | 0 |
| Automated commits | Only dependabot (2 PRs) |
| Risk | **PASS** — No external contributions to relicense |

## SPDX Headers

| Type | Files | Status |
|------|:-----:|:------:|
| Python (.py) | 123 | ✅ MPL-2.0 |
| Markdown (.md) | 30+ | ✅ MPL-2.0 |
| Shell (.sh) | 1 | ✅ MPL-2.0 |
| .cortex | 1 | ✅ MPL-2.0 |

## License Surfaces Updated

| Surface | Status |
|---------|:------:|
| LICENSE | ✅ MPL-2.0 full text |
| README.md | ✅ License block + SPDX |
| CHANGELOG.md | ✅ v0.4.0 entry |
| CONTRIBUTING.md | ✅ MPL-2.0 contribution terms |
| GOVERNANCE.md | ✅ v0.4.0 |
| pyproject.toml (root) | ✅ MPL-2.0 |
| cli/pyproject.toml | ✅ MPL-2.0 + classifier |
| cli/README.md | ✅ License section |
| setup.sh | ✅ MPL-2.0 SPDX |
| CITATION.cff | ✅ MPL-2.0 |

## Legal Documentation

| File | Status |
|------|:------:|
| docs/legal/license.md | ✅ Created |
| docs/legal/trademark-policy.md | ✅ Created |
| docs/legal/legacy-mit-notice.md | ✅ Created |
| docs/security/privacy.md | ✅ Created |

## Validation

| Gate | Result |
|------|:------:|
| Build CLI | ✅ |
| Tests (464) | ✅ 464 passed, 3 skipped |
| Ruff lint | ✅ All checks passed |
| Active MIT SPDX headers | ✅ **0** |
| MIT license classifiers | ✅ **0** |
| Historical MIT preserved | ✅ 123 refs in benchmarks, tests, legacy docs |

## Remaining MIT References (intentional)

| Location | Reason |
|----------|--------|
| benchmarks/v2.* | Historical artifacts |
| cli/LICENSE | CLI package license file |
| cli/skill/ | Legacy skill copies |
| cli/audit.cortex.md | Historical audit |
| cli/INFORME_DE_ENTREGA_*.md | Historical delivery reports |
| docs/legal/license.md | Legacy MIT notice |
| docs/review/ | Historical review |
| src/tests/fixtures/ | Test fixtures (fixed) |
| src/tests/test_*.py | Test expected values |

## Decision

**PASS** — All active surfaces migrated to MPL-2.0.
Historical MIT artifacts preserved.
Build, tests, lint pass.
Ready for release v0.4.0.
