# knowledge-scan

코드베이스를 훑어 쓰인 비자명 문법을 뽑아 wip 초안으로 누적하는 스킬.

## 무엇을 하나

사용자의 명시 명령으로 대상 코드베이스를 스캔해, 언어 카탈로그에 등재된 비자명 문법 중 실제로 쓰인 것을 후보로 뽑는다.<br>
사용자가 고른 topic 마다 `knowledge-writer` 에이전트에 wip 본문 작성을 위임한다.<br>
wip 누적까지만 담당하며, 확정지식 승급은 별도 스킬 [`knowledge-promote`](../knowledge-promote/README.md)가 맡는다.

## 형제 스킬

wip 를 만드는 스킬은 셋이고, 진입 경로가 서로 다르다. 저장 경로 검증 · writer 호출 · 저장 규칙은 [`references/knowledge-wip-protocol.md`](../../references/knowledge-wip-protocol.md) 를 셋이 공유한다.

| 스킬 | 진입 | 앵커 |
|------|------|------|
| [`knowledge-capture`](../knowledge-capture/README.md) | 대화 중 감지 또는 명시 요청 (상시) | 대화 발췌 |
| `knowledge-scan` | 코드베이스 스캔 명령 (단발) | 코드 발췌 |
| [`knowledge-study`](../knowledge-study/README.md) | CS 로드맵에서 주제 선택 (단발) | 카탈로그 항목 |

## 언제 쓰나

`/knowledge-scan` 슬래시 명령으로 **명시적으로 활성**했을 때만 동작한다.<br>
명령 한 번에 시작해 끝나는 단발 작업이다.

## 구조

- `overview.md` -- 진입점. 발동 규칙 · 대상 경로 · 언어 판정 · 스캐너 호출 · 후보 게이트 · writer 위임
- `languages/<lang>.md` -- 언어별 비자명 문법 카탈로그 (현재 `cpp.md`)
- `knowledge-code-scanner` 에이전트 (플러그인 루트 `agents/knowledge-code-scanner.md`) -- 코드베이스 순회 + 문법 탐지 + 후보 반환
- `knowledge-writer` 에이전트 (플러그인 루트 `agents/knowledge-writer.md`) -- 메인 입력을 받아 wip 본문 작성 후 반환 (저장은 안 함)

## 동작 흐름

1. 스캔 명시 명령 인식 (자연어, 오발동 방지 3단 규칙 -- 뚜렷하면 즉시 / 모호하면 한 줄 확인 / 의도 없으면 무시)
2. 스캔 대상 경로 확보(항상 명시) + 언어 판정 (확장자 감지 -> 카탈로그 교차 -> 사용자 확인)
3. `knowledge-code-scanner` 를 **포그라운드**로 호출 -> 후보 목록(`topic` / `usages` / `why`) 반환
4. 후보 게이트 -- 사용자가 캡처할 topic 을 고른다 (이 스킬의 유일한 질문)
5. 고른 topic 마다 writer 에 **백그라운드** 위임 -> 반환 본문을 메인이 저장

## 비자명 문법 카탈로그

스캔은 언어별 카탈로그 `languages/<lang>.md` 에 등재된 "정리할 만한 비자명 문법" 만 후보로 본다(언어 기본기는 제외). 각 항목의 신호는 그 토픽을 고유하게 대표하는 **강앵커**로 정의하며, `&&`·`|` 같이 흔하고 모호한 토큰은 오탐만 늘리므로 신호로 쓰지 않는다.<br>
스캐너는 강앵커를 Grep 으로 찾고 Read 로 확증하며, 기존 knowledge/wip 파일명과 겹치는 topic 은 걸러낸다(dedup). 새 언어는 `languages/` 에 `<lang>.md` 를 더하면 된다.

## 입력 / 출력

- **저장 위치** -- 활성 시 사용자에게 입력받는 디렉토리 하위 `<저장경로>/<topic>.md`. 입력 경로는 origin remote 가 `git@github.com:Olbbemi/Herbarium.git` 인 Herbarium 저장소 하위여야 한다
- **스캔 대상 경로** -- 저장 경로와 별개로, 스캔할 코드베이스 경로를 항상 명시적으로 확보한다 (명령에 있으면 그것, 없으면 물어 받음)
- **writer 입력 포맷** -- `triggered_by` 는 `code-scan`, `user_known` 은 "기초부터", `kind` 는 항상 `code`, `snippets` 은 스캐너가 준 코드 발췌

## 주의

- LLM 자가판단으로 스캔을 발동하지 않는다. 사용자의 명시 명령 전용이다.
- 후보 게이트에서 사용자가 고른 topic 만 캡처한다. 고르지 않은 후보·"카탈로그 보강 후보" 를 임의로 캡처하지 않는다.
- 백그라운드 writer 에게 wip 파일을 직접 저장(Write/Edit)시키지 않는다. 저장은 메인이 한다.
