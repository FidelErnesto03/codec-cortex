package cortex

import (
	"sort"
	"strings"
)

var (
	formatKeyOrderV10 = []string{"cortex", "encoding", "language", "type"}
	sigilKeyOrderV10  = []string{"type", "encoding", "weight", "slots", "focus", "schema", "desc", "open", "namespace", "version"}
	sigilMapKeyOrder  = []string{"marker", "codepoint", "base", "syntax", "order"}
	enumKeyOrderV10   = []string{"values"}
	microKeyOrderV10  = []string{"expand"}
	nsKeyOrderV10     = []string{"id", "uri", "version", "required", "desc"}
	extKeyOrderV10    = []string{"namespace", "id", "version", "required", "desc"}
)

func preNormalizeV10(doc *Document) {
	if doc.Glossary.Format != nil {
		for i := range doc.Glossary.Format.Attrs {
			doc.Glossary.Format.Attrs[i].Value = nfcScalar(doc.Glossary.Format.Attrs[i].Value)
		}
	}
	for i := range doc.Glossary.Enums {
		for j := range doc.Glossary.Enums[i].Values {
			doc.Glossary.Enums[i].Values[j] = ToNFC(doc.Glossary.Enums[i].Values[j])
		}
	}
	for i := range doc.Glossary.Micros {
		doc.Glossary.Micros[i].Expand = ToNFC(doc.Glossary.Micros[i].Expand)
	}
	for i := range doc.Glossary.Namespaces {
		for j := range doc.Glossary.Namespaces[i].Attrs {
			doc.Glossary.Namespaces[i].Attrs[j].Value = nfcScalar(doc.Glossary.Namespaces[i].Attrs[j].Value)
		}
	}
	for i := range doc.Glossary.Extensions {
		for j := range doc.Glossary.Extensions[i].Attrs {
			doc.Glossary.Extensions[i].Attrs[j].Value = nfcScalar(doc.Glossary.Extensions[i].Attrs[j].Value)
		}
	}
	for i := range doc.Glossary.Meta {
		for j := range doc.Glossary.Meta[i].Attrs {
			doc.Glossary.Meta[i].Attrs[j].Value = nfcScalar(doc.Glossary.Meta[i].Attrs[j].Value)
		}
	}
	for i := range doc.Glossary.Symbols {
		for j := range doc.Glossary.Symbols[i].Attrs {
			doc.Glossary.Symbols[i].Attrs[j].Value = nfcScalar(doc.Glossary.Symbols[i].Attrs[j].Value)
		}
		doc.Glossary.Symbols[i].Desc = ToNFC(doc.Glossary.Symbols[i].Desc)
	}
	micro := map[string]string{}
	for _, m := range doc.Glossary.Micros {
		micro[m.Token] = m.Expand
	}
	for si := range doc.Sections {
		sec := &doc.Sections[si]
		for ii := range sec.Ideas {
			idea := &sec.Ideas[ii]
			if idea.SlotEncoded {
				for fi := range idea.SlotValues {
					v := idea.SlotValues[fi].Value
					if v.Kind == ScalarAtom {
						if ex, ok := micro[v.Text]; ok {
							v = Scalar{Kind: ScalarAtom, Text: ex, Lexeme: ex}
						}
					}
					idea.SlotValues[fi].Value = nfcScalar(v)
				}
				continue
			}
			for ai := range idea.Attrs {
				idea.Attrs[ai].Value = nfcScalar(idea.Attrs[ai].Value)
			}
			for ci := range idea.Cells {
				idea.Cells[ci] = nfcScalar(idea.Cells[ci])
			}
			if idea.Shape == "cuerpo" {
				idea.Body = ToNFC(idea.Body)
			}
		}
		if sec.Title != nil {
			t := ToNFC(*sec.Title)
			sec.Title = &t
		}
	}
}

