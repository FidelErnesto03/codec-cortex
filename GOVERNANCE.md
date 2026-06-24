# Governance

CODEC-CORTEX is governed by **Fidel Ernesto Lozada A.** as BDFL (Benevolent Dictator for Life) under the following model:

## Decision Making

| Decision Type | Authority | Process |
|---------------|-----------|---------|
| **Specification changes** | BDFL | Review → Approval → SKILL.md update |
| **Implementation PRs** | BDFL + contributors | PR review → CI passes → Merge |
| **Version releases** | BDFL | Semver: MAJOR.MINOR.PATCH |
| **Licensing changes** | BDFL only | Requires explicit announcement |

## The BDFL Role

- Maintains the canonical `skill/SKILL.md` specification
- Approves or rejects PRs based on protocol consistency
- Arbitrates disputes about protocol interpretation
- Represents the project publicly

## Versioning

CODEC-CORTEX follows [Semantic Versioning](https://semver.org):

- **MAJOR** (x.0.0): Breaking changes to the `.cortex` format. New mandatory sigil, parse rule change.
- **MINOR** (0.x.0): New backward-compatible features. New handlers, principles, sections.
- **PATCH** (0.0.x): Fixes, clarifications, typos, doc adjustments.

### Release Cycle

| Phase | Action | Trigger |
|-------|--------|---------|
| Development | Commits to `main` | Continuous DIALECT cycle work |
| Release Candidate | `vX.Y.Z-rc1` tag | All cycle ACs met |
| Release | `vX.Y.Z` tag + GitHub Release + CHANGELOG | Cycle RE approved |
| Diffusion | PRs to awesome-lists | Same day as release |
| Monitoring | Review incoming issues/PRs | Continuous |

### Commit Convention

```
<type>: <short description>

feat:   New feature (MINOR)
fix:    Bugfix (PATCH)
docs:   Documentation only (PATCH)
spec:   Specification change (MAJOR/MINOR)
chore:  Maintenance, structure (PATCH)
```

Current version: **v0.1.0**

## Contact

- GitHub: [@FidelErnesto03](https://github.com/FidelErnesto03)
- Email: fidelernesto@gmail.com
