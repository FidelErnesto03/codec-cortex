package cortex

import (
	"fmt"
	"regexp"
	"sort"
	"strings"
)

var (
	v10SectionCapaRE  = regexp.MustCompile(`^\$([1-9][0-9]*):(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$`)
	v10SectionNumRE   = regexp.MustCompile(`^\$([0-9]+)(?:\s+(.*))?$`)
	v10SectionTitleRE = regexp.MustCompile(`^\$([1-9][0-9]*):\s+(.*)$`)
	v10CapaTailRE     = regexp.MustCompile(`:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)\s*$`)
	v10IdeaHeadRE     = regexp.MustCompile(`^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):([^{|}\s]+)`)
	v10SymbolHeadRE   = regexp.MustCompile(`^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):(.+)$`)
	v10SlotPosRE      = regexp.MustCompile(`^([1-9][0-9]*)$`)
)

const slotMarker = "※"

type v10Parser struct {
	lines           []string
	doc             *Document
	inGlossary      bool
	current         *Section
	inBody          bool
	bodyLines       []string
	bodyIdea        *Idea
	bodyKind        string
	seenSigilMap    bool
	seenAnySlots    bool
	seenSectionIDs  map[int]bool
	seenIdeaAddress map[string]bool
	seenSymbolKeys  map[string]bool
}

type slotEntry struct {
	index int
	value Scalar
}

// ParseV10 parses a CORTEX 1.0/0.2 document with the slots surface.
func ParseV10(source string, version string) (*Document, error) {
	if strings.HasPrefix(source, "\ufeff") {
		return nil, &ParseError{Code: "U001_BOM_FORBIDDEN", Message: "BOM forbidden"}
	}
	p := &v10Parser{
		lines:           strings.Split(normalizeLineEndings(source), "\n"),
		doc:             &Document{CortexVersion: version, Encoding: "UTF-8"},
		seenSectionIDs:  map[int]bool{},
		seenIdeaAddress: map[string]bool{},
		seenSymbolKeys:  map[string]bool{},
	}
	return p.parse()
}

func (p *v10Parser) parse() (*Document, error) {
	for i := 0; i < len(p.lines); i++ {
		raw := p.lines[i]
		lineNo := i + 1
		if p.inBody {
			stripped := strings.TrimSpace(raw)
			if stripped == "}" {
				text := strings.Join(p.bodyLines, "\n")
				if p.bodyKind == "cuerpo" {
					p.bodyIdea.Body = text
					p.bodyIdea.Shape = "cuerpo"
				} else {
					p.bodyIdea.Body = text
					p.bodyIdea.Shape = "bloque"
				}
				if p.current != nil {
					p.current.Ideas = append(p.current.Ideas, *p.bodyIdea)
				}
				p.inBody = false
				p.bodyLines = nil
				p.bodyIdea = nil
				p.bodyKind = ""
				continue
			}
			p.bodyLines = append(p.bodyLines, raw)
			continue
		}
		stripped := strings.TrimSpace(raw)
		if stripped == "" || strings.HasPrefix(stripped, "#") {
			continue
		}
		if m := regexp.MustCompile(`^\$0:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$`).FindStringSubmatch(stripped); m != nil {
			if p.inGlossary {
				return nil, &ParseError{Code: "G002_GLOSSARY_REOPENED", Message: "$0 reopened", Line: lineNo}
			}
			p.inGlossary = true
			p.doc.Glossary.Capa = m[1]
			continue
		}
		if regexp.MustCompile(`^\$0:\s+`).MatchString(stripped) && !regexp.MustCompile(`^\$0:\s*(?:format|enum_|micro_|namespace_|extension_|sigil-map)`).MatchString(stripped) {
			if p.inGlossary {
				return nil, &ParseError{Code: "G002_GLOSSARY_REOPENED", Message: "$0 reopened", Line: lineNo}
			}
			p.inGlossary = true
			continue
		}
		if m := v10SectionCapaRE.FindStringSubmatch(stripped); m != nil {
			sid := atoi(m[1])
			if err := p.startSection(sid, "", m[2], lineNo); err != nil {
				return nil, err
			}
			continue
		}
		if m := v10SectionNumRE.FindStringSubmatch(stripped); m != nil && !strings.HasPrefix(stripped, "$0:") {
			sid := atoi(m[1])
			if sid == 0 {
				if p.inGlossary {
					return nil, &ParseError{Code: "G002_GLOSSARY_REOPENED", Message: "$0 reopened", Line: lineNo}
				}
				p.inGlossary = true
				continue
			}
			title := strings.TrimSpace(m[2])
			capa := ""
			if title != "" {
				if cm := v10CapaTailRE.FindStringSubmatchIndex(title); cm != nil {
					capa = title[cm[2]:cm[3]]
					title = strings.TrimSpace(title[:cm[0]])
				}
			}
			if err := p.startSection(sid, title, capa, lineNo); err != nil {
				return nil, err
			}
			continue
		}
		if m := v10SectionTitleRE.FindStringSubmatch(stripped); m != nil {
			sid := atoi(m[1])
			title := strings.TrimSpace(m[2])
			capa := ""
			if cm := v10CapaTailRE.FindStringSubmatchIndex(title); cm != nil {
				capa = title[cm[2]:cm[3]]
				title = strings.TrimSpace(title[:cm[0]])
			}
			if err := p.startSection(sid, title, capa, lineNo); err != nil {
				return nil, err
			}
			continue
		}
		if p.inGlossary && (strings.HasPrefix(stripped, "$0:") || isGlossaryDeclLine(stripped)) {
			if err := p.parseGlossaryDeclaration(stripped, lineNo); err != nil {
				return nil, err
			}
			continue
		}
		if p.current == nil && !p.inGlossary {
			return nil, &ParseError{Code: "S005_CONTENT_OUTSIDE_SECTION", Message: fmt.Sprintf("Content outside section: %q", stripped), Line: lineNo}
		}
		if p.inGlossary {
			if err := p.parseGlossaryDeclaration(stripped, lineNo); err != nil {
				return nil, err
			}
			continue
		}
		idea, err := p.parseIdeaLine(stripped, p.current.ID, lineNo)
		if err != nil {
			return nil, err
		}
		if (idea.Shape == "cuerpo" || idea.Shape == "bloque") && idea.Body == "\x00multiline" {
			p.inBody = true
			p.bodyLines = nil
			p.bodyIdea = idea
			p.bodyKind = idea.Shape
			continue
		}
		p.current.Ideas = append(p.current.Ideas, *idea)
	}
	if p.seenAnySlots && !p.seenSigilMap {
		return nil, &ParseError{Code: "G030_SIGIL_MAP_REQUIRED", Message: "0.2 uses slots but $0:sigil-map is missing"}
	}
	if p.inBody {
		return nil, &ParseError{Code: "S007_UNCLOSED_BODY", Message: "Unclosed body"}
	}
	return p.doc, nil
}

