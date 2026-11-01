use std::collections::{HashMap, HashSet};
use std::env;
use std::fs;
use std::io::{self, Read};
use std::path::Path;
use std::process;

use serde::Serialize;

pub mod canonicalize;

// ===== Diagnostic types =====

#[derive(Debug, Clone, Serialize)]
pub struct Span {
    line: usize,
    column: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct Diagnostic {
    code: String,
    severity: String,
    span: Span,
    message: String,
}

// ===== AST types matching ast-schema.json =====

type SourceLine = usize;

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
    NullValue { value: Option<()>, lexeme: String },
    #[serde(rename = "ListValue")]
    ListValue { items: Vec<Scalar>, lexeme: String },
}

#[derive(Debug, Clone, Serialize)]
pub struct AttrPair {
    pub node: String,
    pub key: String,
    pub value: Box<Scalar>,
}

#[derive(Debug, Clone, Serialize)]
pub struct FormatDeclaration {
    pub node: String,
    pub cortex: String,
    pub encoding: String,
    pub attributes: Vec<AttrPair>,
    pub sourceLine: SourceLine,
}

#[derive(Debug, Clone, Serialize)]
pub struct MetaDeclaration {
    pub node: String,
    pub name: String,
    pub attributes: Vec<AttrPair>,
    pub sourceLine: SourceLine,
}

#[derive(Debug, Clone, Serialize)]
pub struct EnumDeclaration {
    pub node: String,
    pub name: String,
    pub values: Vec<String>,
    pub sourceLine: SourceLine,
}

#[derive(Debug, Clone, Serialize)]
pub struct MicroDeclaration {
    pub node: String,
    pub token: String,
    pub expand: String,
    pub sourceLine: SourceLine,
}

#[derive(Debug, Clone, Serialize)]
pub struct NamespaceDeclaration {
    pub node: String,
    pub alias: String,
    pub id: String,
    pub version: Option<String>,
    pub attributes: Vec<AttrPair>,
    pub sourceLine: SourceLine,
}

#[derive(Debug, Clone, Serialize)]
pub struct ExtensionDeclaration {
    pub node: String,
    pub name: String,
    pub namespace: String,
    pub id: String,
    pub version: String,
    pub required: bool,
    pub attributes: Vec<AttrPair>,
    pub sourceLine: SourceLine,
}

#[derive(Debug, Clone, Serialize)]
pub struct ContractField {
    pub name: String,
    #[serde(rename = "type")]
    pub field_type: String,
    pub required: bool,
}

#[derive(Debug, Clone, Serialize)]
pub struct SymbolDefinition {
    pub node: String,
    pub surface: String,
    pub namespace: Option<String>,
    pub qualified: String,
    pub label: String,
    pub shape: String,
    pub weight: String,
    pub focus: String,
    pub description: String,
    pub open: bool,
    pub contract: Vec<ContractField>,
    pub attributes: Vec<AttrPair>,
    pub sourceLine: SourceLine,
}

#[derive(Debug, Clone, Serialize)]
pub struct AttrsPayload {
    pub node: String,
    pub pairs: Vec<AttrPair>,
}

#[derive(Debug, Clone, Serialize)]
pub struct BoundValue {
    pub field: String,
    pub value: Scalar,
}

#[derive(Debug, Clone, Serialize)]
pub struct PositionalPayload {
    pub node: String,
    pub cells: Vec<Scalar>,
    pub bound: Vec<BoundValue>,
}

#[derive(Debug, Clone, Serialize)]
pub struct RelationPayload {
    pub node: String,
    pub cells: Vec<Scalar>,
    pub bound: Vec<BoundValue>,
}

#[derive(Debug, Clone, Serialize)]
#[serde(tag = "node")]
pub enum Payload {
    #[serde(rename = "AttrsPayload")]
    Attrs(AttrsPayload),
    #[serde(rename = "PositionalPayload")]
    Positional(PositionalPayload),
    #[serde(rename = "RelationPayload")]
    Relation(RelationPayload),
    #[serde(rename = "TextPayload")]
    Text(TextPayloadContent),
    #[serde(rename = "BlockPayload")]
    Block(BlockPayloadContent),
}

