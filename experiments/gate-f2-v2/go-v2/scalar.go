package main

import (
	"fmt"
	"strconv"
	"strings"
	"unicode"
)

// ScalarParser handles parsing of scalar values
type ScalarParser struct {
	diagnostics *DiagnosticList
}

func NewScalarParser(diag *DiagnosticList) *ScalarParser {
	return &ScalarParser{diagnostics: diag}
}

// parseScalar parses a scalar value from the input
// Returns the parsed value and the number of bytes consumed
func (sp *ScalarParser) parseScalar(input string, line, col int) (ScalarValue, int, int) {
	if len(input) == 0 {
		return NullValue{Node: "NullValue", Value: nil, Lexeme: ""}, 0, line
	}

	// Skip whitespace
	start := 0
	for start < len(input) && (input[start] == ' ' || input[start] == '\t') {
		start++
	}

	if start >= len(input) {
		return NullValue{Node: "NullValue", Value: nil, Lexeme: ""}, start, line
	}

	// Check for string literal
	if input[start] == '"' {
		return sp.parseString(input, line, col+start)
	}

	// Check for list
	if input[start] == '[' {
		return sp.parseList(input, line, col+start)
	}

	// Check for number (decimal or integer)
	if input[start] == '-' || (input[start] >= '0' && input[start] <= '9') {
		return sp.parseNumber(input, line, col+start)
	}

	// Check for boolean
	if strings.HasPrefix(input[start:], "true") {
		remain := start + 4
		if remain >= len(input) || !isIdentChar(rune(input[remain])) {
			return BooleanValue{
				Node:   "BooleanValue",
				Value:  true,
				Lexeme: input[start : start+4],
			}, start + 4, line
		}
	}
	if strings.HasPrefix(input[start:], "false") {
		remain := start + 5
		if remain >= len(input) || !isIdentChar(rune(input[remain])) {
			return BooleanValue{
				Node:   "BooleanValue",
				Value:  false,
				Lexeme: input[start : start+5],
			}, start + 5, line
		}
	}

	// Check for null
	if strings.HasPrefix(input[start:], "null") {
		remain := start + 4
		if remain >= len(input) || !isIdentChar(rune(input[remain])) {
			return NullValue{
				Node:   "NullValue",
				Value:  nil,
				Lexeme: input[start : start+4],
			}, start + 4, line
		}
	}

	// Must be an atom
	return sp.parseAtom(input, start, line, col+start)
}

// parseString parses a quoted string "..."
func (sp *ScalarParser) parseString(input string, line, col int) (ScalarValue, int, int) {
	if len(input) == 0 || input[0] != '"' {
		return StringValue{}, 0, line
	}

	var buf strings.Builder
	i := 1 // skip opening quote
	startLine := line

	for i < len(input) {
		ch := input[i]
		if ch == '"' {
			// End of string
			lexeme := input[:i+1]
			return StringValue{
				Node:   "StringValue",
				Value:  buf.String(),
				Lexeme: lexeme,
			}, i + 1, line
		}
		if ch == '\\' {
			// Escape sequence
			if i+1 >= len(input) {
				sp.diagnostics.Add("L005_INVALID_STRING", SeverityError, line, col+i, "Escaped string en EOF.")
				return StringValue{Node: "StringValue", Value: buf.String(), Lexeme: input[:i]}, i, line
			}
			i++
			esc := input[i]
			switch esc {
			case '"':
				buf.WriteByte('"')
			case '\\':
				buf.WriteByte('\\')
			case 'n':
				buf.WriteByte('\n')
			case 'r':
				buf.WriteByte('\r')
			case 't':
				buf.WriteByte('\t')
			case 'b':
				buf.WriteByte('\b')
			case 'f':
				buf.WriteByte('\f')
			case 'u':
				// Unicode escape \uXXXX
				if i+4 >= len(input) {
					sp.diagnostics.Add("L005_INVALID_STRING", SeverityError, line, col+i, "Unicode escape incompleto.")
					return StringValue{Node: "StringValue", Value: buf.String(), Lexeme: input[:i+1]}, i + 1, line
				}
				hexStr := input[i+1 : i+5]
				code, err := strconv.ParseUint(hexStr, 16, 32)
				if err != nil {
					sp.diagnostics.Add("L005_INVALID_STRING", SeverityError, line, col+i, fmt.Sprintf("Unicode escape invalido: %s", hexStr))
					return StringValue{Node: "StringValue", Value: buf.String(), Lexeme: input[:i+5]}, i + 5, line
				}
				buf.WriteRune(rune(code))
				i += 4
			default:
				sp.diagnostics.Add("L005_INVALID_STRING", SeverityError, line, col+i, fmt.Sprintf("Escape invalido: \\%c", esc))
				return StringValue{Node: "StringValue", Value: buf.String(), Lexeme: input[:i+1]}, i + 1, line
			}
			i++
			continue
		}
		if ch == '\n' || ch == '\r' {
			line++
		}
		buf.WriteByte(ch)
		i++
	}

	// Unterminated string
	sp.diagnostics.Add("L005_INVALID_STRING", SeverityError, startLine, col, "String sin cierre.")
	return StringValue{Node: "StringValue", Value: buf.String(), Lexeme: input}, i, line
}

