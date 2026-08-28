---
tool: codex
entry: AGENTS.md
file_load: read
delegate: spawn_agent
progress: none
loop: followup_task
path_base: repo_root
---

# Codex 어댑터

## 진입

저장소 루트 `AGENTS.md` 가 이 스킬을 가리킨다. Codex 에는 스킬 발동 개념이 없으므로
`AGENTS.md` 에 어느 상황에서 `core/core.md` 를 읽을지 적는다. 나머지는 그 지도가 가리킨다.

## 파일 경로

경로는 저장소 루트 기준이다.

## 위임

`spawn_agent` 를 쓴다. 자식에게 깨끗한 컨텍스트를 주려면 `fork_turns` 를 `none` 으로 둔다.
`multi_agent` 기능이 꺼져 있으면 위임을 쓸 수 없으므로 generic 경로로 내려간다.

## 루프

Stop 훅에 해당하는 자리가 없으므로 종료를 기계가 막지 못한다.
`scripts/loop.py tick` 을 매 회차 직접 호출하고 `action` 으로 판정한다.

`followup_task` 로 같은 작업을 다시 시킬 때도 판정은 `tick` 의 결과로만 한다.
