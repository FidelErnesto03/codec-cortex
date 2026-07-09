# medication-alert: p_4471 / enc_99201

## Identity
- **System**: cds-engine-v2
- **Role**: clinical decision support

## Domain
- **Area**: medication-alert
- **Patient pseudo id**: p_4471
- **Encounter**: enc_99201

## Constraints
- **hitl** (blocking): physician must confirm before action
- **disclaimer** (blocking): output is advisory, not diagnosis

## Focus
Evaluar interaccion warfarin + ibuprofen en paciente p_4471

## Objective
Producir recomendacion block/monitor/allow para prescripcion

- Status: in_progress
- Success: recomendacion emitida con fuente citada y disclaimer

## Work State
- Phase: interaction check
- Current: warfarin + ibuprofen detectado, severity=high
- Blocked: false

## Next Step
Emitir alerta BLOCK con referencia a Lexicomp

## Risks
- **alarm_fatigue** (medium): Exceso de alertas BLOCK causa ignorancia clinica. Mitigation: tiered severity + override workflow.

## Audit
- 2026-06-28: interaction check p_4471. Lexicomp warfarin+ibuprofen, severity=high, recommendation=block.

## References
- lexicomp://interactions/warfarin-ibuprofen
