package cortex

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
)

var (
	sectionBareRE  = regexp.MustCompile(`^\$([0-9]+)([ \t]+(.*))?$`)
	sectionColonRE = regexp.MustCompile(`^\$([1-9][0-9]*):[ \t]+(.*)$`)
	glossaryDeclRE = regexp.MustCompile(`^(([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):`)
	symbolHeadRE   = regexp.MustCompile(`^(([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):(.+)$`)
	ideaHeadRE     = regexp.MustCompile(`^(([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):([^\{\|\}\s]+)`)
)

func normalizeLineEndings(s string) string {
	s = strings.ReplaceAll(s, "\r\n", "\n")
	return strings.ReplaceAll(s, "\r", "\n")
}

func ParseContractFields(s string) ([]ContractField, error) {
	parts := strings.Split(s, "|")
	out := make([]ContractField, 0, len(parts))
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part == "" {
			return nil, &ParseError{Code: "G008_INVALID_CONTRACT", Message: fmt.Sprintf("Empty contract field in %q", s)}
		}
		required := true
		if strings.Contains(part, "?") {
			required = false
			part = part[:len(part)-1]
		}
		name, typ := part, "any"
		if idx := strings.Index(part, ":"); idx >= 0 {
			name, typ = part[:idx], part[idx+1:]
		}
		out = append(out, ContractField{Name: strings.TrimSpace(name), Type: strings.TrimSpace(typ), Required: required})
	}
	return out, nil
}

func Parse(source string) (*Document, error) { return ParseCortex(source) }

func ParseCortex(source string) (*Document, error) {
	if strings.HasPrefix(source, "\ufeff") {
		return nil, &ParseError{Code: "U001_BOM_FORBIDDEN", Message: "BOM forbidden"}
	}
	lines := strings.Split(normalizeLineEndings(source), "\n")
	doc := NewDocument()
	inGlossary := false
	currentSection := -1
	inBody := false
	bodyLines := []string{}
	var bodyIdea *Idea
	bodyKind := ""

	for idx := 0; idx < len(lines); idx++ {
		raw := lines[idx]
		lineNo := idx + 1
		if inBody {
			if strings.TrimSpace(raw) == "}" {
				bodyIdea.Body = strings.Join(bodyLines, "\n")
				bodyIdea.multiline = false
				doc.Sections[currentSection].Ideas = append(doc.Sections[currentSection].Ideas, *bodyIdea)
				inBody = false
				bodyLines = nil
				bodyIdea = nil
				bodyKind = ""
				continue
			}
			bodyLines = append(bodyLines, raw)
			continue
		}

		stripped := strings.TrimSpace(raw)
		if stripped == "" || strings.HasPrefix(stripped, "#") {
			continue
		}

		if m := sectionBareRE.FindStringSubmatch(stripped); m != nil && !strings.HasPrefix(stripped, "$0:") {
			sid, _ := strconv.Atoi(m[1])
			if sid == 0 {
				if inGlossary {
					return nil, &ParseError{Code: "G002_GLOSSARY_REOPENED", Message: "$0 reopened", Line: lineNo}
				}
				inGlossary = true
				continue
			}
			var title *string
			if len(m) > 3 && m[3] != "" {
				t := strings.TrimSpace(m[3])
				title = &t
			}
			doc.Sections = append(doc.Sections, Section{ID: sid, Title: title})
			currentSection = len(doc.Sections) - 1
			inGlossary = false
			continue
		}
		if m := sectionColonRE.FindStringSubmatch(stripped); m != nil {
			sid, _ := strconv.Atoi(m[1])
			t := strings.TrimSpace(m[2])
			doc.Sections = append(doc.Sections, Section{ID: sid, Title: &t})
			currentSection = len(doc.Sections) - 1
			inGlossary = false
			continue
		}

		if inGlossary && (strings.HasPrefix(stripped, "$0:") || isGlossaryDeclLine(stripped)) {
			if err := parseGlossaryDeclaration(stripped, doc, lineNo); err != nil {
				return nil, err
			}
			continue
		}
		if currentSection < 0 && !inGlossary {
			return nil, &ParseError{Code: "S005_CONTENT_OUTSIDE_SECTION", Message: fmt.Sprintf("Content outside section: %q", stripped), Line: lineNo}
		}
		if inGlossary {
			if err := parseGlossaryDeclaration(stripped, doc, lineNo); err != nil {
				return nil, err
			}
			continue
		}

		idea, err := parseIdeaLine(stripped, doc.Sections[currentSection].ID, doc, lineNo)
		if err != nil {
			return nil, err
		}
		if (idea.Shape == "cuerpo" || idea.Shape == "bloque") && idea.multiline {
			inBody = true
			bodyLines = []string{}
			bodyIdea = &idea
			bodyKind = idea.Shape
			_ = bodyKind
			continue
		}
		doc.Sections[currentSection].Ideas = append(doc.Sections[currentSection].Ideas, idea)
	}
	return doc, nil
}

