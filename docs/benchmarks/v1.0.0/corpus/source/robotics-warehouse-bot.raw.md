Agent: wh-bot-007, warehouse navigation, internal vendor.
Domain: robotics-warehouse, facility DC-3, aisle A-12.

We are navigating aisle A-12 while avoiding a detected pedestrian. The objective is to deliver SKU 9921 at dock-4 in less than 90 seconds, with success criterion being SKU delivered, no collisions, and battery above 20%.

Hard constraints: distance to human MUST be more than 1 meter at all times (blocking). Max speed 1.5 m/s in shared zones (blocking). Battery MUST stay above 20% to complete mission (warning).

Current state: navigation phase, speed 0.8 m/s, pedestrian at 1.4m, slowing down. Not blocked.

Next step: reduce speed to 0.3 m/s and maintain heading, because pedestrian at 1.4m is approaching the 1m limit.

Risk: deadlock in narrow aisle if another bot comes in opposite direction, mitigated by rerouting via B-12 if deadlock exceeds 5 seconds.

Claim: 0 collisions in 999 operating hours (telemetry Q1-Q2 2026).

Limit: payload maximum 25 kg.
