// CORTEX 0.1 Parser — Rust implementation
// Built solely from normative artifacts: CORTEX-SPEC-0.1.md, cortex.ebnf, ast-schema.json
// No reference to Python implementation.
//
// Usage: cortex-parse <file.cortex>
//   stdout: AST JSON (if parse succeeds)
//   stderr: diagnostics (errors/warnings)
//   exit code: 0 if structure-valid, 1 otherwise

use serde::Serialize;
use std::collections::{HashMap, HashSet};
use std::env;
use std::fs;
use std::io::{self, BufRead, Write};
use std::path::Path;
use std::process;

// ---------------------------------------------------------------------------
// Diagnostic types
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize)]
struct Span {
    line: usize,
    column: usize,
}

#[derive(Debug, Clone, Serialize)]
struct Diagnostic {
    code: String,
    severity: String,
    span: Span,
    message: String,
}

impl Diagnostic {
    fn error(code: &str, line: usize, column: usize, msg: &str) -> Self {
        Self {
            code: code.to_string(),
            severity: "error".to_string(),
            span: Span { line, column },
            message: msg.to_string(),
        }
    }
}

// ---------------------------------------------------------------------------
// Scalar AST nodes (mirrors ast-schema.json exactly)
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize)]
#[serde(tag = "node")]
pub enum Scalar {
    #[serde(rename = "StringValue")]
    StringValue { value: String, lexeme: String },
    #[serde(rename = "AtomValue")]
    AtomValue { value: String, lexeme: String, #[serde(skip_serializing_if = "Option::is_none")] micro: Option<String> },
    #[serde(rename = "IntegerValue")]
    IntegerValue { value: String, lexeme: String },
    #[serde(rename = "DecimalValue")]
    DecimalValue { value: String, lexeme: String },
    #[serde(rename = "BooleanValue")]
    BooleanValue { value: bool, lexeme: String },
    #[serde(rename = "NullValue")]
    NullValue { value: (), lexeme: String },
    #[serde(rename = "ListValue")]
    ListValue { items: Vec<Scalar>, lexeme: String },
}

impl Scalar {
    fn string_value(s: &str) -> Self {
        let escaped = escape_json_string(s);
        Scalar::StringValue {
            value: s.to_string(),
            lexeme: format!("\"{}\"", escaped),
        }
    }
    fn atom_value(s: &str) -> Self {
        Scalar::AtomValue {
            value: s.to_string(),
            lexeme: s.to_string(),
            micro: None,
        }
    }
    fn int_value(s: &str) -> Self {
        Scalar::IntegerValue {
            value: s.to_string(),
            lexeme: s.to_string(),
        }
    }
    fn dec_value(s: &str) -> Self {
        Scalar::DecimalValue {
            value: s.to_string(),
            lexeme: s.to_string(),
        }
    }
    fn bool_value(b: bool) -> Self {
        let l = if b { "true" } else { "false" };
        Scalar::BooleanValue {
            value: b,
            lexeme: l.to_string(),
        }
    }
    fn null_value() -> Self {
        Scalar::NullValue {
            value: (),
            lexeme: "null".to_string(),
        }
    }
}

fn escape_json_string(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c => out.push(c),
        }
    }
    out
}

fn unescape_cortex_string(s: &str) -> Result<String, String> {
    let mut out = String::with_capacity(s.len());
    let mut chars = s.chars();
    while let Some(c) = chars.next() {
        if c == '\\' {
            match chars.next() {
                Some('"') => out.push('"'),
                Some('\\') => out.push('\\'),
                Some('n') => out.push('\n'),
                Some('r') => out.push('\r'),
                Some('t') => out.push('\t'),
                Some('b') => out.push('\u{0008}'),
                Some('f') => out.push('\u{000C}'),
                Some('u') => {
                    let hex: String = chars.by_ref().take(4).collect();
                    if hex.len() != 4 {
                        return Err("Invalid unicode escape".to_string());
                    }
                    let code = u32::from_str_radix(&hex, 16).map_err(|_| "Bad unicode hex".to_string())?;
                    let ch = char::from_u32(code).ok_or("Invalid codepoint".to_string())?;
                    out.push(ch);
                }
                Some(c) => {
                    out.push('\\');
                    out.push(c);
                }
                None => return Err("Trailing backslash".to_string()),
            }
        } else {
            out.push(c);
        }
    }
    Ok(out)
}

// ---------------------------------------------------------------------------
// AST node types (mirrors ast-schema.json)
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize)]
pub struct AttrPair {
    node: String,
    key: String,
    value: Scalar,
}

