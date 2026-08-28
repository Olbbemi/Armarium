---
tool: claude-code
entry: SKILL.md
file_load: Read
delegate: Task/subagent_type
progress: TaskCreate
loop: ralph-loop
path_base: plugin_root
---

# Claude Code 어댑터

## 진입

`SKILL.md` 가 진입점이다. 프론트매터의 `name` 과 `description` 으로 발동 여부가 정해지고,
본문은 `core/core.md` 를 읽으라는 지시만 담는다.

`description` 은 이 스킬을 부를지 판단하는 기준이다. 무엇을 하는지의 요약이 아니라
필요한 상황과 사용자가 실제로 할 법한 말을 적는다.

## 파일 경로

경로는 플러그인 루트 기준으로 쓴다. `skills/<이름>/...` 형태이며 프로젝트 절대경로를 쓰지 않는다.
파일은 Read 툴로 읽는다.

셸 스크립트를 호출할 때는 `${CLAUDE_PLUGIN_ROOT}/skills/<이름>/<스크립트>` 를 쓴다.

## 위임

판정을 나눠 돌릴 때 Task 도구로 서브에이전트를 호출한다. 에이전트 정의 파일은
플러그인 루트 `agents/` 에 두어야 `subagent_type` 으로 디스패치된다.

서브에이전트는 결과 본문을 반환하고, 파일 저장은 메인이 맡는다.
백그라운드 서브에이전트는 권한 프롬프트를 띄울 수 없어 사전 허용되지 않은 쓰기가 거부되기 때문이다.

## 진행 표시

위임이나 사용자 확인이 있는 단계만 TaskCreate 로 표시한다.
백그라운드 호출은 호출 즉시 completed 로 닫는다.

## 루프

Stop 훅(`hooks/stop-verify-loop.py`)이 종료를 가로채 검증을 직접 돌린다.
통과하지 못하면 결함 목록과 함께 다시 작업하게 만든다.
완료 판정이 실행 모델을 거치지 않으므로 완료를 선언해서 빠져나갈 수 없다.

### 시작

```
python3 scripts/loop.py start \
  --report <산출물>/report.json --max 20 --label <이름> \
  --verify python3 engine/verify.py --out-dir <산출물>
```

`--verify` 뒤는 끝까지 검증 명령으로 읽는다. 그래서 마지막에 둔다.

### 도는 방식

| 검증 종료 코드 | 훅의 처리 |
|---|---|
| 0 | 상태를 지우고 종료를 허용한다 |
| 1 | 종료를 막고 결함 목록을 실어 다시 돌린다 |
| 2 | 상태를 지우고 멈춘다. 남은 결함은 사람이 본다 |
| 3 | 종료를 막고 확정할 후보를 실어 다시 돌린다 |

반복 상한에 도달해도 상태를 지우고 끝낸다. 상태 파일이 없으면 훅은 아무것도 하지 않는다.

### 중단

`python3 scripts/loop.py stop` 을 실행하거나 `.claude/skill-loop.local.json` 을 지운다.

### 세션 소유권

상태 파일은 프로젝트 범위이고 Stop 훅은 그 프로젝트의 모든 세션에서 걸린다.
`--session` 으로 세션을 적어 두거나, 적지 않으면 처음 걸린 세션이 소유권을 잡는다.
다른 세션은 그 루프를 가로채지 않는다.
