#!/bin/bash
# C14N-0.1 Canonicalization — Pure Bash (v3)
# Usage: c14n.sh [file]  →  canonical CORTEX text on stdout, JSON report on stderr
set -eo pipefail

CHANGES_ORDERED=()
add_change() { local c; for c in "${CHANGES_ORDERED[@]}"; do [ "$c" = "$1" ] && return; done; CHANGES_ORDERED+=("$1"); }

json_esc() { local s="$1"; s="${s//\\/\\\\}"; s="${s//\"/\\\"}"; printf '%s' "$s"; }

colpos() {
    local s="$1" i c q=0
    for ((i=0; i<${#s}; i++)); do
        c="${s:$i:1}"; [ "$q" -eq 1 ] && { [ "$c" = '\' ] && i=$((i+1)); [ "$c" = '"' ] && q=0; continue; }
        [ "$c" = '"' ] && q=1; [ "$c" = ':' ] && { echo $i; return; }
    done; echo -1
}

atom_safe() {
    local s="$1" i c; [ -z "$s" ] && return 1
    for ((i=0; i<${#s}; i++)); do
        c="${s:$i:1}"
        case "$c" in ' '|$'\t'|$'\n'|'['|']'|'{'|'}'|','|'"'|'|') return 1 ;; esac
    done; return 0
}

decode_string() {
    local s="$1" out="" i c
    for ((i=0; i<${#s}; i++)); do
        c="${s:$i:1}"
        if [ "$c" = '\' ] && [ $i -lt $((${#s}-1)) ]; then
            local n="${s:$((i+1)):1}"
            case "$n" in
                '"') out+='"'; i=$((i+1)) ;;
                '\') out+='\'; i=$((i+1)) ;;
                '/') out+='/'; i=$((i+1)) ;;
                n) out+=$'\n'; i=$((i+1)) ;;
                r) out+=$'\r'; i=$((i+1)) ;;
                t) out+=$'\t'; i=$((i+1)) ;;
                b) out+=$'\b'; i=$((i+1)) ;;
                f) out+=$'\f'; i=$((i+1)) ;;
                u)
                    local hex="${s:$((i+2)):4}" dec=0
                    printf -v dec '%d' 0x$hex 2>/dev/null || dec=0
                    printf -v ch '\\U%08x' $dec 2>/dev/null
                    out+="$ch"
                    i=$((i+5))
                    ;;
                *) out+="$c" ;;
            esac
        else out+="$c"; fi
    done; echo "$out"
}

emit_string_v2() {
    local v="$1" out="\"" i c cp
    for ((i=0; i<${#v}; i++)); do
        c="${v:$i:1}"
        case "$c" in
            '"') out+='\"' ;;
            '\') out+='\\' ;;
            $'\b') out+='\b' ;;
            $'\f') out+='\f' ;;
            $'\n') out+='\n' ;;
            $'\r') out+='\r' ;;
            $'\t') out+='\t' ;;
            *)
                printf -v cp '%d' "'$c"
                [ "$cp" -lt 32 -o "$cp" -eq 127 ] && { printf -v hex '%04X' "$cp"; out+="\\u$hex"; } || out+="$c"
                ;;
        esac
    done; out+='"'; echo "$out"
}

emit_scalar() {
    local v="$1" kind="$2"
    case "$kind" in
        string) emit_string_v2 "$v" ;;
        atom) atom_safe "$v" && echo "$v" || emit_string_v2 "$v" ;;
        int) [ "$v" = "0" -o "$v" = "-0" ] && { echo "0"; return; }
            local neg=""; [[ "$v" == -* ]] && neg="-" && v="${v:1}"; v="${v#0}"; v="${v#0}"
            [ -z "$v" ] && v="0"; echo "${neg}${v}" ;;
        dec) echo "$v" ;;
        bool) [ "$v" = "true" ] && echo "true" || echo "false" ;;
        null) echo "null" ;;
        *) echo "$v" ;;
    esac
}

declare -A SYM_CONTRACT SYM_FOCUS SYM_SHAPE MICRO_EXPAND
init_sym_info() { local s="$1" c="$2" f="$3" h="$4"; SYM_CONTRACT["$s"]="$c"; SYM_FOCUS["$s"]="$f"; SYM_SHAPE["$s"]="$h"; }

