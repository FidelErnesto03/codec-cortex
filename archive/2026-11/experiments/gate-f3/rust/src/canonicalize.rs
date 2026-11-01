use sha2::{Sha256, Digest};
use std::collections::HashMap;
use unicode_normalization::UnicodeNormalization;

use crate::{Parser, Scalar};

#[derive(Debug, Clone, serde::Serialize)]
pub struct Report {
    pub canonicalization: String,
    pub inputSha256: String,
    pub canonicalSha256: String,
    pub canonicalHash: String,
    pub changed: bool,
    pub structuralLoss: bool,
    pub losses: Vec<String>,
    pub sourceFidelityChanges: Vec<String>,
    pub diagnostics: Vec<String>,
}

/// Main entry point: canonicalize raw CORTEX 0.1 bytes.
/// Returns (canonical_bytes, report).
pub fn canonicalize(raw: &[u8]) -> (Vec<u8>, Report) {
    // Detect changes
    let mut changes: Vec<String> = Vec::new();

    // Normalize newlines for change detection
    let raw_text = String::from_utf8_lossy(raw);
    if raw_text.contains('\r') {
        changes.push("newline-normalized".to_string());
    }

    // Check for comments
    let normalized_text = raw_text.replace("\r\n", "\n").replace('\r', "\n");
    let has_comments = normalized_text.lines().any(|l| l.trim().starts_with('#'));
    if has_comments {
        changes.push("comments-removed".to_string());
    }

    // Check for blank lines (internal, not the last line which may be empty)
    // Python oracle checks lines[:-1] for blanks
    let all_lines: Vec<&str> = normalized_text.split('\n').collect();
    let has_internal_blanks = if all_lines.len() > 1 {
        all_lines[..all_lines.len() - 1].iter()
            .any(|l| l.trim().is_empty())
    } else {
        false
    };
    if has_internal_blanks {
        changes.push("blank-lines-removed".to_string());
    }

    // Parse
    let input_clean = raw_text.replace("\r\n", "\n").replace('\r', "\n");
    let mut parser = Parser::new(&input_clean);
    parser.parse_document();

    // Build canonical output
    let mut out_lines: Vec<String> = Vec::new();

    // $0 header
    out_lines.push("$0".to_string());

    // --- Canonical meta order ---
    let ordered_metas = extract_metas_ordered(&parser);
    let original_meta_names: Vec<String> = parser.glossary.as_ref()
        .map(|g| g.meta.iter().map(|m| m.name.clone()).collect())
        .unwrap_or_default();

    if ordered_metas.iter().map(|(n,_)| n.clone()).collect::<Vec<_>>() != original_meta_names {
        if !changes.contains(&"glossary-order-normalized".to_string()) {
            changes.push("glossary-order-normalized".to_string());
        }
    }

    for (name, attrs) in &ordered_metas {
        let cat = meta_category(name);
        let base_order: &[&str] = match cat.0 {
            0 => &["cortex", "encoding", "language"],
            1 => &["values"],
            2 => &["expand"],
            3 => &["id", "version", "required", "desc"],
            4 => &["namespace", "id", "version", "required", "desc"],
            _ => &[],
        };

        let keys = ordered_keys(attrs, base_order);
        let prev_keys: Vec<String> = attrs.keys().cloned().collect();
        if keys != prev_keys {
            if !changes.contains(&"attribute-order-normalized".to_string()) {
                changes.push("attribute-order-normalized".to_string());
            }
        }

        let attrs_str = emit_attrs_str(&keys, attrs, &parser.micro_map);
        out_lines.push(format!("$0:{}{}", name, attrs_str));
    }

    // --- Canonical symbol order ---
    let ordered_symbols = extract_symbols_ordered(&parser);
    if let Some(g) = &parser.glossary {
        let orig_syms: Vec<String> = g.symbols.iter().map(|s| s.surface.clone()).collect();
        let new_syms: Vec<String> = ordered_symbols.iter().map(|s| s.surface.clone()).collect();
        if orig_syms != new_syms {
            if !changes.contains(&"glossary-order-normalized".to_string()) {
                changes.push("glossary-order-normalized".to_string());
            }
        }
    }

    for sd in &ordered_symbols {
        let base_symbol_order = &["type", "weight", "fields", "pos", "focus", "desc", "open", "namespace", "version"];
        let sym_attrs = extract_symbol_attrs(sd);
        let keys = ordered_keys(&sym_attrs, base_symbol_order);
        let prev_keys: Vec<String> = sym_attrs.keys().cloned().collect();
        if keys != prev_keys {
            if !changes.contains(&"attribute-order-normalized".to_string()) {
                changes.push("attribute-order-normalized".to_string());
            }
        }

        let sigil = sd.surface.clone();
        let label = sd.label.clone();
        let attrs_str = emit_attrs_str(&keys, &sym_attrs, &parser.micro_map);
        out_lines.push(format!("{}:{}{}", sigil, label, attrs_str));
    }

    // --- Sections ---
    for sec in &parser.sections {
        let title_str = if let Some(ref t) = sec.title {
            let nfc_title: String = t.chars().nfc().collect();
            format!(": {}", nfc_title)
        } else {
            String::new()
        };
        out_lines.push(format!("${}{}", sec.id, title_str));

        for idea in &sec.ideas {
            let shape = determine_idea_shape(idea, &parser.symbol_map);

            let head = format!("{}:{}", idea.qualifiedSymbol, idea.name);

            match shape.as_str() {
                "attrs" => {
                    let sym_def = parser.symbol_map.get(&idea.symbol)
                        .or_else(|| parser.symbol_map.values().find(|s| s.qualified == idea.symbol));
                    let contract = if let Some(ref sd) = sym_def {
                        &sd.contract
                    } else {
                        &vec![]
                    };
                    let contract_names: Vec<String> = contract.iter().map(|f| f.name.clone()).collect();
                    let payload_map = extract_idea_attrs_payload(idea);
                    let mut extras: Vec<String> = payload_map.keys()
                        .filter(|k| !contract_names.contains(k))
                        .cloned()
                        .collect();
                    extras.sort_by(|a, b| {
                        let a_nfc: String = a.chars().nfc().collect();
                        let b_nfc: String = b.chars().nfc().collect();
                        a_nfc.cmp(&b_nfc)
                    });
                    let keys: Vec<String> = contract_names.iter()
                        .filter(|k| payload_map.contains_key(*k))
                        .cloned()
                        .chain(extras)
                        .collect();

                    let prev_keys: Vec<String> = payload_map.keys().cloned().collect();
                    if keys != prev_keys {
                        if !changes.contains(&"attribute-order-normalized".to_string()) {
                            changes.push("attribute-order-normalized".to_string());
                        }
                    }

                    // Check for microtoken expansion
                    for k in &keys {
                        if let Some(val) = payload_map.get(k) {
                            if let Scalar::AtomValue { ref value, .. } = val {
                                if parser.micro_map.contains_key(value) {
                                    if !changes.contains(&"microtoken-expanded".to_string()) {
                                        changes.push("microtoken-expanded".to_string());
                                    }
                                }
                            }
                        }
                    }

                    let focus = sym_def.map(|sd| sd.focus.as_str());
                    let attrs_str = emit_idea_attrs(&keys, &payload_map, contract, focus, &parser.micro_map);
                    out_lines.push(format!("{}{}", head, attrs_str));
                }
                "attrs-pos" | "relacion" => {
                    let cells = extract_pipe_cells(idea);
                    let sym_def = parser.symbol_map.get(&idea.symbol)
                        .or_else(|| parser.symbol_map.values().find(|s| s.qualified == idea.symbol));
                    let contract = if let Some(ref sd) = sym_def {
                        &sd.contract
                    } else {
                        &vec![]
                    };

                    let mut cell_strs: Vec<String> = Vec::new();
                    for (idx, s) in cells.iter().enumerate() {
                        let field_type = if idx < contract.len() {
                            contract[idx].field_type.clone()
                        } else {
                            "any".to_string()
                        };
                        let ex = expand_micro_scalar(s, &parser.micro_map);
                        if let Scalar::AtomValue { ref value, .. } = s {
                            if parser.micro_map.contains_key(value) {
                                if !changes.contains(&"microtoken-expanded".to_string()) {
                                    changes.push("microtoken-expanded".to_string());
                                }
                            }
                        }
                        let base_type = field_type.trim_end_matches('?');
                        if base_type == "text" {
                            let val_str = get_scalar_text(&ex);
                            let val_nfc: String = val_str.chars().nfc().collect();
                            if val_nfc.is_empty() || (!val_nfc.contains('|') && !val_nfc.contains('\n') && val_nfc.trim() == val_nfc && !val_nfc.starts_with('"') && val_nfc == val_nfc.trim()) {
                                cell_strs.push(val_nfc);
                            } else {
                                cell_strs.push(emit_string(&val_nfc));
                            }
                            continue;
                        }
                        cell_strs.push(emit_scalar_str(&ex, &parser.micro_map));
                    }
                    out_lines.push(format!("{}|{}", head, cell_strs.join("|")));
                }
                "cuerpo" => {
                    let val = extract_body_text(idea);
                    let val = val.replace("\r\n", "\n").replace('\r', "\n");
                    let val_nfc: String = val.chars().nfc().collect();
                    if val_nfc.contains('\n') {
                        out_lines.push(format!("{}{{", head));
                        for line in val_nfc.split('\n') {
                            out_lines.push(line.to_string());
                        }
                        out_lines.push("}".to_string());
                    } else {
                        out_lines.push(format!("{}{{{}}}", head, val_nfc));
                    }
                }
                "bloque" => {
                    let val = extract_body_text(idea);
                    // Bloque: CRLF→LF only, no NFC
                    let val = val.replace("\r\n", "\n").replace('\r', "\n");
                    out_lines.push(format!("{}{{", head));
                    for line in val.split('\n') {
                        out_lines.push(line.to_string());
                    }
                    out_lines.push("}".to_string());
                }
                _ => {
                    let payload_map = extract_idea_attrs_payload(idea);
                    let mut keys: Vec<String> = payload_map.keys().cloned().collect();
                    keys.sort();
                    let attrs_str = emit_idea_attrs(&keys, &payload_map, &vec![], None, &parser.micro_map);
                    out_lines.push(format!("{}{}", head, attrs_str));
                }
            }
        }
    }

    let out_text = out_lines.join("\n") + "\n";
    let out_bytes = out_text.into_bytes();

    // Detect source change
    if out_bytes != raw {
        if !changes.contains(&"source-form-normalized".to_string()) {
            changes.push("source-form-normalized".to_string());
        }
    }

    // Deduplicate changes while preserving order
    let mut seen = std::collections::HashSet::new();
    changes.retain(|c| seen.insert(c.clone()));

    // Compute hashes
    let raw_sha = sha256_hex(raw);
    let can_sha = sha256_hex(&out_bytes);

    let mut hasher = Sha256::new();
    hasher.update(b"CORTEX-C14N-0.1\x00");
    hasher.update(&out_bytes);
    let chash = format!("sha256:{}", hex_encode(&hasher.finalize()));

    let report = Report {
        canonicalization: "C14N-0.1".to_string(),
        inputSha256: raw_sha,
        canonicalSha256: can_sha,
        canonicalHash: chash,
        changed: out_bytes != raw,
        structuralLoss: false,
        losses: Vec::new(),
        sourceFidelityChanges: changes,
        diagnostics: Vec::new(),
    };

    (out_bytes, report)
}

