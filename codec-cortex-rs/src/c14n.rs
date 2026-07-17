use std::collections::{HashMap, HashSet};

use crate::model::*;
use crate::scalars::{atom_matches, emit_string_literal, to_nfc};

const FORMAT_KEY_ORDER: &[&str] = &["cortex", "encoding", "language"];
const SIGIL_KEY_ORDER: &[&str] = &["type", "weight", "fields", "pos", "focus", "desc", "open", "namespace", "version"];
const ENUM_KEY_ORDER: &[&str] = &["values"];
const MICRO_KEY_ORDER: &[&str] = &["expand"];
const NS_KEY_ORDER: &[&str] = &["id", "uri", "version", "required", "desc"];
const EXT_KEY_ORDER: &[&str] = &["namespace", "id", "version", "required", "desc"];

fn sort_keys_canonical(attrs: &Attrs, order: &[&str]) -> Attrs {
    let mut by_key: HashMap<&str, &Scalar> = HashMap::new();
    for (key, value) in attrs { by_key.insert(key, value); }
    let mut out = Vec::new();
    let mut used = HashSet::new();
    for key in order {
        if let Some(value) = by_key.get(key) {
            out.push(((*key).to_string(), (*value).clone()));
            used.insert(*key);
        }
    }
    let mut extras: Attrs = attrs.iter().filter(|(key, _)| !used.contains(key.as_str())).cloned().collect();
    extras.sort_by(|(a, _), (b, _)| to_nfc(a).as_bytes().cmp(to_nfc(b).as_bytes()));
    out.extend(extras);
    out
}

fn nfc_scalar(scalar: &Scalar) -> Scalar {
    match &scalar.value {
        ScalarValue::String(value) => {
            let value = to_nfc(value);
            Scalar::string(value.clone(), emit_string_literal(&value))
        }
        ScalarValue::Atom(value) => Scalar::atom(to_nfc(value)),
        ScalarValue::List(items) => Scalar::list(items.iter().map(nfc_scalar).collect()),
        _ => scalar.clone(),
    }
}

fn normalize_document(doc: &mut Document) {
    if let Some(format) = &mut doc.glossary.format {
        format.attrs = format.attrs.iter().map(|(k, v)| (k.clone(), nfc_scalar(v))).collect();
    }
    for item in &mut doc.glossary.enums { item.values = item.values.iter().map(|v| to_nfc(v)).collect(); }
    for item in &mut doc.glossary.micros { item.expand = to_nfc(&item.expand); }
    for item in &mut doc.glossary.namespaces { item.attrs = item.attrs.iter().map(|(k, v)| (k.clone(), nfc_scalar(v))).collect(); }
    for item in &mut doc.glossary.extensions { item.attrs = item.attrs.iter().map(|(k, v)| (k.clone(), nfc_scalar(v))).collect(); }
    for item in &mut doc.glossary.meta { item.attrs = item.attrs.iter().map(|(k, v)| (k.clone(), nfc_scalar(v))).collect(); }
    for symbol in &mut doc.glossary.symbols {
        symbol.attrs = symbol.attrs.iter().map(|(k, v)| (k.clone(), nfc_scalar(v))).collect();
        symbol.desc = to_nfc(&symbol.desc);
    }
    for section in &mut doc.sections {
        section.title = section.title.as_ref().map(|v| to_nfc(v));
        for idea in &mut section.ideas {
            match &mut idea.payload {
                IdeaPayload::Attrs(attrs) => *attrs = attrs.iter().map(|(k, v)| (k.clone(), nfc_scalar(v))).collect(),
                IdeaPayload::Positional(values) => *values = values.iter().map(nfc_scalar).collect(),
                IdeaPayload::Body(text) => *text = to_nfc(text),
                IdeaPayload::Block(_) | IdeaPayload::MultilinePending => {}
            }
        }
    }
}

fn expand_microtokens(doc: &mut Document) {
    let micros: HashMap<String, String> = doc.glossary.micros.iter().map(|m| (m.token.clone(), m.expand.clone())).collect();
    if micros.is_empty() { return; }
    for section in &mut doc.sections {
        for idea in &mut section.ideas {
            match &mut idea.payload {
                IdeaPayload::Attrs(attrs) => {
                    for (_, value) in attrs {
                        if let ScalarValue::Atom(atom) = &value.value {
                            if let Some(expanded) = micros.get(atom) { *value = Scalar::atom(expanded.clone()); }
                        }
                    }
                }
                IdeaPayload::Positional(values) => {
                    for value in values {
                        if let ScalarValue::Atom(atom) = &value.value {
                            if let Some(expanded) = micros.get(atom) { *value = Scalar::atom(expanded.clone()); }
                        }
                    }
                }
                _ => {}
            }
        }
    }
}

