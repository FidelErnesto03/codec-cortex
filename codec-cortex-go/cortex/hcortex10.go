package cortex

import (
	"fmt"
	"strings"
)

// RenderHCORTEX10 renders the HCORTEX 1.0 projection of a parsed document.
func RenderHCORTEX10(doc *Document) (string, error) {
	out := []string{}
	version := doc.CortexVersion
	if version != "0.2" && version != "1.0" {
		version = "1.0"
	}
	out = append(out, fmt.Sprintf("<!-- HCORTEX v=%s t=canonical k=corpus -->", version))
	out = append(out, "")
	out = append(out, "<!-- glossary -->")
	out = append(out, renderGlossaryV10(doc))
	out = append(out, "<!-- /glossary -->")
	out = append(out, "")
	symLookup := map[string]*SymbolDef{}
	for i := range doc.Glossary.Symbols {
		s := &doc.Glossary.Symbols[i]
		symLookup[s.Namespace+"\x00"+s.Sigil] = s
	}
	for si := range doc.Sections {
		sec := &doc.Sections[si]
		title := fmt.Sprintf("Sección %d", sec.ID)
		if sec.Title != nil {
			title = *sec.Title
		}
		out = append(out, fmt.Sprintf("## §%d: %s", sec.ID, title))
		out = append(out, "")
		capa := ""
		if sec.Capa != "" {
			capa = " capa:" + sec.Capa
		}
		out = append(out, fmt.Sprintf("<!-- schema:%d%s -->", sec.ID, capa))
		for ii := range sec.Ideas {
			idea := &sec.Ideas[ii]
			sym := symLookup[idea.Namespace+"\x00"+idea.Symbol]
			out = append(out, renderIdeaV10(*idea, sym)...)
			out = append(out, "")
		}
		out = append(out, fmt.Sprintf("<!-- /schema:%d -->", sec.ID))
		out = append(out, "")
	}
	return strings.Join(out, "\n") + "\n", nil
}

func renderGlossaryV10(doc *Document) string {
	lines := []string{}
	gl := doc.Glossary
	if gl.Capa != "" {
		lines = append(lines, "$0:"+gl.Capa)
	}
	if gl.Format != nil {
		parts := make([]string, 0, len(gl.Format.Attrs))
		for _, a := range gl.Format.Attrs {
			parts = append(parts, a.Key+":"+a.Value.Lexeme)
		}
		lines = append(lines, "$0:format{"+strings.Join(parts, ",")+"}")
	}
	for _, e := range gl.Enums {
		lines = append(lines, fmt.Sprintf(`$0:enum_%s{values:"%s"}`, e.Name, strings.Join(e.Values, "|")))
	}
	for _, m := range gl.Micros {
		expand := m.Expand
		if strings.HasPrefix(expand, `"`) && strings.HasSuffix(expand, `"`) && len(expand) >= 2 {
			expand = expand[1 : len(expand)-1]
		}
		if strings.Contains(expand, " ") || expand == "" {
			lines = append(lines, fmt.Sprintf(`$0:micro_%s{expand:"%s"}`, m.Token, expand))
		} else {
			lines = append(lines, fmt.Sprintf(`$0:micro_%s{expand:%s}`, m.Token, expand))
		}
	}
	for _, ns := range gl.Namespaces {
		lines = append(lines, "$0:namespace_"+ns.Alias+renderAttrPairs(ns.Attrs))
	}
	for _, ext := range gl.Extensions {
		lines = append(lines, "$0:extension_"+ext.Name+renderAttrPairs(ext.Attrs))
	}
	for _, md := range gl.Meta {
		line := "$0:" + md.Name + renderAttrPairs(md.Attrs)
		if md.Capa != "" {
			line += ":" + md.Capa
		}
		lines = append(lines, line)
	}
	anySlots := false
	for _, s := range gl.Symbols {
		if s.Encoding == "slots" {
			anySlots = true
			break
		}
	}
	if anySlots && gl.SigilMap != nil {
		cp := strings.TrimPrefix(gl.SigilMap.Codepoint, "U+")
		for len(cp) < 4 {
			cp = "0" + cp
		}
		lines = append(lines, fmt.Sprintf(`$0:sigil-map{marker:"%s",codepoint:"U+%s",base:%d,syntax:"%s",order:"%s"}`,
			gl.SigilMap.Marker, cp, gl.SigilMap.Base, gl.SigilMap.Syntax, gl.SigilMap.Order))
	}
	for _, s := range gl.Symbols {
		qualified := s.Sigil
		if s.Namespace != "" {
			qualified = s.Namespace + "::" + s.Sigil
		}
		parts := []string{}
		seen := map[string]bool{}
		for _, a := range s.Attrs {
			if a.Key == "contract" {
				continue
			}
			if seen[a.Key] {
				continue
			}
			seen[a.Key] = true
			parts = append(parts, a.Key+":"+a.Value.Lexeme)
		}
		openVal := ""
		hasOpen := false
		for _, a := range s.Attrs {
			if a.Key == "open" {
				hasOpen = true
				openVal = a.Value.Lexeme
			}
		}
		if hasOpen && !seen["open"] {
			parts = append(parts, "open:"+openVal)
		}
		lines = append(lines, qualified+":"+s.Label+"{"+strings.Join(parts, ",")+"}")
	}
	return strings.Join(lines, "\n") + "\n"
}

