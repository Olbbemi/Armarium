# 스킬 검증

만들어진 스킬이 `skill-writing` 규격과 의도대로 동작하는지 확인하는 스킬.

---

## 출력 규칙

결과는 `<프로젝트 루트>/.claude/verify/<대상스킬명>/result.md` 에 저장한다. 콘솔에는 저장이 끝난 뒤 요약 테이블과 저장 경로만 출력한다.

보고서를 대상 스킬 디렉토리 안에 두면 그 스킬을 다시 검증할 때 추가 마크다운 파일로 잘못 분류되거나 스킬 시스템에 부수 인식된다.

<FORBIDDEN>
단계별 상세 결과를 콘솔에 출력하지 않는다.
</FORBIDDEN>

<FORBIDDEN>
보고서 파일을 대상 스킬 디렉토리(`<대상 스킬 디렉토리>/`) 안에 저장하지 않는다.
</FORBIDDEN>

### 보고서 저장 위치 기준

`<프로젝트 루트>` 는 **대상 스킬 파일 경로에서 거슬러 올라가 결정한 그 스킬의 프로젝트 루트**다. 따라서 armarium 내부 스킬을 검증하면 armarium 루트의 `.claude/` 에, 별도 프로젝트(예: terrarium) 안에 있는 스킬을 검증하면 그 프로젝트 루트의 `.claude/` 에 보고서가 생성된다.

프로젝트 루트는 대상 스킬 디렉토리를 기준으로 `git -C <대상 스킬 디렉토리> rev-parse --show-toplevel` 로 구한다. git 저장소가 아니어서 결과를 얻지 못하면 사용자에게 프로젝트 루트를 확인한다.

<FORBIDDEN>
보고서 저장 경로의 `.claude` 를 현재 작업 디렉토리나 이 플러그인 루트 기준으로 고정하지 않는다.
</FORBIDDEN>

<FORBIDDEN>
프로젝트 루트를 git 으로 구하지 못했을 때 임의로 추정해 저장하지 않는다.
</FORBIDDEN>

---

## 검증 대상 확인

검증 시작 전 사용자에게 대상 스킬을 확인한다.

<FORBIDDEN>
대상 스킬이 확정되지 않은 상태에서 검증을 시작하지 않는다.
</FORBIDDEN>

> "어떤 스킬을 검증할까요? SKILL.md 경로를 알려주세요."

---

## 하위 스킬

검증 절차의 단일 출처는 `checks/` 디렉토리에 있다. 2단계 병렬 에이전트는 각자 자신이 담당하는 check 파일을 Read 해서 절차를 수행하며, 판정에 다른 검사 파일이 필요하면 그것도 읽는다 (태그 검증의 무검출 대조가 그 경우다).

| 검증 항목 | check 파일 | 실행 주체 |
|----------|------------|----------|
| 구조 검증 | `skills/skill-verify/checks/structure-check.md` | 메인 (1단계 게이트) |
| 프론트매터 검증 | `skills/skill-verify/checks/frontmatter-check.md` | 에이전트 `skill-verify-frontmatter` (2단계 병렬) |
| Description 검증 | `skills/skill-verify/checks/description-check.md` | 에이전트 `skill-verify-description` (2단계 병렬) |
| 금지 규칙 태그 검증 | `skills/skill-verify/checks/tag-check.md` | 에이전트 `skill-verify-tag` (2단계 병렬) |
| 형식·언어 검증 | `skills/skill-verify/checks/format-check.md` | 에이전트 `skill-verify-format` (2단계 병렬) |
| 에이전트 검증 | `skills/skill-verify/checks/agent-check.md` | 에이전트 `skill-verify-agent` (2단계 병렬, 조건부) |
| 동작 검증 | `skills/skill-verify/checks/behavior-check.md` | 메인 (3단계 마무리) |

---

## 실행 순서

사전 준비 후 총 3단계로 진행한다.

### 사전 준비 -- 작업 디렉토리 생성

1단계 진입 전 메인이 Bash 로 두 디렉토리를 생성한다 (`mkdir -p`).

- `<대상 스킬 디렉토리>/wip/` -- 단계별 개별 검증 결과 저장용
- `<프로젝트 루트>/.claude/verify/<대상스킬명>/` -- 최종 보고서 저장용 (`<프로젝트 루트>` 는 출력 규칙 섹션의 보고서 저장 위치 기준을 따른다)

이후 모든 단계가 자신의 검증 결과를 wip 디렉토리에 개별 파일로 저장하고, 결과 취합 후 최종 보고서를 결과 디렉토리에 작성한다. 메인이 직접 수행하는 1단계·3단계도 예외 없이 wip 파일에 저장한다.

#### wip 쓰기 가능 확인

