#!/usr/bin/env bash
# CORTEX 1.0 declared loss report (spec §8.2 / §8.3) — reference-parity surface.

ccx_loss_detail() {
  case $1 in
    L402_COMMENT_DROPPED) printf '%s' 'comment line outside a multiline body is not represented in the AST' ;;
    L403_INTRALINE_WHITESPACE) printf '%s' 'intraline whitespace is collapsed by canonicalization' ;;
    L405_OPEN_ATTR_ORDER) printf '%s' 'editorial attribute order of an open sigil is not preserved' ;;
    L499_UNCLASSIFIED_LOSS) printf '%s' 'roundtrip diverges and no declared loss classifies the divergence' ;;
  esac
}

ccx_loss_finding() { # code path category recoverability
  local code=$1 path=$2 category=$3 recoverability=$4 severity=loss action=declare-only detail
  if [[ $code == L499_UNCLASSIFIED_LOSS ]]; then severity=error; action=fix-surface; fi
  detail=$(ccx_loss_detail "$code")
  jq -cn --arg action "$action" --arg category "$category" --arg code "$code" \
    --arg detail "$detail" --arg path "$path" --arg recoverability "$recoverability" \
    --arg severity "$severity" \
    '{action:$action,category:$category,code:$code,detail:$detail,path:$path,recoverability:$recoverability,severity:$severity}'
}

ccx_loss_lexical() { # input -> TSV: path code category recoverability
  awk '
    function trim(s) { sub(/^[ \t]+/, "", s); sub(/[ \t]+$/, "", s); return s }
    {
      raw = $0
      sub(/\r$/, "", raw)
      t = trim(raw)
      if (inbody) { if (t == "}") inbody = 0; next }
      if (t == "") next
      if (substr(t, 1, 1) == "#") {
        printf "line:%d\tL402_COMMENT_DROPPED\tstructure\tfrom-source-only\n", NR
        next
      }
      if (substr(t, length(t)) == "{" && substr(t, 1, 3) != "$0:") inbody = 1
      probe = raw
      gsub(/"([^"\\]|\\.)*"/, "\"\"", probe)
      ws = 0
      if (probe ~ /[ \t]$/) ws = 1
      if (probe ~ /\t/) ws = 1
      if (probe ~ /  /) ws = 1
      if (ws) printf "line:%d\tL403_INTRALINE_WHITESPACE\tpresentation\tfrom-source-only\n", NR
    }
  ' "$1"
}

ccx_loss_attr_order() { # ast -> TSV: path code category recoverability
  jq -r '
    . as $doc
    | $doc.sections[]?
    | . as $sec
    | $sec.ideas[]?
    | select(.shape == "attrs" and (.payload | type) == "array" and .payload[0] == "attrs")
    | . as $idea
    | first($doc.glossary.symbols[]?
        | select(.sigil == $idea.symbol and ((.namespace // null) == ($idea.namespace // null)))) as $sym
    | select($sym != null and $sym.open == true)
    | ([ $idea.payload[1][] | .key ]) as $keys
    | ([ $sym.contract[]? | .name ]) as $contract
    | ([ $contract[] as $c | select($keys | index($c)) | $c ]) as $base
    | ([ $keys[] as $k | select(($contract | index($k)) | not) | $k ] | sort) as $extras
    | select($keys != ($base + $extras))
    | (("$" + ($sec.id | tostring)) + "\tL405_OPEN_ATTR_ORDER\torder\tfrom-source-only")
  ' "$1"
}

ccx_loss_case_name() { # path
  local base
  if [[ -z ${1:-} || $1 == '-' ]]; then printf '%s' stdin; return; fi
  base=$(basename -- "$1")
  if [[ $base == *.* && ${base%.*} != '' ]]; then base=${base%.*}; fi
  printf '%s' "$base"
}

ccx_loss_report_file() { # input case_name -> canonical JSON on stdout
  local input=$1 case_name=$2
  local ast rend rt diag can1 can2 src_sha tgt_sha reversible losses
  ccx_tmp_init || return 1
  ast="$CCX_TMP_ROOT/loss_ast.$RANDOM.json"
  rend="$CCX_TMP_ROOT/loss_rend.$RANDOM.md"
  rt="$CCX_TMP_ROOT/loss_rt.$RANDOM.json"
  diag="$CCX_TMP_ROOT/loss_diag.$RANDOM.json"
  can1="$CCX_TMP_ROOT/loss_c1.$RANDOM"
  can2="$CCX_TMP_ROOT/loss_c2.$RANDOM"

  ccx_parse_cortex_file "$input" "$ast" || return 1
  if [[ $(jq -r '.cortex_version' "$ast") != 1.0 ]]; then
    ccx_error G007_UNSUPPORTED_VERSION 'loss-report requires cortex:1.0' 0 0
    return 1
  fi

  ccx_render_hcortex_ast "$ast" >"$rend" || return 1
  ccx_canonicalize_ast "$ast" >"$can1" || return 1
  ccx_compile_hcortex_file "$rend" "$rt" "$diag" || return 1
  if [[ $(jq 'length' "$diag" 2>/dev/null || printf 0) -gt 0 ]]; then
    ccx_error H400 'HCORTEX roundtrip compilation failed' 0 0
    return 1
  fi
  ccx_canonicalize_ast "$rt" >"$can2" || return 1

  reversible=false
  if cmp -s "$can1" "$can2"; then reversible=true; fi

  src_sha=$(sha256sum "$input" | cut -d' ' -f1)
  tgt_sha=$(sha256sum "$rend" | cut -d' ' -f1)

  losses=$(
    {
      ccx_loss_lexical "$input"
      ccx_loss_attr_order "$ast"
      if [[ $reversible != true ]]; then printf '$\tL499_UNCLASSIFIED_LOSS\tstructure\tirrecoverable\n'; fi
    } | while IFS=$'\t' read -r path code category recoverability; do
      [[ -n $path ]] || continue
      ccx_loss_finding "$code" "$path" "$category" "$recoverability"
    done | jq -sc 'sort_by(.path, .code) | unique_by([.path, .code])'
  )

  jq -n --arg case_name "$case_name" --argjson losses "$losses" \
    --argjson reversible "$reversible" --arg src_sha "$src_sha" --arg tgt_sha "$tgt_sha" \
    '{
      case:$case_name,
      losses:$losses,
      mode:"canonical",
      operation:"render",
      preserved:["blocks","identity","scalars","structure"],
      reversible:$reversible,
      schema_version:"1.0",
      source_format:"cortex:1.0",
      source_sha256:$src_sha,
      structural_equivalence:$reversible,
      target_format:"hcortex:1.0",
      target_sha256:$tgt_sha,
      warnings:[]
    }' | jq -S .
}

ccx_loss_report_exit_code() { # report json
  if jq -e '[.losses[] | select(.severity == "error")] | length > 0' <<<"$1" >/dev/null; then return 1; fi
  return 0
}
