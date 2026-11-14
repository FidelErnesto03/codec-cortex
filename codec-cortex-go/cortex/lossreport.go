package cortex

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"sort"
	"strings"

	"golang.org/x/text/unicode/norm"
)

// Declared loss catalog (spec §8.2). Closed list: a roundtrip divergence that no
// entry classifies is L499_UNCLASSIFIED_LOSS and makes the command fail.
const (
	LossCommentDropped       = "L402_COMMENT_DROPPED"
	LossIntralineWhitespace  = "L403_INTRALINE_WHITESPACE"
	LossOpenAttrOrder        = "L405_OPEN_ATTR_ORDER"
	LossCompileSideDrop      = "L406_COMPILE_SIDE_DROP"
	LossUnclassified         = "L499_UNCLASSIFIED_LOSS"
)

var lossPreserved = []string{"blocks", "identity", "scalars", "structure"}

// Coverage declaration (spec §8.2): which pipeline operations the report
// models. The compile pipeline (source -> AST) is not modelled, so declaring
// it explicitly keeps `reversible: true` honest about its scope.
var lossCoveredOperations = []string{"render"}
var lossUncoveredOperations = []string{"compile"}

var lossDetail = map[string]string{
	LossCommentDropped:      "comment line outside a multiline body is not represented in the AST",
	LossIntralineWhitespace: "intraline whitespace is collapsed by canonicalization",
	LossOpenAttrOrder:       "editorial attribute order of an open sigil is not preserved",
	LossCompileSideDrop:     "an idea present in the AST is lost across the render/compile roundtrip (its rendered header does not round-trip)",
	LossUnclassified:        "roundtrip diverges and no declared loss classifies the divergence",
}

var lossAction = map[string]string{
	LossCommentDropped:      "declare-only",
	LossIntralineWhitespace: "declare-only",
	LossOpenAttrOrder:       "declare-only",
	LossCompileSideDrop:     "fix-surface",
	LossUnclassified:        "fix-surface",
}

// LossFinding is one declared loss entry (loss-report 1.0 finding shape).
type LossFinding struct {
	Action         string `json:"action"`
	Category       string `json:"category"`
	Code           string `json:"code"`
	Detail         string `json:"detail"`
	Path           string `json:"path"`
	Recoverability string `json:"recoverability"`
	Severity       string `json:"severity"`
}

// LossCoverage declares which pipeline operations the report models.
type LossCoverage struct {
	Complete            bool     `json:"complete"`
	Operations          []string `json:"operations"`
	UncoveredOperations []string `json:"uncovered_operations"`
}

// LossReport is the canonical loss report. Field order is alphabetical so the
// JSON encoder emits the same key order as the reference implementation.
type LossReport struct {
	Case                  string        `json:"case"`
	Coverage              LossCoverage  `json:"coverage"`
	Losses                []LossFinding `json:"losses"`
	Mode                  string        `json:"mode"`
	Operation             string        `json:"operation"`
	Preserved             []string      `json:"preserved"`
	Reversible            bool          `json:"reversible"`
	SchemaVersion         string        `json:"schema_version"`
	SourceFormat          string        `json:"source_format"`
	SourceSHA256          string        `json:"source_sha256"`
	StructuralEquivalence bool          `json:"structural_equivalence"`
	TargetFormat          string        `json:"target_format"`
	TargetSHA256          string        `json:"target_sha256"`
	Warnings              []LossFinding `json:"warnings"`
}

func lossFinding(code, path, category, recoverability string) LossFinding {
	severity := "loss"
	if code == LossUnclassified || code == LossCompileSideDrop {
		severity = "error"
	}
	return LossFinding{
		Action:         lossAction[code],
		Category:       category,
		Code:           code,
		Detail:         lossDetail[code],
		Path:           path,
		Recoverability: recoverability,
		Severity:       severity,
	}
}

func sha256Hex(text string) string {
	sum := sha256.Sum256([]byte(text))
	return hex.EncodeToString(sum[:])
}

// stripQuoted replaces double-quoted literals with empty literals so intraline
// whitespace inside strings is never reported as a loss.
func stripQuoted(line string) string {
	var b strings.Builder
	i := 0
	for i < len(line) {
		if line[i] != '"' {
			b.WriteByte(line[i])
			i++
			continue
		}
		b.WriteString(`""`)
		i++
		for i < len(line) {
			if line[i] == '\\' {
				i += 2
				continue
			}
			if line[i] == '"' {
				i++
				break
			}
			i++
		}
	}
	return b.String()
}

func lexicalLosses(source string) []LossFinding {
	losses := []LossFinding{}
	inBody := false
	for index, raw := range strings.Split(source, "\n") {
		line := strings.TrimSuffix(raw, "\r")
		stripped := strings.TrimSpace(line)
		if inBody {
			if stripped == "}" {
				inBody = false
			}
			continue
		}
		if stripped == "" {
			continue
		}
		if strings.HasPrefix(stripped, "#") {
			losses = append(losses, lossFinding(LossCommentDropped,
				fmt.Sprintf("line:%d", index+1), "structure", "from-source-only"))
			continue
		}
		if strings.HasSuffix(stripped, "{") && !strings.HasPrefix(stripped, "$0:") {
			inBody = true
		}
		probe := stripQuoted(line)
		if strings.TrimRight(probe, " \t") != probe ||
			strings.Contains(probe, "\t") ||
			strings.Contains(probe, "  ") {
			losses = append(losses, lossFinding(LossIntralineWhitespace,
				fmt.Sprintf("line:%d", index+1), "presentation", "from-source-only"))
		}
	}
	return losses
}

func nfcBytes(value string) string {
	return norm.NFC.String(value)
}

