#![forbid(unsafe_code)]

//! CODEC-CORTEX Rust implementation.
//!
//! This crate implements the behavior exposed by the Python reference package:
//! CORTEX 0.1 parsing, C14N-0.1 canonicalization, HCORTEX canonical rendering /
//! compilation, and the F3/F4 conformance harness.

pub mod c14n;
pub mod error;
pub mod harness;
pub mod hcortex;
pub mod model;
pub mod parser;
pub mod scalars;

pub use c14n::{canonicalize, canonicalize_in_place};
pub use error::ParseError;
pub use harness::{c14n_hash, run_all_tests, run_phase3, run_phase4, sha256_bytes};
pub use hcortex::{compile_hcortex, render_hcortex, HDiagnostic};
pub use model::*;
pub use parser::{parse_contract_fields, parse_cortex};
pub use scalars::{emit_string_literal, is_atom_lexeme, parse_string_literal, to_nfc, utf8_bytes};
