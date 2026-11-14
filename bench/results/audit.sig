{
  "artifacts": {
    "archive_seal": {
      "archive/2026-11/SHA256SUMS": "932/932 OK"
    },
    "certificate.json": {
      "sha256": "831b237e010dd099b5b987789f11b67a4ad2cee1fb91a74bc271bc75c7b167a1"
    },
    "certifier_sha256": "ecb028746474bb2ecdd4c83f0628046261eb9331d7fcc58e5d8e42e3148f6c8b",
    "corpus_seal": {
      "tests/SHA256SUMS": "985/985 OK"
    },
    "instrument_sha256": "52a1b03cb84415ba026a54aba05d0bf014a126aa9dc06ad7888ef50d3d34f11d"
  },
  "audit_sig": "1.8",
  "audited_at": "2026-11-14T16:30:51.308980+00:00",
  "auditor": "heimdall",
  "commit": "ffe0b0e5b3186666e40ec07c3523dd7e8614d98b",
  "nonconformance": [],
  "observations": [
    "Two alias layers were retired: docs/spec (symlinks to docs/standard) and examples (symlinks to conformance). Removing them leaves one canonical path per artifact; the corpus seal lost its only alias entry (986 -> 985).",
    "Removed regenerable weight: target/debug (1.5 GB), build/, tools/ (pycache of an already archived validator), egg-info and test/lint caches. target/release is kept so the certificate does not rebuild Rust on every run.",
    "bench/lokky run-001 (476 raw outputs + scores + batch log) was unversioned evidence of BLP-003 and is now committed; the run had completed (476/476, BATCH DONE).",
    "CORTEX-DB v0.1 documents were delegated to Proyecto_X (E-0272/E-0273) but had never been transferred; they are archived under archive/2026-11/cortex-db-line with the delegation note instead of being deleted.",
    "profiles/ was a placeholder for an agent-runtime layer that the codec explicitly excludes; archived. docs/transition (PHASE0 evidence) archived.",
    "Kept deliberately: docs/standard program docs (GATE-F2, F3/F4-CHARTER, REV-*, PHASE-1 index) because 8 governance files still reference them; security/ and governance/ are active policy enforced by boundary.yml.",
    "Open gates unchanged: AC-10 (green CI in the remote) and AC-12 (Architect ratification of 1.0)."
  ],
  "role": "independent auditor (read-only, distinct from executor and governor)",
  "scope": "repository hygiene over commit ffe0b0e: no certified input changed, seals and suites verified, out-of-scope material archived",
  "signature": "heimdall:c2508e9800aa3b0ba58e130bb9f94089aa34a5440e92744ac148106c9e0a2706",
  "signature_scheme": "heimdall:<sha256 of this object without the 'signature' key, serialized as UTF-8 JSON with sorted keys and 2-space indent, no trailing newline>",
  "subject": "CODEC-CORTEX - deep repository hygiene: alias layers retired, out-of-scope material archived, artifacts removed",
  "verdict": "SIGNED-PASS",
  "verifications": [
    "certified inputs untouched by this pass: git diff 1b54337..HEAD over codec_cortex/, bench/certify.py, conformance/ and skill/ is empty",
    "certificate.json is byte-identical to the artifact signed in audit 1.7 (sha256 831b237e010d); no re-execution was required because no instrument or corpus input changed",
    "tests/SHA256SUMS 985/985 OK (the single alias-layer entry was removed with examples/) and archive/2026-11/SHA256SUMS 932/932 OK",
    "probes 29/29; unittest OK; error catalog closed; node --test green; go test green; cargo test green; bash slots + loss-report green",
    "working tree clean after the hygiene commits (74f44b9, 949dbcd, ffe0b0e)",
    "audit 1.7 signature still verifies (bench/verify_audit.py exit 0) before this audit was issued"
  ]
}