// parseNumber parses integer or decimal
func (sp *ScalarParser) parseNumber(input string, line, col int) (ScalarValue, int, int) {
	if len(input) == 0 {
		return NullValue{}, 0, line
	}

	i := 0
	neg := false
	if input[i] == '-' {
		neg = true
		i++
	}

	if i >= len(input) || input[i] < '0' || input[i] > '9' {
		sp.diagnostics.Add("L009_INVALID_NUMBER", SeverityError, line, col, "Numero invalido despues de signo.")
		return NullValue{}, i, line
	}

	// Integer part
	start := i
	for i < len(input) && input[i] >= '0' && input[i] <= '9' {
		i++
	}
	intPart := input[start:i]

	// Check for decimal
	if i < len(input) && input[i] == '.' {
		i++
		decStart := i
		for i < len(input) && input[i] >= '0' && input[i] <= '9' {
			i++
		}
		if i == decStart {
			// Just a trailing dot
			sp.diagnostics.Add("L009_INVALID_NUMBER", SeverityError, line, col, "Decimal incompleto.")
			return IntegerValue{
				Node:   "IntegerValue",
				Value:  intPart,
				Lexeme: input[:i],
			}, i, line
		}
		decPart := input[decStart:i]
		fullVal := intPart + "." + decPart
		if neg {
			fullVal = "-" + fullVal
		}
		return DecimalValue{
			Node:   "DecimalValue",
			Value:  fullVal,
			Lexeme: input[:i],
		}, i, line
	}

	// Integer
	fullVal := intPart
	if neg {
		fullVal = "-" + fullVal
	}
	return IntegerValue{
		Node:   "IntegerValue",
		Value:  fullVal,
		Lexeme: input[:i],
	}, i, line
}

// parseAtom parses a bare (unquoted) atom value
func (sp *ScalarParser) parseAtom(input string, start, line, col int) (ScalarValue, int, int) {
	// Atom: optional $N: prefix, then at least one alpha/_, then more chars
	i := start
	atomStart := start

	// Skip $N: prefix (section reference)
	// format: $positive-integer:
	if i+1 < len(input) && input[i] == '$' && i+1 < len(input) && input[i+1] >= '1' && input[i+1] <= '9' {
		j := i + 2
		for j < len(input) && input[j] >= '0' && input[j] <= '9' {
			j++
		}
		if j < len(input) && input[j] == ':' {
			i = j + 1
		}
	}

	// Must start with alpha or _
	if i >= len(input) || !((input[i] >= 'a' && input[i] <= 'z') || (input[i] >= 'A' && input[i] <= 'Z') || input[i] == '_') {
		// Could be empty or just punctuation
		if i >= len(input) || input[i] == ',' || input[i] == '}' || input[i] == ']' || input[i] == '\n' || input[i] == '\r' {
			// Empty atom / end
			return NullValue{Node: "NullValue", Value: nil, Lexeme: ""}, i, line
		}
		// Some other character that shouldn't start an atom
		sp.diagnostics.Add("L010_INVALID_ATOM", SeverityError, line, col, fmt.Sprintf("Atomo invalido empezando con '%c'.", rune(input[i])))
		return NullValue{}, i, line
	}

	// Collect atom characters
	for i < len(input) && isAtomChar(rune(input[i])) {
		i++
	}

	lexeme := input[atomStart:i]
	if len(lexeme) == 0 {
		return NullValue{Node: "NullValue", Value: nil, Lexeme: ""}, i, line
	}

	// Check microtokens
	// For now, just emit as AtomValue
	return AtomValue{
		Node:   "AtomValue",
		Value:  lexeme,
		Lexeme: lexeme,
	}, i, line
}

