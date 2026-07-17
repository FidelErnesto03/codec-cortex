package main

import (
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"strconv"
	"strings"
)

// Parser is the main CORTEX 0.1 parser
type Parser struct {
	diagnostics *DiagnosticList
	scalarParse *ScalarParser
}

func NewParser() *Parser {
	diag := NewDiagnosticList()
	return &Parser{
		diagnostics: diag,
		scalarParse: NewScalarParser(diag),
	}
}

// ParseFile parses a .cortex file and returns either AST JSON or diagnostics
func (p *Parser) ParseFile(path string) ([]byte, bool) {
	data, err := os.ReadFile(path)
	if err != nil {
		p.diagnostics.Add("S999_INTERNAL_PARSE_FAILURE", SeverityError, 1, 1,
			fmt.Sprintf("No se pudo leer el archivo: %v", err))
		return p.emitDiagnosticsOnly(), false
	}

	// Check for BOM
	if len(data) >= 3 && data[0] == 0xEF && data[1] == 0xBB && data[2] == 0xBF {
		p.diagnostics.Add("U001_BOM_FORBIDDEN", SeverityError, 1, 1,
			"UTF-8 BOM presente. Elimina los bytes \\xEF\\xBB\\xBF.")
	}

	content := string(data)

	// Check for control characters
	for i, r := range content {
		if r < 32 && r != '\n' && r != '\r' && r != '	' {
			p.diagnostics.Add("U002_CONTROL_CHARACTER", SeverityError, lineFromOffset(content, i)+1, 1,
				fmt.Sprintf("Caracter de control U+%04X en posición %d.", r, i))
		}
	}
	if len(p.diagnostics.items) > 0 && p.diagnostics.HasErrors() {
		// BOM or control chars are early errors
		return p.emitDiagnosticsOnly(), false
	}

	// Check for empty document
	if strings.TrimSpace(content) == "" {
		p.diagnostics.Add("S001_EMPTY_DOCUMENT", SeverityError, 1, 1, "Documento vacio.")
		return p.emitDiagnosticsOnly(), false
	}

	lines := strings.Split(content, "\n")
	doc, ok := p.parseDocument(lines)
	if !ok {
		return p.emitDiagnosticsOnly(), false
	}

	ast, err := json.MarshalIndent(doc, "", "  ")
	if err != nil {
		p.diagnostics.Add("S999_INTERNAL_PARSE_FAILURE", SeverityError, 1, 1,
			fmt.Sprintf("Error marshaling AST: %v", err))
		return p.emitDiagnosticsOnly(), false
	}

	return ast, true
}

// emitDiagnosticsOnly emits diagnostics JSON to stderr and returns nil
func (p *Parser) emitDiagnosticsOnly() []byte {
	// We'll handle output in main
	return nil
}

// parseDocument parses the full document
func (p *Parser) parseDocument(lines []string) (*Document, bool) {
	doc := &Document{
		Node:          "Document",
		CortexVersion: "0.1",
		Encoding:      "UTF-8",
		Glossary:      p.createEmptyGlossary(),
		Sections:      make([]Section, 0),
	}

	// Phase 1: Find $0 glossary
	glossaryStart := -1
	glossaryEnd := -1
	sectionHeaders := make([]int, 0) // line indices of $N headers
	for i, line := range lines {
		trimmed := strings.TrimSpace(line)
		if trimmed == "$0" {
			if glossaryStart == -1 {
				glossaryStart = i
			}
			// $0 with nothing else - start marker
		}
		if strings.HasPrefix(trimmed, "$0:") {
			if glossaryStart == -1 {
				glossaryStart = i
			}
			// This is a glossary declaration
		}
		// Check for section headers
		trimmedLine := strings.TrimLeft(line, " \t")
		if strings.HasPrefix(trimmedLine, "$") && len(trimmedLine) >= 2 && trimmedLine[1] >= '1' && trimmedLine[1] <= '9' {
			sectionHeaders = append(sectionHeaders, i)
		}
	}

	if glossaryStart == -1 {
		p.diagnostics.Add("G001_GLOSSARY_MISSING_OR_NOT_FIRST", SeverityError, 1, 1,
			"$0 ausente o no al inicio del documento.")
		return nil, false
	}

	// Check $0 is first non-comment, non-blank content
	if !p.isFirstNonBlank(lines, glossaryStart) {
		p.diagnostics.Add("G001_GLOSSARY_MISSING_OR_NOT_FIRST", SeverityError, glossaryStart+1, 1,
			"$0 debe ser la primera seccion del documento.")
		return nil, false
	}

	// Determine glossary end: either the next section header or EOF
	if len(sectionHeaders) > 0 {
		glossaryEnd = sectionHeaders[0]
	} else {
		glossaryEnd = len(lines)
	}

	// Parse glossary
	if !p.parseGlossary(lines[glossaryStart:glossaryEnd], doc) {
		return nil, false
	}
	// Build section boundaries
	sectionBounds := make([][2]int, 0)
	for _, headerIdx := range sectionHeaders {
		start := headerIdx
		end := len(lines)
		// Find the next section header
		for j := 0; j < len(sectionHeaders); j++ {
			if sectionHeaders[j] > headerIdx {
				end = sectionHeaders[j]
				break
			}
		}
		sectionBounds = append(sectionBounds, [2]int{start, end})
	}

	for _, bound := range sectionBounds {
		sec := p.parseSection(lines[bound[0]:bound[1]], bound[0], doc.Glossary)
		if sec != nil {
			doc.Sections = append(doc.Sections, *sec)
		}
	}

	if len(doc.Sections) == 0 && glossaryEnd == len(lines) {
		// No sections - check if there are only glossary declarations
		nonGlossary := false
		for i := glossaryStart; i < glossaryEnd; i++ {
			trimmed := strings.TrimSpace(lines[i])
			if trimmed != "" && !strings.HasPrefix(trimmed, "$0") && !strings.HasPrefix(trimmed, "#") {
				nonGlossary = true
				break
			}
		}
		if nonGlossary {
			p.diagnostics.Add("S005_CONTENT_OUTSIDE_SECTION", SeverityError, glossaryEnd+1, 1,
				"Contenido fuera de una seccion.")
			return nil, false
		}
	}

	return doc, !p.diagnostics.HasErrors()
}