func (p *v10Parser) startSection(sid int, title, capa string, lineNo int) error {
	if p.seenSectionIDs[sid] {
		return &ParseError{Code: "S002_DUPLICATE_SECTION", Message: fmt.Sprintf("Duplicate section $%d", sid), Line: lineNo}
	}
	p.seenSectionIDs[sid] = true
	if p.seenAnySlots && !p.seenSigilMap {
		return &ParseError{Code: "G030_SIGIL_MAP_REQUIRED", Message: "0.2 uses slots but $0:sigil-map is missing", Line: lineNo}
	}
	var titlePtr *string
	if title != "" {
		titlePtr = &title
	}
	sec := Section{ID: sid, Title: titlePtr, Capa: capa}
	p.doc.Sections = append(p.doc.Sections, sec)
	p.current = &p.doc.Sections[len(p.doc.Sections)-1]
	p.inGlossary = false
	return nil
}

func (p *v10Parser) parseGlossaryDeclaration(line string, lineNo int) error {
	braceIdx := strings.Index(line, "{")
	if braceIdx < 0 {
		return &ParseError{Code: "G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS", Message: fmt.Sprintf("Glossary declaration must use attrs: %q", line), Line: lineNo}
	}
	closeIdx, err := findMatchingBrace(line, braceIdx)
	if err != nil {
		return err
	}
	head := strings.TrimSpace(line[:braceIdx])
	payload := line[braceIdx : closeIdx+1]
	tail := strings.TrimSpace(line[closeIdx+1:])
	capa := ""
	if tail != "" {
		if m := regexp.MustCompile(`^:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$`).FindStringSubmatch(tail); m != nil {
			capa = m[1]
		}
	}
	if strings.HasPrefix(head, "$0:") {
		return p.addMetaDeclaration(head[3:], payload, lineNo, capa)
	}
	m := v10SymbolHeadRE.FindStringSubmatch(head)
	if m == nil {
		return &ParseError{Code: "L001_INVALID_SYMBOL", Message: fmt.Sprintf("Invalid sigil declaration head: %q", head), Line: lineNo}
	}
	ns, sigil, label := m[1], m[2], m[3]
	key := ns + "\x00" + sigil
	if p.seenSymbolKeys[key] {
		return &ParseError{Code: "G015_DUPLICATE_SYMBOL", Message: fmt.Sprintf("Duplicate symbol %s%s", nsPrefix(ns), sigil), Line: lineNo}
	}
	attrs, err := ParseAttrsPayload(payload, lineNo)
	if err != nil {
		return err
	}
	sym, err := p.buildSymbolDef(ns, sigil, label, attrs, lineNo)
	if err != nil {
		return err
	}
	p.doc.Glossary.Symbols = append(p.doc.Glossary.Symbols, sym)
	p.seenSymbolKeys[key] = true
	return nil
}