func renderAttrPairs(attrs []Attr) string {
	parts := make([]string, 0, len(attrs))
	for _, a := range attrs {
		parts = append(parts, a.Key+":"+a.Value.Lexeme)
	}
	return "{" + strings.Join(parts, ",") + "}"
}

func renderIdeaV10(idea Idea, sym *SymbolDef) []string {
	out := []string{}
	qualified := idea.Symbol
	if idea.Namespace != "" {
		qualified = idea.Namespace + "::" + idea.Symbol
	}
	out = append(out, "### "+qualified+":"+idea.Name)
	if idea.SlotEncoded {
		headers := make([]string, 0)
		row := make([]string, 0)
		if sym != nil {
			for _, f := range sym.Contract {
				headers = append(headers, f.Name)
			}
			for _, f := range sym.Contract {
				fv := findFieldValue(idea.SlotValues, f.Position)
				if fv == nil {
					row = append(row, "")
				} else {
					row = append(row, fv.Value.Lexeme)
				}
			}
		}
		out = append(out, renderTable(headers, row)...)
		return out
	}
	switch idea.Shape {
	case "attrs":
		headers := []string{}
		row := []string{}
		if sym != nil && sym.Encoding == "slots" {
			for _, f := range sym.Contract {
				headers = append(headers, f.Name)
			}
			for _, f := range sym.Contract {
				v, ok := attrValue(idea.Attrs, f.Name)
				if !ok {
					row = append(row, "")
				} else {
					row = append(row, v.Lexeme)
				}
			}
		} else {
			for _, a := range idea.Attrs {
				headers = append(headers, a.Key)
				row = append(row, a.Value.Lexeme)
			}
		}
		out = append(out, renderTable(headers, row)...)
	case "attrs-pos", "relacion":
		headers := []string{}
		if sym != nil {
			for i := range idea.Cells {
				if i < len(sym.Contract) {
					headers = append(headers, sym.Contract[i].Name)
				} else {
					headers = append(headers, fmt.Sprintf("c%d", i+1))
				}
			}
		}
		row := make([]string, len(idea.Cells))
		for i, c := range idea.Cells {
			row[i] = c.Lexeme
		}
		out = append(out, renderTable(headers, row)...)
	case "cuerpo":
		out = append(out, idea.Body)
	case "bloque":
		out = append(out, "```")
		out = append(out, idea.Body)
		out = append(out, "```")
	}
	return out
}

func renderTable(headers, row []string) []string {
	return []string{
		"| " + strings.Join(headers, " | ") + " |",
		"|" + strings.Repeat("---|", len(headers)),
		"| " + strings.Join(row, " | ") + " |",
	}
}

func findFieldValue(fvs []FieldValue, position int) *FieldValue {
	for i := range fvs {
		if fvs[i].Position == position {
			return &fvs[i]
		}
	}
	return nil
}

func attrValue(attrs []Attr, key string) (Scalar, bool) {
	for _, a := range attrs {
		if a.Key == key {
			return a.Value, true
		}
	}
	return Scalar{}, false
}
