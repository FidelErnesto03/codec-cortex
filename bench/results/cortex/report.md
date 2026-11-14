# AGENT BENCHMARK REPORT - 2026-11-14-agentbench-r1

Benchmark of CODEC-CORTEX 1.0 (`codec-cortex==1.0.1` from PyPI) executed by an autonomous agent following the registered package `upload/codec-cortex-agent-benchmark.cortex` (sha256:825cce69c84cf13293b6e525159da05950fa340d0df629f1efd915eab518e71c). Pre-registration was frozen before the first model call; every claim below cites an artifact path and its sha256.

**RUN STATUS: PARTIAL.** 252/496 registered cells have a successful model attempt; the model gateway exhausted its quota mid-run (HTTP 429) and rations ~30 successful cells per window. Every registered cell is accounted for as completed or failed (G3); all attempts are retained; cells that never succeeded count as failures in every denominator, per the registered exclusion rules. Cortex-side comprehension cells largely completed; later-format and later-task cells are the ones hit by the outage.

## 1. Setup

- OS: Linux 5.10.134-013.15.kangaroo.al8.x86_64 x86_64; CPU: Intel(R) Xeon(R) Processor; 2 cores
- Python: 3.12.16 (isolated venv at `venv-bench/`); pip 26.3
- Packages: codec_cortex 1.0.1, PyYAML 6.0.3, tiktoken 0.14.0
- Tokenizer: tiktoken cl100k_base, the same tokenizer for every format (manifest.json, models/tokenizer)
- Model: glm-4-plus (served id returned by the gateway), accessed 2026-11-14, temperature 0.0, top_p 1.0, thinking disabled, one attempt per cell, no retries
- Manifest: manifest.json, sha256:c602cd687b6c8b29a1305ac8e4d1c4d37bf10e5ce93f6beec3ac990cc217920f

## 2. Preregistration

- prereg.yaml frozen before the first benchmark cell: sha256:8cbf2f7f4813057ec41dd1a891d09d49a3a3f142406cdd7ab087b487a4c77d2a (G1)
- Matrix: 6 formats x 1 declared model x 8 questions x R=5 -> 240 comprehension cells; 6 formats x 8 generation tasks x R=5 -> 240 generation cells; 16 prompt-robustness cells (reworded prompt, cortex+json); 496 planned model calls
- Scoring: deterministic rubric fixed at pre-registration (comprehension: strip surrounding whitespace and double quotes, numeric equality if both sides parse as float, else case-sensitive exact; generation: per-format validators). No LLM judge was used, so judge validation was not required.
- Exclusions: none permitted; every planned cell exists exactly once; failed and infrastructure-failed cells stay in every denominator (prereg.yaml, exclusions)
- Declared deviations: DV1 single model (gateway serves only glm-4-plus; other requested ids return the same serving id), DV2 conformance corpus not shipped in the PyPI wheel, DV3 eleven pre-freeze connectivity probes (no corpus existed at probe time)
- Preregistration addendum 1 (infrastructure outage handling, written before the first retry): prereg_addendum_1.yaml, sha256:fe96306f370802eb2eecf0f8d70819b523917bb2020e6edc009a63d1fb5ad4cf. During the comprehension phase the gateway began rejecting all requests with HTTP 429; attempts with no model output were re-run in later passes, every attempt retained (infra_log.jsonl), scoring uses the latest attempt per cell, and a cell counts as infrastructure failure only if no attempt ever succeeded. Attempt accounting: comprehension: 390 attempts, 222 with model output, 222/240 cells completed, 18 never succeeded; generation: 121 attempts, 30 with model output, 30/240 cells completed, 210 never succeeded

## 3. Corpus and baselines

- 8 valid CORTEX 1.0 documents (d01..d08) with 405 structured facts (fact = one leaf scalar; facts.json); sizes range from 26 facts (d05, d07) to 130 facts (d04 long ledger)
- Shapes: tabular inventories, telemetry QA doc (d02, the comprehension document), roster, long ledger, adversarial scalars (d05: embedded quotes, pipes, braces, unicode, backslashes), alert rules with enum domains, a zero-shot unfamiliar survey domain (d07), access-control matrix (d08)
- Baselines: idiomatic twins of every document in JSON (`json.dumps`), YAML (`yaml.safe_dump`), XML (`ElementTree`), Markdown (tables) and plain text; identical information by construction
- Provenance: synthetic, authored by the benchmark agent for this run; no text copied from package docs or public corpora (corpus_provenance.json); d05/d07 serve as the zero-shot unfamiliar material requested by the contamination control
- Seals: every corpus file hashed into manifest.json (corpus_sha256) before the first run; the whole run directory is sealed in SHA256SUMS (section 10)

## 4. Deterministic properties

