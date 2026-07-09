#!/usr/bin/env python3
"""
Generador del corpus de benchmark CODEC-CORTEX.

Construye un corpus Nivel 2 (multidominio) siguiendo el protocolo canónico:
- 10 dominios
- 2-3 casos por dominio
- Para cada caso: representacion .cortex + alternativas (raw_prose, markdown, JSON, YAML-like)
- Hashes SHA-256 registrados
- Metadatos de dominio, proposito operacional, estado, restricciones, riesgos, decisiones

Salida:
- /home/z/my-project/download/benchmark-cortex/corpus/source/*.cortex
- /home/z/my-project/download/benchmark-cortex/corpus/source/*.raw.md
- /home/z/my-project/download/benchmark-cortex/corpus/source/*.md
- /home/z/my-project/download/benchmark-cortex/corpus/source/*.json
- /home/z/my-project/download/benchmark-cortex/corpus/source/*.yaml
- /home/z/my-project/download/benchmark-cortex/corpus/normalized/hashes.json
- /home/z/my-project/download/benchmark-cortex/corpus/normalized/corpus_manifest.json
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List

BASE = Path("/home/z/my-project/download/benchmark-cortex")
SRC = BASE / "corpus" / "source"
NORM = BASE / "corpus" / "normalized"
SRC.mkdir(parents=True, exist_ok=True)
NORM.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Definicion de los 10 dominios y sus casos
# ---------------------------------------------------------------------------
# Cada caso incluye el contenido .cortex completo + alternativas.

CASES: List[Dict] = []

# --- Dominio 1: DevOps / SRE ---
CASES.append({
    "case_id": "devops-k8s-rollout",
    "domain": "devops",
    "purpose": "Operar rollout seguro de servicio stateful en Kubernetes con constraint de PDB",
    "state": "current",
    "restrictions": ["no downtime > 30s", "PDB minAvailable=2", "registry interno"],
    "risks": ["rolling update puede violar PDB si MaxSurge=1"],
    "decisions": ["adoptar MaxSurge=2 MaxUnavailable=0", "healthcheck readinessProbe +5s"],
    "cortex": """# SPDX-FileCopyrightText: 2026 Benchmark Corpus
# SPDX-License-Identifier: MIT

$0: MINIMAL LOCAL GLOSSARY

# Sigil | Name | Type | Risk | Cognitive Layer | Description
# IDN  | identity   | attrs | B | Semantic   | Actor identity
# DOM  | domain     | attrs | B | Semantic   | Operating domain
# CNST | constraint | attrs | H | Prefrontal  | Hard boundary
# FCS  | focus      | attrs | H | Working     | Active attention
# OBJ  | objective  | attrs | H | Working     | Active goal
# WRK  | work       | attrs | M | Working     | Current state
# STP  | step       | attrs | M | Working     | Next action
# NXT  | next       | attrs | M | Working     | Queued action
# AUD  | audit      | attrs | M | Prefrontal  | Verification record
# RSK  | risk       | attrs | M | Prefrontal  | Identified risk
# CLAIM| claim      | attrs | M | Prefrontal  | Verifiable claim
# LIM  | limit      | attrs | M | Prefrontal  | Explicit limit
# SES  | session    | attrs | M | Episodic    | Compressed episode
# KNW  | knowledge  | attrs | B | Semantic    | Stable knowledge
# REF  | reference  | attrs | B | Semantic    | File/source ref

$1: IDENTITY
IDN:operator{name:"sre-oncall", role:"rollout operator", team:"platform-sre"}
DOM:project{area:"k8s-rollout", cluster:"prod-eu-west-1", service:"payments-api"}

$2: OPERATIONAL STATE
CNST:no_downtime{rule:"rolling update must keep minAvailable=2", severity:"blocking", survive:"min"}
CNST:registry{rule:"images only from registry.internal.corp", severity:"warning", survive:"work"}
FCS:primary{what:"Rolling update payments-api v2.4.1 con PDB respected", priority:"high", status:"current", survive:"min"}
OBJ:rollout{goal:"Desplegar v2.4.1 a 6 replicas sin downtime", status:"in_progress", success:"6/6 pods ready con v2.4.1, PDB nunca violado", survive:"min"}
WRK:state{phase:"rolling update", current:"3/6 pods en v2.4.1, 3/6 en v2.4.0", blocked:false, survive:"work"}
STP:next{action:"kubectl rollout status deployment/payments-api --timeout=300s", reason:"verificar progresion del rollout", owner:"sre-oncall", status:"current", survive:"min"}

$3: RISKS AND AUDIT
RSK:pdb_violation{risk:"MaxSurge=1 con PDB minAvailable=2 puede causar downtime", impact:"high", mitigation:"MaxSurge=2 MaxUnavailable=0", status:"current", survive:"recovery"}
AUD:rollout_start{event:"rollout v2.4.1 started", evidence:"kubectl rollout history", result:"3 pods updated, 0 errors", date:"2026-06-28"}

$4: NEXT ACTIONS
NXT:verify_pdb{action:"Verificar PDB status durante rollout", priority:"high", trigger:"after_30s", status:"queued", survive:"work"}
NXT:rollback{action:"kubectl rollout undo si downtime > 30s", priority:"high", trigger:"on_failure", status:"queued", survive:"work"}

$5: CLAIMS AND LIMITS
CLAIM:strategy{statement:"MaxSurge=2 MaxUnavailable=0 respeta PDB minAvailable=2", evidence:"k8s docs + simulation", status:"current"}
LIM:timeout{limit:"Rollout debe completar en < 300s", scope:"operacional", status:"current"}
""",
    "alternatives": {
        "raw_prose": """Operator: sre-oncall, platform-sre team.
Domain: k8s-rollout in cluster prod-eu-west-1, service payments-api.

We are performing a rolling update of payments-api to version v2.4.1 across 6 replicas. The current state is 3 out of 6 pods running v2.4.1 and 3 still on v2.4.0. The rollout is in progress and not blocked.

The hard constraint is no downtime: the rolling update must keep minAvailable=2 at all times. Images must come only from registry.internal.corp.

Our objective is to deploy v2.4.1 to all 6 replicas without downtime, success criterion being all 6 pods ready with the new version and PDB never violated.

The immediate next step is to run kubectl rollout status deployment/payments-api --timeout=300s to verify progress.

Risk: MaxSurge=1 with PDB minAvailable=2 could cause downtime, mitigated by using MaxSurge=2 MaxUnavailable=0.

We claim that MaxSurge=2 MaxUnavailable=0 respects PDB minAvailable=2.

The rollout must complete in under 300 seconds.

Pending actions: verify PDB status after 30s; rollback if downtime exceeds 30s.
""",
        "markdown": """# k8s-rollout: payments-api v2.4.1

## Identity
- **Operator**: sre-oncall (platform-sre)
- **Cluster**: prod-eu-west-1
- **Service**: payments-api

## Constraints
- **no_downtime** (blocking): rolling update must keep minAvailable=2
- **registry** (warning): images only from registry.internal.corp

## Current Focus
Rolling update payments-api v2.4.1 con PDB respected

## Objective
Desplegar v2.4.1 a 6 replicas sin downtime

- Status: in_progress
- Success: 6/6 pods ready con v2.4.1, PDB nunca violado

## Work State
- Phase: rolling update
- Current: 3/6 pods en v2.4.1, 3/6 en v2.4.0
- Blocked: false

## Next Step
Run `kubectl rollout status deployment/payments-api --timeout=300s`

## Risks
- **pdb_violation** (high): MaxSurge=1 con PDB minAvailable=2 puede causar downtime. Mitigation: MaxSurge=2 MaxUnavailable=0.

## Audit
- 2026-06-28: rollout v2.4.1 started. 3 pods updated, 0 errors.

## Claims
- MaxSurge=2 MaxUnavailable=0 respeta PDB minAvailable=2.

## Limits
- Rollout debe completar en < 300s.
""",
        "json": """{
  "identity": {"name": "sre-oncall", "role": "rollout operator", "team": "platform-sre"},
  "domain": {"area": "k8s-rollout", "cluster": "prod-eu-west-1", "service": "payments-api"},
  "constraints": [
    {"id": "no_downtime", "rule": "rolling update must keep minAvailable=2", "severity": "blocking", "survive": "min"},
    {"id": "registry", "rule": "images only from registry.internal.corp", "severity": "warning", "survive": "work"}
  ],
  "focus": {"what": "Rolling update payments-api v2.4.1 con PDB respected", "priority": "high", "status": "current", "survive": "min"},
  "objective": {"goal": "Desplegar v2.4.1 a 6 replicas sin downtime", "status": "in_progress", "success": "6/6 pods ready con v2.4.1, PDB nunca violado", "survive": "min"},
  "work": {"phase": "rolling update", "current": "3/6 pods en v2.4.1, 3/6 en v2.4.0", "blocked": false, "survive": "work"},
  "step": {"action": "kubectl rollout status deployment/payments-api --timeout=300s", "owner": "sre-oncall", "status": "current", "survive": "min"},
  "risks": [
    {"id": "pdb_violation", "risk": "MaxSurge=1 con PDB minAvailable=2 puede causar downtime", "impact": "high", "mitigation": "MaxSurge=2 MaxUnavailable=0"}
  ],
  "audit": [{"event": "rollout v2.4.1 started", "result": "3 pods updated, 0 errors", "date": "2026-06-28"}],
  "claims": [{"id": "strategy", "statement": "MaxSurge=2 MaxUnavailable=0 respeta PDB minAvailable=2"}],
  "limits": [{"id": "timeout", "limit": "Rollout debe completar en < 300s"}]
}
""",
        "yaml": """identity:
  name: sre-oncall
  role: rollout operator
  team: platform-sre
domain:
  area: k8s-rollout
  cluster: prod-eu-west-1
  service: payments-api
constraints:
  - id: no_downtime
    rule: rolling update must keep minAvailable=2
    severity: blocking
    survive: min
  - id: registry
    rule: images only from registry.internal.corp
    severity: warning
    survive: work
