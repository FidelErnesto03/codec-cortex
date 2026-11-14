"""CORTEX 1.0 declared loss report — reference surface tests.

Run with: python -m unittest discover -s tests -p 'test_*.py'
"""

import json
import unittest

from codec_cortex.lossreport import build_loss_report, dumps_canonical

CLEAN = """$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8}
KNW:knowledge{type:attrs,weight:B,focus:content,desc:"x",fields:"topic:text|content:text"}
$1:KNOW
KNW:alpha{topic:"T",content:"C"}
"""

OPEN_SOURCE = """$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8}
META:metadata{type:attrs,weight:B,focus:subject,desc:"m",fields:"subject:text",open:true}
$1:DATA
META:item{custom:"p",subject:"S",priority:high}
"""


def codes(report):
    return [item["code"] for item in report["losses"]]


class LossReportTest(unittest.TestCase):
    def test_clean_document_has_no_losses(self):
        report = build_loss_report(CLEAN, "clean")
        self.assertEqual(codes(report), [])
        self.assertTrue(report["reversible"])
        self.assertTrue(report["structural_equivalence"])
        self.assertEqual(report["warnings"], [])

    def test_coverage_declares_compile_gap(self):
        report = build_loss_report(CLEAN, "clean")
        self.assertEqual(
            report["coverage"],
            {"complete": False, "operations": ["render"], "uncovered_operations": ["compile"]},
        )

    def test_dotted_namespace_roundtrips(self):
        # Regression: a namespace with '.' must survive the render/compile
        # roundtrip (marker grammar aligned with CORTEX), emitting no loss.
        source = CLEAN.replace("KNW:knowledge", "tenant.x::KNW:knowledge").replace(
            "KNW:alpha", "tenant.x::KNW:alpha"
        )
        report = build_loss_report(source, "nsdot")
        self.assertEqual(codes(report), [])
        self.assertTrue(report["reversible"])

    def test_comment_is_declared_loss(self):
        source = CLEAN.replace("$1:KNOW", "# comentario\n$1:KNOW")
        report = build_loss_report(source, "comment")
        self.assertEqual(codes(report), ["L402_COMMENT_DROPPED"])
        self.assertEqual(report["losses"][0]["path"], "line:4")

    def test_whitespace_is_declared_loss(self):
        source = CLEAN.replace('KNW:alpha{topic:"T",content:"C"}',
                               'KNW:alpha{topic:"T",  content:"C"}')
        report = build_loss_report(source, "whitespace")
        self.assertEqual(codes(report), ["L403_INTRALINE_WHITESPACE"])

    def test_quoted_whitespace_is_not_a_loss(self):
        source = CLEAN.replace('desc:"x"', 'desc:"dos  espacios"')
        self.assertEqual(codes(build_loss_report(source, "quoted")), [])

    def test_open_attr_order_is_declared_loss(self):
        report = build_loss_report(OPEN_SOURCE, "open")
        self.assertEqual(codes(report), ["L405_OPEN_ATTR_ORDER"])
        self.assertEqual(report["losses"][0]["path"], "$1")

    def test_canonical_open_attr_order_is_not_a_loss(self):
        source = OPEN_SOURCE.replace('META:item{custom:"p",subject:"S",priority:high}',
                                     'META:item{subject:"S",custom:"p",priority:high}')
        self.assertEqual(codes(build_loss_report(source, "open-ok")), [])

    def test_bare_glossary_roundtrips(self):
        source = CLEAN.replace("$0:KERNEL", "$0")
        report = build_loss_report(source, "bare")
        self.assertEqual(codes(report), [])
        self.assertTrue(report["reversible"])

    def test_glossary_title_is_rejected(self):
        source = CLEAN.replace("$0:KERNEL", "$0: Titulo")
        with self.assertRaises(Exception) as ctx:
            build_loss_report(source, "title")
        self.assertIn("G042_GLOSSARY_HEADER_INVALID", str(ctx.exception))

    def test_canonical_serialization_is_stable(self):
        text = dumps_canonical(build_loss_report(CLEAN, "clean"))
        self.assertTrue(text.endswith("}\n"))
        self.assertEqual(text, dumps_canonical(json.loads(text)))
        keys = [line.split('"')[1] for line in text.splitlines() if line.startswith('  "')]
        self.assertEqual(keys, sorted(keys))


if __name__ == "__main__":
    unittest.main()
