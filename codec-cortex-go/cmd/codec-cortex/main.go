package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"

	cc "github.com/codec-cortex/codec-cortex-go/cortex"
)

const version = "0.1.0-go"

func main() {
	if err := run(os.Args[1:]); err != nil {
		fmt.Fprintln(os.Stderr, "ERROR:", err)
		os.Exit(1)
	}
}

func run(args []string) error {
	if len(args) == 0 {
		return runHarness(nil)
	}

	switch args[0] {
	case "help", "-h", "--help":
		printUsage(os.Stdout)
		return nil
	case "version", "--version":
		fmt.Fprintln(os.Stdout, version)
		return nil
	case "parse":
		return commandParse(args[1:])
	case "validate":
		return commandValidate(args[1:])
	case "canonicalize", "format":
		return commandCanonicalize(args[1:])
	case "to-hcortex":
		return commandToHCORTEX(args[1:])
	case "from-hcortex":
		return commandFromHCORTEX(args[1:])
	case "hash":
		return commandHash(args[1:])
	case "explain-loss":
		return commandExplainLoss(args[1:])
	case "harness", "conformance":
		return runHarness(args[1:])
	default:
		// Compatibility with the Python entry point: positional directories mean harness mode.
		return runHarness(args)
	}
}

func printUsage(w io.Writer) {
	fmt.Fprintln(w, `codec-cortex-go — CORTEX 0.1 / C14N-0.1 / HCORTEX-0.1

Usage:
  codec-cortex parse FILE|-                 Parse CORTEX and emit JSON AST
  codec-cortex validate FILE|-              Validate CORTEX syntax and glossary
  codec-cortex canonicalize FILE|-          Emit canonical CORTEX
  codec-cortex to-hcortex FILE|-            Render canonical HCORTEX representation
  codec-cortex from-hcortex FILE|-          Compile HCORTEX and emit canonical CORTEX
  codec-cortex hash FILE|-                  Emit CORTEX-C14N-0.1 domain-separated hash
  codec-cortex explain-loss FILE|-          Report inherited HCORTEX loss risks
  codec-cortex harness [C14N_DIR] [HC_DIR] [--report FILE]
  codec-cortex version

With no command, the program runs the F3/F4 harness using REV_PACKAGE or ./experiments.`)
}

func requireOneFile(args []string) (string, error) {
	if len(args) != 1 {
		return "", errors.New("expected exactly one input file or - for stdin")
	}
	return args[0], nil
}

func readInput(path string) ([]byte, error) {
	if path == "-" {
		return io.ReadAll(os.Stdin)
	}
	return os.ReadFile(path)
}

func parseInput(args []string) (*cc.Document, error) {
	path, err := requireOneFile(args)
	if err != nil {
		return nil, err
	}
	b, err := readInput(path)
	if err != nil {
		return nil, err
	}
	return cc.ParseCortex(string(b))
}

func commandParse(args []string) error {
	doc, err := parseInput(args)
	if err != nil {
		return err
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	enc.SetEscapeHTML(false)
	return enc.Encode(doc)
}

func commandValidate(args []string) error {
	if _, err := parseInput(args); err != nil {
		return err
	}
	fmt.Fprintln(os.Stdout, "PASS")
	return nil
}

func commandCanonicalize(args []string) error {
	doc, err := parseInput(args)
	if err != nil {
		return err
	}
	out, err := cc.Canonicalize(doc)
	if err != nil {
		return err
	}
	_, err = io.WriteString(os.Stdout, out)
	return err
}

func commandToHCORTEX(args []string) error {
	doc, err := parseInput(args)
	if err != nil {
		return err
	}
	// Match the reference harness: normalize/expand before HCORTEX rendering.
	if _, err = cc.Canonicalize(doc); err != nil {
		return err
	}
	out, err := cc.RenderHCORTEX(doc)
	if err != nil {
		return err
	}
	_, err = io.WriteString(os.Stdout, out)
	return err
}

func commandFromHCORTEX(args []string) error {
	path, err := requireOneFile(args)
	if err != nil {
		return err
	}
	b, err := readInput(path)
	if err != nil {
		return err
	}
	doc, diags := cc.CompileHCORTEX(string(b))
	hasError := doc == nil
	for _, d := range diags {
		if d.Severity == "error" {
			hasError = true
		}
	}
	if hasError {
		enc := json.NewEncoder(os.Stderr)
		enc.SetIndent("", "  ")
		_ = enc.Encode(diags)
		return errors.New("HCORTEX compilation failed")
	}
	out, err := cc.Canonicalize(doc)
	if err != nil {
		return err
	}
	_, err = io.WriteString(os.Stdout, out)
	return err
}

func commandHash(args []string) error {
	doc, err := parseInput(args)
	if err != nil {
		return err
	}
	canonical, err := cc.Canonicalize(doc)
	if err != nil {
		return err
	}
	fmt.Fprintln(os.Stdout, cc.CanonicalHash([]byte(canonical)))
	return nil
}

func commandExplainLoss(args []string) error {
	doc, err := parseInput(args)
	if err != nil {
		return err
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	enc.SetEscapeHTML(false)
	return enc.Encode(cc.ExplainHCORTEXLoss(doc))
}

func runHarness(args []string) error {
	base := os.Getenv("REV_PACKAGE")
	if base == "" {
		base = "experiments"
	}
	c14nDir := filepath.Join(base, "gate-f3", "c14n-corpus")
	hcortexDir := filepath.Join(base, "gate-f4")
	reportPath := "rev-report.json"

	positional := []string{}
	for i := 0; i < len(args); i++ {
		if args[i] == "--report" {
			if i+1 >= len(args) {
				return errors.New("--report requires a file path")
			}
			reportPath = args[i+1]
			i++
			continue
		}
		positional = append(positional, args[i])
	}
	if len(positional) > 0 {
		c14nDir = positional[0]
	}
	if len(positional) > 1 {
		hcortexDir = positional[1]
	}
	if len(positional) > 2 {
		reportPath = positional[2]
	}

	if !pathExists(c14nDir) {
		alt := filepath.Join(base, "c14n", "corpus")
		if pathExists(alt) {
			c14nDir = alt
		}
	}
	if !pathExists(hcortexDir) {
		alt := filepath.Join(base, "hcortex")
		if pathExists(alt) {
			hcortexDir = alt
		}
	}
	if !pathExists(c14nDir) && !pathExists(hcortexDir) {
		return fmt.Errorf("neither corpus directory exists: %s, %s", c14nDir, hcortexDir)
	}

	fmt.Fprintf(os.Stderr, "C14N directory: %s\n", c14nDir)
	fmt.Fprintf(os.Stderr, "HCORTEX directory: %s\n", hcortexDir)
	report := cc.RunAllTests(c14nDir, hcortexDir)
	b, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		return err
	}
	b = append(b, '\n')
	if reportPath != "-" {
		if dir := filepath.Dir(reportPath); dir != "." {
			if err := os.MkdirAll(dir, 0o755); err != nil {
				return err
			}
		}
		if err := os.WriteFile(reportPath, b, 0o644); err != nil {
			return err
		}
		fmt.Fprintf(os.Stderr, "Report written to: %s\n", reportPath)
	}
	_, _ = os.Stdout.Write(b)
	verdict, _ := report["verdict"].(string)
	if strings.EqualFold(verdict, "PASS") || strings.EqualFold(verdict, "CONDITIONAL_PASS") {
		return nil
	}
	return fmt.Errorf("conformance verdict: %s", verdict)
}

func pathExists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}
