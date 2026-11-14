<!-- HCORTEX v=1.0 t=canonical k=corpus -->

<!-- glossary -->
$0:KERNEL
$0:format{cortex:1.0,encoding:UTF-8,language:en}
$0:enum_phase{values:"P0|P1|P2|P3|P4"}
$0:enum_gate{values:"G1|G2|G3|G4|G5"}
$0:enum_level{values:"blocking|warning"}
RUL:rule{type:attrs,weight:H,focus:rule,desc:"Normative rule",fields:"rule:text|detail:text"}
CMD:cmd{type:attrs,weight:H,focus:command,desc:"Executable step",fields:"command:text|expect:text"}
MET:metric{type:attrs,weight:H,focus:definition,desc:"Metric",fields:"definition:text|unit:atom|formula:text?"}
HYP:hyp{type:attrs,weight:H,focus:statement,desc:"Hypothesis",fields:"statement:text|prediction:text|falsified:text"}
GATE:gate{type:attrs,weight:H,focus:criterion,desc:"Gate",fields:"criterion:text|evidence:text"}
ART:artifact{type:attrs,weight:M,focus:path,desc:"Artifact",fields:"path:text|content:text"}
RSK:risk{type:attrs,weight:M,focus:threat,desc:"Threat",fields:"threat:text|control:text"}
PRC:step{type:attrs-pos,weight:H,focus:action,desc:"Procedure step",pos:"action:text|expect:text|phase:atom"}
TMPL:template{type:bloque,weight:M,desc:"Template"}
TXT:note{type:cuerpo,weight:M,desc:"Rationale"}

<!-- /glossary -->

## §1: MISSION

<!-- schema:1 capa:CORE -->
### TXT:mission
This package instructs an autonomous agent to benchmark CODEC-CORTEX 1.0 from its
PyPI installation, scientifically and reproducibly. The agent must produce
evidence, not opinions: every claim it writes must point to an artifact and a
hash. Measure properties (fidelity, determinism, density, error precision,
auditability) and model-facing benefits (comprehension, generation validity),
against fair baselines (JSON, YAML, Markdown, XML, plain text).

### RUL:autonomy
| rule | detail |
|---|---|
| "The agent may choose models, questions and corpus only during pre-registration, never after seeing results." | "Freeze order: prereg -> runs -> analysis -> report." |

### RUL:non_goals
| rule | detail |
|---|---|
| "Do not claim CORTEX is faster, prettier or smaller in general. Claim only what a registered metric supports with its confidence interval." | "Art. XVII: no claim without reproducible evidence." |

### RUL:falsifiability
| rule | detail |
|---|---|
| "Every hypothesis carries an explicit falsifier. If the falsifier occurs, report failure, never rename the hypothesis." | "A benchmark that cannot fail is marketing." |

### TXT:fairness
Fair comparison means equal information, equal instruction budget and identical
questions across formats. Any format-specific tuning must be declared and
applied symmetrically. Baselines are not strawmen: use canonical, idiomatic
representations produced by standard serializers.

<!-- /schema:1 -->

## §2: PREPARATION

<!-- schema:2 capa:CORE -->
### RUL:environment
| rule | detail |
|---|---|
| "Python 3.10+, isolated venv, no network during measurement runs." | "Record OS, CPU, Python, pip and package versions in manifest.json." |

### CMD:install
| command | expect |
|---|---|
| "python -m pip install codec-cortex==1.0.0" | "import succeeds and codec_cortex.__version__ is 1.0.0" |

### CMD:verify
| command | expect |
|---|---|
| "python -m codec_cortex hash <file.cortex>" | "prints sha256:64hex; identical across repeated runs" |

### CMD:selfcheck
| command | expect |
|---|---|
| "python -m codec_cortex loss-report <this-package.cortex>" | "reversible true and losses empty; otherwise STOP and report a toolchain defect" |

### CMD:render
| command | expect |
|---|---|
| "python -m codec_cortex to-hcortex <file.cortex>" | "deterministic HCORTEX; same bytes on every run" |

### CMD:compile
| command | expect |
|---|---|
| "python -m codec_cortex from-hcortex <file.hcortex.md>" | "canonical CORTEX; roundtrip equals the source canonical form" |

### CMD:conformance
| command | expect |
|---|---|
| "python -m codec_cortex conformance" | "harness reports zero failures for the shipped corpus" |

