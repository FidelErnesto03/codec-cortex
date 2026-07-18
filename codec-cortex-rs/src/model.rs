use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", content = "value", rename_all = "kebab-case")]
pub enum ScalarValue {
    String(String),
    Atom(String),
    Integer(String),
    Decimal(String),
    Boolean(bool),
    Null,
    List(Vec<Scalar>),
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Scalar {
    #[serde(flatten)]
    pub value: ScalarValue,
    pub lexeme: String,
}

impl Scalar {
    pub fn string(value: impl Into<String>, lexeme: impl Into<String>) -> Self {
        Self { value: ScalarValue::String(value.into()), lexeme: lexeme.into() }
    }
    pub fn atom(value: impl Into<String>) -> Self {
        let value = value.into();
        Self { value: ScalarValue::Atom(value.clone()), lexeme: value }
    }
    pub fn integer(value: impl Into<String>) -> Self {
        let value = value.into();
        Self { value: ScalarValue::Integer(value.clone()), lexeme: value }
    }
    pub fn decimal(value: impl Into<String>) -> Self {
        let value = value.into();
        Self { value: ScalarValue::Decimal(value.clone()), lexeme: value }
    }
    pub fn boolean(value: bool) -> Self {
        Self { value: ScalarValue::Boolean(value), lexeme: value.to_string() }
    }
    pub fn null() -> Self {
        Self { value: ScalarValue::Null, lexeme: "null".into() }
    }
    pub fn list(items: Vec<Scalar>) -> Self {
        let lexeme = format!("[{}]", items.iter().map(|v| v.lexeme.as_str()).collect::<Vec<_>>().join(","));
        Self { value: ScalarValue::List(items), lexeme }
    }
    pub fn kind(&self) -> &'static str {
        match &self.value {
            ScalarValue::String(_) => "string",
            ScalarValue::Atom(_) => "atom",
            ScalarValue::Integer(_) => "integer",
            ScalarValue::Decimal(_) => "decimal",
            ScalarValue::Boolean(_) => "boolean",
            ScalarValue::Null => "null",
            ScalarValue::List(_) => "list",
        }
    }
    pub fn text_value(&self) -> Option<&str> {
        match &self.value {
            ScalarValue::String(v) | ScalarValue::Atom(v) | ScalarValue::Integer(v) | ScalarValue::Decimal(v) => Some(v),
            _ => None,
        }
    }
    pub fn is_true(&self) -> bool {
        matches!(&self.value, ScalarValue::Boolean(true)) || matches!(&self.value, ScalarValue::Atom(v) if v == "true")
    }
}

pub type Attrs = Vec<(String, Scalar)>;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct FormatDecl {
    pub cortex: String,
    pub encoding: String,
    pub attrs: Attrs,
    pub source_line: usize,
}

impl Default for FormatDecl {
    fn default() -> Self {
        Self { cortex: "0.1".into(), encoding: "UTF-8".into(), attrs: Vec::new(), source_line: 1 }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct MetaDecl { pub name: String, pub attrs: Attrs, pub source_line: usize, pub capa: Option<String> }
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EnumDecl { pub name: String, pub values: Vec<String>, pub source_line: usize }
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct MicroDecl { pub token: String, pub expand: String, pub source_line: usize }
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct NamespaceDecl { pub alias: String, pub attrs: Attrs, pub source_line: usize }
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ExtensionDecl { pub name: String, pub attrs: Attrs, pub source_line: usize }

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct ContractField { pub name: String, pub field_type: String, pub required: bool }

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct SymbolDef {
    pub namespace: Option<String>,
    pub sigil: String,
    pub label: String,
    pub shape: String,
    pub weight: String,
    pub focus: String,
    pub desc: String,
    pub open: bool,
    pub contract: Vec<ContractField>,
    pub attrs: Attrs,
    pub source_line: usize,
}

impl SymbolDef {
    pub fn qualified(&self) -> String {
        self.namespace.as_ref().map(|ns| format!("{ns}::{}", self.sigil)).unwrap_or_else(|| self.sigil.clone())
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "shape", content = "value", rename_all = "kebab-case")]
pub enum IdeaPayload {
    Attrs(Attrs),
    Positional(Vec<Scalar>),
    Body(String),
    Block(String),
    MultilinePending,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Idea {
    pub section: u64,
    pub namespace: Option<String>,
    pub symbol: String,
    pub name: String,
    pub shape: String,
    pub payload: IdeaPayload,
    pub source_line: usize,
}

impl Idea {
    pub fn qualified_symbol(&self) -> String {
        self.namespace.as_ref().map(|ns| format!("{ns}::{}", self.symbol)).unwrap_or_else(|| self.symbol.clone())
    }
    pub fn address(&self) -> String {
        format!("${}:{}:{}", self.section, self.qualified_symbol(), self.name)
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Section { pub id: u64, pub title: Option<String>, pub ideas: Vec<Idea>, pub capa: Option<String> }

impl Section {
    pub fn resolve_capa(&self) -> Option<&str> {
        if self.capa.is_some() {
            return self.capa.as_deref();
        }
        if self.id >= 2 {
            return Some("DATA");
        }
        None
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize, Default)]
pub struct Glossary {
    pub format: Option<FormatDecl>,
    pub meta: Vec<MetaDecl>,
    pub enums: Vec<EnumDecl>,
    pub micros: Vec<MicroDecl>,
    pub namespaces: Vec<NamespaceDecl>,
    pub extensions: Vec<ExtensionDecl>,
    pub symbols: Vec<SymbolDef>,
    pub capa: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Document {
    pub cortex_version: String,
    pub encoding: String,
    pub glossary: Glossary,
    pub sections: Vec<Section>,
}

impl Default for Document {
    fn default() -> Self {
        Self { cortex_version: "0.1".into(), encoding: "UTF-8".into(), glossary: Glossary::default(), sections: Vec::new() }
    }
}
