# 지식 캡처

논의에 필요한 지식, 그리고 코드베이스에 쓰인 문법 지식을 감지·수집해 wip 문서로 누적하는 스킬.

이 스킬은 두 모드로 나뉘며, 공유 기반(저장 경로 · `knowledge-writer` 호출 · 반환 처리) 위에서 각 모드가 입력을 다르게 모은다. 모드는 2개지만, 캡처가 시작되는 트리거로 보면 모드 1 이 두 갈래로 갈려 총 3개다.

| 모드 | 트리거 | 촉발 | 대상 지식 |
|------|--------|------|----------|
| 1 논의 감시 (`modes/conversation.md`) | 1-a 자동 감지 | LLM 이 대화를 점수로 자동 발동 | 개념만 (코드/문법은 자동 감지 안 함) |
| 1 논의 감시 (`modes/conversation.md`) | 1-b 명시 요청 | 사용자가 저장을 직접 지시 | 개념 + 코드/문법(지명) |
| 2 코드 스캔 (`modes/code-scan.md`) | 2 스캔 | 사용자가 스캔을 명시 명령 | 코드/문법(코드베이스에서 발견) |

코드/문법 지식은 자동 감지(1-a)가 잡지 않는다 -- 눈앞에 코드가 있어야 물어볼 수 있어서다. 그래서 코드/문법은 1-b(지명)나 2(스캔)로만 들어온다. 각 갈래의 트리거·게이트·에이전트 세부는 해당 모드 파일에 있다.

wip 를 확정지식으로 올리는 승급(지식화) 단계는 별도 독립 스킬 `knowledge-promote` 가 담당한다. 본 스킬은 캡처(wip 누적)까지만 다룬다.

---

## 활성 조건

`knowledge-capture` 는 사용자가 `/knowledge-capture` 슬래시 명령으로 명시적으로 호출했을 때만 활성된다.
활성 여부의 판단은 사용자에게만 있다.

활성 후 모드 1(논의 감시)은 상시 돌고, 모드 2(코드 스캔)는 사용자가 명시적으로 스캔을 명령할 때만 돈다. 둘은 충돌하지 않고 공존한다.

<RICOCHET>
LLM 자가판단으로 스킬을 활성하거나 점수 계산을 시작하지 않는다.
</RICOCHET>

---

## 저장 경로 설정

활성 직후, wip 파일을 저장할 디렉토리 경로를 사용자에게 입력받는다.
경로를 코드에 고정하지 않으며, 매 활성마다 새로 입력받는다.

입력 경로는 Herbarium 저장소 하위여야 한다. 디렉토리명은 동명 저장소가 있을 수 있어 신뢰할 수 없으므로, 검증은 git origin remote 조회로 한다.

### 검증 절차

1. 입력 경로에서 origin remote 를 조회한다.
   `git -C <입력경로> remote get-url origin`
2. 결과가 아래 기대 remote URL 과 정확히 일치하면 채택한다.
3. 일치하지 않거나 조회에 실패하면(존재하지 않는 경로 포함) 사유를 한 줄로 알리고 경로를 다시 입력받는다. 일치할 때까지 반복한다.

#### 기대 remote URL

이 값이 저장 경로 검증의 단일 기준이다.

```
git@github.com:Olbbemi/Herbarium.git
```

채택한 저장 경로는 점수표와 마찬가지로 메인 LLM 컨텍스트에만 유지하며(세션 휘발), 별도 파일 · 인덱스에 저장하지 않는다.

<PENETRATE>
활성 직후 wip 저장 디렉토리 경로를 사용자에게 입력받는다.
</PENETRATE>

<PENETRATE>
입력 경로의 git origin remote 가 기대 remote URL 과 정확히 일치할 때만 저장 경로로 채택한다.
</PENETRATE>

<RICOCHET>
origin remote 가 기대 remote URL 과 일치하지 않는 경로를 저장 경로로 채택하지 않는다.
</RICOCHET>

<RICOCHET>
wip 저장 경로를 코드에 고정 리터럴로 두지 않는다.
</RICOCHET>

---

## 하위 스킬

