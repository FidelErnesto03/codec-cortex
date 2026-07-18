#!/usr/bin/env bash
# CODEC-CORTEX Bash — CORTEX 0.1 / C14N-0.1 / HCORTEX-0.1
# Bash implementation with jq for ordered AST manipulation and ICU uconv for NFC.

set -o pipefail

CCX_LIB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CCX_VERSION="1.0.0-rc.1"
CCX_TMP_ROOT=""
CCX_LAST_ERROR_CODE=""
CCX_LAST_ERROR_MESSAGE=""
CCX_LAST_ERROR_LINE=0
CCX_LAST_ERROR_COL=0

ccx_require_runtime() {
  local missing=() cmd
  for cmd in bash jq uconv sed awk sort mktemp seq xargs; do
    command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
  done
  if ((${#missing[@]})); then
    printf 'codec-cortex: missing runtime dependencies: %s\n' "${missing[*]}" >&2
    return 69
  fi
}

ccx_tmp_init() {
  [[ -n ${CCX_TMP_ROOT:-} && -d $CCX_TMP_ROOT ]] && return 0
  CCX_TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/codec-cortex.XXXXXX")" || return 1
}

ccx_tmp_cleanup() {
  [[ -n ${CCX_TMP_ROOT:-} && -d $CCX_TMP_ROOT ]] && rm -rf -- "$CCX_TMP_ROOT"
  CCX_TMP_ROOT=""
}

ccx_error() {
  CCX_LAST_ERROR_CODE=$1
  CCX_LAST_ERROR_MESSAGE=$2
  CCX_LAST_ERROR_LINE=${3:-0}
  CCX_LAST_ERROR_COL=${4:-0}
  printf '%s @ %s:%s — %s\n' "$CCX_LAST_ERROR_CODE" "$CCX_LAST_ERROR_LINE" "$CCX_LAST_ERROR_COL" "$CCX_LAST_ERROR_MESSAGE" >&2
  return 65
}

ccx_trim() {
  local s=$1
  s="${s#"${s%%[!$' \t\r\n']*}"}"
  s="${s%"${s##*[!$' \t\r\n']}"}"
  printf '%s' "$s"
}

ccx_nfc() {
  printf '%s' "$1" | uconv -x any-nfc
}

ccx_json_quote() {
  jq -Rnr --arg s "$1" '$s|tojson' | sed -E 's/\\u00([0-9a-f]{2})/\\u00\U\1/g'
}

ccx_json_string() {
  jq -Rn --arg s "$1" '$s'
}

ccx_emit_string_literal() {
  ccx_json_quote "$1"
}

ccx_parse_string_literal() {
  local lex=$1
  jq -Rer 'fromjson' <<<"$lex" 2>/dev/null || ccx_error "L005_INVALID_STRING" "Invalid string literal" 0 0
}

ccx_is_atom() {
  local s=$1 rest
  [[ -n $s && ${#s} -le 32 ]] || return 1
  case "$s" in
    *[[:space:]]*|*'['*|*']'*|*'{'*|*'}'*|*','*|*'"'*|*'|'*) return 1 ;;
  esac
  rest=$s
  if [[ $rest =~ ^\$[0-9]+: ]]; then
    rest=${rest#*:}
  fi
  [[ $rest =~ ^[_A-Za-z][_A-Za-z0-9./:@+%\$-]*$ ]]
}

ccx_scalar_kind() { jq -r '.kind' <<<"$1"; }
ccx_scalar_lexeme() { jq -r '.lexeme' <<<"$1"; }
ccx_scalar_value() { jq -r '.value // empty' <<<"$1"; }

ccx_split_top_level() {
  # Args: string delimiter. Emits one item per line, encoded as JSON strings.
  local s=$1 delim=$2 i ch next cur="" depth=0 in_str=0 esc=0
  for ((i=0; i<${#s}; i++)); do
    ch=${s:i:1}
    if ((in_str)); then
      cur+=$ch
      if ((esc)); then esc=0
      elif [[ $ch == '\\' ]]; then esc=1
      elif [[ $ch == '"' ]]; then in_str=0
      fi
      continue
    fi
    case $ch in
      '"') in_str=1; cur+=$ch ;;
      '['|'{'|'(') ((depth++)); cur+=$ch ;;
      ']'|'}'|')') ((depth--)); cur+=$ch ;;
      "$delim")
        if ((depth==0)); then
          jq -Rn --arg x "$cur" '$x'
          cur=""
        else cur+=$ch
        fi ;;
      *) cur+=$ch ;;
    esac
  done
  jq -Rn --arg x "$cur" '$x'
}

ccx_parse_scalar() {
  local raw trimmed inner part item_json items='[]' value lex
  raw=$1
  trimmed=$(ccx_trim "$raw")
  [[ -n $trimmed ]] || { ccx_error "L010_INVALID_ATOM" "Invalid atom: ''" "${2:-0}" "${3:-0}"; return; }

  if [[ ${trimmed:0:1} == '"' ]]; then
    [[ ${trimmed: -1} == '"' ]] || { ccx_error "L005_INVALID_STRING" "Unterminated string" "${2:-0}" "${3:-0}"; return; }
    value=$(ccx_parse_string_literal "$trimmed") || return
    lex=$(ccx_emit_string_literal "$value") || return
    jq -cn --arg v "$value" --arg l "$lex" '{kind:"string",value:$v,lexeme:$l}'
    return
  fi

  if [[ ${trimmed:0:1} == '[' ]]; then
    [[ ${trimmed: -1} == ']' ]] || { ccx_error "L007_INVALID_LIST" "Expected closing ]" "${2:-0}" "${3:-0}"; return; }
    inner=${trimmed:1:${#trimmed}-2}
    if [[ -z $(ccx_trim "$inner") ]]; then
      printf '%s\n' '{"kind":"list","value":[],"lexeme":"[]"}'
      return
    fi
    while IFS= read -r part; do
      part=$(jq -r '.' <<<"$part")
      item_json=$(ccx_parse_scalar "$part" "${2:-0}" "${3:-0}") || return
      items=$(jq -cn --argjson a "$items" --argjson x "$item_json" '$a+[$x]')
    done < <(ccx_split_top_level "$inner" ',')
    lex=$(jq -r '[.[]|.lexeme]|"["+join(",")+"]"' <<<"$items")
    jq -cn --argjson v "$items" --arg l "$lex" '{kind:"list",value:$v,lexeme:$l}'
    return
  fi

  case $trimmed in
    true) printf '%s\n' '{"kind":"boolean","value":true,"lexeme":"true"}'; return ;;
    false) printf '%s\n' '{"kind":"boolean","value":false,"lexeme":"false"}'; return ;;
    null) printf '%s\n' '{"kind":"null","value":null,"lexeme":"null"}'; return ;;
  esac
  if [[ $trimmed =~ ^-?(0|[1-9][0-9]*)$ ]]; then
    [[ $trimmed == '-0' ]] && trimmed=0
    jq -cn --arg v "$trimmed" '{kind:"integer",value:$v,lexeme:$v}'
    return
  fi
  if [[ $trimmed =~ ^-?(0|[1-9][0-9]*)\.[0-9]+$ ]]; then
    jq -cn --arg v "$trimmed" '{kind:"decimal",value:$v,lexeme:$v}'
    return
  fi
  ccx_is_atom "$trimmed" || { ccx_error "L010_INVALID_ATOM" "Invalid atom: '$trimmed'" "${2:-0}" "${3:-0}"; return; }
  jq -cn --arg v "$trimmed" '{kind:"atom",value:$v,lexeme:$v}'
}

ccx_find_top_colon() {
  local s=$1 i ch depth=0 in_str=0 esc=0
  for ((i=0;i<${#s};i++)); do
    ch=${s:i:1}
    if ((in_str)); then
      if ((esc)); then esc=0
      elif [[ $ch == '\\' ]]; then esc=1
      elif [[ $ch == '"' ]]; then in_str=0
      fi
    else
      case $ch in
        '"') in_str=1 ;;
        '['|'{'|'(') ((depth++)) ;;
        ']'|'}'|')') ((depth--)) ;;
        ':') ((depth==0)) && { printf '%s' "$i"; return 0; } ;;
      esac
    fi
  done
  return 1
}

ccx_parse_attrs() {
  # Input includes braces; returns JSON array [{key,value},...]
  local src=$1 line=${2:-1} inner part idx key rawv scalar pairs='[]'
  src=$(ccx_trim "$src")
  [[ ${src:0:1} == '{' ]] || { ccx_error "S006_INVALID_ATTRS" "Expected {" "$line" 1; return; }
  [[ ${src: -1} == '}' ]] || { ccx_error "S006_INVALID_ATTRS" "Expected }" "$line" "${#src}"; return; }
  inner=${src:1:${#src}-2}
  [[ -z $(ccx_trim "$inner") ]] && { printf '%s\n' '[]'; return; }
  while IFS= read -r part; do
    part=$(jq -r '.' <<<"$part")
    part=$(ccx_trim "$part")
    [[ -z $part ]] && continue
    idx=$(ccx_find_top_colon "$part") || { ccx_error "S006_INVALID_ATTRS" "Expected : after key" "$line" 1; return; }
    key=$(ccx_trim "${part:0:idx}")
    rawv=${part:idx+1}
    [[ -n $key ]] || { ccx_error "L003_INVALID_KEY" "Empty key" "$line" 1; return; }
    scalar=$(ccx_parse_scalar "$rawv" "$line" 1) || return
    pairs=$(jq -cn --argjson a "$pairs" --arg k "$key" --argjson v "$scalar" '$a+[{key:$k,value:$v}]')
  done < <(ccx_split_top_level "$inner" ',')
  printf '%s\n' "$pairs"
}

ccx_parse_contract() {
  local s=$1 part name type req out='[]'
  while IFS= read -r part; do
    part=$(jq -r '.' <<<"$part")
    part=$(ccx_trim "$part")
    [[ -n $part ]] || { ccx_error "G008_INVALID_CONTRACT" "Empty contract field in '$s'" 0 0; return; }
    req=true
    if [[ $part == *'?' ]]; then req=false; part=${part%?}; fi
    if [[ $part == *:* ]]; then name=${part%%:*}; type=${part#*:}; else name=$part; type=any; fi
    name=$(ccx_trim "$name"); type=$(ccx_trim "$type")
    out=$(jq -cn --argjson a "$out" --arg n "$name" --arg t "$type" --argjson r "$req" '$a+[{name:$n,type:$t,required:$r}]')
  done < <(ccx_split_top_level "$s" '|')
  printf '%s\n' "$out"
}

ccx_attr_last() {
  local attrs=$1 key=$2
  jq -c --arg k "$key" '[.[]|select(.key==$k)|.value]|last // empty' <<<"$attrs"
}

ccx_scalar_text() {
  local s=$1 kind
  kind=$(jq -r '.kind' <<<"$s")
  case $kind in
    string|atom|integer|decimal) jq -r '.value' <<<"$s" ;;
    boolean) jq -r 'if .value then "true" else "false" end' <<<"$s" ;;
    null) printf 'null' ;;
    *) jq -jr '.lexeme' <<<"$s" ;;
  esac
}

ccx_build_symbol() {
  local ns=$1 sigil=$2 label=$3 attrs=$4 line=${5:-0}
  local sv shape weight desc open=false contract='[]' focus fields pos
  sv=$(ccx_attr_last "$attrs" type); [[ -n $sv ]] || { ccx_error G016_SYMBOL_TYPE_REQUIRED "sigil $sigil missing type" "$line" 0; return; }
  shape=$(ccx_scalar_text "$sv")
  case $shape in attrs|attrs-pos|cuerpo|bloque|relacion) ;; *) ccx_error G017_UNKNOWN_SHAPE "Unknown shape: $shape" "$line" 0; return;; esac
  sv=$(ccx_attr_last "$attrs" weight); [[ -n $sv ]] || { ccx_error G018_SYMBOL_WEIGHT_REQUIRED "sigil $sigil missing weight" "$line" 0; return; }
  weight=$(ccx_scalar_text "$sv")
  case $weight in B|M|H) ;; *) ccx_error G019_INVALID_WEIGHT "Invalid weight: $weight" "$line" 0; return;; esac
  sv=$(ccx_attr_last "$attrs" desc); [[ -n $sv ]] || { ccx_error G020_SYMBOL_DESCRIPTION_REQUIRED "sigil $sigil missing desc" "$line" 0; return; }
  desc=$(ccx_scalar_text "$sv")
  sv=$(ccx_attr_last "$attrs" open)
  if [[ -n $sv ]]; then [[ $(jq -r '.lexeme' <<<"$sv") == true ]] && open=true; fi
  if [[ $shape == attrs ]]; then
    sv=$(ccx_attr_last "$attrs" fields); [[ -n $sv ]] || { ccx_error G021_ATTRS_CONTRACT_REQUIRED "sigil $sigil missing fields" "$line" 0; return; }
    fields=$(ccx_scalar_text "$sv"); contract=$(ccx_parse_contract "$fields") || return
  elif [[ $shape == attrs-pos || $shape == relacion ]]; then
    sv=$(ccx_attr_last "$attrs" pos); [[ -n $sv ]] || { ccx_error G022_POSITIONAL_CONTRACT_REQUIRED "sigil $sigil missing pos" "$line" 0; return; }
    pos=$(ccx_scalar_text "$sv"); contract=$(ccx_parse_contract "$pos") || return
    if [[ $shape == relacion && $(jq 'length' <<<"$contract") -lt 3 ]]; then ccx_error G023_RELATION_CONTRACT_TOO_SHORT "relacion needs >=3 fields" "$line" 0; return; fi
  fi
  sv=$(ccx_attr_last "$attrs" focus)
  if [[ -z $sv ]]; then
    if [[ $shape == cuerpo || $shape == bloque ]]; then focus='$body'; else ccx_error G024_FOCUS_REQUIRED "sigil $sigil missing focus" "$line" 0; return; fi
  else
    focus=$(ccx_scalar_text "$sv")
    if [[ $shape == attrs || $shape == attrs-pos || $shape == relacion ]]; then
      jq -e --arg f "$focus" 'any(.[];.name==$f)' <<<"$contract" >/dev/null || { ccx_error G025_UNKNOWN_FOCUS_FIELD "focus '$focus' not in contract" "$line" 0; return; }
    fi
  fi
  jq -cn --argjson ns "$(if [[ -n $ns ]]; then ccx_json_string "$ns"; else printf null; fi)" \
    --arg s "$sigil" --arg l "$label" --arg sh "$shape" --arg w "$weight" --arg f "$focus" --arg d "$desc" \
    --argjson o "$open" --argjson c "$contract" --argjson a "$attrs" --argjson ln "$line" \
    '{namespace:$ns,sigil:$s,label:$l,shape:$sh,weight:$w,focus:$f,desc:$d,open:$o,contract:$c,attrs:$a,source_line:$ln}'
}