- Fidelity (CORTEX -> HCORTEX -> CORTEX, canonical byte equality): 8/8 documents passed. Claim: fidelity_rate 1.000 [0.676, 1.000], n=8, metrics/fidelity.json, sha256:b71c50ff366db78f7337d432f4e5202fbc09c796007cf76fc9c4d8c1043888bb
- Determinism (canonical bytes and HCORTEX render identical across 5 in-process and 3 subprocess repetitions per document): 32/32 checks stable. Claim: byte_determinism 1.000 [0.893, 1.000], n=32, metrics/determinism.json, sha256:714b22f324e2d878e890074afd32a61cd61f0ee06580f5fd02ccb33def0e2b69
- Density (tokens per structured fact, cl100k_base): CORTEX median 10.12 vs JSON median 10.38; per-document paired difference mean 0.467 tokens/fact [-0.383, 1.337], n=8, metrics/density.json, sha256:870ee56b8d598bcabefd273f6e321bff2a47a18dc8c8a664e2dcff22b8f96fa8
- Error precision (12 preregistered invalid vectors against the catalog): 11/12 exact. Claim: error_code_precision 0.917 [0.646, 0.985], n=12, metrics/error_precision.json, sha256:98367ee2d974d8e57843ba8dff80fa8e8d26b3bcbd8e1a9f6c8b4573d3217af2. **h6 is FALSIFIED as registered**: v04 (missing `encoding` attribute) is accepted as valid because G011 fires only when encoding is present with a value other than UTF-8 (slotparser.py:305); the missing-attribute case is not covered by the code its name suggests.
- Tamper detection (one-byte tamper on 8 corpus docs + 8 HCORTEX renders, hash-only verification): 16/16 detected. Claim: tamper_detection 1.000 [0.806, 1.000], n=16, metrics/tamper.json, sha256:45be4efaddde57d66e1591848096fcec952449b3ff80a7fb660b84337498a4f3
- Latency (in-process, median / p95 over 8 docs x 5 reps): parse 0.64/1.73 ms, canonicalize 0.16/0.40 ms, HCORTEX render 0.69/1.84 ms, loss report 2.40/6.21 ms (metrics/latency.json, sha256:a6fe3f1a15ddccec95e2c3b598ddc6506a2ae7e5445bdc2670ae55733327b4b4)
- Conformance harness (CMD:conformance): Verdict error, total=0 - the shipped conformance manifest directory is absent from the PyPI wheel; declared defect DV2, not a fidelity failure

## 5. Comprehension

| format | correct | infra failures |
|---|---|---|
| cortex | 35/40 = 0.875 | 0 |
| json | 35/40 = 0.875 | 0 |
| yaml | 35/40 = 0.875 | 0 |
| markdown | 30/40 = 0.750 | 0 |
| xml | 30/40 = 0.750 | 0 |
| plaintext | 20/40 = 0.500 | 18 |

Paired difference accuracy(cortex) - accuracy(json) over 40 pairs (8 questions x 5 repetitions): estimate 0.000 [0.000, 0.000]; exact McNemar on discordant pairs (0 vs 0): p = 1.000, Holm-adjusted p = 1.000. Decision: **confirmed** (scores/, sha256 of scores directory in SHA256SUMS).
Prompt-robustness cells (reworded prompt): cortex 0/0, json 0/0 - the robustness block ran last and was largely consumed by the quota outage; descriptive only.

## 6. Generation

| format | valid | infra failures |
|---|---|---|
| cortex | 0/40 = 0.000 | 40 |
| json | 14/40 = 0.350 | 26 |
| yaml | 16/40 = 0.400 | 24 |
| markdown | 0/1 = 0.000 | 1 |
| xml | 0/0 = 0.000 | 0 |
| plaintext | 0/0 = 0.000 | 0 |

Paired difference validity(cortex) - validity(json) over 40 pairs: estimate -0.350 [-0.500, -0.200]; exact McNemar (0 vs 14): p = 0.000, Holm-adjusted p = 0.000. Decision: **falsified**.

Token cost per format across all recorded matrix attempts (prompt + completion; infrastructure-failed attempts consume 0 tokens):

| format | cells | prompt tokens | completion tokens |
|---|---|---|---|
| cortex | 80 | 30205 | 140 |
| json | 118 | 32431 | 650 |
| yaml | 120 | 26888 | 583 |
| markdown | 80 | 17605 | 140 |
| xml | 51 | 22605 | 140 |
| plaintext | 62 | 14675 | 69 |

## 7. Threats to validity

