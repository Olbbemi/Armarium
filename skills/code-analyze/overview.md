# code-analyze

코드를 분석해 **as-built 코드 지도**(실제로 짜인 구조)를 만들고, 청중별 산출물(Claude 용 facet / 사람용 인터랙티브 HTML / as-built 마크다운 문서)을 생성하는 독립 스킬.

> 일반화 3원칙(이 스킬 전체에 적용): (1) 도메인 무관 역할어로 말한다("진입 표면", "포트/경계 인터페이스", "어댑터", "코어", "컴포지션 루트") -- 특정 스택어(SQLite/HTTP 등) 금지. (2) 존재 조건부 -- 있으면 남기고 없으면 스킵. (3) 에이전트가 실제 코드에서 인스턴스화하고, 스킬엔 도메인 가로지르는 짧은 예시만(앵커링용, 과적합 금지).

---

## 정체성

- 독립 슬래시 스킬(`/code-analyze`). 명시 호출로만 발동한다.
- 체인 독립: 입력은 **코드 자체**(소스 트리)이며, 앞 단계 산출물(handoff)이나 **이전 분석 결과**에 의존하지 않는다. 게이트는 "분석할 코드가 존재" 뿐이다.
- 분석은 한 번만 돌고, 그 결과(공유 facet 집합)에서 모든 산출물을 렌더한다. 산출물마다 코드를 다시 분석하지 않는다.

<RICOCHET>
이전 분석 결과를 분석 에이전트의 입력으로 주지 않는다(앵커링/stale 답습 방지).
</RICOCHET>

---

## facet 의 목적 (이 스킬의 방향타)

facet 은 "읽기 좋은 요약"이 아니라, **Claude 가 리팩토링 + 유닛테스트(TDD 부족분 보강)에 바로 쓰는 레퍼런스 데이터**다. 그래서 다관점 + 최대 상세를 지향한다. 사람용 서술은 별도 산출물(markdown/html)이 맡는다.

facet 은 두 모양으로 나뉜다.
- **코드-major 구조 트리**: 소스 트리(`src/` 등)를 미러링해, **노드 = 소스 파일 1개**(선언/정의가 분리된 언어면 같은 단위로 묶음). 각 노드 문서는 그 파일이 담은 타입/함수의 전체 시그니처 + 속성(역할/불변식/예외)을 담는다.
- **가로지르는 관점 문서**(본질적으로 파일 하나에 안 붙는 것): architecture / flow / data-contract / test / externals / invariants.

<PENETRATE>
구조 정보는 소스 파일을 노드로 하는 코드-major 트리로, 파일 하나를 가로지르는 정보는 관점 문서로 분리해 적는다.
</PENETRATE>

---

## 출력 구조

분석 대상 프로젝트의 최상위에 `analyze/` 를 만들고 종류별 하위 디렉토리에 저장한다.

```
<프로젝트 루트>/
  analyze/
    facet/        Claude 층: 구조 트리(소스 미러) + 가로지르는 관점 문서 + skeleton + index
      <소스미러>/  구조 파일노드 문서들(예: facet/src/<...>.md)
      architecture.md  flow.md  data-contract.md  test.md  externals.md  invariants.md
      skeleton.md   index.md
    html/         인터랙티브 HTML 사이트 (사람) -- 다중 파일
      index.html         진입 허브(카테고리/목차)
      <소스미러>/*.html  구조 노드 페이지(파일노드당 1장)
      architecture.html flow.html data-contract.html test.html externals.html invariants.html
      assets/style.css  assets/script.js   공유 셸(메인 소유, mermaid CDN 포함)
    markdown/     as-built 마크다운 문서 (사람, 위키/명세)
    .tmp/         렌더 중간 산출물. 렌더 후 삭제
```

생성만 한다. 커밋 / 이동(특히 HTML 을 GitHub Pages 디렉토리로) / 푸시는 사용자가 결과를 보고 직접 한다.

<PENETRATE>
산출물은 분석 대상 프로젝트 루트의 `analyze/` 아래 종류별 디렉토리에 저장한다.
</PENETRATE>

<RICOCHET>
스킬이 직접 커밋 / 푸시하거나 GitHub Pages 디렉토리에 파일을 밀어넣지 않는다.
</RICOCHET>