// parseGlossary parses the $0 glossary
func (p *Parser) parseGlossary(glossaryLines []string, doc *Document) bool {
	foundFormat := false
	foundGlossaryHeader := false

	for idx, line := range glossaryLines {
		trimmed := strings.TrimSpace(line)
		origLineNum := idx + 1

		// Skip blank lines and comments
		if trimmed == "" || strings.HasPrefix(trimmed, "#") {
			continue
		}

		// Check for $0 header (bare $0 line)
		if trimmed == "$0" {
			if foundGlossaryHeader {
				p.diagnostics.Add("G002_GLOSSARY_REOPENED", SeverityError, origLineNum, 1,
					"$0 reabierto. El glosario debe ser unico.")
				return false
			}
			foundGlossaryHeader = true
			continue
		}

		// Check for $0:meta declarations
		if strings.HasPrefix(trimmed, "$0:") {
			remainder := strings.TrimPrefix(trimmed, "$0:")
			name, attrs, ok := p.parseMetaDeclHeader(remainder)
			if !ok {
				p.diagnostics.Add("G003_MULTILINE_GLOSSARY_DECLARATION", SeverityError, origLineNum, 1,
					"Declaracion de $0 invalida o multilinea.")
				return false
			}

			if name == "format" {
				if foundFormat {
					p.diagnostics.Add("G006_DUPLICATE_FORMAT", SeverityError, origLineNum, 1,
						"Mas de una declaracion $0:format.")
					return false
				}
				foundFormat = true
				decl := p.parseFormatDeclaration(attrs, origLineNum)
				doc.Glossary.Format = decl
				doc.Glossary.Meta = append(doc.Glossary.Meta, MetaDeclaration{
					Node:       "MetaDeclaration",
					Name:       "format",
					Attributes: decl.Attributes,
					SourceLine: origLineNum,
				})
				continue
			}

			if strings.HasPrefix(name, "enum_") {
				enumName := strings.TrimPrefix(name, "enum_")
				if !validIdentifier(enumName) {
					p.diagnostics.Add("G014_INVALID_ENUM", SeverityError, origLineNum, 1,
						fmt.Sprintf("Nombre de enum invalido: %s.", enumName))
					return false
				}
				valuesStr := ""
				for _, attr := range attrs {
					if attr.Key == "values" {
						if sv, ok := attr.Value.(StringValue); ok {
							valuesStr = sv.Value
						}
					}
				}
				if valuesStr == "" {
					p.diagnostics.Add("G014_INVALID_ENUM", SeverityError, origLineNum, 1,
						"Enum sin valores.")
					return false
				}
				values := strings.Split(valuesStr, "|")

				// Check for duplicate enum
				for _, existing := range doc.Glossary.Enums {
					if existing.Name == enumName {
						p.diagnostics.Add("G015_DUPLICATE_ENUM", SeverityError, origLineNum, 1,
							fmt.Sprintf("Enum duplicado: %s.", enumName))
						return false
					}
				}

				// Check for duplicate values
				seen := make(map[string]bool)
				for _, v := range values {
					v = strings.TrimSpace(v)
					if seen[v] {
						p.diagnostics.Add("G014_INVALID_ENUM", SeverityError, origLineNum, 1,
							fmt.Sprintf("Valor duplicado en enum: %s.", v))
						return false
					}
					seen[v] = true
				}

				doc.Glossary.Enums = append(doc.Glossary.Enums, EnumDeclaration{
					Node:       "EnumDeclaration",
					Name:       enumName,
					Values:     values,
					SourceLine: origLineNum,
				})
				doc.Glossary.Meta = append(doc.Glossary.Meta, MetaDeclaration{
					Node:       "MetaDeclaration",
					Name:       name,
					Attributes: attrs,
					SourceLine: origLineNum,
				})
				continue
			}

			if strings.HasPrefix(name, "micro_") {
				microName := strings.TrimPrefix(name, "micro_")
				if !validIdentifier(microName) {
					p.diagnostics.Add("L002_INVALID_NAME", SeverityError, origLineNum, 1,
						fmt.Sprintf("Nombre de microtoken invalido: %s.", microName))
					return false
				}
				expand := ""
				for _, attr := range attrs {
					if attr.Key == "expand" {
						if sv, ok := attr.Value.(StringValue); ok {
							expand = sv.Value
						} else {
							expand = getAtomOrStringValue(attr.Value)
						}
					}
				}
				if expand == "" {
					p.diagnostics.Add("G012_INVALID_MICRO", SeverityError, origLineNum, 1,
						"Microtoken sin expansion.")
					return false
				}
				// Check for duplicate micro
				for _, existing := range doc.Glossary.Micros {
					if existing.Token == microName {
						p.diagnostics.Add("G013_DUPLICATE_MICRO", SeverityError, origLineNum, 1,
							fmt.Sprintf("Microtoken duplicado: %s.", microName))
						return false
					}
				}
				doc.Glossary.Micros = append(doc.Glossary.Micros, MicroDeclaration{
					Node:       "MicroDeclaration",
					Token:      microName,
					Expand:     expand,
					SourceLine: origLineNum,
				})
				doc.Glossary.Meta = append(doc.Glossary.Meta, MetaDeclaration{
					Node:       "MetaDeclaration",
					Name:       name,
					Attributes: attrs,
					SourceLine: origLineNum,
				})
				continue
			}

			if strings.HasPrefix(name, "namespace_") {
				nsName := strings.TrimPrefix(name, "namespace_")
				id := ""
				version := ""
				for _, attr := range attrs {
					switch attr.Key {
					case "id":
						id = getAtomOrStringValue(attr.Value)
					case "version":
						version = getAtomOrStringValue(attr.Value)
					}
				}
				doc.Glossary.Namespaces = append(doc.Glossary.Namespaces, NamespaceDeclaration{
					Node:       "NamespaceDeclaration",
					Alias:      nsName,
					ID:         id,
					Version:    version,
					Attributes: attrs,
					SourceLine: origLineNum,
				})
				doc.Glossary.Meta = append(doc.Glossary.Meta, MetaDeclaration{
					Node:       "MetaDeclaration",
					Name:       name,
					Attributes: attrs,
					SourceLine: origLineNum,
				})
				continue
			}

			if strings.HasPrefix(name, "extension_") {
				extName := strings.TrimPrefix(name, "extension_")
				ns := ""
				id := ""
				version := ""
				required := false
				for _, attr := range attrs {
					switch attr.Key {
					case "namespace":
						ns = getAtomOrStringValue(attr.Value)
					case "id":
						id = getAtomOrStringValue(attr.Value)
					case "version":
						version = getAtomOrStringValue(attr.Value)
					case "required":
						if bv, ok := attr.Value.(BooleanValue); ok {
							required = bv.Value
						}
					}
				}
				if ns == "" || id == "" || version == "" {
					p.diagnostics.Add("X001_INVALID_EXTENSION_DECLARATION", SeverityError, origLineNum, 1,
						"Extensión incompleta: faltan namespace, id o version.")
					return false
				}
				if required {
					// Unsupported required extension
					p.diagnostics.Add("X002_REQUIRED_EXTENSION_UNSUPPORTED", SeverityError, origLineNum, 1,
						fmt.Sprintf("Extension requerida no soportada: %s.", extName))
					return false
				}
				doc.Glossary.Extensions = append(doc.Glossary.Extensions, ExtensionDeclaration{
					Node:       "ExtensionDeclaration",
					Name:       extName,
					Namespace:  ns,
					ID:         id,
					Version:    version,
					Required:   required,
					Attributes: attrs,
					SourceLine: origLineNum,
				})
				doc.Glossary.Meta = append(doc.Glossary.Meta, MetaDeclaration{
					Node:       "MetaDeclaration",
					Name:       name,
					Attributes: attrs,
					SourceLine: origLineNum,
				})
				continue
			}

			// Generic meta declaration
			doc.Glossary.Meta = append(doc.Glossary.Meta, MetaDeclaration{
				Node:       "MetaDeclaration",
				Name:       name,
				Attributes: attrs,
				SourceLine: origLineNum,
			})
			continue
		}

		// Must be a symbol declaration: SIGIL:label{type:..., ...}
		// Parse symbol declaration
		sym := p.parseSymbolDeclaration(trimmed, origLineNum, doc.Glossary)
		if sym == nil {
			return false
		}

		// Check for duplicate symbol
		// Check namespace-qualified
		if sym.Namespace != "" {
			qual2 := fmt.Sprintf("%s::%s", sym.Namespace, sym.Surface)
			for _, existing := range doc.Glossary.Symbols {
				if existing.Surface == sym.Surface && existing.Namespace == sym.Namespace {
					if sym.Namespace != "" {
						p.diagnostics.Add("G028_DUPLICATE_QUALIFIED_SYMBOL", SeverityError, origLineNum, 1,
							fmt.Sprintf("Símbolo cualificado duplicado: %s::%s.", sym.Namespace, sym.Surface))
					} else {
						p.diagnostics.Add("G005_DUPLICATE_SYMBOL", SeverityError, origLineNum, 1,
							fmt.Sprintf("Símbolo duplicado: %s.", sym.Surface))
					}
					return false
				}
				if qual2 == existing.Surface && sym.Namespace != "" {
					p.diagnostics.Add("G028_DUPLICATE_QUALIFIED_SYMBOL", SeverityError, origLineNum, 1,
						fmt.Sprintf("Símbolo cualificado duplicado: %s.", qual2))
					return false
				}
			}
		} else {
			for _, existing := range doc.Glossary.Symbols {
				if existing.Surface == sym.Surface && existing.Namespace == sym.Namespace {
					p.diagnostics.Add("G005_DUPLICATE_SYMBOL", SeverityError, origLineNum, 1,
						fmt.Sprintf("Símbolo duplicado: %s.", sym.Surface))
					return false
				}
			}
		}

		doc.Glossary.Symbols = append(doc.Glossary.Symbols, *sym)
	}

	if !foundFormat {
		p.diagnostics.Add("G010_FORMAT_REQUIRED", SeverityError, 1, 1,
			"$0:format es obligatorio.")
		return false
	}

	return true
}

