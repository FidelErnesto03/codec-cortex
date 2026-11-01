package main

// -------- AST Value Types --------

// ScalarValue is the interface for all scalar values
type ScalarValue interface {
	isScalar()
}

// StringValue represents a JSON string value
type StringValue struct {
	Node   string `json:"node"`
	Value  string `json:"value"`
	Lexeme string `json:"lexeme"`
}

func (s StringValue) isScalar() {}

// AtomValue represents a bare unquoted value
type AtomValue struct {
	Node   string `json:"node"`
	Value  string `json:"value"`
	Lexeme string `json:"lexeme"`
	Micro  string `json:"micro,omitempty"`
}

func (a AtomValue) isScalar() {}

// IntegerValue represents an integer value
type IntegerValue struct {
	Node   string `json:"node"`
	Value  string `json:"value"`
	Lexeme string `json:"lexeme"`
}

func (i IntegerValue) isScalar() {}

// DecimalValue represents a decimal number
type DecimalValue struct {
	Node   string `json:"node"`
	Value  string `json:"value"`
	Lexeme string `json:"lexeme"`
}

func (d DecimalValue) isScalar() {}

// BooleanValue represents true/false
type BooleanValue struct {
	Node   string `json:"node"`
	Value  bool   `json:"value"`
	Lexeme string `json:"lexeme"`
}

func (b BooleanValue) isScalar() {}

// NullValue represents null
type NullValue struct {
	Node   string      `json:"node"`
	Value  interface{} `json:"value"`
	Lexeme string      `json:"lexeme"`
}

func (n NullValue) isScalar() {}

// ListValue represents a flat list
type ListValue struct {
	Node   string         `json:"node"`
	Items  []ScalarValue  `json:"items,omitempty"`
	Lexeme string         `json:"lexeme"`
}

func (l ListValue) isScalar() {}

// -------- AST Node Types --------

// AttrPair represents a key:value pair
type AttrPair struct {
	Node  string      `json:"node"`
	Key   string      `json:"key"`
	Value ScalarValue `json:"value"`
}

// FormatDeclaration represents the $0:format declaration
type FormatDeclaration struct {
	Node       string     `json:"node"`
	Cortex     string     `json:"cortex"`
	Encoding   string     `json:"encoding"`
	Attributes []AttrPair `json:"attributes"`
	SourceLine int        `json:"sourceLine"`
}

// MetaDeclaration represents a $0:name{...} declaration
type MetaDeclaration struct {
	Node       string     `json:"node"`
	Name       string     `json:"name"`
	Attributes []AttrPair `json:"attributes"`
	SourceLine int        `json:"sourceLine"`
}

// EnumDeclaration represents $0:enum_XXX{values:...}
type EnumDeclaration struct {
	Node       string   `json:"node"`
	Name       string   `json:"name"`
	Values     []string `json:"values"`
	SourceLine int      `json:"sourceLine"`
}

// MicroDeclaration represents $0:micro_XXX{expand:...}
type MicroDeclaration struct {
	Node       string `json:"node"`
	Token      string `json:"token"`
	Expand     string `json:"expand"`
	SourceLine int    `json:"sourceLine"`
}

// NamespaceDeclaration represents $0:namespace_XXX{...}
type NamespaceDeclaration struct {
	Node       string     `json:"node"`
	Alias      string     `json:"alias"`
	ID         string     `json:"id"`
	Version    string     `json:"version"`
	Attributes []AttrPair `json:"attributes"`
	SourceLine int        `json:"sourceLine"`
}

// ExtensionDeclaration represents $0:extension_XXX{...}
type ExtensionDeclaration struct {
	Node       string     `json:"node"`
	Name       string     `json:"name"`
	Namespace  string     `json:"namespace"`
	ID         string     `json:"id"`
	Version    string     `json:"version"`
	Required   bool       `json:"required"`
	Attributes []AttrPair `json:"attributes"`
	SourceLine int        `json:"sourceLine"`
}

// ContractField represents a field definition in a contract
type ContractField struct {
	Name     string `json:"name"`
	Type     string `json:"type"`
	Required bool   `json:"required"`
}

