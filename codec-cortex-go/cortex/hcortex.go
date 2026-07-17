package cortex

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
)

var shapeSchema = map[string]string{"attrs": "table", "attrs-pos": "table", "cuerpo": "prose", "bloque": "diagram", "relacion": "table"}

type HDiagnostic struct {
	Code     string `json:"code"`
	Severity string `json:"severity"`
	Message  string `json:"message"`
	Line     int    `json:"line"`
}

func RenderHCORTEX(doc *Document) (string, error) {
	if doc == nil {
		return "", fmt.Errorf("nil document")
	}
	out := []string{"<!-- HCORTEX v=0.1 t=canonical -->", ""}
	if g := renderGlossaryBlock(doc); g != "" {
		out = append(out, g, "")
	}
	for _, sec := range doc.Sections {
		if sec.Title == nil {
			out = append(out, fmt.Sprintf("## §%d: Sección %d", sec.ID, sec.ID))
		} else {
			out = append(out, fmt.Sprintf("## §%d: %s", sec.ID, *sec.Title))
		}
		out = append(out, "")
		if len(sec.Ideas) == 0 {
			continue
		}
		schema := determineSectionSchema(sec)
		out = append(out, fmt.Sprintf("<!-- %s:%d -->", schema, sec.ID))
		for _, idea := range sec.Ideas {
			sym := doc.FindSymbol(idea.Namespace, idea.Symbol)
			if sym == nil {
				return "", fmt.Errorf("symbol not found for %s", idea.QualifiedSymbol())
			}
			renderIdeaCompact(idea, sym, schema, &out)
		}
		out = append(out, fmt.Sprintf("<!-- /%s:%d -->", schema, sec.ID), "")
	}
	return strings.Join(out, "\n") + "\n", nil
}

func determineSectionSchema(sec Section) string {
	m := map[string]bool{}
	for _, i := range sec.Ideas {
		m[i.Shape] = true
	}
	if len(m) == 1 {
		for sh := range m {
			if s, ok := shapeSchema[sh]; ok {
				return s
			}
		}
	}
	return "prose"
}

func renderGlossaryBlock(doc *Document) string {
	entries := []string{}
	if f := doc.Glossary.Format; f != nil {
		parts := make([]string, len(f.Attrs))
		for i, a := range f.Attrs {
			parts[i] = a.Key + ":" + a.Value.Lexeme
		}
		entries = append(entries, "$0:format{"+strings.Join(parts, ",")+"}")
	}
	for _, e := range doc.Glossary.Enums {
		entries = append(entries, "$0:enum_"+e.Name+"{values:"+EmitStringLiteral(strings.Join(e.Values, "|"))+"}")
	}
	for _, m := range doc.Glossary.Micros {
		lex := m.Expand
		if atomRE.MatchString(lex) && !strings.Contains(lex, " ") {
			entries = append(entries, "$0:micro_"+m.Token+"{expand:"+lex+"}")
		} else {
			entries = append(entries, "$0:micro_"+m.Token+"{expand:"+EmitStringLiteral(lex)+"}")
		}
	}
	for _, n := range doc.Glossary.Namespaces {
		entries = append(entries, "$0:namespace_"+n.Alias+emitGlossaryAttrs(n.Attrs))
	}
	for _, e := range doc.Glossary.Extensions {
		entries = append(entries, "$0:extension_"+e.Name+emitGlossaryAttrs(e.Attrs))
	}
	for _, m := range doc.Glossary.Meta {
		entries = append(entries, "$0:"+m.Name+emitGlossaryAttrs(m.Attrs))
	}
	for _, s := range doc.Glossary.Symbols {
		entries = append(entries, s.Qualified()+":"+s.Label+emitGlossaryAttrs(s.Attrs))
	}
	if len(entries) == 0 {
		return ""
	}
	return "<!-- glossary\n" + strings.Join(entries, "\n") + "\n-->"
}