// parseList parses a flat list [...]
func (sp *ScalarParser) parseList(input string, line, col int) (ScalarValue, int, int) {
	if len(input) == 0 || input[0] != '[' {
		return NullValue{}, 0, line
	}

	i := 1 // skip [
	items := make([]ScalarValue, 0)

	// Skip leading whitespace
	for i < len(input) && (input[i] == ' ' || input[i] == '\t') {
		i++
	}

	// Empty list
	if i < len(input) && input[i] == ']' {
		lexeme := input[:i+1]
		return ListValue{
			Node:   "ListValue",
			Items:  items,
			Lexeme: lexeme,
		}, i + 1, line
	}

	for i < len(input) {
		// Parse value
		val, consumed, _ := sp.parseScalar(input[i:], line, col+i)
		if consumed == 0 {
			// Error or unexpected
			break
		}

		// Check it's not a list (no nested lists)
		if _, ok := val.(ListValue); ok {
			sp.diagnostics.Add("L008_NESTED_LIST", SeverityError, line, col+i, "Listas anidadas no permitidas en CORTEX 0.1.")
		}

		items = append(items, val)
		i += consumed

		// Skip whitespace
		for i < len(input) && (input[i] == ' ' || input[i] == '\t') {
			i++
		}

		// Check for comma
		if i < len(input) && input[i] == ',' {
			i++
			// Skip whitespace after comma
			for i < len(input) && (input[i] == ' ' || input[i] == '\t') {
				i++
			}
			continue
		}

		// Check for closing bracket
		if i < len(input) && input[i] == ']' {
			lexeme := input[:i+1]
			return ListValue{
				Node:   "ListValue",
				Items:  items,
				Lexeme: lexeme,
			}, i + 1, line
		}

		// Unexpected character
		sp.diagnostics.Add("L007_INVALID_LIST", SeverityError, line, col+i, fmt.Sprintf("Caracter inesperado en lista: '%c'.", rune(input[i])))
		break
	}

	// If we got here, list is malformed
	lexeme := input
	if len(lexeme) > i {
		lexeme = input[:i]
	}
	return ListValue{
		Node:   "ListValue",
		Items:  items,
		Lexeme: lexeme,
	}, i, line
}

// ApplyMicrotokens expands microtokens in the atom value
func (sp *ScalarParser) ApplyMicrotokens(val *AtomValue, micros map[string]string) {
	if val == nil || len(micros) == 0 {
		return
	}
}

// isAtomChar checks if a rune is a valid atom character
func isAtomChar(r rune) bool {
	return (r >= 'a' && r <= 'z') ||
		(r >= 'A' && r <= 'Z') ||
		(r >= '0' && r <= '9') ||
		r == '_' || r == '.' || r == '/' ||
		r == ':' || r == '@' || r == '+' ||
		r == '%' || r == '$' || r == '-'
}

// isIdentChar checks if a rune can continue a name/identifier
func isIdentChar(r rune) bool {
	return (r >= 'a' && r <= 'z') ||
		(r >= 'A' && r <= 'Z') ||
		(r >= '0' && r <= '9') ||
		r == '_' || r == '-' || r == '.'
}

// isPrintable checks if a rune is a printable Unicode character (no control chars except TAB)
func isPrintable(r rune) bool {
	return r == '\t' || r >= 32 && !unicode.IsControl(r)
}
