{
  "artifacts": {
    "archive_seal": {
      "archive/2026-11/SHA256SUMS": "932/932 OK"
    },
    "certificate.json": {
      "sha256": "43230c794081d1c3530dd32ee2f42853fcca42a2a7b2246a57739ce71b208f18"
    },
    "certifier_sha256": "ecb028746474bb2ecdd4c83f0628046261eb9331d7fcc58e5d8e42e3148f6c8b",
    "corpus_seal": {
      "tests/SHA256SUMS": "985/985 OK"
    },
    "instrument_sha256": "767c7ed423a0fc8d33ca0523b9eebc8a1c212bd2726008bf6ab8580d2a77cde7",
    "package_seal": {
      "bench/agent-package/SHA256SUMS": "3/3 OK"
    },
    "sdist": {
      "file": "codec_cortex-1.0.1.tar.gz",
      "sha256": "c9ee97e88016b1382815b762b5e54ac40445c9e12cd4ab4d640917450998220d"
    },
    "wheel": {
      "file": "codec_cortex-1.0.1-py3-none-any.whl",
      "sha256": "ace26b21cece036d1d07af49cfeac94c3550c2bdeacd51cab9db63487001a586"
    }
  },
  "audit_sig": "1.9",
  "audited_at": "2026-11-14T17:05:36.021164+00:00",
  "auditor": "heimdall",
  "commit": "7c12b9256fff300b79eaae73d3ba86af0289c336",
  "nonconformance": [],
  "observations": [
    "Version 1.0.1 is a patch release: the dialect and the canonical hash do not change. It packages loss-report across the five surfaces, the closed loss catalog, G042 and the bare-$0 render, D6/D7, the documentation refresh and the hygiene pass.",
    "Breaking changes are documented in CHANGELOG: `$0: <title>` now rejected (G042), bare `$0` emitted for cappaless glossaries, Python `hash` prints sha256:<hex>. Scripts parsing bare hex must strip the prefix.",
    "audit.sig 1.8 no longer matches the certificate after the release bump, as expected; this signature supersedes it.",
    "PyPI publication is delegated to the publish workflow (tag v1.0.1 or workflow_dispatch), which uses the PYPI_API_TOKEN secret. The wheel hash above identifies the locally audited artifact; CI builds its own wheel and its byte hash may differ because zip timestamps are not reproducible. Verify the published version and contents, not the byte hash.",
    "Open gates unchanged: AC-10 (green CI in the remote) and AC-12 (Architect ratification of 1.0)."
  ],
  "role": "independent auditor (read-only, distinct from executor and governor)",
  "scope": "release 1.0.1: package version, wheel and sdist built from commit 7c12b92, certificate and seals verified",
  "signature": "heimdall:44aad83495a9db120277eaf3e62dfb0f1846961b2cf02c83e8b1277f56d31e82",
  "signature_scheme": "heimdall:<sha256 of this object without the 'signature' key, serialized as UTF-8 JSON with sorted keys and 2-space indent, no trailing newline>",
  "subject": "CODEC-CORTEX - release 1.0.1 (PyPI implementation)",
  "verdict": "SIGNED-PASS",
  "verifications": [
    "instrument hash recomputed from the tree (codec_cortex/**/*.py + bench/certify.py) matches certificate.instrument_sha256: 767c7ed423a0fc8d",
    "committed certificate at this commit: VERDICT PASS, D1 141/141, D2 141/141, D2b 70/70, D3 5/5 degraded=-, D3b 101/101, D4 141/141, D5 PASS, D6 75/75, D7 10/10",
    "wheel 1.0.1 built from this commit and installed offline in a clean venv: __version__ 1.0.1, validate OK, hash sha256:89db9359..., to-hcortex OK, loss-report OK",
    "agent package self-check with the installed wheel: reversible true, losses 0",
    "tests/SHA256SUMS 985/985 OK; archive seal 932/932 OK; agent package seal 3/3 OK",
    "probes 29/29; unittest OK; error catalog closed; node --test green; go test green; cargo test green; bash slots + loss-report green",
    "no full independent re-execution in this pass: correspondence between the certificate and the tree is established by instrument-hash recomputation; determinism was demonstrated repeatedly earlier in this session"
  ]
}