func isGlossaryDeclLine(s string) bool { return glossaryDeclRE.MatchString(s) }

func parseGlossaryDeclaration(line string, doc *Document, lineNo int) error {
	brace := strings.Index(line, "{")
	if brace < 0 {
		return &ParseError{Code: "G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS", Message: fmt.Sprintf("Glossary declaration must use attrs: %q", line), Line: lineNo}
	}
	head := strings.TrimSpace(line[:brace])
	attrs, err := ParseAttrsPayload(line[brace:], lineNo)
	if err != nil {
		return err
	}
	if strings.HasPrefix(head, "$0:") {
		return addMetaDeclaration(head[3:], attrs, doc, lineNo)
	}
	m := symbolHeadRE.FindStringSubmatch(head)
	if m == nil {
		return &ParseError{Code: "L001_INVALID_SYMBOL", Message: fmt.Sprintf("Invalid sigil declaration head: %q", head), Line: lineNo}
	}
	ns, sigil, label := m[2], m[3], m[4]
	sym, err := buildSymbolDef(ns, sigil, label, attrs, lineNo)
	if err != nil {
		return err
	}
	doc.Glossary.Symbols = append(doc.Glossary.Symbols, sym)
	return nil
}

func scalarStringValue(s Scalar) string {
	switch s.Kind {
	case ScalarString, ScalarAtom, ScalarInteger, ScalarDecimal:
		return s.Text
	default:
		return s.Lexeme
	}
}

func addMetaDeclaration(name string, attrs []Attr, doc *Document, lineNo int) error {
	if name == "format" {
		if doc.Glossary.Format != nil {
			return &ParseError{Code: "G006_DUPLICATE_FORMAT", Message: "Duplicate $0:format", Line: lineNo}
		}
		cortex, encoding := "0.1", "UTF-8"
		if v, ok := attrLookup(attrs, "cortex"); ok {
			cortex = scalarStringValue(v)
		}
		if v, ok := attrLookup(attrs, "encoding"); ok {
			encoding = scalarStringValue(v)
		}
		if cortex != "0.1" {
			return &ParseError{Code: "G007_UNSUPPORTED_VERSION", Message: fmt.Sprintf("Unsupported cortex version: %s", cortex), Line: lineNo}
		}
		if encoding != "UTF-8" {
			return &ParseError{Code: "G011_ENCODING_REQUIRED", Message: fmt.Sprintf("Encoding must be UTF-8: %s", encoding), Line: lineNo}
		}
		doc.Glossary.Format = &FormatDecl{Cortex: cortex, Encoding: encoding, Attrs: attrs, SourceLine: lineNo}
		return nil
	}
	if strings.HasPrefix(name, "enum_") {
		ename := name[5:]
		v, ok := attrLookup(attrs, "values")
		if !ok || v.Kind != ScalarString {
			return &ParseError{Code: "G014_INVALID_ENUM", Message: fmt.Sprintf("enum %s missing values string", ename), Line: lineNo}
		}
		doc.Glossary.Enums = append(doc.Glossary.Enums, EnumDecl{Name: ename, Values: strings.Split(v.Text, "|"), SourceLine: lineNo})
		return nil
	}
	if strings.HasPrefix(name, "micro_") {
		token := name[6:]
		v, ok := attrLookup(attrs, "expand")
		if !ok {
			return &ParseError{Code: "G012_INVALID_MICRO", Message: fmt.Sprintf("micro %s missing expand", token), Line: lineNo}
		}
		doc.Glossary.Micros = append(doc.Glossary.Micros, MicroDecl{Token: token, Expand: scalarStringValue(v), SourceLine: lineNo})
		return nil
	}
	if strings.HasPrefix(name, "namespace_") {
		doc.Glossary.Namespaces = append(doc.Glossary.Namespaces, NamespaceDecl{Alias: name[10:], Attrs: attrs, SourceLine: lineNo})
		return nil
	}
	if strings.HasPrefix(name, "extension_") {
		doc.Glossary.Extensions = append(doc.Glossary.Extensions, ExtensionDecl{Name: name[10:], Attrs: attrs, SourceLine: lineNo})
		return nil
	}
	doc.Glossary.Meta = append(doc.Glossary.Meta, MetaDecl{Name: name, Attrs: attrs, SourceLine: lineNo})
	return nil
}

