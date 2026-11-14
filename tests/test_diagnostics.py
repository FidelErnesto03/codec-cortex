"""Deterministic diagnostic precedence (spec §9 / errors-1.0.md).

When a single line violates several rules, exactly one diagnostic is emitted,
following the parser's verification order.

Run with: python -m unittest discover -s tests -p 'test_*.py'
"""

import unittest

from codec_cortex.dispatcher import parse_cortex
from codec_cortex.scalars import ParseError

GLOSSARY = (
    "$0:KERNEL\n"
    "$0:format{cortex:1.0,encoding:UTF-8}\n"
    'KNW:knowledge{type:attrs,weight:B,focus:content,desc:"x",'
    'fields:"topic:text|content:text"}\n'
    "$1:KNOW\n"
)


def code_for(line):
    try:
        parse_cortex(GLOSSARY + line + "\n")
    except ParseError as exc:
        return getattr(exc, "code", None)
    return None


class DiagnosticPrecedenceTest(unittest.TestCase):
    def test_invalid_head_beats_undeclared_symbol(self):
        self.assertEqual(code_for("???bad"), "S003_INVALID_IDEA_HEAD")

    def test_non_ascii_name_beats_undeclared_symbol(self):
        # Name is non-ASCII *and* the sigil is undeclared: U003 wins.
        self.assertEqual(code_for("ZZZ:\u03b1\u03bb{ }"), "U003_NON_ASCII_IDENTIFIER")

    def test_undeclared_symbol_when_head_and_name_ok(self):
        self.assertEqual(code_for('ZZZ:alpha{x:"1"}'), "I001_UNDECLARED_SYMBOL")

    def test_shape_delimiter_mismatch(self):
        self.assertEqual(code_for("KNW:alpha| T | C |"), "I004_SHAPE_DELIMITER_MISMATCH")

    def test_duplicate_field_within_payload(self):
        self.assertEqual(
            code_for('KNW:alpha{topic:"T",topic:"U",content:"C"}'), "I006_DUPLICATE_FIELD"
        )


if __name__ == "__main__":
    unittest.main()