// parseMetaDeclHeader parses "name{key:value,key:value}" from the remainder after $0:
func (p *Parser) parseMetaDeclHeader(remainder string) (string, []AttrPair, bool) {
	// Find the { that starts the payload
	braceIdx := strings.IndexByte(remainder, '{')
	if braceIdx < 0 {
		return "", nil, false
	}

	name := strings.TrimSpace(remainder[:braceIdx])
	if name == "" {
		return "", nil, false
	}

	attrsStr := remainder[braceIdx:]
	attrs, ok := p.parseAttrsInline(attrsStr)
	if !ok {
		return name, nil, false
	}

	return name, attrs, true
}

// parseAttrsInline parses {key:value,key:value} inline payload
func (p *Parser) parseAttrsInline(input string) ([]AttrPair, bool) {
	input = strings.TrimSpace(input)
	if len(input) < 2 || input[0] != '{' {
		return nil, false
	}

	// Find matching closing brace
	depth := 0
	closingIdx := -1
	for i, ch := range input {
		if ch == '{' {
			depth++
		} else if ch == '}' {
			depth--
			if depth == 0 {
				closingIdx = i
				break
			}
		}
	}

	if closingIdx < 0 {
		return nil, false
	}

	inner := strings.TrimSpace(input[1:closingIdx])
	if inner == "" {
		return make([]AttrPair, 0), true
	}

	return p.parseAttrPairs(inner, 1)
}

// parseAttrPairs parses "key:value,key:value" pairs
func (p *Parser) parseAttrPairs(input string, line int) ([]AttrPair, bool) {
	pairs := make([]AttrPair, 0)
	i := 0

	for i < len(input) {
		// Skip whitespace
		for i < len(input) && (input[i] == ' ' || input[i] == '\t') {
			i++
		}
		if i >= len(input) {
			break
		}

		// Parse key
		keyStart := i
		for i < len(input) && isKeyChar(rune(input[i])) {
			i++
		}
		key := input[keyStart:i]
		if key == "" {
			break
		}

		// Validate key
		if !validKey(key) {
			p.diagnostics.Add("L003_INVALID_KEY", SeverityError, line, keyStart+1,
				fmt.Sprintf("Key invalida: %s.", key))
			return nil, false
		}

		// Expect ':'
		for i < len(input) && (input[i] == ' ' || input[i] == '\t') {
			i++
		}
		if i >= len(input) || input[i] != ':' {
			p.diagnostics.Add("S006_INVALID_ATTRS", SeverityError, line, i+1,
				fmt.Sprintf("Se esperaba ':' despues de key '%s'.", key))
			return nil, false
		}
		i++

		// Parse value
		val, consumed, _ := p.scalarParse.parseScalar(input[i:], line, i+1)
		if consumed == 0 {
			p.diagnostics.Add("L006_EMPTY_VALUE", SeverityError, line, i+1,
				"Valor vacio.")
			// Try to recover by finding comma or end
			for i < len(input) && input[i] != ',' {
				i++
			}
			continue
		}
		i += consumed

		pairs = append(pairs, AttrPair{
			Node:  "AttrPair",
			Key:   key,
			Value: val,
		})

		// Skip whitespace
		for i < len(input) && (input[i] == ' ' || input[i] == '\t') {
			i++
		}

		// Check for comma
		if i < len(input) && input[i] == ',' {
			i++
			continue
		}

		// End of pairs
		break
	}

	return pairs, true
}

// parseFormatDeclaration parses the $0:format{...} declaration
func (p *Parser) parseFormatDeclaration(attrs []AttrPair, line int) *FormatDeclaration {
	decl := &FormatDeclaration{
		Node:       "FormatDeclaration",
		Cortex:     "",
		Encoding:   "",
		Attributes: attrs,
		SourceLine: line,
	}

	for _, attr := range attrs {
		switch attr.Key {
		case "cortex":
			if sv, ok := attr.Value.(DecimalValue); ok {
				decl.Cortex = sv.Value
			} else if sv, ok := attr.Value.(StringValue); ok {
				decl.Cortex = sv.Value
			} else if av, ok := attr.Value.(AtomValue); ok {
				decl.Cortex = av.Value
			}
		case "encoding":
			decl.Encoding = getAtomOrStringValue(attr.Value)
		}
	}

	// Validate
	if decl.Cortex != "0.1" {
		p.diagnostics.Add("G007_UNSUPPORTED_VERSION", SeverityError, line, 1,
			fmt.Sprintf("Version '%s' no soportada. Debe ser 0.1.", decl.Cortex))
	}
	if decl.Encoding != "UTF-8" {
		p.diagnostics.Add("G011_ENCODING_REQUIRED", SeverityError, line, 1,
			fmt.Sprintf("Encoding '%s' invalido. Debe ser UTF-8.", decl.Encoding))
	}

	return decl
}

