use codec_cortex::{
    c14n_hash, emit_string_literal, is_atom_lexeme, parse_contract_fields,
    parse_string_literal,
};

#[test]
fn public_scalar_helpers_are_reversible() {
    let value = "line one\nCafé \"quoted\"";
    let literal = emit_string_literal(value);
    assert_eq!(parse_string_literal(&literal[1..literal.len() - 1]).unwrap(), value);
}

#[test]
fn public_contract_parser_preserves_required_flags() {
    let fields = parse_contract_fields("topic:text|state:%state?|count:integer").unwrap();
    assert_eq!(fields.len(), 3);
    assert!(fields[0].required);
    assert!(!fields[1].required);
    assert_eq!(fields[1].field_type, "%state");
}

#[test]
fn atom_rules_and_domain_hash_are_stable() {
    assert!(is_atom_lexeme("agent::ACT"));
    assert!(!is_atom_lexeme("contains spaces"));
    assert_eq!(
        c14n_hash(b"abc"),
        "sha256:742b30be1f17b269a0df04fe8f065f1e5588c2940952c441d0a0b5fb35ed45ab"
    );
}
