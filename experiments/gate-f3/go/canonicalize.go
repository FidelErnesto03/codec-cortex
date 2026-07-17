package main

import (
	"crypto/sha256"
	"fmt"
	"sort"
	"strings"

	"golang.org/x/text/unicode/norm"
)

// -------- C14N-0.1 Canonicalization --------

// Canonicalize performs C14N-0.1 canonicalization on raw CORTEX bytes.
// Returns (canonical_bytes, report_json, ok).
func buildReport(raw, outBytes []byte, changes []string) map[string]interface{} {
	rawSHA := fmt.Sprintf("%x", sha256.Sum256(raw))
	canSHA := fmt.Sprintf("%x", sha256.Sum256(outBytes))
	chash := fmt.Sprintf("sha256:%x", sha256.Sum256(append([]byte("CORTEX-C14N-0.1\x00"), outBytes...)))
	return map[string]interface{}{
		"canonicalization":      "C14N-0.1",
		"inputSha256":           rawSHA,
		"canonicalSha256":       canSHA,
		"canonicalHash":         chash,
		"changed":               !bytesEqual(outBytes, raw),
		"structuralLoss":        false,
		"losses":                []string{},
		"sourceFidelityChanges": changes,
		"diagnostics":           []string{},
	}
}

func Canonicalize(raw []byte, doc *Document) ([]byte, map[string]interface{}, bool) {
	changes := make([]string, 0)

	// Handle nil doc gracefully
	if doc == nil {
		out := strings.ReplaceAll(string(raw), "\r\n", "\n")
		out = strings.ReplaceAll(out, "\r", "\n")
		canonical := []byte(out)
		report := buildReport(raw, canonical, changes)
		return canonical, report, true
	}

	// Detect changes
	rawText := string(raw)
	if strings.ContainsRune(rawText, '\r') {
		changes = append(changes, "newline-normalized")
	}

	// Normalize newlines for change detection
	normalizedText := strings.ReplaceAll(rawText, "\r\n", "\n")
	normalizedText = strings.ReplaceAll(normalizedText, "\r", "\n")

	// Check for comments
	hasComments := false
	for _, line := range strings.Split(normalizedText, "\n") {
		if strings.TrimSpace(line) != "" && strings.HasPrefix(strings.TrimSpace(line), "#") {
			hasComments = true
			break
		}
	}
	if hasComments {
		changes = append(changes, "comments-removed")
	}

	// Check for blank lines (internal, not last)
	allLines := strings.Split(normalizedText, "\n")
	hasInternalBlanks := false
	if len(allLines) > 1 {
		for _, l := range allLines[:len(allLines)-1] {
			if strings.TrimSpace(l) == "" {
				hasInternalBlanks = true
				break
			}
		}
	}
	if hasInternalBlanks {
		changes = append(changes, "blank-lines-removed")
	}

	// Check for NFC changes
	if docHasNFCChange(doc) {
		changes = append(changes, "unicode-normalized")
	}

	// Build canonical output
	outLines := make([]string, 0)
	outLines = append(outLines, "$0")

	// --- Canonical meta order ---
	orderedMetas := extractMetasOrdered(doc)
	originalMetaNames := make([]string, 0)
	for _, m := range doc.Glossary.Meta {
		originalMetaNames = append(originalMetaNames, m.Name)
	}

	orderedMetaNames := make([]string, 0)
	for _, m := range orderedMetas {
		orderedMetaNames = append(orderedMetaNames, m.Name)
	}
	if !stringSliceEqual(orderedMetaNames, originalMetaNames) {
		changes = addChange(changes, "glossary-order-normalized")
	}

	for _, meta := range orderedMetas {
		metaAttrs := extractMetaAttrs(meta.Name, doc)
		cat := metaCategory(meta.Name)
		var baseOrder []string
		switch cat.idx {
		case 0:
			baseOrder = []string{"cortex", "encoding", "language"}
		case 1:
			baseOrder = []string{"values"}
		case 2:
			baseOrder = []string{"expand"}
		case 3:
			baseOrder = []string{"id", "version", "required", "desc"}
		case 4:
			baseOrder = []string{"namespace", "id", "version", "required", "desc"}
		default:
			baseOrder = []string{}
		}

		keys := orderedKeys(metaAttrs, baseOrder)
		prevKeys := mapKeys(metaAttrs)
		if !stringSliceEqual(keys, prevKeys) {
			changes = addChange(changes, "attribute-order-normalized")
		}

		attrsStr := emitAttrsStr(keys, metaAttrs, doc.Glossary.Micros)
		outLines = append(outLines, fmt.Sprintf("$0:%s%s", meta.Name, attrsStr))
	}

	// --- Canonical symbol order ---
	orderedSymbols := extractSymbolsOrdered(doc)
	origSyms := make([]string, 0)
	for _, s := range doc.Glossary.Symbols {
		origSyms = append(origSyms, s.Surface)
	}
	newSyms := make([]string, 0)
	for _, s := range orderedSymbols {
		newSyms = append(newSyms, s.Surface)
	}
	if !stringSliceEqual(origSyms, newSyms) {
		changes = addChange(changes, "glossary-order-normalized")
	}

	for _, sd := range orderedSymbols {
		symbolOrder := []string{"type", "weight", "fields", "pos", "focus", "desc", "open", "namespace", "version"}
		symAttrs := extractSymbolAttrsMap(&sd)
		keys := orderedKeys(symAttrs, symbolOrder)
		prevKeys := mapKeys(symAttrs)
		if !stringSliceEqual(keys, prevKeys) {
			changes = addChange(changes, "attribute-order-normalized")
		}

		sigil := sd.Surface
		label := sd.Label
		attrsStr := emitAttrsStr(keys, symAttrs, doc.Glossary.Micros)
		outLines = append(outLines, fmt.Sprintf("%s:%s%s", sigil, label, attrsStr))
	}

	// --- Sections ---
	microMap := buildMicroMap(doc.Glossary.Micros)
	symbolMap := buildSymbolMap(doc.Glossary.Symbols)

	for _, sec := range doc.Sections {
		titleStr := ""
		if sec.Title != "" {
			nfcTitle := NFC(sec.Title)
			titleStr = fmt.Sprintf(": %s", nfcTitle)
		}
		outLines = append(outLines, fmt.Sprintf("$%d%s", sec.ID, titleStr))

		for _, idea := range sec.Ideas {
			shape := determineShape(idea, symbolMap)
			head := fmt.Sprintf("%s:%s", idea.QualifiedSymbol, idea.Name)

			switch shape {
			case "attrs":
				symDef, _ := symbolMap[idea.Symbol]
				contract := symDef.Contract
				contractNames := make([]string, 0, len(contract))
				for _, f := range contract {
					contractNames = append(contractNames, f.Name)
				}

				payloadMap := extractIdeaAttrsPayload(idea)
				extras := make([]string, 0)
				for k := range payloadMap {
					found := false
					for _, cn := range contractNames {
						if k == cn {
							found = true
							break
						}
					}
					if !found {
						extras = append(extras, k)
					}
				}
				sort.Slice(extras, func(i, j int) bool {
					return NFC(extras[i]) < NFC(extras[j])
				})

				keys := make([]string, 0)
				for _, cn := range contractNames {
					if _, ok := payloadMap[cn]; ok {
						keys = append(keys, cn)
					}
				}
				keys = append(keys, extras...)

				prevKeys := mapKeys(payloadMap)
				if !stringSliceEqual(keys, prevKeys) {
					changes = addChange(changes, "attribute-order-normalized")
				}

				// Check for microtoken expansion
				for _, k := range keys {
					if val, ok := payloadMap[k]; ok {
						if av, ok2 := val.(AtomValue); ok2 {
							if _, found := microMap[av.Value]; found {
								changes = addChange(changes, "microtoken-expanded")
							}
						}
					}
				}

				focus := symDef.Focus
				attrsStr := emitIdeaAttrs(keys, payloadMap, contract, focus, microMap)
				outLines = append(outLines, head+attrsStr)

			case "attrs-pos", "relacion":
				cells := extractPipeCells(idea)
				symDef, _ := symbolMap[idea.Symbol]
				contract := symDef.Contract

				cellStrs := make([]string, 0, len(cells))
				for idx, s := range cells {
					fieldType := "any"
					if idx < len(contract) {
						fieldType = contract[idx].Type
						if contract[idx].Required {
							// Type is already in fieldType
						}
					}

					ex := expandMicroScalar(s, microMap)

					// Check for microtoken expansion
					if av, ok := s.(AtomValue); ok {
						if _, found := microMap[av.Value]; found {
							changes = addChange(changes, "microtoken-expanded")
						}
					}

					baseType := strings.TrimSuffix(fieldType, "?")
					if baseType == "text" {
						valStr := getScalarText(ex)
						valNFC := NFC(valStr)
						if valNFC == "" || (!strings.ContainsRune(valNFC, '|') && !strings.ContainsRune(valNFC, '\n') && valNFC == strings.TrimSpace(valNFC) && !strings.HasPrefix(valNFC, "\"") && valNFC == strings.Trim(valNFC, " \t")) {
							cellStrs = append(cellStrs, valNFC)
						} else {
							cellStrs = append(cellStrs, emitString(valNFC))
						}
					} else {
						cellStrs = append(cellStrs, emitScalarStr(ex, microMap))
					}
				}
				outLines = append(outLines, head+"|"+strings.Join(cellStrs, "|"))

			case "cuerpo":
				val := extractBodyText(idea)
				val = strings.ReplaceAll(val, "\r\n", "\n")
				val = strings.ReplaceAll(val, "\r", "\n")
				valNFC := NFC(val)
				if strings.ContainsRune(valNFC, '\n') {
					outLines = append(outLines, head+"{")
					for _, line := range strings.Split(valNFC, "\n") {
						outLines = append(outLines, line)
					}
					outLines = append(outLines, "}")
				} else {
					outLines = append(outLines, fmt.Sprintf("%s{%s}", head, valNFC))
				}

			case "bloque":
				val := extractBodyText(idea)
				val = strings.ReplaceAll(val, "\r\n", "\n")
				val = strings.ReplaceAll(val, "\r", "\n")
				outLines = append(outLines, head+"{")
				for _, line := range strings.Split(val, "\n") {
					outLines = append(outLines, line)
				}
				outLines = append(outLines, "}")
			}
		}
	}

	outText := strings.Join(outLines, "\n") + "\n"
	outBytes := []byte(outText)

	// Detect source change
	if !bytesEqual(outBytes, raw) {
		changes = addChange(changes, "source-form-normalized")
	}

	// Deduplicate changes preserving order
	changes = dedupChanges(changes)

	// Compute hashes
	rawSHA := sha256Hex(raw)
	canSHA := sha256Hex(outBytes)

	chashHasher := sha256.New()
	chashHasher.Write([]byte("CORTEX-C14N-0.1\x00"))
	chashHasher.Write(outBytes)
	chash := fmt.Sprintf("sha256:%x", chashHasher.Sum(nil))

	report := map[string]interface{}{
		"canonicalization":        "C14N-0.1",
		"inputSha256":             rawSHA,
		"canonicalSha256":         canSHA,
		"canonicalHash":           chash,
		"changed":                 !bytesEqual(outBytes, raw),
		"structuralLoss":          false,
		"losses":                  []string{},
		"sourceFidelityChanges":   changes,
		"diagnostics":             []string{},
	}

	return outBytes, report, true
}