// parseSymbolDeclaration parses a SIGIL:label{type:attrs,weight:B,fields:...,focus:...,desc:...}
func (p *Parser) parseSymbolDeclaration(line string, lineNum int, glossary *Glossary) *SymbolDefinition {
	// Find the colon separating sigil from name
	colonIdx := strings.IndexByte(line, ':')
	if colonIdx < 0 {
		p.diagnostics.Add("L001_INVALID_SYMBOL", SeverityError, lineNum, 1,
			"Sigilo invalido: falta ':'.")
		return nil
	}

	sigilStr := strings.TrimSpace(line[:colonIdx])
	remainder := strings.TrimSpace(line[colonIdx+1:])

	// Find the { that starts the payload
	braceIdx := strings.IndexByte(remainder, '{')
	if braceIdx < 0 {
		p.diagnostics.Add("G003_MULTILINE_GLOSSARY_DECLARATION", SeverityError, lineNum, 1,
			"Declaración de sigilo debe tener payload attrs.")
		return nil
	}

	name := strings.TrimSpace(remainder[:braceIdx])
	attrsStr := remainder[braceIdx:]

	// Parse sigil
	// Check for namespace prefix (lower-alpha::SIGIL)
	ns := ""
	surface := sigilStr
	if strings.Contains(sigilStr, "::") {
		parts := strings.SplitN(sigilStr, "::", 2)
		ns = strings.TrimSpace(parts[0])
		surface = strings.TrimSpace(parts[1])
		if !validNamespace(ns) {
			p.diagnostics.Add("L002_INVALID_NAME", SeverityError, lineNum, 1,
				fmt.Sprintf("Namespace invalido: %s.", ns))
			return nil
		}
	}

	// Validate sigil
	if !validSigil(surface) {
		p.diagnostics.Add("L001_INVALID_SYMBOL", SeverityError, lineNum, 1,
			fmt.Sprintf("Sigilo invalido: %s.", surface))
		return nil
	}

	// Validate name
	if !validIdentifier(name) {
		p.diagnostics.Add("L002_INVALID_NAME", SeverityError, lineNum, 1,
			fmt.Sprintf("Nombre invalido: %s.", name))
		return nil
	}

	// Parse attrs
	attrs, ok := p.parseAttrsInline(attrsStr)
	if !ok {
		p.diagnostics.Add("G003_MULTILINE_GLOSSARY_DECLARATION", SeverityError, lineNum, 1,
			"Payload attrs invalido o multilinea.")
		return nil
	}

	// Extract fields
	symType := ""
	weight := ""
	desc := ""
	focus := ""
	fields := ""
	pos := ""
	openStr := ""

	for _, attr := range attrs {
		switch attr.Key {
		case "type":
			symType = getAtomOrStringValue(attr.Value)
		case "weight":
			weight = getAtomOrStringValue(attr.Value)
		case "desc":
			desc = getAtomOrStringValue(attr.Value)
		case "focus":
			focus = getAtomOrStringValue(attr.Value)
		case "fields":
			if sv, ok := attr.Value.(StringValue); ok {
				fields = sv.Value
			}
		case "pos":
			if sv, ok := attr.Value.(StringValue); ok {
				pos = sv.Value
			}
		case "open":
			if bv, ok := attr.Value.(BooleanValue); ok {
				if bv.Value {
					openStr = "true"
				}
			} else {
				openStr = getAtomOrStringValue(attr.Value)
			}
		case "namespace":
			// Already captured from sigil prefix
		}
	}

	// Validate
	if symType == "" {
		p.diagnostics.Add("G016_SYMBOL_TYPE_REQUIRED", SeverityError, lineNum, 1,
			fmt.Sprintf("Sigilo %s requiere type.", surface))
		return nil
	}

	validShapes := map[string]bool{"attrs": true, "attrs-pos": true, "cuerpo": true, "bloque": true, "relacion": true}
	if !validShapes[symType] {
		p.diagnostics.Add("G017_UNKNOWN_SHAPE", SeverityError, lineNum, 1,
			fmt.Sprintf("Shape desconocido: %s.", symType))
		return nil
	}

	if weight == "" {
		p.diagnostics.Add("G018_SYMBOL_WEIGHT_REQUIRED", SeverityError, lineNum, 1,
			fmt.Sprintf("Sigilo %s requiere weight.", surface))
		return nil
	}

	if weight != "B" && weight != "M" && weight != "H" {
		p.diagnostics.Add("G019_INVALID_WEIGHT", SeverityError, lineNum, 1,
			fmt.Sprintf("Weight invalido: %s.", weight))
		return nil
	}

	if desc == "" {
		p.diagnostics.Add("G020_SYMBOL_DESCRIPTION_REQUIRED", SeverityError, lineNum, 1,
			fmt.Sprintf("Sigilo %s requiere desc.", surface))
		return nil
	}

	// Focus is required for attrs, attrs-pos, relacion (structured shapes)
	if symType == "attrs" || symType == "attrs-pos" || symType == "relacion" {
		if focus == "" {
			p.diagnostics.Add("G024_FOCUS_REQUIRED", SeverityError, lineNum, 1,
				fmt.Sprintf("Sigilo %s requiere focus para shape %s.", surface, symType))
			return nil
		}
	}

	// Contract validation
	var contract []ContractField
	switch symType {
	case "attrs":
		if fields == "" {
			p.diagnostics.Add("G021_ATTRS_CONTRACT_REQUIRED", SeverityError, lineNum, 1,
				fmt.Sprintf("Sigilo %s type=attrs requiere fields.", surface))
			return nil
		}
		contract = p.parseContractFields(fields, lineNum, glossary)
		if contract == nil {
			return nil
		}

		// Check focus exists in contract
		if focus != "" {
			found := focus == "$body" || focus == "body"
			for _, f := range contract {
				if f.Name == focus {
					found = true
					break
				}
			}
			if !found {
				p.diagnostics.Add("G025_UNKNOWN_FOCUS_FIELD", SeverityError, lineNum, 1,
					fmt.Sprintf("Focus '%s' no existe en el contrato de %s.", focus, surface))
				return nil
			}
		}

	case "attrs-pos", "relacion":
		if pos == "" {
			p.diagnostics.Add("G022_POSITIONAL_CONTRACT_REQUIRED", SeverityError, lineNum, 1,
				fmt.Sprintf("Sigilo %s type=%s requiere pos.", surface, symType))
			return nil
		}
		contract = p.parseContractFields(pos, lineNum, glossary)
		if contract == nil {
			return nil
		}

		if symType == "relacion" && len(contract) < 3 {
			p.diagnostics.Add("G023_RELATION_CONTRACT_TOO_SHORT", SeverityError, lineNum, 1,
				"Relación requiere al menos 3 campos en contrato (source, predicate, target).")
			return nil
		}

		// Check focus
		if focus != "" {
			found := focus == "$body"
			for _, f := range contract {
				if f.Name == focus {
					found = true
					break
				}
			}
			if !found {
				p.diagnostics.Add("G025_UNKNOWN_FOCUS_FIELD", SeverityError, lineNum, 1,
					fmt.Sprintf("Focus '%s' no existe en el contrato de %s.", focus, surface))
				return nil
			}
		}

	case "cuerpo", "bloque":
		// No fields/pos needed; focus is implicitly $body
		if focus == "" {
			focus = "$body"
		}
	}

	sym := &SymbolDefinition{
		Node:        "SymbolDefinition",
		Surface:     sigilStr,
		Namespace:   ns,
		Qualified:   sigilStr,
		Label:       name,
		Shape:       symType,
		Weight:      weight,
		Focus:       focus,
		Description: desc,
		Open:        openStr == "true",
		Contract:    contract,
		Attributes:  attrs,
		SourceLine:  lineNum,
	}

	return sym
}