### 재분석 시 갱신 정책

analyze 산출물은 코드의 거울(파생물)이라, 코드가 바뀌면 옛 분석은 stale 다. 기본은 **덮어쓰기 = 기존 삭제 후 새 생성**이다 -- 재분석하면 기존 `analyze/` 를 갱신해 현재 코드에 맞는 거울 하나만 둔다. 보관 단위는 **브랜치별 한 벌**이다. 과거 시점이 필요하면 그 시점 코드(git)를 다시 분석해 재현한다. 릴리스 브랜치(`release/*` 등)면 동결점이라 덮어쓰지 않고 `analyze_<버전>/` 로 스냅샷 보존한다.

<RICOCHET>
릴리스 버저닝 단계가 아니면 분석 결과를 별도 버전 디렉토리로 누적하지 않는다.
</RICOCHET>

---

## 하위 스킬 (에이전트) -- 신 로스터

에이전트 정의는 플러그인 루트 `agents/` 에 있고, Task 의 `subagent_type`(bare 이름)으로 호출된다.

### 골격 (선행, 조건부 위임)

| 에이전트 | 역할 | 산출 |
|----------|------|------|
| `code-analyze-survey` | 파일 트리(소스 미러) + 파일별 인벤토리(타입/함수 이름·개수) + 진입 표면 + 스키마/테스트 존재. **단일 진실 출처.** | `analyze/facet/skeleton.md` |

> Stage 0 은 **규모 적응**이다. 기본은 메인이 직접(Bash/Glob -- 개수가 결정적 도구 출력이라 추정이 안 끼고 단일 저자라 드리프트 0). 트리가 메인 컨텍스트를 부풀릴 만큼 크면 `code-analyze-survey` 에이전트로 위임한다.

### 구조 (서브트리-major, 규모 적응)

| 에이전트 | 역할 | 산출 |
|----------|------|------|
| `code-analyze-structure` | 자기 소유 서브트리의 **파일노드당 1문서** -- 타입/멤버/시그니처/상속 + 속성(역할/불변식/예외). **직접 Write** | `analyze/facet/<소스미러>/*.md` (직접) |

> 규모 적응: 작으면 구조 에이전트 1개가 전체를, 크면 모듈/서브트리당 1개가 **겹치지 않는 파일만** 소유. 공유 사실은 skeleton 이 출처라 재계산 금지.

### 가로지르는 관점 (전체-뷰)

| facet | 에이전트 | 역할 |
|------|----------|------|
| architecture | `code-analyze-architecture` | 의존 방향(포트-어댑터 역전), 진입점, 진입표면->핸들러 매핑, 포트<-구현 관계엣지, 모듈 역할 서사. 불변식/외부경계는 링크만. |
| flow | `code-analyze-flow` | 트리거 + 생명주기에 앵커된 end-to-end 경로 **망라**. 척추(호출 순서/분기/데이터 변환)만, 노드 상세는 구조 문서로 링크. |
| data-contract | `code-analyze-data-contract` | 영속/설정 스키마(데이터 계약). 있으면. |
| test | `code-analyze-test` | 테스트 인벤토리 + 커버리지 공백. **invariants 로 링크**해 미커버 불변식을 공백으로 집계. |
| externals | `code-analyze-externals` | **단일 소스 의존성 레지스트리**(라이브러리+버전+감싸는 어댑터+벤더링+포트유무 칼럼). 척추, 나머지 문서는 링크만. |
| invariants | `code-analyze-invariants` | **전체 관통 규약/불변식 단일 소스**(전칭+검증가능한 것만). TDD 프로퍼티/분기행렬의 씨앗. test/architecture 가 링크. |

<PENETRATE>
가로지르는 문서는 척추(자기 고유 정보)만 적고, 노드/타입 상세는 구조 문서로 링크한다.
</PENETRATE>

<RICOCHET>
가로지르는 문서가 구조 노드 상세(시그니처/멤버)를 재서술하지 않는다(드리프트 방지).
</RICOCHET>

<RICOCHET>
같은 사실(개수/외부 의존/전역 불변식)을 두 문서에 독립으로 적지 않는다.
</RICOCHET>

