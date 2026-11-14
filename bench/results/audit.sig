{
  "artifacts": {
    "archive_seal": {
      "archive/2026-11/SHA256SUMS": "928/928 OK"
    },
    "certificate.json": {
      "sha256": "1e7e3cc71071fb63f7f18cbc5c3ec00f2efa6d719eb92a89357b1da432ae7cbb"
    },
    "certifier_sha256": "119c18ce8e2598f7e42fae5c5cf4f0c06230e82cedf819d809a4abff9a442d95",
    "corpus_seal": {
      "tests/SHA256SUMS": "983/983 OK"
    },
    "instrument_sha256": "dd7831f084b91390170d7e23902d850b1b82ea61cb6708e799eab07818acb8ab",
    "loss_vectors": {
      "conformance/1.0/loss": "5 fixtures + expected reports, sealed"
    }
  },
  "audit_sig": "1.5",
  "audited_at": "2026-11-14T13:47:41.463642+00:00",
  "auditor": "heimdall",
  "commit": "ca5dbd2e3b450a4d6bb4b9dcc6eb132ae1e14da7",
  "nonconformance": [],
  "observations": [
    "cargo test is not fully green: v10_oracle_parity unwraps /tmp/oracle/* artifacts that no longer exist. Pre-existing and non-hermetic test infrastructure, not a regression of this audit; the oracle fixture is ephemeral by design.",
    "D6 adds ~7 minutes to the certificate (75 documents x 5 surfaces). Correct but heavy for CI; consider sampling or parallel execution if pipeline time becomes a constraint.",
    "cortex.checkpoint accepted content and returned ok without applying fcs/obj (it only updated last_turn), leaving stale work state; corrected via cortex.entry.update. ArqUX framework defect, reproducible in this session.",
    "BLP-004 premise 'docs/spec/ is a byte-exact duplicate' was wrong: it was a symlink alias layer. Corrected during T-4.1 and documented in the archive README.",
    "pyproject classifier remains 'Development Status :: 4 - Beta' despite 1.0.0 (carried from audit 1.4).",
    "AC-10 (green CI in the remote) and AC-12 (Architect ratification of 1.0) remain open human/external gates; this signature covers the implementation and archive, not those gates."
  ],
  "role": "independent auditor (read-only, distinct from executor and governor)",
  "scope": "CORTEX 1.0 canon implementation: loss-report parity across five surfaces, closed error catalog, 0.x archive",
  "signature": "heimdall:a2f0c052885a13266c39e3bf4acde9e12db219f64debc0efd27b7fc2f2384bb3",
  "signature_scheme": "heimdall:<sha256 of this object without the 'signature' key, serialized as UTF-8 JSON with sorted keys and 2-space indent, no trailing newline>",
  "subject": "CODEC-CORTEX - CORTEX 1.0 canon: declared loss report, closed error catalog, 0.x archive",
  "verdict": "SIGNED-PASS",
  "verifications": [
    "certificate re-executed by the auditor from a clean process: VERDICT PASS, certificate.json byte-identical to the committed artifact (sha256 1e7e3cc71071)",
    "D1 141/141, D2 141/141, D2b 70/70, D3 ok=bash,go,node,python,rust degraded=-, D3b 101/101, D4 141/141, D5 PASS, D6 75/75",
    "loss-report byte-identical across the five surfaces on 75 documents (vectors + full 1.0 corpus); L499_UNCLASSIFIED_LOSS never emitted",
    "declared loss catalog closed: scripts/ccx_error_catalog.py exit 0 (103 codes = emitted across surfaces union declared reserves)",
    "tests/SHA256SUMS 983/983 OK; archive/2026-11/SHA256SUMS 928/928 OK",
    "probes 29/29; unittest 9/9; node --test 32/32; go test green; bash self-tests (slots + loss-report) green",
    "HCORTEX render parity 5/5 on 101 vectors; CORTEX 0.1/0.2/1.0 alias read preserved"
  ]
}