func openAttrOrderLosses(doc *Document) []LossFinding {
	losses := []LossFinding{}
	for _, section := range doc.Sections {
		for _, idea := range section.Ideas {
			sym := doc.FindSymbol(idea.Namespace, idea.Symbol)
			if sym == nil || !sym.Open || len(idea.Attrs) == 0 {
				continue
			}
			keys := make([]string, 0, len(idea.Attrs))
			for _, attr := range idea.Attrs {
				keys = append(keys, attr.Key)
			}
			inContract := map[string]bool{}
			expected := []string{}
			for _, field := range sym.Contract {
				inContract[field.Name] = true
			}
			for _, field := range sym.Contract {
				for _, key := range keys {
					if key == field.Name {
						expected = append(expected, key)
						break
					}
				}
			}
			extras := []string{}
			for _, key := range keys {
				if !inContract[key] {
					extras = append(extras, key)
				}
			}
			sort.Slice(extras, func(i, j int) bool { return nfcBytes(extras[i]) < nfcBytes(extras[j]) })
			expected = append(expected, extras...)
			if strings.Join(keys, "\x00") != strings.Join(expected, "\x00") {
				losses = append(losses, lossFinding(LossOpenAttrOrder,
					fmt.Sprintf("$%d", section.ID), "order", "from-source-only"))
			}
		}
	}
	return losses
}

func dedupeLosses(losses []LossFinding) []LossFinding {
	seen := map[string]bool{}
	out := []LossFinding{}
	for _, item := range losses {
		key := item.Path + "\x00" + item.Code
		if seen[key] {
			continue
		}
		seen[key] = true
		out = append(out, item)
	}
	sort.SliceStable(out, func(i, j int) bool {
		if out[i].Path != out[j].Path {
			return out[i].Path < out[j].Path
		}
		return out[i].Code < out[j].Code
	})
	return out
}

// ideaKeys returns the address of every idea in the AST, used to detect
// compile-side drops (ideas present in the source AST but not in the roundtrip).
func ideaKeys(doc *Document) map[string]bool {
	keys := map[string]bool{}
	for _, section := range doc.Sections {
		for _, idea := range section.Ideas {
			keys[fmt.Sprintf("%d|%s|%s|%s", section.ID, idea.Namespace, idea.Symbol, idea.Name)] = true
		}
	}
	return keys
}

// BuildLossReport produces the CORTEX 1.0 declared loss report for source.
func BuildLossReport(source, caseName string) (*LossReport, error) {
	doc, err := ParseAny(source)
	if err != nil {
		return nil, err
	}
	if doc.CortexVersion != "1.0" {
		return nil, fmt.Errorf("loss-report requires cortex:1.0 (declared: %s)", doc.CortexVersion)
	}
	// Render and detect source-order losses before canonicalizing: C14N mutates
	// the AST in place (microtoken expansion, attribute normalization).
	attrLosses := openAttrOrderLosses(doc)
	srcIdeas := ideaKeys(doc)
	rendered, err := RenderHCORTEXAny(doc)
	if err != nil {
		return nil, err
	}
	canonicalSource, err := CanonicalizeAny(doc)
	if err != nil {
		return nil, err
	}
	roundtrip, _ := CompileHCORTEXAny(rendered)
	if roundtrip == nil {
		return nil, fmt.Errorf("HCORTEX roundtrip compilation failed")
	}
	rtIdeas := ideaKeys(roundtrip)
	canonicalRoundtrip, err := CanonicalizeAny(roundtrip)
	if err != nil {
		return nil, err
	}

	dropped := false
	for key := range srcIdeas {
		if !rtIdeas[key] {
			dropped = true
			break
		}
	}
	losses := lexicalLosses(source)
	losses = append(losses, attrLosses...)
	equivalent := canonicalSource == canonicalRoundtrip
	if dropped {
		losses = append(losses, lossFinding(LossCompileSideDrop, "$", "structure", "irrecoverable"))
	}
	if !equivalent && !dropped {
		losses = append(losses, lossFinding(LossUnclassified, "$", "structure", "irrecoverable"))
	}

	return &LossReport{
		Case: caseName,
		Coverage: LossCoverage{
			Complete:            len(lossUncoveredOperations) == 0 && equivalent,
			Operations:          append([]string{}, lossCoveredOperations...),
			UncoveredOperations: append([]string{}, lossUncoveredOperations...),
		},
		Losses:                dedupeLosses(losses),
		Mode:                  "canonical",
		Operation:             "render",
		Preserved:             append([]string{}, lossPreserved...),
		Reversible:            equivalent,
		SchemaVersion:         "1.0",
		SourceFormat:          "cortex:1.0",
		SourceSHA256:          sha256Hex(source),
		StructuralEquivalence: equivalent,
		TargetFormat:          "hcortex:1.0",
		TargetSHA256:          sha256Hex(rendered),
		Warnings:              []LossFinding{},
	}, nil
}

// WriteLossReport writes the canonical JSON form (sorted keys, 2-space indent,
// final newline) to w.
func WriteLossReport(w io.Writer, report *LossReport) error {
	enc := json.NewEncoder(w)
	enc.SetEscapeHTML(false)
	enc.SetIndent("", "  ")
	return enc.Encode(report)
}

// LossCaseName derives the report "case" from a path, matching the reference.
func LossCaseName(path string) string {
	if path == "" || path == "-" {
		return "stdin"
	}
	base := path
	if idx := strings.LastIndexAny(base, "/\\"); idx >= 0 {
		base = base[idx+1:]
	}
	if idx := strings.LastIndex(base, "."); idx > 0 {
		base = base[:idx]
	}
	return base
}