func renderIdeaCompact(idea Idea, sym *SymbolDef, schema string, out *[]string) {
	q := idea.QualifiedSymbol()
	switch schema {
	case "table":
		vals := extractIdeaValues(idea, sym)
		*out = append(*out, fmt.Sprintf("<!-- %s:%s --> | %s |", q, idea.Name, strings.Join(vals, " | ")))
	case "prose":
		switch idea.Shape {
		case "cuerpo":
			*out = append(*out, fmt.Sprintf("<!-- %s:%s -->", q, idea.Name))
			if idea.Body != "" {
				*out = append(*out, strings.Split(ToNFC(idea.Body), "\n")...)
			}
		case "attrs":
			parts := make([]string, len(idea.Attrs))
			for i, a := range idea.Attrs {
				parts[i] = a.Key + ":" + a.Value.Lexeme
			}
			*out = append(*out, fmt.Sprintf("<!-- %s:%s --> %s", q, idea.Name, strings.Join(parts, ",")))
		case "attrs-pos", "relacion":
			parts := make([]string, len(idea.Cells))
			for i, c := range idea.Cells {
				parts[i] = c.Lexeme
			}
			*out = append(*out, fmt.Sprintf("<!-- %s:%s --> %s", q, idea.Name, strings.Join(parts, "|")))
		default:
			*out = append(*out, fmt.Sprintf("<!-- %s:%s -->", q, idea.Name))
		}
	case "list":
		content := "idea"
		switch idea.Shape {
		case "attrs":
			p := make([]string, len(idea.Attrs))
			for i, a := range idea.Attrs {
				p[i] = a.Key + ":" + a.Value.Lexeme
			}
			content = strings.Join(p, ",")
		case "attrs-pos", "relacion":
			p := make([]string, len(idea.Cells))
			for i, c := range idea.Cells {
				p[i] = c.Lexeme
			}
			content = strings.Join(p, "|")
		case "cuerpo":
			content = ToNFC(idea.Body)
		}
		*out = append(*out, fmt.Sprintf("<!-- %s:%s --> - **%s**", q, idea.Name, content))
	case "check":
		content := "idea"
		switch idea.Shape {
		case "attrs":
			p := make([]string, len(idea.Attrs))
			for i, a := range idea.Attrs {
				p[i] = a.Key + ":" + a.Value.Lexeme
			}
			content = strings.Join(p, ",")
		case "attrs-pos", "relacion":
			p := make([]string, len(idea.Cells))
			for i, c := range idea.Cells {
				p[i] = c.Lexeme
			}
			content = strings.Join(p, "|")
		case "cuerpo":
			content = ToNFC(idea.Body)
		}
		*out = append(*out, fmt.Sprintf("<!-- %s:%s --> - [ ] %s", q, idea.Name, content))
	case "diagram":
		*out = append(*out, fmt.Sprintf("<!-- %s:%s -->", q, idea.Name))
		if idea.Body != "" {
			*out = append(*out, "```puml")
			*out = append(*out, strings.Split(idea.Body, "\n")...)
			*out = append(*out, "```")
		}
	}
}
func extractIdeaValues(idea Idea, sym *SymbolDef) []string {
	switch idea.Shape {
	case "attrs":
		m := map[string]Scalar{}
		for _, a := range idea.Attrs {
			m[a.Key] = a.Value
		}
		out := []string{}
		for _, f := range sym.Contract {
			if v, ok := m[f.Name]; ok {
				out = append(out, v.Lexeme)
			}
		}
		return out
	case "attrs-pos", "relacion":
		out := make([]string, len(idea.Cells))
		for i, c := range idea.Cells {
			out[i] = c.Lexeme
		}
		return out
	case "cuerpo", "bloque":
		return []string{idea.Body}
	default:
		return []string{""}
	}
}

var hcHeaderRE = regexp.MustCompile(`<!-- HCORTEX v=[\d.]+ t=\w+ -->`)
var sectionHeadingRE = regexp.MustCompile(`^## §(\d+):\s*(.*)$`)
var schemaOpenRE = regexp.MustCompile(`^<!-- (\w+):(\d+) -->$`)
var schemaCloseRE = regexp.MustCompile(`^<!-- /\w+:\d+ -->$`)
var markerRE = regexp.MustCompile(`<!-- ([!]?[_A-Za-z0-9:]+):([_A-Za-z0-9-]+) -->`)