func buildSymbolDef(ns, sigil, label string, attrs []Attr, lineNo int) (SymbolDef, error) {
	typeV, ok := attrLookup(attrs, "type")
	if !ok {
		return SymbolDef{}, &ParseError{Code: "G016_SYMBOL_TYPE_REQUIRED", Message: fmt.Sprintf("sigil %s missing type", sigil), Line: lineNo}
	}
	shape := scalarStringValue(typeV)
	if shape != "attrs" && shape != "attrs-pos" && shape != "cuerpo" && shape != "bloque" && shape != "relacion" {
		return SymbolDef{}, &ParseError{Code: "G017_UNKNOWN_SHAPE", Message: fmt.Sprintf("Unknown shape: %s", shape), Line: lineNo}
	}
	weightV, ok := attrLookup(attrs, "weight")
	if !ok {
		return SymbolDef{}, &ParseError{Code: "G018_SYMBOL_WEIGHT_REQUIRED", Message: fmt.Sprintf("sigil %s missing weight", sigil), Line: lineNo}
	}
	weight := scalarStringValue(weightV)
	if weight != "B" && weight != "M" && weight != "H" {
		return SymbolDef{}, &ParseError{Code: "G019_INVALID_WEIGHT", Message: fmt.Sprintf("Invalid weight: %s", weight), Line: lineNo}
	}
	descV, ok := attrLookup(attrs, "desc")
	if !ok {
		return SymbolDef{}, &ParseError{Code: "G020_SYMBOL_DESCRIPTION_REQUIRED", Message: fmt.Sprintf("sigil %s missing desc", sigil), Line: lineNo}
	}
	desc := descV.Lexeme
	if descV.Kind == ScalarString {
		desc = descV.Text
	}
	open := false
	if v, ok := attrLookup(attrs, "open"); ok {
		open = (v.Kind == ScalarBoolean && v.Bool) || (v.Kind == ScalarAtom && v.Text == "true")
	}
	contract := []ContractField{}
	if shape == "attrs" {
		v, ok := attrLookup(attrs, "fields")
		if !ok {
			return SymbolDef{}, &ParseError{Code: "G021_ATTRS_CONTRACT_REQUIRED", Message: fmt.Sprintf("sigil %s missing fields", sigil), Line: lineNo}
		}
		var err error
		contract, err = ParseContractFields(v.Text)
		if err != nil {
			return SymbolDef{}, err
		}
	}
	if shape == "attrs-pos" || shape == "relacion" {
		v, ok := attrLookup(attrs, "pos")
		if !ok {
			return SymbolDef{}, &ParseError{Code: "G022_POSITIONAL_CONTRACT_REQUIRED", Message: fmt.Sprintf("sigil %s missing pos", sigil), Line: lineNo}
		}
		var err error
		contract, err = ParseContractFields(v.Text)
		if err != nil {
			return SymbolDef{}, err
		}
		if shape == "relacion" && len(contract) < 3 {
			return SymbolDef{}, &ParseError{Code: "G023_RELATION_CONTRACT_TOO_SHORT", Message: "relacion needs >=3 fields", Line: lineNo}
		}
	}
	focus := ""
	if v, ok := attrLookup(attrs, "focus"); ok {
		focus = scalarStringValue(v)
	} else if shape == "cuerpo" || shape == "bloque" {
		focus = "$body"
	} else {
		return SymbolDef{}, &ParseError{Code: "G024_FOCUS_REQUIRED", Message: fmt.Sprintf("sigil %s missing focus", sigil), Line: lineNo}
	}
	if shape == "attrs" || shape == "attrs-pos" || shape == "relacion" {
		found := false
		for _, f := range contract {
			if f.Name == focus {
				found = true
				break
			}
		}
		if !found {
			return SymbolDef{}, &ParseError{Code: "G025_UNKNOWN_FOCUS_FIELD", Message: fmt.Sprintf("focus %q not in contract", focus), Line: lineNo}
		}
	}
	return SymbolDef{Namespace: ns, Sigil: sigil, Label: label, Shape: shape, Weight: weight, Focus: focus, Desc: desc, Open: open, Contract: contract, Attrs: attrs, SourceLine: lineNo}, nil
}

