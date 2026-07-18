#!/usr/bin/env python3
"""
HCORTEX Transformer — Bidirectional CORTEX ↔ HCORTEX with paired schemas.

render(cortex_text: str) -> str   — CORTEX → HCORTEX (canonical, reversible)
compile(hcortex_text: str) -> str  — HCORTEX → CORTEX (exact reconstruction)

CLI: --render, --compile, --roundtrip, --corpus DIR
"""
import re, sys, json, argparse
from pathlib import Path

# ── Shape → Schema mapping ──────────────────────────────────────────
SHAPE_SCHEMA = {
    "attrs": "table",
    "attrs-pos": "table",
    "cuerpo": "prose",
    "bloque": "diagram",
    "relacion": "table",
}

# ── CORTEX Parser ───────────────────────────────────────────────────

def _parse_attrs_body(body: str) -> dict:
    """Parse key:val,key:val,... respecting quoted values and list values."""
    pairs = {}
    i = 0
    n = len(body)
    while i < n:
        while i < n and body[i] in " ,":
            i += 1
        if i >= n:
            break
        key_start = i
        while i < n and body[i] != ":":
            i += 1
        key = body[key_start:i].strip()
        if i >= n:
            break
        i += 1
        if i < n and body[i] == '"':
            i += 1
            val_chars = []
            while i < n:
                if body[i] == '\\' and i + 1 < n:
                    val_chars.append(body[i])
                    val_chars.append(body[i + 1])
                    i += 2
                elif body[i] == '"':
                    i += 1
                    break
                else:
                    val_chars.append(body[i])
                    i += 1
            val = "".join(val_chars)
        elif i < n and body[i] == "[":
            depth = 1
            i += 1
            start = i
            while i < n and depth > 0:
                if body[i] == "[":
                    depth += 1
                elif body[i] == "]":
                    depth -= 1
                i += 1
            val = "[" + body[start:i - 1] + "]"
        else:
            val_start = i
            while i < n and body[i] not in ",}":
                i += 1
            val = body[val_start:i].strip()
        pairs[key] = val
    return pairs


def _parse_glossary_sigils(text: str) -> dict:
    """Extract full sigil definitions from $0. Returns {sigil_lower: {shape, fields, focus, ...}}."""
    sigils = {}
    in_glossary = False
    for line in text.split("\n"):
        s = line.strip()
        if s == "$0":
            in_glossary = True
            continue
        if in_glossary:
            if re.match(r"\$[1-9]", s):
                break
            if s.startswith("#") or not s:
                continue
            if "type:" in s and "{" in s:
                sig = s.split(":")[0].lower()
                # Remove namespace prefix
                if "::" in sig:
                    sig = sig.split("::")[-1]
                inner = s[s.index("{") + 1:]
                if inner.rstrip().endswith("}"):
                    inner = inner[:inner.rstrip().rfind("}")]
                attrs = _parse_attrs_body(inner)
                shape = attrs.get("type", "")
                sigils[sig] = {
                    "shape": shape,
                    "fields": attrs.get("fields", ""),
                    "pos": attrs.get("pos", ""),
                    "focus": attrs.get("focus", ""),
                    "weight": attrs.get("weight", "B"),
                    "desc": attrs.get("desc", ""),
                    "open": attrs.get("open", ""),
                }
    return sigils


def _extract_sigil_name(line: str) -> tuple:
    """Extract (sigil, name, rest) from a CORTEX idea line."""
    m = re.match(r"((?:[a-zA-Z_][\w]*::)?[A-Z][A-Z0-9_]*):([\w_-]+)(.*)$", line.strip())
    if m:
        return m.group(1), m.group(2), m.group(3)
    return None, None, None