func CompileHCORTEX(text string) (*Document, []HDiagnostic) {
	diags := []HDiagnostic{}
	if strings.HasPrefix(text, "\ufeff") {
		return nil, []HDiagnostic{{Code: "H490", Severity: "error", Message: "BOM forbidden", Line: 1}}
	}
	text = normalizeLineEndings(text)
	if !hcHeaderRE.MatchString(text) {
		return nil, []HDiagnostic{{Code: "H400", Severity: "error", Message: "Missing HCORTEX header", Line: 1}}
	}

	doc := NewDocument()
	registry := map[string]sigilInfo{}
	if start := strings.Index(text, "<!-- glossary\n"); start >= 0 {
		bodyStart := start + len("<!-- glossary\n")
		if endRel := strings.Index(text[bodyStart:], "\n-->"); endRel >= 0 {
			parseGlossaryFromBlock(text[bodyStart:bodyStart+endRel], doc, registry, &diags)
		}
	} else {
		doc.Glossary.Format = &FormatDecl{
			Cortex:   "0.1",
			Encoding: "UTF-8",
			Attrs: []Attr{
				{Key: "cortex", Value: Scalar{Kind: ScalarAtom, Text: "0.1", Lexeme: "0.1"}},
				{Key: "encoding", Value: Scalar{Kind: ScalarAtom, Text: "UTF-8", Lexeme: "UTF-8"}},
			},
		}
	}

	body := hcHeaderRE.ReplaceAllString(text, "")
	if start := strings.Index(body, "<!-- glossary\n"); start >= 0 {
		bodyStart := start + len("<!-- glossary\n")
		if endRel := strings.Index(body[bodyStart:], "\n-->"); endRel >= 0 {
			end := bodyStart + endRel + len("\n-->")
			body = body[:start] + body[end:]
		}
	}

	lines := strings.Split(body, "\n")
	for i := 0; i < len(lines); i++ {
		hm := sectionHeadingRE.FindStringSubmatch(strings.TrimSpace(lines[i]))
		if hm == nil {
			continue
		}
		sid, _ := strconv.Atoi(hm[1])
		title := strings.TrimSpace(hm[2])
		j := i + 1
		for j < len(lines) && strings.TrimSpace(lines[j]) == "" {
			j++
		}
		if j >= len(lines) {
			continue
		}
		om := schemaOpenRE.FindStringSubmatch(strings.TrimSpace(lines[j]))
		if om == nil {
			continue
		}
		schema := om[1]
		contentStart := j + 1
		k := contentStart
		for k < len(lines) && !schemaCloseRE.MatchString(strings.TrimSpace(lines[k])) {
			k++
		}
		if k >= len(lines) {
			continue
		}
		content := strings.Join(lines[contentStart:k], "\n")
		t := title
		sec := Section{ID: sid, Title: &t}
		if strings.TrimSpace(content) != "" {
			sec.Ideas = parseSchemaContent(content, schema, registry, sid, &diags)
		}
		doc.Sections = append(doc.Sections, sec)
		i = k
	}
	return doc, diags
}

type sigilInfo struct {
	Shape  string
	Fields []string
	Focus  string
	Open   bool
}

