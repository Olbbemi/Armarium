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

# 작업을 이어가는 맥락(resume: 기존 대화 재개 / compact: 자동 압축 직후)에서는
# 화면 배너를 띄우지 않는다. 사용자가 이미 보고 시작한 목록을 다시 들이밀 이유가 없다.
#
# 다만 컨텍스트 주입(additionalContext)은 그때도 한다. 배너와 주입은 별개 필드이고,
# 특히 compact 는 앞서 주입한 knowledge-capture overview 를 컨텍스트에서 날려버린다.
# 여기서 다시 넣지 않으면 압축 이후 감시가 조용히 멈춘다.
show_banner=1
case "$source" in
  resume|compact) show_banner=0 ;;
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

# knowledge-capture 자동 활성.
#
# 이 스킬만 예외로 매 세션 자동 활성한다. 논의 중 지식 부재는 사용자가 스킬을
# 부를 생각을 못 하는 순간에 드러나므로, 명시 호출에만 의존하면 잡을 시점을 놓친다.
# 나머지 스킬은 목록만 노출하고 발동은 description 판단에 맡긴다.
#
# overview 전문을 실어 보내 모델이 Read 없이 바로 따르게 한다. 파일을 런타임에
# 읽으므로 스킬을 고치면 다음 세션부터 자동 반영된다.
capture_overview="$skills_dir/knowledge-capture/overview.md"
if [ -f "$capture_overview" ]; then
  additional_context="${additional_context}

---

이 세션에서 \`knowledge-capture\` 는 자동 활성된 상태다. 사용자가 슬래시 명령으로 부르지
않았어도 아래 overview 를 이미 로드한 것으로 보고 그대로 따른다. 별도로 Read 하지 않아도 된다.

overview 가 Read 를 지시하는 파일 경로는 모두 아래 플러그인 루트 기준이다.
${plugin_root}

단 wip 저장 경로는 활성 시점에 묻지 않는다. 실제 캡처가 확정되는 순간에 처음 묻는다
(delegate.md 의 \`저장 경로 확보 시점\` 참조). 캡처가 일어나지 않는 세션은 경로를 묻지 않는다.

$(cat "$capture_overview")"
fi

# JSON 출력으로 systemMessage(화면) + additionalContext(컨텍스트) 전달.
# 배너를 안 띄우는 맥락(resume/compact)에서는 systemMessage 를 아예 빼고 주입만 한다.
# python3 우선, 없으면 plain stdout 폴백(배너는 안 뜨지만 컨텍스트로는 주입됨).
if command -v python3 >/dev/null 2>&1; then
  SM="$system_message" AC="$additional_context" BANNER="$show_banner" python3 -c '
import json, os
out = {
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": os.environ["AC"],
  }
}
if os.environ["BANNER"] == "1":
    out["systemMessage"] = os.environ["SM"]
print(json.dumps(out, ensure_ascii=False))'
else
  # 폴백: 배너 표시는 안 되지만 컨텍스트로는 주입됨.
  printf '%s\n' "$additional_context"
fi