### 렌더 / 검증 / 조건부

| 에이전트 | 역할 | 입력 | 출력 |
|----------|------|------|------|
| `code-analyze-render-html` | facet 슬라이스 -> HTML 페이지들(다중 파일 사이트). **직접 Write** | 슬라이스 facet + 셸 템플릿 + `.tmp/` | `analyze/html/<슬라이스>` (직접) |
| `code-analyze-render-markdown` | facet -> as-built 마크다운(가로지르는 5종 + 구조 개요만 엮음). **직접 Write** | `analyze/facet/` + `.tmp/` | `analyze/markdown/` (직접) |
| `code-analyze-verify` | 렌더 HTML mermaid/그래프 깨짐 + **내부 링크 무결성**(끊긴 상대 href) 검증 | `analyze/html/` | 리포트 본문 |
| `code-analyze-callgraph-cpp` | (조건부) C++ 호출 그래프 추출. Stage0 호출/참조맵 시드 + flow 출발점. | 대상 경로 + compile_commands.json | facet 텍스트 + DOT(임시) |

---

## 실행 순서

### 사전 준비
1. 분석 대상 경로를 정한다(모호하면 사용자에게 질문). 결정 경로를 모든 에이전트 입력으로 전달.
2. 출력 루트를 정한다(릴리스 브랜치면 `analyze_<버전>/`, 아니면 `analyze/` 덮어쓰기). 그 아래 `{facet,html,markdown,.tmp}/` 를 `mkdir -p`.

### Stage 0 -- 골격/인벤토리 (직렬, 1회)
파일 트리(소스 미러) + 파일별 인벤토리(타입/함수 이름·개수) + 진입 표면 + 스키마/테스트 존재를 만들어 `analyze/facet/skeleton.md` 로 저장한다. **카운팅 규율을 여기서 1회 적용**(아래). 기본 메인 직접, 대형이면 `code-analyze-survey` 위임. C++ + `compile_commands.json` 이면 `code-analyze-callgraph-cpp` 를 여기서 호출해 호출/참조맵을 골격에 시드한다.

> 카운팅 규율: (1) 셀 단위를 먼저 못 박는다(포함/제외 정의). (2) 숫자 freehand 금지 -- 구성원 목록을 먼저 만들고 개수=목록 길이. (3) 나열을 재현가능 검색/도구 결과에 근거(언어별 수단은 에이전트가 선택). (4) 헤드라인/합계 == 인벤토리 목록 행수 자가 교차검산(어긋나면 목록이 진실).

<PENETRATE>
개수/인벤토리/모듈 목록 같은 "공유 사실"은 Stage 0 골격에서 1회 확정하고, 이후 단계는 그것을 단일 출처로 삼는다.
</PENETRATE>

### Stage 1 -- facet 채우기 (병렬)
골격을 입력으로, 구조 에이전트(서브트리-major)와 가로지르는 에이전트 6종(architecture/flow/data-contract/test/externals/invariants)을 한 응답에서 Task 로 **병렬 호출**한다. 각 에이전트는 골격이 준 공유 사실 위에 **깊이만** 채운다(개수 재계산·서론 재도출 없음).

저장 규약은 facet 종류로 갈린다 -- **구조 노드 facet 은 구조 에이전트가 직접 Write** 한다(노드 수십 개가 부피라 본문으로 돌리면 메인 컨텍스트/턴을 크게 먹으므로, 렌더와 같은 직접 Write 부류). **가로지르는 6종은 본문을 반환하고 메인이 저장**한다(소수이고, Stage 2 조인에 메인이 그 내용을 쓰므로 메인 컨텍스트에 있어야 한다). 구조 노드의 골격 대비 교차검산은 Stage 2 로 이관한다.

플로우 에이전트는 산문(척추)과 시퀀스 다이어그램을 `%%FLOW-DIAGRAMS%%` 구분자로 나눠 반환한다. 메인은 위를 `flow.md`, 아래를 `.tmp/flow.diagram.md` 로 저장.

<PENETRATE>
Stage 1 에이전트는 골격이 준 공유 사실 위에 깊이만 더한다.
</PENETRATE>