func parseGlossaryFromBlock(body string, doc *Document, registry map[string]sigilInfo, diags *[]HDiagnostic) {
	for _, raw := range strings.Split(body, "\n") {
		line := strings.TrimSpace(raw)
		if line == "" {
			continue
		}
		switch {
		case strings.HasPrefix(line, "$0:format{"):
			inner := line[strings.Index(line, "{")+1:]
			if strings.HasSuffix(inner, "}") {
				inner = inner[:len(inner)-1]
			}
			doc.Glossary.Format = &FormatDecl{Cortex: "0.1", Encoding: "UTF-8", Attrs: classifyAttrs(parseCompactAttrs(inner))}

		case strings.HasPrefix(line, "$0:enum_"):
			if name, inner, ok := extractNamedDecl(line, "$0:enum_"); ok {
				vals := ""
				for _, a := range parseCompactAttrs(inner) {
					if a.Key == "values" {
						vals = a.Value
					}
				}
				if strings.HasPrefix(vals, "\"") && strings.HasSuffix(vals, "\"") {
					if v, err := ParseStringLiteral(vals[1 : len(vals)-1]); err == nil {
						vals = v
					}
				}
				doc.Glossary.Enums = append(doc.Glossary.Enums, EnumDecl{Name: name, Values: strings.Split(vals, "|")})
			}

		case strings.HasPrefix(line, "$0:micro_"):
			if token, inner, ok := extractNamedDecl(line, "$0:micro_"); ok {
				expand := ""
				for _, a := range parseCompactAttrs(inner) {
					if a.Key == "expand" {
						expand = a.Value
					}
				}
				if strings.HasPrefix(expand, "\"") && strings.HasSuffix(expand, "\"") {
					if v, err := ParseStringLiteral(expand[1 : len(expand)-1]); err == nil {
						expand = v
					}
				}
				doc.Glossary.Micros = append(doc.Glossary.Micros, MicroDecl{Token: token, Expand: expand})
			}

		case strings.HasPrefix(line, "$0:namespace_"):
			if name, inner, ok := extractNamedDecl(line, "$0:namespace_"); ok {
				doc.Glossary.Namespaces = append(doc.Glossary.Namespaces, NamespaceDecl{Alias: name, Attrs: classifyAttrs(parseCompactAttrs(inner))})
			}

		case strings.HasPrefix(line, "$0:extension_"):
			if name, inner, ok := extractNamedDecl(line, "$0:extension_"); ok {
				doc.Glossary.Extensions = append(doc.Glossary.Extensions, ExtensionDecl{Name: name, Attrs: classifyAttrs(parseCompactAttrs(inner))})
			}

		case strings.HasPrefix(line, "$0:"):
			if name, inner, ok := extractNamedDecl(line, "$0:"); ok {
				doc.Glossary.Meta = append(doc.Glossary.Meta, MetaDecl{Name: name, Attrs: classifyAttrs(parseCompactAttrs(inner))})
			}

		default:
			brace := strings.LastIndex(line, "{")
			if brace < 0 || !strings.HasSuffix(line, "}") {
				continue
			}
			head := line[:brace]
			inner := line[brace+1 : len(line)-1]
			m := symbolHeadRE.FindStringSubmatch(head)
			if m == nil {
				continue
			}
			ns, sigil, label := m[2], m[3], m[4]
			sym, err := buildSymbolDef(ns, sigil, label, classifyAttrs(parseCompactAttrs(inner)), 0)
			if err == nil {
				doc.Glossary.Symbols = append(doc.Glossary.Symbols, sym)
				fields := make([]string, len(sym.Contract))
				for i, f := range sym.Contract {
					fields[i] = f.Name
				}
				registry[strings.ToLower(sigil)] = sigilInfo{Shape: sym.Shape, Fields: fields, Focus: sym.Focus, Open: sym.Open}
			}
		}
	}
}

func extractNamedDecl(line, prefix string) (string, string, bool) {
	rest := strings.TrimPrefix(line, prefix)
	brace := strings.Index(rest, "{")
	if brace < 1 || !strings.HasSuffix(rest, "}") {
		return "", "", false
	}
	name := rest[:brace]
	var pattern string
	if prefix == "$0:namespace_" || prefix == "$0:extension_" {
		pattern = `^[a-z][a-z0-9_.-]*$`
	} else {
		pattern = `^\w+$`
	}
	ok, _ := regexp.MatchString(pattern, name)
	if !ok {
		return "", "", false
	}
	return name, rest[brace+1 : len(rest)-1], true
}

