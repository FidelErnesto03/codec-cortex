package main

import (
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"strconv"
	"strings"
)

// ─── AST types (from ast-schema.json) ────────────────────────────────────────

type SourceLine int

type Document struct {
	Node          string    `json:"node"`
	CortexVersion string    `json:"cortexVersion"`
	Encoding      string    `json:"encoding"`
	Glossary      Glossary  `json:"glossary"`
	Sections      []Section `json:"sections"`
}

type Glossary struct {
	Node       string                 `json:"node"`
	Format     FormatDeclaration      `json:"format"`
	Meta       []MetaDeclaration      `json:"meta"`
	Enums      []EnumDeclaration      `json:"enums"`
	Micros     []MicroDeclaration     `json:"micros"`
	Namespaces []NamespaceDeclaration `json:"namespaces"`
	Extensions []ExtensionDeclaration `json:"extensions"`
	Symbols    []SymbolDefinition     `json:"symbols"`
}

type FormatDeclaration struct {
	Node       string     `json:"node"`
	Cortex     string     `json:"cortex"`
	Encoding   string     `json:"encoding"`
	Attributes []AttrPair `json:"attributes"`
	SourceLine SourceLine `json:"sourceLine"`
}

type MetaDeclaration struct {
	Node       string     `json:"node"`
	Name       string     `json:"name"`
	Attributes []AttrPair `json:"attributes"`
	SourceLine SourceLine `json:"sourceLine"`
}

type EnumDeclaration struct {
	Node       string   `json:"node"`
	Name       string   `json:"name"`
	Values     []string `json:"values"`
	SourceLine SourceLine `json:"sourceLine"`
}

type MicroDeclaration struct {
	Node       string     `json:"node"`
	Token      string     `json:"token"`
	Expand     string     `json:"expand"`
	SourceLine SourceLine `json:"sourceLine"`
}

type NamespaceDeclaration struct {
	Node       string     `json:"node"`
	Alias      string     `json:"alias"`
	ID         string     `json:"id"`
	Version    *string    `json:"version"`
	Attributes []AttrPair `json:"attributes"`
	SourceLine SourceLine `json:"sourceLine"`
}

type ExtensionDeclaration struct {
	Node       string     `json:"node"`
	Name       string     `json:"name"`
	Namespace  string     `json:"namespace"`
	ID         string     `json:"id"`
	Version    string     `json:"version"`
	Required   bool       `json:"required"`
	Attributes []AttrPair `json:"attributes"`
	SourceLine SourceLine `json:"sourceLine"`
}

type SymbolDefinition struct {
	Node        string          `json:"node"`
	Surface     string          `json:"surface"`
	Namespace   *string         `json:"namespace"`
	Qualified   string          `json:"qualified"`
	Label       string          `json:"label"`
	Shape       string          `json:"shape"`
	Weight      string          `json:"weight"`
	Focus       string          `json:"focus"`
	Description string          `json:"description"`
	Open        bool            `json:"open"`
	Contract    []ContractField `json:"contract"`
	Attributes  []AttrPair      `json:"attributes"`
	SourceLine  SourceLine      `json:"sourceLine"`
}

type ContractField struct {
	Name     string `json:"name"`
	Type     string `json:"type"`
	Required bool   `json:"required"`
}

type Section struct {
	Node  string  `json:"node"`
	ID    int     `json:"id"`
	Title *string `json:"title"`
	Ideas []Idea  `json:"ideas"`
}

type Idea struct {
	Node            string      `json:"node"`
	Address         string      `json:"address"`
	Section         int         `json:"section"`
	Symbol          string      `json:"symbol"`
	QualifiedSymbol string      `json:"qualifiedSymbol"`
	Name            string      `json:"name"`
	Function        FunctionDef `json:"function"`
	Shape           string      `json:"shape"`
	Payload         interface{} `json:"payload"`
	SourceLine      SourceLine  `json:"sourceLine"`
}

type FunctionDef struct {
	Label  string `json:"label"`
	Weight string `json:"weight"`
	Focus  string `json:"focus"`
}

type AttrPair struct {
	Node  string `json:"node"`
	Key   string `json:"key"`
	Value Scalar `json:"value"`
}

type Scalar struct{ raw json.RawMessage }

func (s Scalar) MarshalJSON() ([]byte, error) { return s.raw, nil }

type AttrsPayload struct {
	Node  string     `json:"node"`
	Pairs []AttrPair `json:"pairs"`
}

type PositionalPayload struct {
	Node  string       `json:"node"`
	Cells []Scalar     `json:"cells"`
	Bound []BoundValue `json:"bound"`
}

type RelationPayload struct {
	Node  string       `json:"node"`
	Cells []Scalar     `json:"cells"`
	Bound []BoundValue `json:"bound"`
}

type BoundValue struct {
	Field string `json:"field"`
	Value Scalar `json:"value"`
}

type TextPayload struct {
	Node string `json:"node"`
	Text string `json:"text"`
}

type BlockPayload struct {
	Node string `json:"node"`
	Text string `json:"text"`
}

// ─── Diagnostics ────────────────────────────────────────────────────────────

type Diag struct {
	Code     string      `json:"code"`
	Severity string      `json:"severity"`
	Span     DiagSpan    `json:"span"`
	Message  string      `json:"message"`
}

type DiagSpan struct {
	Line   int `json:"line"`
	Column int `json:"column"`
}

var diags []Diag

func addDiag(code, sev, msg string, line, col int) {
	diags = append(diags, Diag{Code: code, Severity: sev, Span: DiagSpan{Line: line, Column: col}, Message: msg})
}

func fatalDiag(code, sev, msg string, line, col int) {
	addDiag(code, sev, msg, line, col)
	emitDiags()
	os.Exit(1)
}

func emitDiags() {
	if len(diags) == 0 {
		return
	}
	b, _ := json.MarshalIndent(diags, "", "  ")
	os.Stderr.Write(b)
	os.Stderr.WriteString("\n")
}

// ─── Parser globals ──────────────────────────────────────────────────────────

var micros = map[string]string{}
var enums = map[string][]string{}
var symbols = map[string]*SymbolDefinition{}
var sectionIDs = map[int]bool{}
var addresses = map[string]bool{}
var formatLine int

// ─── Main ────────────────────────────────────────────────────────────────────

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "Usage: cortex01 <file.cortex>")
		os.Exit(1)
	}
	data, err := os.ReadFile(os.Args[1])
	if err != nil {
		fatalDiag("S999_INTERNAL_PARSE_FAILURE", "error", fmt.Sprintf("Cannot read file: %v", err), 0, 0)
	}

	content := strings.ReplaceAll(string(data), "\r\n", "\n")

	// BOM check
	if len(content) >= 3 && content[0] == 0xEF && content[1] == 0xBB && content[2] == 0xBF {
		fatalDiag("U001_BOM_FORBIDDEN", "error", "UTF-8 BOM presente.", 1, 1)
	}

	// Control character check
	for i, r := range content {
		if r < 0x20 && r != '\n' && r != '\t' {
			line := strings.Count(content[:i], "\n") + 1
			fatalDiag("U002_CONTROL_CHARACTER", "error", fmt.Sprintf("Control character U+%04X.", r), line, 1)
		}
	}

	lines := strings.Split(content, "\n")

	// Phase 1: Parse $0 glossary
	parseGlossary(lines)

	// Phase 2: Parse sections and ideas
	sections := parseSections(lines)

	// Phase 3: Build output
	buildOutput(lines, sections)
}

