// CORTEX 0.2 — C14N-0.2 hash domain wrapper.
'use strict';

const { hashSlots } = require('./slotparser');

function canonicalizeSlots(_doc) {
  // Full C14N-0.2 canonicalization is delegated to the Python reference.
  // This module exposes only the hash domain wrapper for byte-level testing.
  throw new Error('canonicalize_slots not implemented in Node port — use Python reference');
}

module.exports = { canonicalizeSlots, hashSlots };