fn is_atom_safe_bare(s: &str) -> bool {
    !s.is_empty() && !s.chars().any(|c| c.is_whitespace() || matches!(c, '[' | ']' | '{' | '}' | ',' | '"' | '|'))
}

fn is_text_safe_bare(s: &str) -> bool {
    !s.is_empty() && !s.contains('\n') && !s.contains('\r') && !s.contains('|') && s == s.trim() && !s.starts_with('\"')
}

fn emit_scalar_attrs(value: &Scalar, is_focus_text: bool, is_text_field: bool) -> String {
    match &value.value {
        ScalarValue::String(text) => {
            if is_focus_text { value.lexeme.clone() }
            else if is_text_field && is_atom_safe_bare(text) && atom_matches(text) { text.clone() }
            else { value.lexeme.clone() }
        }
        ScalarValue::Atom(atom) => if is_atom_safe_bare(atom) { atom.clone() } else { emit_string_literal(atom) },
        _ => value.lexeme.clone(),
    }
}

fn emit_scalar_positional(value: &Scalar, is_text_field: bool) -> String {
    match &value.value {
        ScalarValue::String(text) => if is_text_field && is_text_safe_bare(text) { text.clone() } else { value.lexeme.clone() },
        ScalarValue::Atom(atom) => if is_atom_safe_bare(atom) { atom.clone() } else { emit_string_literal(atom) },
        _ => value.lexeme.clone(),
    }
}

fn emit_glossary_attrs(attrs: &Attrs) -> String {
    format!("{{{}}}", attrs.iter().map(|(k, v)| format!("{k}:{}", v.lexeme)).collect::<Vec<_>>().join(","))
}

fn symbol_canonical(symbol: &SymbolDef) -> String {
    format!("{}:{}{}", symbol.qualified(), symbol.label, emit_glossary_attrs(&sort_keys_canonical(&symbol.attrs, SIGIL_KEY_ORDER)))
}

fn idea_canonical(idea: &Idea, symbol: &SymbolDef) -> String {
    let head = format!("{}:{}", idea.qualified_symbol(), idea.name);
    match &idea.payload {
        IdeaPayload::Attrs(attrs) => {
            let mut pair_map: HashMap<&str, &Scalar> = HashMap::new();
            for (key, value) in attrs { pair_map.insert(key, value); }
            let mut output: Attrs = Vec::new();
            let mut used = HashSet::new();
            for field in &symbol.contract {
                if let Some(value) = pair_map.get(field.name.as_str()) {
                    output.push((field.name.clone(), (*value).clone()));
                    used.insert(field.name.as_str());
                }
            }
            if symbol.open {
                let mut extras: Attrs = attrs.iter().filter(|(k, _)| !used.contains(k.as_str())).cloned().collect();
                extras.sort_by(|(a, _), (b, _)| to_nfc(a).as_bytes().cmp(to_nfc(b).as_bytes()));
                output.extend(extras);
            }
            let types: HashMap<&str, &str> = symbol.contract.iter().map(|f| (f.name.as_str(), f.field_type.as_str())).collect();
            let parts = output.iter().map(|(key, value)| {
                let field_type = types.get(key.as_str()).copied().unwrap_or("any");
                format!("{key}:{}", emit_scalar_attrs(value, key == &symbol.focus && field_type == "text", field_type == "text"))
            }).collect::<Vec<_>>();
            format!("{head}{{{}}}", parts.join(","))
        }
        IdeaPayload::Positional(values) => {
            let parts = values.iter().enumerate().map(|(index, value)| {
                let is_text = symbol.contract.get(index).is_some_and(|f| f.field_type == "text");
                emit_scalar_positional(value, is_text)
            }).collect::<Vec<_>>();
            format!("{head}|{}", parts.join("|"))
        }
        IdeaPayload::Body(text) => {
            let text = to_nfc(text);
            if text.contains('\n') { format!("{head}{{\n{text}\n}}") } else { format!("{head}{{{text}}}") }
        }
        IdeaPayload::Block(text) => format!("{head}{{\n{text}\n}}"),
        IdeaPayload::MultilinePending => panic!("cannot canonicalize pending multiline idea"),
    }
}

/// Canonicalize without mutating the caller's AST.
pub fn canonicalize(doc: &Document) -> String {
    let mut cloned = doc.clone();
    canonicalize_in_place(&mut cloned)
}