def parse_cortex(text: str) -> dict:
    """
    Parse CORTEX into structured form.
    Returns: {glossary_lines, sigils, sections: [{id, title, ideas: [{sigil, name, shape, body_raw, payload, line}]}]}
    """
    result = {"glossary_lines": [], "sigils": {}, "sections": []}
    in_glossary = False
    glossary_buf = []
    current_section = None

    for line in text.split("\n"):
        s = line.strip()

        if s == "$0":
            in_glossary = True
            glossary_buf.append(line)
            continue

        if in_glossary:
            if re.match(r"\$[1-9]", s):
                in_glossary = False
                result["glossary_lines"] = glossary_buf[:]
                result["sigils"] = _parse_glossary_sigils("\n".join(glossary_buf))
                m = re.match(r"\$(\d+):?\s*(.*)", s)
                if m:
                    sec_id = int(m.group(1))
                    raw_title = m.group(2).strip()
                    has_title = ":" in s and raw_title
                    title = raw_title if raw_title else f"Sección {sec_id}"
                    current_section = {"id": sec_id, "title": title, "has_explicit_title": has_title, "ideas": []}
                    result["sections"].append(current_section)
                continue
            if s.startswith("#"):
                glossary_buf.append(line)
                continue
            glossary_buf.append(line)
            continue

        m = re.match(r"\$(\d+):?\s*(.*)", s)
        if m:
            sec_id = int(m.group(1))
            raw_title = m.group(2).strip()
            has_title = ":" in s and raw_title
            title = raw_title if raw_title else f"Sección {sec_id}"
            current_section = {"id": sec_id, "title": title, "has_explicit_title": has_title, "ideas": []}
            result["sections"].append(current_section)
            continue

        if current_section is not None and s and not s.startswith("#"):
            sigil, name, rest = _extract_sigil_name(s)
            if sigil and name:
                sig_lower = sigil.lower()
                sig_clean = sig_lower.split("::")[-1] if "::" in sig_lower else sig_lower
                sig_info = result["sigils"].get(sig_clean, result["sigils"].get(sigil.lower(), {}))
                shape = sig_info.get("shape", "") if isinstance(sig_info, dict) else ""

                if not shape:
                    if rest.startswith("|"):
                        shape = "attrs-pos"
                    elif rest.startswith("{") and "\n" in rest:
                        shape = "bloque"
                    elif rest.startswith("{"):
                        shape = "attrs"
                    else:
                        shape = "prose"

                payload = _body_to_payload(rest, shape)

                current_section["ideas"].append({
                    "sigil": sigil, "name": name, "shape": shape,
                    "body_raw": rest, "payload": payload, "line": line,
                })

    if in_glossary and glossary_buf:
        result["glossary_lines"] = glossary_buf[:]
        result["sigils"] = _parse_glossary_sigils("\n".join(glossary_buf))

    return result


def _body_to_payload(rest: str, shape: str) -> dict | str:
    """Parse CORTEX body into payload dict/string."""
    if shape == "attrs-pos":
        vals = []
        i = 1
        while i < len(rest):
            if i < len(rest) and rest[i] == '"':
                i += 1
                val_chars = []
                while i < len(rest):
                    if rest[i] == '\\' and i + 1 < len(rest):
                        val_chars.append(rest[i + 1])
                        i += 2
                    elif rest[i] == '"':
                        i += 1
                        break
                    else:
                        val_chars.append(rest[i])
                        i += 1
                vals.append("".join(val_chars))
                while i < len(rest) and rest[i] != '|':
                    i += 1
                if i < len(rest):
                    i += 1
            else:
                val_start = i
                while i < len(rest) and rest[i] != '|' and rest[i] != '\n':
                    i += 1
                vals.append(rest[val_start:i].strip())
                if i < len(rest) and rest[i] == '|':
                    i += 1
        return {"positional": vals}

    elif shape == "bloque":
        if rest.startswith("{") and "\n" in rest:
            inner = rest[rest.index("\n"):]
            if inner.rstrip().endswith("}"):
                inner = inner[:inner.rstrip().rfind("}")].rstrip()
            return inner.strip()
        elif rest.startswith("{") and rest.endswith("}"):
            return rest[1:-1].strip()
        return rest.strip()

    elif shape == "cuerpo":
        if rest.startswith("{"):
            inner = rest[1:]
            if inner.rstrip().endswith("}"):
                inner = inner.rstrip()[:-1]
            if "\n" in inner:
                inner = inner.strip()
            return inner.strip()
        return rest.strip()

    elif shape == "relacion":
        parts = rest.split("|")
        vals = [p.strip() for p in parts if p.strip()]
        return {"positional": vals}

    else:  # attrs
        if rest.startswith("{"):
            inner = rest[1:]
            if inner.rstrip().endswith("}"):
                inner = inner[:inner.rstrip().rfind("}")]
            return _parse_attrs_body(inner)
        return {}


