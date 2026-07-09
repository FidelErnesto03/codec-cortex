# ecom-fraud-checkout: tx_88291

## Identity
- **System**: fraud-detector-v3
- **Role**: realtime decision
- **Region**: eu-west

## Constraints
- **latency** (blocking): decision must return in < 200ms p99
- **pii** (blocking): no PII in application logs

## Focus
Evaluate transaction tx_88291 risk score

## Objective
Decide block/allow/manual_review para tx_88291

- Status: in_progress
- Success: decision emitted in <200ms with documented rationale

## Work State
- Phase: scoring
- Current: score=0.87 computed, awaiting rule engine
- Blocked: false

## Next Step
Apply rule: score > 0.85 -> block

## Risks
- **false_positive** (medium): Bloquear cliente VIP con score 0.87 falso positivo. Mitigation: whitelist dominios corporativos.

## Audit
- 2026-06-28: score computation tx_88291. score=0.87 model=fraud-v3.

## Claims
- score > 0.85 has precision 0.92 in offline eval (backtest Q2 2026).

## Limits
- max 1000 decisions/second.
