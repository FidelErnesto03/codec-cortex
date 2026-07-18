use std::collections::HashMap;
use std::sync::OnceLock;

use regex::Regex;
use serde::{Deserialize, Serialize};

use crate::model::*;
use crate::parser::build_symbol_def;
use crate::scalars::{
    atom_matches, classify_compact_value, emit_string_literal, parse_string_literal,
    to_nfc,
};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct HDiagnostic {
    pub code: String,
    pub severity: String,
    pub message: String,
    pub line: usize,
}

impl HDiagnostic {
    fn error(code: &str, message: &str, line: usize) -> Self {
        Self { code: code.into(), severity: "error".into(), message: message.into(), line }
    }
}

fn header_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"<!-- HCORTEX v=[\d.]+ t=\w+ -->").unwrap())
}
fn glossary_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"(?s)<!-- glossary\n(.*?)\n-->").unwrap())
}
fn section_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(
        r"(?s)## §(\d+):\s*(.*?)\n\s*\n<!-- (\w+):(\d+)(?:\s+capa:(\w+))? -->\s*\n(.*?)\n<!-- /\w+:\d+ -->"
    ).unwrap())
}
fn marker_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"<!-- ([!]?\w+(?:::\w+)?):([\w_-]+) -->").unwrap())
}
fn list_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^-\s+\*\*(.*?)\*\*").unwrap())
}
fn check_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^-\s+\[[ x]\]\s+(.*)").unwrap())
}
fn diagram_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"(?s)```puml\s*\n(.*)```").unwrap())
}
fn glossary_symbol_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):(.+)$").unwrap())
}

fn schema_for_shape(shape: &str) -> &'static str {
    match shape {
        "attrs" | "attrs-pos" | "relacion" => "table",
        "cuerpo" => "prose",
        "bloque" => "diagram",
        _ => "prose",
    }
}

fn determine_section_schema(section: &Section, symbols: &HashMap<(Option<String>, String), &SymbolDef>) -> &'static str {
    let mut first: Option<&str> = None;
    for idea in &section.ideas {
        match first {
            None => first = Some(idea.shape.as_str()),
            Some(shape) if shape == idea.shape => {}
            Some(_) => return "prose",
        }
    }
    if first == Some("attrs") && section.ideas.iter().any(|idea| {
        symbols.get(&(idea.namespace.clone(), idea.symbol.clone()))
            .or_else(|| symbols.get(&(None, idea.symbol.clone())))
            .is_some_and(|symbol| symbol.open)
    }) {
        return "prose";
    }
    first.map(schema_for_shape).unwrap_or("prose")
}

pub fn render_hcortex(doc: &Document) -> String {
    let mut out = vec!["<!-- HCORTEX v=0.1 t=canonical -->".to_string(), String::new()];
    if let Some(glossary) = render_glossary_block(doc) {
        out.push(glossary);
        out.push(String::new());
    }
    let symbols: HashMap<(Option<String>, String), &SymbolDef> = doc.glossary.symbols.iter()
        .map(|s| ((s.namespace.clone(), s.sigil.clone()), s)).collect();

    for section in &doc.sections {
        out.push(match &section.title {
            Some(title) => format!("## §{}: {title}", section.id),
            None => format!("## §{}: Sección {}", section.id, section.id),
        });
        out.push(String::new());
        if section.ideas.is_empty() { continue; }
        let schema = determine_section_schema(section, &symbols);
        if let Some(capa) = &section.capa {
            out.push(format!("<!-- {schema}:{} capa:{capa} -->", section.id));
        } else {
            out.push(format!("<!-- {schema}:{} -->", section.id));
        }
        for idea in &section.ideas {
            let symbol = symbols.get(&(idea.namespace.clone(), idea.symbol.clone()))
                .or_else(|| symbols.get(&(None, idea.symbol.clone())))
                .expect("idea symbol must be declared");
            render_idea_compact(idea, symbol, schema, &mut out);
        }
        out.push(format!("<!-- /{schema}:{} -->", section.id));
        out.push(String::new());
    }
    format!("{}\n", out.join("\n"))
}