// ===== Helper functions for canonicalization =====

type metaCat struct {
	idx  int
	sub  string
}

func metaCategory(name string) metaCat {
	if name == "format" {
		return metaCat{0, ""}
	}
	prefixes := []string{"enum_", "micro_", "namespace_", "extension_"}
	for i, p := range prefixes {
		if strings.HasPrefix(name, p) {
			return metaCat{i + 1, name[len(p):]}
		}
	}
	return metaCat{5, name}
}

type metaEntry struct {
	Name string
	Attrs map[string]ScalarValue
}

func extractMetasOrdered(doc *Document) []metaEntry {
	metaNames := make([]string, 0)
	for _, m := range doc.Glossary.Meta {
		metaNames = append(metaNames, m.Name)
	}

	metaMap := make(map[string]map[string]ScalarValue)
	for _, name := range metaNames {
		metaMap[name] = extractMetaAttrs(name, doc)
	}

	sorted := make([]metaEntry, 0, len(metaMap))
	for name, attrs := range metaMap {
		sorted = append(sorted, metaEntry{Name: name, Attrs: attrs})
	}

	sort.Slice(sorted, func(i, j int) bool {
		ai := metaCategory(sorted[i].Name)
		bj := metaCategory(sorted[j].Name)
		if ai.idx != bj.idx {
			return ai.idx < bj.idx
		}
		if ai.idx == 0 {
			return NFC(sorted[i].Name) < NFC(sorted[j].Name)
		}
		return NFC(ai.sub) < NFC(bj.sub)
	})

	return sorted
}