func (p *v10Parser) addMetaDeclaration(name, payload string, lineNo int, capa string) error {
	attrs, err := ParseAttrsPayload(payload, lineNo)
	if err != nil {
		return err
	}
	if name != "sigil-map" {
		for _, a := range attrs {
			if strings.Contains(a.Key, slotMarker) {
				return &ParseError{Code: "I050_SLOT_NOT_ALLOWED_IN_GLOSSARY", Message: fmt.Sprintf("※ in $0:%s key %q", name, a.Key), Line: lineNo}
			}
			if a.Value.Kind == ScalarString && strings.Contains(a.Value.Text, slotMarker) {
				return &ParseError{Code: "I050_SLOT_NOT_ALLOWED_IN_GLOSSARY", Message: fmt.Sprintf("※ in $0:%s attr %s", name, a.Key), Line: lineNo}
			}
		}
	}
	switch {
	case name == "format":
		if p.doc.Glossary.Format != nil {
			return &ParseError{Code: "G006_DUPLICATE_FORMAT", Message: "Duplicate $0:format", Line: lineNo}
		}
		amap := attrMap(attrs)
		cortex := "0.1"
		if v, ok := amap["cortex"]; ok {
			cortex = scalarStringValue(v)
		}
		encoding := "UTF-8"
		if v, ok := amap["encoding"]; ok {
			encoding = scalarStringValue(v)
		}
		if cortex != "0.2" && cortex != "1.0" {
			return &ParseError{Code: "G007_UNSUPPORTED_VERSION", Message: fmt.Sprintf("Declared cortex %s != parser version %s", cortex, p.doc.CortexVersion), Line: lineNo}
		}
		if encoding != "UTF-8" {
			return &ParseError{Code: "G011_ENCODING_REQUIRED", Message: fmt.Sprintf("Encoding must be UTF-8: %s", encoding), Line: lineNo}
		}
		p.doc.Glossary.Format = &FormatDecl{Cortex: cortex, Encoding: encoding, Attrs: attrs, SourceLine: lineNo}
	case name == "sigil-map":
		if p.seenAnySlots {
			return &ParseError{Code: "G041_SIGIL_MAP_ORDER", Message: "$0:sigil-map must appear before any sigil with encoding:slots", Line: lineNo}
		}
		if p.seenSigilMap {
			return &ParseError{Code: "G031_DUPLICATE_SIGIL_MAP", Message: "More than one $0:sigil-map", Line: lineNo}
		}
		amap := attrMap(attrs)
		sm := SigilMapDecl{Marker: slotMarker, Codepoint: "U+203B", Base: 1, Syntax: "※N:valor", Order: "ascending", SourceLine: lineNo}
		if v, ok := amap["marker"]; ok {
			sm.Marker = scalarStringValue(v)
		}
		if v, ok := amap["codepoint"]; ok {
			sm.Codepoint = scalarStringValue(v)
		}
		if v, ok := amap["base"]; ok && v.Kind == ScalarInteger {
			sm.Base = atoi(v.Text)
		}
		if v, ok := amap["syntax"]; ok {
			sm.Syntax = scalarStringValue(v)
		}
		if v, ok := amap["order"]; ok {
			sm.Order = scalarStringValue(v)
		}
		if sm.Marker != slotMarker || sm.Codepoint != "U+203B" || sm.Base != 1 || sm.Syntax != "※N:valor" || sm.Order != "ascending" {
			return &ParseError{Code: "G032_INVALID_SIGIL_MAP", Message: "sigil-map values are not canonical", Line: lineNo}
		}
		p.doc.Glossary.SigilMap = &sm
		p.seenSigilMap = true
	case strings.HasPrefix(name, "enum_"):
		ename := name[5:]
		amap := attrMap(attrs)
		v, ok := amap["values"]
		if !ok || v.Kind != ScalarString {
			return &ParseError{Code: "G014_INVALID_ENUM", Message: fmt.Sprintf("enum %s missing values string", ename), Line: lineNo}
		}
		p.doc.Glossary.Enums = append(p.doc.Glossary.Enums, EnumDecl{Name: ename, Values: strings.Split(v.Text, "|"), SourceLine: lineNo})
	case strings.HasPrefix(name, "micro_"):
		token := name[6:]
		amap := attrMap(attrs)
		v, ok := amap["expand"]
		if !ok {
			return &ParseError{Code: "G012_INVALID_MICRO", Message: fmt.Sprintf("micro %s missing expand", token), Line: lineNo}
		}
		expand := v.Text
		if v.Kind != ScalarAtom && v.Kind != ScalarString {
			expand = v.Lexeme
		}
		p.doc.Glossary.Micros = append(p.doc.Glossary.Micros, MicroDecl{Token: token, Expand: expand, SourceLine: lineNo})
	case strings.HasPrefix(name, "namespace_"):
		p.doc.Glossary.Namespaces = append(p.doc.Glossary.Namespaces, NamespaceDecl{Alias: name[10:], Attrs: attrs, SourceLine: lineNo})
	case strings.HasPrefix(name, "extension_"):
		p.doc.Glossary.Extensions = append(p.doc.Glossary.Extensions, ExtensionDecl{Name: name[10:], Attrs: attrs, SourceLine: lineNo})
	default:
		p.doc.Glossary.Meta = append(p.doc.Glossary.Meta, MetaDecl{Name: name, Attrs: attrs, Capa: capa, SourceLine: lineNo})
	}
	return nil
}

