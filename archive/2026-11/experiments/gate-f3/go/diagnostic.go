package main

import (
	"encoding/json"
	"fmt"
	"os"
)

// Severity type
type Severity string

const (
	SeverityError   Severity = "error"
	SeverityWarning Severity = "warning"
	SeverityInfo    Severity = "info"
)

// Span represents a source location
type Span struct {
	Line   int `json:"line"`
	Column int `json:"column"`
}

// Diagnostic represents a single diagnostic message
type Diagnostic struct {
	Code     string   `json:"code"`
	Severity Severity `json:"severity"`
	Span     Span     `json:"span"`
	Message  string   `json:"message"`
}

// DiagnosticList holds diagnostics
type DiagnosticList struct {
	items []Diagnostic
}

func NewDiagnosticList() *DiagnosticList {
	return &DiagnosticList{items: make([]Diagnostic, 0)}
}

func (dl *DiagnosticList) Add(code string, severity Severity, line, col int, msg string) {
	dl.items = append(dl.items, Diagnostic{
		Code:     code,
		Severity: severity,
		Span:     Span{Line: line, Column: col},
		Message:  msg,
	})
}

func (dl *DiagnosticList) HasErrors() bool {
	for _, d := range dl.items {
		if d.Severity == SeverityError {
			return true
		}
	}
	return false
}

func (dl *DiagnosticList) HasCode(code string) bool {
	for _, d := range dl.items {
		if d.Code == code {
			return true
		}
	}
	return false
}

func (dl *DiagnosticList) Len() int {
	return len(dl.items)
}

func (dl *DiagnosticList) EmitAll() {
	enc := json.NewEncoder(os.Stderr)
	enc.SetIndent("", "  ")
	for _, d := range dl.items {
		_ = enc.Encode(d)
	}
}

// EmitDiagnosticsJSON emits the diagnostics in the format expected for invalid test cases
func (dl *DiagnosticList) EmitDiagnosticsJSON() {
	// Build the output in the expected format
	requiredCodes := make([]string, 0)
	for _, d := range dl.items {
		requiredCodes = append(requiredCodes, d.Code)
	}

	output := struct {
		RequiredCodes []string     `json:"requiredCodes"`
		Primary       *Diagnostic  `json:"primary,omitempty"`
		All           []Diagnostic `json:"all,omitempty"`
	}{
		RequiredCodes: requiredCodes,
		All:           dl.items,
	}
	if len(dl.items) > 0 {
		output.Primary = &dl.items[0]
	}

	enc := json.NewEncoder(os.Stderr)
	enc.SetIndent("", "  ")
	_ = enc.Encode(output)
}

func formatDiagnostic(code, msg string, line int) string {
	return fmt.Sprintf("%s|%s|line:%d", code, msg, line)
}
