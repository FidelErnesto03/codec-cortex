# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2026 Fidel Ernesto Lozada A.

"""Tests for :mod:`cortex.core.document_handle` — the unified transport layer.

Verifies:
  1. DocumentHandle creation and dialect query helpers
  2. detect_dialect() heuristic for Core, V2, HCORTEX
  3. CoreDocumentAdapter load/loads/render (roundtrip)
  4. V2DocumentAdapter load/loads/render (roundtrip, no v1 downcast)
  5. HCortexDocumentAdapter load/loads/render (roundtrip)
  6. adapter_for() factory returns cached instances
  7. load_doc() with return_handle=True returns (CortexDocument, DocumentHandle)
"""

import hashlib
import os
import tempfile

import pytest

from cortex.core.ast import CortexDocument, compute_document_hash
from cortex.core.document_handle import (
    CoreDocumentAdapter,
    Dialect,
    Diagnostic,
    DocumentHandle,
    HCortexDocumentAdapter,
    V2DocumentAdapter,
    adapter_for,
    detect_dialect,
)
from cortex.core.errors import CortexError
from cortex.cli.commands import load_doc


# ---------------------------------------------------------------------------
# Shared fixture text
# ---------------------------------------------------------------------------

CORE_TEXT = """\
$0: MINIMAL LOCAL GLOSSARY

# -- $0: MINIMAL LOCAL GLOSSARY --
# Sigil | Name    | Type   | Risk | Layer      | Description
# IDN   | identity| attrs  | B    | Semantic   | Identity
# FCS   | focus   | attrs  | H    | Working    | Active focus
# OBJ   | objective| attrs | H    | Working    | Active objective

$1: FOCUS

FCS:primary{what:"Test focus", status:current}
OBJ:primary{goal:"Test objective", status:current}
"""

V2_TEXT = """\
```markdown
<!-- CODEC-CORTEX
internal_encoding: CORTEX
source_artifact: test
-->

$0
IDN:identity{type:attrs,risk:B,cortex:Semantic,desc:"Identity"}
FCS:focus{type:attrs,risk:H,cortex:Working,desc:"Active focus"}
OBJ:objective{type:attrs,risk:H,cortex:Working,desc:"Active objective"}

$1: FOCUS
FCS:primary{what:"Test focus v2",status:current,scope:"test"}
OBJ:primary{goal:"Test objective v2",status:current,scope:"test"}
```
"""

HCORTEX_TEXT = """\
<!-- cortex-render: hcortex-edit; roundtrip: structural; source: test; hash: test-hash -->

<!-- cortex-section: id="$0" title="MINIMAL LOCAL GLOSSARY" -->
## MINIMAL LOCAL GLOSSARY

```cortex-glossary
# Sigil | Name | Type | Risk | Layer | Description
IDN | identity | attrs | B | Semantic | Identity
FCS | focus | attrs | H | Working | Active focus
OBJ | objective | attrs | H | Working | Active objective
```

<!-- cortex-section: id="$1" title="FOCUS" -->
## FOCUS

<!-- cortex-entry: section="$1" sigil="FCS" name="primary" type="attrs" -->
| what | status |
|---|---|
| Test focus hcortex | current |

<!-- cortex-entry: section="$1" sigil="OBJ" name="primary" type="attrs" -->
| goal | status |
|---|---|
| Test objective hcortex | current |
"""


# ---------------------------------------------------------------------------
# 1. DocumentHandle creation
# ---------------------------------------------------------------------------


class TestDocumentHandle:
    def test_create(self):
        ast = object()
        handle = DocumentHandle(
            dialect=Dialect.CORE,
            source="<test>",
            source_hash="sha256:abc",
            ast=ast,
        )
        assert handle.dialect == Dialect.CORE
        assert handle.source == "<test>"
        assert handle.source_hash == "sha256:abc"
        assert handle.ast is ast
        assert handle.diagnostics == []

    def test_query_helpers(self):
        core_h = DocumentHandle(Dialect.CORE, "f", "h", object())
        v2_h = DocumentHandle(Dialect.V2, "f", "h", object())
        hc_h = DocumentHandle(Dialect.HCORTEX, "f", "h", object())

        assert core_h.is_core is True
        assert core_h.is_v2 is False
        assert core_h.is_hcortex is False

        assert v2_h.is_core is False
        assert v2_h.is_v2 is True
        assert v2_h.is_hcortex is False

        assert hc_h.is_core is False
        assert hc_h.is_v2 is False
        assert hc_h.is_hcortex is True

    def test_core_ast_returns_cortex_document(self):
        from cortex.core.ast import CortexDocument

        doc = CortexDocument()
        handle = DocumentHandle(Dialect.CORE, "f", "h", doc)
        assert handle.core_ast() is doc

    def test_core_ast_raises_for_v2(self):
        handle = DocumentHandle(Dialect.V2, "f", "h", object())
        with pytest.raises(TypeError, match="cannot return CortexDocument"):
            handle.core_ast()


