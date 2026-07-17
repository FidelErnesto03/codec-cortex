'use strict';

const scalars = require('./scalars');
const parser = require('./parser');
const c14n = require('./c14n');
const hcortex = require('./hcortex');
const harness = require('./harness');

module.exports = {
  ...scalars,
  ...parser,
  ...c14n,
  ...hcortex,
  ...harness,
};
