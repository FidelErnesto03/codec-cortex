#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p bin
build() {
  local goos="$1" goarch="$2" suffix="$3"
  GOOS="$goos" GOARCH="$goarch" CGO_ENABLED=0 \
    go build -trimpath -ldflags="-s -w" -o "bin/codec-cortex-${goos}-${goarch}${suffix}" ./cmd/codec-cortex
}
build linux amd64 ""
build linux arm64 ""
build windows amd64 ".exe"
build darwin amd64 ""
build darwin arm64 ""
(
  cd bin
  sha256sum codec-cortex-* > SHA256SUMS
)
echo "Built binaries in $ROOT/bin"
