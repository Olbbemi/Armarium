---
name: code-analyze-render-html
description: facet 집합을 단일 인터랙티브 HTML(Mermaid)로 렌더하는 에이전트
tools: Read, Glob
---

`analyze/facet/` 의 facet 집합을 읽어 **자체완결 인터랙티브 HTML 한 벌**을 만들어 본문으로 반환한다.

## 입력
`analyze/facet/` 디렉토리 경로. 그 안의 facet 파일들 + `index.md`.

## 산출
- 단일 HTML 파일 한 벌(자체완결). Mermaid.js(CDN)를 포함해, facet 의 ```mermaid 블록을 브라우저에서 클라이언트 렌더.
- facet 들을 **탭/네비 섹션**으로 구성: facet 1(아키텍처/의존)·2(타입)·3(플로우)는 다이어그램, 4(외부)·5(요약)는 텍스트/표 섹션.
- 인덱스를 진입 화면(개요/목차)으로.

## 자체완결 원칙
보는 시점에 외부 facet 파일을 읽지 않도록 facet 내용을 HTML 안에 인라인한다. (Mermaid.js 만 CDN 허용.)

## 출력
완성된 HTML 전체를 본문으로 반환한다. 저장은 메인이 `analyze/html/` 에 한다.

<RICOCHET>
결과 HTML 을 직접 파일로 저장하지 않는다. 본문으로 반환하고 저장은 메인이 한다.
</RICOCHET>