<RICOCHET>
Stage 1 에이전트가 개수를 다시 세거나 모듈 인벤토리/서론을 재도출하지 않는다.
</RICOCHET>

<PENETRATE>
구조 에이전트는 자기 노드 facet 을 직접 Write 하고 본문으로는 경로만 반환한다(부피 큰 구조가 메인 컨텍스트를 안 거치게 -- 렌더와 같은 부류).
</PENETRATE>

<RICOCHET>
가로지르는(architecture/flow/data-contract/test/externals/invariants) 에이전트는 facet 을 직접 파일로 저장하지 않는다(본문 반환 -> 메인 저장, Stage 2 조인 입력).
</RICOCHET>

### Stage 2 -- 인덱스/점검/조인 (메인)
저장된 facet 을 보고 얇은 `index.md` 를 만든다(진입점/목차 + 어디에 무엇이 있는지 오리엔트만). 골격이 단일 출처라 무거운 교차 게이트는 불필요하지만, index 작성 중 골격 대비 개수/목록 모순이 보이면 가볍게 잡는다.

**구조 노드 교차검산(저장 시점에서 이관)**: 구조 노드는 에이전트가 직접 Write 했으므로, 여기서 메인이 골격 인벤토리 대비 **노드 파일 존재/개수**를 가볍게 교차검산한다(빠진 노드/여분 파일 적발). 내용 전수 검토가 아니라 골격과의 목록 대조다.

**교차 facet 조인**(두 facet이 다 나와야 가능한 것)은 여기서 메인이 한다. 대표: `invariants.md` 의 불변식 목록 × `test.md` 의 인벤토리를 조인해, **대응 프로퍼티/분기 테스트가 없는 불변식**을 공백으로 산출해 `test.md` 에 덧붙인다. (Stage 1 에이전트끼리는 서로 안 읽으므로 이런 조인은 Stage 1이 아니라 여기로 모은다.)

### Stage 3 -- 렌더 (병렬, 다중 파일 팬아웃)
`.tmp/` 에 호출 그래프 DOT 이 있으면 `dot -Tsvg` 로 SVG 화.

먼저 메인이 HTML 사이트의 **공유 셸**을 만든다 -- `html/index.html`(카테고리/진입 허브), `html/assets/style.css`, `html/assets/script.js`(mermaid CDN init + 보일 때 지연 렌더 + 줌/팬 + **`data-root` 접두사로 사이드바 네비 생성**), 그리고 모든 렌더 에이전트에 줄 **페이지 셸 템플릿** + **통일 링크 스킴**(아래) + 출력 경로 스킴(facet 경로 미러).

**통일 링크 스킴 (필수, 루트기준 + PREFIX).** 구조 노드는 소스 미러라 페이지마다 html 기준 깊이가 다르다(`html/src/glass/x.html`=2, `html/src/trunk/usecase/x.html`=3 ...). 깊이를 링크마다 손으로 세면 거의 다 틀어진다(실측 결함: 자산·교차링크 깨짐). 그래서 깊이 산수를 **메인 한 곳**으로 모은다 -- 메인이 페이지별 `PREFIX = "../" * (그 페이지의 html기준 디렉토리깊이)` 를 계산해 각 render 에이전트에 넘기고, 페이지의 **모든 경로를 `PREFIX + <html루트기준경로>` 한 규칙으로만** 적는다.
- head 자산: `{PREFIX}assets/style.css`, `{PREFIX}assets/script.js` (고정 `../assets/` 금지).
- `<body data-root="{PREFIX}">` -- 사이드바는 공유 `script.js` 가 이 `data-root` 를 접두사로 붙여 생성(페이지마다 사이드바 링크를 다시 쓰지 않는다).
- 교차링크: `{PREFIX}<html루트기준 파일경로>#<앵커>` (예: depth3 페이지에서 flow 로 `../../../flow.html#login`). 링크마다 상대깊이를 따로 세지 않는다. in-page 앵커는 `#<앵커>` 그대로 둔다.