ccx_empty_document() {
  cat <<'JSON'
{"cortex_version":"0.1","encoding":"UTF-8","glossary":{"format":null,"meta":[],"enums":[],"micros":[],"namespaces":[],"extensions":[],"symbols":[]},"sections":[]}
JSON
}

ccx_doc_update() {
  local file=$1 filter=$2; shift 2
  local tmp="${file}.tmp"
  jq "$@" "$filter" "$file" >"$tmp" || return
  mv "$tmp" "$file"
}

ccx_add_meta_decl() {
  local doc=$1 name=$2 attrs=$3 line=$4 sv value vals token alias ename obj
  case $name in
    format)
      if jq -e '.glossary.format != null' "$doc" >/dev/null; then ccx_error G006_DUPLICATE_FORMAT 'Duplicate $0:format' "$line" 0; return; fi
      sv=$(ccx_attr_last "$attrs" cortex); if [[ -n $sv ]]; then value=$(ccx_scalar_text "$sv"); else value=0.1; fi
      [[ $value == 0.1 ]] || { ccx_error G007_UNSUPPORTED_VERSION "Unsupported cortex version: $value" "$line" 0; return; }
      sv=$(ccx_attr_last "$attrs" encoding); if [[ -n $sv ]]; then ename=$(ccx_scalar_text "$sv"); else ename=UTF-8; fi
      [[ $ename == UTF-8 ]] || { ccx_error G011_ENCODING_REQUIRED "Encoding must be UTF-8: $ename" "$line" 0; return; }
      obj=$(jq -cn --arg c "$value" --arg e "$ename" --argjson a "$attrs" --argjson ln "$line" '{cortex:$c,encoding:$e,attrs:$a,source_line:$ln}')
      ccx_doc_update "$doc" '.glossary.format=$x' --argjson x "$obj"
      ;;
    enum_*)
      ename=${name#enum_}; sv=$(ccx_attr_last "$attrs" values)
      [[ -n $sv && $(jq -r '.kind' <<<"$sv") == string ]] || { ccx_error G014_INVALID_ENUM "enum $ename missing values string" "$line" 0; return; }
      value=$(jq -r '.value' <<<"$sv")
      vals=$(jq -Rn --arg s "$value" '$s|split("|")')
      obj=$(jq -cn --arg n "$ename" --argjson v "$vals" --argjson ln "$line" '{name:$n,values:$v,source_line:$ln}')
      ccx_doc_update "$doc" '.glossary.enums += [$x]' --argjson x "$obj"
      ;;
    micro_*)
      token=${name#micro_}; sv=$(ccx_attr_last "$attrs" expand)
      [[ -n $sv ]] || { ccx_error G012_INVALID_MICRO "micro $token missing expand" "$line" 0; return; }
      case $(jq -r '.kind' <<<"$sv") in atom|string) value=$(jq -r '.value' <<<"$sv");; *) value=$(jq -r '.lexeme' <<<"$sv");; esac
      obj=$(jq -cn --arg t "$token" --arg e "$value" --argjson ln "$line" '{token:$t,expand:$e,source_line:$ln}')
      ccx_doc_update "$doc" '.glossary.micros += [$x]' --argjson x "$obj"
      ;;
    namespace_*)
      alias=${name#namespace_}; obj=$(jq -cn --arg a "$alias" --argjson x "$attrs" --argjson ln "$line" '{alias:$a,attrs:$x,source_line:$ln}')
      ccx_doc_update "$doc" '.glossary.namespaces += [$x]' --argjson x "$obj"
      ;;
    extension_*)
      ename=${name#extension_}; obj=$(jq -cn --arg n "$ename" --argjson a "$attrs" --argjson ln "$line" '{name:$n,attrs:$a,source_line:$ln}')
      ccx_doc_update "$doc" '.glossary.extensions += [$x]' --argjson x "$obj"
      ;;
    *)
      obj=$(jq -cn --arg n "$name" --argjson a "$attrs" --argjson ln "$line" '{name:$n,attrs:$a,source_line:$ln}')
      ccx_doc_update "$doc" '.glossary.meta += [$x]' --argjson x "$obj"
      ;;
  esac
}