// ─── Phase 1: Glossary ───────────────────────────────────────────────────────

func parseGlossary(lines []string) {
	found := false
	for i, raw := range lines {
		line := strings.TrimSpace(raw)
		ln := i + 1
		if line == "" || isComment(raw) {
			continue
		}
		if line == "$0" {
			found = true
			continue
		}
		if !found {
			// Content before $0
			if strings.HasPrefix(line, "$") {
				fatalDiag("G001_GLOSSARY_MISSING_OR_NOT_FIRST", "error", "$0 ausente o no es primero.", ln, 1)
			}
			continue // skip leading blanks/comments
		}
		// Section header = end of glossary
		if strings.HasPrefix(line, "$") && len(line) > 1 && line[1] >= '1' && line[1] <= '9' {
			break
		}
		// $0 re-opened
		if line == "$0" {
			fatalDiag("G002_GLOSSARY_REOPENED", "error", "$0 reaparece.", ln, 1)
		}

		// Parse line
		if strings.HasPrefix(line, "$0:") {
			parseMetaDecl(raw, ln)
		} else if colonIdx := strings.Index(line, ":"); colonIdx > 0 {
			parseSigilDecl(raw, ln)
		} else {
			fatalDiag("G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS", "error", "Glosario debe usar attrs.", ln, 1)
		}
	}
	if !found {
		fatalDiag("S001_EMPTY_DOCUMENT", "error", "Documento vacío.", 1, 1)
	}
}

func isComment(line string) bool {
	return strings.HasPrefix(strings.TrimLeft(line, " \t"), "#")
}

func parseMetaDecl(raw string, ln int) {
	trimmed := strings.TrimLeft(raw, " \t")
	// $0:name{...}
	rest := trimmed[3:]
	nameEnd := strings.IndexAny(rest, "{")
	if nameEnd < 0 {
		fatalDiag("G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS", "error", "Meta-decl sin payload.", ln, 1)
	}
	name := strings.TrimSpace(rest[:nameEnd])
	if !validName(name) {
		fatalDiag("L002_INVALID_NAME", "error", fmt.Sprintf("Nombre '%s' inválido.", name), ln, 1)
	}
	pairsStr := braceContent(trimmed, ln)
	pairs := parsePairs(pairsStr, ln)

	switch {
	case name == "format":
		parseFormat(pairs, ln)
	case strings.HasPrefix(name, "enum_"):
		parseEnum(name[5:], pairs, ln)
	case strings.HasPrefix(name, "micro_"):
		parseMicro(name[6:], pairs, ln)
	case strings.HasPrefix(name, "namespace_"):
		parseNamespace(name[10:], pairs, ln)
	case strings.HasPrefix(name, "extension_"):
		parseExtension(name[10:], pairs, ln)
	}
}

func parseFormat(pairs []AttrPair, ln int) {
	if formatLine > 0 {
		fatalDiag("G006_DUPLICATE_FORMAT", "error", "Duplicado $0:format.", ln, 1)
	}
	formatLine = ln
	var cv, enc string
	for _, p := range pairs {
		switch p.Key {
		case "cortex":
			cv = scalarStr(p.Value)
		case "encoding":
			enc = scalarStr(p.Value)
		}
	}
	if cv != "0.1" {
		fatalDiag("G007_UNSUPPORTED_VERSION", "error", fmt.Sprintf("Versión '%s'.", cv), ln, 1)
	}
	if enc != "UTF-8" {
		fatalDiag("G011_ENCODING_REQUIRED", "error", fmt.Sprintf("Encoding '%s'.", enc), ln, 1)
	}
}

func parseEnum(name string, pairs []AttrPair, ln int) {
	if _, dup := enums[name]; dup {
		fatalDiag("G015_DUPLICATE_ENUM", "error", fmt.Sprintf("Enum '%s' duplicado.", name), ln, 1)
	}
	var vs string
	for _, p := range pairs {
		if p.Key == "values" {
			vs = scalarStr(p.Value)
		}
	}
	if vs == "" {
		fatalDiag("G014_INVALID_ENUM", "error", fmt.Sprintf("Enum '%s' sin values.", name), ln, 1)
	}
	vals := strings.Split(vs, "|")
	seen := map[string]bool{}
	var clean []string
	for _, v := range vals {
		v = strings.TrimSpace(v)
		if v == "" { continue }
		if seen[v] { fatalDiag("G014_INVALID_ENUM", "error", fmt.Sprintf("Enum '%s' value dup: %s.", name, v), ln, 1) }
		seen[v] = true
		clean = append(clean, v)
	}
	if len(clean) == 0 {
		fatalDiag("G014_INVALID_ENUM", "error", fmt.Sprintf("Enum '%s' vacío.", name), ln, 1)
	}
	enums[name] = clean
}

func parseMicro(token string, pairs []AttrPair, ln int) {
	if _, dup := micros[token]; dup {
		fatalDiag("G013_DUPLICATE_MICRO", "error", fmt.Sprintf("Micro '%s' duplicado.", token), ln, 1)
	}
	var exp string
	for _, p := range pairs {
		if p.Key == "expand" {
			exp = scalarStr(p.Value)
		}
	}
	if exp == "" {
		fatalDiag("G012_INVALID_MICRO", "error", fmt.Sprintf("Micro '%s' sin expand.", token), ln, 1)
	}
	micros[token] = exp
}

func parseNamespace(alias string, pairs []AttrPair, ln int) { /* stored in meta */ }

func parseExtension(name string, pairs []AttrPair, ln int) {
	var id string
	var req bool
	hasNS, hasID, hasVer := false, false, false
	for _, p := range pairs {
		switch p.Key {
		case "namespace": _ = scalarStr(p.Value); hasNS = true
		case "id": id = scalarStr(p.Value); hasID = true
		case "version": _ = scalarStr(p.Value); hasVer = true
		case "required": req = scalarBool(p.Value)
		}
	}
	if !hasNS || !hasID || !hasVer {
		fatalDiag("X001_INVALID_EXTENSION_DECLARATION", "error", fmt.Sprintf("Ext '%s' incompleta.", name), ln, 1)
	}
	if req {
		fatalDiag("X002_REQUIRED_EXTENSION_UNSUPPORTED", "error", fmt.Sprintf("Ext requerida '%s' no soportada.", id), ln, 1)
	}
}

// ─── Sigil declaration ───────────────────────────────────────────────────────

