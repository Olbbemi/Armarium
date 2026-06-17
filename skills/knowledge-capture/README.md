# knowledge-capture

논의 중 전제 지식의 부재를 감지해 wip 초안으로 누적하는 스킬.

## 무엇을 하나

활성된 동안 메인 LLM이 매 발화에서 점수표로 지식 부재를 자동 감지하고, 임계에 도달하면 `knowledge-writer` 에이전트에 wip 본문 작성을 위임한다. wip 누적까지만 담당하며, 확정지식 승급은 별도 스킬 [`knowledge-promote`](../knowledge-promote/README.md)가 맡는다.

## 언제 쓰나

`/knowledge-capture` 슬래시 명령으로 **명시적으로 활성**했을 때만 동작한다. "이거 무슨 개념인지 모르겠어", "이 부분 배경 지식이 부족한 것 같아" 같은 상황에서 켜둔다. 활성 판단은 사용자에게만 있고, LLM 자가판단으로 활성하지 않는다.

## 구조

- `overview.md` — 진입점. 점수표·트리거·호출 규칙 정의
- `knowledge-writer` 에이전트 (플러그인 루트 `agents/knowledge-writer.md`) — 메인 입력을 받아 외부 조사 + wip 본문 작성 후 반환 (저장은 안 함)

## 동작 흐름

1. 활성 (슬래시 명령) — 활성 직후 저장 경로를 사용자에게 입력받고 git origin remote 로 Herbarium 여부 검증
2. 매 발화마다 두 트리거 동시 감시
   - **자동 감지** — 점수표 합계 3점 이상
   - **명시 지시** — 사용자의 직접 저장 요청 ("이거 knowledge로 남겨줘" 등)
3. 트리거 발생 시 호출 입력 구성
4. `knowledge-writer` 를 **백그라운드**(Task, `run_in_background: true`)로 호출 — 메인은 논의 계속
5. writer가 본문 전체를 최종 메시지로 반환 (Write 안 함)
6. 메인이 완료 통지를 받아 wip 파일로 저장 (HTML 엔티티 원복)

## 자동 감지 점수표

개념 지식만 자동 감지한다(코드/문법은 명시 요청으로만 캡처). 점수표는 세 그룹으로 나뉘고, 각 행에 역할 태그(`gate`/`user_known`/`both`)가 붙어 발동 판정과 깊이 보정을 한 표에서 갈라 뽑는다.

- **공백** (A1~A4) — 처음 등장·판단 불가·자기보고 "모른다"·이름만 앎
- **오해** (M1~M3) — 개념 혼용·절대화·옛 정의를 사실로 (같은 오해 2회 반복 시 해당 행 +1 가산)
- **앵커** (C1~C3) — 인접 계층 이탈·친숙 개념 환원·하위를 전체로 착각

켜진 행 점수 합계가 **3점 이상**(임계 3~4)이면 즉시 위임, 미만은 무시. 점수는 메인 LLM 컨텍스트에만 존재하며 세션 단위로 휘발(파일 저장 안 함). 상세 표(점수·역할 태그·드러나는 user_known)는 overview.md 참조.

## 입력 / 출력

- **저장 위치** — 활성 시 사용자에게 입력받는 디렉토리 하위 `<저장경로>/<topic>.md`. 입력 경로는 origin remote 가 `git@github.com:Olbbemi/Herbarium.git` 인 Herbarium 저장소 하위여야 하며, 아니면 다시 입력받는다
- **writer 입력 포맷** — `save_path` / `topic` / `triggered_by` / `trigger_summary` / `user_known` / `discussion_context` / `snippets` / `kind` / `language` (라벨+콜론 구조화 텍스트, JSON 아님)

## 주의

- LLM 자가판단으로 활성·점수 계산을 시작하지 않는다.
- 백그라운드 writer에게 wip 파일을 직접 저장(Write/Edit)시키지 않는다. 저장은 메인이 한다.
- wip 단계에서는 위임·묶음·분리 여부를 사용자에게 묻지 않고 자동 진행한다 (승급 단계는 별도 승인 규약). 단 명시 요청 경로에서 `user_known` 이 비면 writer 호출 전에 수준 보충 질문은 한다.