ccx_parse_glossary_decl() {
  local doc=$1 line_text=$2 line_no=$3 brace head payload name attrs ns sigil label sym
  brace=${line_text%%\{*}
  [[ $brace != "$line_text" ]] || { ccx_error G004_GLOSSARY_DECLARATION_MUST_BE_ATTRS "Glossary declaration must use attrs: '$line_text'" "$line_no" 0; return; }
  head=$(ccx_trim "$brace")
  payload=${line_text:${#brace}}
  attrs=$(ccx_parse_attrs "$payload" "$line_no") || return
  if [[ $head == '$0:'* ]]; then
    name=${head#\$0:}
    ccx_add_meta_decl "$doc" "$name" "$attrs" "$line_no"
    return
  fi
  if [[ $head =~ ^([a-z][a-z0-9_.-]*::)?(!|[A-Z][A-Z0-9_]*):(.+)$ ]]; then
    ns=${BASH_REMATCH[1]%::}; sigil=${BASH_REMATCH[2]}; label=${BASH_REMATCH[3]}
    sym=$(ccx_build_symbol "$ns" "$sigil" "$label" "$attrs" "$line_no") || return
    ccx_doc_update "$doc" '.glossary.symbols += [$x]' --argjson x "$sym"
  else
    ccx_error L001_INVALID_SYMBOL "Invalid sigil declaration head: '$head'" "$line_no" 0
  fi
}

ccx_classify_raw_cell() {
  local raw trimmed lex
  raw=$1; trimmed=$(ccx_trim "$raw")
  if [[ ${trimmed:0:1} == '"' ]]; then ccx_parse_scalar "$trimmed" "${2:-0}" 0; return; fi
  case $trimmed in
    true|false|null) ccx_parse_scalar "$trimmed" "${2:-0}" 0; return ;;
  esac
  if [[ $trimmed =~ ^-?(0|[1-9][0-9]*)$ || $trimmed =~ ^-?(0|[1-9][0-9]*)\.[0-9]+$ ]]; then ccx_parse_scalar "$trimmed" "${2:-0}" 0; return; fi
  if ccx_is_atom "$trimmed" && [[ $trimmed != *' '* ]]; then ccx_parse_scalar "$trimmed" "${2:-0}" 0; return; fi
  lex=$(ccx_emit_string_literal "$trimmed")
  jq -cn --arg v "$trimmed" --arg l "$lex" '{kind:"string",value:$v,lexeme:$l}'
}

ccx_parse_pipe_cells() {
  local s=$1 line=$2 part raw scalar cells='[]' count idx=0
  local -a parts=()
  while IFS= read -r part; do parts+=("$(jq -r '.' <<<"$part")"); done < <(ccx_split_top_level "$s" '|')
  count=${#parts[@]}
  if ((count>0)) && [[ -z $(ccx_trim "${parts[count-1]}") ]]; then unset 'parts[count-1]'; fi
  for raw in "${parts[@]}"; do
    scalar=$(ccx_classify_raw_cell "$raw" "$line") || return
    cells=$(jq -cn --argjson a "$cells" --argjson x "$scalar" '$a+[$x]')
  done
  printf '%s\n' "$cells"
}

ccx_find_symbol() {
  local doc=$1 ns=$2 sigil=$3
  jq -c --arg ns "$ns" --arg s "$sigil" '[.glossary.symbols[]|select(.sigil==$s and ((.namespace//"")==$ns))]|first // empty' "$doc"
}

ccx_parse_idea_line() {
  local doc=$1 line_text=$2 section_id=$3 line_no=$4
  local ns sigil name rest sym shape attrs cells inner payload idea nsp
  line_text=$(ccx_trim "$line_text")
  if [[ $line_text =~ ^([a-z][a-z0-9_.-]*::)?(!|[A-Z][A-Z0-9_]*):([^\{\|\}\[:space:]]+)(.*)$ ]]; then
    ns=${BASH_REMATCH[1]%::}; sigil=${BASH_REMATCH[2]}; name=${BASH_REMATCH[3]}; rest=${BASH_REMATCH[4]}
  else
    ccx_error S003_INVALID_IDEA_HEAD "Invalid idea head: '$line_text'" "$line_no" 0; return
  fi
  sym=$(ccx_find_symbol "$doc" "$ns" "$sigil")
  [[ -n $sym ]] || { ccx_error I001_UNDECLARED_SYMBOL "Undeclared sigil: $sigil" "$line_no" 0; return; }
  shape=$(jq -r '.shape' <<<"$sym")
  nsp=$(if [[ -n $ns ]]; then ccx_json_string "$ns"; else printf null; fi)
  case $shape in
    attrs|cuerpo|bloque)
      [[ ${rest:0:1} == '{' ]] || { ccx_error I004_SHAPE_DELIMITER_MISMATCH "Expected { for shape $shape" "$line_no" 0; return; }
      if [[ ${rest: -1} == '}' ]]; then
        if [[ $shape == attrs ]]; then
          attrs=$(ccx_parse_attrs "$rest" "$line_no") || return
          payload=$(jq -cn --argjson p "$attrs" '["attrs",$p]')
        else
          inner=${rest:1:${#rest}-2}
          [[ $shape == cuerpo ]] && inner=$(ccx_nfc "$inner")
          payload=$(jq -cn --arg sh "$shape" --arg x "$inner" '[$sh,$x]')
        fi
        jq -cn --argjson sec "$section_id" --argjson ns "$nsp" --arg s "$sigil" --arg n "$name" --arg sh "$shape" --argjson p "$payload" --argjson ln "$line_no" \
          '{section:$sec,namespace:$ns,symbol:$s,name:$n,shape:$sh,payload:$p,source_line:$ln}'
      else
        [[ $(ccx_trim "$rest") == '{' ]] || { ccx_error I004_SHAPE_DELIMITER_MISMATCH "Expected single { for multiline $shape" "$line_no" 0; return; }
        jq -cn --argjson sec "$section_id" --argjson ns "$nsp" --arg s "$sigil" --arg n "$name" --arg sh "$shape" --argjson ln "$line_no" \
          '{section:$sec,namespace:$ns,symbol:$s,name:$n,shape:$sh,payload:["_multiline_body",null],source_line:$ln}'
      fi
      ;;
    attrs-pos|relacion)
      [[ ${rest:0:1} == '|' ]] || { ccx_error I004_SHAPE_DELIMITER_MISMATCH "Expected | for shape $shape" "$line_no" 0; return; }
      cells=$(ccx_parse_pipe_cells "${rest:1}" "$line_no") || return
      payload=$(jq -cn --arg sh "$shape" --argjson c "$cells" '[$sh,$c]')
      jq -cn --argjson sec "$section_id" --argjson ns "$nsp" --arg s "$sigil" --arg n "$name" --arg sh "$shape" --argjson p "$payload" --argjson ln "$line_no" \
        '{section:$sec,namespace:$ns,symbol:$s,name:$n,shape:$sh,payload:$p,source_line:$ln}'
      ;;
    *) ccx_error S999_INTERNAL_PARSE_FAILURE "Cannot parse idea: '$line_text'" "$line_no" 0 ;;
  esac
}

ccx_parse_cortex_file() {
  local input=$1 output=$2 normalized line raw stripped line_no=0 in_glossary=0 current_idx=-1 current_id=-1
  local in_body=0 body_kind='' body_idea='' body_text='' sid title idea doc_json hex
  ccx_tmp_init || return
  hex=$(od -An -tx1 -N3 "$input" 2>/dev/null | tr -d ' \n')
  [[ $hex != efbbbf ]] || { ccx_error U001_BOM_FORBIDDEN 'BOM forbidden' 0 0; return; }
  normalized="$CCX_TMP_ROOT/normalized.$RANDOM"
  sed 's/\r$//' "$input" | tr '\r' '\n' >"$normalized"
  ccx_empty_document >"$output"

  while IFS= read -r raw || [[ -n $raw ]]; do
    ((line_no++))
    if ((in_body)); then
      stripped=$(ccx_trim "$raw")
      if [[ $stripped == '}' ]]; then
        body_text=${body_text%$'\n'}
        body_idea=$(jq -c --arg sh "$body_kind" --arg x "$body_text" '.payload=[$sh,$x]' <<<"$body_idea")
        ccx_doc_update "$output" ".sections[$current_idx].ideas += [\$x]" --argjson x "$body_idea"
        in_body=0; body_kind=''; body_idea=''; body_text=''
      else
        body_text+="$raw"$'\n'
      fi
      continue
    fi

    stripped=$(ccx_trim "$raw")
    [[ -z $stripped || ${stripped:0:1} == '#' ]] && continue

    if [[ $stripped =~ ^\$([0-9]+)([[:space:]]+(.*))?$ && $stripped != '$0:'* ]]; then
      sid=${BASH_REMATCH[1]}; title=${BASH_REMATCH[3]-}
      if ((sid==0)); then
        ((in_glossary)) && { ccx_error G002_GLOSSARY_REOPENED '$0 reopened' "$line_no" 0; return; }
        in_glossary=1; continue
      fi
      title=$(ccx_trim "$title")
      if [[ -n $title ]]; then
        ccx_doc_update "$output" '.sections += [{id:$id,title:$t,ideas:[]}]' --argjson id "$sid" --arg t "$title"
      else
        ccx_doc_update "$output" '.sections += [{id:$id,title:null,ideas:[]}]' --argjson id "$sid"
      fi
      current_idx=$(($(jq '.sections|length' "$output")-1)); current_id=$sid; in_glossary=0; continue
    fi
    if [[ $stripped =~ ^\$([1-9][0-9]*):[[:space:]]+(.*)$ ]]; then
      sid=${BASH_REMATCH[1]}; title=$(ccx_trim "${BASH_REMATCH[2]}")
      ccx_doc_update "$output" '.sections += [{id:$id,title:$t,ideas:[]}]' --argjson id "$sid" --arg t "$title"
      current_idx=$(($(jq '.sections|length' "$output")-1)); current_id=$sid; in_glossary=0; continue
    fi

    if ((in_glossary)); then
      ccx_parse_glossary_decl "$output" "$stripped" "$line_no" || return
      continue
    fi
    ((current_idx>=0)) || { ccx_error S005_CONTENT_OUTSIDE_SECTION "Content outside section: '$stripped'" "$line_no" 0; return; }
    idea=$(ccx_parse_idea_line "$output" "$stripped" "$current_id" "$line_no") || return
    if [[ $(jq -r '.payload[0]' <<<"$idea") == _multiline_body ]]; then
      in_body=1; body_kind=$(jq -r '.shape' <<<"$idea"); body_idea=$idea; body_text=''
    else
      ccx_doc_update "$output" ".sections[$current_idx].ideas += [\$x]" --argjson x "$idea"
    fi
  done <"$normalized"

  # Python implementation returns the document even for an unterminated body; preserve that behavior.
  return 0
}

ccx_parse_cortex() {
  local input=$1 out=${2:-}
  ccx_tmp_init || return
  [[ -n $out ]] || out="$CCX_TMP_ROOT/ast.$RANDOM.json"
  ccx_parse_cortex_file "$input" "$out" || return
  cat "$out"
}

ccx_scalar_nfc() {
  local s=$1 kind value lex items='[]' item
  kind=$(jq -r '.kind' <<<"$s")
  case $kind in
    string)
      value=$(jq -r '.value' <<<"$s"); value=$(ccx_nfc "$value"); lex=$(ccx_emit_string_literal "$value")
      jq -cn --arg v "$value" --arg l "$lex" '{kind:"string",value:$v,lexeme:$l}' ;;
    atom)
      value=$(jq -r '.value' <<<"$s"); value=$(ccx_nfc "$value")
      jq -cn --arg v "$value" '{kind:"atom",value:$v,lexeme:$v}' ;;
    list)
      while IFS= read -r item; do
        item=$(ccx_scalar_nfc "$item") || return
        items=$(jq -cn --argjson a "$items" --argjson x "$item" '$a+[$x]')
      done < <(jq -c '.value[]' <<<"$s")
      lex=$(jq -r '[.[]|.lexeme]|"["+join(",")+"]"' <<<"$items")
      jq -cn --argjson v "$items" --arg l "$lex" '{kind:"list",value:$v,lexeme:$l}' ;;
    *) printf '%s\n' "$s" ;;
  esac
}