focus:
  what: Rolling update payments-api v2.4.1 con PDB respected
  priority: high
  status: current
  survive: min
objective:
  goal: Desplegar v2.4.1 a 6 replicas sin downtime
  status: in_progress
  success: 6/6 pods ready con v2.4.1, PDB nunca violado
  survive: min
work:
  phase: rolling update
  current: 3/6 pods en v2.4.1, 3/6 en v2.4.0
  blocked: false
  survive: work
step:
  action: kubectl rollout status deployment/payments-api --timeout=300s
  owner: sre-oncall
  status: current
  survive: min
""",
    },
})

# --- Dominio 2: E-commerce / Fraud Detection ---
CASES.append({
    "case_id": "ecom-fraud-checkout",
    "domain": "ecommerce",
    "purpose": "Decidir bloqueo de transaccion sospechosa de fraude en checkout",
    "state": "current",
    "restrictions": ["PCI-DSS compliant", "no PII en logs", "max 200ms decision"],
    "risks": ["falso positivo bloquea cliente legitimo", "falso negativo permite chargeback"],
    "decisions": ["score > 0.85 block", "score 0.6-0.85 manual review"],
    "cortex": """# SPDX-FileCopyrightText: 2026 Benchmark Corpus
# SPDX-License-Identifier: MIT

$0: MINIMAL LOCAL GLOSSARY

# Sigil | Name | Type | Risk | Cognitive Layer | Description
# IDN  | identity   | attrs | B | Semantic   | Actor identity
# DOM  | domain     | attrs | B | Semantic   | Operating domain
# CNST | constraint | attrs | H | Prefrontal  | Hard boundary
# FCS  | focus      | attrs | H | Working     | Active attention
# OBJ  | objective  | attrs | H | Working     | Active goal
# WRK  | work       | attrs | M | Working     | Current state
# STP  | step       | attrs | M | Working     | Next action
# NXT  | next       | attrs | M | Working     | Queued action
# AUD  | audit      | attrs | M | Prefrontal  | Verification record
# RSK  | risk       | attrs | M | Prefrontal  | Identified risk
# CLAIM| claim      | attrs | M | Prefrontal  | Verifiable claim
# LIM  | limit      | attrs | M | Prefrontal  | Explicit limit
# STAT | status     | attrs | B | Working     | State classifier

$1: IDENTITY
IDN:system{name:"fraud-detector-v3", role:"realtime decision", vendor:"internal"}
DOM:project{area:"ecom-fraud-checkout", region:"eu-west", vertical:"fashion"}

$2: OPERATIONAL STATE
CNST:latency{rule:"decision must return in < 200ms p99", severity:"blocking", survive:"min"}
CNST:pii{rule:"no PII in application logs", severity:"blocking", survive:"min"}
FCS:primary{what:"Evaluate transaction tx_88291 risk score", priority:"high", status:"current", survive:"min"}
OBJ:decide{goal:"Decide block/allow/manual_review para tx_88291", status:"in_progress", success:"decision emitted in <200ms with documented rationale", survive:"min"}
WRK:state{phase:"scoring", current:"score=0.87 computed, awaiting rule engine", blocked:false, survive:"work"}
STP:next{action:"Apply rule: score > 0.85 -> block", reason:"score 0.87 supera threshold", owner:"fraud-detector", status:"current", survive:"min"}
STAT:txn{state:"current", polarity:"current", survive:"min"}

$3: RISKS AND AUDIT
RSK:false_positive{risk:"Bloquear cliente VIP con score 0.87 falso positivo", impact:"medium", mitigation:"whitelist dominios corporativos conocidos", status:"current", survive:"recovery"}
AUD:score_log{event:"score computation tx_88291", evidence:"feature_vector hashed", result:"score=0.87 model=fraud-v3", date:"2026-06-28"}

$4: CLAIMS AND LIMITS
CLAIM:threshold{statement:"score > 0.85 has precision 0.92 in offline eval", evidence:"monthly backtest Q2 2026", status:"current"}
LIM:throughput{limit:"max 1000 decisions/second", scope:"capacity", status:"current"}
""",
    "alternatives": {
        "raw_prose": """System: fraud-detector-v3, realtime decision, internal vendor.
Domain: ecom-fraud-checkout, region eu-west, vertical fashion.

The current focus is to evaluate transaction tx_88291 risk score. The objective is to decide block, allow, or manual_review for tx_88291. Success criterion: decision emitted in less than 200ms with documented rationale.

Hard constraints: decision must return in less than 200ms p99 (blocking). No PII in application logs (blocking).

Current work state: scoring phase, score=0.87 computed, awaiting rule engine. Not blocked.

The next step is to apply the rule: if score > 0.85 then block, because score 0.87 exceeds threshold.

Risk: blocking a VIP customer with score 0.87 as false positive. Mitigation: whitelist known corporate domains.

Audit: 2026-06-28 score computation tx_88291, feature_vector hashed, result score=0.87 model=fraud-v3.

Claim: score > 0.85 has precision 0.92 in offline evaluation, evidenced by monthly backtest Q2 2026.

Limit: max 1000 decisions/second capacity.
""",
        "markdown": """# ecom-fraud-checkout: tx_88291

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
""",
        "json": """{
  "identity": {"name": "fraud-detector-v3", "role": "realtime decision"},
  "domain": {"area": "ecom-fraud-checkout", "region": "eu-west", "vertical": "fashion"},
  "constraints": [
    {"id": "latency", "rule": "decision must return in < 200ms p99", "severity": "blocking", "survive": "min"},
    {"id": "pii", "rule": "no PII in application logs", "severity": "blocking", "survive": "min"}
  ],
  "focus": {"what": "Evaluate transaction tx_88291 risk score", "priority": "high", "status": "current", "survive": "min"},
  "objective": {"goal": "Decide block/allow/manual_review para tx_88291", "status": "in_progress", "success": "decision emitted in <200ms with documented rationale", "survive": "min"},
  "work": {"phase": "scoring", "current": "score=0.87 computed, awaiting rule engine", "blocked": false, "survive": "work"},
  "step": {"action": "Apply rule: score > 0.85 -> block", "owner": "fraud-detector", "status": "current", "survive": "min"},
  "risks": [{"id": "false_positive", "risk": "Bloquear cliente VIP con score 0.87 falso positivo", "impact": "medium", "mitigation": "whitelist dominios corporativos"}],
  "claims": [{"id": "threshold", "statement": "score > 0.85 has precision 0.92 in offline eval", "evidence": "monthly backtest Q2 2026"}],
  "limits": [{"id": "throughput", "limit": "max 1000 decisions/second"}]
}
""",
        "yaml": """identity:
  name: fraud-detector-v3
  role: realtime decision
domain:
  area: ecom-fraud-checkout
  region: eu-west
constraints:
  - id: latency
    rule: decision must return in < 200ms p99
    severity: blocking
    survive: min
  - id: pii
    rule: no PII in application logs
    severity: blocking
    survive: min
focus:
  what: Evaluate transaction tx_88291 risk score
  priority: high
  status: current
  survive: min
objective:
  goal: Decide block/allow/manual_review para tx_88291
  status: in_progress
  success: decision emitted in <200ms with documented rationale
  survive: min
work:
  phase: scoring
  current: score=0.87 computed, awaiting rule engine
  blocked: false
step:
  action: Apply rule: score > 0.85 -> block
  status: current
  survive: min
""",
    },
})

# --- Dominio 3: Healthcare / Clinical Decision Support ---
CASES.append({
    "case_id": "health-medication-alert",
    "domain": "healthcare",
    "purpose": "Evaluar alerta de interaccion farmacologica antes de prescripcion",
    "state": "current",
    "restrictions": ["HIPAA compliant", "medical disclaimer mandatory", "human-in-the-loop"],
    "risks": ["sobre-alerta causa fatiga de alarmas", "omitir interaccion causa dano"],
    "decisions": ["warfarin + NSAID -> block", "monitor INR semanal"],
    "cortex": """# SPDX-FileCopyrightText: 2026 Benchmark Corpus
# SPDX-License-Identifier: MIT

$0: MINIMAL LOCAL GLOSSARY

# Sigil | Name | Type | Risk | Cognitive Layer | Description
# IDN  | identity   | attrs | B | Semantic   | Actor identity
# DOM  | domain     | attrs | B | Semantic   | Operating domain
# CNST | constraint | attrs | H | Prefrontal  | Hard boundary
# FCS  | focus      | attrs | H | Working     | Active attention
# OBJ  | objective  | attrs | H | Working     | Active goal
# WRK  | work       | attrs | M | Working     | Current state
# STP  | step       | attrs | M | Working     | Next action
# NXT  | next       | attrs | M | Working     | Queued action
# AUD  | audit      | attrs | M | Prefrontal  | Verification record
# RSK  | risk       | attrs | M | Prefrontal  | Identified risk
# CLAIM| claim      | attrs | M | Prefrontal  | Verifiable claim
# LIM  | limit      | attrs | M | Prefrontal  | Explicit limit
# REF  | reference  | attrs | B | Semantic    | Source ref

$1: IDENTITY
IDN:system{name:"cds-engine-v2", role:"clinical decision support", vendor:"internal"}
DOM:project{area:"medication-alert", patient_pseudo_id:"p_4471", encounter:"enc_99201"}

$2: OPERATIONAL STATE
CNST:hitl{rule:"physician must confirm before action", severity:"blocking", survive:"min"}
CNST:disclaimer{rule:"output is advisory, not diagnosis", severity:"blocking", survive:"min"}
FCS:primary{what:"Evaluar interaccion warfarin + ibuprofen en paciente p_4471", priority:"high", status:"current", survive:"min"}
OBJ:alert{goal:"Producir recomendacion block/monitor/allow para prescripcion", status:"in_progress", success:"recomendacion emitida con fuente citada y disclaimer", survive:"min"}
WRK:state{phase:"interaction check", current:"warfarin + ibuprofen detectado, severity=high", blocked:false, survive:"work"}
STP:next{action:"Emitir alerta BLOCK con referencia a Lexicomp", reason:"interaccion aumenta riesgo sangrado", owner:"cds-engine", status:"current", survive:"min"}