func extractMetaAttrs(name string, doc *Document) map[string]ScalarValue {
	result := make(map[string]ScalarValue)

	if name == "format" {
		if doc.Glossary.Format != nil {
			for _, attr := range doc.Glossary.Format.Attributes {
				result[attr.Key] = attr.Value
			}
		}
		return result
	}

	if strings.HasPrefix(name, "enum_") {
		enumName := name[5:]
		for _, en := range doc.Glossary.Enums {
			if en.Name == enumName {
				vals := strings.Join(en.Values, "|")
				result["values"] = StringValue{
					Node:   "StringValue",
					Value:  vals,
					Lexeme: "\"" + vals + "\"",
				}
				return result
			}
		}
		return result
	}

	if strings.HasPrefix(name, "micro_") {
		microName := name[6:]
		for _, mic := range doc.Glossary.Micros {
			if mic.Token == microName {
				result["expand"] = AtomValue{
					Node:   "AtomValue",
					Value:  mic.Expand,
					Lexeme: mic.Expand,
				}
				return result
			}
		}
		return result
	}

	if strings.HasPrefix(name, "namespace_") {
		alias := name[10:]
		for _, ns := range doc.Glossary.Namespaces {
			if ns.Alias == alias {
				for _, attr := range ns.Attributes {
					result[attr.Key] = attr.Value
				}
				return result
			}
		}
		return result
	}

	if strings.HasPrefix(name, "extension_") {
		extName := name[10:]
		for _, ext := range doc.Glossary.Extensions {
			if ext.Name == extName {
				for _, attr := range ext.Attributes {
					result[attr.Key] = attr.Value
				}
				return result
			}
		}
		return result
	}

	// Other meta - iterate Meta declarations
	for _, md := range doc.Glossary.Meta {
		if md.Name == name {
			for _, attr := range md.Attributes {
				result[attr.Key] = attr.Value
			}
			return result
		}
	}

	return result
}

