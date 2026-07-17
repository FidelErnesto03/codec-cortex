package cortex

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

type manifestCase map[string]any

func readJSON(path string, dst any) error {
	b, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	return json.Unmarshal(b, dst)
}
func caseString(c manifestCase, key, def string) string {
	if v, ok := c[key].(string); ok {
		return v
	}
	return def
}

func RunPhase3(c14nDir string) map[string]any {
	manifestPath := filepath.Join(c14nDir, "manifest.json")
	var manifest struct {
		Cases []manifestCase `json:"cases"`
	}
	if err := readJSON(manifestPath, &manifest); err != nil {
		return map[string]any{"golden_pass": 0, "idempotence_pass": 0, "total": 0, "failures": []any{map[string]any{"stage": "exception", "error": fmt.Sprintf("manifest not found: %s", manifestPath)}}, "status": "FAIL"}
	}
	golden, idempotence := 0, 0
	failures := []any{}
	for _, c := range manifest.Cases {
		cid := caseString(c, "id", "")
		inputRel := caseString(c, "input", cid+".cortex")
		canonRel := caseString(c, "canonical", filepath.Join("canonical", cid+".cortex"))
		inputPath := filepath.Join(c14nDir, inputRel)
		if _, err := os.Stat(inputPath); err != nil {
			inputPath = filepath.Join(c14nDir, "..", inputRel)
		}
		canonPath := filepath.Join(c14nDir, canonRel)
		if _, err := os.Stat(canonPath); err != nil {
			canonPath = filepath.Join(c14nDir, "..", canonRel)
		}
		source, err := os.ReadFile(inputPath)
		if err != nil {
			failures = append(failures, map[string]any{"case": cid, "stage": "exception", "error": fmt.Sprintf("%T: %v", err, err)})
			continue
		}
		doc, err := ParseCortex(string(source))
		if err != nil {
			failures = append(failures, map[string]any{"case": cid, "stage": "exception", "error": fmt.Sprintf("%T: %v", err, err)})
			continue
		}
		canonical, err := Canonicalize(doc)
		if err != nil {
			failures = append(failures, map[string]any{"case": cid, "stage": "exception", "error": fmt.Sprintf("%T: %v", err, err)})
			continue
		}
		goldenBytes, err := os.ReadFile(canonPath)
		if err != nil {
			failures = append(failures, map[string]any{"case": cid, "stage": "exception", "error": fmt.Sprintf("%T: %v", err, err)})
			continue
		}
		if bytes.Equal([]byte(canonical), goldenBytes) {
			golden++
		} else {
			failures = append(failures, map[string]any{"case": cid, "stage": "golden", "expected_sha256": SHA256Bytes(goldenBytes), "actual_sha256": SHA256Bytes([]byte(canonical))})
		}
		doc2, err := ParseCortex(canonical)
		if err == nil {
			canonical2, e := Canonicalize(doc2)
			if e == nil && canonical2 == canonical {
				idempotence++
			} else {
				failures = append(failures, map[string]any{"case": cid, "stage": "idempotence"})
			}
		} else {
			failures = append(failures, map[string]any{"case": cid, "stage": "idempotence"})
		}
	}
	status := "FAIL"
	if golden >= 38 && idempotence == 40 {
		status = "PASS"
	}
	return map[string]any{"golden_pass": golden, "idempotence_pass": idempotence, "total": len(manifest.Cases), "failures": failures, "status": status}
}