$3: RISKS AND AUDIT
RSK:alarm_fatigue{risk:"Exceso de alertas BLOCK causa ignorancia clinica", impact:"medium", mitigation:"tiered severity + override workflow", status:"current", survive:"recovery"}
AUD:check{event:"interaction check p_4471", evidence:"Lexicomp lookup warfarin+ibuprofen", result:"severity=high, recommendation=block", date:"2026-06-28"}

$4: REFERENCES
REF:lexicomp{PATH:"lexicomp://interactions/warfarin-ibuprofen", purpose:"Fuente canonica de interacciones"}
""",
    "alternatives": {
        "raw_prose": """System: cds-engine-v2, clinical decision support, internal vendor.
Domain: medication-alert, patient pseudo id p_4471, encounter enc_99201.

We are evaluating the interaction between warfarin and ibuprofen in patient p_4471. The objective is to produce a recommendation block, monitor, or allow for the prescription, with success criterion being a recommendation emitted with cited source and disclaimer.

Hard constraints: physician must confirm before action (blocking, human-in-the-loop). Output is advisory, not diagnosis (blocking, disclaimer mandatory).

Current state: interaction check phase, warfarin + ibuprofen detected with severity=high. Not blocked.

Next step: emit a BLOCK alert referencing Lexicomp, because the interaction increases bleeding risk.

Risk: excess of BLOCK alerts causes clinical alarm fatigue, mitigated by tiered severity and override workflow.

Audit: 2026-06-28 interaction check p_4471, Lexicomp lookup warfarin+ibuprofen, severity=high, recommendation=block.

Reference: lexicomp://interactions/warfarin-ibuprofen as canonical source.
""",
        "markdown": """# medication-alert: p_4471 / enc_99201

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
""",
        "json": """{
  "identity": {"name": "cds-engine-v2", "role": "clinical decision support"},
  "domain": {"area": "medication-alert", "patient_pseudo_id": "p_4471", "encounter": "enc_99201"},
  "constraints": [
    {"id": "hitl", "rule": "physician must confirm before action", "severity": "blocking", "survive": "min"},
    {"id": "disclaimer", "rule": "output is advisory, not diagnosis", "severity": "blocking", "survive": "min"}
  ],
  "focus": {"what": "Evaluar interaccion warfarin + ibuprofen en paciente p_4471", "priority": "high", "status": "current", "survive": "min"},
  "objective": {"goal": "Producir recomendacion block/monitor/allow para prescripcion", "status": "in_progress", "success": "recomendacion emitida con fuente citada y disclaimer", "survive": "min"},
  "work": {"phase": "interaction check", "current": "warfarin + ibuprofen detectado, severity=high", "blocked": false, "survive": "work"},
  "step": {"action": "Emitir alerta BLOCK con referencia a Lexicomp", "owner": "cds-engine", "status": "current", "survive": "min"},
  "risks": [{"id": "alarm_fatigue", "risk": "Exceso de alertas BLOCK causa ignorancia clinica", "impact": "medium", "mitigation": "tiered severity + override workflow"}],
  "audit": [{"event": "interaction check p_4471", "evidence": "Lexicomp lookup warfarin+ibuprofen", "result": "severity=high, recommendation=block", "date": "2026-06-28"}],
  "references": [{"id": "lexicomp", "path": "lexicomp://interactions/warfarin-ibuprofen"}]
}
""",
        "yaml": """identity:
  name: cds-engine-v2
  role: clinical decision support
domain:
  area: medication-alert
  patient_pseudo_id: p_4471
  encounter: enc_99201
constraints:
  - id: hitl
    rule: physician must confirm before action
    severity: blocking
    survive: min
  - id: disclaimer
    rule: output is advisory, not diagnosis
    severity: blocking
    survive: min
focus:
  what: Evaluar interaccion warfarin + ibuprofen en paciente p_4471
  priority: high
  status: current
  survive: min
objective:
  goal: Producir recomendacion block/monitor/allow para prescripcion
  status: in_progress
  success: recomendacion emitida con fuente citada y disclaimer
  survive: min
work:
  phase: interaction check
  current: warfarin + ibuprofen detectado, severity=high
  blocked: false
step:
  action: Emitir alerta BLOCK con referencia a Lexicomp
  status: current
  survive: min
""",
    },
})

# --- Dominio 4: FinTech / AML Compliance ---
CASES.append({
    "case_id": "fintech-aml-kyc",
    "domain": "fintech",
    "purpose": "Verificar KYC/AML antes de aprobar cuenta de alto valor",
    "state": "current",
    "restrictions": ["GDPR compliant", "MUST log decision rationale", "freeze if score>0.9"],
    "risks": ["onboarding friccion para clientes legitimos", "fraude no detectado"],
    "decisions": ["PEP check mandatory", "manual review para tx > 10k EUR"],
    "cortex": """# SPDX-FileCopyrightText: 2026 Benchmark Corpus
# SPDX-License-Identifier: MIT

$0: MINIMAL LOCAL GLOSSARY

# Sigil | Name | Type | Risk | Cognitive Layer | Description
# IDN  | identity   | attrs | B | Semantic   | Actor identity
# DOM  | domain     | attrs | B | Semantic   | Operating domain
# CNST | constraint | attrs | H | Prefrontal  | Hard boundary
# FCS  | focus      | attrs | H | Working     | Active attention
# OBJ  | objective  | attrs | H | Working     | Active goal
# WRK  | work       | attrs | M | Working     | Current state
# STP  | step       | attrs | M | Working     | Next action
# NXT  | next       | attrs | M | Working     | Queued action
# AUD  | audit      | attrs | M | Prefrontal  | Verification record
# RSK  | risk       | attrs | M | Prefrontal  | Identified risk
# CLAIM| claim      | attrs | M | Prefrontal  | Verifiable claim
# LIM  | limit      | attrs | M | Prefrontal  | Explicit limit

$1: IDENTITY
IDN:system{name:"aml-engine-v4", role:"KYC/AML screening", vendor:"internal"}
DOM:project{area:"aml-kyc", jurisdiction:"EU", customer_id:"cust_5512"}

$2: OPERATIONAL STATE
CNST:freeze{rule:"score > 0.9 MUST freeze account pending review", severity:"blocking", survive:"min"}
CNST:audit_log{rule:"decision rationale MUST be logged with timestamp", severity:"blocking", survive:"min"}
FCS:primary{what:"KYC screening cust_5512 high-value onboarding", priority:"high", status:"current", survive:"min"}
OBJ:approve{goal:"Decidir approve/review/reject para cuenta cust_5512", status:"in_progress", success:"decision emitida con rationale y PEP check", survive:"min"}
WRK:state{phase:"screening", current:"PEP match=true, sanctions=false, score=0.92", blocked:false, survive:"work"}
STP:next{action:"Freeze account y escalar a compliance officer", reason:"score 0.92 > 0.9 trigger freeze", owner:"aml-engine", status:"current", survive:"min"}

$3: RISKS AND CLAIMS
RSK:false_block{risk:"Bloquear cliente legitimo con PEP match falso positivo", impact:"medium", mitigation:"manual review por compliance officer en 24h", status:"current", survive:"recovery"}
CLAIM:pep_threshold{statement:"score > 0.9 correlaciona con risk confirmed en 88% de casos", evidence:"Q1 2026 audit interno", status:"current"}
LIM:sla{limit:"Compliance review debe completar en < 24h", scope:"operacional", status:"current"}
""",
    "alternatives": {
        "raw_prose": """System: aml-engine-v4, KYC/AML screening, internal vendor.
Domain: aml-kyc, jurisdiction EU, customer id cust_5512.

We are performing KYC screening for high-value onboarding of customer cust_5512. The objective is to decide approve, review, or reject the account, with success criterion being a decision emitted with rationale and PEP check.

Hard constraints: score > 0.9 MUST freeze the account pending review (blocking). Decision rationale MUST be logged with timestamp (blocking).

Current state: screening phase, PEP match=true, sanctions=false, score=0.92. Not blocked.

Next step: freeze account and escalate to compliance officer, because score 0.92 exceeds 0.9 threshold triggering freeze.

Risk: blocking legitimate customer with false-positive PEP match, mitigated by manual review by compliance officer within 24h.

Claim: score > 0.9 correlates with confirmed risk in 88% of cases (Q1 2026 internal audit).

Limit: compliance review must complete within 24h.
""",
        "markdown": """# aml-kyc: cust_5512

## Identity
- **System**: aml-engine-v4
- **Role**: KYC/AML screening
- **Jurisdiction**: EU

## Constraints
- **freeze** (blocking): score > 0.9 MUST freeze account pending review
- **audit_log** (blocking): decision rationale MUST be logged with timestamp

## Focus
KYC screening cust_5512 high-value onboarding

## Objective
Decidir approve/review/reject para cuenta cust_5512

- Status: in_progress
- Success: decision emitida con rationale y PEP check

## Work State
- Phase: screening
- Current: PEP match=true, sanctions=false, score=0.92
- Blocked: false

## Next Step
Freeze account y escalar a compliance officer

## Risks
- **false_block** (medium): Bloquear cliente legitimo con PEP match falso positivo. Mitigation: manual review 24h.

## Claims
- score > 0.9 correlaciona con risk confirmed en 88% (Q1 2026 audit).