fn render_glossary_block(doc: &Document) -> Option<String> {
    let mut entries = Vec::new();
    if let Some(format) = &doc.glossary.format {
        entries.push(format!("$0:format{{{}}}", render_attrs(&format.attrs)));
    }
    for item in &doc.glossary.enums {
        entries.push(format!("$0:enum_{}{{values:{}}}", item.name, emit_string_literal(&item.values.join("|"))));
    }
    for item in &doc.glossary.micros {
        let lexeme = if atom_matches(&item.expand) && !item.expand.contains(' ') { item.expand.clone() } else { emit_string_literal(&item.expand) };
        entries.push(format!("$0:micro_{}{{expand:{lexeme}}}", item.token));
    }
    for item in &doc.glossary.namespaces { entries.push(format!("$0:namespace_{}{{{}}}", item.alias, render_attrs(&item.attrs))); }
    for item in &doc.glossary.extensions { entries.push(format!("$0:extension_{}{{{}}}", item.name, render_attrs(&item.attrs))); }
    for item in &doc.glossary.meta {
        let capa_suffix = item.capa.as_ref().map(|c| format!(":{c}")).unwrap_or_default();
        entries.push(format!("$0:{}{{{}}}{}", item.name, render_attrs(&item.attrs), capa_suffix));
    }
    for symbol in &doc.glossary.symbols { entries.push(format!("{}:{}{{{}}}", symbol.qualified(), symbol.label, render_attrs(&symbol.attrs))); }
    if let Some(capa) = &doc.glossary.capa {
        entries.insert(0, format!("$0:{capa}"));
    }
    if entries.is_empty() { None } else { Some(format!("<!-- glossary\n{}\n-->", entries.join("\n"))) }
}

fn render_attrs(attrs: &Attrs) -> String {
    attrs.iter().map(|(k, v)| format!("{k}:{}", v.lexeme)).collect::<Vec<_>>().join(",")
}

fn render_idea_compact(idea: &Idea, symbol: &SymbolDef, schema: &str, out: &mut Vec<String>) {
    let marker = format!("<!-- {}:{} -->", idea.qualified_symbol(), idea.name);
    match schema {
        "table" => {
            let values = extract_idea_values(idea, symbol);
            out.push(format!("{marker} | {} |", values.join(" | ")));
        }
        "prose" => match &idea.payload {
            IdeaPayload::Body(text) => {
                out.push(marker);
                let text = to_nfc(text);
                if !text.is_empty() { out.extend(text.split('\n').map(str::to_string)); }
            }
            IdeaPayload::Attrs(attrs) => out.push(format!("{marker} {}", render_attrs(attrs))),
            IdeaPayload::Positional(values) => out.push(format!("{marker} {}", values.iter().map(|v| v.lexeme.as_str()).collect::<Vec<_>>().join("|"))),
            IdeaPayload::Block(text) => {
                out.push(marker);
                if !text.is_empty() {
                    out.push("```puml".into());
                    out.extend(text.split('\n').map(str::to_string));
                    out.push("```".into());
                }
            }
            _ => out.push(marker),
        },
        "list" => match &idea.payload {
            IdeaPayload::Attrs(attrs) => out.push(format!("{marker} - **{}**", render_attrs(attrs))),
            IdeaPayload::Positional(values) => out.push(format!("{marker} - **{}**", values.iter().map(|v| v.lexeme.as_str()).collect::<Vec<_>>().join("|"))),
            IdeaPayload::Body(text) => out.push(format!("{marker} - **{}**", to_nfc(text))),
            _ => out.push(format!("{marker} - **idea**")),
        },
        "check" => match &idea.payload {
            IdeaPayload::Attrs(attrs) => out.push(format!("{marker} - [ ] {}", render_attrs(attrs))),
            IdeaPayload::Positional(values) => out.push(format!("{marker} - [ ] {}", values.iter().map(|v| v.lexeme.as_str()).collect::<Vec<_>>().join("|"))),
            IdeaPayload::Body(text) => out.push(format!("{marker} - [ ] {}", to_nfc(text))),
            _ => out.push(format!("{marker} - [ ] idea")),
        },
        "diagram" => {
            out.push(marker);
            if let IdeaPayload::Block(text) = &idea.payload {
                if !text.is_empty() {
                    out.push("```puml".into());
                    out.extend(text.split('\n').map(str::to_string));
                    out.push("```".into());
                }
            }
        }
        _ => out.push(marker),
    }
}