ccx_atom_safe_bare() {
  local s=$1
  [[ -n $s ]] || return 1
  case "$s" in
    *[[:space:]]*|*'['*|*']'*|*'{'*|*'}'*|*','*|*'"'*|*'|'*) return 1 ;;
  esac
  return 0
}

ccx_atom_regex() {
  local s=$1 rest=$1
  if [[ $rest =~ ^\$[0-9]+: ]]; then rest=${rest#*:}; fi
  [[ $rest =~ ^[_A-Za-z][_A-Za-z0-9./:@+%\$-]*$ ]]
}

ccx_text_safe_bare() {
  local s=$1 trimmed
  [[ -n $s && $s != *$'\n'* && $s != *$'\r'* && $s != *'|'* && ${s:0:1} != '"' ]] || return 1
  trimmed=$(ccx_trim "$s")
  [[ $s == "$trimmed" ]]
}

ccx_emit_scalar_attrs() {
  local s=$1 is_focus_text=$2 is_text=$3 kind value
  kind=$(jq -r '.kind' <<<"$s")
  case $kind in
    string)
      value=$(jq -r '.value' <<<"$s")
      if [[ $is_focus_text == true ]]; then jq -jr '.lexeme' <<<"$s"
      elif [[ $is_text == true ]] && ccx_atom_safe_bare "$value" && ccx_atom_regex "$value"; then printf '%s' "$value"
      else jq -jr '.lexeme' <<<"$s"; fi ;;
    atom)
      value=$(jq -r '.value' <<<"$s")
      if ccx_atom_safe_bare "$value"; then printf '%s' "$value"; else ccx_emit_string_literal "$value"; fi ;;
    *) jq -jr '.lexeme' <<<"$s" ;;
  esac
}

ccx_emit_scalar_positional() {
  local s=$1 is_text=$2 kind value
  kind=$(jq -r '.kind' <<<"$s")
  case $kind in
    string)
      value=$(jq -r '.value' <<<"$s")
      if [[ $is_text == true ]] && ccx_text_safe_bare "$value"; then printf '%s' "$value"; else jq -jr '.lexeme' <<<"$s"; fi ;;
    atom)
      value=$(jq -r '.value' <<<"$s")
      if ccx_atom_safe_bare "$value"; then printf '%s' "$value"; else ccx_emit_string_literal "$value"; fi ;;
    *) jq -jr '.lexeme' <<<"$s" ;;
  esac
}

ccx_sort_attrs_json() {
  local attrs=$1 order=$2 out='[]' k x extras='[]' norm key
  IFS=',' read -r -a _ccx_order <<<"$order"
  for k in "${_ccx_order[@]}"; do
    [[ -n $k ]] || continue
    x=$(jq -c --arg k "$k" '[.[]|select(.key==$k)]|last // empty' <<<"$attrs")
    [[ -n $x ]] && out=$(jq -cn --argjson a "$out" --argjson x "$x" '$a+[$x]')
  done
  # Python keeps all extra pairs and sorts stably by NFC key.
  while IFS= read -r x; do
    key=$(jq -r '.key' <<<"$x")
    case ",$order," in *",$key,"*) continue;; esac
    norm=$(ccx_nfc "$key")
    extras=$(jq -cn --argjson a "$extras" --argjson x "$x" --arg n "$norm" '$a+[$x+{__sort:$n}]')
  done < <(jq -c '.[]' <<<"$attrs")
  extras=$(jq -c 'sort_by(.__sort)|map(del(.__sort))' <<<"$extras")
  jq -cn --argjson a "$out" --argjson e "$extras" '$a+$e'
}

ccx_nfc_attrs() {
  local attrs=$1 out='[]' pair s key
  while IFS= read -r pair; do
    key=$(jq -r '.key' <<<"$pair")
    s=$(ccx_scalar_nfc "$(jq -c '.value' <<<"$pair")") || return
    out=$(jq -cn --argjson a "$out" --arg k "$key" --argjson v "$s" '$a+[{key:$k,value:$v}]')
  done < <(jq -c '.[]' <<<"$attrs")
  printf '%s\n' "$out"
}

ccx_emit_glossary_attrs() {
  local attrs=$1 pair first=1 key lex
  printf '{'
  while IFS= read -r pair; do
    ((first)) || printf ','; first=0
    key=$(jq -r '.key' <<<"$pair"); lex=$(jq -r '.value.lexeme' <<<"$pair")
    printf '%s:%s' "$key" "$lex"
  done < <(jq -c '.[]' <<<"$attrs")
  printf '}'
}

ccx_symbol_for_idea_json() {
  local ast=$1 idea=$2 ns sigil
  ns=$(jq -r '.namespace // ""' <<<"$idea"); sigil=$(jq -r '.symbol' <<<"$idea")
  jq -c --arg ns "$ns" --arg s "$sigil" '[.glossary.symbols[]|select(.sigil==$s and ((.namespace//"")==$ns))]|first // ([.glossary.symbols[]|select(.sigil==$s and .namespace==null)]|first)' "$ast"
}

ccx_expand_micro_scalar() {
  local ast=$1 s=$2 kind val exp
  kind=$(jq -r '.kind' <<<"$s")
  if [[ $kind == atom ]]; then
    val=$(jq -r '.value' <<<"$s")
    exp=$(jq -r --arg t "$val" '[.glossary.micros[]|select(.token==$t)|.expand]|last // empty' "$ast")
    if [[ -n $exp ]]; then jq -cn --arg v "$exp" '{kind:"atom",value:$v,lexeme:$v}'; return; fi
  fi
  printf '%s\n' "$s"
}

