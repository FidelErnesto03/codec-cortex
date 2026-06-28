System: aml-engine-v4, KYC/AML screening, internal vendor.
Domain: aml-kyc, jurisdiction EU, customer id cust_5512.

We are performing KYC screening for high-value onboarding of customer cust_5512. The objective is to decide approve, review, or reject the account, with success criterion being a decision emitted with rationale and PEP check.

Hard constraints: score > 0.9 MUST freeze the account pending review (blocking). Decision rationale MUST be logged with timestamp (blocking).

Current state: screening phase, PEP match=true, sanctions=false, score=0.92. Not blocked.

Next step: freeze account and escalate to compliance officer, because score 0.92 exceeds 0.9 threshold triggering freeze.

Risk: blocking legitimate customer with false-positive PEP match, mitigated by manual review by compliance officer within 24h.

Claim: score > 0.9 correlates with confirmed risk in 88% of cases (Q1 2026 internal audit).

Limit: compliance review must complete within 24h.
