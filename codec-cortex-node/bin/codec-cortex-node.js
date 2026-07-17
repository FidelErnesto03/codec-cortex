#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const {
  ParseError,
  parseCortex,
  canonicalize,
  renderHcortex,
  compileHcortex,
  c14nHash,
  runAllTests,
} = require('../src');

function usage(stream = process.stdout) {
  stream.write(`codec-cortex-node — CORTEX 0.1 / C14N-0.1 / HCORTEX-0.1\n\n`);
  stream.write(`Uso:\n`);
  stream.write(`  codec-cortex-node parse <archivo.cortex>\n`);
  stream.write(`  codec-cortex-node canonicalize <archivo.cortex> [-o salida]\n`);
  stream.write(`  codec-cortex-node to-hcortex <archivo.cortex> [-o salida.md]\n`);
  stream.write(`  codec-cortex-node from-hcortex <archivo.md> [-o salida.cortex]\n`);
  stream.write(`  codec-cortex-node hash <archivo.cortex>\n`);
  stream.write(`  codec-cortex-node test <directorio-c14n> <directorio-hcortex> [--report archivo.json]\n`);
  stream.write(`  codec-cortex-node <directorio-c14n> <directorio-hcortex>\n\n`);
  stream.write(`Use '-' como archivo para leer desde stdin.\n`);
}

function readInput(file) {
  return file === '-' ? fs.readFileSync(0, 'utf8') : fs.readFileSync(file, 'utf8');
}

function outputTarget(args) {
  const index = args.indexOf('-o');
  if (index >= 0) return args[index + 1];
  const longIndex = args.indexOf('--output');
  return longIndex >= 0 ? args[longIndex + 1] : null;
}

function writeOutput(value, target) {
  if (target) fs.writeFileSync(target, value, 'utf8');
  else process.stdout.write(value);
}

function astReplacer(key, value) {
  if (value instanceof Map) return Object.fromEntries(value);
  return value;
}

function defaultCorpusPaths(args) {
  const base = process.env.REV_PACKAGE || path.resolve(__dirname, '..', '..', 'experiments');
  let c14nDir = args[0] || path.join(base, 'gate-f3', 'c14n-corpus');
  let hcortexDir = args[1] || path.join(base, 'gate-f4');
  if (!fs.existsSync(c14nDir)) {
    const alternate = path.join(base, 'c14n', 'corpus');
    if (fs.existsSync(alternate)) c14nDir = alternate;
  }
  if (!fs.existsSync(hcortexDir)) {
    const alternate = path.join(base, 'hcortex');
    if (fs.existsSync(alternate)) hcortexDir = alternate;
  }
  return [c14nDir, hcortexDir];
}

function runHarness(args) {
  const reportFlag = args.indexOf('--report');
  const reportPath = reportFlag >= 0 ? args[reportFlag + 1] : path.resolve(process.cwd(), 'rev-report-node.json');
  const positional = args.filter((arg, index) => index !== reportFlag && index !== reportFlag + 1);
  const [c14nDir, hcortexDir] = defaultCorpusPaths(positional);
  process.stdout.write(`C14N directory: ${c14nDir}\nHCORTEX directory: ${hcortexDir}\n\n`);
  if (!fs.existsSync(c14nDir) && !fs.existsSync(hcortexDir)) {
    process.stderr.write('ERROR: Neither corpus directory found.\n');
    process.stderr.write('Provide paths: codec-cortex-node test C14N_DIR HCORTEX_DIR\n');
    return 1;
  }
  const report = runAllTests(c14nDir, hcortexDir);
  fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  process.stdout.write(`\nReport written to: ${reportPath}\n`);
  return report.verdict === 'FAIL' ? 1 : 0;
}

function main(argv = process.argv.slice(2)) {
  if (!argv.length || argv[0] === '--help' || argv[0] === '-h') {
    usage();
    return 0;
  }
  const command = argv[0];
  const args = argv.slice(1);
  try {
    if (command === 'parse') {
      if (!args[0]) throw new Error('Falta el archivo CORTEX.');
      const doc = parseCortex(readInput(args[0]));
      writeOutput(`${JSON.stringify(doc, astReplacer, 2)}\n`, outputTarget(args));
      return 0;
    }
    if (command === 'canonicalize' || command === 'format') {
      if (!args[0]) throw new Error('Falta el archivo CORTEX.');
      writeOutput(canonicalize(parseCortex(readInput(args[0]))), outputTarget(args));
      return 0;
    }
    if (command === 'to-hcortex') {
      if (!args[0]) throw new Error('Falta el archivo CORTEX.');
      writeOutput(renderHcortex(parseCortex(readInput(args[0]))), outputTarget(args));
      return 0;
    }
    if (command === 'from-hcortex') {
      if (!args[0]) throw new Error('Falta el archivo HCORTEX.');
      const [doc, diagnostics] = compileHcortex(readInput(args[0]));
      for (const diag of diagnostics) process.stderr.write(`${diag.severity.toUpperCase()} ${diag.code} line ${diag.line}: ${diag.message}\n`);
      if (!doc || diagnostics.some((diag) => diag.severity === 'error')) return 1;
      writeOutput(canonicalize(doc), outputTarget(args));
      return 0;
    }
    if (command === 'hash') {
      if (!args[0]) throw new Error('Falta el archivo CORTEX.');
      const bytes = Buffer.from(canonicalize(parseCortex(readInput(args[0]))), 'utf8');
      process.stdout.write(`${c14nHash(bytes)}\n`);
      return 0;
    }
    if (command === 'test' || command === 'conformance') return runHarness(args);
    if (!command.startsWith('-')) return runHarness(argv);
    usage(process.stderr);
    return 2;
  } catch (error) {
    if (error instanceof ParseError) {
      process.stderr.write(`${error.code} @ ${error.line}:${error.col} — ${error.message}\n`);
    } else {
      process.stderr.write(`${error.name || 'Error'}: ${error.message}\n`);
    }
    return 1;
  }
}

process.exitCode = main();