func parseIdeaLine(line string, sectionID int, doc *Document, lineNo int) (Idea, error) {
	line = strings.TrimSpace(line)
	m := ideaHeadRE.FindStringSubmatch(line)
	if m == nil {
		return Idea{}, &ParseError{Code: "S003_INVALID_IDEA_HEAD", Message: fmt.Sprintf("Invalid idea head: %q", line), Line: lineNo}
	}
	ns, sigil, name := m[2], m[3], m[4]
	rest := line[len(m[0]):]
	sym := doc.FindSymbol(ns, sigil)
	if sym == nil {
		return Idea{}, &ParseError{Code: "I001_UNDECLARED_SYMBOL", Message: fmt.Sprintf("Undeclared sigil: %s", sigil), Line: lineNo}
	}
	idea := Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: name, Shape: sym.Shape, SourceLine: lineNo}
	switch sym.Shape {
	case "attrs", "cuerpo", "bloque":
		if !strings.HasPrefix(rest, "{") {
			return Idea{}, &ParseError{Code: "I004_SHAPE_DELIMITER_MISMATCH", Message: fmt.Sprintf("Expected { for shape %s", sym.Shape), Line: lineNo}
		}
		if strings.HasSuffix(rest, "}") {
			if sym.Shape == "attrs" {
				attrs, err := ParseAttrsPayload(rest, lineNo)
				if err != nil {
					return Idea{}, err
				}
				idea.Attrs = attrs
				return idea, nil
			}
			inner := rest[1 : len(rest)-1]
			if sym.Shape == "cuerpo" {
				inner = ToNFC(inner)
			}
			idea.Body = inner
			return idea, nil
		}
		if strings.TrimSpace(rest) != "{" {
			return Idea{}, &ParseError{Code: "I004_SHAPE_DELIMITER_MISMATCH", Message: fmt.Sprintf("Expected single { for multiline %s", sym.Shape), Line: lineNo}
		}
		idea.multiline = true
		return idea, nil
	case "attrs-pos", "relacion":
		if !strings.HasPrefix(rest, "|") {
			return Idea{}, &ParseError{Code: "I004_SHAPE_DELIMITER_MISMATCH", Message: fmt.Sprintf("Expected | for shape %s", sym.Shape), Line: lineNo}
		}
		cells, err := parsePipeCells(rest[1:], lineNo)
		if err != nil {
			return Idea{}, err
		}
		idea.Cells = cells
		return idea, nil
	}
	return Idea{}, &ParseError{Code: "S999_INTERNAL_PARSE_FAILURE", Message: fmt.Sprintf("Cannot parse idea: %q", line), Line: lineNo}
}

func parsePipeCells(s string, lineNo int) ([]Scalar, error) {
	r := []rune(s)
	cells := []Scalar{}
	i := 0
	n := len(r)
	for i <= n {
		if i < n && r[i] == '"' {
			c := newCursor(string(r[i:]), lineNo, 1)
			sc, err := parseStringScalar(c)
			if err != nil {
				return nil, err
			}
			cells = append(cells, sc)
			i += c.i
			for i < n && (r[i] == ' ' || r[i] == '\t') {
				i++
			}
			if i >= n {
				return cells, nil
			}
			if r[i] != '|' {
				return nil, &ParseError{Code: "S006_INVALID_ATTRS", Message: "Expected | after quoted cell", Line: lineNo, Col: i}
			}
			i++
			continue
		}
		j := i
		for j < n && r[j] != '|' {
			j++
		}
		raw := strings.TrimSpace(string(r[i:j]))
		if raw == "" && j >= n {
			return cells, nil
		}
		cells = append(cells, classifyRawCell(raw))
		i = j
		if i < n && r[i] == '|' {
			i++
			continue
		}
		return cells, nil
	}
	return cells, nil
}

func classifyRawCell(raw string) Scalar {
	if intRE.MatchString(raw) {
		if raw == "-0" {
			raw = "0"
		}
		return Scalar{Kind: ScalarInteger, Text: raw, Lexeme: raw}
	}
	if decRE.MatchString(raw) {
		return Scalar{Kind: ScalarDecimal, Text: raw, Lexeme: raw}
	}
	switch raw {
	case "true":
		return Scalar{Kind: ScalarBoolean, Bool: true, Lexeme: "true"}
	case "false":
		return Scalar{Kind: ScalarBoolean, Bool: false, Lexeme: "false"}
	case "null":
		return Scalar{Kind: ScalarNull, Lexeme: "null"}
	}
	if atomRE.MatchString(raw) && !strings.Contains(raw, " ") {
		return Scalar{Kind: ScalarAtom, Text: raw, Lexeme: raw}
	}
	return Scalar{Kind: ScalarString, Text: raw, Lexeme: EmitStringLiteral(raw)}
}
