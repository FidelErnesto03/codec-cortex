use codec_cortex::{
    canonicalize, compile_hcortex, parse_cortex, render_hcortex, sha256_bytes,
};

const ROUNDTRIP_SOURCE: &str = include_str!("fixtures/roundtrip.cortex");
const ROUNDTRIP_CANONICAL: &str = include_str!("fixtures/roundtrip.canonical.cortex");
const ROUNDTRIP_HCORTEX: &str = include_str!("fixtures/roundtrip.hcortex.md");
const FULL_SOURCE: &str = include_str!("../examples/full.cortex");
const FULL_CANONICAL: &str = include_str!("../examples/full.canonical.cortex");
const FULL_HCORTEX: &str = include_str!("../examples/full.hcortex.md");

#[test]
fn canonical_bytes_match_python_reference() {
    let document = parse_cortex(ROUNDTRIP_SOURCE).expect("fixture must parse");
    assert_eq!(canonicalize(&document), ROUNDTRIP_CANONICAL);
}

#[test]
fn hcortex_bytes_match_python_reference() {
    let document = parse_cortex(ROUNDTRIP_SOURCE).expect("fixture must parse");
    assert_eq!(render_hcortex(&document), ROUNDTRIP_HCORTEX);
}

#[test]
fn hcortex_roundtrip_matches_canonical_bytes() {
    let (document, diagnostics) = compile_hcortex(ROUNDTRIP_HCORTEX);
    assert!(diagnostics.is_empty(), "unexpected diagnostics: {diagnostics:?}");
    let document = document.expect("canonical HCORTEX must compile");
    assert_eq!(canonicalize(&document), ROUNDTRIP_CANONICAL);
    assert_eq!(render_hcortex(&document), ROUNDTRIP_HCORTEX);
}

#[test]
fn canonicalization_is_idempotent_on_reference_fixture() {
    let first = canonicalize(&parse_cortex(ROUNDTRIP_SOURCE).unwrap());
    let second = canonicalize(&parse_cortex(&first).unwrap());
    assert_eq!(first.as_bytes(), second.as_bytes());
}

#[test]
fn comprehensive_fixture_matches_python_outputs() {
    let document = parse_cortex(FULL_SOURCE).unwrap();
    assert_eq!(canonicalize(&document), FULL_CANONICAL);
    assert_eq!(render_hcortex(&document), FULL_HCORTEX);
}

#[test]
fn inherited_open_attrs_projection_is_explicitly_pinned() {
    let document = parse_cortex(FULL_SOURCE).unwrap();
    let rendered = render_hcortex(&document);
    let (compiled, diagnostics) = compile_hcortex(&rendered);
    assert!(diagnostics.is_empty());
    let roundtrip = canonicalize(&compiled.unwrap());
    assert_ne!(roundtrip, FULL_CANONICAL);
    assert!(FULL_CANONICAL.contains("extra:z"));
    assert!(!roundtrip.contains("extra:z"));
}

#[test]
fn reference_hash_vectors_are_stable() {
    assert_eq!(
        sha256_bytes(ROUNDTRIP_CANONICAL.as_bytes()),
        "fbee0b99e464dfee332c2e6ed21f60b28c7f46764e66dc05b6efa243bf649c58"
    );
    assert_eq!(
        sha256_bytes(ROUNDTRIP_HCORTEX.as_bytes()),
        "35ed3d5381050ca31a775ecd62b0e16406a02b61b8d91e1e851102ca80556242"
    );
}

#[test]
fn parser_diagnostic_codes_match_python_contract() {
    let cases = [
        ("\u{FEFF}$0\n", "U001_BOM_FORBIDDEN"),
        (
            "$0\n$0:format{cortex:0.1,encoding:UTF-8}\n$0:format{cortex:0.1,encoding:UTF-8}\n",
            "G006_DUPLICATE_FORMAT",
        ),
        (
            "$0\n$0:format{cortex:9.9,encoding:UTF-8}\n",
            "G007_UNSUPPORTED_VERSION",
        ),
        (
            "$0\n$0:format{cortex:0.1,encoding:UTF-8}\nOBJ:Object{weight:H,fields:\"topic:text\",focus:topic,desc:\"Object\"}\n",
            "G016_SYMBOL_TYPE_REQUIRED",
        ),
        (
            "$0\n$0:format{cortex:0.1,encoding:UTF-8}\n$1\nOBJ:x{topic:y}\n",
            "I001_UNDECLARED_SYMBOL",
        ),
    ];

    for (source, expected) in cases {
        let error = parse_cortex(source).expect_err("case must be invalid");
        assert_eq!(error.code, expected);
    }
}

#[test]
fn hcortex_diagnostic_codes_match_python_contract() {
    let (document, diagnostics) = compile_hcortex("# no header\n");
    assert!(document.is_none());
    assert_eq!(diagnostics[0].code, "H400");

    let (document, diagnostics) = compile_hcortex("\u{FEFF}<!-- HCORTEX v=0.1 t=canonical -->\n");
    assert!(document.is_none());
    assert_eq!(diagnostics[0].code, "H490");
}