impl AttrPair {
    fn new(key: &str, value: Scalar) -> Self {
        Self {
            node: "AttrPair".to_string(),
            key: key.to_string(),
            value,
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct ContractField {
    name: String,
    #[serde(rename = "type")]
    field_type: String,
    required: bool,
}

#[derive(Debug, Clone, Serialize)]
pub struct FormatDeclaration {
    node: String,
    cortex: String,
    encoding: String,
    attributes: Vec<AttrPair>,
    #[serde(rename = "sourceLine")]
    source_line: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct MetaDeclaration {
    node: String,
    name: String,
    attributes: Vec<AttrPair>,
    #[serde(rename = "sourceLine")]
    source_line: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct EnumDeclaration {
    node: String,
    name: String,
    values: Vec<String>,
    #[serde(rename = "sourceLine")]
    source_line: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct MicroDeclaration {
    node: String,
    token: String,
    expand: String,
    #[serde(rename = "sourceLine")]
    source_line: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct NamespaceDeclaration {
    node: String,
    alias: String,
    id: String,
    version: Option<String>,
    attributes: Vec<AttrPair>,
    #[serde(rename = "sourceLine")]
    source_line: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct ExtensionDeclaration {
    node: String,
    name: String,
    namespace: String,
    id: String,
    version: String,
    #[serde(rename = "required")]
    required: bool,
    attributes: Vec<AttrPair>,
    #[serde(rename = "sourceLine")]
    source_line: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct SymbolDefinition {
    node: String,
    surface: String,
    namespace: Option<String>,
    qualified: String,
    label: String,
    shape: String,
    weight: String,
    focus: String,
    description: String,
    open: bool,
    contract: Vec<ContractField>,
    attributes: Vec<AttrPair>,
    #[serde(rename = "sourceLine")]
    source_line: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct AttrsPayload {
    node: String,
    pairs: Vec<AttrPair>,
}

#[derive(Debug, Clone, Serialize)]
pub struct BoundValue {
    field: String,
    value: Scalar,
}

#[derive(Debug, Clone, Serialize)]
pub struct PositionalPayload {
    node: String,
    cells: Vec<Scalar>,
    bound: Vec<BoundValue>,
}

#[derive(Debug, Clone, Serialize)]
pub struct RelationPayload {
    node: String,
    cells: Vec<Scalar>,
    bound: Vec<BoundValue>,
}

#[derive(Debug, Clone, Serialize)]
pub struct TextPayload {
    node: String,
    text: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct BlockPayload {
    node: String,
    text: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct FunctionInfo {
    label: String,
    weight: String,
    focus: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct Idea {
    node: String,
    address: String,
    section: usize,
    symbol: String,
    #[serde(rename = "qualifiedSymbol")]
    qualified_symbol: String,
    name: String,
    #[serde(rename = "function")]
    func: FunctionInfo,
    shape: String,
    payload: PayloadUnion,
    #[serde(rename = "sourceLine")]
    source_line: usize,
}

#[derive(Debug, Clone, Serialize)]
#[serde(untagged)]
pub enum PayloadUnion {
    Attrs(AttrsPayload),
    Positional(PositionalPayload),
    Relation(RelationPayload),
    Text(TextPayload),
    Block(BlockPayload),
}

#[derive(Debug, Clone, Serialize)]
pub struct Section {
    node: String,
    id: usize,
    title: Option<String>,
    ideas: Vec<Idea>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Glossary {
    node: String,
    format: FormatDeclaration,
    meta: Vec<MetaDeclaration>,
    enums: Vec<EnumDeclaration>,
    micros: Vec<MicroDeclaration>,
    namespaces: Vec<NamespaceDeclaration>,
    extensions: Vec<ExtensionDeclaration>,
    symbols: Vec<SymbolDefinition>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Document {
    node: String,
    #[serde(rename = "cortexVersion")]
    cortex_version: String,
    encoding: String,
    glossary: Glossary,
    sections: Vec<Section>,
}

// ---------------------------------------------------------------------------
// Line-based lexer context
// ---------------------------------------------------------------------------

struct ParseCtx {
    lines: Vec<String>,
    diagnostics: Vec<Diagnostic>,
    has_errors: bool,
}

impl ParseCtx {
    fn new(lines: Vec<String>) -> Self {
        Self {
            lines,
            diagnostics: Vec::new(),
            has_errors: false,
        }
    }

    fn error(&mut self, code: &str, line: usize, column: usize, msg: &str) {
        self.has_errors = true;
        self.diagnostics.push(Diagnostic::error(code, line, column, msg));
    }

    fn emit_diagnostics(&self) {
        let mut out = io::stderr();
        for d in &self.diagnostics {
            let _ = writeln!(
                out,
                "{}|{}:{}|{}|{}",
                d.code, d.span.line, d.span.column, d.severity, d.message
            );
        }
    }
}

// ---------------------------------------------------------------------------
// Contract parser
// ---------------------------------------------------------------------------

fn parse_contract(s: &str) -> Result<Vec<ContractField>, String> {
    let mut fields = Vec::new();
    for part in s.split('|') {
        let part = part.trim();
        if part.is_empty() {
            return Err("Empty field in contract".to_string());
        }
        let optional = part.ends_with('?');
        let base = if optional { &part[..part.len() - 1] } else { part };
        let (name, ftype) = if let Some(idx) = base.find(':') {
            let n = &base[..idx];
            let t = &base[idx + 1..];
            if n.is_empty() || t.is_empty() {
                return Err("Empty name or type in contract field".to_string());
            }
            (n.to_string(), t.to_string())
        } else {
            (base.to_string(), "any".to_string())
        };
        fields.push(ContractField {
            name,
            field_type: ftype,
            required: !optional,
        });
    }
    Ok(fields)
}

// ---------------------------------------------------------------------------
// Scalar parsers
// ---------------------------------------------------------------------------

fn try_parse_atom(s: &str) -> Option<Scalar> {
    if s.is_empty() { return None; }
    // First char must be alpha, _, or $
    let first = s.chars().next()?;
    if !first.is_ascii_alphabetic() && first != '_' && first != '$' {
        return None;
    }
    // Rest: alpha, digit, _, ., /, :, @, +, %, $, -
    for c in s.chars() {
        if !c.is_ascii_alphanumeric() && c != '_' && c != '.' && c != '/' && c != ':'
            && c != '@' && c != '+' && c != '%' && c != '$' && c != '-'
        {
            return None;
        }
    }
    // Check not a boolean or null
    if s == "true" || s == "false" {
        return None; // These are parsed as booleans
    }
    if s == "null" {
        return None;
    }
    Some(Scalar::atom_value(s))
}

fn try_parse_number(s: &str) -> Option<Scalar> {
    if s.is_empty() { return None; }
    let neg = s.starts_with('-');
    let rest = if neg { &s[1..] } else { s };
    if rest.is_empty() { return None; }
    // Check if it has a decimal point
    if let Some(dot) = rest.find('.') {
        if dot == 0 || dot == rest.len() - 1 { return None; }
        // Must be digits before and after
        let int_part = &rest[..dot];
        let frac_part = &rest[dot + 1..];
        if int_part.is_empty() || frac_part.is_empty() { return None; }
        if !int_part.chars().all(|c| c.is_ascii_digit()) { return None; }
        if !frac_part.chars().all(|c| c.is_ascii_digit()) { return None; }
        if int_part.len() > 1 && int_part.starts_with('0') { return None; } // no leading zeros in int part for dec
        Some(Scalar::dec_value(s))
    } else {
        // Integer
        if rest == "0" {
            Some(Scalar::int_value(s))
        } else if rest.starts_with('0') {
            None // No leading zeros
        } else if rest.chars().all(|c| c.is_ascii_digit()) {
            Some(Scalar::int_value(s))
        } else {
            None
        }
    }
}

fn parse_scalar_token(tok: &str) -> Option<Scalar> {
    let tok = tok.trim();
    if tok.is_empty() { return None; }
    // String
    if tok.starts_with('"') {
        let inner = &tok[1..];
        if let Some(end) = inner.rfind('"') {
            let content = &inner[..end];
            if end == inner.len() - 1 {
                if let Ok(unesc) = unescape_cortex_string(content) {
                    return Some(Scalar::string_value(&unesc));
                }
            }
        }
        return None;
    }
    // Boolean
    if tok == "true" { return Some(Scalar::bool_value(true)); }
    if tok == "false" { return Some(Scalar::bool_value(false)); }
    // Null
    if tok == "null" { return Some(Scalar::null_value()); }
    // Number
    if let Some(n) = try_parse_number(tok) { return Some(n); }
    // Atom
    try_parse_atom(tok)
}

// ---------------------------------------------------------------------------
// List parser
// ---------------------------------------------------------------------------

fn parse_list(s: &str) -> Result<Vec<Scalar>, String> {
    let s = s.trim();
    if !s.starts_with('[') || !s.ends_with(']') {
        return Err("Not a list".to_string());
    }
    let inner = s[1..s.len() - 1].trim();
    if inner.is_empty() {
        return Ok(Vec::new());
    }
    // Parse comma-separated scalars (no nested lists)
    let mut items = Vec::new();
    let mut depth = 0;
    let mut start = 0;
    let chars: Vec<char> = inner.chars().collect();
    for i in 0..chars.len() {
        match chars[i] {
            '[' => depth += 1,
            ']' => {
                if depth == 0 { return Err("Unbalanced brackets in list".to_string()); }
                depth -= 1;
            }
            '"' => {
                // Skip string content
                let mut j = i + 1;
                while j < chars.len() {
                    if chars[j] == '\\' { j += 2; continue; }
                    if chars[j] == '"' { break; }
                    j += 1;
                }
                // continue from after the string
                continue;
            }
            ',' if depth == 0 => {
                let part: String = chars[start..i].iter().collect();
                let part = part.trim();
                if !part.is_empty() {
                    if let Some(scalar) = parse_scalar_token(part) {
                        items.push(scalar);
                    } else {
                        return Err(format!("Invalid scalar in list: {}", part));
                    }
                }
                start = i + 1;
            }
            _ => {}
        }
    }
    // Last element
    if start < chars.len() {
        let part: String = chars[start..].iter().collect();
        let part = part.trim();
        if !part.is_empty() {
            if let Some(scalar) = parse_scalar_token(part) {
                items.push(scalar);
            } else {
                return Err(format!("Invalid scalar in list: {}", part));
            }
        }
    }
    if depth != 0 { return Err("Unbalanced brackets".to_string()); }
    Ok(items)
}

// ---------------------------------------------------------------------------
// Attrs payload parser: {key:value, key:value, ...}
// ---------------------------------------------------------------------------

fn parse_attrs_payload(s: &str) -> Result<Vec<AttrPair>, String> {
    let s = s.trim();
    if !s.starts_with('{') || !s.ends_with('}') {
        return Err("Not an attrs payload".to_string());
    }
    let inner = s[1..s.len() - 1].trim();
    if inner.is_empty() {
        return Ok(Vec::new());
    }
    let mut pairs = Vec::new();
    let mut depth = 0;
    let mut start = 0;
    let mut in_string = false;
    let chars: Vec<char> = inner.chars().collect();
    for i in 0..chars.len() {
        match chars[i] {
            '"' if !in_string => {
                in_string = true;
            }
            '"' if in_string => {
                // Check if escaped
                if i == 0 || chars[i-1] != '\\' {
                    in_string = false;
                }
            }
            '{' => depth += 1,
            '}' => {
                if depth > 0 { depth -= 1; }
            }
            '[' => depth += 1,
            ']' => {
                if depth > 0 { depth -= 1; }
            }
            ',' if depth == 0 && !in_string => {
                let part: String = chars[start..i].iter().collect();
                let part = part.trim();
                if !part.is_empty() {
                    pairs.push(parse_attr_pair(&part)?);
                }
                start = i + 1;
            }
            _ => {}
        }
    }
    // Last pair
    if start < chars.len() {
        let part: String = chars[start..].iter().collect();
        let part = part.trim();
        if !part.is_empty() {
            pairs.push(parse_attr_pair(&part)?);
        }
    }
    Ok(pairs)
}

fn parse_attr_pair(s: &str) -> Result<AttrPair, String> {
    let s = s.trim();
    let colon = s.find(':').ok_or_else(|| format!("Missing ':' in attr pair: {}", s))?;
    let key = s[..colon].trim();
    if key.is_empty() {
        return Err("Empty key in attr pair".to_string());
    }
    // Validate key
    for (i, c) in key.chars().enumerate() {
        if i == 0 {
            if !c.is_ascii_lowercase() && c != '_' {
                return Err(format!("Invalid key start: {}", key));
            }
        } else {
            if !c.is_ascii_lowercase() && !c.is_ascii_digit() && c != '_' && c != '-' {
                return Err(format!("Invalid key char: {}", key));
            }
        }
    }
    let value_str = s[colon + 1..].trim();
    if value_str.is_empty() {
        return Err(format!("Empty value for key: {}", key));
    }

    // Check if it's a list
    if value_str.starts_with('[') {
        let items = parse_list(value_str)?;
        let lexeme = value_str.to_string();
        return Ok(AttrPair::new(key, Scalar::ListValue { items, lexeme }));
    }

    if let Some(scalar) = parse_scalar_token(value_str) {
        Ok(AttrPair::new(key, scalar))
    } else {
        Err(format!("Cannot parse value for key '{}': {}", key, value_str))
    }
}

// ---------------------------------------------------------------------------
// Main parser
// ---------------------------------------------------------------------------

struct ParserState {
    current_section_id: usize,
    section_titles: HashMap<usize, String>,
    declared_symbols: HashMap<String, SymbolDefinition>, // surface -> def
    declared_symbols_by_label: HashMap<String, SymbolDefinition>, // label -> def
    enums: HashMap<String, EnumDeclaration>,
    micros: HashMap<String, MicroDeclaration>,
    namespaces: HashMap<String, NamespaceDeclaration>,
    extensions: HashMap<String, ExtensionDeclaration>,
    format_decl: Option<FormatDeclaration>,
    meta_decls: Vec<MetaDeclaration>,
    seen_addresses: HashSet<String>,
    seen_section_ids: HashSet<usize>,
    has_glossary: bool,
    glossary_line: usize,
    format_version: Option<String>,
    format_encoding: Option<String>,
}

fn parse_cortex_file(ctx: &mut ParseCtx, path: &Path) -> Option<Document> {
    let content = match fs::read_to_string(path) {
        Ok(c) => c,
        Err(e) => {
            ctx.error("S999_INTERNAL_PARSE_FAILURE", 1, 1, &format!("Cannot read file: {}", e));
            return None;
        }
    };

    // Check for BOM
    if content.starts_with('\u{FEFF}') {
        ctx.error("U001_BOM_FORBIDDEN", 1, 1, "UTF-8 BOM is forbidden.");
        return None;
    }

    // Split into lines, normalize CRLF
    let content = content.replace("\r\n", "\n");
    let lines: Vec<String> = content.split('\n').map(|s| s.to_string()).collect();

    if lines.is_empty() || lines.iter().all(|l| l.trim().is_empty() || l.trim().starts_with('#')) {
        ctx.error("S001_EMPTY_DOCUMENT", 1, 1, "Documento vacío.");
        return None;
    }

    let mut state = ParserState {
        current_section_id: 0,
        section_titles: HashMap::new(),
        declared_symbols: HashMap::new(),
        declared_symbols_by_label: HashMap::new(),
        enums: HashMap::new(),
        micros: HashMap::new(),
        namespaces: HashMap::new(),
        extensions: HashMap::new(),
        format_decl: None,
        meta_decls: Vec::new(),
        seen_addresses: HashSet::new(),
        seen_section_ids: HashSet::new(),
        has_glossary: false,
        glossary_line: 0,
        format_version: None,
        format_encoding: None,
    };

    let mut sections: Vec<Section> = Vec::new();
    let mut in_glossary = false;
    let mut glossary_done = false;
    let mut in_body = false;
    let mut body_sigil = String::new();
    let mut body_name = String::new();
    let mut body_lines: Vec<String> = Vec::new();
    let mut body_brace_line = 0;

    for (idx, raw_line) in lines.iter().enumerate() {
        let line_num = idx + 1;
        let trimmed = raw_line.trim();

        // Handle multiline cuerpo/bloque continuation
        if in_body {
            if trimmed == "}" {
                // End of body
                let body_text = body_lines.join("\n");
                // Record this idea
                if let Some(section) = sections.last_mut() {
                    let qualified = resolve_qualified(&body_sigil, &state);
                    let sym = state.declared_symbols.get(&qualified).or_else(|| {
                        state.declared_symbols.get(&body_sigil)
                    }).or_else(|| {
                        state.declared_symbols_by_label.get(&body_sigil)
                    });
                    let (shape, label, weight, focus) = if let Some(s) = sym {
                        (s.shape.clone(), s.label.clone(), s.weight.clone(), s.focus.clone())
                    } else {
                        ("cuerpo".to_string(), body_sigil.clone(), "B".to_string(), "$body".to_string())
                    };
                    let addr = format!("${}:{}:{}", state.current_section_id, body_sigil, body_name);
                    let payload = if shape == "bloque" {
                        PayloadUnion::Block(BlockPayload { node: "BlockPayload".to_string(), text: body_text })
                    } else {
                        PayloadUnion::Text(TextPayload { node: "TextPayload".to_string(), text: body_text })
                    };
                    section.ideas.push(Idea {
                        node: "Idea".to_string(),
                        address: addr.clone(),
                        section: state.current_section_id,
                        symbol: body_sigil.clone(),
                        qualified_symbol: qualified.clone(),
                        name: body_name.clone(),
                        func: FunctionInfo { label, weight, focus },
                        shape: shape.clone(),
                        payload,
                        source_line: body_brace_line,
                    });
                    state.seen_addresses.insert(addr);
                }
                in_body = false;
                body_lines.clear();
                continue;
            }
            body_lines.push(raw_line.clone());
            continue;
        }

        // Skip blank lines and comments
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }

        // Check for control characters (except TAB)
        for (col, c) in raw_line.chars().enumerate() {
            if c.is_control() && c != '\t' && c != '\n' && c != '\r' {
                ctx.error("U002_CONTROL_CHARACTER", line_num, col + 1, &format!("Control character U+{:04X} not allowed.", c as u32));
                return None;
            }
        }

        if !glossary_done && trimmed.starts_with("$0") {
            if in_glossary {
                ctx.error("G002_GLOSSARY_REOPENED", line_num, 1, "$0 reabierto.");
                return None;
            }
            in_glossary = true;
            state.has_glossary = true;
            state.glossary_line = line_num;

            if trimmed == "$0" {
                // Just the header line
                continue;
            }

            // Parse glossary declaration
            // Format: $0:name{...} or SIGIL:label{...}
            if let Some(content) = trimmed.strip_prefix("$0:") {
                // Meta-declaration
                parse_glossary_meta_decl(ctx, &mut state, line_num, content);
            } else if trimmed.starts_with("$0") {
                // Could be $0 followed by something else
                let rest = trimmed[2..].trim();
                if rest.starts_with(':') {
                    let content = &rest[1..];
                    parse_glossary_meta_decl(ctx, &mut state, line_num, content);
                } else if !rest.is_empty() {
                    ctx.error("S003_INVALID_IDEA_HEAD", line_num, 1, "Formato inválido en $0.");
                    return None;
                }
            }
            continue;
        }

        if in_glossary && !glossary_done && !trimmed.starts_with("$0") {
            // Symbol declaration in glossary
            // Handle both SIGIL:label{...} and namespace::SIGIL:label{...}
            let sym_info = if let Some(ns_idx) = trimmed.find("::") {
                // Check format: namespace::SIGIL:label{...}
                let after_ns = &trimmed[ns_idx + 2..];
                if let Some(colon_idx) = after_ns.find(':') {
                    let sigil_part = &after_ns[..colon_idx];
                    if is_valid_sigil(sigil_part) {
                        // Full sigil includes namespace prefix
                        let full_sigil = &trimmed[..ns_idx + 2 + colon_idx];
                        let payload_rest = &trimmed[ns_idx + 2 + colon_idx + 1..];
                        Some((full_sigil.to_string(), payload_rest.to_string()))
                    } else {
                        None
                    }
                } else {
                    None
                }
            } else if let Some((sigil_name, payload_rest)) = trimmed.split_once(':') {
                if is_valid_sigil(sigil_name) {
                    Some((sigil_name.to_string(), payload_rest.to_string()))
                } else {
                    None
                }
            } else {
                None
            };

            if let Some((sigil_name, payload_str)) = sym_info {
                parse_symbol_declaration(ctx, &mut state, line_num, &sigil_name, &payload_str);
                continue;
            }
            // Not a valid glossary entry - check if it's a section header
            if trimmed.starts_with('$') {
                // Transition to sections
                glossary_done = true;
                in_glossary = false;
            } else {
                ctx.error("G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS", line_num, 1, "Toda declaración de $0 debe usar attrs.");
                return None;
            }
        }

        // Section headers
        if trimmed.starts_with('$') && !in_body {
            glossary_done = true;
            in_glossary = false;
            parse_section_header(ctx, &mut state, line_num, trimmed, &mut sections);
            continue;
        }

        // Idea lines (after glossary is done)
        if glossary_done || (!in_glossary && state.has_glossary) {
            // Parse regular idea
            parse_idea_line(ctx, &mut state, line_num, trimmed, raw_line, &mut sections, &mut in_body,
                &mut body_sigil, &mut body_name, &mut body_lines, &mut body_brace_line);
        }
    }

    // Check for unclosed body
    if in_body {
        ctx.error("I014_UNCLOSED_BODY", body_brace_line, 1, "Cuerpo o bloque sin cierre.");
        return None;
    }

    // Validate format
    let format = state.format_decl.clone().unwrap_or_else(|| {
        ctx.error("G010_FORMAT_REQUIRED", 1, 1, "Falta declaración $0:format.");
        FormatDeclaration {
            node: "FormatDeclaration".to_string(),
            cortex: "".to_string(),
            encoding: "".to_string(),
            attributes: Vec::new(),
            source_line: 0,
        }
    });

    if format.cortex != "0.1" && !format.cortex.is_empty() {
        ctx.error("G007_UNSUPPORTED_VERSION", format.source_line, 1, &format!("Versión '{}' no soportada. Se requiere 0.1.", format.cortex));
    }
    if format.encoding != "UTF-8" && !format.encoding.is_empty() {
        ctx.error("G011_ENCODING_REQUIRED", format.source_line, 1, "Encoding debe ser UTF-8.");
    }

    // Check all used symbols are declared
    // (Already checked during parsing, but let's verify)

    if ctx.has_errors {
        return None;
    }

    // Build glossary
    let symbols: Vec<SymbolDefinition> = state.declared_symbols.values().cloned().collect();
    let enums: Vec<EnumDeclaration> = state.enums.values().cloned().collect();
    let micros: Vec<MicroDeclaration> = state.micros.values().cloned().collect();
    let namespaces: Vec<NamespaceDeclaration> = state.namespaces.values().cloned().collect();
    let extensions: Vec<ExtensionDeclaration> = state.extensions.values().cloned().collect();

    Some(Document {
        node: "Document".to_string(),
        cortex_version: "0.1".to_string(),
        encoding: "UTF-8".to_string(),
        glossary: Glossary {
            node: "Glossary".to_string(),
            format,
            meta: state.meta_decls,
            enums,
            micros,
            namespaces,
            extensions,
            symbols,
        },
        sections,
    })
}

fn is_valid_sigil(s: &str) -> bool {
    if s == "!" { return true; }
    if s.is_empty() { return false; }
    let first = s.chars().next().unwrap();
    if !first.is_ascii_uppercase() { return false; }
    if s.len() > 16 { return false; }
    s.chars().all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || c == '_')
}

fn is_valid_name(s: &str) -> bool {
    if s.is_empty() { return false; }
    let first = s.chars().next().unwrap();
    if !first.is_ascii_alphabetic() && first != '_' { return false; }
    // Allow Unicode in names per spec (but field keys are ASCII)
    true
}

fn resolve_qualified(sigil: &str, state: &ParserState) -> String {
    // Check if sigil has a namespace prefix
    if let Some(idx) = sigil.find("::") {
        return sigil.to_string();
    }
    // Check if the symbol has a namespace
    if let Some(sym) = state.declared_symbols.get(sigil) {
        if let Some(ref ns) = sym.namespace {
            return format!("{}::{}", ns, sigil);
        }
    }
    sigil.to_string()
}

fn parse_glossary_meta_decl(ctx: &mut ParseCtx, state: &mut ParserState, line_num: usize, content: &str) {
    // content is "name{...}" or "name{...}"
    let brace = content.find('{');
    let (name, payload_str) = if let Some(b) = brace {
        let n = content[..b].trim();
        let p = &content[b..];
        (n, p)
    } else {
        ctx.error("S006_INVALID_ATTRS", line_num, 1, "Meta-declaración mal formada.");
        return;
    };

    if name.is_empty() {
        ctx.error("L002_INVALID_NAME", line_num, 1, "Nombre de meta-declaración vacío.");
        return;
    }

    if name == "format" {
        // Format declaration
        if state.format_decl.is_some() {
            ctx.error("G006_DUPLICATE_FORMAT", line_num, 1, "Múltiples declaraciones $0:format.");
            return;
        }
        let pairs = match parse_attrs_payload(payload_str) {
            Ok(p) => p,
            Err(e) => {
                ctx.error("S006_INVALID_ATTRS", line_num, 1, &format!("Error en format: {}", e));
                return;
            }
        };
        let mut cortex_ver = String::new();
        let mut encoding = String::new();
        for pair in &pairs {
            if pair.key == "cortex" {
                if let Scalar::DecimalValue { ref value, .. } = pair.value {
                    cortex_ver = value.clone();
                } else if let Scalar::StringValue { ref value, .. } = pair.value {
                    cortex_ver = value.clone();
                } else if let Scalar::AtomValue { ref value, .. } = pair.value {
                    cortex_ver = value.clone();
                }
            } else if pair.key == "encoding" {
                if let Scalar::AtomValue { ref value, .. } = pair.value {
                    encoding = value.clone();
                } else if let Scalar::StringValue { ref value, .. } = pair.value {
                    encoding = value.clone();
                }
            }
        }
        state.format_decl = Some(FormatDeclaration {
            node: "FormatDeclaration".to_string(),
            cortex: cortex_ver,
            encoding,
            attributes: pairs,
            source_line: line_num,
        });
        state.meta_decls.push(MetaDeclaration {
            node: "MetaDeclaration".to_string(),
            name: "format".to_string(),
            attributes: pairs,
            source_line: line_num,
        });
    } else if name.starts_with("enum_") {
        // Enum declaration: $0:enum_name{values:"a|b|c"}
        let enum_name = &name[5..];
        if enum_name.is_empty() {
            ctx.error("L002_INVALID_NAME", line_num, 1, "Nombre de enum vacío.");
            return;
        }
        if state.enums.contains_key(enum_name) {
            ctx.error("G015_DUPLICATE_ENUM", line_num, 1, &format!("Enum '{}' duplicado.", enum_name));
            return;
        }
        let pairs = match parse_attrs_payload(payload_str) {
            Ok(p) => p,
            Err(e) => {
                ctx.error("G014_INVALID_ENUM", line_num, 1, &format!("Error en enum: {}", e));
                return;
            }
        };
        let mut values = Vec::new();
        for pair in &pairs {
            if pair.key == "values" {
                if let Scalar::StringValue { ref value, .. } = pair.value {
                    values = value.split('|').map(|s| s.trim().to_string()).collect();
                }
            }
        }
        if values.is_empty() {
            ctx.error("G014_INVALID_ENUM", line_num, 1, &format!("Enum '{}' sin values.", enum_name));
            return;
        }
        // Check for duplicates in values
        let mut seen = HashSet::new();
        for v in &values {
            if !seen.insert(v.clone()) {
                ctx.error("G014_INVALID_ENUM", line_num, 1, &format!("Valor duplicado '{}' en enum.", v));
                return;
            }
        }
        state.enums.insert(enum_name.to_string(), EnumDeclaration {
            node: "EnumDeclaration".to_string(),
            name: enum_name.to_string(),
            values,
            source_line: line_num,
        });
        state.meta_decls.push(MetaDeclaration {
            node: "MetaDeclaration".to_string(),
            name: name.to_string(),
            attributes: pairs,
            source_line: line_num,
        });
    } else if name.starts_with("micro_") {
        // Micro declaration: $0:micro_token{expand:value}
        let token = &name[6..];
        if token.is_empty() {
            ctx.error("G012_INVALID_MICRO", line_num, 1, "Nombre de microtoken vacío.");
            return;
        }
        if state.micros.contains_key(token) {
            ctx.error("G013_DUPLICATE_MICRO", line_num, 1, &format!("Microtoken '{}' duplicado.", token));
            return;
        }
        let pairs = match parse_attrs_payload(payload_str) {
            Ok(p) => p,
            Err(e) => {
                ctx.error("G012_INVALID_MICRO", line_num, 1, &format!("Error en micro: {}", e));
                return;
            }
        };
        let mut expand = String::new();
        for pair in &pairs {
            if pair.key == "expand" {
                if let Scalar::StringValue { ref value, .. } = pair.value {
                    expand = value.clone();
                } else if let Scalar::AtomValue { ref value, .. } = pair.value {
                    expand = value.clone();
                }
            }
        }
        if expand.is_empty() {
            ctx.error("G012_INVALID_MICRO", line_num, 1, &format!("Microtoken '{}' sin expand.", token));
            return;
        }
        state.micros.insert(token.to_string(), MicroDeclaration {
            node: "MicroDeclaration".to_string(),
            token: token.to_string(),
            expand,
            source_line: line_num,
        });
        state.meta_decls.push(MetaDeclaration {
            node: "MetaDeclaration".to_string(),
            name: name.to_string(),
            attributes: pairs,
            source_line: line_num,
        });
    } else if name.starts_with("namespace_") {
        // Namespace declaration: $0:namespace_alias{id:..., version:..., required:...}
        let alias = &name[10..];
        if alias.is_empty() {
            ctx.error("L002_INVALID_NAME", line_num, 1, "Nombre de namespace vacío.");
            return;
        }
        if state.namespaces.contains_key(alias) {
            ctx.error("G005_DUPLICATE_SYMBOL", line_num, 1, &format!("Namespace '{}' duplicado.", alias));
            return;
        }
        let pairs = match parse_attrs_payload(payload_str) {
            Ok(p) => p,
            Err(e) => {
                ctx.error("X001_INVALID_EXTENSION_DECLARATION", line_num, 1, &format!("Error en namespace: {}", e));
                return;
            }
        };
        let mut id = String::new();
        let mut version = None;
        for pair in &pairs {
            if pair.key == "id" {
                if let Scalar::StringValue { ref value, .. } = pair.value {
                    id = value.clone();
                } else if let Scalar::AtomValue { ref value, .. } = pair.value {
                    id = value.clone();
                }
            } else if pair.key == "version" {
                if let Scalar::StringValue { ref value, .. } = pair.value {
                    version = Some(value.clone());
                } else if let Scalar::AtomValue { ref value, .. } = pair.value {
                    version = Some(value.clone());
                }
            }
        }
        if id.is_empty() {
            ctx.error("X001_INVALID_EXTENSION_DECLARATION", line_num, 1, &format!("Namespace '{}' sin id.", alias));
            return;
        }
        state.namespaces.insert(alias.to_string(), NamespaceDeclaration {
            node: "NamespaceDeclaration".to_string(),
            alias: alias.to_string(),
            id: id.clone(),
            version,
            attributes: pairs.clone(),
            source_line: line_num,
        });
        state.meta_decls.push(MetaDeclaration {
            node: "MetaDeclaration".to_string(),
            name: name.to_string(),
            attributes: pairs,
            source_line: line_num,
        });
    } else if name.starts_with("extension_") {
        // Extension declaration: $0:extension_name{namespace:..., id:..., version:..., required:...}
        let ext_name = &name[10..];
        if ext_name.is_empty() {
            ctx.error("X001_INVALID_EXTENSION_DECLARATION", line_num, 1, "Nombre de extensión vacío.");
            return;
        }
        if state.extensions.contains_key(ext_name) {
            ctx.error("X001_INVALID_EXTENSION_DECLARATION", line_num, 1, &format!("Extensión '{}' duplicada.", ext_name));
            return;
        }
        let pairs = match parse_attrs_payload(payload_str) {
            Ok(p) => p,
            Err(e) => {
                ctx.error("X001_INVALID_EXTENSION_DECLARATION", line_num, 1, &format!("Error en extensión: {}", e));
                return;
            }
        };
        let mut ext_ns = String::new();
        let mut ext_id = String::new();
        let mut ext_ver = String::new();
        let mut required = false;
        for pair in &pairs {
            match pair.key.as_str() {
                "namespace" => {
                    if let Scalar::StringValue { ref value, .. } = pair.value {
                        ext_ns = value.clone();
                    } else if let Scalar::AtomValue { ref value, .. } = pair.value {
                        ext_ns = value.clone();
                    }
                }
                "id" => {
                    if let Scalar::StringValue { ref value, .. } = pair.value {
                        ext_id = value.clone();
                    } else if let Scalar::AtomValue { ref value, .. } = pair.value {
                        ext_id = value.clone();
                    }
                }
                "version" => {
                    if let Scalar::StringValue { ref value, .. } = pair.value {
                        ext_ver = value.clone();
                    } else if let Scalar::AtomValue { ref value, .. } = pair.value {
                        ext_ver = value.clone();
                    } else if let Scalar::DecimalValue { ref value, .. } = pair.value {
                        ext_ver = value.clone();
                    }
                }
                "required" => {
                    if let Scalar::BooleanValue { ref value, .. } = pair.value {
                        required = *value;
                    }
                }
                _ => {}
            }
        }
        if ext_ns.is_empty() || ext_id.is_empty() || ext_ver.is_empty() {
            ctx.error("X001_INVALID_EXTENSION_DECLARATION", line_num, 1,
                "Extensión debe tener namespace, id y version.");
            return;
        }
        if required {
            ctx.error("X002_REQUIRED_EXTENSION_UNSUPPORTED", line_num, 1,
                &format!("Extensión requerida '{}' no soportada.", ext_name));
            return;
        }
        state.extensions.insert(ext_name.to_string(), ExtensionDeclaration {
            node: "ExtensionDeclaration".to_string(),
            name: ext_name.to_string(),
            namespace: ext_ns,
            id: ext_id,
            version: ext_ver,
            required: false,
            attributes: pairs.clone(),
            source_line: line_num,
        });
        state.meta_decls.push(MetaDeclaration {
            node: "MetaDeclaration".to_string(),
            name: name.to_string(),
            attributes: pairs,
            source_line: line_num,
        });
    } else {
        // Other meta declarations
        let pairs = match parse_attrs_payload(payload_str) {
            Ok(p) => p,
            Err(e) => {
                ctx.error("S006_INVALID_ATTRS", line_num, 1, &format!("Error en declaración: {}", e));
                return;
            }
        };
        state.meta_decls.push(MetaDeclaration {
            node: "MetaDeclaration".to_string(),
            name: name.to_string(),
            attributes: pairs,
            source_line: line_num,
        });
    }
}

fn parse_symbol_declaration(ctx: &mut ParseCtx, state: &mut ParserState, line_num: usize, sigil: &str, payload: &str) {
    // payload is "label{...}" or "label{...}"
    // Support namespace::SIGIL:label{...} format
    let (bare_sigil, label, payload_str) = if let Some(colon_idx) = payload.find(':') {
        // Check if there's a :: prefix before the colon
        let before_label = &payload[..colon_idx];
        let after_colon = &payload[colon_idx + 1..];

        // The label part starts after the last :: or colon
        let brace = after_colon.find('{');
        let (lbl, rest) = if let Some(b) = brace {
            (after_colon[..b].trim(), after_colon[b..].trim())
        } else {
            (after_colon.trim(), "")
        };

        // Check if sigil has :: namespace
        if let Some(ns_idx) = sigil.find("::") {
            let ns = &sigil[..ns_idx];
            let s = &sigil[ns_idx + 2..];
            if ns.is_empty() || s.is_empty() {
                ctx.error("L001_INVALID_SYMBOL", line_num, 1, "Namespace o sigilo vacío.");
                return;
            }
            (sigil, lbl, rest)
        } else {
            (sigil, lbl, rest)
        }
    } else {
        ctx.error("S006_INVALID_ATTRS", line_num, 1, &format!("Declaración de sigilo {} mal formada.", sigil));
        return;
    };

    if label.is_empty() {
        ctx.error("L002_INVALID_NAME", line_num, 1, &format!("Etiqueta vacía para sigilo {}.", sigil));
        return;
    }

    // Extract namespace from sigil if present
    let (surface, namespace) = if let Some(idx) = sigil.find("::") {
        let ns = &sigil[..idx];
        let s = &sigil[idx + 2..];
        (sigil.to_string(), Some(ns.to_string()))
    } else {
        (sigil.to_string(), None)
    };

    // Parse the attrs payload
    let attrs_content = if payload_str.starts_with('{') {
        // We already split at :, so the payload starts with the attrs content
        // Actually we need to find the { in the original payload
        payload
    } else {
        payload_str
    };

    // Find the attrs braces in the full payload
    let brace_start = attrs_content.find('{');
    let brace_end = attrs_content.rfind('}');

    let pairs = if let (Some(start), Some(end)) = (brace_start, brace_end) {
        if end <= start {
            ctx.error("S006_INVALID_ATTRS", line_num, 1, "Llaves desbalanceadas.");
            return;
        }
        match parse_attrs_payload(&attrs_content[start..=end]) {
            Ok(p) => p,
            Err(e) => {
                ctx.error("S006_INVALID_ATTRS", line_num, 1, &format!("Error en attrs de sigilo: {}", e));
                return;
            }
        }
    } else {
        ctx.error("S006_INVALID_ATTRS", line_num, 1, "Declaración de sigilo sin llaves.");
        return;
    };

    // Check for duplicate
    if state.declared_symbols.contains_key(sigil) {
        if namespace.is_some() {
            ctx.error("G028_DUPLICATE_QUALIFIED_SYMBOL", line_num, 1, &format!("Sigilo cualificado '{}' duplicado.", sigil));
        } else {
            ctx.error("G005_DUPLICATE_SYMBOL", line_num, 1, &format!("Sigilo '{}' duplicado.", sigil));
        }
        return;
    }

    let mut shape = String::new();
    let mut weight = String::new();
    let mut focus = String::new();
    let mut desc = String::new();
    let mut fields_str = String::new();
    let mut pos_str = String::new();
    let mut open = false;
    let mut sym_ns = namespace.clone();

    for pair in &pairs {
        match pair.key.as_str() {
            "type" => {
                if let Scalar::AtomValue { ref value, .. } = pair.value {
                    shape = value.clone();
                } else if let Scalar::StringValue { ref value, .. } = pair.value {
                    shape = value.clone();
                }
            }
            "weight" => {
                if let Scalar::AtomValue { ref value, .. } = pair.value {
                    weight = value.clone();
                }
            }
            "focus" => {
                if let Scalar::AtomValue { ref value, .. } = pair.value {
                    focus = value.clone();
                } else if let Scalar::StringValue { ref value, .. } = pair.value {
                    focus = value.clone();
                }
            }
            "desc" => {
                if let Scalar::StringValue { ref value, .. } = pair.value {
                    desc = value.clone();
                } else if let Scalar::AtomValue { ref value, .. } = pair.value {
                    desc = value.clone();
                }
            }
            "fields" => {
                if let Scalar::StringValue { ref value, .. } = pair.value {
                    fields_str = value.clone();
                }
            }
            "pos" => {
                if let Scalar::StringValue { ref value, .. } = pair.value {
                    pos_str = value.clone();
                }
            }
            "open" => {
                if let Scalar::BooleanValue { ref value, .. } = pair.value {
                    open = *value;
                }
            }
            "namespace" => {
                if let Scalar::StringValue { ref value, .. } = pair.value {
                    sym_ns = Some(value.clone());
                } else if let Scalar::AtomValue { ref value, .. } = pair.value {
                    sym_ns = Some(value.clone());
                }
            }
            _ => {}
        }
    }

    // Validate required fields
    if shape.is_empty() {
        ctx.error("G016_SYMBOL_TYPE_REQUIRED", line_num, 1, &format!("Sigilo '{}' sin type.", sigil));
        return;
    }
    let valid_shapes = ["attrs", "attrs-pos", "cuerpo", "bloque", "relacion"];
    if !valid_shapes.contains(&shape.as_str()) {
        ctx.error("G017_UNKNOWN_SHAPE", line_num, 1, &format!("Shape '{}' desconocida.", shape));
        return;
    }
    if weight.is_empty() {
        ctx.error("G018_SYMBOL_WEIGHT_REQUIRED", line_num, 1, &format!("Sigilo '{}' sin weight.", sigil));
        return;
    }
    if weight != "B" && weight != "M" && weight != "H" {
        ctx.error("G019_INVALID_WEIGHT", line_num, 1, &format!("Weight '{}' inválido.", weight));
        return;
    }
    if desc.is_empty() {
        ctx.error("G020_SYMBOL_DESCRIPTION_REQUIRED", line_num, 1, &format!("Sigilo '{}' sin desc.", sigil));
        return;
    }

    // Validate contract based on shape
    let contract = match shape.as_str() {
        "attrs" => {
            if fields_str.is_empty() {
                ctx.error("G021_ATTRS_CONTRACT_REQUIRED", line_num, 1, &format!("Sigilo attrs '{}' sin fields.", sigil));
                return Vec::new();
            }
            match parse_contract(&fields_str) {
                Ok(f) => f,
                Err(e) => {
                    ctx.error("G008_INVALID_CONTRACT", line_num, 1, &format!("Contrato inválido: {}", e));
                    return;
                }
            }
        }
        "attrs-pos" => {
            if pos_str.is_empty() {
                ctx.error("G022_POSITIONAL_CONTRACT_REQUIRED", line_num, 1, &format!("Sigilo attrs-pos '{}' sin pos.", sigil));
                return Vec::new();
            }
            match parse_contract(&pos_str) {
                Ok(f) => f,
                Err(e) => {
                    ctx.error("G008_INVALID_CONTRACT", line_num, 1, &format!("Contrato inválido: {}", e));
                    return;
                }
            }
        }
        "relacion" => {
            if pos_str.is_empty() {
                ctx.error("G022_POSITIONAL_CONTRACT_REQUIRED", line_num, 1, &format!("Sigilo relacion '{}' sin pos.", sigil));
                return Vec::new();
            }
            let fields = match parse_contract(&pos_str) {
                Ok(f) => f,
                Err(e) => {
                    ctx.error("G008_INVALID_CONTRACT", line_num, 1, &format!("Contrato inválido: {}", e));
                    return;
                }
            };
            if fields.len() < 3 {
                ctx.error("G023_RELATION_CONTRACT_TOO_SHORT", line_num, 1, "Relación debe tener al menos 3 campos.");
                return Vec::new();
            }
            fields
        }
        "cuerpo" | "bloque" => Vec::new(),
        _ => Vec::new(),
    };

    // Validate focus
    if focus.is_empty() && shape != "cuerpo" && shape != "bloque" {
        ctx.error("G024_FOCUS_REQUIRED", line_num, 1, &format!("Sigilo '{}' sin focus.", sigil));
        return;
    }
    if shape == "cuerpo" || shape == "bloque" {
        focus = "$body".to_string();
    }

    // Validate focus exists in contract for structured shapes
    if shape == "attrs" && !contract.is_empty() {
        let has_focus = contract.iter().any(|f| f.name == focus);
        if !has_focus {
            ctx.error("G025_UNKNOWN_FOCUS_FIELD", line_num, 1,
                &format!("Focus '{}' no existe en contrato de '{}'.", focus, sigil));
            return;
        }
    }

    // Validate field types
    for field in &contract {
        let ft = &field.field_type;
        if ft.starts_with('%') {
            let enum_name = &ft[1..];
            if !state.enums.contains_key(enum_name) {
                ctx.error("G026_UNKNOWN_ENUM_REFERENCE", line_num, 1,
                    &format!("Enum '{}' no declarado.", enum_name));
                return;
            }
        } else if !["any", "text", "atom", "int", "dec", "bool", "null", "list"].contains(&ft.as_str()) {
            ctx.error("G027_UNKNOWN_FIELD_TYPE", line_num, 1,
                &format!("Tipo de campo '{}' desconocido.", ft));
            return;
        }
    }

    // Check duplicate contract field names
    {
        let mut seen = HashSet::new();
        for f in &contract {
            if !seen.insert(f.name.clone()) {
                ctx.error("G009_DUPLICATE_CONTRACT_FIELD", line_num, 1,
                    &format!("Campo '{}' duplicado en contrato.", f.name));
                return;
            }
        }
    }

    let qualified = if let Some(ref ns) = sym_ns {
        format!("{}::{}", ns, sigil.split("::").last().unwrap_or(sigil))
    } else {
        sigil.to_string()
    };

    let sym_def = SymbolDefinition {
        node: "SymbolDefinition".to_string(),
        surface: surface.clone(),
        namespace: sym_ns,
        qualified,
        label: label.to_string(),
        shape: shape.clone(),
        weight: weight.clone(),
        focus: focus.clone(),
        description: desc,
        open,
        contract,
        attributes: pairs,
        source_line: line_num,
    };

    state.declared_symbols.insert(sigil.to_string(), sym_def);
}

fn parse_section_header(ctx: &mut ParseCtx, state: &mut ParserState, line_num: usize, line: &str, sections: &mut Vec<Section>) {
    // $N or $N: Title
    let rest = &line[1..].trim();
    let (id_str, title) = if let Some(idx) = rest.find(':') {
        let id = rest[..idx].trim();
        let t = rest[idx + 1..].trim();
        // Title requires at least one space after colon
        if t.is_empty() || rest.as_bytes().get(idx + 1).copied() == Some(b' ') || !t.is_empty() {
            (id, Some(t.to_string()))
        } else {
            (id, None)
        }
    } else {
        (rest, None)
    };

    let section_id: usize = match id_str.parse() {
        Ok(n) if n > 0 => n,
        _ => {
            ctx.error("S002_DUPLICATE_SECTION", line_num, 1, &format!("ID de sección inválido: {}${}", line, id_str));
            return;
        }
    };

    if state.seen_section_ids.contains(&section_id) {
        ctx.error("S002_DUPLICATE_SECTION", line_num, 1, &format!("Sección ${} duplicada.", section_id));
        return;
    }
    state.seen_section_ids.insert(section_id);
    state.current_section_id = section_id;
    if let Some(ref t) = title {
        state.section_titles.insert(section_id, t.clone());
    }

    sections.push(Section {
        node: "Section".to_string(),
        id: section_id,
        title,
        ideas: Vec::new(),
    });
}

fn parse_idea_line(ctx: &mut ParseCtx, state: &mut ParserState, line_num: usize, trimmed: &str, raw_line: &str,
    sections: &mut Vec<Section>, in_body: &mut bool,
    body_sigil: &mut String, body_name: &mut String, body_lines: &mut Vec<String>, body_brace_line: &mut usize) {

    if sections.is_empty() {
        ctx.error("S005_CONTENT_OUTSIDE_SECTION", line_num, 1, "Contenido fuera de sección.");
        return;
    }

    // Check for attrs (braced): SIGIL:name{...}
    // Check for positional (pipe): SIGIL:name|...|...
    // Check for multiline start: SIGIL:name{ followed by newline

    // Find the idea head: SIGIL:name
    let head_end = find_idea_head_end(trimmed);
    if head_end == 0 {
        ctx.error("S003_INVALID_IDEA_HEAD", line_num, 1, &format!("Encabezado inválido: {}", trimmed));
        return;
    }

    let head = &trimmed[..head_end];
    let rest = trimmed[head_end..].trim();

    // Parse head: [namespace::]SIGIL:name
    let (sigil, name) = if let Some(idx) = head.find("::") {
        let full = head;
        let after_ns = &head[idx + 2..];
        if let Some(colon) = after_ns.find(':') {
            let s = &after_ns[..colon];
            let n = &after_ns[colon + 1..];
            (full, n.to_string())
        } else {
            ctx.error("S003_INVALID_IDEA_HEAD", line_num, 1, &format!("Encabezado inválido: {}", head));
            return;
        }
    } else {
        if let Some(colon) = head.find(':') {
            let s = &head[..colon];
            let n = &head[colon + 1..];
            (s, n.to_string())
        } else {
            ctx.error("S003_INVALID_IDEA_HEAD", line_num, 1, &format!("Encabezado inválido: {}", head));
            return;
        }
    };

    // Validate sigil
    let bare_sigil = sigil.split("::").last().unwrap_or(sigil);
    if !is_valid_sigil(bare_sigil) {
        ctx.error("L001_INVALID_SYMBOL", line_num, 1, &format!("Sigilo inválido: {}", bare_sigil));
        return;
    }

    // Validate name
    if !is_valid_name(&name) {
        ctx.error("L002_INVALID_NAME", line_num, 1, &format!("Nombre inválido: {}", name));
        return;
    }

    // Resolve symbol
    let qualified = resolve_qualified(sigil, state);
    let sym = state.declared_symbols.get(sigil)
        .or_else(|| state.declared_symbols_by_label.get(sigil));

    if sym.is_none() {
        // Undeclared symbol - still parse, but flag error
        ctx.error("I001_UNDECLARED_SYMBOL", line_num, 1, &format!("Sigilo '{}' no declarado en $0.", bare_sigil));
        return;
    }

    let sym = sym.unwrap();

    // Determine shape from rest
    if rest.starts_with('{') {
        if sym.shape == "attrs-pos" || sym.shape == "relacion" {
            ctx.error("I004_SHAPE_DELIMITER_MISMATCH", line_num, 1,
                &format!("Sigilo '{}' usa shape '{}' pero se encontró '{{'.",
                    bare_sigil, sym.shape));
            return;
        }

        if sym.shape == "cuerpo" || sym.shape == "bloque" {
            // Check if it's a one-line body: {text}
            let trimmed_rest = rest.trim();
            if trimmed_rest.len() > 1 && trimmed_rest.ends_with('}') && !trimmed_rest[1..trimmed_rest.len()-1].contains('\n') {
                // One-line body
                // Need to check the actual raw line to find the closing brace
                let raw_trimmed = raw_line.trim();
                if let Some(end) = raw_trimmed.rfind('}') {
                    let inner = raw_trimmed[raw_trimmed.find('{').unwrap() + 1..end].trim();
                    let text = if sym.shape == "bloque" {
                        PayloadUnion::Block(BlockPayload { node: "BlockPayload".to_string(), text: inner.to_string() })
                    } else {
                        PayloadUnion::Text(TextPayload { node: "TextPayload".to_string(), text: inner.to_string() })
                    };
                    let addr = format!("${}:{}:{}", state.current_section_id, sigil, name);
                    if state.seen_addresses.contains(&addr) {
                        ctx.error("I002_DUPLICATE_IDEA_ADDRESS", line_num, 1, &format!("Dirección duplicada: {}", addr));
                    }
                    let section = sections.last_mut().unwrap();
                    section.ideas.push(Idea {
                        node: "Idea".to_string(),
                        address: addr.clone(),
                        section: state.current_section_id,
                        symbol: sigil.to_string(),
                        qualified_symbol: qualified,
                        name: name.clone(),
                        func: FunctionInfo {
                            label: sym.label.clone(),
                            weight: sym.weight.clone(),
                            focus: sym.focus.clone(),
                        },
                        shape: sym.shape.clone(),
                        payload: text,
                        source_line: line_num,
                    });
                    state.seen_addresses.insert(addr);
                    return;
                }
            }

            // Multi-line body
            *in_body = true;
            *body_sigil = sigil.to_string();
            *body_name = name.clone();
            *body_brace_line = line_num;
            body_lines.clear();
            // Check if there's content on the opening line after {
            let open_brace = raw_line.find('{').unwrap();
            let after_brace = raw_line[open_brace + 1..].trim();
            if !after_brace.is_empty() && !after_brace.starts_with('}') {
                // Some content on the same line as the opening brace
                // But actually per spec, multiline body should have content on next lines
                // We'll ignore content on the opening line
            }
            return;
        }

        // Attrs payload
        let payload_str = find_matching_brace(raw_line, line_num, ctx);
        if payload_str.is_none() {
            ctx.error("S006_INVALID_ATTRS", line_num, 1, "Attrs mal formados.");
            return;
        }
        let payload_str = payload_str.unwrap();

        let pairs = match parse_attrs_payload(&payload_str) {
            Ok(p) => p,
            Err(e) => {
                ctx.error("S006_INVALID_ATTRS", line_num, 1, &format!("Error en attrs: {}", e));
                return;
            }
        };

        // Validate pairs against contract
        validate_attrs_against_contract(ctx, state, sym, &pairs, line_num);

        let addr = format!("${}:{}:{}", state.current_section_id, sigil, name);
        if state.seen_addresses.contains(&addr) {
            ctx.error("I002_DUPLICATE_IDEA_ADDRESS", line_num, 1, &format!("Dirección duplicada: {}", addr));
            return;
        }
        state.seen_addresses.insert(addr.clone());

        // Check attrs must be one line
        if raw_line.trim() != trimmed {
            ctx.error("I003_ATTRS_MUST_BE_ONE_LINE", line_num, 1, "Attrs debe estar en una sola línea.");
            return;
        }

        let section = sections.last_mut().unwrap();
        section.ideas.push(Idea {
            node: "Idea".to_string(),
            address: addr,
            section: state.current_section_id,
            symbol: sigil.to_string(),
            qualified_symbol: qualified,
            name: name.clone(),
            func: FunctionInfo {
                label: sym.label.clone(),
                weight: sym.weight.clone(),
                focus: sym.focus.clone(),
            },
            shape: sym.shape.clone(),
            payload: PayloadUnion::Attrs(AttrsPayload {
                node: "AttrsPayload".to_string(),
                pairs,
            }),
            source_line: line_num,
        });
    } else if rest.starts_with('|') {
        if sym.shape == "attrs" {
            ctx.error("I004_SHAPE_DELIMITER_MISMATCH", line_num, 1,
                &format!("Sigilo '{}' usa shape 'attrs' pero se encontró '|'.", bare_sigil));
            return;
        }

        // Positional / pipe payload
        let cells_str = &rest[1..]; // Skip leading |
        let raw_cells: Vec<&str> = split_pipe_cells(cells_str);
        let mut cells: Vec<Scalar> = Vec::new();

        for (ci, cell) in raw_cells.iter().enumerate() {
            let cell = cell.trim();
            if cell.is_empty() {
                cells.push(Scalar::null_value());
                continue;
            }

            // Determine type from contract if available
            let expected_type = sym.contract.get(ci).map(|f| f.field_type.as_str()).unwrap_or("text");

            if cell.starts_with('"') {
                // Quoted pipe cell - always parse as string
                if let Some(scalar) = parse_scalar_token(cell) {
                    cells.push(scalar);
                } else {
                    ctx.error("L005_INVALID_STRING", line_num, 1, &format!("String inválido: {}", cell));
                    return;
                }
            } else if expected_type == "atom" {
                // Try parsing as atom value
                if let Some(scalar) = try_parse_atom(cell) {
                    cells.push(scalar);
                } else {
                    // Fallback to string
                    cells.push(Scalar::string_value(cell));
                }
            } else if expected_type == "int" {
                if let Some(scalar) = try_parse_number(cell) {
                    cells.push(scalar);
                } else {
                    cells.push(Scalar::string_value(cell));
                }
            } else {
                // Default: treat as string value
                cells.push(Scalar::string_value(cell));
            }
        }

        // Validate positional arity
        let required_count = sym.contract.iter().filter(|f| f.required).count();
        if cells.len() < required_count {
            ctx.error("I012_POSITIONAL_ARITY", line_num, 1,
                &format!("Esperados al menos {} campos, se encontraron {}.", required_count, cells.len()));
            return;
        }
        if cells.len() > sym.contract.len() {
            ctx.error("I012_POSITIONAL_ARITY", line_num, 1,
                &format!("Esperados máximo {} campos, se encontraron {}.", sym.contract.len(), cells.len()));
            return;
        }

        // If relacion, validate min 3 cells
        if sym.shape == "relacion" && cells.len() < 3 {
            ctx.error("I013_RELATION_ARITY", line_num, 1, "Relación debe tener al menos 3 células.");
            return;
        }

        let addr = format!("${}:{}:{}", state.current_section_id, sigil, name);
        if state.seen_addresses.contains(&addr) {
            ctx.error("I002_DUPLICATE_IDEA_ADDRESS", line_num, 1, &format!("Dirección duplicada: {}", addr));
            return;
        }
        state.seen_addresses.insert(addr.clone());

        // Build bound values
        let mut bound = Vec::new();
        for (i, cell) in cells.iter().enumerate() {
            if i < sym.contract.len() {
                bound.push(BoundValue {
                    field: sym.contract[i].name.clone(),
                    value: cell.clone(),
                });
            }
        }

        let section = sections.last_mut().unwrap();
        if sym.shape == "relacion" {
            section.ideas.push(Idea {
                node: "Idea".to_string(),
                address: addr,
                section: state.current_section_id,
                symbol: sigil.to_string(),
                qualified_symbol: qualified,
                name: name.clone(),
                func: FunctionInfo {
                    label: sym.label.clone(),
                    weight: sym.weight.clone(),
                    focus: sym.focus.clone(),
                },
                shape: sym.shape.clone(),
                payload: PayloadUnion::Relation(RelationPayload {
                    node: "RelationPayload".to_string(),
                    cells,
                    bound,
                }),
                source_line: line_num,
            });
        } else {
            section.ideas.push(Idea {
                node: "Idea".to_string(),
                address: addr,
                section: state.current_section_id,
                symbol: sigil.to_string(),
                qualified_symbol: qualified,
                name: name.clone(),
                func: FunctionInfo {
                    label: sym.label.clone(),
                    weight: sym.weight.clone(),
                    focus: sym.focus.clone(),
                },
                shape: sym.shape.clone(),
                payload: PayloadUnion::Positional(PositionalPayload {
                    node: "PositionalPayload".to_string(),
                    cells,
                    bound,
                }),
                source_line: line_num,
            });
        }
    } else {
        ctx.error("S004_MISSING_PAYLOAD", line_num, 1, &format!("Idea '{}:{}' sin payload.", sigil, name));
    }
}

fn find_idea_head_end(line: &str) -> usize {
    // Find end of SIGIL:name pattern
    // Could have namespace:: prefix
    let mut i = 0;
    let chars: Vec<char> = line.chars().collect();
    // Skip namespace if present
    if let Some(idx) = line.find("::") {
        i = idx + 2;
    }
    // Find SIGIL
    while i < chars.len() && (chars[i].is_ascii_uppercase() || chars[i].is_ascii_digit() || chars[i] == '_' || chars[i] == '!') {
        i += 1;
    }
    if i < chars.len() && chars[i] == ':' {
        i += 1;
        // Find name
        while i < chars.len() && (chars[i].is_ascii_alphanumeric() || chars[i] == '_' || chars[i] == '.' || chars[i] == '-') {
            i += 1;
        }
        return i;
    }
    0
}

fn find_matching_brace(line: &str, line_num: usize, ctx: &mut ParseCtx) -> Option<String> {
    let start = line.find('{')?;
    let end = line.rfind('}')?;
    if end <= start {
        ctx.error("S006_INVALID_ATTRS", line_num, 1, "Llaves desbalanceadas.");
        return None;
    }
    Some(line[start..=end].to_string())
}

fn split_pipe_cells(s: &str) -> Vec<&str> {
    let mut cells = Vec::new();
    let mut depth = 0;
    let mut in_string = false;
    let mut start = 0;
    let chars: Vec<char> = s.chars().collect();
    for i in 0..chars.len() {
        match chars[i] {
            '"' => {
                in_string = !in_string;
            }
            '|' if !in_string && depth == 0 => {
                cells.push(&s[start..i]);
                start = i + 1;
            }
            _ => {}
        }
    }
    cells.push(&s[start..]);
    cells
}

fn validate_attrs_against_contract(ctx: &mut ParseCtx, state: &ParserState, sym: &SymbolDefinition, pairs: &[AttrPair], line_num: usize) {
    if sym.contract.is_empty() {
        return;
    }

    // Check unknown fields (if not open)
    if !sym.open {
        let known: HashSet<&str> = sym.contract.iter().map(|f| f.name.as_str()).collect();
        for pair in pairs {
            if !known.contains(pair.key.as_str()) {
                ctx.error("I005_UNKNOWN_FIELD", line_num, 1,
                    &format!("Campo desconocido '{}' para sigilo '{}'.", pair.key, sym.surface));
                return;
            }
        }
    }

    // Check duplicate fields
    let mut seen = HashSet::new();
    for pair in pairs {
        if !seen.insert(pair.key.clone()) {
            ctx.error("I006_DUPLICATE_FIELD", line_num, 1,
                &format!("Campo duplicado '{}'.", pair.key));
            return;
        }
    }

    // Check field order
    let order: HashMap<&str, usize> = sym.contract.iter().enumerate().map(|(i, f)| (f.name.as_str(), i)).collect();
    let mut last_pos: Option<usize> = None;
    for pair in pairs {
        if let Some(pos) = order.get(pair.key.as_str()) {
            if let Some(lp) = last_pos {
                if *pos < lp {
                    ctx.error("I007_FIELD_ORDER", line_num, 1,
                        &format!("Campo '{}' fuera de orden contractual.", pair.key));
                    return;
                }
            }
            last_pos = Some(*pos);
        }
    }

    // Check required fields present
    let present: HashSet<&str> = pairs.iter().map(|p| p.key.as_str()).collect();
    for field in &sym.contract {
        if field.required && !present.contains(field.name.as_str()) {
            ctx.error("I008_REQUIRED_FIELD_MISSING", line_num, 1,
                &format!("Falta campo requerido: {}.", field.name));
            return;
        }
    }

    // Check focus is not empty
    let focus = &sym.focus;
    if focus != "$body" {
        for pair in pairs {
            if pair.key == *focus {
                match &pair.value {
                    Scalar::StringValue { value, .. } if value.is_empty() => {
                        ctx.error("I016_EMPTY_FOCUS", line_num, 1, "Foco textual vacío.");
                        return;
                    }
                    _ => {}
                }
            }
        }
    }

    // Check enum violations
    for pair in pairs {
        for field in &sym.contract {
            if field.name == pair.key && field.field_type.starts_with('%') {
                let enum_name = &field.field_type[1..];
                if let Some(enum_decl) = state.enums.get(enum_name) {
                    match &pair.value {
                        Scalar::AtomValue { ref value, .. } => {
                            if !enum_decl.values.contains(value) {
                                ctx.error("I010_ENUM_VIOLATION", line_num, 1,
                                    &format!("'{}' no es un valor válido para enum '{}'. Valores: {:?}",
                                        value, enum_name, enum_decl.values));
                                return;
                            }
                        }
                        Scalar::StringValue { ref value, .. } => {
                            if !enum_decl.values.contains(value) {
                                ctx.error("I010_ENUM_VIOLATION", line_num, 1,
                                    &format!("'{}' no es un valor válido para enum '{}'.", value, enum_name));
                                return;
                            }
                        }
                        _ => {
                            ctx.error("I009_FIELD_TYPE_MISMATCH", line_num, 1,
                                &format!("Campo '{}' espera tipo enum (atom).", field.name));
                            return;
                        }
                    }
                }
            }
        }
    }

    // Check type mismatches (basic check)
    for pair in pairs {
        for field in &sym.contract {
            if field.name != pair.key { continue; }
            let expected = &field.field_type;
            match expected.as_str() {
                "text" => {
                    match &pair.value {
                        Scalar::StringValue { .. } => {}
                        _ => {
                            ctx.error("I009_FIELD_TYPE_MISMATCH", line_num, 1,
                                &format!("Campo '{}' espera string.", field.name));
                            return;
                        }
                    }
                }
                "atom" => {
                    match &pair.value {
                        Scalar::AtomValue { .. } => {}
                        Scalar::StringValue { .. } => {} // Allow strings too
                        _ => {
                            ctx.error("I009_FIELD_TYPE_MISMATCH", line_num, 1,
                                &format!("Campo '{}' espera atom.", field.name));
                            return;
                        }
                    }
                }
                "int" => {
                    match &pair.value {
                        Scalar::IntegerValue { .. } => {}
                        _ => {
                            ctx.error("I009_FIELD_TYPE_MISMATCH", line_num, 1,
                                &format!("Campo '{}' espera integer.", field.name));
                            return;
                        }
                    }
                }
                "dec" => {
                    match &pair.value {
                        Scalar::DecimalValue { .. } => {}
                        _ => {
                            ctx.error("I009_FIELD_TYPE_MISMATCH", line_num, 1,
                                &format!("Campo '{}' espera decimal.", field.name));
                            return;
                        }
                    }
                }
                "bool" => {
                    match &pair.value {
                        Scalar::BooleanValue { .. } => {}
                        _ => {
                            ctx.error("I009_FIELD_TYPE_MISMATCH", line_num, 1,
                                &format!("Campo '{}' espera boolean.", field.name));
                            return;
                        }
                    }
                }
                "null" => {
                    match &pair.value {
                        Scalar::NullValue { .. } => {}
                        _ => {
                            ctx.error("I009_FIELD_TYPE_MISMATCH", line_num, 1,
                                &format!("Campo '{}' espera null.", field.name));
                            return;
                        }
                    }
                }
                "list" => {
                    match &pair.value {
                        Scalar::ListValue { .. } => {}
                        _ => {
                            ctx.error("I009_FIELD_TYPE_MISMATCH", line_num, 1,
                                &format!("Campo '{}' espera list.", field.name));
                            return;
                        }
                    }
                }
                "any" => {}
                _ if expected.starts_with('%') => {} // Enum checked above
                _ => {}
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Main entry point
// ---------------------------------------------------------------------------

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: cortex-parse <file.cortex>");
        process::exit(1);
    }

    let path = Path::new(&args[1]);
    let content = match fs::read_to_string(path) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("S999_INTERNAL_PARSE_FAILURE|1|1|error|Cannot read file: {}", e);
            process::exit(1);
        }
    };

    let lines: Vec<String> = content.replace("\r\n", "\n")
        .split('\n')
        .map(|s| s.to_string())
        .collect();

    let mut ctx = ParseCtx::new(lines);

    match parse_cortex_file(&mut ctx, path) {
        Some(doc) => {
            // Output AST JSON to stdout
            match serde_json::to_string_pretty(&doc) {
                Ok(json) => {
                    println!("{}", json);
                }
                Err(e) => {
                    ctx.error("S999_INTERNAL_PARSE_FAILURE", 1, 1, &format!("JSON serialization error: {}", e));
                }
            }
        }
        None => {
            // Parse failed, diagnostics already collected
        }
    }

    // Emit diagnostics to stderr
    ctx.emit_diagnostics();

    if ctx.has_errors {
        process::exit(1);
    }
}