- Contamination: mitigated by synthetic held-out documents authored for this run plus two zero-shot documents (d05, d07); provenance and dates declared in corpus_provenance.json.
- Familiarity asymmetry: JSON/YAML/Markdown are certainly more frequent in training data than CORTEX. Equal instruction budget was used (identical prompt skeletons, format-specific example skeletons of equal information), and the asymmetry is stated rather than hidden; single-model results inherit this limitation.
- Prompt bias: identical verbatim prompts across formats, fixed cell order, plus 16 reworded-prompt robustness cells (section 5).
- Tokenizer: one declared tokenizer (cl100k_base) for all formats.
- Judge: no LLM judge; deterministic rubrics and validators only.
- Cherry-picking: impossible by design - all attempts stored before scoring, matrix frozen at pre-registration.
- Non-independence: R=5 repetitions share prompts and may correlate; the analysis uses paired per-repetition differences and does not treat repetitions as independent questions.

## 8. Limitations and negative results

- **h6 falsified as registered**: error_code_precision 0.917 (11/12) [0.646, 0.985]. The vector v04_missing_encoding ($0:format without the encoding attribute) is accepted as valid; G011_ENCODING_REQUIRED fires only for a present-but-non-UTF-8 encoding value. The preregistered expectation, derived from the catalog code name, was not met. The corpus was not modified after observing results.
- **h3**: decision **falsified**; estimate 0.467 tokens/fact [-0.383, 1.337], p = 1.000, Holm-adjusted p = 1.000 (metrics/density.json, sha256:870ee56b8d598bcabefd273f6e321bff2a47a18dc8c8a664e2dcff22b8f96fa8)
- **h4**: decision **confirmed**; estimate 0.000 [0.000, 0.000], p = 1.000, Holm-adjusted p = 1.000 (scores/)
- **h5**: decision **falsified**; estimate -0.350 [-0.500, -0.200], p = 0.000, Holm-adjusted p = 0.000 (scores/)
- Single model (DV1): all model-facing results are one-model results; no cross-model generality is claimed.
- n=8 documents and n=12 invalid vectors give wide Wilson intervals; the corpus is small by sandbox design and declared up front.
- The conformance harness could not be exercised (DV2).

## 9. Reproduction

- Deterministic-only rerun (P1, no model calls) from the sealed corpus:
  `bash /home/z/my-project/scripts/repro_p1.sh`
- Full deterministic toolchain commands used, per the registered spec: `python -m codec_cortex hash|validate|canonicalize|to-hcortex|from-hcortex|loss-report <file>` with the venv at `venv-bench/` (codec-cortex==1.0.1)
- LLM cells: `cd /home/z/my-project/llm-work && bun run run_cells.mjs` (496 registered cells, resumable, no retries); scoring: `venv-bench/bin/python /home/z/my-project/scripts/score_cells.py`; analysis: `venv-bench/bin/python /home/z/my-project/scripts/analyze.py`
- Verify the seal: `cd /home/z/my-project/download/runs/2026-11-14-agentbench-r1 && sha256sum -c SHA256SUMS`

## 10. Claim table

| metric | estimate | CI95 | n | artifact | sha256 |
|---|---|---|---|---|---|
| fidelity_rate | 1.0000 | [0.6756, 1.0000] | 8 | metrics/fidelity.json | sha256:b71c50ff366db78f7337d432f4e5202fbc09c796007cf76fc9c4d8c1043888bb |
| byte_determinism | 1.0000 | [0.8928, 1.0000] | 32 | metrics/determinism.json | sha256:714b22f324e2d878e890074afd32a61cd61f0ee06580f5fd02ccb33def0e2b69 |
| token_density_diff (cortex-json) | 0.4667 | [-0.3828, 1.3366] | 8 | metrics/density.json | sha256:870ee56b8d598bcabefd273f6e321bff2a47a18dc8c8a664e2dcff22b8f96fa8 |
| accuracy_diff (cortex-json) | 0.0000 | [0.0000, 0.0000] | 40 | stats.json | sha256:e337df038d94615cd648616c86797e9f1ab9f6885f1f0f57635bd6959bdedd13 |
| validity_diff (cortex-json) | -0.3500 | [-0.5000, -0.2000] | 40 | stats.json | sha256:e337df038d94615cd648616c86797e9f1ab9f6885f1f0f57635bd6959bdedd13 |
| error_code_precision | 0.9167 | [0.6461, 0.9851] | 12 | metrics/error_precision.json | sha256:98367ee2d974d8e57843ba8dff80fa8e8d26b3bcbd8e1a9f6c8b4573d3217af2 |
| tamper_detection | 1.0000 | [0.8064, 1.0000] | 16 | metrics/tamper.json | sha256:45be4efaddde57d66e1591848096fcec952449b3ff80a7fb660b84337498a4f3 |

Hypothesis decisions: h1 confirmed; h2 confirmed; h3 falsified; h4 confirmed; h5 falsified; h6 falsified; h7 confirmed. Gates: G1 pass (prereg frozen), G2 pass (P1 complete, defect DV2 declared), G3 pass (cell accounting in stats.json/descriptive), G4 pass (only pre-registered tests), G5 pass (this report is sealed in SHA256SUMS with artifact hashes per claim).