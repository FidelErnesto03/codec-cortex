System: building-agent-v1, HVAC control, internal vendor.
Domain: iot-hvac, building HQ-Tower, zone floor-7-east.

The current focus is to respond to a thermal anomaly in floor-7-east, with a delta of +3.5C in 10 minutes. The objective is to restore temperature to the comfort band without exceeding 150kWh daily consumption, with success criterion being temperature sustained in 21-24C for 30 minutes.

Hard constraint: temperature must stay in 21-24C during occupied hours (blocking). Daily energy consumption must not exceed 150kWh (warning).

Current state: anomaly response phase, AC unit 7E-3 boosted at 100%, temperature at 27.1C and decreasing. Not blocked.

Next step: verify sensor calibration for floor-7-east to discard sensor drift before continuing.

Risk: continuous AC at 100% can overheat the compressor, mitigated by cycling 15min on / 5min off if temp drops below 26C.

Audit: 2026-06-28 anomaly floor-7-east, delta +3.5C in 10min, z-score 3.2, alert emitted and response initiated.

Claim: z-score > 3 correlates with real failure in 91% of cases (6 months of telemetry).

Limit: response must initiate within 60 seconds of detection.