func parseSigilDecl(raw string, ln int) {
	trimmed := strings.TrimLeft(raw, " \t")
	qidx := strings.Index(trimmed, "::")
	var symStr, label, nsPart string
	qualified := false
	if qidx > 0 {
		nsPart = trimmed[:qidx]
		rest := trimmed[qidx+2:]
		ci := strings.Index(rest, ":")
		if ci < 0 { fatalDiag("L001_INVALID_SYMBOL", "error", "Símbolo cualif. inválido.", ln, 1) }
		symStr = rest[:ci]
		label = labelFrom(rest[ci+1:])
		qualified = true
	} else {
		ci := strings.Index(trimmed, ":")
		if ci < 0 { fatalDiag("L001_INVALID_SYMBOL", "error", "Símbolo inválido.", ln, 1) }
		symStr = trimmed[:ci]
		label = labelFrom(trimmed[ci+1:])
	}

	if symStr != "!" && !validSigil(symStr) {
		fatalDiag("L001_INVALID_SYMBOL", "error", fmt.Sprintf("Símbolo '%s' inválido.", symStr), ln, 1)
	}
	if !validName(label) {
		fatalDiag("L002_INVALID_NAME", "error", fmt.Sprintf("Nombre '%s' inválido.", label), ln, 1)
	}

	surface := symStr
	qualifiedSym := symStr
	if qualified {
		surface = nsPart + "::" + symStr
		qualifiedSym = nsPart + "::" + symStr
	}
	if _, dup := symbols[surface]; dup {
		fatalDiag("G005_DUPLICATE_SYMBOL", "error", fmt.Sprintf("Símbolo '%s' duplicado.", surface), ln, 1)
	}

	pairsStr := braceContent(trimmed, ln)
	pairs := parsePairs(pairsStr, ln)

	var shape, weight, focus, desc string
	open := false
	hasFields, hasPos := false, false
	var contractStr string
	for _, p := range pairs {
		switch p.Key {
		case "type": shape = scalarStr(p.Value)
		case "weight": weight = scalarStr(p.Value)
		case "focus": focus = scalarStr(p.Value)
		case "desc": desc = scalarStr(p.Value)
		case "fields": contractStr = scalarStr(p.Value); hasFields = true
		case "pos": contractStr = scalarStr(p.Value); hasPos = true
		case "open": open = scalarBool(p.Value)
		case "namespace":
			if !qualified {
				ns := scalarStr(p.Value)
				if ns != "" {
					qualifiedSym = ns + "::" + symStr
				}
			}
		}
	}

	if shape == "" { fatalDiag("G016_SYMBOL_TYPE_REQUIRED", "error", fmt.Sprintf("'%s' sin type.", surface), ln, 1) }
	validShapes := map[string]bool{"attrs": true, "attrs-pos": true, "cuerpo": true, "bloque": true, "relacion": true}
	if !validShapes[shape] { fatalDiag("G017_UNKNOWN_SHAPE", "error", fmt.Sprintf("Shape '%s'.", shape), ln, 1) }
	if weight == "" { fatalDiag("G018_SYMBOL_WEIGHT_REQUIRED", "error", fmt.Sprintf("'%s' sin weight.", surface), ln, 1) }
	if !map[string]bool{"B": true, "M": true, "H": true}[weight] { fatalDiag("G019_INVALID_WEIGHT", "error", fmt.Sprintf("Weight '%s'.", weight), ln, 1) }
	if desc == "" { fatalDiag("G020_SYMBOL_DESCRIPTION_REQUIRED", "error", fmt.Sprintf("'%s' sin desc.", surface), ln, 1) }

	var contract []ContractField
	if shape == "attrs" {
		if !hasFields { fatalDiag("G021_ATTRS_CONTRACT_REQUIRED", "error", fmt.Sprintf("'%s' sin fields.", surface), ln, 1) }
		contract = parseContract(contractStr, ln)
	} else if shape == "attrs-pos" || shape == "relacion" {
		if !hasPos { fatalDiag("G022_POSITIONAL_CONTRACT_REQUIRED", "error", fmt.Sprintf("'%s' sin pos.", surface), ln, 1) }
		contract = parseContract(contractStr, ln)
		if shape == "relacion" && len(contract) < 3 {
			fatalDiag("G023_RELATION_CONTRACT_TOO_SHORT", "error", fmt.Sprintf("'%s' contrato corto.", surface), ln, 1)
		}
	}
	if shape == "cuerpo" || shape == "bloque" {
		if focus == "" { focus = "$body" }
	} else {
		if focus == "" { fatalDiag("G024_FOCUS_REQUIRED", "error", fmt.Sprintf("'%s' sin focus.", surface), ln, 1) }
		found := false
		for _, f := range contract {
			if f.Name == focus { found = true; break }
		}
		if !found { fatalDiag("G025_UNKNOWN_FOCUS_FIELD", "error", fmt.Sprintf("Focus '%s' no existe.", focus), ln, 1) }
	}

	var nsPtr *string
	if qualified && nsPart != "" {
		nsPtr = &nsPart
	} else if !qualified {
		for _, p := range pairs {
			if p.Key == "namespace" {
				ns := scalarStr(p.Value)
				if ns != "" { nsPtr = &ns }
			}
		}
	}

	sym := &SymbolDefinition{
		Node: "SymbolDefinition", Surface: surface, Namespace: nsPtr, Qualified: qualifiedSym,
		Label: label, Shape: shape, Weight: weight, Focus: focus, Description: desc,
		Open: open, Contract: contract, Attributes: pairs, SourceLine: SourceLine(ln),
	}
	symbols[surface] = sym
}

func labelFrom(s string) string {
	s = strings.TrimSpace(s)
	bi := strings.Index(s, "{")
	if bi >= 0 { return strings.TrimSpace(s[:bi]) }
	return s
}

// ─── Contract parsing ────────────────────────────────────────────────────────

func parseContract(s string, ln int) []ContractField {
	s = strings.TrimSpace(s)
	if s == "" { fatalDiag("G008_INVALID_CONTRACT", "error", "Contrato vacío.", ln, 1) }
	fields := strings.Split(s, "|")
	seen := map[string]bool{}
	var res []ContractField
	for _, f := range fields {
		f = strings.TrimSpace(f)
		if f == "" { continue }
		req := true
		if strings.HasSuffix(f, "?") {
			req = false
			f = f[:len(f)-1]
		}
		name, typ := f, "any"
		if ci := strings.Index(f, ":"); ci >= 0 {
			name = f[:ci]
			typ = f[ci+1:]
		}
		name = strings.TrimSpace(name)
		typ = strings.TrimSpace(typ)
		if name == "" { fatalDiag("G008_INVALID_CONTRACT", "error", "Field sin nombre.", ln, 1) }
		if seen[name] { fatalDiag("G009_DUPLICATE_CONTRACT_FIELD", "error", fmt.Sprintf("Field '%s' dup.", name), ln, 1) }
		seen[name] = true
		validTypes := map[string]bool{"any": true, "text": true, "atom": true, "int": true, "dec": true, "bool": true, "null": true, "list": true}
		if !validTypes[typ] {
			if strings.HasPrefix(typ, "%") {
				if _, ok := enums[typ[1:]]; !ok {
					fatalDiag("G026_UNKNOWN_ENUM_REFERENCE", "error", fmt.Sprintf("Enum '%s' no declarado.", typ[1:]), ln, 1)
				}
			} else {
				fatalDiag("G027_UNKNOWN_FIELD_TYPE", "error", fmt.Sprintf("Tipo '%s'.", typ), ln, 1)
			}
		}
		res = append(res, ContractField{Name: name, Type: typ, Required: req})
	}
	if len(res) == 0 { fatalDiag("G008_INVALID_CONTRACT", "error", "Contrato vacío.", ln, 1) }
	return res
}

// ─── Phase 2: Sections ───────────────────────────────────────────────────────

type bodyState struct {
	symbol string
	symDef *SymbolDefinition
	name   string
	lines  []string
	ln     int
	sec    *Section
}