#[derive(Debug, Clone, Serialize)]
pub struct TextPayloadContent {
    pub text: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct BlockPayloadContent {
    pub text: String,
}

// Used by new structs below
#[derive(Debug, Clone, Serialize)]
pub struct Function {
    pub label: String,
    pub weight: String,
    pub focus: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct Idea {
    pub node: String,
    pub address: String,
    pub section: usize,
    pub symbol: String,
    pub qualifiedSymbol: String,
    pub name: String,
    pub function: Function,
    pub shape: String,
    pub payload: Payload,
    pub sourceLine: SourceLine,
}

#[derive(Debug, Clone, Serialize)]
pub struct Section {
    pub node: String,
    pub id: usize,
    pub title: Option<String>,
    pub ideas: Vec<Idea>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Glossary {
    pub node: String,
    pub format: FormatDeclaration,
    pub meta: Vec<MetaDeclaration>,
    pub enums: Vec<EnumDeclaration>,
    pub micros: Vec<MicroDeclaration>,
    pub namespaces: Vec<NamespaceDeclaration>,
    pub extensions: Vec<ExtensionDeclaration>,
    pub symbols: Vec<SymbolDefinition>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Document {
    pub node: String,
    pub cortexVersion: String,
    pub encoding: String,
    pub glossary: Glossary,
    pub sections: Vec<Section>,
}

// ===== Parser state =====

pub struct Parser {
    pub lines: Vec<String>,
    pub line_count: usize,
    pub current_line: usize,
    pub diagnostics: Vec<Diagnostic>,
    pub glossary: Option<Glossary>,
    pub sections: Vec<Section>,
    pub symbol_map: HashMap<String, SymbolDefinition>,
    pub enum_map: HashMap<String, Vec<String>>,
    pub micro_map: HashMap<String, String>,
    pub namespace_map: HashMap<String, NamespaceDeclaration>,
    pub section_ids: HashSet<usize>,
    pub seen_addresses: HashSet<String>,
    pub has_glossary: bool,
    pub glossary_ended: bool,
    pub current_section: Option<usize>,
}

impl Parser {
    fn new(text: &str) -> Self {
        let lines: Vec<String> = text.lines().map(|l| l.to_string()).collect();
        let line_count = lines.len();
        Parser {
            lines,
            line_count,
            current_line: 0,
            diagnostics: Vec::new(),
            glossary: None,
            sections: Vec::new(),
            symbol_map: HashMap::new(),
            enum_map: HashMap::new(),
            micro_map: HashMap::new(),
            namespace_map: HashMap::new(),
            section_ids: HashSet::new(),
            seen_addresses: HashSet::new(),
            has_glossary: false,
            glossary_ended: false,
            current_section: None,
        }
    }

    fn add_diag(&mut self, code: &str, severity: &str, line: usize, col: usize, msg: String) {
        // Avoid duplicate diagnostics for the same code at the same line
        if self.diagnostics.iter().any(|d| d.code == code && d.span.line == line) {
            return;
        }
        self.diagnostics.push(Diagnostic {
            code: code.to_string(),
            severity: severity.to_string(),
            span: Span { line, column: col },
            message: msg,
        });
    }

    fn peek_line(&self) -> Option<&str> {
        if self.current_line < self.line_count {
            Some(self.lines[self.current_line].as_str())
        } else {
            None
        }
    }

    fn advance(&mut self) {
        self.current_line += 1;
    }

    fn lineno(&self) -> usize {
        self.current_line + 1
    }

    fn at_end(&self) -> bool {
        self.current_line >= self.line_count
    }

    fn is_blank_or_comment(line: &str) -> bool {
        let trimmed = line.trim();
        trimmed.is_empty() || trimmed.starts_with('#')
    }

    pub fn parse_document(&mut self) {
        // Check for BOM
        if !self.lines.is_empty() {
            if self.lines[0].starts_with('\u{feff}') {
                self.add_diag("U001_BOM_FORBIDDEN", "error", 1, 1,
                    "UTF-8 BOM presente. Eliminar BOM.".to_string());
                // Remove BOM from first line
                self.lines[0] = self.lines[0].trim_start_matches('\u{feff}').to_string();
            }
        }

        // Check for empty document
        if self.line_count == 0 || self.lines.iter().all(|l| l.trim().is_empty()) {
            self.add_diag("S001_EMPTY_DOCUMENT", "error", 1, 1,
                "Documento vacío.".to_string());
            // Build minimal fallback AST
            self.glossary = Some(Glossary {
                node: "Glossary".to_string(),
                format: FormatDeclaration {
                    node: "FormatDeclaration".to_string(),
                    cortex: "0.1".to_string(),
                    encoding: "UTF-8".to_string(),
                    attributes: vec![],
                    sourceLine: 0,
                },
                meta: vec![],
                enums: vec![],
                micros: vec![],
                namespaces: vec![],
                extensions: vec![],
                symbols: vec![],
            });
            return;
        }

        // Skip leading blank/comment lines
        while !self.at_end() && Self::is_blank_or_comment(&self.lines[self.current_line]) {
            if self.lines[self.current_line].trim().starts_with('#') {
                // Comments are fine, just skip
            }
            self.advance();
        }

        // Step 1: Must find $0
        if self.at_end() {
            self.add_diag("G001_GLOSSARY_MISSING_OR_NOT_FIRST", "error", 1, 1,
                "$0 ausente o no primero. Ubicar $0 al inicio.".to_string());
            // Build fallback
            self.build_fallback_glossary();
            return;
        }

        // Check content before $0
        let first_line = self.lines[self.current_line].trim();
        if first_line != "$0" {
            self.add_diag("G001_GLOSSARY_MISSING_OR_NOT_FIRST", "error", self.lineno(), 1,
                "$0 ausente o no primero. Ubicar $0 al inicio.".to_string());
            self.build_fallback_glossary();
            // Try to parse remaining anyway
            self.parse_non_glossary_content();
            return;
        }

        // Found $0 header
        self.advance();
        self.has_glossary = true;

        // Parse glossary declarations (meta and symbol declarations)
        self.parse_glossary_declarations();

        // Parse sections
        self.parse_sections();
    }

    fn build_fallback_glossary(&mut self) {
        self.glossary = Some(Glossary {
            node: "Glossary".to_string(),
            format: FormatDeclaration {
                node: "FormatDeclaration".to_string(),
                cortex: "0.1".to_string(),
                encoding: "UTF-8".to_string(),
                attributes: vec![],
                sourceLine: 0,
            },
            meta: vec![],
            enums: vec![],
            micros: vec![],
            namespaces: vec![],
            extensions: vec![],
            symbols: vec![],
        });
    }

    fn parse_non_glossary_content(&mut self) {
        while !self.at_end() {
            let line = self.lines[self.current_line].trim().to_string();
            if Self::is_blank_or_comment(&line) {
                self.advance();
                continue;
            }
            if line.starts_with("$") {
                self.parse_section_header();
            } else {
                // Attempt to parse as idea outside section - error
                self.add_diag("S005_CONTENT_OUTSIDE_SECTION", "error", self.lineno(), 1,
                    "Contenido fuera de sección. Mover bajo $N.".to_string());
                self.advance();
            }
        }
    }

    fn parse_glossary_declarations(&mut self) {
        let mut format_found = false;
        let mut seen_symbols: HashSet<String> = HashSet::new();
        let mut seen_enums: HashSet<String> = HashSet::new();
        let mut seen_micros: HashSet<String> = HashSet::new();
        let mut seen_qualified: HashSet<String> = HashSet::new();
        let mut meta_decls: Vec<MetaDeclaration> = Vec::new();

        while !self.at_end() {
            let line = self.lines[self.current_line].trim().to_string();
            if Self::is_blank_or_comment(&line) {
                self.advance();
                continue;
            }
            // Check if we hit a section header - glossary is over
            if (line.starts_with("$") && !line.starts_with("$0:") && line.len() > 1 && line.as_bytes()[1].is_ascii_digit()) {
                self.glossary_ended = true;
                break;
            }

            // Parse line as glossary declaration
            let lineno = self.lineno();

            // Check for multiline declaration (G003)
            if line.contains('{') && !line.contains('}') && !line.starts_with("$") {
                // Only flag if it's not a section header
                self.add_diag("G003_MULTILINE_GLOSSARY_DECLARATION", "error", lineno, 1,
                    "Declaración de $0 ocupa varias líneas. Compactar a una línea.".to_string());
                // Skip until we find closing brace or next section
                self.advance();
                while !self.at_end() {
                    let l = self.lines[self.current_line].trim().to_string();
                    if l.contains('}') || (l.starts_with("$") && l.len() > 1 && l.as_bytes()[1].is_ascii_digit()) {
                        break;
                    }
                    self.advance();
                }
                if !self.at_end() && self.lines[self.current_line].trim().contains('}') {
                    self.advance();
                }
                continue;
            }

            self.advance();

            // Parse meta-declaration: $0:name{...}
            if line.starts_with("$0:") {
                let after_colon = &line[3..];
                let name_end = after_colon.find(|c| c == '{' || c == ' ');
                let name = if let Some(pos) = name_end {
                    if after_colon.as_bytes().get(pos) == Some(&b'{') {
                        after_colon[..pos].to_string()
                    } else {
                        // space before { is possible
                        let after_space = after_colon[pos..].trim();
                        if after_space.starts_with('{') {
                            after_colon[..pos].to_string()
                        } else {
                            after_colon[..pos].to_string()
                        }
                    }
                } else {
                    // No payload
                    self.add_diag("G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS", "error", lineno, 1,
                        "Declaración no usa attrs. Usar {key:value}.".to_string());
                    continue;
                };

                if name == "format" {
                    if format_found {
                        self.add_diag("G006_DUPLICATE_FORMAT", "error", lineno, 1,
                            "Más de un $0:format. Conservar uno.".to_string());
                    }
                    format_found = true;
                    if let Some(attrs) = Self::parse_attrs_payload(&line, lineno) {
                        let mut cortex_ver = String::new();
                        let mut encoding = String::new();
                        let mut format_attrs = Vec::new();
                        for attr in &attrs {
                            format_attrs.push(AttrPair {
                                node: "AttrPair".to_string(),
                                key: attr.key.clone(),
                                value: Box::new(attr.value.clone()),
                            });
                            if attr.key == "cortex" {
                                if let Scalar::StringValue { ref value, .. } = attr.value {
                                    cortex_ver = value.clone();
                                } else if let Scalar::DecimalValue { ref value, .. } = attr.value {
                                    cortex_ver = value.clone();
                                }
                            } else if attr.key == "encoding" {
                                if let Scalar::AtomValue { ref value, .. } = attr.value {
                                    encoding = value.clone();
                                }
                            }
                        }

                        if cortex_ver.is_empty() {
                            self.add_diag("G010_FORMAT_REQUIRED", "error", lineno, 1,
                                "Falta $0:format. Agregar declaración.".to_string());
                        } else if cortex_ver != "0.1" {
                            self.add_diag("G007_UNSUPPORTED_VERSION", "error", lineno, 1,
                                format!("Versión de cortex no soportada: {}. Usar parser de la versión declarada.", cortex_ver));
                        }

                        if encoding.is_empty() {
                            self.add_diag("G011_ENCODING_REQUIRED", "error", lineno, 1,
                                "Encoding no es UTF-8. Convertir y declarar UTF-8.".to_string());
                        }

                        let format_decl = FormatDeclaration {
                            node: "FormatDeclaration".to_string(),
                            cortex: if cortex_ver.is_empty() { "0.1".to_string() } else { cortex_ver.clone() },
                            encoding: if encoding.is_empty() { "UTF-8".to_string() } else { encoding.clone() },
                            attributes: format_attrs,
                            sourceLine: lineno,
                        };

                        meta_decls.push(MetaDeclaration {
                            node: "MetaDeclaration".to_string(),
                            name: "format".to_string(),
                            attributes: attrs.iter().map(|a| AttrPair {
                                node: "AttrPair".to_string(),
                                key: a.key.clone(),
                                value: Box::new(a.value.clone()),
                            }).collect(),
                            sourceLine: lineno,
                        });

                        if self.glossary.is_none() {
                            self.glossary = Some(Glossary {
                                node: "Glossary".to_string(),
                                format: format_decl,
                                meta: Vec::new(),
                                enums: Vec::new(),
                                micros: Vec::new(),
                                namespaces: Vec::new(),
                                extensions: Vec::new(),
                                symbols: Vec::new(),
                            });
                        } else {
                            // Update format in existing glossary
                            if let Some(ref mut g) = self.glossary {
                                g.format = format_decl;
                            }
                        }
                    }
                } else if name.starts_with("enum_") {
                    let enum_name = name[5..].to_string();
                    if seen_enums.contains(&enum_name) {
                        self.add_diag("G015_DUPLICATE_ENUM", "error", lineno, 1,
                            format!("Enum local repetido: {}.", enum_name));
                    }
                    seen_enums.insert(enum_name.clone());

                    if let Some(attrs) = Self::parse_attrs_payload(&line, lineno) {
                        let values = Self::extract_enum_values(&attrs);
                        if values.is_empty() {
                            self.add_diag("G014_INVALID_ENUM", "error", lineno, 1,
                                "Enum vacío, duplicado o con values inválidos. Corregir values.".to_string());
                        }
                        self.enum_map.insert(enum_name.clone(), values.clone());

                        if let Some(ref mut g) = self.glossary {
                            g.enums.push(EnumDeclaration {
                                node: "EnumDeclaration".to_string(),
                                name: enum_name,
                                values,
                                sourceLine: lineno,
                            });
                        }
                    } else {
                        self.add_diag("G014_INVALID_ENUM", "error", lineno, 1,
                            "Enum inválido.".to_string());
                    }

                    meta_decls.push(MetaDeclaration {
                        node: "MetaDeclaration".to_string(),
                        name: name.clone(),
                        attributes: vec![],
                        sourceLine: lineno,
                    });
                } else if name.starts_with("micro_") {
                    let micro_name = name[6..].to_string();
                    if seen_micros.contains(&micro_name) {
                        self.add_diag("G013_DUPLICATE_MICRO", "error", lineno, 1,
                            format!("Microtoken repetido: {}.", micro_name));
                    }
                    seen_micros.insert(micro_name.clone());

                    if let Some(attrs) = Self::parse_attrs_payload(&line, lineno) {
                        let expand = Self::extract_micro_expand(&attrs);
                        if expand.is_empty() {
                            self.add_diag("G012_INVALID_MICRO", "error", lineno, 1,
                                "Microtoken inválido o sin expansión. Corregir token/expand.".to_string());
                        }
                        self.micro_map.insert(micro_name.clone(), expand.clone());

                        if let Some(ref mut g) = self.glossary {
                            g.micros.push(MicroDeclaration {
                                node: "MicroDeclaration".to_string(),
                                token: micro_name,
                                expand,
                                sourceLine: lineno,
                            });
                        }
                    }

                    meta_decls.push(MetaDeclaration {
                        node: "MetaDeclaration".to_string(),
                        name: name.clone(),
                        attributes: vec![],
                        sourceLine: lineno,
                    });
                } else if name.starts_with("namespace_") {
                    let ns_alias = name[10..].to_string();
                    if let Some(attrs) = Self::parse_attrs_payload(&line, lineno) {
                        let mut ns_id = String::new();
                        let mut ns_version = None;
                        for attr in &attrs {
                            if attr.key == "id" {
                                if let Scalar::StringValue { ref value, .. } = attr.value {
                                    ns_id = value.clone();
                                } else if let Scalar::AtomValue { ref value, .. } = attr.value {
                                    ns_id = value.clone();
                                }
                            }
                            if attr.key == "version" {
                                if let Scalar::StringValue { ref value, .. } = attr.value {
                                    ns_version = Some(value.clone());
                                } else if let Scalar::AtomValue { ref value, .. } = attr.value {
                                    ns_version = Some(value.clone());
                                }
                            }
                        }

                        let ns_decl = NamespaceDeclaration {
                            node: "NamespaceDeclaration".to_string(),
                            alias: ns_alias.clone(),
                            id: ns_id,
                            version: ns_version,
                            attributes: attrs.iter().map(|a| AttrPair {
                                node: "AttrPair".to_string(),
                                key: a.key.clone(),
                                value: Box::new(a.value.clone()),
                            }).collect(),
                            sourceLine: lineno,
                        };

                        self.namespace_map.insert(ns_alias, ns_decl);

                        if let Some(ref mut g) = self.glossary {
                            // We'll add it to namespaces after format is set up
                            // For now just store in the map
                        }

                        meta_decls.push(MetaDeclaration {
                            node: "MetaDeclaration".to_string(),
                            name: name.clone(),
                            attributes: vec![],
                            sourceLine: lineno,
                        });
                    }
                } else if name.starts_with("extension_") {
                    let ext_name = name[10..].to_string();
                    if let Some(attrs) = Self::parse_attrs_payload(&line, lineno) {
                        let mut ns = String::new();
                        let mut id = String::new();
                        let mut version = String::new();
                        let mut required = false;
                        let mut has_ns = false;
                        let mut has_id = false;
                        let mut has_ver = false;

                        for attr in &attrs {
                            match attr.key.as_str() {
                                "namespace" => {
                                    if let Scalar::AtomValue { ref value, .. } = attr.value {
                                        ns = value.clone();
                                        has_ns = true;
                                    }
                                }
                                "id" => {
                                    if let Scalar::AtomValue { ref value, .. } = attr.value {
                                        id = value.clone();
                                        has_id = true;
                                    } else if let Scalar::StringValue { ref value, .. } = attr.value {
                                        id = value.clone();
                                        has_id = true;
                                    }
                                }
                                "version" => {
                                    if let Scalar::AtomValue { ref value, .. } = attr.value {
                                        version = value.clone();
                                        has_ver = true;
                                    } else if let Scalar::StringValue { ref value, .. } = attr.value {
                                        version = value.clone();
                                        has_ver = true;
                                    }
                                }
                                "required" => {
                                    if let Scalar::BooleanValue { ref value, .. } = attr.value {
                                        required = *value;
                                    }
                                }
                                _ => {}
                            }
                        }

                        if !has_ns || !has_id || !has_ver {
                            self.add_diag("X001_INVALID_EXTENSION_DECLARATION", "error", lineno, 1,
                                "Falta namespace, id, version o required. Completar declaración.".to_string());
                        }

                        let ext_decl = ExtensionDeclaration {
                            node: "ExtensionDeclaration".to_string(),
                            name: ext_name,
                            namespace: ns,
                            id,
                            version,
                            required,
                            attributes: attrs.iter().map(|a| AttrPair {
                                node: "AttrPair".to_string(),
                                key: a.key.clone(),
                                value: Box::new(a.value.clone()),
                            }).collect(),
                            sourceLine: lineno,
                        };

                        if let Some(ref mut g) = self.glossary {
                            g.extensions.push(ext_decl);
                        }

                        meta_decls.push(MetaDeclaration {
                            node: "MetaDeclaration".to_string(),
                            name: name.clone(),
                            attributes: vec![],
                            sourceLine: lineno,
                        });
                    }
                } else {
                    // Other meta declaration
                    let attrs = Self::parse_attrs_payload(&line, lineno);
                    meta_decls.push(MetaDeclaration {
                        node: "MetaDeclaration".to_string(),
                        name,
                        attributes: if let Some(a) = attrs {
                            a.iter().map(|ap| AttrPair {
                                node: "AttrPair".to_string(),
                                key: ap.key.clone(),
                                value: Box::new(ap.value.clone()),
                            }).collect()
                        } else {
                            vec![]
                        },
                        sourceLine: lineno,
                    });
                }
                continue;
            }

            // Parse symbol declaration: SIGIL:name{...} or ns::SIGIL:name{...}
            if let Some(sym_def) = self.parse_symbol_declaration(&line, lineno, &mut seen_symbols, &mut seen_qualified) {
                if let Some(ref mut g) = self.glossary {
                    g.symbols.push(sym_def);
                }
            }
        }

        // Check if format was found
        if !format_found {
            self.add_diag("G010_FORMAT_REQUIRED", "error", 1, 1,
                "Falta $0:format. Agregar declaración.".to_string());
        }

        // Add meta declarations to glossary
        if let Some(ref mut g) = self.glossary {
            g.meta = meta_decls;
        }

        // If no glossary was created, create fallback
        if self.glossary.is_none() {
            self.build_fallback_glossary();
        }
    }

    fn parse_symbol_declaration(&mut self, line: &str, lineno: usize,
        seen_symbols: &mut HashSet<String>,
        seen_qualified: &mut HashSet<String>) -> Option<SymbolDefinition> {
        // Extract symbol and label
        // Format: [ns::]SIGIL:label{...}
        // Or: SIGIL:label{...}

        // Find the split point - look for :: first, then the colon after the sigil
        let (symbol_part, after_colon) = if let Some(dcolon) = line.find("::") {
            // ns::SIGIL:label{...}
            let ns_name = &line[..dcolon];
            let rest = &line[dcolon+2..];
            // Now find the colon separating SIGIL from label
            if let Some(colon_pos) = rest.find(':') {
                let sig = &rest[..colon_pos];
                let label_part = &rest[colon_pos+1..];
                // Combine ns::SIGIL as symbol_part
                (format!("{}::{}", ns_name, sig), label_part.to_string())
            } else {
                return None;
            }
        } else if let Some(colon_pos) = line.find(':') {
            if colon_pos == 0 {
                return None; // $0: declarations
            }
            let symbol = line[..colon_pos].to_string();
            let rest = line[colon_pos+1..].to_string();
            (symbol, rest)
        } else {
            return None;
        };

        let (ns, sigil) = if let Some(dcolon) = symbol_part.find("::") {
            let ns_name = symbol_part[..dcolon].to_string();
            let sig = symbol_part[dcolon+2..].to_string();
            (Some(ns_name), sig)
        } else {
            (None, symbol_part)
        };

        // Validate sigil
        if !Self::is_valid_sigil(&sigil) {
            self.add_diag("L001_INVALID_SYMBOL", "error", lineno, 1,
                format!("Sigilo inválido: {}.", sigil));
            return None;
        }

        // Find label end (at '{' or end)
        let label_end = after_colon.find(|c| c == '{' || c == '|').unwrap_or(after_colon.len());
        let label = after_colon[..label_end].trim().to_string();

        // Validate name/label
        if !Self::is_valid_name(&label) {
            self.add_diag("L002_INVALID_NAME", "error", lineno, 1,
                format!("Nombre inválido: {}.", label));
        }

        let qualified = if let Some(ref ns_name) = ns {
            format!("{}::{}", ns_name, sigil)
        } else {
            sigil.clone()
        };

        if seen_qualified.contains(&qualified) {
            self.add_diag("G028_DUPLICATE_QUALIFIED_SYMBOL", "error", lineno, 1,
                format!("Namespace + sigilo declarados más de una vez: {}.", qualified));
        }
        seen_qualified.insert(qualified.clone());

        if seen_symbols.contains(&sigil) {
            self.add_diag("G005_DUPLICATE_SYMBOL", "error", lineno, 1,
                format!("Mismo sigilo declarado dos veces: {}. Consolidar contrato o renombrar alias.", sigil));
        }
        seen_symbols.insert(sigil.clone());

        // Parse payload
        let attrs = Self::parse_attrs_payload(line, lineno);
        let attrs_vec = if let Some(ref a) = attrs { a.clone() } else { vec![] };

        // Extract symbol definition fields
        let shape = Self::get_attr_value(&attrs_vec, "type", "");
        let weight = Self::get_attr_value(&attrs_vec, "weight", "");
        let focus = Self::get_attr_value(&attrs_vec, "focus", "");
        let desc = Self::get_attr_str(&attrs_vec, "desc", "");
        let fields_str = Self::get_attr_str(&attrs_vec, "fields", "");
        let pos_str = Self::get_attr_str(&attrs_vec, "pos", "");
        let open_str = Self::get_attr_value(&attrs_vec, "open", "false");
        let ns_in_attr = Self::get_attr_value(&attrs_vec, "namespace", "");

        // Validate required fields
        if shape.is_empty() {
            self.add_diag("G016_SYMBOL_TYPE_REQUIRED", "error", lineno, 1,
                format!("Sigilo sin type: {}.", sigil));
        }

        if !shape.is_empty() && !["attrs", "attrs-pos", "cuerpo", "bloque", "relacion"].contains(&shape.as_str()) {
            self.add_diag("G017_UNKNOWN_SHAPE", "error", lineno, 1,
                format!("Shape desconocido: {}.", shape));
        }

        if weight.is_empty() {
            self.add_diag("G018_SYMBOL_WEIGHT_REQUIRED", "error", lineno, 1,
                format!("Sigilo sin weight: {}.", sigil));
        } else if !["B", "M", "H"].contains(&weight.as_str()) {
            self.add_diag("G019_INVALID_WEIGHT", "error", lineno, 1,
                format!("Peso desconocido: {}.", weight));
        }

        if desc.is_empty() {
            self.add_diag("G020_SYMBOL_DESCRIPTION_REQUIRED", "error", lineno, 1,
                format!("Sigilo sin desc: {}.", sigil));
        }

        // Validate contract
        let contract = match shape.as_str() {
            "attrs" => {
                if fields_str.is_empty() {
                    self.add_diag("G021_ATTRS_CONTRACT_REQUIRED", "error", lineno, 1,
                        format!("Attrs sin fields: {}.", sigil));
                    vec![]
                } else {
                    Self::parse_contract_fields(&fields_str, lineno, self)
                }
            }
            "attrs-pos" | "relacion" => {
                let contract_str = if !pos_str.is_empty() { pos_str.clone() } else { fields_str.clone() };
                if contract_str.is_empty() {
                    if shape == "attrs-pos" {
                        self.add_diag("G022_POSITIONAL_CONTRACT_REQUIRED", "error", lineno, 1,
                            format!("Attrs-pos sin pos: {}.", sigil));
                    } else {
                        self.add_diag("G022_POSITIONAL_CONTRACT_REQUIRED", "error", lineno, 1,
                            format!("Relacion sin pos: {}.", sigil));
                    }
                    vec![]
                } else {
                    let fields = Self::parse_contract_fields(&contract_str, lineno, self);
                    if shape == "relacion" && fields.len() < 3 {
                        self.add_diag("G023_RELATION_CONTRACT_TOO_SHORT", "error", lineno, 1,
                            format!("Relación con menos de tres fields: {}. Declarar source, predicate, target.", sigil));
                    }
                    fields
                }
            }
            "cuerpo" | "bloque" => {
                vec![]
            }
            _ => vec![],
        };

        // Validate focus
        if !shape.is_empty() && shape != "cuerpo" && shape != "bloque" {
            if focus.is_empty() {
                self.add_diag("G024_FOCUS_REQUIRED", "error", lineno, 1,
                    format!("Shape estructurado sin focus: {}.", sigil));
            } else if !contract.iter().any(|f| f.name == focus) {
                self.add_diag("G025_UNKNOWN_FOCUS_FIELD", "error", lineno, 1,
                    format!("Focus no existe en contrato: {}.", focus));
            }
        }

        let effective_focus = if shape == "cuerpo" || shape == "bloque" {
            "$body".to_string()
        } else if focus.is_empty() {
            String::new()
        } else {
            focus.clone()
        };

        let is_open = open_str == "true";

        let surface = if let Some(ref ns_name) = ns {
            format!("{}::{}", ns_name, sigil)
        } else {
            sigil.clone()
        };

        let sym_def = SymbolDefinition {
            node: "SymbolDefinition".to_string(),
            surface,
            namespace: ns.clone(),
            qualified,
            label,
            shape: if shape.is_empty() { "attrs".to_string() } else { shape.clone() },
            weight: if weight.is_empty() { "B".to_string() } else { weight.clone() },
            focus: effective_focus,
            description: desc,
            open: is_open,
            contract,
            attributes: attrs_vec.iter().map(|a| AttrPair {
                node: "AttrPair".to_string(),
                key: a.key.clone(),
                value: Box::new(a.value.clone()),
            }).collect(),
            sourceLine: lineno,
        };

        self.symbol_map.insert(sigil, sym_def.clone());
        Some(sym_def)
    }

    fn parse_sections(&mut self) {
        while !self.at_end() {
            let line = self.lines[self.current_line].trim().to_string();
            if Self::is_blank_or_comment(&line) {
                self.advance();
                continue;
            }

            if self.current_line == 0 && line == "$0" {
                // Already handled
                self.advance();
                continue;
            }

            if line.starts_with("$") && line.len() > 1 {
                let bytes = line.as_bytes();
                if bytes[1].is_ascii_digit() {
                    self.parse_section_header();
                    continue;
                }
            }

            // If we see a glossary-level line outside $0 after sections started
            // Check for glossary reopened
            if !self.glossary_ended && line.starts_with("$0") {
                self.add_diag("G002_GLOSSARY_REOPENED", "error", self.lineno(), 1,
                    "$0 reaparece. Consolidar glosario.".to_string());
                self.advance();
                continue;
            }

            // Must be an idea
            if self.current_section.is_none() {
                // Check if it looks like an idea head (SIGIL:name...)
                if line.contains(':') && !line.starts_with('#') {
                    self.add_diag("S005_CONTENT_OUTSIDE_SECTION", "error", self.lineno(), 1,
                        "Contenido fuera de sección. Mover bajo $N.".to_string());
                }
                self.advance();
                continue;
            }

            // Try to parse as idea
            let section_id = self.current_section.unwrap();
            self.parse_idea(section_id);
        }
    }

    fn parse_section_header(&mut self) {
        let line = self.lines[self.current_line].trim().to_string();
        let lineno = self.lineno();
        self.advance();

        // Format: $N or $N: Title
        let colon_pos = line.find(':');
        let id_str = if let Some(pos) = colon_pos {
            line[1..pos].trim().to_string()
        } else {
            line[1..].trim().to_string()
        };

        let title = if let Some(pos) = colon_pos {
            let rest = &line[pos+1..].trim();
            if rest.is_empty() {
                None
            } else {
                Some(rest.to_string())
            }
        } else {
            None
        };

        if let Ok(id) = id_str.parse::<usize>() {
            if id == 0 {
                // $0 is glossary, not a regular section
                self.add_diag("G002_GLOSSARY_REOPENED", "error", lineno, 1,
                    "$0 reaparece. Consolidar glosario.".to_string());
                return;
            }

            if self.section_ids.contains(&id) {
                self.add_diag("S002_DUPLICATE_SECTION", "error", lineno, 1,
                    format!("Id de sección repetido: {}. Usar id único.", id));
            }
            self.section_ids.insert(id);

            self.sections.push(Section {
                node: "Section".to_string(),
                id,
                title,
                ideas: Vec::new(),
            });
            self.current_section = Some(id);
        } else {
            self.add_diag("S003_INVALID_IDEA_HEAD", "error", lineno, 1,
                format!("Encabezado de sección inválido: {}.", line));
        }
    }

    fn parse_idea(&mut self, section_id: usize) {
        let lineno = self.lineno();
        let line = self.lines[self.current_line].clone();
        let trimmed = line.trim().to_string();

        if trimmed.is_empty() || trimmed.starts_with('#') {
            self.advance();
            return;
        }

        // Must match SIGIL:name[payload]
        if !trimmed.contains(':') {
            self.add_diag("S003_INVALID_IDEA_HEAD", "error", lineno, 1,
                format!("Falta SIGIL:nombre válido en: {}.", trimmed));
            self.advance();
            return;
        }

        // Split into head and payload
        // Find the correct split - handle ns::SIGIL:name{...}
        let (symbol_part, after_colon) = if let Some(dcolon) = trimmed.find("::") {
            // ns::SIGIL:name{...}
            let rest = &trimmed[dcolon+2..];
            if let Some(colon_pos) = rest.find(':') {
                let sig = &rest[..colon_pos];
                let label_rest = &rest[colon_pos+1..];
                let ns_name = &trimmed[..dcolon];
                (format!("{}::{}", ns_name, sig), label_rest.to_string())
            } else {
                self.add_diag("S003_INVALID_IDEA_HEAD", "error", lineno, 1,
                    format!("Falta SIGIL:nombre válido en: {}.", trimmed));
                self.advance();
                return;
            }
        } else if let Some(colon_pos) = trimmed.find(':') {
            if colon_pos == 0 {
                self.add_diag("S003_INVALID_IDEA_HEAD", "error", lineno, 1,
                    format!("Falta SIGIL:nombre válido en: {}.", trimmed));
                self.advance();
                return;
            }
            let symbol = trimmed[..colon_pos].to_string();
            let rest = trimmed[colon_pos+1..].to_string();
            (symbol, rest)
        } else {
            self.add_diag("S003_INVALID_IDEA_HEAD", "error", lineno, 1,
                format!("Falta SIGIL:nombre válido en: {}.", trimmed));
            self.advance();
            return;
        };

        let (ns, sigil) = if let Some(dcolon) = symbol_part.find("::") {
            let ns_name = symbol_part[..dcolon].to_string();
            let sig = symbol_part[dcolon+2..].to_string();
            (Some(ns_name), sig)
        } else {
            (None, symbol_part)
        };

        // Validate sigil
        if !Self::is_valid_sigil(&sigil) {
            self.add_diag("L001_INVALID_SYMBOL", "error", lineno, 1,
                format!("Sigilo inválido: {}.", sigil));
            self.advance();
            return;
        }

        // Find name end - up to {, |, or end of line
        let name_end = after_colon.find(|c| c == '{' || c == '|').unwrap_or(after_colon.len());
        let name = after_colon[..name_end].trim().to_string();

        if !Self::is_valid_name(&name) {
            self.add_diag("L002_INVALID_NAME", "error", lineno, 1,
                format!("Nombre inválido: {}.", name));
        }

        // Check if symbol is declared
        let symbol_key = if let Some(ref ns_name) = ns {
            // Try qualified lookup
            format!("{}::{}", ns_name, sigil)
        } else {
            sigil.clone()
        };

        let sym_def = self.symbol_map.get(&sigil).cloned();
        let sym_def_qualified = if ns.is_some() {
            self.symbol_map.values().find(|s| s.qualified == symbol_key).cloned()
        } else {
            None
        };
        let effective_sym = sym_def.or(sym_def_qualified);

        if effective_sym.is_none() {
            self.add_diag("I001_UNDECLARED_SYMBOL", "error", lineno, 1,
                format!("Sigilo no declarado en $0: {}.", sigil));
            // Parse as attrs anyway for basic AST
            self.parse_idea_payload_unknown(section_id, &sigil, &name, &after_colon[name_end..], lineno, ns.clone());
            return;
        }

        let sym = effective_sym.unwrap();

        // Check address uniqueness
        let qualified_sym = if ns.is_some() { symbol_key.clone() } else { sigil.clone() };
        let address = format!("${}:{}:{}", section_id, qualified_sym, name);
        if self.seen_addresses.contains(&address) {
            self.add_diag("I002_DUPLICATE_IDEA_ADDRESS", "error", lineno, 1,
                format!("Dirección local repetida: {}.", address));
        }
        self.seen_addresses.insert(address.clone());

        // Determine expected shape
        let expected_shape = sym.shape.as_str();

        // Parse payload based on shape
        let payload_rest = after_colon[name_end..].to_string();

        match expected_shape {
            "attrs" => {
                // Must be braced and one line
                if !payload_rest.trim().starts_with('{') {
                    self.add_diag("I004_SHAPE_DELIMITER_MISMATCH", "error", lineno, 1,
                        format!("Delimitador no coincide con shape attrs. Usar braces."));
                    self.advance();
                    return;
                }
                if !payload_rest.trim().ends_with('}') {
                    self.add_diag("I003_ATTRS_MUST_BE_ONE_LINE", "error", lineno, 1,
                        "Attrs distribuido en varias líneas. Compactar la Idea.".to_string());
                    // Try to consume multiline
                    self.advance();
                    return;
                }
                let attrs = Self::parse_attrs_payload(&trimmed, lineno);
                if let Some(a) = attrs {
                    let (pairs, _) = self.validate_and_map_attrs(&a, &sym, lineno, section_id, &name, &sigil);
                    let payload = Payload::Attrs(AttrsPayload {
                        node: "AttrsPayload".to_string(),
                        pairs,
                    });
                    let idea = Idea {
                        node: "Idea".to_string(),
                        address,
                        section: section_id,
                        symbol: sigil.clone(),
                        qualifiedSymbol: qualified_sym,
                        name,
                        function: Function {
                            label: sym.label.clone(),
                            weight: sym.weight.clone(),
                            focus: sym.focus.clone(),
                        },
                        shape: "attrs".to_string(),
                        payload,
                        sourceLine: lineno,
                    };
                    if let Some(section) = self.sections.iter_mut().rev().find(|s| s.id == section_id) {
                        section.ideas.push(idea);
                    }
                } else {
                    self.add_diag("S006_INVALID_ATTRS", "error", lineno, 1,
                        "Attrs no separables o desbalanceados. Corregir pares y delimitadores.".to_string());
                }
                self.advance();
            }
            "attrs-pos" | "relacion" => {
                // Must be pipe-delimited, one line
                if !payload_rest.trim().starts_with('|') {
                    self.add_diag("I004_SHAPE_DELIMITER_MISMATCH", "error", lineno, 1,
                        format!("Delimitador no coincide con shape {}. Usar pipes.", expected_shape));
                    self.advance();
                    return;
                }
                if trimmed.contains('\n') {
                    self.add_diag("I011_PIPE_IDEA_MUST_BE_ONE_LINE", "error", lineno, 1,
                        format!("{} multilínea. Compactar a una línea.", expected_shape));
                }

                let cells = Self::parse_pipe_cells(payload_rest.trim());
                let shape_name = expected_shape.to_string();

                // Validate arity
                let required_count = sym.contract.iter().filter(|f| f.required).count();
                let total_count = sym.contract.len();

                if expected_shape == "attrs-pos" {
                    if cells.len() < required_count || cells.len() > total_count {
                        self.add_diag("I012_POSITIONAL_ARITY", "error", lineno, 1,
                            format!("Cells incompatibles con contrato. Esperadas entre {} y {}, obtenidas {}.",
                                required_count, total_count, cells.len()));
                    }
                } else {
                    // relation must have at least 3
                    if cells.len() < 3 {
                        self.add_diag("I013_RELATION_ARITY", "error", lineno, 1,
                            format!("Relación incompleta o excedida. Cumplir contrato. Esperadas >=3, obtenidas {}.", cells.len()));
                    }
                }

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

                let payload = if expected_shape == "relacion" {
                    Payload::Relation(RelationPayload {
                        node: "RelationPayload".to_string(),
                        cells,
                        bound,
                    })
                } else {
                    Payload::Positional(PositionalPayload {
                        node: "PositionalPayload".to_string(),
                        cells,
                        bound,
                    })
                };

                let idea = Idea {
                    node: "Idea".to_string(),
                    address,
                    section: section_id,
                    symbol: sigil.clone(),
                    qualifiedSymbol: qualified_sym,
                    name,
                    function: Function {
                        label: sym.label.clone(),
                        weight: sym.weight.clone(),
                        focus: sym.focus.clone(),
                    },
                    shape: shape_name,
                    payload,
                    sourceLine: lineno,
                };
                if let Some(section) = self.sections.iter_mut().rev().find(|s| s.id == section_id) {
                    section.ideas.push(idea);
                }
                self.advance();
            }
            "cuerpo" | "bloque" => {
                // cuerpo/bloque can be braced inline or multiline
                if payload_rest.trim().starts_with('{') && payload_rest.trim().ends_with('}') && !trimmed.contains('\n') {
                    // Inline braced
                    let inner = payload_rest.trim();
                    let text = inner[1..inner.len()-1].trim().to_string();
                    let text = Self::strip_outer_braces(text);

                    let payload = if expected_shape == "bloque" {
                        Payload::Block(BlockPayloadContent { text })
                     } else {
                        Payload::Text(TextPayloadContent { text })
                    };
                    let idea = Idea {
                        node: "Idea".to_string(),
                        address,
                        section: section_id,
                        symbol: sigil.clone(),
                        qualifiedSymbol: qualified_sym,
                        name,
                        function: Function {
                            label: sym.label.clone(),
                            weight: sym.weight.clone(),
                            focus: "$body".to_string(),
                        },
                        shape: expected_shape.to_string(),
                        payload,
                        sourceLine: lineno,
                    };
                    if let Some(section) = self.sections.iter_mut().rev().find(|s| s.id == section_id) {
                        section.ideas.push(idea);
                    }
                    self.advance();
                } else if payload_rest.trim().starts_with('{') {
                    // Multiline braced
                    self.advance();
                    let mut body_lines = Vec::new();
                    while !self.at_end() {
                        let bline = self.lines[self.current_line].trim().to_string();
                        if bline == "}" {
                            break;
                        }
                        body_lines.push(self.lines[self.current_line].clone());
                        self.advance();
                    }

                    if self.at_end() && !self.lines.is_empty() && self.lines[self.lineno()-1].trim() != "}" {
                        self.add_diag("I014_UNCLOSED_BODY", "error", lineno, 1,
                            "Cuerpo/bloque sin cierre. Agregar línea '}'.".to_string());
                    } else {
                        self.advance(); // skip '}'
                    }

                    let text = body_lines.join("\n");

                    let payload = if expected_shape == "bloque" {
                        Payload::Block(BlockPayloadContent { text })
                     } else {
                        Payload::Text(TextPayloadContent { text })
                    };
                    let idea = Idea {
                        node: "Idea".to_string(),
                        address,
                        section: section_id,
                        symbol: sigil.clone(),
                        qualifiedSymbol: qualified_sym,
                        name,
                        function: Function {
                            label: sym.label.clone(),
                            weight: sym.weight.clone(),
                            focus: "$body".to_string(),
                        },
                        shape: expected_shape.to_string(),
                        payload,
                        sourceLine: lineno,
                    };
                    if let Some(section) = self.sections.iter_mut().rev().find(|s| s.id == section_id) {
                        section.ideas.push(idea);
                    }
                } else {
                    self.add_diag("S004_MISSING_PAYLOAD", "error", lineno, 1,
                        format!("Idea sin payload. Agregar {{...}} o |... ."));
                    self.advance();
                }
            }
            _ => {
                // Unknown shape - treat as attrs
                let attrs = Self::parse_attrs_payload(&trimmed, lineno);
                if let Some(a) = attrs {
                    let pairs: Vec<AttrPair> = a.iter().map(|ap| AttrPair {
                        node: "AttrPair".to_string(),
                        key: ap.key.clone(),
                        value: Box::new(ap.value.clone()),
                    }).collect();
                    let payload = Payload::Attrs(AttrsPayload {
                        node: "AttrsPayload".to_string(),
                        pairs,
                    });
                    let idea = Idea {
                        node: "Idea".to_string(),
                        address,
                        section: section_id,
                        symbol: sigil.clone(),
                        qualifiedSymbol: qualified_sym,
                        name,
                        function: Function {
                            label: sym.label.clone(),
                            weight: "B".to_string(),
                            focus: String::new(),
                        },
                        shape: "attrs".to_string(),
                        payload,
                        sourceLine: lineno,
                    };
                    if let Some(section) = self.sections.iter_mut().rev().find(|s| s.id == section_id) {
                        section.ideas.push(idea);
                    }
                }
                self.advance();
            }
        }
    }

    fn parse_idea_payload_unknown(&mut self, section_id: usize, sigil: &str, name: &str,
        payload_rest: &str, lineno: usize, ns: Option<String>) {
        let qualified_sym = if let Some(ref ns_name) = ns {
            format!("{}::{}", ns_name, sigil)
        } else {
            sigil.to_string()
        };
        let address = format!("${}:{}:{}", section_id, qualified_sym, name);

        if payload_rest.trim().starts_with('{') {
            // Try attrs
            let full_line = self.lines[self.current_line].clone();
            let attrs = Self::parse_attrs_payload(&full_line, lineno);
            if let Some(a) = attrs {
                let pairs: Vec<AttrPair> = a.iter().map(|ap| AttrPair {
                    node: "AttrPair".to_string(),
                    key: ap.key.clone(),
                    value: Box::new(ap.value.clone()),
                }).collect();
                let idea = Idea {
                    node: "Idea".to_string(),
                    address,
                    section: section_id,
                    symbol: sigil.to_string(),
                    qualifiedSymbol: qualified_sym,
                    name: name.to_string(),
                    function: Function { label: String::new(), weight: "B".to_string(), focus: String::new() },
                    shape: "attrs".to_string(),
                    payload: Payload::Attrs(AttrsPayload { node: "AttrsPayload".to_string(), pairs }),
                    sourceLine: lineno,
                };
                if let Some(section) = self.sections.iter_mut().rev().find(|s| s.id == section_id) {
                    section.ideas.push(idea);
                }
            }
        } else if payload_rest.trim().starts_with('|') {
            let cells = Self::parse_pipe_cells(payload_rest.trim());
            let idea = Idea {
                node: "Idea".to_string(),
                address,
                section: section_id,
                symbol: sigil.to_string(),
                qualifiedSymbol: qualified_sym,
                name: name.to_string(),
                function: Function { label: String::new(), weight: "B".to_string(), focus: String::new() },
                shape: "attrs-pos".to_string(),
                payload: Payload::Positional(PositionalPayload {
                    node: "PositionalPayload".to_string(),
                    cells,
                    bound: vec![],
                }),
                sourceLine: lineno,
            };
            if let Some(section) = self.sections.iter_mut().rev().find(|s| s.id == section_id) {
                section.ideas.push(idea);
            }
        }

        self.advance();
    }

    fn validate_and_map_attrs(&self, attrs: &[RawAttr], sym: &SymbolDefinition,
        lineno: usize, _section_id: usize, _name: &str, _sigil: &str) -> (Vec<AttrPair>, Vec<Diagnostic>) {
        let mut pairs = Vec::new();
        let mut seen_keys = HashSet::new();
        let mut diags = Vec::new();

        if sym.contract.is_empty() && sym.open {
            // Open contract - accept anything
            for attr in attrs {
                seen_keys.insert(attr.key.clone());
                pairs.push(AttrPair {
                    node: "AttrPair".to_string(),
                    key: attr.key.clone(),
                    value: Box::new(attr.value.clone()),
                });
            }
            return (pairs, diags);
        }

        // Check field order - non-optional fields must come first, in contract order
        let contract_keys: Vec<&str> = sym.contract.iter().map(|f| f.name.as_str()).collect();
        let mut order_idx = 0;
        let mut found_keys = Vec::new();

        for attr in attrs {
            seen_keys.insert(attr.key.clone());
            found_keys.push(attr.key.clone());
        }

        // Validate field order (known fields must appear in contract order)
        let mut contract_pos = 0;
        for attr in attrs {
            if let Some(ci) = contract_keys.iter().position(|k| *k == attr.key) {
                if ci < contract_pos {
                    // Out of order
                    diags.push(Diagnostic {
                        code: "I007_FIELD_ORDER".to_string(),
                        severity: "error".to_string(),
                        span: Span { line: lineno, column: 1 },
                        message: format!("Fields fuera del orden contractual. Se esperaba {} después de posición {}.",
                            attr.key, contract_pos - 1),
                    });
                }
                contract_pos = ci + 1;
            } else {
                if !sym.open {
                    diags.push(Diagnostic {
                        code: "I005_UNKNOWN_FIELD".to_string(),
                        severity: "error".to_string(),
                        span: Span { line: lineno, column: 1 },
                        message: format!("Field no declarado en contrato cerrado: {}.", attr.key),
                    });
                }
            }
        }

        // Check for duplicate keys
        let mut key_counts = HashMap::new();
        for attr in attrs {
            let count = key_counts.entry(attr.key.clone()).or_insert(0);
            *count += 1;
            if *count > 1 {
                diags.push(Diagnostic {
                    code: "I006_DUPLICATE_FIELD".to_string(),
                    severity: "error".to_string(),
                    span: Span { line: lineno, column: 1 },
                    message: format!("Field repetido en attrs: {}.", attr.key),
                });
            }
        }

        // Check required fields
        for field in &sym.contract {
            if field.required && !seen_keys.contains(field.name.as_str()) {
                diags.push(Diagnostic {
                    code: "I008_REQUIRED_FIELD_MISSING".to_string(),
                    severity: "error".to_string(),
                    span: Span { line: lineno, column: 1 },
                    message: format!("Falta campo requerido: {}.", field.name),
                });
            }
        }

        // Check focus not empty
        if let Some(focus_attr) = attrs.iter().find(|a| a.key == sym.focus) {
            match &focus_attr.value {
                Scalar::StringValue { value, .. } if value.is_empty() => {
                    diags.push(Diagnostic {
                        code: "I016_EMPTY_FOCUS".to_string(),
                        severity: "error".to_string(),
                        span: Span { line: lineno, column: 1 },
                        message: "Foco textual vacío. Expresar la idea principal.".to_string(),
                    });
                }
                _ => {}
            }
        }

        // Build output pairs
        for attr in attrs {
            pairs.push(AttrPair {
                node: "AttrPair".to_string(),
                key: attr.key.clone(),
                value: Box::new(attr.value.clone()),
            });
        }

        // Merge diagnostics from validation
        for d in &diags {
            // We'll add these later if not duplicates
        }

        (pairs, diags)
    }

    // ===== Static utility methods =====

    fn strip_outer_braces(s: String) -> String {
        let s = s.trim();
        if s.starts_with('{') && s.ends_with('}') {
            s[1..s.len()-1].trim().to_string()
        } else {
            s.to_string()
        }
    }
}

#[derive(Clone)]
pub struct RawAttr {
    pub key: String,
    pub value: Scalar,
}

/// Parse a scalar value from a string representation.
/// This mirrors the logic in Parser::parse_scalar but works on a standalone string.
pub fn parse_scalar_from_str(s: &str) -> Scalar {
    let chars: Vec<char> = s.chars().collect();
    let (scalar, _) = Parser::parse_scalar(&chars, 0);
    scalar
}

impl Parser {

    pub fn parse_attrs_payload(line: &str, _lineno: usize) -> Option<Vec<RawAttr>> {
        // Find the opening brace
        let brace_start = line.find('{')?;
        let brace_end = line.rfind('}')?;
        if brace_end <= brace_start {
            return None;
        }

        let inner = &line[brace_start+1..brace_end];
        let inner = inner.trim();

        if inner.is_empty() {
            return Some(Vec::new());
        }

        // Parse key:value pairs separated by commas
        // Need to handle strings with commas inside
        let mut pairs = Vec::new();
        let mut i = 0;
        let chars: Vec<char> = inner.chars().collect();
        let len = chars.len();

        while i < len {
            // Skip spaces
            while i < len && (chars[i] == ' ' || chars[i] == '\t') { i += 1; }
            if i >= len { break; }

            // Parse key
            let key_start = i;
            while i < len && chars[i] != ':' && chars[i] != ',' && chars[i] != ' ' && chars[i] != '\t' {
                i += 1;
            }
            let key: String = chars[key_start..i].iter().collect();
            if key.is_empty() { break; }

            // Skip spaces and colon
            while i < len && (chars[i] == ' ' || chars[i] == '\t') { i += 1; }
            if i >= len || chars[i] != ':' { break; }
            i += 1; // skip ':'
            while i < len && (chars[i] == ' ' || chars[i] == '\t') { i += 1; }

            // Parse value
            if i >= len { break; }

            let (value, consumed) = Self::parse_scalar(&chars, i);
            i = consumed;

            pairs.push(RawAttr { key, value });

            // Skip comma
            while i < len && (chars[i] == ' ' || chars[i] == '\t') { i += 1; }
            if i < len && chars[i] == ',' {
                i += 1;
            }
        }

        Some(pairs)
    }

    pub(crate) fn parse_scalar(chars: &[char], start: usize) -> (Scalar, usize) {
        let mut i = start;
        let len = chars.len();

        if i >= len {
            return (Scalar::NullValue { value: None, lexeme: String::new() }, i);
        }

        // Skip spaces
        while i < len && (chars[i] == ' ' || chars[i] == '\t') { i += 1; }
        let val_start = i;

        if i >= len {
            return (Scalar::NullValue { value: None, lexeme: String::new() }, i);
        }

        // String
        if chars[i] == '"' {
            i += 1; // skip opening "
            let mut value = String::new();
            let mut escaped = false;
            while i < len {
                if escaped {
                    match chars[i] {
                        '"' => value.push('"'),
                        '\\' => value.push('\\'),
                        'n' => value.push('\n'),
                        'r' => value.push('\r'),
                        't' => value.push('\t'),
                        'b' => value.push('\u{0008}'),
                        'f' => value.push('\u{000C}'),
                        'u' => {
                            // Parse 4 hex digits
                            if i + 4 < len {
                                let hex: String = chars[i+1..i+5].iter().collect();
                                if let Ok(code) = u32::from_str_radix(&hex, 16) {
                                    if let Some(c) = char::from_u32(code) {
                                        value.push(c);
                                    }
                                    i += 4;
                                }
                            }
                        }
                        _ => value.push(chars[i]),
                    }
                    escaped = false;
                    i += 1;
                } else if chars[i] == '\\' {
                    escaped = true;
                    i += 1;
                } else if chars[i] == '"' {
                    i += 1; // skip closing "
                    break;
                } else {
                    value.push(chars[i]);
                    i += 1;
                }
            }
            let lexeme: String = chars[val_start..i].iter().collect();
            return (Scalar::StringValue { value, lexeme }, i);
        }

        // List
        if chars[i] == '[' {
            i += 1; // skip '['
            let mut items = Vec::new();
            while i < len {
                while i < len && (chars[i] == ' ' || chars[i] == '\t' || chars[i] == '\n') { i += 1; }
                if i >= len || chars[i] == ']' {
                    if i < len { i += 1; } // skip ']'
                    break;
                }
                let (item, new_i) = Self::parse_scalar(chars, i);
                // Check for nested list
                if let Scalar::ListValue { .. } = item {
                    // Nested list not allowed in CORTEX 0.1
                    // We'll still parse it but validation should catch
                }
                items.push(item);
                i = new_i;
                while i < len && (chars[i] == ' ' || chars[i] == '\t' || chars[i] == '\n') { i += 1; }
                if i < len && chars[i] == ',' {
                    i += 1;
                }
            }
            let lexeme: String = chars[val_start..i].iter().collect();
            return (Scalar::ListValue { items, lexeme }, i);
        }

        // Number-like: integer, decimal, negative
        if chars[i] == '-' || chars[i].is_ascii_digit() {
            let mut num_chars = Vec::new();
            let mut is_decimal = false;
            if chars[i] == '-' { num_chars.push('-'); i += 1; }
            while i < len && chars[i].is_ascii_digit() {
                num_chars.push(chars[i]);
                i += 1;
            }
            if i < len && chars[i] == '.' {
                is_decimal = true;
                num_chars.push('.');
                i += 1;
                while i < len && chars[i].is_ascii_digit() {
                    num_chars.push(chars[i]);
                    i += 1;
                }
            }
            let num_str: String = num_chars.iter().collect();
            if !num_str.is_empty() {
                let lexeme: String = chars[val_start..i].iter().collect();
                if is_decimal {
                    return (Scalar::DecimalValue { value: num_str, lexeme }, i);
                } else {
                    return (Scalar::IntegerValue { value: num_str, lexeme }, i);
                }
            }
        }

        // Boolean, null, atom
        let mut word = String::new();
        while i < len && chars[i] != ',' && chars[i] != ']' && chars[i] != ' ' && chars[i] != '\t' && chars[i] != '\n' && chars[i] != '}' {
            word.push(chars[i]);
            i += 1;
        }
        let lexeme: String = chars[val_start..i].iter().collect();

        match word.as_str() {
            "true" => (Scalar::BooleanValue { value: true, lexeme }, i),
            "false" => (Scalar::BooleanValue { value: false, lexeme }, i),
            "null" | "null" => (Scalar::NullValue { value: None, lexeme }, i),
            _ => {
                // Check for microtoken expansion
                let value = word.clone();
                (Scalar::AtomValue { value, lexeme, micro: None }, i)
            }
        }
    }

    fn parse_pipe_cells(s: &str) -> Vec<Scalar> {
        let s = s.trim();
        if !s.starts_with('|') {
            return vec![];
        }
        let inner = &s[1..]; // skip leading '|'
        let mut cells = Vec::new();
        let chars: Vec<char> = inner.chars().collect();
        let len = chars.len();
        let mut i = 0;

        while i < len {
            // Skip leading spaces
            while i < len && chars[i] == ' ' { i += 1; }

            if i >= len {
                // Trailing empty cell
                cells.push(Scalar::AtomValue { value: String::new(), lexeme: String::new(), micro: None });
                break;
            }

            // Check if quoted
            if chars[i] == '"' {
                // Parse as string
                i += 1; // skip opening "
                let mut value = String::new();
                let mut escaped = false;
                while i < len {
                    if escaped {
                        match chars[i] {
                            '"' => value.push('"'),
                            '\\' => value.push('\\'),
                            'n' => value.push('\n'),
                            'r' => value.push('\r'),
                            't' => value.push('\t'),
                            'b' => value.push('\u{0008}'),
                            'f' => value.push('\u{000C}'),
                            _ => value.push(chars[i]),
                        }
                        escaped = false;
                        i += 1;
                    } else if chars[i] == '\\' {
                        escaped = true;
                        i += 1;
                    } else if chars[i] == '"' {
                        i += 1; // skip closing "
                        break;
                    } else {
                        value.push(chars[i]);
                        i += 1;
                    }
                }
                // Skip to next pipe
                let start = i;
                while i < len && chars[i] != '|' { i += 1; }
                let lexeme: String = chars[start..i].iter().collect();
                cells.push(Scalar::StringValue { value, lexeme });
            } else {
                // Raw cell - read until pipe or end
                let start = i;
                while i < len && chars[i] != '|' { i += 1; }
                let cell_text: String = chars[start..i].iter().collect();
                let trimmed = cell_text.trim().to_string();
                let lexeme = cell_text.clone();
                cells.push(Scalar::AtomValue { value: trimmed, lexeme, micro: None });
            }

            // Skip pipe
            if i < len && chars[i] == '|' {
                i += 1;
            }
        }

        cells
    }

    fn get_attr_value(attrs: &[RawAttr], key: &str, default: &str) -> String {
        for attr in attrs {
            if attr.key == key {
                match &attr.value {
                    Scalar::AtomValue { value, .. } => return value.clone(),
                    Scalar::StringValue { value, .. } => return value.clone(),
                    Scalar::BooleanValue { value: true, .. } => return "true".to_string(),
                    Scalar::BooleanValue { value: false, .. } => return "false".to_string(),
                    _ => return default.to_string(),
                }
            }
        }
        default.to_string()
    }

    fn get_attr_str(attrs: &[RawAttr], key: &str, default: &str) -> String {
        for attr in attrs {
            if attr.key == key {
                match &attr.value {
                    Scalar::StringValue { value, .. } => return value.clone(),
                    Scalar::AtomValue { value, .. } => return value.clone(),
                    _ => return default.to_string(),
                }
            }
        }
        default.to_string()
    }

    fn extract_enum_values(attrs: &[RawAttr]) -> Vec<String> {
        for attr in attrs {
            if attr.key == "values" {
                if let Scalar::StringValue { ref value, .. } = attr.value {
                    return value.split('|').map(|s| s.trim().to_string()).filter(|s| !s.is_empty()).collect();
                }
            }
        }
        vec![]
    }

    fn extract_micro_expand(attrs: &[RawAttr]) -> String {
        for attr in attrs {
            if attr.key == "expand" {
                match &attr.value {
                    Scalar::AtomValue { value, .. } => return value.clone(),
                    Scalar::StringValue { value, .. } => return value.clone(),
                    _ => {}
                }
            }
        }
        String::new()
    }

    fn is_valid_sigil(s: &str) -> bool {
        if s == "!" { return true; }
        if s.is_empty() || s.len() > 16 { return false; }
        let chars: Vec<char> = s.chars().collect();
        if !chars[0].is_ascii_uppercase() { return false; }
        chars.iter().all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || *c == '_')
    }

    fn is_valid_name(s: &str) -> bool {
        if s.is_empty() { return false; }
        let chars: Vec<char> = s.chars().collect();
        if !chars[0].is_ascii_alphabetic() && chars[0] != '_' { return false; }
        chars.iter().all(|c| c.is_ascii_alphanumeric() || *c == '_' || *c == '.' || *c == '-')
    }

    fn parse_contract_fields(s: &str, _lineno: usize, parser: &mut Parser) -> Vec<ContractField> {
        let mut fields = Vec::new();
        let mut seen_names = HashSet::new();

        for part in s.split('|') {
            let part = part.trim();
            if part.is_empty() { continue; }

            let is_optional = part.ends_with('?');
            let base = if is_optional { &part[..part.len()-1] } else { part };

            let (name, field_type) = if let Some(colon_pos) = base.find(':') {
                let n = base[..colon_pos].trim().to_string();
                let t = base[colon_pos+1..].trim().to_string();
                (n, t)
            } else {
                (base.trim().to_string(), "any".to_string())
            };

            if seen_names.contains(&name) {
                parser.add_diag("G009_DUPLICATE_CONTRACT_FIELD", "error", _lineno, 1,
                    format!("Field repetido: {}. Mantener una definición.", name));
            }
            seen_names.insert(name.clone());

            // Validate field type
            if field_type.starts_with('%') {
                let enum_name = &field_type[1..];
                if !parser.enum_map.contains_key(enum_name) && field_type != "%state" {
                    // Only flag if we have enums defined but this one isn't found
                    if !parser.enum_map.is_empty() && !parser.enum_map.contains_key(enum_name) {
                        // Actually, the enum might be declared later - we'll check after full parsing
                    }
                }
            } else if !["any", "text", "atom", "int", "dec", "bool", "null", "list"].contains(&field_type.as_str()) {
                // May be unknown
            }

            fields.push(ContractField {
                name,
                field_type: if field_type.is_empty() { "any".to_string() } else { field_type },
                required: !is_optional,
            });
        }

        fields
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let do_canonicalize = args.iter().any(|a| a == "--canonicalize");

    // Read raw bytes for canonicalization
    let raw_bytes: Vec<u8> = if do_canonicalize {
        // With --canonicalize flag, file path is at position after flag
        let file_idx = if args.len() > 2 && args[1] == "--canonicalize" { 2 }
                       else if args.len() > 1 && !args[1].starts_with("--") { 1 }
                       else { 0 };
        if file_idx > 0 && file_idx < args.len() {
            let path = &args[file_idx];
            match fs::read(path) {
                Ok(content) => content,
                Err(e) => {
                    eprintln!("Error reading file: {}", e);
                    process::exit(1);
                }
            }
        } else {
            let mut buffer = Vec::new();
            if io::stdin().read_to_end(&mut buffer).is_err() {
                eprintln!("Error reading stdin");
                process::exit(1);
            }
            buffer
        }
    } else if args.len() > 1 && !args[1].starts_with("--") {
        let path = &args[1];
        match fs::read(path) {
            Ok(content) => content,
            Err(e) => {
                eprintln!("Error reading file: {}", e);
                process::exit(1);
            }
        }
    } else {
        let mut buffer = Vec::new();
        if io::stdin().read_to_end(&mut buffer).is_err() {
            eprintln!("Error reading stdin");
            process::exit(1);
        }
        buffer
    };

    if do_canonicalize {
        let (canonical_bytes, report) = canonicalize::canonicalize(&raw_bytes);
        let report_json = serde_json::to_string_pretty(&report).unwrap_or_else(|_| "{}".to_string());
        // Write canonical bytes to stdout
        // Use stdout lock for binary output
        use std::io::Write;
        let stdout = io::stdout();
        let mut handle = stdout.lock();
        // Write report as JSON to stderr
        eprintln!("{}", report_json);
        // Write canonical bytes to stdout
        handle.write_all(&canonical_bytes).unwrap_or_else(|_| {
            // fallback to writing as text
        });
        return;
    }

    // Normalize CRLF to LF for text processing
    let input = String::from_utf8_lossy(&raw_bytes).replace("\r\n", "\n");
    let input = input.replace('\r', "\n");

    let mut parser = Parser::new(&input);
    parser.parse_document();

    // Post-processing: validate enum references in contracts
    let diag_count = parser.diagnostics.len();

    // Build the document AST
    let doc = Document {
        node: "Document".to_string(),
        cortexVersion: "0.1".to_string(),
        encoding: "UTF-8".to_string(),
        glossary: parser.glossary.unwrap_or_else(|| Glossary {
            node: "Glossary".to_string(),
            format: FormatDeclaration {
                node: "FormatDeclaration".to_string(),
                cortex: "0.1".to_string(),
                encoding: "UTF-8".to_string(),
                attributes: vec![],
                sourceLine: 0,
            },
            meta: vec![],
            enums: vec![],
            micros: vec![],
            namespaces: vec![],
            extensions: vec![],
            symbols: vec![],
        }),
        sections: parser.sections,
    };

    // Output AST JSON to stdout
    let json = serde_json::to_string_pretty(&doc).unwrap_or_else(|_| "{}".to_string());
    println!("{}", json);

    // Output diagnostics to stderr
    if diag_count > 0 {
        for diag in &parser.diagnostics {
            let diag_json = serde_json::to_string(diag).unwrap_or_default();
            eprintln!("{}", diag_json);
        }
        process::exit(diag_count as i32);
    }
}