func (p *v10Parser) buildSymbolDef(ns, sigil, label string, attrs []Attr, lineNo int) (SymbolDef, error) {
	amap := attrMap(attrs)
	typeV, ok := amap["type"]
	if !ok {
		return SymbolDef{}, &ParseError{Code: "G016_SYMBOL_TYPE_REQUIRED", Message: fmt.Sprintf("sigil %s missing type", sigil), Line: lineNo}
	}
	shape := typeV.Text
	if typeV.Kind != ScalarAtom && typeV.Kind != ScalarString {
		shape = typeV.Lexeme
	}
	if !inSet(shape, "attrs", "attrs-pos", "cuerpo", "bloque", "relacion") {
		return SymbolDef{}, &ParseError{Code: "G017_UNKNOWN_SHAPE", Message: fmt.Sprintf("Unknown shape: %s", shape), Line: lineNo}
	}
	weightV, ok := amap["weight"]
	if !ok {
		return SymbolDef{}, &ParseError{Code: "G018_SYMBOL_WEIGHT_REQUIRED", Message: fmt.Sprintf("sigil %s missing weight", sigil), Line: lineNo}
	}
	weight := weightV.Text
	if weightV.Kind != ScalarAtom && weightV.Kind != ScalarString {
		weight = weightV.Lexeme
	}
	if !inSet(weight, "B", "M", "H") {
		return SymbolDef{}, &ParseError{Code: "G019_INVALID_WEIGHT", Message: fmt.Sprintf("Invalid weight: %s", weight), Line: lineNo}
	}
	descV, ok := amap["desc"]
	if !ok {
		return SymbolDef{}, &ParseError{Code: "G020_SYMBOL_DESCRIPTION_REQUIRED", Message: fmt.Sprintf("sigil %s missing desc", sigil), Line: lineNo}
	}
	desc := descV.Lexeme
	if descV.Kind == ScalarString {
		desc = descV.Text
	}
	isOpen := false
	if v, ok := amap["open"]; ok {
		isOpen = (v.Kind == ScalarBoolean && v.Bool) || (v.Kind == ScalarAtom && v.Text == "true")
	}
	encoding := ""
	if v, ok := amap["encoding"]; ok {
		encoding = v.Text
		if v.Kind != ScalarAtom && v.Kind != ScalarString {
			encoding = v.Lexeme
		}
		if encoding != "slots" {
			return SymbolDef{}, &ParseError{Code: "G039_ENCODING_SHAPE_MISMATCH", Message: fmt.Sprintf("Unknown encoding: %s", encoding), Line: lineNo}
		}
		if !inSet(shape, "attrs", "attrs-pos", "relacion") {
			return SymbolDef{}, &ParseError{Code: "G039_ENCODING_SHAPE_MISMATCH", Message: fmt.Sprintf("encoding:slots not valid for shape %s", shape), Line: lineNo}
		}
		p.seenAnySlots = true
		if !p.seenSigilMap {
			return SymbolDef{}, &ParseError{Code: "G030_SIGIL_MAP_REQUIRED", Message: fmt.Sprintf("sigil %s uses encoding:slots but $0:sigil-map not yet declared", sigil), Line: lineNo}
		}
	}
	var contract []ContractField
	if encoding == "slots" {
		slotsV, ok := amap["slots"]
		if !ok {
			return SymbolDef{}, &ParseError{Code: "G033_SLOT_CONTRACT_REQUIRED", Message: fmt.Sprintf("sigil %s with encoding:slots missing slots", sigil), Line: lineNo}
		}
		slotsStr := slotsV.Text
		if slotsV.Kind != ScalarString {
			slotsStr = slotsV.Lexeme
		}
		if _, ok := amap["fields"]; ok {
			return SymbolDef{}, &ParseError{Code: "G040_CONTRACT_SURFACE_CONFLICT", Message: fmt.Sprintf("sigil %s cannot have fields/pos + slots", sigil), Line: lineNo}
		}
		if _, ok := amap["pos"]; ok {
			return SymbolDef{}, &ParseError{Code: "G040_CONTRACT_SURFACE_CONFLICT", Message: fmt.Sprintf("sigil %s cannot have fields/pos + slots", sigil), Line: lineNo}
		}
		fields, err := parseSlotContract(slotsStr, lineNo)
		if err != nil {
			return SymbolDef{}, err
		}
		if isOpen {
			return SymbolDef{}, &ParseError{Code: "G038_SLOTS_OPEN_FORBIDDEN", Message: fmt.Sprintf("sigil %s slots cannot be open", sigil), Line: lineNo}
		}
		contract = fields
	} else if shape == "attrs" {
		fieldsV, ok := amap["fields"]
		if !ok {
			return SymbolDef{}, &ParseError{Code: "G021_ATTRS_CONTRACT_REQUIRED", Message: fmt.Sprintf("sigil %s missing fields", sigil), Line: lineNo}
		}
		fields, err := ParseContractFields(fieldsV.Text)
		if err != nil {
			return SymbolDef{}, err
		}
		contract = fields
	} else if shape == "attrs-pos" || shape == "relacion" {
		posV, ok := amap["pos"]
		if !ok {
			return SymbolDef{}, &ParseError{Code: "G022_POSITIONAL_CONTRACT_REQUIRED", Message: fmt.Sprintf("sigil %s missing pos", sigil), Line: lineNo}
		}
		fields, err := ParseContractFields(posV.Text)
		if err != nil {
			return SymbolDef{}, err
		}
		if shape == "relacion" && len(fields) < 3 {
			return SymbolDef{}, &ParseError{Code: "G023_RELATION_CONTRACT_TOO_SHORT", Message: "relacion needs >=3 fields", Line: lineNo}
		}
		contract = fields
	}
	focus := ""
	if v, ok := amap["focus"]; ok {
		focus = v.Text
		if v.Kind != ScalarAtom && v.Kind != ScalarString {
			focus = v.Lexeme
		}
		if inSet(shape, "attrs", "attrs-pos", "relacion") {
			var focusField *ContractField
			for i := range contract {
				if contract[i].Name == focus {
					focusField = &contract[i]
					break
				}
			}
			if focusField == nil {
				if encoding == "slots" {
					return SymbolDef{}, &ParseError{Code: "G037_SLOT_FOCUS_UNRESOLVED", Message: fmt.Sprintf("focus %q not in slot contract", focus), Line: lineNo}
				}
				return SymbolDef{}, &ParseError{Code: "G025_UNKNOWN_FOCUS_FIELD", Message: fmt.Sprintf("focus %q not in contract", focus), Line: lineNo}
			}
			if encoding == "slots" && !focusField.Required {
				return SymbolDef{}, &ParseError{Code: "G037_SLOT_FOCUS_UNRESOLVED", Message: fmt.Sprintf("focus %q must be a required slot", focus), Line: lineNo}
			}
		}
	} else if shape == "cuerpo" || shape == "bloque" {
		focus = "$body"
	} else {
		return SymbolDef{}, &ParseError{Code: "G024_FOCUS_REQUIRED", Message: fmt.Sprintf("sigil %s missing focus", sigil), Line: lineNo}
	}
	return SymbolDef{Namespace: ns, Sigil: sigil, Label: label, Shape: shape, Weight: weight,
		Focus: focus, Desc: desc, Open: isOpen, Contract: contract, Attrs: attrs,
		Encoding: encoding, SourceLine: lineNo}, nil
}