func parseSections(lines []string) []Section {
	var sections []Section
	var cur *Section
	var body *bodyState

	for i, raw := range lines {
		ln := i + 1
		trimmed := strings.TrimSpace(raw)
		trimLeft := strings.TrimLeft(raw, " \t")

		// Skip empty lines and comments (outside body)
		if body == nil {
			if trimmed == "" || isComment(raw) { continue }
		}

		// Section header (skip $0)
		if body == nil && strings.HasPrefix(trimmed, "$") && len(trimmed) > 1 && trimmed[1] >= '1' && trimmed[1] <= '9' {
			if cur != nil { sections = append(sections, *cur) }
			cur = parseSection(trimmed, ln)
			continue
		}

		if body != nil {
			// Inside multiline body
			if trimmed == "}" {
				// Close body
				bodyText := strings.Join(body.lines, "\n")
				bodyText = strings.TrimRight(bodyText, "\n")
				idea := makeBodyIdea(body.symbol, body.symDef, body.name, bodyText, body.ln, body.sec)
				addr := fmt.Sprintf("$%d:%s:%s", body.sec.ID, body.symbol, body.name)
				if addresses[addr] { fatalDiag("I002_DUPLICATE_IDEA_ADDRESS", "error", fmt.Sprintf("Addr dup: %s.", addr), ln, 1) }
				addresses[addr] = true
				body.sec.Ideas = append(body.sec.Ideas, *idea)
				body = nil
				continue
			}
			body.lines = append(body.lines, raw)
			continue
		}

		// Regular idea line
		if cur == nil {
			// Skip glossary lines (still before first section)
			if trimmed == "$0" || strings.HasPrefix(trimLeft, "$0:") || (!strings.HasPrefix(trimLeft, "$") && strings.Contains(trimLeft, ":")) {
				continue
			}
			fatalDiag("S005_CONTENT_OUTSIDE_SECTION", "error", "Contenido fuera de sección.", ln, 1)
		}

		// Detect shape from payload delimiter
		symName, name, payload := splitIdeaHead(trimLeft, ln)
		if symName == "" { continue }

		sym := resolveSymbol(symName, ln)
		if sym == nil { continue }

		// Validate name
		if !validName(name) {
			fatalDiag("L002_INVALID_NAME", "error", fmt.Sprintf("Nombre '%s' inválido.", name), ln, 1)
		}

		payload = strings.TrimSpace(payload)

		// Determine shape
		switch sym.Shape {
		case "attrs":
			idea := parseAttrsIdea(symName, name, sym, payload, ln, cur)
			if idea == nil { continue }
			addr := fmt.Sprintf("$%d:%s:%s", cur.ID, idea.Symbol, idea.Name)
			if addresses[addr] { fatalDiag("I002_DUPLICATE_IDEA_ADDRESS", "error", fmt.Sprintf("Addr dup: %s.", addr), ln, 1) }
			addresses[addr] = true
			cur.Ideas = append(cur.Ideas, *idea)
		case "attrs-pos":
			idea := parsePosIdea(symName, name, sym, payload, ln, cur, false)
			if idea == nil { continue }
			addr := fmt.Sprintf("$%d:%s:%s", cur.ID, idea.Symbol, idea.Name)
			if addresses[addr] { fatalDiag("I002_DUPLICATE_IDEA_ADDRESS", "error", fmt.Sprintf("Addr dup: %s.", addr), ln, 1) }
			addresses[addr] = true
			cur.Ideas = append(cur.Ideas, *idea)
		case "relacion":
			idea := parsePosIdea(symName, name, sym, payload, ln, cur, true)
			if idea == nil { continue }
			addr := fmt.Sprintf("$%d:%s:%s", cur.ID, idea.Symbol, idea.Name)
			if addresses[addr] { fatalDiag("I002_DUPLICATE_IDEA_ADDRESS", "error", fmt.Sprintf("Addr dup: %s.", addr), ln, 1) }
			addresses[addr] = true
			cur.Ideas = append(cur.Ideas, *idea)
		case "cuerpo", "bloque":
			// Check if inline or multiline
			payload = strings.TrimSpace(payload)
			if !strings.HasPrefix(payload, "{") {
				fatalDiag("I004_SHAPE_DELIMITER_MISMATCH", "error", "Se esperaba {.", ln, 1)
			}
			// Find closing brace on same line
			closeIdx := findMatchingBrace(payload)
			if closeIdx >= 0 && !strings.Contains(payload[closeIdx+1:], "{") {
				// Inline
				inner := payload[1:closeIdx]
				idea := makeBodyIdea(symName, sym, name, inner, ln, cur)
				if sym.Shape == "cuerpo" {
					idea.Payload = TextPayload{Node: "TextPayload", Text: inner}
				} else {
					idea.Payload = BlockPayload{Node: "BlockPayload", Text: inner}
				}
				addr := fmt.Sprintf("$%d:%s:%s", cur.ID, idea.Symbol, idea.Name)
				if addresses[addr] { fatalDiag("I002_DUPLICATE_IDEA_ADDRESS", "error", fmt.Sprintf("Addr dup: %s.", addr), ln, 1) }
				addresses[addr] = true
				cur.Ideas = append(cur.Ideas, *idea)
			} else {
				// Start multiline body
				body = &bodyState{symbol: symName, symDef: sym, name: name, lines: []string{}, ln: ln, sec: cur}
			}
		default:
			fatalDiag("G017_UNKNOWN_SHAPE", "error", fmt.Sprintf("Shape '%s'.", sym.Shape), ln, 1)
		}
	}

	if cur != nil {
		sections = append(sections, *cur)
	}

	if body != nil {
		fatalDiag("I014_UNCLOSED_BODY", "error", "Cuerpo/bloque sin cerrar.", body.ln, 1)
	}

	return sections
}

func splitIdeaHead(s string, ln int) (sym, name, payload string) {
	qidx := strings.Index(s, "::")
	if qidx > 0 {
		ns := s[:qidx]
		rest := s[qidx+2:]
		ci := strings.Index(rest, ":")
		if ci < 0 { fatalDiag("S003_INVALID_IDEA_HEAD", "error", "Encabezado inválido.", ln, 1) }
		sym = ns + "::" + rest[:ci]
		after := rest[ci+1:]
		nameEnd := nameEndIdx(after)
		name = strings.TrimSpace(after[:nameEnd])
		payload = strings.TrimSpace(after[nameEnd:])
		return
	}
	ci := strings.Index(s, ":")
	if ci < 0 { fatalDiag("S003_INVALID_IDEA_HEAD", "error", "Encabezado inválido.", ln, 1) }
	sym = s[:ci]
	after := s[ci+1:]
	nameEnd := nameEndIdx(after)
	name = strings.TrimSpace(after[:nameEnd])
	payload = strings.TrimSpace(after[nameEnd:])
	return
}

func nameEndIdx(s string) int {
	for i, c := range s {
		if c == '{' || c == '|' || c == ' ' || c == '\t' { return i }
	}
	return len(s)
}

func resolveSymbol(name string, ln int) *SymbolDefinition {
	if sym, ok := symbols[name]; ok { return sym }
	// Try as qualified
	if _, ok := symbols[name]; !ok {
		fatalDiag("I001_UNDECLARED_SYMBOL", "error", fmt.Sprintf("Símbolo '%s' no declarado.", name), ln, 1)
	}
	return nil
}

