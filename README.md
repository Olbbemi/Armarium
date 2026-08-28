# Armarium

**현재 버전: `0.38.0`**

개인 커스텀 스킬을 담아 **여러 프로젝트에서 공통으로 쓰는 비공개 Claude Code 플러그인**.

라틴어로 도구/책을 넣어두는 보관장(캐비닛)을 뜻한다. Hortus 네이밍 패밀리의 한 구역.

```
Hortus (정원 — 상위 우산)
├── Terrarium   작업 본체
├── Herbarium   지식 보존 아카이브 (확정지식 저장소)
└── Armarium    스킬·도구 보관장   <- 이 repo
```

---

## 이 repo의 역할

커스텀 스킬을 한 곳에서 버전관리하고, 플러그인으로 설치해 **어느 프로젝트에서나** 쓰기 위한 저장소.

- 프로젝트별 `.claude/skills/` 에 흩어두면 다른 프로젝트에서 못 쓴다 -> 플러그인으로 묶어 해결.
- **공개 마켓플레이스에 게시하지 않는다.** `marketplace.json` 은 repo 안 파일일 뿐이고, 사용자가 이 repo 를 직접 마켓플레이스로 add 해야 쓸 수 있다. (git repo 가 public 이어도 그건 일반 repo 노출이지 공개 마켓플레이스 등재가 아니다.)
- 플러그인이라 스킬뿐 아니라 **에이전트·규약(CLAUDE.md)·훅까지 묶어** 배포되어, 다른 프로젝트에서도 의존성 없이 자기완결로 동작한다.

---

## 구조

```
Armarium/
├── .claude-plugin/
│   ├── marketplace.json   # 이 repo 를 마켓플레이스로 선언 (name: hortus)
│   └── plugin.json        # 플러그인 정의 (name: armarium)
├── CLAUDE.md              # 규칙 소유 지점과 작업 규칙
├── verify.json            # 규칙 셋 목록 + 대상 종류별 경로
├── core/                  # 툴과 무관한 절차
│   ├── core.md            # 나머지 코어 문서의 지도
│   ├── verify.md          # 검증을 돌리고 결과를 읽는다
│   ├── rules.md           # 규칙을 만들고 고친다
│   └── writing.md         # 문서 본문에 넣지 않는 것
├── rules/                 # 산출물 규칙 1개 = 파일 1개. 유일한 원본
├── engine/
│   ├── verify.py          # 규칙을 읽어 판정기를 돌리는 엔진
│   ├── gen_index.py       # 규칙 인덱스 생성
│   ├── render.py          # 산출물을 사람이 읽는 형태로
│   ├── scaffold.py        # 스킬·규칙 뼈대 생성
│   ├── selftest.py        # 엔진 최하층 자기검사
│   ├── checks/            # 규칙별 판정기
│   └── meta-rules/        # 규칙 셋과 코어를 검사하는 규칙
├── adapters/              # 툴별 실행 차이 (claude-code / codex / generic)
├── .githooks/
│   └── pre-commit         # 검증을 통과해야 커밋이 된다
├── scripts/
│   ├── loop.py            # 검증을 반복해 돌리는 루프 러너 (툴 중립)
│   └── install-hooks.sh   # core.hooksPath 를 .githooks 로 설정
├── hooks/
│   ├── session-skill-list.sh   # 세션 시작 배너
│   └── stop-verify-loop.py     # 루프 활성 시 통과 못 한 종료를 막는다
├── old/                   # 개편 이전 스킬 보관본 (등록에서 빠짐, 참고용)
└── skills/                # 스킬 본체 (각 디렉토리 = 스킬 1개)
    └── skill-writing/
        ├── SKILL.md       # Claude Code 진입점
        └── procedure.md   # 새 스킬을 만드는 절차

여러 스킬이 쓸 수 있는 것은 루트에 둔다. 한 스킬에서만 참인 것만 그 스킬 아래 둔다.
```