# ---------------------------------------------------------------------------
# 2. Dialect detection
# ---------------------------------------------------------------------------


class TestDetectDialect:
    def test_core(self):
        assert detect_dialect(CORE_TEXT) == Dialect.CORE

    def test_v2_markdown_wrapper(self):
        assert detect_dialect(V2_TEXT) == Dialect.V2

    def test_v2_codec_cortex_header(self):
        text = "some preamble\n<!-- CODEC-CORTEX\nkey: val\n-->\n$0"
        assert detect_dialect(text) == Dialect.V2

    def test_hcortex(self):
        assert detect_dialect(HCORTEX_TEXT) == Dialect.HCORTEX

    def test_empty_text_defaults_to_core(self):
        assert detect_dialect("") == Dialect.CORE
        assert detect_dialect("   \n\n  ") == Dialect.CORE


# ---------------------------------------------------------------------------
# 3. CoreDocumentAdapter roundtrip
# ---------------------------------------------------------------------------


class TestCoreAdapter:
    def test_loads_returns_core_handle(self):
        adapter = CoreDocumentAdapter()
        handle = adapter.loads(CORE_TEXT, source="<test>")

        assert handle.dialect == Dialect.CORE
        assert handle.source == "<test>"
        assert isinstance(handle.ast, CortexDocument)
        assert handle.source_hash == compute_document_hash(CORE_TEXT)

    def test_roundtrip(self):
        adapter = CoreDocumentAdapter()
        handle = adapter.loads(CORE_TEXT)
        rendered = adapter.render(handle)
        # Re-parse and compare
        handle2 = adapter.loads(rendered)
        assert handle2.ast.sections[0].id == "$0"
        assert len(handle2.ast.sections) == 2  # $0 + $1

    def test_load_raises_on_missing_file(self):
        adapter = CoreDocumentAdapter()
        with pytest.raises(CortexError, match="E013_NOT_FOUND"):
            adapter.load("/nonexistent/path.cortex")

    def test_load_from_file(self):
        adapter = CoreDocumentAdapter()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cortex", delete=False, encoding="utf-8"
        ) as f:
            f.write(CORE_TEXT)
            tmp = f.name
        try:
            handle = adapter.load(tmp)
            assert handle.dialect == Dialect.CORE
            assert handle.source == tmp
            assert isinstance(handle.ast, CortexDocument)
        finally:
            os.unlink(tmp)


# ---------------------------------------------------------------------------
# 4. V2DocumentAdapter roundtrip (no v1 downcast)
# ---------------------------------------------------------------------------


class TestV2Adapter:
    def test_loads_returns_v2_handle(self):
        adapter = V2DocumentAdapter()
        handle = adapter.loads(V2_TEXT, source="<test-v2>")

        assert handle.dialect == Dialect.V2
        assert handle.source == "<test-v2>"
        assert handle.source_hash == compute_document_hash(V2_TEXT)
        # Validate the AST is a CortexV2Document, not CortexDocument
        from cortex.v2.parser import CortexV2Document

        assert isinstance(handle.ast, CortexV2Document)

    def test_roundtrip_preserves_content(self):
        """V2 roundtrip must preserve all entries and their values.

        Section header titles (``$1:FOCUS`` vs ``$1``) may be normalised
        by the writer — what matters is that every entry survives.
        """
        adapter = V2DocumentAdapter()
        handle = adapter.loads(V2_TEXT)
        rendered = adapter.render(handle)

        # Re-parse the rendered output and verify entries
        handle2 = adapter.loads(rendered)
        fcs_entries = handle2.ast.get_entries(section_id="$1", sigil="FCS")
        assert len(fcs_entries) >= 1
        assert fcs_entries[0].value.get("what") == "Test focus v2"

    def test_no_downcast_to_v1(self):
        """Loading a v2 doc via V2DocumentAdapter must NOT cast to v1."""
        adapter = V2DocumentAdapter()
        handle = adapter.loads(V2_TEXT)
        from cortex.v2.parser import CortexV2Document

        assert isinstance(handle.ast, CortexV2Document)
        with pytest.raises(TypeError):
            handle.core_ast()

    def test_adapter_has_v2_entries(self):
        adapter = V2DocumentAdapter()
        handle = adapter.loads(V2_TEXT)
        # FCS entries: $0 has sigil decl (FCS:focus), $1 has operational (FCS:primary)
        entries = handle.ast.get_entries(section_id="$1", sigil="FCS")
        assert len(entries) >= 1
        assert entries[0].value.get("what") == "Test focus v2"


