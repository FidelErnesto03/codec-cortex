"""CODEC-CORTEX error model.

Every error has a stable machine-readable code (``E0xx_*``) and a human
message.  Errors are raised as :class:`CortexError` (or subclasses) and
collected as diagnostics in the AST during parsing/validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Error code registry — matches Section 17 of the specification
# ---------------------------------------------------------------------------

E001_MISSING_GLOSSARY = "E001_MISSING_GLOSSARY"
E002_GLOSSARY_NOT_FIRST = "E002_GLOSSARY_NOT_FIRST"
E003_UNKNOWN_SIGIL = "E003_UNKNOWN_SIGIL"
E004_UNKNOWN_TYPE = "E004_UNKNOWN_TYPE"
E005_UNBALANCED_BRACES = "E005_UNBALANCED_BRACES"
E006_INVALID_ATTRS = "E006_INVALID_ATTRS"
E007_ATTRS_POS_CONTRACT_MISSING = "E007_ATTRS_POS_CONTRACT_MISSING"
E008_DUPLICATE_ENTRY = "E008_DUPLICATE_ENTRY"
E009_PROTECTED_ENTRY = "E009_PROTECTED_ENTRY"
E010_HCORTEX_READ_NOT_COMPILABLE = "E010_HCORTEX_READ_NOT_COMPILABLE"
E011_HCORTEX_EDIT_METADATA_MISSING = "E011_HCORTEX_EDIT_METADATA_MISSING"
E012_ROUNDTRIP_FAILED = "E012_ROUNDTRIP_FAILED"

# Extended codes (operational, not in the spec's compact list)
E013_NOT_FOUND = "E013_NOT_FOUND"
E014_AMBIGUOUS_SELECTOR = "E014_AMBIGUOUS_SELECTOR"
E015_ATOMIC_WRITE_FAILED = "E015_ATOMIC_WRITE_FAILED"
E016_INVALID_SECTION_HEADER = "E016_INVALID_SECTION_HEADER"
E017_UNPARSED_LINE = "E017_UNPARSED_LINE"
E018_PROTECTED_SIGIL = "E018_PROTECTED_SIGIL"
E019_SIGIL_IN_USE = "E019_SIGIL_IN_USE"
E020_MICRO_IN_USE = "E020_MICRO_IN_USE"
E021_INVALID_VALUE = "E021_INVALID_VALUE"
E022_TEMPLATE_UNKNOWN = "E022_TEMPLATE_UNKNOWN"

# Codes introduced in 1.1.0 for cognitive governance (audit gaps)
E023_LEVEL1_LIVE_STATE = "E023_LEVEL1_LIVE_STATE"
E024_LEVEL2_MISSING_FOCUS = "E024_LEVEL2_MISSING_FOCUS"
E025_INVALID_SURVIVE = "E025_INVALID_SURVIVE"
E026_BLOCKING_NOT_P0 = "E026_BLOCKING_NOT_P0"
E027_ATTRS_POS_ARITY = "E027_ATTRS_POS_ARITY"
E028_SECRET_IN_CLEAR = "E028_SECRET_IN_CLEAR"
E029_LEVEL3_LIVE_STATE = "E029_LEVEL3_LIVE_STATE"
E030_RECOVERY_INCOMPLETE = "E030_RECOVERY_INCOMPLETE"

# Codes introduced in 1.1.3 (verification gaps)
E031_SECRET_NOT_BYPASSABLE = "E031_SECRET_NOT_BYPASSABLE"
E032_CRITICAL_SIGIL_INCOMPLETE = "E032_CRITICAL_SIGIL_INCOMPLETE"

# Codes introduced in 1.1.5 ($0 section integrity)
E033_ZERO_SECTION_MEMORY_ENTRY = "E033_ZERO_SECTION_MEMORY_ENTRY"

# Codes introduced in 1.1.6 (semantic emptiness)
E034_CRITICAL_REQUIRED_FIELD_EMPTY = "E034_CRITICAL_REQUIRED_FIELD_EMPTY"

# Codes introduced in v0.3.4 (E2 — Security & Governance)
E035_MODE_READ_ONLY = "E035_MODE_READ_ONLY"
E036_MODE_EDITOR_CONFIRM = "E036_MODE_EDITOR_CONFIRM"
E037_MODE_UNKNOWN = "E037_MODE_UNKNOWN"
E038_AUDIT_LOGGING_OFF = "E038_AUDIT_LOGGING_OFF"
E039_SIGNATURE_MISMATCH = "E039_SIGNATURE_MISMATCH"
E040_SECRET_DETECTED = "E040_SECRET_DETECTED"


@dataclass
class CortexError(Exception):
    """Base error for the CODEC-CORTEX CLI.

    Carries a stable ``code`` (E0xx_*) and optional structural context
    (line number, section id, sigil, entry name) so the CLI can render
    actionable diagnostics.
    """

    code: str
    message: str
    line: Optional[int] = None
    section: Optional[str] = None
    sigil: Optional[str] = None
    entry: Optional[str] = None

    def __post_init__(self) -> None:
        # ``dataclass`` + ``Exception`` requires us to forward the message
        # to ``Exception`` so ``str(err)`` keeps working.
        super().__init__(self.message)

    def __str__(self) -> str:  # pragma: no cover - trivial
        loc = []
        if self.line is not None:
            loc.append(f"line {self.line}")
        if self.section is not None:
            loc.append(f"section {self.section}")
        if self.sigil is not None:
            loc.append(f"sigil {self.sigil}")
        if self.entry is not None:
            loc.append(f"entry {self.entry}")
        prefix = f"[{self.code}]"
        if loc:
            prefix += " (" + ", ".join(loc) + ")"
        return f"{prefix} {self.message}"


# ---------------------------------------------------------------------------
# Concrete subclasses — convenient ``except`` targets
# ---------------------------------------------------------------------------

class MissingGlossaryError(CortexError):
    def __init__(self, message: str = "$0 local glossary is missing", **kw):
        super().__init__(E001_MISSING_GLOSSARY, message, **kw)


class GlossaryNotFirstError(CortexError):
    def __init__(self, message: str = "$0 must be the first section", **kw):
        super().__init__(E002_GLOSSARY_NOT_FIRST, message, **kw)


class UnknownSigilError(CortexError):
    def __init__(self, sigil: str, **kw):
        kw.setdefault("sigil", sigil)
        super().__init__(E003_UNKNOWN_SIGIL, f"sigil '{sigil}' not declared in $0", **kw)


class UnknownTypeError(CortexError):
    def __init__(self, type_name: str, **kw):
        super().__init__(E004_UNKNOWN_TYPE, f"expansion type '{type_name}' not declared in $0", **kw)


class BraceError(CortexError):
    def __init__(self, message: str = "unbalanced braces", **kw):
        super().__init__(E005_UNBALANCED_BRACES, message, **kw)


class InvalidAttrsError(CortexError):
    def __init__(self, message: str = "invalid attrs body", **kw):
        super().__init__(E006_INVALID_ATTRS, message, **kw)


class AttrsPosContractMissingError(CortexError):
    def __init__(self, sigil: str, **kw):
        kw.setdefault("sigil", sigil)
        super().__init__(
            E007_ATTRS_POS_CONTRACT_MISSING,
            f"attrs-pos sigil '{sigil}' has no positional contract in $0",
            **kw,
        )


class DuplicateEntryError(CortexError):
    def __init__(self, sigil: str, name: str, **kw):
        kw.setdefault("sigil", sigil)
        kw.setdefault("entry", name)
        super().__init__(
            E008_DUPLICATE_ENTRY,
            f"duplicate entry {sigil}:{name} not allowed without --allow-duplicate",
            **kw,
        )


class ProtectedEntryError(CortexError):
    def __init__(self, sigil: str, name: str, **kw):
        kw.setdefault("sigil", sigil)
        kw.setdefault("entry", name)
        super().__init__(
            E009_PROTECTED_ENTRY,
            f"entry {sigil}:{name} is protected; use --force to override",
            **kw,
        )


class HCortexReadNotCompilableError(CortexError):
    def __init__(self, **kw):
        super().__init__(
            E010_HCORTEX_READ_NOT_COMPILABLE,
            "HCORTEX-READ is not roundtrip-compilable; use HCORTEX-EDIT instead",
            **kw,
        )


class HCortexEditMetadataMissingError(CortexError):
    def __init__(self, message: str = "HCORTEX-EDIT metadata missing", **kw):
        super().__init__(E011_HCORTEX_EDIT_METADATA_MISSING, message, **kw)


class RoundtripFailedError(CortexError):
    def __init__(self, message: str = "structural roundtrip comparison failed", **kw):
        super().__init__(E012_ROUNDTRIP_FAILED, message, **kw)


class NotFoundError(CortexError):
    def __init__(self, selector: str, **kw):
        super().__init__(E013_NOT_FOUND, f"no entry matches selector '{selector}'", **kw)


class AmbiguousSelectorError(CortexError):
    def __init__(self, selector: str, count: int, **kw):
        super().__init__(
            E014_AMBIGUOUS_SELECTOR,
            f"selector '{selector}' matched {count} entries; refine to a single match",
            **kw,
        )


class AtomicWriteError(CortexError):
    def __init__(self, message: str = "atomic write failed", **kw):
        super().__init__(E015_ATOMIC_WRITE_FAILED, message, **kw)


class InvalidSectionHeaderError(CortexError):
    def __init__(self, message: str = "invalid section header", **kw):
        super().__init__(E016_INVALID_SECTION_HEADER, message, **kw)


class UnparsedLineError(CortexError):
    def __init__(self, line: int, **kw):
        kw.setdefault("line", line)
        super().__init__(E017_UNPARSED_LINE, f"line {line} could not be parsed", **kw)


class ProtectedSigilError(CortexError):
    def __init__(self, sigil: str, **kw):
        kw.setdefault("sigil", sigil)
        super().__init__(
            E018_PROTECTED_SIGIL,
            f"sigil '{sigil}' is canonical and cannot be redefined without --force-governance",
            **kw,
        )


class SigilInUseError(CortexError):
    def __init__(self, sigil: str, count: int, **kw):
        kw.setdefault("sigil", sigil)
        super().__init__(
            E019_SIGIL_IN_USE,
            f"sigil '{sigil}' is used by {count} entries; cannot change type or remove",
            **kw,
        )


class MicroInUseError(CortexError):
    def __init__(self, token: str, **kw):
        super().__init__(
            E020_MICRO_IN_USE,
            f"micro-token '{token}' is used by at least one entry; cannot remove without --force",
            **kw,
        )


class InvalidValueError(CortexError):
    def __init__(self, message: str = "invalid value for entry", **kw):
        super().__init__(E021_INVALID_VALUE, message, **kw)


class TemplateUnknownError(CortexError):
    def __init__(self, kind: str, **kw):
        super().__init__(E022_TEMPLATE_UNKNOWN, f"unknown template kind '{kind}'", **kw)


# ---------------------------------------------------------------------------
# Diagnostic record (non-fatal parser findings)
# ---------------------------------------------------------------------------

@dataclass
class Diagnostic:
    """Non-fatal diagnostic collected during parsing/validation.

    Diagnostics are preserved in ``CortexDocument.diagnostics`` so callers
    can decide whether to surface them as warnings or hard errors.
    """

    code: str
    message: str
    line: Optional[int] = None
    section: Optional[str] = None
    sigil: Optional[str] = None
    entry: Optional[str] = None
    severity: str = "warning"  # warning | info

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"[{self.code}] {self.message}"


@dataclass
class DiagnosticBag:
    """Mutable collection of :class:`Diagnostic` with helper queries."""

    items: List[Diagnostic] = field(default_factory=list)

    def add(self, diag: Diagnostic) -> None:
        self.items.append(diag)

    def extend(self, others: List[Diagnostic]) -> None:
        self.items.extend(others)

    def errors(self) -> List[Diagnostic]:
        return [d for d in self.items if d.severity == "error"]

    def warnings(self) -> List[Diagnostic]:
        return [d for d in self.items if d.severity == "warning"]

    def infos(self) -> List[Diagnostic]:
        return [d for d in self.items if d.severity == "info"]

    def has_errors(self) -> bool:
        return any(d.severity == "error" for d in self.items)

    def to_list(self) -> List[dict]:
        return [
            {
                "code": d.code,
                "message": d.message,
                "line": d.line,
                "section": d.section,
                "sigil": d.sigil,
                "entry": d.entry,
                "severity": d.severity,
            }
            for d in self.items
        ]


# Canonical sigils — protected from silent redefinition (Section 4.2)
CANONICAL_SIGILS = frozenset({
    "IDN", "DOM", "KNW", "REF", "TAG", "AXM", "CNST", "!",
    "CLAIM", "LIM", "AUD", "RSK", "FCS", "OBJ", "WRK", "STP",
    "NXT", "SES", "LNG", "DIAG", "HDL", "PFL", "DEP", "DESC", "ERR",
})

# Reserved sigils used inside $0 to declare the glossary itself
GLOSSARY_RESERVED_SIGILS = frozenset({"GSIG", "GTYP", "GMIC"})

# Canonical expansion types (Section 4.3)
CANONICAL_TYPES = frozenset({"attrs", "attrs-pos", "cuerpo", "bloque", "relación"})

# Allowed status / severity / priority values (Section 6)
ALLOWED_STATUS = frozenset({
    "current", "specification", "planned", "future",
    "experimental", "deprecated", "blocked", "done",
})
ALLOWED_SEVERITY = frozenset({"blocking", "warning", "info"})
ALLOWED_PRIORITY = frozenset({"high", "medium", "low"})

# Allowed values for the `survive` attribute (Section 11.3 of SKILL.md).
# `survive` maps to P-level: min→P0, recovery→P1, work→P2, full→P5.
ALLOWED_SURVIVE = frozenset({"min", "recovery", "work", "full"})

# Mapping from `survive` value to canonical P-level (priority pack).
SURVIVE_TO_PLEVEL = {
    "min": "P0",
    "recovery": "P1",
    "work": "P2",
    "full": "P5",
}

# Mapping from sigil + attributes to P-level (priority classifier).
# These are the canonical rules per Section 11.2 of SKILL.md.
SIGIL_DEFAULT_PLEVEL = {
    "FCS": "P0",
    "OBJ": "P0",
    "STP": "P0",
    "CNST": "P0",   # may be overridden to P1+ if not blocking
    "WRK": "P1",
    "AUD": "P1",
    "RSK": "P1",
    "NXT": "P1",
    "CLAIM": "P2",
    "LIM": "P2",
    "KNW": "P2",
    "LNG": "P2",
    "SES": "P3",
    "STAT": "P3",
    "REF": "P4",
    "DIAG": "P5",
    "TAG": "P5",
    "IDN": "P2",
    "DOM": "P2",
    "AXM": "P0",
    "!": "P0",
    "HDL": "P3",
    "PFL": "P2",
    "DEP": "P3",
    "DESC": "P4",
    "ERR": "P1",
}

# Canonical P-level ordering (lowest P0 = highest priority)
PLEVEL_ORDER = ["P0", "P1", "P2", "P3", "P4", "P5"]

# Canonical micro-tokens (Section 4.1.1)
CANONICAL_MICRO = {
    "cur": "current",
    "pln": "planned",
    "fut": "future",
    "blk": "blocked",
    "min": "minimum",
    "rec": "recovery",
    "wrk": "work",
    "full": "full",
    "ok": "success",
    "fail": "failure",
    "part": "partial",
}