// ===== Determine shape for idea =====
fn determine_idea_shape(idea: &crate::Idea, symbol_map: &HashMap<String, crate::SymbolDefinition>) -> String {
    if idea.shape != "attrs" {
        return idea.shape.clone();
    }
    // Check symbol definition for authoritative shape
    if let Some(sd) = symbol_map.get(&idea.symbol) {
        return sd.shape.clone();
    }
    if let Some(sd) = symbol_map.values().find(|s| s.qualified == idea.symbol) {
        return sd.shape.clone();
    }
    idea.shape.clone()
}

// ===== Helper: meta category for ordering =====

fn meta_category(name: &str) -> (u32, String) {
    if name == "format" {
        return (0, String::new());
    }
    for (idx, prefix) in ["enum_", "micro_", "namespace_", "extension_"].iter().enumerate() {
        if name.starts_with(prefix) {
            return ((idx + 1) as u32, name[prefix.len()..].to_string());
        }
    }
    (5, name.to_string())
}

// ===== Extract metas in canonical order =====

fn extract_metas_ordered(parser: &Parser) -> Vec<(String, HashMap<String, Scalar>)> {
    let meta_names: Vec<String> = parser.glossary.as_ref()
        .map(|g| g.meta.iter().map(|m| m.name.clone()).collect())
        .unwrap_or_default();

    let mut meta_map: HashMap<String, HashMap<String, Scalar>> = HashMap::new();

    for name in &meta_names {
        let attrs = extract_meta_attrs(name, parser);
        meta_map.insert(name.clone(), attrs);
    }

    let mut sorted: Vec<(String, HashMap<String, Scalar>)> = meta_map.into_iter().collect();
    sorted.sort_by(|(a_name, _), (b_name, _)| {
        let (a_cat, a_sub) = meta_category(a_name);
        let (b_cat, b_sub) = meta_category(b_name);
        if a_cat != b_cat {
            a_cat.cmp(&b_cat)
        } else if a_cat == 0 {
            let a_nfc: String = a_name.chars().nfc().collect();
            let b_nfc: String = b_name.chars().nfc().collect();
            a_nfc.cmp(&b_nfc)
        } else {
            let a_nfc: String = a_sub.chars().nfc().collect();
            let b_nfc: String = b_sub.chars().nfc().collect();
            a_nfc.cmp(&b_nfc)
        }
    });

    sorted
}

