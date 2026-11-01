{
  "audit_sig": "1.3",
  "auditor": "heimdall",
  "role": "independent auditor (read-only, distinct from executor and governor)",
  "subject": "CODEC-CORTEX - BLP-008 instrument hardening and record cleanup",
  "audited_at": "2026-11-01T20:05:59.705456+00:00",
  "commit": "b1ec81a3a606b49091f5b5281cadcfede86fb7b0",
  "artifacts": {
    "certificate.json": {
      "sha256": "be68c3f47e20af2beb1d1b77c533790e9b696d996819e6adc1efcd7dedfc86cc"
    },
    "instrument_sha256": "319bf6e40878a4c8af6dea7b1d5d0b19620288568ce5d86c30068e04cb8118cd",
    "certifier_sha256": "a38b07cd082c1f641384e8cd700bc27a5ddb5405332d380f200199ce33673131",
    "corpus_seal": {
      "tests/SHA256SUMS": "972/972 OK"
    }
  },
  "verifications": [
    "certificate re-executed by auditor in a clean copy WITHOUT Go/Rust binaries: preflight built both, VERDICT PASS, certificate byte-identical",
    "instrument_sha256 includes bench/certify.py (319bf6e4) and certifier_sha256=a38b07cd is exposed",
    "D1 141/141, D2 PASS, D2b 70/70, D3 5/5, D3b 101/101 across python/go/node/rust/bash (degraded=[]), D4 141/141, D5 PASS",
    "conformance 67/67; probes 29/29",
    "go test green; node --test 24/24; cargo test 19+3+9+10 green; bash self-test green",
    "independent 5-surface render parity: 101/101 identical sha256",
    "tests/SHA256SUMS 972/972 OK",
    "BLP-007 record: 0 stale FAIL notes; parity sections say 101 docs + 70 vectors"
  ],
  "nonconformance": [],
  "observations": [
    "BLP-008 AC-5 is the signature itself; Alfred must record it",
    "empty-checkpoint handler guard remains an ArqUX framework item",
    "D3b adds runtime because it renders 101 documents on five surfaces"
  ],
  "verdict": "SIGNED-PASS",
  "scope": "BLP-008 instrument hardening, reproducibility and BLP-007 record cleanup",
  "signature": "heimdall:2e61fe32abc74f3b783b9c3713b49334efb8248ad9b9591f370ff094eeb85fa4"
}