func (p *v10Parser) parseIdeaLine(line string, sectionID int, lineNo int) (*Idea, error) {
	m := v10IdeaHeadRE.FindStringSubmatchIndex(line)
	if m == nil {
		return nil, &ParseError{Code: "S003_INVALID_IDEA_HEAD", Message: fmt.Sprintf("Invalid idea head: %q", line), Line: lineNo}
	}
	ns := ""
	if m[2] >= 0 {
		ns = line[m[2]:m[3]]
	}
	sigil := line[m[4]:m[5]]
	name := line[m[6]:m[7]]
	rest := line[m[1]:]
	var sym *SymbolDef
	for i := range p.doc.Glossary.Symbols {
		s := &p.doc.Glossary.Symbols[i]
		if s.Sigil == sigil && s.Namespace == ns {
			sym = s
			break
		}
	}
	if sym == nil {
		return nil, &ParseError{Code: "I001_UNDECLARED_SYMBOL", Message: fmt.Sprintf("Undeclared sigil: %s", sigil), Line: lineNo}
	}
	addr := fmt.Sprintf("$%d:%s%s:%s", sectionID, nsPrefix(ns), sigil, name)
	if p.seenIdeaAddress[addr] {
		return nil, &ParseError{Code: "I006_DUPLICATE_IDEA_ADDRESS", Message: fmt.Sprintf("Duplicate idea address %s", addr), Line: lineNo}
	}
	p.seenIdeaAddress[addr] = true
	if sym.Encoding == "slots" {
		if !strings.HasPrefix(rest, "{") {
			return nil, &ParseError{Code: "I004_SHAPE_DELIMITER_MISMATCH", Message: "Expected { for slot-encoded Idea", Line: lineNo}
		}
		if !strings.HasSuffix(rest, "}") || strings.Contains(rest, "\n") {
			return nil, &ParseError{Code: "I004_SHAPE_DELIMITER_MISMATCH", Message: "Slot-encoded Idea must be single-line", Line: lineNo}
		}
		entries, err := parseSlotPayload(rest, lineNo)
		if err != nil {
			return nil, err
		}
		fvs, err := resolveSlotEntries(entries, *sym, lineNo)
		if err != nil {
			return nil, err
		}
		return &Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: name,
			Shape: sym.Shape, SlotValues: fvs, SlotEncoded: true, SourceLine: lineNo}, nil
	}
	return p.parseIdeaLineLegacy(sectionID, lineNo, ns, sigil, name, rest, *sym)
}

