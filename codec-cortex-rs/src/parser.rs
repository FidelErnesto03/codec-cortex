use std::collections::HashMap;
use std::sync::OnceLock;

use regex::Regex;

use crate::error::ParseError;
use crate::model::*;
use crate::scalars::{
    classify_raw_cell, parse_attrs_payload, parse_string_scalar, to_nfc,
    StringCursor,
};

fn section_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^\$([0-9]+)(?:\s+(.*))?$").unwrap())
}
fn titled_section_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^\$([1-9][0-9]*):\s+(.*)$").unwrap())
}
fn glossary_idea_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^(?:[a-z][a-z0-9_.-]*::)?(?:!|[A-Z][A-Z0-9_]*):").unwrap())
}
fn symbol_head_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):(.+)$").unwrap())
}
fn idea_head_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):([^\{\|\}\s]+)").unwrap())
}

pub fn parse_contract_fields(s: &str) -> Result<Vec<ContractField>, ParseError> {
    let mut out = Vec::new();
    for raw in s.split('|') {
        let mut part = raw.trim().to_string();
        if part.is_empty() {
            return Err(ParseError::new("G008_INVALID_CONTRACT", format!("Empty contract field in {s:?}")));
        }
        let required = !part.ends_with('?');
        if !required { part.pop(); }
        let (name, field_type) = part.split_once(':').map(|(n, t)| (n.trim(), t.trim())).unwrap_or((part.trim(), "any"));
        out.push(ContractField { name: name.to_string(), field_type: field_type.to_string(), required });
    }
    Ok(out)
}

pub fn parse_cortex(source: &str) -> Result<Document, ParseError> {
    if source.starts_with('\u{FEFF}') {
        return Err(ParseError::at("U001_BOM_FORBIDDEN", "BOM forbidden", 0, 0));
    }
    let normalized = source.replace("\r\n", "\n").replace('\r', "\n");
    let lines: Vec<&str> = normalized.split('\n').collect();

    let mut doc = Document::default();
    let mut in_glossary = false;
    let mut current_section: Option<usize> = None;
    let mut body_idea: Option<Idea> = None;
    let mut body_lines: Vec<String> = Vec::new();

    let mut i = 0usize;
    while i < lines.len() {
        let raw = lines[i];
        let line_no = i + 1;

        if let Some(mut idea) = body_idea.take() {
            if raw.trim() == "}" {
                let text = body_lines.join("\n");
                idea.payload = if idea.shape == "cuerpo" { IdeaPayload::Body(text) } else { IdeaPayload::Block(text) };
                let idx = current_section.ok_or_else(|| ParseError::at("S999_INTERNAL_PARSE_FAILURE", "Multiline body without section", line_no, 0))?;
                doc.sections[idx].ideas.push(idea);
                body_lines.clear();
                i += 1;
                continue;
            }
            body_lines.push(raw.to_string());
            body_idea = Some(idea);
            i += 1;
            continue;
        }

        let stripped = raw.trim();
        if stripped.is_empty() || stripped.starts_with('#') { i += 1; continue; }

        if let Some(caps) = section_re().captures(stripped) {
            if !stripped.starts_with("$0:") {
                let sid: u64 = caps[1].parse().unwrap();
                if sid == 0 {
                    if in_glossary { return Err(ParseError::at("G002_GLOSSARY_REOPENED", "$0 reopened", line_no, 0)); }
                    in_glossary = true;
                    current_section = None;
                } else {
                    let title = caps.get(2).map(|m| m.as_str().trim().to_string());
                    doc.sections.push(Section { id: sid, title, ideas: Vec::new() });
                    current_section = Some(doc.sections.len() - 1);
                    in_glossary = false;
                }
                i += 1;
                continue;
            }
        }

        if let Some(caps) = titled_section_re().captures(stripped) {
            let sid: u64 = caps[1].parse().unwrap();
            let title = caps[2].trim().to_string();
            doc.sections.push(Section { id: sid, title: Some(title), ideas: Vec::new() });
            current_section = Some(doc.sections.len() - 1);
            in_glossary = false;
            i += 1;
            continue;
        }

        if in_glossary {
            parse_glossary_declaration(stripped, &mut doc, line_no)?;
            i += 1;
            continue;
        }

        let section_idx = current_section.ok_or_else(|| ParseError::at(
            "S005_CONTENT_OUTSIDE_SECTION",
            format!("Content outside section: {stripped:?}"),
            line_no,
            0,
        ))?;
        let section_id = doc.sections[section_idx].id;
        let idea = parse_idea_line(stripped, section_id, &doc, line_no)?;
        if matches!(&idea.payload, IdeaPayload::MultilinePending) {
            body_idea = Some(idea);
            body_lines.clear();
        } else {
            doc.sections[section_idx].ideas.push(idea);
        }
        i += 1;
    }

    if let Some(idea) = body_idea {
        return Err(ParseError::at("I004_SHAPE_DELIMITER_MISMATCH", format!("Unclosed multiline {}", idea.shape), idea.source_line, 0));
    }
    Ok(doc)
}

