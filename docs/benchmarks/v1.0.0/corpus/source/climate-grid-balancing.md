# climate-grid: EU-continental

## Identity
- **System**: grid-balancer-v3
- **Role**: automatic generation control

## Constraints
- **frequency** (blocking): grid frequency MUST stay in 49.8-50.2 Hz
- **reserve** (blocking): operating reserve MUST stay > 5% of demand
- **blackout** (blocking): no blackout allowed under any circumstance

## Focus
Balancear red ante rampa solar +12% en 15min

## Objective
Mantener frecuencia en 49.95-50.05 Hz con reserva > 5%

- Status: in_progress
- Success: frecuencia estable 30min consecutivos

## Work State
- Phase: balancing
- Current: freq=50.18 Hz subiendo, solar ramping, reserve=4.8%
- Blocked: false

## Next Step
Curtail solar 8% y dispatch gas peaker 200MW

## Risks
- **over_frequency** (high): Sobre-produccion solar causa over-frequency > 50.2 Hz. Mitigation: curtail automatico si freq > 50.1 Hz.

## Audit
- 2026-06-28: solar ramp event. +12% solar en 15min. Curtail initiated, peaker dispatched.

## Claims
- AGC responde en < 30s a eventos de rampa (Q1 2026).

## Limits
- max ramp rate 10 MW/min para gas peaker.
