// CORTEX 0.2 — migration stub.
'use strict';

class MigrationError extends Error {
  constructor(code, message) {
    super(`${code}: ${message}`);
    this.code = code;
    this.message = message;
  }
}

function migrateInspect(_sourcePath) {
  throw new MigrationError('NOT_IMPLEMENTED', 'Node port does not implement migration — use Python reference');
}

module.exports = { MigrationError, migrateInspect };