fn is_glossary_decl_line(s: &str) -> bool { glossary_idea_re().is_match(s) }

fn parse_glossary_declaration(line: &str, doc: &mut Document, line_no: usize) -> Result<(), ParseError> {
    if !line.starts_with("$0:") && !is_glossary_decl_line(line) {
        return Err(ParseError::at(
            "G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS",
            format!("Glossary declaration must use attrs: {line:?}"),
            line_no,
            0,
        ));
    }
    let brace_idx = line.find('{').ok_or_else(|| ParseError::at(
        "G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS",
        format!("Glossary declaration must use attrs: {line:?}"),
        line_no,
        0,
    ))?;
    let head = line[..brace_idx].trim();
    let attrs = parse_attrs_payload(&line[brace_idx..], line_no)?;
    if let Some(name) = head.strip_prefix("$0:") {
        add_meta_declaration(name, attrs, doc, line_no)
    } else {
        let caps = symbol_head_re().captures(head).ok_or_else(|| ParseError::at(
            "L001_INVALID_SYMBOL", format!("Invalid sigil declaration head: {head:?}"), line_no, 0))?;
        let ns = caps.get(1).map(|m| m.as_str().to_string());
        let sigil = caps[2].to_string();
        let label = caps[3].to_string();
        let symbol = build_symbol_def(ns, sigil, label, attrs, line_no)?;
        doc.glossary.symbols.push(symbol);
        Ok(())
    }
}

fn attrs_map(attrs: &Attrs) -> HashMap<&str, &Scalar> {
    attrs.iter().map(|(k, v)| (k.as_str(), v)).collect()
}

fn add_meta_declaration(name: &str, attrs: Attrs, doc: &mut Document, line_no: usize) -> Result<(), ParseError> {
    if name == "format" {
        if doc.glossary.format.is_some() { return Err(ParseError::at("G006_DUPLICATE_FORMAT", "Duplicate $0:format", line_no, 0)); }
        let map = attrs_map(&attrs);
        let cortex = map.get("cortex").and_then(|v| v.text_value()).unwrap_or("0.1").to_string();
        let encoding = map.get("encoding").and_then(|v| v.text_value()).unwrap_or("UTF-8").to_string();
        if cortex != "0.1" { return Err(ParseError::at("G007_UNSUPPORTED_VERSION", format!("Unsupported cortex version: {cortex}"), line_no, 0)); }
        if encoding != "UTF-8" { return Err(ParseError::at("G011_ENCODING_REQUIRED", format!("Encoding must be UTF-8: {encoding}"), line_no, 0)); }
        doc.cortex_version = cortex.clone();
        doc.encoding = encoding.clone();
        doc.glossary.format = Some(FormatDecl { cortex, encoding, attrs, source_line: line_no });
        return Ok(());
    }
    if let Some(enum_name) = name.strip_prefix("enum_") {
        let map = attrs_map(&attrs);
        let values = map.get("values").ok_or_else(|| ParseError::at("G014_INVALID_ENUM", format!("enum {enum_name} missing values string"), line_no, 0))?;
        let ScalarValue::String(value) = &values.value else {
            return Err(ParseError::at("G014_INVALID_ENUM", format!("enum {enum_name} missing values string"), line_no, 0));
        };
        doc.glossary.enums.push(EnumDecl { name: enum_name.to_string(), values: value.split('|').map(str::to_string).collect(), source_line: line_no });
        return Ok(());
    }
    if let Some(token) = name.strip_prefix("micro_") {
        let map = attrs_map(&attrs);
        let expand = map.get("expand").ok_or_else(|| ParseError::at("G012_INVALID_MICRO", format!("micro {token} missing expand"), line_no, 0))?;
        let expand = expand.text_value().unwrap_or(&expand.lexeme).to_string();
        doc.glossary.micros.push(MicroDecl { token: token.to_string(), expand, source_line: line_no });
        return Ok(());
    }
    if let Some(alias) = name.strip_prefix("namespace_") {
        doc.glossary.namespaces.push(NamespaceDecl { alias: alias.to_string(), attrs, source_line: line_no });
        return Ok(());
    }
    if let Some(ext_name) = name.strip_prefix("extension_") {
        doc.glossary.extensions.push(ExtensionDecl { name: ext_name.to_string(), attrs, source_line: line_no });
        return Ok(());
    }
    doc.glossary.meta.push(MetaDecl { name: name.to_string(), attrs, source_line: line_no });
    Ok(())
}

