# 지식 승급 (promote)

캡처 스킬들(`knowledge-capture` · `knowledge-scan` · `knowledge-study`)이 쌓은 wip 초안을 확정지식으로 가공해 전역 지식 저장소에 올리는 스킬. 세 스킬 모두 같은 형식의 wip 를 같은 디렉토리에 쌓으므로, 승급은 누가 만들었는지 따지지 않는다.

---

## 활성 조건

사용자가 `/knowledge-promote` 슬래시 명령으로 호출했을 때만 활성된다.

---

## 하위 스킬

| 파일 | 역할 |
|------|------|
| `skills/knowledge-promote/format/format.md` | 확정지식 형식 규격 -- 프론트매터 칸 · 본문 표기 규칙 · 코드 지식 구성 |
| `references/herbarium-path.md` | 네 knowledge 스킬 공용 -- 경로가 Herbarium 인지 판정 |

에이전트는 쓰지 않는다.

---

## 경로 설정

경로가 Herbarium 인지 판정하는 규약은 아래 공용 파일이 단일 출처다.

    references/herbarium-path.md

활성 직후 이 파일을 Read 툴로 로드해 따른다. 본 스킬이 사용자에게 받는 경로는 Herbarium 저장소 루트 하나이며, 공용 파일의 검증 절차를 그 경로에 적용한다.

채택한 루트 하위에서 wip 폴더(`<루트>/wip`)와 확정지식 디렉토리(`<루트>/knowledge`)를 도출한다. 이 둘은 따로 입력받지 않는다.

<FORBIDDEN>
wip 폴더나 확정지식 디렉토리 경로를 사용자에게 별도로 입력받지 않는다.
</FORBIDDEN>

---

## 렌더 surface 전제

확정지식의 1차이자 유일한 설계 타겟 렌더 surface 는 Herbarium 의 GitHub Pages 다. GitHub 블롭 뷰나 다른 마크다운 뷰어로도 열 수는 있으나 포맷을 그쪽에 맞추지 않는다.

빌드는 Jekyll 을 GitHub Actions 커스텀 워크플로로 돌린다. 마크다운이 단일 진실원천이고, `knowledge/<id>.md` 가 푸시될 때마다 워크플로가 사이트 전체를 자동 재빌드·배포한다. 그래서 promote 는 노트별 HTML 을 만들거나 별도 빌드를 호출하지 않는다 -- md 저장이 곧 산출이고 렌더는 CI 가 맡는다.

사이트 기반 파일(`_config.yml`·`_layouts`·`assets/css`·인덱스·워크플로)은 Herbarium 레포가 관리하며 이 스킬의 범위 밖이다. 스킬은 그 기반 파일이 렌더하기 좋은 깨끗한 마크다운만 산출한다.

기반 파일이 전제하는 계약(스킬이 맞춰 산출할 것):

- 레이아웃은 기반 파일의 `_config.yml` `defaults` 로 `knowledge/` 전체에 일괄 부여한다. 노트 frontmatter 에 `layout` 을 개별로 두지 않아 md 를 지식 내용만으로 깨끗이 유지한다.
- `summary` 는 레이아웃이 `white-space: pre-line` 으로 출력한다. 그래서 값의 줄바꿈이 화면 줄바꿈으로 보인다(아래 summary 표기).
- Mermaid 는 레이아웃이 포함한 클라이언트측 `mermaid.js` 가 렌더한다. Jekyll 플러그인은 쓰지 않는다.

---

## 실행 순서

활성 직후 위 "경로 설정" 을 먼저 수행해 wip · knowledge 경로를 확정한 뒤, 아래 순서로 진행한다.

1. 대상 선택
2. 형식 변환
3. 관계 추출
4. 일반화
5. 검증
6. 중복·충돌 점검
7. 브랜치 생성·체크아웃
8. 초안 저장 후 사용자 검토·승인
9. 원본 wip 처리
10. 커밋
11. 종료 보고

### 1. 대상 선택

TaskCreate 로 "1. 대상 선택" task 를 등록하고 in_progress 로 설정한다. 대상 wip 가 결정되면 completed 로 닫는다.

