Operator: sre-oncall, platform-sre team.
Domain: k8s-rollout in cluster prod-eu-west-1, service payments-api.

We are performing a rolling update of payments-api to version v2.4.1 across 6 replicas. The current state is 3 out of 6 pods running v2.4.1 and 3 still on v2.4.0. The rollout is in progress and not blocked.

The hard constraint is no downtime: the rolling update must keep minAvailable=2 at all times. Images must come only from registry.internal.corp.

Our objective is to deploy v2.4.1 to all 6 replicas without downtime, success criterion being all 6 pods ready with the new version and PDB never violated.

The immediate next step is to run kubectl rollout status deployment/payments-api --timeout=300s to verify progress.

Risk: MaxSurge=1 with PDB minAvailable=2 could cause downtime, mitigated by using MaxSurge=2 MaxUnavailable=0.

We claim that MaxSurge=2 MaxUnavailable=0 respects PDB minAvailable=2.

The rollout must complete in under 300 seconds.

Pending actions: verify PDB status after 30s; rollback if downtime exceeds 30s.