## Limits
- Compliance review < 24h.
""",
        "json": """{
  "identity": {"name": "aml-engine-v4", "role": "KYC/AML screening"},
  "domain": {"area": "aml-kyc", "jurisdiction": "EU", "customer_id": "cust_5512"},
  "constraints": [
    {"id": "freeze", "rule": "score > 0.9 MUST freeze account pending review", "severity": "blocking", "survive": "min"},
    {"id": "audit_log", "rule": "decision rationale MUST be logged with timestamp", "severity": "blocking", "survive": "min"}
  ],
  "focus": {"what": "KYC screening cust_5512 high-value onboarding", "priority": "high", "status": "current", "survive": "min"},
  "objective": {"goal": "Decidir approve/review/reject para cuenta cust_5512", "status": "in_progress", "success": "decision emitida con rationale y PEP check", "survive": "min"},
  "work": {"phase": "screening", "current": "PEP match=true, sanctions=false, score=0.92", "blocked": false, "survive": "work"},
  "step": {"action": "Freeze account y escalar a compliance officer", "owner": "aml-engine", "status": "current", "survive": "min"},
  "risks": [{"id": "false_block", "risk": "Bloquear cliente legitimo con PEP match falso positivo", "impact": "medium", "mitigation": "manual review por compliance officer en 24h"}],
  "claims": [{"id": "pep_threshold", "statement": "score > 0.9 correlaciona con risk confirmed en 88% de casos", "evidence": "Q1 2026 audit interno"}],
  "limits": [{"id": "sla", "limit": "Compliance review debe completar en < 24h"}]
}
""",
        "yaml": """identity:
  name: aml-engine-v4
  role: KYC/AML screening
domain:
  area: aml-kyc
  jurisdiction: EU
  customer_id: cust_5512
constraints:
  - id: freeze
    rule: score > 0.9 MUST freeze account pending review
    severity: blocking
    survive: min
  - id: audit_log
    rule: decision rationale MUST be logged with timestamp
    severity: blocking
    survive: min
focus:
  what: KYC screening cust_5512 high-value onboarding
  status: current
  survive: min
objective:
  goal: Decidir approve/review/reject para cuenta cust_5512
  status: in_progress
  survive: min
work:
  phase: screening
  current: PEP match=true, sanctions=false, score=0.92
  blocked: false
step:
  action: Freeze account y escalar a compliance officer
  status: current
  survive: min
""",
    },
})

# --- Dominio 5: IoT / Smart Building ---
CASES.append({
    "case_id": "iot-hvac-anomaly",
    "domain": "iot",
    "purpose": "Detectar y responder a anomalia termica en edificio inteligente",
    "state": "current",
    "restrictions": ["comfort band 21-24C", "max energy 150kWh/day", "safety first"],
    "risks": ["sobre-calentamiento de equipos", "falsas anomalias por sensor drift"],
    "decisions": ["anomaly > 2sigma -> alert", "anomaly > 3sigma -> shutdown"],
    "cortex": """# SPDX-FileCopyrightText: 2026 Benchmark Corpus
# SPDX-License-Identifier: MIT

$0: MINIMAL LOCAL GLOSSARY

# Sigil | Name | Type | Risk | Cognitive Layer | Description
# IDN  | identity   | attrs | B | Semantic   | Actor identity
# DOM  | domain     | attrs | B | Semantic   | Operating domain
# CNST | constraint | attrs | H | Prefrontal  | Hard boundary
# FCS  | focus      | attrs | H | Working     | Active attention
# OBJ  | objective  | attrs | H | Working     | Active goal
# WRK  | work       | attrs | M | Working     | Current state
# STP  | step       | attrs | M | Working     | Next action
# NXT  | next       | attrs | M | Working     | Queued action
# AUD  | audit      | attrs | M | Prefrontal  | Verification record
# RSK  | risk       | attrs | M | Prefrontal  | Identified risk
# LIM  | limit      | attrs | M | Prefrontal  | Explicit limit

$1: IDENTITY
IDN:system{name:"building-agent-v1", role:"HVAC control", vendor:"internal"}
DOM:project{area:"iot-hvac", building:"HQ-Tower", zone:"floor-7-east"}

$2: OPERATIONAL STATE
CNST:comfort{rule:"temperature must stay in 21-24C during occupied hours", severity:"blocking", survive:"min"}
CNST:energy{rule:"daily energy consumption must not exceed 150kWh", severity:"warning", survive:"work"}
FCS:primary{what:"Responder a anomalia termica floor-7-east (delta +3.5C en 10min)", priority:"high", status:"current", survive:"min"}
OBJ:mitigate{goal:"Restaurar temperatura a comfort band sin exceder 150kWh", status:"in_progress", success:"temp 21-24C sostenida por 30min", survive:"min"}
WRK:state{phase:"anomaly response", current:"AC unit 7E-3 boosted 100%, temp=27.1C bajando", blocked:false, survive:"work"}
STP:next{action:"Verificar sensor calibration floor-7-east", reason:"descartar sensor drift antes de continuar", owner:"building-agent", status:"current", survive:"min"}

$3: RISKS AND AUDIT
RSK:equipment_overheat{risk:"AC continuo al 100% puede sobrecalentar compressor", impact:"high", mitigation:"cycle 15min on / 5min off si temp < 26C", status:"current", survive:"recovery"}
AUD:anomaly_detected{event:"anomaly floor-7-east", evidence:"delta +3.5C en 10min, z-score 3.2", result:"alert emitted, response initiated", date:"2026-06-28"}

$4: CLAIMS AND LIMITS
CLAIM:threshold{statement:"z-score > 3 correlaciona con falla real en 91% de casos", evidence:"6 meses de telemetria", status:"current"}
LIM:response_time{limit:"response must initiate within 60s of detection", scope:"operacional", status:"current"}
""",
    "alternatives": {
        "raw_prose": """System: building-agent-v1, HVAC control, internal vendor.
Domain: iot-hvac, building HQ-Tower, zone floor-7-east.

The current focus is to respond to a thermal anomaly in floor-7-east, with a delta of +3.5C in 10 minutes. The objective is to restore temperature to the comfort band without exceeding 150kWh daily consumption, with success criterion being temperature sustained in 21-24C for 30 minutes.

Hard constraint: temperature must stay in 21-24C during occupied hours (blocking). Daily energy consumption must not exceed 150kWh (warning).

Current state: anomaly response phase, AC unit 7E-3 boosted at 100%, temperature at 27.1C and decreasing. Not blocked.

Next step: verify sensor calibration for floor-7-east to discard sensor drift before continuing.

Risk: continuous AC at 100% can overheat the compressor, mitigated by cycling 15min on / 5min off if temp drops below 26C.

Audit: 2026-06-28 anomaly floor-7-east, delta +3.5C in 10min, z-score 3.2, alert emitted and response initiated.

Claim: z-score > 3 correlates with real failure in 91% of cases (6 months of telemetry).

Limit: response must initiate within 60 seconds of detection.
""",
        "markdown": """# iot-hvac: HQ-Tower / floor-7-east

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
""",
        "json": """{
  "identity": {"name": "building-agent-v1", "role": "HVAC control"},
  "domain": {"area": "iot-hvac", "building": "HQ-Tower", "zone": "floor-7-east"},
  "constraints": [
    {"id": "comfort", "rule": "temperature must stay in 21-24C during occupied hours", "severity": "blocking", "survive": "min"},
    {"id": "energy", "rule": "daily energy consumption must not exceed 150kWh", "severity": "warning", "survive": "work"}
  ],
  "focus": {"what": "Responder a anomalia termica floor-7-east (delta +3.5C en 10min)", "priority": "high", "status": "current", "survive": "min"},
  "objective": {"goal": "Restaurar temperatura a comfort band sin exceder 150kWh", "status": "in_progress", "success": "temp 21-24C sostenida por 30min", "survive": "min"},
  "work": {"phase": "anomaly response", "current": "AC unit 7E-3 boosted 100%, temp=27.1C bajando", "blocked": false, "survive": "work"},
  "step": {"action": "Verificar sensor calibration floor-7-east", "owner": "building-agent", "status": "current", "survive": "min"},
  "risks": [{"id": "equipment_overheat", "risk": "AC continuo al 100% puede sobrecalentar compressor", "impact": "high", "mitigation": "cycle 15min on / 5min off si temp < 26C"}],
  "audit": [{"event": "anomaly floor-7-east", "evidence": "delta +3.5C en 10min, z-score 3.2", "result": "alert emitted, response initiated", "date": "2026-06-28"}],
  "claims": [{"id": "threshold", "statement": "z-score > 3 correlaciona con falla real en 91% de casos", "evidence": "6 meses de telemetria"}],
  "limits": [{"id": "response_time", "limit": "response must initiate within 60s of detection"}]
}
""",
        "yaml": """identity:
  name: building-agent-v1
  role: HVAC control
domain:
  area: iot-hvac
  building: HQ-Tower
  zone: floor-7-east
constraints:
  - id: comfort
    rule: temperature must stay in 21-24C during occupied hours
    severity: blocking
    survive: min
  - id: energy
    rule: daily energy consumption must not exceed 150kWh
    severity: warning
    survive: work
focus:
  what: Responder a anomalia termica floor-7-east
  status: current
  survive: min
objective:
  goal: Restaurar temperatura a comfort band sin exceder 150kWh
  status: in_progress
  survive: min
work:
  phase: anomaly response
  current: AC unit 7E-3 boosted 100%, temp=27.1C bajando
  blocked: false
step:
  action: Verificar sensor calibration floor-7-east
  status: current
  survive: min
""",
    },
})

# --- Dominio 6: Legal / Contract Review ---
CASES.append({
    "case_id": "legal-contract-redline",
    "domain": "legal",
    "purpose": "Revisar clausulas criticas de contrato SaaS antes de firma",
    "state": "current",
    "restrictions": ["liability cap mandatory", "GDPR DPA mandatory", "auto-renew < 12 meses"],
    "risks": ["clausula ambigua genera litigio", "falta de indemnidad genera perdida"],
    "decisions": ["liability cap = 12 meses fees", "indemnidad mutua"],
    "cortex": """# SPDX-FileCopyrightText: 2026 Benchmark Corpus
# SPDX-License-Identifier: MIT

$0: MINIMAL LOCAL GLOSSARY

