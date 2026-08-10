#!/usr/bin/env bash
# PreToolUse(Bash) 훅: 워킹트리의 미커밋 변경을 되돌릴 수 없게 지우는 git 명령을
# 미커밋 변경이 있을 때만 거부한다.
#
# 막는 것 -- 대상을 지정하지 않고 워킹트리를 통째로 덮어쓰는 명령
#   git checkout -f / --force,  git switch -f / --force / --discard-changes
#   git reset --hard
#   git clean -f 계열
#   git checkout . / git checkout -- . / git restore . 처럼 전체를 되돌리는 형태
#   git stash drop / clear (대피시켜 둔 것을 버림)
#
# 워킹트리가 깨끗하면 파괴할 것이 없으므로 통과시킨다. 파일을 지정한 형태
# (`git checkout -- path/to/file`)도 범위가 한정되므로 통과시킨다.
#
# 왜 있나 (2026-08-10 사고)
#   훅 로직을 검증하려고 임시 브랜치를 오가다 원복에 `git checkout -f` 를 썼다.
#   그 -f 는 검증용 파일 하나가 아니라 워킹트리 전체를 덮어썼고, 커밋도 add 도
#   안 된 다른 작업분이 통째로 사라졌다. git 으로 복구할 수 없었다.
#   당시 상황에서 옳은 방법은 임시 클론(별도 디렉토리)에서 검증하는 것이었다.
set -uo pipefail

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""')

repo="${CLAUDE_PROJECT_DIR:-$PWD}"
git -C "$repo" rev-parse --git-dir >/dev/null 2>&1 || exit 0

# 명령 위치(줄 시작 또는 셸 구분자 뒤)의 git 만 본다. 환경변수 프리픽스도 포함해
# `FOO=1 git reset --hard` 가 빠져나가지 않게 한다.
lead='(^|[;&|(]|&&|\|\|)[[:space:]]*([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*[[:space:]]+)*git([[:space:]]+(-C[[:space:]]+[^[:space:]]+|-c[[:space:]]+[^[:space:]]+))*[[:space:]]+'

hit=""
printf '%s' "$cmd" | grep -qE "${lead}(checkout|switch)([[:space:]]+[^;&|]*)?[[:space:]]+(-f|--force|--discard-changes)([[:space:]]|$|;|&|\|)" && hit="checkout/switch 강제 전환"
printf '%s' "$cmd" | grep -qE "${lead}(checkout|switch)[[:space:]]+(-f|--force|--discard-changes)" && hit="checkout/switch 강제 전환"
printf '%s' "$cmd" | grep -qE "${lead}reset([[:space:]]+[^;&|]*)?[[:space:]]+--hard" && hit="reset --hard"
printf '%s' "$cmd" | grep -qE "${lead}clean([[:space:]]+[^;&|]*)?[[:space:]]+-[a-zA-Z]*f" && hit="clean -f"
printf '%s' "$cmd" | grep -qE "${lead}(checkout|restore)([[:space:]]+--)?[[:space:]]+\.([[:space:]]|$|;|&|\|)" && hit="워킹트리 전체 되돌리기"
printf '%s' "$cmd" | grep -qE "${lead}stash[[:space:]]+(drop|clear)" && hit="stash 폐기"

[ -n "$hit" ] || exit 0

# 미커밋 변경이 없으면 파괴할 것이 없다 → 통과
dirty=$(git -C "$repo" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
[ "${dirty:-0}" -gt 0 ] || exit 0

# stash 폐기는 워킹트리 상태와 무관하게 stash 목록이 있을 때만 의미가 있다
if [ "$hit" = "stash 폐기" ]; then
  n=$(git -C "$repo" stash list 2>/dev/null | wc -l | tr -d ' ')
  [ "${n:-0}" -gt 0 ] || exit 0
fi

sample=$(git -C "$repo" status --porcelain 2>/dev/null | head -5 | sed 's/^/    /')
reason="'${hit}' 은 미커밋 변경을 되돌릴 수 없게 지웁니다. 지금 워킹트리에 미커밋 변경이 ${dirty}건 있습니다.

${sample}

git add 하지 않은 변경은 stash 도 reflog 도 남기지 않아 복구가 불가능합니다. 먼저 아래 중 하나를 하세요.
  - 대피: git stash -u  (되돌린 뒤 git stash pop)
  - 범위 한정: 파일을 직접 지정  (git checkout -- <파일>)
  - 격리 검증: 별도 디렉토리에 임시 클론을 만들어 거기서 실험

정말 이 변경을 버려야 한다면 사용자에게 무엇이 사라지는지 알리고 확인을 받으세요."

jq -nc --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
exit 0
