#!/usr/bin/env bash
# SessionStart 훅: armarium 가 제공하는 스킬 목록을 세션 시작 안내로 출력한다.
# SessionStart 의 stdout 은 Claude 컨텍스트로 들어가므로, 목록과 함께
# "사용자에게 한 번 보여달라"는 지시를 붙여 첫 응답에서 렌더되게 한다.
set -euo pipefail

# 표준입력으로 들어오는 훅 JSON 에서 source 를 추출 (jq 의존 없이).
payload="$(cat 2>/dev/null || true)"
source="$(printf '%s' "$payload" \
  | grep -o '"source"[[:space:]]*:[[:space:]]*"[^"]*"' \
  | head -1 \
  | sed 's/.*"\([^"]*\)"$/\1/' || true)"

# compact(자동 압축) 으로 인한 재시작에는 목록을 반복하지 않는다.
# startup·resume·clear 및 source 미상일 때만 출력한다.
case "$source" in
  compact) exit 0 ;;
esac

# 스크립트 위치에서 플러그인 루트를 유도 (CLAUDE_PLUGIN_ROOT 의존 없이 동작).
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plugin_root="$(dirname "$script_dir")"
skills_dir="$plugin_root/skills"

[ -d "$skills_dir" ] || exit 0

# 각 SKILL.md 에서 name 과 description 첫 줄을 뽑는다.
rows=""
for skill_file in "$skills_dir"/*/SKILL.md; do
  [ -f "$skill_file" ] || continue
  line="$(awk '
    /^name:/ { name=$0; sub(/^name:[[:space:]]*/, "", name) }
    /^description:/ { indesc=1; next }
    indesc {
      l=$0
      if (l ~ /^[A-Za-z_-]+:/ || l ~ /^---/) { indesc=0; next }
      gsub(/^[[:space:]]+/, "", l)
      if (l != "" && desc == "") desc=l
    }
    END { if (name != "") printf "%-18s %s", name, desc }
  ' "$skill_file")"
  [ -n "$line" ] && rows="${rows}  ${line}"$'\n'
done

[ -n "$rows" ] || exit 0

count="$(printf '%s' "$rows" | grep -c '.')"

cat <<EOF
<armarium-skills note="세션 시작 안내">
이번 세션 첫 응답 맨 앞에서, 아래 armarium 스킬 목록을 코드블록 그대로 사용자에게 한 번만 보여줘라. 이후 응답에서는 반복하지 마라.

armarium 스킬 ${count}개
${rows}</armarium-skills>
EOF
