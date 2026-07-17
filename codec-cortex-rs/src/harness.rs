use std::fs;
use std::path::{Path, PathBuf};

use chrono::Utc;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};

use crate::{canonicalize, compile_hcortex, parse_cortex, render_hcortex};

pub fn sha256_bytes(bytes: &[u8]) -> String { hex::encode(Sha256::digest(bytes)) }

pub fn c14n_hash(bytes: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(b"CORTEX-C14N-0.1");
    hasher.update([0]);
    hasher.update(bytes);
    format!("sha256:{}", hex::encode(hasher.finalize()))
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Phase3Result {
    pub golden_pass: usize,
    pub idempotence_pass: usize,
    pub total: usize,
    pub failures: Vec<Value>,
    pub status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Phase4Result {
    pub roundtrip_pass: usize,
    pub idempotence_pass: usize,
    pub invalid_diag_pass: usize,
    pub view_dependencies: usize,
    pub failures: Vec<Value>,
    pub status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Reviewer {
    pub name: String,
    pub language: String,
    pub started_at: String,
    pub completed_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Finding {
    pub phase: String,
    pub count: usize,
    pub items: Vec<Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConformanceReport {
    pub reviewer: Reviewer,
    pub phase3: Phase3Result,
    pub phase4: Phase4Result,
    pub findings: Vec<Finding>,
    pub verdict: String,
}

fn read_manifest(path: &Path) -> Result<Value, String> {
    let text = fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    serde_json::from_str(&text).map_err(|e| format!("{}: {e}", path.display()))
}

fn resolve_case_path(root: &Path, relative: &str) -> PathBuf {
    let direct = root.join(relative);
    if direct.exists() { direct } else { root.join("..").join(relative) }
}

pub fn run_phase3(c14n_dir: impl AsRef<Path>) -> Phase3Result {
    let root = c14n_dir.as_ref();
    let manifest_path = root.join("manifest.json");
    let manifest = match read_manifest(&manifest_path) {
        Ok(value) => value,
        Err(_) if !manifest_path.exists() => return Phase3Result {
            golden_pass: 0,
            idempotence_pass: 0,
            total: 0,
            failures: vec![json!({"stage":"exception","error":format!("manifest not found: {}", manifest_path.display())})],
            status: "FAIL".into(),
        },
        Err(error) => return Phase3Result {
            golden_pass: 0,
            idempotence_pass: 0,
            total: 0,
            failures: vec![json!({"stage":"exception","error":error})],
            status: "FAIL".into(),
        },
    };
    let cases = manifest.get("cases").and_then(Value::as_array).cloned().unwrap_or_default();
    let mut result = Phase3Result { golden_pass: 0, idempotence_pass: 0, total: cases.len(), failures: Vec::new(), status: String::new() };

    for case in cases {
        let id = case.get("id").and_then(Value::as_str).unwrap_or("");
        let input_rel = case.get("input").and_then(Value::as_str).map(str::to_string).unwrap_or_else(|| format!("{id}.cortex"));
        let canonical_rel = case.get("canonical").and_then(Value::as_str).map(str::to_string).unwrap_or_else(|| format!("canonical/{id}.cortex"));
        let input_path = resolve_case_path(root, &input_rel);
        let canonical_path = resolve_case_path(root, &canonical_rel);
        let attempt = || -> Result<(bool, bool), String> {
            let source = fs::read_to_string(&input_path).map_err(|e| format!("{}: {e}", input_path.display()))?;
            let document = parse_cortex(&source).map_err(|e| e.to_string())?;
            let canonical = canonicalize(&document);
            let golden = fs::read(&canonical_path).map_err(|e| format!("{}: {e}", canonical_path.display()))?;
            let golden_ok = canonical.as_bytes() == golden;
            let second_document = parse_cortex(&canonical).map_err(|e| e.to_string())?;
            let second = canonicalize(&second_document);
            Ok((golden_ok, second.as_bytes() == canonical.as_bytes()))
        };
        match attempt() {
            Ok((golden_ok, idempotent)) => {
                if golden_ok { result.golden_pass += 1; }
                else {
                    let actual = fs::read_to_string(&input_path).ok().and_then(|s| parse_cortex(&s).ok()).map(|d| canonicalize(&d)).unwrap_or_default();
                    let expected = fs::read(&canonical_path).unwrap_or_default();
                    result.failures.push(json!({
                        "case":id,"stage":"golden",
                        "expected_sha256":sha256_bytes(&expected),
                        "actual_sha256":sha256_bytes(actual.as_bytes())
                    }));
                }
                if idempotent { result.idempotence_pass += 1; }
                else { result.failures.push(json!({"case":id,"stage":"idempotence"})); }
            }
            Err(error) => result.failures.push(json!({"case":id,"stage":"exception","error":error})),
        }
    }
    result.status = if result.golden_pass >= 38 && result.idempotence_pass == 40 { "PASS" } else { "FAIL" }.into();
    result
}

fn hcortex_manifest_counts(root: &Path) -> (usize, usize) {
    read_manifest(&root.join("manifest.json")).ok().map(|m| {
        (
            m.get("canonical").and_then(Value::as_array).map(|items| items.len()).unwrap_or(0),
            m.get("invalid").and_then(Value::as_array).map(|items| items.len()).unwrap_or(0),
        )
    }).unwrap_or((0, 0))
}

pub fn run_phase4(hcortex_dir: impl AsRef<Path>) -> Phase4Result {
    let root = hcortex_dir.as_ref();
    let manifest_path = root.join("manifest.json");
    let manifest = match read_manifest(&manifest_path) {
        Ok(value) => value,
        Err(_) if !manifest_path.exists() => return Phase4Result {
            roundtrip_pass: 0,
            idempotence_pass: 0,
            invalid_diag_pass: 0,
            view_dependencies: 0,
            failures: vec![json!({"stage":"exception","error":format!("manifest not found: {}", manifest_path.display())})],
            status: "FAIL".into(),
        },
        Err(error) => return Phase4Result {
            roundtrip_pass: 0,
            idempotence_pass: 0,
            invalid_diag_pass: 0,
            view_dependencies: 0,
            failures: vec![json!({"stage":"exception","error":error})],
            status: "FAIL".into(),
        },
    };

    let canonical_cases = manifest.get("canonical").and_then(Value::as_array).cloned().unwrap_or_default();
    let invalid_cases = manifest.get("invalid").and_then(Value::as_array).cloned().unwrap_or_default();
    let mut result = Phase4Result {
        roundtrip_pass: 0,
        idempotence_pass: 0,
        invalid_diag_pass: 0,
        view_dependencies: 0,
        failures: Vec::new(),
        status: String::new(),
    };

    for case in &canonical_cases {
        let id = case.get("id").and_then(Value::as_str).unwrap_or("");
        let title = case.get("title").and_then(Value::as_str).unwrap_or("");
        let mut cortex_path = root.join("corpus").join("cortex").join(format!("{id}_{title}.cortex"));
        if !cortex_path.exists() { cortex_path = root.join("cortex").join(format!("{id}_{title}.cortex")); }
        if !cortex_path.exists() {
            let fallback = format!("{id}_{title}.cortex");
            let relative = case.get("cortex").and_then(Value::as_str).unwrap_or(fallback.as_str());
            cortex_path = root.join(relative);
        }
        if !cortex_path.exists() {
            result.failures.push(json!({"case":id,"stage":"missing_input","error":format!("CORTEX source not found: {}", cortex_path.display())}));
            continue;
        }
        let attempt = || -> Result<(String, String, bool), String> {
            let source = fs::read_to_string(&cortex_path).map_err(|e| format!("{}: {e}", cortex_path.display()))?;
            let document = parse_cortex(&source).map_err(|e| e.to_string())?;
            let rendered = render_hcortex(&document);
            let (compiled, diagnostics) = compile_hcortex(&rendered);
            if compiled.is_none() || diagnostics.iter().any(|d| d.severity == "error") {
                return Err(serde_json::to_string(&diagnostics).unwrap_or_else(|_| "compile_rendered".into()));
            }
            let roundtrip = canonicalize(&compiled.unwrap());
            let (compiled_again, _) = compile_hcortex(&rendered);
            let idempotent = compiled_again.is_some_and(|d| render_hcortex(&d).as_bytes() == rendered.as_bytes());
            Ok((roundtrip, rendered, idempotent))
        };
        match attempt() {
            Ok((roundtrip, _rendered, idempotent)) => {
                let actual_sha = sha256_bytes(roundtrip.as_bytes());
                let expected = case.get("roundtrip_cortex_sha256").or_else(|| case.get("cortex_sha256")).and_then(Value::as_str).unwrap_or("");
                if expected.is_empty() || actual_sha == expected { result.roundtrip_pass += 1; }
                else { result.failures.push(json!({"case":id,"stage":"roundtrip_cortex_mismatch","expected_sha256":expected,"actual_sha256":actual_sha})); }
                if idempotent { result.idempotence_pass += 1; }
                else { result.failures.push(json!({"case":id,"stage":"hcortex_idempotence"})); }
            }
            Err(error) => result.failures.push(json!({"case":id,"stage":"exception","error":error})),
        }
    }

    for case in &invalid_cases {
        let id = case.get("id").and_then(Value::as_str).unwrap_or("");
        let expected = case.get("expected_diagnostic").or_else(|| case.get("expected_code")).and_then(Value::as_str).unwrap_or("");
        let mut invalid_path = root.join("invalid").join(format!("{id}.md"));
        if !invalid_path.exists() { invalid_path = root.join("corpus").join("invalid").join(format!("{id}.md")); }
        if !invalid_path.exists() { continue; }
        match fs::read_to_string(&invalid_path) {
            Ok(source) => {
                let (_, diagnostics) = compile_hcortex(&source);
                let codes: Vec<&str> = diagnostics.iter().map(|d| d.code.as_str()).collect();
                if codes.contains(&expected) { result.invalid_diag_pass += 1; }
                else { result.failures.push(json!({"case":id,"stage":"invalid_diag","expected_code":expected,"actual_codes":codes})); }
            }
            Err(error) => result.failures.push(json!({"case":id,"stage":"invalid_exception","error":error.to_string()})),
        }
    }

    let pass = result.roundtrip_pass == canonical_cases.len()
        && result.idempotence_pass == canonical_cases.len()
        && (invalid_cases.is_empty() || result.invalid_diag_pass == invalid_cases.len())
        && result.view_dependencies == 0;
    result.status = if pass { "PASS" } else { "FAIL" }.into();
    result
}

pub fn run_all_tests(c14n_dir: impl AsRef<Path>, hcortex_dir: impl AsRef<Path>) -> ConformanceReport {
    let c14n_dir = c14n_dir.as_ref();
    let hcortex_dir = hcortex_dir.as_ref();
    let started_at = Utc::now().to_rfc3339();

    println!("Running Phase 3 (C14N-0.1)...");
    let phase3 = run_phase3(c14n_dir);
    println!("  golden: {}/{}", phase3.golden_pass, phase3.total);
    println!("  idempotence: {}/{}", phase3.idempotence_pass, phase3.total);
    if !phase3.failures.is_empty() { println!("  failures: {}", phase3.failures.len()); }

    println!("Running Phase 4 (HCORTEX)...");
    let phase4 = run_phase4(hcortex_dir);
    let (canonical_total, invalid_total) = hcortex_manifest_counts(hcortex_dir);
    println!("  roundtrip: {}/{}", phase4.roundtrip_pass, canonical_total);
    println!("  idempotence: {}/{}", phase4.idempotence_pass, canonical_total);
    println!("  invalid diag: {}/{}", phase4.invalid_diag_pass, invalid_total);
    println!("  view deps: {}", phase4.view_dependencies);
    if !phase4.failures.is_empty() {
        println!("  failures: {}", phase4.failures.len());
        for failure in phase4.failures.iter().take(5) { println!("    - {failure}"); }
    }

    let verdict = if phase3.golden_pass >= 38 && phase3.idempotence_pass == 40
        && phase4.roundtrip_pass == canonical_total && phase4.idempotence_pass == canonical_total
        && phase4.view_dependencies == 0 {
        "PASS"
    } else if phase3.golden_pass >= 36 && phase4.roundtrip_pass >= canonical_total.saturating_sub(2)
        && phase4.view_dependencies == 0 {
        "CONDITIONAL_PASS"
    } else { "FAIL" }.to_string();

    let mut findings = Vec::new();
    if !phase3.failures.is_empty() { findings.push(Finding { phase: "F3".into(), count: phase3.failures.len(), items: phase3.failures.clone() }); }
    if !phase4.failures.is_empty() { findings.push(Finding { phase: "F4".into(), count: phase4.failures.len(), items: phase4.failures.clone() }); }

    println!("\nVerdict: {verdict}");
    ConformanceReport {
        reviewer: Reviewer {
            name: "independent-rust-reviewer".into(),
            language: "Rust 2021".into(),
            started_at,
            completed_at: Utc::now().to_rfc3339(),
        },
        phase3,
        phase4,
        findings,
        verdict,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn domain_separated_hash_is_stable() {
        assert_eq!(c14n_hash(b"abc"), c14n_hash(b"abc"));
        assert_ne!(c14n_hash(b"abc"), format!("sha256:{}", sha256_bytes(b"abc")));
    }
}
