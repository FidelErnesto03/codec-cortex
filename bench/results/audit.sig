{
  "artifacts": {
    "archive_seal": {
      "archive/2026-11/SHA256SUMS": "928/928 OK"
    },
    "certificate.json": {
      "sha256": "00c2155c0c70493b644d1408f3f0fb9e0facd89e05b620a2eea59f9d24e57276"
    },
    "certifier_sha256": "ecb028746474bb2ecdd4c83f0628046261eb9331d7fcc58e5d8e42e3148f6c8b",
    "corpus_seal": {
      "tests/SHA256SUMS": "986/986 OK"
    },
    "dialect_vectors": {
      "conformance/0.1-contract": "2 fixtures + README, sealed"
    },
    "instrument_sha256": "bda495abacd88f2153e58de23e62d38a201c5607ee470a7a37591809c42c0b70",
    "loss_vectors": {
      "conformance/1.0/loss": "5 fixtures + expected reports, sealed"
    }
  },
  "audit_sig": "1.6",
  "audited_at": "2026-11-14T15:16:10.578129+00:00",
  "auditor": "heimdall",
  "commit": "5ba2a98f6a1e450215eb2a4149202d08d4ed1198",
  "nonconformance": [],
  "observations": [
    "Ergonomics sweep over 217 real cortex:1.0 documents outside the corpus: 136 (63%) report declared losses, distribution L402 3447 / L405 342 / L403 1. L403 is not noise; L402 is ubiquitous (governance files separate with '#' lines) and must remain informational — it is truthful but useless as a pass/fail metric.",
    "Recommendation: add a counts/summary mode to loss-report before using it as a developer-facing report; today it emits per-line findings that are correct but heavy at corpus scale.",
    "Breaking change with real-world cost: `$0: <title>` is now rejected (G042). Two frozen benchmark documents are affected (bench/formats/cortex.cortex, bench/lokky/corpus-migration/cortex.cortex). They were left untouched by design and the migration is documented in CHANGELOG; a migration rule in `migrate` would reduce the manual cost.",
    "Of the 9/217 non-zero exits, 2 are the G042 benchmark documents, 2 are intentional invalid conformance vectors, 3 are governance files that are not 1.0-parseable (missing $0:format, invalid idea head, undeclared sigil), 1 is a stray workspace file whose name contains a colon, 1 was a not-found path from the sweep query. No loss-report defect.",
    "D6 adds ~7 minutes to the certificate (75 documents x 5 surfaces). Correct but heavy for CI; sampling or parallelism is the hardening path. D7 costs seconds.",
    "ArqUX framework papercuts observed while auditing: cortex.checkpoint returns ok without applying fcs/obj (stale work state persisted); identity.switch right after a client restart needs a bound session first, and session.context_set then reports the transport identity in the header until the switch is repeated.",
    "pyproject classifier remains 'Development Status :: 4 - Beta' despite 1.0.0 (carried from audit 1.4).",
    "AC-10 (green CI in the remote) and AC-12 (Architect ratification of 1.0) remain open human/external gates; this signature covers the implementation, the dialect contract and the archive, not those gates."
  ],
  "role": "independent auditor (read-only, distinct from executor and governor)",
  "scope": "CORTEX 1.0 canon implementation: loss-report parity across five surfaces, closed error catalog, 0.x archive, 0.1 dialect contract",
  "signature": "heimdall:61d0c95fa79cca7dc1327cd488bd89e7523347d4f11438b4b1bf14c2d9bf5d72",
  "signature_scheme": "heimdall:<sha256 of this object without the 'signature' key, serialized as UTF-8 JSON with sorted keys and 2-space indent, no trailing newline>",
  "subject": "CODEC-CORTEX - CORTEX 1.0 canon: declared loss report, closed error catalog, 0.x archive, 0.1 dialect contract",
  "verdict": "SIGNED-PASS",
  "verifications": [
    "certificate re-executed twice by the auditor from clean processes: VERDICT PASS and certificate.json byte-identical to the committed artifact (sha256 00c2155c0c70)",
    "D1 141/141, D2 141/141, D2b 70/70, D3 ok=bash,go,node,python,rust degraded=-, D3b 101/101, D4 141/141, D5 PASS, D6 75/75, D7 10/10",
    "D6: loss-report byte-identical across the five surfaces on 75 documents; L499_UNCLASSIFIED_LOSS never emitted",
    "D7: all five surfaces reject `$0: <title>` with G042_GLOSSARY_HEADER_INVALID and render a bare `$0` that their own compiler accepts",
    "declared loss catalog closed (scripts/ccx_error_catalog.py exit 0): 103 codes = emitted across surfaces union declared reserves",
    "tests/SHA256SUMS 986/986 OK; archive/2026-11/SHA256SUMS 928/928 OK",
    "probes 29/29; unittest 9/9; node --test 32/32; go test green; cargo test 19+3+4+9+10 green; bash self-tests (slots + loss-report) green",
    "HCORTEX render parity 5/5 on 101 vectors; CORTEX 0.1/0.2/1.0 alias read preserved"
  ]
}
