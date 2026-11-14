# ISSUE: U9+U12: cortex diff semantico + cortex verify de firma
# Severity: medium | Status: fixed | Handler: Alfred | Date: 2026-11-03

## PROBLEM
Lokky C3-U9+U12: sin forma de ver divergencia semantica cuando un roundtrip difiere, ni verificacion declarativa de firma. cortex diff a.ctx b.ctx (compara canonicos/AST, no texto) y cortex verify <file> sha256:<hash> (si/no + diff si difiere).

## CONTEXT
reported_by: Alfred
reported_at: 2026-11-04T00:10:33Z

## LESSON
cause:      pending triage
fix:        pending triage
prevention: pending triage

## UPDATE 2026-11-14

FIXED 2026-11-14 (SES004). __main__.py: 'cortex diff <a> <b>' compara formas canonicas (no texto crudo) — exit 0 si canonizan igual, exit 1 + unified diff si difieren, exit 2 en uso/parse. 'cortex verify <file> <expect>' acepta sha256:<hex>, hex de 64 chars, u otro archivo .cortex (comparacion semantica con diff en mismatch). Tests CLI en test_api.py — 47/47 OK.
