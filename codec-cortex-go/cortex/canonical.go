package cortex

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"sort"
	"strings"
)

var (
	formatKeyOrder = []string{"cortex", "encoding", "language"}
	sigilKeyOrder  = []string{"type", "weight", "fields", "pos", "focus", "desc", "open", "namespace", "version"}
	enumKeyOrder   = []string{"values"}
	microKeyOrder  = []string{"expand"}
	nsKeyOrder     = []string{"id", "uri", "version", "required", "desc"}
	extKeyOrder    = []string{"namespace", "id", "version", "required", "desc"}
)

func sortKeysCanonical(attrs []Attr, order []string) []Attr {
	byKey := map[string]Scalar{}
	for _, a := range attrs {
		byKey[a.Key] = a.Value
	}
	out := make([]Attr, 0, len(attrs))
	used := map[string]bool{}
	for _, k := range order {
		if v, ok := byKey[k]; ok {
			out = append(out, Attr{Key: k, Value: v})
			used[k] = true
		}
	}
	extras := make([]Attr, 0)
	for _, a := range attrs {
		if !used[a.Key] {
			extras = append(extras, a)
		}
	}
	sort.SliceStable(extras, func(i, j int) bool { return ToNFC(extras[i].Key) < ToNFC(extras[j].Key) })
	return append(out, extras...)
}

func nfcScalar(s Scalar) Scalar {
	switch s.Kind {
	case ScalarString:
		s.Text = ToNFC(s.Text)
		s.Lexeme = EmitStringLiteral(s.Text)
	case ScalarAtom:
		s.Text = ToNFC(s.Text)
		s.Lexeme = s.Text
	case ScalarList:
		for i := range s.Items {
			s.Items[i] = nfcScalar(s.Items[i])
		}
		parts := make([]string, len(s.Items))
		for i := range s.Items {
			parts[i] = s.Items[i].Lexeme
		}
		s.Lexeme = "[" + strings.Join(parts, ",") + "]"
	}
	return s
}

func expandMicrotokens(doc *Document) {
	if len(doc.Glossary.Micros) == 0 {
		return
	}
	m := map[string]string{}
	for _, x := range doc.Glossary.Micros {
		m[x.Token] = x.Expand
	}
	for si := range doc.Sections {
		for ii := range doc.Sections[si].Ideas {
			idea := &doc.Sections[si].Ideas[ii]
			if idea.Shape == "attrs" {
				for ai := range idea.Attrs {
					v := &idea.Attrs[ai].Value
					if v.Kind == ScalarAtom {
						if ex, ok := m[v.Text]; ok {
							*v = Scalar{Kind: ScalarAtom, Text: ex, Lexeme: ex}
						}
					}
				}
			}
			if idea.Shape == "attrs-pos" || idea.Shape == "relacion" {
				for ci := range idea.Cells {
					v := &idea.Cells[ci]
					if v.Kind == ScalarAtom {
						if ex, ok := m[v.Text]; ok {
							*v = Scalar{Kind: ScalarAtom, Text: ex, Lexeme: ex}
						}
					}
				}
			}
		}
	}
}

func isAtomSafeBare(s string) bool { return s != "" && !strings.ContainsAny(s, " \t\r\n[]{},\"|") }
func isTextSafeBare(s string) bool {
	return s != "" && !strings.ContainsAny(s, "\r\n|") && s == strings.TrimSpace(s) && !strings.HasPrefix(s, "\"")
}

func emitScalarAttrs(v Scalar, isFocusText, isTextField bool) string {
	switch v.Kind {
	case ScalarString:
		if isFocusText {
			return v.Lexeme
		}
		if isTextField && isAtomSafeBare(v.Text) && atomRE.MatchString(v.Text) {
			return v.Text
		}
		return v.Lexeme
	case ScalarAtom:
		if isAtomSafeBare(v.Text) {
			return v.Text
		}
		return EmitStringLiteral(v.Text)
	default:
		return v.Lexeme
	}
}
func emitScalarPositional(v Scalar, isTextField bool) string {
	switch v.Kind {
	case ScalarString:
		if isTextField && isTextSafeBare(v.Text) {
			return v.Text
		}
		return v.Lexeme
	case ScalarAtom:
		if isAtomSafeBare(v.Text) {
			return v.Text
		}
		return EmitStringLiteral(v.Text)
	default:
		return v.Lexeme
	}
}
func emitGlossaryAttrs(attrs []Attr) string {
	parts := make([]string, len(attrs))
	for i, a := range attrs {
		parts[i] = a.Key + ":" + a.Value.Lexeme
	}
	return "{" + strings.Join(parts, ",") + "}"
}