func extractSymbolsOrdered(doc *Document) []SymbolDefinition {
	syms := make([]SymbolDefinition, len(doc.Glossary.Symbols))
	copy(syms, doc.Glossary.Symbols)

	sort.Slice(syms, func(i, j int) bool {
		keyI := NFC(syms[i].Surface)
		keyJ := NFC(syms[j].Surface)
		return keyI < keyJ
	})

	return syms
}

func extractSymbolAttrsMap(sd *SymbolDefinition) map[string]ScalarValue {
	result := make(map[string]ScalarValue)
	for _, attr := range sd.Attributes {
		result[attr.Key] = attr.Value
	}
	return result
}

func extractIdeaAttrsPayload(idea Idea) map[string]ScalarValue {
	result := make(map[string]ScalarValue)
	if ap, ok := idea.Payload.(AttrsPayload); ok {
		for _, pair := range ap.Pairs {
			result[pair.Key] = pair.Value
		}
	}
	return result
}

func extractPipeCells(idea Idea) []ScalarValue {
	switch p := idea.Payload.(type) {
	case PositionalPayload:
		return p.Cells
	case RelationPayload:
		return p.Cells
	}
	return nil
}

func extractBodyText(idea Idea) string {
	switch p := idea.Payload.(type) {
	case TextPayload:
		return p.Text
	case BlockPayload:
		return p.Text
	}
	return ""
}

func determineShape(idea Idea, symbolMap map[string]SymbolDefinition) string {
	if idea.Shape != "attrs" {
		return idea.Shape
	}
	if sd, ok := symbolMap[idea.Symbol]; ok {
		return sd.Shape
	}
	return idea.Shape
}

func buildMicroMap(micros []MicroDeclaration) map[string]string {
	m := make(map[string]string)
	for _, mic := range micros {
		m[mic.Token] = mic.Expand
	}
	return m
}

func buildSymbolMap(symbols []SymbolDefinition) map[string]SymbolDefinition {
	m := make(map[string]SymbolDefinition)
	for _, s := range symbols {
		m[s.Surface] = s
		if s.Qualified != s.Surface {
			m[s.Qualified] = s
		}
	}
	return m
}