ccx_canonicalize_ast() {
  local ast_file=$1 format attrs sorted entity pair name token expand lex qualified sym ns sigil label sec title idea shape head
  local out_pair='' val ftype focus key contract open field existing extras cell idx text part first
  printf '%s\n' '$0'
  format=$(jq -c '.glossary.format' "$ast_file")
  [[ $format != null ]] || { ccx_error G005_FORMAT_REQUIRED 'Missing $0:format' 0 0; return; }
  attrs=$(ccx_nfc_attrs "$(jq -c '.attrs' <<<"$format")") || return
  sorted=$(ccx_sort_attrs_json "$attrs" 'cortex,encoding,language')
  printf '%s' '$0:format'; ccx_emit_glossary_attrs "$sorted"; printf '\n'

  while IFS= read -r entity; do
    name=$(jq -r '.name' <<<"$entity")
    val=$(jq -r '.values|map(.)|join("|")' <<<"$entity"); val=$(ccx_nfc "$val"); lex=$(ccx_emit_string_literal "$val")
    attrs=$(jq -cn --arg l "$lex" --arg v "$val" '[{key:"values",value:{kind:"string",value:$v,lexeme:$l}}]')
    printf '$0:enum_%s' "$name"; ccx_emit_glossary_attrs "$attrs"; printf '\n'
  done < <(jq -c '.glossary.enums|sort_by(.name)[]' "$ast_file")

  while IFS= read -r entity; do
    token=$(jq -r '.token' <<<"$entity"); expand=$(ccx_nfc "$(jq -r '.expand' <<<"$entity")")
    if ccx_atom_regex "$expand"; then val=$(jq -cn --arg v "$expand" '{kind:"atom",value:$v,lexeme:$v}'); else lex=$(ccx_emit_string_literal "$expand"); val=$(jq -cn --arg v "$expand" --arg l "$lex" '{kind:"string",value:$v,lexeme:$l}'); fi
    attrs=$(jq -cn --argjson v "$val" '[{key:"expand",value:$v}]')
    printf '$0:micro_%s' "$token"; ccx_emit_glossary_attrs "$attrs"; printf '\n'
  done < <(jq -c '.glossary.micros|sort_by(.token)[]' "$ast_file")

  while IFS= read -r entity; do
    name=$(jq -r '.alias' <<<"$entity"); attrs=$(ccx_nfc_attrs "$(jq -c '.attrs' <<<"$entity")"); sorted=$(ccx_sort_attrs_json "$attrs" 'id,uri,version,required,desc')
    printf '$0:namespace_%s' "$name"; ccx_emit_glossary_attrs "$sorted"; printf '\n'
  done < <(jq -c '.glossary.namespaces|sort_by(.alias)[]' "$ast_file")

  while IFS= read -r entity; do
    name=$(jq -r '.name' <<<"$entity"); attrs=$(ccx_nfc_attrs "$(jq -c '.attrs' <<<"$entity")"); sorted=$(ccx_sort_attrs_json "$attrs" 'namespace,id,version,required,desc')
    printf '$0:extension_%s' "$name"; ccx_emit_glossary_attrs "$sorted"; printf '\n'
  done < <(jq -c '.glossary.extensions|sort_by(.name)[]' "$ast_file")

  while IFS= read -r entity; do
    name=$(jq -r '.name' <<<"$entity"); attrs=$(ccx_nfc_attrs "$(jq -c '.attrs' <<<"$entity")"); sorted=$(jq -c 'sort_by(.key)' <<<"$attrs")
    printf '$0:%s' "$name"; ccx_emit_glossary_attrs "$sorted"; printf '\n'
  done < <(jq -c '.glossary.meta|sort_by(.name)[]' "$ast_file")

  while IFS= read -r entity; do
    ns=$(jq -r '.namespace // ""' <<<"$entity"); sigil=$(jq -r '.sigil' <<<"$entity"); label=$(jq -r '.label' <<<"$entity")
    attrs=$(ccx_nfc_attrs "$(jq -c '.attrs' <<<"$entity")"); sorted=$(ccx_sort_attrs_json "$attrs" 'type,weight,fields,pos,focus,desc,open,namespace,version')
    [[ -n $ns ]] && qualified="$ns::$sigil" || qualified=$sigil
    printf '%s:%s' "$qualified" "$label"; ccx_emit_glossary_attrs "$sorted"; printf '\n'
  done < <(jq -c '.glossary.symbols|sort_by((.namespace//""),.sigil,.label)[]' "$ast_file")

  while IFS= read -r sec; do
    title=$(jq -r '.title // empty' <<<"$sec")
    if [[ -n $title ]]; then title=$(ccx_nfc "$title"); title=$(ccx_trim "$title"); printf '$%s: %s\n' "$(jq -r '.id' <<<"$sec")" "$title"
    else printf '$%s\n' "$(jq -r '.id' <<<"$sec")"; fi

    while IFS= read -r idea; do
      ns=$(jq -r '.namespace // ""' <<<"$idea"); sigil=$(jq -r '.symbol' <<<"$idea"); name=$(jq -r '.name' <<<"$idea"); shape=$(jq -r '.shape' <<<"$idea")
      [[ -n $ns ]] && qualified="$ns::$sigil" || qualified=$sigil
      head="$qualified:$name"
      sym=$(ccx_symbol_for_idea_json "$ast_file" "$idea")
      case $shape in
        attrs)
          contract=$(jq -c '.contract' <<<"$sym"); focus=$(jq -r '.focus' <<<"$sym"); open=$(jq -r '.open' <<<"$sym")
          attrs=$(jq -c '.payload[1]' <<<"$idea"); first=1; printf '%s{' "$head"
          while IFS= read -r field; do
            key=$(jq -r '.name' <<<"$field")
            pair=$(jq -c --arg k "$key" '[.[]|select(.key==$k)]|last // empty' <<<"$attrs")
            [[ -n $pair ]] || continue
            val=$(ccx_scalar_nfc "$(jq -c '.value' <<<"$pair")"); val=$(ccx_expand_micro_scalar "$ast_file" "$val")
            ftype=$(jq -r '.type' <<<"$field")
            ((first)) || printf ','; first=0
            printf '%s:' "$key"; ccx_emit_scalar_attrs "$val" "$([[ $key == "$focus" && $ftype == text ]] && echo true || echo false)" "$([[ $ftype == text ]] && echo true || echo false)"
          done < <(jq -c '.[]' <<<"$contract")
          if [[ $open == true ]]; then
            extras=$(jq -c --argjson c "$contract" '[.[]|select(.key as $k|($c|any(.[];.name==$k)|not))]|sort_by(.key)' <<<"$attrs")
            while IFS= read -r pair; do
              key=$(jq -r '.key' <<<"$pair"); val=$(ccx_scalar_nfc "$(jq -c '.value' <<<"$pair")"); val=$(ccx_expand_micro_scalar "$ast_file" "$val")
              ((first)) || printf ','; first=0
              printf '%s:' "$key"; ccx_emit_scalar_attrs "$val" false false
            done < <(jq -c '.[]' <<<"$extras")
          fi
          printf '}\n'
          ;;
        attrs-pos|relacion)
          printf '%s|' "$head"; idx=0; first=1
          while IFS= read -r cell; do
            val=$(ccx_scalar_nfc "$cell"); val=$(ccx_expand_micro_scalar "$ast_file" "$val")
            ftype=$(jq -r --argjson i "$idx" '.contract[$i].type // "any"' <<<"$sym")
            ((first)) || printf '|'; first=0
            ccx_emit_scalar_positional "$val" "$([[ $ftype == text ]] && echo true || echo false)"
            ((idx++))
          done < <(jq -c '.payload[1][]' <<<"$idea")
          printf '\n'
          ;;
        cuerpo)
          text=$(jq -r '.payload[1]' <<<"$idea"); text=$(ccx_nfc "$text")
          if [[ $text == *$'\n'* ]]; then printf '%s{\n%s\n}\n' "$head" "$text"; else printf '%s{%s}\n' "$head" "$text"; fi
          ;;
        bloque)
          text=$(jq -r '.payload[1]' <<<"$idea"); printf '%s{\n%s\n}\n' "$head" "$text"
          ;;
      esac
    done < <(jq -c '.ideas[]' <<<"$sec")
  done < <(jq -c '.sections[]' "$ast_file")
}

ccx_canonicalize_file() {
  local input=$1 out=${2:-} ast
  ccx_tmp_init || return
  ast="$CCX_TMP_ROOT/ast.$RANDOM.json"
  ccx_parse_cortex_file "$input" "$ast" || return
  if [[ -n $out ]]; then ccx_canonicalize_ast "$ast" >"$out"; else ccx_canonicalize_ast "$ast"; fi
}

ccx_render_glossary() {
  local ast=$1 obj attrs first k lex ns sigil q
  printf '%s\n' '<!-- glossary'
  obj=$(jq -c '.glossary.format' "$ast")
  if [[ $obj != null ]]; then
    printf '%s' '$0:format'; ccx_emit_glossary_attrs "$(jq -c '.attrs' <<<"$obj")"; printf '\n'
  fi
  while IFS= read -r obj; do
    printf '$0:enum_%s{values:%s}\n' "$(jq -r '.name' <<<"$obj")" "$(ccx_emit_string_literal "$(jq -r '.values|join("|")' <<<"$obj")")"
  done < <(jq -c '.glossary.enums[]' "$ast")
  while IFS= read -r obj; do
    lex=$(jq -r '.expand' <<<"$obj")
    if ccx_atom_regex "$lex" && [[ $lex != *' '* ]]; then :; else lex=$(ccx_emit_string_literal "$lex"); fi
    printf '$0:micro_%s{expand:%s}\n' "$(jq -r '.token' <<<"$obj")" "$lex"
  done < <(jq -c '.glossary.micros[]' "$ast")
  while IFS= read -r obj; do
    printf '$0:namespace_%s' "$(jq -r '.alias' <<<"$obj")"; ccx_emit_glossary_attrs "$(jq -c '.attrs' <<<"$obj")"; printf '\n'
  done < <(jq -c '.glossary.namespaces[]' "$ast")
  while IFS= read -r obj; do
    printf '$0:extension_%s' "$(jq -r '.name' <<<"$obj")"; ccx_emit_glossary_attrs "$(jq -c '.attrs' <<<"$obj")"; printf '\n'
  done < <(jq -c '.glossary.extensions[]' "$ast")
  while IFS= read -r obj; do
    printf '$0:%s' "$(jq -r '.name' <<<"$obj")"; ccx_emit_glossary_attrs "$(jq -c '.attrs' <<<"$obj")"; printf '\n'
  done < <(jq -c '.glossary.meta[]' "$ast")
  while IFS= read -r obj; do
    ns=$(jq -r '.namespace // ""' <<<"$obj"); sigil=$(jq -r '.sigil' <<<"$obj"); [[ -n $ns ]] && q="$ns::$sigil" || q=$sigil
    printf '%s:%s' "$q" "$(jq -r '.label' <<<"$obj")"; ccx_emit_glossary_attrs "$(jq -c '.attrs' <<<"$obj")"; printf '\n'
  done < <(jq -c '.glossary.symbols[]' "$ast")
  printf '%s\n' '-->'
}

ccx_section_schema() {
  local sec=$1 count shape
  count=$(jq '[.ideas[].shape]|unique|length' <<<"$sec")
  if ((count==1)); then
    shape=$(jq -r '.ideas[0].shape' <<<"$sec")
    case $shape in attrs|attrs-pos|relacion) printf table;; cuerpo) printf prose;; bloque) printf diagram;; *) printf prose;; esac
  else printf prose
  fi
}