// SymbolDefinition represents a SIGIL:label{type:..., weight:..., ...} declaration
type SymbolDefinition struct {
	Node        string          `json:"node"`
	Surface     string          `json:"surface"`
	Namespace   string          `json:"namespace"`
	Qualified   string          `json:"qualified"`
	Label       string          `json:"label"`
	Shape       string          `json:"shape"`
	Weight      string          `json:"weight"`
	Focus       string          `json:"focus"`
	Description string          `json:"description"`
	Open        bool            `json:"open"`
	Contract    []ContractField `json:"contract"`
	Attributes  []AttrPair      `json:"attributes"`
	SourceLine  int             `json:"sourceLine"`
}

// Glossary represents the $0 section
type Glossary struct {
	Node       string                `json:"node"`
	Format     *FormatDeclaration    `json:"format"`
	Meta       []MetaDeclaration     `json:"meta"`
	Enums      []EnumDeclaration     `json:"enums"`
	Micros     []MicroDeclaration    `json:"micros"`
	Namespaces []NamespaceDeclaration `json:"namespaces"`
	Extensions []ExtensionDeclaration `json:"extensions"`
	Symbols    []SymbolDefinition     `json:"symbols"`
}

// -------- Payload Types --------

// AttrsPayload represents {key:value, ...}
type AttrsPayload struct {
	Node  string     `json:"node"`
	Pairs []AttrPair `json:"pairs"`
}

// BoundValue represents a named field in positional payloads
type BoundValue struct {
	Field string      `json:"field"`
	Value ScalarValue `json:"value"`
}

// PositionalPayload represents a | separated payload
type PositionalPayload struct {
	Node  string       `json:"node"`
	Cells []ScalarValue `json:"cells"`
	Bound []BoundValue  `json:"bound"`
}

// RelationPayload represents a | separated payload with at least 3 cells
type RelationPayload struct {
	Node  string       `json:"node"`
	Cells []ScalarValue `json:"cells"`
	Bound []BoundValue  `json:"bound"`
}

// TextPayload represents a cuerpo payload (inline text or multiline body)
type TextPayload struct {
	Node string `json:"node"`
	Text string `json:"text"`
}

// BlockPayload represents a bloque payload (verbatim block)
type BlockPayload struct {
	Node string `json:"node"`
	Text string `json:"text"`
}

// Payload is the union type for all payload types
type Payload interface {
	isPayload()
}

func (a AttrsPayload) isPayload()       {}
func (p PositionalPayload) isPayload()  {}
func (r RelationPayload) isPayload()    {}
func (t TextPayload) isPayload()        {}
func (b BlockPayload) isPayload()       {}

// -------- Higher Level AST Nodes --------

// Idea represents a single idea
type Idea struct {
	Node            string    `json:"node"`
	Address         string    `json:"address"`
	Section         int       `json:"section"`
	Symbol          string    `json:"symbol"`
	QualifiedSymbol string    `json:"qualifiedSymbol"`
	Name            string    `json:"name"`
	Function        Function  `json:"function"`
	Shape           string    `json:"shape"`
	Payload         Payload   `json:"payload"`
	SourceLine      int       `json:"sourceLine"`
}

// Function represents the symbol's function info
type Function struct {
	Label  string `json:"label"`
	Weight string `json:"weight"`
	Focus  string `json:"focus"`
}

// Section represents a $N section with its ideas
type Section struct {
	Node   string `json:"node"`
	ID     int    `json:"id"`
	Title  string `json:"title"`
	Ideas  []Idea `json:"ideas"`
}

// Document represents the top-level AST node
type Document struct {
	Node          string    `json:"node"`
	CortexVersion string    `json:"cortexVersion"`
	Encoding      string    `json:"encoding"`
	Glossary      *Glossary `json:"glossary"`
	Sections      []Section `json:"sections"`
}

// -------- JSON Marshaling Helpers --------

// payloadJSON is a helper for JSON marshaling
type payloadJSON struct {
	AttrsPayload      *AttrsPayload      `json:",omitempty"`
	PositionalPayload *PositionalPayload `json:",omitempty"`
	RelationPayload   *RelationPayload   `json:",omitempty"`
	TextPayload       *TextPayload       `json:",omitempty"`
	BlockPayload      *BlockPayload      `json:",omitempty"`
}

// marshalPayload converts a Payload interface to the right JSON representation
func marshalPayload(p Payload) interface{} {
	switch v := p.(type) {
	case AttrsPayload:
		return v
	case PositionalPayload:
		return v
	case RelationPayload:
		return v
	case TextPayload:
		return v
	case BlockPayload:
		return v
	}
	return nil
}
