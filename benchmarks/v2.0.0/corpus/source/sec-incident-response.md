# sec-incident: INC-2026-0628-003

## Identity
- **System**: ir-agent-v1
- **Role**: incident response
- **Team**: soc-tier2
- **Severity**: high

## Constraints
- **containment_sla** (blocking): containment must initiate within 15min of detection
- **evidence** (blocking): forensic evidence must be preserved before any destructive action
- **approval** (blocking): destructive actions require SOC lead approval

## Focus
Responder a exfiltracion credenciales INC-2026-0628-003

## Objective
Contener incidente preservando evidencia y rotando credenciales

- Status: in_progress
- Success: host aislado, evidencia capturada, credenciales rotadas

## Work State
- Phase: containment
- Current: host win-7E-3 marcado para aislamiento, captura memoria pendiente
- Blocked: false

## Next Step
Ejecutar memory dump antes de isolation

## Risks
- **lateral_movement** (high): Adversario puede moverse lateralmente durante delay. Mitigation: block SMB lateral ports.

## Audit
- 2026-06-28: detection INC-2026-0628-003. EDR alert: credenciales en plaintext.

## Next Actions (queued)
- Isolar host win-7E-3 via EDR (after memory dump)
- Rotar credenciales servicio-svc-42 y servicio-svc-17 (after isolation)

## Claims
- MTTD para exfiltracion de credenciales es 4.2min (Q2 2026 SOC).

## Limits
- Containment scope limited a hosts confirmados comprometidos.
