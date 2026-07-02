"""Default learning policy text used when no ``learn-policies.cortex`` exists.

This mirrors SPEC §4.3 exactly — golden-ratio Fibonacci thresholds,
candidate detection, candidate elevation, policy-driven elevation and
the gates that protect critical sigils.
"""

from __future__ import annotations


def default_policy_text() -> str:
    return """# -- $0: GLOSSARY --
GSIG:IDN{sigil:"IDN", name:"identity", type:"attrs", risk:"B", description:"policy identity"}
GSIG:POL{sigil:"POL", name:"policy", type:"attrs", risk:"M", description:"learning policy"}
GSIG:THR{sigil:"THR", name:"threshold", type:"attrs", risk:"M", description:"learning thresholds"}
GSIG:GTE{sigil:"GTE", name:"gate", type:"attrs", risk:"H", description:"policy gate"}
GSIG:PRT{sigil:"PRT", name:"protected", type:"attrs", risk:"H", description:"protected targets"}

# -- $1: IDENTITY --
IDN:learn_policies{name:"default_learning_policies", version:"0.1.0", target:".cortex/brain.cortex"}

# -- $2: SCORING --
THR:golden_fibonacci{observed:1, repeated:2, pattern:3, candidate:5, ask_user:8, strong_candidate:13, critical:21}

# -- $3: PROTECTED TARGETS --
PRT:critical_sigils{items:"IDN|AXM|CNST:blocking|CLAIM|LIM", mutation:"explicit_user_confirmation"}

# -- $4: CANDIDATE-DRIVEN LEARNING --
POL:candidate_detection{source:"brain", scan_sigils:"WRK|SES|LNG|RSK|NXT|CLAIM|LIM", action:"score", algorithm:"golden_fibonacci_v1"}
POL:candidate_elevation{source:"SES|LNG", target:"LNG|KNW", when:"promotion_score>=8", action:"propose", requires:"user_confirmation"}

# -- $5: POLICY-DRIVEN LEARNING --
POL:auto_ses_to_lng{source:"SES", target:"LNG", when:"promotion_score>=8|user_validated=true", action:"apply", requires:"policy_authorized"}
POL:auto_lng_to_knw{source:"LNG", target:"KNW", when:"promotion_score>=13|user_validated=true|risk_weight>=8", action:"apply", requires:"admin_policy"}

# -- $6: GATES --
GTE:default_mutation{action:"mutate_brain", default:"dry_run_first"}
GTE:critical_mutation{targets:"IDN|AXM|CNST:blocking|CLAIM|LIM|KNW", default:"block_unless_admin_policy"}
"""


__all__ = ["default_policy_text"]
