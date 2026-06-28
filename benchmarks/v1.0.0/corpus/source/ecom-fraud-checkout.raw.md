System: fraud-detector-v3, realtime decision, internal vendor.
Domain: ecom-fraud-checkout, region eu-west, vertical fashion.

The current focus is to evaluate transaction tx_88291 risk score. The objective is to decide block, allow, or manual_review for tx_88291. Success criterion: decision emitted in less than 200ms with documented rationale.

Hard constraints: decision must return in less than 200ms p99 (blocking). No PII in application logs (blocking).

Current work state: scoring phase, score=0.87 computed, awaiting rule engine. Not blocked.

The next step is to apply the rule: if score > 0.85 then block, because score 0.87 exceeds threshold.

Risk: blocking a VIP customer with score 0.87 as false positive. Mitigation: whitelist known corporate domains.

Audit: 2026-06-28 score computation tx_88291, feature_vector hashed, result score=0.87 model=fraud-v3.

Claim: score > 0.85 has precision 0.92 in offline evaluation, evidenced by monthly backtest Q2 2026.

Limit: max 1000 decisions/second capacity.