# ── CORTEX → HCORTEX Render ────────────────────────────────────────

def render(cortex_text: str) -> str:
    """Render CORTEX → HCORTEX with paired schemas and hidden metadata for exact roundtrip."""
    parsed = parse_cortex(cortex_text)
    lines = ["<!-- HCORTEX v=0.1 t=canonical -->", ""]

    # Glossary block
    glossary_block = _render_glossary_block(parsed)
    if glossary_block:
        lines.append(glossary_block)
        lines.append("")

    for sec in parsed["sections"]:
        n = sec["id"]
        has_title = sec.get("has_explicit_title", True)
        title = sec.get("title", "")
        if has_title and title:
            lines.append(f"## §{n}: {title}")
        else:
            lines.append(f"## §{n}")
        lines.append("")

        if not sec["ideas"]:
            continue

        # Determine dominant schema for this section
        schema = _dominant_schema(sec, parsed["sigils"])

        lines.append(f"<!-- {schema}:{n} -->")

        for idea in sec["ideas"]:
            _render_idea_canonical(idea, schema, lines)

        lines.append(f"<!-- /{schema}:{n} -->")
        lines.append("")

    return "\n".join(lines)


def _dominant_schema(sec: dict, sigils: dict) -> str:
    """Determine the schema for this section based on its ideas."""
    # If all ideas have same shape, use that
    shapes = set()
    for idea in sec["ideas"]:
        sig_clean = idea["sigil"].lower().split("::")[-1]
        shape = idea["shape"]
        shapes.add(shape)
    if len(shapes) == 1:
        shape = list(shapes)[0]
        return SHAPE_SCHEMA.get(shape, "prose")
    # Mixed section: use prose as fallback
    # But check if we can infer from sigils
    for idea in sec["ideas"]:
        sig_clean = idea["sigil"].lower().split("::")[-1]
        if sig_clean in sigils:
            shape = sigils[sig_clean].get("shape", "")
            if shape in SHAPE_SCHEMA:
                return SHAPE_SCHEMA[shape]
    return "prose"


def _render_glossary_block(parsed: dict) -> str:
    """Build glossary comment block with ALL glossary entries."""
    glossary_lines = parsed.get("glossary_lines", [])
    entries = []
    for line in glossary_lines:
        s = line.strip()
        if not s or s.startswith("#") or s == "$0":
            continue
        entries.append(s)
    if not entries:
        return ""
    return "<!-- glossary\n" + "\n".join(entries) + "\n-->"


