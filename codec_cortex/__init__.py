#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORTEX 0.1 + slots surface + C14N + HCORTEX — dual-surface codec.

Modules:
- scalars: Scalar model, lexer, scalar parser (0.1)
- parser: CORTEX 0.1 parser + AST model
- c14n: C14N-0.1 canonicalizer
- hcortex: HCORTEX renderer + compiler (paired schema format)
- harness: Test harness for F3 and F4 gates
- slots: slot lexer (※N:valor) and slot contract parser
- slotparser: slots parser + AST extensions
- slotc14n: slots canonicalizer + hash with domain separation
- dispatcher: parse_cortex / canonicalize / hash_cortex dispatchers

Public API:
- parse_cortex (dispatcher, dual-surface) is the canonical entry point.
- The 0.1 parser remains accessible as parse_cortex_01.
"""

__version__ = "1.0.0-rc.1"

from .scalars import Scalar, ParseError, to_nfc, utf8_bytes, emit_string_literal, parse_string_literal
from .parser import (
    Document, Glossary, FormatDecl, EnumDecl, MicroDecl,
    NamespaceDecl, ExtensionDecl, MetaDecl, SymbolDef, ContractField,
    Section, Idea, parse_cortex as parse_cortex_01, parse_contract_fields,
)
from .c14n import canonicalize as canonicalize_01
from .hcortex import render_hcortex, compile_hcortex, HDiagnostic
from .harness import run_phase3, run_phase4, run_all_tests, sha256_bytes, c14n_hash

# slots surface
from .slots import (
    SLOT_MARKER, HOMOGLYPHS, SLOT_INDEX_MAX,
    SlotContractField, FieldValue,
    parse_slot_contract, validate_slot_contract,
    parse_slot_payload, check_mixed_surface_legacy,
)
from .slotparser import parse_slots, SigilMapDecl, GlossarySlots
from .slotc14n import (
    canonicalize_slots, hash_slots, hash_legacy,
    HASH_DOMAIN_SLOTS, HASH_DOMAIN_LEGACY,
)
from .dispatcher import parse_cortex, canonicalize, hash_cortex
from .slotharness import run_slots_conformance
from .slothcortex import render_hcortex_slots, compile_hcortex_slots, run_roundtrip
from .slotmigrate import migrate_inspect, migrate_plan, migrate_apply, migrate_verify, migrate_rollback

__all__ = [
    # 0.1 preserved
    "Scalar", "ParseError", "Document", "Glossary", "FormatDecl",
    "EnumDecl", "MicroDecl", "NamespaceDecl", "ExtensionDecl", "MetaDecl",
    "SymbolDef", "ContractField", "Section", "Idea",
    "parse_cortex_01", "canonicalize_01", "parse_contract_fields",
    "render_hcortex", "compile_hcortex", "HDiagnostic",
    "run_phase3", "run_phase4", "run_all_tests", "sha256_bytes", "c14n_hash",
    # slots
    "SLOT_MARKER", "HOMOGLYPHS", "SLOT_INDEX_MAX",
    "SlotContractField", "FieldValue",
    "parse_slot_contract", "validate_slot_contract",
    "parse_slot_payload", "check_mixed_surface_legacy",
    "parse_slots", "SigilMapDecl", "GlossarySlots",
    "canonicalize_slots", "hash_slots", "hash_legacy",
    "HASH_DOMAIN_SLOTS", "HASH_DOMAIN_LEGACY",
    "parse_cortex", "canonicalize", "hash_cortex",
    "run_slots_conformance",
    "render_hcortex_slots", "compile_hcortex_slots", "run_roundtrip",
    "migrate_inspect", "migrate_plan", "migrate_apply", "migrate_verify", "migrate_rollback",
    "__version__",
]
