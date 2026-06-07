# code-analyze

코드를 분석해 **as-built 코드 지도**(실제로 짜인 구조)를 만들고, 청중별 산출물(Claude 용 facet 파일 / 사람용 인터랙티브 HTML / as-built 마크다운 문서)을 생성하는 독립 스킬.

---

## 정체성

- 독립 슬래시 스킬(`/code-analyze`). 명시 호출로만 발동한다.
- 체인 독립: 입력은 **코드 자체**(소스 트리)이며, 앞 단계 산출물(handoff)에 의존하지 않는다. 게이트는 "분석할 코드가 존재" 뿐이다.
- 분석은 한 번만 돌고, 그 결과(공유 facet 집합)에서 모든 산출물을 렌더한다. 산출물마다 코드를 다시 분석하지 않는다.

---

## 출력 구조

분석 대상 프로젝트의 최상위에 `analyze/` 를 만들고 종류별 하위 디렉토리에 저장한다.

```
<프로젝트 루트>/
  analyze/
    facet/       facet 파일들 + index (Claude 층)
    html/        인터랙티브 HTML (사람, Mermaid)
    markdown/    as-built 마크다운 문서 (사람, 위키/명세)
    .tmp/        렌더 중간 산출물(예: flow.diagram.md). 렌더 후 삭제
```

생성만 한다. 커밋 / 이동(특히 HTML 을 GitHub Pages 디렉토리로) / 푸시는 사용자가 결과를 보고 직접 한다.

<PENETRATE>
산출물은 분석 대상 프로젝트 루트의 `analyze/` 아래 종류별 디렉토리에 저장한다.
</PENETRATE>

<RICOCHET>
스킬이 직접 커밋 / 푸시하거나 GitHub Pages 디렉토리에 파일을 밀어넣지 않는다. 게시는 사용자 몫이다.
</RICOCHET>

---

## 하위 스킬 (에이전트)

에이전트 정의는 플러그인 루트 `agents/` 에 있고, 플러그인 시스템이 자동 발견해 Task 의 `subagent_type` (bare 이름)으로 호출된다.

### 분석 에이전트 (facet 별)

| facet | 에이전트 | 역할 | 산출 형식 |
|------|----------|------|----------|
| 1 아키텍처/의존 | `code-analyze-architecture` | 모듈/디렉토리 레이아웃, 의존성 방향, 진입점 | 다이어그램 가능 |
| 2 타입/관계 | `code-analyze-types` | 구조체/클래스/인터페이스 + 멤버 + 상속/구현 | 다이어그램 가능 |
| 3 플로우 | `code-analyze-flow` | 주요 시나리오의 호출/데이터 흐름 | 산문(facet) + 시퀀스(임시) 분리 |
| 4 외부의존 | `code-analyze-externals` | 사용 라이브러리/패키지 + 사용 위치 | 텍스트 |
| 5 로직요약 | `code-analyze-summary` | 모듈별 동작을 사람 말로 서술 | 텍스트 |

플로우(facet 3)만 예외다. 시퀀스 다이어그램은 Claude 층에 무거우므로 facet 에는 산문만 영구 저장하고, 시퀀스 다이어그램은 임시 파일(`analyze/.tmp/flow.diagram.md`)로 빼서 렌더에만 쓰고 렌더 후 삭제한다. 구조형 다이어그램(아키텍처/타입/외부)은 Claude 에게도 유용하므로 facet 에 그대로 영구 보존한다.

### 렌더 에이전트

| 에이전트 | 역할 | 입력 | 출력 |
|----------|------|------|------|
| `code-analyze-render-html` | facet + 임시 시퀀스 -> 단일 인터랙티브 HTML (Mermaid) | `analyze/facet/` + `analyze/.tmp/flow.diagram.md` | `analyze/html/` |
| `code-analyze-render-markdown` | facet + 임시 시퀀스 -> as-built 마크다운 문서 | `analyze/facet/` + `analyze/.tmp/flow.diagram.md` | `analyze/markdown/` |

### 검증 에이전트

