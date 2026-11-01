package cortex

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func repoRoot(t *testing.T) string {
	t.Helper()
	root, err := filepath.Abs("../..")
	if err != nil {
		t.Fatal(err)
	}
	return root
}

func TestV10RoundtripCorpus(t *testing.T) {
	root := repoRoot(t)
	cases := []struct {
		dir     string
		version string
	}{
		{"conformance/1.0/valid", "1.0"},
		{"conformance/slots/valid", "0.2"},
	}
	total, ok := 0, 0
	for _, c := range cases {
		files, _ := filepath.Glob(filepath.Join(root, c.dir, "*.cortex"))
		for _, f := range files {
			src, err := os.ReadFile(f)
			if err != nil {
				t.Fatal(err)
			}
			doc, err := ParseV10(string(src), c.version)
			if err != nil {
				t.Errorf("%s parse: %v", f, err)
				continue
			}
			expected, err := canonicalizeV10(doc)
			if err != nil {
				t.Errorf("%s c14n: %v", f, err)
				continue
			}
			render, err := RenderHCORTEX10(doc)
			if err != nil {
				t.Errorf("%s render: %v", f, err)
				continue
			}
			back, diags := CompileHCORTEX10(render)
			if back == nil || len(diags) > 0 {
				t.Errorf("%s compile: %v", f, diags)
				continue
			}
			got, err := canonicalizeV10(back)
			if err != nil {
				t.Errorf("%s back c14n: %v", f, err)
				continue
			}
			total++
			if got == expected {
				ok++
			} else {
				t.Errorf("%s roundtrip mismatch", f)
			}
		}
	}
	if ok != total {
		t.Fatalf("roundtrip %d/%d", ok, total)
	}
	t.Logf("roundtrip %d/%d", ok, total)
}

func TestV10NormativeVectors(t *testing.T) {
	root := repoRoot(t)
	vectors, _ := filepath.Glob(filepath.Join(root, "conformance/1.0/hcortex/*.md"))
	if len(vectors) == 0 {
		t.Fatal("no HCORTEX 1.0 vectors found")
	}
	ok := 0
	for _, v := range vectors {
		text, err := os.ReadFile(v)
		if err != nil {
			t.Fatal(err)
		}
		doc, diags := CompileHCORTEX10(string(text))
		if doc == nil || len(diags) > 0 {
			t.Errorf("%s compile: %v", v, diags)
			continue
		}
		source := filepath.Join(root, "conformance/1.0/valid", strings.TrimSuffix(filepath.Base(v), ".md")+".cortex")
		src, err := os.ReadFile(source)
		if err != nil {
			t.Errorf("%s source: %v", v, err)
			continue
		}
		expectedDoc, err := ParseV10(string(src), "1.0")
		if err != nil {
			t.Errorf("%s source parse: %v", source, err)
			continue
		}
		expected, err := canonicalizeV10(expectedDoc)
		if err != nil {
			t.Errorf("%s source c14n: %v", source, err)
			continue
		}
		got, err := canonicalizeV10(doc)
		if err != nil {
			t.Errorf("%s c14n: %v", v, err)
			continue
		}
		if got == expected {
			ok++
		} else {
			t.Errorf("%s vector mismatch", v)
		}
	}
	if ok != len(vectors) {
		t.Fatalf("vectors %d/%d", ok, len(vectors))
	}
	t.Logf("vectors %d/%d", ok, len(vectors))
}
