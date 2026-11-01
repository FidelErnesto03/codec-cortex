{
  "audit_sig": "1.2",
  "auditor": "heimdall",
  "role": "independent auditor (read-only, distinct from executor and governor)",
  "subject": "CODEC-CORTEX - BLP-006 fence fix + BLP-007 HCORTEX 1.0 on five surfaces",
  "audited_at": "2026-11-01T19:45:07.508084+00:00",
  "commit": "c0e0ec33cc89d7d9450b5f46cb278d251183f904",
  "artifacts": {
    "certificate.json": {
      "sha256": "490769bde246fe30d08c20ba6c43c52c92363fc8877d5d1e6cdd0abc38c9586d"
    },
    "instrument_sha256": "4143d16c3d843efe21e9efe478f07be6a68409fea65e06129e0b77f38bead3c1",
    "corpus_seal": {
      "tests/SHA256SUMS": "972/972 OK"
    }
  },
  "verifications": [
    "bench/certify.py re-executed by auditor in isolated copy: VERDICT PASS, certificate byte-identical",
    "D1 141/141, D2 PASS, D2b 70/70, D3 5/5, D3b 101/101 across python/go/node/rust/bash (degraded=[]), D4 141/141, D5 PASS",
    "conformance 67/67; probes 29/29",
    "go test ./... green; node --test 24/24; cargo test 19 lib + 3 + 9 + 10 green; bash self-tests green",
    "independent 5-surface render parity: 101/101 identical sha256",
    "tests/SHA256SUMS 972/972 OK",
    "spec 1.0 §8 envelope v=1.0; 70/70 HCORTEX 1.0 vectors; hcortex-slots superseded-by-1.0"
  ],
  "nonconformance": [],
  "observations": [
    "audit.sig 1.1 is stale and is superseded by this signature",
    "BLP-007 AC-4/AC-5/AC-6 keep stale FAIL notes under their verified status",
    "BLP-007 §11/§13 still say 141 documents; §7.4 corrected to 101 + 70 vectors",
    "instrument_sha256 covers codec_cortex only, not bench/certify.py",
    "D3b depends on prebuilt Go/Rust binaries in git-ignored paths",
    "empty-checkpoint handler guard remains a framework hardening item"
  ],
  "verdict": "SIGNED-PASS",
  "scope": "BLP-006 fence fix and BLP-007 HCORTEX 1.0 five-surface parity",
  "signature": "heimdall:996f724af789a4d30013481eded3e2deeb7053fb31b3a1b2c54ce1a091fff427"
}