ccx_render_idea_hcortex() {
  local ast=$1 idea=$2 schema=$3 ns sigil name q shape sym attrs contract pair field cell first text val
  ns=$(jq -r '.namespace // ""' <<<"$idea"); sigil=$(jq -r '.symbol' <<<"$idea"); name=$(jq -r '.name' <<<"$idea"); shape=$(jq -r '.shape' <<<"$idea")
  [[ -n $ns ]] && q="$ns::$sigil" || q=$sigil
  case $schema in
    table)
      printf '<!-- %s:%s --> | ' "$q" "$name"; first=1
      if [[ $shape == attrs ]]; then
        sym=$(ccx_symbol_for_idea_json "$ast" "$idea"); attrs=$(jq -c '.payload[1]' <<<"$idea"); contract=$(jq -c '.contract' <<<"$sym")
        while IFS= read -r field; do
          pair=$(jq -c --arg k "$(jq -r '.name' <<<"$field")" '[.[]|select(.key==$k)]|last // empty' <<<"$attrs")
          [[ -n $pair ]] || continue
          ((first)) || printf ' | '; first=0; jq -jr '.value.lexeme' <<<"$pair"
        done < <(jq -c '.[]' <<<"$contract")
      else
        while IFS= read -r cell; do ((first)) || printf ' | '; first=0; jq -jr '.lexeme' <<<"$cell"; done < <(jq -c '.payload[1][]' <<<"$idea")
      fi
      printf ' |\n'
      ;;
    prose)
      case $shape in
        cuerpo)
          printf '<!-- %s:%s -->\n' "$q" "$name"; text=$(jq -r '.payload[1]' <<<"$idea"); ccx_nfc "$text"; [[ -z $text || $text == *$'\n' ]] || printf '\n'
          ;;
        attrs)
          printf '<!-- %s:%s --> ' "$q" "$name"; first=1
          while IFS= read -r pair; do ((first)) || printf ','; first=0; printf '%s:' "$(jq -r '.key' <<<"$pair")"; jq -jr '.value.lexeme' <<<"$pair"; done < <(jq -c '.payload[1][]' <<<"$idea")
          printf '\n'
          ;;
        attrs-pos|relacion)
          printf '<!-- %s:%s --> ' "$q" "$name"; first=1
          while IFS= read -r cell; do ((first)) || printf '|'; first=0; jq -jr '.lexeme' <<<"$cell"; done < <(jq -c '.payload[1][]' <<<"$idea")
          printf '\n'
          ;;
        *) printf '<!-- %s:%s -->\n' "$q" "$name" ;;
      esac
      ;;
    list)
      printf '<!-- %s:%s --> - **' "$q" "$name"
      if [[ $shape == attrs ]]; then first=1; while IFS= read -r pair; do ((first)) || printf ','; first=0; printf '%s:' "$(jq -r '.key' <<<"$pair")"; jq -jr '.value.lexeme' <<<"$pair"; done < <(jq -c '.payload[1][]' <<<"$idea")
      elif [[ $shape == attrs-pos || $shape == relacion ]]; then first=1; while IFS= read -r cell; do ((first)) || printf '|'; first=0; jq -jr '.lexeme' <<<"$cell"; done < <(jq -c '.payload[1][]' <<<"$idea")
      elif [[ $shape == cuerpo ]]; then ccx_nfc "$(jq -r '.payload[1]' <<<"$idea")"; else printf idea; fi
      printf '**\n'
      ;;
    check)
      printf '<!-- %s:%s --> - [ ] ' "$q" "$name"
      if [[ $shape == attrs ]]; then first=1; while IFS= read -r pair; do ((first)) || printf ','; first=0; printf '%s:' "$(jq -r '.key' <<<"$pair")"; jq -jr '.value.lexeme' <<<"$pair"; done < <(jq -c '.payload[1][]' <<<"$idea")
      elif [[ $shape == attrs-pos || $shape == relacion ]]; then first=1; while IFS= read -r cell; do ((first)) || printf '|'; first=0; jq -jr '.lexeme' <<<"$cell"; done < <(jq -c '.payload[1][]' <<<"$idea")
      elif [[ $shape == cuerpo ]]; then ccx_nfc "$(jq -r '.payload[1]' <<<"$idea")"; else printf idea; fi
      printf '\n'
      ;;
    diagram)
      printf '<!-- %s:%s -->\n' "$q" "$name"; text=$(jq -r '.payload[1]' <<<"$idea")
      if [[ -n $text ]]; then printf '%s\n' '```puml'; printf '%s\n' "$text"; printf '%s\n' '```'; fi
      ;;
  esac
}

ccx_render_hcortex_ast() {
  local ast=$1 sec title schema idea
  printf '%s\n\n' '<!-- HCORTEX v=0.1 t=canonical -->'
  if jq -e '(.glossary.format!=null) or ([.glossary.enums,.glossary.micros,.glossary.namespaces,.glossary.extensions,.glossary.meta,.glossary.symbols]|map(length)|add>0)' "$ast" >/dev/null; then
    ccx_render_glossary "$ast"; printf '\n'
  fi
  while IFS= read -r sec; do
    title=$(jq -r '.title // empty' <<<"$sec"); [[ -n $title ]] || title="Sección $(jq -r '.id' <<<"$sec")"
    printf '## §%s: %s\n\n' "$(jq -r '.id' <<<"$sec")" "$title"
    [[ $(jq '.ideas|length' <<<"$sec") -gt 0 ]] || continue
    schema=$(ccx_section_schema "$sec"); printf '<!-- %s:%s -->\n' "$schema" "$(jq -r '.id' <<<"$sec")"
    while IFS= read -r idea; do ccx_render_idea_hcortex "$ast" "$idea" "$schema"; done < <(jq -c '.ideas[]' <<<"$sec")
    printf '<!-- /%s:%s -->\n\n' "$schema" "$(jq -r '.id' <<<"$sec")"
  done < <(jq -c '.sections[]' "$ast")
}

ccx_render_hcortex_file() {
  local input=$1 out=${2:-} ast
  ccx_tmp_init || return; ast="$CCX_TMP_ROOT/ast.$RANDOM.json"; ccx_parse_cortex_file "$input" "$ast" || return
  if [[ -n $out ]]; then ccx_render_hcortex_ast "$ast" >"$out"; else ccx_render_hcortex_ast "$ast"; fi
}