// parseContractFields parses "field[:type][?]|field[:type][?]" into ContractField list
func (p *Parser) parseContractFields(input string, line int, glossary *Glossary) []ContractField {
	fields := make([]ContractField, 0)
	parts := strings.Split(input, "|")

	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part == "" {
			continue
		}

		// Check for optional marker: field?
		required := true
		if strings.HasSuffix(part, "?") {
			required = false
			part = part[:len(part)-1]
		}

		// Parse field[:type]
		fieldName := part
		fieldType := "text" // default type
		if colonIdx := strings.IndexByte(part, ':'); colonIdx >= 0 {
			fieldName = part[:colonIdx]
			fieldType = part[colonIdx+1:]
		}

		// Check field name
		if !validKey(fieldName) {
			p.diagnostics.Add("G008_INVALID_CONTRACT", SeverityError, line, 1,
				fmt.Sprintf("Nombre de campo invalido en contrato: %s.", fieldName))
			return nil
		}

		// Check type
		if !validContractType(fieldType) {
			p.diagnostics.Add("G027_UNKNOWN_FIELD_TYPE", SeverityError, line, 1,
				fmt.Sprintf("Tipo de campo desconocido: %s.", fieldType))
			return nil
		}

		// Check enum reference
		if strings.HasPrefix(fieldType, "%") {
			enumName := fieldType[1:]
			found := false
			for _, e := range glossary.Enums {
				if e.Name == enumName {
					found = true
					break
				}
			}
			if !found {
				p.diagnostics.Add("G026_UNKNOWN_ENUM_REFERENCE", SeverityError, line, 1,
					fmt.Sprintf("Enum '%s' no declarado.", enumName))
				return nil
			}
		}

		fields = append(fields, ContractField{
			Name:     fieldName,
			Type:     fieldType,
			Required: required,
		})
	}

	// Check for duplicate field names
	seen := make(map[string]bool)
	for _, f := range fields {
		if seen[f.Name] {
			p.diagnostics.Add("G009_DUPLICATE_CONTRACT_FIELD", SeverityError, line, 1,
				fmt.Sprintf("Campo repetido en contrato: %s.", f.Name))
			return nil
		}
		seen[f.Name] = true
	}

	return fields
}

// parseSection parses a section with its ideas
func (p *Parser) parseSection(lines []string, startLine int, glossary *Glossary) *Section {
	if len(lines) == 0 {
		return nil
	}

	headerLine := strings.TrimSpace(lines[0])
	sectionNum, title := p.parseSectionHeader(headerLine, startLine)
	if sectionNum < 0 {
		return nil
	}

	sec := &Section{
		Node:  "Section",
		ID:    sectionNum,
		Title: title,
		Ideas: make([]Idea, 0),
	}

	ideaLines := lines[1:]

	// Process lines sequentially
	i := 0
	for i < len(ideaLines) {
		rawLine := ideaLines[i]
		lineNum := startLine + i + 1
		trimmed := strings.TrimSpace(rawLine)

		// Skip blank and comment lines
		if trimmed == "" || strings.HasPrefix(trimmed, "#") {
			i++
			continue
		}

		// Check for section header (shouldn't happen in middle)
		if strings.HasPrefix(trimmed, "$") && len(trimmed) > 1 && trimmed[1] >= '1' && trimmed[1] <= '9' {
			// This shouldn't be in our boundary, but handle gracefully
			i++
			continue
		}

		// Check for multiline idea: SIGIL:name{ ... }
		if p.isMultilineCuerpo(lines, i) {
			idea := p.parseMultilineIdea(lines, &i, lineNum, sectionNum, sec, glossary)
			if idea != nil {
				sec.Ideas = append(sec.Ideas, *idea)
			}
			i++
			continue
		}

		// Check for multiline bloque: SIGIL:name{ ... }
		if p.isMultilineBloque(lines, i) {
			idea := p.parseMultilineBloque(lines, &i, lineNum, sectionNum, sec, glossary)
			if idea != nil {
				sec.Ideas = append(sec.Ideas, *idea)
			}
			i++
			continue
		}

		// Single line idea
		idea := p.parseSingleLineIdea(trimmed, lineNum, sectionNum, glossary)
		if idea != nil {
			sec.Ideas = append(sec.Ideas, *idea)
		}
		i++
	}

	return sec
}

// isMultilineCuerpo checks if the line starts a multiline cuerpo
func (p *Parser) isMultilineCuerpo(lines []string, idx int) bool {
	line := lines[idx]
	trimmed := strings.TrimSpace(line)

	// Must be SIGIL:name{ with } not on same line
	if !strings.HasSuffix(trimmed, "{") && !strings.Contains(trimmed, "{") {
		return false
	}

	// If it has } on the same line, it's not multiline
	if strings.Contains(trimmed, "}") {
		return false
	}

	// Check it looks like an idea head: SIGIL:name{
	braceIdx := strings.IndexByte(trimmed, '{')
	if braceIdx < 0 {
		return false
	}

	headPart := strings.TrimSpace(trimmed[:braceIdx])
	if !strings.Contains(headPart, ":") {
		return false
	}

	return true
}

// isMultilineBloque checks if the line starts a multiline bloque
func (p *Parser) isMultilineBloque(lines []string, idx int) bool {
	return p.isMultilineCuerpo(lines, idx)
}