# Sigil | Name | Type | Risk | Cognitive Layer | Description
# IDN  | identity   | attrs | B | Semantic   | Actor identity
# DOM  | domain     | attrs | B | Semantic   | Operating domain
# CNST | constraint | attrs | H | Prefrontal  | Hard boundary
# FCS  | focus      | attrs | H | Working     | Active attention
# OBJ  | objective  | attrs | H | Working     | Active goal
# WRK  | work       | attrs | M | Working     | Current state
# STP  | step       | attrs | M | Working     | Next action
# AUD  | audit      | attrs | M | Prefrontal  | Verification record
# RSK  | risk       | attrs | M | Prefrontal  | Identified risk
# CLAIM| claim      | attrs | M | Prefrontal  | Verifiable claim
# LIM  | limit      | attrs | M | Prefrontal  | Explicit limit

$1: IDENTITY
IDN:human{name:"legal-counsel", role:"contract reviewer", team:"legal-ops"}
DOM:project{area:"legal-contract-redline", contract_id:"ctr_2026_0417", counterparty:"VendorX"}

$2: OPERATIONAL STATE
CNST:liability{rule:"liability cap must be >= 12 meses fees", severity:"blocking", survive:"min"}
CNST:dpa{rule:"GDPR DPA must be in place before signature", severity:"blocking", survive:"min"}
CNST:renewal{rule:"auto-renew clause must be < 12 meses", severity:"warning", survive:"work"}
FCS:primary{what:"Redline ctr_2026_0417 con VendorX", priority:"high", status:"current", survive:"min"}
OBJ:approve{goal:"Aprobar o rechazar contrato para firma", status:"in_progress", success:"redline emitido con clausulas criticas verificadas", survive:"min"}
WRK:state{phase:"clause review", current:"liability cap ausente, DPA pendiente, auto-renew=24meses", blocked:true, survive:"work"}
STP:next{action:"Solicitar enmienda: liability cap + DPA + auto-renew 6 meses", reason:"3 clausulas criticas no conformes", owner:"legal-counsel", status:"current", survive:"min"}

$3: RISKS AND CLAIMS
RSK:ambiguous_clause{risk:"Cláusula de indemnidad ambigua genera litigio futuro", impact:"high", mitigation:"exigir lenguaje mutuo y explicito", status:"current", survive:"recovery"}
CLAIM:standard{statement:"liability cap 12 meses fees es estandar de industria SaaS", evidence:"internal benchmark 2025", status:"current"}
LIM:timeline{limit:"Review debe completar en < 5 dias habiles", scope:"SLA legal", status:"current"}
""",
    "alternatives": {
        "raw_prose": """Legal counsel, contract reviewer, legal-ops team.
Domain: legal-contract-redline, contract ctr_2026_0417, counterparty VendorX.

We are redlining contract ctr_2026_0417 with VendorX. The objective is to approve or reject the contract for signature, with success criterion being a redline emitted with critical clauses verified.

Hard constraints: liability cap must be at least 12 months fees (blocking). GDPR DPA must be in place before signature (blocking). Auto-renew clause must be less than 12 months (warning).

Current state: clause review phase. Liability cap is absent, DPA is pending, auto-renew is 24 months. Blocked: true.

Next step: request an amendment for liability cap, DPA, and auto-renew reduced to 6 months, because 3 critical clauses are non-conforming.

Risk: ambiguous indemnity clause generates future litigation, mitigated by requiring mutual and explicit language.

Claim: liability cap of 12 months fees is industry standard for SaaS (internal benchmark 2025).

Limit: review must complete within 5 business days.
""",
        "markdown": """# legal-contract-redline: ctr_2026_0417

## Identity
- **Counsel**: legal-counsel
- **Team**: legal-ops
- **Counterparty**: VendorX

## Constraints
- **liability** (blocking): liability cap must be >= 12 meses fees
- **dpa** (blocking): GDPR DPA must be in place before signature
- **renewal** (warning): auto-renew clause must be < 12 meses

## Focus
Redline ctr_2026_0417 con VendorX

## Objective
Aprobar o rechazar contrato para firma

- Status: in_progress
- Success: redline emitido con clausulas criticas verificadas

## Work State
- Phase: clause review
- Current: liability cap ausente, DPA pendiente, auto-renew=24meses
- Blocked: true

## Next Step
Solicitar enmienda: liability cap + DPA + auto-renew 6 meses

## Risks
- **ambiguous_clause** (high): Cláusula de indemnidad ambigua genera litigio. Mitigation: lenguaje mutuo y explicito.

## Claims
- liability cap 12 meses fees es estandar de industria SaaS (2025).

## Limits
- Review < 5 dias habiles.
""",
        "json": """{
  "identity": {"name": "legal-counsel", "role": "contract reviewer", "team": "legal-ops"},
  "domain": {"area": "legal-contract-redline", "contract_id": "ctr_2026_0417", "counterparty": "VendorX"},
  "constraints": [
    {"id": "liability", "rule": "liability cap must be >= 12 meses fees", "severity": "blocking", "survive": "min"},
    {"id": "dpa", "rule": "GDPR DPA must be in place before signature", "severity": "blocking", "survive": "min"},
    {"id": "renewal", "rule": "auto-renew clause must be < 12 meses", "severity": "warning", "survive": "work"}
  ],
  "focus": {"what": "Redline ctr_2026_0417 con VendorX", "priority": "high", "status": "current", "survive": "min"},
  "objective": {"goal": "Aprobar o rechazar contrato para firma", "status": "in_progress", "success": "redline emitido con clausulas criticas verificadas", "survive": "min"},
  "work": {"phase": "clause review", "current": "liability cap ausente, DPA pendiente, auto-renew=24meses", "blocked": true, "survive": "work"},
  "step": {"action": "Solicitar enmienda: liability cap + DPA + auto-renew 6 meses", "owner": "legal-counsel", "status": "current", "survive": "min"},
  "risks": [{"id": "ambiguous_clause", "risk": "Cláusula de indemnidad ambigua genera litigio futuro", "impact": "high", "mitigation": "exigir lenguaje mutuo y explicito"}],
  "claims": [{"id": "standard", "statement": "liability cap 12 meses fees es estandar de industria SaaS", "evidence": "internal benchmark 2025"}],
  "limits": [{"id": "timeline", "limit": "Review debe completar en < 5 dias habiles"}]
}
""",
        "yaml": """identity:
  name: legal-counsel
  role: contract reviewer
  team: legal-ops
domain:
  area: legal-contract-redline
  contract_id: ctr_2026_0417
  counterparty: VendorX
constraints:
  - id: liability
    rule: liability cap must be >= 12 meses fees
    severity: blocking
    survive: min
  - id: dpa
    rule: GDPR DPA must be in place before signature
    severity: blocking
    survive: min
  - id: renewal
    rule: auto-renew clause must be < 12 meses
    severity: warning
    survive: work
focus:
  what: Redline ctr_2026_0417 con VendorX
  status: current
  survive: min
objective:
  goal: Aprobar o rechazar contrato para firma
  status: in_progress
  survive: min
work:
  phase: clause review
  current: liability cap ausente, DPA pendiente, auto-renew=24meses
  blocked: true
step:
  action: Solicitar enmienda
  status: current
  survive: min
""",
    },
})

# --- Dominio 7: Education / Adaptive Learning ---
CASES.append({
    "case_id": "edu-adaptive-lesson",
    "domain": "education",
    "purpose": "Adaptar leccion segun progreso y emocion del estudiante",
    "state": "current",
    "restrictions": ["no frustration > 3 intentos", "COPPA compliant (under 13)", "max 30min sesion"],
    "risks": ["contenido demasiado facil aburre", "contenido demasiado dificil frustra"],
    "decisions": ["3 fallos consecutivos -> reducir dificultad", "5 aciertos -> subir dificultad"],
    "cortex": """# SPDX-FileCopyrightText: 2026 Benchmark Corpus
# SPDX-License-Identifier: MIT

$0: MINIMAL LOCAL GLOSSARY

# Sigil | Name | Type | Risk | Cognitive Layer | Description
# IDN  | identity   | attrs | B | Semantic   | Actor identity
# DOM  | domain     | attrs | B | Semantic   | Operating domain
# CNST | constraint | attrs | H | Prefrontal  | Hard boundary
# FCS  | focus      | attrs | H | Working     | Active attention
# OBJ  | objective  | attrs | H | Working     | Active goal
# WRK  | work       | attrs | M | Working     | Current state
# STP  | step       | attrs | M | Working     | Next action
# AUD  | audit      | attrs | M | Prefrontal  | Verification record
# RSK  | risk       | attrs | M | Prefrontal  | Identified risk
# CLAIM| claim      | attrs | M | Prefrontal  | Verifiable claim
# LIM  | limit      | attrs | M | Prefrontal  | Explicit limit

$1: IDENTITY
IDN:agent{name:"tutor-agent-v2", role:"adaptive learning", vendor:"edu-platform"}
DOM:project{area:"edu-adaptive", student_id:"stu_3301", subject:"algebra-basics"}

$2: OPERATIONAL STATE
CNST:no_frustration{rule:"3 fallos consecutivos => reducir dificultad", severity:"blocking", survive:"min"}
CNST:coppa{rule:"no PII para estudiantes < 13 anos", severity:"blocking", survive:"min"}
FCS:primary{what:"Adaptar leccion algebra-basics para stu_3301", priority:"high", status:"current", survive:"min"}
OBJ:mastery{goal:"Estudiante alcanza 80% mastery en subtopic eq-lineal", status:"in_progress", success:"3 ejercicios consecutivos correctos", survive:"min"}
WRK:state{phase:"adaptacion", current:"2 fallos consecutivos en eq-lineal-2, dificultad=medium", blocked:false, survive:"work"}
STP:next{action:"Reducir dificultad a easy y ofrecer hint guiado", reason:"prevenir frustration antes del 3er fallo", owner:"tutor-agent", status:"current", survive:"min"}

$3: RISKS AND CLAIMS
RSK:boredom{risk:"5 aciertos consecutivos sin subir dificultad causa abandono", impact:"medium", mitigation:"auto-bump dificultad tras 5 aciertos", status:"current", survive:"recovery"}
CLAIM:zone{statement:"Mantener dificultad en zona proximal desarrollo mejora retencion 35%", evidence:"Vygotsky-based pilot 2025", status:"current"}
LIM:session{limit:"Sesion maximo 30 minutos continuos", scope:"UX", status:"current"}
""",
    "alternatives": {
        "raw_prose": """Agent: tutor-agent-v2, adaptive learning, edu-platform vendor.