func findMatchingBrace(s string) int {
	depth := 0
	for i, c := range s {
		if c == '{' { depth++ }
		if c == '}' {
			depth--
			if depth == 0 { return i }
		}
	}
	return -1
}

func parseSection(line string, ln int) *Section {
	trimmed := strings.TrimSpace(line)
	rest := trimmed[1:] // after $
	var idStr string
	var title *string
	if ci := strings.Index(rest, ":"); ci >= 0 {
		idStr = strings.TrimSpace(rest[:ci])
		ts := strings.TrimSpace(rest[ci+1:])
		if ts != "" { title = &ts }
	} else {
		idStr = strings.TrimSpace(rest)
	}
	id, err := strconv.Atoi(idStr)
	if err != nil || id < 1 {
		fatalDiag("S003_INVALID_IDEA_HEAD", "error", fmt.Sprintf("ID sección '%s'.", idStr), ln, 1)
	}
	if sectionIDs[id] {
		fatalDiag("S002_DUPLICATE_SECTION", "error", fmt.Sprintf("Sección %d dup.", id), ln, 1)
	}
	sectionIDs[id] = true
	return &Section{Node: "Section", ID: id, Title: title, Ideas: []Idea{}}
}

func makeBodyIdea(symbol string, sym *SymbolDefinition, name, text string, ln int, sec *Section) *Idea {
	payloadType := "TextPayload"
	nodeType := "TextPayload"
	if sym.Shape == "bloque" {
		payloadType = "BlockPayload"
		nodeType = "BlockPayload"
	}
	var pl interface{}
	if payloadType == "TextPayload" {
		pl = TextPayload{Node: nodeType, Text: text}
	} else {
		pl = BlockPayload{Node: nodeType, Text: text}
	}
	return &Idea{
		Node: "Idea", Address: fmt.Sprintf("$%d:%s:%s", sec.ID, symbol, name),
		Section: sec.ID, Symbol: symbol, QualifiedSymbol: symbol,
		Name: name, Function: FunctionDef{Label: sym.Label, Weight: sym.Weight, Focus: sym.Focus},
		Shape: sym.Shape, Payload: pl, SourceLine: SourceLine(ln),
	}
}

// ─── Attrs idea ──────────────────────────────────────────────────────────────

func parseAttrsIdea(symName, name string, sym *SymbolDefinition, payload string, ln int, sec *Section) *Idea {
	if payload == "" { fatalDiag("S004_MISSING_PAYLOAD", "error", "Attrs sin payload.", ln, 1) }
	if !strings.HasPrefix(payload, "{") {
		fatalDiag("I004_SHAPE_DELIMITER_MISMATCH", "error", "Se esperaba {.", ln, 1)
	}
	// Check single line
	if strings.Contains(payload, "\n") {
		fatalDiag("I003_ATTRS_MUST_BE_ONE_LINE", "error", "Attrs debe ser una línea.", ln, 1)
	}
	pairsStr := braceContent(payload, ln)
	pairs := parsePairs(pairsStr, ln)

	// Validate
	pairsMap := map[string]int{}
	for i, p := range pairs {
		if _, dup := pairsMap[p.Key]; dup {
			fatalDiag("I006_DUPLICATE_FIELD", "error", fmt.Sprintf("Field '%s' dup.", p.Key), ln, 1)
		}
		pairsMap[p.Key] = i
	}

	// Check unknown fields
	if !sym.Open {
		for _, p := range pairs {
			found := false
			for _, f := range sym.Contract { if f.Name == p.Key { found = true; break } }
			if !found { fatalDiag("I005_UNKNOWN_FIELD", "error", fmt.Sprintf("Campo '%s' desconocido.", p.Key), ln, 1) }
		}
	}

	// Check required fields and order
	lastIdx := -1
	for _, f := range sym.Contract {
		if idx, ok := pairsMap[f.Name]; ok {
			if idx < lastIdx { fatalDiag("I007_FIELD_ORDER", "error", fmt.Sprintf("'%s' fuera de orden.", f.Name), ln, 1) }
			lastIdx = idx
			checkType(pairs[idx].Value, f, ln)
		} else if f.Required {
			fatalDiag("I008_REQUIRED_FIELD_MISSING", "error", fmt.Sprintf("Falta campo '%s'.", f.Name), ln, 1)
		}
	}

	checkFocus(pairs, sym, ln)

	return &Idea{
		Node: "Idea", Address: fmt.Sprintf("$%d:%s:%s", sec.ID, symName, name),
		Section: sec.ID, Symbol: symName, QualifiedSymbol: sym.Qualified,
		Name: name, Function: FunctionDef{Label: sym.Label, Weight: sym.Weight, Focus: sym.Focus},
		Shape: sym.Shape, Payload: AttrsPayload{Node: "AttrsPayload", Pairs: pairs},
		SourceLine: SourceLine(ln),
	}
}

func checkFocus(pairs []AttrPair, sym *SymbolDefinition, ln int) {
	if sym.Focus == "$body" { return }
	found := false
	for _, p := range pairs {
		if p.Key == sym.Focus {
			found = true
			s, _ := json.Marshal(p.Value)
			var m map[string]interface{}
			json.Unmarshal(s, &m)
			if m["node"] == "StringValue" {
				if v, _ := m["value"].(string); v == "" {
					fatalDiag("I016_EMPTY_FOCUS", "error", fmt.Sprintf("Foco '%s' vacío.", sym.Focus), ln, 1)
				}
			}
			break
		}
	}
	if !found {
		fatalDiag("I015_FOCUS_VALUE_MISSING", "error", fmt.Sprintf("Foco '%s' no materializado.", sym.Focus), ln, 1)
	}
}

// ─── Positional idea ─────────────────────────────────────────────────────────