func orderedKeys(attrs map[string]ScalarValue, base []string) []string {
	result := make([]string, 0)

	for _, b := range base {
		if _, ok := attrs[b]; ok {
			result = append(result, b)
		}
	}

	extras := make([]string, 0)
	for k := range attrs {
		found := false
		for _, b := range base {
			if k == b {
				found = true
				break
			}
		}
		if !found {
			extras = append(extras, k)
		}
	}

	sort.Slice(extras, func(i, j int) bool {
		return NFC(extras[i]) < NFC(extras[j])
	})

	result = append(result, extras...)
	return result
}

func mapKeys(m map[string]ScalarValue) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}

// ===== Emission helpers =====

var controlEsc = map[rune]string{
	0x08: "\\b",
	0x0c: "\\f",
	0x0a: "\\n",
	0x0d: "\\r",
	0x09: "\\t",
}

func NFC(s string) string {
	return norm.NFC.String(s)
}

func emitString(v string) string {
	v = NFC(v)
	var b strings.Builder
	b.WriteByte('"')
	for _, ch := range v {
		switch {
		case ch == '"':
			b.WriteString("\\\"")
		case ch == '\\':
			b.WriteString("\\\\")
		case ch == '\b':
			b.WriteString("\\b")
		case ch == '\f':
			b.WriteString("\\f")
		case ch == '\n':
			b.WriteString("\\n")
		case ch == '\r':
			b.WriteString("\\r")
		case ch == '\t':
			b.WriteString("\\t")
		case ch < 0x20 || ch == 0x7f:
			fmt.Fprintf(&b, "\\u%04X", ch)
		default:
			b.WriteRune(ch)
		}
	}
	b.WriteByte('"')
	return b.String()
}

func canonInt(s string) string {
	// Trim leading zeros, keep sign
	if s == "0" || s == "-0" {
		return "0"
	}
	neg := false
	if strings.HasPrefix(s, "-") {
		neg = true
		s = s[1:]
	}
	s = strings.TrimLeft(s, "0")
	if s == "" {
		return "0"
	}
	if neg {
		return "-" + s
	}
	return s
}

func atomSafe(s string) bool {
	if s == "" {
		return false
	}
	for _, r := range s {
		if r == ' ' || r == '\t' || r == '[' || r == ']' || r == '{' || r == '}' || r == ',' || r == '"' || r == '|' {
			return false
		}
	}
	return true
}

func expandMicroScalar(s ScalarValue, micros map[string]string) ScalarValue {
	switch v := s.(type) {
	case AtomValue:
		if expanded, ok := micros[v.Value]; ok {
			// Parse and return the expanded value
			sp := NewScalarParser(NewDiagnosticList())
			parsed, _, _ := sp.parseScalar(expanded, 1, 1)
			return parsed
		}
		return v
	case ListValue:
		newItems := make([]ScalarValue, len(v.Items))
		for i, item := range v.Items {
			newItems[i] = expandMicroScalar(item, micros)
		}
		return ListValue{
			Node:  "ListValue",
			Items: newItems,
			Lexeme: v.Lexeme,
		}
	default:
		return s
	}
}

func emitScalarStr(s ScalarValue, micros map[string]string) string {
	ex := expandMicroScalar(s, micros)
	switch v := ex.(type) {
	case StringValue:
		return emitString(v.Value)
	case AtomValue:
		valNFC := NFC(v.Value)
		if atomSafe(valNFC) {
			return valNFC
		}
		return emitString(valNFC)
	case IntegerValue:
		return canonInt(v.Value)
	case DecimalValue:
		return v.Value
	case BooleanValue:
		if v.Value {
			return "true"
		}
		return "false"
	case NullValue:
		return "null"
	case ListValue:
		parts := make([]string, 0, len(v.Items))
		for _, item := range v.Items {
			parts = append(parts, emitScalarStr(item, micros))
		}
		return "[" + strings.Join(parts, ",") + "]"
	default:
		return ""
	}
}

func emitAttrsStr(keys []string, attrs map[string]ScalarValue, micros []MicroDeclaration) string {
	microMap := buildMicroMap(micros)
	parts := make([]string, 0, len(keys))
	for _, k := range keys {
		v := attrs[k]
		parts = append(parts, fmt.Sprintf("%s:%s", k, emitScalarStr(v, microMap)))
	}
	return "{" + strings.Join(parts, ",") + "}"
}