func (p *v10Parser) parseIdeaLineLegacy(sectionID, lineNo int, ns, sigil, name, rest string, sym SymbolDef) (*Idea, error) {
	shape := sym.Shape
	if shape == "attrs" || shape == "cuerpo" || shape == "bloque" {
		if !strings.HasPrefix(rest, "{") {
			return nil, &ParseError{Code: "I004_SHAPE_DELIMITER_MISMATCH", Message: fmt.Sprintf("Expected { for shape %s", shape), Line: lineNo}
		}
		if strings.HasSuffix(rest, "}") && !strings.Contains(rest, "\n") {
			if shape == "attrs" {
				pairs, err := ParseAttrsPayload(rest, lineNo)
				if err != nil {
					return nil, err
				}
				if err := validateAttrsPayload(pairs, sym, lineNo); err != nil {
					return nil, err
				}
				return &Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: name, Shape: shape, Attrs: pairs, SourceLine: lineNo}, nil
			}
			inner := rest[1 : len(rest)-1]
			if shape == "cuerpo" {
				inner = ToNFC(inner)
			}
			return &Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: name, Shape: shape, Body: inner, SourceLine: lineNo}, nil
		}
		if strings.TrimSpace(rest) != "{" {
			return nil, &ParseError{Code: "I004_SHAPE_DELIMITER_MISMATCH", Message: fmt.Sprintf("Expected single { for multiline %s", shape), Line: lineNo}
		}
		return &Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: name, Shape: shape, Body: "\x00multiline", SourceLine: lineNo}, nil
	}
	if shape == "attrs-pos" || shape == "relacion" {
		if !strings.HasPrefix(rest, "|") {
			return nil, &ParseError{Code: "I004_SHAPE_DELIMITER_MISMATCH", Message: fmt.Sprintf("Expected | for shape %s", shape), Line: lineNo}
		}
		cells, err := parsePipeCells(rest[1:], lineNo)
		if err != nil {
			return nil, err
		}
		required := 0
		for _, f := range sym.Contract {
			if f.Required {
				required++
			}
		}
		if len(cells) < required {
			return nil, &ParseError{Code: "I012_POSITIONAL_ARITY", Message: fmt.Sprintf("shape %s needs ≥%d cells, got %d", shape, required, len(cells)), Line: lineNo}
		}
		if len(cells) > len(sym.Contract) {
			return nil, &ParseError{Code: "I012_POSITIONAL_ARITY", Message: fmt.Sprintf("shape %s expects ≤%d cells, got %d", shape, len(sym.Contract), len(cells)), Line: lineNo}
		}
		return &Idea{Section: sectionID, Namespace: ns, Symbol: sigil, Name: name, Shape: shape, Cells: cells, SourceLine: lineNo}, nil
	}
	return nil, &ParseError{Code: "S999_INTERNAL_PARSE_FAILURE", Message: fmt.Sprintf("Cannot parse idea: %q", rest), Line: lineNo}
}

func validateAttrsPayload(pairs []Attr, sym SymbolDef, lineNo int) error {
	seen := map[string]bool{}
	for _, a := range pairs {
		if seen[a.Key] {
			return &ParseError{Code: "I006_DUPLICATE_FIELD", Message: fmt.Sprintf("Duplicate field %q", a.Key), Line: lineNo}
		}
		seen[a.Key] = true
	}
	if !sym.Open {
		names := map[string]bool{}
		for _, f := range sym.Contract {
			names[f.Name] = true
		}
		for _, a := range pairs {
			if !names[a.Key] {
				return &ParseError{Code: "I005_UNKNOWN_FIELD", Message: fmt.Sprintf("Unknown field %q", a.Key), Line: lineNo}
			}
		}
	}
	for _, f := range sym.Contract {
		if f.Required && !seen[f.Name] {
			return &ParseError{Code: "I008_REQUIRED_FIELD_MISSING", Message: fmt.Sprintf("Required field %q missing", f.Name), Line: lineNo}
		}
	}
	return nil
}