def _render_idea_canonical(idea: dict, schema: str, lines: list):
    """Render one idea to HCORTEX with hidden metadata marker for roundtrip."""
    shape = idea.get("shape", "attrs")
    sigil = idea["sigil"]
    name = idea["name"]

    marker = f"<!-- {sigil}:{name} -->"

    if schema == "table":
        vals = _get_table_values(idea)
        if vals:
            lines.append(f"{marker} | " + " | ".join(str(v) for v in vals) + " |")
        else:
            lines.append(marker)

    elif schema == "list":
        payload = idea.get("payload", "")
        if isinstance(payload, dict):
            payload = ", ".join(f"{k}:{v}" for k, v in payload.items())
        lines.append(f"{marker} - **{payload}**")

    elif schema == "check":
        payload = idea.get("payload", "")
        if isinstance(payload, dict):
            payload = ", ".join(f"{k}:{v}" for k, v in payload.items())
        lines.append(f"{marker} - [ ] {payload}")

    elif schema == "diagram":
        lines.append(marker)
        body = idea.get("payload", "")
        if isinstance(body, dict):
            body = str(body)
        if body:
            lines.append("```puml")
            for l2 in body.split("\n"):
                l2 = l2.strip()
                if l2:
                    lines.append(l2)
            lines.append("```")

    else:  # prose
        lines.append(marker)
        if shape == "cuerpo" or shape == "bloque":
            body = idea.get("payload", "")
            if isinstance(body, dict):
                body = str(body)
            if body:
                for l2 in body.split("\n"):
                    lines.append(l2)
        elif shape == "attrs":
            payload = idea.get("payload", {})
            if isinstance(payload, dict) and payload:
                parts = [f"{k}:{v}" for k, v in payload.items()]
                lines.append(", ".join(parts))
            elif isinstance(payload, str):
                lines.append(payload)
        elif shape == "attrs-pos":
            payload = idea.get("payload", {})
            if isinstance(payload, dict) and "positional" in payload:
                lines.append(", ".join(str(v) for v in payload["positional"]))
        elif shape == "relacion":
            payload = idea.get("payload", {})
            if isinstance(payload, dict) and "positional" in payload:
                lines.append(", ".join(str(v) for v in payload["positional"]))
        else:
            lines.append(str(idea.get("payload", "")))


def _get_table_values(idea: dict) -> list:
    """Extract table cell values from payload."""
    shape = idea.get("shape", "attrs")
    payload = idea.get("payload", {})

    if shape == "attrs":
        if isinstance(payload, dict) and payload:
            return list(payload.values())
        elif isinstance(payload, str):
            return [payload]

    elif shape == "attrs-pos":
        if isinstance(payload, dict) and "positional" in payload:
            return payload["positional"]

    elif shape == "relacion":
        if isinstance(payload, dict) and "positional" in payload:
            return payload["positional"]

    return []


# ── HCORTEX → CORTEX Compiler ──────────────────────────────────────