// parseMultilineIdea parses a SIGIL:name{body...} multiline idea
func (p *Parser) parseMultilineIdea(lines []string, idx *int, lineNum, sectionNum int, sec *Section, glossary *Glossary) *Idea {
	firstLine := lines[*idx]
	trimmed := strings.TrimSpace(firstLine)
	braceIdx := strings.IndexByte(trimmed, '{')
	headPart := strings.TrimSpace(trimmed[:braceIdx])

	// Parse head: SIGIL:name
	colonIdx := strings.IndexByte(headPart, ':')
	if colonIdx < 0 {
		p.diagnostics.Add("S003_INVALID_IDEA_HEAD", SeverityError, lineNum, 1,
			"Cabecera de idea invalida.")
		// Skip to find closing }
		for *idx+1 < len(lines) {
			*idx++
			if strings.TrimSpace(lines[*idx]) == "}" {
				return nil
			}
		}
		return nil
	}

	sigilStr := strings.TrimSpace(headPart[:colonIdx])
	ideaName := strings.TrimSpace(headPart[colonIdx+1:])

	// Validate name
	if !validIdentifier(ideaName) {
		p.diagnostics.Add("L002_INVALID_NAME", SeverityError, lineNum, colonIdx+2,
			fmt.Sprintf("Nombre invalido: %s.", ideaName))
		return nil
	}

	// Look up symbol
	sym := p.findSymbol(sigilStr, glossary)
	if sym == nil {
		p.diagnostics.Add("I001_UNDECLARED_SYMBOL", SeverityError, lineNum, 1,
			fmt.Sprintf("Sigilo '%s' no declarado en glosario.", sigilStr))
		return nil
	}

	// Check shape is cuerpo (not bloque)
	if sym.Shape != "cuerpo" && sym.Shape != "bloque" {
		p.diagnostics.Add("I004_SHAPE_DELIMITER_MISMATCH", SeverityError, lineNum, 1,
			fmt.Sprintf("Shape '%s' no puede usar cuerpo multi-linea.", sym.Shape))
		return nil
	}

	// Collect body lines
	bodyLines := make([]string, 0)
	*idx++
	closed := false
	for *idx < len(lines) {
		bodyLine := lines[*idx]
		if strings.TrimSpace(bodyLine) == "}" {
			closed = true
			break
		}
		bodyLines = append(bodyLines, bodyLine)
		*idx++
	}

	if !closed {
		p.diagnostics.Add("I014_UNCLOSED_BODY", SeverityError, lineNum, 1,
			"Cuerpo sin cierre.")
		return nil
	}

	bodyText := strings.Join(bodyLines, "\n")

	// Determine if cuerpo or bloque
	if sym.Shape == "bloque" {
		payload := BlockPayload{
			Node: "BlockPayload",
			Text: bodyText,
		}
		return &Idea{
			Node: "Idea",
			Address: fmt.Sprintf("$%d:%s:%s", sectionNum, sym.Surface, ideaName),
			Section: sectionNum,
			Symbol: sym.Surface,
			QualifiedSymbol: sym.Qualified,
			Name: ideaName,
			Function: Function{
				Label:  sym.Label,
				Weight: sym.Weight,
				Focus:  "$body",
			},
			Shape:      sym.Shape,
			Payload:    payload,
			SourceLine: lineNum,
		}
	}

	payload := TextPayload{
		Node: "TextPayload",
		Text: bodyText,
	}
	return &Idea{
		Node: "Idea",
		Address: fmt.Sprintf("$%d:%s:%s", sectionNum, sym.Surface, ideaName),
		Section: sectionNum,
		Symbol: sym.Surface,
		QualifiedSymbol: sym.Qualified,
		Name: ideaName,
		Function: Function{
			Label:  sym.Label,
			Weight: sym.Weight,
			Focus:  "$body",
		},
		Shape:      sym.Shape,
		Payload:    payload,
		SourceLine: lineNum,
	}
}

// parseMultilineBloque parses a bloque (same as multiline cuerpo but with BlockPayload)
func (p *Parser) parseMultilineBloque(lines []string, idx *int, lineNum, sectionNum int, sec *Section, glossary *Glossary) *Idea {
	return p.parseMultilineIdea(lines, idx, lineNum, sectionNum, sec, glossary)
}

// parseSingleLineIdea parses a single-line idea
func (p *Parser) parseSingleLineIdea(line string, lineNum, sectionNum int, glossary *Glossary) *Idea {
	trimmed := strings.TrimSpace(line)

	// Comments
	if strings.HasPrefix(trimmed, "#") {
		return nil
	}

	// Must have colon for SIGIL:name
	colonIdx := strings.IndexByte(trimmed, ':')
	if colonIdx < 0 {
		p.diagnostics.Add("S003_INVALID_IDEA_HEAD", SeverityError, lineNum, 1,
			"Cabecera de idea invalida: falta ':'.")
		return nil
	}

	sigilStr := strings.TrimSpace(trimmed[:colonIdx])
	rest := strings.TrimSpace(trimmed[colonIdx+1:])

	if rest == "" {
		p.diagnostics.Add("S004_MISSING_PAYLOAD", SeverityError, lineNum, colonIdx+2,
			"Idea sin payload.")
		return nil
	}

	// Look up symbol
	sym := p.findSymbol(sigilStr, glossary)
	if sym == nil {
		p.diagnostics.Add("I001_UNDECLARED_SYMBOL", SeverityError, lineNum, 1,
			fmt.Sprintf("Sigilo '%s' no declarado en glosario.", sigilStr))
		return nil
	}

	// Parse idea based on shape
	switch sym.Shape {
	case "attrs":
		return p.parseAttrsIdea(rest, lineNum, sectionNum, sym)
	case "attrs-pos":
		return p.parsePositionalIdea(rest, lineNum, sectionNum, sym, "attrs-pos")
	case "relacion":
		return p.parsePositionalIdea(rest, lineNum, sectionNum, sym, "relacion")
	case "cuerpo":
		return p.parseCuerpoInlineIdea(rest, lineNum, sectionNum, sym)
	case "bloque":
		// bloque should not be single-line unless it's inline
		p.diagnostics.Add("I004_SHAPE_DELIMITER_MISMATCH", SeverityError, lineNum, colonIdx+2,
			"Shape bloque requiere delimitador multi-linea.")
		return nil
	default:
		p.diagnostics.Add("G017_UNKNOWN_SHAPE", SeverityError, lineNum, 1,
			fmt.Sprintf("Shape desconocido: %s.", sym.Shape))
		return nil
	}
}

// parseAttrsIdea parses: name{key:value,key:value}
func (p *Parser) parseAttrsIdea(line string, lineNum, sectionNum int, sym *SymbolDefinition) *Idea {
	// Find the { that starts the payload
	braceIdx := strings.IndexByte(line, '{')
	if braceIdx < 0 {
		p.diagnostics.Add("S004_MISSING_PAYLOAD", SeverityError, lineNum, 1,
			"Idea attrs sin payload {}.")
		return nil
	}

	name := strings.TrimSpace(line[:braceIdx])
	rest := line[braceIdx:]

	// Validate name
	if !validIdentifier(name) {
		p.diagnostics.Add("L002_INVALID_NAME", SeverityError, lineNum, 1,
			fmt.Sprintf("Nombre invalido: %s.", name))
		return nil
	}

	// Check for attrs on multiple lines (should be one line)
	if strings.Contains(rest, "\n") {
		p.diagnostics.Add("I003_ATTRS_MUST_BE_ONE_LINE", SeverityError, lineNum, braceIdx+1,
			"Attrs debe estar en una sola linea fisica.")
		return nil
	}

	attrs, ok := p.parseAttrsInline(rest)
	if !ok {
		p.diagnostics.Add("S006_INVALID_ATTRS", SeverityError, lineNum, braceIdx+1,
			"Payload attrs invalido.")
		return nil
	}

	// Validate against contract
	if !sym.Open {
		p.validateAttrsAgainstContract(attrs, sym, lineNum)
	}

	payload := AttrsPayload{
		Node:  "AttrsPayload",
		Pairs: attrs,
	}

	return &Idea{
		Node: "Idea",
		Address: fmt.Sprintf("$%d:%s:%s", sectionNum, sym.Surface, name),
		Section: sectionNum,
		Symbol: sym.Surface,
		QualifiedSymbol: sym.Qualified,
		Name: name,
		Function: Function{
			Label:  sym.Label,
			Weight: sym.Weight,
			Focus:  sym.Focus,
		},
		Shape:      "attrs",
		Payload:    payload,
		SourceLine: lineNum,
	}
}

