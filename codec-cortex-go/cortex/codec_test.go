package cortex

import (
	"os"
	"strings"
	"testing"
)

func readFixture(t *testing.T, name string) string {
	t.Helper()
	b, err := os.ReadFile("../testdata/" + name)
	if err != nil {
		t.Fatal(err)
	}
	return string(b)
}

func TestPythonCanonicalGolden(t *testing.T) {
	doc, err := ParseCortex(readFixture(t, "full.cortex"))
	if err != nil {
		t.Fatal(err)
	}
	got, err := Canonicalize(doc)
	if err != nil {
		t.Fatal(err)
	}
	want := readFixture(t, "full.canonical.cortex")
	if got != want {
		t.Fatalf("canonical mismatch\n--- got ---\n%s\n--- want ---\n%s", got, want)
	}
}

func TestHCORTEXGoldenAndRoundtrip(t *testing.T) {
	doc, err := ParseCortex(readFixture(t, "full.cortex"))
	if err != nil {
		t.Fatal(err)
	}
	if _, err = Canonicalize(doc); err != nil {
		t.Fatal(err)
	}
	h, err := RenderHCORTEX(doc)
	if err != nil {
		t.Fatal(err)
	}
	if want := readFixture(t, "full.hcortex.md"); h != want {
		t.Fatalf("HCORTEX mismatch")
	}
	doc2, diags := CompileHCORTEX(h)
	for _, d := range diags {
		if d.Severity == "error" {
			t.Fatalf("unexpected diagnostic: %+v", d)
		}
	}
	round, err := Canonicalize(doc2)
	if err != nil {
		t.Fatal(err)
	}
	if round != readFixture(t, "full.roundtrip.cortex") {
		t.Fatalf("roundtrip mismatch")
	}
	h2, err := RenderHCORTEX(doc2)
	if err != nil {
		t.Fatal(err)
	}
	if h2 != h {
		t.Fatalf("HCORTEX idempotence mismatch")
	}
}

func TestCanonicalIdempotence(t *testing.T) {
	doc, err := ParseCortex(readFixture(t, "full.cortex"))
	if err != nil {
		t.Fatal(err)
	}
	one, err := Canonicalize(doc)
	if err != nil {
		t.Fatal(err)
	}
	doc2, err := ParseCortex(one)
	if err != nil {
		t.Fatal(err)
	}
	two, err := Canonicalize(doc2)
	if err != nil {
		t.Fatal(err)
	}
	if one != two {
		t.Fatalf("canonicalization is not idempotent")
	}
}

func TestDiagnostics(t *testing.T) {
	if doc, diags := CompileHCORTEX("plain text"); doc != nil || len(diags) != 1 || diags[0].Code != "H400" {
		t.Fatalf("missing-header diagnostic mismatch: %#v", diags)
	}
	if doc, diags := CompileHCORTEX("\ufeff<!-- HCORTEX v=0.1 t=canonical -->"); doc != nil || len(diags) != 1 || diags[0].Code != "H490" {
		t.Fatalf("BOM diagnostic mismatch: %#v", diags)
	}
	_, err := ParseCortex("content")
	pe, ok := err.(*ParseError)
	if !ok || pe.Code != "S005_CONTENT_OUTSIDE_SECTION" {
		t.Fatalf("parse diagnostic mismatch: %v", err)
	}
}

func TestCanonicalHash(t *testing.T) {
	got := CanonicalHash([]byte(readFixture(t, "full.canonical.cortex")))
	const want = "sha256:6e99f262135750e7202be3ba3faf3dfda12e077735122c719b83c9f5a19a2698"
	if got != want {
		t.Fatalf("hash mismatch: got %s want %s", got, want)
	}
}

func TestUnicodeNFC(t *testing.T) {
	if ToNFC("e\u0301") != "é" {
		t.Fatal("NFC normalization failed")
	}
}

func TestQuotedScalarsAndLists(t *testing.T) {
	attrs, err := ParseAttrsPayload(`{s:"a\nb",l:[a,"b c",-0,1.20,true,false,null],}`, 1)
	if err != nil {
		t.Fatal(err)
	}
	if len(attrs) != 2 || attrs[1].Value.Kind != ScalarList || len(attrs[1].Value.Items) != 7 {
		t.Fatalf("unexpected attrs: %#v", attrs)
	}
	if !strings.Contains(attrs[0].Value.Text, "\n") {
		t.Fatalf("string escape not decoded")
	}
	if attrs[1].Value.Items[2].Lexeme != "0" {
		t.Fatalf("-0 was not normalized")
	}
}

func FuzzCanonicalRoundtrip(f *testing.F) {
	f.Add(readFixtureForFuzz("../testdata/full.cortex"))
	f.Fuzz(func(t *testing.T, source string) {
		doc, err := ParseCortex(source)
		if err != nil {
			return
		}
		canonical, err := Canonicalize(doc)
		if err != nil {
			return
		}
		doc2, err := ParseCortex(canonical)
		if err != nil {
			t.Fatalf("canonical output did not parse: %v", err)
		}
		canonical2, err := Canonicalize(doc2)
		if err != nil {
			t.Fatal(err)
		}
		if canonical != canonical2 {
			t.Fatalf("non-idempotent canonicalization")
		}
	})
}

func readFixtureForFuzz(path string) string {
	b, _ := os.ReadFile(path)
	return string(b)
}

func TestExplainHCORTEXLoss(t *testing.T) {
	doc, err := ParseCortex(readFixture(t, "full.cortex"))
	if err != nil {
		t.Fatal(err)
	}
	diags := ExplainHCORTEXLoss(doc)
	if len(diags) != 0 {
		t.Fatalf("unexpected HCORTEX loss diagnostics after lossless open-attrs rendering: %#v", diags)
	}
}
