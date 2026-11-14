{
  "artifacts": {
    "archive_seal": {
      "archive/2026-11/SHA256SUMS": "928/928 OK"
    },
    "certificate.json": {
      "sha256": "831b237e010dd099b5b987789f11b67a4ad2cee1fb91a74bc271bc75c7b167a1"
    },
    "certifier_sha256": "ecb028746474bb2ecdd4c83f0628046261eb9331d7fcc58e5d8e42e3148f6c8b",
    "corpus_seal": {
      "tests/SHA256SUMS": "986/986 OK"
    },
    "instrument_sha256": "52a1b03cb84415ba026a54aba05d0bf014a126aa9dc06ad7888ef50d3d34f11d",
    "skill": {
      "path": "skill/codec-cortex.skill.md",
      "state": "valid, roundtrip lossless, 0 declared losses"
    }
  },
  "audit_sig": "1.7",
  "audited_at": "2026-11-14T16:07:45.890914+00:00",
  "auditor": "heimdall",
  "commit": "1b54337b896eb264c0b34c5415efe6b1058aa2c1",
  "nonconformance": [],
  "observations": [
    "CLI-visible change: Python `hash` now prints sha256:<hex> like the other four surfaces (previously bare hex). Scripts parsing the bare hex must strip the prefix; documented in CHANGELOG.",
    "The skill is a certified corpus vector: editing it changes D1/D2/D4/D3b inputs. Any future skill edit requires re-seal, re-certification and re-audit, as done here.",
    "Docs now separate canonical 1.0 from historical 0.x; dated reports (relevamiento, external reviews, REV, charters) intentionally keep pre-archive paths per archive rule 4.",
    "Certificate runtime is ~8 minutes with D6 (75 documents x 5 surfaces); D7 costs seconds.",
    "AC-10 (green CI in the remote) and AC-12 (Architect ratification of 1.0) remain open human/external gates."
  ],
  "role": "independent auditor (read-only, distinct from executor and governor)",
  "scope": "documentation refresh (README, index, QUICKSTART, LOSS-REPORT, MIGRATION, parser-api, authoring, surface READMEs, skill) and Python CLI hash alignment over commit 1b54337",
  "signature": "heimdall:87afdb253dbf58aaa86cb75457cd81757a0c246e22d3737297ab04b318f833fc",
  "signature_scheme": "heimdall:<sha256 of this object without the 'signature' key, serialized as UTF-8 JSON with sorted keys and 2-space indent, no trailing newline>",
  "subject": "CODEC-CORTEX - CORTEX 1.0 canon documentation refresh and CLI hash alignment",
  "verdict": "SIGNED-PASS-PARTIAL",
  "verifications": [
    "committed certificate at this commit: VERDICT PASS, D1 141/141, D2 141/141, D2b 70/70, D3 5/5 degraded=-, D3b 101/101, D4 141/141, D5 PASS, D6 75/75, D7 10/10",
    "no fresh independent re-execution in this pass: the auditor's re-run was interrupted by session close. Determinism was demonstrated twice earlier in this session (audits 1.5 and 1.6) with byte-identical certificates on the then-current tree.",
    "tests/SHA256SUMS 986/986 OK; archive/2026-11/SHA256SUMS 928/928 OK",
    "probes 29/29; unittest OK; node --test 32/32; go test green; cargo test 19+3+4+9+10 green; bash slots + loss-report green",
    "error catalog closed (scripts/ccx_error_catalog.py exit 0)",
    "updated skill parses, renders and roundtrips losslessly; its HCORTEX view was regenerated from it",
    "documentation examples executed: authoring examples (attrs/attrs-pos/cuerpo/bloque and slots) validate and report zero declared losses"
  ]
}
