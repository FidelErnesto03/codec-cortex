package cortex

// Decode parses CORTEX source into its AST.
func Decode(source string) (*Document, error) { return ParseCortex(source) }

// Encode emits canonical CORTEX bytes from an AST.
func Encode(doc *Document) (string, error) { return Canonicalize(doc) }

// ToHCORTEX renders canonical HCORTEX.
func ToHCORTEX(doc *Document) (string, error) { return RenderHCORTEX(doc) }

// FromHCORTEX compiles canonical HCORTEX into an AST and diagnostics.
func FromHCORTEX(source string) (*Document, []HDiagnostic) { return CompileHCORTEX(source) }