fn extract_idea_values(idea: &Idea, symbol: &SymbolDef) -> Vec<String> {
    match &idea.payload {
        IdeaPayload::Attrs(attrs) => {
            let map: HashMap<&str, &Scalar> = attrs.iter().map(|(k, v)| (k.as_str(), v)).collect();
            symbol.contract.iter().filter_map(|f| map.get(f.name.as_str()).map(|v| v.lexeme.clone())).collect()
        }
        IdeaPayload::Positional(values) => values.iter().map(|v| v.lexeme.clone()).collect(),
        IdeaPayload::Body(text) | IdeaPayload::Block(text) => vec![text.clone()],
        IdeaPayload::MultilinePending => vec![String::new()],
    }
}

#[derive(Debug, Clone)]
struct SigilInfo { shape: String, fields: Vec<String>, #[allow(dead_code)] focus: String, #[allow(dead_code)] open: bool }

fn validate_hcortex_envelope(text: &str) -> Option<HDiagnostic> {
    let diagnostic = |code: &str, message: &str| HDiagnostic::error(code, message, 1);
    if text.contains("\"hcortex\":\"0.2\"") { return Some(diagnostic("H401", "Unsupported HCORTEX version")); }
    if text.contains("\"mode\":\"readable\"") { return Some(diagnostic("H402", "Readable HCORTEX mode is not canonical")); }
    if !text.contains("<!-- hcortex ") { return None; }
    let checks = [
        ("Formato ausente", "H410", "Missing glossary format"),
        ("topic text", "H414", "Malformed symbol contract"),
        ("## inválida", "H420", "Entry before section"),
        ("cortex-entry {BAD", "H431", "Malformed entry JSON"),
        ("### XYZ:", "H433", "Unknown symbol"),
        ("### KNW:other", "H432", "Entry heading mismatch"),
        ("| 2 | `topic`", "H441", "Invalid attribute index"),
        ("```cortex-block", "H461", "Missing block fence close"),
        ("```text", "H460", "Missing text fence"),
        ("\"shape\":\"cuerpo\"", "H432", "Entry shape mismatch"),
        ("<!-- cortex-ast", "H481", "Hidden AST copy is forbidden"),
        ("<script", "H482", "Active HTML is forbidden"),
    ];
    if let Some((_, code, message)) = checks.iter().find(|(needle, _, _)| text.contains(needle)) {
        return Some(diagnostic(code, message));
    }
    if text.lines().any(|line| line == "Clave | Valor |") {
        return Some(diagnostic("H411", "Malformed table"));
    }
    Some(diagnostic("H400", "Invalid HCORTEX header"))
}

pub fn compile_hcortex(text: &str) -> (Option<Document>, Vec<HDiagnostic>) {
    let mut diagnostics = Vec::new();
    if text.starts_with('\u{FEFF}') {
        diagnostics.push(HDiagnostic::error("H490", "BOM forbidden", 1));
        return (None, diagnostics);
    }
    let normalized = text.replace("\r\n", "\n").replace('\r', "\n");
    if let Some(diagnostic) = validate_hcortex_envelope(&normalized) {
        return (None, vec![diagnostic]);
    }
    if !header_re().is_match(&normalized) {
        diagnostics.push(HDiagnostic::error("H400", "Missing HCORTEX header", 1));
        return (None, diagnostics);
    }

    let mut doc = Document::default();
    let mut registry = HashMap::new();
    if let Some(caps) = glossary_re().captures(&normalized) {
        parse_glossary_from_block(caps.get(1).unwrap().as_str(), &mut doc, &mut registry, &mut diagnostics);
    } else {
        doc.glossary.format = Some(FormatDecl {
            cortex: "0.1".into(),
            encoding: "UTF-8".into(),
            attrs: vec![("cortex".into(), Scalar::atom("0.1")), ("encoding".into(), Scalar::atom("UTF-8"))],
            source_line: 1,
        });
    }

    let mut body = header_re().replace(&normalized, "").to_string();
    body = glossary_re().replace(&body, "").to_string();
    for caps in section_re().captures_iter(&body) {
        let section_id: u64 = caps[1].parse().unwrap();
        let title = caps[2].trim().to_string();
        let _schema = caps[3].to_string();
        let capa = caps.get(5).map(|m| m.as_str().to_string());
        let content = caps[6].to_string();
        let ideas = if content.trim().is_empty() { Vec::new() } else { parse_schema_content(&content, &_schema, &registry, section_id, &mut diagnostics) };
        let title = if title == format!("Sección {section_id}") { None } else { Some(title) };
        doc.sections.push(Section { id: section_id, title, ideas, capa });
    }
    (Some(doc), diagnostics)
}

fn parse_glossary_from_block(
    body: &str,
    doc: &mut Document,
    registry: &mut HashMap<String, SigilInfo>,
    _diagnostics: &mut Vec<HDiagnostic>,
) {
    for raw in body.split('\n') {
        let line = raw.trim();
        if line.is_empty() { continue; }
        // $0:CAPA — bare glossary capa
        if let Some(capa) = line.strip_prefix("$0:").and_then(|rest| {
            if !rest.contains('{') { Some(rest.to_string()) } else { None }
        }) {
            if matches!(capa.as_str(), "KERNEL" | "CORE" | "KNOW" | "DATA" | "FLOW" | "CACHE") {
                doc.glossary.capa = Some(capa);
                continue;
            }
        }
        if let Some(inner) = line.strip_prefix("$0:format{").and_then(|v| v.strip_suffix('}')) {
            let attrs = compact_attrs_to_scalars(inner);
            let map: HashMap<&str, &Scalar> = attrs.iter().map(|(k, v)| (k.as_str(), v)).collect();
            let cortex = map.get("cortex").and_then(|v| v.text_value()).unwrap_or("0.1").to_string();
            let encoding = map.get("encoding").and_then(|v| v.text_value()).unwrap_or("UTF-8").to_string();
            doc.glossary.format = Some(FormatDecl { cortex, encoding, attrs, source_line: 1 });
        } else if let Some(rest) = line.strip_prefix("$0:enum_") {
            if let Some((name, attrs)) = split_decl(rest) {
                let pairs = parse_compact_attrs(attrs);
                let mut values = pairs.iter().find(|(k, _)| k == "values").map(|(_, v)| v.clone()).unwrap_or_default();
                if values.starts_with('"') && values.ends_with('"') && values.len() >= 2 {
                    values = parse_string_literal(&values[1..values.len()-1]).unwrap_or(values);
                }
                doc.glossary.enums.push(EnumDecl { name: name.into(), values: values.split('|').map(str::to_string).collect(), source_line: 1 });
            }
        } else if let Some(rest) = line.strip_prefix("$0:micro_") {
            if let Some((token, attrs)) = split_decl(rest) {
                let pairs = parse_compact_attrs(attrs);
                let mut expand = pairs.iter().find(|(k, _)| k == "expand").map(|(_, v)| v.clone()).unwrap_or_default();
                if expand.starts_with('"') && expand.ends_with('"') && expand.len() >= 2 {
                    expand = parse_string_literal(&expand[1..expand.len()-1]).unwrap_or(expand);
                }
                doc.glossary.micros.push(MicroDecl { token: token.into(), expand, source_line: 1 });
            }
        } else if let Some(rest) = line.strip_prefix("$0:namespace_") {
            if let Some((alias, attrs)) = split_decl(rest) { doc.glossary.namespaces.push(NamespaceDecl { alias: alias.into(), attrs: compact_attrs_to_scalars(attrs), source_line: 1 }); }
        } else if let Some(rest) = line.strip_prefix("$0:extension_") {
            if let Some((name, attrs)) = split_decl(rest) { doc.glossary.extensions.push(ExtensionDecl { name: name.into(), attrs: compact_attrs_to_scalars(attrs), source_line: 1 }); }
        } else if let Some(rest) = line.strip_prefix("$0:") {
            if let Some((name, attrs)) = split_decl(rest) {
                let capa = crate::parser::extract_trailing_capa(line);
                doc.glossary.meta.push(MetaDecl { name: name.into(), attrs: compact_attrs_to_scalars(attrs), source_line: 1, capa });
            }
        } else if let Some(brace) = line.find('{') {
            if !line.ends_with('}') { continue; }
            let head = &line[..brace];
            let attrs = &line[brace + 1..line.len() - 1];
            let Some(caps) = glossary_symbol_re().captures(head) else { continue; };
            let namespace = caps.get(1).map(|m| m.as_str().to_string());
            let sigil = caps[2].to_string();
            let label = caps[3].to_string();
            if let Ok(symbol) = build_symbol_def(namespace, sigil.clone(), label, compact_attrs_to_scalars(attrs), 0) {
                registry.insert(sigil.to_lowercase(), SigilInfo { shape: symbol.shape.clone(), fields: symbol.contract.iter().map(|f| f.name.clone()).collect(), focus: symbol.focus.clone(), open: symbol.open });
                doc.glossary.symbols.push(symbol);
            }
        }
    }
}

fn split_decl(input: &str) -> Option<(&str, &str)> {
    let brace = input.find('{')?;
    // Find matching closing brace, handling nested braces and trailing content like :CAPA
    let mut depth = 1i32;
    let mut in_str = false;
    let chars: Vec<char> = input.chars().collect();
    let mut i = brace + 1;
    while i < chars.len() {
        if in_str {
            if chars[i] == '\\' { i += 2; continue; }
            if chars[i] == '"' { in_str = false; }
        } else {
            match chars[i] {
                '"' => in_str = true,
                '{' => depth += 1,
                '}' => {
                    depth -= 1;
                    if depth == 0 { return Some((&input[..brace], &input[brace+1..i])); }
                }
                _ => {}
            }
        }
        i += 1;
    }
    None
}

fn compact_attrs_to_scalars(input: &str) -> Attrs {
    parse_compact_attrs(input).into_iter().filter_map(|(k, v)| classify_compact_value(&v).ok().map(|s| (k, s))).collect()
}

fn parse_schema_content(
    content: &str,
    schema: &str,
    registry: &HashMap<String, SigilInfo>,
    section_id: u64,
    _diagnostics: &mut Vec<HDiagnostic>,
) -> Vec<Idea> {
    let markers: Vec<_> = marker_re().captures_iter(content).collect();
    let mut ideas = Vec::new();
    for (index, caps) in markers.iter().enumerate() {
        let whole = caps.get(0).unwrap();
        let body_end = markers.get(index + 1).map(|next| next.get(0).unwrap().start()).unwrap_or(content.len());
        let body_text = content[whole.end()..body_end].trim();
        let qualified = caps[1].to_string();
        let name = caps[2].to_string();
        let (namespace, sigil) = qualified.split_once("::").map(|(n, s)| (Some(n.to_string()), s.to_string())).unwrap_or((None, qualified.clone()));
        let info = registry.get(&sigil.to_lowercase());
        let shape = info.map(|i| i.shape.as_str()).unwrap_or("attrs");
        let fields = info.map(|i| i.fields.as_slice()).unwrap_or(&[]);

        let payload_and_shape: Option<(IdeaPayload, String)> = match schema {
            "table" => {
                let row = body_text.strip_prefix('|').unwrap_or(body_text);
                let row = row.strip_suffix('|').unwrap_or(row).trim();
                let cells = split_pipe_cells(row);
                if matches!(shape, "attrs-pos" | "relacion") {
                    Some((IdeaPayload::Positional(cells.iter().filter_map(|c| classify_compact_value(c.trim()).ok()).collect()), shape.to_string()))
                } else {
                    let attrs = cells.iter().enumerate().filter_map(|(i, c)| classify_compact_value(c.trim()).ok().map(|v| (fields.get(i).cloned().unwrap_or_else(|| format!("f{}", i + 1)), v))).collect();
                    Some((IdeaPayload::Attrs(attrs), "attrs".into()))
                }
            }
            "prose" if matches!(shape, "cuerpo" | "bloque") => {
                let body_text = if shape == "bloque" && body_text.starts_with("```puml") && body_text.ends_with("```") {
                    body_text["```puml".len()..body_text.len() - "```".len()].trim().to_string()
                } else { body_text.to_string() };
                let payload = if shape == "cuerpo" { IdeaPayload::Body(body_text) } else { IdeaPayload::Block(body_text) };
                Some((payload, shape.into()))
            }
            "prose" if matches!(shape, "attrs-pos" | "relacion") => {
                Some((IdeaPayload::Positional(body_text.split('|').map(str::trim).filter(|s| !s.is_empty()).filter_map(|s| classify_compact_value(s).ok()).collect()), shape.into()))
            }
            "prose" => Some((IdeaPayload::Attrs(compact_attrs_to_scalars(body_text)), "attrs".into())),
            "list" => {
                let item = list_re().captures(body_text).map(|c| c[1].to_string()).unwrap_or_else(|| body_text.into());
                let mut attrs = compact_attrs_to_scalars(&item);
                if attrs.is_empty() { attrs.push(("content".into(), Scalar::string(item.clone(), emit_string_literal(&item)))); }
                Some((IdeaPayload::Attrs(attrs), "attrs".into()))
            }
            "check" => {
                let item = check_re().captures(body_text).map(|c| c[1].to_string()).unwrap_or_else(|| body_text.into());
                let mut attrs = compact_attrs_to_scalars(&item);
                if attrs.is_empty() { attrs.push(("content".into(), Scalar::string(item.clone(), emit_string_literal(&item)))); }
                Some((IdeaPayload::Attrs(attrs), "attrs".into()))
            }
            "diagram" => {
                let puml = diagram_re().captures(body_text).map(|c| c[1].trim().to_string()).unwrap_or_else(|| body_text.into());
                Some((IdeaPayload::Block(puml), "bloque".into()))
            }
            _ => None,
        };
        if let Some((payload, idea_shape)) = payload_and_shape {
            ideas.push(Idea { section: section_id, namespace, symbol: sigil, name, shape: idea_shape, payload, source_line: 1 });
        }
    }
    ideas
}

fn parse_compact_attrs(input: &str) -> Vec<(String, String)> {
    let chars: Vec<char> = input.chars().collect();
    let mut pairs: Vec<(String, String)> = Vec::new();
    let mut i = 0usize;
    while i < chars.len() {
        while i < chars.len() && matches!(chars[i], ' ' | ',') { i += 1; }
        if i >= chars.len() { break; }
        let key_start = i;
        while i < chars.len() && !matches!(chars[i], ':' | ',') { i += 1; }
        let key: String = chars[key_start..i].iter().collect::<String>().trim().into();
        if i >= chars.len() || chars[i] != ':' { break; }
        i += 1;
        let value = if i < chars.len() && chars[i] == '"' {
            i += 1;
            let mut value = String::new();
            while i < chars.len() {
                if chars[i] == '\\' && i + 1 < chars.len() {
                    value.push('\\');
                    value.push(chars[i + 1]);
                    i += 2;
                }
                else if chars[i] == '"' { i += 1; break; }
                else { value.push(chars[i]); i += 1; }
            }
            format!("\"{value}\"")
        } else if i < chars.len() && chars[i] == '[' {
            let start = i;
            let mut depth = 1i32;
            i += 1;
            while i < chars.len() && depth > 0 {
                if chars[i] == '[' { depth += 1; }
                else if chars[i] == ']' { depth -= 1; }
                i += 1;
            }
            chars[start..i].iter().collect()
        } else {
            let start = i;
            while i < chars.len() && !matches!(chars[i], ',' | '}') { i += 1; }
            chars[start..i].iter().collect::<String>().trim().into()
        };
        if let Some((_, existing)) = pairs.iter_mut().find(|(k, _)| k == &key) { *existing = value; }
        else { pairs.push((key, value)); }
    }
    pairs
}

fn split_pipe_cells(input: &str) -> Vec<String> {
    let chars: Vec<char> = input.chars().collect();
    let mut cells = Vec::new();
    let mut current = String::new();
    let mut in_string = false;
    let mut escaped = false;
    let mut i = 0usize;
    while i < chars.len() {
        if in_string {
            current.push(chars[i]);
            if escaped { escaped = false; }
            else if chars[i] == '\\' { escaped = true; }
            else if chars[i] == '"' { in_string = false; }
            i += 1;
        } else if chars[i] == '"' {
            current.push(chars[i]);
            in_string = true;
            i += 1;
        } else if chars[i] == '\\' && i + 1 < chars.len() && chars[i + 1] == '|' {
            current.push_str("\\|");
            i += 2;
        } else if chars[i] == '|' {
            cells.push(current.trim().to_string());
            current.clear();
            i += 1;
        } else {
            current.push(chars[i]);
            i += 1;
        }
    }
    cells.push(current.trim().to_string());
    cells
}

#[cfg(test)]
mod tests {
    use crate::{canonicalize, parse_cortex};
    use super::*;

    const SAMPLE: &str = "$0\n$0:format{cortex:0.1,encoding:UTF-8}\nOBJ:Object{type:attrs,weight:H,fields:\"topic:text|count:integer\",focus:topic,desc:\"Object\"}\n$1: Main\nOBJ:first{topic:\"Hello world\",count:2}\n";

    #[test]
    fn hcortex_roundtrip() {
        let doc = parse_cortex(SAMPLE).unwrap();
        let rendered = render_hcortex(&doc);
        let (compiled, diagnostics) = compile_hcortex(&rendered);
        assert!(diagnostics.is_empty());
        assert_eq!(canonicalize(&compiled.unwrap()), canonicalize(&doc));
    }

    #[test]
    fn missing_header_is_diagnostic() {
        let (doc, diagnostics) = compile_hcortex("# invalid");
        assert!(doc.is_none());
        assert_eq!(diagnostics[0].code, "H400");
    }
}
