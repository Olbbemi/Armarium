# wip 캡처 공용 프로토콜

`knowledge-capture` · `knowledge-scan` · `knowledge-study` 세 스킬이 공유하는 기반 규약.
세 스킬은 wip 를 만드는 진입 경로가 서로 다르지만, 저장할 곳을 정하는 방법과 `knowledge-writer` 를 부르고 그 결과를 저장하는 방법은 같다. 그 공통분모를 여기 한 곳에 둔다.

각 스킬은 자기 overview 에서 이 파일을 Read 툴로 로드해 따른다. 스킬끼리 서로를 참조하지 않는다.

---

## 1. Herbarium 경로 검증

wip 를 비롯한 지식 파일은 Herbarium 저장소에만 둔다. 스킬이 사용자에게 디렉토리 경로를 입력받을 때마다 아래 절차로 검증한다.

경로를 코드에 고정하지 않으며, 매 활성마다 새로 입력받는다. 디렉토리명은 동명 저장소가 있을 수 있어 신뢰할 수 없으므로, 검증은 git origin remote 조회로 한다.

### 절차

1. 입력 경로에서 origin remote 를 조회한다.
   `git -C <입력경로> remote get-url origin`
2. 결과가 아래 기대 remote URL 과 정확히 일치하면 채택한다.
3. 일치하지 않거나 조회에 실패하면(존재하지 않는 경로 포함) 사유를 한 줄로 알리고 경로를 다시 입력받는다. 일치할 때까지 반복한다.

### 기대 remote URL

이 값이 경로 검증의 단일 기준이다.

```
git@github.com:Olbbemi/Herbarium.git
```

### 무슨 경로를 몇 개 받을지는 호출한 스킬이 정한다

이 절은 "경로 하나를 어떻게 검증하나" 만 정의한다. 어떤 용도의 경로를 몇 개 받을지는 각 스킬이 자기 overview 에서 정한다. 받은 경로마다 위 절차를 각각 적용한다.

채택한 경로는 메인 LLM 컨텍스트에만 유지하며(세션 휘발), 별도 파일 · 인덱스에 저장하지 않는다.

<FORBIDDEN>
origin remote 가 기대 remote URL 과 일치하지 않는 경로를 채택하지 않는다.
</FORBIDDEN>

<FORBIDDEN>
지식 파일 경로를 코드에 고정 리터럴로 두지 않는다.
</FORBIDDEN>

---

## 2. knowledge-writer 호출

캡처가 확정되면 이 규칙으로 `knowledge-writer` 를 호출한다. 스킬은 아래 입력을 어떻게 채우는지만 다르다.

### 호출 형태

| 항목 | 값 |
|------|----|
| 호출 도구 | Task |
| `subagent_type` | `knowledge-writer` |
| `run_in_background` | `true` (백그라운드) |
| writer 출력 | wip 파일 전체 본문을 최종 메시지로 반환 (Write 안 함) |

<FORBIDDEN>
`knowledge-writer` 를 포그라운드로 호출하지 않는다.
</FORBIDDEN>

### 입력 포맷

Task 도구의 prompt 파라미터에 아래 라벨 + 콜론 구조화 텍스트로 전달한다. JSON 형식은 사용하지 않는다.

| 필드 | 의미 | 비고 |
|------|------|------|
| `save_path` | wip 저장 디렉토리 절대경로 | 1절에서 채택한 경로. writer 가 충돌 검사·파일명 결정 기준으로 사용 |
| `topic` | 주제 식별자 (kebab-case) | wip 파일명 기반 |
| `triggered_by` | 발동 사유 코드 | 값 목록은 호출한 스킬이 자기 문서에 정의한다. 복수 가능. writer 가 깊이·정정 타깃 산정에 사용 |
| `trigger_summary` | 한 줄 사유 | 1~2 문장 |
| `user_known` | 사용자가 안다고 명시한 인접 지식 | writer 의 출발 지식 수준 결정 기준 |
| `discussion_context` | 캡처가 발생한 맥락 | 왜 이 주제가 지금 필요한가. 이 값들은 writer 의 작성 참고용 입력이며 wip "캡처 맥락" 섹션에 전사하지 않는다 |
| `snippets` | 근거 발췌 | 무엇을 앵커로 넣을지는 스킬마다 다르다 (대화 발췌 / 코드 발췌 / 카탈로그 항목 발췌) |
| `kind` | 지식 종류 | `concept`(기본) 또는 `code`. 노트가 답하는 질문으로 정한다(무엇·왜=concept / 어떻게 쓰나=code). 결정 규칙 상세는 promote `2. 형식 변환` 의 kind 결정 규칙 |
| `language` | 대상 언어 | `kind: code` 일 때만. `python` / `rust` / `cpp` 등 |

`triggered_by` 의 값 목록을 이 파일에 나열하지 않는 이유는, 그 값이 각 스킬의 발동 논리에 종속되기 때문이다. 여기 모아 두면 스킬 하나가 코드를 바꿀 때마다 공용 파일을 함께 고쳐야 한다.

<FORBIDDEN>
`triggered_by` 의 스킬별 값 목록을 이 공용 파일에 나열하지 않는다.
</FORBIDDEN>

### 입력 예시

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

---

## 3. 반환 본문 저장

writer 는 파일을 저장하지 않는다. 메인 에이전트가 완료 통지를 받아 저장한다.

- 저장 위치는 `<save_path>/<권장파일명>` 이다. 권장 파일명은 writer 가 충돌 검사를 거쳐 반환한다.
- 반환 본문의 `&`/`<`/`>` HTML 엔티티는 저장 전 원래 문자로 원복한다. task-notification 이 이스케이프해 넘기기 때문이다.

<FORBIDDEN>
백그라운드 writer 에게 Write/Edit 으로 wip 파일을 직접 저장하게 하지 않는다.
</FORBIDDEN>