### RUL:freeze
| rule | detail |
|---|---|
| "Before the first model call, write prereg.yaml and record its sha256 in manifest.json." | "G1 blocks execution until the freeze hash exists." |

<!-- /schema:2 -->

## §3: PREREGISTRATION

<!-- schema:3 capa:CORE -->
### HYP:h1_fidelity
| statement | prediction | falsified |
|---|---|---|
| "Every valid 1.0 document survives CORTEX to HCORTEX to CORTEX with an equal canonical form." | "fidelity_rate = 1.0 on the declared corpus" | "any divergence that no declared L4xx loss class explains" |

### HYP:h2_determinism
| statement | prediction | falsified |
|---|---|---|
| "Canonical bytes and HCORTEX render are a pure function of the AST within and across processes." | "byte_determinism = 1.0 across 5 repetitions" | "one differing byte for the same input" |

### HYP:h3_density
| statement | prediction | falsified |
|---|---|---|
| "For structured facts, CORTEX uses fewer tokens than idiomatic JSON." | "median token_density(cortex) lower than json" | "paired difference CI includes zero or favors JSON" |

### HYP:h4_comprehension
| statement | prediction | falsified |
|---|---|---|
| "Models answer content questions about a CORTEX document at least as accurately as about its JSON twin." | "accuracy(cortex) - accuracy(json) greater or equal to 0" | "paired CI entirely below zero after correction" |

### HYP:h5_generation
| statement | prediction | falsified |
|---|---|---|
| "Models instructed to answer in CORTEX produce a higher rate of schema-valid output than when instructed to answer in JSON." | "validity(cortex) greater than validity(json)" | "paired CI includes zero or favors JSON" |

### HYP:h6_errors
| statement | prediction | falsified |
|---|---|---|
| "Invalid documents yield the specific catalog code, not a generic failure." | "error_code_precision = 1.0 on the invalid corpus" | "one vector mapped to a wrong or missing code" |

### HYP:h7_audit
| statement | prediction | falsified |
|---|---|---|
| "A third party can detect a one-byte tamper from the artifact and its hash alone." | "tamper_detection = 1.0 over sampled cases" | "any undetected tamper" |

### RUL:design
| rule | detail |
|---|---|
| "Matrix: 6 formats x 2 or more declared models x 8 questions x R=5 repetitions. Fixed temperature, top_p, prompt verbatim." | "Declare exact model ids and dates; a model swap is a new preregistration." |

### RUL:scoring
| rule | detail |
|---|---|
| "Score with a deterministic rubric fixed before runs. If an LLM judge is used, validate it against a human sample and report agreement." | "Unvalidated judges are not evidence." |

### RUL:exclusions
| rule | detail |
|---|---|
| "Pre-register exclusion rules. Missing or failed runs count as failures; never drop them silently." | "Report n attempted, n completed, n failed per cell." |

<!-- /schema:3 -->

## §4: METRICS

<!-- schema:4 capa:CORE -->
### MET:fidelity_rate
| definition | unit | formula |
|---|---|---|
| "Share of corpus documents whose canonical form is identical after roundtrip." | ratio | "pass / n" |

### MET:byte_determinism
| definition | unit | formula |
|---|---|---|
| "Share of inputs with identical bytes across R repetitions." | ratio | "stable / n" |

### MET:token_density
| definition | unit | formula |
|---|---|---|
| "Tokens needed to express one structured fact, same tokenizer for all formats." | tokens_per_fact | "tokens / facts" |

### MET:answer_accuracy
| definition | unit | formula |
|---|---|---|
| "Share of content questions answered correctly, scoring fixed at pre-registration." | ratio | "correct / questions" |

### MET:generation_validity
| definition | unit | formula |
|---|---|---|
| "Share of model outputs that parse and validate against the declared contract." | ratio | "valid / attempts" |

### MET:error_code_precision
| definition | unit | formula |
|---|---|---|
| "Share of invalid vectors that produce the expected specific code." | ratio | "exact / vectors" |

### MET:tamper_detection
| definition | unit | formula |
|---|---|---|
| "Share of tampered artifacts whose hash mismatch is detected." | ratio | "detected / tampered" |

### MET:latency
| definition | unit | formula |
|---|---|---|
| "Wall-clock time per operation, median and p95." | ms | "quantile(elapsed, 0.5 and 0.95)" |