func parseSchemaContent(content, schema string, registry map[string]sigilInfo, sectionID int, diags *[]HDiagnostic) []Idea {
	locs := markerRE.FindAllStringSubmatchIndex(content, -1)
	ideas := []Idea{}
	listRE := regexp.MustCompile(`-\s+\*\*(.*?)\*\*`)
	checkRE := regexp.MustCompile(`-\s+\[[ x]\]\s+(.*)`)
	diagramRE := regexp.MustCompile("(?s)```puml\\s*\\n(.*?)```")

	for idx, loc := range locs {
		sigil := content[loc[2]:loc[3]]
		name := content[loc[4]:loc[5]]
		start := loc[1]
		end := len(content)
		if idx+1 < len(locs) {
			end = locs[idx+1][0]
		}
		body := strings.TrimSpace(content[start:end])
		key := strings.ToLower(sigil)
		if x := strings.LastIndex(key, "::"); x >= 0 {
			key = key[x+2:]
		}
		info, ok := registry[key]
		shape := "attrs"
		fields := []string{}
		if ok {
			shape, fields = info.Shape, info.Fields
		}
		ns, short := "", sigil
		if x := strings.Index(sigil, "::"); x >= 0 {
			ns, short = sigil[:x], sigil[x+2:]
		}
		idea := Idea{Section: sectionID, Namespace: ns, Symbol: short, Name: name, Shape: shape}

		switch schema {
		case "table":
			row := strings.TrimSpace(body)
			row = strings.TrimPrefix(row, "|")
			row = strings.TrimSuffix(row, "|")
			cells := splitPipeCells(strings.TrimSpace(row))
			if shape == "attrs-pos" || shape == "relacion" {
				for _, cell := range cells {
					idea.Cells = append(idea.Cells, classifyCompactValue(strings.TrimSpace(cell)))
				}
			} else {
				idea.Shape = "attrs"
				for i, cell := range cells {
					field := fmt.Sprintf("f%d", i+1)
					if i < len(fields) {
						field = fields[i]
					}
					idea.Attrs = append(idea.Attrs, Attr{Key: field, Value: classifyCompactValue(strings.TrimSpace(cell))})
				}
			}

		case "prose":
			if shape == "cuerpo" || shape == "bloque" {
				idea.Body = body
			} else if shape == "attrs-pos" || shape == "relacion" {
				for _, cell := range strings.Split(body, "|") {
					cell = strings.TrimSpace(cell)
					if cell != "" {
						idea.Cells = append(idea.Cells, classifyCompactValue(cell))
					}
				}
			} else {
				idea.Shape = "attrs"
				idea.Attrs = classifyAttrs(parseCompactAttrs(body))
			}

		case "list":
			item := body
			if m := listRE.FindStringSubmatch(body); m != nil {
				item = m[1]
			}
			idea.Shape = "attrs"
			idea.Attrs = classifyAttrs(parseCompactAttrs(item))
			if len(idea.Attrs) == 0 {
				idea.Attrs = []Attr{{Key: "content", Value: Scalar{Kind: ScalarString, Text: item, Lexeme: EmitStringLiteral(item)}}}
			}

		case "check":
			item := body
			if m := checkRE.FindStringSubmatch(body); m != nil {
				item = m[1]
			}
			idea.Shape = "attrs"
			idea.Attrs = classifyAttrs(parseCompactAttrs(item))
			if len(idea.Attrs) == 0 {
				idea.Attrs = []Attr{{Key: "content", Value: Scalar{Kind: ScalarString, Text: item, Lexeme: EmitStringLiteral(item)}}}
			}

		case "diagram":
			idea.Shape = "bloque"
			if m := diagramRE.FindStringSubmatch(body); m != nil {
				idea.Body = strings.TrimSpace(m[1])
			} else {
				idea.Body = body
			}
		}
		ideas = append(ideas, idea)
	}
	return ideas
}

type rawAttr struct{ Key, Value string }