pub(crate) fn build_symbol_def(
    namespace: Option<String>,
    sigil: String,
    label: String,
    attrs: Attrs,
    line_no: usize,
) -> Result<SymbolDef, ParseError> {
    let map = attrs_map(&attrs);
    let shape = map.get("type").and_then(|v| v.text_value()).ok_or_else(|| ParseError::at("G016_SYMBOL_TYPE_REQUIRED", format!("sigil {sigil} missing type"), line_no, 0))?.to_string();
    if !matches!(shape.as_str(), "attrs" | "attrs-pos" | "cuerpo" | "bloque" | "relacion") {
        return Err(ParseError::at("G017_UNKNOWN_SHAPE", format!("Unknown shape: {shape}"), line_no, 0));
    }
    let weight = map.get("weight").and_then(|v| v.text_value()).ok_or_else(|| ParseError::at("G018_SYMBOL_WEIGHT_REQUIRED", format!("sigil {sigil} missing weight"), line_no, 0))?.to_string();
    if !matches!(weight.as_str(), "B" | "M" | "H") { return Err(ParseError::at("G019_INVALID_WEIGHT", format!("Invalid weight: {weight}"), line_no, 0)); }
    let desc_scalar = map.get("desc").ok_or_else(|| ParseError::at("G020_SYMBOL_DESCRIPTION_REQUIRED", format!("sigil {sigil} missing desc"), line_no, 0))?;
    let desc = desc_scalar.text_value().unwrap_or(&desc_scalar.lexeme).to_string();
    let open = map.get("open").is_some_and(|v| v.is_true());

    let mut contract = Vec::new();
    if shape == "attrs" {
        let fields = map.get("fields").and_then(|v| v.text_value()).ok_or_else(|| ParseError::at("G021_ATTRS_CONTRACT_REQUIRED", format!("sigil {sigil} missing fields"), line_no, 0))?;
        contract = parse_contract_fields(fields)?;
    } else if shape == "attrs-pos" || shape == "relacion" {
        let pos = map.get("pos").and_then(|v| v.text_value()).ok_or_else(|| ParseError::at("G022_POSITIONAL_CONTRACT_REQUIRED", format!("sigil {sigil} missing pos"), line_no, 0))?;
        contract = parse_contract_fields(pos)?;
        if shape == "relacion" && contract.len() < 3 { return Err(ParseError::at("G023_RELATION_CONTRACT_TOO_SHORT", "relacion needs >=3 fields", line_no, 0)); }
    }

    let focus = if let Some(value) = map.get("focus") {
        value.text_value().unwrap_or(&value.lexeme).to_string()
    } else if shape == "cuerpo" || shape == "bloque" {
        "$body".to_string()
    } else {
        return Err(ParseError::at("G024_FOCUS_REQUIRED", format!("sigil {sigil} missing focus"), line_no, 0));
    };
    if matches!(shape.as_str(), "attrs" | "attrs-pos" | "relacion") && !contract.iter().any(|f| f.name == focus) {
        return Err(ParseError::at("G025_UNKNOWN_FOCUS_FIELD", format!("focus {focus:?} not in contract"), line_no, 0));
    }
    Ok(SymbolDef { namespace, sigil, label, shape, weight, focus, desc, open, contract, attrs, source_line: line_no })
}