### MET:cost
| definition | unit | formula |
|---|---|---|
| "Total model tokens consumed per cell including prompt and completion." | tokens | "sum(prompt, completion)" |

<!-- /schema:4 -->

## §5: PROTOCOL

<!-- schema:5 capa:FLOW -->
### PRC:p0_setup
| action | expect | phase |
|---|---|---|
| "Create venv, install the package, record manifest.json and run the self-check commands." | "G1: manifest sha256 recorded" | P0 |

### PRC:p1_freeze
| action | expect | phase |
|---|---|---|
| "Build corpus and baselines, write prereg.yaml, seal both, record hashes." | "prereg and corpus hashes in manifest" | P0 |

### PRC:p2_deterministic
| action | expect | phase |
|---|---|---|
| "Run fidelity, determinism, density, error precision, latency and tamper checks without any LLM." | "metrics written per document" | P1 |

### PRC:p3_comprehension
| action | expect | phase |
|---|---|---|
| "For each model, format and question, run R=5 comprehension cells with identical prompts and settings." | "one JSON cell per attempt, no silent retries" | P2 |

### PRC:p4_generation
| action | expect | phase |
|---|---|---|
| "For each model and format, request a valid structured answer for 8 tasks, R=5, and validate raw output." | "raw output stored before scoring" | P3 |

### PRC:p5_analysis
| action | expect | phase |
|---|---|---|
| "Compute only pre-registered statistics: paired differences, Wilson intervals, Holm correction." | "stats.json with effect sizes and CIs" | P4 |

### PRC:p6_report
| action | expect | phase |
|---|---|---|
| "Write report.md, cite artifact and hash per claim, seal the run directory." | "G5: seal verifies, every claim traceable" | P4 |

<!-- /schema:5 -->

## §6: ARTIFACTS

<!-- schema:6 capa:DATA -->
### ART:manifest
| path | content |
|---|---|
| "runs/<run-id>/manifest.json" | "environment, versions, tokenizer, model ids, corpus and prereg sha256, start time" |

### ART:prereg
| path | content |
|---|---|
| "runs/<run-id>/prereg.yaml" | "hypotheses, falsifiers, matrix, R, scoring rubric, exclusions, analysis plan" |

### ART:cells
| path | content |
|---|---|
| "runs/<run-id>/cells/" | "one JSON per attempt with prompt, raw output, parser diagnostics, tokens, latency" |

### ART:scores
| path | content |
|---|---|
| "runs/<run-id>/scores/" | "one JSON per scored attempt with rubric fields and rater" |

### ART:stats
| path | content |
|---|---|
| "runs/<run-id>/stats.json" | "per metric: n, estimate, CI, paired test, effect size, corrected p" |

### ART:report
| path | content |
|---|---|
| "runs/<run-id>/report.md" | "sections defined in REPORT section, claims with artifact and hash" |

### ART:seal
| path | content |
|---|---|
| "runs/<run-id>/SHA256SUMS" | "seal of every artifact in the run, verifiable with sha256sum -c" |

### RUL:cell_template
| rule | detail |
|---|---|
| "TMPL:cell_schema is the member list of the JSON object; wrap it in braces to form cells/<cell>.json." | "Keeping the member list avoids delimiter ambiguity inside a bloque." |

### TMPL:cell_schema
```
"run": "<run-id>",
"cell": "<model>_<format>_<question>_r<k>",
"model": "<declared-id>",
"format": "cortex or json or yaml or markdown or xml or plaintext",
"question": "Q1",
"attempt": 1,
"prompt_sha256": "<64 hex>",
"raw_output": "<verbatim>",
"valid": true,
"diagnostics": [],
"tokens": {"prompt": 0, "completion": 0},
"latency_ms": 0
```

<!-- /schema:6 -->

## §7: GATES

<!-- schema:7 capa:CORE -->
### GATE:g1
| criterion | evidence |
|---|---|
| "Pre-registration frozen before any model call." | "prereg sha256 present in manifest and committed before first cell" |

### GATE:g2
| criterion | evidence |
|---|---|
| "Deterministic phase complete with results or declared defects." | "P1 metrics for every corpus document, none missing" |

### GATE:g3
| criterion | evidence |
|---|---|
| "Every planned cell accounted for as completed or failed." | "counts per cell match the matrix; failures reported as failures" |

### GATE:g4
| criterion | evidence |
|---|---|
| "Analysis uses only pre-registered tests and corrections." | "stats.json cites the hypothesis id per test" |