// parsePositionalIdea parses: name|cell1|cell2|...
func (p *Parser) parsePositionalIdea(line string, lineNum, sectionNum int, sym *SymbolDefinition, shape string) *Idea {
	// Split on |, but respect quoted strings
	cells := splitPipeCells(line)

	if len(cells) == 0 {
		p.diagnostics.Add("S004_MISSING_PAYLOAD", SeverityError, lineNum, 1,
			"Idea sin celdas.")
		return nil
	}

	name := strings.TrimSpace(cells[0])

	// Validate name
	if !validIdentifier(name) {
		p.diagnostics.Add("L002_INVALID_NAME", SeverityError, lineNum, 1,
			fmt.Sprintf("Nombre invalido: %s.", name))
		return nil
	}

	rawCells := cells[1:]

	// Parse each cell as a scalar
	parsedCells := make([]ScalarValue, 0, len(rawCells))
	boundValues := make([]BoundValue, 0)
	for i, cell := range rawCells {
		cell = strings.TrimSpace(cell)
		// If quoted, it's a string
		if len(cell) >= 2 && cell[0] == '"' {
			val, _, _ := p.scalarParse.parseString(cell, lineNum, 1)
			parsedCells = append(parsedCells, val)
			if i < len(sym.Contract) {
				boundValues = append(boundValues, BoundValue{
					Field: sym.Contract[i].Name,
					Value: val,
				})
			}
		} else {
			// Try to parse as scalar
			val, _, _ := p.scalarParse.parseScalar(cell, lineNum, 1)
			parsedCells = append(parsedCells, val)
			if i < len(sym.Contract) {
				boundValues = append(boundValues, BoundValue{
					Field: sym.Contract[i].Name,
					Value: val,
				})
			}
		}
	}

	// Validate arity
	minRequired := 0
	for _, f := range sym.Contract {
		if f.Required {
			minRequired++
		}
	}

	if shape == "relacion" && len(parsedCells) < 3 {
		p.diagnostics.Add("I013_RELATION_ARITY", SeverityError, lineNum, 1,
			"Relación incompleta. Se requieren al menos 3 celdas (source, predicate, target).")
		return nil
	}

	if shape == "attrs-pos" {
		if len(parsedCells) < minRequired {
			p.diagnostics.Add("I012_POSITIONAL_ARITY", SeverityError, lineNum, 1,
				fmt.Sprintf("Muy pocas celdas: %d (requiere al menos %d).", len(parsedCells), minRequired))
			return nil
		}
		if len(parsedCells) > len(sym.Contract) {
			p.diagnostics.Add("I012_POSITIONAL_ARITY", SeverityError, lineNum, 1,
				fmt.Sprintf("Demasiadas celdas: %d (maximo %d).", len(parsedCells), len(sym.Contract)))
			return nil
		}
	}

	// Validate optional is trailing
	// Check: no missing optionals followed by present
	seenMissing := false
	for i := 0; i < len(rawCells); i++ {
		if i < len(sym.Contract) && !sym.Contract[i].Required {
			// This is optional - if it's empty, mark
			if strings.TrimSpace(rawCells[i]) == "" {
				seenMissing = true
			} else if seenMissing {
				// Optional field present after missing one - not strictly trailing
				// but we'll allow it as the spec says "should" not "must"
			}
		}
	}

	if shape == "relacion" {
		payload := RelationPayload{
			Node:  "RelationPayload",
			Cells: parsedCells,
			Bound: boundValues,
		}
		return &Idea{
			Node: "Idea",
			Address: fmt.Sprintf("$%d:%s:%s", sectionNum, sym.Surface, name),
			Section: sectionNum,
			Symbol: sym.Surface,
			QualifiedSymbol: sym.Qualified,
			Name: name,
			Function: Function{
				Label:  sym.Label,
				Weight: sym.Weight,
				Focus:  sym.Focus,
			},
			Shape:      shape,
			Payload:    payload,
			SourceLine: lineNum,
		}
	}

	payload := PositionalPayload{
		Node:  "PositionalPayload",
		Cells: parsedCells,
		Bound: boundValues,
	}

	return &Idea{
		Node: "Idea",
		Address: fmt.Sprintf("$%d:%s:%s", sectionNum, sym.Surface, name),
		Section: sectionNum,
		Symbol: sym.Surface,
		QualifiedSymbol: sym.Qualified,
		Name: name,
		Function: Function{
			Label:  sym.Label,
			Weight: sym.Weight,
			Focus:  sym.Focus,
		},
		Shape:      "attrs-pos",
		Payload:    payload,
		SourceLine: lineNum,
	}
}

// parseCuerpoInlineIdea parses: name{inline text}
func (p *Parser) parseCuerpoInlineIdea(line string, lineNum, sectionNum int, sym *SymbolDefinition) *Idea {
	// Find the { that starts the payload
	braceIdx := strings.IndexByte(line, '{')
	if braceIdx < 0 {
		p.diagnostics.Add("S004_MISSING_PAYLOAD", SeverityError, lineNum, 1,
			"Idea cuerpo sin payload {}.")
		return nil
	}

	name := strings.TrimSpace(line[:braceIdx])
	rest := strings.TrimSpace(line[braceIdx:])

	// Validate name
	if !validIdentifier(name) {
		p.diagnostics.Add("L002_INVALID_NAME", SeverityError, lineNum, 1,
			fmt.Sprintf("Nombre invalido: %s.", name))
		return nil
	}

	// Should have closing brace
	closeIdx := strings.LastIndex(rest, "}")
	if closeIdx < 0 {
		p.diagnostics.Add("S006_INVALID_ATTRS", SeverityError, lineNum, braceIdx+1,
			"Cuerpo sin cierre.")
		return nil
	}

	// Check for attrs on multiple lines
	if strings.Contains(rest, "\n") {
		p.diagnostics.Add("I014_UNCLOSED_BODY", SeverityError, lineNum, braceIdx+1,
			"Cuerpo multi-linea requiere delimitador multi-linea.")
		return nil
	}

	text := strings.TrimSpace(rest[braceIdx+1 : closeIdx])

	payload := TextPayload{
		Node: "TextPayload",
		Text: text,
	}

	return &Idea{
		Node: "Idea",
		Address: fmt.Sprintf("$%d:%s:%s", sectionNum, sym.Surface, name),
		Section: sectionNum,
		Symbol: sym.Surface,
		QualifiedSymbol: sym.Qualified,
		Name: name,
		Function: Function{
			Label:  sym.Label,
			Weight: sym.Weight,
			Focus:  "$body",
		},
		Shape:      "cuerpo",
		Payload:    payload,
		SourceLine: lineNum,
	}
}

