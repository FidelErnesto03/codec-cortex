System: grid-balancer-v3, automatic generation control, internal vendor.
Domain: climate-grid, region EU-continental, frequency baseline 50 Hz.

We are balancing the grid facing a solar ramp of +12% in 15 minutes. The objective is to maintain frequency in 49.95-50.05 Hz with reserve above 5%, with success criterion being stable frequency for 30 consecutive minutes.

Hard constraints: grid frequency MUST stay in 49.8-50.2 Hz (blocking). Operating reserve MUST stay above 5% of demand (blocking). No blackout allowed under any circumstance (blocking).

Current state: balancing phase, frequency at 50.18 Hz rising, solar ramping, reserve at 4.8%. Not blocked.

Next step: curtail solar 8% and dispatch 200 MW gas peaker, because frequency 50.18 is near limit and reserve 4.8% is below 5%.

Risk: solar over-production causes over-frequency above 50.2 Hz, mitigated by automatic curtailment if frequency exceeds 50.1 Hz.

Audit: 2026-06-28 solar ramp event, +12% solar in 15 min, curtail initiated and peaker dispatched.

Claim: AGC responds in less than 30 seconds to ramp events (Q1 2026 compliance report).

Limit: max ramp rate 10 MW/min for gas peaker.