def compile(hcortex_text: str) -> str:
    """Compile HCORTEX with paired schemas + metadata markers back to exact CORTEX."""
    lines_out = []

    # Parse header
    if not re.search(r"<!-- HCORTEX v=[\d.]+ t=\w+ -->", hcortex_text):
        raise ValueError("Missing HCORTEX header")

    # Parse glossary → sigil definitions
    glossary_match = re.search(r"<!-- glossary\n(.*?)\n-->", hcortex_text, re.DOTALL)
    sigil_registry = {}
    raw_glossary_lines = []
    if glossary_match:
        glossary_body = glossary_match.group(1)
        for line in glossary_body.split("\n"):
            line_stripped = line.strip()
            if line_stripped:
                raw_glossary_lines.append(line_stripped)
            if "type:" in line_stripped and "{" in line_stripped:
                sig = line_stripped.split(":")[0].lower()
                if "::" in sig:
                    sig = sig.split("::")[-1]
                inner = line_stripped[line_stripped.index("{") + 1:]
                if inner.rstrip().endswith("}"):
                    inner = inner[:inner.rstrip().rfind("}")]
                attrs = _parse_attrs_body(inner)
                shape = attrs.get("type", "")
                fields_str = attrs.get("fields", attrs.get("pos", ""))
                field_names = []
                if fields_str:
                    for fdef in fields_str.split("|"):
                        fname = fdef.split(":")[0].strip()
                        field_names.append(fname)
                sigil_registry[sig] = {
                    "shape": shape,
                    "fields": field_names,
                    "focus": attrs.get("focus", ""),
                    "open": attrs.get("open", ""),
                }

    # Build $0 section
    lines_out.append("$0")

    # Emit glossary entries in order, but skip the format line (we add it first)
    format_written = False
    if glossary_match:
        glossary_body = glossary_match.group(1)
        for line in glossary_body.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("$0:format"):
                if not format_written:
                    lines_out.append(line)
                    format_written = True
            else:
                lines_out.append(line)

    if not format_written:
        lines_out.insert(1, "$0:format{cortex:0.1,encoding:UTF-8,language:es}")

    # Parse sections
    body = hcortex_text
    body = re.sub(r"<!-- HCORTEX v=[\d.]+ t=\w+ -->\s*", "", body)
    body = re.sub(r"<!-- glossary\n.*?\n-->\s*", "", body, flags=re.DOTALL)

    # Parse sections: ## §N: Title ... <!-- schema:N --> ... <!-- /schema:N -->
    # or ## §N (no title) ... 
    section_pattern = re.compile(
        r"## §(\d+)(?::\s*(.*?))?\n\s*\n"
        r"<!-- (\w+):(\d+) -->\s*\n"
        r"(.*?)"
        r"\n<!-- /\w+:\d+ -->",
        re.DOTALL,
    )

    for m in section_pattern.finditer(body):
        sec_id = int(m.group(1))
        sec_title = (m.group(2) or "").strip()
        schema_name = m.group(3)
        content = m.group(5)

        if sec_title:
            lines_out.append(f"${sec_id}: {sec_title}")
        else:
            lines_out.append(f"${sec_id}")

        if not content.strip():
            continue

        # Extract ideas from content using markers: <!-- SIG:name --> ... content
        ideas = _parse_schema_content(content, schema_name, sigil_registry)
        for idea in ideas:
            lines_out.append(idea)

    return "\n".join(lines_out)