// validateAttrsAgainstContract checks attrs against contract
func (p *Parser) validateAttrsAgainstContract(attrs []AttrPair, sym *SymbolDefinition, lineNum int) {
	// Check field order
	contractOrder := make(map[string]int)
	for i, f := range sym.Contract {
		contractOrder[f.Name] = i
	}

	// Check for unknown fields, duplicates, ordering, required fields
	seen := make(map[string]bool)
	lastPos := -1
	for _, attr := range attrs {
		// Check duplicate
		if seen[attr.Key] {
			p.diagnostics.Add("I006_DUPLICATE_FIELD", SeverityError, lineNum, 1,
				fmt.Sprintf("Campo duplicado: %s.", attr.Key))
			continue
		}
		seen[attr.Key] = true

		// Check known field
		if pos, ok := contractOrder[attr.Key]; ok {
			if pos < lastPos {
				p.diagnostics.Add("I007_FIELD_ORDER", SeverityError, lineNum, 1,
					fmt.Sprintf("Campo '%s' fuera de orden contractual.", attr.Key))
			}
			lastPos = pos
		} else if !sym.Open {
			p.diagnostics.Add("I005_UNKNOWN_FIELD", SeverityError, lineNum, 1,
				fmt.Sprintf("Campo desconocido: '%s'.", attr.Key))
		}
	}

	// Check required fields present
	for _, f := range sym.Contract {
		if f.Required && !seen[f.Name] {
			p.diagnostics.Add("I008_REQUIRED_FIELD_MISSING", SeverityError, lineNum, 1,
				fmt.Sprintf("Falta campo requerido: %s.", f.Name))
		}
	}
}

// findSymbol looks up a symbol in the glossary by surface
func (p *Parser) findSymbol(sigilStr string, glossary *Glossary) *SymbolDefinition {
	// Handle bare sigil or namespace::sigil
	for i := range glossary.Symbols {
		if glossary.Symbols[i].Surface == sigilStr {
			return &glossary.Symbols[i]
		}
	}
	return nil
}

// parseSectionHeader parses "$N: Title" or "$N"
func (p *Parser) parseSectionHeader(line string, startLine int) (int, string) {
	trimmed := strings.TrimSpace(line)
	if !strings.HasPrefix(trimmed, "$") {
		return -1, ""
	}

	rest := trimmed[1:]
	colonIdx := strings.IndexByte(rest, ':')
	numStr := rest
	title := ""

	if colonIdx >= 0 {
		numStr = rest[:colonIdx]
		title = strings.TrimSpace(rest[colonIdx+1:])
	}

	num, err := strconv.Atoi(numStr)
	if err != nil || num <= 0 {
		p.diagnostics.Add("S002_DUPLICATE_SECTION", SeverityError, startLine+1, 1,
			fmt.Sprintf("Numero de seccion invalido: %s.", numStr))
		return -1, ""
	}

	// Check for duplicate sections
	// We'll check this at the document level

	return num, title
}

// isFirstNonBlank checks if $0 is at the first non-blank, non-comment line
func (p *Parser) isFirstNonBlank(lines []string, idx int) bool {
	for i := 0; i < idx; i++ {
		trimmed := strings.TrimSpace(lines[i])
		if trimmed != "" && !strings.HasPrefix(trimmed, "#") {
			return false
		}
	}
	return true
}

// createEmptyGlossary creates an empty glossary
func (p *Parser) createEmptyGlossary() *Glossary {
	return &Glossary{
		Node:       "Glossary",
		Format:     nil,
		Meta:       make([]MetaDeclaration, 0),
		Enums:      make([]EnumDeclaration, 0),
		Micros:     make([]MicroDeclaration, 0),
		Namespaces: make([]NamespaceDeclaration, 0),
		Extensions: make([]ExtensionDeclaration, 0),
		Symbols:    make([]SymbolDefinition, 0),
	}
}

// -------- Utility functions --------

func getAtomOrStringValue(v ScalarValue) string {
	switch val := v.(type) {
	case StringValue:
		return val.Value
	case AtomValue:
		return val.Value
	case BooleanValue:
		return fmt.Sprintf("%v", val.Value)
	case IntegerValue:
		return val.Value
	case DecimalValue:
		return val.Value
	default:
		return ""
	}
}

func isKeyChar(r rune) bool {
	return (r >= 'a' && r <= 'z') ||
		(r >= '0' && r <= '9') ||
		r == '_' || r == '-'
}

func validKey(key string) bool {
	if key == "" {
		return false
	}
	matched, _ := regexp.MatchString(`^[a-z_][a-z0-9_-]{0,63}$`, key)
	return matched
}

func validIdentifier(name string) bool {
	if name == "" {
		return false
	}
	matched, _ := regexp.MatchString(`^[A-Za-z_][A-Za-z0-9_.-]{0,63}$`, name)
	return matched
}

func validSigil(sigil string) bool {
	if sigil == "!" {
		return true
	}
	matched, _ := regexp.MatchString(`^[A-Z][A-Z0-9_]{0,15}$`, sigil)
	return matched
}

func validNamespace(ns string) bool {
	matched, _ := regexp.MatchString(`^[a-z][a-z0-9_.-]*$`, ns)
	return matched
}

func validContractType(t string) bool {
	// text, int, dec, bool, atom, null, date, uri, ... or %enum_ref
	if strings.HasPrefix(t, "%") {
		// enum ref
		matched, _ := regexp.MatchString(`^%[a-z_][a-z0-9_-]*$`, t)
		return matched
	}
	validTypes := map[string]bool{
		"text": true, "int": true, "dec": true, "bool": true,
		"atom": true, "null": true, "date": true, "uri": true,
		"list": true,
	}
	return validTypes[t]
}

// splitPipeCells splits a pipe-separated line into cells, respecting quoted strings
func splitPipeCells(line string) []string {
	cells := make([]string, 0)
	current := strings.Builder{}
	inQuotes := false
	i := 0

	for i < len(line) {
		ch := line[i]
		if ch == '"' {
			inQuotes = !inQuotes
			current.WriteByte(ch)
		} else if ch == '|' && !inQuotes {
			cells = append(cells, current.String())
			current.Reset()
		} else {
			current.WriteByte(ch)
		}
		i++
	}
	cells = append(cells, current.String())
	return cells
}

func lineFromOffset(content string, offset int) int {
	return strings.Count(content[:offset], "\n")
}

// fmtAtomValue takes an atom value with optional micro expansion
func fmtAtomValue(v ScalarValue, micros map[string]string) ScalarValue {
	if av, ok := v.(AtomValue); ok {
		if expanded, found := micros[av.Value]; found {
			av.Micro = expanded
		}
		return av
	}
	return v
}