# ---------------------------------------------------------------------------
# 5. HCortexDocumentAdapter roundtrip
# ---------------------------------------------------------------------------


class TestHCortexAdapter:
    def test_loads_returns_hcortex_handle(self):
        adapter = HCortexDocumentAdapter()
        handle = adapter.loads(HCORTEX_TEXT, source="<test-hc>")

        assert handle.dialect == Dialect.HCORTEX
        assert handle.source == "<test-hc>"
        assert isinstance(handle.ast, CortexDocument)

    def test_roundtrip(self):
        adapter = HCortexDocumentAdapter()
        handle = adapter.loads(HCORTEX_TEXT)
        rendered = adapter.render(handle)
        # Re-parse and verify structure
        handle2 = adapter.loads(rendered)
        entries = list(handle2.ast.iter_entries())
        sigils = {e.sigil for _, e in entries}
        assert "FCS" in sigils
        assert "OBJ" in sigils


# ---------------------------------------------------------------------------
# 6. adapter_for() factory
# ---------------------------------------------------------------------------


class TestAdapterFactory:
    def test_returns_cached_instance(self):
        a1 = adapter_for(Dialect.CORE)
        a2 = adapter_for(Dialect.CORE)
        assert a1 is a2  # same cached instance

        a3 = adapter_for(Dialect.V2)
        a4 = adapter_for(Dialect.V2)
        assert a3 is a4

    def test_returns_correct_types(self):
        assert isinstance(adapter_for(Dialect.CORE), CoreDocumentAdapter)
        assert isinstance(adapter_for(Dialect.V2), V2DocumentAdapter)
        assert isinstance(adapter_for(Dialect.HCORTEX), HCortexDocumentAdapter)

    def test_unknown_dialect_raises(self):
        with pytest.raises(ValueError, match="unknown dialect"):
            adapter_for("fake")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 7. load_doc() with return_handle
# ---------------------------------------------------------------------------


class TestLoadDocWithHandle:
    def test_core_return_handle(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cortex", delete=False, encoding="utf-8"
        ) as f:
            f.write(CORE_TEXT)
            tmp = f.name
        try:
            doc, handle = load_doc(tmp, return_handle=True)
            assert isinstance(doc, CortexDocument)
            assert isinstance(handle, DocumentHandle)
            assert handle.dialect == Dialect.CORE
            assert handle.source == tmp
        finally:
            os.unlink(tmp)

    def test_v2_return_handle(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cortex.md", delete=False, encoding="utf-8"
        ) as f:
            f.write(V2_TEXT)
            tmp = f.name
        try:
            doc, handle = load_doc(tmp, return_handle=True)
            assert isinstance(doc, CortexDocument)
            assert isinstance(handle, DocumentHandle)
            assert handle.dialect == Dialect.V2
            # Must NOT have been downcast at the DocumentHandle level
            from cortex.v2.parser import CortexV2Document

            assert isinstance(handle.ast, CortexV2Document)
        finally:
            os.unlink(tmp)

    def test_core_default_no_handle(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cortex", delete=False, encoding="utf-8"
        ) as f:
            f.write(CORE_TEXT)
            tmp = f.name
        try:
            result = load_doc(tmp)
            assert isinstance(result, CortexDocument)
            assert not isinstance(result, tuple)
        finally:
            os.unlink(tmp)


# ---------------------------------------------------------------------------
# 8. Diagnostic model
# ---------------------------------------------------------------------------


class TestDiagnostic:
    def test_create(self):
        d = Diagnostic(code="E001", message="test error", severity="error", line=42)
        assert d.code == "E001"
        assert d.line == 42
        assert d.severity == "error"

    def test_default_line_is_none(self):
        d = Diagnostic(code="W001", message="warning", severity="warning")
        assert d.line is None