| 스킬 | 파일 | 역할 |
|------|------|------|
| 모드 1: 논의 감시형 | `skills/knowledge-capture/modes/conversation.md` | 점수표 자동 감지 + 명시 저장 요청으로 wip 캡처 |
| 모드 2: 코드 스캔형 | `skills/knowledge-capture/modes/code-scan.md` | 코드베이스를 훑어 비자명 문법 후보를 뽑고 골라 wip 캡처 |
| 언어 카탈로그 | `skills/knowledge-capture/languages/<lang>.md` (현재 `cpp.md`) | 언어별 "정리할 만한 비자명 문법" 목록. 모드 2 스캐너가 로드해 코드와 대조 (모드 2) |
| `knowledge-code-scanner` 에이전트 | `agents/knowledge-code-scanner.md` | 코드베이스 순회 + 문법 사용처 탐지 + 파일명 dedup 후 후보 목록 반환 (모드 2) |
| `knowledge-writer` 에이전트 | `agents/knowledge-writer.md` | 메인의 입력을 받아 wip 본문을 작성하고 메인에 반환 (저장은 메인이 수행. 두 모드 공용) |

세부 실행 규칙은 각 모드 파일을 Read 툴로 로드해 따른다.

---

## 실행 순서

1. 활성 (슬래시 명령). 활성 직후 저장 경로를 설정한다 (`저장 경로 설정` 섹션)
2. 모드 분기
   - 모드 1(논의 감시): 활성 중 매 발화마다 상시 감시. `modes/conversation.md` 를 Read 툴로 로드해 따른다
   - 모드 2(코드 스캔): 사용자가 코드베이스 스캔을 명시 명령했을 때만. `modes/code-scan.md` 를 Read 툴로 로드해 따른다
3. 두 모드 공히, 캡처가 확정되면 `공유: knowledge-writer 호출` 규칙으로 writer 를 호출하고, 반환 본문을 메인이 wip 파일로 저장한다

각 모드의 트리거·게이트·에이전트 호출 세부는 해당 모드 파일에 정의한다. 에이전트가 어떻게 병렬/직렬로 도는지도 모드 파일이 정한다.

### 단계 시각화 (TaskCreate)

실행 단계가 드러나는 모드 2(코드 스캔)는 진행을 TaskCreate 로 시각화한다. 원칙은 다음과 같다.

- 포그라운드 단계 -- 시작 시 in_progress, 완료 시 completed
- 백그라운드 에이전트 호출 단계 -- 호출 즉시 completed ("위임 완료"). subject 는 "X 에이전트 호출" 형식
- 사용자 확인 게이트(후보 게이트) -- 확인 요청 직전 completed, 응답 후 다음 task in_progress
- 아주 짧은 준비 작업(언어 판정 등) -- task 생략

모드 1(논의 감시)은 발화마다 배후에서 도는 상시 감지라 매 발화를 task 로 만들지 않는다. 임계 도달로 writer 위임이 발생하는 시점만 위 원칙(백그라운드 호출 = 즉시 completed)으로 표시한다.

---

## 공유: knowledge-writer 호출

두 모드 모두 캡처가 확정되면 이 규칙으로 `knowledge-writer` 를 호출한다. 모드는 아래 입력을 어떻게 채우는지만 다르다.

### 호출 형태

| 항목 | 값 |
|------|----|
| 호출 도구 | Task |
| `subagent_type` | `knowledge-writer` |
| `run_in_background` | `true` (백그라운드) |
| writer 출력 | wip 파일 전체 본문을 최종 메시지로 반환 (Write 안 함) |
| 저장 | 메인 에이전트가 통지를 받아 활성 시 설정한 저장 경로 하위 `<저장경로>/<topic>.md` (또는 suffix) 로 직접 저장 |

<PENETRATE>
`knowledge-writer` 호출은 백그라운드(`run_in_background: true`)로 한다. 메인은 완료 통지 도착까지 사용자 논의를 계속한다.
</PENETRATE>

<PENETRATE>
작업(조사·작문)은 백그라운드 서브에이전트 writer 에 위임하고, wip 파일 저장은 메인 에이전트가 완료 통지 도착 시 직접 수행한다.
</PENETRATE>

