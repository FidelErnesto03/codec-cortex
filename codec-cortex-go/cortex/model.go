package cortex

import "fmt"

type ScalarKind string

const (
	ScalarString  ScalarKind = "string"
	ScalarAtom    ScalarKind = "atom"
	ScalarInteger ScalarKind = "integer"
	ScalarDecimal ScalarKind = "decimal"
	ScalarBoolean ScalarKind = "boolean"
	ScalarNull    ScalarKind = "null"
	ScalarList    ScalarKind = "list"
)

type Scalar struct {
	Kind   ScalarKind `json:"kind"`
	Text   string     `json:"text,omitempty"`
	Bool   bool       `json:"bool,omitempty"`
	Items  []Scalar   `json:"items,omitempty"`
	Lexeme string     `json:"lexeme"`
}

func (s Scalar) Clone() Scalar {
	out := s
	if s.Kind == ScalarList {
		out.Items = make([]Scalar, len(s.Items))
		for i := range s.Items {
			out.Items[i] = s.Items[i].Clone()
		}
	}
	return out
}

type Attr struct {
	Key   string `json:"key"`
	Value Scalar `json:"value"`
}

type FormatDecl struct {
	Cortex     string `json:"cortex"`
	Encoding   string `json:"encoding"`
	Attrs      []Attr `json:"attrs"`
	SourceLine int    `json:"source_line"`
}

type MetaDecl struct {
	Name       string `json:"name"`
	Attrs      []Attr `json:"attrs"`
	SourceLine int    `json:"source_line"`
	Capa       string `json:"capa,omitempty"`
}

type EnumDecl struct {
	Name       string   `json:"name"`
	Values     []string `json:"values"`
	SourceLine int      `json:"source_line"`
}

type MicroDecl struct {
	Token      string `json:"token"`
	Expand     string `json:"expand"`
	SourceLine int    `json:"source_line"`
}

type NamespaceDecl struct {
	Alias      string `json:"alias"`
	Attrs      []Attr `json:"attrs"`
	SourceLine int    `json:"source_line"`
}

type ExtensionDecl struct {
	Name       string `json:"name"`
	Attrs      []Attr `json:"attrs"`
	SourceLine int    `json:"source_line"`
}

type ContractField struct {
	Name     string `json:"name"`
	Type     string `json:"type"`
	Required bool   `json:"required"`
}

type SymbolDef struct {
	Namespace  string          `json:"namespace,omitempty"`
	Sigil      string          `json:"sigil"`
	Label      string          `json:"label"`
	Shape      string          `json:"shape"`
	Weight     string          `json:"weight"`
	Focus      string          `json:"focus"`
	Desc       string          `json:"desc"`
	Open       bool            `json:"open"`
	Contract   []ContractField `json:"contract"`
	Attrs      []Attr          `json:"attrs"`
	SourceLine int             `json:"source_line"`
}

func (s SymbolDef) Qualified() string {
	if s.Namespace != "" {
		return s.Namespace + "::" + s.Sigil
	}
	return s.Sigil
}

type Idea struct {
	Section    int      `json:"section"`
	Namespace  string   `json:"namespace,omitempty"`
	Symbol     string   `json:"symbol"`
	Name       string   `json:"name"`
	Shape      string   `json:"shape"`
	Attrs      []Attr   `json:"attrs,omitempty"`
	Cells      []Scalar `json:"cells,omitempty"`
	Body       string   `json:"body,omitempty"`
	SourceLine int      `json:"source_line"`
	multiline  bool
}

func (i Idea) QualifiedSymbol() string {
	if i.Namespace != "" {
		return i.Namespace + "::" + i.Symbol
	}
	return i.Symbol
}

func (i Idea) Address() string {
	return fmt.Sprintf("$%d:%s:%s", i.Section, i.QualifiedSymbol(), i.Name)
}

type Section struct {
	ID    int     `json:"id"`
	Title *string `json:"title"`
	Capa  string  `json:"capa"`
	Ideas []Idea  `json:"ideas"`
}

type Glossary struct {
	Capa       string          `json:"capa"`
	Format     *FormatDecl     `json:"format,omitempty"`
	Meta       []MetaDecl      `json:"meta"`
	Enums      []EnumDecl      `json:"enums"`
	Micros     []MicroDecl     `json:"micros"`
	Namespaces []NamespaceDecl `json:"namespaces"`
	Extensions []ExtensionDecl `json:"extensions"`
	Symbols    []SymbolDef     `json:"symbols"`
}

type Document struct {
	CortexVersion string    `json:"cortex_version"`
	Encoding      string    `json:"encoding"`
	Glossary      Glossary  `json:"glossary"`
	Sections      []Section `json:"sections"`
}

func NewDocument() *Document {
	return &Document{CortexVersion: "0.1", Encoding: "UTF-8"}
}

func (d *Document) FindSymbol(namespace, sigil string) *SymbolDef {
	for i := range d.Glossary.Symbols {
		s := &d.Glossary.Symbols[i]
		if s.Namespace == namespace && s.Sigil == sigil {
			return s
		}
	}
	return nil
}

func attrLookup(attrs []Attr, key string) (Scalar, bool) {
	for i := len(attrs) - 1; i >= 0; i-- {
		if attrs[i].Key == key {
			return attrs[i].Value, true
		}
	}
	return Scalar{}, false
}
