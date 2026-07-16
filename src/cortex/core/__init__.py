# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Core module exports."""

from .ast import (
    AttrsPosContract,
    CortexDocument,
    Entry,
    Glossary,
    MicroDef,
    Section,
    SigilDef,
    TypeDef,
    compute_document_hash,
    compute_entry_hash,
    normalize_section_id,
)
from .compare import Diff, DiffResult, compare_ast
from .errors import (
    CANONICAL_MICRO,
    CANONICAL_SIGILS,
    CANONICAL_TYPES,
    CortexError,
    Diagnostic,
    DiagnosticBag,
    GLOSSARY_RESERVED_SIGILS,
    MissingGlossaryError,
    GlossaryNotFirstError,
    UnknownSigilError,
    UnknownTypeError,
    BraceError,
    InvalidAttrsError,
    AttrsPosContractMissingError,
    DuplicateEntryError,
    ProtectedEntryError,
    HCortexReadNotCompilableError,
    HCortexEditMetadataMissingError,
    RoundtripFailedError,
    NotFoundError,
    AmbiguousSelectorError,
    AtomicWriteError,
    InvalidSectionHeaderError,
    UnparsedLineError,
    ProtectedSigilError,
    SigilInUseError,
    MicroInUseError,
    InvalidValueError,
    TemplateUnknownError,
)
from .lexer import lex
from .parser import parse_cortex, parse_attrs_body, parse_attrs_pos_body, build_entry_from_value
from .validator import validate, is_valid, is_protected_entry
from .document_kind import (
    DocumentKind, infer_document_kind, validate_level_policy,
    LIVE_STATE_SIGILS,
)
from .writer import write_cortex, serialize_entry, serialize_entry_value, serialize_glossary

__all__ = [
    # AST
    "AttrsPosContract", "CortexDocument", "Entry", "Glossary", "MicroDef",
    "Section", "SigilDef", "TypeDef", "compute_document_hash",
    "compute_entry_hash", "normalize_section_id",
    # Compare
    "Diff", "DiffResult", "compare_ast",
    # Errors
    "CANONICAL_MICRO", "CANONICAL_SIGILS", "CANONICAL_TYPES",
    "CortexError", "Diagnostic", "DiagnosticBag",
    "GLOSSARY_RESERVED_SIGILS",
    "MissingGlossaryError", "GlossaryNotFirstError", "UnknownSigilError",
    "UnknownTypeError", "BraceError", "InvalidAttrsError",
    "AttrsPosContractMissingError", "DuplicateEntryError",
    "ProtectedEntryError", "HCortexReadNotCompilableError",
    "HCortexEditMetadataMissingError", "RoundtripFailedError",
    "NotFoundError", "AmbiguousSelectorError", "AtomicWriteError",
    "InvalidSectionHeaderError", "UnparsedLineError", "ProtectedSigilError",
    "SigilInUseError", "MicroInUseError", "InvalidValueError",
    "TemplateUnknownError",
    # Parser / writer / validator
    "lex", "parse_cortex", "parse_attrs_body", "parse_attrs_pos_body",
    "build_entry_from_value",
    "validate", "is_valid", "is_protected_entry",
    "DocumentKind", "infer_document_kind", "validate_level_policy",
    "LIVE_STATE_SIGILS",
    "write_cortex", "serialize_entry", "serialize_entry_value",
    "serialize_glossary",
]
