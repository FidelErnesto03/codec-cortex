use std::sync::OnceLock;

use regex::Regex;
use unicode_normalization::UnicodeNormalization;

use crate::error::ParseError;
use crate::model::Scalar;

fn atom_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^(?:\$[0-9]+:)?[_A-Za-z][_A-Za-z0-9./:@+%$-]*$").unwrap())
}
fn int_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^-?(0|[1-9][0-9]*)$").unwrap())
}
fn dec_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^-?(0|[1-9][0-9]*)\.[0-9]+$").unwrap())
}

pub(crate) fn atom_matches(s: &str) -> bool { atom_re().is_match(s) }
pub(crate) fn int_matches(s: &str) -> bool { int_re().is_match(s) }
pub(crate) fn dec_matches(s: &str) -> bool { dec_re().is_match(s) }

pub fn to_nfc(s: &str) -> String { s.nfc().collect() }
pub fn utf8_bytes(s: &str) -> Vec<u8> { s.as_bytes().to_vec() }

pub fn is_atom_lexeme(s: &str) -> bool {
    if s.is_empty() || s.chars().count() > 32 { return false; }
    if s.chars().any(|c| c.is_whitespace() || matches!(c, '[' | ']' | '{' | '}' | ',' | '"' | '|')) {
        return false;
    }
    atom_matches(s)
}

pub fn parse_string_literal(s: &str) -> Result<String, ParseError> {
    let chars: Vec<char> = s.chars().collect();
    let mut out = String::new();
    let mut i = 0usize;
    while i < chars.len() {
        let c = chars[i];
        if c == '\\' {
            if i + 1 >= chars.len() {
                return Err(ParseError::new("L005_INVALID_STRING", "Trailing backslash in string"));
            }
            let next = chars[i + 1];
            match next {
                '"' => out.push('"'),
                '\\' => out.push('\\'),
                'n' => out.push('\n'),
                'r' => out.push('\r'),
                't' => out.push('\t'),
                'b' => out.push('\u{0008}'),
                'f' => out.push('\u{000C}'),
                '/' => out.push('/'),
                'u' => {
                    if i + 5 >= chars.len() {
                        return Err(ParseError::new("L005_INVALID_STRING", "Bad \\u escape"));
                    }
                    let hex: String = chars[i + 2..=i + 5].iter().collect();
                    if !hex.chars().all(|h| h.is_ascii_hexdigit()) {
                        return Err(ParseError::new("L005_INVALID_STRING", "Bad \\u escape"));
                    }
                    let value = u32::from_str_radix(&hex, 16).unwrap();
                    let ch = char::from_u32(value).ok_or_else(|| ParseError::new("L005_INVALID_STRING", "Invalid Unicode scalar"))?;
                    out.push(ch);
                    i += 4;
                }
                other => return Err(ParseError::new("L005_INVALID_STRING", format!("Unknown escape \\{other}"))),
            }
            i += 2;
        } else if c == '"' {
            return Err(ParseError::new("L005_INVALID_STRING", "Unescaped quote in string body"));
        } else {
            out.push(c);
            i += 1;
        }
    }
    Ok(out)
}

