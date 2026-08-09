# knowledge-scan

코드베이스를 훑어 쓰인 비자명 문법을 뽑아 wip 초안으로 누적하는 스킬.

## 무엇을 하나

사용자의 명시 명령으로 대상 코드베이스를 스캔해, 언어 카탈로그에 등재된 비자명 문법 중 실제로 쓰인 것을 후보로 뽑는다.<br>
사용자가 고른 topic 마다 `knowledge-writer` 에이전트에 wip 본문 작성을 위임한다.<br>
wip 누적까지만 담당하며, 확정지식 승급은 별도 스킬 [`knowledge-promote`](../knowledge-promote/README.md)가 맡는다.

## 형제 스킬

wip 를 만드는 스킬은 셋이고, 진입 경로가 서로 다르다. writer 호출 · 저장 규칙은 [`references/knowledge-wip-protocol.md`](../../references/knowledge-wip-protocol.md) 를 셋이 공유하고, 대상 저장소 판정은 [`references/knowledge-repos.md`](../../references/knowledge-repos.md) 를 `knowledge-promote` 까지 넷이 공유한다.

| 스킬 | 진입 | 앵커 |
|------|------|------|
| [`knowledge-capture`](../knowledge-capture/README.md) | 대화 중 감지 또는 명시 요청 (상시) | 대화 발췌 |
| `knowledge-scan` | 코드베이스 스캔 명령 (단발) | 코드 발췌 |
| [`knowledge-study`](../knowledge-study/README.md) | CS 로드맵에서 주제 선택 (단발) | 카탈로그 항목 |

## 언제 쓰나

`/knowledge-scan` 슬래시 명령으로 호출했을 때만 동작한다. 자연어 발화로는 뜨지 않도록 description 을 슬래시 호출로 닫아 두었다.<br>
대상 경로는 활성 직후 물어서 받는다.<br>
명령 한 번에 시작해 끝나는 단발 작업이다.

## 구조

- `overview.md` -- 진입점. 대상 경로 · 범위와 언어 확인 · 스캐너 호출 · 후보 게이트 · writer 위임
- `languages/<lang>.md` -- 언어별 스캔 대상 확장자 + 비자명 문법 카탈로그 (현재 `cpp.md`)
- `knowledge-code-scanner` 에이전트 (플러그인 루트 `agents/knowledge-code-scanner.md`) -- 코드베이스 순회 + 문법 탐지 + 후보 반환
- `knowledge-writer` 에이전트 (플러그인 루트 `agents/knowledge-writer.md`) -- 메인 입력을 받아 wip 본문 작성 후 반환 (저장은 안 함)

## 동작 흐름

1. 활성 (`/knowledge-scan` 슬래시 명령)
2. 스캔 대상 경로 확보 (항상 명시, 실재 디렉토리인지 확인)
3. 범위와 언어 확인 -- 카탈로그의 확장자에 걸리는 파일만 세어 디렉토리별 표로 제시하고, 뺄 경로와 스캔 언어를 함께 확인받는다
4. wip 저장 경로 확보 (여기서 중단될 수 있는 3단계를 지난 뒤에 묻는다)
5. `knowledge-code-scanner` 를 **포그라운드**로 호출 -> 후보 목록(`topic` / `usages` / `why`) 반환. 언어가 여럿이면 병렬
6. 후보 게이트 -- 사용자가 캡처할 topic 을 고른다 (언어가 여럿이면 언어별로 나눠 제시)
7. 고른 topic 마다 writer 에 **백그라운드** 위임 -> 반환 본문을 메인이 저장
8. 저장된 파일 경로를 목록으로 알리고 종료

## 비자명 문법 카탈로그

카탈로그 파일은 두 가지를 정한다 -- **스캔 대상 확장자**(cpp 라면 `.cpp .cc .cxx .h .hh .hpp .hxx`)와 **등재된 비자명 문법 목록**(언어 기본 문법은 제외). 확장자는 범위 집계와 순회 양쪽의 기준이라, 빌드 산출물이나 다른 언어 소스는 애초에 세지도 읽지도 않는다.<br>
각 항목의 신호는 그 토픽을 고유하게 대표하는 **강앵커**로 정의하며, `&&`·`|` 같이 흔하고 모호한 토큰은 오탐만 늘리므로 신호로 쓰지 않는다.<br>
스캐너는 강앵커를 Grep 으로 찾고 Read 로 확증하며, 기존 knowledge/wip 파일명(`<language>-<topic>`)과 겹치는 topic 은 걸러낸다(dedup). 언어가 이름에 있어 다른 언어의 같은 topic 을 잘못 걸러내지 않는다. 새 언어는 `languages/` 에 `<lang>.md` 를 더하면 된다.

## 입력 / 출력

- **저장 위치** -- 스캔 발동이 확정된 뒤 사용자에게 입력받는 디렉토리 하위 `<저장경로>/<language>-<topic>.md`. 이 스킬의 산출은 언어 문법이라 파일명에 언어가 앞에 붙는다. 입력 경로는 `references/knowledge-repos.md` 의 등록 저장소 표에 있는 remote 를 가진 저장소 하위여야 한다
- **스캔 대상 경로** -- 저장 경로와 별개로, 활성 직후 물어서 받고 실재하는 디렉토리인지 확인한다
- **제외 경로** -- 미리 정한 목록은 없다. 범위 표를 보고 사용자가 고른 것만 `exclude_globs` 로 넘어간다
- **writer 입력 포맷** -- `sections_path` 로 wip 섹션 규격 파일의 절대경로를 함께 넘긴다. `triggered_by` 는 `code-scan`, `user_known` 은 "기초부터" 고정(아는 주제를 골랐어도 바꾸지 않는다), `kind` 는 항상 `code`, `snippets` 은 스캐너가 준 코드 발췌

## 주의

- 후보 게이트에서 사용자가 고른 topic 만 캡처한다. 고르지 않은 후보·"카탈로그 보강 후보" 를 임의로 캡처하지 않는다.
- 제외도 사용자가 고른 것만 반영한다. 벤더 디렉토리처럼 보여도 임의로 빼지 않고 제외 후보로 제안만 한다.
- 백그라운드 writer 에게 wip 파일을 직접 저장(Write/Edit)시키지 않는다. 저장은 메인이 한다.
