# robotics-warehouse: wh-bot-007 / DC-3 / A-12

## Identity
- **Agent**: wh-bot-007
- **Role**: warehouse navigation

## Constraints
- **safety** (blocking): distance to human MUST be > 1m at all times
- **speed** (blocking): max speed 1.5 m/s in shared zones
- **battery** (warning): battery MUST stay > 20% to complete mission

## Focus
Navegar aisle A-12 evitando peaton detectado

## Objective
Entregar SKU 9921 en dock-4 en < 90s

- Status: in_progress
- Success: SKU entregado, sin colisiones, battery > 20%

## Work State
- Phase: navigation
- Current: speed 0.8 m/s, peaton a 1.4m, slowing down
- Blocked: false

## Next Step
Reduce speed a 0.3 m/s y mantener rumbo

## Risks
- **deadlock** (medium): Deadlock en pasillo estrecho si otro bot viene en sentido contrario. Mitigation: reroute via B-12 si deadlock > 5s.

## Claims
- 0 colisiones en 999 horas operativas (Q1-Q2 2026).

## Limits
- payload max 25 kg.