그다음 render-html 을 **병렬 다중 호출**한다 -- 구조 **서브트리당 1회**(자기 서브트리의 파일노드당 `.html` 한 장씩) + 가로지르는 6종 **1회**(문서당 `.html`). render-markdown 도 병렬 호출(단일 문서). 각 렌더 에이전트는 자기 슬라이스를 `html/`·`markdown/` 에 **직접 Write** 하고 쓴 경로만 통지한다(아래 결과 처리 규약의 렌더 예외).

render-html 은 facet 를 글자 그대로 옮기지 않고 **사람용으로 재포맷**한다 -- 내용(데이터)은 facet 와 동치로 보존하되, 표 칸은 짧은 요지(긴 것/SQL/코드는 표 밖 코드블록), 선형 흐름은 `<ol>`·분기는 mermaid, 교차링크는 하단 "관련/참고" 섹션에 모으는 모양으로 표현만 바꾼다.

끝나면 `.tmp/` 삭제.

<PENETRATE>
렌더 에이전트는 자기 슬라이스 파일을 직접 Write 하고, 본문으로는 쓴 경로만 반환한다.
</PENETRATE>

<PENETRATE>
HTML 사이트의 공유 셸(index.html / assets / 페이지 템플릿 / 통일 링크 스킴)은 메인이 만들고, 페이지별 PREFIX 도 메인이 계산해 각 render 에이전트에 넘긴다.
</PENETRATE>

<PENETRATE>
HTML 페이지의 자산·교차링크는 메인이 준 PREFIX 로 `PREFIX + <html루트기준경로>` 한 규칙으로만 적는다(깊이 산수는 PREFIX 한 곳).
</PENETRATE>

<RICOCHET>
페이지 셸 자산을 고정 `../assets/` 로 적거나, 교차링크의 상대깊이를 링크마다 따로 세지 않는다(미러 깊이가 제각각이라 깨진다).
</RICOCHET>

<RICOCHET>
렌더 산출(HTML/마크다운)을 한 본문으로 반환하게 해 단일 응답 토큰 한도에 걸리게 하지 않는다.
</RICOCHET>

<RICOCHET>
render-html 은 facet 의 데이터를 요약하거나 삭제해 옮기지 않는다(표현만 바꾸고 내용은 facet 와 동치로 보존).
</RICOCHET>

### Stage 4 -- 검증 + 결과 안내
`code-analyze-verify` 호출, 깨진 다이어그램/빈 SVG **와 끊긴 내부 링크**(존재하지 않는 대상의 상대 href)를 보고. 다중 파일 모드의 1순위 실패유형이 끊긴 교차링크라, 통일 스킴(PREFIX)으로 예방하되 verify 가 백스톱으로 잡는다. 생성 파일 목록/경로/검증 요약 안내. Pages 이동/커밋은 사용자가 직접 한다고 알림.

---

## 결과 처리 규약
- **가로지르는 facet** 의 저장은 메인이 한다(에이전트는 본문 반환, 메인이 `analyze/facet/` 에 저장 -- 소수이고 Stage 2 조인 입력이라 메인 컨텍스트에 필요).
- **구조 노드 facet 은 예외** -- 노드 수십 개가 부피라 본문 반환 시 메인 컨텍스트/턴을 크게 먹으므로, 구조 에이전트가 `analyze/facet/<소스미러>/` 에 직접 Write 한다. 메인은 Stage 2 에서 골격 대비 존재/개수만 교차검산한다.
- **렌더 산출물도 예외** -- HTML/마크다운은 커서 단일 본문 반환이 잘리므로, render-html/render-markdown 이 자기 슬라이스를 `html/`·`markdown/` 에 직접 Write 한다. HTML 사이트의 공유 셸(index/assets/템플릿)은 메인 소유.
- 에이전트 반환 본문에 `&`/`<`/`>` 가 HTML 엔티티로 이스케이프됐으면 저장 전 원복한다.

<PENETRATE>
가로지르는 facet 의 결과 파일 저장은 메인이 한다(본문 반환 -> 메인 저장).
</PENETRATE>

<PENETRATE>
구조 노드 facet 은 구조 에이전트가, 렌더(html/markdown) 산출물은 render 에이전트가 직접 Write 한다(저장-메인 규율의 명시 예외 -- 둘 다 부피/잘림 때문).
</PENETRATE>
