package cortex

import (
	"fmt"
	"regexp"
	"strings"
)

var (
	envelopeV10RE = regexp.MustCompile(`<!--\s*HCORTEX\s+v=([0-9.]+)\s+t=(\w+)(?:\s+k=(\w+))?\s*-->`)
	glossaryV10RE = regexp.MustCompile(`(?s)<!--\s*glossary\s*-->\n(.*?)\n<!--\s*/glossary\s*-->`)
	hiddenV10RE   = regexp.MustCompile(`<!--\s*(cortex-ast:|base64:|payload-shadow:|shadow:|ast:|internal:)`)
	sectionHeadV10RE = regexp.MustCompile(`^##\s*§(\d+):\s*(.*?)\s*$`)
	schemaOpenV10RE  = regexp.MustCompile(`^<!--\s*schema:(\d+)(?:\s+capa:(\w+))?\s*-->$`)
	schemaCloseV10RE = regexp.MustCompile(`^<!--\s*/schema:\d+\s*-->$`)
	ideaMarkerRE  = regexp.MustCompile(`^### ([!]?(?:\w+::)?[!\w]+):([\w_-]+)\s*$`)
)

// CompileHCORTEX10 compiles an HCORTEX 1.0/0.2 document back to the AST.
func CompileHCORTEX10(text string) (*Document, []HDiagnostic) {
	diags := []HDiagnostic{}
	if strings.HasPrefix(text, "\ufeff") {
		return nil, []HDiagnostic{{Code: "H490", Severity: "error", Message: "BOM forbidden", Line: 1}}
	}
	text = normalizeLineEndings(text)
	if hiddenV10RE.MatchString(text) {
		return nil, []HDiagnostic{{Code: "H481_HIDDEN_COPY", Severity: "error", Message: "HCORTEX contains hidden CORTEX/AST copy", Line: 1}}
	}
	vm := envelopeV10RE.FindStringSubmatch(text)
	if vm == nil {
		return nil, []HDiagnostic{{Code: "H401_MISSING_ENVELOPE", Severity: "error", Message: "Missing or malformed HCORTEX envelope", Line: 1}}
	}
	version := vm[1]
	if version != "0.2" && version != "1.0" {
		return nil, []HDiagnostic{{Code: "H401_UNSUPPORTED_HCORTEX_VERSION", Severity: "error", Message: "Unsupported HCORTEX version: " + version, Line: 1}}
	}
	gm := glossaryV10RE.FindStringSubmatch(text)
	if gm == nil {
		return nil, []HDiagnostic{{Code: "H403_MISSING_GLOSSARY_BLOCK", Severity: "error", Message: "Missing glossary block", Line: 1}}
	}
	doc, err := ParseV10(strings.TrimSpace(gm[1])+"\n", version)
	if err != nil {
		code := "S999"
		if pe, ok := err.(*ParseError); ok {
			code = pe.Code
		}
		return nil, []HDiagnostic{{Code: code, Severity: "error", Message: "Glossary parse failed: " + err.Error(), Line: 1}}
	}
	doc.CortexVersion = version
	symLookup := map[string]*SymbolDef{}
	for i := range doc.Glossary.Symbols {
		s := &doc.Glossary.Symbols[i]
		symLookup[s.Namespace+"\x00"+s.Sigil] = s
	}
	for _, sec := range iterSectionsV10(text) {
		var titlePtr *string
		if sec.title != fmt.Sprintf("Sección %d", sec.id) {
			t := sec.title
			titlePtr = &t
		}
		section := Section{ID: sec.id, Title: titlePtr, Capa: sec.capa}
		if strings.TrimSpace(sec.body) != "" {
			section.Ideas = parseIdeasV10(sec.body, sec.id, symLookup)
		}
		doc.Sections = append(doc.Sections, section)
	}
	return doc, diags
}

type sectionChunk struct {
	id    int
	title string
	capa  string
	body  string
}