Domain: edu-adaptive, student stu_3301, subject algebra-basics.

We are adapting an algebra-basics lesson for student stu_3301. The objective is for the student to reach 80% mastery in subtopic eq-lineal, with success criterion being 3 consecutive correct exercises.

Hard constraints: 3 consecutive failures must reduce difficulty (blocking). No PII for students under 13 years old (blocking, COPPA).

Current state: adaptation phase, 2 consecutive failures on eq-lineal-2, difficulty=medium. Not blocked.

Next step: reduce difficulty to easy and offer a guided hint, to prevent frustration before the third failure.

Risk: 5 consecutive correct answers without increasing difficulty causes abandonment, mitigated by auto-bump difficulty after 5 correct answers.

Claim: maintaining difficulty in the zone of proximal development improves retention by 35% (Vygotsky-based pilot 2025).

Limit: session maximum 30 minutes continuous.
""",
        "markdown": """# edu-adaptive: stu_3301 / algebra-basics

## Identity
- **Agent**: tutor-agent-v2
- **Role**: adaptive learning

## Constraints
- **no_frustration** (blocking): 3 fallos consecutivos => reducir dificultad
- **coppa** (blocking): no PII para estudiantes < 13 anos

## Focus
Adaptar leccion algebra-basics para stu_3301

## Objective
Estudiante alcanza 80% mastery en subtopic eq-lineal

- Status: in_progress
- Success: 3 ejercicios consecutivos correctos

## Work State
- Phase: adaptacion
- Current: 2 fallos consecutivos en eq-lineal-2, dificultad=medium
- Blocked: false

## Next Step
Reducir dificultad a easy y ofrecer hint guiado

## Risks
- **boredom** (medium): 5 aciertos consecutivos sin subir dificultad causa abandono. Mitigation: auto-bump.

## Claims
- Mantener dificultad en zona proximal desarrollo mejora retencion 35% (Vygotsky pilot 2025).

## Limits
- Sesion maximo 30 minutos continuos.
""",
        "json": """{
  "identity": {"name": "tutor-agent-v2", "role": "adaptive learning"},
  "domain": {"area": "edu-adaptive", "student_id": "stu_3301", "subject": "algebra-basics"},
  "constraints": [
    {"id": "no_frustration", "rule": "3 fallos consecutivos => reducir dificultad", "severity": "blocking", "survive": "min"},
    {"id": "coppa", "rule": "no PII para estudiantes < 13 anos", "severity": "blocking", "survive": "min"}
  ],
  "focus": {"what": "Adaptar leccion algebra-basics para stu_3301", "priority": "high", "status": "current", "survive": "min"},
  "objective": {"goal": "Estudiante alcanza 80% mastery en subtopic eq-lineal", "status": "in_progress", "success": "3 ejercicios consecutivos correctos", "survive": "min"},
  "work": {"phase": "adaptacion", "current": "2 fallos consecutivos en eq-lineal-2, dificultad=medium", "blocked": false, "survive": "work"},
  "step": {"action": "Reducir dificultad a easy y ofrecer hint guiado", "owner": "tutor-agent", "status": "current", "survive": "min"},
  "risks": [{"id": "boredom", "risk": "5 aciertos consecutivos sin subir dificultad causa abandono", "impact": "medium", "mitigation": "auto-bump dificultad tras 5 aciertos"}],
  "claims": [{"id": "zone", "statement": "Mantener dificultad en zona proximal desarrollo mejora retencion 35%", "evidence": "Vygotsky-based pilot 2025"}],
  "limits": [{"id": "session", "limit": "Sesion maximo 30 minutos continuos"}]
}
""",
        "yaml": """identity:
  name: tutor-agent-v2
  role: adaptive learning
domain:
  area: edu-adaptive
  student_id: stu_3301
  subject: algebra-basics
constraints:
  - id: no_frustration
    rule: 3 fallos consecutivos => reducir dificultad
    severity: blocking
    survive: min
  - id: coppa
    rule: no PII para estudiantes < 13 anos
    severity: blocking
    survive: min
focus:
  what: Adaptar leccion algebra-basics para stu_3301
  status: current
  survive: min
objective:
  goal: Estudiante alcanza 80% mastery en subtopic eq-lineal
  status: in_progress
  survive: min
work:
  phase: adaptacion
  current: 2 fallos consecutivos en eq-lineal-2, dificultad=medium
  blocked: false
step:
  action: Reducir dificultad a easy y ofrecer hint guiado
  status: current
  survive: min
""",
    },
})

# --- Dominio 8: Cybersecurity / Incident Response ---
CASES.append({
    "case_id": "sec-incident-response",
    "domain": "cybersecurity",
    "purpose": "Responder a incidente de exfiltracion de credenciales",
    "state": "current",
    "restrictions": ["containment < 15min", "preserve forensic evidence", "no destructive action without approval"],
    "risks": ["lateral movement", "evidence destruction"],
    "decisions": ["isolate host", "rotate credentials"],
    "cortex": """# SPDX-FileCopyrightText: 2026 Benchmark Corpus
# SPDX-License-Identifier: MIT

$0: MINIMAL LOCAL GLOSSARY

# Sigil | Name | Type | Risk | Cognitive Layer | Description
# IDN  | identity   | attrs | B | Semantic   | Actor identity
# DOM  | domain     | attrs | B | Semantic   | Operating domain
# CNST | constraint | attrs | H | Prefrontal  | Hard boundary
# FCS  | focus      | attrs | H | Working     | Active attention
# OBJ  | objective  | attrs | H | Working     | Active goal
# WRK  | work       | attrs | M | Working     | Current state
# STP  | step       | attrs | M | Working     | Next action
# NXT  | next       | attrs | M | Working     | Queued action
# AUD  | audit      | attrs | M | Prefrontal  | Verification record
# RSK  | risk       | attrs | M | Prefrontal  | Identified risk
# CLAIM| claim      | attrs | M | Prefrontal  | Verifiable claim
# LIM  | limit      | attrs | M | Prefrontal  | Explicit limit

$1: IDENTITY
IDN:system{name:"ir-agent-v1", role:"incident response", team:"soc-tier2"}
DOM:project{area:"sec-incident", severity:"high", incident_id:"INC-2026-0628-003"}

$2: OPERATIONAL STATE
CNST:containment_sla{rule:"containment must initiate within 15min of detection", severity:"blocking", survive:"min"}
CNST:evidence{rule:"forensic evidence must be preserved before any destructive action", severity:"blocking", survive:"min"}
CNST:approval{rule:"destructive actions require SOC lead approval", severity:"blocking", survive:"min"}
FCS:primary{what:"Responder a exfiltracion credenciales INC-2026-0628-003", priority:"high", status:"current", survive:"min"}
OBJ:contain{goal:"Contener incidente preservando evidencia y rotando credenciales", status:"in_progress", success:"host aislado, evidencia capturada, credenciales rotadas", survive:"min"}
WRK:state{phase:"containment", current:"host win-7E-3 marcado para aislamiento, captura memoria pendiente", blocked:false, survive:"work"}
STP:next{action:"Ejecutar memory dump antes de isolation", reason:"preservar evidencia volatile primero", owner:"ir-agent", status:"current", survive:"min"}

$3: RISKS AND AUDIT
RSK:lateral_movement{risk:"Adversario puede moverse lateralmente durante delay", impact:"high", mitigation:"block SMB lateral ports inmediatamente", status:"current", survive:"recovery"}
AUD:detection{event:"detection INC-2026-0628-003", evidence:"EDR alert: credenciales en plaintext en proceso malicioso", result:"confirmed exfiltration", date:"2026-06-28"}

$4: NEXT ACTIONS
NXT:isolate{action:"Isolar host win-7E-3 via EDR network containment", priority:"high", trigger:"after_memory_dump", status:"queued", survive:"work"}
NXT:rotate{action:"Rotar credenciales servicio-svc-42 y servicio-svc-17", priority:"high", trigger:"after_isolation", status:"queued", survive:"work"}

$5: CLAIMS AND LIMITS
CLAIM:mttd{statement:"MTTD para exfiltracion de credenciales es 4.2min", evidence:"Q2 2026 SOC metrics", status:"current"}
LIM:scope{limit:"Containment scope limited a hosts confirmados comprometidos", scope:"policy", status:"current"}
""",
    "alternatives": {
        "raw_prose": """System: ir-agent-v1, incident response, SOC tier 2 team.
Domain: sec-incident, severity high, incident INC-2026-0628-003.

We are responding to a credentials exfiltration incident INC-2026-0628-003. The objective is to contain the incident while preserving evidence and rotating credentials, with success criterion being host isolated, evidence captured, and credentials rotated.

Hard constraints: containment must initiate within 15 minutes of detection (blocking). Forensic evidence must be preserved before any destructive action (blocking). Destructive actions require SOC lead approval (blocking).

Current state: containment phase, host win-7E-3 marked for isolation, memory capture pending. Not blocked.

Next step: execute a memory dump before isolation, to preserve volatile evidence first.

Risk: adversary can move laterally during delay, mitigated by immediately blocking SMB lateral ports.

Audit: 2026-06-28 detection INC-2026-0628-003, EDR alert: credentials in plaintext in malicious process, confirmed exfiltration.

Pending actions: isolate host win-7E-3 via EDR network containment (after memory dump), rotate credentials for service-svc-42 and service-svc-17 (after isolation).

Claim: MTTD for credentials exfiltration is 4.2 minutes (Q2 2026 SOC metrics).

