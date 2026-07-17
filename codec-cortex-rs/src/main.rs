#![forbid(unsafe_code)]

use std::fs;
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use clap::{Parser, Subcommand, ValueEnum};
use codec_cortex::{
    c14n_hash, canonicalize, compile_hcortex, parse_cortex, render_hcortex,
    run_all_tests, sha256_bytes,
};
use serde_json::json;

#[derive(Debug, Parser)]
#[command(name = "cortex", version, about = "CORTEX 0.1 / C14N-0.1 / HCORTEX-0.1 codec")]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Debug, Subcommand)]
enum Command {
    /// Parse CORTEX and emit the logical AST as JSON.
    Parse { input: PathBuf, #[arg(short, long)] output: Option<PathBuf> },
    /// Validate CORTEX syntax and glossary contracts.
    Validate { input: PathBuf, #[arg(long)] json: bool },
    /// Emit canonical CORTEX bytes.
    Canonicalize { input: PathBuf, #[arg(short, long)] output: Option<PathBuf> },
    /// Render canonical HCORTEX.
    ToHcortex { input: PathBuf, #[arg(short, long)] output: Option<PathBuf> },
    /// Compile HCORTEX to canonical CORTEX or AST JSON.
    FromHcortex {
        input: PathBuf,
        #[arg(short, long)] output: Option<PathBuf>,
        #[arg(long, value_enum, default_value = "cortex")] format: OutputFormat,
    },
    /// Compute ordinary SHA-256 or the domain-separated C14N hash.
    Hash { input: PathBuf, #[arg(long)] raw: bool },
    /// Compare two documents by canonical bytes.
    Compare { left: PathBuf, right: PathBuf, #[arg(long)] json: bool },
    /// Show a compact structural summary.
    Inspect { input: PathBuf, #[arg(long)] json: bool },
    /// Run the Python-compatible F3/F4 conformance harness.
    Conformance {
        c14n_dir: PathBuf,
        hcortex_dir: PathBuf,
        #[arg(short, long, default_value = "rev-report-rs.json")] report: PathBuf,
    },
}

#[derive(Debug, Clone, Copy, ValueEnum)]
enum OutputFormat { Cortex, Ast }

fn read_input(path: &Path) -> Result<String, String> {
    if path == Path::new("-") {
        let mut text = String::new();
        io::stdin().read_to_string(&mut text).map_err(|e| e.to_string())?;
        Ok(text)
    } else {
        fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))
    }
}

fn write_output(path: Option<&Path>, bytes: &[u8]) -> Result<(), String> {
    if let Some(path) = path {
        fs::write(path, bytes).map_err(|e| format!("{}: {e}", path.display()))
    } else {
        io::stdout().write_all(bytes).map_err(|e| e.to_string())
    }
}

fn report_error(error: impl std::fmt::Display) -> ExitCode {
    eprintln!("{error}");
    ExitCode::FAILURE
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    match run(cli.command) {
        Ok(code) => code,
        Err(error) => report_error(error),
    }
}

fn run(command: Command) -> Result<ExitCode, String> {
    match command {
        Command::Parse { input, output } => {
            let source = read_input(&input)?;
            let doc = parse_cortex(&source).map_err(|e| e.to_string())?;
            let json = serde_json::to_vec_pretty(&doc).map_err(|e| e.to_string())?;
            write_output(output.as_deref(), &json)?;
            if output.is_none() { println!(); }
            Ok(ExitCode::SUCCESS)
        }
        Command::Validate { input, json: json_output } => {
            let source = read_input(&input)?;
            match parse_cortex(&source) {
                Ok(doc) => {
                    if json_output {
                        println!("{}", serde_json::to_string_pretty(&json!({
                            "valid": true,
                            "sections": doc.sections.len(),
                            "symbols": doc.glossary.symbols.len()
                        })).unwrap());
                    } else { println!("VALID"); }
                    Ok(ExitCode::SUCCESS)
                }
                Err(error) => {
                    if json_output { println!("{}", serde_json::to_string_pretty(&json!({"valid":false,"diagnostic":error})).unwrap()); }
                    else { eprintln!("{error}"); }
                    Ok(ExitCode::FAILURE)
                }
            }
        }
        Command::Canonicalize { input, output } => {
            let doc = parse_cortex(&read_input(&input)?).map_err(|e| e.to_string())?;
            write_output(output.as_deref(), canonicalize(&doc).as_bytes())?;
            Ok(ExitCode::SUCCESS)
        }
        Command::ToHcortex { input, output } => {
            let doc = parse_cortex(&read_input(&input)?).map_err(|e| e.to_string())?;
            write_output(output.as_deref(), render_hcortex(&doc).as_bytes())?;
            Ok(ExitCode::SUCCESS)
        }
        Command::FromHcortex { input, output, format } => {
            let (doc, diagnostics) = compile_hcortex(&read_input(&input)?);
            if diagnostics.iter().any(|d| d.severity == "error") || doc.is_none() {
                return Err(serde_json::to_string_pretty(&diagnostics).unwrap_or_else(|_| "HCORTEX compilation failed".into()));
            }
            let doc = doc.unwrap();
            let bytes = match format {
                OutputFormat::Cortex => canonicalize(&doc).into_bytes(),
                OutputFormat::Ast => serde_json::to_vec_pretty(&doc).map_err(|e| e.to_string())?,
            };
            write_output(output.as_deref(), &bytes)?;
            if matches!(format, OutputFormat::Ast) && output.is_none() { println!(); }
            Ok(ExitCode::SUCCESS)
        }
        Command::Hash { input, raw } => {
            let doc = parse_cortex(&read_input(&input)?).map_err(|e| e.to_string())?;
            let canonical = canonicalize(&doc);
            println!("{}", if raw { sha256_bytes(canonical.as_bytes()) } else { c14n_hash(canonical.as_bytes()) });
            Ok(ExitCode::SUCCESS)
        }
        Command::Compare { left, right, json: json_output } => {
            let left_doc = parse_cortex(&read_input(&left)?).map_err(|e| e.to_string())?;
            let right_doc = parse_cortex(&read_input(&right)?).map_err(|e| e.to_string())?;
            let left_canonical = canonicalize(&left_doc);
            let right_canonical = canonicalize(&right_doc);
            let equivalent = left_canonical == right_canonical;
            if json_output {
                println!("{}", serde_json::to_string_pretty(&json!({
                    "equivalent": equivalent,
                    "left_sha256": sha256_bytes(left_canonical.as_bytes()),
                    "right_sha256": sha256_bytes(right_canonical.as_bytes())
                })).unwrap());
            } else { println!("{}", if equivalent { "EQUIVALENT" } else { "DIFFERENT" }); }
            Ok(if equivalent { ExitCode::SUCCESS } else { ExitCode::from(2) })
        }
        Command::Inspect { input, json: json_output } => {
            let doc = parse_cortex(&read_input(&input)?).map_err(|e| e.to_string())?;
            let idea_count: usize = doc.sections.iter().map(|s| s.ideas.len()).sum();
            let summary = json!({
                "cortex_version": doc.cortex_version,
                "encoding": doc.encoding,
                "sections": doc.sections.len(),
                "ideas": idea_count,
                "symbols": doc.glossary.symbols.len(),
                "enums": doc.glossary.enums.len(),
                "micros": doc.glossary.micros.len(),
                "namespaces": doc.glossary.namespaces.len(),
                "extensions": doc.glossary.extensions.len()
            });
            if json_output { println!("{}", serde_json::to_string_pretty(&summary).unwrap()); }
            else {
                println!("CORTEX {} / {}", summary["cortex_version"].as_str().unwrap(), summary["encoding"].as_str().unwrap());
                println!("sections={} ideas={} symbols={}", summary["sections"], summary["ideas"], summary["symbols"]);
            }
            Ok(ExitCode::SUCCESS)
        }
        Command::Conformance { c14n_dir, hcortex_dir, report } => {
            let result = run_all_tests(&c14n_dir, &hcortex_dir);
            let bytes = serde_json::to_vec_pretty(&result).map_err(|e| e.to_string())?;
            fs::write(&report, bytes).map_err(|e| format!("{}: {e}", report.display()))?;
            println!("\nReport written to: {}", report.display());
            Ok(if matches!(result.verdict.as_str(), "PASS" | "CONDITIONAL_PASS") { ExitCode::SUCCESS } else { ExitCode::FAILURE })
        }
    }
}
