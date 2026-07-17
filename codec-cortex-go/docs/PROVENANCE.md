# Provenance

- Source archive: `codec_cortex.tar(1).gz`
- Source SHA-256: `47640ad335bc8f422d346c3f962b12e5e7b317b06080560d1b25070eb54259b2`
- Port date: `2026-07-17`
- Go toolchain used for verification: `go1.23.2 linux/amd64`
- Python reference: supplied seven-module implementation, copied unchanged under `reference/python/codec_cortex/` excluding bytecode caches.

## Differential vectors

- Canonical CORTEX SHA-256: `52215b472dfffd7b8e9f1350523ff82d8ade651de29c54b25a20d2bd0d011f23`
- HCORTEX SHA-256: `7970e0192034ef065725c50be3780a023d63f720ced4306b34baa2450169d511`
- HCORTEX roundtrip CORTEX SHA-256: `6ed1457e485b64edad4d87dd6bd0dfddf3e5ac0c3f18199ecbe7ae07f995bccc`

These vectors are regenerated and compared by `scripts/differential_check.sh`.