fn extract_meta_attrs(name: &str, parser: &Parser) -> HashMap<String, Scalar> {
    let g = match &parser.glossary { Some(g) => g, None => return HashMap::new() };

    if name == "format" {
        let mut map = HashMap::new();
        for attr in &g.format.attributes {
            map.insert(attr.key.clone(), *attr.value.clone());
        }
        return map;
    }

    if name.starts_with("enum_") {
        let enum_name = &name[5..];
        for en in &g.enums {
            if en.name == enum_name {
                let mut map = HashMap::new();
                let vals = en.values.join("|");
                map.insert("values".to_string(), Scalar::StringValue {
                    value: vals,
                    lexeme: format!("\"{}\"", en.values.join("|")),
                });
                return map;
            }
        }
        return HashMap::new();
    }

    if name.starts_with("micro_") {
        let micro_name = &name[6..];
        for mic in &g.micros {
            if mic.token == micro_name {
                let mut map = HashMap::new();
                map.insert("expand".to_string(), Scalar::AtomValue {
                    value: mic.expand.clone(),
                    lexeme: mic.expand.clone(),
                    micro: None,
                });
                return map;
            }
        }
        return HashMap::new();
    }

    if name.starts_with("namespace_") {
        let alias = &name[10..];
        if let Some(ns) = parser.namespace_map.get(alias) {
            let mut map = HashMap::new();
            for attr in &ns.attributes {
                map.insert(attr.key.clone(), *attr.value.clone());
            }
            return map;
        }
        return HashMap::new();
    }

    if name.starts_with("extension_") {
        let ext_name = &name[10..];
        for ext in &g.extensions {
            if ext.name == ext_name {
                let mut map = HashMap::new();
                for attr in &ext.attributes {
                    map.insert(attr.key.clone(), *attr.value.clone());
                }
                return map;
            }
        }
        return HashMap::new();
    }

    // Other meta - use md.attributes
    for md in &g.meta {
        if md.name == name {
            let mut map = HashMap::new();
            for attr in &md.attributes {
                map.insert(attr.key.clone(), *attr.value.clone());
            }
            return map;
        }
    }

    HashMap::new()
}

