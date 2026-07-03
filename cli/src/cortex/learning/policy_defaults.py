"""Default learning policy text used when no ``learn-policies.cortex`` exists.

This mirrors SPEC §4.3 exactly — golden-ratio Fibonacci thresholds,
candidate detection, candidate elevation, policy-driven elevation and
the gates that protect critical sigils.

v0.2.0 adds the configurable-threshold profile entries defined in
``learning-engine-evolution.md`` §E:

- ``POL:fibonacci_thresholds``  — per-sigil promotion thresholds
- ``POL:cooling``               — decay half-life and survival floor
- ``POL:detection``             — pattern-detection window
- ``POL:feedback``              — adaptive-threshold tuning
- ``POL:protected_patterns``    — glob-style protected sigils
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
IDN:learn_policies{name:"default_learning_policies", version:"0.2.0", target:".cortex/brain.cortex"}

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

# -- $7: CONFIGURABLE THRESHOLDS (v0.2.0) --
POL:fibonacci_thresholds{ses:1, lng:3, knw:8, auto_knw:13}
POL:cooling{half_life_days:7, min_score_to_survive:1}
POL:detection{same_sigil_in_window:3, window_hours:72, cross_session:true}
POL:feedback{adaptive:true, adjustment_rate:0.1, min_threshold:1, max_threshold:20}
POL:protected_patterns{patterns:"CNST:*|!:*|FCS:*|OBJ:*"}
"""


# ---------------------------------------------------------------------------
# v0.2.0 — Predefined profiles (aggressive / conservative / default)
# ---------------------------------------------------------------------------


def aggressive_policy_text() -> str:
    """Profile: detect fast, forget fast. For agile projects.

    - SES:1, LNG:2, KNW:5  (lower thresholds → more candidates)
    - half_life: 3 days    (forget fast)
    - detection window: 24h, 2 occurrences
    """

    return default_policy_text().replace(
        'POL:fibonacci_thresholds{ses:1, lng:3, knw:8, auto_knw:13}',
        'POL:fibonacci_thresholds{ses:1, lng:2, knw:5, auto_knw:8}',
    ).replace(
        'POL:cooling{half_life_days:7, min_score_to_survive:1}',
        'POL:cooling{half_life_days:3, min_score_to_survive:1}',
    ).replace(
        'POL:detection{same_sigil_in_window:3, window_hours:72, cross_session:true}',
        'POL:detection{same_sigil_in_window:2, window_hours:24, cross_session:true}',
    )


def conservative_policy_text() -> str:
    """Profile: detect slow, remember long. For compliance / audit.

    - SES:1, LNG:5, KNW:13 (higher thresholds → fewer candidates)
    - half_life: 30 days   (remember long)
    - detection window: 168h (1 week), 5 occurrences
    """

    return default_policy_text().replace(
        'POL:fibonacci_thresholds{ses:1, lng:3, knw:8, auto_knw:13}',
        'POL:fibonacci_thresholds{ses:1, lng:5, knw:13, auto_knw:21}',
    ).replace(
        'POL:cooling{half_life_days:7, min_score_to_survive:1}',
        'POL:cooling{half_life_days:30, min_score_to_survive:1}',
    ).replace(
        'POL:detection{same_sigil_in_window:3, window_hours:72, cross_session:true}',
        'POL:detection{same_sigil_in_window:5, window_hours:168, cross_session:true}',
    )


PROFILES = {
    "default": default_policy_text,
    "aggressive": aggressive_policy_text,
    "conservative": conservative_policy_text,
}


__all__ = [
    "default_policy_text",
    "aggressive_policy_text",
    "conservative_policy_text",
    "PROFILES",
]
