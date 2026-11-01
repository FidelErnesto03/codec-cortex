package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, `{"code":"S999_INTERNAL_PARSE_FAILURE","severity":"error","span":{"line":1,"column":1},"message":"Uso: cortex01 <archivo.cortex>"}`)
		os.Exit(1)
	}

	// Check for flags
	if os.Args[1] == "--canonicalize" {
		if len(os.Args) < 3 {
			fmt.Fprintln(os.Stderr, "Uso: cortex01 --canonicalize <archivo.cortex>")
			os.Exit(1)
		}
		runCanonicalize(os.Args[2])
		return
	}

	if os.Args[1] == "--batch-c14n" {
		if len(os.Args) < 3 {
			fmt.Fprintln(os.Stderr, "Uso: cortex01 --batch-c14n <directorio_input> <directorio_golden>")
			os.Exit(1)
		}
		inputDir := os.Args[2]
		goldenDir := ""
		if len(os.Args) > 3 {
			goldenDir = os.Args[3]
		}
		runBatchC14N(inputDir, goldenDir)
		return
	}

	path := os.Args[1]
	parser := NewParser()
	ast, ok := parser.ParseFile(path)

	if !ok {
		// Emit diagnostics
		emitDiagnostics(parser.diagnostics)
		os.Exit(1)
	}

	// Output AST to stdout
	fmt.Println(string(ast))
	os.Exit(0)
}

func runCanonicalize(path string) {
	data, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading %s: %v\n", path, err)
		os.Exit(1)
	}

	// Parse the document
	parser := NewParser()
	content := string(data)
	lines := strings.Split(content, "\n")
	doc, ok := parser.parseDocument(lines)
	if !ok {
		// Try canonicalization anyway with partial doc
		canonical, report, cok := Canonicalize(data, doc)
		if cok {
			os.Stdout.Write(canonical)
			reportJSON, _ := json.MarshalIndent(report, "", "  ")
			fmt.Fprintln(os.Stderr, string(reportJSON))
			return
		}
		emitDiagnostics(parser.diagnostics)
		os.Exit(1)
	}

	canonical, report, ok := Canonicalize(data, doc)
	if !ok {
		fmt.Fprintln(os.Stderr, "Canonicalization failed")
		os.Exit(1)
	}

	// Output canonical form to stdout
	os.Stdout.Write(canonical)

	// Output report to stderr as JSON
	reportJSON, _ := json.MarshalIndent(report, "", "  ")
	fmt.Fprintln(os.Stderr, string(reportJSON))
}

func runBatchC14N(inputDir, goldenDir string) {
	type result struct {
		File       string `json:"file"`
		Pass       bool   `json:"pass"`
		InputSHA   string `json:"inputSha256,omitempty"`
		OutputSHA  string `json:"outputSha256,omitempty"`
		GoldenSHA  string `json:"goldenSha256,omitempty"`
		Error      string `json:"error,omitempty"`
		Changed    bool   `json:"changed"`
	}

	results := make([]result, 0)
	passed := 0
	failed := 0

	// List input files
	entries, err := os.ReadDir(inputDir)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading input dir: %v\n", err)
		os.Exit(1)
	}

	for _, entry := range entries {
		if entry.IsDir() || !strings.HasSuffix(entry.Name(), ".cortex") {
			continue
		}

		inputPath := filepath.Join(inputDir, entry.Name())
		goldenPath := filepath.Join(goldenDir, entry.Name())

		r := result{File: entry.Name()}

		data, err := os.ReadFile(inputPath)
		if err != nil {
			r.Error = fmt.Sprintf("read error: %v", err)
			r.Pass = false
			failed++
			results = append(results, r)
			continue
		}

		r.InputSHA = sha256Hex(data)

		// Parse
		parser := NewParser()
		content := string(data)
		lines := strings.Split(content, "\n")
		doc, ok := parser.parseDocument(lines)
		if !ok {
			r.Error = "parse error"
			r.Pass = false
			failed++
			results = append(results, r)
			continue
		}

		canonical, report, ok := Canonicalize(data, doc)
		if !ok {
			r.Error = "canonicalization error"
			r.Pass = false
			failed++
			results = append(results, r)
			continue
		}

		r.OutputSHA = sha256Hex(canonical)

		// Compare with golden
		goldenData, err := os.ReadFile(goldenPath)
		if err != nil {
			r.Error = fmt.Sprintf("golden read error: %v", err)
			r.Pass = false
			failed++
			results = append(results, r)
			continue
		}

		r.GoldenSHA = sha256Hex(goldenData)

		if bytesEqual(canonical, goldenData) {
			r.Pass = true
			passed++
		} else {
			r.Pass = false
			r.Error = fmt.Sprintf("mismatch: got %s, expected %s", r.OutputSHA, r.GoldenSHA)
			failed++
		}

		r.Changed = report["changed"].(bool)
		results = append(results, r)
	}

	// Output results JSON
	output := struct {
		Passed  int      `json:"passed"`
		Failed  int      `json:"failed"`
		Results []result `json:"results"`
	}{
		Passed:  passed,
		Failed:  failed,
		Results: results,
	}

	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	enc.Encode(output)
}

func emitDiagnostics(diag *DiagnosticList) {
	if diag.Len() == 0 {
		return
	}

	// Build the output format matching expected-diagnostics format
	requiredCodes := make([]string, 0)
	for _, d := range diag.items {
		requiredCodes = append(requiredCodes, d.Code)
	}

	output := struct {
		RequiredCodes []string     `json:"requiredCodes"`
		Primary       *Diagnostic  `json:"primary,omitempty"`
		All           []Diagnostic `json:"all,omitempty"`
	}{
		RequiredCodes: requiredCodes,
		All:           diag.items,
	}
	if len(diag.items) > 0 {
		output.Primary = &diag.items[0]
	}

	enc := json.NewEncoder(os.Stderr)
	enc.SetIndent("", "  ")
	_ = enc.Encode(output)
}