func parseSlotContract(s string, line int) ([]ContractField, error) {
	out := []ContractField{}
	if s == "" {
		return out, nil
	}
	for _, part := range strings.Split(s, "|") {
		part = strings.TrimSpace(part)
		if part == "" {
			return nil, &ParseError{Code: "G008_INVALID_CONTRACT", Message: fmt.Sprintf("Empty slot-contract entry in %q", s), Line: line}
		}
		idx := strings.Index(part, "=")
		if idx < 0 {
			return nil, &ParseError{Code: "G008_INVALID_CONTRACT", Message: fmt.Sprintf("Slot entry missing '=': %q", part), Line: line}
		}
		posStr := strings.TrimSpace(part[:idx])
		rest := part[idx+1:]
		if !v10SlotPosRE.MatchString(posStr) {
			return nil, &ParseError{Code: "G008_INVALID_CONTRACT", Message: fmt.Sprintf("Invalid slot position %q", posStr), Line: line}
		}
		position := atoi(posStr)
		if position == 0 {
			return nil, &ParseError{Code: "L022_SLOT_ZERO_FORBIDDEN", Message: "Slot position 0 forbidden", Line: line}
		}
		if position > 1000000 {
			return nil, &ParseError{Code: "I057_SLOT_INDEX_LIMIT", Message: fmt.Sprintf("Slot position %d exceeds max", position), Line: line}
		}
		required := true
		if strings.HasSuffix(rest, "?") {
			required = false
			rest = rest[:len(rest)-1]
		}
		name, typ := rest, "any"
		if i := strings.Index(rest, ":"); i >= 0 {
			name, typ = rest[:i], rest[i+1:]
		}
		name, typ = strings.TrimSpace(name), strings.TrimSpace(typ)
		if name == "" {
			return nil, &ParseError{Code: "G008_INVALID_CONTRACT", Message: fmt.Sprintf("Empty slot name in %q", part), Line: line}
		}
		out = append(out, ContractField{Name: name, Type: typ, Required: required, Position: position})
	}
	seenPos := map[int]bool{}
	seenName := map[string]bool{}
	for _, f := range out {
		if seenPos[f.Position] {
			return nil, &ParseError{Code: "G035_DUPLICATE_SLOT_POSITION", Message: fmt.Sprintf("Duplicate slot position %d", f.Position), Line: line}
		}
		if seenName[f.Name] {
			return nil, &ParseError{Code: "G036_DUPLICATE_SLOT_NAME", Message: fmt.Sprintf("Duplicate slot name %q", f.Name), Line: line}
		}
		seenPos[f.Position] = true
		seenName[f.Name] = true
	}
	sorted := append([]ContractField(nil), out...)
	sort.Slice(sorted, func(i, j int) bool { return sorted[i].Position < sorted[j].Position })
	expected := 1
	for _, f := range sorted {
		if f.Position != expected {
			return nil, &ParseError{Code: "G034_SLOT_CONTRACT_GAP", Message: fmt.Sprintf("Slot positions not contiguous: expected %d, got %d", expected, f.Position), Line: line}
		}
		expected++
	}
	return out, nil
}

func parseSlotPayload(s string, startLine int) ([]slotEntry, error) {
	c := newCursor(s, startLine, 1)
	skipInlineWS(c)
	if c.peek() != '{' {
		return nil, &ParseError{Code: "S006_INVALID_ATTRS", Message: "Expected { for slot payload", Line: c.line, Col: c.col}
	}
	c.next()
	entries := []slotEntry{}
	skipInlineWS(c)
	if c.peek() == '}' {
		c.next()
		return entries, nil
	}
	if err := checkSlotStart(c); err != nil {
		return nil, err
	}
	for {
		skipInlineWS(c)
		if err := checkSlotStart(c); err != nil {
			return nil, err
		}
		idx, err := parseSlotRef(c)
		if err != nil {
			return nil, err
		}
		skipInlineWS(c)
		v, err := parseScalar(c)
		if err != nil {
			return nil, err
		}
		entries = append(entries, slotEntry{index: idx, value: v})
		skipInlineWS(c)
		switch c.peek() {
		case ',':
			c.next()
			skipInlineWS(c)
			if c.peek() == '}' {
				return nil, &ParseError{Code: "S006_INVALID_ATTRS", Message: "Trailing comma before } in slot payload", Line: c.line, Col: c.col}
			}
		case '}':
			c.next()
			return entries, nil
		default:
			return nil, &ParseError{Code: "S006_INVALID_ATTRS", Message: fmt.Sprintf("Expected , or } got %q", c.peek()), Line: c.line, Col: c.col}
		}
	}
}