fn parse_idea_line(line: &str, section_id: u64, doc: &Document, line_no: usize) -> Result<Idea, ParseError> {
    let caps = idea_head_re().captures(line).ok_or_else(|| ParseError::at("S003_INVALID_IDEA_HEAD", format!("Invalid idea head: {line:?}"), line_no, 0))?;
    let namespace = caps.get(1).map(|m| m.as_str().to_string());
    let symbol = caps[2].to_string();
    let name = caps[3].to_string();
    let matched = caps.get(0).unwrap();
    let rest = &line[matched.end()..];
    let sym = doc.glossary.symbols.iter().find(|s| s.sigil == symbol && s.namespace == namespace)
        .ok_or_else(|| ParseError::at("I001_UNDECLARED_SYMBOL", format!("Undeclared sigil: {symbol}"), line_no, 0))?;
    let shape = sym.shape.clone();

    let payload = match shape.as_str() {
        "attrs" | "cuerpo" | "bloque" => {
            if !rest.starts_with('{') { return Err(ParseError::at("I004_SHAPE_DELIMITER_MISMATCH", format!("Expected {{ for shape {shape}"), line_no, 0)); }
            if rest.ends_with('}') {
                if shape == "attrs" { IdeaPayload::Attrs(parse_attrs_payload(rest, line_no)?) }
                else {
                    let inner = &rest[1..rest.len()-1];
                    if shape == "cuerpo" { IdeaPayload::Body(to_nfc(inner)) } else { IdeaPayload::Block(inner.to_string()) }
                }
            } else {
                if rest.trim() != "{" { return Err(ParseError::at("I004_SHAPE_DELIMITER_MISMATCH", format!("Expected single {{ for multiline {shape}"), line_no, 0)); }
                IdeaPayload::MultilinePending
            }
        }
        "attrs-pos" | "relacion" => {
            let Some(rest) = rest.strip_prefix('|') else { return Err(ParseError::at("I004_SHAPE_DELIMITER_MISMATCH", format!("Expected | for shape {shape}"), line_no, 0)); };
            IdeaPayload::Positional(parse_pipe_cells(rest, line_no)?)
        }
        _ => return Err(ParseError::at("S999_INTERNAL_PARSE_FAILURE", format!("Cannot parse idea: {line:?}"), line_no, 0)),
    };
    Ok(Idea { section: section_id, namespace, symbol, name, shape, payload, source_line: line_no })
}

fn parse_pipe_cells(s: &str, line_no: usize) -> Result<Vec<Scalar>, ParseError> {
    let chars: Vec<char> = s.chars().collect();
    let mut cells = Vec::new();
    let mut i = 0usize;
    while i <= chars.len() {
        if i < chars.len() && chars[i] == '"' {
            let remainder: String = chars[i..].iter().collect();
            let mut cur = StringCursor::new(&remainder, line_no, 1);
            let scalar = parse_string_scalar(&mut cur)?;
            cells.push(scalar);
            i += cur.i;
            while i < chars.len() && matches!(chars[i], ' ' | '\t') { i += 1; }
            if i >= chars.len() { return Ok(cells); }
            if chars[i] != '|' { return Err(ParseError::at("S006_INVALID_ATTRS", "Expected | after quoted cell", line_no, i)); }
            i += 1;
        } else {
            let mut j = i;
            while j < chars.len() && chars[j] != '|' { j += 1; }
            let raw: String = chars[i..j].iter().collect::<String>().trim().to_string();
            if raw.is_empty() && j >= chars.len() { return Ok(cells); }
            cells.push(classify_raw_cell(&raw));
            i = j;
            if i < chars.len() && chars[i] == '|' { i += 1; } else { return Ok(cells); }
        }
    }
    Ok(cells)
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = r#"$0
$0:format{cortex:0.1,encoding:UTF-8}
OBJ:Object{type:attrs,weight:H,fields:"topic:text|count:integer",focus:topic,desc:"Object"}
$1: Main
OBJ:first{count:2,topic:"Hello world"}
"#;

    #[test]
    fn parses_document() {
        let doc = parse_cortex(SAMPLE).unwrap();
        assert_eq!(doc.sections.len(), 1);
        assert_eq!(doc.sections[0].ideas[0].address(), "$1:OBJ:first");
    }

    #[test]
    fn rejects_undeclared_symbol() {
        let source = "$0\n$0:format{cortex:0.1,encoding:UTF-8}\n$1\nBAD:x{a:b}\n";
        assert_eq!(parse_cortex(source).unwrap_err().code, "I001_UNDECLARED_SYMBOL");
    }
}
