package cortex

import (
	"fmt"
	"regexp"
	"strings"
	"unicode/utf8"

	"golang.org/x/text/unicode/norm"
)

func ToNFC(s string) string     { return norm.NFC.String(s) }
func UTF8Bytes(s string) []byte { return []byte(s) }

type ParseError struct {
	Code    string `json:"code"`
	Message string `json:"message"`
	Line    int    `json:"line"`
	Col     int    `json:"col"`
}

func (e *ParseError) Error() string {
	return fmt.Sprintf("%s @ %d:%d — %s", e.Code, e.Line, e.Col, e.Message)
}

var (
	atomRE = regexp.MustCompile(`^(\$[0-9]+:)?[_A-Za-z][_A-Za-z0-9./:@+%$-]*$`)
	intRE  = regexp.MustCompile(`^-?(0|[1-9][0-9]*)$`)
	decRE  = regexp.MustCompile(`^-?(0|[1-9][0-9]*)\.[0-9]+$`)
)

func IsAtomLexeme(s string) bool {
	if s == "" || utf8.RuneCountInString(s) > 32 {
		return false
	}
	if strings.ContainsAny(s, " \t\r\n[]{}\",|") {
		return false
	}
	return atomRE.MatchString(s)
}

func ParseStringLiteral(s string) (string, error) {
	r := []rune(s)
	var out strings.Builder
	for i := 0; i < len(r); {
		c := r[i]
		if c == '\\' {
			if i+1 >= len(r) {
				return "", &ParseError{Code: "L005_INVALID_STRING", Message: "Trailing backslash in string"}
			}
			n := r[i+1]
			switch n {
			case '"':
				out.WriteRune('"')
			case '\\':
				out.WriteRune('\\')
			case 'n':
				out.WriteRune('\n')
			case 'r':
				out.WriteRune('\r')
			case 't':
				out.WriteRune('\t')
			case 'b':
				out.WriteRune('\b')
			case 'f':
				out.WriteRune('\f')
			case '/':
				out.WriteRune('/')
			case 'u':
				if i+5 >= len(r) {
					return "", &ParseError{Code: "L005_INVALID_STRING", Message: "Bad \\u escape"}
				}
				hex := string(r[i+2 : i+6])
				var v rune
				for _, h := range hex {
					v <<= 4
					switch {
					case h >= '0' && h <= '9':
						v += h - '0'
					case h >= 'a' && h <= 'f':
						v += h - 'a' + 10
					case h >= 'A' && h <= 'F':
						v += h - 'A' + 10
					default:
						return "", &ParseError{Code: "L005_INVALID_STRING", Message: "Bad \\u escape"}
					}
				}
				out.WriteRune(v)
				i += 6
				continue
			default:
				return "", &ParseError{Code: "L005_INVALID_STRING", Message: fmt.Sprintf("Unknown escape \\%c", n)}
			}
			i += 2
			continue
		}
		if c == '"' {
			return "", &ParseError{Code: "L005_INVALID_STRING", Message: "Unescaped quote in string body"}
		}
		out.WriteRune(c)
		i++
	}
	return out.String(), nil
}

func EmitStringLiteral(value string) string {
	var out strings.Builder
	out.WriteByte('"')
	for _, ch := range value {
		switch ch {
		case '"':
			out.WriteString(`\"`)
		case '\\':
			out.WriteString(`\\`)
		case '\n':
			out.WriteString(`\n`)
		case '\r':
			out.WriteString(`\r`)
		case '\t':
			out.WriteString(`\t`)
		case '\b':
			out.WriteString(`\b`)
		case '\f':
			out.WriteString(`\f`)
		default:
			if ch < 0x20 || ch == 0x7f {
				fmt.Fprintf(&out, `\u%04X`, ch)
			} else {
				out.WriteRune(ch)
			}
		}
	}
	out.WriteByte('"')
	return out.String()
}

type stringCursor struct {
	runes        []rune
	i, line, col int
}

func newCursor(s string, line, col int) *stringCursor {
	return &stringCursor{runes: []rune(s), line: line, col: col}
}
func (c *stringCursor) eof() bool { return c.i >= len(c.runes) }
func (c *stringCursor) peek(off ...int) rune {
	o := 0
	if len(off) > 0 {
		o = off[0]
	}
	j := c.i + o
	if j < 0 || j >= len(c.runes) {
		return 0
	}
	return c.runes[j]
}
func (c *stringCursor) next() rune {
	r := c.runes[c.i]
	c.i++
	if r == '\n' {
		c.line++
		c.col = 1
	} else {
		c.col++
	}
	return r
}
func (c *stringCursor) remainingFrom(start int) string { return string(c.runes[start:c.i]) }
func skipInlineWS(c *stringCursor) {
	for c.peek() == ' ' || c.peek() == '\t' {
		c.next()
	}
}

func parseScalar(c *stringCursor) (Scalar, error) {
	skipInlineWS(c)
	switch c.peek() {
	case '"':
		return parseStringScalar(c)
	case '[':
		return parseListScalar(c)
	default:
		return parseAtomOrNumber(c)
	}
}