func parsePosIdea(symName, name string, sym *SymbolDefinition, payload string, ln int, sec *Section, isRel bool) *Idea {
	if payload == "" { fatalDiag("S004_MISSING_PAYLOAD", "error", "Idea sin payload.", ln, 1) }
	if !strings.HasPrefix(payload, "|") {
		if strings.HasPrefix(payload, "{") {
			fatalDiag("I004_SHAPE_DELIMITER_MISMATCH", "error", "Se esperaba |.", ln, 1)
		}
		fatalDiag("S004_MISSING_PAYLOAD", "error", "Idea sin payload.", ln, 1)
	}
	if strings.Contains(payload, "\n") {
		fatalDiag("I011_PIPE_IDEA_MUST_BE_ONE_LINE", "error", "Pipe idea debe ser una línea.", ln, 1)
	}

	cells := strings.Split(payload, "|")
	if len(cells) > 0 && cells[0] == "" { cells = cells[1:] }

	var cellVals []Scalar
	for _, c := range cells {
		c = strings.TrimSpace(c)
		if c == "" {
			cellVals = append(cellVals, Scalar{raw: rawStringVal("", "")})
			continue
		}
		if strings.HasPrefix(c, "\"") {
			end := findStrEnd(c)
			if end < 0 { fatalDiag("L005_INVALID_STRING", "error", "String sin cerrar.", ln, 1) }
			raw := c[1:end]
			lex := c[:end+1]
			cellVals = append(cellVals, Scalar{raw: rawStringVal(unescape(raw), lex)})
		} else {
			cellVals = append(cellVals, Scalar{raw: rawStringVal(c, c)})
		}
	}

	// Check arity
	minReq := 0
	for _, f := range sym.Contract { if f.Required { minReq++ } }
	maxF := len(sym.Contract)
	arityCode := "I012_POSITIONAL_ARITY"
	if isRel { arityCode = "I013_RELATION_ARITY" }
	if len(cellVals) < minReq || len(cellVals) > maxF {
		fatalDiag(arityCode, "error", fmt.Sprintf("%d cells, esperaba %d-%d.", len(cellVals), minReq, maxF), ln, 1)
	}

	// Build bound
	bound := []BoundValue{}
	for i, f := range sym.Contract {
		if i < len(cellVals) {
			checkType(cellVals[i], f, ln)
			bound = append(bound, BoundValue{Field: f.Name, Value: cellVals[i]})
		}
	}

	// Focus check for positional
	if sym.Focus != "$body" {
		focusFound := false
		for i, f := range sym.Contract {
			if f.Name == sym.Focus {
				focusFound = true
				if i < len(cellVals) {
					s, _ := json.Marshal(cellVals[i].raw)
					var m map[string]interface{}
					json.Unmarshal(s, &m)
					if m["node"] == "StringValue" {
						if v, _ := m["value"].(string); v == "" {
							fatalDiag("I016_EMPTY_FOCUS", "error", fmt.Sprintf("Foco '%s' vacío.", sym.Focus), ln, 1)
						}
					}
				}
				break
			}
		}
		if !focusFound {
			fatalDiag("I015_FOCUS_VALUE_MISSING", "error", fmt.Sprintf("Foco '%s' no materializado.", sym.Focus), ln, 1)
		}
	}

	if isRel {
		return &Idea{
			Node: "Idea", Address: fmt.Sprintf("$%d:%s:%s", sec.ID, symName, name),
			Section: sec.ID, Symbol: symName, QualifiedSymbol: sym.Qualified,
			Name: name, Function: FunctionDef{Label: sym.Label, Weight: sym.Weight, Focus: sym.Focus},
			Shape: sym.Shape, Payload: RelationPayload{Node: "RelationPayload", Cells: cellVals, Bound: bound},
			SourceLine: SourceLine(ln),
		}
	}
	return &Idea{
		Node: "Idea", Address: fmt.Sprintf("$%d:%s:%s", sec.ID, symName, name),
		Section: sec.ID, Symbol: symName, QualifiedSymbol: sym.Qualified,
		Name: name, Function: FunctionDef{Label: sym.Label, Weight: sym.Weight, Focus: sym.Focus},
		Shape: sym.Shape, Payload: PositionalPayload{Node: "PositionalPayload", Cells: cellVals, Bound: bound},
		SourceLine: SourceLine(ln),
	}
}

// ─── Type checking ───────────────────────────────────────────────────────────

func checkType(val Scalar, field ContractField, ln int) {
	s, _ := json.Marshal(val.raw)
	var m map[string]interface{}
	json.Unmarshal(s, &m)
	nt, _ := m["node"].(string)
	fieldType := field.Type
	switch fieldType {
	case "text":
		if nt != "StringValue" && nt != "AtomValue" {
			addDiag("I009_FIELD_TYPE_MISMATCH", "error", fmt.Sprintf("'%s' esperaba text, obtuvo %s.", field.Name, nt), ln, 1)
		}
	case "atom":
		if nt != "AtomValue" && nt != "StringValue" {
			addDiag("I009_FIELD_TYPE_MISMATCH", "error", fmt.Sprintf("'%s' esperaba atom.", field.Name), ln, 1)
		}
	case "int":
		if nt != "IntegerValue" { addDiag("I009_FIELD_TYPE_MISMATCH", "error", fmt.Sprintf("'%s' esperaba int.", field.Name), ln, 1) }
	case "dec":
		if nt != "DecimalValue" { addDiag("I009_FIELD_TYPE_MISMATCH", "error", fmt.Sprintf("'%s' esperaba dec.", field.Name), ln, 1) }
	case "bool":
		if nt != "BooleanValue" { addDiag("I009_FIELD_TYPE_MISMATCH", "error", fmt.Sprintf("'%s' esperaba bool.", field.Name), ln, 1) }
	case "null":
		if nt != "NullValue" { addDiag("I009_FIELD_TYPE_MISMATCH", "error", fmt.Sprintf("'%s' esperaba null.", field.Name), ln, 1) }
	case "list":
		if nt != "ListValue" { addDiag("I009_FIELD_TYPE_MISMATCH", "error", fmt.Sprintf("'%s' esperaba list.", field.Name), ln, 1) }
	default:
		if strings.HasPrefix(fieldType, "%") {
			enumName := fieldType[1:]
			if ev, ok := enums[enumName]; ok && nt == "AtomValue" {
				vs, _ := m["value"].(string)
				valid := false
				for _, v := range ev {
					if v == vs { valid = true; break }
				}
				if !valid {
					fatalDiag("I010_ENUM_VIOLATION", "error", fmt.Sprintf("'%s' no en enum %s.", vs, enumName), ln, 1)
				}
			}
		}
	}
}

// ─── Scalar parsing ──────────────────────────────────────────────────────────

func rawStringVal(value, lexeme string) json.RawMessage {
	b, _ := json.Marshal(StringValue{Node: "StringValue", Value: value, Lexeme: lexeme})
	return json.RawMessage(b)
}

func parseScalar(s string, ln int) Scalar {
	s = strings.TrimSpace(s)
	if s == "" { return Scalar{raw: rawStringVal("", "")} }

	// String
	if strings.HasPrefix(s, "\"") {
		end := findStrEnd(s)
		if end < 0 { fatalDiag("L005_INVALID_STRING", "error", "String sin cerrar.", ln, 1) }
		raw := s[1:end]
		lex := s[:end+1]
		return Scalar{raw: rawStringVal(unescape(raw), lex)}
	}

	// List
	if strings.HasPrefix(s, "[") {
		return parseList(s, ln)
	}

	// Boolean
	switch s {
	case "true", "TRUE", "True":
		b, _ := json.Marshal(BooleanValue{Node: "BooleanValue", Value: true, Lexeme: s})
		return Scalar{raw: json.RawMessage(b)}
	case "false", "FALSE", "False":
		b, _ := json.Marshal(BooleanValue{Node: "BooleanValue", Value: false, Lexeme: s})
		return Scalar{raw: json.RawMessage(b)}
	}

	// Null
	switch s {
	case "null", "NULL", "Null":
		b, _ := json.Marshal(NullValue{Node: "NullValue", Value: nil, Lexeme: s})
		return Scalar{raw: json.RawMessage(b)}
	}

	// Number
	if isNumStart(s[0]) {
		if isDec(s) { return Scalar{raw: rawDecVal(s)} }
		if isInt(s) {
			cl := cleanIntStr(s)
			b, _ := json.Marshal(IntegerValue{Node: "IntegerValue", Value: cl, Lexeme: s})
			return Scalar{raw: json.RawMessage(b)}
		}
	}

	// Atom
	if validAtom(s) {
		// Micro expansion
		if exp, ok := micros[s]; ok {
			m := map[string]interface{}{"node": "AtomValue", "value": s, "lexeme": s, "micro": exp}
			b, _ := json.Marshal(m)
			return Scalar{raw: json.RawMessage(b)}
		}
		b, _ := json.Marshal(AtomValue{Node: "AtomValue", Value: s, Lexeme: s})
		return Scalar{raw: json.RawMessage(b)}
	}

	fatalDiag("L010_INVALID_ATOM", "error", fmt.Sprintf("Valor '%s'.", s), ln, 1)
	return Scalar{}
}

