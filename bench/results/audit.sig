{
  "audit_sig": "1.0",
  "auditor": "heimdall",
  "role": "independent auditor (distinct from executor and governor, Art. XII)",
  "subject": "BLP-003 Nivel A - certificate.json",
  "audited_at": "2026-11-01T13:59:35.933833+00:00",
  "commit": "0f21ca4f7ff61687d85bd179bd2ccb30c4442f67",
  "remote": "github/FidelErnesto03/codec-cortex main == HEAD",
  "artifacts": {
    "certificate.json": {
      "sha256": "91eaeb3867c6b1aa75926f319c847e36238a66878e761f837c6a82af9a517ce6"
    },
    "determinism.json": {
      "sha256": "f3648465fdc405fb94f8cff092a4edf319d86a116e72d47b1df1143eb644c486"
    },
    "instrument_sha256": "0d9da90df7c0ebe0b7a54673fe0a9d92716660cd576363e2b8994b7bc5036324"
  },
  "verifications": [
    "corpus seal: tests/SHA256SUMS 845/845 OK",
    "heldout seal: bench/corpus-heldout/SHA256SUMS OK",
    "re-executed python -m bench.certify by auditor: VERDICT PASS, D3 5/5 bash/go/node/python/rust",
    "instrument_sha256 recomputed == certificate value",
    "PyPI wheel codec_cortex-1.0.0rc1 hash == instrument_sha256 (published package byte-identical to audited tree)",
    "CI run github#41313736247 (cortex-certificate): green, D3 5/5 remote",
    "D6 determinism: cortex unique=1, llm unique=5, pass=true",
    "parser.py at HEAD (GSIG stash reverted): local == PyPI rc1"
  ],
  "verdict": "SIGNED-PASS",
  "signature": "heimdall:50fb193e27bbcab318efdb505203b2d5da5b9bd48aacdb52ffa3d398c794c84e"
}