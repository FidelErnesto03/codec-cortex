# k8s-rollout: payments-api v2.4.1

## Identity
- **Operator**: sre-oncall (platform-sre)
- **Cluster**: prod-eu-west-1
- **Service**: payments-api

## Constraints
- **no_downtime** (blocking): rolling update must keep minAvailable=2
- **registry** (warning): images only from registry.internal.corp

## Current Focus
Rolling update payments-api v2.4.1 con PDB respected

## Objective
Desplegar v2.4.1 a 6 replicas sin downtime

- Status: in_progress
- Success: 6/6 pods ready con v2.4.1, PDB nunca violado

## Work State
- Phase: rolling update
- Current: 3/6 pods en v2.4.1, 3/6 en v2.4.0
- Blocked: false

## Next Step
Run `kubectl rollout status deployment/payments-api --timeout=300s`

## Risks
- **pdb_violation** (high): MaxSurge=1 con PDB minAvailable=2 puede causar downtime. Mitigation: MaxSurge=2 MaxUnavailable=0.

## Audit
- 2026-06-28: rollout v2.4.1 started. 3 pods updated, 0 errors.

## Claims
- MaxSurge=2 MaxUnavailable=0 respeta PDB minAvailable=2.

## Limits
- Rollout debe completar en < 300s.
