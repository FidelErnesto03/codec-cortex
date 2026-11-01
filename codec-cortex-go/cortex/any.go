package cortex

import (
	"regexp"
)

var formatVersionRE = regexp.MustCompile(`\$0:format\{[^}]*cortex:"?([0-9.]+)"?`)

// ParseAny dispatches to the 0.1 parser or the 1.0/0.2 slots parser.
func ParseAny(source string) (*Document, error) {
	version := "0.1"
	if m := formatVersionRE.FindStringSubmatch(source); m != nil {
		version = m[1]
	}
	if version == "0.1" {
		return ParseCortex(source)
	}
	return ParseV10(source, version)
}

// CanonicalizeAny canonicalizes with the dialect declared by the document.
func CanonicalizeAny(doc *Document) (string, error) {
	if doc.CortexVersion == "0.1" {
		return Canonicalize(doc)
	}
	return canonicalizeV10(doc)
}

// RenderHCORTEXAny renders the projection for the document dialect.
func RenderHCORTEXAny(doc *Document) (string, error) {
	if doc.CortexVersion == "0.1" {
		return RenderHCORTEX(doc)
	}
	return RenderHCORTEX10(doc)
}

// CompileHCORTEXAny compiles an HCORTEX projection back to the AST.
func CompileHCORTEXAny(text string) (*Document, []HDiagnostic) {
	if m := envelopeV10RE.FindStringSubmatch(text); m != nil && m[1] == "0.1" {
		return CompileHCORTEX(text)
	}
	return CompileHCORTEX10(text)
}

// HashAny returns the domain-separated hash for the document dialect.
func HashAny(doc *Document) (string, error) {
	canonical, err := CanonicalizeAny(doc)
	if err != nil {
		return "", err
	}
	if doc.CortexVersion == "0.1" {
		return CanonicalHash([]byte(canonical)), nil
	}
	return HashSlots([]byte(canonical)), nil
}