채택한 wip 디렉토리를 Glob 해 목록을 보여주고 사용자가 하나를 고르게 한다. 한 번에 하나의 wip 만 승급한다.

목록이 비면 승급할 초안이 없는 것이다. 그 사실과 확인한 경로를 알리고 여기서 끝낸다. 뒤 단계는 전부 대상 wip 를 전제하므로 진행할 수 없다.

### 2. 형식 변환

TaskCreate 로 "2. 형식 변환" task 를 등록하고 in_progress 로 설정한다. 형식 변환이 완료되면 completed 로 닫는다.

wip 산문을 확정지식 형식(프론트매터 + 정제 본문)으로 바꾼다. 프론트매터 칸과 본문 표기 규칙의 단일 출처는 아래 하위 파일이다.

    skills/knowledge-promote/format/format.md

이 단계에 들어올 때 그 파일을 Read 툴로 로드해 따른다.

`kind`(`concept` 또는 `code`)가 본문 구성을 가르며, 그 값은 wip 맨 위 `<!-- wip-meta: ... -->` 주석에서 읽는다. `relations` 칸은 다음 단계가 채운다.

### 3. 관계 추출

TaskCreate 로 "3. 관계 추출" task 를 등록하고 in_progress 로 설정한다. 추출이 완료되면 completed 로 닫는다.

wip 의 "관련 개념"·본문 언급을 relations 타입드 엣지로 만든다. 종류 4개:

- `contrasts_with` — 같은 역할의 반대/경쟁 선택지
- `same_family` — 같은 계열의 동료
- `part_of` — 부분-전체 종속 (하위가 상위의 일부). 예: views 는 Ranges 의 일부
- `related` — 그 밖에 엮인 연관 개념 (종류 미분류)

대상은 다른 확정지식의 id 다. 채택한 knowledge 디렉토리를 Glob 으로 보고 실재 id 와 우선 연결한다.

저장 포맷 -- relations 는 `타입:대상` 문자열의 평탄 리스트로 frontmatter 에 둔다. 중첩 맵을 쓰지 않는다.

```yaml
relations: [contrasts_with:characterization-test, same_family:bdd, part_of:ranges, related:unit-test]
```

타입이 문자열 prefix 라 새 종류 추가가 스키마 변경이 아니다. 그래도 종류 남발은 피하고, 위 4종으로 안 잡히는 더 세밀한 세분화는 노드가 쌓인 뒤로 미룬다.

<FORBIDDEN>
가리키는 id 파일이 아직 없다는 이유로 그 관계를 relations 에서 빼지 않는다.
</FORBIDDEN>

### 4. 일반화

TaskCreate 로 "4. 일반화" task 를 등록하고 in_progress 로 설정한다. 완료되면 completed 로 닫는다.

확정지식은 전역이라 특정 프로젝트에 종속된 부분을 걷어낸다. wip 의 "캡처 맥락" 격리 블록(프로젝트 이름·언어·규모·아키텍처·그 프로젝트의 결정)은 확정지식에서 들어내거나 압축한다. 보편 서술은 "본 프로젝트는 ..." 대신 조건 서술("...할 때")로 다듬는다. 미해결 질문은 그 주제에 보편적인 항목만 남기고 특정 프로젝트의 결정은 뺀다.

프로젝트 특유 요소는 산문에만 있지 않다. 코드 예제·발췌(특히 code-scan 유래 wip)에 스캔 원본의 프로젝트 고유 식별자(함수·타입·변수명)가 남아 있으면 범용 이름으로 치환한다.

캡처 맥락이 `[전제 없음]` 표식 한 줄이면, capture 의 writer 가 검토 후 걷어낼 프로젝트 특유 요소가 없다고 판단한 것이다. 이때는 본문을 그대로 통과시키고 추가로 덜어낼 프로젝트 특유 요소를 찾지 않는다(표식 줄만 strip). 반대로 캡처 맥락이 표식도 내용도 없이 진짜 비었거나 섹션 자체가 없으면 writer 누락을 의심해, 본문에 프로젝트 특유 요소가 남아 있는지 한 번 더 점검하고 의심되면 사용자에게 확인한다.