def _parse_schema_content(content: str, schema_name: str, sigil_registry: dict) -> list:
    """Parse schema content with <!-- SIG:name --> markers back to CORTEX lines."""
    ideas = []

    # Split content by <!-- SIG:name --> markers
    # Pattern: <!-- SIG:name --> content (until next marker or end)
    marker_pattern = re.compile(r"<!-- ([\w:]+):([\w_-]+) -->\s*\n?(.*?)(?=\n?<!-- [\w:]+:[\w_-]+ -->|$)", re.DOTALL)

    for m in marker_pattern.finditer(content):
        sigil = m.group(1)
        name = m.group(2)
        body_text = m.group(3).strip()

        # Determine shape from sigil registry
        sig_clean = sigil.lower().split("::")[-1]
        sig_info = sigil_registry.get(sig_clean, sigil_registry.get(sigil.lower(), {}))
        shape = sig_info.get("shape", "attrs") if isinstance(sig_info, dict) else "attrs"

        if schema_name == "table":
            if shape == "attrs" or shape == "attrs-pos" or shape == "relacion":
                # Parse pipe row: | val1 | val2 | ... |
                # Strip leading/trailing whitespace, then remove leading | and trailing |
                row_text = body_text.strip()
                if row_text.startswith("|"):
                    row_text = row_text[1:]
                if row_text.endswith("|"):
                    row_text = row_text[:-1]
                row_text = row_text.strip()
                cells = _split_pipe_cells(row_text)
                fields = sig_info.get("fields", []) if isinstance(sig_info, dict) else []

                if shape == "attrs-pos" or shape == "relacion":
                    # Reconstruct positional: SIG:name|v1|v2|v3
                    vals = "|".join(cells)
                    ideas.append(f"{sigil}:{name}|{vals}")
                else:
                    # Reconstruct attrs: SIG:name{k1:v1, k2:v2, ...}
                    parts = []
                    for i, cell in enumerate(cells):
                        field_name = fields[i] if i < len(fields) else f"f{i+1}"
                        # List values: preserve [ ... ] as-is
                        if cell.startswith("[") and cell.endswith("]"):
                            parts.append(f"{field_name}:{cell}")
                        # Quote if contains special chars
                        elif any(c in cell for c in ' ,"{}|'):
                            cell_escaped = cell.replace('\\', '\\\\').replace('"', '\\"')
                            parts.append(f'{field_name}:"{cell_escaped}"')
                        else:
                            parts.append(f"{field_name}:{cell}")
                    ideas.append(f"{sigil}:{name}{{{','.join(parts)}}}")
            else:
                ideas.append(f"{sigil}:{name}{{}}")

        elif schema_name == "list":
            # - **content**
            item_match = re.match(r"-\s+\*\*(.*?)\*\*", body_text)
            if item_match:
                item = item_match.group(1)
                ideas.append(f"{sigil}:{name}{{{item}}}")
            else:
                ideas.append(f"{sigil}:{name}{{{body_text}}}")

        elif schema_name == "check":
            # - [ ] content  or  - [x] content
            item_match = re.match(r"-\s+\[[ x]\]\s+(.*)", body_text)
            if item_match:
                item = item_match.group(1)
                ideas.append(f"{sigil}:{name}{{{item}}}")
            else:
                ideas.append(f"{sigil}:{name}{{{body_text}}}")

        elif schema_name == "diagram":
            # ```puml\n...\n```
            m = re.search(r"```puml\s*\n(.*?)```", body_text, re.DOTALL)
            if m:
                puml_body = m.group(1).strip()
                ideas.append(f"{sigil}:{name}{{\n{puml_body}\n}}")
            else:
                ideas.append(f"{sigil}:{name}{{}}")

        else:  # prose
            if shape == "cuerpo" or shape == "bloque":
                if "\n" in body_text or not body_text:
                    ideas.append(f"{sigil}:{name}{{\n{body_text}\n}}")
                else:
                    ideas.append(f"{sigil}:{name}{{{body_text}}}")
            elif shape == "attrs":
                # Body text might be key:val pairs
                parts = _parse_keyval_pairs(body_text)
                if parts:
                    inner = ", ".join(parts)
                    ideas.append(f"{sigil}:{name}{{{inner}}}")
                else:
                    ideas.append(f"{sigil}:{name}{{{body_text}}}")
            elif shape == "attrs-pos":
                fields = sig_info.get("fields", []) if isinstance(sig_info, dict) else []
                if fields and body_text:
                    vals = body_text.split(", ")
                    parts = [f"\"{v}\"" if (" " in v or "|" in v) else v for v in vals]
                    ideas.append(f"{sigil}:{name}|{'|'.join(parts)}")
                else:
                    ideas.append(f"{sigil}:{name}|{body_text}")
            else:
                ideas.append(f"{sigil}:{name}{{{body_text}}}")

    return ideas


def _split_pipe_cells(text: str) -> list:
    """Split a pipe-delimited row into cells, respecting escaped pipes in quoted values."""
    cells = []
    i = 0
    while i < len(text):
        if i < len(text) and text[i] == '"':
            i += 1
            buf = []
            while i < len(text):
                if text[i] == '\\' and i + 1 < len(text):
                    buf.append(text[i + 1])
                    i += 2
                elif text[i] == '"':
                    i += 1
                    break
                else:
                    buf.append(text[i])
                    i += 1
            cells.append("".join(buf))
        else:
            # Find next |
            bar = text.find("|", i)
            if bar == -1:
                cells.append(text[i:].strip())
                break
            cells.append(text[i:bar].strip())
            i = bar + 1
    return cells


