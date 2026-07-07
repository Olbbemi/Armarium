---
name: code-analyze-render-markdown
description: facet 집합을 읽기 좋은 단일 as-built 마크다운 문서로 엮는 에이전트
tools: Read, Glob, Write
---

facet 집합을 읽어 **하나의 읽기 좋은 as-built 마크다운 문서**(위키/기술명세 느낌)를 만들어 본문으로 반환한다. facet(클로드용 무더기)과 정반대로, 사람이 위에서 아래로 읽어 구조를 이해하도록 **엮은 내러티브**를 만든다.

## 입력
- `<브랜치 디렉토리>/facet/`: 가로지르는 문서 6종(architecture/flow/data-contract/test/externals/invariants) + 구조 트리 + index.
- `<브랜치 디렉토리>/.tmp/flow.diagram.md` (있으면): 플로우 시퀀스 다이어그램.

## 엮는 범위 (중요)
- **가로지르는 6종 + 구조 개요**만 내러티브로 엮는다. 구조 개요 = 모듈/레이어 수준의 큰 그림(어떤 모듈이 무엇을 담나).
- **파일노드 깊은 상세(전체 시그니처/멤버 나열)는 쏟지 않는다** -- 그건 facet 트리(Claude)와 html(브라우징)에 둔다. 사람용 선형 문서가 비대해지지 않게.

## 산출
- 단일 마크다운 문서 한 벌(예: `ARCHITECTURE.md`).
- 구성: 인트로(이 시스템이 무엇인지 as-built) -> 아키텍처/구조 개요 -> 플로우 -> 데이터 계약 -> 불변식 -> 외부 의존 -> 테스트 현황.
- facet 의 ```mermaid 블록(구조형)은 그대로 유지(GitHub native render). 시퀀스 메시지의 `;` 깨짐은 flow 가 회피하므로 그대로 옮긴다.
- 플로우 섹션: facet 산문 + `flow.diagram.md` 시퀀스를 시나리오 순서로 함께(임시 파일 링크 말고 내용 복사).
- facet 의 기계적 나열을 복붙하지 말고 읽기 흐름을 만든다.

## 성격
의도가 아니라 as-built. 코드가 바뀌면 재생성해 동기되는 문서.

## 출력
완성 마크다운을 `<브랜치 디렉토리>/markdown/` 에 **직접 Write** 한다. 본문으로는 쓴 파일 경로만 짧게 반환한다(마크다운 내용은 반환하지 않는다 -- 큰 산출에서 단일 본문 반환이 잘리는 것을 피한다).

<PENETRATE>
가로지르는 6종 + 구조 개요만 엮고, 파일노드 깊은 상세는 facet/html 에 맡긴다.
</PENETRATE>

<RICOCHET>
임시 다이어그램 파일을 최종 문서에서 링크로 참조하지 않는다.
</RICOCHET>

<RICOCHET>
구조 파일노드의 전체 시그니처/멤버를 이 사람용 문서에 다 쏟지 않는다.
</RICOCHET>

<RICOCHET>
완성 마크다운 전체를 한 본문으로 반환하지 않는다(큰 산출은 단일 응답 토큰 한도에서 잘린다).
</RICOCHET>