ATTR_KEYS=(); ATTR_VALS=(); ATTR_KINDS=(); ATTR_COUNT=0

parse_attrs() {
    local inner="$1"
    ATTR_KEYS=(); ATTR_VALS=(); ATTR_KINDS=(); ATTR_COUNT=0
    inner="${inner:1:${#inner}-2}"; inner="${inner## }"; inner="${inner%% }"
    [ -z "$inner" ] && return
    local i c cur="" q=0 d=0 n=0; local -a pairs=()
    for ((i=0; i<${#inner}; i++)); do
        c="${inner:$i:1}"
        [ "$q" -eq 1 ] && { [ "$c" = '\' ] && i=$((i+1)); [ "$c" = '"' ] && q=0; cur+="$c"; continue; }
        [ "$c" = '"' ] && q=1; [ "$c" = "[" ] && d=$((d+1)); [ "$c" = "]" ] && d=$((d-1))
        if [ "$c" = "," ] && [ $d -eq 0 ]; then
            cur="${cur## }"; cur="${cur%% }"; [ -n "$cur" ] && { pairs[$n]="$cur"; n=$((n+1)); }; cur=""
        else cur+="$c"; fi
    done
    cur="${cur## }"; cur="${cur%% }"; [ -n "$cur" ] && { pairs[$n]="$cur"; n=$((n+1)); }
    local idx; for ((idx=0; idx<n; idx++)); do
        local pair="${pairs[$idx]}" cp; cp=$(colpos "$pair"); [ "$cp" -le 0 ] && continue
        local k="${pair:0:$cp}"; k="${k## }"; k="${k%% }"
        local v="${pair:$((cp+1))}"; v="${v## }"; v="${v%% }"
        local kind="atom"
        [ "$v" = "null" ] && kind="null"
        [ "$v" = "true" -o "$v" = "false" ] && kind="bool"
        [ "${v:0:1}" = '"' ] && kind="string" && v=$(decode_string "${v:1:${#v}-2}")
        [ "${v:0:1}" = "[" ] && kind="list"
        if [ "$kind" = "atom" ]; then
            [[ "$v" =~ ^-?(0|[1-9][0-9]*)$ ]] && kind="int"
            [[ "$v" =~ ^-?(0|[1-9][0-9]*)\.[0-9]+$ ]] && kind="dec"
        fi
        ATTR_KEYS[$idx]="$k"; ATTR_VALS[$idx]="$v"; ATTR_KINDS[$idx]="$kind"
    done; ATTR_COUNT=$n
}

emit_attrs_ordered() {
    local ctx="$1"; shift; local -a keys=("$@")
    local out="{"; local sep=""; local i_sym=""
    [[ "$ctx" == idea:* ]] && i_sym="${ctx#idea:}"
    local i; for ((i=0; i<${#keys[@]}; i++)); do
        local k="${keys[$i]}"; local j
        for ((j=0; j<ATTR_COUNT; j++)); do
            [ "${ATTR_KEYS[$j]}" != "$k" ] && continue
            local v="${ATTR_VALS[$j]}" kind="${ATTR_KINDS[$j]}"
            if [ -n "$i_sym" ]; then
                local contract="${SYM_CONTRACT[$i_sym]:-}" focus="${SYM_FOCUS[$i_sym]:-}"
                local field_type="any"
                if [ -n "$contract" ]; then
                    local cfi; IFS='|' read -ra cf <<< "$contract"
                    for cfi in "${cf[@]}"; do
                        local cfname="${cfi%%:*}" cfrest="${cfi#*:}"
                        [ "$cfname" = "$k" ] && { field_type="${cfrest%\?}"; break; }
                    done
                fi
                if [ "$field_type" = "text" ]; then
                    if [ "$k" = "$focus" ]; then out+="${sep}${k}:$(emit_string_v2 "$v")"
                    elif atom_safe "$v" && [[ "$v" != *$'\n'* ]]; then out+="${sep}${k}:${v}"
                    else out+="${sep}${k}:$(emit_string_v2 "$v")"
                    fi; sep=","; break
                fi
                local expanded=""
                [ -n "${MICRO_EXPAND[$v]:-}" ] && expanded="${MICRO_EXPAND[$v]}" && kind="atom" && v="$expanded" && add_change "microtoken-expanded"
                out+="${sep}${k}:$(emit_scalar "$v" "$kind")"; sep=","; break
            else
                out+="${sep}${k}:$(emit_scalar "$v" "$kind")"; sep=","; break
            fi
        done
    done; out+="}"; echo "$out"
}

main() {
    local TEST_MODE=0 INPUT_FILE=""
    [ "$1" = "--test" ] && { TEST_MODE=1; INPUT_FILE="$2"; } || INPUT_FILE="${1:-}"

    local RAW=""
    if [ -n "$INPUT_FILE" ] && [ "$INPUT_FILE" != "-" ]; then RAW=$(cat "$INPUT_FILE" 2>/dev/null || true)
    else RAW=$(cat /dev/stdin 2>/dev/null || true); fi
    [ -z "$RAW" ] && { echo "Error: empty input" >&2; exit 1; }

    local RAW_BYTES="$RAW"
    local HAS_CRLF=0; [[ "$RAW" == *$'\r'* ]] && HAS_CRLF=1
    [ $HAS_CRLF -eq 1 ] && add_change "newline-normalized"
    local TEXT="${RAW//$'\r\n'/$'\n'}"; TEXT="${TEXT//$'\r'/$'\n'}"

    # ============================================================
    # Phase 1: Parse — two-pass: first collect all lines
    # ============================================================
    local -a ALL_LINES=()
    local HAS_COMMENTS=0 HAS_BLANKS=0
    while IFS= read -r line || [ -n "$line" ]; do ALL_LINES+=("$line"); done <<< "$TEXT"
    local TL=${#ALL_LINES[@]}

    local -a META_NAMES=() META_RAW=() META_CATKEY=()
    local -a SYM_QUAL=() SYM_RAW_SYM=()
    # Sections: parallel arrays
    local -a SEC_IDS=() SEC_TITLES=()
    # Ideas per section: store processed lines in a flat array with section counts
    local -a ALL_IDEAS=()       # All processed idea lines (flat)
    local -a SEC_IDEA_COUNTS=() # How many ideas per section
    local CURRENT_SEC_IDEA_COUNT=0

    local li=0
    while [ $li -lt $TL ]; do
        local line="${ALL_LINES[$li]}"
        local trimmed="${line## }"; trimmed="${trimmed##$'\t'}"

        # Skip blank/comments ONLY in glossary area
        if [ $IN_GLOSSARY -eq 1 ]; then
            if [ -z "$line" ]; then HAS_BLANKS=1; li=$((li+1)); continue; fi
            if [ -n "$trimmed" ] && [ "${trimmed:0:1}" = "#" ]; then HAS_COMMENTS=1; li=$((li+1)); continue; fi
        fi

        # $0 header
        if [[ "$line" =~ ^\$0[[:space:]]*$ ]]; then IN_GLOSSARY=1; li=$((li+1)); continue; fi

        # Glossary
        if [ $IN_GLOSSARY -eq 1 ]; then
            # Meta
            if [[ "$line" =~ ^\$0:([A-Za-z_][A-Za-z0-9_.-]*)\{(.*)\}$ ]]; then
                local mn="${BASH_REMATCH[1]}" ma="${BASH_REMATCH[2]}"
                local cat=5 sub="$mn"
                [ "$mn" = "format" ] && cat=0 && sub=""
                [[ "$mn" == enum_* ]] && cat=1 && sub="${mn#enum_}"
                [[ "$mn" == micro_* ]] && cat=2 && sub="${mn#micro_}"
                [[ "$mn" == namespace_* ]] && cat=3 && sub="${mn#namespace_}"
                [[ "$mn" == extension_* ]] && cat=4 && sub="${mn#extension_}"
                META_NAMES+=("$mn"); META_RAW+=("$line"); META_CATKEY+=("$cat:$sub")
                if [[ "$mn" == micro_* ]] && [ -n "$ma" ] && [[ "$ma" =~ expand:([^,}]*) ]]; then
                    local mexpand="${BASH_REMATCH[1]}"; mexpand="${mexpand## }"; mexpand="${mexpand%% }"; mexpand="${mexpand#\"}"; mexpand="${mexpand%\"}"
                    MICRO_EXPAND["${mn#micro_}"]="$mexpand"
                fi
                li=$((li+1)); continue
            fi
            # Symbol
            local smatch=0 sym="" ns="" label="" attrs="" q=""
            if [[ "$line" =~ ^([a-z][a-z0-9_.-]*)::(!|[A-Z][A-Z0-9_]{0,15}):([a-zA-Z_][a-zA-Z0-9_.-]*)\{(.*)\}$ ]]; then
                sym="${BASH_REMATCH[2]}"; ns="${BASH_REMATCH[1]}"; label="${BASH_REMATCH[3]}"; attrs="${BASH_REMATCH[4]}"; q="${ns}::${sym}"; smatch=1
            elif [[ "$line" =~ ^(!|[A-Z][A-Z0-9_]{0,15}):([a-zA-Z_][a-zA-Z0-9_.-]*)\{(.*)\}$ ]]; then
                sym="${BASH_REMATCH[1]}"; label="${BASH_REMATCH[2]}"; attrs="${BASH_REMATCH[3]}"; q="$sym"; smatch=1
            fi
            if [ $smatch -eq 1 ]; then
                SYM_QUAL+=("$q"); SYM_RAW_SYM+=("$line")
                parse_attrs "{$attrs}"
                local contract="" focus="" shape="cuerpo"
                local j; for ((j=0; j<ATTR_COUNT; j++)); do
                    case "${ATTR_KEYS[$j]}" in fields|pos) contract="${ATTR_VALS[$j]}" ;; focus) focus="${ATTR_VALS[$j]}" ;; type) shape="${ATTR_VALS[$j]}" ;; esac
                done
                init_sym_info "$q" "$contract" "$focus" "$shape"
                li=$((li+1)); continue
            fi
            # Section transition
            [[ "$line" =~ ^\$[1-9] ]] && { IN_GLOSSARY=0; }
        fi

        # Section header
        if [[ "$line" =~ ^\$([1-9][0-9]*)(:[[:space:]]*)?(.*)?$ ]]; then
            # If we already have sections, save current section's count
            if [ ${#SEC_IDS[@]} -gt 0 ]; then
                SEC_IDEA_COUNTS+=("$CURRENT_SEC_IDEA_COUNT")
            fi
            CURRENT_SEC_IDEA_COUNT=0
            SEC_IDS+=("${BASH_REMATCH[1]}")
            local stitle="${BASH_REMATCH[3]:-}"
            stitle=$(echo -n "$stitle" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            SEC_TITLES+=("$stitle")
            li=$((li+1)); continue
        fi

        # Idea line — check for multiline body
        local head_re='^(([a-z][a-z0-9_.-]*::)?(!|[A-Z][A-Z0-9_]{0,15})):([a-zA-Z_][a-zA-Z0-9_.-]*)(.*)$'
        if [[ "$line" =~ $head_re ]]; then
            local i_tail="${BASH_REMATCH[5]}"; i_tail="${i_tail## }"
            if [ "$i_tail" = "{" ]; then
                # Multiline body
                local i_sym="${BASH_REMATCH[1]}" i_name="${BASH_REMATCH[4]}"
                local -a body_lines=()
                li=$((li+1))
                while [ $li -lt $TL ]; do
                    local bline="${ALL_LINES[$li]}"
                    local btrim="${bline## }"; btrim="${btrim##$'\t'}"
                    if [ "$btrim" = "}" ]; then li=$((li+1)); break; fi
                    body_lines+=("$bline")
                    li=$((li+1))
                done
                local shape="${SYM_SHAPE[$i_sym]:-cuerpo}"
                local body_text=""; local OIFS="$IFS"; IFS=$'\n'; body_text="${body_lines[*]}"; IFS="$OIFS"
                if [ "$shape" = "cuerpo" ]; then
                    body_text="${body_text//$'\r\n'/$'\n'}"; body_text="${body_text//$'\r'/$'\n'}"
                    local body_trimmed="$body_text"
                    while [[ "$body_trimmed" == *$'\n' ]]; do body_trimmed="${body_trimmed%$'\n'}"; done
                    if [[ "$body_trimmed" != *$'\n'* ]]; then
                        ALL_IDEAS+=("${i_sym}:${i_name}{${body_trimmed}}"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1))
                    else
                        ALL_IDEAS+=("${i_sym}:${i_name}{"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1))
                        local bl; IFS=$'\n' read -ra blines <<< "$body_text"
                        for bl in "${blines[@]}"; do ALL_IDEAS+=("$bl"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1)); done
                        ALL_IDEAS+=("}"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1))
                    fi
                else
                    ALL_IDEAS+=("${i_sym}:${i_name}{"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1))
                    local bl; IFS=$'\n' read -ra blines <<< "$body_text"
                    for bl in "${blines[@]}"; do ALL_IDEAS+=("$bl"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1)); done
                    ALL_IDEAS+=("}"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1))
                fi
                continue
            fi
        fi

        # Regular idea line
        local head_re2='^(([a-z][a-z0-9_.-]*::)?(!|[A-Z][A-Z0-9_]{0,15})):([a-zA-Z_][a-zA-Z0-9_.-]*)(.*)$'
        if [[ "$line" =~ $head_re2 ]]; then
            local i_sym2="${BASH_REMATCH[1]}" i_name2="${BASH_REMATCH[4]}" i_tail2="${BASH_REMATCH[5]}"; i_tail2="${i_tail2## }"
            local shape2="${SYM_SHAPE[$i_sym2]:-cuerpo}"

            if [ "$shape2" = "attrs" ] && [[ "$i_tail2" =~ ^\{([^}]*)\}$ ]]; then
                # Attrs idea — reorder keys, apply quoting
                local inner="${BASH_REMATCH[1]}"
                parse_attrs "{$inner}"
                local contract="${SYM_CONTRACT[$i_sym2]:-}"
                local -a okeys=()
                if [ -n "$contract" ]; then
                    IFS='|' read -ra cfields <<< "$contract"
                    local cf; for cf in "${cfields[@]}"; do
                        local cfname="${cf%%:*}"
                        local j; for ((j=0; j<ATTR_COUNT; j++)); do [ "${ATTR_KEYS[$j]}" = "$cfname" ] && okeys+=("$cfname") && break; done
                    done
                fi
                local -a extras=()
                for ((j=0; j<ATTR_COUNT; j++)); do
                    local found=0; local k="${ATTR_KEYS[$j]}"
                    local ck; for ck in "${okeys[@]}"; do [ "$ck" = "$k" ] && found=1 && break; done
                    [ $found -eq 0 ] && extras+=("$k")
                done
                # Sort extras
                for ((ei=0; ei<${#extras[@]}; ei++)); do
                    for ((ej=ei+1; ej<${#extras[@]}; ej++)); do [[ "${extras[$ei]}" > "${extras[$ej]}" ]] && { local et="${extras[$ei]}"; extras[$ei]="${extras[$ej]}"; extras[$ej]="$et"; }; done
                done
                okeys+=("${extras[@]}")
                ALL_IDEAS+=("${i_sym2}:${i_name2}$(emit_attrs_ordered "idea:${i_sym2}" "${okeys[@]}")"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1))
            elif [ "$shape2" = "attrs-pos" ] || [ "$shape2" = "relacion" ]; then
                # Positional — check for micro expansion
                if [[ "$i_tail2" == \|* ]]; then
                    local raw_cells="${i_tail2:1}"
                    local -a cells=() cell=""
                    local ci; for ((ci=0; ci<${#raw_cells}; ci++)); do
                        local cc="${raw_cells:$ci:1}"
                        [ "$cc" = "|" ] && { cells+=("$cell"); cell=""; } || cell+="$cc"
                    done
                    cells+=("$cell")
                    local has_micro=0
                    for cell in "${cells[@]}"; do
                        local ctrim="${cell## }"; ctrim="${ctrim%% }"
                        [ -n "${MICRO_EXPAND[$ctrim]:-}" ] && has_micro=1
                    done
                    if [ $has_micro -eq 1 ]; then
                        add_change "microtoken-expanded"
                        local rebuilt="" sep=""
                        for cell in "${cells[@]}"; do
                            ctrim="${cell## }"; ctrim="${ctrim%% }"
                            local expanded="${MICRO_EXPAND[$ctrim]:-$ctrim}"
                            rebuilt+="${sep}${expanded}"; sep="|"
                        done
                        ALL_IDEAS+=("${i_sym2}:${i_name2}|${rebuilt}"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1))
                    else
                        ALL_IDEAS+=("$line"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1))
                    fi
                else
                    ALL_IDEAS+=("$line"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1))
                fi
            else
                # cuerpo/bloque inline
                ALL_IDEAS+=("$line"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1))
            fi
        else
            ALL_IDEAS+=("$line"); CURRENT_SEC_IDEA_COUNT=$((CURRENT_SEC_IDEA_COUNT+1))
        fi
        li=$((li+1))
    done

    # Save last section's idea count
    SEC_IDEA_COUNTS+=("$CURRENT_SEC_IDEA_COUNT")

    # ============================================================
    # Phase 2: Sort metas
    # ============================================================
    local MC=${#META_NAMES[@]}
    for ((i=0; i<MC; i++)); do
        for ((j=i+1; j<MC; j++)); do
            if [[ "${META_CATKEY[$i]}" > "${META_CATKEY[$j]}" ]]; then
                local tmp="${META_NAMES[$i]}"; META_NAMES[$i]="${META_NAMES[$j]}"; META_NAMES[$j]="$tmp"
                tmp="${META_RAW[$i]}"; META_RAW[$i]="${META_RAW[$j]}"; META_RAW[$j]="$tmp"
                tmp="${META_CATKEY[$i]}"; META_CATKEY[$i]="${META_CATKEY[$j]}"; META_CATKEY[$j]="$tmp"
            fi
        done
    done

    # ============================================================
    # Phase 3: Sort symbols
    # ============================================================
    local SC=${#SYM_QUAL[@]}
    for ((i=0; i<SC; i++)); do
        for ((j=i+1; j<SC; j++)); do
            if [[ "${SYM_QUAL[$i]}" > "${SYM_QUAL[$j]}" ]]; then
                tmp="${SYM_QUAL[$i]}"; SYM_QUAL[$i]="${SYM_QUAL[$j]}"; SYM_QUAL[$j]="$tmp"
                tmp="${SYM_RAW_SYM[$i]}"; SYM_RAW_SYM[$i]="${SYM_RAW_SYM[$j]}"; SYM_RAW_SYM[$j]="$tmp"
            fi
        done
    done

    # ============================================================
    # Phase 4: Build canonical output
    # ============================================================
    local -a FINAL=()
    FINAL+=("\$0")
    local sym_base=("type" "weight" "fields" "pos" "focus" "desc" "open" "namespace" "version")

    for ((i=0; i<MC; i++)); do
        local mline="${META_RAW[$i]}" mname="${META_NAMES[$i]}"
        if [[ "$mline" =~ ^\$0:([A-Za-z_][A-Za-z0-9_.-]*)\{(.*)\}$ ]]; then
            local mattrs="${BASH_REMATCH[2]}"
            if [ -z "$mattrs" ]; then FINAL+=("\$0:${mname}{}"); continue; fi
            parse_attrs "{$mattrs}"
            local -a base=()
            case "$mname" in
                format) base=("cortex" "encoding" "language") ;;
                enum_*) base=("values") ;;
                micro_*) base=("expand") ;;
                namespace_*) base=("id" "version" "required" "desc") ;;
                extension_*) base=("namespace" "id" "version" "required" "desc") ;;
            esac
            local -a okeys=(); local bk; for bk in "${base[@]}"; do
                local j; for ((j=0; j<ATTR_COUNT; j++)); do [ "${ATTR_KEYS[$j]}" = "$bk" ] && okeys+=("$bk") && break; done
            done
            local -a extras=()
            for ((j=0; j<ATTR_COUNT; j++)); do
                local found=0; for bk in "${base[@]}"; do [ "${ATTR_KEYS[$j]}" = "$bk" ] && found=1 && break; done
                [ $found -eq 0 ] && extras+=("${ATTR_KEYS[$j]}")
            done
            for ((ei=0; ei<${#extras[@]}; ei++)); do
                for ((ej=ei+1; ej<${#extras[@]}; ej++)); do [[ "${extras[$ei]}" > "${extras[$ej]}" ]] && { local et="${extras[$ei]}"; extras[$ei]="${extras[$ej]}"; extras[$ej]="$et"; }; done
            done
            okeys+=("${extras[@]}")
            FINAL+=("\$0:${mname}$(emit_attrs_ordered "" "${okeys[@]}")")
        fi
    done

    for ((i=0; i<SC; i++)); do
        local sline="${SYM_RAW_SYM[$i]}" q="${SYM_QUAL[$i]}"
        if [[ "$sline" =~ ^(([a-z][a-z0-9_.-]*::)?(!|[A-Z][A-Z0-9_]{0,15})):([a-zA-Z_][a-zA-Z0-9_.-]*)\{(.*)\}$ ]]; then
            label="${BASH_REMATCH[4]}"; local sattrs="${BASH_REMATCH[5]}"
            if [ -z "$sattrs" ]; then FINAL+=("$sline"); continue; fi
            parse_attrs "{$sattrs}"
            local -a okeys=(); local bk; for bk in "${sym_base[@]}"; do
                local j; for ((j=0; j<ATTR_COUNT; j++)); do [ "${ATTR_KEYS[$j]}" = "$bk" ] && okeys+=("$bk") && break; done
            done
            local -a extras=()
            for ((j=0; j<ATTR_COUNT; j++)); do
                local found=0; for bk in "${sym_base[@]}"; do [ "${ATTR_KEYS[$j]}" = "$bk" ] && found=1 && break; done
                [ $found -eq 0 ] && extras+=("${ATTR_KEYS[$j]}")
            done
            for ((ei=0; ei<${#extras[@]}; ei++)); do
                for ((ej=ei+1; ej<${#extras[@]}; ej++)); do [[ "${extras[$ei]}" > "${extras[$ej]}" ]] && { local et="${extras[$ei]}"; extras[$ei]="${extras[$ej]}"; extras[$ej]="$et"; }; done
            done
            okeys+=("${extras[@]}")
            FINAL+=("${q}:${label}$(emit_attrs_ordered "" "${okeys[@]}")")
        fi
    done

    # Sections — use ALL_IDEAS with SEC_IDEA_COUNTS
    local idea_ptr=0
    for ((si=0; si<${#SEC_IDS[@]}; si++)); do
        local sec_id="${SEC_IDS[$si]}"
        local sec_title="${SEC_TITLES[$si]}"
        if [ -n "$sec_title" ]; then FINAL+=("\$${sec_id}: ${sec_title}")
        else FINAL+=("\$${sec_id}"); fi
        local count="${SEC_IDEA_COUNTS[$si]:-0}"
        local end_ptr=$((idea_ptr + count))
        while [ $idea_ptr -lt $end_ptr ]; do
            FINAL+=("${ALL_IDEAS[$idea_ptr]}")
            idea_ptr=$((idea_ptr+1))
        done
    done

    local OUT_TEXT=""; local OIFS="$IFS"; IFS=$'\n'; OUT_TEXT="${FINAL[*]}"; IFS="$OIFS"
    OUT_TEXT+=$'\n'

    # Detect changes
    if [ "$OUT_TEXT" != "$RAW_BYTES" ]; then
        local has_form=0; local cc; for cc in "${CHANGES_ORDERED[@]}"; do [ "$cc" = "source-form-normalized" ] && has_form=1; done
        [ $has_form -eq 0 ] && add_change "source-form-normalized"
    fi

    local RAW_SHA; RAW_SHA=$(echo -n "$RAW_BYTES" | sha256sum | cut -d' ' -f1)
    local CAN_SHA; CAN_SHA=$(echo -n "$OUT_TEXT" | sha256sum | cut -d' ' -f1)
    local CHASH; CHASH=$(printf 'CORTEX-C14N-0.1\x00%s' "$OUT_TEXT" | sha256sum | cut -d' ' -f1)

    local CJ=""; local sep_ch=""
    for c in "${CHANGES_ORDERED[@]}"; do CJ+="${sep_ch}\"$c\""; sep_ch=","; done
    [ -z "$CJ" ] && CJ="[]" || CJ="[$CJ]"
    local CHANGED="false"; [ "$RAW_SHA" != "$CAN_SHA" ] && CHANGED="true"

    local REPORT="{\"canonicalization\":\"C14N-0.1\",\"inputSha256\":\"$RAW_SHA\",\"canonicalSha256\":\"$CAN_SHA\",\"canonicalHash\":\"sha256:$CHASH\",\"changed\":$CHANGED,\"structuralLoss\":false,\"losses\":[],\"sourceFidelityChanges\":$CJ,\"diagnostics\":[]}"

    if [ $TEST_MODE -eq 1 ]; then echo "$REPORT"
    else echo -n "$OUT_TEXT"; echo "$REPORT" >&2; fi
}

main "$@"