def _parse_keyval_pairs(text: str) -> list:
    """Parse comma-separated key:val pairs."""
    parts = []
    for pair in text.split(","):
        pair = pair.strip()
        if ":" in pair:
            k, v = pair.split(":", 1)
            k, v = k.strip(), v.strip()
            parts.append(f"{k}:{v}")
        elif pair:
            parts.append(pair)
    return parts


# ── Roundtrip Verification ─────────────────────────────────────────

def roundtrip_verify(cortex_text: str) -> dict:
    """Verify compile(render(input)) == input (normalized)."""
    result = {"ok": False, "original_length": len(cortex_text),
              "rendered": None, "compiled": None, "match": False, "differences": []}

    try:
        rendered = render(cortex_text)
        result["rendered"] = rendered
        compiled = compile(rendered)
        result["compiled"] = compiled

        norm_orig = _normalize_cortex(cortex_text)
        norm_comp = _normalize_cortex(compiled)

        if norm_orig == norm_comp:
            result["ok"] = True
            result["match"] = True
        else:
            orig_lines = norm_orig.split("\n")
            comp_lines = norm_comp.split("\n")
            max_len = max(len(orig_lines), len(comp_lines))
            for i in range(max_len):
                o = orig_lines[i] if i < len(orig_lines) else "<missing>"
                c = comp_lines[i] if i < len(comp_lines) else "<missing>"
                if o != c:
                    result["differences"].append({"line": i + 1, "original": o, "compiled": c})
            if not result["differences"]:
                result["ok"] = True
                result["match"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


def _normalize_cortex(text: str) -> str:
    """Normalize CORTEX: strip blank lines, normalize internal whitespace."""
    lines = []
    for line in text.split("\n"):
        s = line.strip()
        if s:
            lines.append(s)
    return "\n".join(lines)


# ── CLI ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="HCORTEX bidirectional transformer")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--compile", action="store_true")
    parser.add_argument("--roundtrip", action="store_true")
    parser.add_argument("--corpus", type=str, help="CORTEX corpus directory")
    parser.add_argument("--input", type=str, help="Single input file")
    parser.add_argument("--output", type=str, help="Output file")
    parser.add_argument("--results", type=str,
                        default="experiments/gate-f4/roundtrip-results.json")
    args = parser.parse_args()

    if args.roundtrip:
        _run_roundtrip(args)
    elif args.render and args.input:
        text = Path(args.input).read_text()
        result = render(text)
        if args.output:
            Path(args.output).write_text(result)
        else:
            print(result)
    elif args.compile and args.input:
        text = Path(args.input).read_text()
        result = compile(text)
        if args.output:
            Path(args.output).write_text(result)
        else:
            print(result)
    else:
        parser.print_help()


def _run_roundtrip(args):
    corpus_dir = args.corpus or "conformance/hcortex/cortex"
    corpus_path = Path(corpus_dir)
    if not corpus_path.is_absolute():
        repo = Path(__file__).resolve().parent.parent
        corpus_path = repo / corpus_dir
        if not corpus_path.exists():
            corpus_path = Path(corpus_dir)

    results = {"files": {}, "summary": {"total": 0, "passed": 0, "failed": 0, "errors": 0}}

    for f in sorted(corpus_path.glob("*.cortex")):
        name = f.stem
        text = f.read_text()
        r = roundtrip_verify(text)
        results["files"][name] = r
        results["summary"]["total"] += 1
        if r["ok"]:
            results["summary"]["passed"] += 1
        elif "error" in r:
            results["summary"]["errors"] += 1
        else:
            results["summary"]["failed"] += 1
        status = "✅" if r["ok"] else ("❌" if "error" not in r else "⚠️")
        print(f"{status} {name}")

    results_path = Path(args.results)
    if not results_path.is_absolute():
        repo = Path(__file__).resolve().parent.parent
        results_path = repo / args.results
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSummary: {results['summary']['passed']}/{results['summary']['total']} passed")
    print(f"Results: {results_path}")


if __name__ == "__main__":
    main()