type StringValue struct {
	Node   string `json:"node"`
	Value  string `json:"value"`
	Lexeme string `json:"lexeme"`
}
type IntegerValue struct {
	Node   string `json:"node"`
	Value  string `json:"value"`
	Lexeme string `json:"lexeme"`
}
type DecimalValue struct {
	Node   string `json:"node"`
	Value  string `json:"value"`
	Lexeme string `json:"lexeme"`
}
type BooleanValue struct {
	Node   string `json:"node"`
	Value  bool   `json:"value"`
	Lexeme string `json:"lexeme"`
}
type NullValue struct {
	Node   string      `json:"node"`
	Value  interface{} `json:"value"`
	Lexeme string      `json:"lexeme"`
}
type ListValue struct {
	Node   string            `json:"node"`
	Items  []json.RawMessage `json:"items"`
	Lexeme string            `json:"lexeme"`
}
type AtomValue struct {
	Node   string  `json:"node"`
	Value  string  `json:"value"`
	Lexeme string  `json:"lexeme"`
	Micro  *string `json:"micro,omitempty"`
}

func rawDecVal(s string) json.RawMessage {
	b, _ := json.Marshal(DecimalValue{Node: "DecimalValue", Value: s, Lexeme: s})
	return json.RawMessage(b)
}

func parseList(s string, ln int) Scalar {
	depth := 0
	end := -1
	for i, c := range s {
		if c == '[' { depth++ }
		if c == ']' {
			depth--
			if depth == 0 { end = i; break }
		}
	}
	if end < 0 { fatalDiag("L007_INVALID_LIST", "error", "Lista sin cierre.", ln, 1) }
	inner := strings.TrimSpace(s[1:end])
	lex := s[:end+1]
	if inner == "" {
		b, _ := json.Marshal(ListValue{Node: "ListValue", Items: []json.RawMessage{}, Lexeme: lex})
		return Scalar{raw: json.RawMessage(b)}
	}
	items := splitComma(inner)
	var vals []json.RawMessage
	for _, item := range items {
		item = strings.TrimSpace(item)
		if item == "" { continue }
		if strings.HasPrefix(item, "[") { fatalDiag("L008_NESTED_LIST", "error", "Lista anidada.", ln, 1) }
		sc := parseScalarNoList(item, ln)
		vals = append(vals, sc.raw)
	}
	b, _ := json.Marshal(ListValue{Node: "ListValue", Items: vals, Lexeme: lex})
	return Scalar{raw: json.RawMessage(b)}
}

func parseScalarNoList(s string, ln int) Scalar {
	if strings.HasPrefix(s, "[") { fatalDiag("L008_NESTED_LIST", "error", "Lista anidada.", ln, 1) }
	return parseScalar(s, ln)
}

// ─── Parsers for pairs ──────────────────────────────────────────────────────

func parsePairs(s string, ln int) []AttrPair {
	s = strings.TrimSpace(s)
	if s == "" { return []AttrPair{} }
	parts := splitComma(s)
	var pairs []AttrPair
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part == "" { continue }
		ci := strings.Index(part, ":")
		if ci < 0 { fatalDiag("L003_INVALID_KEY", "error", fmt.Sprintf("Par inválido: %s.", part), ln, 1) }
		key := strings.TrimSpace(part[:ci])
		val := strings.TrimSpace(part[ci+1:])
		if !validKey(key) { fatalDiag("L003_INVALID_KEY", "error", fmt.Sprintf("Key '%s'.", key), ln, 1) }
		pairs = append(pairs, AttrPair{Node: "AttrPair", Key: key, Value: parseScalar(val, ln)})
	}
	return pairs
}

func braceContent(s string, ln int) string {
	bi := strings.Index(s, "{")
	if bi < 0 { return "" }
	depth := 0
	for i := bi; i < len(s); i++ {
		if s[i] == '{' { depth++ }
		if s[i] == '}' {
			depth--
			if depth == 0 { return s[bi+1 : i] }
		}
	}
	fatalDiag("S006_INVALID_ATTRS", "error", "Llaves no balanceadas.", ln, 1)
	return ""
}

func splitComma(s string) []string {
	var parts []string
	depth := 0
	inStr := false
	start := 0
	for i := 0; i < len(s); i++ {
		c := s[i]
		if inStr {
			if c == '\\' { i++; continue }
			if c == '"' { inStr = false }
			continue
		}
		if c == '"' { inStr = true; continue }
		if c == '[' || c == '{' { depth++; continue }
		if c == ']' || c == '}' { depth--; continue }
		if c == ',' && depth == 0 {
			parts = append(parts, s[start:i])
			start = i + 1
		}
	}
	if start <= len(s) { parts = append(parts, s[start:]) }
	return parts
}

func findStrEnd(s string) int {
	if !strings.HasPrefix(s, "\"") { return -1 }
	for i := 1; i < len(s); i++ {
		if s[i] == '\\' { i++; continue }
		if s[i] == '"' { return i }
	}
	return -1
}

func unescape(s string) string {
	var b strings.Builder
	for i := 0; i < len(s); i++ {
		if s[i] == '\\' && i+1 < len(s) {
			switch s[i+1] {
			case '"': b.WriteByte('"'); i++
			case '\\': b.WriteByte('\\'); i++
			case 'n': b.WriteByte('\n'); i++
			case 'r': b.WriteByte('\r'); i++
			case 't': b.WriteByte('\t'); i++
			case 'b': b.WriteByte('\b'); i++
			case 'f': b.WriteByte('\f'); i++
			case 'u':
				if i+5 < len(s) {
					h := s[i+2 : i+6]
					if v, err := strconv.ParseUint(h, 16, 32); err == nil {
						b.WriteRune(rune(v)); i += 5
					} else { b.WriteString("\\u" + h); i += 5 }
				} else { b.WriteByte(s[i]) }
			default: b.WriteByte(s[i])
			}
		} else { b.WriteByte(s[i]) }
	}
	return b.String()
}

// ─── Validation helpers ──────────────────────────────────────────────────────

var keyRx = regexp.MustCompile(`^[a-z_][a-z0-9_-]{0,63}$`)
var nameRx = regexp.MustCompile(`^[a-zA-Z_][a-zA-Z0-9_.-]{0,63}$`)
var sigilRx = regexp.MustCompile(`^[A-Z][A-Z0-9_]{0,15}$`)
var atomRx = regexp.MustCompile(`^(\$[1-9][0-9]*:)?[a-zA-Z_][a-zA-Z0-9_./:@+%$-]*$`)

func validKey(k string) bool { return keyRx.MatchString(k) }
func validName(n string) bool { return nameRx.MatchString(n) }
func validSigil(s string) bool { return sigilRx.MatchString(s) }

func validAtom(s string) bool {
	switch s {
	case "true", "TRUE", "True", "false", "FALSE", "False", "null", "NULL", "Null":
		return false
	}
	if strings.HasPrefix(s, "\"") { return false }
	if isInt(s) || isDec(s) { return false }
	return atomRx.MatchString(s)
}

