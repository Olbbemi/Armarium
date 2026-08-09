# 코드 스캔 캡처

사용자의 명시 명령으로 대상 코드베이스를 훑어, 쓰인 비자명 문법을 후보로 뽑고 사용자가 골라 wip 로 캡처하는 스킬.

wip 를 확정지식으로 올리는 승급은 별도 스킬 `knowledge-promote` 가 담당한다. 본 스킬은 캡처까지만 다룬다.

---

## 활성 조건

사용자가 `/knowledge-scan` 슬래시 명령으로 호출했을 때만 활성된다.

---

## 공용 프로토콜

공용 파일 둘이 각각 단일 출처다.

| 파일 | 담는 것 |
|------|--------|
| `references/knowledge-repos.md` | 받은 경로가 등록된 지식 저장소인지 판정하는 절차 |
| `references/knowledge-wip-protocol.md` | `knowledge-writer` 호출 형태 · 입력 포맷 · 반환 본문 저장 |

wip 저장 경로를 확보하는 단계에서 둘 다 Read 툴로 로드해 따른다. 본 스킬이 받는 경로는 wip 저장 디렉토리 하나이며, 경로 검증 절차를 그 경로에 적용한다.

---

## 하위 스킬

| 파일 | 역할 |
|------|------|
| `skills/knowledge-scan/languages/<lang>.md` (예: `cpp.md`) | 언어별 스캔 대상 확장자 + "정리할 만한 비자명 문법" 목록. 범위 집계와 스캐너 대조의 기준 |
| `references/knowledge-repos.md` | 네 knowledge 스킬 공용 -- 경로 검증 |
| `references/knowledge-wip-protocol.md` | wip 를 만드는 세 스킬 공용 -- writer 호출 · 저장 규칙 |

에이전트 2개를 쓴다. 정의 파일은 플러그인 루트 `agents/` 에 있다.

| 에이전트 | 파일 | 역할 |
|----------|------|------|
| `knowledge-code-scanner` | `agents/knowledge-code-scanner.md` | 코드베이스 순회 + 문법 사용처 탐지 + 파일명 dedup 후 후보 목록 반환 |
| `knowledge-writer` | `agents/knowledge-writer.md` | 메인의 입력을 받아 wip 본문을 작성하고 반환 (저장은 메인이 수행) |

---

## 실행 순서

1. 활성 (`/knowledge-scan` 슬래시 명령)
2. 스캔 대상 경로 확보 (`스캔 대상 경로`)
3. 범위와 언어 확인 (`범위와 언어 확인`)
4. 공용 프로토콜을 로드하고 wip 저장 경로를 확정한다 (`공용 프로토콜`)
5. `knowledge-code-scanner` 호출 -- 포그라운드. 입력: `codebase_path` / `exclude_globs` / `language` / `catalog_path` / `knowledge_glob` / `wip_glob`. 출력: 후보 목록을 최종 메시지로 반환
6. 후보 게이트 -- 사용자가 캡처할 topic 을 고른다
7. 고른 topic 마다 `knowledge-writer` 호출 -- 백그라운드 (`run_in_background: true`). 입력: `writer 위임` 의 값. 출력: wip 본문을 반환
8. 저장과 보고 (`저장과 보고`)

### 단계 시각화 (TaskCreate)

- 대상 경로·저장 경로 확보 같은 짧은 준비는 task 로 만들지 않는다
- 범위와 언어 확인 -- 사용자에게 확인 요청 직전 completed, 응답 후 다음 task in_progress
- 스캐너 호출(포그라운드) -- 시작 시 in_progress, 반환 시 completed
- 후보 게이트 -- 사용자에게 확인 요청 직전 completed, 응답 후 다음 task in_progress
- writer 호출(백그라운드) -- 호출 즉시 completed ("위임 완료"). subject 는 "knowledge-writer 에이전트 호출" 형식. 고른 topic 마다 하나씩
- 저장과 보고 -- 첫 통지가 도착할 때 in_progress, 마지막 저장이 끝나면 completed

---

## 스캔 대상 경로

스캔할 코드베이스 경로는 항상 명시적으로 확보한다. 현재 작업 디렉토리가 곧 소스라고 가정하지 않는다.

