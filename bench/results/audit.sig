{
  "audit_sig": "1.4",
  "auditor": "heimdall",
  "role": "independent auditor (read-only, distinct from executor and governor)",
  "subject": "CODEC-CORTEX - release 1.0.0 (PyPI implementation)",
  "audited_at": "2026-11-01T20:24:36.109513+00:00",
  "commit": "e0e7aa9ed5a2d674277f1e9536a9a8534ddf5982",
  "artifacts": {
    "certificate.json": {
      "sha256": "33ac3f962624dae8637c449538c86e8a53aa96056c4ac9df5f67efa21103643b"
    },
    "instrument_sha256": "095d26d54d7f5ecb4d0ba56ecf16e7308e6a55d16e34b79430b62c26faabd64f",
    "certifier_sha256": "a38b07cd082c1f641384e8cd700bc27a5ddb5405332d380f200199ce33673131",
    "wheel": {
      "file": "codec_cortex-1.0.0-py3-none-any.whl",
      "sha256": "790804f91cf5e3aa2d0f39204ebfe9319fa24c4a6f0752142c7c6fb758122366"
    },
    "corpus_seal": {
      "tests/SHA256SUMS": "972/972 OK"
    }
  },
  "verifications": [
    "certificate re-executed by auditor in a clean copy WITHOUT Go/Rust binaries: preflight built both, VERDICT PASS, certificate byte-identical",
    "wheel built independently from the audited commit: Version 1.0.0, 14 modules, _fence_mask present, HCORTEX envelope v={version}",
    "D1 141/141, D2 PASS, D2b 70/70, D3 5/5, D3b 101/101 across five surfaces (degraded=[]), D4 141/141, D5 PASS",
    "conformance 67/67; probes 29/29",
    "go test green; node --test 24/24; cargo test 19+3+9+10 green; bash self-test green",
    "independent 5-surface render parity: 101/101 identical sha256",
    "tests/SHA256SUMS 972/972 OK"
  ],
  "nonconformance": [],
  "observations": [
    "pyproject classifier remains 'Development Status :: 4 - Beta' despite the 1.0.0 version",
    "N4 ratification of the CORTEX 1.0 canon remains a separate human gate",
    "empty-checkpoint handler guard remains an ArqUX framework item"
  ],
  "verdict": "SIGNED-PASS",
  "scope": "release 1.0.0 implementation and PyPI wheel",
  "signature": "heimdall:6042e40203505eb95e5d15de39a95e4b9e77e17c1dec77dc6b4f31b4784f6f4a"
}
