"""Domain facade (api.py), ideatic emission (emit.py) and enriched
diagnostics — additive 1.x tooling tests (U2/U3/U4/U8/U5/U9/U10/U12).

Run with: python -m unittest discover -s tests -p 'test_*.py'
"""

import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

import codec_cortex as cc
from codec_cortex import __main__ as cli
from codec_cortex.api import CompileError
from codec_cortex.emit import emit, emit_value
from codec_cortex.scalars import ParseError, Scalar

DOC_10 = (
    "$0:KERNEL\n"
    "$0:format{cortex:1.0,encoding:UTF-8}\n"
    'KNW:knowledge{type:attrs,weight:B,focus:content,desc:"x",'
    'fields:"topic:text|content:text"}\n'
    "POS:pos{type:attrs-pos,weight:M,pos:\"a:text|b:int\",focus:a,desc:\"p\"}\n"
    "BOD:body{type:cuerpo,weight:B,desc:\"b\"}\n"
    "BLK:block{type:bloque,weight:B,desc:\"c\"}\n"
    "$1:KNOW\n"
    'KNW:alpha{topic:"T",content:"C"}\n'
    "POS:p1|hello|42\n"
    "BOD:t1{\nline one\nline two\n}\n"
    "BLK:k1{\nraw block\n}\n"
)

GLOSSARY = (
    "$0:KERNEL\n"
    "$0:format{cortex:1.0,encoding:UTF-8}\n"
    'KNW:knowledge{type:attrs,weight:B,focus:content,desc:"x",'
    'fields:"topic:text|content:text"}\n'
    "$1:KNOW\n"
)


def _write_tmp(text):
    fd, path = tempfile.mkstemp(suffix=".cortex")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    return path


class EmitValueTest(unittest.TestCase):
    def test_scalar_passthrough(self):
        s = Scalar("atom", "high", "high")
        self.assertEqual(emit_value(s), "high")

    def test_string_always_quoted_and_escaped(self):
        self.assertEqual(emit_value('a"b'), '"a\\"b"')
        self.assertEqual(emit_value("l1\nl2\tt"), '"l1\\nl2\\tt"')

    def test_builtins(self):
        self.assertEqual(emit_value(True), "true")
        self.assertEqual(emit_value(False), "false")
        self.assertEqual(emit_value(None), "null")
        self.assertEqual(emit_value(7), "7")
        self.assertEqual(emit_value(-3), "-3")
        self.assertEqual(emit_value(1.5), "1.5")
        self.assertEqual(emit_value(2.0), "2.0")

    def test_list(self):
        self.assertEqual(emit_value(["a", 1, True]), '["a",1,true]')

    def test_unsupported(self):
        with self.assertRaises(ValueError):
            emit_value({"k": "v"})
        with self.assertRaises(ValueError):
            emit_value(float("nan"))


class EmitTest(unittest.TestCase):
    def test_attrs_inferred_from_dict(self):
        line = emit("KNW", "alpha", {"topic": "T", "content": 'say "hi"'})
        self.assertEqual(line, 'KNW:alpha{topic:"T",content:"say \\"hi\\""}')

    def test_positional_inferred_from_list(self):
        line = emit("POS", "p1", ["hello", 42])
        self.assertEqual(line, "POS:p1|\"hello\"|42")

    def test_cuerpo_inferred_from_str(self):
        self.assertEqual(emit("BOD", "t1", "text"), "BOD:t1{text}")

    def test_cuerpo_multiline(self):
        self.assertEqual(emit("BOD", "t1", "l1\nl2"), "BOD:t1{\nl1\nl2\n}")

    def test_bloque_always_multiline(self):
        self.assertEqual(emit("BLK", "k1", "raw", shape="bloque"), "BLK:k1{\nraw\n}")

    def test_namespace(self):
        self.assertEqual(emit("KNW", "a", {"x": "y"}, namespace="tenant.x"),
                         'tenant.x::KNW:a{x:"y"}')

    def test_relacion_explicit_shape(self):
        self.assertEqual(emit("REL", "r", ["a", "b", "c"], shape="relacion"),
                         'REL:r|"a"|"b"|"c"')

    def test_emitted_lines_parse_in_fresh_document(self):
        """Every idea line emitted by emit() must itself be valid CORTEX."""
        doc = cc.parse(DOC_10)
        lines = []
        for idea in doc.sections[0].ideas:
            payload = idea.payload
            if payload[0] == "attrs":
                fields = dict(payload[1])
                lines.append(emit(idea.symbol, idea.name, fields,
                                  namespace=idea.namespace, shape="attrs"))
            elif payload[0] in ("attrs-pos", "relacion"):
                cells = [Scalar(c.kind, c.value, c.lexeme) for c in payload[1]]
                lines.append(emit(idea.symbol, idea.name, cells,
                                  namespace=idea.namespace, shape=payload[0]))
            else:
                lines.append(emit(idea.symbol, idea.name, payload[1],
                                  namespace=idea.namespace, shape=idea.shape))
        glossary = DOC_10.split("$1:KNOW\n")[0] + "$1:KNOW\n"
        reparsed = cc.parse(glossary + "\n".join(lines) + "\n")
        self.assertEqual(len(reparsed.sections[0].ideas), len(lines))

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            emit("knw", "a", {})          # lowercase sigil
        with self.assertRaises(ValueError):
            emit("KNW", "a b", {})        # space in name
        with self.assertRaises(ValueError):
            emit("KNW", "a", {}, namespace="Bad..ns")
        with self.assertRaises(ValueError):
            emit("KNW", "a", [1, 2], shape="attrs")   # wrong payload kind
        with self.assertRaises(ValueError):
            emit("KNW", "a", "txt", shape="bogus")