// ===== Extract symbols in canonical order =====

fn extract_symbols_ordered(parser: &Parser) -> Vec<crate::SymbolDefinition> {
    let g = match &parser.glossary { Some(g) => g, None => return vec![] };

    let mut syms = g.symbols.clone();
    syms.sort_by(|a, b| {
        let a_key: String = a.surface.chars().nfc().collect();
        let b_key: String = b.surface.chars().nfc().collect();
        a_key.cmp(&b_key)
    });
    syms
}

// ===== Extract symbol attributes from SymbolDefinition =====

fn extract_symbol_attrs(sd: &crate::SymbolDefinition) -> HashMap<String, Scalar> {
    let mut map = HashMap::new();
    for attr in &sd.attributes {
        map.insert(attr.key.clone(), *attr.value.clone());
    }
    map
}

// ===== Extract idea payload as attrs =====

fn extract_idea_attrs_payload(idea: &crate::Idea) -> HashMap<String, Scalar> {
    let mut map = HashMap::new();
    match &idea.payload {
        crate::Payload::Attrs(ap) => {
            for pair in &ap.pairs {
                map.insert(pair.key.clone(), *pair.value.clone());
            }
        }
        _ => {}
    }
    map
}

// ===== Extract positional cells =====

fn extract_pipe_cells(idea: &crate::Idea) -> Vec<Scalar> {
    match &idea.payload {
        crate::Payload::Positional(pp) => pp.cells.clone(),
        crate::Payload::Relation(rp) => rp.cells.clone(),
        _ => vec![],
    }
}

