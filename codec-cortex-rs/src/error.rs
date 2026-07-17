use serde::{Deserialize, Serialize};
use thiserror::Error;

/// Structured CORTEX parse error compatible with the Python implementation.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize, Error)]
#[error("{code} @ {line}:{col} — {message}")]
pub struct ParseError {
    pub code: String,
    pub message: String,
    pub line: usize,
    pub col: usize,
}

impl ParseError {
    pub fn new(code: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            message: message.into(),
            line: 0,
            col: 0,
        }
    }

    pub fn at(
        code: impl Into<String>,
        message: impl Into<String>,
        line: usize,
        col: usize,
    ) -> Self {
        Self {
            code: code.into(),
            message: message.into(),
            line,
            col,
        }
    }
}