활성 직후 대상 경로를 한 줄 물어 받는다.

받은 경로가 실재하는 디렉토리인지 확인한다(`ls -d`). 없거나 디렉토리가 아니면 사유를 한 줄로 알리고 다시 받는다.

상대경로로 받았으면 절대경로로 바꿔 둔다.

이 경로가 스캐너 입력 `codebase_path` 가 된다. 저장 경로(지식 저장소의 wip)와는 별개다.

---

## 범위와 언어 확인

무엇을 스캔할지와 어느 언어로 스캔할지를 한 게이트에서 함께 확정한다.

### 절차

1. 보유 카탈로그(`skills/knowledge-scan/languages/` 하위 `<lang>.md` 존재분)를 모두 읽어, 각 카탈로그의 `스캔 대상 확장자` 를 모은다.
2. 대상 경로 하위에서 그 확장자에 걸리는 파일만 훑어 디렉토리별·언어별 파일 수를 센다. 깊이 제한은 두지 않는다.
3. 아래 형식으로 제시하고, 뺄 디렉토리와 스캔 언어를 함께 확인받는다.
4. 사용자가 뺀 경로가 스캐너 입력 `exclude_globs` 가 된다. 제외를 반영해 언어별 수를 다시 세고 확정한다.

### 제시 형식

파일이 있는 디렉토리를 깊이 제한 없이 나열한다.

```
| 디렉토리          | 파일 수 | 언어 |
| src/core/         |      92 | cpp  |
| src/net/          |      56 | cpp  |
| src/vendor/spdlog |     311 | cpp  |
| tests/            |      42 | cpp  |

"src/vendor/spdlog 를 빼고 cpp 401개 파일을 스캔할까요?
 더 뺄 것이 있으면 알려주세요."
```

남의 코드로 보이는 것이 있으면 제외 후보로 짚어 제안하되, 실제로 뺄지는 사용자가 정한다.

### 판정 갈래

- **보유 언어 하나** -- 그 언어로 확인받는다.
- **보유 언어 여럿** -- 언어별 수를 함께 보여주고 전부 할지 일부만 할지 확인받는다.
- **보유 언어가 하나도 없음** -- "스캔 가능한 언어(카탈로그 보유)가 없습니다" 를 알리고 중단한다. 경로를 잘못 받았을 수 있으므로 대상 경로도 함께 다시 확인한다.

사용자가 특정 언어를 콕 집어 명령했으면(그 언어 카탈로그가 있으면) 감지보다 그 지정을 우선한다.

확정된 언어마다 그 언어의 `skills/knowledge-scan/languages/<lang>.md` 절대경로가 스캐너 입력 `catalog_path` 가 된다.

<FORBIDDEN>
감지한 언어를 사용자 확인 없이 스캔 언어로 확정하지 않는다.
</FORBIDDEN>

<FORBIDDEN>
사용자가 빼라고 하지 않은 경로를 `exclude_globs` 에 넣지 않는다.
</FORBIDDEN>

---

## 스캐너 호출

언어가 확정되면 언어마다 `knowledge-code-scanner` 에이전트를 호출해 후보 목록을 받는다. `exclude_globs` 는 언어와 무관하게 확정된 하나를 모든 호출에 같이 넘긴다.

언어가 여럿이면 호출을 한 응답에 모아 보내 병렬로 돌린다. 언어마다 대조할 카탈로그가 달라 서로 의존하지 않는다.

### 호출 형태

| 항목 | 값 |
|------|----|
| 호출 도구 | Task |
| `subagent_type` | `knowledge-code-scanner` |
| `run_in_background` | `false` (포그라운드) |
| 스캐너 출력 | 후보 목록을 최종 메시지로 반환 (파일 저장 안 함) |

### 스캐너 입력 포맷

Task 도구의 prompt 파라미터에 라벨 + 콜론 구조화 텍스트로 전달한다. JSON 형식은 쓰지 않는다.