func checkSlotStart(c *stringCursor) error {
	ch := c.peek()
	if ch == 0 || ch == rune(0) {
		return nil
	}
	if string(ch) == slotMarker {
		return nil
	}
	if hg, ok := homoglyphs[string(ch)]; ok {
		return &ParseError{Code: "L020_INVALID_SLOT_MARKER", Message: fmt.Sprintf("Slot marker is not ※ (got %s)", hg), Line: c.line, Col: c.col}
	}
	if ch == '|' {
		return &ParseError{Code: "I056_PIPE_PAYLOAD_IN_SLOT_IDEA", Message: "Pipe payload not allowed in slot-encoded Idea", Line: c.line, Col: c.col}
	}
	if (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || ch == '_' {
		saveI, saveLine, saveCol := c.i, c.line, c.col
		for c.peek() != 0 && c.peek() != rune(0) && !strings.ContainsRune(" \t:,", c.peek()) {
			if c.peek() == '}' {
				break
			}
			c.next()
		}
		if c.peek() == ':' {
			return &ParseError{Code: "I055_NAMED_ATTR_IN_SLOT_IDEA", Message: "Named key:value not allowed in slot-encoded Idea", Line: saveLine, Col: saveCol}
		}
		c.i, c.line, c.col = saveI, saveLine, saveCol
	}
	return nil
}

func parseSlotRef(c *stringCursor) (int, error) {
	ch := c.peek()
	if string(ch) != slotMarker {
		if hg, ok := homoglyphs[string(ch)]; ok {
			return 0, &ParseError{Code: "L020_INVALID_SLOT_MARKER", Message: fmt.Sprintf("Slot marker is not ※ (got %s)", hg), Line: c.line, Col: c.col}
		}
		return 0, &ParseError{Code: "L020_INVALID_SLOT_MARKER", Message: fmt.Sprintf("Expected ※ at start of slot ref, got %q", ch), Line: c.line, Col: c.col}
	}
	c.next()
	digits := []rune{}
	for c.peek() >= '0' && c.peek() <= '9' {
		digits = append(digits, c.peek())
		c.next()
	}
	if len(digits) == 0 {
		return 0, &ParseError{Code: "L021_INVALID_SLOT_INDEX", Message: "Missing integer after ※", Line: c.line, Col: c.col}
	}
	raw := string(digits)
	if len(raw) > 1 && raw[0] == '0' {
		return 0, &ParseError{Code: "L023_SLOT_LEADING_ZERO", Message: fmt.Sprintf("Slot index has leading zero: ※%s", raw), Line: c.line, Col: c.col}
	}
	if raw == "0" {
		return 0, &ParseError{Code: "L022_SLOT_ZERO_FORBIDDEN", Message: "Slot index 0 is forbidden", Line: c.line, Col: c.col}
	}
	idx := atoi(raw)
	if idx > 1000000 {
		return 0, &ParseError{Code: "I057_SLOT_INDEX_LIMIT", Message: fmt.Sprintf("Slot index %d exceeds max", idx), Line: c.line, Col: c.col}
	}
	if c.peek() != ':' {
		return 0, &ParseError{Code: "L024_SLOT_SEPARATOR_REQUIRED", Message: fmt.Sprintf("Missing ':' after slot index ※%s", raw), Line: c.line, Col: c.col}
	}
	c.next()
	return idx, nil
}

func resolveSlotEntries(entries []slotEntry, sym SymbolDef, lineNo int) ([]FieldValue, error) {
	seen := map[int]bool{}
	out := []FieldValue{}
	last := 0
	for _, e := range entries {
		if seen[e.index] {
			return nil, &ParseError{Code: "I051_DUPLICATE_SLOT", Message: fmt.Sprintf("slot ※%d duplicated", e.index), Line: lineNo}
		}
		seen[e.index] = true
		if e.index <= last {
			return nil, &ParseError{Code: "I054_SLOT_OUT_OF_ORDER", Message: fmt.Sprintf("slots not in ascending order (※%d after ※%d)", e.index, last), Line: lineNo}
		}
		last = e.index
		var cf *ContractField
		for i := range sym.Contract {
			if sym.Contract[i].Position == e.index {
				cf = &sym.Contract[i]
				break
			}
		}
		if cf == nil {
			return nil, &ParseError{Code: "I052_UNKNOWN_SLOT", Message: fmt.Sprintf("slot ※%d not declared in contract", e.index), Line: lineNo}
		}
		out = append(out, FieldValue{Position: e.index, Name: cf.Name, Type: cf.Type, Required: cf.Required, Value: e.value})
	}
	for _, cf := range sym.Contract {
		if cf.Required && !seen[cf.Position] {
			return nil, &ParseError{Code: "I053_MISSING_REQUIRED_SLOT", Message: fmt.Sprintf("missing required slot ※%d (%s)", cf.Position, cf.Name), Line: lineNo}
		}
	}
	return out, nil
}

func findMatchingBrace(line string, braceIdx int) (int, error) {
	depth := 0
	for i := braceIdx; i < len(line); i++ {
		switch line[i] {
		case '{':
			depth++
		case '}':
			depth--
			if depth == 0 {
				return i, nil
			}
		}
	}
	return 0, &ParseError{Code: "S006_INVALID_ATTRS", Message: "Unclosed {"}
}

func attrMap(attrs []Attr) map[string]Scalar {
	out := map[string]Scalar{}
	for _, a := range attrs {
		out[a.Key] = a.Value
	}
	return out
}

func nsPrefix(ns string) string {
	if ns == "" {
		return ""
	}
	return ns + "::"
}

func inSet(s string, values ...string) bool {
	for _, v := range values {
		if s == v {
			return true
		}
	}
	return false
}

func atoi(s string) int {
	n := 0
	for _, r := range s {
		if r < '0' || r > '9' {
			return n
		}
		n = n*10 + int(r-'0')
	}
	return n
}

var homoglyphs = map[string]string{
	"•": "U+2022 BULLET",
	"·": "U+00B7 MIDDLE DOT",
	"∙": "U+2219 BULLET OPERATOR",
	"●": "U+25CF BLACK CIRCLE",
}