// ===== Extract body text =====

fn extract_body_text(idea: &crate::Idea) -> String {
    match &idea.payload {
        crate::Payload::Text(tp) => tp.text.clone(),
        crate::Payload::Block(bp) => bp.text.clone(),
        _ => String::new(),
    }
}

// ===== Ordered keys =====

fn ordered_keys(attrs: &HashMap<String, Scalar>, base: &[&str]) -> Vec<String> {
    let mut result: Vec<String> = Vec::new();
    for &b in base {
        if attrs.contains_key(b) {
            result.push(b.to_string());
        }
    }

    let mut extras: Vec<String> = attrs.keys()
        .filter(|k| !base.contains(&k.as_str()))
        .cloned()
        .collect();
    extras.sort_by(|a, b| {
        let a_nfc: String = a.chars().nfc().collect();
        let b_nfc: String = b.chars().nfc().collect();
        a_nfc.cmp(&b_nfc)
    });

    result.extend(extras);
    result
}

// ===== Emit helpers =====

fn emit_string(v: &str) -> String {
    let v_nfc: String = v.chars().nfc().collect();
    let mut out = String::from("\"");
    for ch in v_nfc.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\x08' => out.push_str("\\b"),
            '\x0c' => out.push_str("\\f"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            _ if (ch as u32) < 0x20 || ch as u32 == 0x7f => {
                out.push_str(&format!("\\u{:04X}", ch as u32));
            }
            _ => out.push(ch),
        }
    }
    out.push('"');
    out
}

fn atom_safe(s: &str) -> bool {
    if s.is_empty() {
        return false;
    }
    !s.chars().any(|c| {
        c.is_whitespace() || c == '[' || c == ']' || c == '{' || c == '}' || c == ',' || c == '"' || c == '|'
    })
}

