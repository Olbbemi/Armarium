#!/usr/bin/env bash
# SessionStart 훅: armarium 가 제공하는 스킬 목록을 세션 시작 시 화면에 보여준다.
#
# SessionStart 의 stdout/additionalContext 는 "컨텍스트로만" 들어가 화면에 안 뜬다.
# initialUserMessage 는 비대화형(-p) 모드 전용이라 인터랙티브 세션에선 무시된다.
# 따라서 화면 표시는 범용 출력 필드 systemMessage 로 한다 (모든 훅 이벤트 지원,
# 사용자 화면에 표시되나 모델 컨텍스트엔 안 들어감).
# 모델도 목록을 알게 하려면 additionalContext 를 함께 내보낸다.
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

# 화면에 띄울 배너(systemMessage)와, 모델이 인지할 컨텍스트(additionalContext).
system_message="$list_text"
additional_context="아래는 이 세션에서 쓸 수 있는 armarium 플러그인 스킬 목록(이름 + 설명 첫 줄)이다.
사용자가 목록을 요청하면, 아래 내용을 그대로 코드블록 하나에 담아 보여줘라. 군더더기 설명은 붙이지 마라.

${list_text}"

# JSON 출력으로 systemMessage(화면) + additionalContext(컨텍스트) 전달.
# python3 우선, 없으면 plain stdout 폴백(배너는 안 뜨지만 컨텍스트로는 주입됨).
if command -v python3 >/dev/null 2>&1; then
  SM="$system_message" AC="$additional_context" python3 -c '
import json, os
print(json.dumps({
  "systemMessage": os.environ["SM"],
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": os.environ["AC"],
  }
}, ensure_ascii=False))'
else
  # 폴백: 배너 표시는 안 되지만 컨텍스트로는 주입됨.
  printf '%s\n' "$additional_context"
fi
