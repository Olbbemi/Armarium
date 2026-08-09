# wip 캡처 공용 프로토콜

`knowledge-capture` · `knowledge-scan` · `knowledge-study` 세 스킬이 공유하는 기반 규약.
세 스킬은 wip 를 만드는 진입 경로가 서로 다르지만, `knowledge-writer` 를 부르고 그 결과를 저장하는 방법은 같다. 그 공통분모를 여기 한 곳에 둔다.

저장할 경로가 등록된 지식 저장소인지 판정하는 방법은 여기 두지 않는다. 그 규약은 `references/knowledge-repos.md` 가 단일 출처이며, wip 를 만들지 않는 `knowledge-promote` 도 그것을 함께 쓴다.

각 스킬은 자기 문서에서 이 파일을 Read 툴로 로드해 따른다. 어느 파일의 어느 시점에서 로드할지는 그 스킬이 정한다. 스킬끼리 서로를 참조하지 않는다.

---

## knowledge-writer 호출

캡처가 확정되면 이 규칙으로 `knowledge-writer` 를 호출한다. 스킬은 아래 입력을 어떻게 채우는지만 다르다.

### 호출 형태

| 항목 | 값 |
|------|----|
| 호출 도구 | Task |
| `subagent_type` | `knowledge-writer` |
| `run_in_background` | `true` (백그라운드) |
| writer 출력 | wip 파일 전체 본문을 최종 메시지로 반환 (Write 안 함) |

### 입력 포맷

Task 도구의 prompt 파라미터에 아래 라벨 + 콜론 구조화 텍스트로 전달한다. JSON 형식은 사용하지 않는다.

| 필드 | 의미 | 비고 |
|------|------|------|
| `save_path` | wip 저장 디렉토리 절대경로 | 경로 검증을 거쳐 채택한 경로. writer 가 충돌 검사·파일명 결정 기준으로 사용 |
| `sections_path` | wip 섹션 규격 파일 절대경로 | 플러그인 루트 `references/knowledge-wip-sections.md`. writer 가 Read 로 로드해 섹션 구성을 따른다 |
| `topic` | 주제 식별자 (kebab-case) | wip 파일명 기반 |
| `triggered_by` | 발동 사유 코드 | 값 목록은 호출한 스킬이 자기 문서에 정의한다. 복수 가능. writer 가 깊이·정정 타깃 산정에 사용 |
| `trigger_summary` | 한 줄 사유 | 1~2 문장 |
| `user_known` | 사용자가 안다고 명시한 인접 지식 | writer 의 출발 지식 수준 결정 기준 |
| `discussion_context` | 캡처가 발생한 맥락 | 왜 이 주제가 지금 필요한가. 이 값들은 writer 의 작성 참고용 입력이며 `캡처 맥락` 섹션에 전사하지 않는다 |
| `snippets` | 근거 발췌 | 무엇을 앵커로 넣을지는 스킬마다 다르다 (대화 발췌 / 코드 발췌 / 카탈로그 항목 발췌) |
| `kind` | 지식 종류 | `concept`(기본) 또는 `code`. 노트가 답하는 질문으로 정한다(무엇·왜=concept / 어떻게 쓰나=code). 결정 규칙 상세는 `skills/knowledge-promote/format/format.md` 의 `kind 결정 규칙` |
| `language` | 대상 언어 | `kind: code` 일 때만. `python` / `rust` / `cpp` 등 |

### 입력 예시

```
save_path: <지식 저장소 루트>/wip
sections_path: /home/olbbemi/.claude/plugins/cache/hortus/armarium/<버전>/references/knowledge-wip-sections.md
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

## 반환 본문 저장

writer 는 파일을 저장하지 않는다. 메인 에이전트가 완료 통지를 받아 저장한다.

- 저장 위치는 `<save_path>/<권장파일명>` 이다. 권장 파일명은 writer 가 충돌 검사를 거쳐 반환한다.
- 반환 본문의 `&`/`<`/`>` HTML 엔티티는 저장 전 원래 문자로 원복한다.