<FORBIDDEN>
코드 예제·발췌에 스캔 원본 프로젝트의 고유 식별자를 그대로 남기지 않는다.
</FORBIDDEN>

### 5. 검증

TaskCreate 로 "5. 검증" task 를 등록하고 in_progress 로 설정한다. 검증이 완료되면 completed 로 닫는다.

- 참고 자료의 URL 이 살아있는지 WebFetch 로 확인한다. 죽은 링크는 사용자에게 보고한다. URL 이 꺾쇠(`<url>`) 또는 `[라벨](url)` 형식인지 함께 확인하고, bare URL 이면 교정한다.
- wip 의 `조사 보류 목록`(capture 의 백그라운드 writer 가 권한 제약으로 못 메운 항목)을 처리한다. 각 항목의 출처를 실제 WebFetch 로 가져와 본문의 대응 `[미검증 #N]` 마커 위치와 대조하고, 어긋나면 정정한다. promote 는 포그라운드라 도메인 미허용이어도 사용자 일회 승인(등록 없이)으로 fetch 할 수 있다. 검증으로 확정된 항목은 보류 목록에서 내리고 본문의 `[미검증 #N]` 마커를 지운다. 이 마커와 보류 목록은 wip 전용이라 확정지식 최종본에 남기지 않는다.
- 사용자가 fetch 승인을 거부하거나 출처로도 확정 못 한 항목은 `미해결 질문` 으로 옮겨 잔류시킨다(graceful).
- 전체 예제(코드 예제)를 실제로 컴파일·실행해 통과를 확인한다. 순수 illustration 코드(실행할 API 가 아님)는 대상이 아니다.
  - 컴파일러·런타임 부재 등으로 못 돌리면(검증 불가) "검증 불가" 로 사용자에게 보고한다(graceful).
  - 빌드는 됐는데 실패하면(검증 실패 = 코드 결함) 메인이 명백한 누락(빠진 include 등)을 정정해 재빌드한다. 몇 차례로도 통과 못 하면 8단계 이슈로 사용자에게 보고한다(자동 무한 정정은 하지 않는다).
- 사실성이 의심되는 서술은 표시해 사용자 확인 항목으로 남긴다.

<FORBIDDEN>
조사 보류 목록에서 검증되지 못한 미검증 서술을 확정지식 본문에 단정형으로 올리지 않는다.
</FORBIDDEN>

### 6. 중복·충돌 점검

TaskCreate 로 "6. 중복·충돌 점검" task 를 등록하고 in_progress 로 설정한다. 점검이 완료되면 completed 로 닫는다.

`knowledge/` 의 기존 확정지식과 summary 를 비교해 의미적으로 겹치는 후보를 찾는다. 중복(같은 주제) 또는 충돌(같은 주제, 다른 서술)이 의심되면 병합·대체·별도 중 무엇이 맞는지 사용자에게 묻는다.

고른 갈래가 뒤 단계의 대상 파일과 브랜치명을 가른다. 겹치는 후보가 없으면 묻지 않고 별도로 본다.

| 갈래 | 대상 id | 8단계가 쓰는 파일 |
|------|--------|------------------|
| 별도 | 새 id | `<knowledge>/<새 id>.md` 신규 생성 |
| 병합 | 기존 id | `<knowledge>/<기존 id>.md` 를 읽어 이번 내용을 반영해 다시 쓴다. 기존 서술을 지우지 않고 합친다 |
| 대체 | 기존 id | `<knowledge>/<기존 id>.md` 를 이번 변환 결과로 갈아엎는다 |

<FORBIDDEN>
병합을 고른 사용자에게 기존 파일 내용을 덜어낸 결과를 내지 않는다.
</FORBIDDEN>

### 7. 브랜치 생성·체크아웃

TaskCreate 로 "7. 브랜치 생성·체크아웃" task 를 등록하고 in_progress 로 설정한다. 브랜치 생성 및 체크아웃이 완료되면 completed 로 닫는다.

승급 산출을 Herbarium main 에 직접 넣지 않고 브랜치에서 격리해, main 머지 시점에 CI 자동 배포가 일어나도록 한다.

