"""Diagnostics for v2.3.0 — formal error taxonomy.

11 error codes + 1 warning per spec section 5.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


# ---------------------------------------------------------------------------
# Diagnostic dataclass
# ---------------------------------------------------------------------------

@dataclass
class Diagnostic:
    code: str
    message: str
    severity: str = "error"  # error | warning | info
    location: Optional[str] = None  # e.g. "VIEW:foo", "$0/IDN:project"

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "location": self.location,
        }


# ---------------------------------------------------------------------------
# Formal error codes (v2.3.0 spec section 5)
# ---------------------------------------------------------------------------

ERROR_CODES = {
    # HCORTEX-level
    "E_HCORTEX_HEADER_INVALID":      "Header ausente o inválido",
    "E_HCORTEX_NOT_REVERSIBLE":      "Declara o requiere reversión pero no cumple",
    "E_VIEW_MISSING":                "Bloque semántico sin VIEW",
    "E_VIEW_TARGET_UNRESOLVED":      "Target no resoluble",
    "E_VIEW_REVERSE_UNSUPPORTED":    "Estrategia inversa no soportada",
    "E_VIEW_HASH_MISMATCH":          "Hash no coincide",
    "E_HUMAN_BLOCK_UNDECLARED":      "Prosa humana no marcada",
    "E_TABLE_SCHEMA_MISMATCH":       "Tabla no coincide con fields declarados",
    "E_BLOCK_NOT_PRESERVED":         "Bloque verbatim alterado",
    "E_AST_EQUIVALENCE_FAIL":        "No se conserva equivalencia AST",
    "W_HCORTEX_DISPLAY_ONLY":        "Markdown legible, pero no HCORTEX canónico",
}


def has_errors(diags: List[Diagnostic]) -> bool:
    return any(d.severity == "error" for d in diags)


def has_view_errors(diags: List[Diagnostic]) -> bool:
    return any(d.code.startswith("E_VIEW_") and d.severity == "error" for d in diags)