func getScalarText(s ScalarValue) string {
	switch v := s.(type) {
	case StringValue:
		return v.Value
	case AtomValue:
		return v.Value
	case IntegerValue:
		return v.Value
	case DecimalValue:
		return v.Value
	case BooleanValue:
		if v.Value {
			return "true"
		}
		return "false"
	case NullValue:
		return ""
	case ListValue:
		parts := make([]string, 0, len(v.Items))
		for _, item := range v.Items {
			parts = append(parts, getScalarText(item))
		}
		return strings.Join(parts, ",")
	default:
		return ""
	}
}

func emitIdeaAttrs(keys []string, attrs map[string]ScalarValue, contract []ContractField, focus string, micros map[string]string) string {
	parts := make([]string, 0, len(keys))
	for _, k := range keys {
		rawVal := attrs[k]
		ex := expandMicroScalar(rawVal, micros)

		fieldType := "any"
		for _, f := range contract {
			if f.Name == k {
				fieldType = f.Type
				break
			}
		}

		baseType := strings.TrimSuffix(fieldType, "?")

		var rendered string
		if baseType == "text" {
			textStr := getScalarText(ex)
			textNFC := NFC(textStr)
			isFocus := focus == k
			if isFocus || !atomSafe(textNFC) {
				rendered = emitString(textNFC)
			} else {
				rendered = textNFC
			}
		} else {
			rendered = emitScalarStr(ex, micros)
		}
		parts = append(parts, fmt.Sprintf("%s:%s", k, rendered))
	}
	return "{" + strings.Join(parts, ",") + "}"
}

// ===== Utility functions =====

func stringSliceEqual(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

func bytesEqual(a, b []byte) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

func sha256Hex(data []byte) string {
	h := sha256.Sum256(data)
	return fmt.Sprintf("%x", h[:])
}

func addChange(changes []string, change string) []string {
	for _, c := range changes {
		if c == change {
			return changes
		}
	}
	return append(changes, change)
}

func dedupChanges(changes []string) []string {
	seen := make(map[string]bool)
	result := make([]string, 0, len(changes))
	for _, c := range changes {
		if !seen[c] {
			seen[c] = true
			result = append(result, c)
		}
	}
	return result
}

func docHasNFCChange(doc *Document) bool {
	// Check meta names and attrs
	for _, md := range doc.Glossary.Meta {
		if NFC(md.Name) != md.Name {
			return true
		}
		for _, attr := range md.Attributes {
			if scalarHasNFCChange(attr.Value) {
				return true
			}
		}
	}

	// Check symbol attrs
	for _, sd := range doc.Glossary.Symbols {
		for _, attr := range sd.Attributes {
			if scalarHasNFCChange(attr.Value) {
				return true
			}
		}
	}

	// Check sections
	for _, sec := range doc.Sections {
		if sec.Title != "" && NFC(sec.Title) != sec.Title {
			return true
		}
		for _, idea := range sec.Ideas {
			switch idea.Shape {
			case "attrs":
				if ap, ok := idea.Payload.(AttrsPayload); ok {
					for _, pair := range ap.Pairs {
						if scalarHasNFCChange(pair.Value) {
							return true
						}
					}
				}
			case "attrs-pos", "relacion":
				if pp, ok := idea.Payload.(PositionalPayload); ok {
					for _, cell := range pp.Cells {
						if scalarHasNFCChange(cell) {
							return true
						}
					}
				}
				if rp, ok := idea.Payload.(RelationPayload); ok {
					for _, cell := range rp.Cells {
						if scalarHasNFCChange(cell) {
							return true
						}
					}
				}
			case "cuerpo":
				if tp, ok := idea.Payload.(TextPayload); ok {
					if NFC(tp.Text) != tp.Text {
						return true
					}
				}
			// bloque excluded
			}
		}
	}

	return false
}

func scalarHasNFCChange(s ScalarValue) bool {
	switch v := s.(type) {
	case StringValue:
		return NFC(v.Value) != v.Value
	case AtomValue:
		return NFC(v.Value) != v.Value
	case ListValue:
		for _, item := range v.Items {
			if scalarHasNFCChange(item) {
				return true
			}
		}
	}
	return false
}