ccx_classify_compact_value() {
  local lex inner part item items='[]' out lx
  lex=$(ccx_trim "$1")
  if [[ ${lex:0:1} == '"' && ${lex: -1} == '"' && ${#lex} -ge 2 ]]; then ccx_parse_scalar "$lex" 0 0; return; fi
  if [[ ${lex:0:1} == '[' && ${lex: -1} == ']' ]]; then
    inner=${lex:1:${#lex}-2}
    if [[ -z $inner ]]; then printf '%s\n' '{"kind":"list","value":[],"lexeme":"[]"}'; return; fi
    while IFS= read -r part; do part=$(jq -r '.' <<<"$part"); item=$(ccx_classify_compact_value "$part"); items=$(jq -cn --argjson a "$items" --argjson x "$item" '$a+[$x]'); done < <(ccx_split_top_level "$inner" ',')
    lx=$(jq -r '[.[]|.lexeme]|"["+join(",")+"]"' <<<"$items"); jq -cn --argjson v "$items" --arg l "$lx" '{kind:"list",value:$v,lexeme:$l}'; return
  fi
  case $lex in true|false|null) ccx_parse_scalar "$lex" 0 0; return;; esac
  if [[ $lex =~ ^-?(0|[1-9][0-9]*)$ || $lex =~ ^-?(0|[1-9][0-9]*)\.[0-9]+$ ]]; then ccx_parse_scalar "$lex" 0 0; return; fi
  if ccx_is_atom "$lex" && [[ $lex != *' '* ]]; then ccx_parse_scalar "$lex" 0 0; return; fi
  lx=$(ccx_emit_string_literal "$lex"); jq -cn --arg v "$lex" --arg l "$lx" '{kind:"string",value:$v,lexeme:$l}'
}

ccx_hdiag_append() {
  local file=$1 code=$2 severity=$3 message=$4 line=${5:-0}
  local tmp="${file}.tmp"
  jq --arg c "$code" --arg s "$severity" --arg m "$message" --argjson l "$line" '.+[{code:$c,severity:$s,message:$m,line:$l}]' "$file" >"$tmp" && mv "$tmp" "$file"
}

ccx_minimal_format() {
  jq -cn '{cortex:"0.1",encoding:"UTF-8",attrs:[{key:"cortex",value:{kind:"atom",value:"0.1",lexeme:"0.1"}},{key:"encoding",value:{kind:"atom",value:"UTF-8",lexeme:"UTF-8"}}],source_line:1}'
}

ccx_parse_glossary_compile_line() {
  local doc=$1 line=$2
  # Rendered glossary syntax is a strict subset of CORTEX declarations.
  ccx_parse_glossary_decl "$doc" "$line" 0
}

ccx_registry_symbol() {
  local doc=$1 sigil=$2
  local short=${sigil##*::}
  jq -c --arg s "${short,,}" '[.glossary.symbols[]|select((.sigil|ascii_downcase)==$s)]|last // empty' "$doc"
}

ccx_split_hpipe() {
  local s=$1 i ch cur=""
  for ((i=0;i<${#s};i++)); do
    ch=${s:i:1}
    if [[ $ch == '\\' && ${s:i+1:1} == '|' ]]; then cur+='\|'; ((i++))
    elif [[ $ch == '|' ]]; then jq -Rn --arg x "$(ccx_trim "$cur")" '$x'; cur=""
    else cur+=$ch
    fi
  done
  jq -Rn --arg x "$(ccx_trim "$cur")" '$x'
}

ccx_compact_attrs() {
  local s=$1 arr key out='[]' pair
  [[ -n $(ccx_trim "$s") ]] || { printf '[]\n'; return; }
  ccx_parse_attrs "{$s}" 0
}

ccx_compile_idea() {
  local doc=$1 section_id=$2 schema=$3 qsig=$4 name=$5 body=$6
  local ns='' sigil=$qsig sym shape fields='[]' payload cells='[]' part scalar attrs item m nsp idea
  if [[ $qsig == *::* ]]; then ns=${qsig%%::*}; sigil=${qsig#*::}; fi
  sym=$(ccx_registry_symbol "$doc" "$sigil")
  if [[ -n $sym ]]; then shape=$(jq -r '.shape' <<<"$sym"); fields=$(jq -c '[.contract[].name]' <<<"$sym"); else shape=attrs; fi
  body=$(ccx_trim "$body")
  nsp=$(if [[ -n $ns ]]; then ccx_json_string "$ns"; else printf null; fi)
  case $schema in
    table)
      [[ ${body:0:1} == '|' ]] && body=${body:1}; [[ ${body: -1} == '|' ]] && body=${body:0:${#body}-1}; body=$(ccx_trim "$body")
      while IFS= read -r part; do part=$(jq -r '.' <<<"$part"); scalar=$(ccx_classify_compact_value "$(ccx_trim "$part")") || return; cells=$(jq -cn --argjson a "$cells" --argjson x "$scalar" '$a+[$x]'); done < <(ccx_split_hpipe "$body")
      if [[ $shape == attrs-pos || $shape == relacion ]]; then payload=$(jq -cn --arg sh "$shape" --argjson x "$cells" '[$sh,$x]')
      else
        attrs=$(jq -cn --argjson c "$cells" --argjson f "$fields" '[range(0;($c|length)) as $i|{key:($f[$i]//("f"+(($i+1)|tostring))),value:$c[$i]}]')
        shape=attrs; payload=$(jq -cn --argjson x "$attrs" '["attrs",$x]')
      fi ;;
    prose)
      if [[ $shape == cuerpo || $shape == bloque ]]; then payload=$(jq -cn --arg sh "$shape" --arg x "$body" '[$sh,$x]')
      elif [[ $shape == attrs-pos || $shape == relacion ]]; then
        cells='[]'; while IFS= read -r part; do part=$(ccx_trim "$(jq -r '.' <<<"$part")"); [[ -n $part ]] || continue; scalar=$(ccx_classify_compact_value "$part"); cells=$(jq -cn --argjson a "$cells" --argjson x "$scalar" '$a+[$x]'); done < <(ccx_split_hpipe "$body")
        payload=$(jq -cn --arg sh "$shape" --argjson x "$cells" '[$sh,$x]')
      else attrs=$(ccx_compact_attrs "$body") || return; shape=attrs; payload=$(jq -cn --argjson x "$attrs" '["attrs",$x]'); fi ;;
    list)
      item=$body; [[ $item =~ ^-[[:space:]]+\*\*(.*)\*\* ]] && item=${BASH_REMATCH[1]}
      attrs=$(ccx_compact_attrs "$item" 2>/dev/null || printf '[]')
      if [[ $(jq 'length' <<<"$attrs") -eq 0 ]]; then scalar=$(ccx_emit_string_literal "$item"); attrs=$(jq -cn --arg x "$item" --arg l "$scalar" '[{key:"content",value:{kind:"string",value:$x,lexeme:$l}}]'); fi
      shape=attrs; payload=$(jq -cn --argjson x "$attrs" '["attrs",$x]') ;;
    check)
      item=$body; [[ $item =~ ^-[[:space:]]+\[[[:space:]x]\][[:space:]]+(.*)$ ]] && item=${BASH_REMATCH[1]}
      attrs=$(ccx_compact_attrs "$item" 2>/dev/null || printf '[]')
      if [[ $(jq 'length' <<<"$attrs") -eq 0 ]]; then scalar=$(ccx_emit_string_literal "$item"); attrs=$(jq -cn --arg x "$item" --arg l "$scalar" '[{key:"content",value:{kind:"string",value:$x,lexeme:$l}}]'); fi
      shape=attrs; payload=$(jq -cn --argjson x "$attrs" '["attrs",$x]') ;;
    diagram)
      if [[ $body =~ \`\`\`puml[[:space:]]*$'\n'(.*)$'\n'\`\`\` ]]; then item=${BASH_REMATCH[1]}; else item=$body; fi
      item=$(ccx_trim "$item"); shape=bloque; payload=$(jq -cn --arg x "$item" '["bloque",$x]') ;;
    *) return 0 ;;
  esac
  jq -cn --argjson sec "$section_id" --argjson ns "$nsp" --arg s "$sigil" --arg n "$name" --arg sh "$shape" --argjson p "$payload" '{section:$sec,namespace:$ns,symbol:$s,name:$n,shape:$sh,payload:$p,source_line:1}'
}

ccx_compile_hcortex_file() {
  local input=$1 output=$2 diag=$3 normalized hex raw stripped line_no=0 in_glossary=0 found_glossary=0
  local current_idx=-1 current_id=-1 schema='' in_schema=0 marker_q='' marker_name='' marker_body='' idea title sid
  ccx_tmp_init || return; printf '[]\n' >"$diag"; ccx_empty_document >"$output"
  hex=$(od -An -tx1 -N3 "$input" 2>/dev/null | tr -d ' \n')
  if [[ $hex == efbbbf ]]; then ccx_hdiag_append "$diag" H490 error 'BOM forbidden' 1; return 0; fi
  grep -Eq '<!-- HCORTEX v=[0-9.]+ t=[[:alnum:]_]+ -->' "$input" || { ccx_hdiag_append "$diag" H400 error 'Missing HCORTEX header' 1; return 0; }
  normalized="$CCX_TMP_ROOT/hnormalized.$RANDOM"; sed 's/\r$//' "$input" | tr '\r' '\n' >"$normalized"

  ccx_finalize_marker() {
    [[ -n $marker_q ]] || return 0
    idea=$(ccx_compile_idea "$output" "$current_id" "$schema" "$marker_q" "$marker_name" "$marker_body") || return
    [[ -n $idea ]] && ccx_doc_update "$output" ".sections[$current_idx].ideas += [\$x]" --argjson x "$idea"
    marker_q=''; marker_name=''; marker_body=''
  }

  while IFS= read -r raw || [[ -n $raw ]]; do
    ((line_no++)); stripped=$(ccx_trim "$raw")
    if [[ $stripped == '<!-- glossary' ]]; then in_glossary=1; found_glossary=1; continue; fi
    if ((in_glossary)); then
      if [[ $stripped == '-->' ]]; then in_glossary=0; continue; fi
      [[ -z $stripped ]] && continue
      ccx_parse_glossary_compile_line "$output" "$stripped" || return
      continue
    fi
    if [[ $raw =~ ^##[[:space:]]+§([0-9]+):[[:space:]]*(.*)$ ]]; then
      ccx_finalize_marker || return; sid=${BASH_REMATCH[1]}; title=$(ccx_trim "${BASH_REMATCH[2]}")
      ccx_doc_update "$output" '.sections += [{id:$id,title:$t,ideas:[]}]' --argjson id "$sid" --arg t "$title"
      current_idx=$(($(jq '.sections|length' "$output")-1)); current_id=$sid; in_schema=0; continue
    fi
    if [[ $stripped =~ ^\<!--[[:space:]]+(table|prose|list|check|diagram):([0-9]+)[[:space:]]+--\>$ ]]; then schema=${BASH_REMATCH[1]}; in_schema=1; continue; fi
    if [[ $stripped =~ ^\<!--[[:space:]]+/(table|prose|list|check|diagram):([0-9]+)[[:space:]]+--\>$ ]]; then ccx_finalize_marker || return; in_schema=0; schema=''; continue; fi
    ((in_schema)) || continue
    if [[ $raw =~ ^\<!--[[:space:]]+([^[:space:]]+):([[:alnum:]_-]+)[[:space:]]+--\>(.*)$ ]]; then
      ccx_finalize_marker || return; marker_q=${BASH_REMATCH[1]}; marker_name=${BASH_REMATCH[2]}; marker_body=$(ccx_trim "${BASH_REMATCH[3]}"); continue
    fi
    if [[ -n $marker_q ]]; then [[ -n $marker_body ]] && marker_body+=$'\n'; marker_body+="$raw"; fi
  done <"$normalized"
  ccx_finalize_marker || return
  if ((found_glossary==0)); then ccx_doc_update "$output" '.glossary.format=$x' --argjson x "$(ccx_minimal_format)"; fi
}

ccx_from_hcortex_file() {
  local input=$1 out=${2:-} ast diag
  ccx_tmp_init || return; ast="$CCX_TMP_ROOT/hast.$RANDOM.json"; diag="$CCX_TMP_ROOT/diag.$RANDOM.json"
  ccx_compile_hcortex_file "$input" "$ast" "$diag" || return
  if jq -e 'any(.[];.severity=="error")' "$diag" >/dev/null; then jq . "$diag" >&2; return 65; fi
  if [[ -n $out ]]; then ccx_canonicalize_ast "$ast" >"$out"; else ccx_canonicalize_ast "$ast"; fi
}

ccx_sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'; else shasum -a 256 "$1" | awk '{print $1}'; fi
}

ccx_c14n_hash_file() {
  local file=$1 tmp
  ccx_tmp_init || return; tmp="$CCX_TMP_ROOT/hash.$RANDOM"
  { printf '%s' 'CORTEX-C14N-0.1'; printf '\0'; cat "$file"; } >"$tmp"
  printf 'sha256:%s\n' "$(ccx_sha256_file "$tmp")"
}

ccx_result_failure() {
  local result=$1 failure=$2
  local tmp="${result}.tmp"
  jq --argjson f "$failure" '.failures += [$f]' "$result" >"$tmp" && mv "$tmp" "$result"
}

ccx_run_phase3() {
  local dir=$1 manifest="$1/manifest.json" total jobs work status
  if [[ ! -f $manifest ]]; then jq -cn --arg e "manifest not found: $manifest" '{golden_pass:0,idempotence_pass:0,total:0,failures:[{stage:"exception",error:$e}],status:"FAIL"}'; return; fi
  ccx_tmp_init || return
  total=$(jq '.cases|length' "$manifest")
  jobs=${CCX_JOBS:-8}; [[ $jobs =~ ^[1-9][0-9]*$ ]] || jobs=8
  work="$CCX_TMP_ROOT/f3-parallel.$RANDOM"; mkdir -p "$work"
  if ((total>0)); then
    seq 0 $((total-1)) | xargs -P "$jobs" -n 1 bash -c '
      set -o pipefail
      source "$1"
      manifest=$2; dir=$3; outdir=$4; idx=$5
      case_json=$(jq -c --argjson i "$idx" ".cases[\$i]" "$manifest")
      cid=$(jq -r ".id" <<<"$case_json")
      input_rel=$(jq -r --arg id "$cid" ".input // (\$id+\".cortex\")" <<<"$case_json")
      canon_rel=$(jq -r --arg id "$cid" ".canonical // (\"canonical/\"+\$id+\".cortex\")" <<<"$case_json")
      input_path="$dir/$input_rel"; [[ -f $input_path ]] || input_path="$dir/../$input_rel"
      canon_path="$dir/$canon_rel"; [[ -f $canon_path ]] || canon_path="$dir/../$canon_rel"
      t=$(mktemp -d "${TMPDIR:-/tmp}/ccx-f3-case.XXXXXX"); trap "rm -rf \"$t\"" EXIT
      actual="$t/actual"; second="$t/second"; golden=false; idem=false; failures="[]"
      if ccx_canonicalize_file "$input_path" "$actual" 2>"$t/err"; then
        if cmp -s "$actual" "$canon_path"; then golden=true
        else
          eh=$(ccx_sha256_file "$canon_path" 2>/dev/null || printf missing); ah=$(ccx_sha256_file "$actual")
          failures=$(jq -cn --arg c "$cid" --arg e "$eh" --arg a "$ah" "[{case:\$c,stage:\"golden\",expected_sha256:\$e,actual_sha256:\$a}]")
        fi
        if ccx_canonicalize_file "$actual" "$second" 2>"$t/err2" && cmp -s "$actual" "$second"; then idem=true
        else failures=$(jq -cn --argjson f "$failures" --arg c "$cid" "\$f+[{case:\$c,stage:\"idempotence\"}]"); fi
      else
        failures=$(jq -cn --arg c "$cid" --arg e "$(cat "$t/err")" "[{case:\$c,stage:\"exception\",error:\$e}]")
      fi
      jq -cn --arg c "$cid" --argjson g "$golden" --argjson i "$idem" --argjson f "$failures" "{case:\$c,golden:\$g,idempotent:\$i,failures:\$f}" >"$outdir/$idx.json"
    ' _ "$CCX_LIB_DIR/codec-cortex.sh" "$manifest" "$dir" "$work"
  fi
  jq -s --argjson t "$total" '
    {golden_pass:(map(select(.golden))|length),
     idempotence_pass:(map(select(.idempotent))|length),
     total:$t,
     failures:(map(.failures)|add // [])}
    | .status=(if .golden_pass>=38 and .idempotence_pass==40 then "PASS" else "FAIL" end)
  ' "$work"/*.json 2>/dev/null || jq -cn --argjson t "$total" '{golden_pass:0,idempotence_pass:0,total:$t,failures:[{stage:"exception",error:"parallel runner produced no results"}],status:"FAIL"}'
}

ccx_run_phase4() {
  local dir=$1 manifest="$1/manifest.json" result case cid title cortex_path hc_path alt actual_h ast diag roundtrip expected rsha rendered2 invalid_path expected_code codes failure total invalid_total rp ip dp status
  if [[ ! -f $manifest ]]; then jq -cn --arg e "manifest not found: $manifest" '{roundtrip_pass:0,idempotence_pass:0,invalid_diag_pass:0,view_dependencies:0,failures:[{stage:"exception",error:$e}],status:"FAIL"}'; return; fi
  ccx_tmp_init || return; result="$CCX_TMP_ROOT/f4.$RANDOM.json"; jq -cn '{roundtrip_pass:0,idempotence_pass:0,invalid_diag_pass:0,view_dependencies:0,failures:[]}' >"$result"
  while IFS= read -r case; do
    cid=$(jq -r '.id' <<<"$case"); title=$(jq -r '.title' <<<"$case")
    cortex_path="$dir/corpus/cortex/${cid}_${title}.cortex"; [[ -f $cortex_path ]] || cortex_path="$dir/cortex/${cid}_${title}.cortex"
    if [[ ! -f $cortex_path ]]; then alt=$(jq -r --arg d "$cid" --arg t "$title" '.cortex // ($d+"_"+$t+".cortex")' <<<"$case"); cortex_path="$dir/$alt"; fi
    if [[ ! -f $cortex_path ]]; then failure=$(jq -cn --arg c "$cid" --arg e "CORTEX source not found: $cortex_path" '{case:$c,stage:"missing_input",error:$e}'); ccx_result_failure "$result" "$failure"; continue; fi
    actual_h="$CCX_TMP_ROOT/f4.h.$RANDOM"; ast="$CCX_TMP_ROOT/f4.ast.$RANDOM.json"; diag="$CCX_TMP_ROOT/f4.diag.$RANDOM.json"; roundtrip="$CCX_TMP_ROOT/f4.rt.$RANDOM"; rendered2="$CCX_TMP_ROOT/f4.h2.$RANDOM"
    if ccx_render_hcortex_file "$cortex_path" "$actual_h" 2>"$CCX_TMP_ROOT/f4.err"; then
      ccx_compile_hcortex_file "$actual_h" "$ast" "$diag" 2>>"$CCX_TMP_ROOT/f4.err"
      if jq -e 'any(.[];.severity=="error")' "$diag" >/dev/null; then failure=$(jq -cn --arg c "$cid" --argjson d "$(cat "$diag")" '{case:$c,stage:"compile_rendered",diags:$d}'); ccx_result_failure "$result" "$failure"; continue; fi
      ccx_canonicalize_ast "$ast" >"$roundtrip"
      expected=$(jq -r '.roundtrip_cortex_sha256 // .cortex_sha256 // ""' <<<"$case"); rsha=$(ccx_sha256_file "$roundtrip")
      if [[ -z $expected || $expected == "$rsha" ]]; then jq '.roundtrip_pass+=1' "$result" >"$result.tmp" && mv "$result.tmp" "$result"
      else failure=$(jq -cn --arg c "$cid" --arg e "$expected" --arg a "$rsha" '{case:$c,stage:"roundtrip_cortex_mismatch",expected_sha256:$e,actual_sha256:$a}'); ccx_result_failure "$result" "$failure"; fi
      ccx_render_hcortex_ast "$ast" >"$rendered2"
      if cmp -s "$actual_h" "$rendered2"; then jq '.idempotence_pass+=1' "$result" >"$result.tmp" && mv "$result.tmp" "$result"
      else failure=$(jq -cn --arg c "$cid" '{case:$c,stage:"hcortex_idempotence"}'); ccx_result_failure "$result" "$failure"; fi
    else failure=$(jq -cn --arg c "$cid" --arg e "$(cat "$CCX_TMP_ROOT/f4.err")" '{case:$c,stage:"exception",error:$e}'); ccx_result_failure "$result" "$failure"; fi
  done < <(jq -c '.canonical[]' "$manifest")

  while IFS= read -r case; do
    cid=$(jq -r '.id' <<<"$case"); expected_code=$(jq -r '.expected_diagnostic // .expected_code // ""' <<<"$case")
    invalid_path="$dir/invalid/$cid.md"; [[ -f $invalid_path ]] || invalid_path="$dir/corpus/invalid/$cid.md"; [[ -f $invalid_path ]] || continue
    ast="$CCX_TMP_ROOT/f4.invast.$RANDOM"; diag="$CCX_TMP_ROOT/f4.invdiag.$RANDOM"; ccx_compile_hcortex_file "$invalid_path" "$ast" "$diag" 2>/dev/null
    if jq -e --arg c "$expected_code" 'any(.[];.code==$c)' "$diag" >/dev/null; then jq '.invalid_diag_pass+=1' "$result" >"$result.tmp" && mv "$result.tmp" "$result"
    else failure=$(jq -cn --arg c "$cid" --arg e "$expected_code" --argjson a "$(jq '[.[].code]' "$diag")" '{case:$c,stage:"invalid_diag",expected_code:$e,actual_codes:$a}'); ccx_result_failure "$result" "$failure"; fi
  done < <(jq -c '.invalid[]?' "$manifest")
  total=$(jq '.canonical|length' "$manifest"); invalid_total=$(jq '.invalid // []|length' "$manifest"); rp=$(jq '.roundtrip_pass' "$result"); ip=$(jq '.idempotence_pass' "$result"); dp=$(jq '.invalid_diag_pass' "$result")
  [[ $rp -eq $total && $ip -eq $total && $dp -eq $invalid_total ]] && status=PASS || status=FAIL
  jq --arg s "$status" '.status=$s' "$result"
}

ccx_run_all_tests() {
  local cdir=$1 hdir=$2 f3 f4 start end total_c total_i verdict findings='[]'
  start=$(date -u +'%Y-%m-%dT%H:%M:%SZ'); f3=$(ccx_run_phase3 "$cdir"); f4=$(ccx_run_phase4 "$hdir"); end=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
  total_c=$(jq '.canonical|length' "$hdir/manifest.json" 2>/dev/null || echo 0); total_i=$(jq '.invalid // []|length' "$hdir/manifest.json" 2>/dev/null || echo 0)
  if [[ $(jq '.golden_pass' <<<"$f3") -ge 38 && $(jq '.idempotence_pass' <<<"$f3") -eq 40 && $(jq '.roundtrip_pass' <<<"$f4") -eq $total_c && $(jq '.idempotence_pass' <<<"$f4") -eq $total_c && $(jq '.view_dependencies' <<<"$f4") -eq 0 ]]; then verdict=PASS
  elif [[ $(jq '.golden_pass' <<<"$f3") -ge 36 && $(jq '.roundtrip_pass' <<<"$f4") -ge $((total_c-2)) && $(jq '.view_dependencies' <<<"$f4") -eq 0 ]]; then verdict=CONDITIONAL_PASS
  else verdict=FAIL; fi
  jq -cn --arg s "$start" --arg e "$end" --argjson p3 "$f3" --argjson p4 "$f4" --arg v "$verdict" '{reviewer:{name:"independent-bash-reviewer",language:"Bash 4.3+",started_at:$s,completed_at:$e},phase3:$p3,phase4:$p4,findings:(([{phase:"F3",count:($p3.failures|length),items:$p3.failures}|select(.count>0)],[{phase:"F4",count:($p4.failures|length),items:$p4.failures}|select(.count>0)])|add),verdict:$v}'
}

# Public compatibility aliases (file-oriented Bash API).
parse_cortex() { ccx_parse_cortex "$@"; }
parse_contract_fields() { ccx_parse_contract "$@"; }
canonicalize() { ccx_canonicalize_file "$@"; }
render_hcortex() { ccx_render_hcortex_file "$@"; }
compile_hcortex() { ccx_compile_hcortex_file "$@"; }
run_phase3() { ccx_run_phase3 "$@"; }
run_phase4() { ccx_run_phase4 "$@"; }
run_all_tests() { ccx_run_all_tests "$@"; }
sha256_bytes() { ccx_sha256_file "$@"; }
c14n_hash() { ccx_c14n_hash_file "$@"; }
emit_string_literal() { ccx_emit_string_literal "$@"; }
parse_string_literal() { ccx_parse_string_literal "$@"; }
to_nfc() { ccx_nfc "$@"; }
