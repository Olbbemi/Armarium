# knowledge-promote

캡처 스킬들([`knowledge-capture`](../knowledge-capture/README.md) · [`knowledge-scan`](../knowledge-scan/README.md) · [`knowledge-study`](../knowledge-study/README.md))이 쌓은 wip 초안을 확정지식으로 가공해 전역 지식 저장소에 올리는 스킬.

## 무엇을 하나

wip 산문 한 건을 골라 확정지식 형식(프론트매터 + 정제 본문)으로 변환하고, 관계 추출·일반화·검증·중복 점검을 거쳐 사용자 승인 후 `knowledge/` 에 저장한다.<br>
Herbarium main 에 직접 넣지 않고 `promote/<id>` 브랜치에서 격리해 커밋하며, 푸시·머지는 사용자가 한다.<br>
캡처(wip 누적)와 별개의 독립 스킬이다.

## 언제 쓰나

`/knowledge-promote` 슬래시 명령으로 호출했을 때만 동작한다. 자연어 발화로는 뜨지 않도록 description 을 슬래시 호출로 닫아 두었다.<br>
승급은 사용자가 시점을 고르는 단발 작업이라 자동 호출 대상이 아니다.

## 구조

- `overview.md` -- 진입점. 경로 설정 · 렌더 surface 전제 · 11단계 실행 순서
- `format/format.md` -- 확정지식 형식 규격. 프론트매터 칸 · 본문 표기 규칙 · 코드 지식 구성. 2단계에서만 로드한다
- [`references/herbarium-path.md`](../../references/herbarium-path.md) -- 네 knowledge 스킬 공용 경로 검증

## 경로

wip 폴더와 확정지식 디렉토리는 Herbarium 저장소 하위에 있다.<br>
경로를 코드에 고정하지 않고, 활성 직후 사용자에게 Herbarium 루트를 입력받아 git origin remote 로 검증한 뒤 `<루트>/wip` 와 `<루트>/knowledge` 를 도출한다. 검증 규약은 캡처 스킬 셋과 공유하는 [`references/herbarium-path.md`](../../references/herbarium-path.md) 가 단일 출처다 -- 기대 remote URL 이 그 파일에만 있어, 저장소를 옮겨도 한 곳만 고치면 네 스킬이 함께 따라온다.

## 동작 흐름 (11단계)

1. **대상 선택** — `wip/` 를 Glob 해 목록을 보여주고 사용자가 하나를 고름. 한 번에 하나만. 목록이 비면 승급할 초안이 없는 것이라 여기서 끝냄
2. **형식 변환** — 산문을 프론트매터(kind/id/title/summary/category/tags/relations) + 정제 본문으로. 형식 규격은 `format/format.md` 가 단일 출처다. `kind`(concept/code)가 본문 구성을 가른다 — concept은 핵심·오해·참고 자유 구성, code는 문법·예제·주의점·통념 정정 구성(`language`·`since` 칸 추가). "노트가 답하는 질문"으로 kind 결정(무엇·왜=concept / 어떻게 쓰나=code)
3. **관계 추출** — "관련 개념"을 relations 타입드 엣지로. 종류 4개: `contrasts_with`(반대/경쟁), `same_family`(동료), `part_of`(부분-전체), `related`(그 외). `타입:대상` 문자열 평탄 리스트로 저장
4. **일반화** — 특정 프로젝트에 종속된 부분(이름·언어·규모·결정)을 걷어내고 조건 서술로 다듬음. 캡처 맥락이 `[전제 없음]` 표식이면 걷어낼 게 없다는 신호
5. **검증** — 참고 URL 생존 확인, 조사 보류 목록 fetch·대조·정정, 전체 예제 컴파일·실행 확인, 사실성 의심 항목 표시
6. **중복·충돌 점검** — 기존 확정지식과 summary 비교, 병합/대체/별도를 사용자에게 질의. 고른 갈래가 8단계 대상 파일과 7단계 브랜치명, 10단계 커밋 메시지를 가름 (병합·대체는 기존 id 를 그대로 씀)
7. **브랜치 생성·체크아웃** — Herbarium main 에 직접 저장하지 않고 `promote/<id>` 브랜치를 main 에서 생성·체크아웃해 격리
8. **초안 저장 후 검토·승인** — 7단계 브랜치 위 `knowledge/<id>.md` 에 먼저 저장하고, 그 경로와 검증·중복 이슈를 알려 사용자가 파일을 직접 열어 검토·승인. 승인이 10단계 커밋의 게이트
9. **원본 wip 처리** — 삭제할지 남길지 사용자 확인
10. **커밋** — 저장·원본 처리 결과를 그 브랜치에 커밋. 메시지는 갈래별로 다름(`Promote` / `Merge` / `Replace`). 푸시·머지는 사용자가 함
11. **종료 보고** — 저장 경로와 브랜치명, 원본 wip 처리 결과, 미해결로 남은 이슈를 알리고 끝냄

## 주의

- 관계 정보는 프론트매터 relations가 단일 출처다. 본문에 산문으로 중복하지 않는다.
- 가리키는 id 파일이 아직 없어도 그 관계를 빼지 않는다.
- 초안은 브랜치에 먼저 저장하고 사용자 승인을 받는다. 승인 없이 커밋으로 넘어가지 않는다.
- 사용자 확인 없이 원본 wip를 삭제하지 않는다.

## 다루지 않는 것

- 마크다운 -> SQLite/벡터 빌드, 임베딩, 그래프 시각화 (범위 밖)
- 여러 wip 동시 승급(배치) (범위 밖)
