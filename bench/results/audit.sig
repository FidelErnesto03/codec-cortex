{
  "audit_sig": "1.1",
  "auditor": "heimdall",
  "role": "independent auditor (read-only, distinct from executor and governor)",
  "subject": "CODEC-CORTEX - BLP-006 fence fix + BLP-007 Go/Node/Rust + D3b",
  "audited_at": "2026-11-01T19:05:23.546660+00:00",
  "commit": "4a19c311048f623c7f4264135b132434dc93579f",
  "artifacts": {
    "certificate.json": {
      "sha256": "5aa7e91ef1b3a7327c06baa9655520bfb091e679d928ed8e6062c6ff6a8cbced"
    },
    "instrument_sha256": "4143d16c3d843efe21e9efe478f07be6a68409fea65e06129e0b77f38bead3c1",
    "corpus_seal": {
      "tests/SHA256SUMS": "972/972 OK"
    }
  },
  "verifications": [
    "bench/certify.py re-executed by auditor in isolated copy: VERDICT PASS",
    "D1 141/141, D2 PASS, D2b 70/70, D3 5/5, D3b 101/101 across python/go/node/rust, D4 141/141, D5 PASS",
    "conformance 67/67; probes 29/29",
    "go test ./... green; node --test 24/24; cargo test green",
    "independent render parity: 101/101 identical sha256 across 4 surfaces",
    "tests/SHA256SUMS 972/972 OK",
    "spec 1.0 §8 envelope v=1.0; 70/70 HCORTEX 1.0 vectors; hcortex-slots superseded-by-1.0"
  ],
  "nonconformance": [
    "AC-4/AC-5/AC-6: Bash surface does not implement HCORTEX 1.0 slots (L005 on skill)",
    "audit.sig 1.0 no longer matches certificate.json or instrument_sha256"
  ],
  "observations": [
    "BLP-007 §3 Architect decision checkbox unchecked",
    "BLP-007 §7.4/AC-1 wording says 141 docs; parity evidence is 101 1.0/0.2 docs + 70 vectors",
    "BLP-007 AC-5 evidence stale vs T-7.5 (D3b extended, 4/5)",
    "Rust lacks a vector-level test (corpus-level only)",
    "D3b depends on prebuilt binaries in git-ignored paths"
  ],
  "verdict": "SIGNED-PASS-PARTIAL",
  "scope": "verified claims only; BLP-007 remains incomplete (Bash)",
  "signature": "heimdall:dc4ce711b50d19c517677fa27de492f1a627e9e583b2745709f31778ae46fce0"
}
