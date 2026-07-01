---
view: display-only
reversible: false
profile: HCORTEX-HOWTO
source: skill/cortex/SKILL.md §3, docs/cortex/api/
mode: READABLE
---

# HCORTEX How-to Guides

> **source:** skill/cortex/SKILL.md §3:HDL:* · docs/cortex/api/*

Practical procedures for common tasks with CODEC-CORTEX. Each guide is self-contained.

---

## 1. How to create a `.cortex` file

| Step | Action | source |
|:----:|--------|--------|
| 1 | `cortex new myfile.cortex` | `docs/cortex/api/canonicalize.cortex` |
| 2 | Edit the generated file | `$0:canonical_sigils` |
| 3 | `cortex verify --strict myfile.cortex` | `docs/cortex/api/verify.cortex` |

**From scratch with explicit content:**

```bash
cat > myfile.cortex << 'EOF'
$0
GSIG:FCS{name:"focus",type:"attrs",risk:"H",layer:"Working",desc:"active attention anchor"}
GSIG:OBJ{name:"objective",type:"attrs",risk:"H",layer:"Working",desc:"active goal with success criterion"}

$1
IDN:artifact{name:"myfile",author:"user",version:"0.1",status:"draft"}

$3
FCS:primary{what:"Task description",priority:high,status:current,survive:min}
OBJ:first{goal:"Complete task",status:current,success:"verified",survive:min}
EOF
```

**Required sections for any .cortex:**

| Section | Content | Mandatory | source |
|:-------:|---------|:---------:|--------|
| `$0` | Glossary (sigil declarations) | ✅ Always | `$0:canonical_sigils` |
| `$1` | Identity (IDN, DOM, REF) | ✅ Always | `$1:IDN:project` |
| `$2`+ | Operational state (FCS, OBJ, etc.) | Depends | `$3:HDL:*` |

---

## 2. How to verify a `.cortex` file

| Action | Command | source |
|--------|---------|--------|
| Basic verification | `cortex verify --strict file.cortex` | `docs/cortex/api/verify.cortex` |
| VIEW coverage | `cortex verify-view file.cortex` | `docs/cortex/api/verify.cortex` |
| Structural roundtrip | `cortex roundtrip file.cortex` | `docs/cortex/api/convert.cortex` |
| Bidirectional roundtrip | `cortex roundtrip-bidir file.cortex` | `docs/cortex/api/convert.cortex` |
| Signature (E2) | `cortex verify --signature file.cortex` | `docs/cortex/api/verify.cortex` |
| Secret scan (E2) | `cortex doctor --scan-secrets file.cortex` | `docs/cortex/api/doctor.cortex` |

**What `--strict` checks:**

| Check | Code | source |
|-------|:----:|--------|
| Unknown sigil | `E003` | `!:extend_glossary` |
| Missing required field | `E032` | `$7:CNST:contract_*` |
| Empty critical field | `E034` | `$7:CNST:contract_*` |
| Level violation | `E023-030` | `$5:CNST:sep_l1` |
| View error | `E_VIEW_*` | `$13:VIEW:*` |

---

## 3. How to add VIEW directives

| Field | Values | source |
|-------|--------|--------|
| `kind` | `table`, `kv_table`, `prose`, `puml`, `numbered_list`, `callout` | `$13:VIEW:*` |
| `target` | `$N:SIGIL:name`, `$N:SIGIL:*`, `$N:NAME` | `$13:VIEW:*` |
| `reverse` | `rows_to_entries`, `row_to_attrs`, `body_to_cuerpo`, etc. | `$13:VIEW:*` |
| `fields` | Comma-separated field list | `$13:VIEW:*` |
| `preserve` | `verbatim` for PUML | `$13:VIEW:*` |

**Example:**

```cortex
$13
VIEW:my_view{kind:"table",target:"$3:FCS:*",reverse:"rows_to_entries",status:cur,title:"My Focus Entries"}
```

**Verify:**

| Step | Command | source |
|:----:|---------|--------|
| 1 | `cortex verify-view file.cortex` | `docs/cortex/api/verify.cortex` |

---

## 4. How to run benchmarks

| Action | Command | source |
|--------|---------|--------|
| List suites | `cortex benchmark --list` | `docs/cortex/api/benchmark.cortex` |
| Inspect a suite | `cortex benchmark --inspect v2.0.0` | `docs/cortex/api/benchmark.cortex` |
| JSON output | `cortex benchmark --list --format json` | `docs/cortex/api/benchmark.cortex` |

**Available suites:** v1.0.0, v2.0.0, v2.1.0 (4,840 runs each).

---

## 5. How to use `cortex docstring`

| Goal | Command | source |
|:----:|---------|--------|
| One command | `cortex docstring canonicalize` | `docs/cortex/api/docstring.cortex` |
| All commands | `cortex docstring --all` | `docs/cortex/api/docstring.cortex` |
| Custom docs root | `cortex docstring canonicalize --docs-root docs/cortex/api` | `docs/cortex/api/docstring.cortex` |
| JSON output | `cortex docstring canonicalize --format json` | `docs/cortex/api/docstring.cortex` |

**Workflow:**

| Step | Action |
|:----:|--------|
| 1 | Edit `docs/cortex/api/<command>.cortex` |
| 2 | `cortex verify docs/cortex/api/<command>.cortex --strict` |
| 3 | `cortex docstring <command>` |
| 4 | Review help reflects arguments, status, and limits |

---

## 6. How to recover legacy files

| Action | Command | source |
|--------|---------|--------|
| Basic recovery | `cortex recover legacy.cortex --out recovered.cortex` | `!hcortex_expand` |
| With audit trail | `cortex recover legacy.cortex --out recovered.cortex --embed-aud-rsk` | `!:extend_glossary` |

**What recovery does:**

1. Detects missing or incomplete `$0`.
2. Reconstructs a minimal glossary from apparent sigils.
3. Adds RSK entries for reconstructed sigils.
4. Optionally embeds AUD and RSK for traceability.
5. Validates the recovered file with `verify --strict`.
6. Returns non-zero exit code if the result is not fully conformant.

---

## 7. How to audit and scan for secrets

| Action | Command | source |
|--------|---------|--------|
| Start audit log | `cortex audit on` | `docs/cortex/api/audit.cortex` |
| Check status | `cortex audit status` | `docs/cortex/api/audit.cortex` |
| Snapshot | `cortex audit snapshot` | `docs/cortex/api/audit.cortex` |
| Secret scan | `cortex doctor --scan-secrets brain.cortex` | `docs/cortex/api/doctor.cortex` |
| Full diagnostic | `cortex doctor --strict` | `docs/cortex/api/doctor.cortex` |

**Secret patterns detected (E2):**

| Pattern | Example |
|---------|---------|
| API keys | `sk-...`, `api_key=...` |
| Passwords | `password=...`, `passwd=...` |
| Tokens | `token=...`, `secret=...` |
| AWS keys | `AKIA...` |
| Private keys | `-----BEGIN ... PRIVATE KEY-----` |
| URLs with credentials | `https://user:pass@host` |

---

## 8. How to close a session

| Step | Action | source |
|:----:|--------|--------|
| 1 | `cortex add brain.cortex --section 5 --sigil SES --name session_001 --attrs '...'` | `$3:HDL:session_close` |
| 2 | `cortex add brain.cortex --section 5 --sigil LNG --name observed_pattern --attrs '...'` | `$3:HDL:session_close` |
| 3 | `cortex add brain.cortex --section 6 --sigil NXT --name follow_up --attrs '...'` | `$3:HDL:session_close` |
| 4 | `cortex verify --strict brain.cortex` | `docs/cortex/api/verify.cortex` |
| 5 | `cortex doctor --scan-secrets brain.cortex` | `docs/cortex/api/doctor.cortex` |
| 6 | `git add brain.cortex && git commit -m "session: summary"` | `!:precommit_verify` |

---

## See also

| Topic | source |
|-------|--------|
| Full tutorial | `docs/en/hcortex/tutorials/getting-started.md` |
| Protocol explanation | `docs/en/hcortex/explanations/documentation-protocol.md` |
| Quick reference | `docs/en/hcortex/reference/README.md` |