func iterSectionsV10(text string) []sectionChunk {
	lines := strings.Split(text, "\n")
	fenced := fenceMask(lines)
	out := []sectionChunk{}
	i := 0
	for i < len(lines) {
		var m []string
		if !fenced[i] {
			m = sectionHeadV10RE.FindStringSubmatch(lines[i])
		}
		if m != nil && i+2 < len(lines) && strings.TrimSpace(lines[i+1]) == "" {
			sm := schemaOpenV10RE.FindStringSubmatch(lines[i+2])
			if sm != nil {
				j := i + 3
				for j < len(lines) {
					if !fenced[j] && schemaCloseV10RE.MatchString(lines[j]) {
						break
					}
					j++
				}
				if j < len(lines) {
					out = append(out, sectionChunk{id: atoi(m[1]), title: strings.TrimSpace(m[2]), capa: sm[2], body: strings.Join(lines[i+3:j], "\n")})
					i = j + 1
					continue
				}
			}
		}
		i++
	}
	return out
}

func fenceMask(lines []string) []bool {
	mask := make([]bool, len(lines))
	i := 0
	for i < len(lines) {
		if strings.HasPrefix(strings.TrimLeft(lines[i], " \t"), "```") {
			j := i + 1
			for j < len(lines) && !strings.HasPrefix(strings.TrimLeft(lines[j], " \t"), "```") {
				j++
			}
			if j < len(lines) {
				for k := i; k <= j; k++ {
					mask[k] = true
				}
				i = j + 1
				continue
			}
		}
		i++
	}
	return mask
}

type markerPos struct {
	line      int
	qualified string
	name      string
}

func parseIdeasV10(body string, sectionID int, symLookup map[string]*SymbolDef) []Idea {
	lines := strings.Split(body, "\n")
	fenced := fenceMask(lines)
	markers := []markerPos{}
	for i, line := range lines {
		if fenced[i] {
			continue
		}
		if m := ideaMarkerRE.FindStringSubmatch(line); m != nil {
			markers = append(markers, markerPos{line: i, qualified: m[1], name: m[2]})
		}
	}
	ideas := []Idea{}
	for idx, mk := range markers {
		end := len(lines)
		if idx+1 < len(markers) {
			end = markers[idx+1].line
		}
		rest := strings.TrimSpace(strings.Join(lines[mk.line+1:end], "\n"))
		ns, sigil := "", mk.qualified
		if strings.Contains(mk.qualified, "::") {
			parts := strings.SplitN(mk.qualified, "::", 2)
			ns, sigil = parts[0], parts[1]
		}
		sym := symLookup[ns+"\x00"+sigil]
		if sym == nil {
			sym = symLookup["\x00"+sigil]
		}
		shape := "attrs"
		encoding := ""
		if sym != nil {
			shape = sym.Shape
			encoding = sym.Encoding
		}
		rows, order := parseTableRowsV10(rest)
		if len(rows) > 0 && !(sym != nil && (shape == "bloque" || shape == "cuerpo")) {
			switch {
			case encoding == "slots" && sym != nil:
				fvs := []FieldValue{}
				for _, f := range sym.Contract {
					col := rows[0][f.Name]
					if col != "" {
						fvs = append(fvs, FieldValue{Position: f.Position, Name: f.Name, Type: f.Type, Required: f.Required, Value: makeScalarCell(col)})
					}
				}
				if len(fvs) > 0 {
					ideas = append(ideas, Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: mk.name, Shape: "attrs", SlotValues: fvs, SlotEncoded: true})
				}
			case sym != nil && shape == "cuerpo":
				ideas = append(ideas, Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: mk.name, Shape: "cuerpo", Body: rest})
			case sym != nil && shape == "bloque":
				ideas = append(ideas, Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: mk.name, Shape: "bloque", Body: extractFence(rest)})
			case sym != nil && (shape == "attrs-pos" || shape == "relacion"):
				cells := []Scalar{}
				for _, f := range sym.Contract {
					val := rows[0][f.Name]
					if val == "" && !f.Required {
						break
					}
					cells = append(cells, makeScalarCell(val))
				}
				ideas = append(ideas, Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: mk.name, Shape: shape, Cells: cells})
			default:
				attrs := []Attr{}
				for _, hdr := range order {
					attrs = append(attrs, Attr{Key: hdr, Value: makeScalarCell(rows[0][hdr])})
				}
				ideas = append(ideas, Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: mk.name, Shape: "attrs", Attrs: attrs})
			}
		} else {
			if sym != nil && shape == "cuerpo" {
				ideas = append(ideas, Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: mk.name, Shape: "cuerpo", Body: rest})
			} else if sym != nil && shape == "bloque" {
				ideas = append(ideas, Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: mk.name, Shape: "bloque", Body: extractFence(rest)})
			} else {
				ideas = append(ideas, Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: mk.name, Shape: shape, Attrs: []Attr{}})
			}
		}
	}
	return ideas
}

