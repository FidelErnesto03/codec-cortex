//! CORTEX 1.0 declared loss report (spec §8.2 / §8.3), reference-parity surface.

use serde_json::{json, Value};
use unicode_normalization::UnicodeNormalization;

use crate::harness::sha256_bytes;
use crate::v10::{canonicalize_any, compile_any, parse_any, render_any, AnyDoc, V10Doc, V10Payload};

const L402: &str = "L402_COMMENT_DROPPED";
const L403: &str = "L403_INTRALINE_WHITESPACE";
const L405: &str = "L405_OPEN_ATTR_ORDER";
const L406: &str = "L406_COMPILE_SIDE_DROP";
const L499: &str = "L499_UNCLASSIFIED_LOSS";

const PRESERVED: [&str; 4] = ["blocks", "identity", "scalars", "structure"];

// Coverage declaration (spec §8.2): which pipeline operations the report
// models. The compile pipeline (source -> AST) is not modelled, so declaring
// it explicitly keeps `reversible: true` honest about its scope.
const COVERED_OPERATIONS: [&str; 1] = ["render"];
const UNCOVERED_OPERATIONS: [&str; 1] = ["compile"];

fn detail(code: &str) -> &'static str {
    match code {
        L402 => "comment line outside a multiline body is not represented in the AST",
        L403 => "intraline whitespace is collapsed by canonicalization",
        L405 => "editorial attribute order of an open sigil is not preserved",
        L406 => "an idea present in the AST is lost across the render/compile roundtrip (its rendered header does not round-trip)",
        _ => "roundtrip diverges and no declared loss classifies the divergence",
    }
}

fn action(code: &str) -> &'static str {
    if code == L499 || code == L406 {
        "fix-surface"
    } else {
        "declare-only"
    }
}

fn finding(code: &str, path: &str, category: &str, recoverability: &str) -> Value {
    json!({
        "action": action(code),
        "category": category,
        "code": code,
        "detail": detail(code),
        "path": path,
        "recoverability": recoverability,
        "severity": if code == L499 || code == L406 { "error" } else { "loss" },
    })
}

fn idea_keys_v10(doc: &V10Doc) -> std::collections::HashSet<String> {
    let mut keys = std::collections::HashSet::new();
    for section in &doc.sections {
        for idea in &section.ideas {
            keys.insert(format!(
                "{}|{}|{}|{}",
                section.id,
                idea.namespace.clone().unwrap_or_default(),
                idea.symbol,
                idea.name
            ));
        }
    }
    keys
}

fn idea_keys_any(doc: &AnyDoc) -> std::collections::HashSet<String> {
    match doc {
        AnyDoc::V10(d) => idea_keys_v10(d),
        AnyDoc::V01(_) => std::collections::HashSet::new(),
    }
}

fn strip_quoted(line: &str) -> String {
    let mut out = String::new();
    let chars: Vec<char> = line.chars().collect();
    let mut i = 0;
    while i < chars.len() {
        if chars[i] != '"' {
            out.push(chars[i]);
            i += 1;
            continue;
        }
        out.push_str("\"\"");
        i += 1;
        while i < chars.len() {
            if chars[i] == '\\' {
                i += 2;
                continue;
            }
            if chars[i] == '"' {
                i += 1;
                break;
            }
            i += 1;
        }
    }
    out
}

fn lexical_losses(source: &str) -> Vec<Value> {
    let mut losses = Vec::new();
    let mut in_body = false;
    for (index, raw) in source.split('\n').enumerate() {
        let line = raw.strip_suffix('\r').unwrap_or(raw);
        let stripped = line.trim();
        if in_body {
            if stripped == "}" {
                in_body = false;
            }
            continue;
        }
        if stripped.is_empty() {
            continue;
        }
        if stripped.starts_with('#') {
            losses.push(finding(L402, &format!("line:{}", index + 1), "structure", "from-source-only"));
            continue;
        }
        if stripped.ends_with('{') && !stripped.starts_with("$0:") {
            in_body = true;
        }
        let probe = strip_quoted(line);
        let trailing = probe.trim_end_matches([' ', '\t']);
        if trailing.len() != probe.len() || probe.contains('\t') || probe.contains("  ") {
            losses.push(finding(L403, &format!("line:{}", index + 1), "presentation", "from-source-only"));
        }
    }
    losses
}

