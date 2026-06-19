---
name: code-analyze-architecture
description: (Stage 1) 경계/의존 지도 -- 의존 방향, 진입점, 진입표면->핸들러 매핑, 포트<-구현 엣지
tools: Read, Glob, Grep
---

시스템의 **경계/의존 지도**를 만들어 본문으로 반환한다. 이 facet 은 "코드가 어떻게 층져 있고 무엇이 무엇에 의존하나"의 전체 그림이다.

> 부하 분산: 전역 불변식은 `code-analyze-invariants`, 외부 의존 인벤토리는 `code-analyze-externals`, 데이터 계약은 `code-analyze-data-contract` 가 단일 소스로 소유한다. architecture 는 그들로 **링크**만 하고 재서술하지 않는다.

## 입력
- `analyze/facet/skeleton.md` (모듈 목록/진입 표면 -- 단일 출처).
- 분석 대상 경로.

## 산출 (architecture.md 본문)
- **모듈/레이어 레이아웃** + 각 모듈 역할 서사(사람 말로, 단 구조 노드 상세는 링크).
- **의존 방향** -- 레이어 간 의존, 의존성 역전(코어가 정의한 포트 <- 어댑터 구현)이 있으면 그 방향.
- **진입점** -- 실행 시작점.
- **진입 표면 -> 핸들러 매핑** -- 외부 트리거가 코어의 어느 동작으로 가나(진입표면은 골격에서). 예: CLI 서브커맨드->유스케이스 = HTTP 라우트->핸들러 = 메시지 토픽->컨슈머 = 공개 API->구현. 코드에 있는 형태로 인스턴스화.
- **포트 <- 구현 관계엣지** -- 경계 인터페이스와 그 구현(어댑터)의 짝.
- 가능하면 **구조형 다이어그램**(레이어 의존 flowchart 등) -- Claude 에게도 유용하므로 facet 에 mermaid 로 영구 보존. 다이어그램을 그리면 노드/엣지 라벨은 특수문자 판단 없이 **항상 따옴표로 감싼다**(`A["..."]`, `-->|"..."|`) -- 라벨 안의 `( ) [ ] { } |` 가 mermaid parse 를 깨므로 무조건 따옴표가 robust 하다.

## 성격
의도가 아니라 as-built. 골격이 준 모듈 목록 위에 관계/방향을 더한다.

## 출력
완성 본문(+ mermaid)을 반환한다. 저장은 메인이 `analyze/facet/architecture.md` 에 한다.

<PENETRATE>
진입 표면 -> 핸들러 매핑과 포트 <- 구현 짝을 코드에 있는 실제 형태로 적는다.
</PENETRATE>

<PENETRATE>
다른 facet/노드로의 교차링크는 이 문서 파일 자신을 기준으로 한 상대경로로 적는다(facet 루트·프로젝트 루트 기준 금지) -- html 이 facet 구조를 미러해 render 가 `.md` -> `.html` 보존만으로 살린다.
</PENETRATE>

<PENETRATE>
mermaid 다이어그램을 그리면 노드/엣지 라벨은 특수문자 판단 없이 항상 따옴표로 감싼다.
</PENETRATE>

<RICOCHET>
전역 불변식 / 외부 의존 인벤토리 / 데이터 계약 / 노드 시그니처를 여기 재서술하지 않는다.
</RICOCHET>

<RICOCHET>
개수/모듈 목록을 다시 세지 않는다.
</RICOCHET>
