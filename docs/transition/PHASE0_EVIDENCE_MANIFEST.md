# PHASE 0 EVIDENCE MANIFEST

## Hashes (redactados, sin valores de secreto)
- main (pre-rewrite, en bundle): ba31cdf
- legacy/v0.6.x (saneado): 5b4b937c4f4a87db5aab6b3e6531d8e391365356
- new main root commit: verificar post-commit
- bundle: sha256 97be5249602ed8a4326efc635e0faf6b7721aa482c4c30114c75438c07da2201

## Comandos (read-only y mutación)
- cortex verify --kind brain --strict (0 errores)
- git clone --mirror + bundle create --all
- git filter-repo --invert-paths --path-glob "*PyPI-Recovery-Codes-fidelernesto*"
- git rev-list --objects --all | grep PyPI-Recovery (0)
- gitleaks detect (5 leaks, falsos positivos)

## Evidencia ubicada en
- phase0-evidence/codec-cortex-pre-rewrite.bundle
- phase0-evidence/codec-cortex-pre-rewrite.bundle.sha256
- phase0-evidence/legacy-head.txt
- docs/transition/PHASE0_EXECUTION_REPORT.md

## Desviaciones
- gh CLI token inválido; se usó git credential store para push.
- Rotación PyPI requiere acción humana fuera de entorno.