브랜치명은 `promote/<id>` 를 기본으로 하고, 날짜형 `promote/<YYYY-MM-DD>` 를 대안으로 허용한다. base 는 main. `<id>` 는 6단계에서 정해진 대상 id 이며, 병합·대체면 기존 id 다.

1. 현재 브랜치가 main 인지 확인하고, main 이 아니면 먼저 main 으로 이동한다.
2. `git -C <herbarium루트> checkout -b promote/<id>` 로 신규 브랜치를 생성·체크아웃한다.

이후 8·9 단계(저장·원본 wip 처리)는 이 브랜치 위에서 수행한다.

<FORBIDDEN>
브랜치를 만들지 않고 Herbarium main 에 직접 저장하지 않는다.
</FORBIDDEN>

### 8. 초안 저장 후 사용자 검토·승인

TaskCreate 로 "8. 확정지식 초안 저장" task 를 등록하고 in_progress 로 설정한 뒤, 7단계에서 만든 브랜치의 `<knowledge>/<id>.md` 로 변환 초안을 먼저 저장한다. 저장이 끝나면 completed 로 닫는다. 이어서 TaskCreate 로 "8. 사용자 검토·승인" task 를 등록하고 in_progress 로 설정한다. 검토를 요청하기 직전 completed 로 닫고, 응답을 받아 다음 단계로 간다.

저장한 파일 경로를 알리고, 5·6 단계의 이슈(죽은 링크, 사실성 의심, 중복·충돌 후보)만 대화창에 함께 제시해, 사용자가 파일을 직접 열어 검토·승인하게 한다. 사용자가 수정을 요청하면 파일을 고쳐 다시 검토받는다.

파일은 이 단계에서 이미 브랜치 작업트리에 쓰였고(커밋 전), 승인은 이후 10단계 커밋의 게이트가 된다.

<FORBIDDEN>
변환 초안 본문을 대화창에 통째로 출력하지 않는다.
</FORBIDDEN>

<FORBIDDEN>
사용자 승인을 받지 않은 초안을 10단계 커밋으로 넘기지 않는다.
</FORBIDDEN>

### 9. 원본 wip 처리

TaskCreate 로 "9. 원본 wip 처리" task 를 등록하고 in_progress 로 설정한다. 처리가 완료되면 completed 로 닫는다.

승급 후 원본 wip 를 삭제할지 남길지 사용자에게 확인한다.

<FORBIDDEN>
사용자 확인 없이 원본 wip 파일을 삭제하지 않는다.
</FORBIDDEN>

### 10. 커밋

TaskCreate 로 "10. 커밋" task 를 등록하고 in_progress 로 설정한다. 커밋이 완료되면 completed 로 닫는다.

승급 산출(`knowledge/<id>.md`)과 원본 wip 처리 결과를 7단계에서 만든 브랜치에 커밋한다. 커밋 메시지 형식은 갈래를 따른다.

| 갈래 | 커밋 메시지 |
|------|------------|
| 별도 | `Promote <id> to knowledge` |
| 병합 | `Merge <wip topic> into <id>` |
| 대체 | `Replace <id> with promoted <wip topic>` |

<FORBIDDEN>
커밋한 브랜치를 대신 푸시하지 않는다.
</FORBIDDEN>

<FORBIDDEN>
커밋한 브랜치를 대신 머지하지 않는다.
</FORBIDDEN>

### 11. 종료 보고

TaskCreate 로 "11. 종료 보고" task 를 등록하고 in_progress 로 설정한다. 보고가 끝나면 completed 로 닫는다.

아래를 한 번에 알리고 끝낸다.

- 저장된 확정지식 파일 경로와 브랜치명
- 원본 wip 를 지웠는지 남겼는지
- 5·6 단계에서 미해결로 남은 이슈 (검증 불가 예제, 죽은 링크, 중복·충돌 후보)

---

## 다루지 않는 것

- 마크다운 -> SQLite/벡터 빌드, 임베딩, 그래프 시각화는 본 스킬 범위 밖이다.
- 여러 wip 를 한 번에 승급하는 배치 처리는 본 스킬 범위 밖이다.