func canonicalizeV10(doc *Document) (string, error) {
	preNormalizeV10(doc)
	lines := []string{}
	if doc.Glossary.Capa != "" {
		lines = append(lines, "$0:"+doc.Glossary.Capa)
	} else {
		lines = append(lines, "$0")
	}
	if doc.Glossary.Format != nil {
		lines = append(lines, formatCanonicalV10(doc.Glossary.Format))
	}
	anySlots := false
	for _, s := range doc.Glossary.Symbols {
		if s.Encoding == "slots" {
			anySlots = true
			break
		}
	}
	if anySlots && doc.Glossary.SigilMap != nil {
		lines = append(lines, sigilMapCanonical(doc.Glossary.SigilMap))
	}
	enums := append([]EnumDecl(nil), doc.Glossary.Enums...)
	sort.SliceStable(enums, func(i, j int) bool { return ToNFC(enums[i].Name) < ToNFC(enums[j].Name) })
	for _, e := range enums {
		values := strings.Join(e.Values, "|")
		lines = append(lines, "$0:enum_"+e.Name+emitGlossaryAttrs([]Attr{{Key: "values", Value: Scalar{Kind: ScalarString, Text: values, Lexeme: EmitStringLiteral(values)}}}))
	}
	micros := append([]MicroDecl(nil), doc.Glossary.Micros...)
	sort.SliceStable(micros, func(i, j int) bool { return ToNFC(micros[i].Token) < ToNFC(micros[j].Token) })
	for _, m := range micros {
		var v Scalar
		if atomRE.MatchString(m.Expand) {
			v = Scalar{Kind: ScalarAtom, Text: m.Expand, Lexeme: m.Expand}
		} else {
			v = Scalar{Kind: ScalarString, Text: m.Expand, Lexeme: EmitStringLiteral(m.Expand)}
		}
		lines = append(lines, "$0:micro_"+m.Token+emitGlossaryAttrs([]Attr{{Key: "expand", Value: v}}))
	}
	nss := append([]NamespaceDecl(nil), doc.Glossary.Namespaces...)
	sort.SliceStable(nss, func(i, j int) bool { return ToNFC(nss[i].Alias) < ToNFC(nss[j].Alias) })
	for _, ns := range nss {
		lines = append(lines, "$0:namespace_"+ns.Alias+emitGlossaryAttrs(sortKeysCanonical(ns.Attrs, nsKeyOrderV10)))
	}
	exts := append([]ExtensionDecl(nil), doc.Glossary.Extensions...)
	sort.SliceStable(exts, func(i, j int) bool { return ToNFC(exts[i].Name) < ToNFC(exts[j].Name) })
	for _, e := range exts {
		lines = append(lines, "$0:extension_"+e.Name+emitGlossaryAttrs(sortKeysCanonical(e.Attrs, extKeyOrderV10)))
	}
	meta := append([]MetaDecl(nil), doc.Glossary.Meta...)
	sort.SliceStable(meta, func(i, j int) bool { return ToNFC(meta[i].Name) < ToNFC(meta[j].Name) })
	for _, m := range meta {
		attrs := append([]Attr(nil), m.Attrs...)
		sort.SliceStable(attrs, func(i, j int) bool { return ToNFC(attrs[i].Key) < ToNFC(attrs[j].Key) })
		line := "$0:" + m.Name + emitGlossaryAttrs(attrs)
		if m.Capa != "" {
			line += ":" + m.Capa
		}
		lines = append(lines, line)
	}
	syms := append([]SymbolDef(nil), doc.Glossary.Symbols...)
	sort.SliceStable(syms, func(i, j int) bool {
		if syms[i].Namespace != syms[j].Namespace {
			return ToNFC(syms[i].Namespace) < ToNFC(syms[j].Namespace)
		}
		if syms[i].Sigil != syms[j].Sigil {
			return ToNFC(syms[i].Sigil) < ToNFC(syms[j].Sigil)
		}
		return ToNFC(syms[i].Label) < ToNFC(syms[j].Label)
	})
	for _, s := range syms {
		qualified := s.Sigil
		if s.Namespace != "" {
			qualified = s.Namespace + "::" + s.Sigil
		}
		lines = append(lines, qualified+":"+s.Label+emitGlossaryAttrs(sortKeysCanonical(s.Attrs, sigilKeyOrderV10)))
	}
	for si := range doc.Sections {
		sec := &doc.Sections[si]
		if sec.Title == nil {
			if sec.Capa != "" {
				lines = append(lines, "$"+itoa(sec.ID)+":"+sec.Capa)
			} else {
				lines = append(lines, "$"+itoa(sec.ID))
			}
		} else {
			if sec.Capa != "" {
				lines = append(lines, "$"+itoa(sec.ID)+": "+*sec.Title+":"+sec.Capa)
			} else {
				lines = append(lines, "$"+itoa(sec.ID)+": "+*sec.Title)
			}
		}
		for ii := range sec.Ideas {
			idea := &sec.Ideas[ii]
			line, err := ideaCanonicalV10(*idea, doc)
			if err != nil {
				return "", err
			}
			lines = append(lines, line)
		}
	}
	return strings.Join(lines, "\n") + "\n", nil
}