fn open_attr_order_losses(doc: &crate::v10::V10Doc) -> Vec<Value> {
    let mut losses = Vec::new();
    for section in &doc.sections {
        for idea in &section.ideas {
            let attrs = match &idea.payload {
                V10Payload::Attrs(attrs) => attrs,
                _ => continue,
            };
            let sym = doc
                .glossary
                .symbols
                .iter()
                .find(|s| s.sigil == idea.symbol && s.namespace == idea.namespace);
            let sym = match sym {
                Some(sym) if sym.open => sym,
                _ => continue,
            };
            let keys: Vec<&str> = attrs.iter().map(|(k, _)| k.as_str()).collect();
            let contract: Vec<&str> = sym.contract.iter().map(|f| f.name.as_str()).collect();
            let mut expected: Vec<&str> = contract
                .iter()
                .copied()
                .filter(|name| keys.contains(name))
                .collect();
            let mut extras: Vec<&str> = keys
                .iter()
                .copied()
                .filter(|key| !contract.contains(key))
                .collect();
            extras.sort_by(|a, b| a.nfc().collect::<String>().cmp(&b.nfc().collect::<String>()));
            expected.extend(extras);
            if keys != expected {
                losses.push(finding(L405, &format!("${}", section.id), "order", "from-source-only"));
            }
        }
    }
    losses
}

fn dedupe(mut losses: Vec<Value>) -> Vec<Value> {
    let mut seen: Vec<(String, String)> = Vec::new();
    let mut out = Vec::new();
    for item in losses.drain(..) {
        let path = item["path"].as_str().unwrap_or("").to_string();
        let code = item["code"].as_str().unwrap_or("").to_string();
        if seen.iter().any(|(p, c)| p == &path && c == &code) {
            continue;
        }
        seen.push((path, code));
        out.push(item);
    }
    out.sort_by(|a, b| {
        let left = (a["path"].as_str().unwrap_or(""), a["code"].as_str().unwrap_or(""));
        let right = (b["path"].as_str().unwrap_or(""), b["code"].as_str().unwrap_or(""));
        left.cmp(&right)
    });
    out
}

/// Build the declared loss report for a `cortex:1.0` source.
pub fn build_loss_report(source: &str, case_name: &str) -> Result<Value, String> {
    let mut doc = parse_any(source).map_err(|e| e.to_string())?;
    let v10 = match &doc {
        AnyDoc::V10(d) => {
            if d.cortex_version != "1.0" {
                return Err(format!(
                    "loss-report requires cortex:1.0 (declared: {})",
                    d.cortex_version
                ));
            }
            d.clone()
        }
        _ => return Err("loss-report requires cortex:1.0 (declared: 0.1)".to_string()),
    };

    // Render and detect source-order losses before canonicalizing: C14N mutates
    // the AST in place (microtoken expansion, attribute normalization).
    let attr_losses = open_attr_order_losses(&v10);
    let src_ideas = idea_keys_v10(&v10);
    let rendered = render_any(&doc);
    let canonical_source = canonicalize_any(&mut doc);
    let roundtrip = compile_any(&rendered).map_err(|e| e.to_string())?;
    let mut roundtrip_doc = roundtrip;
    let rt_ideas = idea_keys_any(&roundtrip_doc);
    let canonical_roundtrip = canonicalize_any(&mut roundtrip_doc);

    let dropped = src_ideas.iter().any(|key| !rt_ideas.contains(key));
    let mut losses = lexical_losses(source);
    losses.extend(attr_losses);
    let equivalent = canonical_source == canonical_roundtrip;
    if dropped {
        losses.push(finding(L406, "$", "structure", "irrecoverable"));
    }
    if !equivalent && !dropped {
        losses.push(finding(L499, "$", "structure", "irrecoverable"));
    }

    Ok(json!({
        "case": case_name,
        "coverage": {
            "complete": UNCOVERED_OPERATIONS.len() == 0 && equivalent,
            "operations": COVERED_OPERATIONS,
            "uncovered_operations": UNCOVERED_OPERATIONS,
        },
        "losses": dedupe(losses),
        "mode": "canonical",
        "operation": "render",
        "preserved": PRESERVED,
        "reversible": equivalent,
        "schema_version": "1.0",
        "source_format": "cortex:1.0",
        "source_sha256": sha256_bytes(source.as_bytes()),
        "structural_equivalence": equivalent,
        "target_format": "hcortex:1.0",
        "target_sha256": sha256_bytes(rendered.as_bytes()),
        "warnings": Vec::<Value>::new(),
    }))
}

/// Canonical JSON serialization (sorted keys, 2-space indent, final newline).
pub fn dumps_canonical(report: &Value) -> String {
    let mut text = serde_json::to_string_pretty(report).expect("loss report serializes");
    text.push('\n');
    text
}

/// True when the report carries an error-severity finding.
pub fn has_errors(report: &Value) -> bool {
    report["losses"]
        .as_array()
        .map(|items| items.iter().any(|item| item["severity"] == "error"))
        .unwrap_or(false)
}

/// Derive the report `case` from a path, matching the reference implementation.
pub fn loss_case_name(path: &str) -> String {
    if path.is_empty() || path == "-" {
        return "stdin".to_string();
    }
    let base = path.rsplit(['/', '\\']).next().unwrap_or(path);
    match base.rfind('.') {
        Some(idx) if idx > 0 => base[..idx].to_string(),
        _ => base.to_string(),
    }
}