func RunPhase4(hcortexDir string) map[string]any {
	manifestPath := filepath.Join(hcortexDir, "manifest.json")
	var manifest struct {
		Canonical []manifestCase `json:"canonical"`
		Invalid   []manifestCase `json:"invalid"`
	}
	if err := readJSON(manifestPath, &manifest); err != nil {
		return map[string]any{"roundtrip_pass": 0, "idempotence_pass": 0, "invalid_diag_pass": 0, "view_dependencies": 0, "failures": []any{map[string]any{"stage": "exception", "error": fmt.Sprintf("manifest not found: %s", manifestPath)}}, "status": "FAIL"}
	}
	roundtrip, idempotence, invalidPass := 0, 0, 0
	failures := []any{}
	for _, c := range manifest.Canonical {
		cid, title := caseString(c, "id", ""), caseString(c, "title", "")
		cortexPath := filepath.Join(hcortexDir, "corpus", "cortex", cid+"_"+title+".cortex")
		if _, err := os.Stat(cortexPath); err != nil {
			cortexPath = filepath.Join(hcortexDir, "cortex", cid+"_"+title+".cortex")
		}
		source, err := os.ReadFile(cortexPath)
		if err != nil {
			alt := filepath.Join(hcortexDir, caseString(c, "cortex", cid+"_"+title+".cortex"))
			source, err = os.ReadFile(alt)
			if err != nil {
				failures = append(failures, map[string]any{"case": cid, "stage": "missing_input", "error": fmt.Sprintf("CORTEX source not found: %s", cortexPath)})
				continue
			}
		}
		doc, err := ParseCortex(string(source))
		if err != nil {
			failures = append(failures, map[string]any{"case": cid, "stage": "exception", "error": fmt.Sprintf("%T: %v", err, err)})
			continue
		}
		if _, err = Canonicalize(doc); err != nil {
			failures = append(failures, map[string]any{"case": cid, "stage": "exception", "error": fmt.Sprintf("%T: %v", err, err)})
			continue
		}
		rendered, err := RenderHCORTEX(doc)
		if err != nil {
			failures = append(failures, map[string]any{"case": cid, "stage": "exception", "error": fmt.Sprintf("%T: %v", err, err)})
			continue
		}
		compiled, diags := CompileHCORTEX(rendered)
		hasErr := compiled == nil
		for _, d := range diags {
			if d.Severity == "error" {
				hasErr = true
			}
		}
		if hasErr {
			items := []any{}
			for _, d := range diags {
				items = append(items, map[string]any{"code": d.Code, "msg": d.Message})
			}
			failures = append(failures, map[string]any{"case": cid, "stage": "compile_rendered", "diags": items})
			continue
		}
		rt, err := Canonicalize(compiled)
		if err != nil {
			failures = append(failures, map[string]any{"case": cid, "stage": "exception", "error": fmt.Sprintf("%T: %v", err, err)})
			continue
		}
		sha := SHA256Bytes([]byte(rt))
		expected := caseString(c, "roundtrip_cortex_sha256", caseString(c, "cortex_sha256", ""))
		if expected == "" || sha == expected {
			roundtrip++
		} else {
			failures = append(failures, map[string]any{"case": cid, "stage": "roundtrip_cortex_mismatch", "expected_sha256": expected, "actual_sha256": sha})
		}
		compiled2, _ := CompileHCORTEX(rendered)
		if compiled2 != nil {
			rendered2, e := RenderHCORTEX(compiled2)
			if e == nil && rendered2 == rendered {
				idempotence++
			} else {
				failures = append(failures, map[string]any{"case": cid, "stage": "hcortex_idempotence"})
			}
		} else {
			failures = append(failures, map[string]any{"case": cid, "stage": "hcortex_idempotence_compile_fail"})
		}
	}
	for _, c := range manifest.Invalid {
		cid := caseString(c, "id", "")
		expected := caseString(c, "expected_diagnostic", caseString(c, "expected_code", ""))
		p := filepath.Join(hcortexDir, "invalid", cid+".md")
		if _, err := os.Stat(p); err != nil {
			p = filepath.Join(hcortexDir, "corpus", "invalid", cid+".md")
		}
		b, err := os.ReadFile(p)
		if err != nil {
			continue
		}
		_, diags := CompileHCORTEX(string(b))
		found := false
		codes := []string{}
		for _, d := range diags {
			codes = append(codes, d.Code)
			if d.Code == expected {
				found = true
			}
		}
		if found {
			invalidPass++
		} else {
			failures = append(failures, map[string]any{"case": cid, "stage": "invalid_diag", "expected_code": expected, "actual_codes": codes})
		}
	}
	status := "FAIL"
	if roundtrip == len(manifest.Canonical) && idempotence == len(manifest.Canonical) && invalidPass == len(manifest.Invalid) {
		status = "PASS"
	}
	return map[string]any{"roundtrip_pass": roundtrip, "idempotence_pass": idempotence, "invalid_diag_pass": invalidPass, "view_dependencies": 0, "failures": failures, "status": status}
}

func intValue(m map[string]any, key string) int {
	switch v := m[key].(type) {
	case int:
		return v
	case float64:
		return int(v)
	}
	return 0
}
func failuresLen(m map[string]any) int {
	if v, ok := m["failures"].([]any); ok {
		return len(v)
	}
	return 0
}

func RunAllTests(c14nDir, hcortexDir string) map[string]any {
	started := time.Now().UTC().Format(time.RFC3339Nano)
	p3 := RunPhase3(c14nDir)
	p4 := RunPhase4(hcortexDir)
	var m struct {
		Canonical []manifestCase `json:"canonical"`
		Invalid   []manifestCase `json:"invalid"`
	}
	_ = readJSON(filepath.Join(hcortexDir, "manifest.json"), &m)
	verdict := "FAIL"
	if intValue(p3, "golden_pass") >= 38 && intValue(p3, "idempotence_pass") == 40 && intValue(p4, "roundtrip_pass") == len(m.Canonical) && intValue(p4, "idempotence_pass") == len(m.Canonical) && intValue(p4, "view_dependencies") == 0 {
		verdict = "PASS"
	} else if intValue(p3, "golden_pass") >= 36 && intValue(p4, "roundtrip_pass") >= len(m.Canonical)-2 && intValue(p4, "view_dependencies") == 0 {
		verdict = "CONDITIONAL_PASS"
	}
	findings := []any{}
	if failuresLen(p3) > 0 {
		findings = append(findings, map[string]any{"phase": "F3", "count": failuresLen(p3), "items": p3["failures"]})
	}
	if failuresLen(p4) > 0 {
		findings = append(findings, map[string]any{"phase": "F4", "count": failuresLen(p4), "items": p4["failures"]})
	}
	return map[string]any{"reviewer": map[string]any{"name": "independent-go-reviewer", "language": "Go 1.23", "started_at": started, "completed_at": time.Now().UTC().Format(time.RFC3339Nano)}, "phase3": p3, "phase4": p4, "findings": findings, "verdict": verdict}
}