func extractFence(rest string) string {
	re := regexp.MustCompile("(?s)```\\s*\n(.*?)```")
	if m := re.FindStringSubmatch(rest); m != nil {
		return strings.TrimSpace(m[1])
	}
	return rest
}

func parseTableRowsV10(text string) ([]map[string]string, []string) {
	lines := []string{}
	for _, ln := range strings.Split(text, "\n") {
		if strings.TrimSpace(ln) != "" {
			lines = append(lines, strings.TrimSpace(ln))
		}
	}
	table := []string{}
	for _, ln := range lines {
		if strings.HasPrefix(ln, "|") && strings.HasSuffix(ln, "|") {
			table = append(table, ln)
		}
	}
	if len(table) < 2 {
		return nil, nil
	}
	headers := splitTableRow(table[0])
	var data []string
	for _, ln := range table[1:] {
		cells := splitTableRow(ln)
		sep := true
		for _, c := range cells {
			if c != "" && strings.Trim(c, "-:") != "" {
				sep = false
				break
			}
		}
		if sep {
			continue
		}
		data = cells
		break
	}
	if data == nil {
		return nil, nil
	}
	row := map[string]string{}
	for i, h := range headers {
		if i < len(data) {
			row[h] = data[i]
		} else {
			row[h] = ""
		}
	}
	return []map[string]string{row}, headers
}

func splitTableRow(line string) []string {
	s := strings.TrimSpace(line)
	s = strings.TrimPrefix(s, "|")
	s = strings.TrimSuffix(s, "|")
	cells := []string{}
	var buf strings.Builder
	inQuotes := false
	escaped := false
	for _, ch := range s {
		switch {
		case escaped:
			buf.WriteRune(ch)
			escaped = false
		case ch == '\\' && inQuotes:
			buf.WriteRune(ch)
			escaped = true
		case ch == '"':
			inQuotes = !inQuotes
			buf.WriteRune(ch)
		case ch == '|' && !inQuotes:
			cells = append(cells, strings.TrimSpace(buf.String()))
			buf.Reset()
		default:
			buf.WriteRune(ch)
		}
	}
	cells = append(cells, strings.TrimSpace(buf.String()))
	return cells
}

func makeScalarCell(lex string) Scalar {
	lex = strings.TrimSpace(lex)
	if lex == "" {
		return Scalar{Kind: ScalarNull, Lexeme: "null"}
	}
	if strings.HasPrefix(lex, `"`) && strings.HasSuffix(lex, `"`) && len(lex) >= 2 {
		inner, err := ParseStringLiteral(lex[1 : len(lex)-1])
		if err == nil {
			return Scalar{Kind: ScalarString, Text: inner, Lexeme: EmitStringLiteral(inner)}
		}
	}
	if lex == "true" {
		return Scalar{Kind: ScalarBoolean, Bool: true, Lexeme: "true"}
	}
	if lex == "false" {
		return Scalar{Kind: ScalarBoolean, Bool: false, Lexeme: "false"}
	}
	if lex == "null" {
		return Scalar{Kind: ScalarNull, Lexeme: "null"}
	}
	if strings.HasPrefix(lex, "[") && strings.HasSuffix(lex, "]") {
		inner := strings.TrimSpace(lex[1 : len(lex)-1])
		if inner == "" {
			return Scalar{Kind: ScalarList, Items: []Scalar{}, Lexeme: "[]"}
		}
		parts := strings.Split(inner, ",")
		items := make([]Scalar, 0, len(parts))
		for _, p := range parts {
			items = append(items, makeScalarCell(p))
		}
		lexemes := make([]string, len(items))
		for i := range items {
			lexemes[i] = items[i].Lexeme
		}
		return Scalar{Kind: ScalarList, Items: items, Lexeme: "[" + strings.Join(lexemes, ",") + "]"}
	}
	return classifyRawCell(lex)
}