2단계 에이전트는 백그라운드로 돌아 권한 프롬프트를 띄우지 못하므로, wip 경로가 사전 허용되어 있지 않으면 Write 가 조용히 거부된다. 에이전트는 완료 통지를 보내는데 파일은 없는 상태가 된다.

디렉토리 생성 직후 메인이 wip 경로에 시험 쓰기를 한 번 해 본다 (예: Bash 로 임시 파일을 만들었다 지운다). 실패하면 그 경로가 사전 허용되지 않은 것이므로, 2단계로 넘어가지 않고 사용자에게 경로와 실패 사실을 알린 뒤 판단을 받는다.

### 1단계 -- 구조 검증 (게이트)

메인 Claude 가 직접 수행한다. 빠른 분기가 필요하고 후속 단계의 전제이기 때문에 에이전트로 위임하지 않는다.

TaskCreate 로 "1단계: 구조 검증" task 를 등록하고 in_progress 로 설정한 뒤 검증을 시작한다. wip 파일 저장이 끝나면 completed 로 닫는다.

`skills/skill-verify/checks/structure-check.md` 를 Read 툴로 로드해서 검증을 실행한다.

검증 결과는 메인이 Write 툴로 `<대상 스킬 디렉토리>/wip/skill-verify-structure.md` 에 저장한다.

이 단계가 실패하면 즉시 중단하고 1단계 결과를 wip 파일에 저장한 뒤 보고서를 작성한다. 후속 단계가 의존하는 파일 자체가 없을 수 있다.

<FORBIDDEN>
1단계 구조 검증이 실패한 상태로 2단계·3단계를 진행하지 않는다.
</FORBIDDEN>

### 2단계 -- 병렬 검증 (5개 에이전트)

아래 에이전트들을 Task 도구로 한 응답 안에 모두 백그라운드 호출(`run_in_background: true`) 한다. 5개 호출 직후 메인은 3단계로 넘어가고, 완료 통지는 결과 취합 시점에 모은다.

순차로 부르면 병렬 효과가 사라지고, 일반 호출로 바꾸면 메인이 통지 대기로 멈춰 3단계 병렬 진행이 막힌다.

<FORBIDDEN>
5개 검증 에이전트를 여러 응답에 나눠 호출하지 않는다.
</FORBIDDEN>

<FORBIDDEN>
5개 검증 에이전트를 일반 호출(`run_in_background` 생략)로 시작하지 않는다.
</FORBIDDEN>

TaskCreate 로 "검증 에이전트 호출" task 를 등록하고 in_progress 로 설정한다. 아래 5개 에이전트를 한 응답에 호출한 즉시 completed 로 닫는다.

- [ ] 에이전트 `skill-verify-frontmatter`: 백그라운드 호출 (`run_in_background: true`). 입력: 대상 스킬 디렉토리 경로. 출력: `<대상 스킬 디렉토리>/wip/skill-verify-frontmatter.md`
- [ ] 에이전트 `skill-verify-description`: 백그라운드 호출 (`run_in_background: true`). 입력: 동일. 출력: `<대상 스킬 디렉토리>/wip/skill-verify-description.md`
- [ ] 에이전트 `skill-verify-tag`: 백그라운드 호출 (`run_in_background: true`). 입력: 동일. 출력: `<대상 스킬 디렉토리>/wip/skill-verify-tag.md`
- [ ] 에이전트 `skill-verify-format`: 백그라운드 호출 (`run_in_background: true`). 입력: 동일. 출력: `<대상 스킬 디렉토리>/wip/skill-verify-format.md`
- [ ] 에이전트 `skill-verify-agent`: 백그라운드 호출 (`run_in_background: true`). 입력: 동일. 출력: `<대상 스킬 디렉토리>/wip/skill-verify-agent.md` (진입 조건 미충족 시 "해당 없음" 만 기록)

각 에이전트는 자체적으로 자신이 담당하는 `checks/<항목>-check.md` 를 Read 해서 절차를 수행하고, 결과를 자체 Write 로 wip 파일에 저장한 뒤 짧은 완료 통지를 메인에 반환한다.

### 3단계 -- 동작 검증 (2단계와 병렬 진행)

메인 Claude 가 직접 수행한다. Read 툴로 실제 로드 흐름을 시뮬레이션해야 하므로 에이전트로 위임하지 않는다.

2단계 백그라운드 호출을 시작한 직후 바로 진입한다. 3단계 검증 항목은 2단계 결과에 의존하지 않으므로 5개 에이전트 통지를 기다리지 않는다.

TaskCreate 로 "3단계: 동작 검증" task 를 등록하고 in_progress 로 설정한다. wip 파일 저장이 끝나면 completed 로 닫는다.

`skills/skill-verify/checks/behavior-check.md` 를 Read 툴로 로드해서 검증을 실행한다.