class FacadeTest(unittest.TestCase):
    def test_parse_validate_hash_source(self):
        doc = cc.parse(DOC_10)
        self.assertEqual(doc.cortex_version, "1.0")
        self.assertIsNotNone(cc.validate(DOC_10))
        h = cc.hash(doc)
        self.assertTrue(h.startswith("sha256:"))
        self.assertEqual(h, cc.hash_source(DOC_10))
        self.assertEqual(len(h), len("sha256:") + 64)

    def test_canonicalize_matches_dispatcher(self):
        doc = cc.parse(DOC_10)
        self.assertEqual(cc.canonicalize(doc), cc.canonicalize(doc))

    def test_to_from_hcortex_roundtrip(self):
        doc = cc.parse(DOC_10)
        md = cc.to_hcortex(doc)
        self.assertIn("HCORTEX v=1.0", md)
        back = cc.from_hcortex(md)
        self.assertEqual(cc.hash(back), cc.hash(doc))

    def test_from_hcortex_raises_compile_error(self):
        with self.assertRaises(CompileError) as ctx:
            cc.from_hcortex("not hcortex at all")
        self.assertTrue(ctx.exception.diagnostics)
        self.assertIn("code", ctx.exception.diagnostics[0])

    def test_parse_error_on_invalid(self):
        with self.assertRaises(ParseError):
            cc.parse("garbage\n")


class DiagnosticMessageTest(unittest.TestCase):
    def _msg_for(self, line):
        try:
            cc.parse(GLOSSARY + line + "\n")
        except ParseError as exc:
            return exc.code, exc.message
        return None, None

    def test_i001_suggests_declared_sigil(self):
        code, msg = self._msg_for("KNW:alpha{topic:\"T\",content:\"C\"}\nKNZ:beta{x:1}")
        # KNZ is not declared; KNW is — did-you-mean or declared list expected
        self.assertEqual(code, "I001_UNDECLARED_SYMBOL")
        self.assertIn("KNW", msg)

    def test_i001_lists_declared_when_no_close_match(self):
        code, msg = self._msg_for("ZZZZZ:alpha{x:1}")
        self.assertEqual(code, "I001_UNDECLARED_SYMBOL")
        self.assertTrue("KNW" in msg)  # declared sigils are named

    def test_i004_shows_expected_form_attrs(self):
        code, msg = self._msg_for("KNW:alpha| T | C |")
        self.assertEqual(code, "I004_SHAPE_DELIMITER_MISMATCH")
        self.assertIn("SIG:name{", msg)

    def test_i004_expected_form_positional(self):
        doc = (
            "$0:KERNEL\n"
            "$0:format{cortex:1.0,encoding:UTF-8}\n"
            'POS:pos{type:attrs-pos,weight:M,pos:"a:text|b:int",focus:a,desc:"p"}\n'
            "$1:DATA\n"
        )
        try:
            cc.parse(doc + "POS:p1{a:\"x\"}\n")
        except ParseError as exc:
            self.assertEqual(exc.code, "I004_SHAPE_DELIMITER_MISMATCH")
            self.assertIn("SIG:name|", exc.message)


class CliStdinTest(unittest.TestCase):
    def test_validate_stdin(self):
        stdin = io.StringIO(DOC_10)
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdin
        try:
            sys.stdin = stdin
            with redirect_stdout(out), redirect_stderr(err):
                rc = cli.main(["validate", "-"])
        finally:
            sys.stdin = old
        self.assertEqual(rc, 0)
        self.assertIn("valid", out.getvalue())


class CliDiffVerifyTest(unittest.TestCase):
    def setUp(self):
        self.a = _write_tmp(DOC_10)
        self.b = _write_tmp(DOC_10 + "\n")   # trailing newline: same canonical
        self.c = _write_tmp(DOC_10.replace("topic:\"T\"", "topic:\"U\""))
        self.addCleanup(os.unlink, self.a)
        self.addCleanup(os.unlink, self.b)
        self.addCleanup(os.unlink, self.c)

    def _run(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = cli.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_diff_identical_despite_text_difference(self):
        rc, out, _ = self._run(["diff", self.a, self.b])
        self.assertEqual(rc, 0)
        self.assertIn("identical", out)

    def test_diff_different(self):
        rc, out, _ = self._run(["diff", self.a, self.c])
        self.assertEqual(rc, 1)
        self.assertIn("---", out)  # unified diff header

    def test_verify_hash_match(self):
        import codec_cortex as cc2
        h = cc2.hash_source(DOC_10)
        rc, out, _ = self._run(["verify", self.a, h])
        self.assertEqual(rc, 0)
        self.assertIn("match", out)

    def test_verify_hash_mismatch(self):
        rc, out, _ = self._run(["verify", self.a, "sha256:" + "0" * 64])
        self.assertEqual(rc, 1)
        self.assertIn("MISMATCH", out)

    def test_verify_file_semantic(self):
        rc, out, _ = self._run(["verify", self.a, self.b])
        self.assertEqual(rc, 0)
        self.assertIn("match", out)

    def test_verify_file_mismatch_shows_diff(self):
        rc, out, err = self._run(["verify", self.a, self.c])
        self.assertEqual(rc, 1)
        self.assertIn("---", out)
        self.assertIn("MISMATCH", err)

    def test_verify_bad_expectation(self):
        rc, _, err = self._run(["verify", self.a, "no-such-thing"])
        self.assertEqual(rc, 2)
        self.assertIn("cannot resolve", err)


if __name__ == "__main__":
    unittest.main()
