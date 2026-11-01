//! CORTEX 1.0 / 0.2 slots surface: parser, C14N and HCORTEX 1.0 render/compile.

use crate::error::ParseError;
use crate::model::{Attrs, Scalar, ScalarValue};
use crate::scalars::{
    classify_raw_cell, emit_string_literal, parse_attrs_payload, parse_scalar, skip_inline_ws,
    to_nfc, StringCursor,
};
use regex::Regex;
use serde::Serialize;

pub const SLOT_MARKER: char = '※';
pub const SLOT_INDEX_MAX: usize = 1_000_000;

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct V10ContractField {
    pub position: usize,
    pub name: String,
    pub field_type: String,
    pub required: bool,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct V10FieldValue {
    pub position: usize,
    pub name: String,
    pub field_type: String,
    pub required: bool,
    pub value: Scalar,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct V10SigilMap {
    pub marker: String,
    pub codepoint: String,
    pub base: usize,
    pub syntax: String,
    pub order: String,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct V10Symbol {
    pub namespace: Option<String>,
    pub sigil: String,
    pub label: String,
    pub shape: String,
    pub weight: String,
    pub focus: String,
    pub desc: String,
    pub open: bool,
    pub contract: Vec<V10ContractField>,
    pub attrs: Attrs,
    pub encoding: Option<String>,
}

impl V10Symbol {
    pub fn qualified(&self) -> String {
        self.namespace
            .as_ref()
            .map(|ns| format!("{ns}::{}", self.sigil))
            .unwrap_or_else(|| self.sigil.clone())
    }
}

#[derive(Debug, Clone, PartialEq, Serialize)]
#[serde(tag = "shape", content = "value", rename_all = "kebab-case")]
pub enum V10Payload {
    Attrs(Attrs),
    Positional(Vec<Scalar>),
    Slots(Vec<V10FieldValue>),
    Body(String),
    Block(String),
    MultilinePending,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct V10Idea {
    pub section: u64,
    pub namespace: Option<String>,
    pub symbol: String,
    pub name: String,
    pub shape: String,
    pub payload: V10Payload,
}

impl V10Idea {
    pub fn qualified_symbol(&self) -> String {
        self.namespace
            .as_ref()
            .map(|ns| format!("{ns}::{}", self.symbol))
            .unwrap_or_else(|| self.symbol.clone())
    }
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct V10Section {
    pub id: u64,
    pub title: Option<String>,
    pub ideas: Vec<V10Idea>,
    pub capa: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Default, Serialize)]
pub struct V10Glossary {
    pub capa: Option<String>,
    pub format: Option<crate::model::FormatDecl>,
    pub meta: Vec<crate::model::MetaDecl>,
    pub enums: Vec<crate::model::EnumDecl>,
    pub micros: Vec<crate::model::MicroDecl>,
    pub namespaces: Vec<crate::model::NamespaceDecl>,
    pub extensions: Vec<crate::model::ExtensionDecl>,
    pub symbols: Vec<V10Symbol>,
    pub sigil_map: Option<V10SigilMap>,
}

#[derive(Debug, Clone, PartialEq, Default, Serialize)]
pub struct V10Doc {
    pub cortex_version: String,
    pub glossary: V10Glossary,
    pub sections: Vec<V10Section>,
}

struct V10Parser {
    lines: Vec<String>,
    doc: V10Doc,
    in_glossary: bool,
    current: Option<usize>,
    in_body: bool,
    body_lines: Vec<String>,
    body_idea: Option<V10Idea>,
    body_kind: String,
    seen_sigil_map: bool,
    seen_any_slots: bool,
    seen_section_ids: Vec<u64>,
    seen_idea_addresses: Vec<String>,
    seen_symbol_keys: Vec<String>,
}

pub fn parse_v10(source: &str, version: &str) -> Result<V10Doc, ParseError> {
    if source.starts_with('\u{feff}') {
        return Err(ParseError::new("U001_BOM_FORBIDDEN", "BOM forbidden"));
    }
    let normalized = source.replace("\r\n", "\n").replace('\r', "\n");
    let parser = V10Parser {
        lines: normalized.split('\n').map(String::from).collect(),
        doc: V10Doc { cortex_version: version.to_string(), ..Default::default() },
        in_glossary: false,
        current: None,
        in_body: false,
        body_lines: Vec::new(),
        body_idea: None,
        body_kind: String::new(),
        seen_sigil_map: false,
        seen_any_slots: false,
        seen_section_ids: Vec::new(),
        seen_idea_addresses: Vec::new(),
        seen_symbol_keys: Vec::new(),
    };
    parser.parse()
}

impl V10Parser {
    fn parse(mut self) -> Result<V10Doc, ParseError> {
        let mut i = 0;
        while i < self.lines.len() {
            let raw = self.lines[i].clone();
            let line_no = i + 1;
            if self.in_body {
                if raw.trim() == "}" {
                    let text = self.body_lines.join("\n");
                    if let Some(idea) = self.body_idea.as_mut() {
                        idea.payload = if self.body_kind == "cuerpo" {
                            V10Payload::Body(text)
                        } else {
                            V10Payload::Block(text)
                        };
                    }
                    if let (Some(idx), Some(idea)) = (self.current, self.body_idea.take()) {
                        self.doc.sections[idx].ideas.push(idea);
                    }
                    self.in_body = false;
                    self.body_lines.clear();
                    self.body_kind.clear();
                    i += 1;
                    continue;
                }
                self.body_lines.push(raw);
                i += 1;
                continue;
            }
            let stripped = raw.trim().to_string();
            if stripped.is_empty() || stripped.starts_with('#') {
                i += 1;
                continue;
            }
            if let Some(c) = capa_zero(&stripped) {
                if self.in_glossary {
                    return Err(ParseError::at("G002_GLOSSARY_REOPENED", "$0 reopened", line_no, 0));
                }
                self.in_glossary = true;
                self.doc.glossary.capa = Some(c);
                i += 1;
                continue;
            }
            if is_glossary_title(&stripped) {
                if self.in_glossary {
                    return Err(ParseError::at("G002_GLOSSARY_REOPENED", "$0 reopened", line_no, 0));
                }
                self.in_glossary = true;
                i += 1;
                continue;
            }
            if let Some((sid, capa)) = section_capa(&stripped) {
                self.start_section(sid, None, Some(capa), line_no)?;
                i += 1;
                continue;
            }
            if let Some((sid, title_raw)) = section_number(&stripped) {
                if sid == 0 {
                    if self.in_glossary {
                        return Err(ParseError::at("G002_GLOSSARY_REOPENED", "$0 reopened", line_no, 0));
                    }
                    self.in_glossary = true;
                    i += 1;
                    continue;
                }
                let mut title = title_raw.map(|t| t.trim().to_string()).filter(|t| !t.is_empty());
                let mut capa = None;
                if let Some(t) = title.as_ref() {
                    let (new_title, c) = split_capa(t);
                    title = Some(new_title);
                    capa = c;
                }
                self.start_section(sid, title, capa, line_no)?;
                i += 1;
                continue;
            }
            if let Some((sid, title_raw)) = section_title(&stripped) {
                let (title, capa) = split_capa(&title_raw);
                self.start_section(sid, Some(title), capa, line_no)?;
                i += 1;
                continue;
            }
            if self.in_glossary && (stripped.starts_with("$0:") || is_glossary_decl(&stripped)) {
                self.parse_glossary_declaration(&stripped, line_no)?;
                i += 1;
                continue;
            }
            if self.current.is_none() && !self.in_glossary {
                return Err(ParseError::at(
                    "S005_CONTENT_OUTSIDE_SECTION",
                    format!("Content outside section: {stripped:?}"),
                    line_no,
                    0,
                ));
            }
            if self.in_glossary {
                self.parse_glossary_declaration(&stripped, line_no)?;
                i += 1;
                continue;
            }
            let section_id = self.current.unwrap();
            let idea = self.parse_idea_line(&stripped, section_id as u64, line_no)?;
            if matches!(idea.payload, V10Payload::MultilinePending) {
                self.in_body = true;
                self.body_lines.clear();
                self.body_kind = idea.shape.clone();
                self.body_idea = Some(idea);
                i += 1;
                continue;
            }
            self.doc.sections[section_id].ideas.push(idea);
            i += 1;
        }
        if self.seen_any_slots && !self.seen_sigil_map {
            return Err(ParseError::new("G030_SIGIL_MAP_REQUIRED", "0.2 uses slots but $0:sigil-map is missing"));
        }
        if self.in_body {
            return Err(ParseError::new("S007_UNCLOSED_BODY", "Unclosed body"));
        }
        Ok(self.doc)
    }

    fn start_section(
        &mut self,
        sid: u64,
        title: Option<String>,
        capa: Option<String>,
        line_no: usize,
    ) -> Result<(), ParseError> {
        if self.seen_section_ids.contains(&sid) {
            return Err(ParseError::at("S002_DUPLICATE_SECTION", format!("Duplicate section ${sid}"), line_no, 0));
        }
        self.seen_section_ids.push(sid);
        if self.seen_any_slots && !self.seen_sigil_map {
            return Err(ParseError::at("G030_SIGIL_MAP_REQUIRED", "0.2 uses slots but $0:sigil-map is missing", line_no, 0));
        }
        self.doc.sections.push(V10Section { id: sid, title, ideas: Vec::new(), capa });
        self.current = Some(self.doc.sections.len() - 1);
        self.in_glossary = false;
        Ok(())
    }

    fn parse_glossary_declaration(&mut self, line: &str, line_no: usize) -> Result<(), ParseError> {
        let brace_idx = line.find('{').ok_or_else(|| {
            ParseError::at("G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS", format!("Glossary declaration must use attrs: {line:?}"), line_no, 0)
        })?;
        let close_idx = find_matching_brace(line, brace_idx)
            .ok_or_else(|| ParseError::at("S006_INVALID_ATTRS", "Unclosed {", line_no, 0))?;
        let head = line[..brace_idx].trim().to_string();
        let payload = line[brace_idx..=close_idx].to_string();
        let tail = line[close_idx + 1..].trim().to_string();
        let mut capa = None;
        if !tail.is_empty() {
            let re = Regex::new(r"^:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$").unwrap();
            if let Some(c) = re.captures(&tail) {
                capa = Some(c[1].to_string());
            }
        }
        if let Some(name) = head.strip_prefix("$0:") {
            return self.add_meta_declaration(name, &payload, line_no, capa);
        }
        let re = Regex::new(r"^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):(.+)$").unwrap();
        let caps = re.captures(&head).ok_or_else(|| {
            ParseError::at("L001_INVALID_SYMBOL", format!("Invalid sigil declaration head: {head:?}"), line_no, 0)
        })?;
        let ns = caps.get(1).map(|m| m.as_str().to_string());
        let sigil = caps[2].to_string();
        let label = caps[3].to_string();
        let key = format!("{}\u{0}{}", ns.clone().unwrap_or_default(), sigil);
        if self.seen_symbol_keys.contains(&key) {
            return Err(ParseError::at(
                "G015_DUPLICATE_SYMBOL",
                format!("Duplicate symbol {}{}", ns.as_ref().map(|n| format!("{n}::")).unwrap_or_default(), sigil),
                line_no,
                0,
            ));
        }
        let attrs = parse_attrs_payload(&payload, line_no)?;
        let sym = self.build_symbol_def(ns, sigil, label, attrs, line_no)?;
        self.doc.glossary.symbols.push(sym);
        self.seen_symbol_keys.push(key);
        Ok(())
    }

    fn add_meta_declaration(
        &mut self,
        name: &str,
        payload: &str,
        line_no: usize,
        capa: Option<String>,
    ) -> Result<(), ParseError> {
        let attrs = parse_attrs_payload(payload, line_no)?;
        if name != "sigil-map" {
            for (k, v) in &attrs {
                if k.contains(SLOT_MARKER) {
                    return Err(ParseError::at("I050_SLOT_NOT_ALLOWED_IN_GLOSSARY", format!("※ in $0:{name} key {k:?}"), line_no, 0));
                }
                if let ScalarValue::String(s) = &v.value {
                    if s.contains(SLOT_MARKER) {
                        return Err(ParseError::at("I050_SLOT_NOT_ALLOWED_IN_GLOSSARY", format!("※ in $0:{name} attr {k}"), line_no, 0));
                    }
                }
            }
        }
        let map = |key: &str| attrs.iter().find(|(k, _)| k == key).map(|(_, v)| v.clone());
        match name {
            "format" => {
                if self.doc.glossary.format.is_some() {
                    return Err(ParseError::at("G006_DUPLICATE_FORMAT", "Duplicate $0:format", line_no, 0));
                }
                let cortex = map("cortex").and_then(|v| v.text_value().map(String::from)).unwrap_or_else(|| "0.1".into());
                let encoding = map("encoding").and_then(|v| v.text_value().map(String::from)).unwrap_or_else(|| "UTF-8".into());
                if cortex != "0.2" && cortex != "1.0" {
                    return Err(ParseError::at("G007_UNSUPPORTED_VERSION", format!("Declared cortex {cortex} != parser version {}", self.doc.cortex_version), line_no, 0));
                }
                if encoding != "UTF-8" {
                    return Err(ParseError::at("G011_ENCODING_REQUIRED", format!("Encoding must be UTF-8: {encoding}"), line_no, 0));
                }
                self.doc.glossary.format = Some(crate::model::FormatDecl { cortex, encoding, attrs, source_line: line_no });
            }
            "sigil-map" => {
                if self.seen_any_slots {
                    return Err(ParseError::at("G041_SIGIL_MAP_ORDER", "$0:sigil-map must appear before any sigil with encoding:slots", line_no, 0));
                }
                if self.seen_sigil_map {
                    return Err(ParseError::at("G031_DUPLICATE_SIGIL_MAP", "More than one $0:sigil-map", line_no, 0));
                }
                let sm = V10SigilMap {
                    marker: map("marker").and_then(|v| v.text_value().map(String::from)).unwrap_or_else(|| "※".into()),
                    codepoint: map("codepoint").and_then(|v| v.text_value().map(String::from)).unwrap_or_else(|| "U+203B".into()),
                    base: map("base").and_then(|v| v.text_value().map(|s| s.parse().ok()).flatten()).unwrap_or(1),
                    syntax: map("syntax").and_then(|v| v.text_value().map(String::from)).unwrap_or_else(|| "※N:valor".into()),
                    order: map("order").and_then(|v| v.text_value().map(String::from)).unwrap_or_else(|| "ascending".into()),
                };
                if sm.marker != "※" || sm.codepoint != "U+203B" || sm.base != 1 || sm.syntax != "※N:valor" || sm.order != "ascending" {
                    return Err(ParseError::at("G032_INVALID_SIGIL_MAP", "sigil-map values are not canonical", line_no, 0));
                }
                self.doc.glossary.sigil_map = Some(sm);
                self.seen_sigil_map = true;
            }
            _ if name.starts_with("enum_") => {
                let ename = name[5..].to_string();
                let v = map("values").ok_or_else(|| ParseError::at("G014_INVALID_ENUM", format!("enum {ename} missing values string"), line_no, 0))?;
                let s = match &v.value {
                    ScalarValue::String(s) => s.clone(),
                    _ => return Err(ParseError::at("G014_INVALID_ENUM", format!("enum {ename} missing values string"), line_no, 0)),
                };
                self.doc.glossary.enums.push(crate::model::EnumDecl { name: ename, values: s.split('|').map(String::from).collect(), source_line: line_no });
            }
            _ if name.starts_with("micro_") => {
                let token = name[6..].to_string();
                let v = map("expand").ok_or_else(|| ParseError::at("G012_INVALID_MICRO", format!("micro {token} missing expand"), line_no, 0))?;
                let expand = v.text_value().map(String::from).unwrap_or_else(|| v.lexeme.clone());
                self.doc.glossary.micros.push(crate::model::MicroDecl { token, expand, source_line: line_no });
            }
            _ if name.starts_with("namespace_") => {
                self.doc.glossary.namespaces.push(crate::model::NamespaceDecl { alias: name[10..].to_string(), attrs, source_line: line_no });
            }
            _ if name.starts_with("extension_") => {
                self.doc.glossary.extensions.push(crate::model::ExtensionDecl { name: name[10..].to_string(), attrs, source_line: line_no });
            }
            _ => {
                self.doc.glossary.meta.push(crate::model::MetaDecl { name: name.to_string(), attrs, source_line: line_no, capa });
            }
        }
        Ok(())
    }

    fn build_symbol_def(
        &mut self,
        ns: Option<String>,
        sigil: String,
        label: String,
        attrs: Attrs,
        line_no: usize,
    ) -> Result<V10Symbol, ParseError> {
        let map = |key: &str| attrs.iter().find(|(k, _)| k == key).map(|(_, v)| v.clone());
        let type_v = map("type").ok_or_else(|| ParseError::at("G016_SYMBOL_TYPE_REQUIRED", format!("sigil {sigil} missing type"), line_no, 0))?;
        let shape = type_v.text_value().map(String::from).unwrap_or_else(|| type_v.lexeme.clone());
        if !["attrs", "attrs-pos", "cuerpo", "bloque", "relacion"].contains(&shape.as_str()) {
            return Err(ParseError::at("G017_UNKNOWN_SHAPE", format!("Unknown shape: {shape}"), line_no, 0));
        }
        let weight_v = map("weight").ok_or_else(|| ParseError::at("G018_SYMBOL_WEIGHT_REQUIRED", format!("sigil {sigil} missing weight"), line_no, 0))?;
        let weight = weight_v.text_value().map(String::from).unwrap_or_else(|| weight_v.lexeme.clone());
        if !["B", "M", "H"].contains(&weight.as_str()) {
            return Err(ParseError::at("G019_INVALID_WEIGHT", format!("Invalid weight: {weight}"), line_no, 0));
        }
        let desc_v = map("desc").ok_or_else(|| ParseError::at("G020_SYMBOL_DESCRIPTION_REQUIRED", format!("sigil {sigil} missing desc"), line_no, 0))?;
        let desc = desc_v.text_value().map(String::from).unwrap_or_else(|| desc_v.lexeme.clone());
        let is_open = map("open").map(|v| v.is_true()).unwrap_or(false);
        let mut encoding = None;
        if let Some(v) = map("encoding") {
            let enc = v.text_value().map(String::from).unwrap_or_else(|| v.lexeme.clone());
            if enc != "slots" {
                return Err(ParseError::at("G039_ENCODING_SHAPE_MISMATCH", format!("Unknown encoding: {enc}"), line_no, 0));
            }
            if !["attrs", "attrs-pos", "relacion"].contains(&shape.as_str()) {
                return Err(ParseError::at("G039_ENCODING_SHAPE_MISMATCH", format!("encoding:slots not valid for shape {shape}"), line_no, 0));
            }
            self.seen_any_slots = true;
            if !self.seen_sigil_map {
                return Err(ParseError::at("G030_SIGIL_MAP_REQUIRED", format!("sigil {sigil} uses encoding:slots but $0:sigil-map not yet declared"), line_no, 0));
            }
            encoding = Some(enc);
        }
        let mut contract: Vec<V10ContractField> = Vec::new();
        if encoding.as_deref() == Some("slots") {
            let slots_v = map("slots").ok_or_else(|| ParseError::at("G033_SLOT_CONTRACT_REQUIRED", format!("sigil {sigil} with encoding:slots missing slots"), line_no, 0))?;
            let slots_str = slots_v.text_value().map(String::from).unwrap_or_else(|| slots_v.lexeme.clone());
            if map("fields").is_some() || map("pos").is_some() {
                return Err(ParseError::at("G040_CONTRACT_SURFACE_CONFLICT", format!("sigil {sigil} cannot have fields/pos + slots"), line_no, 0));
            }
            contract = parse_slot_contract(&slots_str, line_no)?;
            if is_open {
                return Err(ParseError::at("G038_SLOTS_OPEN_FORBIDDEN", format!("sigil {sigil} slots cannot be open"), line_no, 0));
            }
        } else if shape == "attrs" {
            let fields_v = map("fields").ok_or_else(|| ParseError::at("G021_ATTRS_CONTRACT_REQUIRED", format!("sigil {sigil} missing fields"), line_no, 0))?;
            let fields = fields_v.text_value().map(String::from).unwrap_or_else(|| fields_v.lexeme.clone());
            contract = crate::parser::parse_contract_fields(&fields)?
                .into_iter()
                .map(|f| V10ContractField { position: 0, name: f.name, field_type: f.field_type, required: f.required })
                .collect();
        } else if shape == "attrs-pos" || shape == "relacion" {
            let pos_v = map("pos").ok_or_else(|| ParseError::at("G022_POSITIONAL_CONTRACT_REQUIRED", format!("sigil {sigil} missing pos"), line_no, 0))?;
            let pos = pos_v.text_value().map(String::from).unwrap_or_else(|| pos_v.lexeme.clone());
            contract = crate::parser::parse_contract_fields(&pos)?
                .into_iter()
                .map(|f| V10ContractField { position: 0, name: f.name, field_type: f.field_type, required: f.required })
                .collect();
            if shape == "relacion" && contract.len() < 3 {
                return Err(ParseError::at("G023_RELATION_CONTRACT_TOO_SHORT", "relacion needs >=3 fields", line_no, 0));
            }
        }
        let focus = if let Some(v) = map("focus") {
            let f = v.text_value().map(String::from).unwrap_or_else(|| v.lexeme.clone());
            if ["attrs", "attrs-pos", "relacion"].contains(&shape.as_str()) {
                let field = contract.iter().find(|c| c.name == f);
                match field {
                    None if encoding.as_deref() == Some("slots") => {
                        return Err(ParseError::at("G037_SLOT_FOCUS_UNRESOLVED", format!("focus {f:?} not in slot contract"), line_no, 0))
                    }
                    None => return Err(ParseError::at("G025_UNKNOWN_FOCUS_FIELD", format!("focus {f:?} not in contract"), line_no, 0)),
                    Some(cf) if encoding.as_deref() == Some("slots") && !cf.required => {
                        return Err(ParseError::at("G037_SLOT_FOCUS_UNRESOLVED", format!("focus {f:?} must be a required slot"), line_no, 0))
                    }
                    Some(_) => {}
                }
            }
            f
        } else if shape == "cuerpo" || shape == "bloque" {
            "$body".to_string()
        } else {
            return Err(ParseError::at("G024_FOCUS_REQUIRED", format!("sigil {sigil} missing focus"), line_no, 0));
        };
        Ok(V10Symbol { namespace: ns, sigil, label, shape, weight, focus, desc, open: is_open, contract, attrs, encoding })
    }

    fn parse_idea_line(&mut self, line: &str, section_id: u64, line_no: usize) -> Result<V10Idea, ParseError> {
        let re = Regex::new(r"^(?:([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):([^{|}\s]+)").unwrap();
        let caps = re.captures(line).ok_or_else(|| ParseError::at("S003_INVALID_IDEA_HEAD", format!("Invalid idea head: {line:?}"), line_no, 0))?;
        let ns = caps.get(1).map(|m| m.as_str().to_string());
        let sigil = caps[2].to_string();
        let name = caps[3].to_string();
        let rest = line[caps.get(0).unwrap().end()..].to_string();
        let sym = self.doc.glossary.symbols.iter().find(|s| s.sigil == sigil && s.namespace == ns).cloned();
        let sym = sym.ok_or_else(|| ParseError::at("I001_UNDECLARED_SYMBOL", format!("Undeclared sigil: {sigil}"), line_no, 0))?;
        let addr = format!("${section_id}:{}{}:{}", ns.as_ref().map(|n| format!("{n}::")).unwrap_or_default(), sigil, name);
        if self.seen_idea_addresses.contains(&addr) {
            return Err(ParseError::at("I006_DUPLICATE_IDEA_ADDRESS", format!("Duplicate idea address {addr}"), line_no, 0));
        }
        self.seen_idea_addresses.push(addr);
        if sym.encoding.as_deref() == Some("slots") {
            if !rest.starts_with('{') {
                return Err(ParseError::at("I004_SHAPE_DELIMITER_MISMATCH", "Expected { for slot-encoded Idea", line_no, 0));
            }
            if !rest.ends_with('}') || rest.contains('\n') {
                return Err(ParseError::at("I004_SHAPE_DELIMITER_MISMATCH", "Slot-encoded Idea must be single-line", line_no, 0));
            }
            let entries = parse_slot_payload(&rest, line_no)?;
            let fvs = resolve_slot_entries(&entries, &sym, line_no)?;
            return Ok(V10Idea { section: section_id, namespace: ns, symbol: sigil, name, shape: sym.shape.clone(), payload: V10Payload::Slots(fvs) });
        }
        self.parse_idea_line_legacy(section_id, line_no, ns, sigil, name, rest, &sym)
    }

    fn parse_idea_line_legacy(
        &self,
        section_id: u64,
        line_no: usize,
        ns: Option<String>,
        sigil: String,
        name: String,
        rest: String,
        sym: &V10Symbol,
    ) -> Result<V10Idea, ParseError> {
        let shape = sym.shape.clone();
        if ["attrs", "cuerpo", "bloque"].contains(&shape.as_str()) {
            if !rest.starts_with('{') {
                return Err(ParseError::at("I004_SHAPE_DELIMITER_MISMATCH", format!("Expected {{ for shape {shape}"), line_no, 0));
            }
            if rest.ends_with('}') && !rest.contains('\n') {
                if shape == "attrs" {
                    let pairs = parse_attrs_payload(&rest, line_no)?;
                    validate_attrs_payload(&pairs, sym, line_no)?;
                    return Ok(V10Idea { section: section_id, namespace: ns, symbol: sigil, name, shape, payload: V10Payload::Attrs(pairs) });
                }
                let inner = rest[1..rest.len() - 1].to_string();
                let inner = if shape == "cuerpo" { to_nfc(&inner) } else { inner };
                let payload = if shape == "cuerpo" { V10Payload::Body(inner) } else { V10Payload::Block(inner) };
                return Ok(V10Idea { section: section_id, namespace: ns, symbol: sigil, name, shape, payload });
            }
            if rest.trim() != "{" {
                return Err(ParseError::at("I004_SHAPE_DELIMITER_MISMATCH", format!("Expected single {{ for multiline {shape}"), line_no, 0));
            }
            return Ok(V10Idea { section: section_id, namespace: ns, symbol: sigil, name, shape, payload: V10Payload::MultilinePending });
        }
        if shape == "attrs-pos" || shape == "relacion" {
            if !rest.starts_with('|') {
                return Err(ParseError::at("I004_SHAPE_DELIMITER_MISMATCH", format!("Expected | for shape {shape}"), line_no, 0));
            }
            let cells = parse_pipe_cells(&rest[1..], line_no)?;
            let required = sym.contract.iter().filter(|f| f.required).count();
            if cells.len() < required {
                return Err(ParseError::at("I012_POSITIONAL_ARITY", format!("shape {shape} needs ≥{required} cells, got {}", cells.len()), line_no, 0));
            }
            if cells.len() > sym.contract.len() {
                return Err(ParseError::at("I012_POSITIONAL_ARITY", format!("shape {shape} expects ≤{} cells, got {}", sym.contract.len(), cells.len()), line_no, 0));
            }
            return Ok(V10Idea { section: section_id, namespace: ns, symbol: sigil, name, shape, payload: V10Payload::Positional(cells) });
        }
        Err(ParseError::at("S999_INTERNAL_PARSE_FAILURE", format!("Cannot parse idea: {rest:?}"), line_no, 0))
    }
}

fn validate_attrs_payload(pairs: &Attrs, sym: &V10Symbol, line_no: usize) -> Result<(), ParseError> {
    let mut seen: Vec<String> = Vec::new();
    for (k, _) in pairs {
        if seen.contains(k) {
            return Err(ParseError::at("I006_DUPLICATE_FIELD", format!("Duplicate field {k:?}"), line_no, 0));
        }
        seen.push(k.clone());
    }
    if !sym.open {
        for (k, _) in pairs {
            if !sym.contract.iter().any(|f| &f.name == k) {
                return Err(ParseError::at("I005_UNKNOWN_FIELD", format!("Unknown field {k:?}"), line_no, 0));
            }
        }
    }
    for f in &sym.contract {
        if f.required && !seen.contains(&f.name) {
            return Err(ParseError::at("I008_REQUIRED_FIELD_MISSING", format!("Required field {:?} missing", f.name), line_no, 0));
        }
    }
    Ok(())
}

fn parse_slot_contract(source: &str, line: usize) -> Result<Vec<V10ContractField>, ParseError> {
    let mut out = Vec::new();
    if source.is_empty() {
        return Ok(out);
    }
    for raw in source.split('|') {
        let part = raw.trim();
        if part.is_empty() {
            return Err(ParseError::at("G008_INVALID_CONTRACT", format!("Empty slot-contract entry in {source:?}"), line, 0));
        }
        let (pos_str, mut rest) = part
            .split_once('=')
            .ok_or_else(|| ParseError::at("G008_INVALID_CONTRACT", format!("Slot entry missing '=': {part:?}"), line, 0))?;
        let pos_str = pos_str.trim();
        let re = Regex::new(r"^[1-9][0-9]*$").unwrap();
        if !re.is_match(pos_str) {
            return Err(ParseError::at("G008_INVALID_CONTRACT", format!("Invalid slot position {pos_str:?}"), line, 0));
        }
        let position: usize = pos_str.parse().unwrap();
        if position == 0 {
            return Err(ParseError::at("L022_SLOT_ZERO_FORBIDDEN", "Slot position 0 forbidden", line, 0));
        }
        if position > SLOT_INDEX_MAX {
            return Err(ParseError::at("I057_SLOT_INDEX_LIMIT", format!("Slot position {position} exceeds max"), line, 0));
        }
        let required = !rest.ends_with('?');
        if !required {
            rest = &rest[..rest.len() - 1];
        }
        let (name, field_type) = rest.split_once(':').unwrap_or((rest, "any"));
        let name = name.trim().to_string();
        if name.is_empty() {
            return Err(ParseError::at("G008_INVALID_CONTRACT", format!("Empty slot name in {part:?}"), line, 0));
        }
        out.push(V10ContractField { position, name, field_type: field_type.trim().to_string(), required });
    }
    let mut seen_pos = Vec::new();
    let mut seen_name: Vec<String> = Vec::new();
    for f in &out {
        if seen_pos.contains(&f.position) {
            return Err(ParseError::at("G035_DUPLICATE_SLOT_POSITION", format!("Duplicate slot position {}", f.position), line, 0));
        }
        if seen_name.contains(&f.name) {
            return Err(ParseError::at("G036_DUPLICATE_SLOT_NAME", format!("Duplicate slot name {:?}", f.name), line, 0));
        }
        seen_pos.push(f.position);
        seen_name.push(f.name.clone());
    }
    let mut sorted = out.clone();
    sorted.sort_by_key(|f| f.position);
    for (idx, f) in sorted.iter().enumerate() {
        if f.position != idx + 1 {
            return Err(ParseError::at("G034_SLOT_CONTRACT_GAP", format!("Slot positions not contiguous: expected {}, got {}", idx + 1, f.position), line, 0));
        }
    }
    Ok(out)
}

fn parse_slot_payload(source: &str, start_line: usize) -> Result<Vec<(usize, Scalar)>, ParseError> {
    let mut cur = StringCursor::new(source, start_line, 1);
    skip_inline_ws(&mut cur);
    if cur.peek() != Some('{') {
        return Err(ParseError::at("S006_INVALID_ATTRS", "Expected { for slot payload", cur.line, cur.col));
    }
    cur.next();
    let mut entries = Vec::new();
    skip_inline_ws(&mut cur);
    if cur.peek() == Some('}') {
        cur.next();
        return Ok(entries);
    }
    check_slot_start(&mut cur)?;
    loop {
        skip_inline_ws(&mut cur);
        check_slot_start(&mut cur)?;
        let index = parse_slot_ref(&mut cur)?;
        skip_inline_ws(&mut cur);
        let value = parse_scalar(&mut cur)?;
        entries.push((index, value));
        skip_inline_ws(&mut cur);
        match cur.peek() {
            Some(',') => {
                cur.next();
                skip_inline_ws(&mut cur);
                if cur.peek() == Some('}') {
                    cur.next();
                    return Err(ParseError::at("S006_INVALID_ATTRS", "Trailing comma before } in slot payload", cur.line, cur.col));
                }
            }
            Some('}') => {
                cur.next();
                break;
            }
            other => {
                return Err(ParseError::at("S006_INVALID_ATTRS", format!("Expected , or }} got {other:?}"), cur.line, cur.col))
            }
        }
    }
    Ok(entries)
}

fn check_slot_start(cur: &mut StringCursor) -> Result<(), ParseError> {
    let ch = match cur.peek() {
        None => return Ok(()),
        Some(c) => c,
    };
    if ch == SLOT_MARKER {
        return Ok(());
    }
    if let Some(name) = homoglyph(ch) {
        return Err(ParseError::at("L020_INVALID_SLOT_MARKER", format!("Slot marker is not ※ (got {name})"), cur.line, cur.col));
    }
    if ch == '|' {
        return Err(ParseError::at("I056_PIPE_PAYLOAD_IN_SLOT_IDEA", "Pipe payload not allowed in slot-encoded Idea", cur.line, cur.col));
    }
    if ch.is_ascii_alphabetic() || ch == '_' {
        let save = (cur.i, cur.line, cur.col);
        while let Some(c) = cur.peek() {
            if c == ' ' || c == '\t' || c == ':' || c == ',' {
                break;
            }
            if c == '}' {
                break;
            }
            cur.next();
        }
        if cur.peek() == Some(':') {
            return Err(ParseError::at("I055_NAMED_ATTR_IN_SLOT_IDEA", "Named key:value not allowed in slot-encoded Idea", save.1, save.2));
        }
        cur.i = save.0;
        cur.line = save.1;
        cur.col = save.2;
    }
    Ok(())
}

fn parse_slot_ref(cur: &mut StringCursor) -> Result<usize, ParseError> {
    let ch = cur.peek();
    if ch != Some(SLOT_MARKER) {
        if let Some(c) = ch {
            if let Some(name) = homoglyph(c) {
                return Err(ParseError::at("L020_INVALID_SLOT_MARKER", format!("Slot marker is not ※ (got {name})"), cur.line, cur.col));
            }
        }
        return Err(ParseError::at("L020_INVALID_SLOT_MARKER", format!("Expected ※ at start of slot ref, got {ch:?}"), cur.line, cur.col));
    }
    cur.next();
    let mut raw = String::new();
    while let Some(c) = cur.peek() {
        if c.is_ascii_digit() {
            raw.push(c);
            cur.next();
        } else {
            break;
        }
    }
    if raw.is_empty() {
        return Err(ParseError::at("L021_INVALID_SLOT_INDEX", "Missing integer after ※", cur.line, cur.col));
    }
    if raw.len() > 1 && raw.starts_with('0') {
        return Err(ParseError::at("L023_SLOT_LEADING_ZERO", format!("Slot index has leading zero: ※{raw}"), cur.line, cur.col));
    }
    if raw == "0" {
        return Err(ParseError::at("L022_SLOT_ZERO_FORBIDDEN", "Slot index 0 is forbidden", cur.line, cur.col));
    }
    let index: usize = raw.parse().unwrap_or(SLOT_INDEX_MAX + 1);
    if index > SLOT_INDEX_MAX {
        return Err(ParseError::at("I057_SLOT_INDEX_LIMIT", format!("Slot index {index} exceeds max"), cur.line, cur.col));
    }
    if cur.peek() != Some(':') {
        return Err(ParseError::at("L024_SLOT_SEPARATOR_REQUIRED", format!("Missing ':' after slot index ※{raw}"), cur.line, cur.col));
    }
    cur.next();
    Ok(index)
}

fn resolve_slot_entries(
    entries: &[(usize, Scalar)],
    sym: &V10Symbol,
    line_no: usize,
) -> Result<Vec<V10FieldValue>, ParseError> {
    let mut seen = Vec::new();
    let mut out = Vec::new();
    let mut last = 0;
    for (index, value) in entries {
        if seen.contains(index) {
            return Err(ParseError::at("I051_DUPLICATE_SLOT", format!("slot ※{index} duplicated"), line_no, 0));
        }
        seen.push(*index);
        if *index <= last {
            return Err(ParseError::at("I054_SLOT_OUT_OF_ORDER", format!("slots not in ascending order (※{index} after ※{last})"), line_no, 0));
        }
        last = *index;
        let field = sym.contract.iter().find(|f| f.position == *index).ok_or_else(|| {
            ParseError::at("I052_UNKNOWN_SLOT", format!("slot ※{index} not declared in contract"), line_no, 0)
        })?;
        out.push(V10FieldValue {
            position: *index,
            name: field.name.clone(),
            field_type: field.field_type.clone(),
            required: field.required,
            value: value.clone(),
        });
    }
    for f in &sym.contract {
        if f.required && !seen.contains(&f.position) {
            return Err(ParseError::at("I053_MISSING_REQUIRED_SLOT", format!("missing required slot ※{} ({})", f.position, f.name), line_no, 0));
        }
    }
    Ok(out)
}

fn parse_pipe_cells(source: &str, line_no: usize) -> Result<Vec<Scalar>, ParseError> {
    let chars: Vec<char> = source.chars().collect();
    let mut cells = Vec::new();
    let mut i = 0;
    let n = chars.len();
    while i <= n {
        if i < n && chars[i] == '"' {
            let rest: String = chars[i..].iter().collect();
            let mut cur = StringCursor::new(&rest, line_no, 1);
            let scalar = crate::scalars::parse_string_scalar(&mut cur)?;
            cells.push(scalar);
            i += cur.i;
            while i < n && (chars[i] == ' ' || chars[i] == '\t') {
                i += 1;
            }
            if i >= n {
                return Ok(cells);
            }
            if chars[i] != '|' {
                return Err(ParseError::at("S006_INVALID_ATTRS", "Expected | after quoted cell", line_no, i));
            }
            i += 1;
        } else {
            let mut j = i;
            while j < n && chars[j] != '|' {
                j += 1;
            }
            let raw: String = chars[i..j].iter().collect();
            let trimmed = raw.trim();
            if trimmed.is_empty() && j >= n {
                return Ok(cells);
            }
            cells.push(classify_raw_cell(trimmed));
            i = j;
            if i < n && chars[i] == '|' {
                i += 1;
            } else {
                return Ok(cells);
            }
        }
    }
    Ok(cells)
}

fn homoglyph(ch: char) -> Option<&'static str> {
    match ch {
        '•' => Some("U+2022 BULLET"),
        '·' => Some("U+00B7 MIDDLE DOT"),
        '∙' => Some("U+2219 BULLET OPERATOR"),
        '●' => Some("U+25CF BLACK CIRCLE"),
        _ => None,
    }
}

fn find_matching_brace(line: &str, brace_idx: usize) -> Option<usize> {
    let mut depth = 0;
    for (idx, ch) in line.char_indices().filter(|(i, _)| *i >= brace_idx) {
        match ch {
            '{' => depth += 1,
            '}' => {
                depth -= 1;
                if depth == 0 {
                    return Some(idx);
                }
            }
            _ => {}
        }
    }
    None
}

fn capa_zero(s: &str) -> Option<String> {
    let re = Regex::new(r"^\$0:(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$").unwrap();
    re.captures(s).map(|c| c[1].to_string())
}

fn is_glossary_title(s: &str) -> bool {
    let starts = Regex::new(r"^\$0:\s+").unwrap();
    let decl = Regex::new(r"^\$0:\s*(?:format|enum_|micro_|namespace_|extension_|sigil-map)").unwrap();
    starts.is_match(s) && !decl.is_match(s)
}

fn section_capa(s: &str) -> Option<(u64, String)> {
    let re = Regex::new(r"^\$([1-9][0-9]*):(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)$").unwrap();
    re.captures(s).map(|c| (c[1].parse().unwrap(), c[2].to_string()))
}

fn section_number(s: &str) -> Option<(u64, Option<String>)> {
    if s.starts_with("$0:") {
        return None;
    }
    let re = Regex::new(r"^\$([0-9]+)(?:\s+(.*))?$").unwrap();
    re.captures(s).map(|c| (c[1].parse().unwrap(), c.get(2).map(|m| m.as_str().to_string())))
}

fn section_title(s: &str) -> Option<(u64, String)> {
    let re = Regex::new(r"^\$([1-9][0-9]*):\s+(.*)$").unwrap();
    re.captures(s).map(|c| (c[1].parse().unwrap(), c[2].to_string()))
}

fn split_capa(title: &str) -> (String, Option<String>) {
    let re = Regex::new(r":(KERNEL|CORE|KNOW|DATA|FLOW|CACHE)\s*$").unwrap();
    if let Some(c) = re.captures(title) {
        let start = c.get(0).unwrap().start();
        (title[..start].trim().to_string(), Some(c[1].to_string()))
    } else {
        (title.trim().to_string(), None)
    }
}

fn is_glossary_decl(s: &str) -> bool {
    let re = Regex::new(r"^(([a-z][a-z0-9_.-]*)::)?(!|[A-Z][A-Z0-9_]*):").unwrap();
    re.is_match(s)
}

// ---------------------------------------------------------------------------
// C14N 1.0
// ---------------------------------------------------------------------------

fn nfc_scalar(s: &Scalar) -> Scalar {
    match &s.value {
        ScalarValue::String(v) => {
            let n = to_nfc(v);
            Scalar::string(n.clone(), emit_string_literal(&n))
        }
        ScalarValue::Atom(v) => Scalar::atom(to_nfc(v)),
        ScalarValue::List(items) => Scalar::list(items.iter().map(nfc_scalar).collect()),
        _ => s.clone(),
    }
}

fn pre_normalize(doc: &mut V10Doc) {
    if let Some(f) = doc.glossary.format.as_mut() {
        f.attrs = f.attrs.iter().map(|(k, v)| (k.clone(), nfc_scalar(v))).collect();
    }
    for e in &mut doc.glossary.enums {
        e.values = e.values.iter().map(|v| to_nfc(v)).collect();
    }
    for m in &mut doc.glossary.micros {
        m.expand = to_nfc(&m.expand);
    }
    for ns in &mut doc.glossary.namespaces {
        ns.attrs = ns.attrs.iter().map(|(k, v)| (k.clone(), nfc_scalar(v))).collect();
    }
    for ext in &mut doc.glossary.extensions {
        ext.attrs = ext.attrs.iter().map(|(k, v)| (k.clone(), nfc_scalar(v))).collect();
    }
    for md in &mut doc.glossary.meta {
        md.attrs = md.attrs.iter().map(|(k, v)| (k.clone(), nfc_scalar(v))).collect();
    }
    for sym in &mut doc.glossary.symbols {
        sym.attrs = sym.attrs.iter().map(|(k, v)| (k.clone(), nfc_scalar(v))).collect();
        sym.desc = to_nfc(&sym.desc);
    }
    let micro: Vec<(String, String)> = doc.glossary.micros.iter().map(|m| (m.token.clone(), m.expand.clone())).collect();
    for sec in &mut doc.sections {
        for idea in &mut sec.ideas {
            match &mut idea.payload {
                V10Payload::Attrs(attrs) => {
                    *attrs = attrs.iter().map(|(k, v)| (k.clone(), nfc_scalar(v))).collect();
                }
                V10Payload::Positional(cells) => {
                    *cells = cells.iter().map(nfc_scalar).collect();
                }
                V10Payload::Slots(fvs) => {
                    for fv in fvs {
                        if let ScalarValue::Atom(a) = &fv.value.value {
                            if let Some((_, ex)) = micro.iter().find(|(t, _)| t == a) {
                                fv.value = Scalar::atom(ex.clone());
                            }
                        }
                        fv.value = nfc_scalar(&fv.value);
                    }
                }
                V10Payload::Body(text) => {
                    *text = to_nfc(text);
                }
                _ => {}
            }
        }
        if let Some(t) = sec.title.as_mut() {
            *t = to_nfc(t);
        }
    }
}

fn sort_keys_canonical(attrs: &Attrs, order: &[&str]) -> Attrs {
    let mut out = Vec::new();
    let mut used = Vec::new();
    for key in order {
        if let Some((k, v)) = attrs.iter().find(|(k, _)| k == key) {
            out.push((k.clone(), v.clone()));
            used.push((*key).to_string());
        }
    }
    let mut extras: Vec<(String, Scalar)> = attrs.iter().filter(|(k, _)| !used.contains(k)).cloned().collect();
    extras.sort_by(|a, b| to_nfc(&a.0).cmp(&to_nfc(&b.0)));
    out.extend(extras);
    out
}

fn is_atom_safe_bare(s: &str) -> bool {
    !s.is_empty() && !s.chars().any(|c| c.is_whitespace() || "[]{} ,\"|".contains(c))
}

fn emit_scalar_attrs(v: &Scalar, is_focus_text: bool, is_text_field: bool) -> String {
    match &v.value {
        ScalarValue::String(s) => {
            if is_focus_text {
                v.lexeme.clone()
            } else if is_text_field && is_atom_safe_bare(s) && crate::scalars::is_atom_lexeme(s) {
                s.clone()
            } else {
                v.lexeme.clone()
            }
        }
        ScalarValue::Atom(s) => {
            if is_atom_safe_bare(s) {
                s.clone()
            } else {
                emit_string_literal(s)
            }
        }
        _ => v.lexeme.clone(),
    }
}

fn emit_glossary_attrs(attrs: &Attrs) -> String {
    format!("{{{}}}", attrs.iter().map(|(k, v)| format!("{k}:{}", v.lexeme)).collect::<Vec<_>>().join(","))
}

pub fn canonicalize_v10(doc: &mut V10Doc) -> String {
    pre_normalize(doc);
    let mut lines: Vec<String> = Vec::new();
    lines.push(match &doc.glossary.capa {
        Some(c) => format!("$0:{c}"),
        None => "$0".to_string(),
    });
    if let Some(f) = &doc.glossary.format {
        lines.push(format!("$0:format{}", emit_glossary_attrs(&sort_keys_canonical(&f.attrs, &["cortex", "encoding", "language", "type"]))));
    }
    let any_slots = doc.glossary.symbols.iter().any(|s| s.encoding.as_deref() == Some("slots"));
    if any_slots {
        if let Some(sm) = &doc.glossary.sigil_map {
            let attrs: Attrs = vec![
                ("marker".into(), Scalar::string(sm.marker.clone(), emit_string_literal(&sm.marker))),
                ("codepoint".into(), Scalar::string(sm.codepoint.clone(), emit_string_literal(&sm.codepoint))),
                ("base".into(), Scalar::integer(sm.base.to_string())),
                ("syntax".into(), Scalar::string(sm.syntax.clone(), emit_string_literal(&sm.syntax))),
                ("order".into(), Scalar::string(sm.order.clone(), emit_string_literal(&sm.order))),
            ];
            lines.push(format!("$0:sigil-map{}", emit_glossary_attrs(&sort_keys_canonical(&attrs, &["marker", "codepoint", "base", "syntax", "order"]))));
        }
    }
    let mut enums = doc.glossary.enums.clone();
    enums.sort_by(|a, b| to_nfc(&a.name).cmp(&to_nfc(&b.name)));
    for e in &enums {
        let values = e.values.join("|");
        let attrs: Attrs = vec![("values".into(), Scalar::string(values.clone(), emit_string_literal(&values)))];
        lines.push(format!("$0:enum_{}{}", e.name, emit_glossary_attrs(&sort_keys_canonical(&attrs, &["values"]))));
    }
    let mut micros = doc.glossary.micros.clone();
    micros.sort_by(|a, b| to_nfc(&a.token).cmp(&to_nfc(&b.token)));
    for m in &micros {
        let v = if crate::scalars::is_atom_lexeme(&m.expand) { Scalar::atom(m.expand.clone()) } else { Scalar::string(m.expand.clone(), emit_string_literal(&m.expand)) };
        let attrs: Attrs = vec![("expand".into(), v)];
        lines.push(format!("$0:micro_{}{}", m.token, emit_glossary_attrs(&sort_keys_canonical(&attrs, &["expand"]))));
    }
    let mut nss = doc.glossary.namespaces.clone();
    nss.sort_by(|a, b| to_nfc(&a.alias).cmp(&to_nfc(&b.alias)));
    for ns in &nss {
        lines.push(format!("$0:namespace_{}{}", ns.alias, emit_glossary_attrs(&sort_keys_canonical(&ns.attrs, &["id", "uri", "version", "required", "desc"]))));
    }
    let mut exts = doc.glossary.extensions.clone();
    exts.sort_by(|a, b| to_nfc(&a.name).cmp(&to_nfc(&b.name)));
    for e in &exts {
        lines.push(format!("$0:extension_{}{}", e.name, emit_glossary_attrs(&sort_keys_canonical(&e.attrs, &["namespace", "id", "version", "required", "desc"]))));
    }
    let mut meta = doc.glossary.meta.clone();
    meta.sort_by(|a, b| to_nfc(&a.name).cmp(&to_nfc(&b.name)));
    for m in &meta {
        let mut attrs = m.attrs.clone();
        attrs.sort_by(|a, b| to_nfc(&a.0).cmp(&to_nfc(&b.0)));
        let mut line = format!("$0:{}{}", m.name, emit_glossary_attrs(&attrs));
        if let Some(c) = &m.capa {
            line.push_str(&format!(":{c}"));
        }
        lines.push(line);
    }
    let mut syms = doc.glossary.symbols.clone();
    syms.sort_by(|a, b| {
        let ns_a = a.namespace.clone().unwrap_or_default();
        let ns_b = b.namespace.clone().unwrap_or_default();
        to_nfc(&ns_a).cmp(&to_nfc(&ns_b)).then_with(|| to_nfc(&a.sigil).cmp(&to_nfc(&b.sigil))).then_with(|| to_nfc(&a.label).cmp(&to_nfc(&b.label)))
    });
    for s in &syms {
        lines.push(format!("{}:{}{}", s.qualified(), s.label, emit_glossary_attrs(&sort_keys_canonical(&s.attrs, &["type", "encoding", "weight", "slots", "focus", "schema", "desc", "open", "namespace", "version"]))));
    }
    for sec in &doc.sections {
        match (&sec.title, &sec.capa) {
            (None, None) => lines.push(format!("${}", sec.id)),
            (None, Some(c)) => lines.push(format!("${}:{c}", sec.id)),
            (Some(t), None) => lines.push(format!("${}: {t}", sec.id)),
            (Some(t), Some(c)) => lines.push(format!("${}: {t}:{c}", sec.id)),
        }
        for idea in &sec.ideas {
            lines.push(idea_canonical_v10(idea, doc));
        }
    }
    format!("{}\n", lines.join("\n"))
}

fn idea_canonical_v10(idea: &V10Idea, doc: &V10Doc) -> String {
    let head = format!("{}:{}", idea.qualified_symbol(), idea.name);
    let sym = doc.glossary.symbols.iter().find(|s| s.sigil == idea.symbol && s.namespace == idea.namespace);
    match &idea.payload {
        V10Payload::Slots(fvs) => {
            let sym = sym.expect("undeclared symbol");
            let focus_pos = sym.contract.iter().find(|f| f.name == sym.focus).map(|f| f.position);
            let parts: Vec<String> = fvs
                .iter()
                .map(|fv| {
                    let ftype = sym.contract.iter().find(|f| f.position == fv.position).map(|f| f.field_type.as_str()).unwrap_or("any");
                    let is_text = ftype == "text";
                    let is_focus_text = Some(fv.position) == focus_pos && ftype == "text";
                    format!("※{}:{}", fv.position, emit_scalar_attrs(&fv.value, is_focus_text, is_text))
                })
                .collect();
            format!("{head}{{{}}}", parts.join(","))
        }
        V10Payload::Attrs(attrs) => {
            let sym = sym.expect("undeclared symbol");
            let parts: Vec<String> = attrs
                .iter()
                .map(|(k, v)| {
                    let ftype = sym.contract.iter().find(|f| &f.name == k).map(|f| f.field_type.as_str()).unwrap_or("any");
                    format!("{k}:{}", emit_scalar_attrs(v, k == &sym.focus && ftype == "text", ftype == "text"))
                })
                .collect();
            format!("{head}{{{}}}", parts.join(","))
        }
        V10Payload::Positional(cells) => format!("{head}|{}", cells.iter().map(|c| c.lexeme.as_str()).collect::<Vec<_>>().join("|")),
        V10Payload::Body(text) => {
            let text = to_nfc(text);
            if text.contains('\n') {
                format!("{head}{{\n{text}\n}}")
            } else {
                format!("{head}{{{text}}}")
            }
        }
        V10Payload::Block(text) => format!("{head}{{\n{text}\n}}"),
        V10Payload::MultilinePending => head,
    }
}

// ---------------------------------------------------------------------------
// HCORTEX 1.0 render
// ---------------------------------------------------------------------------

pub fn render_hcortex10(doc: &V10Doc) -> String {
    let version = if doc.cortex_version == "0.2" { "0.2" } else { "1.0" };
    let mut out: Vec<String> = Vec::new();
    out.push(format!("<!-- HCORTEX v={version} t=canonical k=corpus -->"));
    out.push(String::new());
    out.push("<!-- glossary -->".into());
    out.push(render_glossary(doc));
    out.push("<!-- /glossary -->".into());
    out.push(String::new());
    for sec in &doc.sections {
        let title = sec.title.clone().unwrap_or_else(|| format!("Sección {}", sec.id));
        out.push(format!("## §{}: {}", sec.id, title));
        out.push(String::new());
        let capa = sec.capa.as_ref().map(|c| format!(" capa:{c}")).unwrap_or_default();
        out.push(format!("<!-- schema:{}{} -->", sec.id, capa));
        for idea in &sec.ideas {
            let sym = doc.glossary.symbols.iter().find(|s| s.sigil == idea.symbol && s.namespace == idea.namespace);
            out.extend(render_idea(idea, sym));
            out.push(String::new());
        }
        out.push(format!("<!-- /schema:{} -->", sec.id));
        out.push(String::new());
    }
    format!("{}\n", out.join("\n"))
}

fn render_glossary(doc: &V10Doc) -> String {
    let gl = &doc.glossary;
    let mut lines: Vec<String> = Vec::new();
    if let Some(c) = &gl.capa {
        lines.push(format!("$0:{c}"));
    }
    if let Some(f) = &gl.format {
        lines.push(format!("$0:format{{{}}}", f.attrs.iter().map(|(k, v)| format!("{k}:{}", v.lexeme)).collect::<Vec<_>>().join(",")));
    }
    for e in &gl.enums {
        lines.push(format!("$0:enum_{}{{values:\"{}\"}}", e.name, e.values.join("|")));
    }
    for m in &gl.micros {
        let mut expand = m.expand.clone();
        if expand.starts_with('"') && expand.ends_with('"') && expand.len() >= 2 {
            expand = expand[1..expand.len() - 1].to_string();
        }
        if expand.contains(' ') || expand.is_empty() {
            lines.push(format!("$0:micro_{}{{expand:\"{expand}\"}}", m.token));
        } else {
            lines.push(format!("$0:micro_{}{{expand:{expand}}}", m.token));
        }
    }
    for ns in &gl.namespaces {
        lines.push(format!("$0:namespace_{}{{{}}}", ns.alias, ns.attrs.iter().map(|(k, v)| format!("{k}:{}", v.lexeme)).collect::<Vec<_>>().join(",")));
    }
    for ext in &gl.extensions {
        lines.push(format!("$0:extension_{}{{{}}}", ext.name, ext.attrs.iter().map(|(k, v)| format!("{k}:{}", v.lexeme)).collect::<Vec<_>>().join(",")));
    }
    for md in &gl.meta {
        let mut line = format!("$0:{}{{{}}}", md.name, md.attrs.iter().map(|(k, v)| format!("{k}:{}", v.lexeme)).collect::<Vec<_>>().join(","));
        if let Some(c) = &md.capa {
            line.push_str(&format!(":{c}"));
        }
        lines.push(line);
    }
    let any_slots = gl.symbols.iter().any(|s| s.encoding.as_deref() == Some("slots"));
    if any_slots {
        if let Some(sm) = &gl.sigil_map {
            let cp = sm.codepoint.trim_start_matches("U+");
            let cp = format!("{cp:0>4}");
            lines.push(format!("$0:sigil-map{{marker:\"{}\",codepoint:\"U+{}\",base:{},syntax:\"{}\",order:\"{}\"}}", sm.marker, cp, sm.base, sm.syntax, sm.order));
        }
    }
    for s in &gl.symbols {
        let mut parts: Vec<String> = Vec::new();
        let mut seen: Vec<String> = Vec::new();
        for (k, v) in &s.attrs {
            if k == "contract" || seen.contains(k) {
                continue;
            }
            seen.push(k.clone());
            parts.push(format!("{k}:{}", v.lexeme));
        }
        if let Some((_, v)) = s.attrs.iter().find(|(k, _)| k == "open") {
            if !seen.contains(&"open".to_string()) {
                parts.push(format!("open:{}", v.lexeme));
            }
        }
        lines.push(format!("{}:{}{{{}}}", s.qualified(), s.label, parts.join(",")));
    }
    format!("{}\n", lines.join("\n"))
}

fn render_idea(idea: &V10Idea, sym: Option<&V10Symbol>) -> Vec<String> {
    let mut out = vec![format!("### {}:{}", idea.qualified_symbol(), idea.name)];
    match &idea.payload {
        V10Payload::Slots(fvs) => {
            if let Some(sym) = sym {
                let headers: Vec<String> = sym.contract.iter().map(|f| f.name.clone()).collect();
                let row: Vec<String> = sym
                    .contract
                    .iter()
                    .map(|f| fvs.iter().find(|fv| fv.position == f.position).map(|fv| fv.value.lexeme.clone()).unwrap_or_default())
                    .collect();
                out.extend(render_table(&headers, &row));
            }
        }
        V10Payload::Attrs(attrs) => {
            let (headers, row) = if let Some(sym) = sym.filter(|s| s.encoding.as_deref() == Some("slots")) {
                let headers: Vec<String> = sym.contract.iter().map(|f| f.name.clone()).collect();
                let row: Vec<String> = sym
                    .contract
                    .iter()
                    .map(|f| attrs.iter().find(|(k, _)| k == &f.name).map(|(_, v)| v.lexeme.clone()).unwrap_or_default())
                    .collect();
                (headers, row)
            } else {
                let headers: Vec<String> = attrs.iter().map(|(k, _)| k.clone()).collect();
                let row: Vec<String> = attrs.iter().map(|(_, v)| v.lexeme.clone()).collect();
                (headers, row)
            };
            out.extend(render_table(&headers, &row));
        }
        V10Payload::Positional(cells) => {
            let headers: Vec<String> = match sym {
                Some(sym) => (0..cells.len())
                    .map(|i| sym.contract.get(i).map(|f| f.name.clone()).unwrap_or_else(|| format!("c{}", i + 1)))
                    .collect(),
                None => Vec::new(),
            };
            let row: Vec<String> = cells.iter().map(|c| c.lexeme.clone()).collect();
            out.extend(render_table(&headers, &row));
        }
        V10Payload::Body(text) => out.push(text.clone()),
        V10Payload::Block(text) => {
            out.push("```".into());
            out.push(text.clone());
            out.push("```".into());
        }
        V10Payload::MultilinePending => {}
    }
    out
}

fn render_table(headers: &[String], row: &[String]) -> Vec<String> {
    vec![
        format!("| {} |", headers.join(" | ")),
        format!("|{}", "---|".repeat(headers.len())),
        format!("| {} |", row.join(" | ")),
    ]
}

// ---------------------------------------------------------------------------
// HCORTEX 1.0 compile
// ---------------------------------------------------------------------------

fn fence_mask(lines: &[String]) -> Vec<bool> {
    let mut mask = vec![false; lines.len()];
    let mut i = 0;
    while i < lines.len() {
        if lines[i].trim_start().starts_with("```") {
            let mut j = i + 1;
            while j < lines.len() && !lines[j].trim_start().starts_with("```") {
                j += 1;
            }
            if j < lines.len() {
                for k in i..=j {
                    mask[k] = true;
                }
                i = j + 1;
                continue;
            }
        }
        i += 1;
    }
    mask
}

pub fn compile_hcortex10(text: &str) -> Result<V10Doc, ParseError> {
    if text.starts_with('\u{feff}') {
        return Err(ParseError::new("H490", "BOM forbidden"));
    }
    let text = text.replace("\r\n", "\n").replace('\r', "\n");
    if Regex::new(r"<!--\s*(cortex-ast:|base64:|payload-shadow:|shadow:|ast:|internal:)").unwrap().is_match(&text) {
        return Err(ParseError::new("H481_HIDDEN_COPY", "HCORTEX contains hidden CORTEX/AST copy"));
    }
    let envelope = Regex::new(r"<!--\s*HCORTEX\s+v=([0-9.]+)\s+t=(\w+)(?:\s+k=(\w+))?\s*-->").unwrap();
    let caps = envelope.captures(&text).ok_or_else(|| ParseError::new("H401_MISSING_ENVELOPE", "Missing or malformed HCORTEX envelope"))?;
    let version = caps[1].to_string();
    if version != "0.2" && version != "1.0" {
        return Err(ParseError::new("H401_UNSUPPORTED_HCORTEX_VERSION", format!("Unsupported HCORTEX version: {version}")));
    }
    let glossary_re = Regex::new(r"(?s)<!--\s*glossary\s*-->\n(.*?)\n<!--\s*/glossary\s*-->").unwrap();
    let gm = glossary_re.captures(&text).ok_or_else(|| ParseError::new("H403_MISSING_GLOSSARY_BLOCK", "Missing glossary block"))?;
    let mut doc = parse_v10(&format!("{}\n", gm[1].trim()), &version)?;
    doc.cortex_version = version;
    let lines: Vec<String> = text.split('\n').map(String::from).collect();
    let fenced = fence_mask(&lines);
    let heading_re = Regex::new(r"^##\s*§(\d+):\s*(.*?)\s*$").unwrap();
    let open_re = Regex::new(r"^<!--\s*schema:(\d+)(?:\s+capa:(\w+))?\s*-->$").unwrap();
    let close_re = Regex::new(r"^<!--\s*/schema:\d+\s*-->$").unwrap();
    let mut i = 0;
    while i < lines.len() {
        if !fenced[i] {
            if let Some(m) = heading_re.captures(&lines[i]) {
                if i + 2 < lines.len() && lines[i + 1].trim().is_empty() {
                    if let Some(sm) = open_re.captures(&lines[i + 2]) {
                        let mut j = i + 3;
                        while j < lines.len() {
                            if !fenced[j] && close_re.is_match(&lines[j]) {
                                break;
                            }
                            j += 1;
                        }
                        if j < lines.len() {
                            let id: u64 = m[1].parse().unwrap();
                            let raw_title = m[2].trim().to_string();
                            let title = if raw_title == format!("Sección {id}") { None } else { Some(raw_title) };
                            let capa = sm.get(2).map(|c| c.as_str().to_string());
                            let body = lines[i + 3..j].join("\n");
                            let ideas = if body.trim().is_empty() { Vec::new() } else { parse_ideas_v10(&body, id, &doc)? };
                            doc.sections.push(V10Section { id, title, ideas, capa });
                            i = j + 1;
                            continue;
                        }
                    }
                }
            }
        }
        i += 1;
    }
    Ok(doc)
}

fn parse_ideas_v10(body: &str, section_id: u64, doc: &V10Doc) -> Result<Vec<V10Idea>, ParseError> {
    let lines: Vec<String> = body.split('\n').map(String::from).collect();
    let fenced = fence_mask(&lines);
    let marker_re = Regex::new(r"^### ([!]?(?:\w+::)?[!\w]+):([\w_-]+)\s*$").unwrap();
    let mut markers: Vec<(usize, String, String)> = Vec::new();
    for (i, line) in lines.iter().enumerate() {
        if fenced[i] {
            continue;
        }
        if let Some(m) = marker_re.captures(line) {
            markers.push((i, m[1].to_string(), m[2].to_string()));
        }
    }
    let mut ideas = Vec::new();
    for (idx, (start, qualified, name)) in markers.iter().enumerate() {
        let end = markers.get(idx + 1).map(|m| m.0).unwrap_or(lines.len());
        let rest = lines[start + 1..end].join("\n").trim().to_string();
        let (ns, sigil) = match qualified.split_once("::") {
            Some((ns, s)) => (Some(ns.to_string()), s.to_string()),
            None => (None, qualified.clone()),
        };
        let sym = doc
            .glossary
            .symbols
            .iter()
            .find(|s| s.sigil == sigil && s.namespace == ns)
            .or_else(|| doc.glossary.symbols.iter().find(|s| s.sigil == sigil && s.namespace.is_none()));
        let shape = sym.map(|s| s.shape.clone()).unwrap_or_else(|| "attrs".into());
        let encoding = sym.and_then(|s| s.encoding.clone());
        let table = parse_table_rows(&rest);
        let idea = if let Some((rows, order)) = table {
            if encoding.as_deref() == Some("slots") && sym.is_some() {
                let sym = sym.unwrap();
                let fvs: Vec<V10FieldValue> = sym
                    .contract
                    .iter()
                    .filter_map(|f| {
                        let col = rows.iter().find(|(k, _)| k == &f.name).map(|(_, v)| v.clone()).unwrap_or_default();
                        if col.is_empty() {
                            None
                        } else {
                            Some(V10FieldValue { position: f.position, name: f.name.clone(), field_type: f.field_type.clone(), required: f.required, value: make_scalar_cell(&col) })
                        }
                    })
                    .collect();
                if fvs.is_empty() {
                    None
                } else {
                    Some(V10Idea { section: section_id, namespace: ns.clone(), symbol: sigil.clone(), name: name.clone(), shape: "attrs".into(), payload: V10Payload::Slots(fvs) })
                }
            } else if shape == "cuerpo" {
                Some(V10Idea { section: section_id, namespace: ns.clone(), symbol: sigil.clone(), name: name.clone(), shape, payload: V10Payload::Body(rest.clone()) })
            } else if shape == "bloque" {
                Some(V10Idea { section: section_id, namespace: ns.clone(), symbol: sigil.clone(), name: name.clone(), shape, payload: V10Payload::Block(extract_fence(&rest)) })
            } else if shape == "attrs-pos" || shape == "relacion" {
                let sym = sym.unwrap();
                let mut cells = Vec::new();
                for f in &sym.contract {
                    let val = rows.iter().find(|(k, _)| k == &f.name).map(|(_, v)| v.clone()).unwrap_or_default();
                    if val.is_empty() && !f.required {
                        break;
                    }
                    cells.push(make_scalar_cell(&val));
                }
                Some(V10Idea { section: section_id, namespace: ns.clone(), symbol: sigil.clone(), name: name.clone(), shape, payload: V10Payload::Positional(cells) })
            } else {
                let attrs: Attrs = order
                    .iter()
                    .map(|h| (h.clone(), make_scalar_cell(rows.iter().find(|(k, _)| k == h).map(|(_, v)| v.clone()).unwrap_or_default().as_str())))
                    .collect();
                Some(V10Idea { section: section_id, namespace: ns.clone(), symbol: sigil.clone(), name: name.clone(), shape: "attrs".into(), payload: V10Payload::Attrs(attrs) })
            }
        } else if shape == "cuerpo" {
            Some(V10Idea { section: section_id, namespace: ns.clone(), symbol: sigil.clone(), name: name.clone(), shape, payload: V10Payload::Body(rest.clone()) })
        } else if shape == "bloque" {
            Some(V10Idea { section: section_id, namespace: ns.clone(), symbol: sigil.clone(), name: name.clone(), shape, payload: V10Payload::Block(extract_fence(&rest)) })
        } else {
            Some(V10Idea { section: section_id, namespace: ns.clone(), symbol: sigil.clone(), name: name.clone(), shape, payload: V10Payload::Attrs(Vec::new()) })
        };
        if let Some(idea) = idea {
            ideas.push(idea);
        }
    }
    Ok(ideas)
}

fn extract_fence(rest: &str) -> String {
    let re = Regex::new(r"(?s)```\s*\n(.*?)```").unwrap();
    re.captures(rest).map(|m| m[1].trim().to_string()).unwrap_or_else(|| rest.to_string())
}

fn parse_table_rows(text: &str) -> Option<(Vec<(String, String)>, Vec<String>)> {
    let lines: Vec<String> = text.split('\n').map(|l| l.trim().to_string()).filter(|l| !l.is_empty()).collect();
    let table: Vec<&String> = lines.iter().filter(|l| l.starts_with('|') && l.ends_with('|')).collect();
    if table.len() < 2 {
        return None;
    }
    let headers = split_table_row(table[0]);
    let mut data: Option<Vec<String>> = None;
    for line in &table[1..] {
        let cells = split_table_row(line);
        let sep = cells.iter().all(|c| c.is_empty() || c.chars().all(|ch| ch == '-' || ch == ':'));
        if sep {
            continue;
        }
        data = Some(cells);
        break;
    }
    let data = data?;
    let rows: Vec<(String, String)> = headers
        .iter()
        .enumerate()
        .map(|(i, h)| (h.clone(), data.get(i).cloned().unwrap_or_default()))
        .collect();
    Some((rows, headers))
}

fn split_table_row(line: &str) -> Vec<String> {
    let mut s = line.trim();
    if s.starts_with('|') {
        s = &s[1..];
    }
    if s.ends_with('|') {
        s = &s[..s.len() - 1];
    }
    let mut cells = Vec::new();
    let mut buf = String::new();
    let mut in_quotes = false;
    let mut escaped = false;
    for ch in s.chars() {
        if escaped {
            buf.push(ch);
            escaped = false;
        } else if ch == '\\' && in_quotes {
            buf.push(ch);
            escaped = true;
        } else if ch == '"' {
            in_quotes = !in_quotes;
            buf.push(ch);
        } else if ch == '|' && !in_quotes {
            cells.push(buf.trim().to_string());
            buf.clear();
        } else {
            buf.push(ch);
        }
    }
    cells.push(buf.trim().to_string());
    cells
}

fn make_scalar_cell(lex: &str) -> Scalar {
    let lex = lex.trim();
    if lex.is_empty() {
        return Scalar::null();
    }
    if lex.starts_with('"') && lex.ends_with('"') && lex.len() >= 2 {
        let mut cur = StringCursor::new(lex, 1, 1);
        if let Ok(sc) = crate::scalars::parse_string_scalar(&mut cur) {
            return sc;
        }
    }
    if lex == "true" {
        return Scalar::boolean(true);
    }
    if lex == "false" {
        return Scalar::boolean(false);
    }
    if lex == "null" {
        return Scalar::null();
    }
    if lex.starts_with('[') && lex.ends_with(']') {
        let inner = lex[1..lex.len() - 1].trim();
        if inner.is_empty() {
            return Scalar::list(Vec::new());
        }
        let items = inner.split(',').map(make_scalar_cell).collect();
        return Scalar::list(items);
    }
    classify_raw_cell(lex)
}

#[cfg(test)]
mod v10_oracle_tests {
    use super::*;
    use std::fs;
    use std::path::Path;

    #[test]
    fn v10_oracle_parity() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap();
        let mut targets: Vec<(String, String, String)> = Vec::new();
        for (dir, version) in [("conformance/1.0/valid", "1.0"), ("conformance/slots/valid", "0.2")] {
            let mut files: Vec<_> = fs::read_dir(root.join(dir))
                .unwrap()
                .filter_map(|e| e.ok().map(|e| e.path()))
                .filter(|p| p.extension().map(|x| x == "cortex").unwrap_or(false))
                .collect();
            files.sort();
            for f in files {
                let key = format!(
                    "{}__{}",
                    f.parent().unwrap().file_name().unwrap().to_string_lossy(),
                    f.file_stem().unwrap().to_string_lossy()
                );
                targets.push((f.to_string_lossy().to_string(), version.to_string(), key));
            }
        }
        targets.push(("skill/codec-cortex.skill.md".into(), "1.0".into(), "skill__codec-cortex.skill".into()));

        let mut c14n_ok = 0;
        let mut render_ok = 0;
        let mut rt_ok = 0;
        for (file, version, key) in &targets {
            let source = fs::read_to_string(root.join(file)).unwrap();
            let want_c = fs::read_to_string(format!("/tmp/oracle/c14n/{key}.txt")).unwrap();
            let want_r = fs::read_to_string(format!("/tmp/oracle/hcortex/{key}.md")).unwrap();
            let mut doc = parse_v10(&source, version).unwrap_or_else(|e| panic!("{file}: {e:?}"));
            let got_c = canonicalize_v10(&mut doc);
            if got_c == want_c {
                c14n_ok += 1;
            }
            let doc2 = parse_v10(&source, version).unwrap();
            let render = render_hcortex10(&doc2);
            if render == want_r {
                render_ok += 1;
            }
            let mut back = compile_hcortex10(&render).unwrap();
            if canonicalize_v10(&mut back) == want_c {
                rt_ok += 1;
            }
        }
        assert_eq!(c14n_ok, targets.len(), "c14n {c14n_ok}/{}", targets.len());
        assert_eq!(render_ok, targets.len(), "render {render_ok}/{}", targets.len());
        assert_eq!(rt_ok, targets.len(), "roundtrip {rt_ok}/{}", targets.len());
    }
}

// ---------------------------------------------------------------------------
// Dialect dispatch
// ---------------------------------------------------------------------------

use crate::model::Document;

pub enum AnyDoc {
    V01(Document),
    V10(V10Doc),
}

pub fn version_of(source: &str) -> String {
    let re = Regex::new(r#"\$0:format\{[^}]*cortex:"?([0-9.]+)"?"#).unwrap();
    re.captures(source).map(|c| c[1].to_string()).unwrap_or_else(|| "0.1".into())
}

pub fn parse_any(source: &str) -> Result<AnyDoc, ParseError> {
    let version = version_of(source);
    if version == "0.1" {
        crate::parser::parse_cortex(source).map(AnyDoc::V01)
    } else {
        parse_v10(source, &version).map(AnyDoc::V10)
    }
}

pub fn canonicalize_any(doc: &mut AnyDoc) -> String {
    match doc {
        AnyDoc::V01(d) => crate::c14n::canonicalize(d),
        AnyDoc::V10(d) => canonicalize_v10(d),
    }
}

pub fn render_any(doc: &AnyDoc) -> String {
    match doc {
        AnyDoc::V01(d) => crate::hcortex::render_hcortex(d),
        AnyDoc::V10(d) => render_hcortex10(d),
    }
}

pub fn compile_any(text: &str) -> Result<AnyDoc, ParseError> {
    let re = Regex::new(r"<!--\s*HCORTEX\s+v=([0-9.]+)").unwrap();
    if let Some(c) = re.captures(text) {
        if &c[1] == "0.1" {
            let (doc, diags) = crate::hcortex::compile_hcortex(text);
            if let Some(d) = doc {
                if !diags.iter().any(|x| x.severity == "error") {
                    return Ok(AnyDoc::V01(d));
                }
            }
            let message = diags.first().map(|d| format!("{}: {}", d.code, d.message)).unwrap_or_else(|| "HCORTEX compilation failed".into());
            return Err(ParseError::new("H400", message));
        }
    }
    compile_hcortex10(text).map(AnyDoc::V10)
}

pub fn hash_any(doc: &mut AnyDoc) -> String {
    match doc {
        AnyDoc::V01(d) => crate::harness::c14n_hash(crate::c14n::canonicalize(d).as_bytes()),
        AnyDoc::V10(d) => crate::slotparser::hash_slots(canonicalize_v10(d).as_bytes()),
    }
}