검증 결과는 메인이 Write 툴로 `<대상 스킬 디렉토리>/wip/skill-verify-behavior.md` 에 저장한다.

---

## 결과 취합

3단계가 끝나고 2단계 백그라운드 호출 5개의 완료 통지가 모두 도착한 시점에 결과 취합을 시작한다.

일부만 도착한 시점에 보고서를 작성하면 결과가 불완전해진다.

<FORBIDDEN>
5개 백그라운드 통지가 모두 도착하기 전에 결과 취합을 시작하지 않는다.
</FORBIDDEN>

TaskCreate 로 "결과 취합 및 보고서 저장" task 를 등록하고 in_progress 로 설정한다. 보고서 저장이 완료되면 completed 로 닫는다.

각 단계의 검증 결과를 취합해 두 가지를 처리한다.

### 결과 수집

메인이 `<대상 스킬 디렉토리>/wip/` 아래 파일들을 Read 툴로 모두 로드해 보고서 입력으로 사용한다.

- `wip/skill-verify-structure.md` (1단계 결과)
- `wip/skill-verify-frontmatter.md` (2단계 결과)
- `wip/skill-verify-description.md` (2단계 결과)
- `wip/skill-verify-tag.md` (2단계 결과)
- `wip/skill-verify-format.md` (2단계 결과)
- `wip/skill-verify-agent.md` (2단계 결과, "해당 없음" 가능)
- `wip/skill-verify-behavior.md` (3단계 결과)

1단계 게이트 실패로 중단된 경우 2·3단계 결과 파일은 존재하지 않을 수 있다. 그 때는 1단계 결과만 보고서에 반영한다.

게이트 실패가 아닌데 파일이 없으면 그 항목을 "검증 실패 -- 결과 파일 미생성"으로 표시하고, 해당 에이전트가 완료 통지를 보냈는지와 wip 경로를 보고서에 함께 적는다. 통지는 왔는데 파일이 없으면 Write 거부가 원인이다.

<FORBIDDEN>
wip 결과 파일이 없는 항목을 통과로 적지 않는다.
</FORBIDDEN>

### 대화창 요약

항목별 통과/실패를 판단해 대화창에 표시한다.

| 항목              | 결과                |
|-------------------|---------------------|
| 구조 검증         | 통과/실패           |
| 프론트매터 검증   | 통과/실패           |
| Description 검증  | 통과/실패           |
| 금지 규칙 태그    | 통과/실패           |
| 형식·언어 검증    | 통과/실패           |
| 에이전트 검증     | 통과/실패/해당 없음 |
| 동작 검증         | 통과/실패           |

최종: 통과/실패  |  상세 보고서: `<저장 경로>`

### 보고서 파일 저장

각 검증 출력을 그대로 섹션에 삽입하고 하단에 최종 판정을 추가해 저장한다.

저장 경로: `<프로젝트 루트>/.claude/verify/<대상스킬명>/result.md` (`<프로젝트 루트>` 는 출력 규칙 섹션의 보고서 저장 위치 기준을 따른다)

같은 경로에 이전 보고서가 이미 존재하면 메인이 Bash 로 먼저 삭제한 뒤(`rm -f`) 새 보고서를 Write 로 작성한다. 이전 내용 잔존을 막고, Write 가 Read 선행을 요구하는 상황을 피하기 위함이다.

```markdown
# 스킬 검증 결과

**대상:** `skills/<스킬명>/SKILL.md`
**검증 일시:** YYYY-MM-DD HH:MM

---

## 구조 검증

(wip/skill-verify-structure.md 내용 그대로)

---

## 프론트매터 검증

(skill-verify-frontmatter 에이전트가 저장한 wip 파일 내용 그대로)

---

## Description 검증

(skill-verify-description 에이전트가 저장한 wip 파일 내용 그대로)

---

## 금지 규칙 태그 검증

(skill-verify-tag 에이전트가 저장한 wip 파일 내용 그대로)

---

## 형식·언어 검증

(skill-verify-format 에이전트가 저장한 wip 파일 내용 그대로)

---

## 에이전트 검증

(skill-verify-agent 에이전트가 저장한 wip 파일 내용 그대로, 해당 없음이면 그 사실만 기재)

---

## 동작 검증

(wip/skill-verify-behavior.md 내용 그대로)

---

**최종 판정: 통과/실패**
```

저장 완료 후 대화창 요약 아래에 저장 경로를 알린다.

### wip 디렉토리 정리

보고서 저장이 끝나면 메인이 Bash 로 `<대상 스킬 디렉토리>/wip/` 디렉토리를 삭제한다 (`rm -rf <대상 스킬 디렉토리>/wip/`). 남겨 두면 다음 검증의 입력과 섞이거나 잔여 파일이 결과로 오해된다.