func formatCanonicalV10(f *FormatDecl) string {
	return "$0:format" + emitGlossaryAttrs(sortKeysCanonical(f.Attrs, formatKeyOrderV10))
}

func sigilMapCanonical(sm *SigilMapDecl) string {
	attrs := []Attr{
		{Key: "marker", Value: Scalar{Kind: ScalarString, Text: sm.Marker, Lexeme: EmitStringLiteral(sm.Marker)}},
		{Key: "codepoint", Value: Scalar{Kind: ScalarString, Text: sm.Codepoint, Lexeme: EmitStringLiteral(sm.Codepoint)}},
		{Key: "base", Value: Scalar{Kind: ScalarInteger, Text: itoa(sm.Base), Lexeme: itoa(sm.Base)}},
		{Key: "syntax", Value: Scalar{Kind: ScalarString, Text: sm.Syntax, Lexeme: EmitStringLiteral(sm.Syntax)}},
		{Key: "order", Value: Scalar{Kind: ScalarString, Text: sm.Order, Lexeme: EmitStringLiteral(sm.Order)}},
	}
	return "$0:sigil-map" + emitGlossaryAttrs(sortKeysCanonical(attrs, sigilMapKeyOrder))
}

func ideaCanonicalV10(idea Idea, doc *Document) (string, error) {
	qualified := idea.Symbol
	if idea.Namespace != "" {
		qualified = idea.Namespace + "::" + idea.Symbol
	}
	head := qualified + ":" + idea.Name
	sym := doc.FindSymbol(idea.Namespace, idea.Symbol)
	if idea.SlotEncoded {
		if sym == nil {
			return "", &ParseError{Code: "I001_UNDECLARED_SYMBOL", Message: "Undeclared sigil in canonicalize: " + idea.Symbol}
		}
		fieldTypes := map[int]string{}
		focusPos := 0
		for _, f := range sym.Contract {
			fieldTypes[f.Position] = f.Type
			if f.Name == sym.Focus {
				focusPos = f.Position
			}
		}
		parts := make([]string, 0, len(idea.SlotValues))
		for _, fv := range idea.SlotValues {
			ftype := fieldTypes[fv.Position]
			if ftype == "" {
				ftype = "any"
			}
			isText := ftype == "text"
			isFocusText := fv.Position == focusPos && ftype == "text"
			parts = append(parts, "※"+itoa(fv.Position)+":"+emitScalarAttrs(fv.Value, isFocusText, isText))
		}
		return head + "{" + strings.Join(parts, ",") + "}", nil
	}
	switch idea.Shape {
	case "attrs":
		if sym == nil {
			return "", &ParseError{Code: "I001_UNDECLARED_SYMBOL", Message: "Undeclared sigil in canonicalize: " + idea.Symbol}
		}
		fieldTypes := map[string]string{}
		for _, f := range sym.Contract {
			fieldTypes[f.Name] = f.Type
		}
		parts := make([]string, 0, len(idea.Attrs))
		for _, a := range idea.Attrs {
			ftype := fieldTypes[a.Key]
			if ftype == "" {
				ftype = "any"
			}
			isText := ftype == "text"
			isFocusText := a.Key == sym.Focus && ftype == "text"
			parts = append(parts, a.Key+":"+emitScalarAttrs(a.Value, isFocusText, isText))
		}
		return head + "{" + strings.Join(parts, ",") + "}", nil
	case "attrs-pos", "relacion":
		parts := make([]string, len(idea.Cells))
		for i, c := range idea.Cells {
			parts[i] = c.Lexeme
		}
		return head + "|" + strings.Join(parts, "|"), nil
	case "cuerpo":
		text := ToNFC(idea.Body)
		if strings.Contains(text, "\n") {
			return head + "{\n" + text + "\n}", nil
		}
		return head + "{" + text + "}", nil
	case "bloque":
		return head + "{\n" + idea.Body + "\n}", nil
	}
	return head, nil
}

func itoa(n int) string {
	if n == 0 {
		return "0"
	}
	digits := []byte{}
	for n > 0 {
		digits = append([]byte{byte('0' + n%10)}, digits...)
		n /= 10
	}
	return string(digits)
}
