package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, `{"code":"S999_INTERNAL_PARSE_FAILURE","severity":"error","span":{"line":1,"column":1},"message":"Uso: cortex01 <archivo.cortex>"}`)
		os.Exit(1)
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
		ID     string `json:"id"`
		Source string `json:"source"`
		ExpectedAst string `json:"expectedAst,omitempty"`
		ExpectedDiagnostics string `json:"expectedDiagnostics,omitempty"`
		RequiredCodes []string `json:"requiredCodes,omitempty"`
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