func ideaCanonical(idea Idea, sym *SymbolDef) (string, error) {
	if sym == nil {
		return "", fmt.Errorf("symbol not found for %s", idea.QualifiedSymbol())
	}
	head := idea.QualifiedSymbol() + ":" + idea.Name
	switch idea.Shape {
	case "attrs":
		pairMap := map[string]Scalar{}
		for _, a := range idea.Attrs {
			pairMap[a.Key] = a.Value
		}
		out := []Attr{}
		used := map[string]bool{}
		for _, f := range sym.Contract {
			if v, ok := pairMap[f.Name]; ok {
				out = append(out, Attr{Key: f.Name, Value: v})
				used[f.Name] = true
			}
		}
		if sym.Open {
			extras := []Attr{}
			for _, a := range idea.Attrs {
				if !used[a.Key] {
					extras = append(extras, a)
				}
			}
			sort.SliceStable(extras, func(i, j int) bool { return ToNFC(extras[i].Key) < ToNFC(extras[j].Key) })
			out = append(out, extras...)
		}
		fieldTypes := map[string]string{}
		for _, f := range sym.Contract {
			fieldTypes[f.Name] = f.Type
		}
		parts := make([]string, len(out))
		for i, a := range out {
			ft := fieldTypes[a.Key]
			parts[i] = a.Key + ":" + emitScalarAttrs(a.Value, a.Key == sym.Focus && ft == "text", ft == "text")
		}
		return head + "{" + strings.Join(parts, ",") + "}", nil
	case "attrs-pos", "relacion":
		parts := make([]string, len(idea.Cells))
		for i, c := range idea.Cells {
			ft := "any"
			if i < len(sym.Contract) {
				ft = sym.Contract[i].Type
			}
			parts[i] = emitScalarPositional(c, ft == "text")
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
	default:
		return head, nil
	}
}

func Canonicalize(doc *Document) (string, error) {
	if doc == nil {
		return "", fmt.Errorf("nil document")
	}
	if doc.Glossary.Format == nil {
		return "", fmt.Errorf("missing $0:format declaration")
	}
	for i := range doc.Glossary.Format.Attrs {
		doc.Glossary.Format.Attrs[i].Value = nfcScalar(doc.Glossary.Format.Attrs[i].Value)
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
	for si := range doc.Sections {
		sec := &doc.Sections[si]
		if sec.Title != nil {
			t := ToNFC(*sec.Title)
			sec.Title = &t
		}
		for ii := range sec.Ideas {
			idea := &sec.Ideas[ii]
			switch idea.Shape {
			case "attrs":
				for ai := range idea.Attrs {
					idea.Attrs[ai].Value = nfcScalar(idea.Attrs[ai].Value)
				}
			case "attrs-pos", "relacion":
				for ci := range idea.Cells {
					idea.Cells[ci] = nfcScalar(idea.Cells[ci])
				}
			case "cuerpo":
				idea.Body = ToNFC(idea.Body)
			}
		}
	}
	expandMicrotokens(doc)

	lines := []string{}
	if doc.Glossary.Capa != "" {
		lines = append(lines, "$0:"+doc.Glossary.Capa)
	} else {
		lines = append(lines, "$0")
	}
	lines = append(lines, "$0:format"+emitGlossaryAttrs(sortKeysCanonical(doc.Glossary.Format.Attrs, formatKeyOrder)))
	enums := append([]EnumDecl(nil), doc.Glossary.Enums...)
	sort.SliceStable(enums, func(i, j int) bool { return ToNFC(enums[i].Name) < ToNFC(enums[j].Name) })
	for _, e := range enums {
		v := strings.Join(e.Values, "|")
		lines = append(lines, "$0:enum_"+e.Name+emitGlossaryAttrs(sortKeysCanonical([]Attr{{Key: "values", Value: Scalar{Kind: ScalarString, Text: v, Lexeme: EmitStringLiteral(v)}}}, enumKeyOrder)))
	}
	micros := append([]MicroDecl(nil), doc.Glossary.Micros...)
	sort.SliceStable(micros, func(i, j int) bool { return ToNFC(micros[i].Token) < ToNFC(micros[j].Token) })
	for _, m := range micros {
		v := Scalar{Kind: ScalarString, Text: m.Expand, Lexeme: EmitStringLiteral(m.Expand)}
		if atomRE.MatchString(m.Expand) {
			v = Scalar{Kind: ScalarAtom, Text: m.Expand, Lexeme: m.Expand}
		}
		lines = append(lines, "$0:micro_"+m.Token+emitGlossaryAttrs(sortKeysCanonical([]Attr{{Key: "expand", Value: v}}, microKeyOrder)))
	}
	nss := append([]NamespaceDecl(nil), doc.Glossary.Namespaces...)
	sort.SliceStable(nss, func(i, j int) bool { return ToNFC(nss[i].Alias) < ToNFC(nss[j].Alias) })
	for _, n := range nss {
		lines = append(lines, "$0:namespace_"+n.Alias+emitGlossaryAttrs(sortKeysCanonical(n.Attrs, nsKeyOrder)))
	}
	exts := append([]ExtensionDecl(nil), doc.Glossary.Extensions...)
	sort.SliceStable(exts, func(i, j int) bool { return ToNFC(exts[i].Name) < ToNFC(exts[j].Name) })
	for _, e := range exts {
		lines = append(lines, "$0:extension_"+e.Name+emitGlossaryAttrs(sortKeysCanonical(e.Attrs, extKeyOrder)))
	}
	meta := append([]MetaDecl(nil), doc.Glossary.Meta...)
	sort.SliceStable(meta, func(i, j int) bool { return ToNFC(meta[i].Name) < ToNFC(meta[j].Name) })
	for _, m := range meta {
		a := append([]Attr(nil), m.Attrs...)
		sort.SliceStable(a, func(i, j int) bool { return ToNFC(a[i].Key) < ToNFC(a[j].Key) })
		suffix := ""
		if m.Capa != "" {
			suffix = ":" + m.Capa
		}
		lines = append(lines, "$0:"+m.Name+emitGlossaryAttrs(a)+suffix)
	}
	syms := append([]SymbolDef(nil), doc.Glossary.Symbols...)
	sort.SliceStable(syms, func(i, j int) bool {
		a, b := syms[i], syms[j]
		if ToNFC(a.Namespace) != ToNFC(b.Namespace) {
			return ToNFC(a.Namespace) < ToNFC(b.Namespace)
		}
		if ToNFC(a.Sigil) != ToNFC(b.Sigil) {
			return ToNFC(a.Sigil) < ToNFC(b.Sigil)
		}
		return ToNFC(a.Label) < ToNFC(b.Label)
	})
	for _, s := range syms {
		lines = append(lines, s.Qualified()+":"+s.Label+emitGlossaryAttrs(sortKeysCanonical(s.Attrs, sigilKeyOrder)))
	}

	for _, sec := range doc.Sections {
		capa := resolveCapa(sec)
		if sec.Title == nil {
			if capa != "" {
				lines = append(lines, fmt.Sprintf("$%d:%s", sec.ID, capa))
			} else {
				lines = append(lines, fmt.Sprintf("$%d", sec.ID))
			}
		} else {
			title := strings.TrimSpace(*sec.Title)
			if capa != "" {
				lines = append(lines, fmt.Sprintf("$%d: %s:%s", sec.ID, title, capa))
			} else {
				lines = append(lines, fmt.Sprintf("$%d: %s", sec.ID, title))
			}
		}
		for _, idea := range sec.Ideas {
			line, err := ideaCanonical(idea, doc.FindSymbol(idea.Namespace, idea.Symbol))
			if err != nil {
				return "", err
			}
			lines = append(lines, line)
		}
	}
	return strings.Join(lines, "\n") + "\n", nil
}

func CanonicalHash(canonical []byte) string {
	h := sha256.New()
	h.Write([]byte("CORTEX-C14N-0.1"))
	h.Write([]byte{0})
	h.Write(canonical)
	return "sha256:" + hex.EncodeToString(h.Sum(nil))
}
func SHA256Bytes(b []byte) string { h := sha256.Sum256(b); return hex.EncodeToString(h[:]) }