pub fn emit_string_literal(value: &str) -> String {
    let mut out = String::with_capacity(value.len() + 2);
    out.push('"');
    for ch in value.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\u{0008}' => out.push_str("\\b"),
            '\u{000C}' => out.push_str("\\f"),
            c if (c as u32) < 0x20 || c == '\u{007F}' => out.push_str(&format!("\\u{:04X}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

#[derive(Debug, Clone)]
pub(crate) struct StringCursor {
    chars: Vec<char>,
    pub i: usize,
    pub line: usize,
    pub col: usize,
}

impl StringCursor {
    pub fn new(s: &str, line: usize, col: usize) -> Self {
        Self { chars: s.chars().collect(), i: 0, line, col }
    }
    pub fn peek(&self) -> Option<char> { self.chars.get(self.i).copied() }
    pub fn next(&mut self) -> Option<char> {
        let c = self.peek()?;
        self.i += 1;
        if c == '\n' { self.line += 1; self.col = 1; } else { self.col += 1; }
        Some(c)
    }
    pub fn slice(&self, start: usize, end: usize) -> String { self.chars[start..end].iter().collect() }
}

pub(crate) fn skip_inline_ws(cur: &mut StringCursor) {
    while matches!(cur.peek(), Some(' ' | '\t')) { cur.next(); }
}

pub(crate) fn parse_scalar(cur: &mut StringCursor) -> Result<Scalar, ParseError> {
    skip_inline_ws(cur);
    match cur.peek() {
        Some('"') => parse_string_scalar(cur),
        Some('[') => parse_list_scalar(cur),
        Some(_) => parse_atom_or_number(cur),
        None => Err(ParseError::at("L010_INVALID_ATOM", "Empty scalar", cur.line, cur.col)),
    }
}

pub(crate) fn parse_string_scalar(cur: &mut StringCursor) -> Result<Scalar, ParseError> {
    debug_assert_eq!(cur.peek(), Some('"'));
    cur.next();
    let mut body = String::new();
    loop {
        match cur.peek() {
            None => return Err(ParseError::at("L005_INVALID_STRING", "Unterminated string", cur.line, cur.col)),
            Some('"') => { cur.next(); break; }
            Some('\\') => {
                body.push('\\');
                cur.next();
                let next = cur.peek().ok_or_else(|| ParseError::at("L005_INVALID_STRING", "Trailing backslash", cur.line, cur.col))?;
                body.push(next);
                cur.next();
                if next == 'u' {
                    for _ in 0..4 {
                        let h = cur.peek().ok_or_else(|| ParseError::at("L005_INVALID_STRING", "Bad \\u escape", cur.line, cur.col))?;
                        body.push(h);
                        cur.next();
                    }
                }
            }
            Some(c) => { body.push(c); cur.next(); }
        }
    }
    let value = parse_string_literal(&body)?;
    let lexeme = emit_string_literal(&value);
    Ok(Scalar::string(value, lexeme))
}

fn parse_list_scalar(cur: &mut StringCursor) -> Result<Scalar, ParseError> {
    debug_assert_eq!(cur.peek(), Some('['));
    cur.next();
    let mut items = Vec::new();
    skip_inline_ws(cur);
    if cur.peek() == Some(']') { cur.next(); return Ok(Scalar::list(items)); }
    loop {
        items.push(parse_scalar(cur)?);
        skip_inline_ws(cur);
        match cur.peek() {
            Some(',') => { cur.next(); skip_inline_ws(cur); }
            Some(']') => { cur.next(); break; }
            other => return Err(ParseError::at("L007_INVALID_LIST", format!("Expected , or ] got {other:?}"), cur.line, cur.col)),
        }
    }
    Ok(Scalar::list(items))
}

fn parse_atom_or_number(cur: &mut StringCursor) -> Result<Scalar, ParseError> {
    let start = cur.i;
    while let Some(c) = cur.peek() {
        if c.is_whitespace() || matches!(c, ',' | '}' | ']' | '|') { break; }
        cur.next();
    }
    let raw = cur.slice(start, cur.i);
    match raw.as_str() {
        "true" => Ok(Scalar::boolean(true)),
        "false" => Ok(Scalar::boolean(false)),
        "null" => Ok(Scalar::null()),
        _ if int_matches(&raw) => Ok(Scalar::integer(if raw == "-0" { "0" } else { &raw })),
        _ if dec_matches(&raw) => Ok(Scalar::decimal(raw)),
        _ if atom_matches(&raw) => Ok(Scalar::atom(raw)),
        _ => Err(ParseError::at("L010_INVALID_ATOM", format!("Invalid atom: {raw:?}"), cur.line, cur.col)),
    }
}

pub(crate) fn parse_attrs_payload(s: &str, start_line: usize) -> Result<Vec<(String, Scalar)>, ParseError> {
    let mut cur = StringCursor::new(s, start_line, 1);
    skip_inline_ws(&mut cur);
    if cur.peek() != Some('{') { return Err(ParseError::at("S006_INVALID_ATTRS", "Expected {", cur.line, cur.col)); }
    cur.next();
    let mut pairs = Vec::new();
    skip_inline_ws(&mut cur);
    if cur.peek() == Some('}') { cur.next(); return Ok(pairs); }
    loop {
        skip_inline_ws(&mut cur);
        let start = cur.i;
        while let Some(c) = cur.peek() {
            if c == '}' || c.is_whitespace() || matches!(c, ':' | ',') { break; }
            cur.next();
        }
        let key = cur.slice(start, cur.i);
        if key.is_empty() { return Err(ParseError::at("L003_INVALID_KEY", "Empty key", cur.line, cur.col)); }
        skip_inline_ws(&mut cur);
        if cur.peek() != Some(':') { return Err(ParseError::at("S006_INVALID_ATTRS", "Expected : after key", cur.line, cur.col)); }
        cur.next();
        let value = parse_scalar(&mut cur)?;
        pairs.push((key, value));
        skip_inline_ws(&mut cur);
        match cur.peek() {
            Some(',') => {
                cur.next();
                skip_inline_ws(&mut cur);
                if cur.peek() == Some('}') { cur.next(); break; }
            }
            Some('}') => { cur.next(); break; }
            other => return Err(ParseError::at("S006_INVALID_ATTRS", format!("Expected , or }} got {other:?}"), cur.line, cur.col)),
        }
    }
    Ok(pairs)
}

pub(crate) fn classify_raw_cell(raw: &str) -> Scalar {
    if int_matches(raw) { return Scalar::integer(if raw == "-0" { "0" } else { raw }); }
    if dec_matches(raw) { return Scalar::decimal(raw); }
    match raw {
        "true" => Scalar::boolean(true),
        "false" => Scalar::boolean(false),
        "null" => Scalar::null(),
        _ if atom_matches(raw) && !raw.contains(' ') => Scalar::atom(raw),
        _ => Scalar::string(raw, emit_string_literal(raw)),
    }
}

pub(crate) fn classify_compact_value(lex: &str) -> Result<Scalar, ParseError> {
    let lex = lex.trim();
    if lex.starts_with('"') && lex.ends_with('"') && lex.len() >= 2 {
        let value = parse_string_literal(&lex[1..lex.len() - 1])?;
        return Ok(Scalar::string(value.clone(), emit_string_literal(&value)));
    }
    if lex.starts_with('[') && lex.ends_with(']') {
        let inner = &lex[1..lex.len() - 1];
        if inner.is_empty() { return Ok(Scalar::list(Vec::new())); }
        let mut items = Vec::new();
        for part in split_comma_top(inner) { items.push(classify_compact_value(&part)?); }
        return Ok(Scalar::list(items));
    }
    Ok(classify_raw_cell(lex))
}

pub(crate) fn split_comma_top(s: &str) -> Vec<String> {
    let mut parts = Vec::new();
    let mut current = String::new();
    let mut depth = 0i32;
    let mut in_string = false;
    let mut escaped = false;
    for ch in s.chars() {
        if in_string {
            current.push(ch);
            if escaped { escaped = false; }
            else if ch == '\\' { escaped = true; }
            else if ch == '"' { in_string = false; }
        } else {
            match ch {
                '"' => { in_string = true; current.push(ch); }
                '[' | '{' | '(' => { depth += 1; current.push(ch); }
                ']' | '}' | ')' => { depth -= 1; current.push(ch); }
                ',' if depth == 0 => { parts.push(current.trim().to_string()); current.clear(); }
                _ => current.push(ch),
            }
        }
    }
    if !current.is_empty() { parts.push(current.trim().to_string()); }
    parts
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::model::ScalarValue;

    #[test]
    fn string_roundtrip() {
        let source = "hello\\n\\u00E9\\\"";
        let value = parse_string_literal(source).unwrap();
        assert_eq!(value, "hello\né\"");
        assert_eq!(parse_string_literal(&emit_string_literal(&value)[1..emit_string_literal(&value).len()-1]).unwrap(), value);
    }

    #[test]
    fn parses_nested_list() {
        let mut cur = StringCursor::new("[a,1,[true,\"x\"]]", 1, 1);
        let scalar = parse_scalar(&mut cur).unwrap();
        assert_eq!(scalar.lexeme, "[a,1,[true,\"x\"]]");
        assert!(matches!(scalar.value, ScalarValue::List(_)));
    }
}