Limit: containment scope limited to confirmed compromised hosts.
""",
        "markdown": """# sec-incident: INC-2026-0628-003

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
""",
        "json": """{
  "identity": {"name": "ir-agent-v1", "role": "incident response", "team": "soc-tier2"},
  "domain": {"area": "sec-incident", "severity": "high", "incident_id": "INC-2026-0628-003"},
  "constraints": [
    {"id": "containment_sla", "rule": "containment must initiate within 15min of detection", "severity": "blocking", "survive": "min"},
    {"id": "evidence", "rule": "forensic evidence must be preserved before any destructive action", "severity": "blocking", "survive": "min"},
    {"id": "approval", "rule": "destructive actions require SOC lead approval", "severity": "blocking", "survive": "min"}
  ],
  "focus": {"what": "Responder a exfiltracion credenciales INC-2026-0628-003", "priority": "high", "status": "current", "survive": "min"},
  "objective": {"goal": "Contener incidente preservando evidencia y rotando credenciales", "status": "in_progress", "success": "host aislado, evidencia capturada, credenciales rotadas", "survive": "min"},
  "work": {"phase": "containment", "current": "host win-7E-3 marcado para aislamiento, captura memoria pendiente", "blocked": false, "survive": "work"},
  "step": {"action": "Ejecutar memory dump antes de isolation", "owner": "ir-agent", "status": "current", "survive": "min"},
  "risks": [{"id": "lateral_movement", "risk": "Adversario puede moverse lateralmente durante delay", "impact": "high", "mitigation": "block SMB lateral ports inmediatamente"}],
  "audit": [{"event": "detection INC-2026-0628-003", "evidence": "EDR alert: credenciales en plaintext en proceso malicioso", "result": "confirmed exfiltration", "date": "2026-06-28"}],
  "claims": [{"id": "mttd", "statement": "MTTD para exfiltracion de credenciales es 4.2min", "evidence": "Q2 2026 SOC metrics"}],
  "limits": [{"id": "scope", "limit": "Containment scope limited a hosts confirmados comprometidos"}]
}
""",
        "yaml": """identity:
  name: ir-agent-v1
  role: incident response
  team: soc-tier2
domain:
  area: sec-incident
  severity: high
  incident_id: INC-2026-0628-003
constraints:
  - id: containment_sla
    rule: containment must initiate within 15min of detection
    severity: blocking
    survive: min
  - id: evidence
    rule: forensic evidence must be preserved before any destructive action
    severity: blocking
    survive: min
  - id: approval
    rule: destructive actions require SOC lead approval
    severity: blocking
    survive: min
focus:
  what: Responder a exfiltracion credenciales INC-2026-0628-003
  status: current
  survive: min
objective:
  goal: Contener incidente preservando evidencia y rotando credenciales
  status: in_progress
  survive: min
work:
  phase: containment
  current: host win-7E-3 marcado para aislamiento, captura memoria pendiente
  blocked: false
step:
  action: Ejecutar memory dump antes de isolation
  status: current
  survive: min
""",
    },
})

# --- Dominio 9: Robotics / Warehouse Bot ---
CASES.append({
    "case_id": "robotics-warehouse-bot",
    "domain": "robotics",
    "purpose": "Navegar bot de almacen evitando obstaculos dinamicos",
    "state": "current",
    "restrictions": ["max speed 1.5 m/s", "human safety distance 1m", "battery > 20%"],
    "risks": ["colision con humano", "deadlock en pasillo estrecho"],
    "decisions": ["stop if human < 1m", "reroute if deadlock > 5s"],
    "cortex": """# SPDX-FileCopyrightText: 2026 Benchmark Corpus
# SPDX-License-Identifier: MIT

$0: MINIMAL LOCAL GLOSSARY

# Sigil | Name | Type | Risk | Cognitive Layer | Description
# IDN  | identity   | attrs | B | Semantic   | Actor identity
# DOM  | domain     | attrs | B | Semantic   | Operating domain
# CNST | constraint | attrs | H | Prefrontal  | Hard boundary
# FCS  | focus      | attrs | H | Working     | Active attention
# OBJ  | objective  | attrs | H | Working     | Active goal
# WRK  | work       | attrs | M | Working     | Current state
# STP  | step       | attrs | M | Working     | Next action
# AUD  | audit      | attrs | M | Prefrontal  | Verification record
# RSK  | risk       | attrs | M | Prefrontal  | Identified risk
# CLAIM| claim      | attrs | M | Prefrontal  | Verifiable claim
# LIM  | limit      | attrs | M | Prefrontal  | Explicit limit

$1: IDENTITY
IDN:agent{name:"wh-bot-007", role:"warehouse navigation", vendor:"internal"}
DOM:project{area:"robotics-warehouse", facility:"DC-3", aisle:"A-12"}

$2: OPERATIONAL STATE
CNST:safety{rule:"distance to human MUST be > 1m at all times", severity:"blocking", survive:"min"}
CNST:speed{rule:"max speed 1.5 m/s in shared zones", severity:"blocking", survive:"min"}
CNST:battery{rule:"battery MUST stay > 20% to complete mission", severity:"warning", survive:"work"}
FCS:primary{what:"Navegar aisle A-12 evitando peaton detectado", priority:"high", status:"current", survive:"min"}
OBJ:deliver{goal:"Entregar SKU 9921 en dock-4 en < 90s", status:"in_progress", success:"SKU entregado, sin colisiones, battery > 20%", survive:"min"}
WRK:state{phase:"navigation", current:"speed 0.8 m/s, peaton a 1.4m, slowing down", blocked:false, survive:"work"}
STP:next{action:"Reduce speed a 0.3 m/s y mantener rumbo", reason:"peaton a 1.4m aproximando limite 1m", owner:"wh-bot-007", status:"current", survive:"min"}

$3: RISKS AND CLAIMS
RSK:deadlock{risk:"Deadlock en pasillo estrecho si otro bot viene en sentido contrario", impact:"medium", mitigation:"reroute via B-12 si deadlock > 5s", status:"current", survive:"recovery"}
CLAIM:safety_record{statement:"0 colisiones en 999 horas operativas", evidence:"telemetria Q1-Q2 2026", status:"current"}
LIM:payload{limit:"payload max 25 kg", scope:"hardware", status:"current"}
""",
    "alternatives": {
        "raw_prose": """Agent: wh-bot-007, warehouse navigation, internal vendor.
Domain: robotics-warehouse, facility DC-3, aisle A-12.

We are navigating aisle A-12 while avoiding a detected pedestrian. The objective is to deliver SKU 9921 at dock-4 in less than 90 seconds, with success criterion being SKU delivered, no collisions, and battery above 20%.

Hard constraints: distance to human MUST be more than 1 meter at all times (blocking). Max speed 1.5 m/s in shared zones (blocking). Battery MUST stay above 20% to complete mission (warning).

Current state: navigation phase, speed 0.8 m/s, pedestrian at 1.4m, slowing down. Not blocked.

Next step: reduce speed to 0.3 m/s and maintain heading, because pedestrian at 1.4m is approaching the 1m limit.

Risk: deadlock in narrow aisle if another bot comes in opposite direction, mitigated by rerouting via B-12 if deadlock exceeds 5 seconds.

Claim: 0 collisions in 999 operating hours (telemetry Q1-Q2 2026).

Limit: payload maximum 25 kg.
""",
        "markdown": """# robotics-warehouse: wh-bot-007 / DC-3 / A-12

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
""",
        "json": """{
  "identity": {"name": "wh-bot-007", "role": "warehouse navigation"},
  "domain": {"area": "robotics-warehouse", "facility": "DC-3", "aisle": "A-12"},
  "constraints": [
    {"id": "safety", "rule": "distance to human MUST be > 1m at all times", "severity": "blocking", "survive": "min"},
    {"id": "speed", "rule": "max speed 1.5 m/s in shared zones", "severity": "blocking", "survive": "min"},
    {"id": "battery", "rule": "battery MUST stay > 20% to complete mission", "severity": "warning", "survive": "work"}
  ],
  "focus": {"what": "Navegar aisle A-12 evitando peaton detectado", "priority": "high", "status": "current", "survive": "min"},
  "objective": {"goal": "Entregar SKU 9921 en dock-4 en < 90s", "status": "in_progress", "success": "SKU entregado, sin colisiones, battery > 20%", "survive": "min"},
  "work": {"phase": "navigation", "current": "speed 0.8 m/s, peaton a 1.4m, slowing down", "blocked": false, "survive": "work"},
  "step": {"action": "Reduce speed a 0.3 m/s y mantener rumbo", "owner": "wh-bot-007", "status": "current", "survive": "min"},
  "risks": [{"id": "deadlock", "risk": "Deadlock en pasillo estrecho si otro bot viene en sentido contrario", "impact": "medium", "mitigation": "reroute via B-12 si deadlock > 5s"}],
  "claims": [{"id": "safety_record", "statement": "0 colisiones en 999 horas operativas", "evidence": "telemetria Q1-Q2 2026"}],
  "limits": [{"id": "payload", "limit": "payload max 25 kg"}]
}
""",
        "yaml": """identity:
  name: wh-bot-007
  role: warehouse navigation
domain:
  area: robotics-warehouse
  facility: DC-3
  aisle: A-12
constraints:
  - id: safety
    rule: distance to human MUST be > 1m at all times
    severity: blocking
    survive: min
  - id: speed
    rule: max speed 1.5 m/s in shared zones
    severity: blocking
    survive: min
  - id: battery
    rule: battery MUST stay > 20% to complete mission
    severity: warning
    survive: work
focus:
  what: Navegar aisle A-12 evitando peaton detectado
  status: current
  survive: min
objective:
  goal: Entregar SKU 9921 en dock-4 en < 90s
  status: in_progress
  survive: min
work:
  phase: navigation
  current: speed 0.8 m/s, peaton a 1.4m, slowing down
  blocked: false
step:
  action: Reduce speed a 0.3 m/s y mantener rumbo
  status: current
  survive: min
""",
    },
})

# --- Dominio 10: Climate / Energy Grid ---
CASES.append({
    "case_id": "climate-grid-balancing",
    "domain": "climate",
    "purpose": "Balancear red electrica con alta penetracion renovable",
    "state": "current",
    "restrictions": ["frequency 49.8-50.2 Hz", "reserve margin > 5%", "no blackout"],
    "risks": ["sobre-produccion solar causa over-frequency", "rampa de demanda supera reserva"],
    "decisions": ["curtail solar if freq > 50.1", "dispatch gas peaker if reserve < 5%"],
    "cortex": """# SPDX-FileCopyrightText: 2026 Benchmark Corpus
