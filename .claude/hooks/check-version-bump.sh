#!/usr/bin/env bash
# PreToolUse(Bash) 훅: armarium 저장소에서 git push 시 세 가지를 점검한다.
#  (1) payload 가 origin/main 대비 바뀌었는데 .claude-plugin/plugin.json 의
#      version 이 그대로면 push 를 거부한다.
#  (2) .claude-plugin/marketplace.json 의 같은 플러그인 version 이 plugin.json
#      version 과 다르면(한쪽만 올린 경우) 거부한다.
#  (3) README.md 상단의 "현재 버전" 표기가 plugin.json version 과 다르면
#      (README 갱신 누락) 거부한다.
#
# version 을 안 올리거나 세 곳이 어긋난 채 push 하면 /plugin marketplace
# update 시 변경이 반영되지 않거나 README 표기가 실제와 달라지므로, 그 사고를
# push 직전에 차단한다.
#
# 설계 근거 두 가지 (2026-08-10, 버전 누락 사고 후 보강)
#  - 비교 기준은 origin/main 고정이다. upstream 을 우선하면 같은 PR 에 두 번째
#    push 부터 "이미 올린 버전" 과 비교해 매번 오탐이 났다. 경보가 반복되면
#    무시하게 되고, 실제로 그렇게 뚫렸다. PR 은 main 에 머지되므로 판정 기준도
#    main 이어야 맞다.
#  - 판정은 ask 가 아니라 deny 다. ask 는 결정권을 실행 모델에 넘기는데, 그
#    모델이 "절차에 없는 부수 경고" 로 보고 넘기면 아무것도 막지 못한다.
#    payload 판정으로 오탐을 없앴으므로 거부해도 정상 작업을 막지 않는다.
set -uo pipefail

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""')

# 이 훅은 모든 Bash 호출에서 실행된다(settings.json 에 if 게이트 없음). git push
# 판정은 여기 한 곳에서만 하며, 복합 명령(`git push && ...`, `cd x && git push`)과
# git 과 push 사이에 전역 옵션이 끼는 형태(`git -C <경로> push`, `git -c k=v push`)
# 까지 잡는다. 명령 위치(줄 시작 또는 셸 구분자 뒤)의 git 만 보므로 `echo "git push"`
# 같은 문자열 안의 가짜 매칭은 발동하지 않는다.
#
# 환경변수 프리픽스(`GIT_PAGER=cat git push`, `FOO=1 BAR=2 git push`)도 잡는다.
# 이 형태는 2026-08-10 우회 표면 점검에서 발견됐다 -- 의도적 우회는 아니어도
# 무심코 쓰면 검사를 통째로 빠져나가므로 명령 위치 판정에 포함한다.
env_pfx='([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*[[:space:]]+)*'
push_re='(^|[;&|(]|&&|\|\|)[[:space:]]*'"$env_pfx"'git([[:space:]]+(-C[[:space:]]+[^[:space:]]+|-c[[:space:]]+[^[:space:]]+|--[A-Za-z-]+(=[^[:space:]]+)?|-[A-Za-z]+))*[[:space:]]+push([[:space:]]|$|;|&|\|)'
printf '%s' "$cmd" | grep -qE "$push_re" || exit 0

repo="${CLAUDE_PROJECT_DIR:-$PWD}"

# armarium 플러그인 저장소가 아니면 통과
[ -f "$repo/.claude-plugin/plugin.json" ] || exit 0

# 비교 기준(base)은 origin/main 고정이다. upstream 을 쓰면 같은 PR 재push 때
# 이미 올린 버전과 비교해 오탐이 난다. origin/main 이 없으면 비교 불가 → 통과.
if git -C "$repo" rev-parse --verify -q origin/main >/dev/null 2>&1; then
  base="origin/main"
else
  exit 0
fi

# base 대비 새 커밋이 없으면 통과
ahead=$(git -C "$repo" rev-list --count "$base..HEAD" 2>/dev/null || echo 0)
[ "${ahead:-0}" -gt 0 ] || exit 0

cur=$(git -C "$repo" show HEAD:.claude-plugin/plugin.json 2>/dev/null | jq -r '.version // ""')
old=$(git -C "$repo" show "$base:.claude-plugin/plugin.json" 2>/dev/null | jq -r '.version // ""')

# version 필드가 없으면(commit SHA 전략) 강제하지 않음 → 통과
[ -n "$cur" ] || exit 0

# payload(배포물)가 바뀌었는지 판정한다. 비배포 파일(.claude/ 훅·설정,
# .planning/, docs/)만 고친 push 는 버전과 무관하므로 통과시킨다. 이 판정이
# 없으면 훅 스크립트 자체를 고칠 때도 경보가 떠서 오탐이 된다.
payload_re='^(skills/|agents/|references/|CLAUDE\.md$|\.claude-plugin/)'
changed=$(git -C "$repo" diff --name-only "$base..HEAD" 2>/dev/null | grep -cE "$payload_re" || true)
[ "${changed:-0}" -gt 0 ] || exit 0

# (2) marketplace.json 의 같은 플러그인 version 이 plugin.json 과 다르면 확인 요청
name=$(git -C "$repo" show HEAD:.claude-plugin/plugin.json 2>/dev/null | jq -r '.name // ""')
mkt=$(git -C "$repo" show HEAD:.claude-plugin/marketplace.json 2>/dev/null | jq -r --arg n "$name" '.plugins[]? | select(.name==$n) | .version // ""')
if [ -n "$mkt" ] && [ "$mkt" != "$cur" ]; then
  reason="plugin.json version('${cur}') 과 marketplace.json 의 '${name}' version('${mkt}') 이 다릅니다. 두 파일 version 을 같은 값으로 맞춘 뒤 다시 push 하세요. 이대로 푸시하면 카탈로그 버전이 어긋나 update 가 제대로 반영되지 않습니다."
  jq -nc --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  exit 0
fi

# (3) README.md 상단 "현재 버전" 표기가 plugin.json 과 다르면 확인 요청
#     README 는 사람용 문서라 훅 사각지대였음 → 여기서 parity 로 잡는다.
#     README 에 버전 표기가 없으면(구버전) 비강제 통과.
rdme=$(git -C "$repo" show HEAD:README.md 2>/dev/null | grep -m1 -oE '현재 버전: `[0-9]+\.[0-9]+\.[0-9]+`' | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
if [ -n "$rdme" ] && [ "$rdme" != "$cur" ]; then
  reason="plugin.json version('${cur}') 과 README.md 상단 표기('${rdme}') 가 다릅니다. README 상단 '현재 버전' 줄을 '${cur}' 로 맞춘 뒤 다시 push 하세요. README 갱신을 빠뜨리면 표기가 실제 배포 버전과 어긋납니다."
  jq -nc --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  exit 0
fi

if [ "$cur" = "$old" ]; then
  reason="payload 가 origin/main 대비 바뀌었는데 plugin.json version 이 '${cur}' 그대로입니다. 이대로 push 하면 머지해도 /plugin marketplace update 가 변경을 받아오지 않습니다. README.md 의 '## 버전 규칙' 질문 사다리로 등급을 정해 plugin.json · marketplace.json · README.md 상단 세 곳을 같은 값으로 올리고 커밋한 뒤 다시 push 하세요."
  jq -nc --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  exit 0
fi

# 버전이 바뀌었으면 정상 통과
exit 0
