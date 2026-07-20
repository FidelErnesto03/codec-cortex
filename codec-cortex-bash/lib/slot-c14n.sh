#!/usr/bin/env bash
# C14N-0.2 hash domain wrapper for Bash.
# Conformance level: byte-level-marker-detection-only.

# shellcheck source=slot-parser.sh
source "$(dirname "${BASH_SOURCE[0]}")/slot-parser.sh"

cortex_slots_canonicalize() {
    # Full C14N-0.2 canonicalization is delegated to the Python reference.
    echo "NOT_IMPLEMENTED: Bash port does not implement full C14N-0.2 canonicalization" >&2
    return 1
}