func isNumStart(c byte) bool { return (c >= '0' && c <= '9') || c == '-' }

func isInt(s string) bool {
	if s == "" { return false }
	start := 0
	if s[0] == '-' { start = 1; if len(s) == 1 { return false } }
	if s[start] == '0' && len(s[start:]) > 1 { return false }
	for i := start; i < len(s); i++ {
		if s[i] < '0' || s[i] > '9' { return false }
	}
	return true
}

func cleanIntStr(s string) string {
	if s == "" { return s }
	neg := false
	start := 0
	if s[0] == '-' { neg = true; start = 1 }
	i := start
	for i < len(s)-1 && s[i] == '0' { i++ }
	r := s[i:]
	if neg { r = "-" + r }
	return r
}

func isDec(s string) bool {
	if s == "" { return false }
	start := 0
	if s[0] == '-' { start = 1; if len(s) == 1 { return false } }
	hasDot := false
	for i := start; i < len(s); i++ {
		if s[i] == '.' {
			if hasDot { return false }
			hasDot = true
		} else if s[i] < '0' || s[i] > '9' { return false }
	}
	return hasDot
}

func scalarStr(s Scalar) string {
	var m map[string]interface{}
	json.Unmarshal(s.raw, &m)
	v, _ := m["value"].(string)
	return v
}

func scalarBool(s Scalar) bool {
	var m map[string]interface{}
	json.Unmarshal(s.raw, &m)
	v, _ := m["value"].(bool)
	return v
}

// ─── Build output ────────────────────────────────────────────────────────────

func buildOutput(lines []string, sections []Section) {
	var metaDecls []MetaDeclaration
	var enumDecls []EnumDeclaration
	var microDecls []MicroDeclaration
	var nsDecls []NamespaceDeclaration
	var extDecls []ExtensionDeclaration
	var fmtDecl FormatDeclaration
	var symDefs []SymbolDefinition

	inGlossary := false
	for i, raw := range lines {
		ln := i + 1
		trimmed := strings.TrimSpace(raw)
		if trimmed == "" || isComment(raw) { continue }
		if trimmed == "$0" { inGlossary = true; continue }
		if !inGlossary { continue }
		if strings.HasPrefix(trimmed, "$") && len(trimmed) > 1 && trimmed[1] >= '1' && trimmed[1] <= '9' { break }

		trimLeft := strings.TrimLeft(raw, " \t")

		if strings.HasPrefix(trimLeft, "$0:") {
			rest := trimLeft[3:]
			ne := strings.IndexAny(rest, "{")
			if ne < 0 { continue }
			name := strings.TrimSpace(rest[:ne])
			pairsStr := braceContent(trimLeft, ln)
			pairs := parsePairs(pairsStr, ln)

			meta := MetaDeclaration{Node: "MetaDeclaration", Name: name, Attributes: pairs, SourceLine: SourceLine(ln)}
			metaDecls = append(metaDecls, meta)

			switch {
			case name == "format":
				fmtDecl = FormatDeclaration{Node: "FormatDeclaration", Cortex: "0.1", Encoding: "UTF-8", Attributes: pairs, SourceLine: SourceLine(ln)}
			case strings.HasPrefix(name, "enum_"):
				en := name[5:]
				vals := []string{}
				if v, ok := enums[en]; ok { vals = v }
				enumDecls = append(enumDecls, EnumDeclaration{Node: "EnumDeclaration", Name: en, Values: vals, SourceLine: SourceLine(ln)})
			case strings.HasPrefix(name, "micro_"):
				tok := name[6:]
				exp := ""
				if v, ok := micros[tok]; ok { exp = v }
				microDecls = append(microDecls, MicroDeclaration{Node: "MicroDeclaration", Token: tok, Expand: exp, SourceLine: SourceLine(ln)})
			case strings.HasPrefix(name, "namespace_"):
				ns := name[10:]
				var id, ver string
				for _, p := range pairs {
					if p.Key == "id" { id = scalarStr(p.Value) }
					if p.Key == "version" { ver = scalarStr(p.Value) }
				}
				vp := &ver
				if ver == "" { vp = nil }
				nsDecls = append(nsDecls, NamespaceDeclaration{Node: "NamespaceDeclaration", Alias: ns, ID: id, Version: vp, Attributes: pairs, SourceLine: SourceLine(ln)})
			case strings.HasPrefix(name, "extension_"):
				en := name[10:]
				var ns, id, ver string
				var req bool
				for _, p := range pairs {
					switch p.Key {
					case "namespace": ns = scalarStr(p.Value)
					case "id": id = scalarStr(p.Value)
					case "version": ver = scalarStr(p.Value)
					case "required": req = scalarBool(p.Value)
					}
				}
				extDecls = append(extDecls, ExtensionDeclaration{Node: "ExtensionDeclaration", Name: en, Namespace: ns, ID: id, Version: ver, Required: req, Attributes: pairs, SourceLine: SourceLine(ln)})
			}
		} else if colonIdx := strings.Index(trimLeft, ":"); colonIdx > 0 && !strings.HasPrefix(trimLeft, "$0:") {
			symStr := trimLeft[:colonIdx]
			if strings.Contains(symStr, "::") {
				symStr = extractQualSym(trimLeft, colonIdx)
			}
			if sym, ok := symbols[symStr]; ok && int(sym.SourceLine) == ln {
				symDefs = append(symDefs, *sym)
			} else {
				// Try scanning
				for _, s := range symbols {
					if int(s.SourceLine) == ln {
						symDefs = append(symDefs, *s)
						break
					}
				}
			}
		}
	}

	// Collect remaining symbols
	for _, sym := range symbols {
		already := false
		for _, sd := range symDefs {
			if sd.Surface == sym.Surface { already = true; break }
		}
		if !already {
			// Only include if sourceLine matches a glossary line
			// Hmm, let's just add all symbols
			symDefs = append(symDefs, *sym)
		}
	}

	// Build glossary
	gloss := Glossary{
		Node: "Glossary", Format: fmtDecl, Meta: metaDecls,
		Enums: enumDecls, Micros: microDecls,
		Namespaces: nsDecls, Extensions: extDecls, Symbols: symDefs,
	}

	// Ensure empty slices not null
	if gloss.Enums == nil { gloss.Enums = []EnumDeclaration{} }
	if gloss.Micros == nil { gloss.Micros = []MicroDeclaration{} }
	if gloss.Namespaces == nil { gloss.Namespaces = []NamespaceDeclaration{} }
	if gloss.Extensions == nil { gloss.Extensions = []ExtensionDeclaration{} }
	if gloss.Meta == nil { gloss.Meta = []MetaDeclaration{} }
	if gloss.Symbols == nil { gloss.Symbols = []SymbolDefinition{} }

	doc := Document{
		Node: "Document", CortexVersion: "0.1", Encoding: "UTF-8",
		Glossary: gloss, Sections: sections,
	}

	j, err := json.MarshalIndent(doc, "", "  ")
	if err != nil {
		fatalDiag("S999_INTERNAL_PARSE_FAILURE", "error", fmt.Sprintf("JSON error: %v", err), 1, 1)
	}
	fmt.Println(string(j))
}

func extractQualSym(s string, ci int) string {
	return s
}
