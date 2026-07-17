#!/usr/bin/env bash
set -euo pipefail
PREFIX=${PREFIX:-/usr/local}
DESTDIR=${DESTDIR:-}
install -d "$DESTDIR$PREFIX/bin" "$DESTDIR$PREFIX/lib/codec-cortex"
install -m 0755 "$(dirname "$0")/bin/codec-cortex" "$DESTDIR$PREFIX/bin/codec-cortex"
ln -sf codec-cortex "$DESTDIR$PREFIX/bin/cortex"
install -m 0644 "$(dirname "$0")/lib/codec-cortex.sh" "$DESTDIR$PREFIX/lib/codec-cortex/codec-cortex.sh"
printf 'Installed codec-cortex under %s\n' "$DESTDIR$PREFIX"