func parseStringScalar(c *stringCursor) (Scalar, error) {
	c.next()
	var body strings.Builder
	for {
		r := c.peek()
		if r == 0 {
			return Scalar{}, &ParseError{Code: "L005_INVALID_STRING", Message: "Unterminated string", Line: c.line, Col: c.col}
		}
		if r == '"' {
			c.next()
			break
		}
		if r == '\\' {
			body.WriteRune(c.next())
			n := c.peek()
			if n == 0 {
				return Scalar{}, &ParseError{Code: "L005_INVALID_STRING", Message: "Trailing backslash", Line: c.line, Col: c.col}
			}
			body.WriteRune(c.next())
			if n == 'u' {
				for j := 0; j < 4; j++ {
					h := c.peek()
					if h == 0 {
						return Scalar{}, &ParseError{Code: "L005_INVALID_STRING", Message: "Bad \\u escape", Line: c.line, Col: c.col}
					}
					body.WriteRune(c.next())
				}
			}
		} else {
			body.WriteRune(c.next())
		}
	}
	v, err := ParseStringLiteral(body.String())
	if err != nil {
		return Scalar{}, err
	}
	return Scalar{Kind: ScalarString, Text: v, Lexeme: EmitStringLiteral(v)}, nil
}

func parseListScalar(c *stringCursor) (Scalar, error) {
	c.next()
	items := []Scalar{}
	skipInlineWS(c)
	if c.peek() == ']' {
		c.next()
		return Scalar{Kind: ScalarList, Items: items, Lexeme: "[]"}, nil
	}
	for {
		v, err := parseScalar(c)
		if err != nil {
			return Scalar{}, err
		}
		items = append(items, v)
		skipInlineWS(c)
		switch c.peek() {
		case ',':
			c.next()
			skipInlineWS(c)
		case ']':
			c.next()
			var b strings.Builder
			b.WriteByte('[')
			for i, it := range items {
				if i > 0 {
					b.WriteByte(',')
				}
				b.WriteString(it.Lexeme)
			}
			b.WriteByte(']')
			return Scalar{Kind: ScalarList, Items: items, Lexeme: b.String()}, nil
		default:
			return Scalar{}, &ParseError{Code: "L007_INVALID_LIST", Message: fmt.Sprintf("Expected , or ] got %q", c.peek()), Line: c.line, Col: c.col}
		}
	}
}

func parseAtomOrNumber(c *stringCursor) (Scalar, error) {
	start := c.i
	for {
		r := c.peek()
		if r == 0 || strings.ContainsRune(" \t\r\n,}]|", r) {
			break
		}
		c.next()
	}
	raw := string(c.runes[start:c.i])
	switch raw {
	case "true":
		return Scalar{Kind: ScalarBoolean, Bool: true, Lexeme: "true"}, nil
	case "false":
		return Scalar{Kind: ScalarBoolean, Bool: false, Lexeme: "false"}, nil
	case "null":
		return Scalar{Kind: ScalarNull, Lexeme: "null"}, nil
	}
	if intRE.MatchString(raw) {
		if raw == "-0" {
			raw = "0"
		}
		return Scalar{Kind: ScalarInteger, Text: raw, Lexeme: raw}, nil
	}
	if decRE.MatchString(raw) {
		return Scalar{Kind: ScalarDecimal, Text: raw, Lexeme: raw}, nil
	}
	if !atomRE.MatchString(raw) {
		return Scalar{}, &ParseError{Code: "L010_INVALID_ATOM", Message: fmt.Sprintf("Invalid atom: %q", raw), Line: c.line, Col: c.col}
	}
	return Scalar{Kind: ScalarAtom, Text: raw, Lexeme: raw}, nil
}

func ParseAttrsPayload(s string, startLine int) ([]Attr, error) {
	c := newCursor(s, startLine, 1)
	skipInlineWS(c)
	if c.peek() != '{' {
		return nil, &ParseError{Code: "S006_INVALID_ATTRS", Message: "Expected {", Line: c.line, Col: c.col}
	}
	c.next()
	attrs := []Attr{}
	skipInlineWS(c)
	if c.peek() == '}' {
		c.next()
		return attrs, nil
	}
	for {
		skipInlineWS(c)
		start := c.i
		for {
			r := c.peek()
			if r == 0 || r == ' ' || r == '\t' || r == ':' || r == ',' || r == '}' {
				break
			}
			c.next()
		}
		key := string(c.runes[start:c.i])
		if key == "" {
			return nil, &ParseError{Code: "L003_INVALID_KEY", Message: "Empty key", Line: c.line, Col: c.col}
		}
		skipInlineWS(c)
		if c.peek() != ':' {
			return nil, &ParseError{Code: "S006_INVALID_ATTRS", Message: "Expected : after key", Line: c.line, Col: c.col}
		}
		c.next()
		v, err := parseScalar(c)
		if err != nil {
			return nil, err
		}
		attrs = append(attrs, Attr{Key: key, Value: v})
		skipInlineWS(c)
		switch c.peek() {
		case ',':
			c.next()
			skipInlineWS(c)
			if c.peek() == '}' {
				c.next()
				return attrs, nil
			}
		case '}':
			c.next()
			return attrs, nil
		default:
			return nil, &ParseError{Code: "S006_INVALID_ATTRS", Message: fmt.Sprintf("Expected , or } got %q", c.peek()), Line: c.line, Col: c.col}
		}
	}
}
