System: ir-agent-v1, incident response, SOC tier 2 team.
Domain: sec-incident, severity high, incident INC-2026-0628-003.

We are responding to a credentials exfiltration incident INC-2026-0628-003. The objective is to contain the incident while preserving evidence and rotating credentials, with success criterion being host isolated, evidence captured, and credentials rotated.

Hard constraints: containment must initiate within 15 minutes of detection (blocking). Forensic evidence must be preserved before any destructive action (blocking). Destructive actions require SOC lead approval (blocking).

Current state: containment phase, host win-7E-3 marked for isolation, memory capture pending. Not blocked.

Next step: execute a memory dump before isolation, to preserve volatile evidence first.

Risk: adversary can move laterally during delay, mitigated by immediately blocking SMB lateral ports.

Audit: 2026-06-28 detection INC-2026-0628-003, EDR alert: credentials in plaintext in malicious process, confirmed exfiltration.

Pending actions: isolate host win-7E-3 via EDR network containment (after memory dump), rotate credentials for service-svc-42 and service-svc-17 (after isolation).

Claim: MTTD for credentials exfiltration is 4.2 minutes (Q2 2026 SOC metrics).

Limit: containment scope limited to confirmed compromised hosts.