- `skills/<스킬>/SKILL.md` — 진입점. 어느 문서를 로드할지만 담고, 절차 본문은 그 문서가 갖는다.
- 문서 안의 파일 경로는 **플러그인 루트 상대**로 쓴다. 프로젝트 절대경로를 쓰지 않는다.
- 서브에이전트는 개편 이후 아직 쓰지 않는다. 툴 고유 기능이라 어댑터 소관이다.

---

## 설치

`/plugin` 은 슬래시 명령이라 세션에서 직접 입력한다. 평생 1회면 된다.

```
/plugin marketplace add Olbbemi/Armarium
/plugin install armarium@hortus
/reload-plugins
```

- GitHub `owner/repo` 로 add 하면 Claude Code 가 자동으로 clone·캐시한다 (`~/.claude/plugins/`). 직접 clone 할 필요 없다.
- **user scope** 설치라 1회만 하면 어느 프로젝트에서 켜든 `armarium:<스킬>` 으로 노출된다.
- 등록이 바로 안 보이면 `/reload-plugins` 또는 새 세션.

---

## 커밋 전 검사

`.githooks/pre-commit` 이 `engine/selftest.py` 와 `engine/verify.py` 를 돌려, 통과하지 못하면
커밋을 막는다. 전체가 0.3초 안에 끝난다.

클론한 자리에서 한 번 설정해야 걸린다.

```
bash scripts/install-hooks.sh
```

- `.git/hooks/` 는 커밋되지 않아 클론에 따라오지 않는다. 그래서 저장소 안 `.githooks/` 를 두고
  `core.hooksPath` 로 가리킨다.
- 검사 대상은 워킹트리다. 일부만 스테이지한 커밋에서는 스테이지 내용과 어긋날 수 있다.
- 설정하지 않은 클론에서는 훅이 아예 안 돈다. 그 사실은 아무것도 검출하지 못한다.

## 세션 시작 배너

설치해 두면 새 세션 시작 시 화면 배너에 스킬 목록(이름 + 한 줄 설명)이 자동 표시된다.

- SessionStart 훅(`hooks/session-skill-list.sh`)이 `skills/*/SKILL.md` 를 훑어 목록을 만든다.
- 기존 대화를 잇는 맥락(resume·compact)에서는 배너를 안 띄운다.

같은 훅이 특정 스킬 본문을 `additionalContext` 로 실어 보내 자동 활성할 수 있다. 개편 이후로는
그렇게 활성되는 스킬이 없다. 되살릴 때 아래 두 가지가 그대로 적용된다.

- 배너와 컨텍스트 주입은 별개 필드(`systemMessage` / `additionalContext`)라 따로 논다.
- `compact` 에서도 주입해야 한다. 자동 압축이 앞서 넣은 본문을 날리므로, 다시 넣지 않으면
  압축 이후 그 스킬이 조용히 멈춘다.

---

## 수록 스킬

| 스킬 | 요약 | 호출 |
|------|------|------|
| [`skill-writing`](skills/skill-writing/README.md) | 새 스킬을 만들고 고칠 때 따르는 절차 | `/skill-writing`, "스킬 만들어줘" |

개편 이전 스킬 9개는 [`old/`](old/README.md) 에 있다. 플러그인 등록에서 빠져 있고 참고용으로만 읽는다.

## 새 스킬 추가

절차는 [`skills/skill-writing/procedure.md`](skills/skill-writing/procedure.md) 가 소유한다.
무엇을 스킬로 만들지, 무엇을 루트에 두고 무엇을 스킬 아래 둘지가 거기 있다.

만든 뒤 위 "수록 스킬" 표에 한 줄을 더하고, 커밋·푸시 후 아래 "업데이트" 흐름으로 반영한다.

## 버전 규칙

`.claude-plugin/plugin.json` 의 `version` 은 SemVer(`major.minor.patch`)를 따른다. **plugin payload**(`skills/` · `core/` · `rules/` · `engine/` · `adapters/` · `CLAUDE.md` 등 배포물)가
바뀔 때만 올리며, `.claude/` 같은 비배포 파일은 버전과 무관하다.

