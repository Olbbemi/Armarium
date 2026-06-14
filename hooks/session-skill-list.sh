#!/usr/bin/env bash
# SessionStart 훅: armarium 가 제공하는 스킬 목록을 세션 시작 시 화면에 보여준다.
#
# SessionStart 의 stdout/additionalContext 는 "컨텍스트로만" 들어가 화면에 안 뜬다.
# 그래서 hookSpecificOutput.initialUserMessage 로 첫 턴을 강제 생성하고
# (= 모델이 응답하게 만들고), additionalContext 에 실제 목록을 실어
# 모델이 그 첫 응답에서 목록을 출력하게 한다.
set -euo pipefail

# 표준입력 훅 JSON 에서 source 추출 (jq 의존 없이).
payload="$(cat 2>/dev/null || true)"
source="$(printf '%s' "$payload" \
  | grep -o '"source"[[:space:]]*:[[:space:]]*"[^"]*"' \
  | head -1 \
  | sed 's/.*"\([^"]*\)"$/\1/' || true)"

# 작업을 이어가는 맥락에서는 턴을 강제로 끼우지 않는다.
#   resume  : 기존 대화 재개 중
#   compact : 자동 압축 직후
case "$source" in
  resume|compact) exit 0 ;;
esac

# 스크립트 위치에서 플러그인 루트 유도 (CLAUDE_PLUGIN_ROOT 의존 없이).
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
plugin_root="$(dirname "$script_dir")"
skills_dir="$plugin_root/skills"

[ -d "$skills_dir" ] || exit 0

# 각 SKILL.md 에서 name 과 description 첫 줄을 뽑아 목록 구성.
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
list_text="armarium 스킬 ${count}개
${rows}"

# 모델에게 줄 데이터(컨텍스트)와, 첫 턴을 만들 사용자 메시지.
additional_context="아래는 이 세션에서 쓸 수 있는 armarium 플러그인 스킬 목록(이름 + 설명 첫 줄)이다.
사용자가 목록을 요청하면, 아래 내용을 그대로 코드블록 하나에 담아 보여줘라. 군더더기 설명은 붙이지 마라.

${list_text}"
initial_user_message="(세션 시작 자동 안내) 이 세션에서 쓸 수 있는 armarium 스킬 목록을 코드블록으로 보여줘."

# JSON 출력으로 initialUserMessage 를 전달 (python3 우선, 없으면 plain stdout 로 폴백).
if command -v python3 >/dev/null 2>&1; then
  AC="$additional_context" IUM="$initial_user_message" python3 -c '
import json, os
print(json.dumps({
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": os.environ["AC"],
    "initialUserMessage": os.environ["IUM"],
  }
}, ensure_ascii=False))'
else
  # 폴백: 자동 표시는 안 되지만 컨텍스트로는 주입됨.
  printf '%s\n' "$additional_context"
fi
