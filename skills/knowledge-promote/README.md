# knowledge-promote

[`knowledge-capture`](../knowledge-capture/README.md)가 쌓은 wip 초안을 확정지식으로 가공해 전역 지식 저장소에 올리는 스킬.

## 무엇을 하나

wip 산문 한 건을 골라 확정지식 형식(프론트매터 + 정제 본문)으로 변환하고, 관계 추출·일반화·검증·중복 점검을 거쳐 사용자 승인 후 `knowledge/` 에 저장한다. 캡처(wip 누적)와 별개의 독립 스킬이다.

## 언제 쓰나

`/knowledge-promote` 슬래시 명령으로 호출했을 때만 동작한다. "이 wip 승급해줘", "지식으로 확정해줘", "knowledge로 올려줘" 같은 상황. 자가판단으로 시작하지 않는다.

## 경로

- wip 인박스: `/home/olbbemi/Project/Herbarium/wip/`
- 확정지식: `/home/olbbemi/Project/Herbarium/knowledge/`

## 동작 흐름 (8단계)

1. **대상 선택** — 인자(topic/파일명)가 있으면 그 wip, 없으면 `wip/` 목록에서 사용자 선택. 한 번에 하나만
2. **형식 변환** — 산문을 프론트매터(id/title/summary/category/tags/relations) + 정제 본문으로
3. **관계 추출** — "관련 개념"을 relations 타입드 엣지로. 종류 3개: `contrasts_with`(반대/경쟁), `same_family`(동료), `related`(그 외)
4. **일반화** — 특정 프로젝트 색(이름·언어·규모·결정)을 걷어내고 조건 서술로 다듬음
5. **검증** — 참고 URL 생존을 WebFetch로 확인, 사실성 의심 항목 표시
6. **중복·충돌 점검** — 기존 확정지식과 summary 비교, 병합/대체/별도를 사용자에게 질의
7. **사용자 확인 후 저장** — 변환 결과 + 검증·중복 이슈를 제시하고 승인받아 `knowledge/<id>.md` 저장
8. **원본 wip 처리** — 삭제할지 남길지 사용자 확인

## 주의

- 관계 정보는 프론트매터 relations가 단일 출처다. 본문에 산문으로 중복하지 않는다.
- 가리키는 id 파일이 아직 없어도 그 관계를 빼지 않는다.
- 확정지식 저장 전 반드시 사용자 승인을 받는다.
- 사용자 확인 없이 원본 wip를 삭제하지 않는다.

## 다루지 않는 것

- 마크다운 → SQLite/벡터 빌드, 임베딩, 그래프 시각화 (범위 밖)
- 여러 wip 동시 승급(배치) (추후)
