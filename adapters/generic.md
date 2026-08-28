---
tool: generic
entry: core/core.md
file_load: none
delegate: none
progress: none
loop: manual
path_base: skill_dir
---

# generic 어댑터

툴 고유 기능을 하나도 쓰지 않고 스킬을 완주하는 최소 경로. 다른 어댑터가 없는 환경의 기본값이다.

이 어댑터로 완주하지 못하는 스킬은 중립이 아니다. 중립성은 선언이 아니라 이 경로의 완주로 판정된다.

툴 고유 기능이든 외부 플러그인이든 판정은 같다. 없을 때 멈추면 의존이라 쓸 수 없고,
느려질 뿐이면 가속이라 써도 된다. 쓰기로 한 능력은 아래 표에 행으로 더해 판정 대상에 올린다.

## 제공하지 않는 것

| 기능 | 대신 |
|---|---|
| 위임 | 순차로 처리한다 |
| 진행 표시 | 표시하지 않는다 |
| 자동 반복 | 사람이 다시 호출한다 |

## 파일 경로

경로는 스킬 디렉토리 기준 상대경로다. 파일을 읽는 방법은 이 어댑터가 규정하지 않는다.

## 실행

```
python3 engine/verify.py --out-dir <산출물 디렉토리>
```

종료 코드로 판정한다. 0 이면 통과, 1 이면 고친 뒤 다시 실행, 2 면 멈추고 사람에게 넘긴다.
3 이면 후보를 확정해 `--verdicts` 파일에 적고 다시 실행한다.

`--out-dir` 를 주면 회차가 `runs/` 에 쌓이고 직전 회차와의 비교가 화면 끝에 나온다.
이 어댑터는 반복을 자동으로 돌리지 않으므로 사람이 다시 호출한다.

## 루프

종료를 막을 수단이 없으므로 사람이 반복한다.

```
python3 scripts/loop.py start --report <산출물>/report.json --max 20 \
  --verify <검증 명령>
python3 scripts/loop.py tick
```

`tick` 을 직접 호출하면 `action` 이 `continue`, `verdict`, `done`, `stalled`, `exhausted` 중 하나로 나온다.
`continue` 면 `reason` 의 결함을 고치고 다시 `tick` 한다.
`verdict` 면 `reason` 의 후보를 판정해 적고 다시 `tick` 한다.
