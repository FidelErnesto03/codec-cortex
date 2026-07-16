# aml-kyc: cust_5512

## Identity
- **System**: aml-engine-v4
- **Role**: KYC/AML screening
- **Jurisdiction**: EU

## Constraints
- **freeze** (blocking): score > 0.9 MUST freeze account pending review
- **audit_log** (blocking): decision rationale MUST be logged with timestamp

## Focus
KYC screening cust_5512 high-value onboarding

## Objective
Decidir approve/review/reject para cuenta cust_5512

- Status: in_progress
- Success: decision emitida con rationale y PEP check

## Work State
- Phase: screening
- Current: PEP match=true, sanctions=false, score=0.92
- Blocked: false

## Next Step
Freeze account y escalar a compliance officer

## Risks
- **false_block** (medium): Bloquear cliente legitimo con PEP match falso positivo. Mitigation: manual review 24h.

## Claims
- score > 0.9 correlaciona con risk confirmed en 88% (Q1 2026 audit).

## Limits
- Compliance review < 24h.
