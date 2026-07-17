package cortex

import (
	"fmt"
	"strings"
)

// LossDiagnostic reports a construct that the reference HCORTEX mapping may not
// preserve. It does not change compatibility behavior; it makes inherited loss auditable.
type LossDiagnostic struct {
	Code     string `json:"code"`
	Severity string `json:"severity"`
	Message  string `json:"message"`
	Address  string `json:"address,omitempty"`
}

// ExplainHCORTEXLoss inspects a document before RenderHCORTEX.
func ExplainHCORTEXLoss(doc *Document) []LossDiagnostic {
	if doc == nil {
		return []LossDiagnostic{{Code: "HLOSS000", Severity: "error", Message: "nil document"}}
	}
	out := []LossDiagnostic{}

	seenSigils := map[string]string{}
	for _, sym := range doc.Glossary.Symbols {
		key := strings.ToLower(sym.Sigil)
		qualified := sym.Qualified()
		if previous, ok := seenSigils[key]; ok && previous != qualified {
			out = append(out, LossDiagnostic{
				Code:     "HLOSS003_NAMESPACE_SIGIL_COLLISION",
				Severity: "warning",
				Message:  fmt.Sprintf("HCORTEX compiler indexes sigil %q without namespace; %s collides with %s", sym.Sigil, qualified, previous),
			})
		} else {
			seenSigils[key] = qualified
		}
	}

	for _, sec := range doc.Sections {
		if len(sec.Ideas) == 0 {
			out = append(out, LossDiagnostic{Code: "HLOSS002_EMPTY_SECTION", Severity: "warning", Message: "empty sections have no paired schema block and are not reconstructed", Address: fmt.Sprintf("$%d", sec.ID)})
			continue
		}
		if sec.Title == nil {
			out = append(out, LossDiagnostic{Code: "HLOSS004_UNTITLED_SECTION", Severity: "warning", Message: "renderer synthesizes a section title, changing the structural form on roundtrip", Address: fmt.Sprintf("$%d", sec.ID)})
		}
		schema := determineSectionSchema(sec)
		for _, idea := range sec.Ideas {
			sym := doc.FindSymbol(idea.Namespace, idea.Symbol)
			if schema == "table" && idea.Shape == "attrs" && sym != nil {
				contract := map[string]bool{}
				for _, f := range sym.Contract {
					contract[f.Name] = true
				}
				for _, a := range idea.Attrs {
					if !contract[a.Key] {
						out = append(out, LossDiagnostic{Code: "HLOSS001_OPEN_EXTRA_FIELD", Severity: "warning", Message: fmt.Sprintf("table rendering omits field %q because it is outside the symbol contract", a.Key), Address: idea.Address()})
					}
				}
			}
			if schema == "table" {
				values := []Scalar{}
				if idea.Shape == "attrs" {
					for _, a := range idea.Attrs {
						values = append(values, a.Value)
					}
				} else {
					values = append(values, idea.Cells...)
				}
				for _, v := range values {
					if scalarContainsPipe(v) {
						out = append(out, LossDiagnostic{Code: "HLOSS005_PIPE_IN_TABLE_VALUE", Severity: "warning", Message: "table renderer does not escape pipe characters before compilation", Address: idea.Address()})
						break
					}
				}
			}
			if idea.Shape == "bloque" && idea.Body != strings.TrimSpace(idea.Body) {
				out = append(out, LossDiagnostic{Code: "HLOSS006_BLOCK_BOUNDARY_WHITESPACE", Severity: "warning", Message: "diagram compilation trims leading or trailing block whitespace", Address: idea.Address()})
			}
			if schema == "prose" && idea.Shape == "cuerpo" && idea.Body != strings.TrimSpace(idea.Body) {
				out = append(out, LossDiagnostic{Code: "HLOSS007_BODY_BOUNDARY_WHITESPACE", Severity: "warning", Message: "prose compilation trims leading or trailing body whitespace", Address: idea.Address()})
			}
		}
	}
	return out
}

func scalarContainsPipe(s Scalar) bool {
	if strings.Contains(s.Text, "|") {
		return true
	}
	for _, item := range s.Items {
		if scalarContainsPipe(item) {
			return true
		}
	}
	return false
}
