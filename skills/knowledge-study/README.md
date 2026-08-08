# knowledge-study

CS 로드맵 카탈로그를 기준으로 아직 정리하지 않은 주제를 골라 wip 초안으로 누적하는 스킬.

## 무엇을 하나

Herbarium 의 영역별 로드맵 카탈로그를 읽고, 이미 정리한 것과 대조해 미착수 주제를 보여준다.<br>
사용자가 고른 주제를 `knowledge-writer` 에이전트에 위임해 wip 본문을 만든다.<br>
wip 누적까지만 담당하며, 확정지식 승급은 별도 스킬 [`knowledge-promote`](../knowledge-promote/README.md)가 맡는다.

## 형제 스킬

wip 를 만드는 스킬은 셋이고, 진입 경로가 서로 다르다. 저장 경로 검증 · writer 호출 · 저장 규칙은 [`references/knowledge-wip-protocol.md`](../../references/knowledge-wip-protocol.md) 를 셋이 공유한다.

| 스킬 | 진입 | 앵커 |
|------|------|------|
| [`knowledge-capture`](../knowledge-capture/README.md) | 대화 중 감지 또는 명시 요청 (상시) | 대화 발췌 |
| [`knowledge-scan`](../knowledge-scan/README.md) | 코드베이스 스캔 명령 (단발) | 코드 발췌 |
| `knowledge-study` | CS 로드맵에서 주제 선택 (단발) | 카탈로그 항목 |

앞의 둘은 반응형이다 -- 막힌 지점이나 눈앞의 코드가 있어야 시작된다. 이 스킬만 능동형으로, 미리 세운 로드맵에서 주제를 골라 시작한다.

## 언제 쓰나

`/knowledge-study` 슬래시 명령으로 **명시적으로 활성**했을 때만 동작한다.<br>
로드맵을 열고, 오늘 볼 주제를 고르고, 위임하고 닫는 단발 작업이다.

## 구조

- `overview.md` -- 진입점. 경로 설정 · 카탈로그 형식 · 진척 대조 · 로드맵 제시 · writer 위임
- `bootstrap/bootstrap.md` -- 카탈로그가 없을 때 처음 채우는 1회성 절차
- `knowledge-roadmap-builder` 에이전트 (플러그인 루트 `agents/knowledge-roadmap-builder.md`) -- 공개 로드맵 조사 후 영역·항목 목록 반환 (부트스트랩 전용)
- `knowledge-writer` 에이전트 (플러그인 루트 `agents/knowledge-writer.md`) -- 메인 입력을 받아 wip 본문 작성 후 반환 (저장은 안 함)

## 카탈로그

로드맵 카탈로그는 armarium 이 아니라 **Herbarium** 에 산다. 정리하다 보면 항목이 계속 늘어나는데, armarium 은 모든 변경이 PR 대상이라 항목 하나 추가에 브랜치를 따야 하기 때문이다.

영역당 파일 하나이며 영역 목록은 디렉토리 Glob 으로 얻는다(별도 인덱스 없음).

```markdown
# 네트워크

> 출처: roadmap.sh/computer-science, Teach Yourself CS (2026-08-08 조사)

## 전송 계층
- `tcp-congestion-control` -- TCP 혼잡 제어
- `head-of-line-blocking` (aliases: hol-blocking) -- 큐 선두 차단
```

슬러그를 kebab-case 영어로 고정하는 이유는 진척 대조가 파일명 대조이기 때문이다.

## 진척 추적

"무엇을 이미 정리했나" 는 **저장하지 않고 매번 계산한다**. 진척 파일을 따로 두면 승급할 때마다 두 군데를 갱신해야 해서 반드시 어긋난다.

`wip/` 와 `knowledge/` 를 Glob 해 파일명 집합을 만들고, 카탈로그 항목의 슬러그·`aliases` 와 대조해 미착수 / wip 있음 / 확정 3상태로 판정한다.<br>
논의 중 `knowledge-capture` 가 로드맵에 있는 주제를 잡으면 이 진척이 저절로 올라간다.

## 동작 흐름

1. roadmap 경로와 wip 경로를 입력받아 검증 (확정지식 경로는 roadmap 경로의 저장소 루트에서 찾음)
2. 카탈로그 로드 -- 없거나 비었으면 부트스트랩으로 빠짐
3. 진척 대조 -- 슬러그 대조로 3상태 판정
4. 영역 선택 -> 그 영역의 **미착수 항목만** 제시 -> 주제 선택
5. 사전 질의 한 번 ("이 주제 어디까지 아세요?")
6. writer 에 **백그라운드** 위임 -> 반환 본문을 메인이 저장
7. 통지를 기다리는 동안 4~6 을 반복할 수 있음

## 부트스트랩

카탈로그가 없으면 1회성으로 돈다. `knowledge-roadmap-builder` 가 공개 로드맵(roadmap.sh, Teach Yourself CS 등)을 조사해 영역 목록을 내고, 사용자가 확정한 영역마다 병렬로 항목 목록을 채운다.<br>
실질 게이트는 영역 확정 한 번이다. 항목 목록은 영역당 수십 개라 전부 검토시키지 않고, 저장 직전 요약 확인만 받는다.

## 주의

- 주제 선택 목록에는 미착수 항목만 올린다. 이미 있는 항목을 굳이 고르면 보강할지 새로 쓸지 묻는다.
- 진척 상태를 파일이나 인덱스에 저장하지 않는다. 매 실행마다 파일명 대조로 계산한다.
- 카탈로그 파일을 쓰기 전에 추가할 항목을 사용자에게 확인받는다. 커밋·푸시는 사용자가 요청할 때만 한다.
- 백그라운드 에이전트에게 파일을 직접 저장(Write/Edit)시키지 않는다. 저장은 메인이 한다.
