# iot-hvac: HQ-Tower / floor-7-east

## Identity
- **System**: building-agent-v1
- **Role**: HVAC control

## Domain
- **Area**: iot-hvac
- **Building**: HQ-Tower
- **Zone**: floor-7-east

## Constraints
- **comfort** (blocking): temperature must stay in 21-24C during occupied hours
- **energy** (warning): daily energy consumption must not exceed 150kWh

## Focus
Responder a anomalia termica floor-7-east (delta +3.5C en 10min)

## Objective
Restaurar temperatura a comfort band sin exceder 150kWh

- Status: in_progress
- Success: temp 21-24C sostenida por 30min

## Work State
- Phase: anomaly response
- Current: AC unit 7E-3 boosted 100%, temp=27.1C bajando
- Blocked: false

## Next Step
Verificar sensor calibration floor-7-east

## Risks
- **equipment_overheat** (high): AC continuo al 100% puede sobrecalentar compressor. Mitigation: cycle 15min on / 5min off si temp < 26C.

## Audit
- 2026-06-28: anomaly floor-7-east. delta +3.5C en 10min, z-score 3.2. Alert emitted.

## Claims
- z-score > 3 correlaciona con falla real en 91% (6 meses telemetria).

## Limits
- response within 60s of detection.
