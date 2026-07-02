"""Safe, deterministic condition parser for learning policies.

A *condition* is a string of the form::

    promotion_score>=8|user_validated=true|risk_weight>=5

Semantics:

- ``|`` is AND (every clause must hold).
- Each clause has the form ``<field> <op> <value>``.
- Supported operators: ``=``, ``!=``, ``>=``, ``<=``, ``>``, ``<``.
- Field names match a ``[A-Za-z_][A-Za-z0-9_]*`` pattern.
- Values may be: integers, floats, ``true``/``false``, ``null`` or
  double-quoted strings.

Hard requirements (enforced by SPEC §9.2):

- MUST NOT use :func:`eval`, :func:`exec`, :func:`compile` or any
  dynamic-execution primitive.
- MUST NOT import :mod:`ast` for expression evaluation.
- MUST fail closed (raise :class:`ConditionError`) on any malformed input.

The parser is intentionally minimal — we only evaluate what the policy
DSL needs, nothing more.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from .errors import LE005_CONDITION_INVALID, LearningError


_FIELD_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_OP_RE = re.compile(r"^(>=|<=|!=|==|=|>|<)$")


@dataclass(frozen=True)
class Clause:
    """A single ``field op value`` clause."""

    field: str
    op: str
    value: Any  # int | float | bool | None | str

    def evaluate(self, context: Dict[str, Any]) -> bool:
        actual = context.get(self.field)
        return _compare(actual, self.op, self.value)


@dataclass(frozen=True)
class Condition:
    """A conjunction (AND) of :class:`Clause` objects."""

    clauses: List[Clause]
    raw: str = ""

    def evaluate(self, context: Optional[Dict[str, Any]] = None) -> bool:
        ctx = context or {}
        return all(c.evaluate(ctx) for c in self.clauses)


# ---------------------------------------------------------------------------
# Value parsing
# ---------------------------------------------------------------------------


def _parse_value(raw: str) -> Any:
    """Convert a raw token into a Python value.

    Forbidden patterns are explicitly rejected to keep the surface
    minimal — we never call :func:`eval` and we never let arbitrary
    strings masquerade as code.
    """

    s = raw.strip()
    if not s:
        raise LearningError(
            LE005_CONDITION_INVALID,
            "empty value in condition clause",
        )
    # double-quoted string
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return _unescape(s[1:-1])
    # bool / null
    low = s.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low in ("null", "none", "nil"):
        return None
    # integer
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    # float
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    # bare identifier: accept as string ONLY if it matches a strict word
    if _FIELD_RE.match(s):
        return s
    raise LearningError(
        LE005_CONDITION_INVALID,
        f"unparseable value {raw!r} in condition clause",
    )


def _unescape(s: str) -> str:
    out: List[str] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "\\" and i + 1 < n:
            nxt = s[i + 1]
            mapping = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}
            out.append(mapping.get(nxt, nxt))
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


def _compare(actual: Any, op: str, expected: Any) -> bool:
    """Compare ``actual`` and ``expected`` using ``op``.

    Type coercions are conservative:

    - ``bool`` vs ``bool``: direct comparison.
    - numeric vs numeric: direct comparison.
    - numeric vs numeric-string: parse the string and compare.
    - bool vs non-bool: ``False`` for ``=``/``==`` (no implicit truthiness).
    - missing (None) vs anything: only ``!=`` and ``==`` are meaningful;
      ``>=``/``<=``/``>``/``<`` against ``None`` return ``False``.
    """

    if op in ("=", "=="):
        return _eq(actual, expected)
    if op == "!=":
        return not _eq(actual, expected)
    # ordering ops: require numeric or string-vs-string
    a, b = _coerce_pair(actual, expected)
    if a is None or b is None:
        return False
    try:
        if op == ">=":
            return a >= b
        if op == "<=":
            return a <= b
        if op == ">":
            return a > b
        if op == "<":
            return a < b
    except TypeError:
        return False
    raise LearningError(LE005_CONDITION_INVALID, f"unknown operator {op!r}")


def _eq(actual: Any, expected: Any) -> bool:
    if isinstance(expected, bool) or isinstance(actual, bool):
        return actual is expected
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return actual == expected
    if isinstance(expected, (int, float)) and isinstance(actual, str):
        try:
            return float(actual) == float(expected)
        except ValueError:
            return False
    if isinstance(expected, str) and isinstance(actual, (int, float)):
        try:
            return float(expected) == float(actual)
        except ValueError:
            return False
    return actual == expected


def _coerce_pair(a: Any, b: Any):
    if isinstance(a, bool) or isinstance(b, bool):
        return None, None
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a, b
    if isinstance(a, str) and isinstance(b, str):
        return a, b
    # numeric coercion when one side is a numeric string
    if isinstance(a, (int, float)) and isinstance(b, str):
        try:
            return a, type(a)(b) if isinstance(a, int) and re.fullmatch(r"-?\d+", b) else float(b)
        except ValueError:
            return None, None
    if isinstance(a, str) and isinstance(b, (int, float)):
        try:
            return type(b)(a) if isinstance(b, int) and re.fullmatch(r"-?\d+", a) else float(a), b
        except ValueError:
            return None, None
    return None, None


# ---------------------------------------------------------------------------
# Top-level parser
# ---------------------------------------------------------------------------


def parse_condition(text: str) -> Condition:
    """Parse a ``|``-conjoined condition string into a :class:`Condition`.

    Raises :class:`LearningError` (LE005) on any malformed input — never
    returns a partially-parsed condition.
    """

    if text is None:
        raise LearningError(LE005_CONDITION_INVALID, "condition is None")
    s = text.strip()
    if not s:
        # Empty condition is treated as the trivially-true conjunction
        # (zero clauses). This is the only "permissive" branch —
        # everything else fails closed.
        return Condition(clauses=[], raw=text)
    parts = [p.strip() for p in s.split("|")]
    clauses: List[Clause] = []
    for part in parts:
        if not part:
            raise LearningError(
                LE005_CONDITION_INVALID,
                f"empty clause in condition {text!r}",
            )
        clauses.append(_parse_clause(part))
    return Condition(clauses=clauses, raw=text)


def _parse_clause(part: str) -> Clause:
    # Find the operator: scan from left for one of the supported ops.
    # We try two-char ops first to avoid mismatches.
    for op in (">=", "<=", "!=", "==", "=", ">", "<"):
        idx = part.find(op)
        if idx > 0:
            field = part[:idx].strip()
            value_raw = part[idx + len(op):].strip()
            if not _FIELD_RE.match(field):
                raise LearningError(
                    LE005_CONDITION_INVALID,
                    f"invalid field name {field!r} in clause {part!r}",
                )
            if not _OP_RE.match(op):
                raise LearningError(
                    LE005_CONDITION_INVALID,
                    f"invalid operator {op!r} in clause {part!r}",
                )
            value = _parse_value(value_raw)
            return Clause(field=field, op=op, value=value)
    raise LearningError(
        LE005_CONDITION_INVALID,
        f"no operator found in clause {part!r}",
    )


# ---------------------------------------------------------------------------
# Convenience: build a callable evaluator
# ---------------------------------------------------------------------------


def make_evaluator(condition_text: str) -> Callable[[Dict[str, Any]], bool]:
    """Return a closure that evaluates ``condition_text`` against a context.

    The condition is parsed ONCE; subsequent calls reuse the parsed
    structure. This is the function the policy evaluator uses.
    """

    cond = parse_condition(condition_text)
    return lambda ctx: cond.evaluate(ctx)


__all__ = [
    "Clause",
    "Condition",
    "parse_condition",
    "make_evaluator",
]