func parseCompactAttrs(s string) []rawAttr {
	out := []rawAttr{}
	if s == "" {
		return out
	}
	i := 0
	for i < len(s) {
		for i < len(s) && (s[i] == ' ' || s[i] == ',') {
			i++
		}
		if i >= len(s) {
			break
		}
		ks := i
		for i < len(s) && s[i] != ':' && s[i] != ',' {
			i++
		}
		key := strings.TrimSpace(s[ks:i])
		if i >= len(s) || s[i] != ':' {
			break
		}
		i++
		val := ""
		if i < len(s) && s[i] == '"' {
			i++
			var b strings.Builder
			for i < len(s) {
				if s[i] == '\\' && i+1 < len(s) {
					b.WriteByte(s[i+1])
					i += 2
				} else if s[i] == '"' {
					i++
					break
				} else {
					b.WriteByte(s[i])
					i++
				}
			}
			val = "\"" + b.String() + "\""
		} else if i < len(s) && s[i] == '[' {
			depth := 1
			start := i
			i++
			for i < len(s) && depth > 0 {
				if s[i] == '[' {
					depth++
				} else if s[i] == ']' {
					depth--
				}
				i++
			}
			val = s[start:i]
		} else {
			vs := i
			for i < len(s) && s[i] != ',' && s[i] != '}' {
				i++
			}
			val = strings.TrimSpace(s[vs:i])
		}
		out = append(out, rawAttr{Key: key, Value: val})
	}
	return out
}
func classifyAttrs(in []rawAttr) []Attr {
	out := make([]Attr, len(in))
	for i, a := range in {
		out[i] = Attr{Key: a.Key, Value: classifyCompactValue(a.Value)}
	}
	return out
}
func classifyCompactValue(lex string) Scalar {
	lex = strings.TrimSpace(lex)
	if strings.HasPrefix(lex, "\"") && strings.HasSuffix(lex, "\"") {
		v, err := ParseStringLiteral(lex[1 : len(lex)-1])
		if err == nil {
			return Scalar{Kind: ScalarString, Text: v, Lexeme: EmitStringLiteral(v)}
		}
	}
	if strings.HasPrefix(lex, "[") && strings.HasSuffix(lex, "]") {
		inner := lex[1 : len(lex)-1]
		if inner == "" {
			return Scalar{Kind: ScalarList, Items: []Scalar{}, Lexeme: "[]"}
		}
		parts := splitCommaTop(inner)
		items := make([]Scalar, len(parts))
		lx := make([]string, len(parts))
		for i, p := range parts {
			items[i] = classifyCompactValue(p)
			lx[i] = items[i].Lexeme
		}
		return Scalar{Kind: ScalarList, Items: items, Lexeme: "[" + strings.Join(lx, ",") + "]"}
	}
	switch lex {
	case "true":
		return Scalar{Kind: ScalarBoolean, Bool: true, Lexeme: "true"}
	case "false":
		return Scalar{Kind: ScalarBoolean, Bool: false, Lexeme: "false"}
	case "null":
		return Scalar{Kind: ScalarNull, Lexeme: "null"}
	}
	if intRE.MatchString(lex) {
		if lex == "-0" {
			lex = "0"
		}
		return Scalar{Kind: ScalarInteger, Text: lex, Lexeme: lex}
	}
	if decRE.MatchString(lex) {
		return Scalar{Kind: ScalarDecimal, Text: lex, Lexeme: lex}
	}
	if atomRE.MatchString(lex) && !strings.Contains(lex, " ") {
		return Scalar{Kind: ScalarAtom, Text: lex, Lexeme: lex}
	}
	return Scalar{Kind: ScalarString, Text: lex, Lexeme: EmitStringLiteral(lex)}
}
func splitPipeCells(s string) []string {
	out := []string{}
	var b strings.Builder
	for i := 0; i < len(s); {
		if s[i] == '\\' && i+1 < len(s) && s[i+1] == '|' {
			b.WriteString(`\|`)
			i += 2
		} else if s[i] == '|' {
			out = append(out, strings.TrimSpace(b.String()))
			b.Reset()
			i++
		} else {
			b.WriteByte(s[i])
			i++
		}
	}
	out = append(out, strings.TrimSpace(b.String()))
	return out
}
func splitCommaTop(s string) []string {
	out := []string{}
	var b strings.Builder
	depth := 0
	inStr, esc := false, false
	for _, ch := range s {
		if inStr {
			b.WriteRune(ch)
			if esc {
				esc = false
			} else if ch == '\\' {
				esc = true
			} else if ch == '"' {
				inStr = false
			}
			continue
		}
		switch ch {
		case '"':
			inStr = true
			b.WriteRune(ch)
		case '[', '{', '(':
			depth++
			b.WriteRune(ch)
		case ']', '}', ')':
			depth--
			b.WriteRune(ch)
		case ',':
			if depth == 0 {
				out = append(out, strings.TrimSpace(b.String()))
				b.Reset()
			} else {
				b.WriteRune(ch)
			}
		default:
			b.WriteRune(ch)
		}
	}
	if b.Len() > 0 {
		out = append(out, strings.TrimSpace(b.String()))
	}
	return out
}
