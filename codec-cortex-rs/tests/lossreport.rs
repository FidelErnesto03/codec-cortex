use std::fs;
use std::path::PathBuf;

use codec_cortex::lossreport::{build_loss_report, dumps_canonical, loss_case_name};
use serde_json::Value;

fn loss_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../conformance/1.0/loss")
}

fn manifest() -> Value {
    let raw = fs::read_to_string(loss_dir().join("manifest.json")).expect("manifest");
    serde_json::from_str(&raw).expect("manifest json")
}

#[test]
fn fixtures_are_byte_identical_to_expected() {
    let manifest = manifest();
    for fixture in manifest["fixtures"].as_array().expect("fixtures") {
        let id = fixture["id"].as_str().unwrap();
        let file = fixture["file"].as_str().unwrap();
        let expected_file = fixture["expected"].as_str().unwrap();
        let source = fs::read_to_string(loss_dir().join(file)).expect("fixture");
        let report = build_loss_report(&source, id).expect("report");
        let expected = fs::read_to_string(loss_dir().join(expected_file)).expect("expected");
        assert_eq!(dumps_canonical(&report), expected, "fixture {id}");
        let codes: Vec<String> = report["losses"]
            .as_array()
            .unwrap()
            .iter()
            .map(|item| item["code"].as_str().unwrap().to_string())
            .collect();
        let want: Vec<String> = fixture["codes"]
            .as_array()
            .unwrap()
            .iter()
            .map(|value| value.as_str().unwrap().to_string())
            .collect();
        assert_eq!(codes, want, "codes for {id}");
    }
}

#[test]
fn glossary_title_is_rejected_with_g042() {
    let source = fs::read_to_string(loss_dir().join("clean.cortex"))
        .unwrap()
        .replace("$0:KERNEL", "$0: Titulo");
    let error = build_loss_report(&source, "title").expect_err("must reject title");
    assert!(error.contains("G042_GLOSSARY_HEADER_INVALID"), "{error}");
}

#[test]
fn bare_glossary_roundtrips() {
    let source = fs::read_to_string(loss_dir().join("bare_glossary.cortex")).unwrap();
    let report = build_loss_report(&source, "bare").expect("report");
    assert_eq!(report["reversible"], true);
    assert_eq!(report["losses"].as_array().unwrap().len(), 0);
}

#[test]
fn case_name_strips_directory_and_extension() {
    assert_eq!(loss_case_name("/tmp/dir/doc.cortex"), "doc");
    assert_eq!(loss_case_name("-"), "stdin");
}