// RunTest runs a test case and returns the result
func RunTest(sourcePath string, expectedAstPath string) bool {
	parser := NewParser()
	ast, ok := parser.ParseFile(sourcePath)

	if !ok {
		// Failed to parse; output diagnostics
		emitDiagnostics(parser.diagnostics)
		return false
	}

	// Compare AST with expected if provided
	if expectedAstPath != "" {
		expected, err := os.ReadFile(expectedAstPath)
		if err != nil {
			fmt.Fprintf(os.Stderr, "No se pudo leer AST esperado: %v\n", err)
			return false
		}

		// Normalize both JSONs
		var expectedDoc, actualDoc interface{}
		if err := json.Unmarshal(expected, &expectedDoc); err != nil {
			fmt.Fprintf(os.Stderr, "AST esperado invalido: %v\n", err)
			return false
		}
		if err := json.Unmarshal(ast, &actualDoc); err != nil {
			fmt.Fprintf(os.Stderr, "AST actual invalido: %v\n", err)
			return false
		}

		// Compare
		expectedJSON, _ := json.Marshal(expectedDoc)
		actualJSON, _ := json.Marshal(actualDoc)
		if string(expectedJSON) != string(actualJSON) {
			fmt.Fprintf(os.Stderr, "AST mismatch para %s\n", sourcePath)
			fmt.Fprintf(os.Stderr, "Esperado: %s\n", string(expectedJSON))
			fmt.Fprintf(os.Stderr, "Actual: %s\n", string(actualJSON))
			return false
		}
	}

	return true
}

// BatchRun runs all test cases and reports results
func BatchRun(manifestPath string) {
	type TestCase struct {
		ID                  string   `json:"id"`
		Source              string   `json:"source"`
		ExpectedAst         string   `json:"expectedAst,omitempty"`
		ExpectedDiagnostics string   `json:"expectedDiagnostics,omitempty"`
		RequiredCodes       []string `json:"requiredCodes,omitempty"`
	}

	type Manifest struct {
		Version string     `json:"version"`
		Valid   []TestCase `json:"valid"`
		Invalid []TestCase `json:"invalid"`
	}

	data, err := os.ReadFile(manifestPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "No se pudo leer manifest: %v\n", err)
		return
	}

	var manifest Manifest
	if err := json.Unmarshal(data, &manifest); err != nil {
		fmt.Fprintf(os.Stderr, "Manifest invalido: %v\n", err)
		return
	}

	baseDir := filepath.Dir(manifestPath)
	passed := 0
	failed := 0

	// Valid cases
	for _, tc := range manifest.Valid {
		sourcePath := filepath.Join(baseDir, tc.Source)
		expectedPath := filepath.Join(baseDir, tc.ExpectedAst)

		parser := NewParser()
		ast, ok := parser.ParseFile(sourcePath)

		if !ok {
			fmt.Fprintf(os.Stderr, "FAIL %s: no se pudo parsear\n", tc.ID)
			emitDiagnostics(parser.diagnostics)
			failed++
			continue
		}

		// Compare with expected AST
		expected, err := os.ReadFile(expectedPath)
		if err != nil {
			fmt.Fprintf(os.Stderr, "FAIL %s: no se pudo leer AST esperado: %v\n", tc.ID, err)
			failed++
			continue
		}

		var expectedDoc, actualDoc interface{}
		if err := json.Unmarshal(expected, &expectedDoc); err != nil {
			fmt.Fprintf(os.Stderr, "FAIL %s: AST esperado invalido: %v\n", tc.ID, err)
			failed++
			continue
		}
		if err := json.Unmarshal(ast, &actualDoc); err != nil {
			fmt.Fprintf(os.Stderr, "FAIL %s: AST actual invalido: %v\n", tc.ID, err)
			failed++
			continue
		}

		expectedJSON, _ := json.Marshal(expectedDoc)
		actualJSON, _ := json.Marshal(actualDoc)

		if string(expectedJSON) != string(actualJSON) {
			fmt.Fprintf(os.Stderr, "FAIL %s: AST mismatch\n", tc.ID)
			fmt.Fprintf(os.Stderr, "  Esperado: %s\n", string(expectedJSON))
			fmt.Fprintf(os.Stderr, "  Actual:   %s\n", string(actualJSON))
			failed++
			continue
		}

		passed++
	}

	// Invalid cases
	for _, tc := range manifest.Invalid {
		sourcePath := filepath.Join(baseDir, tc.Source)
		_ = filepath.Join(baseDir, tc.ExpectedDiagnostics)

		parser := NewParser()
		_, ok := parser.ParseFile(sourcePath)

		if ok {
			fmt.Fprintf(os.Stderr, "FAIL %s: se esperaba rechazo pero se parseo\n", tc.ID)
			failed++
			continue
		}

		// Check that required codes are present
		hasAllCodes := true
		for _, code := range tc.RequiredCodes {
			if !parser.diagnostics.HasCode(code) {
				fmt.Fprintf(os.Stderr, "FAIL %s: falta codigo requerido: %s\n", tc.ID, code)
				hasAllCodes = false
			}
		}

		if !hasAllCodes {
			failed++
			continue
		}

		passed++
	}

	fmt.Printf("Passed: %d/%d, Failed: %d\n", passed, passed+failed, failed)
}

func extractValidInfo(lines []string) map[string]int {
	info := make(map[string]int)
	// Parse manifest.json for the batch runner
	return info
}