| 필드 | 값 |
|------|----|
| `codebase_path` | 스캔 대상 경로 (`스캔 대상 경로` 에서 확보) |
| `exclude_globs` | 순회에서 뺄 경로 목록. 사용자가 `범위와 언어 확인` 에서 고른 것뿐이며, 고른 것이 없으면 빈 값 |
| `language` | 확정 언어 (예: `cpp`) |
| `catalog_path` | 그 언어의 `skills/knowledge-scan/languages/<lang>.md` 절대경로 |
| `knowledge_glob` | dedup 대조용 확정지식 Glob. 저장 경로가 속한 지식 저장소의 `knowledge/**/*.md` |
| `wip_glob` | dedup 대조용 wip Glob. 같은 지식 저장소의 `wip/*.md` |

`knowledge_glob` / `wip_glob` 은 확보한 wip 저장 경로가 속한 지식 저장소 루트에서 구성한다.

---

## 후보 게이트

스캐너가 반환한 후보 목록을 사용자에게 제시하고, 어떤 것을 wip 로 캡처할지 고르게 한다. 무엇을 캡처할지는 이 게이트에서만 정한다.

- 후보마다 `topic` · `usages`(실측 <=3개) · `why` 를 함께 보여 사용자가 판단할 근거를 준다.
- 언어가 여럿이면 언어별로 나눠 제시한다.
- 사용자는 여럿을 한 번에 고를 수 있다. 고른 topic 각각을 캡처 대상으로 확정한다.
- 스캐너가 "카탈로그 보강 후보"(카탈로그 밖 발견)를 붙였으면 정식 후보와 구분해 참고로만 보여주고, 이 게이트의 캡처 선택지로 올리지 않는다.
- 후보가 없으면("정리할 신규 비자명 문법 없음") 그대로 알리고 종료한다. writer 를 호출하지 않는다.
- 후보는 있는데 사용자가 하나도 고르지 않으면 마찬가지로 writer 를 호출하지 않고 종료한다. 다시 고르라고 되묻지 않는다.

<FORBIDDEN>
사용자가 고르지 않은 후보를 임의로 캡처하지 않는다.
</FORBIDDEN>

---

## writer 위임

사용자가 고른 topic 마다 `knowledge-writer` 를 호출해 wip 본문 작성을 위임한다. 호출 형태·입력 포맷·저장 책임은 공용 프로토콜의 `knowledge-writer 호출` 과 `반환 본문 저장` 을 그대로 따른다. 여러 topic 을 골랐으면 각각 백그라운드로 위임한다.

이 스킬이 채우는 입력값은 다음과 같다.

| 필드 | 이 스킬의 값 |
|------|-------------|
| `save_path` | 확보한 wip 저장 경로 |
| `sections_path` | 플러그인 루트 `references/knowledge-wip-sections.md` 의 절대경로 |
| `topic` | 카탈로그의 정식 명칭 그대로 |
| `triggered_by` | `code-scan` |
| `trigger_summary` | 코드 스캔에서 발견된 문법임을 한 줄로 |
| `user_known` | `기초부터` 고정. 사용자가 이미 아는 주제를 골랐더라도 바꾸지 않는다 -- 빠짐없이 적힌 문서를 남기는 것이 목적이다 |
| `discussion_context` | 스캔한 대상 -- 코드베이스 경로, 확정 언어, 그 문법이 발견된 위치 |
| `snippets` | 스캐너가 준 `usages`(코드 발췌 앵커) |
| `kind` | `code` (이 스킬은 항상) |
| `language` | 확정 언어 |

---

## 저장과 보고

위임한 topic 수만큼 완료 통지가 도착한다. 통지마다 반환 본문을 공용 프로토콜의 `반환 본문 저장` 대로 저장한다.

저장 직전에 이번 실행에서 이미 저장한 파일명과 겹치는지 보고, 겹치면 뒤에 번호를 더해(`<이름>-2.md`) 저장한다.

일부만 도착한 시점에 종료하지 않는다. 남은 위임이 있으면 그 통지까지 기다린다.

전부 저장하면 저장된 파일 경로를 목록으로 알리고 종료한다.

<FORBIDDEN>
통지가 도착하지 않은 위임이 남아 있는 상태에서 종료 보고를 하지 않는다.
</FORBIDDEN>

<FORBIDDEN>
이번 실행에서 이미 저장한 파일을 덮어쓰지 않는다.
</FORBIDDEN>