<PENETRATE>
반환 본문의 `&`/`<`/`>` HTML 엔티티는 저장 전 원복한다.
</PENETRATE>

<RICOCHET>
백그라운드 writer 에게 Write/Edit 으로 wip 파일을 직접 저장하게 하지 않는다.
</RICOCHET>

### `knowledge-writer` 에이전트 호출 입력 포맷

Task 도구의 prompt 파라미터에 아래 라벨 + 콜론 구조화 텍스트로 전달한다. JSON 형식은 사용하지 않는다.

| 필드 | 의미 | 비고 |
|------|------|------|
| `save_path` | 활성 시 확정한 wip 저장 디렉토리 절대경로 | `저장 경로 설정` 에서 채택한 경로. writer 가 충돌 검사·파일명 결정 기준으로 사용 |
| `topic` | 주제 식별자 (kebab-case) | wip 파일명 기반. 모드 2 는 언어 카탈로그의 정식 명칭을 쓴다 |
| `triggered_by` | 발동 사유 코드 (모드 1: A1~A4 / M1·M2·M3 / C1~C3 또는 `user-request`, 모드 2: `code-scan`) | 복수 가능. writer 가 깊이·정정 타깃 산정에 사용 |
| `trigger_summary` | 한 줄 사유 | 1~2 문장 |
| `user_known` | 사용자가 안다고 명시한 인접 지식 | 에이전트의 출발 지식 수준 결정 기준. 모드 2 는 스캔 전제상 "기초부터"(해당 문법을 모름)로 채운다 |
| `discussion_context` | 캡처가 발생한 맥락 | 왜 이 주제가 지금 필요한가. 이 값들은 writer 의 작성 참고용 입력이며 wip "캡처 맥락" 섹션에 전사하지 않는다 (writer 골격의 `서술 톤` 참조) |
| `snippets` | 근거 발췌 | 모드 1 은 대화 발췌, 모드 2 는 코드베이스 발췌(file:line + 코드). 앵커 역할은 동일 |
| `kind` | 지식 종류 | `concept`(기본) 또는 `code`. 노트가 답하는 질문으로 정함(무엇·왜=concept / 어떻게 쓰나=code). 모드 2 는 항상 `code`. 결정 규칙 상세는 promote `2. 형식 변환` 의 kind 결정 규칙 |
| `language` | 대상 언어 | `kind: code` 일 때만. `python` / `rust` / `cpp` 등 |

#### 입력 예시 (zmq 라이브러리 — 모드 1, 한 항목 묶음)

```
save_path: /home/olbbemi/Project/Herbarium/wip
topic: zmq
triggered_by: A1, A2, A3
trigger_summary:
  ZMQ 라이브러리 자체에 대한 전제 지식 부재로 라이브러리 선택 논의 진행 불가.
  PUB/SUB 등 메시징 패턴 종류도 전혀 모름.
user_known:
  - TCP/UDP 차이는 알고 있음
  - 메시지 큐 개념은 들어본 정도
discussion_context:
  설계 논의 중 마이크로서비스 간 메시지 큐 라이브러리 후보 선정 중
snippets:
  - Claude: 메시지 큐로 ZMQ 를 검토해볼까요?
  - 사용자: zmq 가 뭐지? 처음 들어봐
  - Claude: PUB/SUB 패턴이 적합할 것 같습니다
  - 사용자: 패턴 종류가 뭐가 있는지 전혀 모르겠어
```

같은 상황을 두 항목으로 쪼갠 예시:

- 항목 1: `topic: zmq` (라이브러리 자체 개요)
- 항목 2: `topic: zmq-messaging-patterns` (PUB/SUB · REQ/REP 등 패턴 종류)

묶음 / 분리 결정은 모드 1 에서 메인 LLM 의 자율 판단이며 사용자 확인을 받지 않는다.

---

## 추후 정의 항목

다음 항목은 별도 단계에서 정의한다. 정의 시 본 overview 또는 하위 파일로 흡수된다.

호스트 스킬 페어링 및 알림 매커니즘 (이전 설계의 훅 등) 은 별도 단계에서 정의한다.

승급(promoter)·확정지식 디렉토리 구조·카테고리 결정은 별도 스킬 `knowledge-promote` 로 분리됨.