# SPDX-License-Identifier: MIT

$0: MINIMAL LOCAL GLOSSARY

# Sigil | Name | Type | Risk | Cognitive Layer | Description
# IDN  | identity   | attrs | B | Semantic   | Actor identity
# DOM  | domain     | attrs | B | Semantic   | Operating domain
# CNST | constraint | attrs | H | Prefrontal  | Hard boundary
# FCS  | focus      | attrs | H | Working     | Active attention
# OBJ  | objective  | attrs | H | Working     | Active goal
# WRK  | work       | attrs | M | Working     | Current state
# STP  | step       | attrs | M | Working     | Next action
# NXT  | next       | attrs | M | Working     | Queued action
# AUD  | audit      | attrs | M | Prefrontal  | Verification record
# RSK  | risk       | attrs | M | Prefrontal  | Identified risk
# CLAIM| claim      | attrs | M | Prefrontal  | Verifiable claim
# LIM  | limit      | attrs | M | Prefrontal  | Explicit limit

$1: IDENTITY
IDN:system{name:"grid-balancer-v3", role:"automatic generation control", vendor:"tsa-internal"}
DOM:project{area:"climate-grid", region:"EU-continental", frequency_baseline:"50Hz"}

$2: OPERATIONAL STATE
CNST:frequency{rule:"grid frequency MUST stay in 49.8-50.2 Hz", severity:"blocking", survive:"min"}
CNST:reserve{rule:"operating reserve MUST stay > 5% of demand", severity:"blocking", survive:"min"}
CNST:blackout{rule:"no blackout allowed under any circumstance", severity:"blocking", survive:"min"}
FCS:primary{what:"Balancear red ante rampa solar +12% en 15min", priority:"high", status:"current", survive:"min"}
OBJ:balance{goal:"Mantener frecuencia en 49.95-50.05 Hz con reserva > 5%", status:"in_progress", success:"frecuencia estable 30min consecutivos", survive:"min"}
WRK:state{phase:"balancing", current:"freq=50.18 Hz subiendo, solar ramping, reserve=4.8%", blocked:false, survive:"work"}
STP:next{action:"Curtail solar 8% y dispatch gas peaker 200MW", reason:"freq 50.18 cerca limite y reserve 4.8% bajo 5%", owner:"grid-balancer", status:"current", survive:"min"}

$3: RISKS AND CLAIMS
RSK:over_frequency{risk:"Sobre-produccion solar causa over-frequency > 50.2 Hz", impact:"high", mitigation:"curtail automatico si freq > 50.1 Hz", status:"current", survive:"recovery"}
AUD:balancing_event{event:"solar ramp event", evidence:"+12% solar en 15min", result:"curtail initiated, peaker dispatched", date:"2026-06-28"}

$4: CLAIMS AND LIMITS
CLAIM:response{statement:"AGC responde en < 30s a eventos de rampa", evidence:"Q1 2026 compliance report", status:"current"}
LIM:ramp_rate{limit:"max ramp rate 10 MW/min para gas peaker", scope:"hardware", status:"current"}
""",
    "alternatives": {
        "raw_prose": """System: grid-balancer-v3, automatic generation control, internal vendor.
Domain: climate-grid, region EU-continental, frequency baseline 50 Hz.

We are balancing the grid facing a solar ramp of +12% in 15 minutes. The objective is to maintain frequency in 49.95-50.05 Hz with reserve above 5%, with success criterion being stable frequency for 30 consecutive minutes.

Hard constraints: grid frequency MUST stay in 49.8-50.2 Hz (blocking). Operating reserve MUST stay above 5% of demand (blocking). No blackout allowed under any circumstance (blocking).

Current state: balancing phase, frequency at 50.18 Hz rising, solar ramping, reserve at 4.8%. Not blocked.

Next step: curtail solar 8% and dispatch 200 MW gas peaker, because frequency 50.18 is near limit and reserve 4.8% is below 5%.

Risk: solar over-production causes over-frequency above 50.2 Hz, mitigated by automatic curtailment if frequency exceeds 50.1 Hz.

Audit: 2026-06-28 solar ramp event, +12% solar in 15 min, curtail initiated and peaker dispatched.

Claim: AGC responds in less than 30 seconds to ramp events (Q1 2026 compliance report).

Limit: max ramp rate 10 MW/min for gas peaker.
""",
        "markdown": """# climate-grid: EU-continental

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
""",
        "json": """{
  "identity": {"name": "grid-balancer-v3", "role": "automatic generation control"},
  "domain": {"area": "climate-grid", "region": "EU-continental", "frequency_baseline": "50Hz"},
  "constraints": [
    {"id": "frequency", "rule": "grid frequency MUST stay in 49.8-50.2 Hz", "severity": "blocking", "survive": "min"},
    {"id": "reserve", "rule": "operating reserve MUST stay > 5% of demand", "severity": "blocking", "survive": "min"},
    {"id": "blackout", "rule": "no blackout allowed under any circumstance", "severity": "blocking", "survive": "min"}
  ],
  "focus": {"what": "Balancear red ante rampa solar +12% en 15min", "priority": "high", "status": "current", "survive": "min"},
  "objective": {"goal": "Mantener frecuencia en 49.95-50.05 Hz con reserva > 5%", "status": "in_progress", "success": "frecuencia estable 30min consecutivos", "survive": "min"},
  "work": {"phase": "balancing", "current": "freq=50.18 Hz subiendo, solar ramping, reserve=4.8%", "blocked": false, "survive": "work"},
  "step": {"action": "Curtail solar 8% y dispatch gas peaker 200MW", "owner": "grid-balancer", "status": "current", "survive": "min"},
  "risks": [{"id": "over_frequency", "risk": "Sobre-produccion solar causa over-frequency > 50.2 Hz", "impact": "high", "mitigation": "curtail automatico si freq > 50.1 Hz"}],
  "audit": [{"event": "solar ramp event", "evidence": "+12% solar en 15min", "result": "curtail initiated, peaker dispatched", "date": "2026-06-28"}],
  "claims": [{"id": "response", "statement": "AGC responde en < 30s a eventos de rampa", "evidence": "Q1 2026 compliance report"}],
  "limits": [{"id": "ramp_rate", "limit": "max ramp rate 10 MW/min para gas peaker"}]
}
""",
        "yaml": """identity:
  name: grid-balancer-v3
  role: automatic generation control
domain:
  area: climate-grid
  region: EU-continental
  frequency_baseline: 50Hz
constraints:
  - id: frequency
    rule: grid frequency MUST stay in 49.8-50.2 Hz
    severity: blocking
    survive: min
  - id: reserve
    rule: operating reserve MUST stay > 5% of demand
    severity: blocking
    survive: min
  - id: blackout
    rule: no blackout allowed under any circumstance
    severity: blocking
    survive: min
focus:
  what: Balancear red ante rampa solar +12% en 15min
  status: current
  survive: min
objective:
  goal: Mantener frecuencia en 49.95-50.05 Hz con reserva > 5%
  status: in_progress
  survive: min
work:
  phase: balancing
  current: freq=50.18 Hz subiendo, solar ramping, reserve=4.8%
  blocked: false
step:
  action: Curtail solar 8% y dispatch gas peaker 200MW
  status: current
  survive: min
""",
    },
})


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    hashes = {}
    corpus_manifest = {
        "version": "1.0.0",
        "generated_at": "2026-06-28",
        "corpus_level": "L2-multidomain",
        "domains": [],
        "cases": [],
    }

    domains_seen = {}
    for case in CASES:
        cid = case["case_id"]
        dom = case["domain"]
        domains_seen.setdefault(dom, 0)
        domains_seen[dom] += 1

        # .cortex file
        cortex_path = SRC / f"{cid}.cortex"
        cortex_path.write_text(case["cortex"], encoding="utf-8")
        hashes[cid + ".cortex"] = sha256(case["cortex"])

        # alternatives
        for ext, content in case["alternatives"].items():
            ext_suffix = "raw.md" if ext == "raw_prose" else ("md" if ext == "markdown" else ext)
            alt_path = SRC / f"{cid}.{ext_suffix}"
            alt_path.write_text(content, encoding="utf-8")
            hashes[f"{cid}.{ext_suffix}"] = sha256(content)

        corpus_manifest["cases"].append({
            "case_id": cid,
            "domain": dom,
            "purpose": case["purpose"],
            "state": case["state"],
            "restrictions": case["restrictions"],
            "risks": case["risks"],
            "decisions": case["decisions"],
            "alternatives": list(case["alternatives"].keys()),
        })

    corpus_manifest["domains"] = [
        {"name": d, "case_count": n} for d, n in sorted(domains_seen.items())
    ]
    corpus_manifest["totals"] = {
        "domains": len(domains_seen),
        "cases": len(CASES),
        "artifacts": len(hashes),
    }

    (NORM / "hashes.json").write_text(
        json.dumps(hashes, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (NORM / "corpus_manifest.json").write_text(
        json.dumps(corpus_manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Validate .cortex files with cortex CLI
    import subprocess
    print("Validating .cortex files with cortex verify --strict...")
    for case in CASES:
        cid = case["case_id"]
        path = SRC / f"{cid}.cortex"
        r = subprocess.run(
            ["/home/z/.venv/bin/python", "-m", "cortex", "verify",
             str(path), "--strict"],
            capture_output=True, text=True,
        )
        last = r.stdout.strip().split("\n")[-1] if r.stdout else r.stderr.strip().split("\n")[-1]
        print(f"  {cid}: rc={r.returncode} | {last}")

    print(f"\nCorpus generated: {len(CASES)} cases, {len(domains_seen)} domains, {len(hashes)} artifacts")
    print(f"  source dir: {SRC}")
    print(f"  hashes:    {NORM / 'hashes.json'}")
    print(f"  manifest:  {NORM / 'corpus_manifest.json'}")


if __name__ == "__main__":
    main()