/// Apply C14N-0.1 in place and return UTF-8/LF text with one final LF.
pub fn canonicalize_in_place(doc: &mut Document) -> String {
    normalize_document(doc);
    expand_microtokens(doc);

    let mut lines = vec!["$0".to_string()];
    let format = doc.glossary.format.as_ref().expect("CORTEX canonicalization requires $0:format");
    lines.push(format!("$0:format{}", emit_glossary_attrs(&sort_keys_canonical(&format.attrs, FORMAT_KEY_ORDER))));

    let mut enums = doc.glossary.enums.clone();
    enums.sort_by(|a, b| to_nfc(&a.name).as_bytes().cmp(to_nfc(&b.name).as_bytes()));
    for item in enums {
        let joined = item.values.join("|");
        let attrs = vec![("values".to_string(), Scalar::string(joined.clone(), emit_string_literal(&joined)))];
        lines.push(format!("$0:enum_{}{}", item.name, emit_glossary_attrs(&sort_keys_canonical(&attrs, ENUM_KEY_ORDER))));
    }

    let mut micros = doc.glossary.micros.clone();
    micros.sort_by(|a, b| to_nfc(&a.token).as_bytes().cmp(to_nfc(&b.token).as_bytes()));
    for item in micros {
        let scalar = if atom_matches(&item.expand) { Scalar::atom(item.expand.clone()) } else { Scalar::string(item.expand.clone(), emit_string_literal(&item.expand)) };
        let attrs = vec![("expand".to_string(), scalar)];
        lines.push(format!("$0:micro_{}{}", item.token, emit_glossary_attrs(&sort_keys_canonical(&attrs, MICRO_KEY_ORDER))));
    }

    let mut namespaces = doc.glossary.namespaces.clone();
    namespaces.sort_by(|a, b| to_nfc(&a.alias).as_bytes().cmp(to_nfc(&b.alias).as_bytes()));
    for item in namespaces {
        lines.push(format!("$0:namespace_{}{}", item.alias, emit_glossary_attrs(&sort_keys_canonical(&item.attrs, NS_KEY_ORDER))));
    }

    let mut extensions = doc.glossary.extensions.clone();
    extensions.sort_by(|a, b| to_nfc(&a.name).as_bytes().cmp(to_nfc(&b.name).as_bytes()));
    for item in extensions {
        lines.push(format!("$0:extension_{}{}", item.name, emit_glossary_attrs(&sort_keys_canonical(&item.attrs, EXT_KEY_ORDER))));
    }

    let mut meta = doc.glossary.meta.clone();
    meta.sort_by(|a, b| to_nfc(&a.name).as_bytes().cmp(to_nfc(&b.name).as_bytes()));
    for item in meta {
        let mut attrs = item.attrs.clone();
        attrs.sort_by(|(a, _), (b, _)| to_nfc(a).as_bytes().cmp(to_nfc(b).as_bytes()));
        lines.push(format!("$0:{}{}", item.name, emit_glossary_attrs(&attrs)));
    }

    let mut symbols = doc.glossary.symbols.clone();
    symbols.sort_by(|a, b| {
        let ak = (to_nfc(a.namespace.as_deref().unwrap_or("")), to_nfc(&a.sigil), to_nfc(&a.label));
        let bk = (to_nfc(b.namespace.as_deref().unwrap_or("")), to_nfc(&b.sigil), to_nfc(&b.label));
        ak.cmp(&bk)
    });
    for symbol in &symbols { lines.push(symbol_canonical(symbol)); }

    let symbol_lookup: HashMap<(Option<String>, String), SymbolDef> = doc.glossary.symbols.iter().cloned().map(|s| ((s.namespace.clone(), s.sigil.clone()), s)).collect();
    for section in &doc.sections {
        match &section.title {
            Some(title) => lines.push(format!("${}: {}", section.id, title.trim())),
            None => lines.push(format!("${}", section.id)),
        }
        for idea in &section.ideas {
            let symbol = symbol_lookup.get(&(idea.namespace.clone(), idea.symbol.clone()))
                .or_else(|| symbol_lookup.get(&(None, idea.symbol.clone())))
                .expect("idea symbol must exist in glossary");
            lines.push(idea_canonical(idea, symbol));
        }
    }
    format!("{}\n", lines.join("\n"))
}

#[cfg(test)]
mod tests {
    use crate::parser::parse_cortex;
    use super::*;

    #[test]
    fn canonicalization_is_idempotent() {
        let source = "$0\n$0:format{encoding:UTF-8,cortex:0.1}\nOBJ:Object{desc:\"Object\",focus:topic,fields:\"topic:text|count:integer\",weight:H,type:attrs}\n$1: Main\nOBJ:first{count:2,topic:\"Hello world\"}\n";
        let first = canonicalize(&parse_cortex(source).unwrap());
        let second = canonicalize(&parse_cortex(&first).unwrap());
        assert_eq!(first, second);
    }
}
