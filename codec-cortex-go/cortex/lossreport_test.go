package cortex

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

const lossDir = "../../conformance/1.0/loss"

type lossManifest struct {
	Fixtures []struct {
		ID       string   `json:"id"`
		File     string   `json:"file"`
		Expected string   `json:"expected"`
		Codes    []string `json:"codes"`
	} `json:"fixtures"`
}

func readLossManifest(t *testing.T) lossManifest {
	t.Helper()
	raw, err := os.ReadFile(filepath.Join(lossDir, "manifest.json"))
	if err != nil {
		t.Fatalf("manifest: %v", err)
	}
	var manifest lossManifest
	if err := json.Unmarshal(raw, &manifest); err != nil {
		t.Fatalf("manifest json: %v", err)
	}
	return manifest
}

func TestLossReportFixturesMatchExpected(t *testing.T) {
	for _, fixture := range readLossManifest(t).Fixtures {
		t.Run(fixture.ID, func(t *testing.T) {
			source, err := os.ReadFile(filepath.Join(lossDir, fixture.File))
			if err != nil {
				t.Fatalf("read fixture: %v", err)
			}
			report, err := BuildLossReport(string(source), fixture.ID)
			if err != nil {
				t.Fatalf("build report: %v", err)
			}
			var buf bytes.Buffer
			if err := WriteLossReport(&buf, report); err != nil {
				t.Fatalf("write report: %v", err)
			}
			expected, err := os.ReadFile(filepath.Join(lossDir, fixture.Expected))
			if err != nil {
				t.Fatalf("read expected: %v", err)
			}
			if buf.String() != string(expected) {
				t.Fatalf("report differs from expected:\n%s", buf.String())
			}
			got := []string{}
			for _, item := range report.Losses {
				got = append(got, item.Code)
			}
			if strings.Join(got, ",") != strings.Join(fixture.Codes, ",") {
				t.Fatalf("codes = %v, want %v", got, fixture.Codes)
			}
		})
	}
}

func TestGlossaryTitleIsRejected(t *testing.T) {
	source, err := os.ReadFile(filepath.Join(lossDir, "clean.cortex"))
	if err != nil {
		t.Fatalf("read fixture: %v", err)
	}
	mutated := strings.Replace(string(source), "$0:KERNEL", "$0: Titulo", 1)
	if _, err := BuildLossReport(mutated, "title"); err == nil ||
		!strings.Contains(err.Error(), "G042_GLOSSARY_HEADER_INVALID") {
		t.Fatalf("expected G042 error, got %v", err)
	}
}

func TestBareGlossaryRoundtrips(t *testing.T) {
	source, err := os.ReadFile(filepath.Join(lossDir, "bare_glossary.cortex"))
	if err != nil {
		t.Fatalf("read fixture: %v", err)
	}
	report, err := BuildLossReport(string(source), "bare")
	if err != nil {
		t.Fatalf("build report: %v", err)
	}
	if !report.Reversible || len(report.Losses) != 0 {
		t.Fatalf("bare glossary should roundtrip losslessly: %+v", report)
	}
}