### GATE:g5
| criterion | evidence |
|---|---|
| "Every claim in the report cites artifact path and sha256." | "seal verifies and each claim line carries a path plus hash" |

<!-- /schema:7 -->

## §8: THREATS

<!-- schema:8 capa:CORE -->
### RSK:contamination
| threat | control |
|---|---|
| "Model may have memorized public CORTEX examples." | "Use held-out corpora and report provenance and dates; include a zero-shot unfamiliar corpus." |

### RSK:familiarity
| threat | control |
|---|---|
| "JSON and Markdown are far more common in training data." | "State it as a limitation and test with equal instruction budget; do not hide the asymmetry." |

### RSK:prompt_bias
| threat | control |
|---|---|
| "Wording and order change outcomes." | "Identical prompts across formats, fixed order, and a small prompt-robustness check." |

### RSK:tokenizer
| threat | control |
|---|---|
| "Density comparisons shift with the tokenizer." | "Use one declared tokenizer for all formats and report it." |

### RSK:judge
| threat | control |
|---|---|
| "An LLM judge may encode its own preferences." | "Validate against a human sample and report agreement; prefer deterministic rubrics." |

### RSK:cherry
| threat | control |
|---|---|
| "Selecting repetitions or questions after seeing results." | "Freeze the matrix and report all attempts; no post-hoc exclusions." |

### RSK:nonindependence
| threat | control |
|---|---|
| "Repetitions may be correlated by caching or temperature." | "Report per-repetition data; do not treat R=5 as 5 independent questions." |

<!-- /schema:8 -->

## §9: REPORT

<!-- schema:9 capa:DATA -->
### RUL:structure
| rule | detail |
|---|---|
| "Report sections: setup, preregistration, corpus and baselines, deterministic properties, comprehension, generation, threats, limitations, reproduction." | "Include the exact commands used." |

### RUL:claims
| rule | detail |
|---|---|
| "Every claim is one line with metric, estimate, CI, n, artifact path and hash." | "Example: fidelity_rate 1.000 [0.994, 1.000], n=70, cells/fidelity.json, sha256:abcd..." |

### RUL:negative
| rule | detail |
|---|---|
| "Report failed hypotheses with the same prominence as confirmed ones." | "A negative result is a valid deliverable." |

### RUL:repro
| rule | detail |
|---|---|
| "Provide a single command that re-runs the deterministic phase from the sealed corpus." | "Third party must reproduce P1 without any model call." |

### TMPL:report_skeleton
```
AGENT BENCHMARK REPORT - <run-id>
1. Setup: OS, CPU, Python, package version, tokenizer, model ids and dates.
2. Preregistration: sha256, matrix, R, rubric, exclusion rules.
3. Corpus and baselines: sizes, shapes, provenance, seals.
4. Deterministic properties: fidelity, determinism, density, error precision, tamper, latency.
5. Comprehension: accuracy per model and format, paired differences with CIs.
6. Generation: validity per model and format, failure modes, token cost.
7. Threats to validity: which controls were applied and which remain.
8. Limitations and negative results: failed hypotheses with the same prominence.
9. Reproduction: exact commands, including the deterministic-only rerun.
10. Claim table: metric, estimate, CI, n, artifact path, sha256.
```

<!-- /schema:9 -->

## §10: ANTI_PATTERNS

<!-- schema:10 capa:CORE -->
### RUL:no_metrics_from_thin_air
| rule | detail |
|---|---|
| "Never invent a metric after looking at data. A new question is a new run." | "Post-hoc metrics are exploratory and must be labeled as such." |

### RUL:no_dropped_failures
| rule | detail |
|---|---|
| "Never remove a failed attempt from the denominator." | "Silent exclusion is the most common way to fake a benchmark." |

### RUL:no_absolute_claims
| rule | detail |
|---|---|
| "Never write CORTEX is better. Write which metric, under which conditions, with which interval." | "Conditions include model, corpus, prompt and tokenizer." |

### RUL:no_toy_only
| rule | detail |
|---|---|
| "Do not benchmark only minimal documents. Include realistic, adversarial and long documents." | "Declare document sizes and shapes." |

### RUL:no_publication_without_seal
| rule | detail |
|---|---|
| "Do not publish results without a verifying seal and a manifest." | "G5 is blocking." |

<!-- /schema:10 -->