| 등급 | 기준 | 예 |
|------|------|----|
| MAJOR `X.0.0` | 부르는 법·연동 규약이 깨짐 | 스킬/슬래시 명령 이름 변경·삭제, 호출·경로·등록 규약 변경, 필수 입력 추가, 명시한 보장 제거 |
| MINOR `0.X.0` | 사용자가 새로 할 수 있는 일이 생김 | 새 스킬·에이전트 추가, 새 옵션·입력 필드·트리거·지식 종류 노출 |
| PATCH `0.0.X` | 새 능력 없이 기존 것을 고치거나 다듬음 | 버그 수정, 문구·오타·README, 내부 리팩터링, 군더더기 제거·단순화, 스펙대로 동작 복원, 기존 규칙의 명확화·강화 |

등급은 위에서부터 질문 사다리로 판정한다.

1. **부르는 법·연동 규약이 바뀌어 기존 방식이 안 통하나?** -> MAJOR. 같은 이름·같은 입력이면 내부 동작을 근본적으로 갈아엎어도 MAJOR 가 아니다.
2. **이 변경으로 사용자가 *새로* 할 수 있게 된 일이 있나?** -> MINOR. 검증을 더 빡세게 거는 등 기존 동작을 조이는 것은 새 능력이 아니다.
3. 둘 다 아니다 -> PATCH. 스킬 문서를 고쳤다는 사실만으로 MINOR 가 되지 않는다. 명확화·교정·단순화·동작 정합 복원은 PATCH 다.

- **0.x 단계:** 스킬 셋과 호출 규약이 안정될 때까지는 1.0 전이며, 이 동안엔 큰 변경도 0.x 안에서 MINOR로 흡수해도 된다. 안정되면 `1.0.0` 으로 올린다.
- 버전을 안 올리고 push 하면 `/plugin marketplace update` 가 변경을 받아오지 않는다. push 직전 확인 훅이 이를 잡아준다.

### 버전 올릴 때 고치는 곳 (3군데, 같은 값으로)

버전을 올릴 때 아래 **세 파일을 모두 같은 값으로** 바꾼다. 하나라도 빠지면 카탈로그 버전이 어긋나거나 README 표기가 실제와 달라진다.

| # | 파일 | 위치 | 자동 검사 |
|---|------|------|----------|
| 1 | `.claude-plugin/plugin.json` | `"version"` 필드 | push 훅이 직전 푸시 대비 상승 여부 검사 |
| 2 | `.claude-plugin/marketplace.json` | 해당 플러그인의 `"version"` 필드 | push 훅이 plugin.json 과 parity 검사 |
| 3 | `README.md` | 상단 `**현재 버전: ...**` 줄 | push 훅이 plugin.json 과 parity 검사 |

`check-version-bump.sh` 훅은 1·2·3 세 곳을 모두 잡는다 — plugin.json 의 직전 푸시 대비 상승, marketplace.json parity, README 상단 표기 parity 를 검사한다. 그래도 버전을 올릴 때 세 곳을 같은 값으로 함께 바꾼다.

---

## 업데이트

소스 저장소(`/home/olbbemi/Project/Armarium`)를 고쳐 GitHub 에 올리고 설치처(캐시)를 갱신하는 흐름이다. 설치된 플러그인은 `~/.claude/plugins/cache/...` 의 읽기전용 사본이라 직접 고치지 않는다.

1. 소스 저장소에서 수정 -> commit -> push
2. 의미 있는 변경이면 `.claude-plugin/plugin.json` 의 `version` 을 올린다 (안 올리면 update 가 변경을 받아오지 않는다).
3. `/plugin marketplace update hortus` -> `/reload-plugins`

> push 시 `version` 미변경을 잡아주는 확인 훅이 `.claude/settings.json` 에 있다 (armarium 저장소에서 작업할 때만 동작).
