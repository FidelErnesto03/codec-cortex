#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORTEX 0.1 + C14N-0.1 + HCORTEX-0.1 — Modularized implementation.

Modules:
- scalars: Scalar model, lexer, scalar parser
- parser: CORTEX 0.1 parser + AST model
- c14n: C14N-0.1 canonicalizer
- hcortex: HCORTEX renderer + compiler (paired schema format)
- harness: Test harness for F3 and F4 gates
"""

__version__ = "0.1.0"

from .scalars import Scalar, ParseError, to_nfc, utf8_bytes, emit_string_literal, parse_string_literal
from .parser import (
    Document, Glossary, FormatDecl, EnumDecl, MicroDecl,
    NamespaceDecl, ExtensionDecl, MetaDecl, SymbolDef, ContractField,
    Section, Idea, parse_cortex, parse_contract_fields,
)
from .c14n import canonicalize
from .hcortex import render_hcortex, compile_hcortex, HDiagnostic
from .harness import run_phase3, run_phase4, run_all_tests, sha256_bytes, c14n_hash