fn emit_scalar_str(s: &Scalar, micros: &HashMap<String, String>) -> String {
    let s_expanded = expand_micro_scalar(s, micros);
    match &s_expanded {
        Scalar::StringValue { value, .. } => emit_string(value),
        Scalar::AtomValue { value, .. } => {
            let val_nfc: String = value.chars().nfc().collect();
            if atom_safe(&val_nfc) {
                val_nfc
            } else {
                emit_string(&val_nfc)
            }
        }
        Scalar::IntegerValue { value, .. } => {
            if value == "0" || value == "-0" {
                "0".to_string()
            } else {
                let neg = value.starts_with('-');
                let digits = if neg { &value[1..] } else { value.as_str() };
                let trimmed = digits.trim_start_matches('0');
                let result = if trimmed.is_empty() { "0" } else { trimmed };
                if neg {
                    format!("-{}", result)
                } else {
                    result.to_string()
                }
            }
        }
        Scalar::DecimalValue { value, .. } => {
            value.clone()
        }
        Scalar::BooleanValue { value, .. } => {
            if *value { "true".to_string() } else { "false".to_string() }
        }
        Scalar::NullValue { .. } => "null".to_string(),
        Scalar::ListValue { items, .. } => {
            let inner: Vec<String> = items.iter().map(|i| emit_scalar_str(i, micros)).collect();
            format!("[{}]", inner.join(","))
        }
    }
}

fn expand_micro_scalar(s: &Scalar, micros: &HashMap<String, String>) -> Scalar {
    match s {
        Scalar::AtomValue { value, .. } if micros.contains_key(value) => {
            let expanded = &micros[value];
            crate::parse_scalar_from_str(expanded)
        }
        Scalar::ListValue { items, lexeme } => {
            let new_items: Vec<Scalar> = items.iter()
                .map(|i| expand_micro_scalar(i, micros))
                .collect();
            Scalar::ListValue { items: new_items, lexeme: lexeme.clone() }
        }
        _ => s.clone(),
    }
}

fn emit_attrs_str(keys: &[String], attrs: &HashMap<String, Scalar>, micros: &HashMap<String, String>) -> String {
    let parts: Vec<String> = keys.iter()
        .map(|k| {
            let v = attrs.get(k).unwrap();
            format!("{}:{}", k, emit_scalar_str(v, micros))
        })
        .collect();
    format!("{{{}}}", parts.join(","))
}

fn get_scalar_text(s: &Scalar) -> String {
    match s {
        Scalar::StringValue { value, .. } => value.clone(),
        Scalar::AtomValue { value, .. } => value.clone(),
        Scalar::IntegerValue { value, .. } => value.clone(),
        Scalar::DecimalValue { value, .. } => value.clone(),
        Scalar::BooleanValue { value, .. } => value.to_string(),
        Scalar::NullValue { .. } => String::new(),
        Scalar::ListValue { items, .. } => {
            items.iter().map(|i| get_scalar_text(i)).collect::<Vec<_>>().join(",")
        }
    }
}

fn emit_idea_attrs(keys: &[String], attrs: &HashMap<String, Scalar>, contract: &[crate::ContractField], focus: Option<&str>, micros: &HashMap<String, String>) -> String {
    let parts: Vec<String> = keys.iter().map(|k| {
        let raw_val = attrs.get(k).unwrap();
        let ex = expand_micro_scalar(raw_val, micros);
        let field_type = contract.iter()
            .find(|f| f.name == *k)
            .map(|f| f.field_type.as_str())
            .unwrap_or("any");

        let base_type = field_type.trim_end_matches('?');

        if base_type == "text" {
            let text_str = get_scalar_text(&ex);
            let text_nfc: String = text_str.chars().nfc().collect();
            let is_focus = focus.map(|f| f == k.as_str()).unwrap_or(false);
            if is_focus || !atom_safe(&text_nfc) {
                format!("{}:{}", k, emit_string(&text_nfc))
            } else {
                format!("{}:{}", k, text_nfc)
            }
        } else {
            format!("{}:{}", k, emit_scalar_str(&ex, micros))
        }
    }).collect();
    format!("{{{}}}", parts.join(","))
}

fn sha256_hex(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hex_encode(&hasher.finalize())
}

fn hex_encode(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{:02x}", b)).collect()
}