| 에이전트 | 역할 | 입력 | 출력 |
|----------|------|------|------|
| `code-analyze-verify` | 렌더 HTML 의 mermaid 문법/렌더 깨짐 검증 | `analyze/html/index.html` | 리포트 본문 반환 |

impact(변경 영향도)는 별도 에이전트/산출물로 두지 않는다. 생성된 facet 지도를 읽어 on-demand 로 추론한다 -- 변경 대상의 직접/간접 호출자, 공개 노출 지점(API/CLI/export), 관련 테스트를 architecture/flow facet 에서 짚어 영향 범위를 파악한다.

---

## 실행 순서

### 사전 준비

1. 분석 대상 경로를 정한다(대화 맥락에서 결정, 모호하면 사용자에게 질문). 결정된 경로를 모든 에이전트 입력으로 전달한다.
2. 메인이 Bash 로 `<프로젝트 루트>/analyze/{facet,html,markdown,.tmp}/` 를 생성한다(`mkdir -p`).

### Phase 1 -- 분석 (병렬)

분석 에이전트(facet 1-5)를 한 응답에서 Task 로 **병렬 호출**한다. 각 에이전트는 facet 결과 본문을 반환하고, 메인이 받아 `analyze/facet/<facet>.md` 로 저장한다.

플로우(facet 3)는 산문과 시퀀스 다이어그램을 `%%FLOW-DIAGRAMS%%` 구분자로 나눠 반환한다. 메인은 구분자 위(산문)를 `analyze/facet/flow.md` 로, 아래(시퀀스 다이어그램)를 `analyze/.tmp/flow.diagram.md` 로 나눠 저장한다.

<PENETRATE>
facet 분석 에이전트들은 한 응답 안에서 병렬로 호출한다.
</PENETRATE>

<RICOCHET>
에이전트가 facet 결과를 직접 파일로 저장하게 하지 않는다. 본문을 반환하고 메인이 저장한다.
</RICOCHET>

### Phase 2 -- 인덱스 합성 (메인)

메인이 저장된 facet 파일들을 보고 얇은 **인덱스**(`analyze/facet/index.md`)를 만든다. 인덱스는 진입점/목차 + 어느 facet 에 무엇이 있는지의 오리엔트만 담는다(facet 내용을 재서술하지 않는다).

### Phase 3 -- 렌더 (병렬)

facet 집합 + 인덱스 + 임시 시퀀스 파일이 준비되면 렌더 에이전트 2개를 Task 로 **병렬 호출**한다. 입력으로 `analyze/facet/` 와 `analyze/.tmp/flow.diagram.md` 경로를 함께 전달한다. 각 에이전트는 렌더 결과 본문을 반환하고, 메인이 `analyze/html/`, `analyze/markdown/` 에 저장한다.

저장이 끝나면 메인이 `analyze/.tmp/` 를 삭제한다. 임시 시퀀스 파일은 렌더 산출물에 이미 복사돼 들어갔으므로 더 보관하지 않는다.

<RICOCHET>
임시 시퀀스 파일을 영구 보존하거나 최종 산출물에서 링크로 참조하지 않는다. 렌더 후 삭제한다.
</RICOCHET>

### Phase 4 -- 검증 (메인 -> 에이전트)

렌더가 끝나면 메인이 `code-analyze-verify` 를 Task 로 호출한다. 입력은 저장된 HTML 경로(`analyze/html/index.html`). 검증 리포트를 받아, 깨진 다이어그램이 있으면 사용자에게 보고한다. 검증 도구가 없어 스킵된 경우에도 그 사실을 안내한다.

### 결과 안내

생성된 파일 목록과 경로, 검증 결과 요약을 안내한다. HTML 을 Pages 로 옮기거나 커밋하려면 사용자가 직접 한다고 알린다.

---

## 결과 처리 규약

- 작업(분석/렌더)은 에이전트에 위임하고, 파일 저장은 메인이 한다.
- 에이전트 반환 본문에 `&`/`<`/`>` 가 HTML 엔티티로 이스케이프됐으면 저장 전 원복한다.

<PENETRATE>
분석/렌더 작업은 에이전트에 위임하고, 결과 파일 저장은 메인이 수행한다.
</PENETRATE>
