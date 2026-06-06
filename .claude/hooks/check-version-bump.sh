#!/usr/bin/env bash
# PreToolUse(Bash) 훅: armarium 저장소에서 git push 시 두 가지를 점검한다.
#  (1) .claude-plugin/plugin.json 의 version 이 직전 푸시(upstream)와 같으면
#      "버전을 올릴지 / 그대로 진행할지" 확인을 요청한다.
#  (2) .claude-plugin/marketplace.json 의 같은 플러그인 version 이 plugin.json
#      version 과 다르면(한쪽만 올린 경우) 확인을 요청한다.
#
# version 을 안 올리거나 두 파일이 어긋난 채 push 하면 /plugin marketplace
# update 시 변경이 반영되지 않으므로, 그 사고를 push 직전에 차단한다.
set -uo pipefail

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""')

# git push 가 아니면 통과 (settings.json 의 if 필터로도 거르지만 이중 안전장치)
case "$cmd" in
  *"git push"*) ;;
  *) exit 0 ;;
esac

repo="${CLAUDE_PROJECT_DIR:-$PWD}"

# armarium 플러그인 저장소가 아니면 통과
[ -f "$repo/.claude-plugin/plugin.json" ] || exit 0

# upstream 추적 브랜치가 없으면 비교 불가 → 통과 (예: 최초 push)
git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1 || exit 0

# 미푸시 커밋이 없으면 통과
ahead=$(git -C "$repo" rev-list --count '@{u}..HEAD' 2>/dev/null || echo 0)
[ "${ahead:-0}" -gt 0 ] || exit 0

cur=$(git -C "$repo" show HEAD:.claude-plugin/plugin.json 2>/dev/null | jq -r '.version // ""')
old=$(git -C "$repo" show '@{u}:.claude-plugin/plugin.json' 2>/dev/null | jq -r '.version // ""')

# version 필드가 없으면(commit SHA 전략) 강제하지 않음 → 통과
[ -n "$cur" ] || exit 0

# (2) marketplace.json 의 같은 플러그인 version 이 plugin.json 과 다르면 확인 요청
name=$(git -C "$repo" show HEAD:.claude-plugin/plugin.json 2>/dev/null | jq -r '.name // ""')
mkt=$(git -C "$repo" show HEAD:.claude-plugin/marketplace.json 2>/dev/null | jq -r --arg n "$name" '.plugins[]? | select(.name==$n) | .version // ""')
if [ -n "$mkt" ] && [ "$mkt" != "$cur" ]; then
  reason="plugin.json version('${cur}') 과 marketplace.json 의 '${name}' version('${mkt}') 이 다릅니다. 두 파일 version 을 같은 값으로 맞춘 뒤 push 하세요. 이대로 푸시하면 카탈로그 버전이 어긋나 update 가 제대로 반영되지 않습니다."
  jq -nc --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"ask",permissionDecisionReason:$r}}'
  exit 0
fi

if [ "$cur" = "$old" ]; then
  reason="plugin.json version 이 '${cur}' 그대로입니다(직전 푸시와 동일). version 을 올리지 않으면 /plugin marketplace update 시 변경이 반영되지 않습니다. 버전을 먼저 올릴까요, 아니면 이대로 푸시할까요?"
  jq -nc --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"ask",permissionDecisionReason:$r}}'
  exit 0
fi

# 버전이 바뀌었으면 정상 통과
exit 0
